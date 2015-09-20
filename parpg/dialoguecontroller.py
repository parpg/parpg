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
from controllerbase import ControllerBase

class DialogueController(ControllerBase):
    """Controller that takes over when a dialogue is started"""
    def __init__(self, 
                 engine, 
                 view, 
                 model, 
                 application):
        """
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
        """
        super(DialogueController, self).__init__(engine,
                                                  view,
                                                  model,
                                                  application)
        self.dialogue = None
        self.view = view
        
    def startTalk(self, npc):
        if npc.dialogue is not None:
            self.model.active_map.centerCameraOnPlayer()            
            npc.fifeagent.behaviour.talk(
                self.model.game_state.\
                getObjectById("PlayerCharacter").fifeagent
            )
            self.dialogue = self.view.hud.showDialogue(npc)
            self.dialogue.initiateDialogue()
            self.model.pause(True)
            self.view.hud.enabled = False

            
    def pump(self, dt):
        ControllerBase.pump(self, dt)
        if self.dialogue and not self.dialogue.active:
            self.application.manager.pop_mode()
            self.model.pause(False)
            self.view.hud.enabled = True
            
