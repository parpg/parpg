import sys

from PySide import QtCore, QtGui

import source_editor
from ui.ui_dialogue_editor import Ui_DialogueEditor

class DialogueEditor(QtGui.QMainWindow, Ui_DialogueEditor):
    """
    Dialogue Editor's main window.
    """

    def __init__(self, parent=None):
        super(DialogueEditor, self).__init__(parent)
        self.setupUi(self)

        font = QtGui.QFont()
        font.setFamily("Courier")
        font.setFixedPitch(True)
        font.setPointSize(10)

        self.source_text_edit.setFont(font)

        self.highlighter = source_editor.Highlighter(
                                         self.source_text_edit.document())
        self.source_text_edit.setCompleter(self.highlighter.completer)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dialogue_editor = DialogueEditor()
    dialogue_editor.show()
    sys.exit(app.exec_())
