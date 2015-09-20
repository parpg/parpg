#!/usr/bin/env python

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

from PyQt4 import QtGui, QtCore
from parpg.parser import parse

class DialogScene(object):
    """
    The scene that contains the dialog map
    """
    def __init__(self, widget):
        """
        Initialize the scene
        @type widget: QtGui.QTextEdit
        @param widget: the widget that contians the text to add objects from
        @return: None
        """
        self.widget = widget
        self.refreshMap()

    def refreshMap(self):
        """
        Refresh the map to reflect all the new data
        @return: None
        """
        self.scene = QtGui.QGraphicsScene()
        objects = self.findObjects(self.widget.toPlainText())
        self.addObjectsFromList(objects)

    def findObjects(self, text):
        """
        Parse text and then return the objects
        @return: a list of all the objects
        """
        objects = []

        ptext = parse(text)
        objects.append(ptext)
        for obj in ptext.options:
            objects.append(obj)

        return objects

    def addObjectsFromList(self, obj_list):
        """
        Add all of the objects in a list to the dialog map
        @type obj_list: list
        @param obj_list: the list of objects
        @return: None
        """
        pos = 50
        for obj in obj_list:
 #           print obj
            item = QtGui.QGraphicsEllipseItem(pos,pos,50,50)
            self.scene.addItem(item)
            pos += 10
#        print "Scene list: " + str(self.scene.items())
    

class DialogMap(QtGui.QGraphicsView):
    """
    The dialog map final widget
    """
    def __init__(self, settings, main_edit, parent):
        """
        @type settings: settings.Settings
        @param settings: the settings for the editor
        @type main_edit: QtGui.QTextEdit
        @param main_edit: The main text editor
        @type parent: Any Qt widget
        @param parent: The widgets' parent
        @return: None
        """
        QtGui.QWidget.__init__(self, parent)
        self.map = DialogScene(main_edit)
        self.setScene(self.map.scene)
        self.setSceneRect(0,0,int(settings.res_width),int(settings.res_height))
        self.setGeometry(QtCore.QRect(0,0,int(settings.res_width),int(settings.res_height)))
