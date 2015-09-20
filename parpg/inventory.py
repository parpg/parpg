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

import copy

# TODO: many missing function definitions in this code

class Inventory(Container):
    """The class to represent inventory 'model': allow operations with
       inventory contents, perform weight/bulk calculations, etc"""
    def __init__(self, **kwargs):
        """Initialise instance"""
        Container.__init__(self,  **kwargs)
        self.items = {"head": Slot(), "neck": Slot(),
                      "shoulders": Slot(), "chest": Slot(),
                      "abdomen": Slot(), "left_arm": Slot(),
                      "right_arm": Slot(),"groin": Slot(),
                      "hips": Slot(), "left_leg": Slot(),
                      "right_leg": Slot(), "left_hand": Slot(),
                      "right_hand": Slot(), "ready": Container(),
                      "backpack": Container()}
        for key, item in self.items.iteritems():
            item.name = key
            kwargs = {}
            kwargs["container"] = item
            item.setScript("onPlaceItem", self.onChildPlaceItem, kwargs = kwargs)
        self.item_lookup = {}
        
    def onChildPlaceItem(self, container):
        for item in container.items.itervalues():
            self.item_lookup[item.ID] = container.name  

    def placeItem(self, item, index=None):
        self.items["backpack"].placeItem(item, index)
        #self.item_lookup[item.ID] = "backpack"
        
    def takeItem(self, item):
        if not item.ID in self.item_lookup:
            raise ValueError ('I do not contain this item: %s' % item)
        self.items[self.item_lookup[item.ID]].takeItem(item)
        del self.item_lookup[item.ID]

    def removeItem(self, item):
        if not item.ID in self.item_lookup:
            raise ValueError ('I do not contain this item: %s' % item)
        self.items[self.item_lookup[item.ID]].removeItem(item)
        del self.item_lookup[item.ID]

    def replaceItem(self, old_item, new_item):
        """Replaces the old item with the new one
        @param old_item: Old item which is removed
        @type old_item: Carryable
        @param new_item: New item which is added
        @type new_item: Carryable
        """
        if not old_item.ID in self.item_lookup:
            raise ValueError ('I do not contain this item: %s' % old_item)
        self.items[self.item_lookup[old_item.ID]]\
            .replaceItem(old_item, new_item)

    def getWeight(self):
        """Total weight of all items in container + container's own weight"""
        return sum((item.weight for item in self.items.values()))

    def setWeightDummy(self, weight):
        pass

    weight = property(getWeight, setWeightDummy, "Total weight of container")


    def count(self, item_type = ""):
        return sum(item.count(item_type) for item in self.items.values())
    
    def takeOff(self, item):
        return self.moveItemToSlot(item, "backpack")

    def moveItemToSlot(self,item,slot,index=None):
        if not slot in self.items:
            raise(ValueError("%s: No such slot" % slot))

        if item.ID in self.item_lookup:
            self.items[self.item_lookup[item.ID]].takeItem(item)
        try:
            self.items[slot].placeItem(item, index)
        except Container.SlotBusy:
            if index == None :
                offending_item = self.items[slot].items[0]
            else :
                offending_item = self.items[slot].items[index]
            self.items[slot].takeItem(offending_item)
            self.items[slot].placeItem(item, index)
            self.placeItem(offending_item)
        self.item_lookup[item.ID] = slot
     
    def getItemsInSlot(self, slot, index=None):
        if not slot in self.items:
            raise(ValueError("%s: No such slot" % slot))
        if index != None:
            return self.items[slot].items.get(index)
        else:
            return copy.copy(self.items[slot].items)

    def isSlotEmpty(self, slot, index=None):
        if not slot in self.items:
            raise(ValueError("%s: No such slot" % slot))
        if index == None:
            return self.items[slot].count() == 0
        else:
            return not index in self.items[slot].items
                 

    def has(self, item_ID):
        return item_ID in self.item_lookup

    def findItemByID(self, ID):
        if ID not in self.item_lookup:
            return None
        return self.items[self.item_lookup[ID]].findItemByID(ID)

    def findItem(self, **kwargs):
        """Find an item in inventory by various attributes. All parameters 
           are optional.
           @type name: String
           @param name: Object name. If the name is non-unique, 
                        first matching object is returned
           @type kind: String
           @param kind: One of the possible object kinds like "openable" or 
                        "weapon" (see base.py)
           @return: The item matching criteria or None if none was found"""
        for slot in self.items:
            item_found = self.items[slot].findItem(**kwargs)
            if item_found != None:
                return item_found
        return None

    def __repr__(self):
        return "[Inventory contents: " + \
                            reduce((lambda a,b: str(a) 
                                    + ', ' + str(b)), 
                                    self.items.values()) + " ]"

    def serializeInventory(self):
        """Returns the inventory items as a list"""
        inventory = []
        inventory.extend(self.items["backpack"].serializeItems())
        for key, slot in self.items.iteritems():
            if key == "ready" or key == "backpack":
                continue
            elif len(slot.items) > 0:
                item = slot.items[0]
                item_dict = item.getStateForSaving()
                item_dict["slot"] = key                                
                item_dict["type"] = type(item).__name__ 
                inventory.append(item_dict)
        return inventory
            
    def getStateForSaving(self):
        """Returns state for saving
        """
        state = {}
        state["Inventory"] = self.serializeInventory()
        return state
