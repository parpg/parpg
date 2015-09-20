#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#   
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

from copy import deepcopy

from base import Base


class FifeAgent(Base):
    """Component that stores the values for a fife agent"""
    
    def __init__(self):
        """Constructor"""
        Base.__init__(self, layer=object, behaviour=object)

    @property
    def saveable_fields(self):
        fields = self.fields.keys()
        fields.remove("layer")
        fields.remove("behaviour")
        return fields

        
def setup_behaviour(agent):
    """Attach the behaviour to the layer"""
    if agent.behaviour:   
        agent.behaviour.attachToLayer(agent.entity.getID(), agent.layer)
        
def approach(agent, target_or_location, action):
    if agent.behaviour: 
        agent.behaviour.approach(target_or_location, action)
        
commands = {"approach":approach}