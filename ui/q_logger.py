from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtGui import QTextCursor


class QLogger(QPlainTextEdit):
    def __init__(self, threshold=10000):
        super().__init__()

        self.setReadOnly(True)

        self.threshold = threshold

    def add_message(self, *messages):
        self.appendPlainText("\n".join(messages))
        cursor = self.textCursor()
        while self.document().lineCount() > 1000:
            cursor.movePosition(QTextCursor.MoveOperation.Start)
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            cursor.removeSelectedText()
            cursor.deleteChar()