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

from fife import fife
from fife.extensions import pychan
from fife.extensions.loaders import loadMapFile

class GameMap(fife.MapChangeListener):
    """Map class used to flag changes in the map"""
    def __init__(self, engine, model):
        # init mapchange listener
        fife.MapChangeListener.__init__(self)
        self.map = None
        self.engine = engine
        self.model = model
        self.settings = self.model.settings

        # init map attributes
        self.my_cam_id = None
        self.cameras = {}
        self.agent_layer = None
        self.top_layer = None
        self.fife_model = engine.getModel()
        self.transitions = []
        self.cur_cam2_x = 0
        self.initial_cam2_x = 0
        self.cam2_scrolling_right = True
        self.target_rotation = 0
        self.outline_renderer = None
        
    def reset(self):
        """Reset the model to default settings.
           @return: None"""
        # We have to delete the map in Fife.
        if self.map:
            self.model.deleteObjects()
            self.model.deleteMap(self.map)

        self.transitions = []
        self.map = None
        self.agent_layer = None        
        self.top_layer = None
        # We have to clear the cameras in the view as well, or we can't reuse
        # camera names like 'main'
        #self.view.clearCameras()
        self.initial_cam2_x = 0
        self.cam2_scrolling_right = True
        #self.cameras = {}
        self.cur_cam2_x = 0
        self.target_rotation = 0
        self.outline_renderer = None
        
    def makeActive(self):
        """Makes this map the active one.
           @return: None"""
        self.cameras[self.my_cam_id].setEnabled(True)
        
    def load(self, filename):
        """Load a map given the filename.
           @type filename: String
           @param filename: Name of map to load
           @return: None"""
        self.reset()

        self.map = loadMapFile(filename, self.engine)

        self.agent_layer = self.map.getLayer('ObjectLayer')
        self.top_layer = self.map.getLayer('TopLayer')      
            
        # it's possible there's no transition layer
        size = len('TransitionLayer')
        for layer in self.map.getLayers():
            # could be many layers, but hopefully no more than 3
            if(layer.getId()[:size] == 'TransitionLayer'):
                self.transitions.append(self.map.getLayer(layer.getId()))

        """ Initialize the camera.
        Note that if we have more than one camera in a map file
        we will have to rework how self.my_cam_id works. To make sure
        the proper camera is set as the 'main' camera.
        At this point we also set the viewport to the current resolution."""
        for cam in self.map.getCameras():
            width = self.engine.getSettings().getScreenWidth()
            height = self.engine.getSettings().getScreenHeight()
            viewport = fife.Rect(0, 0, width, height)
            cam.setViewPort(viewport)
            self.my_cam_id = cam.getId()
            self.cameras[self.my_cam_id] = cam
            cam.resetRenderers()
        
        self.target_rotation = self.cameras[self.my_cam_id].getRotation()

        self.outline_renderer = (
            fife.InstanceRenderer.getInstance(self.cameras[self.my_cam_id])
        )

        # set the render text
        rend = fife.FloatingTextRenderer.getInstance(
            self.cameras[self.my_cam_id]
        )
        font = pychan.manager.hook.guimanager.createFont(
            'fonts/rpgfont.png',
            0,
            self.settings.get("FIFE", "FontGlyphs")
        )

        rend.setFont(font)
        rend.activateAllLayers(self.map)
        rend.setEnabled(True)
        
        # Activate the grid renderer on all layers
        rend = self.cameras['map_camera'].getRenderer('GridRenderer')
        rend.activateAllLayers(self.map)
         
        # Activate the grid renderer on all layers
        rend = fife.CoordinateRenderer.getInstance(
            self.cameras[self.my_cam_id]
        )
        rend.setColor(0, 0, 0)
        rend.addActiveLayer(self.map.getLayer("GroundLayer"))

        # Make World aware that this is now the active map.
        self.model.active_map = self

    def addPC(self):
        """Add the player character to the map
           @return: None"""
        # Update gamestate.player_character
        player = self.model.game_state.getObjectById("PlayerCharacter")
        player.fifeagent.behaviour.onNewMap(self.agent_layer)
        self.centerCameraOnPlayer()

    def toggleRenderer(self, r_name):
        """Enable or disable a renderer.
           @return: None"""
        renderer = self.cameras[self.my_cam_id].getRenderer(str(r_name))
        renderer.setEnabled(not renderer.isEnabled())

    def isPaused(self):
        """Returns wheter the map is currentply paused or not"""
        # Time multiplier is a float, never do equals on floats
        return not self.map.getTimeMultiplier() >= 1.0
    
    def pause(self, paused):
        """ Pause/Unpause the game.
        @return: nothing"""
        if paused:
            self.map.setTimeMultiplier(0.0)
        if not paused and self.isPaused():
            self.map.setTimeMultiplier(1.0)
        
    def togglePause(self):
        """ Toggle paused state.
        @return: nothing"""
        self.pause(not self.isPaused())

    def centerCameraOnPlayer(self):
        """Center the camera on the player"""
        camera = self.cameras[self.my_cam_id]
        player = self.model.game_state.getObjectById("PlayerCharacter")
        camera.setLocation(player.fifeagent.behaviour.getLocation())
