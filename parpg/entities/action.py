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

#exceptions

import logging

logger = logging.getLogger('action')

from parpg.gui import drag_drop_data as data_drag
from parpg.dialoguecontroller import DialogueController
from parpg.components import container, lockable


class NoSuchQuestException(Exception):
    """NoQuestException is used when there is no active quest with the id"""
    pass

#classes

class Action(object):
    """Base Action class, to define the structure"""


    def __init__(self, controller, commands = None):
        """Basic action constructor
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        """
        self.commands = commands or ()
        self.controller = controller
        self.model = controller.model
        self.executed = False
    
    def execute(self):
        """To be overwritten"""        
        #Check if there are special commands and execute them
        for command_data in self.commands:
            command = command_data["Command"]
            if command == "SetQuestVariable":
                quest_id = command_data["ID"]
                variable = command_data["Variable"]
                value = command_data["Value"]
                quest_engine = self.model.game_state.quest_engine 
                if quest_engine.hasQuest(quest_id):
                    quest_engine[quest_id].setValue(variable, value)
                else:
                    raise NoSuchQuestException
            elif command == "ResetMouseCursor":
                self.controller.resetMouseCursor()
            elif command == "StopDragging":
                data_drag.dragging = False
        self.executed = True
                
class ChangeMapAction(Action):
    """A change map scheduled"""
    def __init__(self, controller, target_map_name, target_pos, commands=None):
        """Initiates a change of the position of the character
        possibly flagging a new map to be loaded.
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        @type view: class derived from parpg.ViewBase
        @param view: The view
        @type target_map_name: String
        @param target_map_name: Target map id 
        @type target_pos: Tuple
        @param target_pos: (X, Y) coordinates on the target map.
        @return: None"""
        super(ChangeMapAction, self).__init__(controller, commands)
        self.view = controller.view
        self.target_pos = target_pos
        self.target_map_name = target_map_name

    def execute(self):
        """Executes the map change."""
        self.model.changeMap(self.target_map_name,
                              self.target_pos)
        super(ChangeMapAction, self).execute()

class OpenAction(Action):
    """Open an lockable"""
    def __init__(self, controller, lockable, commands=None):
        """
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        @type view: class derived from parpg.ViewBase
        @param view: The view
        @param lockable: A reference to the lockable
        """
        Action.__init__(self, controller, commands)
        self.view = controller.view
        self.lockable = lockable
    
    def execute(self):
        """Open the lockable."""
        try:
            lockable.open(self.lockable.lockable)
            self.lockable.fifeagent.behaviour.animate("open")
            self.lockable.fifeagent.behaviour.queue_animation("opened", 
                                                              repeating=True)
        except lockable.LockedError:
            self.view.hud.createExamineBox(self.lockable.description.view_name,
                                           "Locked")            
        Action.execute(self)

class CloseAction(Action):
    """Close an lockable"""
    def __init__(self, controller, lockable, commands=None):
        """
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        @type view: class derived from parpg.ViewBase
        @param view: The view
        @param lockable: A reference to the lockable
        """
        Action.__init__(self, controller, commands)
        self.lockable = lockable
    
    def execute(self):
        """Close the lockable."""
        lockable.close(self.lockable.lockable)
        self.lockable.fifeagent.behaviour.animate("close")
        self.lockable.fifeagent.behaviour.queue_animation("closed", 
                                                          repeating=True)
        Action.execute(self)
        
class UnlockAction(Action):
    """Unlocks a lockable."""
    def __init__(self, controller, lockable, commands = None):
        """
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        @param lockable: A reference to the lockable
        """
        Action.__init__(self, controller, commands)
        self.lockable = lockable
    
    def execute(self):
        """Open the box."""
        lockable.unlock(self.lockable.lockable)
        Action.execute(self)
        
class LockAction(Action):
    """Locks a lockable."""
    def __init__(self, controller, lockable, commands = None):
        """
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        @param lockable: A reference to the lockable
        """
        Action.__init__(self, controller, commands)
        self.lockable = lockable
        self.view = controller.view
        
    def execute(self):
        """Lock the box."""
        try:
            lockable.lock(self.lockable.lockable)
        except lockable.OpenError:
            self.view.hud.createExamineBox(self.lockable.description.view_name,
                                           "Is open")            
            
        Action.execute(self)


class ExamineAction(Action):
    """Examine an object."""
    def __init__(self, controller, examine_id, examine_name, examine_desc=None, commands=None):
        """
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param examine_id: An object id
        @type examine_id: integer
        @param examine_name: An object name
        @type examine_name: string
        @param examine_desc: A description of the object that will be displayed.
        @type examine_desc: string
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        """
        super(ExamineAction, self).__init__(controller, commands)
        self.view = controller.view
        self.examine_id = examine_id
        self.examine_name = examine_name
        if examine_desc is not None:
            self.examine_desc = examine_desc
        else:
            self.examine_desc = "No Description"
        
    def execute(self):
        """Display the text."""
        action_text = self.examine_desc
        self.view.hud.addAction(unicode(action_text))
        logger.debug(action_text)
        #this code will cut the line up into smaller lines that will be displayed
        place = 25
        while place < len(action_text):
            if action_text[place] == ' ':
                action_text = action_text[:place] +'\n'+action_text[place:]
                place += 26 #plus 1 character to offset the new line
            else: place += 1
        self.view.displayObjectText(self.examine_id, unicode(action_text), time=3000)
        Action.execute(self)

class ExamineItemAction(Action):
    """Examine an item."""
    def __init__(self, controller, examine_name, examine_desc, commands = None):
        """
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        @type view: class derived from parpg.ViewBase
        @param view: The view
        @type examine_name: String
        @param examine_name: Name of the object to be examined.
        @type examine_name: String
        @param examine_name: Description of the object to be examined.
        """
        super(ExamineItemAction, self).__init__(controller, commands)
        self.view = controller.view
        self.examine_name = examine_name
        self.examine_desc = examine_desc
        
    def execute(self):
        """Display the text."""
        action_text = unicode(self.examine_desc)
        self.view.hud.addAction(action_text)
        logger.debug(action_text)
        Action.execute(self)

class ExamineContentsAction(Action):
    """Examine the contens of an container"""
    def __init__(self, controller, container, commands=None):
        """
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param container: The container
        @type container: parpg.entities.General
        @param commands: Special commands that are executed
        @type commands: Dictionary         
        """
        Action.__init__(self, controller, commands)
        self.view = controller.view
        self.container = container
        
    def execute(self):
        """Examine the contents"""
        self.view.hud.createBoxGUI(self.container.description.view_name,
                                   self.container.container)
        Action.execute(self)

class ReadAction(Action):
    """Read a text."""
    def __init__(self, controller, text_name, text, commands = None):
        """
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        @param view: The view
        @type view: class derived from parpg.ViewBase
        @param text_name: Name of the object containing the text
        @type text_name: String
        @param text: Text to be displayied
        @type text: String
        """
        super(ReadAction, self).__init__(controller, commands)
        self.view = controller.view
        self.text_name = text_name
        self.text = text
        
    def execute(self):
        """Examine the box."""
        action_text = unicode('\n'.join(["You read " + self.text_name + ".", 
                                         self.text]))
        self.view.hud.addAction(action_text)
        logger.debug(action_text)
        super(ReadAction, self).execute()

class TalkAction(Action):
    """An action to represent starting a dialogue"""
    def __init__(self, controller, npc, commands = None):
        """
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        @type view: class derived from parpg.ViewBase
        @param view: The view
        @type npc: NonPlayerCharacter
        @param npc: NPC to interact with.
        """
        super(TalkAction, self).__init__(controller, commands)
        self.view = controller.view
        self.npc = npc
        
    def execute(self):
        """Talk with the NPC when close enough, otherwise move closer.
           @return: None"""
        player_char = self.model.game_state.\
                    getObjectById("PlayerCharacter").fifeagent
        player_char.behaviour.animate(
            'stand', 
            self.npc.fifeagent.behaviour.getLocation()
        )

        if self.npc.dialogue.dialogue is not None:
            dialogue_controller = DialogueController(
                self.controller.engine,
                self.view,
                self.model,
                self.controller.application
            )
            self.controller.application.manager.push_mode(
                dialogue_controller
            )
            dialogue_controller.startTalk(self.npc)
        else:
            self.npc.fifeagent.behaviour.agent.say("Leave me alone!", 1000)
            
        self.model.game_state.getObjectById("PlayerCharacter").\
            fifeagent.behaviour.idle()
        self.model.game_state.getObjectById("PlayerCharacter").\
            fifeagent.behaviour.nextAction = None
        super(TalkAction, self).execute()

class UseAction(Action):
    """Action for carryable items. It executes special commands that can be only
    used on carryable utens"""


    def __init__(self, controller, item, commands = None):
        """
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param item: Item on which the action is called
        @type item: CarryableItem
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        """
        super(UseAction, self).__init__(controller, commands)
        self.view = controller.view
        self.item = item
    
    def execute(self):
        #Check if there are special commands and execute them
        for command_data in self.commands:
            command = command_data["Command"]
            if command == "ReplaceItem":
                object_id = command_data["ID"]
                object_type = command_data["ObjectType"]
                containable = self.item.containable
                new_item = self.model.createItemByType(object_type, 
                                                       object_id, 
                                                       self.item.world)
                container.put_item(containable.container, 
                                   new_item.containable,
                                   containable.slot)
                self.model.deleteObject(self.item.general.identifier)
                self.item.delete()
                self.view.hud.inventory.updateImages()
        super(UseAction, self).execute()

class PickUpAction(Action):
    """Action for picking up items from a map"""

    def __init__(self, controller, item, commands = None):
        super(PickUpAction, self).__init__(controller, commands)
        self.item = item
        self.view = controller.view
        
    def execute(self):
        real_item = self.item.containable
        self.item.fifeagent = None
        player = self.model.game_state.getObjectById("PlayerCharacter")
        self.model.moveObject(self.item.general.identifier, None)
        self.model.updateObjectDB(self.item.world)
        container.put_item(player.container, real_item)
        super(PickUpAction, self).execute()

class DropItemAction(Action):
    """Action for dropping an items on a map"""
    def __init__(self, controller, item, commands = None):
        super(DropItemAction, self).__init__(controller, commands)
        self.item = item
        
    def execute(self):
        map_name = self.model.game_state.current_map_name
        identifier = self.item.entity.general.identifier
        agent_values = self.model.items[identifier]
        coords = (self.model.game_state.getObjectById("PlayerCharacter").
                  fifeagent.behaviour.getLocation().getExactLayerCoordinates()
                  )
        agent_values["Position"] = (coords.x, coords.y)
        agent_values["Rotation"] = 0
        agent_values["Map"] = map_name
        self.model.deleteObject(identifier)
        self.model.addAgent(self.model.ALL_AGENTS_KEY, 
                            {identifier: agent_values})
        self.model.placeAgents(self.item.entity.world)
        self.model.updateObjectDB(self.item.entity.world)
        super(DropItemAction, self).execute()
        
class DropItemFromContainerAction(DropItemAction):
    """Action for dropping an items from the Inventory to a map"""

    def __init__(self, controller, item, container_gui, commands = None):
        super(DropItemFromContainerAction, self).__init__(controller, item, commands)
        self.container_gui = container_gui

    def execute(self):
        super(DropItemFromContainerAction, self).execute()
        container.remove_item(self.item.container, self.item.slot)
        self.container_gui.updateImages()

class RunScriptAction(Action):
    """Action that runs a specific script"""

    def __init__(self, controller, script, commands = None):
        """Basic action constructor
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param script: The name of the script to run.
        @type script: string
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        """
        Action.__init__(self, controller, commands)
        self.script = script
    
    def execute(self):
        self.controller.systems.scripting.runScript(self.script)
        Action.execute(self)
        
class BrewBeerAction(Action):
    """Action for brewing beer in a pot"""
    def __init__(self, controller, pot, commands = None):
        super(BrewBeerAction, self).__init__(controller, commands)
        self.pot = pot.container
        self.view = controller.view
        
    def execute(self):
        """Brew the beer"""
        has_water = False
        has_yeast = False
        has_fruit = False
        has_wood = False
        has_bottle = False
        player_character = (self.model.game_state.
                            getObjectById("PlayerCharacter").container)
        for item in self.pot.children:
            if not item:
                continue
            if item.item_type == "Questionable water":
                if has_water:
                    self.view.hud.addAction(unicode(\
                        "Please put only 1 water in the pot"))
                    return
                has_water = True
                water_type = 1 
                water = item
            elif item.item_type == "Pure water":
                if has_water:
                    self.view.hud.addAction(unicode(\
                        "Please put only 1 water in the pot"))
                    return
                has_water = True
                water_type = 2
                water = item
            elif item.item_type == "Grain":
                if has_fruit:
                    self.view.hud.addAction(unicode(\
                        "Please put only 1 fruit in the pot"))
                    return
                has_fruit = True
                fruit_type = 3
                fruit = item
            elif item.item_type == "Wild potato":
                if has_fruit:
                    self.view.hud.addAction(unicode(\
                        "Please put only 1 fruit in the pot"))
                    return
                has_fruit = True
                fruit_type = 2
                fruit = item
            elif item.item_type == "Rotten yam":
                if has_fruit:
                    self.view.hud.addAction(unicode(\
                        "Please put only 1 fruit in the pot"))
                    return
                has_fruit = True
                fruit_type = 1
                fruit = item
            elif item.item_type == "Yeast":
                if has_yeast:
                    self.view.hud.addAction(unicode(\
                        "Please put only 1 yeast in the pot"))
                    return
                has_yeast = True
                yeast = item 
            else:
                self.view.hud.addAction(unicode(
                    "Item " + (item.entity.description.view_name) + 
                    " is not needed for brewing beer"))
                self.view.hud.addAction(unicode(\
                    "Please put only ingredients for the beer in the pot.\
                    Things like bottles and wood have to be in your inventory"))
                return
        wood = container.get_item(player_character, "Wood")
        if wood:
            has_wood = True        
        bottle = container.get_item(player_character, "Empty beer bottle")
        if bottle:
            has_bottle = True        
        if has_water and has_fruit and has_wood and has_bottle:
            container.remove_item(self.pot, water.slot)
            container.remove_item(self.pot, fruit.slot)
            if has_yeast:
                container.remove_item(self.pot, yeast.slot)
            container.remove_item(player_character, wood.slot)
            new_item = (self.model.createItemByType("Beer", "Beer", 
                                                    self.pot.entity.world)
                        )
            container.put_item(player_character, new_item.containable)
            self.view.hud.inventory.updateImages()
            beer_quality = 0
            if water_type == 1:
                if fruit_type == 1:
                    beer_quality = -1
                elif fruit_type == 2:
                    beer_quality = 2
                elif fruit_type == 3:
                    beer_quality = 3
            if water_type == 2:
                if fruit_type == 1:
                    beer_quality = 1
                elif fruit_type == 2:
                    beer_quality = 3
                elif fruit_type == 3:
                    beer_quality = 4
            if beer_quality > 0 and has_yeast:
                beer_quality += 1
            self.model.game_state.quest_engine.quests["beer"].\
                    setValue("beer_quality", beer_quality)
        else:
            self.view.hud.addAction(unicode(
            """For brewing beer you need at least:
            In the pot:
                Fruit (like grain, potato, yam)
                Water
                Optionally:
                    Good quality yeast.
                    Wild yeast will be used if none present.
            In the inventory:
                Wood
                Empty bottle"""))
        super(BrewBeerAction, self).execute()

class SayAction(Action):
    """Action that will display a short text over the entity and in the action
    box."""

    def __init__(self, controller, entity, text, commands = None):
        """Basic action constructor
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param entity: The entity that says the text
        @type script: parpg.entities.General
        @param text: The text to be displayed
        @type text: string
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        """
        Action.__init__(self, controller, commands)
        self.entity = entity
        self.text = text
    
    def execute(self):
        if self.entity.fifeagent:
            self.entity.fifeagent.behaviour.agent.say(self.text);
        if self.entity.description:
            self.controller.view.hud.actions_box.addDialog(
                self.entity.description.view_name,
                self.text)
        Action.execute(self)

class CodeAction(Action):
    """Executes a code inside the GameEnvironment"""
    def __init__(self, controller, code, commands=None):
        """
        @param controller: A reference to the GameSceneController.
        @type controller: parpg.GameSceneController
        @param commands: Special commands that are executed
        @type commands: Dictionary 
        @type view: class derived from parpg.ViewBase
        @param view: The view
        @param lockable: The code to execute
        """
        Action.__init__(self, controller, commands)
        self.view = controller.view
        self.code = code
    
    def execute(self):
        """Executes the code."""
        globals,  locals = self.controller.model.game_state.getGameEnvironment()
        exec self.code in globals,  locals
        Action.execute(self)

ACTIONS = {"ChangeMap":ChangeMapAction, 
           "Open":OpenAction,
           "Close":CloseAction,
           "Unlock":UnlockAction,
           "Lock":LockAction,
           "ExamineItem":ExamineItemAction,
           "Examine":ExamineAction,
           "Look":ExamineItemAction,
           "Read":ReadAction,
           "Talk":TalkAction,
           "Use":UseAction,
           "PickUp":PickUpAction,
           "DropFromInventory":DropItemFromContainerAction,
           "BrewBeer":BrewBeerAction,
           "ExamineContents": ExamineContentsAction,
           "RunScript": RunScriptAction,
           "Say" : SayAction,
           "Code": CodeAction, 
           "None": Action,
           }
