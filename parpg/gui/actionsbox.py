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

"""Widget for displaying actions"""

from fife.extensions import pychan
from fife.extensions.pychan import ScrollArea
from fife.extensions.pychan import VBox

class ActionsBox(ScrollArea):
    def __init__(self, **kwargs):
        ScrollArea.__init__(self, **kwargs)
        self.ContentBox = VBox(name = "ActionsContentBox", is_focusable=False)
        self.addChild(self.ContentBox)
    
    def refresh(self):
        """Refresh the actions box so that it displays the contents of
        self.actions_text
        @return: None"""
        self.adaptLayout()
        self.vertical_scroll_amount = self.getVerticalMaxScroll()

    def addAction(self, action):
        """Add an action to the actions box.
        @type action: (unicode) string
        @param action: The text that you want to display in the actions box
        @return: None"""      
      
        if not type(action) is unicode:
            action = unicode(action)
        action_label = pychan.widgets.Label(text = action, wrap_text = True)
        action_label.max_width = self.ContentBox.width
        self.ContentBox.addChild(action_label)
        self.refresh()
    
    def addDialog(self, name, text):
        """Add a dialog text to the actions box. Prints first the name and then, indented to the right, the text.
        @type name: (unicode) string
        @param action: The name of the character that spoke
        @type text:: (unicode) string
        @param text: The text that was said
        @return: None"""        
        if not type(name) is unicode:
            name = unicode(name)
        if not type(text) is unicode:
            text = unicode(text)
        
        
        name_label = pychan.widgets.Label(text = name, wrap_text = True)
        self.ContentBox.addChild(name_label)
        text_box = pychan.widgets.HBox()
        spacer = pychan.widgets.Label()
        spacer.min_width = int(self.ContentBox.width * 0.05)
        spacer.max_width = int(self.ContentBox.width * 0.05)
        text_box.addChild(spacer)
        text_label = pychan.widgets.Label(text = text, wrap_text = True)
        text_label.max_width = int(self.ContentBox.width * 0.95)
        text_box.addChild(text_label)
        self.ContentBox.addChild(text_box)
        self.refresh()
        
