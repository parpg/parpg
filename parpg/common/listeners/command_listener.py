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

"""This module contains the CommandListener class for receiving command events"""


class CommandListener(object):
    """Base class for listeners that receiving command events"""

    def __init__(self, event_listener):
        self.event_listener = None
        CommandListener.attach(self, event_listener)
    
    def attach(self, event_listener):
        """Attaches the listener to the event"""
        event_listener.addListener("Command", self)
        self.event_listener = event_listener
        
    def detach(self):
        """Detaches the listener from the event"""
        self.event_listener.removeListener("Command", self)
        self.event_listener = None

    def onCommand(self, command):
        """Called when a command is executed"""
        pass
