from PyQt5.QtWidgets import QLabel
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import QSize, QTimer

from utils import event


PIXMAP_WIDTH = 300
SCALE_X = 2
history_limit = int(PIXMAP_WIDTH / SCALE_X)
tick_time = 50

class PressureMonitor(QLabel):
    pen_pressure = QPen(QColor(255,0,0), 15)
    pen_ticks_thin = QPen(QColor(0,255,0), 6)
    pen_ticks_thick = QPen(QColor(0,255,0), 10)

    def __init__(self):
        super().__init__()
        self.history = []
        self.setScaledContents(True)
        self._pixmap = QtGui.QPixmap(QSize(PIXMAP_WIDTH, 1024))

        self.pixmap_updated = True

        self.update_timer = QTimer()
        self.update_timer.setInterval(tick_time)
        self.update_timer.timeout.connect(self.repaint_pixmap)
        self.update_timer.start()
    
    def paintEvent(self, a0: QPaintEvent) -> None:
        
        painter = QPainter(self)
        width = self.width()
        height = self.height()
        image_width = self._pixmap.width()
        image_height = self._pixmap.height()

        scale_x = width / image_width
        scale_y = height / image_height
        painter.setTransform(QTransform().scale(scale_x, scale_y))
        painter.drawPixmap(0,0, self._pixmap)

        return super().paintEvent(a0)

    def repaint_pixmap(self):
        if self.pixmap_updated:
            return
        pixmap = self._pixmap
        size = pixmap.size()

        pixmap.fill(QColor(0,0,0))
        painter = QtGui.QPainter(pixmap)

        painter.setPen(self.pen_ticks_thick)
        for i in range(2, 10,2):
            painter.drawLine(0,i*size.height()//10,size.width(),i*size.height()//10)

        painter.setPen(self.pen_pressure)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        path = QPainterPath()

        for i, (pressure, freezed) in enumerate(self.history):
            if freezed:
                path.moveTo(i*SCALE_X, pressure)
            path.lineTo(i*SCALE_X, pressure)

        painter.drawPath(path)
        painter.end()
        
        self.pixmap_updated = True
        
        self.update()

    def add_pressure(self, value, was_freezed = False):
        self.history.append((value, was_freezed))
        if len(self.history) > history_limit:
            self.history = self.history[len(self.history) - history_limit:]
        
        self.pixmap_updated = False