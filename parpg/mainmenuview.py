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
#   along with PARPG.  If not, see <http://www.gnu.org/licenses/

from fife.extensions import pychan

from parpg import vfs
from viewbase import ViewBase
from parpg.gui.filebrowser import FileBrowser
from parpg.gui.menus import SettingsMenu

class MainMenuView(ViewBase):
    """View that is used to display the main menu"""

    def __init__(self, engine, model):
        """Constructor for MainMenuView
           @param engine: A fife.Engine instance
           @type engine: fife.Engine
           @param model: a script.GameModel instance
           @type model: script.GameModel 
           """        
        ViewBase.__init__(self, engine, model)
        self.quit_window = None
        self.new_game_callback = None
        self.load_game_callback = None
        self.quit_callback = None
        self.main_menu = None
        self.character_screen = None
    
    def showMenu(self):
        """"Shows the main menu"""
        self.main_menu_background.show()
        self.main_menu.show()
        
    def hideMenu(self):
        """"Hides the main menu"""
        self.main_menu.hide()
        self.main_menu_background.hide()

    def initalizeMainMenu(self, new_game, load_game, quit_game):
        """Initialized the main menu and sets the callbacks"""
        # Set a simple background to display the main screen.
        xml_file = vfs.VFS.open('gui/main_menu_background.xml')
        self.main_menu_background = pychan.loadXML(xml_file)
        
        # Initialize the main menu screen.
        screen_mode = self.engine.getRenderBackend().getCurrentScreenMode()
        self.main_menu_background.width = screen_mode.getWidth()
        self.main_menu_background.height = screen_mode.getHeight()

        xml_file = vfs.VFS.open('gui/main_menu.xml')
        self.main_menu = pychan.loadXML(xml_file)

        self.main_menu.adaptLayout()
        self.new_game_callback = new_game
        self.load_game_callback = load_game
        self.quit_callback = quit_game
        menu_events = {}
        menu_events["newButton"] = self.newGame
        menu_events["loadButton"] = self.loadGame
        menu_events["settingsButton"] = self.displaySettings
        menu_events["quitButton"] = self.quitGame
        self.main_menu.mapEvents(menu_events)
        
        self.initializeQuitDialog()
        self.initializeSettingsMenu()
    
    def newGame(self):
        """Called when user request to start a new game.
           @return: None"""
        self.new_game_callback()
    
    def loadGame(self):
        """ Called when the user wants to load a game.
            @return: None"""
        load_browser = FileBrowser(self.engine,
                                   self.model.settings,
                                   self.load_game_callback,
                                   gui_xml_path='gui/loadbrowser.xml',
                                   save_file=False,
                                   extensions=('.dat'))
        load_browser.showBrowser()
    
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
        self.quit_window.show()

    def initializeSettingsMenu(self):
        self.settings_menu = SettingsMenu(self.engine, self.model.settings)

    def displaySettings(self):
        self.settings_menu.show()
