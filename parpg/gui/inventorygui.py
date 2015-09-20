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
import logging
from types import StringTypes

from fife.extensions.pychan.tools import callbackWithArguments as cbwa
from fife.extensions import pychan
from slot import Slot
from fife.extensions.pychan.attrs import UnicodeAttr

from parpg.gui import drag_drop_data as data_drag
from parpg.gui.containergui_base import ContainerGUIBase
from parpg.entities.action import ACTIONS
from parpg.components import equip, equipable, container
from parpg.entities import General

logger = logging.getLogger('action')

class EquipmentSlot(pychan.VBox):
    def __init__(self, min_size=(50, 50),
                 max_size=(50, 50), margins=None,
                 **kwargs):
        pychan.VBox.__init__(self, min_size=min_size, max_size=max_size,
                             **kwargs)
        self.background_image = 'gui/inv_images/inv_background.png'
        icon = Slot(name="Icon")
        self.addChild(icon)
        self.adaptLayout()
        if self.parent is not None:
            self.beforeShow()

    @property
    def image(self):
        icon = self.findChildByName("Icon")
        return icon.image
    
    @image.setter
    def image(self, image):
        icon = self.findChildByName("Icon")
        icon.image = image        

class InventoryGrid(pychan.VBox):
    ATTRIBUTES = pychan.VBox.ATTRIBUTES + [pychan.attrs.PointAttr('grid_size'), 
                                            pychan.attrs.PointAttr('cell_size')]
    
    
    def _setNColumns(self, n_columns):
        n_rows = self.grid_size[1]
        self.grid_size = (n_columns, n_rows)
    
    def _getNColumns(self):
        n_columns = self.grid_size[0]
        return n_columns
    n_columns = property(fget=_getNColumns, fset=_setNColumns)
    
    def _setNRows(self, n_rows):
        n_columns = self.grid_size[0]
        self.grid_size = (n_columns, n_rows)
    
    def _getNRows(self):
        n_rows = self.grid_size[1]
        return n_rows
    n_rows = property(fget=_getNRows, fset=_getNColumns)
    
    def _setGridSize(self, grid_size):
        n_columns, n_rows = grid_size
        self.removeAllChildren()
        for row_n in xrange(n_rows):
            row_size = (n_columns * self.cell_size[0], self.cell_size[1])
            row = pychan.HBox(min_size=row_size, max_size=row_size,
                              padding=self.padding)
            row.border_size = 1
            row.opaque = 0
            for column_n in xrange(n_columns):
                index = (row_n * n_columns + column_n)
                slot = Slot(min_size=(self.cell_size), 
                                    max_size=(self.cell_size))
                slot.border_size = 1
                slot.name = "Slot_%d" % index
                slot.index = index
                slot.image = None
                slot.size = self.cell_size
                row.addChild(slot)
            self.addChild(row)
        self.min_size = ((n_columns * self.cell_size[0]) + 2, 
                        (n_rows * self.cell_size[1]) + 2)
        self.max_size = self.min_size
    
    def _getGridSize(self):
        n_rows = len(self.children)
        n_columns = len(self.children[0].children)
        return (n_rows, n_columns)
    grid_size = property(fget=_getGridSize, fset=_setGridSize)
    
    def getSlot(self, row_or_index, col=None):
        if col:
            index = row * self.n_columns + col
        else:
            index = row_or_index
        return self.findChildByName("Slot_%d" % index)
    
    def __init__(self, 
                grid_size=(2, 2), 
                cell_size=(50, 50), 
                parent = None, 
                name = None,
                size = None,
                min_size = None, 
                max_size = None, 
                helptext = None, 
                position = None, 
                style = None, 
                hexpand = None,
                vexpand = None,
                font = None,
                base_color = None,
                background_color = None,
                foreground_color = None,
                selection_color = None,
                position_technique = None,
                is_focusable = None,
                comment = None,
                background_image = None,
                _real_widget = None):
        pychan.VBox.__init__(self, 
                            parent=parent, 
                            name=name, 
                            size=size, 
                            min_size=min_size, 
                            max_size=max_size,
                            helptext=helptext, 
                            position=position,
                            style=style, 
                            hexpand=hexpand, 
                            vexpand=vexpand,
                            font=font,
                            base_color=base_color,
                            background_color=background_color,
                            foreground_color=foreground_color,
                            selection_color=selection_color,
                            border_size=1,
                            position_technique=position_technique,
                            is_focusable=is_focusable,
                            comment=comment,
                            padding=0,
                            background_image=background_image,
                            opaque=0,
                            margins=None,
                            _real_widget=_real_widget)
        self.cell_size = cell_size
        self.grid_size = grid_size


class EquipmentGUI(ContainerGUIBase):
    def __init__(self, controller, gui, equip, callbacks, slot_size = (50, 50)):
        ContainerGUIBase.__init__(self, controller, gui)
        self.equip = equip
        self.equip_to_gui = {
            "head": "headSlot",
            "neck": "neckSlot",
            "body": "shirtSlot",
            "belt": "beltSlot",
            "leg": "pantsSlot",
            "feet": "bootsSlot",
            "l_arm": "leftHandSlot",
            "r_arm": "rightHandSlot",
        }
        self.setSlotEvents()
        self.slot_size = slot_size
        
    def updateImages(self):
        for eq_slot, gui_slot in self.equip_to_gui.iteritems():
            widget = self.gui.findChildByName(gui_slot)            
            equipable = equip.get_equipable(self.equip, eq_slot)
            widget.item = equipable.entity if equipable else None
            self.updateImage(widget) 
               
    def updateImage(self, slot):
        assert(isinstance(slot, EquipmentSlot))
        if (slot.item):
            image = slot.item.containable.image
        else:
            image = None
        slot.image = image
                
    def dragObject(self, obj):
        """Drag the selected object.
           @type obj: string
           @param obj: The name of the object
           @return: None"""
        # get the widget from the gui with the name obj
        drag_widget = self.gui.findChildByName(obj)
        drag_item = drag_widget.item
        # only drag if the widget is not empty
        if (drag_item != None):
            if isinstance(drag_item, General):
                drag_item = drag_item.containable
            elif isinstance(drag_item, equipable):
                drag_item = drag_item.entity.containable
            drag_eq = drag_item.entity.equipable
            # get the image of the widget
            image = drag_widget.image
            self.setDragData(drag_item, image, image)
            equip.take_equipable(self.equip, drag_eq.in_slot)
            
            # after dragging the 'item', set the widgets' images
            # so that it has it's default 'empty' images
            drag_widget.item = None
            self.updateImage(drag_widget)

    def dropObject(self, obj):
        """Drops the object being dropped
           @type obj: string
           @param obj: The name of the object
           @return: None"""
        try:
            drop_widget = self.gui.findChildByName(obj)
            drop_slot = drop_widget.slot
            replace_item = None
    
            if data_drag.dragging:
                drag_item = data_drag.dragged_item.entity
                if drag_item.equipable:
                    drag_item = drag_item.equipable
                else:
                    return                
                #this will get the replacement item and the data for drag_drop
                #if there is an item all ready occupying the slot
                replace_item = (
                    equip.equip(self.equip, drag_item, drop_slot)
                )
                
            #if there was no item the stop dragging and reset cursor
            if replace_item:
                image = drop_widget.image
                self.setDragData(replace_item.entity.containable, image, image)
            else:
                data_drag.dragging = False
                #reset the mouse cursor to the normal cursor
                self.controller.resetMouseCursor()
            drop_widget.item = drag_item.entity
            self.updateImage(drop_widget)
        except (equip.AlreadyEquippedError, equip.CannotBeEquippedInSlot):
            #Do we want to notify the player why the item can't be dropped?
            pass

    def mousePressedOnSlot(self, event, widget):
        if event.getButton() == event.LEFT:
            self.dragDrop(widget.name)

    def setSlotEvents(self):
        events_to_map = {}
        for eq_slot, gui_slot in self.equip_to_gui.iteritems():
            widget = self.gui.findChildByName(gui_slot)
            slot_name = widget.name
            widget.slot = eq_slot
            events_to_map[slot_name + "/mousePressed"] = (
                self.mousePressedOnSlot
            )
            events_to_map[slot_name + "/mouseReleased"] = self.showContextMenu

        self.gui.mapEvents(events_to_map)            
        
class InventoryGUI(ContainerGUIBase):
    def __init__(self, controller, gui, container, callbacks):
        ContainerGUIBase.__init__(self, controller, gui)
        self.grid = self.gui.findChildByName("Grid")
        assert(isinstance(self.grid, InventoryGrid))
        self.container = container
        self.setSlotEvents()

    def setSlotEvents(self):
        slot_count = self.grid.n_rows * self.grid.n_columns
        events_to_map = {}
        for counter in xrange(0, slot_count):
            widget = self.grid.getSlot(counter)
            slot_name = widget.name
            widget.index = counter
            events_to_map[slot_name + "/mousePressed"] = (
                self.mousePressedOnSlot
            )
            events_to_map[slot_name + "/mouseReleased"] = self.showContextMenu

        self.grid.mapEvents(events_to_map)
        self.updateImages()

    def updateImages(self):
        for index, child in enumerate(self.container.children):
            slot = self.grid.getSlot(index)
            if child:
                slot.item = child.entity
            else:
                slot.item = None
            self.updateImage(slot)
            
    def updateImage(self, slot):
        assert(isinstance(slot, Slot))
        if (slot.item):
            image = slot.item.containable.image

        else:
            image = None
        slot.image = image
        
    def mousePressedOnSlot(self, event, widget):
        if event.getButton() == event.LEFT:
            self.dragDrop(widget.name)

    def dragObject(self, obj):
        """Drag the selected object.
           @type obj: string
           @param obj: The name of the object
           @return: None"""
        # get the widget from the gui with the name obj
        drag_widget = self.gui.findChild(name = obj)
        drag_item = drag_widget.item
        # only drag if the widget is not empty
        if (drag_item != None):
            if isinstance(drag_item, General):
                drag_item = drag_item.containable
            # get the image of the widget
            image = drag_widget.image
            self.setDragData(drag_item, image, image)
            container.take_item(self.container, drag_item.slot)
            
            # after dragging the 'item', set the widgets' images
            # so that it has it's default 'empty' images
            drag_widget.item = None
            self.updateImage(drag_widget)
            
    def dropObject(self, obj):
        """Drops the object being dropped
           @type obj: string
           @param obj: The name of the object
           @return: None"""
        try:
            drop_widget = self.gui.findChildByName(obj)
            drop_index = drop_widget.index
            replace_item = None
    
            if data_drag.dragging:
                drag_item = data_drag.dragged_item
                #this will get the replacement item and the data for drag_drop if
                ## there is an item all ready occupying the slot
                replace_item = (
                    container.put_item(self.container, drag_item, drop_index)
                )
                
            #if there was no item the stop dragging and reset cursor
            if replace_item:
                image = drop_widget.image
                self.setDragData(replace_item, image, image)
            else:
                data_drag.dragging = False
                #reset the mouse cursor to the normal cursor
                self.controller.resetMouseCursor()
            drop_widget.item = drag_item.entity
            self.updateImage(drop_widget)
        except (container.BulkLimitError):
            #Do we want to notify the player why the item can't be dropped?
            pass
        
    def createMenuItems(self, item, actions):
        """Creates context menu items for the InventoryGUI"""
        menu_actions = ContainerGUIBase.createMenuItems(self, item, actions)
        param_dict = {}
        param_dict["controller"] = self.controller
        param_dict["commands"] = {}
        param_dict["item"] = item.containable
        param_dict["container_gui"] = self
        menu_actions.append(["Drop",
                             "Drop", 
                             self.executeMenuItem, 
                             ACTIONS["DropFromInventory"](**param_dict)])        
        return menu_actions
    
class CharacterGUI(object):
    def __init__(self, controller, gui, container, equip, callbacks):
        self.engine = controller.engine
        self.inventory_shown = False
        if isinstance(gui, pychan.Widget):
            self.gui = gui
        elif isinstance(gui, StringTypes):
            xml_file = vfs.VFS.open(gui)
            self.gui = pychan.loadXML(xml_file)
        else:
            self.gui = pychan.loadXML(gui)
        
        render_backend = self.engine.getRenderBackend()
        screen_mode = render_backend.getCurrentScreenMode()
        screen_width, screen_height = (screen_mode.getWidth(),
                                       screen_mode.getHeight())
        widget_width, widget_height = self.gui.size
        self.gui.position = ((screen_width - widget_width) / 2,
                             (screen_height - widget_height) / 2)
        self.equip_gui = EquipmentGUI(
            controller,
            self.gui.findChildByName("equipmentPage"),
            equip, callbacks
        )
        self.inv_gui = InventoryGUI(
            controller,
            self.gui.findChildByName("inventoryPage"),
            container, callbacks
        )
    
    def toggleInventory(self, toggleImage=True):
        """Pause the game and enter the inventory screen, or close the
           inventory screen and resume the game.
           @type toggleImage: bool
           @param toggleImage:
               Call toggleInventoryCallback if True. Toggling via a
               keypress requires that we toggle the Hud inventory image
               explicitly. Clicking on the Hud inventory button toggles the
               image implicitly, so we don't change it.
           @return: None"""
        if not self.inventory_shown:
            self.showInventory()
            self.inventory_shown = True
        else:
            self.closeInventory()
            self.inventory_shown = False
            
    def updateImages(self):
        self.equip_gui.updateImages()
        self.inv_gui.updateImages()
    
    def showInventory(self):
        self.updateImages()
        self.gui.show()
    
    def closeInventory(self):
        self.gui.hide()
        
