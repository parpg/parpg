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

from PyQt4 import QtCore, QtGui

class Ui_writingEditor(object):  
    def setupUi(self, writingEditor):
        """
        Configure the Ui
        """
        self.writingEditor = writingEditor
        self.writingEditor.setObjectName("writingEditor")
        self.writingEditor.resize(800, 456)
        self.centralwidget = QtGui.QWidget(self.writingEditor)
        self.centralwidget.setObjectName("centralwidget")

        self.main_tabs = QtGui.QTabWidget(self.centralwidget)
        self.main_tabs.setGeometry(QtCore.QRect(0, 0, 801, 421))
        self.main_tabs.setObjectName("main_tabs")
        self.editor_tab = QtGui.QWidget()
        self.editor_tab.setObjectName("editor_tab")
        self.main_edit = QtGui.QTextEdit(self.editor_tab)
        self.main_edit.setGeometry(QtCore.QRect(0, 0, 791, 381))
        self.main_edit.setObjectName("main_edit")
        self.main_edit.setTabStopWidth(40)
        self.main_tabs.addTab(self.editor_tab, "")
        self.dialog_map_tab = QtGui.QWidget()
        self.dialog_map_tab.setObjectName("dialog_map_tab")
        self.main_tabs.addTab(self.dialog_map_tab, "")
        self.writingEditor.setCentralWidget(self.centralwidget)

        self.menubar = QtGui.QMenuBar(self.writingEditor)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuRecent_Files = QtGui.QMenu(self.menuFile)
        self.menuRecent_Files.setObjectName("menuRecent_Files")
        self.menuEdit = QtGui.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuHelp = QtGui.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.writingEditor.setMenuBar(self.menubar)

        self.statusbar = QtGui.QStatusBar(self.writingEditor)
        self.statusbar.setObjectName("statusbar")
        self.writingEditor.setStatusBar(self.statusbar)

        self.actionNew_File = QtGui.QAction(self.writingEditor)
        self.actionNew_File.setObjectName("actionNew_File")
        self.actionOpen_File = QtGui.QAction(self.writingEditor)
        self.actionOpen_File.setObjectName("actionOpen_File")
        self.actionSave = QtGui.QAction(self.writingEditor)
        self.actionSave.setObjectName("actionSave")
        self.actionSave_As = QtGui.QAction(self.writingEditor)
        self.actionSave_As.setObjectName("actionSave_As")
        self.actionPrint = QtGui.QAction(self.writingEditor)
        self.actionPrint.setObjectName("actionPrint")
        self.actionExit = QtGui.QAction(self.writingEditor)
        self.actionExit.setObjectName("actionExit")

        self.actionUndo = QtGui.QAction(self.writingEditor)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRedo = QtGui.QAction(self.writingEditor)
        self.actionRedo.setObjectName("actionRedo")
        self.actionCopy = QtGui.QAction(self.writingEditor)
        self.actionCopy.setObjectName("actionCopy")
        self.actionCut = QtGui.QAction(self.writingEditor)
        self.actionCut.setObjectName("actionCut")
        self.actionPaste = QtGui.QAction(self.writingEditor)
        self.actionPaste.setObjectName("actionPaste")
        self.actionPreferences = QtGui.QAction(self.writingEditor)
        self.actionPreferences.setObjectName("actionPreferences")

        self.actionHelp = QtGui.QAction(self.writingEditor)
        self.actionHelp.setObjectName("actionHelp")
        self.actionAbout = QtGui.QAction(self.writingEditor)
        self.actionAbout.setObjectName("actionAbout")

        self.actionNone = QtGui.QAction(self.writingEditor)
        self.actionNone.setObjectName("actionNone")
        self.menuRecent_Files.addAction(self.actionNone)

        self.menuFile.addAction(self.actionNew_File)
        self.menuFile.addAction(self.actionOpen_File)
        self.menuFile.addAction(self.menuRecent_Files.menuAction())
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionSave)
        self.menuFile.addAction(self.actionSave_As)
        self.menuFile.addAction(self.actionPrint)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)

        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addSeparator()
        self.menuEdit.addAction(self.actionPreferences)

        self.menuHelp.addAction(self.actionHelp)
        self.menuHelp.addAction(self.actionAbout)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi()
        self.main_tabs.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self.writingEditor)

    def retranslateUi(self):
        """
        Set all of the text
        """
        self.writingEditor.setWindowTitle(QtGui.QApplication.translate("writingEditor", "PARPG Writing Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.writingEditor.setWindowIcon(QtGui.QIcon('data/images/window_icon.png'))
        self.main_tabs.setTabText(self.main_tabs.indexOf(self.editor_tab), QtGui.QApplication.translate("writingEditor", "Editor", None, QtGui.QApplication.UnicodeUTF8))
        self.main_tabs.setTabText(self.main_tabs.indexOf(self.dialog_map_tab), QtGui.QApplication.translate("writingEditor", "Dialog Map", None, QtGui.QApplication.UnicodeUTF8))
        self.menuFile.setTitle(QtGui.QApplication.translate("writingEditor", "File", None, QtGui.QApplication.UnicodeUTF8))
        self.menuRecent_Files.setTitle(QtGui.QApplication.translate("writingEditor", "Recent Files", None, QtGui.QApplication.UnicodeUTF8))
        self.menuEdit.setTitle(QtGui.QApplication.translate("writingEditor", "Edit", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHelp.setTitle(QtGui.QApplication.translate("writingEditor", "Help", None, QtGui.QApplication.UnicodeUTF8))

