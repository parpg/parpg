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

"""This module contains the EventListener that receives events and distributes 
them to PARPG listeners"""
import logging

from fife import fife
from fife.extensions import pychan

logger = logging.getLogger('event_listener')

class EventListener(fife.IKeyListener, 
                   fife.ICommandListener, 
                   fife.IMouseListener, 
                   fife.ConsoleExecuter):
    """Class that receives all events and distributes them to the listeners"""
    def __init__(self, engine):
        """Initialize the instance"""
        self.event_manager = engine.getEventManager()

        fife.IKeyListener.__init__(self)
        self.event_manager.addKeyListener(self)
        fife.ICommandListener.__init__(self)
        self.event_manager.addCommandListener(self)
        fife.IMouseListener.__init__(self)
        self.event_manager.addMouseListener(self)
        fife.ConsoleExecuter.__init__(self)
        pychan.manager.hook.guimanager.getConsole().setConsoleExecuter(self)
        
        self.listeners = {"Mouse" : [],                          
                          "Key" : [],
                          "Command" : [],
                          "ConsoleCommand" : [],
                          "Widget" : []}               
                
    def addListener(self, listener_type, listener):
        """Adds a listener"""
        if listener_type in self.listeners.iterkeys():
            if not listener in self.listeners[listener_type]:
                self.listeners[listener_type].append(listener)            
        else:
            logger.warning("Listener type "
                                  "'{0}' not supported".format(listener_type))
    
    def removeListener(self, listener_type, listener):
        """Removes a listener"""
        if listener_type in self.listeners.iterkeys():
            self.listeners[listener_type].remove(listener)
        else:
            logger.warning("Listener type "
                                  "'{0}' not supported".format(listener_type))
            
    def mousePressed(self, evt):
        """Called when a mouse button is pressed"""
        for listeners in self.listeners["Mouse"]:
            listeners.mousePressed(evt)

    def mouseReleased(self, evt):
        """Called when a mouse button is released"""
        for listeners in self.listeners["Mouse"]:
            listeners.mouseReleased(evt)

    def mouseEntered(self, evt):
        """Called when a mouse enters a region"""
        for listeners in self.listeners["Mouse"]:
            listeners.mouseEntered(evt)

    def mouseExited(self, evt):
        """Called when a mouse exits a region"""
        for listeners in self.listeners["Mouse"]:
            listeners.mouseExited(evt)

    def mouseClicked(self, evt):
        """Called after a mouse button is pressed and released"""
        for listeners in self.listeners["Mouse"]:
            listeners.mouseClicked(evt)

    def mouseWheelMovedUp(self, evt):
        """Called when the mouse wheel has been moved up"""
        for listeners in self.listeners["Mouse"]:
            listeners.mouseWheelMovedUp(evt)

    def mouseWheelMovedDown(self, evt):
        """Called when the mouse wheel has been moved down"""
        for listener in self.listeners["Mouse"]:
            listener.mouseWheelMovedDown(evt)

    def mouseMoved(self, evt):
        """Called when when the mouse has been moved"""
        for listener in self.listeners["Mouse"]:
            listener.mouseMoved(evt)

    def mouseDragged(self, evt):
        """Called when dragging the mouse"""
        for listener in self.listeners["Mouse"]:
            listener.mouseDragged(evt)

    def keyPressed(self, evt):
        """Called when a key is being pressed"""
        for listener in self.listeners["Key"]:
            listener.keyPressed(evt)

    def keyReleased(self, evt):
        """Called when a key is being released"""
        for listener in self.listeners["Key"]:
            listener.keyReleased(evt)

    def onCommand(self, command):
        """Called when a command is executed"""
        for listener in self.listeners["Command"]:
            listener.onCommand(command)

    def onToolsClick(self):
        """Called when the tools button has been clicked"""
        for listener in self.listeners["ConsoleCommand"]:
            listener.onToolsClick()

    def onConsoleCommand(self, command):
        """Called when a console command is executed"""
        results = []
        for listener in self.listeners["ConsoleCommand"]:
            results.append(listener.onConsoleCommand(command))
        return "\n".join(results)

    def onWidgetAction(self, evt):
        """Called when a widget action is executed"""
        for listener in self.listeners["Widget"]:
            listener.onWidgetAction(evt)


