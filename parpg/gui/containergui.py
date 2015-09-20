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
from fife.extensions.pychan.tools import callbackWithArguments as cbwa

from parpg.gui.containergui_base import ContainerGUIBase
from parpg.gui import drag_drop_data as data_drag
from parpg.components import container

class ContainerGUI(ContainerGUIBase):
    def __init__(self, controller, title, container):
        """A class to create a window showing the contents of a container.
           @param controller: The current Controller
           @type controller: Class derived from ControllerBase
           @param title: The title of the window
           @type title: string
           @param container: A container to represent
           @type container: parpg.components.Container
           @return: None"""
        super(ContainerGUI, self).__init__(controller, "gui/container_base.xml")
        self.gui.findChild(name="topWindow").title = title
        
        self.empty_images = dict()
        self.container = container
        self.events_to_map = {}        
        self.buttons = ("Slot1", "Slot2", "Slot3",
                        "Slot4", "Slot5", "Slot6",
                        "Slot7", "Slot8", "Slot9")         
    
    def updateImages(self):
        for index, button in enumerate(self.buttons):
            widget = self.gui.findChild(name=button)            
            widget.item = container.get_item(self.container, index)
            self.updateImage(widget) 
               
    def updateImage(self, button):
        if (button.item == None):
            image = self.empty_images[button.name]
        else:
            image = button.item.image
        button.up_image = image
        button.down_image = image
        button.hover_image = image

    def dragObject(self, obj):
        """Drag the selected object.
           @type obj: string
           @param obj: The name of the object within
                       the dictionary 'self.buttons'
           @return: None"""
        # get the widget from the gui with the name obj
        drag_widget = self.gui.findChild(name = obj)
        drag_item = drag_widget.item
        # only drag if the widget is not empty
        if (drag_item != None):
            # get the item that the widget is 'storing'
            data_drag.dragged_item = drag_widget.item
            # get the up and down images of the widget
            up_image = drag_widget.up_image
            down_image = drag_widget.down_image
            self.setDragData(drag_widget.item, down_image, up_image)
            container.take_item(self.container, drag_widget.item.slot)
            
            # after dragging the 'item', set the widgets' images
            # so that it has it's default 'empty' images
            drag_widget.item = None
            self.updateImage(drag_widget)
            
    def dropObject(self, obj):
        """Drops the object being dropped
           @type obj: string
           @param obj: The name of the object within
                       the dictionary 'self.buttons' 
           @return: None"""
        try:
            drop_widget = self.gui.findChild(name = obj)
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
                up_image = drop_widget.up_image
                down_image = drop_widget.down_image
                self.setDragData(replace_item, down_image, up_image)
            else:
                data_drag.dragging = False
                #reset the mouse cursor to the normal cursor
                self.controller.resetMouseCursor()
            drop_widget.item = drag_item
            self.updateImage(drop_widget)
        except (container.BulkLimitError):
            #Do we want to notify the player why the item can't be dropped?
            pass
        
    def showContainer(self):
        """Show the container
           @return: None"""
        # Prepare slots 1 through 9
        empty_image = "gui/inv_images/inv_backpack.png"
        slot_count = 9
        for counter in range(1, slot_count+1):
            slot_name = "Slot%i" % counter
            index = counter - 1
            self.empty_images[slot_name] = empty_image
            widget = self.gui.findChild(name=slot_name)
            widget.item = container.get_item(self.container, index)
            widget.index = index
            self.updateImage(widget)
            self.events_to_map[slot_name] = cbwa(self.dragDrop, slot_name)
            self.events_to_map[slot_name + "/mouseReleased"] = \
                                            self.showContextMenu

        self.gui.mapEvents(self.events_to_map)
        self.gui.show()
        
    def hideContainer(self):
        """Hide the container
           @return: None"""
        if self.gui.isVisible():
            self.gui.hide()      
