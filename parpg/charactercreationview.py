#   This file is part of PARPG.
#
#   PARPG is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   PARPG is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with PARPG.  If not, see <http://www.gnu.org/licenses/>.
"""Provides the view for displaying the character creation screen."""

from fife.extensions import pychan

from parpg import vfs
from viewbase import ViewBase

class CharacterCreationView(ViewBase):
    """View used to display the character creation screen.
       @ivar background: Widget displayed as the background.
       @type background: L{pychan.Widget}
       @ivar start_new_game_callback: Callback attached to the startButton.
       @type start_new_game_callback: callable
       @ivar cancel_new_game_callback: Callback attached to the cancelButton.
       @type cancel_new_game_callback: callable
       @ivar character_screen: Widget used to display the character creation
           screen.
       @type character_screen: L{pychan.Widget}"""

    def __init__(self, engine, model, settings):
        """Construct a new L{CharacterCreationView} instance.
           @param engine: Rendering engine used to display the view.
           @type engine: L{fife.Engine}
           @param model: Model of the game state.
           @type model: L{GameState}"""
        ViewBase.__init__(self, engine, model)
        self.settings = settings
        xml_file = vfs.VFS.open('gui/main_menu_background.xml')
        self.background = pychan.loadXML(xml_file)
        screen_mode = self.engine.getRenderBackend().getCurrentScreenMode()
        self.background.width = screen_mode.getWidth()
        self.background.height = screen_mode.getHeight()
        self.start_new_game_callback = None
        self.cancel_new_game_callback = None

        xml_file = vfs.VFS.open('gui/character_screen.xml')
        self.character_screen = pychan.loadXML(xml_file)

        self.character_screen.adaptLayout()
        character_screen_events = {}
        character_screen_events['startButton'] = self.startNewGame
        character_screen_events['cancelButton'] = self.cancelNewGame
        self.character_screen.mapEvents(character_screen_events)
    
    def show(self):
        """Display the view.
           @return: None"""
        self.background.show()
        self.character_screen.show()
    
    def hide(self):
        """Hide the view.
           @return: None"""
        self.background.hide()
        self.character_screen.hide()
    
    def startNewGame(self):
        """Callback tied to the startButton.
           @return: None"""
        self.start_new_game_callback()
    
    def cancelNewGame(self):
        """Callback tied to the cancelButton.
           @return: None"""
        self.cancel_new_game_callback()
