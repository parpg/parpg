from PySide import QtCore, QtGui

class CompletionTextEdit(QtGui.QTextEdit):
    """
    @note: code adapted from http://rowinggolfer.blogspot.com/2010/08/qtextedit-with-autocompletion-using.html
    """
    def __init__(self, parent=None):
        super(CompletionTextEdit, self).__init__(parent)

        self.setMinimumWidth(400)
        self.completer = None
        self.moveCursor(QtGui.QTextCursor.End)

    def setCompleter(self, completer):
        #TODO: investigate exactly how this works
        if self.completer:
            self.disconnect(self.completer, 0, self, 0)

        if not completer:
            return

        completer.setWidget(self)
        completer.setCompletionMode(QtGui.QCompleter.PopupCompletion)
        self.completer = completer
        self.completer.activated[str].connect(self.insertCompletion)

    def insertCompletion(self, completion):
        text_cursor = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        text_cursor.movePosition(QtGui.QTextCursor.Left)
        text_cursor.movePosition(QtGui.QTextCursor.EndOfWord)
        text_cursor.insertText(completion[-extra:])
        self.setTextCursor(text_cursor)

    def textUnderCursor(self):
        text_cursor = self.textCursor()
        text_cursor.select(QtGui.QTextCursor.WordUnderCursor)

        return text_cursor.selectedText()

    def focusInEvent(self, event):
        if self.completer:
            self.completer.setWidget(self);

        QtGui.QTextEdit.focusInEvent(self, event)

    def keyPressEvent(self, event):
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (QtCore.Qt.Key_Enter, QtCore.Qt.Key_Return,
                               QtCore.Qt.Key_Escape, QtCore.Qt.Key_Tab,
                               QtCore.Qt.Key_Backtab):
                event.ignore()
                return

        ## has ctrl-E been pressed??
        is_shortcut = (event.modifiers() == QtCore.Qt.ControlModifier and
                       event.key() == QtCore.Qt.Key_E)
        if (not self.completer or not is_shortcut):
            QtGui.QTextEdit.keyPressEvent(self, event)

        ## ctrl or shift key on it's own??
        ctrl_or_shift = event.modifiers() in (QtCore.Qt.ControlModifier ,
                QtCore.Qt.ShiftModifier)
        if ctrl_or_shift and len(event.text()) == 0:
            # ctrl or shift key on it's own
            return

        end_of_word = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-="

        has_modifier = ((event.modifiers() != QtCore.Qt.NoModifier) and
                        not ctrl_or_shift)

        completion_prefix = self.textUnderCursor()

        if (not is_shortcut and (has_modifier or len(event.text()) == 0 or
            len(completion_prefix) < 3 or event.text()[-1:] in end_of_word)):
                self.completer.popup().hide()
                return

        if (completion_prefix != self.completer.completionPrefix()):
            self.completer.setCompletionPrefix(completion_prefix)
            popup = self.completer.popup()
            popup.setCurrentIndex(
                self.completer.completionModel().index(0,0))

        cursor_rect = self.cursorRect()
        cursor_rect.setWidth(self.completer.popup().sizeHintForColumn(0)
                + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cursor_rect) 
