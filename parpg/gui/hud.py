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

import os
import logging

from fife.extensions import pychan
from fife.extensions.pychan.tools import callbackWithArguments as cbwa

from parpg import vfs
from parpg.gui.filebrowser import FileBrowser
from parpg.gui.menus import ContextMenu, SettingsMenu
from parpg.gui.popups import ExaminePopup
from parpg.gui.containergui import ContainerGUI
from parpg.gui.dialoguegui import DialogueGUI
from parpg.gui import drag_drop_data as data_drag
from parpg.gui.inventorygui import CharacterGUI
from actionsbox import ActionsBox
from parpg.entities.action import DropItemAction
from parpg.components import container

logger = logging.getLogger('hud')
class Hud(object):
    """Main Hud class"""
    def __init__(self, controller, settings, callbacks):
        """Initialise the instance.
           @type controller: Class derived from ControllerBase
           @param controller: The current controller
           @type settings: settings.Setting
           @param settings: The settings
           @type inv_model: dict
           @type callbacks: dict
           @param callbacks: a dict of callbacks
               saveGame: called when the user clicks on Save
               loadGame: called when the user clicks on Load
               quitGame: called when the user clicks on Quit
           @return: None"""

        # TODO: perhaps this should not be hard-coded here
        self.settings = settings
        pychan.registerWidget(ActionsBox)
        
        xml_file = vfs.VFS.open('gui/hud.xml')
        self.hud = pychan.loadXML(xml_file)

        self.controller = controller
        self.engine = controller.engine
        self.model = controller.model
        self.inventory = None
        self.character_screen = None

        self.save_game_callback = callbacks['saveGame']
        self.load_game_callback = callbacks['loadGame']
        self.quit_callback      = callbacks['quitGame']

        self.box_container = None
        self.examine_box = None
        self.context_menu = None
        self.help_dialog = None
        self.events_to_map = None
        self.main_menu = None
        self.menu_events = None
        self.quit_window = None
        self.bottom_panel = self.hud.findChild(name="mainHudWindow")
        
        self.actions_box = self.hud.findChild(name="actionsBox")
        self.menu_displayed = False
        self.inventory_storage = None
        self.initializeHud()
        self.initializeMainMenu()
        self.initializeContextMenu()
        self.initializeHelpMenu()
        self.initializeEvents()
        self.initializeQuitDialog()
        self.initializeSettingsMenu()
    
    def _getEnabled(self):
        """"Returns whether the gui widget is enabled or not"""
        return self.hud.real_widget.isEnabled()
    
    def _setEnabled(self, enabled):
        """"Sets whether the gui widget is enabled or not"""
        self.hud.real_widget.setEnabled(enabled)
        childs = self.hud.getNamedChildren()
        for child_list in childs.itervalues():
            for child in child_list:
                child.real_widget.setEnabled(enabled)
    
    enabled = property(_getEnabled, _setEnabled)
        
    def initializeHud(self):
        """Initialize and show the main HUD
           @return: None"""
        self.events_to_map = {"menuButton":self.displayMenu, }
        self.hud.mapEvents(self.events_to_map) 
        # set HUD size according to screen size
        screen_width = self.engine.getSettings().getScreenWidth()
        self.hud.findChild(name="mainHudWindow").size = (screen_width, 65)
        self.hud.findChild(name="inventoryButton").position = \
                                                    (screen_width-59, 7)
        # add ready slots
        ready1 = self.hud.findChild(name='hudReady1')
        ready2 = self.hud.findChild(name='hudReady2')
        ready3 = self.hud.findChild(name='hudReady3')
        ready4 = self.hud.findChild(name='hudReady4')

        if (screen_width <=800) :
            gap = 0
        else :
            gap = 40
        ready1.position = (160+gap, 7)
        ready2.position = (220+gap, 7)
        ready3.position = (screen_width-180-gap, 7)
        ready4.position = (screen_width-120-gap, 7)
        self.actions_box.position = (280+gap, 5)
        actions_width = screen_width - 470 - 2*gap

        self.actions_box.ContentBox.min_width = actions_width
        self.actions_box.ContentBox.max_width = actions_width
        
        # and finally add an actions box
        self.actions_box.min_size = (actions_width, 55)
        self.actions_box.max_size = (actions_width, 55)
        # now it should be OK to display it all
        self.showHUD()
        
    def addAction(self, action):
        """Add an action to the actions box.
           @type action: (unicode) string
           @param action: The text that you want to display in the actions box
           @return: None"""    
        self.actions_box.addAction(action)

    def showHUD(self):
        """Show the HUD.
           @return: None"""
        self.hud.show()
        self.enabled = True

    def hideHUD(self):
        """Hide the HUD.
           @return: None"""
        self.hud.hide()
        self.enabled = False

    def initializeInventory(self):
        """Initialize the inventory"""
        if not self.inventory:
            xml_file = vfs.VFS.open('gui/inventory.xml')
            player = self.model.game_state.getObjectById("PlayerCharacter")
            self.inventory = CharacterGUI(self.controller, xml_file, 
                                          player.container, player.equip, None)
#        inv_callbacks = {
#            'refreshReadyImages': self.refreshReadyImages,
#            'toggleInventoryButton': self.toggleInventoryButton,
#        }
#        self.inventory_storage = \
#            self.model.game_state.getObjectById("PlayerCharacter").fifeagent.inventory
#        if self.inventory == None:
#            self.inventory = inventorygui.InventoryGUI(self.controller,
#                                                       self.inventory_storage,
#                                                       inv_callbacks)
#        else:
#            self.inventory.inventory_storage = self.inventory_storage
#        self.refreshReadyImages()
    
    def initializeCharacterScreen(self):
        """Initialize the character screen."""
        # TODO Technomage 2010-12-24: 
        if not self.character_screen:
            xml_file = vfs.VFS.open('gui/character_screen.xml')
            self.character_screen = pychan.loadXML(xml_file)
    
    def initializeContextMenu(self):
        """Initialize the Context Menu
           @return: None"""
        self.context_menu = ContextMenu(self.engine, [], (0, 0))

    def showContextMenu(self, data, pos):
        """Display the Context Menu with model at pos
           @type model: list
           @param model: model to pass to context menu
           @type pos: tuple
           @param pos: tuple of x and y coordinates
           @return: None"""
        self.context_menu = ContextMenu(self.engine, data, pos)
        self.context_menu.show()

    def hideContextMenu(self):
        """Hides the context menu
           @return: None"""
        self.context_menu.hide()

    def initializeMainMenu(self):
        """Initalize the main menu.
           @return: None"""
        
        xml_file = vfs.VFS.open('gui/hud_pause_menu.xml')
        self.main_menu = pychan.loadXML(xml_file)

        #TODO: find more suitalbe place for onOptilonsPress implementation
        self.menu_events = {"resumeButton": self.hideMenu, 
                            "settingsButton": self.displaySettings,
                            "helpButton": self.displayHelp}
        self.main_menu.mapEvents(self.menu_events)

    def displayMenu(self):
        """Displays the main in-game menu.
           @return: None"""
        self.stopActions()
        if (self.menu_displayed == False):
            self.main_menu.show()
            self.menu_displayed = True
            self.model.pause(True)
            self.controller.pause(True)
            self.enabled = False
        elif (self.menu_displayed == True):
            self.hideMenu()

    def hideMenu(self):
        """Hides the main in-game menu.
           @return: None"""
        self.main_menu.hide()
        self.menu_displayed = False
        self.model.pause(False)
        self.controller.pause(False)
        self.enabled = True

    def initializeSettingsMenu(self):
        self.settings_menu = SettingsMenu(self.engine, self.settings)

    def displaySettings(self):
        self.settings_menu.show()

    def initializeHelpMenu(self):
        """Initialize the help menu
           @return: None"""

        xml_file = vfs.VFS.open('gui/help.xml')
        self.help_dialog = pychan.loadXML(xml_file)

        help_events = {"closeButton":self.help_dialog.hide}
        self.help_dialog.mapEvents(help_events)
        main_help_text = u"Welcome to Post-Apocalyptic RPG or PARPG![br][br]"\
        "This game is still in development, so please expect for there to be "\
        "bugs and[br]feel free to tell us about them at "\
        "http://www.forums.parpg.net.[br]This game uses a "\
        "\"Point 'N' Click\" interface, which means that to move around,[br]"\
        "just click where you would like to go and your character will move "\
        "there.[br]PARPG also utilizes a context menu. To access this, just "\
        "right click anywhere[br]on the screen and a menu will come up. This "\
        "menu will change depending on[br]what you have clicked on, hence "\
        "it's name \"context menu\".[br][br]"
        
        k_text = u" Keybindings" 
        k_text += "[br] A : Add a test action to the actions display"
        k_text += "[br] I : Toggle the inventory screen"
        k_text += "[br] F7 : Take a screenshot"
        k_text += "[br]      (Saves to screenshots directory)"
        k_text += "[br] F10 : Toggle console"
        k_text += "[br] PAUSE : (Un)Pause the game"
        k_text += "[br] Q : Quit the game"
        self.help_dialog.distributeInitialData({
                "MainHelpText":main_help_text,
                "KeybindText":k_text
                })

    def displayHelp(self):
        """Display the help screen.
           @return: None"""
        self.help_dialog.show()

    def saveGame(self):
        """ Called when the user wants to save the game.
            @return: None"""
        self.stopActions()
        xml_path = 'gui/savebrowser.xml'
        save_browser = FileBrowser(self.engine,
                                   self.settings,
                                   self.save_game_callback,
                                   xml_path,
                                   self.loadsave_close,
                                   save_file=True,
                                   extensions=('.dat'))
        save_browser.showBrowser()
        self.controller.pause(True)
        self.model.pause(True)
        self.enabled = False

    def stopActions(self):
        """This method stops/resets actions that are currently performed 
        like dragging an item.
        This is done to be able to savely perform other actions that might 
        interfere with current running ones."""
        #Reset dragging - move item back to its old container
        if data_drag.dragging:
            drag_item = data_drag.dragged_item 
            data_drag.dragging = False
            data_drag.dragged_item = None
            DropItemAction(self.controller, drag_item).execute()
        if self.inventory:
            self.inventory.closeInventory()
        
    def newGame(self):
        """Called when user request to start a new game.
           @return: None"""
        self.stopActions()
        logger.info('new game')
    
    def loadsave_close(self):
        """Called when the load/save filebrowser was closed without a file selected"""
        if not self.menu_displayed:
            self.enabled = True
            self.model.pause(False)
            self.controller.pause(False)
            
    def loadGame(self):
        """ Called when the user wants to load a game.
            @return: None"""
        self.stopActions()
        xml_path = 'gui/loadbrowser.xml'
        load_browser = FileBrowser(self.engine,
                                   self.settings,
                                   self.load_game_callback,
                                   xml_path,
                                   close_callback = self.loadsave_close,
                                   save_file=False,
                                   extensions=('.dat'))
        load_browser.showBrowser()
        self.model.pause(True)
        self.controller.pause(True)
        self.enabled = False
    
    def initializeQuitDialog(self):
        """Creates the quit confirmation dialog
           @return: None"""
        self.quit_window = pychan.widgets.Window(title=unicode("Quit?"), \
                                                 min_size=(200,0))

        hbox = pychan.widgets.HBox()
        are_you_sure = "Are you sure you want to quit?"
        label = pychan.widgets.Label(text=unicode(are_you_sure))
        yes_button = pychan.widgets.Button(name="yes_button", 
                                           text=unicode("Yes"),
                                           min_size=(90,20),
                                           max_size=(90,20))
        no_button = pychan.widgets.Button(name="no_button",
                                          text=unicode("No"),
                                          min_size=(90,20),
                                          max_size=(90,20))

        self.quit_window.addChild(label)
        hbox.addChild(yes_button)
        hbox.addChild(no_button)
        self.quit_window.addChild(hbox)

        events_to_map = { "yes_button": self.quit_callback,
                          "no_button":  self.quit_window.hide }
        
        self.quit_window.mapEvents(events_to_map)


    def quitGame(self):
        """Called when user requests to quit game.
           @return: None"""
        self.stopActions()
        self.quit_window.show()

    def toggleInventoryButton(self):
        """Manually toggles the inventory button.
           @return: None"""
        button = self.hud.findChild(name="inventoryButton")
        if button.toggled == 0:
            button.toggled = 1
        else:
            button.toggled = 0

    def toggleInventory(self, toggle_image=True):
        """Displays the inventory screen
           @return: None"""
        if self.inventory is None:
            self.initializeInventory()

        self.inventory.toggleInventory(toggle_image)
    
    def toggleCharacterScreen(self):
        if self.characcter_screen is None:
            self.initializeCharacterScreen()

        if not self.character_screen.isVisible():
            self.character_screen.show()
        else:
            self.character_screen.hide()
    
    def refreshReadyImages(self):
        """Make the Ready slot images on the HUD be the same as those 
           on the inventory
           @return: None"""
        for ready in range(1, 5):
            button = self.hud.findChild(name=("hudReady%d" % ready))
            if self.inventory_storage == None :
                origin = None
            else:
                origin = self.inventory_storage.getItemsInSlot('ready', ready-1)
            if origin == None:
                self.setImages(button, 
                               self.inventory.slot_empty_images['ready'])
            else:
                self.setImages(button, origin.getInventoryThumbnail())

    def setImages(self, widget, image):
        """Set the up, down, and hover images of an Imagebutton.
           @type widget: pychan.widget
           @param widget: widget to set
           @type image: string
           @param image: image to use
           @return: None"""
        widget.up_image = image
        widget.down_image = image
        widget.hover_image = image

    def initializeEvents(self):
        """Intialize Hud events
           @return: None"""
        events_to_map = {}

        # when we click the toggle button don't change the image
        events_to_map["inventoryButton"] = cbwa(self.toggleInventory, False)
        events_to_map["saveButton"] = self.saveGame
        events_to_map["loadButton"] = self.loadGame

        hud_ready_buttons = ["hudReady1", "hudReady2", \
                             "hudReady3", "hudReady4"]

        for item in hud_ready_buttons:
            events_to_map[item] = cbwa(self.readyAction, item)

        self.hud.mapEvents(events_to_map)

        menu_events = {}
        menu_events["newButton"] = self.newGame
        menu_events["quitButton"] = self.quitGame
        menu_events["saveButton"] = self.saveGame
        menu_events["loadButton"] = self.loadGame
        self.main_menu.mapEvents(menu_events)

    def readyAction(self, ready_button):
        """ Called when the user selects a ready button from the HUD """
        text = "Used the item from %s" % ready_button        
        self.addAction(text)
        
    def createBoxGUI(self, title, container):
        """Creates a window to display the contents of a box
           @type title: string
           @param title: The title for the window
           @param items: The box to display
           @return: A new ContainerGui"""
        events = {'takeAllButton':self.hideContainer,
                  'closeButton':self.hideContainer}
        #hide previous container if any, to avoid orphaned dialogs
        self.hideContainer()

        self.box_container = ContainerGUI(self.controller,
                                              unicode(title), container)
        self.box_container.gui.mapEvents(events)
        self.box_container.showContainer()
        return self.box_container

    def hideContainer(self):
        """Hide the container box
           @return: None"""
        if self.box_container:
            self.box_container.hideContainer()
            self.box_container = None

    def createExamineBox(self, title, desc):
        """Create an examine box. It displays some textual description of an
           object
           @type title: string
           @param title: The title of the examine box
           @type desc: string
           @param desc: The main body of the examine box
           @return: None"""
        if self.examine_box is not None:
            self.examine_box.closePopUp()
        self.examine_box = ExaminePopup(self.engine, title, desc)
        self.examine_box.showPopUp()

    def showDialogue(self, npc):
        """Show the NPC dialogue window
           @type npc: actors.NonPlayerCharacter
           @param npc: the npc that we are having a dialogue with
           @return: The dialogue"""
        self.stopActions()
        dialogue = DialogueGUI(
                    self.controller,
                    npc,
                    self.model.game_state.quest_engine,
                    self.model.game_state.met, self.model.game_state.meet,
                    container.get_item,
                    self.model.game_state.getObjectById("PlayerCharacter"))
        return dialogue
