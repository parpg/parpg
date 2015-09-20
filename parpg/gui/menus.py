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

import logging

from fife.extensions import pychan

from parpg import vfs
from dialogs import RestartDialog

logger = logging.getLogger('menus')

class ContextMenu(object):
    def __init__(self, engine, menu_items, pos):
        """@type engine: engine.Engine
           @param engine: An instance of the class Engine from engine.py 
           @type menu_items: list
           @param menu_items: A list of items containing the name and 
                              text for the menu item and callback
                              i.e. [["menu", "Some text",  Callback]
           @type pos: (int, int)
           @param pos: Screen position to use 
           @return: None"""
        self.vbox = pychan.widgets.VBox(position=pos)
        events_to_map = {}
        for item in menu_items:
            p = pychan.widgets.Button(name=item[0], text=unicode(item[1]))
            self.vbox.addChild(p)
            events_to_map [item[0]] = self.actionDecorator(*item[2:])
        self.vbox.mapEvents(events_to_map)
    
    def show(self):
        """Shows the context menu"""
        self.vbox.show()
    def hide(self):
        """Hides the context menu"""
        self.vbox.hide()
        
    def actionDecorator (self,func, *args, **kwargs):
        """This function is supposed to add some generic that should be
        executed before and/or after an action is fired through the
        context menu.
        
        @type func: Any callable
        @param func: The original action function
        @param args: Unpacked list of positional arguments
        @param kwargs: Unpacked list of keyword arguments
        @return: A wrapped version of func"""
        def decoratedFunc ():
            """ This is the actual wrapped version of func, that is returned.
            It takes no external arguments, so it can safely be passed around
            as a callback."""
            # some stuff that we do before the actual action is executed
            self.hide()
            # run the action function, and record the return value
            ret_val = func (*args,**kwargs)
            # we can eventually add some post-action code here, if needed (e.g. logging)
            pass        
            # return the value, as if the original function was called
            return ret_val
        return decoratedFunc
        
class SettingsMenu(object):
    def __init__(self, engine, settings):
        self.engine = engine
        self.settings = settings

        # available options
        screen_modes = self.engine.getDeviceCaps().getSupportedScreenModes()
        resolutions = list(set([(mode.getWidth(), mode.getHeight())
                                for mode in screen_modes]))
        self.resolutions = ["{0}x{1}".format(item[0], item[1])
                            for item in sorted(resolutions)[1:]]

        self.render_backends = ['OpenGL', 'SDL']
        self.lighting_models = range(3)
        
        # selected options
        self.resolution = self.settings.get("FIFE", "ScreenResolution")
        self.render_backend = self.settings.get("FIFE", "RenderBackend")
        self.lighting_model = self.settings.get("FIFE", "Lighting")
        self.fullscreen = self.settings.get("FIFE", "FullScreen")
        self.sound = self.settings.get("FIFE", "PlaySounds")
        self.scroll_speed = self.settings.get("parpg", "ScrollSpeed")
        
        xml_file = vfs.VFS.open('gui/settings_menu.xml')
        self.window = pychan.loadXML(xml_file)
        self.restart_dialog = RestartDialog(self.settings)
        self.window.mapEvents({'okButton': self.save,
                               'cancelButton': self.hide,
                               'defaultButton': self.reset,
                               'scroll_speed': self.update})
        self.initializeWidgets()
        self.fillWidgets()

    def initializeWidgets(self):
        scroll_speed = unicode(self.scroll_speed)
        initial_data = {'screen_resolution': self.resolutions,
                        'render_backend': self.render_backends,
                        'lighting_model': self.lighting_models,
                        'scroll_speed_value': scroll_speed}

        self.window.distributeInitialData(initial_data)


    def fillWidgets(self):
        resolution = self.resolutions.index(self.resolution)
        backend = self.render_backends.index(self.render_backend)
        lighting = self.lighting_models.index(self.lighting_model)
        
        self.window.distributeData({'screen_resolution': resolution,
                                    'render_backend': backend,
                                    'lighting_model': lighting,
                                    'enable_fullscreen': self.fullscreen,
                                    'enable_sound': self.sound})

    def update(self):
        """updates lables to show realtime data"""
        #collects the data from the widgets
        (scroll_speed) = self.window.collectData('scroll_speed')

        #alter the data note:pychan insists that all lables be given
        #  unicode text
        #the slice rounds the number displayed
        scroll_speed = unicode(scroll_speed)[:3]

        #adds the data to the proper widgets
        self.window.distributeInitialData({'scroll_speed_value': scroll_speed})

    def show(self):
        self.window.show()

    def hide(self):
        self.window.hide()

    def reset(self):
        self.settings.read(self.settings.system_path)
        self.fillWidgets()

    def save(self):
        (resolution, backend, lighting, fullscreen, sound, scroll_speed) = \
            self.window.collectData('screen_resolution', 'render_backend',
                                    'lighting_model', 'enable_fullscreen',
                                    'enable_sound', 'scroll_speed')
        self.settings.set("FIFE", "ScreenResolution", self.resolutions[resolution])
        self.settings.set("FIFE", "RenderBackend", self.render_backends[backend])
        self.settings.set("FIFE", "Lighting", self.lighting_models[lighting])
        self.settings.set("FIFE", "FullScreen", fullscreen)
        self.settings.set("FIFE", "EnableSound", sound)
        self.settings.set("FIFE", "ScrollSpeed", scroll_speed)
        self.settings.saveSettings("../settings.xml")
       
        self.restart_dialog.show()
        self.hide()
