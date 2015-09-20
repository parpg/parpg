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

from controllerbase import ControllerBase
from charactercreationview import CharacterCreationView
from charactercreationcontroller import CharacterCreationController
from gamescenecontroller import GameSceneController
from gamesceneview import GameSceneView

#For debugging/code analysis
if False:
    from parpg.mainmenuview import MainMenuView
    from fife import fife
    from gamemodel import GameModel
    from parpg import PARPGApplication

class MainMenuController(ControllerBase):
    """Controller for handling the main menu state"""

    def __init__(self, engine, view, model, application):
        """Constructor"""
        super(MainMenuController, self).__init__(engine, view, model, 
                                                 application)
    
        #this can be helpful for IDEs code analysis
        if False:
            assert(isinstance(self.engine, fife.Engine))
            assert(isinstance(self.view, MainMenuView))
            assert(isinstance(self.model, GameModel))
            assert(isinstance(self.application, PARPGApplication))
            assert(isinstance(self.event_manager, fife.EventManager))
        
        self.view.quit_callback = self.quitGame
        self.view.new_game_callback = self.newGame
        self.view.initalizeMainMenu(self.newGame, self.loadGame, self.quitGame)
        self.view.showMenu()
        self.resetMouseCursor()
    
    def newGame(self):
        """Start a new game and switch to the character creation controller."""
        view = CharacterCreationView(self.engine, self.model,
                                     self.model.settings)
        controller = CharacterCreationController(self.engine, view, self.model,
                                                 self.application)
        self.application.view = view
        self.application.manager.swap_modes(controller)
    
#    def newGame(self):
#        """Starts a new game"""
#        view = GameSceneView(self.engine,
#                             self.model)
#        controller = GameSceneController(self.engine,
#                                         view,
#                                         self.model,
#                                         self.application)        
#        self.application.view = view
#        self.application.manager.swap_modes(controller)
#        start_map = self.model.settings.get("PARPG", "Map")
#        self.model.changeMap(start_map)

    def loadGame(self, *args, **kwargs):
        """Loads the game state
           @return: None"""

        view = GameSceneView(self.engine,
                             self.model)
        controller = GameSceneController(self.engine,
                                         view,
                                         self.model,
                                         self.application)        
        self.application.view = view
        self.application.manager.swap_modes(controller)
        controller.loadGame(*args, **kwargs)
        
    def on_deactivate(self):
        """Called when the controller is removed from the list"""
        self.view.hideMenu()
                                         
    
    def quitGame(self):
        """Quits the game
           @return: None"""
        self.application.listener.quitGame()
