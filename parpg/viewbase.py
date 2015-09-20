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

class ViewBase(object):
    """Base class for views"""
    def __init__(self, engine, model):
        """Constructor for engine
           @param engine: A fife.Engine instance
           @type engine: fife.Engine
           @param model: a script.GameModel instance
           @type model: script.GameModel 
           """
        self.engine = engine
        self.model = model
