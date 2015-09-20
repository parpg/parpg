from bGrease.grease_fife.world import World
from bGrease.component import Component

from bGrease.grease_fife.mode import Mode
from parpg import components
from parpg.components.fifeagent import commands
from parpg.systems import ScriptingSystem
from parpg.entities.action import ACTIONS

class PARPGWorld(World):

    def __init__(self, engine):
        '''
        Constructor
        @param engine: Instance of the active fife engine
        @type engine: fife.Engine
        '''
        World.__init__(self, engine)

        
    def configure(self):
        """Configure the game world's components, systems and renderers"""
        for name, component in components.components.iteritems():
            setattr(self.components, name, component)
        self.systems.scripting = ScriptingSystem(commands, ACTIONS)
