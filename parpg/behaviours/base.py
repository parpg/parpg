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

from collections import deque

from fife import fife

_AGENT_STATE_NONE, _AGENT_STATE_IDLE, _AGENT_STATE_APPROACH, _AGENT_STATE_RUN, _AGENT_STATE_WANDER, _AGENT_STATE_TALK = xrange(6)

class BaseBehaviour (fife.InstanceActionListener):
    """Fife agent listener"""
    def __init__(self):
        fife.InstanceActionListener.__init__(self)
        self.agent = None
        self.state = None
        self.animation_queue = deque()
        self.nextAction = None 
    
    def attachToLayer(self, agent_ID, layer):
        """Attaches to a certain layer
           @type agent_ID: String
           @param agent_ID: ID of the layer to attach to.
           @type layer: Fife layer
           @param layer: Layer of the agent to attach the behaviour to
           @return: None"""
        self.agent = layer.getInstance(agent_ID)
        self.agent.addActionListener(self)
        self.state = _AGENT_STATE_NONE
        
    def getX(self):
        """Get the NPC's x position on the map.
           @rtype: integer"
           @return: the x coordinate of the NPC's location"""
        return self.agent.getLocation().getLayerCoordinates().x

    def getY(self):
        """Get the NPC's y position on the map.
           @rtype: integer
           @return: the y coordinate of the NPC's location"""
        return self.agent.getLocation().getLayerCoordinates().y
        
    def onNewMap(self, layer):
        """Sets the agent onto the new layer."""
        if self.agent is not None:
            self.agent.removeActionListener(self)
            
        self.agent = layer.getInstance(self.parent.general.identifier)
        self.agent.addActionListener(self)
        self.state = _AGENT_STATE_NONE
    
    def idle(self):
        """@return: None"""
        self.state = _AGENT_STATE_IDLE        
        
    def onInstanceActionFinished(self, instance, action):
        """@type instance: ???
           @param instance: ???
           @type action: ???
           @param action: ???
           @return: None"""
        # First we reset the next behavior 
        act = self.nextAction
        self.nextAction = None 
        self.idle()
        
        if act:
            act.execute()
        try:
            animtion = self.animation_queue.popleft()
            self.animate(**animtion)
        except IndexError:
            self.idle()
          
    def onInstanceActionFrame(self, instance, action, frame):
        pass
         
    def getLocation(self):
        """Get the agents position as a fife.Location object. 
           @rtype: fife.Location
           @return: the location of the agent"""
        return self.agent.getLocation()
    
        
    def talk(self, pc):
        """Makes the agent ready to talk to the PC
           @return: None"""
        self.state = _AGENT_STATE_TALK
        self.pc = pc.behaviour.agent
        self.clear_animations()
        self.idle()
        
    def animate(self, action, direction = None, repeating = False):
        """Perform an animation"""
        direction = direction or self.agent.getFacingLocation()
        self.agent.act(action, direction, repeating)
        
    def queue_animation(self, action, direction = None, repeating = False):
        """Add an action to the queue"""
        self.animation_queue.append({"action": action, "direction": direction,
                                  "repeating": repeating})
        
    def clear_animations(self):
        """Remove all actions from the queue"""
        self.animation_queue.clear()
