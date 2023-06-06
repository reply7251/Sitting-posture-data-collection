from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QLabel

class ColorGradient:
    def __init__(self) -> None:
        self.colors = []

    def add_color(self, color, val):
        self.colors.append((color, val))
    
    def clear_color(self):
        self.colors = []
    
    def add_default_colors(self):
        self.add_color((0,0,0),0) #black
        self.add_color((0,0,255),1/6) #blue
        self.add_color((0,255,255),2/6) #cyan
        self.add_color((0,255,0), 3/6) #green
        self.add_color((255,255,0), 4/6) #yellow
        self.add_color((255,0,0), 5/6) #red
        self.add_color((255,255,255),1) #white
    
    def get_gradient_bar(self, size, vertical = True):
        grads = QtGui.QLinearGradient(0, 0, 0, 1) if vertical else QtGui.QLinearGradient(0, 0, 1, 0)
        reversed_grads = QtGui.QLinearGradient(0, 0, 0, 1) if vertical else QtGui.QLinearGradient(0, 0, 1, 0)
        grads.setCoordinateMode(grads.CoordinateMode.ObjectBoundingMode)
        reversed_grads.setCoordinateMode(reversed_grads.CoordinateMode.ObjectBoundingMode)
        for color, val in self.colors:
            grads.setColorAt(1-val, QColor(*color))
            reversed_grads.setColorAt(val, QColor(*color))
        pixmap = QtGui.QPixmap(*size)
        painter = QtGui.QPainter(pixmap)
        painter.fillRect(pixmap.rect(), reversed_grads)
        painter.fillRect(pixmap.rect().marginsRemoved(QtCore.QMargins(2,2,2,2)), grads)
        painter.end()
        bar = QLabel()
        bar.setPixmap(pixmap)
        return bar

    def get_color(self, value):
        if not self.colors:
            return None

        for i, (color, val) in enumerate(self.colors):
            if value < val:
                diff = val - self.colors[i-1][1]
                fract = ((value-self.colors[i-1][1]) / diff) if diff else 0
                return tuple(int((color[j]-self.colors[i-1][0][j]) * fract + self.colors[i-1][0][j]) for j in range(3))
        return tuple(self.colors[-1][0][j] for j in range(3))