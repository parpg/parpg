#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""This module contains the main Application class 
and the basic Listener for PARPG """

import os
import sys

from fife import fife
from fife.extensions import pychan
from fife.extensions.basicapplication import ApplicationBase

from parpg import console, vfs
from parpg.font import PARPGFont
from parpg.gamemodel import GameModel
from parpg.mainmenuview import MainMenuView
from parpg.mainmenucontroller import MainMenuController
from parpg.common.listeners.event_listener import EventListener
from parpg.common.listeners.key_listener import KeyListener
from parpg.common.listeners.mouse_listener import MouseListener
from parpg.common.listeners.command_listener import CommandListener
from parpg.common.listeners.console_executor import ConsoleExecuter
from parpg.common.listeners.widget_listener import WidgetListener
from bGrease.grease_fife.mode import FifeManager

class KeyFilter(fife.IKeyFilter):
    """
    This is the implementation of the fife.IKeyFilter class.

    Prevents any filtered keys from being consumed by guichan.
    """
    def __init__(self, keys):
        fife.IKeyFilter.__init__(self)
        self._keys = keys

    def isFiltered(self, event):
        """Checks if an key is filtered"""
        return event.getKey().getValue() in self._keys

class ApplicationListener(KeyListener,
                          MouseListener,
                          ConsoleExecuter,
                          CommandListener,
                          WidgetListener):    
    """Basic listener for PARPG"""

    def __init__(self, event_listener, engine, view, model):
        """Initialize the instance.
           @type engine: fife.engine
           @param engine: ???
           @type view: viewbase.ViewBase
           @param view: View that draws the current state
           @type model: GameModel
           @param model: The game model"""

        KeyListener.__init__(self, event_listener)
        MouseListener.__init__(self, event_listener)
        ConsoleExecuter.__init__(self, event_listener)
        CommandListener.__init__(self, event_listener)
        WidgetListener.__init__(self, event_listener)        
        self.engine = engine
        self.view = view
        self.model = model
        keyfilter = KeyFilter([fife.Key.ESCAPE])
        keyfilter.__disown__()        

        engine.getEventManager().setKeyFilter(keyfilter)
        self.quit = False
        self.about_window = None
        self.console = console.Console(self)

    def quitGame(self):
        """Forces a quit game on next cycle.
           @return: None"""
        self.quit = True

    def onConsoleCommand(self, command):
        """
        Called on every console comand, delegates calls  to the a console
        object, implementing the callbacks
        @type command: string
        @param command: the command to run
        @return: result
        """
        return self.console.handleConsoleCommand(command)

    def onCommand(self, command):
        """Enables the game to be closed via the 'X' button on the window frame
           @type command: fife.Command
           @param command: The command to read.
           @return: None"""
        if(command.getCommandType() == fife.CMD_QUIT_GAME):
            self.quit = True
            command.consume()

class PARPGApplication(ApplicationBase):
    """Main Application class
       We use an MVC model model
       self.gamesceneview is our view,self.model is our model
       self.controller is the controller"""

    def __init__(self, setting):
        """Initialise the instance.
           @return: None"""
        ApplicationBase.__init__(self, setting)
        self.manager = FifeManager()
        # KLUDGE M. George Hansen 2011-06-04: See parpg/vfs.py.
        vfs.VFS = self.engine.getVFS()
        vfs.VFS.addNewSource(setting.get("parpg","DataPath"))

        self.quitRequested = False
        self.breakRequested = False
        self.returnValues = []
        #self.engine.getModel(self)
        self.model = GameModel(self.engine, setting)
        self.model.readMapFiles()
        self.model.readObjectDB()
        self.model.getAgentImportFiles()
        self.model.readAllAgents()
        self.model.getDialogues()
        # KLUDGE M. George Hansen 2011-06-04: Hack to allow loaded PyChan XML
        #     scripts to locate their resources.
        os.chdir(setting.get("parpg","DataPath"))
        self.view = MainMenuView(self.engine, self.model)
        self.loadFonts()
        self.event_listener = EventListener(self.engine)
        controller = MainMenuController(self.engine, self.view, self.model, 
                                        self)
        #controller.initHud()
        self.manager.push_mode(controller)
        self.listener = ApplicationListener(self.event_listener,
                                            self.engine, 
                                            self.view, 
                                            self.model)

    def loadFonts(self):
        # add the fonts path to the system path to import font definitons
        sys.path.insert(0, os.path.join(self._setting.get("parpg", "DataPath"), 'fonts'))
        from oldtypewriter import fontdefs

        for fontdef in fontdefs:
            pychan.internal.get_manager().addFont(PARPGFont(fontdef,
                                                            self._setting))


    def createListener(self):
        """ __init__ takes care of creating an event listener, so
            basicapplication's createListener is harmful. Without 
            overriding it, the program quit's on esc press, rather than
            invoking the main menu
        """
        pass

    def _pump(self):
        """Main game loop.
           There are 2 main loops, this one and the one in GameSceneView.
           @return: None"""
        if self.listener.quit:
            self.breakRequested = True #pylint: disable-msg=C0103
        else:
            self.manager._pump()
