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

from random import randrange

from fife import fife

import base
from moving import MovingAgentBehaviour

class NPCBehaviour(MovingAgentBehaviour):
    """This is a basic NPC behaviour"""
    def __init__(self, parent=None):
        super(NPCBehaviour, self).__init__()
        
        self.parent = parent
        self.state = base._AGENT_STATE_NONE
        self.pc = None
        self.target_loc = None
        
        # hard code these for now
        self.distRange = (2, 4)
        # these are parameters to lower the rate of wandering
        # wander rate is the number of "IDLEs" before a wander step
        # this could be set for individual NPCs at load time
        # or thrown out altogether.
        # HACK: 09.Oct.2011 Beliar
        # I increased the wander rate to 900 since the idle method
        # gets called way more often now.
        self.wanderCounter = 0
        self.wanderRate = 9
        
    def getTargetLocation(self):
        """@rtype: fife.Location
           @return: NPC's position"""
        x = self.getX()
        y = self.getY()
        if self.state == base._AGENT_STATE_WANDER:
            """ Random Target Location """
            l = [0, 0]
            for i in range(len(l)):
                sign = randrange(0, 2)
                dist = randrange(self.distRange[0], self.distRange[1])
                if sign == 0:
                    dist *= -1
                l[i] = dist
            x += l[0]
            y += l[1]
            # Random walk is
            # rl = randint(-1, 1);ud = randint(-1, 1);x += rl;y += ud
        l = fife.Location(self.agent.getLocation())
        l.setLayerCoordinates(fife.ModelCoordinate(x, y))
        return l

    def onInstanceActionFinished(self, instance, action):
        """What the NPC does when it has finished an action.
           Called by the engine and required for InstanceActionListeners.
           @type instance: fife.Instance
           @param instance: self.agent
           @type action: ???
           @param action: ???
           @return: None"""
        if self.state == base._AGENT_STATE_WANDER:
            self.target_loc = self.getTargetLocation()
        MovingAgentBehaviour.onInstanceActionFinished(self, instance, action)
        
    
    def idle(self):
        """Controls the NPC when it is idling. Different actions
           based on the NPC's state.
           @return: None"""
        if self.state == base._AGENT_STATE_NONE:
            self.state = base._AGENT_STATE_IDLE
            self.animate('stand')
        elif self.state == base._AGENT_STATE_IDLE:
            if self.wanderCounter > self.wanderRate:
                self.wanderCounter = 0
                self.state = base._AGENT_STATE_WANDER
            else:
                self.wanderCounter += 1
                self.state = base._AGENT_STATE_NONE
            
            self.target_loc = self.getTargetLocation()
            self.animate('stand')
        elif self.state == base._AGENT_STATE_WANDER:
            self.wander(self.target_loc)
            self.state = base._AGENT_STATE_NONE
        elif self.state == base._AGENT_STATE_TALK:
            self.animate('stand', self.pc.getLocation())
            
    def wander(self, location):
        """Nice slow movement for random walking.
        @type location: fife.Location
        @param location: Where the NPC will walk to.
        @return: None"""
        self.agent.move('walk', location, self.speed)
        coords = location.getMapCoordinates()
