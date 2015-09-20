# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'xml_object_generator_wizard.ui'
#
# Created: Sat Feb 19 19:31:01 2011
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_XMLObjectGeneratorWizard(object):
    def setupUi(self, XMLObjectGeneratorWizard):
        XMLObjectGeneratorWizard.setObjectName(_fromUtf8("XMLObjectGeneratorWizard"))
        XMLObjectGeneratorWizard.resize(400, 300)
        self.welcome_page = QtGui.QWizardPage()
        self.welcome_page.setObjectName(_fromUtf8("welcome_page"))
        XMLObjectGeneratorWizard.addPage(self.welcome_page)
        self.type_page = QtGui.QWizardPage()
        self.type_page.setObjectName(_fromUtf8("type_page"))
        self.verticalLayout = QtGui.QVBoxLayout(self.type_page)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.static_radio_button = QtGui.QRadioButton(self.type_page)
        self.static_radio_button.setChecked(True)
        self.static_radio_button.setObjectName(_fromUtf8("static_radio_button"))
        self.verticalLayout.addWidget(self.static_radio_button)
        self.animated_radio_button = QtGui.QRadioButton(self.type_page)
        self.animated_radio_button.setObjectName(_fromUtf8("animated_radio_button"))
        self.verticalLayout.addWidget(self.animated_radio_button)
        XMLObjectGeneratorWizard.addPage(self.type_page)
        self.object_path_page = QtGui.QWizardPage()
        self.object_path_page.setObjectName(_fromUtf8("object_path_page"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.object_path_page)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.object_path_line_edit = QtGui.QLineEdit(self.object_path_page)
        self.object_path_line_edit.setObjectName(_fromUtf8("object_path_line_edit"))
        self.horizontalLayout.addWidget(self.object_path_line_edit)
        self.browse_push_button = QtGui.QPushButton(self.object_path_page)
        self.browse_push_button.setObjectName(_fromUtf8("browse_push_button"))
        self.horizontalLayout.addWidget(self.browse_push_button)
        XMLObjectGeneratorWizard.addPage(self.object_path_page)
        self.save_path_page = QtGui.QWizardPage()
        self.save_path_page.setObjectName(_fromUtf8("save_path_page"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.save_path_page)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.save_path_line_edit = QtGui.QLineEdit(self.save_path_page)
        self.save_path_line_edit.setObjectName(_fromUtf8("save_path_line_edit"))
        self.horizontalLayout_2.addWidget(self.save_path_line_edit)
        self.browse_push_button_2 = QtGui.QPushButton(self.save_path_page)
        self.browse_push_button_2.setObjectName(_fromUtf8("browse_push_button_2"))
        self.horizontalLayout_2.addWidget(self.browse_push_button_2)
        XMLObjectGeneratorWizard.addPage(self.save_path_page)
        self.atribute_page = QtGui.QWizardPage()
        self.atribute_page.setObjectName(_fromUtf8("atribute_page"))
        XMLObjectGeneratorWizard.addPage(self.atribute_page)

        self.retranslateUi(XMLObjectGeneratorWizard)
        QtCore.QMetaObject.connectSlotsByName(XMLObjectGeneratorWizard)

    def retranslateUi(self, XMLObjectGeneratorWizard):
        XMLObjectGeneratorWizard.setWindowTitle(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "Wizard", None, QtGui.QApplication.UnicodeUTF8))
        self.welcome_page.setTitle(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "Welcome", None, QtGui.QApplication.UnicodeUTF8))
        self.welcome_page.setSubTitle(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "The ObjectXMLGenerator will go through a directory and make all the proper FIFE XML definitions. Make sure you select the proper object type, and that your directory, subdirectory, and images follow the proper conventions specified at the wiki.", None, QtGui.QApplication.UnicodeUTF8))
        self.type_page.setTitle(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "Object Type", None, QtGui.QApplication.UnicodeUTF8))
        self.type_page.setSubTitle(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "Is this a static object or an animated object?", None, QtGui.QApplication.UnicodeUTF8))
        self.static_radio_button.setText(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "Static", None, QtGui.QApplication.UnicodeUTF8))
        self.animated_radio_button.setText(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "Animated", None, QtGui.QApplication.UnicodeUTF8))
        self.object_path_page.setTitle(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "Object Path", None, QtGui.QApplication.UnicodeUTF8))
        self.object_path_page.setSubTitle(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "In which directory is the object located?", None, QtGui.QApplication.UnicodeUTF8))
        self.browse_push_button.setText(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.save_path_page.setTitle(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "Save Location", None, QtGui.QApplication.UnicodeUTF8))
        self.save_path_page.setSubTitle(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "Where would you like the generated XML file to be saved", None, QtGui.QApplication.UnicodeUTF8))
        self.browse_push_button_2.setText(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.atribute_page.setTitle(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "Attribute", None, QtGui.QApplication.UnicodeUTF8))
        self.atribute_page.setSubTitle(QtGui.QApplication.translate("XMLObjectGeneratorWizard", "What other attributes would you like to modify?", None, QtGui.QApplication.UnicodeUTF8))

