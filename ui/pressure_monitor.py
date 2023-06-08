from PyQt5.QtWidgets import QLabel
from PyQt5 import QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import QSize, QTimer

from utils import event

history_limit = 33 * 5
tick_time = 33

class PressureMonitor(QLabel):
    pen_pressure = QPen(QColor(255,0,0), 15)
    pen_ticks_thin = QPen(QColor(0,255,0), 6)
    pen_ticks_thick = QPen(QColor(0,255,0), 10)

    def __init__(self):
        super().__init__()
        self.history = []
        self.setScaledContents(True)
        self._pixmap = QtGui.QPixmap(QSize(300, 1024))

        self.pixmap_updated = True

        self.update_timer = QTimer()
        self.update_timer.setInterval(tick_time)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.start()
    
    def paintEvent(self, a0: QPaintEvent) -> None:
        if not self.pixmap_updated:
            self.repaint_pixmap()
        
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
                path.moveTo(i, pressure)
            path.lineTo(i, pressure)

        painter.drawPath(path)
        painter.end()
        
        self.pixmap_updated = True
        self.update()

    def add_pressure(self, value, was_freezed = False):
        self.history.append((value, was_freezed))
        if len(self.history) > history_limit:
            self.history = self.history[len(self.history) - history_limit:]
        
        self.pixmap_updated = False