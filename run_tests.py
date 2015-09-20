#!/usr/bin/env python2

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


import sys, os, unittest

#Check if config.py exists. Get 'fife_path' from config
try:
    import config
    sys.path.append(config.fife_path)
except:
    pass

def _jp(path):
    return os.path.sep.join(path.split('/'))

_paths = ('../../engine/swigwrappers/python', '../../engine/extensions', 'tests', "src")
test_suite = unittest.TestSuite()

for p in _paths:
    if p not in sys.path:
        sys.path.append(_jp(p))

for p in os.listdir("tests") :
    if p[-3:] == ".py" :
        test_suite.addTest(unittest.TestLoader().loadTestsFromName(p[:-3]))

unittest.TextTestRunner(verbosity=2).run(test_suite)
