

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLayout
from PyQt5.QtCore import Qt

class VBox(QVBoxLayout):
    def with_widget(self, widget: QWidget, stretch: int = 0, alignment: Qt.Alignment | Qt.AlignmentFlag = Qt.Alignment()):
        self.addWidget(widget, stretch, alignment)
        return self
    
    def with_layout(self, layout: QLayout, stretch: int = 0):
        self.addLayout(layout, stretch)
        return self

class HBox(QHBoxLayout):
    def with_widget(self, widget: QWidget, stretch: int = 0, alignment: Qt.Alignment | Qt.AlignmentFlag = Qt.Alignment()):
        self.addWidget(widget, stretch, alignment)
        return self
    
    def with_layout(self, layout: QLayout, stretch: int = 0):
        self.addLayout(layout, stretch)
        return self