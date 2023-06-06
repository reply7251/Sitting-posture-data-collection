from PyQt5.QtWidgets import QLineEdit

class SyncLineEdit(QLineEdit):
    def __init__(self, callback: callable, value=""):
        super().__init__(value)
        self.callback = callback
        self.editingFinished.connect(self.sync)
        self.textChanged.connect(self.sync)
        self._before = value
    
    def sync(self):
        if self._before != self.text():
            self._before = self.text()
            self.callback(self.text())