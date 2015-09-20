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

from collections import deque
from copy import deepcopy

from bGrease import System

class Script(object):
    """Script object"""

    def __init__(self, actions, system):
        """Constructor"""
        assert(isinstance(actions, deque))
        self.actions = actions
        assert(isinstance(system, ScriptingSystem))
        self.system = system
        self.reset()

    def reset(self):
        """Resets the state of the script"""
        self.running_actions = deepcopy(self.actions)
        self.running = False
        self.finished = False
        self.time = 0
        self.wait = 0
        self.cur_action = None
    
    def update(self, time):
        """Advance the script"""
        if not self.running:
            return
        if self.cur_action and not self.cur_action.executed:
            return
        self.time += time
        if self.wait <= self.time:
            self.time = 0		    
            try:
                globals, locals = self.system.game_state.getGameEnvironment()
                action_data = self.running_actions.popleft()
                action = self.system.actions[action_data[0]]
                action_params = eval(
                                     action_data[1], 
                                     globals, locals
                                     ) 
                if not (isinstance(action_params, list) 
                        or isinstance(action_params, tuple)):
                    action_params = [action_params]
                self.cur_action = action(self.system.world, *action_params)
                self.wait = action_data[2]
                if len(action_data) >= 4:
                    vals = (
                        eval(action_data[4], globals, locals) 
                        if len(action_data) > 4
                        else ()
                    )
                    command = action_data[3]
                    self.system.commands[command](
                        *vals, 
                        action=self.cur_action
                    )
                else:
                    self.cur_action.execute()
            except IndexError:
                self.finished = True
                self.running = False


class ScriptingSystem(System):
    """
    System responsible for managing scripts attached to entities to define 
    their behavior.
    """

    def __init__(self, commands, actions):
        """Constructor"""
        self.commands = commands
        self.actions = actions
        self.game_state = None
        self.reset()

    def reset(self):
        """Resets the script and condition collections"""
        self.scripts = {}
        self.conditions = []

    def step(self, dt):
        """Execute a time step for the system. Must be defined
        by all system classes.

        :param dt: Time since last step invocation
        :type dt: float
        """
        for condition_data in self.conditions:
            condition = condition_data[0]
            script_name = condition_data[1]
            if not self.scripts.has_key(script_name):
                return
            script = self.scripts[script_name]
            if (eval(condition, *self.game_state.getGameEnvironment()) 
                and not script.running):
                script.running = True
        for script in self.scripts.itervalues():
            assert(isinstance(script, Script))
            if script.finished:
                script.reset()
            elif script.running:
                script.update(dt)
                
    def setScript(self, name, actions):
        """Sets a script.
        @param name: The name of the script
        @param actions: What the script does
        @type actions: deque or iterable
        """
        if not(isinstance(actions, deque)):
            actions = deque(actions)
        self.scripts[name] = Script(actions, 
                                    self
                                    )
        
    def addCondition(self, condition, script_name):
        """Adds a condition.
        @param condition: Condition which will be evaluated
        @param script_name: Name of the script that will be executed if the
        condition evaluates to True.
        """
        self.conditions.append((condition, script_name))
    
    
    def runScript(self, name):
        """Runs a script with the given name
        @param name: The name of the script"""
        if self.scripts.has_key(name):
            self.scripts[name].running = True
        
    
