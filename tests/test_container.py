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

import unittest

from bGrease.world import BaseWorld
from bGrease.entity import Entity
from parpg.components import containable, container

class  TestContainer(unittest.TestCase):
    class GameWorld(BaseWorld):
        """GameWorld"""

        def configure(self):
            """Set up the world"""
            self.components.containable = containable.Containable()
            self.components.container = container.Container()

    class Inventory(Entity):
        """Enity representing an Iventory"""
        
        def __init__(self, world, max_bulk, slots):
            """Constructor"""
            self.container.children = slots
            self.container.max_bulk = max_bulk
                
    
    class Item(Entity):
        def __init__(self, world, bulk):
            """Constructor"""
            self.containable.bulk = bulk
        
    def setUp(self):
        unittest.TestCase.setUp(self)        
        self.world = self.GameWorld()
        slots_15 = list()
        slots_25 = list()
        for i in xrange(3):
            slots_15.append(None)
        
        for i in xrange(10):
            slots_25.append(None)

        self.inv_15 = self.Inventory(self.world, 15, slots_15)
        self.inv_25 = self.Inventory(self.world, 25, slots_25)
        self.dagger_1 = self.Item(self.world, 2)
        self.sword_1 = self.Item(self.world, 4)
        self.axe_1 = self.Item(self.world, 4)
        self.mace_1 = self.Item(self.world, 5)
        self.spear_1 = self.Item(self.world, 8)
        self.dagger_2 = self.Item(self.world, 2)
        self.sword_2 = self.Item(self.world, 4)
        self.axe_2 = self.Item(self.world, 4)
        self.mace_2 = self.Item(self.world, 5)
        self.spear_2 = self.Item(self.world, 8)
        
    def tearDown(self):
        self.dagger_1 = None
        self.sword_1 = None
        self.axe_1 = None
        self.mace_1 = None
        self.spear_1 = None
        self.dagger_2 = None
        self.sword_2 = None
        self.axe_2 = None
        self.mace_2 = None
        self.spear_2 = None        
        self.inv_15 = None
        self.inv_25 = None
        self.world = None

    def test_State(self):
        for child in self.inv_15.container.children:
            self.assertIsNone(child)

        for child in self.inv_25.container.children:
            self.assertIsNone(child)            
        
    def test_PutTake(self):
        self.assertIsNone(container.get_item(self.inv_15.container, 0))
        
        container.put_item(self.inv_15.container, self.sword_1.containable, 0)        
        self.assertIsNotNone(container.get_item(self.inv_15.container, 0))        
        self.assertListEqual(self.inv_15.container.children, self.sword_1.containable.container.children)
        self.assertEqual(self.inv_15.container.children[0].container, self.sword_1.containable.container)
        self.assertEqual(self.inv_15.container.children[0].slot, self.sword_1.containable.slot)
        
        container.take_item(self.inv_15.container, 0)
        self.assertIsNone(self.inv_15.container.children[0])
        
    def test_Swap(self):
        self.assertIsNone(self.inv_15.container.children[0])
        
        container.put_item(self.inv_15.container, self.sword_1.containable, 0)        
        sword1 = container.get_item(self.inv_15.container, 0)
        self.assertEqual(sword1.container, self.sword_1.containable.container)
        self.assertEqual(sword1.slot, self.sword_1.containable.slot)
        
        sword2 = container.put_item(self.inv_15.container, self.dagger_1.containable, 0)
        self.assertEqual(sword2.container, sword1.container)
        self.assertEqual(sword2.slot, sword1.slot)

        self.assertIsNotNone(container.get_item(self.inv_15.container, 0))        
        self.assertListEqual(self.inv_15.container.children, self.dagger_1.containable.container.children)
        self.assertEqual(self.inv_15.container.children[0].container, self.dagger_1.containable.container)
        self.assertEqual(self.inv_15.container.children[0].slot, self.dagger_1.containable.slot)
        
    def test_BulkSlots(self):
        container.put_item(self.inv_15.container, self.sword_1.containable)
        container.put_item(self.inv_25.container, self.sword_2.containable)
        self.assertEqual(container.get_total_bulk(self.inv_15.container), self.sword_1.containable.bulk)
        self.assertEqual(container.get_total_bulk(self.inv_25.container), self.sword_2.containable.bulk)
        
        container.put_item(self.inv_15.container, self.axe_1.containable)
        container.put_item(self.inv_25.container, self.axe_2.containable)
        self.assertEqual(container.get_total_bulk(self.inv_15.container), container.get_total_bulk(self.inv_25.container))
        
        self.assertRaises(container.BulkLimitError, container.put_item, self.inv_15.container, self.spear_1.containable)
        container.put_item(self.inv_25.container, self.spear_2.containable)

        container.put_item(self.inv_15.container, self.dagger_1.containable)
        container.put_item(self.inv_25.container, self.dagger_2.containable)
        self.assertNotEqual(container.get_total_bulk(self.inv_15.container), container.get_total_bulk(self.inv_25.container))

        self.assertRaises(container.NoFreeSlotError, container.put_item, self.inv_15.container, self.mace_1.containable)
        container.put_item(self.inv_25.container, self.mace_2.containable)
