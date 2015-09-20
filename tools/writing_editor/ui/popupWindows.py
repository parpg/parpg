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
from parpg.syntaxHighlight import SyntaxHighlighter

class AboutWindow(QtGui.QMainWindow):
    """
    The about window
    """
    def __init__(self, parent=None):
        """
        Initialize the windows
        """
        QtGui.QWidget.__init__(self, parent)
        self.setObjectName("aboutWindow")
        self.setWindowTitle("About")
        self.setWindowIcon(QtGui.QIcon("data/images/about.png"))
        self.resize(225,245)
        self.central_widget = QtGui.QWidget(self)
        self.central_widget.setGeometry(QtCore.QRect(0,0,225,245))

        self.info_icon = QtGui.QLabel(self.central_widget)
        self.info_icon.setPixmap(QtGui.QPixmap("data/images/about_large.png")) 
        self.info_icon.setGeometry(QtCore.QRect(48,1,128,128))

        self.credits_text = QtGui.QLabel(self.central_widget)
        ctext = "PARPG Writing Editor written by:\nBrett Patterson A.K.A Bretzel\n"\
            "Written using the PyQt4 library\n"\
            "Copyright 2009"
        self.credits_text.setText(QtCore.QString(ctext))
        self.credits_text.setWordWrap(True)
        self.credits_text.setGeometry(QtCore.QRect(3,65,225,220))

        self.close_button = QtGui.QPushButton(self.central_widget)
        self.close_button.setText("Close")
        self.close_button.setGeometry(QtCore.QRect(75,215,65,25))

        QtCore.QObject.connect(self.close_button, QtCore.SIGNAL("pressed()"),
                               self.close)

class ChangesWindow(QtGui.QMessageBox):
    """
    The Save, Cancel, Discard Changes window
    """
    def __init__(self, parent=None):
        """
        Creates the message box and then returns the button pressed
        """
        QtGui.QWidget.__init__(self, parent)
        self.setText("The document has been modified.")
        self.setInformativeText("What do you want to do?")
        self.setStandardButtons(QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard |
                                  QtGui.QMessageBox.Cancel)
        self.setDefaultButton(QtGui.QMessageBox.Save)
        self.setWindowTitle("Changes have been made")
        self.setWindowIcon(QtGui.QIcon("data/images/question.png"))

    def run(self):
        ret = self.exec_()
        return ret
        
class PrintDialog(QtGui.QPrintDialog):
    """
    The print dialog
    """
    def __init__(self, printer, parent=None):
        """
        Creates the printer dialog
        """
        QtGui.QWidget.__init__(self, printer, parent)

    def run(self):
        ret = self.exec_()
        return ret

class PrefWindow(QtGui.QMainWindow):
    """
    The preferences window
    """
    def __init__(self, parent, settings):
        """
        Initializes the class
        @type parent: QtGui.QWidget?
        @param parent: the parent widget
        @type settings: parpg.settings.Settings
        @param settings: the settings for the application
        """
        QtGui.QWidget.__init__(self, parent)
        
        self.parent = parent
        self.settings = settings

        self.setObjectName("prefWindow")
        self.setWindowTitle("Preferences")
        self.setWindowIcon(QtGui.QIcon("data/images/preferences.png"))
        self.resize(500,475)
        self.central_widget = QtGui.QWidget(self)
        self.central_widget.setGeometry(QtCore.QRect(0,0,500,350))
        self.button_widget = QtGui.QWidget(self)
        self.button_widget.setGeometry(QtCore.QRect(0,355,500,120))

        self.main_layout = QtGui.QFormLayout()

        self.heading = QtGui.QLabel()
        self.heading.setText("Editor preferences:\n\n")
        self.main_layout.addRow(self.heading, None)

        self.res_width_label = QtGui.QLabel()
        self.res_width_label.setText("Resolution Width:")
        self.res_width = QtGui.QLineEdit()
        self.res_width.setMaxLength(4)
        self.res_width.setMaximumWidth(35)
        self.res_width.setText(self.settings.res_width)
        self.main_layout.addRow(self.res_width_label, self.res_width)
        self.res_height_label = QtGui.QLabel()
        self.res_height_label.setText("Resolution Height: ")
        self.res_height = QtGui.QLineEdit()
        self.res_height.setMaxLength(4)
        self.res_height.setMaximumWidth(35)
        self.res_height.setText(self.settings.res_height)
        self.main_layout.addRow(self.res_height_label, self.res_height)

        self.button_layout = QtGui.QHBoxLayout()
        
        self.button_cancel = QtGui.QPushButton()
        self.button_cancel.setText("Cancel")
        self.button_layout.addWidget(self.button_cancel)
        self.button_layout.insertStretch(1)
        self.button_apply = QtGui.QPushButton()
        self.button_apply.setText("Apply")
        self.button_layout.addWidget(self.button_apply)
        self.button_ok = QtGui.QPushButton()
        self.button_ok.setText("Ok")
        self.button_layout.addWidget(self.button_ok)
        self.button_widget.setLayout(self.button_layout)

        self.central_widget.setLayout(self.main_layout)
        
        self.connectSignals()

    def connectSignals(self):
        """
        Connect all the widgets to their corresponding signals
        @return: None
        """
        QtCore.QObject.connect(self.button_ok, QtCore.SIGNAL("pressed()"),
                               lambda: self.okOptions("data/options.txt"))
        QtCore.QObject.connect(self.button_apply, QtCore.SIGNAL("pressed()"),
                               lambda: self.applyOptions("data/options.txt"))
        QtCore.QObject.connect(self.button_cancel, QtCore.SIGNAL("pressed()"),
                               self.close)
        

    def applyOptions(self, options_file):
        """
        Apply the current options
        @type options_file: string
        @param options_file: the file to write to
        @return: None
        """
        self.settings.res_width = self.res_width.text()
        self.settings.res_height = self.res_height.text()
    
        self.settings.writeSettingsToFile(options_file)
        self.button_apply.setEnabled(False)

        self.parent.resize(int(self.settings.res_width),int(self.settings.res_height))

    def okOptions(self, options_file):
        """
        Apply the current options then close the window
        @type options_file: string
        @param options_file: the file to write to
        @return: None
        """
        self.applyOptions(options_file)
        self.close()

class HelpWindow(QtGui.QMainWindow):
    """
    The help window
    """
    def __init__(self, settings, parent=None):
        """
        @type settings: settings.Settings
        @param settings: The editor's settings
        @return: None
        """
        QtGui.QWidget.__init__(self, parent)
        self.settings = settings

        self.setWindowTitle("Help")

        width = int(self.settings.res_width)
        height = int(self.settings.res_height)
        self.resize(width, height)
        self.setWindowIcon(QtGui.QIcon("data/images/help.png"))

        self.file_names = {"Home":"docs/html/index.html",
                           "Scripting":"docs/html/scripting.html",
                           "Dialog Example":"docs/html/example.html"}

        self.central_widget = QtGui.QWidget(self)
        self.central_widget.setGeometry(QtCore.QRect(0,0,width-10,height-50))

        self.main_layout = QtGui.QHBoxLayout()

        self.list_pane = QtGui.QWidget()
        self.list_pane.setMaximumWidth(175)    
        self.list_layout = QtGui.QVBoxLayout()

        self.list_label = QtGui.QLabel()
        self.list_label.setText("Topics:")
        self.list_layout.addWidget(self.list_label)

        self.list = QtGui.QStandardItemModel()
        self.list.appendRow([QtGui.QStandardItem("Home")])
        self.list.appendRow([QtGui.QStandardItem("Scripting")])
        self.list.appendRow([QtGui.QStandardItem("Dialog Example")])

        self.list_view = QtGui.QListView()
        self.list_view.setMinimumHeight(height-150)
        self.list_view.setMinimumWidth(self.list_pane.width())
        self.list_view.setModel(self.list)
        self.list_view.setEditTriggers(self.list_view.NoEditTriggers)
        self.list_layout.addWidget(self.list_view)
        self.list_pane.setLayout(self.list_layout)
        self.main_layout.addWidget(self.list_pane)

        self.main_help_window = QtGui.QTextBrowser()
        self.main_help_window.setHtml(open("docs/html/index.html", 'r').read())
        self.main_layout.addWidget(self.main_help_window)

        self.central_widget.setLayout(self.main_layout)        
        self.syntax = SyntaxHighlighter(self.main_help_window)
        self.connectSignals()
        
    def openFile(self, index):
        """
        Open the html file according to its index in the list
        @type index: int
        @param index: the index in self.list_view
        @return: None
        """
        page_name = index.data().toString()
        file_name = self.file_names[str(page_name)]
        self.main_help_window.setHtml(open(file_name, 'r').read())
        

    def connectSignals(self):
        """
        Connect all the widgets to their respective functions
        @return: None
        """
        QtCore.QObject.connect(self.list_view, QtCore.SIGNAL("clicked(QModelIndex)"),
                               self.openFile)
