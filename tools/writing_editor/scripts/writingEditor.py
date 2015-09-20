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

import sys, os, codecs

from PyQt4 import QtGui, QtCore
from ui.editor_ui import Ui_writingEditor
from ui.popupWindows import *
from parpg.syntaxHighlight import SyntaxHighlighter
from parpg.settings import Settings
from parpg.dialogMap import DialogMap
from parpg.parser import parse


class WritingEditor(QtGui.QMainWindow):
    """
    The main class for the writing editor
    """
    def __init__(self, parent=None):
        """
        Initialize the editor
        """
        QtGui.QWidget.__init__(self, parent)
        
        self.settings = Settings()
        self.settings.readSettingsFromFile('data/options.txt')
        self.resize(int(self.settings.res_width), int(self.settings.res_height))

        self.ui = Ui_writingEditor()
        self.ui.setupUi(self)
        self.ui.dialog_map = DialogMap(self.settings, self.ui.main_edit, self.ui.dialog_map_tab)
        self.syntax = SyntaxHighlighter(self.ui.main_edit.document())
        self.syntaxCreated = True
        self.changes = False
        self.connectSignals()
        self.setupMenus()

        self.open_file_name = None
        self.saveEnabled(False)
        self.title_asterisk = False
        self.ui.actionNone.setEnabled(False)
        self.getRecentItems('data/recent_files.txt')


    def setupMenus(self):
        """
        Setup the menus:
        Add the shortcuts to all the menu's and also create the shorcuts
        Add the images for the icons
        @return: None
        """
        self.ui.actionNew_File.setText('&New File\tCtrl+N')
        self.ui.actionOpen_File.setText('&Open File\tCtrl+O')
        self.ui.actionSave.setText('&Save\tCtrl+S')
        self.ui.actionSave_As.setText('Save &As\tCtrl+Shift+S')
        self.ui.actionPrint.setText('&Print\tCtrl+P')
        self.ui.actionExit.setText('&Exit\tCtrl+Q')
        self.ui.actionUndo.setText('&Undo\tCtrl+Z')
        self.ui.actionRedo.setText('&Redo\tCtrl+Y')
        self.ui.actionCopy.setText('&Copy\tCtrl+C')
        self.ui.actionCut.setText('C&ut\tCtrl+X')
        self.ui.actionPaste.setText('&Paste\tCtrl+V')
        self.ui.actionPreferences.setText('P&references\tCtrl+Shift+P')
        self.ui.actionHelp.setText("&Help\tF1")
        self.ui.actionAbout.setText('&About\tF2')
        self.ui.actionNone.setText('None')

        self.ui.actionNew_File.setShortcut(QtGui.QKeySequence('Ctrl+N'))
        self.ui.actionOpen_File.setShortcut(QtGui.QKeySequence('Ctrl+O'))
        self.ui.actionSave.setShortcut(QtGui.QKeySequence('Ctrl+S'))
        self.ui.actionSave_As.setShortcut(QtGui.QKeySequence('Ctrl+Shift+S'))
        self.ui.actionPrint.setShortcut(QtGui.QKeySequence('Ctrl+P'))
        self.ui.actionExit.setShortcut(QtGui.QKeySequence('Ctrl+Q'))
        self.ui.actionUndo.setShortcut(QtGui.QKeySequence('Ctrl+Z'))
        self.ui.actionRedo.setShortcut(QtGui.QKeySequence('Ctrl+Y'))
        self.ui.actionCopy.setShortcut(QtGui.QKeySequence('Ctrl+C'))
        self.ui.actionCut.setShortcut(QtGui.QKeySequence('Ctrl+X'))
        self.ui.actionPaste.setShortcut(QtGui.QKeySequence('Ctrl+V'))
        self.ui.actionPreferences.setShortcut(QtGui.QKeySequence('Ctrl+Shift+P'))
        self.ui.actionHelp.setShortcut(QtGui.QKeySequence('F1'))
        self.ui.actionAbout.setShortcut(QtGui.QKeySequence('F2'))

        self.ui.actionNew_File.setIcon(self.createIcon('new.png'))
        self.ui.actionOpen_File.setIcon(self.createIcon('open.png'))
        self.ui.actionSave.setIcon(self.createIcon('save.png'))
        self.ui.actionSave_As.setIcon(self.createIcon('save_as.png'))
        self.ui.actionPrint.setIcon(self.createIcon('printer.png'))
        self.ui.actionExit.setIcon(self.createIcon('close.png'))
        self.ui.actionUndo.setIcon(self.createIcon('undo.png'))
        self.ui.actionRedo.setIcon(self.createIcon('redo.png'))
        self.ui.actionCopy.setIcon(self.createIcon('copy.png'))
        self.ui.actionCut.setIcon(self.createIcon('cut.png'))
        self.ui.actionPaste.setIcon(self.createIcon('paste.png'))
        self.ui.actionPreferences.setIcon(self.createIcon('preferences.png'))
        self.ui.actionHelp.setIcon(self.createIcon('help.png'))
        self.ui.actionAbout.setIcon(self.createIcon('about.png'))

        self.ui.actionNew_File.setStatusTip('Create a new file')
        self.ui.actionOpen_File.setStatusTip('Open a file')
        self.ui.actionSave.setStatusTip('Save the open file to disk')
        self.ui.actionSave_As.setStatusTip('Save the contents of the open file to a new file on the disk')
        self.ui.actionPrint.setStatusTip('Print the open file')
        self.ui.actionExit.setStatusTip('Exit the editor')
        self.ui.actionUndo.setStatusTip('Undo the last action within the text editor')
        self.ui.actionRedo.setStatusTip('Redo the last action within the text editor')
        self.ui.actionCopy.setStatusTip('Copy the selected text to the clipboard')
        self.ui.actionCut.setStatusTip('Delete the selected text and copy it to the clipboard')
        self.ui.actionPaste.setStatusTip('Paste the text on the clipboard')
        self.ui.actionPreferences.setStatusTip('Edit preferences with the editor')
        self.ui.actionHelp.setStatusTip('Help with the editor and scripting language itself')
        self.ui.actionAbout.setStatusTip('About the editor')
        self.ui.actionNone.setStatusTip('There are no recent files')

    def connectSignals(self):
        """
        Connect all the buttons, widgets, etc to their respective functions
        @return: None
        """
        QtCore.QObject.connect(self.ui.main_tabs, QtCore.SIGNAL("currentChanged(int)"),
                               self.onTabChanged)
        QtCore.QObject.connect(self.ui.main_edit, QtCore.SIGNAL("textChanged()"),
                               self.onTextChanged)

        QtCore.QObject.connect(self.ui.actionNew_File, QtCore.SIGNAL("triggered()"),
                               self.newFile)
        QtCore.QObject.connect(self.ui.actionOpen_File, QtCore.SIGNAL("triggered()"),
                               self.openFile)
        QtCore.QObject.connect(self.ui.actionSave, QtCore.SIGNAL("triggered()"),
                               self.saveFile)
        QtCore.QObject.connect(self.ui.actionPrint, QtCore.SIGNAL("triggered()"),
                               self.printFile)
        QtCore.QObject.connect(self.ui.actionExit, QtCore.SIGNAL("triggered()"),
                               lambda: self.quit('data/recent_files.txt'))

        QtCore.QObject.connect(self.ui.actionCopy, QtCore.SIGNAL("triggered()"),
                               self.ui.main_edit.copy)
        QtCore.QObject.connect(self.ui.actionCut, QtCore.SIGNAL("triggered()"),
                               self.ui.main_edit.cut)
        QtCore.QObject.connect(self.ui.actionPaste, QtCore.SIGNAL("triggered()"),
                               self.ui.main_edit.paste)
        QtCore.QObject.connect(self.ui.actionRedo, QtCore.SIGNAL("triggered()"),
                               self.ui.main_edit.redo)
        QtCore.QObject.connect(self.ui.actionUndo, QtCore.SIGNAL("triggered()"),
                               self.ui.main_edit.undo)
        QtCore.QObject.connect(self.ui.actionPreferences, QtCore.SIGNAL("triggered()"),
                               self.createPrefWindow)

        QtCore.QObject.connect(self.ui.actionAbout, QtCore.SIGNAL("triggered()"),
                               self.createAboutWindow)
        QtCore.QObject.connect(self.ui.actionHelp, QtCore.SIGNAL("triggered()"),
                               self.createHelpWindow)

    def onTextChanged(self):
        """
        Function called when text is changed
        """
        if (self.syntaxCreated):
            self.syntaxCreated = False

        else:
            self.saveEnabled(True)
            self.changes = True
            if (self.windowTitle() == "PARPG Writing Editor - Untitled"):
                return

            if (self.open_file_name == None):
                self.setWindowTitle("PARPG Writing Editor - Untitled")
                return

            if (self.title_asterisk == False):
                self.setWindowTitle(self.windowTitle() + " *")
                self.title_asterisk = True
            
    def onTabChanged(self, index):
        """
        Check if the tab is the editor or the map viewer and disable/enable actions
        accordingly
        @type index: int
        @param index: The index of the tab
        @return: None
        """
        # it's the main editor
        if (index == 0):
            self.ui.actionCopy.setEnabled(True)
            self.ui.actionCut.setEnabled(True)
            self.ui.actionPaste.setEnabled(True)
        # it's the dialog map
        elif (index == 1):
            self.ui.dialog_map.map.refreshMap()
            self.ui.actionCopy.setEnabled(False)
            self.ui.actionCut.setEnabled(False)
            self.ui.actionPaste.setEnabled(False)
        else:
            print 'Parameter index should be either 0 or 1. Got %d' % index

    def createIcon(self, name):
        """
        Creates a QIcon object from the path name
        @type name: string
        @param name: the name of the file
        @rtype: QtGui.QIcon
        @return: The QIcon object
        """
        path = 'data/images/' + name
        icon = QtGui.QIcon(path)
        return icon

    def newFile(self):
        """
        Start a new file
        @return: None
        """
        self.open_file_name = None
        self.ui.main_edit.setText("")
        self.saveEnabled(False)

    def saveFile(self, filename=None):
        """
        Save the contents of self.ui.main_edit to filename
        If filename is None, then open a save dialog
        @type filename: string
        @param filename: the file to save to
        @return: None
        """
        # if no filename argument is specified and there is no open file, open the save dialog
        if (filename == None and self.open_file_name == None):
            file_dialog = QtGui.QFileDialog(self)
            file_dialog.setDefaultSuffix("dialog")
            file_dialog.setNameFilter("Dialog Files (*.dialog)")
            self.save_file_name = file_dialog.getSaveFileName()
            self.open_file_name = self.save_file_name
        # otherwise just save the file
        else:
            self.save_file_name = self.open_file_name

        try:
            text = self.ui.main_edit.toPlainText()
            codec_file = codecs.open(self.save_file_name, 'w', 'utf-8')
            codec_file.write(text)
            codec_file.close()
            self.saveEnabled(False)
            last_slash = self.findLastSlash(self.save_file_name)
            self.setWindowTitle("PARPG Writing Editor - " + self.save_file_name[last_slash+1:])
            self.title_asterisk = False
            
        except IOError:
            print 'Unable to save to file: %s' % self.save_file_name

    def saveAs(self):
        """
        Open a dialog to save the current file as a new file
        @return: None
        """
        self.saveFile()

    def openFile(self, filename=None):
        """
        Open a file
        @type filename: String
        @param filename: the file to open
        @return: None
        """
        old_file_name = self.open_file_name
        if (filename == None):
            file_dialog = QtGui.QFileDialog(self)
            self.open_file_name = file_dialog.getOpenFileName()
        else:
            self.open_file_name = filename
        try:
            codec_file = codecs.open(self.open_file_name, 'r', 'utf-8')
            codec_contents = codec_file.read()
            self.ui.main_edit.setText(codec_contents)
            self.saveEnabled(False)

            new_dict = {}

            try:
                recent_length = len(self.recent_items)
                keys = self.recent_items.keys()
                if (recent_length != 0):
                    keys.remove(keys[recent_length-1])
                for key in keys:
                    value = self.recent_items[key]
                    new_dict[key] = value
            except:
                recent_length = 0
                
            last_slash = self.findLastSlash(self.open_file_name)
            before = self.open_file_name[:last_slash+1]
            after = self.open_file_name[last_slash+1:]
            new_dict[after] = before
                
            self.recent_items = new_dict
            self.updateRecentItems()

            slash = self.findLastSlash(self.open_file_name)
            window_title = 'PARPG Writing Editor - ' + self.open_file_name[slash+1:]
            self.ui.writingEditor.setWindowTitle(window_title)
            self.title_asterisk = False

        except IOError:
            print 'Unable to open file: %s' % self.open_file_name
            self.open_file_name = old_file_name           

    def printFile(self):
        """
        Print the currently open file
        """
        qprinter = QtGui.QPrinter()
        print_dialog = PrintDialog(qprinter)
        ret = print_dialog.run()
        if (ret == QtGui.QDialog.Accepted):
            self.ui.main_edit.document().print_(qprinter)

    def saveEnabled(self, value):
        """
        Change whether save is enabled
        @type value: bool
        @param value: whether to enable or disable save
        @return: None
        """
        self.ui.actionSave.setEnabled(value)
        self.ui.actionSave_As.setEnabled(value)

    def createAboutWindow(self):
        """
        Create the about the program window
        @return: None
        """
        if (not hasattr(self, "about_window")):
            self.about_window = AboutWindow(self)
        self.about_window.show()

    def createPrefWindow(self):
        """
        Create the preferences window
        @return: None
        """
        if (not hasattr(self, "pref_window")):
            self.pref_window = PrefWindow(self, self.settings)
        self.pref_window.show()
        self.pref_window.button_apply.setEnabled(True)

    def createHelpWindow(self):
        """
        Create the help window
        @return: None
        """
        if (not hasattr(self, "help_window")):
            self.help_window = HelpWindow(self.settings, self)
        self.help_window.show()

    def getRecentItems(self, filename):
        """
        Reads all the filenames from the file filename that contains all the recent files
        @type filename: string
        @param filename: the path to the file
        @return: None
        """
        self.recent_items = {}
        try:
            recent_files = open(filename, 'r').read().strip()
            
            if (recent_files == ""):
                self.recent_items = None
                return

            recent_list = recent_files.split('\n')

            for item in recent_list:
                last_slash = self.findLastSlash(item)                        
                before = item[:last_slash+1]
                after = item[last_slash+1:]
                self.recent_items[after] = before

            self.updateRecentItems()
            self.ui.menuRecent_Files.removeAction(self.ui.actionNone)

        except IOError:
            print 'Unable to read the recent files from file: %s\n'\
                'No recent files will be displayed' % str(filename)
            

    def updateRecentItems(self):
        """
        Make the recent items show up in the gui
        @return: None
        """
        try:
            self.ui.menuRecent_files.removeAction(self.recent_1)
        except:
            print "Cannot remove action self.recent_1"
        try:
            self.ui.menuRecent_files.removeAction(self.recent_2)
        except:
            print "Cannot remove action self.recent_2"
        try:
            self.ui.menuRecent_files.removeAction(self.recent_3)
        except:
            print "Cannot remove action self.recent_3"
        try:
            self.ui.menuRecent_files.removeAction(self.recent_4)
        except:
            print "Cannot remove action self.recent_4"

        recent_keys = []
        for key in self.recent_items:
            recent_keys.append(key)
            
        try:
            self.recent_1 = QtGui.QAction(self)
            self.recent_1.setObjectName(recent_keys[0])
            self.recent_1.setText(recent_keys[0])
            self.ui.menuRecent_Files.addAction(self.recent_1)
            full_path_1 = self.recent_items[recent_keys[0]] + recent_keys[0]
            QtCore.QObject.connect(self.recent_1, QtCore.SIGNAL('triggered()'),
                                   lambda: self.openFile(full_path_1))
            
        except:
            print 'Error generating widgets for recent item 1'
            
        try:
            self.recent_2 = QtGui.QAction(self)
            self.recent_2.setObjectName(recent_keys[1])
            self.recent_2.setText(recent_keys[1])
            self.ui.menuRecent_Files.addAction(self.recent_2, 0)
            full_path_2 = self.recent_items[recent_keys[1]] + recent_keys[1]
            QtCore.QObject.connect(self.recent_2, QtCore.SIGNAL('triggered()'),
                                   lambda: self.openFile(full_path_2))
                    
        except:
            print 'Error generating widgets for recent item 2'
            
        try:
            self.recent_3 = QtGui.QAction(self)
            self.recent_3.setObjectName(recent_keys[2])
            self.recent_3.setText(recent_keys[2])
            self.ui.menuRecent_Files.addAction(self.recent_3)
            full_path_3 = self.recent_items[recent_keys[2]] + recent_keys[2]
            QtCore.QObject.connect(self.recent_3, QtCore.SIGNAL('triggered()'),
                                   lambda: self.openFile(full_path_3))
        
        except:
            print 'Error generating widgets for recent item 3'

        try:
            self.recent_4 = QtGui.QAction(self)
            self.recent_4.setObjectName(recent_keys[3])
            self.recent_4.setText(recent_keys[3])
            self.ui.menuRecent_Files.addAction(self.recent_4)
            full_path_4 = self.recent_items[recent_keys[3]] + recent_keys[3]
            QtCore.QObject.connect(self.recent_4, QtCore.SIGNAL('triggered()'),
                                   lambda: self.openFile(full_path_4))
        
        except:
            print 'Error generating widgets for recent item 4'
            

    def writeRecentItems(self, filename):
        """
        Write the recent items to the file filename
        @type filename: string
        @param filename: the file to write to
        @return: None
        """
        if self.recent_items == None:
            return
        else:
            try:
                file_open = open(filename, 'w')
                text = ""
                for key in self.recent_items:
                    full_path = self.recent_items[key] + key
                    new_line = full_path + '\n'
                    text += new_line
                file_open.write(text)
                file_open.close()
                    
            except IOError:
                print 'Unable to write the recent files to file: %s\n'\
                    'No recent files will be written' % str(filename)

    def findLastSlash(self, string):
        """
        Find the last slash in string string
        @type string: string
        @param string: The string to find the last slash in
        @return: None
        """
        back_num = 1
        start = len(string)
        while (True):
            new_num = start - back_num
            if (string[new_num] == '/'):
                last_slash = new_num
                break
            else:
                back_num += 1
        return last_slash

    def resizeEvent(self, event):
        """
        Overrides the normal resize event so it will also resize the widgets within
        @type event: QResizeEvent
        @param event: the event (it's provided by the Qt system)
        @return: None
        """
        self.ui.main_edit.setGeometry(QtCore.QRect(0, 0, event.size().width(),
                                                   event.size().height()-73))
        self.ui.dialog_map.setGeometry(QtCore.QRect(0, 0, event.size().width(),
                                                    event.size().height()-73))

    def closeEvent(self, event):
        """
        Overrides the normal close event so it will ask if you want to save changes etc
        @type event: QCloseEvent
        @param event: the event (its provided by the qt system)
        @return: None
        """
        if (self.changes):
            window = ChangesWindow()
            ret = window.run()
            if (ret == QtGui.QMessageBox.Save):
                self.saveFile()
                self.writeRecentItems("data/recent_files.txt")
                event.accept()
            elif (ret == QtGui.QMessageBox.Discard):
                self.writeRecentItems("data/recent_files.txt")
                event.accept()
            elif (ret == QtGui.QMessageBox.Cancel):
                event.ignore()
                
                        
    def quit(self, filename):
        """
        Quit and then write the recent files to filename and ask about changes
        @type filename: string
        @param filename: the file to write to
        @return: None
        """
        self.ui.writingEditor.close()
