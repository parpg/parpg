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

class Container(Base):
    """
    Component that allows an entity to contain one or more child entities.
    """
    
    def __init__(self):
        Base.__init__(self, children=list, max_bulk=int)

    @property
    def saveable_fields(self):
        fields = self.fields.keys()
        fields.remove("children")
        return fields



class BulkLimitError(Exception):
    """Error that gets raised when the item would exceed the 
    bulk limit of the container."""
    
    def __init__(self, bulk, max_bulk):
        self.bulk = bulk
        self.max_bulk = max_bulk
    
    def __str__(self):
        return "Item would exceed the bulk limit of the container."

class NoFreeSlotError(Exception):
    """Error that gets raised when the container has no free slots."""
  
    def __str__(self):
        return "Container can't hold any more items."
    
def get_free_slot(container):
    """Returns the first slot of the container that is not occupied."""
    index = 0
    for child in container.children:
        if not child:
            return index
        index += 1
    raise NoFreeSlotError

def get_total_bulk(container):
    """Returns the bulk of all items in the container."""
    total_bulk = 0
    for child in container.children:
        if child:
            total_bulk += child.bulk
    return total_bulk

def get_total_weight(container):
    """Returns the weight of all items in the container."""
    total_weight = 0
    for child in container.children:
        if child:
            total_weight += child.weight
    return total_weight

def get_item(container, slot_or_type):
    """Returns the item that is in the slot, or has the given type."""
    if type(slot_or_type) == int:
        if len(container.children) >= (slot_or_type + 1):
            return container.children[slot_or_type]
    else:
        for child in container.children:
            if child and child.item_type == slot_or_type:
                return child
                
    return None

def remove_item(container, slot_or_type):
    """Removes the item at the given slot, or with the given type."""
    if type(slot_or_type) == int:
        item = get_item(container, slot_or_type)
        if item:
            container.children[slot_or_type] = None
            item.container = None
            item.slot = -1
    else:
        for child in container.children:
            if child and child.item_type == slot_or_type:
                container.children[child.slot] = None
                child.container = None
                child.slot = -1

def take_item(container, slot_or_type):
    """Moves the item at the given slot, or with the given type,
    out of the container and returns it."""
    item = get_item(container, slot_or_type)
    if item:
        remove_item(container, slot_or_type)
    return item

def put_item(container, item, slot=-1):
    """Puts the item at the given slot in the container.
    Returns the item previously at the slot."""
    if slot == -1:
        slot = get_free_slot(container)
    total_bulk = get_total_bulk(container)
    total_bulk += item.bulk
    old_item = get_item(container, slot)
    if old_item:
        total_bulk -= old_item.bulk
    if total_bulk > container.max_bulk:
        raise BulkLimitError(total_bulk, container.max_bulk)
    remove_item(container, slot)
    container.children[slot] = item
    if item.container:
        remove_item(item.container, item.slot)
    item.container = container
    item.slot = slot
    return old_item