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
"""This file contains the GameSceneController that handles input when the game
   is exploring a scene"""


from datetime import datetime
import random
import glob
import os
import logging

from fife import fife
from fife import extensions
from fife.extensions import pychan

from controllerbase import ControllerBase
from parpg.gui.hud import Hud
from parpg.gui import drag_drop_data as data_drag
from entities.action import (ChangeMapAction, ExamineAction, TalkAction,
                            OpenAction, CloseAction, UnlockAction, LockAction, 
                            PickUpAction, DropItemAction, 
                            ExamineContentsAction,
                            )

from parpg.world import PARPGWorld

#For debugging/code analysis
if False:
    from gamesceneview import GameSceneView
    from gamemodel import GameModel
    from parpg import PARPGApplication


logger = logging.getLogger('gamescenecontroller')

class GameSceneController(PARPGWorld, ControllerBase):
    '''
    This controller handles inputs when the game is in "scene" state.
    "Scene" state is when the player can move around and interact
    with objects. Like, talking to a npc or examining the contents of a box. 
    '''


    def __init__(self, engine, view, model, application):
        '''
        Constructor
        @param engine: Instance of the active fife engine
        @type engine: fife.Engine
        @param view: Instance of a GameSceneView
        @param type: parpg.GameSceneView
        @param model: The model that has the current gamestate
        @type model: parpg.GameModel
        @param application: The application that created this controller
        @type application: parpg.PARPGApplication
        @param settings: The current settings of the application
        @type settings: fife.extensions.fife_settings.Setting
        '''
        ControllerBase.__init__(self,
                                engine,
                                view,
                                model,
                                application)
        PARPGWorld.__init__(self, engine)

        #setup functions for the GameEnvironment        
        createItemByID = lambda identifier : (
                self.model.createItemByID(
                                    identifier=identifier, 
                                    world=self)
            )
        createItemByType = lambda item_type, identifier: (
                self.model.createItemByType(
                                      item_type=item_type, 
                                      identifier=identifier, 
                                      world=self)
            )
        funcs = {
         "createItemByID": createItemByID, 
         "createItemByType": createItemByType, 
         }
        self.model.game_state.funcs.update(funcs)
        self.systems.scripting.game_state = self.model.game_state
        
        #this can be helpful for IDEs code analysis
        if False:
            assert(isinstance(self.engine, fife.Engine))
            assert(isinstance(self.view, GameSceneView))
            assert(isinstance(self.view, GameModel))
            assert(isinstance(self.application, PARPGApplication))
            assert(isinstance(self.event_manager, fife.EventManager))
        
        # Last saved mouse coords        
        self.action_number = 1

        self.has_mouse_focus = True
        self.last_mousecoords = None
        self.mouse_callback = None
        self.original_cursor_id = self.engine.getCursor().getId()
        self.scroll_data = {"mouse":[], "kb":[], "offset":[0,0]}
        self.scroll_timer = extensions.fife_timer.Timer(
            100,
            lambda: self.view.moveCamera(self.scroll_data["offset"]),
        )
        
        #this is temporary until we can set the native cursor
        self.resetMouseCursor()
        self.paused = False

        if model.settings.get("fife", "PlaySounds"):
            if not self.view.sounds.music_init:
                music_path = 'music'
                music_file = random.choice(
                    glob.glob('/'.join([music_path, '*.ogg']))
                )
                self.view.sounds.playMusic(music_file) 
        self.initHud()
                

    def initHud(self):
        """Initialize the hud member
        @return: None"""
        hud_callbacks = {
            'saveGame': self.saveGame,
            'loadGame': self.loadGame,
            'quitGame': self.quitGame,
        }
        self.view.hud = Hud(self, 
                            self.model.settings, 
                            hud_callbacks)

    def keyPressed(self, evt):
        """Whenever a key is pressed, fife calls this routine.
           @type evt: fife.event
           @param evt: The event that fife caught
           @return: None"""
        key = evt.getKey()
        key_val = key.getValue()

        if(key_val == key.Q):
            # we need to quit the game
            self.view.hud.quitGame()
        if(key_val == key.T):
            self.model.active_map.toggleRenderer('GridRenderer')
        if(key_val == key.F1):
            # display the help screen and pause the game
            self.view.hud.displayHelp()
        if(key_val == key.F5):
            self.model.active_map.toggleRenderer('CoordinateRenderer')
        if(key_val == key.F7):
            # F7 saves a screenshot to screenshots directory

            settings = self.model.settings
            # FIXME M. George Hansen 2011-06-06: Not sure that user_path is set
            #     correctly atm.
            screenshot_directory = os.path.join(settings.user_path,
                                                'screenshots')
            # try to create the screenshots directory
            try:
                os.mkdir(screenshot_directory)
            #TODO: distinguish between already existing permissions error
            except OSError:
                logger.warning("screenshot directory wasn't created.")

            screenshot_file = os.path.join(screenshot_directory,
                                           'screen-{0}.png'.format(
                                           datetime.now().strftime(
                                           '%Y-%m-%d-%H-%M-%S')))
            self.engine.getRenderBackend().captureScreen(screenshot_file)
            logger.info("PARPG: Saved: {0}".format(screenshot_file))
        if(key_val == key.F10):
            # F10 shows/hides the console
            pychan.manager.hook.guimanager.getConsole().toggleShowHide()
        if(key_val == key.C):
            # C opens and closes the character screen.
            self.view.hud.toggleCharacterScreen()
        if(key_val == key.I):
            # I opens and closes the inventory
            self.view.hud.toggleInventory()
        if(key_val == key.A):
            # A adds a test action to the action box
            # The test actions will follow this format: Action 1,
            # Action 2, etc.
            self.view.hud.addAction("Action " + str(self.action_number))
            self.action_number += 1
        if(key_val == key.ESCAPE):
            # Escape brings up the main menu
            self.view.hud.displayMenu()
            # Hide the quit menu
            self.view.hud.quit_window.hide()
        if(key_val == key.M):
            self.view.sounds.toggleMusic()
        if(key_val == key.PAUSE):
            # Pause pause/unpause the game 
            self.model.togglePause()
            self.pause(False)
        if(key_val == key.SPACE):
            self.model.active_map.centerCameraOnPlayer()
        
        #alter scroll data if a directional key is hit
        if(key_val == key.UP):
            if not "up" in self.scroll_data["kb"]:
                self.scroll_data["kb"].append("up")

        if(key_val == key.RIGHT):
            if not "right" in self.scroll_data["kb"]:
                self.scroll_data["kb"].append("right")
 
        if(key_val == key.DOWN): 
            if not "down" in self.scroll_data["kb"]:
                self.scroll_data["kb"].append("down")

        if(key_val == key.LEFT):
            if not "left" in self.scroll_data["kb"]:
                self.scroll_data["kb"].append("left")
    
    def keyReleased(self, evt):
        """Whenever a key is pressed, fife calls this routine.
           @type evt: fife.event
           @param evt: The event that fife caught
           @return: None"""
        key = evt.getKey()
        key_val = key.getValue()

        #alter scroll data if a directional key is released
        if(key_val == key.UP):
            if "up" in self.scroll_data["kb"]:
                self.scroll_data["kb"].remove("up")

        if(key_val == key.RIGHT):
            if "right" in self.scroll_data["kb"]:
                self.scroll_data["kb"].remove("right")
 
        if(key_val == key.DOWN): 
            if "down" in self.scroll_data["kb"]:
                self.scroll_data["kb"].remove("down")

        if(key_val == key.LEFT):
            if "left" in self.scroll_data["kb"]:
                self.scroll_data["kb"].remove("left")
        
    def mouseReleased(self, evt):
        """If a mouse button is released, fife calls this routine.
           We want to wait until the button is released, because otherwise
           pychan captures the release if a menu is opened.
           @type evt: fife.event
           @param evt: The event that fife caught
           @return: None"""
        self.view.hud.hideContextMenu()
        scr_point = fife.ScreenPoint(evt.getX(), evt.getY())
        if(evt.getButton() == fife.MouseEvent.LEFT):
            if(data_drag.dragging):
                coord = self.model.getCoords(scr_point)\
                                    .getExactLayerCoordinates()
                commands = ({"Command": "ResetMouseCursor"}, 
                            {"Command": "StopDragging"})
                player_char = (self.model.game_state.
                               getObjectById("PlayerCharacter"))
                action =  DropItemAction(self, 
                                         data_drag.dragged_item, 
                                         commands)
                player_char.fifeagent.behaviour.approach([coord.x, coord.y], 
                                                         action)
            else:
                self.model.movePlayer(self.model.getCoords(scr_point))
        elif(evt.getButton() == fife.MouseEvent.RIGHT):
            # is there an object here?
            tmp_active_map = self.model.active_map
            instances = tmp_active_map.cameras[tmp_active_map.my_cam_id].\
                            getMatchingInstances(scr_point,
                                                 tmp_active_map.agent_layer)
            info = None
            for inst in instances:
                # check to see if this is an active item
                if(self.model.objectActive(inst.getId())):
                    # yes, get the model
                    info = self.getItemActions(inst.getId())
                    break

            # take the menu items returned by the engine or show a
            # default menu if no items
            data = info or \
                [["Walk", "Walk here", self.view.onWalk, 
                  self.model.getCoords(scr_point)]]
            # show the menu
            self.view.hud.showContextMenu(data, (scr_point.x, scr_point.y))
    
        
    def updateMouse(self):
        """Updates the mouse values"""
        if self.paused:
            return
        cursor = self.engine.getCursor()
        #this can be helpful for IDEs code analysis
        if False:
            assert(isinstance(cursor, fife.Cursor))
        self.last_mousecoords = fife.ScreenPoint(cursor.getX(), cursor.getY())
        self.view.highlightFrontObject(self.last_mousecoords)
        
        #set the trigger area in pixles
        pixle_edge = 20
        
        mouse_x = self.last_mousecoords.x
        screen_width = self.model.engine.getSettings().getScreenWidth()
        mouse_y = self.last_mousecoords.y
        screen_height = self.model.engine.getSettings().getScreenHeight()
        
        image = None
        settings = self.model.settings
        
        
        #edge logic
        if self.has_mouse_focus:
            direction = self.scroll_data["mouse"] = []
            
            #up
            if mouse_y <= pixle_edge:
                direction.append("up")
                image = '/'.join(['gui/cursors', settings.get("parpg", "CursorUp")])
                
            #right
            if mouse_x >= screen_width - pixle_edge:
                direction.append("right")
                image = '/'.join(['gui/cursors', settings.get("parpg", "CursorRight")])
                
            #down
            if mouse_y >= screen_height - pixle_edge:
                direction.append("down")
                image = '/'.join(['gui/cursors', settings.get("parpg", "CursorDown")])
                
            #left
            if mouse_x <= pixle_edge:
                direction.append("left")
                image = '/'.join(['gui/cursors', settings.get("parpg", "CursorLeft")])
                
            if image is not None and not data_drag.dragging:
                self.setMouseCursor(image, image)
       

    def handleCommands(self):
        """Check if a command is to be executed
        """
        if self.model.map_change:
            self.pause(True)
            if self.model.active_map:
                self.model.updateObjectDB(self)
                player_char = self.model.game_state.\
                    getObjectById("PlayerCharacter").fifeagent
                pc_agent = self.model.agents\
                    [self.model.ALL_AGENTS_KEY]["PlayerCharacter"]
                pc_agent["Map"] = self.model.target_map_name 
                pc_agent["Position"] = (self.model.target_position or 
                                        pc_agent["Position"])
                player_agent = self.model.active_map.\
                                    agent_layer.getInstance("PlayerCharacter")
                self.model.game_state.deleteObject("PlayerCharacter").delete()
                deleted = self.model.game_state.deleteObjectsFromMap(
                    self.model.game_state.current_map_name
                )
                deleted.extend(
                    self.model.game_state.deleteObjectsFromMap(None)
                )
                for obj in deleted:
                    obj.delete()
            self.model.loadMap(self.model.target_map_name)
            self.setupScripts(self.model.target_map_name)
            
            self.model.setActiveMap(self.model.target_map_name, self)          
            
            self.model.placeAgents(self)
            self.model.placePC(self)
            self.model.updateObjectDB(self)
            self.model.map_change = False
            # The PlayerCharacter has an inventory, and also some 
            # filling of the ready slots in the HUD. 
            # At this point we sync the contents of the ready slots 
            # with the contents of the inventory.
            self.view.hud.inventory = None
            self.view.hud.initializeInventory()         
            self.pause(False)

    def setupScripts(self, map_name):
        """Read scripts for the current map"""
        self.systems.scripting.reset()
        self.model.readScriptsOfMap(map_name, self)

    def handleScrolling(self):
        """
        Merge kb and mouse related scroll data, limit the speed and
        move the camera.
        """
        #this is how many pxls the camera is moved in one time frame
        scroll_offset = self.scroll_data["offset"] = [0,0]
 
        mouse = self.scroll_data["mouse"]
        keyboard = self.scroll_data["kb"]
        speed = self.model.settings.get("parpg", "ScrollSpeed")

        #adds a value to the offset depending on the contents of each
        #  of the controllers: set() removes doubles
        scroll_direction = set(mouse+keyboard)
        for direction in scroll_direction:
            if direction == "up":
                scroll_offset[0] +=1
                scroll_offset[1] -=1
            elif direction == "right":
                scroll_offset[0] +=1
                scroll_offset[1] +=1
            elif direction == "down":
                scroll_offset[0] -=1
                scroll_offset[1] +=1
            elif direction == "left":
                scroll_offset[0] -=1
                scroll_offset[1] -=1

        #keep the speed within bounds
        if scroll_offset[0] > 0: scroll_offset[0] = speed
        if scroll_offset[0] < 0: scroll_offset[0] = -speed
        
        if scroll_offset[1] > 0: scroll_offset[1] = speed
        if scroll_offset[1] < 0: scroll_offset[1] = -speed
        
        #de/activate scrolling
        if scroll_offset != [0, 0]:
            self.scroll_timer.start()
        else: 
            self.scroll_timer.stop()
            if not data_drag.dragging:
                self.resetMouseCursor()

    def nullFunc(self, userdata):
        """Sample callback for the context menus."""
        logger.info(userdata)

    def initTalk(self, npc_info):
        """ Starts the PlayerCharacter talking to an NPC. """
        # TODO: work more on this when we get NPCData and HeroData straightened
        # out
        npc = self.model.game_state.getObjectById(
            npc_info.general.identifier, 
            self.model.game_state.current_map_name
        )
        npc_behaviour = npc.fifeagent.behaviour
        npc_pos = npc_behaviour.getLocation().getLayerCoordinates()
        self.model.game_state.getObjectById("PlayerCharacter").fifeagent.\
            behaviour.approach(npc_behaviour.agent,
                               TalkAction(self, npc))

    def getItemActions(self, obj_id):
        """Given the objects ID, return the text strings and callbacks.
           @type obj_id: string
           @param obj_id: ID of object
           @rtype: list
           @return: List of text and callbacks"""
        actions = []
        obj = self.model.game_state.\
                        getObjectById(obj_id,
                                      self.model.game_state.current_map_name)
        #obj_pos = obj.fifeagent.behaviour.getLocation().getLayerCoordinates()
        agent = obj.fifeagent.behaviour.agent
        player = self.model.game_state.getObjectById("PlayerCharacter")
        is_player = obj.general.identifier == player.general.identifier
        
        
        #TODO: Check all actions to be compatible with the grease components
        if obj is not None:
            if obj.dialogue and not is_player:
                actions.append(["Talk", "Talk", self.initTalk, obj])
            if obj.characterstats and not is_player:
                actions.append(["Attack", "Attack", self.nullFunc, obj])
            if obj.description and obj.description.desc:
                actions.append(["Examine", "Examine",
                                player.fifeagent.behaviour.approach, 
                                agent,
                                ExamineAction(self, 
                                              obj_id, obj.description.view_name, 
                                              obj.description.desc)])

            if obj.change_map:
                actions.append(["Change Map", "Change Map",
                   player.fifeagent.behaviour.approach, 
                   agent,
                   ChangeMapAction(self, obj.change_map.target_map,
                                   obj.change_map.target_position)])
            
            if obj.lockable:
                if obj.lockable.closed:
                    if not obj.lockable.locked:
                        actions.append(["Open", "Open", 
                                        player.fifeagent.behaviour.approach,
                                        agent,
                                        OpenAction(self, obj)])
                else:
                    actions.append(["Close", "Close", 
                                    player.fifeagent.behaviour.approach,
                                    agent,
                                    CloseAction(self, obj)])
                if obj.lockable.locked:
                    actions.append(["Unlock", "Unlock", 
                                    player.fifeagent.behaviour.approach,
                                    agent,
                                    UnlockAction(self, obj)])
                else:
                    if obj.lockable.closed:
                        actions.append(["Lock", "Lock", 
                                        player.fifeagent.behaviour.approach,
                                        agent,
                                        LockAction(self, obj)])
            if obj.container:
                if obj.characterstats:
                    #TODO: This is reserved for a possible "Steal" action.
                    pass                
                elif not obj.lockable or not obj.lockable.closed:
                    actions.append(["Examine contents", "Examine Contents",
                                    player.fifeagent.behaviour.approach,
                                    agent,
                                    ExamineContentsAction(self, obj)])
            if obj.containable:
                actions.append(["Pick Up", "Pick Up", 
                                player.fifeagent.behaviour.approach,
                                agent,
                                PickUpAction(self, obj)])

        return actions
    
    def saveGame(self, *args, **kwargs):
        """Saves the game state, delegates call to gamemodel.GameModel
           @return: None"""
        self.model.pause(False)
        self.pause(False)
        self.view.hud.enabled = True
        self.model.updateObjectDB(self)
        self.model.save(*args, **kwargs)

    def loadGame(self, *args, **kwargs):
        """Loads the game state, delegates call to gamemodel.GameModel
           @return: None"""
        # Remove all currently loaded maps so we can start fresh
        self.model.pause(False)
        self.pause(False)
        self.view.hud.enabled = True
        self.model.deleteMaps()
        for entity in self.entities.copy():
            entity.delete()
        self.view.hud.inventory = None

        self.model.load(*args, **kwargs)
        # Load the current map
        if self.model.game_state.current_map_name:
            self.model.loadMap(self.model.game_state.current_map_name)   
        self.model.placeAgents(self)
        self.model.placePC(self)
        self.setupScripts(self.model.game_state.current_map_name)
        self.view.hud.initializeInventory()          

    def quitGame(self):
        """Quits the game
           @return: None"""
        self.application.listener.quitGame()
    
    def pause(self, paused):
        """Pauses the controller"""
        super(GameSceneController, self).pause(paused)
        self.paused = paused
        if paused:
            self.scroll_timer.stop()
    
    def onCommand(self, command):
        if(command.getCommandType() == fife.CMD_MOUSE_FOCUS_GAINED):
            self.has_mouse_focus = True
        elif(command.getCommandType() == fife.CMD_MOUSE_FOCUS_LOST):
            self.has_mouse_focus = False
   
    def pump(self, dt):
        """Routine called during each frame. Our main loop is in ./run.py"""
        # uncomment to instrument
        # t0 = time.time()
        if self.paused: 
            return
        ControllerBase.pump(self, dt)
        PARPGWorld.pump(self, dt)
        self.updateMouse()
        if self.model.active_map:
            self.view.highlightFrontObject(self.last_mousecoords)
            self.view.refreshTopLayerTransparencies()
            self.handleScrolling()
        self.handleCommands()
        # print "%05f" % (time.time()-t0,)
