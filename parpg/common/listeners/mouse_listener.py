#!/usr/bin/env python

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

"""This module contains the MouseListener class for receiving mouse inputs"""

class MouseListener(object):
    """Base class for listeners receiving mouse input"""
    
    def __init__(self, event_listener):
        self.event_listener = None
        MouseListener.attach(self, event_listener)
    
    def attach(self, event_listener):
        """Attaches the listener to the event"""
        event_listener.addListener("Mouse", self)
        self.event_listener = event_listener
        
    def detach(self):
        """Detaches the listener from the event"""
        self.event_listener.removeListener("Mouse", self)
        self.event_listener = None
        
    def mousePressed(self, evt):
        """Called when a mouse button is pressed"""
        pass

    def mouseReleased(self, evt):
        """Called when a mouse button is released"""
        pass

    def mouseEntered(self, evt):
        """Called when a mouse enters a region"""
        pass

    def mouseExited(self, evt):
        """Called when a mouse exits a region"""
        pass

    def mouseClicked(self, evt):
        """Called after a mouse button is pressed and released"""
        pass

    def mouseWheelMovedUp(self, evt):
        """Called when the mouse wheel has been moved up"""
        pass

    def mouseWheelMovedDown(self, evt):
        """Called when the mouse wheel has been moved down"""
        pass

    def mouseMoved(self, evt):
        """Called when when the mouse has been moved"""
        pass

    def mouseDragged(self, evt):
        """Called when dragging the mouse"""
        pass
