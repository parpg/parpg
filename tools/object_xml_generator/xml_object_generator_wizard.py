import sys
from PyQt4 import QtGui, QtCore
from ObjectXMLGenerator import *
from ui_xml_object_generator_wizard import Ui_XMLObjectGeneratorWizard

class XMLObjectGeneratorWizard(QtGui.QWizard, Ui_XMLObjectGeneratorWizard):

    def __init__(self, parent=None):
        super(XMLObjectGeneratorWizard, self).__init__(parent)
         

        self.setupUi(self)

        # changing of the output file and attributes are currently unsupported
        self.removePage(3)
        self.removePage(4)

        self.object_path = None
        self.save_path = None
        self.path_previously_selected = False
        self.attributes = {}

        #signals and slots
        self.object_path_line_edit.textChanged.connect(self.setObjectPath)
        self.save_path_line_edit.textChanged.connect(self.setSavePath)
        self.browse_push_button.clicked.connect(self.updateObjectPath)
        self.browse_push_button_2.clicked.connect(self.updateSavePath)
        self.accepted.connect(self.generate)

    def updateObjectPath(self):
        dirname = QtGui.QFileDialog.getExistingDirectory(self, 
                                                         "Object Path", ".")
        self.object_path_line_edit.setText(dirname)

    def updateSavePath(self):
        dirname = QtGui.QFileDialog.getOpenFileName(self, 
                                                    "Save Path", ".")
        self.save_path_line_edit.setText(dirname)

    def setObjectPath(self, path):
        self.object_path = str(path)

    def setSavePath(self, path):
        self.save_path = str(path)

    def generate(self):
        if self.static_radio_button.isChecked():
            AutoStaticXML(self.object_path)
        else:
            AutoAnimationXML(self.object_path)



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    wizard = XMLObjectGeneratorWizard()
    wizard.show()
    sys.exit(app.exec_())
