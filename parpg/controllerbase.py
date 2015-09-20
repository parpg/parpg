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

from parpg.common.listeners.key_listener import KeyListener
from parpg.common.listeners.mouse_listener import MouseListener
from parpg.common.listeners.command_listener import CommandListener
from bGrease.grease_fife.mode import Mode

class ControllerBase(Mode, KeyListener, MouseListener, CommandListener):
    """Base of Controllers"""
    def __init__(self, 
                 engine, 
                 view, 
                 model, 
                 application):
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
        KeyListener.__init__(self, application.event_listener)        
        MouseListener.__init__(self, application.event_listener)
        CommandListener.__init__(self, application.event_listener)
        Mode.__init__(self, engine)
        self.event_manager = engine.getEventManager()
        self.view = view
        self.model = model
        self.application = application
        
    def pause(self, paused):
        """Stops receiving events"""
        if paused:
            KeyListener.detach(self)
            MouseListener.detach(self)
        else:
            KeyListener.attach(self, self.application.event_listener)
            MouseListener.attach(self, self.application.event_listener)
    
    def setMouseCursor(self, image, dummy_image, mc_type="native"): 
        """Set the mouse cursor to an image.
           @type image: string
           @param image: The image you want to set the cursor to
           @type dummy_image: string
           @param dummy_image: ???
           @type type: string
           @param type: ???
           @return: None"""
        cursor = self.engine.getCursor()
        img_manager = self.engine.getImageManager()
        if(mc_type == "target"):
            target_cursor_id = img_manager.load(image)  
            dummy_cursor_id = img_manager.load(dummy_image)
            cursor.set(dummy_cursor_id)
            cursor.setDrag(target_cursor_id, -16, -16)
        else:
            cursor_type = fife.CURSOR_IMAGE
            zero_cursor_id = img_manager.load(image)
            cursor.set(zero_cursor_id)
            cursor.setDrag(zero_cursor_id)

    def resetMouseCursor(self):
        """Reset cursor to default image.
           @return: None"""
        image =  '/'.join(['gui/cursors/',
                           self.model.settings.get("parpg", "CursorDefault")])
        self.setMouseCursor(image, image)
    
    def pump(self, dt):
        pass
