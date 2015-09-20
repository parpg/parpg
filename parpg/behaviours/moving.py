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
import base
from base import BaseBehaviour

class MovingAgentBehaviour (BaseBehaviour):
    """Fife agent listener"""
    def __init__(self):
        BaseBehaviour.__init__(self)
        self.speed = 0
        self.idle_counter = 1
        
    def onNewMap(self, layer):
        """Sets the agent onto the new layer."""
        BaseBehaviour.onNewMap(self, layer)
        self.idle_counter = 1


    def approach(self, location_or_agent, action=None):
        """Approaches a location or another agent and then perform an action 
        (if set).
        @type loc: fife.Location
        @param loc: the location or agent to approach
        @type action: Action
        @param action: The action to schedule for execution after the 
        approach.
        @return: None"""
            
        self.state = base._AGENT_STATE_APPROACH
        self.nextAction = action
        if  isinstance(location_or_agent, fife.Instance):
            agent = location_or_agent
            self.agent.follow('run', agent, self.speed + 1)
        else:
            location = location_or_agent
            boxLocation = tuple([int(float(i)) for i in location])
            l = fife.Location(self.getLocation())
            l.setLayerCoordinates(fife.ModelCoordinate(*boxLocation))
            self.agent.move('run', l, self.speed + 1)        
        
    def onInstanceActionFinished(self, instance, action):
        """@type instance: ???
        @param instance: ???
        @type action: ???
        @param action: ???
        @return: None"""
        BaseBehaviour.onInstanceActionFinished(self, instance, action)
            
        if(action.getId() != 'stand'):
            self.idle_counter = 1
        else:
            self.idle_counter += 1 
        
    def idle(self):
        """@return: None"""
        BaseBehaviour.idle(self)
        self.animate('stand')    
        
    def run(self, location):
        """Makes the PC run to a certain location
        @type location: fife.ScreenPoint
        @param location: Screen position to run to.
        @return: None"""
        self.state = base._AGENT_STATE_RUN
        self.clear_animations()
        self.nextAction = None
        self.agent.move('run', location, self.speed + 1)

    def walk(self, location):
        """Makes the PC walk to a certain location.
        @type location: fife.ScreenPoint
        @param location: Screen position to walk to.
        @return: None"""
        self.state = base._AGENT_STATE_RUN
        self.clear_animations()
        self.nextAction = None
        self.agent.move('walk', location, self.speed - 1)
        