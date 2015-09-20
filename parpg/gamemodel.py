#   This file is part of PARPG.

#   PARPG is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   PARPG is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with PARPG.  If not, see <http://www.gnu.org/licenses/>.

# there should be NO references to FIFE here!
import sys
import os.path
import logging
from copy import deepcopy

from fife import fife
from fife.extensions.serializers.xmlobject import XMLObjectLoader 
from bGrease.geometry import Vec2d
from serializers import XmlSerializer

from parpg import vfs
from gamestate import GameState
from gamemap import GameMap
from common.utils import locateFiles
from common.utils import parseBool
from parpg.dialogueparsers import YamlDialogueParser, DialogueFormatError
from parpg.entities import createEntity
from parpg import behaviours
from parpg import components
from parpg.components import fifeagent, container, equip, character_statistics
import characterstatistics as char_stats

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree

import yaml

logger = logging.getLogger('gamemodel')

class GameModel(object):
    """GameModel holds the logic for the game.
       Since some data (object position and so forth) is held in the
       fife, and would be pointless to replicate, we hold a instance of
       the fife view here. This also prevents us from just having a
       function heavy controller."""
    ALL_AGENTS_KEY = "All"
    MAX_ID_NUMBER = 1000
    GENERIC_ITEM_GFX = "generic_item"
    DEFAULT_STAT_VALUE = 50
    
    def __init__(self, engine, settings):
        """Initialize the instance.
        @param engine: A fife.Engine object
        @type emgome: fife.Engine 
        @param setting: The applications settings
        @type setting: parpg.settings.Settings object
        @return: None"""
        self.settings = settings

        self.map_change = False
        self.load_saver = False
        self.savegame = None
        quests_directory = settings.get("parpg", "QuestsPath")
        #setup functions for the GameEnvironment        
        self.game_state = GameState(quests_dir=quests_directory)
        funcs = {
                 "moveObject":self.moveObject, 
                 "deleteObject":self.deleteObject, 
                 "putItemIntoContainer":container.put_item,
                 "equipItem":equip.equip, 
                 }
        self.game_state.funcs.update(funcs)
        self.pc_run = 1
        self.target_position = None
        self.target_map_name = None
        self.object_db = {}
        self.active_map = None
        self.map_files = {}
        self.agents = {}
        self.agents[self.ALL_AGENTS_KEY] = {}
        self.items = {}
        self.engine = engine
        self.fife_model = engine.getModel()

        # set values from settings
        maps_directory = settings.get("parpg", "MapsPath")
        self.game_state.maps_file = '/'.join([maps_directory,
                                              settings.get("parpg", "MapsFile")])
        self.all_agents_file = '/'.join([maps_directory,
                                         settings.get("parpg", "AllAgentsFile")])
        objects_directory = self.settings.get("parpg", "ObjectsPath")
        self.objects_directory = objects_directory
        self.object_db_file = '/'.join([objects_directory,
                                        settings.get("parpg", "ObjectDatabaseFile")])
        self.dialogue_directory = settings.get("parpg", "DialoguesPath")
        self.dialogues = {}
        self.agent_import_files = {}
        self.obj_loader = XMLObjectLoader(self.engine)
        # FIXME M. George Hansen 2011-06-06: character stats scripts aren't
        #     finished, unfortunately.
        # NOTE Beliar 2011-11-05 Activated the stats. Testing needed if it 
        # works correctly, or if they are still unfinished.
        primary_stats_file = (
            vfs.VFS.open('character_scripts/primary_stats.xml')
        )
        self.primary_stats = XmlSerializer.deserialize(primary_stats_file)
        secondary_stats_file = (
            vfs.VFS.open('character_scripts/secondary_stats.xml')
        )
        self.secondary_stats = XmlSerializer.deserialize(secondary_stats_file)        

        
    def create_stats(self, entity):
        for primary_stat in self.primary_stats:
            long_name = primary_stat.long_name
            entity.characterstats.primary_stats[long_name] = (
                char_stats.PrimaryStatisticValue(
                    primary_stat, entity.characterstats, 
                    self.DEFAULT_STAT_VALUE)
            )
        for secondary_stat in self.secondary_stats:
            name = secondary_stat.name            
            entity.characterstats.secondary_stats[name] = (
                char_stats.SecondaryStatisticValue(secondary_stat, 
                                                   entity.characterstats
                                                   )
            )
            
    def checkAttributes(self, attributes, template):
        """Checks for attributes that where not given in the map file
        and fills them with values from the object database
        @param attributes: attributes to check        
        @type attributes: Dictionary
        @param template: Template from which the values will be used
        @return: The modified attributes""" 
        if self.object_db.has_key(template):
            db_attributes = deepcopy(self.object_db[template])
            for key in db_attributes.keys():
                if attributes.has_key(key):                    
                    tmp_attributes = db_attributes[key]
                    tmp_attributes.update(attributes[key])
                    attributes[key] = tmp_attributes
                else:
                    attributes[key] = db_attributes[key]
        return attributes
    
    def isIDUsed(self, ID):
        if self.game_state.hasObject(ID):
            return True
        for namespace in self.agents:
            if ID in self.agents[namespace]:
                return True
        return False
    
    def createUniqueID(self, ID):
        if self.isIDUsed(ID):
            id_number = 1
            while self.isIDUsed(ID + "_" + str(id_number)):
                id_number += 1
                if id_number > self.MAX_ID_NUMBER:
                    raise ValueError(
                        "Number exceeds MAX_ID_NUMBER:" + 
                        str(self.MAX_ID_NUMBER)
                    )
            
            ID = ID + "_" + str(id_number)
        return ID
    
    def moveObject(self, object_id, new_map):
        """Moves the object to a new map, or in a container
        @param object_id: ID of the object
        @type object_id: str 
        @param new_map: ID of the new map, or None
        @type object_id: str """
        game_object = self.deleteObject(object_id)
        self.game_state.addObject(object_id, new_map, game_object)

    def deleteObject(self, object_id):
        """Removes an object from the game
        @param object_id: ID of the object
        @type object_id: str """
        if self.agents["All"].has_key(object_id):
            del self.agents["All"][object_id]
        else:
            del self.items[object_id]
        return self.game_state.deleteObject(object_id)
        
    def save(self, path, filename):
        """Writes the saver to a file.
           @type filename: string
           @param filename: the name of the file to write to
           @return: None"""
        fname = '/'.join([path, filename])
        try:
            save_file = open(fname, 'w')
        except(IOError):
            sys.stderr.write("Error: Can't create save game: " + fname + "\n")
            return

        save_state = {}
        save_state["Agents"] = self.agents
        save_state["Items"] = self.items
        save_state["GameState"] = self.game_state.getStateForSaving()
        
        yaml.dump(save_state, save_file)
        
        save_file.close()       

    def load(self, path, filename):
        """Loads a saver from a file.
           @type filename: string
           @param filename: the name of the file (including path) to load from
           @return: None"""
        fname = os.path.join(path, filename)

        try:
            load_file = open(fname, 'r')
        except(IOError):
            sys.stderr.write("Error: Can't find save game file '" + fname + "'\n")
            return        
        self.deleteMaps()
        self.clearAgents()
        
        save_state = yaml.load(load_file)
        self.game_state.restoreFromState(save_state["GameState"])
        maps = save_state["Agents"]
        for map_name in maps:
            for agent_name in maps[map_name]:
                agent = {agent_name:maps[map_name][agent_name]}
                self.addAgent(map_name, agent)
        self.items = save_state["Items"]               
      
        load_file.close()             
         
    def teleport(self, agent, position):
        """Called when a an agent is moved instantly to a new position. 
        The setting of position may wan to be created as its own method down 
        the road.
        @type position: String Tuple
        @param position: X,Y coordinates passed from engine.changeMap
        @return: fife.Location"""
        logging.debug(position)
        coord = fife.DoublePoint3D(float(position[0]), float(position[1]), 0)
        location = fife.Location(self.active_map.agent_layer)
        location.setMapCoordinates(coord)
        agent.teleport(location)         
               
    def getObjectAtCoords(self, coords):
        """Get the object which is at the given coords
        @type coords: fife.Screenpoint
        @param coords: Coordinates where to check for an object
        @rtype: fife.Object
        @return: An object or None"""
        instances = self.active_map.cameras[
                                            self.active_map.my_cam_id].\
            getMatchingInstances(coords, self.active_map.agent_layer)
        # no object returns an empty tuple
        if(instances != ()):
            front_y = 0
            

            for obj in instances:
                # check to see if this in our list at all
                if(self.objectActive(obj.getId())):
                    # check if the object is on the foreground
                    obj_map_coords = \
                                      obj.getLocation().getMapCoordinates()
                    obj_screen_coords = self.active_map.\
                        cameras[self.active_map.my_cam_id]\
                        .toScreenCoordinates(obj_map_coords)

                    if obj_screen_coords.y > front_y:
                        #Object on the foreground
                        front_y = obj_screen_coords.y
                        return obj
                    else:
                        return None
        else:
            return None

    def getCoords(self, click):
        """Get the map location x, y coordinates from the screen coordinates
           @type click: fife.ScreenPoint
           @param click: Screen coordinates
           @rtype: fife.Location
           @return: The map coordinates"""
        coord = self.active_map.cameras[self.active_map.my_cam_id].\
                    toMapCoordinates(click, False)
        coord.z = 0
        location = fife.Location(self.active_map.agent_layer)
        location.setMapCoordinates(coord)
        return location

    def pause(self, paused):
        """ Pause/Unpause the game
        @return: nothing"""
        if self.active_map:
            self.active_map.pause(paused)
    
    def togglePause(self):
        """ Toggle paused state.
        @return: nothing"""
        self.active_map.togglePause()
        
    def isPaused(self):
        """Returns wheter the game is paused or not"""
        return self.active_map.isPaused()
    
    def readMapFiles(self):
        """Read all a available map-files and store them"""
        maps_file = vfs.VFS.open(self.game_state.maps_file)
        self.map_files = yaml.load(maps_file)["Maps"]
    
    def addAgent(self, namespace, agent):
        """Adds an agent to the agents dictionary
        @param namespace: the namespace where the agent is to be added to
        @type namespace: str
        @param agent: The agent to be added
        @type agent: dict """
        from fife.extensions.serializers.xml_loader_tools import loadImportFile
        if not self.agents.has_key(namespace):
            self.agents[namespace] = {}
            
        agent_values = agent.values()[0]
        unique_agent_id = self.createUniqueID(agent.keys()[0])
        del agent[agent.keys()[0]]
        agent[unique_agent_id] = agent_values
        self.agents[namespace].update(agent)
        object_model = ""
        if agent_values["Entity"].has_key("graphics") \
           and agent_values["Entity"]["graphics"].has_key("gfx"): 
            object_model = agent_values["Entity"]["graphics"]["gfx"]
        elif agent_values.has_key("Template"):
            template = self.object_db[agent_values["Template"]]
            object_model = template["graphics"]["gfx"]
        else:
            object_model = self.GENERIC_ITEM_GFX
        import_file = self.agent_import_files[object_model]
        loadImportFile(self.obj_loader, import_file, self.engine)
        
    def readAgentsOfMap(self, map_name):
        """Read the agents of the map
        @param map_name: Name of the map
        @type map_name: str """
        #Get the agents of the map
        map_agents_file = self.map_files[map_name].\
                            replace(".xml", "_agents.yaml")   
        agents_data = vfs.VFS.open(map_agents_file)
        agents = yaml.load_all(agents_data)
        self.agents[map_name] = {}
        for agent in agents:
            if not agent == None:
                self.addAgent(map_name, agent)  
        
    def readScriptsOfMap(self, map_name, world):
        """Read the scripts of the map
        @param map_name: Name of the map
        @type map_name: str 
        @param world: The current active world
        @type world: parpg.world.World"""
        map_scripts_file = (
            self.map_files[map_name].replace(".xml", "_scripts.yaml")
        )
        if vfs.VFS.exists(map_scripts_file):
            scripts_file = vfs.VFS.open(map_scripts_file)
            scripts_data = yaml.load(scripts_file)
            scripts = (scripts_data["Scripts"])
            conditions = (
                scripts_data["Conditions"] if 
                scripts_data.has_key("Conditions") else ()
            )
            scripting = world.systems.scripting
            for name, actions in scripts.iteritems():
                scripting.setScript(name, actions)
            for condition in conditions:
                scripting.addCondition(*condition)            
            
    def readAllAgents(self):
        """Read the agents of the all_agents_file and store them"""
        agents_file = vfs.VFS.open(self.all_agents_file)
        agents = yaml.load_all(agents_file)
        for agent in agents:
            if agent is not None:
                self.addAgent(self.ALL_AGENTS_KEY, agent)  
                
    def getAgentsOfMap(self, map_name):
        """Returns the agents that are on the given map
        @param map_name: Name of the map
        @type map_name: str
        @return: A dictionary with the agents of the map"""
        if not self.agents.has_key(map_name):
            return {}
        ret_dict = self.agents[map_name].copy()
        for agent_name, agent_value in self.agents[self.ALL_AGENTS_KEY]\
                                                .iteritems():
            if agent_value["Map"] == map_name:
                ret_dict[agent_name] = agent_value
        return ret_dict
                
    def getAgentsOfActiveMap(self):
        """Returns the agents that are on active map
        @return: A dictionary with the agents of the map """
        return self.getAgentsOfMap(self.active_map.map.getId())

    def clearAgents(self):
        """Resets the agents dictionary"""
        self.agents = {}
        self.agents[self.ALL_AGENTS_KEY] = {}
    
    def loadMap(self, map_name):
        """Load a new map.
           @type map_name: string
           @param map_name: Name of the map to load
           @return: None"""
        if not map_name in self.game_state.maps:  
            map_file = self.map_files[map_name]
            new_map = GameMap(self.engine, self)
            self.game_state.maps[map_name] = new_map
            new_map.load(map_file)    

    def createAgent(self, agent, inst_id, world):
        if self.game_state.hasObject(inst_id):
            return None
        entity_data = deepcopy(agent["Entity"])
        entity_data["fifeagent"] = {}
        template = None
        if agent.has_key("Template"):
            template = agent["Template"]
            entity_data = self.checkAttributes(entity_data, template)
        object_id = (entity_data["graphics"]["gfx"] 
                     if entity_data.has_key("graphics") and 
                     entity_data["graphics"].has_key("gfx") 
                     else self.GENERIC_ITEM_GFX
                     )
        map_obj = self.fife_model.getObject(str(object_id), "PARPG")
        if not map_obj:
            logging.warning("Object with inst_id={0}, ns=PARPG, "
                                  "could not be found. "
                                  "Omitting...".format(str(object_id)))

        x_pos = agent["Position"][0]
        y_pos = agent["Position"][1]
        z_pos = agent["Position"][2] if len(agent["Position"]) == 3 \
                                        else 0.0  
        stack_pos = agent["Stackposition"] if \
                        agent.has_key("StackPosition") \
                        else None
        inst = self.active_map.agent_layer.\
                        createInstance(map_obj,
                                       fife.ExactModelCoordinate(x_pos, 
                                                                 y_pos, 
                                                                 z_pos),
                                       inst_id)
        inst.setId(inst_id)

        rotation = agent["Rotation"]
        inst.setRotation(rotation)

        fife.InstanceVisual.create(inst)
        if (stack_pos):
            inst.get2dGfxVisual().setStackPosition(int(stack_pos))

        if (map_obj.getAction('default')):
            target = fife.Location(self.active_map.agent_layer)
            inst.act('default', target, True)        

        if entity_data.has_key("behaviour"):
            entity_data["fifeagent"]["behaviour"] = \
                getattr(behaviours, 
                        entity_data["behaviour"]["behaviour_type"])()
        else:
            entity_data["fifeagent"]["behaviour"] = behaviours.Base()
        if self.dialogues.has_key(inst_id):
            entity_data["dialogue"] = {}
            entity_data["dialogue"]["dialogue"] = self.dialogues[inst_id]
        if (entity_data.has_key("containable") and not 
            entity_data["containable"].has_key("item_type")
            ):
            entity_data["containable"]["item_type"] = template          
                      
        obj = self.createMapObject(self.active_map.agent_layer, 
                                   entity_data, inst_id, world)

        if agent.has_key("Statistics"):
            self.create_stats(obj)
            for name, val in agent["Statistics"].iteritems():
                obj.characterstats.primary_stats[name].value = val

        if agent.has_key("Inventory"):
            inv = agent["Inventory"]
            self.createInventoryItems(inv, obj, world)

        if agent.has_key("Equipment"):
            for slot, data in agent["Equipment"].iteritems():
                item = None
                if data.has_key("type"):
                    item_type = data["type"]
                    item_data = {}
                    item_data = self.checkAttributes(item_data, item_type)
                    if (item_data.has_key("containable") and 
                        item_data.has_key("equipable")):
                        item = self.createItem(
                            self.createUniqueID(data["ID"]), 
                            item_data, world, item_type)
                    else:
                        raise Exception(
                            "Item %s is not containable or equipable." % 
                            item_type
                        )
                else:
                    identifier = data["ID"]
                    if self.game_state.hasObject(identifier):
                        item = self.game_state.getObjectById(identifier)
                    else:
                        item_data = self.items[identifier]["Entity"]
                        item_type = item_data["containable"]["item_type"]
                        item = self.createItem(identifier, item_data,
                                                world, item_type)
                equip.equip(obj.equip, item.equipable, slot)
        if (obj.fifeagent and (obj.lockable and not obj.lockable.closed)):
            obj.fifeagent.behaviour.animate("opened", repeating=True)
        return obj

    def createInventoryItems(self, inv, obj, world):
        slots = inv["Slots"]
        obj.container.children = list()
        for x in xrange(slots):
            obj.container.children.append(None)
        items = inv["Items"] if inv.has_key("Items") else list()
        for data in items:
            item = None
            slot = data["Slot"] if data.has_key("Slot") else -1
            if data.has_key("type"):
                item_type = data["type"]
                item = self.createItemByType(item_type, data["ID"], world)
            else:
                identifier = data["ID"]
                item = self.createItemByID(world, identifier)
                    
            container.put_item(obj.container, item.containable, slot)

    def createItemByID(self, world, identifier):
        if self.game_state.hasObject(identifier):
            item = self.game_state.getObjectById(identifier)
        else:
            agent_data = self.items[identifier]
            item_data = agent_data["Entity"]
            item_type = item_data["containable"]["item_type"]
            item = self.createItem(identifier, item_data,
                                    world, item_type)
            if item.container and agent_data.has_key("Inventory"):
                self.createInventoryItems(agent_data["Inventory"],
                                            item, world)
        return item

    def createItemByType(self, item_type, identifier, world):
        item_data = {}
        item_data = self.checkAttributes(item_data, item_type)
        if item_data.has_key("containable"):
            return self.createItem( self.createUniqueID(identifier), 
                                    item_data, world, item_type)
        else:
            raise Exception("Item %s is not containable." % item_type)

    def createItem(self, identifier, item_data, world, item_type):
        if not item_data["description"].has_key("view_name"):
            item_data["description"]["view_name"] = (
             item_data["description"]["real_name"])
        item = createEntity(item_data, identifier, world, None)
        item.containable.item_type = item_type
        self.game_state.addObject(identifier, None, item)
        self.updateObjectDB(world)
        return item

    def placeAgents(self, world):
        """Places the current maps agents """
        if not self.active_map:
            return
        agents = self.getAgentsOfMap(self.game_state.current_map_name)
        for agent in agents:
            if agent == "PlayerCharacter":
                continue
            if self.active_map.agent_layer.getInstances(agent):
                continue
            self.createAgent(agents[agent], agent, world)

    def placePC(self, world):
        """Places the PlayerCharacter on the map"""
        agent = self.agents[self.ALL_AGENTS_KEY]["PlayerCharacter"]
        inst_id = "PlayerCharacter"
        self.createAgent(agent, inst_id, world)
        
        # create the PlayerCharacter agent
        self.active_map.addPC()
        #self.game_state.getObjectById("PlayerCharacter").fifeagent.start()
        if agent.has_key("PeopleKnown"):
            player = self.game_state.getObjectById("PlayerCharacter")
            player.fifeagent.people_i_know = agent["PeopleKnown"]
                      
    def changeMap(self, map_name, target_position = None):
        """Registers for a map change on the next pump().
           @type map_name: String
           @param map_name: Id of the map to teleport to
           @type map_file: String
           @param map_file: Filename of the map to teleport to
           @type target_position: Tuple
           @param target_position: Position of PlayerCharacter on target map.
           @return None"""
        # set the parameters for the map change if moving to a new map
        if map_name != self.game_state.current_map_name:
            self.target_map_name = map_name
            self.target_position = target_position
            # issue the map change
            self.map_change = True

    def deleteMaps(self):
        """Clear all currently loaded maps from FIFE as well as clear our
            local map cache
            @return: nothing"""
        self.engine.getModel().deleteMaps()
        self.engine.getModel().deleteObjects()
        self.game_state.clearObjects()
        self.game_state.maps = {}
        
    def setActiveMap(self, map_name, world):
        """Sets the active map that is to be rendered.
           @type map_name: String
           @param map_name: The name of the map to load
           @param world: The active world
           @type world: parpg.world.World
           @return: None"""
        # Turn off the camera on the old map before we turn on the camera
        # on the new map.
        self.active_map.cameras[self.active_map.my_cam_id].setEnabled(False)
        # Make the new map active.
        self.active_map = self.game_state.maps[map_name]
        self.active_map.makeActive()
        self.game_state.current_map_name = map_name
        if not self.agents.has_key(map_name):
            self.readAgentsOfMap(map_name)

    def createMapObject (self, layer, attributes, inst_id, world):
        """Create an object and add it to the current map.
           @type layer: fife.Layer
           @param layer: FIFE layer object exists in
           @type attributes: Dictionary
           @param attributes: Dictionary of all object attributes
           @type instance: fife.Instance
           @param instance: FIFE instance corresponding to the object
           @return: The created object"""
        # create the extra data
        extra = {}
        if layer is not None:
            extra['fifeagent'] = {}
            extra['fifeagent']['layer'] = layer
        
        obj = createEntity(attributes, inst_id, world, extra)
        if obj:
            self.addObject(layer, obj)
        return obj

    def addPC(self, layer, player_char):
        """Add the PlayerCharacter to the map
           @type layer: fife.Layer
           @param layer: FIFE layer object exists in
           @type player_char: PlayerCharacter
           @param player_char: PlayerCharacter object
           @type instance: fife.Instance
           @param instance: FIFE instance of PlayerCharacter
           @return: None"""
        # For now we copy the PlayerCharacter, 
        # in the future we will need to copy
        # PlayerCharacter specifics between the different PlayerCharacter's
        player = self.game_state.getObjectById("PlayerCharacter")
        player.fifeagent = player_char
        player.fifeagent.setup()        
        player.fifeagent.behaviour.speed = self.settings.parpg.PCSpeed


    def addObject(self, layer, obj):
        """Adds an object to the map.
           @type layer: fife.Layer
           @param layer: FIFE layer object exists in
           @type obj: GameObject
           @param obj: corresponding object class
           @type instance: fife.Instance
           @param instance: FIFE instance of object
           @return: None"""
        ref = self.game_state.getObjectById(obj.general.identifier,
                                            self.game_state.current_map_name) 
        if ref is None:
            # no, add it to the game state
            self.game_state.addObject(obj.general.identifier, 
                                      self.game_state.current_map_name, obj)
        else:
            # yes, use the current game state data
            obj.fifeagent.pos.X = ref.X
            obj.fifeagent.pos.Y = ref.Y
            obj.fifeagent.gfx = ref.gfx
             
        if obj.fifeagent.behaviour:
            obj.fifeagent.behaviour.parent = obj
            fifeagent.setup_behaviour(obj.fifeagent)
            obj.fifeagent.behaviour.speed = self.settings.get("parpg", "PCSpeed")
            #Start the behaviour            
            obj.fifeagent.behaviour.idle()
            # create the agent
            #obj.setup()
            #obj.behaviour.speed = self.settings.parpg.PCSpeed
            # create the PlayerCharacter agent
            #obj.start()
        #if obj.trueAttr("AnimatedContainer"):
            # create the agent
            #obj.setup()

    def objectActive(self, ident):
        """Given the objects ID, pass back the object if it is active,
           False if it doesn't exist or not displayed
           @type ident: string
           @param ident: ID of object
           @rtype: boolean
           @return: Status of result (True/False)"""
        for game_object in \
           self.game_state.getObjectsFromMap(self.game_state.current_map_name):
            if (game_object.general.identifier == ident):
                # we found a match
                return game_object
        # no match
        return False    

    def movePlayer(self, position):
        """Code called when the player should move to another location
           @type position: fife.ScreenPoint
           @param position: Screen position to move to
           @return: None"""
        player = self.game_state.getObjectById("PlayerCharacter")
        if(self.pc_run == 1):
            player.fifeagent.behaviour.run(position)
        else:
            player.fifeagent.behaviour.walk(position)
        
    def teleportAgent(self, agent, position):
        """Code called when an agent should teleport to another location
           @type position: fife.ScreenPoint
           @param position: Screen position to teleport to
           @return: None"""
        agent.teleport(position)
        self.agents[agent.ID]["Position"] = position

    def readObjectDB(self):
        """Reads the Object Information Database from a file. """
        database_file = vfs.VFS.open(self.object_db_file)
        database = yaml.load_all(database_file)
        for object_info in database:
            self.object_db.update(object_info)

    def updateObjectDB(self, world):
        """Updates the values in the object database with the worlds values"""
        
        all_agents = self.agents[self.ALL_AGENTS_KEY]
        for entity in world.entities:
            identifier = entity.general.identifier
            agent_data = {}
            map_id = self.game_state.getMapOfObject(identifier)
            if map_id:
                if all_agents.has_key(identifier):
                    agent_data = self.agents[self.ALL_AGENTS_KEY][identifier]
                else:
                    agent_data = self.agents[map_id][identifier]

            else:
                if not self.items.has_key(identifier):
                    self.items[identifier] = {}
                agent_data = self.items[identifier]
            entity_data = {}
            entity_data["general"] = {"identifier": identifier}
            for name, component in components.components.iteritems():
                if getattr(entity, name):
                    comp_data = {}
                    comp_vals = getattr(entity, name)
                    #Items that are in containers will be saved with them.
                    for field in component.saveable_fields:
                        try:
                            comp_data[field] = getattr(comp_vals, field)
                        except AttributeError:                            
                            #The entity doesn't have this specific value,
                            #ignore it
                            pass
                    if comp_data:
                        entity_data[name] = comp_data
                    if name == "fifeagent":
                        if entity.fifeagent.layer:
                            layer = entity.fifeagent.layer
                            inst = layer.getInstance(identifier)
                            loc = inst.getLocation().getExactLayerCoordinates()
                            agent_data["Position"] = (loc.x, loc.y, loc.z)
                            if all_agents.has_key(identifier):
                                agent_data["Map"] = map_id
                            agent_data["Rotation"]  = inst.getRotation()
                    elif name == "characterstats":
                        agent_data["Statistics"] = (
                            character_statistics.get_stat_values(
                                entity.characterstats
                            )["primary"]
                        )
                    elif name == "container" and hasattr(comp_vals, 
                                                         "children"):
                        inventory_data = {}
                        inventory_data["Slots"] = len(comp_vals.children)
                        items = []
                        for child in comp_vals.children:
                            if not child:
                                continue
                            items.append(
                                {"ID": child.entity.general.identifier,
                                 "Slot": child.slot}
                            )
                        inventory_data["Items"] = items
                        agent_data["Inventory"] = inventory_data
                    elif name == "equip":
                        equip_data = {}
                        for field in component.fields:
                            if(hasattr(comp_vals, field)):
                                equipable = getattr(comp_vals, field)
                                if equipable:
                                    equip_data[field] = {
                                        "ID": 
                                         equipable.entity.general.identifier
                                    }
                        agent_data["Equipment"] = equip_data
            agent_data["Entity"] = entity_data           
        
    def getAgentImportFiles(self):
        """Searches the agents directory for import files """
        filepaths = locateFiles("*.xml", self.objects_directory)
        for filepath in filepaths:
            try:
                xml_file = vfs.VFS.open(filepath)
                root = ElementTree.parse(xml_file).getroot()
                if root.tag == "object":
                    self.agent_import_files[root.attrib["id"]] = filepath
            except SyntaxError as error:
                logging.error("Error parsing file {0}: {1}".format(filepath,
                                                                   error))
    
    def getDialogues(self):
        """Searches the dialogue directory for dialogues """
        files = locateFiles("*.yaml", self.dialogue_directory)
        dialogue_parser = YamlDialogueParser()
        for dialogue_filepath in files:
            # Note Technomage 2010-11-13: the new DialogueEngine uses its own
            #     parser now, YamlDialogueParser.
#            dialogues = yaml.load_all(file(dialogue_file, "r"))
            dialogue_file = vfs.VFS.open(dialogue_filepath)
            try:
                dialogue = dialogue_parser.load(dialogue_file)
            except DialogueFormatError as error:
                logging.error('unable to load dialogue file {0}: {1}'
                              .format(dialogue_filepath, error))
            else:
                self.dialogues[dialogue.npc_name] = dialogue
            # Note Technomage 2010-11-13: the below code is used to load
            #     multiple dialogues from a single file. Is this functionality
            #     used/necessary?
#            for dialogue in dialogues:
#                self.dialogues[dialogue["NPC"]] = dialogue
