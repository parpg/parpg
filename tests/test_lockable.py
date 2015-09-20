#!/usr/bin/env python

# This file is part of PARPG.
# 
# PARPG is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PARPG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PARPG.  If not, see <http://www.gnu.org/licenses/>.

from bGrease.world import BaseWorld
from bGrease.entity import Entity
from parpg.components import lockable

import unittest

class TestLockable(unittest.TestCase):
    class Lock(Entity):
        """Enity representing an Lock"""
        
        def __init__(self, world, locked, closed):
            """Constructor"""
            self.lockable.locked = locked
            self.lockable.closed = closed

    class GameWorld(BaseWorld):
        """GameWorld"""

        def configure(self):
            """Set up the world"""
            self.components.lockable = lockable.Lockable()

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.world = self.GameWorld()
        self.lock = self.Lock(self.world, False, True)
        
    def tearDown(self):
        self.lock = None
        self.world = None
        
    def testOpenClose(self):
        lockable.open(self.lock.lockable)
        self.assertFalse(self.lock.lockable.closed)
        lockable.close(self.lock.lockable)
        self.assertTrue(self.lock.lockable.closed)
         
    def testLockUnlock(self):
        lockable.lock(self.lock.lockable)
        self.assertTrue(self.lock.lockable.locked)
        self.assertRaises(lockable.LockedError, lockable.open, self.lock.lockable)
        lockable.unlock(self.lock.lockable)
        self.assertFalse(self.lock.lockable.locked)
        lockable.open(self.lock.lockable)
        self.assertRaises(lockable.OpenError, lockable.lock, self.lock.lockable)

