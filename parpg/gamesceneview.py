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

from sounds import SoundEngine
from viewbase import ViewBase
from fife import fife

class GameSceneView(ViewBase):
    """GameSceneView is responsible for drawing the scene"""
    def __init__(self, engine, model):
        """Constructor for GameSceneView
           @param engine: A fife.Engine instance
           @type engine: fife.Engine
           @param model: a script.GameModel instance
           @type model: script.GameModel 
           """
        super(GameSceneView, self).__init__(engine, model)

        # init the sound
        self.sounds = SoundEngine(engine)

        self.hud = None        

        # The current highlighted object
        self.highlight_obj = None
     
        # faded objects in top layer
        self.faded_objects = set()

    def displayObjectText(self, obj_id, text, time=1000):
        """Display on screen the text of the object over the object.
           @type obj_id: id of fife.instance
           @param obj: id of object to draw over
           @type text: String
           @param text: text to display over object
           @return: None"""
        try:
            if obj_id:
                obj = self.model.active_map.agent_layer.getInstance(obj_id)
            else:
                obj = None
        except RuntimeError as error:
            if error.args[0].split(',')[0].strip() == "_[NotFound]_":
                obj = None
            else:
                raise
        if obj:
            obj.say(str(text), time)

    def onWalk(self, click):
        """Callback sample for the context menu."""
        self.hud.hideContainer()
        self.model.game_state.getObjectById("PlayerCharacter").fifeagent.behaviour.run(click)

    def refreshTopLayerTransparencies(self):
        """Fade or unfade TopLayer instances if the PlayerCharacter 
        is under them."""
        if not self.model.active_map:
            return

        # get the PlayerCharacter's screen coordinates
        camera = self.model.active_map.cameras[self.model.active_map.my_cam_id]
        point = self.model.game_state.getObjectById("PlayerCharacter").fifeagent.\
                                        behaviour.agent.getLocation()
        scr_coords = camera.toScreenCoordinates(point.getMapCoordinates())

        # find all instances on TopLayer that fall on those coordinates
        instances = camera.getMatchingInstances(scr_coords,
                        self.model.active_map.top_layer)
        instance_ids = [ instance.getId() for instance in instances ]
        faded_objects = self.faded_objects

        # fade instances
        for instance_id in instance_ids:
            if instance_id not in faded_objects:
                faded_objects.add(instance_id)
                self.model.active_map.top_layer.getInstance(instance_id).\
                        get2dGfxVisual().setTransparency(128)

        # unfade previously faded instances
        for instance_id in faded_objects.copy():
            if instance_id not in instance_ids:
                faded_objects.remove(instance_id)
                self.model.active_map.top_layer.getInstance(instance_id).\
                        get2dGfxVisual().setTransparency(0)


    #def removeHighlight(self):
        
    
    def highlightFrontObject(self, mouse_coords):
        """Highlights the object that is at the 
        current mouse coordinates"""        
        if not self.model.active_map:
            return
        if mouse_coords:
            front_obj = self.model.getObjectAtCoords(mouse_coords)
            if front_obj != None:
                if self.highlight_obj == None \
                                    or front_obj.getId() != \
                                    self.highlight_obj:
                    if self.model.game_state.hasObject(front_obj.getId()):
                        self.displayObjectText(self.highlight_obj, "")
                    self.model.active_map.outline_renderer.removeAllOutlines()
                    self.highlight_obj = front_obj.getId()
                    self.model.active_map.outline_renderer.addOutlined(
                                                    front_obj, 
                                                    0,
                                                    137, 255, 2)
                    # get the text
                    item = self.model.objectActive(self.highlight_obj)
                    if item is not None:
                        self.displayObjectText(self.highlight_obj, 
                                                    item.description.view_name)
            else:
                self.model.active_map.outline_renderer.removeAllOutlines()
                self.highlight_obj = None  
           

    def moveCamera(self, direction):
        """Move the camera in the given direction.
        @type direction: list of two integers
        @param direction: the two integers can be 1, -1, or 0
        @return: None """  
        
        if 'cameras' in dir(self.model.active_map):
            cam = self.model.active_map.cameras[self.model.active_map.my_cam_id]
            location = cam.getLocation()
            position = location.getMapCoordinates()
            
            #how many pixls to move by each call
            move_by = 1
            #create a new DoublePoint3D and add it to position DoublePoint3D
            new_x, new_y = move_by * direction[0], move_by * direction[1]

            position_offset = fife.DoublePoint3D(int(new_x), int(new_y))
            position += position_offset
            
            #give location the new position
            location.setMapCoordinates(position)

            #detach the camera from any objects
            cam.detach()
            #move the camera to the new location
            cam.setLocation(location)
            
            
