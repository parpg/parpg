#/usr/bin/python

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

from fife.extensions import pychan

class ExaminePopup():
    """Create a popup for when you click examine on an object"""
    def __init__(self, engine, object_title, desc):
        """Initialize the popup  
           @type engine: fife.Engine
           @param engine: an instance of the fife engine
           @type object_title: string
           @param object_title: The title for the window, probably should just
                                be the name of the object
           @type desc: string
           @param desc: The description of the object
           @return: None"""
        self.engine = engine

        self.examine_window = pychan.widgets.\
                                Window(title=unicode(object_title),
                                       position_technique="center:center",
                                       min_size=(175,175))

        self.scroll = pychan.widgets.ScrollArea(name='scroll', size=(150,150))
        self.description = pychan.widgets.Label(name='descText',
                                                text=unicode(desc),
                                                wrap_text=True)
        self.description.max_width = 170
        self.scroll.addChild(self.description)
        self.examine_window.addChild(self.scroll)
        
        self.close_button = pychan.widgets.Button(name='closeButton',
                                                  text=unicode('Close'))
        self.examine_window.addChild(self.close_button)

        self.examine_window.mapEvents({'closeButton':self.examine_window.hide})

    def closePopUp(self):
        # TODO: missing function information
        if self.examine_window.isVisible():
            self.examine_window.hide()
    
    def showPopUp(self):
        # TODO: missing function information
        self.examine_window.show()
