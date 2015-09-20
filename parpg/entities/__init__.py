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

import sys

from general import General

def createEntity(info, identifier, world, extra = None):
    """Called when we need to get an actual object.
       @type info: dict
       @param info: stores information about the object we want to create
       @type extra: dict
       @param extra: stores additionally required attributes
       @return: the object"""
    # First, we try to get the world, which every game_obj needs.
    extra = extra or {}

    # add the extra info
    for key, val in extra.items():
        info[key].update(val)

    # this is for testing purposes
    new_ent = General(world, identifier)
    for component, data in info.items():
        comp_obj = getattr(new_ent, component)
        for key, value in data.items():
            setattr(comp_obj, key, value)
    return new_ent
