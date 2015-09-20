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
from parpg.components import Equipable
from parpg.components import Equip
from parpg.components import equip

import unittest

class TestEquip(unittest.TestCase):
           
    class GameWorld(BaseWorld):
        """GameWorld"""

        def configure(self):
            """Set up the world"""
            self.components.equipable = Equipable()
            self.components.equip = Equip()

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.world = self.GameWorld()
        self.wearer = Entity(self.world)
        self.arms_item = Entity(self.world)
        self.arms_item.equipable.possible_slots = ["l_arm", "r_arm"]
        self.l_arm_item = Entity(self.world)
        self.l_arm_item.equipable.possible_slots = ["l_arm"]
        self.r_arm_item = Entity(self.world)
        self.r_arm_item.equipable.possible_slots = ["r_arm"]
        self.t_arm_item = Entity(self.world)
        self.t_arm_item.equipable.possible_slots = ["t_arm"]
        
    def test_equip_and_take(self):
        print "Raise SlotInvalidError"
        self.assertRaises(equip.SlotInvalidError, equip.equip, self.wearer.equip, self.t_arm_item.equipable, "t_arm")
        print "Raise CannotBeEquippedInSlot"
        self.assertRaises(equip.CannotBeEquippedInSlot, equip.equip, self.wearer.equip, self.l_arm_item.equipable, "r_arm")
        print "Equip l_arm"
        equip.equip(self.wearer.equip, self.l_arm_item.equipable, "l_arm")
        print "Equip r_arm"
        equip.equip(self.wearer.equip, self.r_arm_item.equipable, "r_arm")
        self.assertIsNotNone(self.l_arm_item.equipable.wearer)
        print "Raise AlreadyEquipped"
        self.assertRaises(equip.AlreadyEquippedError, equip.equip, self.wearer.equip, self.l_arm_item.equipable, "r_arm")
        print "Switch r_arm with arms"
        equip.equip(self.wearer.equip, self.arms_item.equipable, "r_arm")
        self.assertIsNone(self.r_arm_item.equipable.wearer)
        self.assertIsNotNone(self.arms_item.equipable.wearer)
        print "Take l_arm"
        equip.take_equipable( self.wearer.equip, self.l_arm_item.equipable.in_slot)
        self.assertIsNone(self.l_arm_item.equipable.wearer)
        
    def tearDown(self):
        self.world = None
        self.wearer = None
        self.arms_item = None
        self.l_arm_item = None
        self.r_arm_item = None
        self.t_arm_item = None


