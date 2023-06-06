import typing
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget
from .pressure_monitor import PressureMonitor
from PyQt5.QtGui import QTextCursor

from .q_logger import QLogger

from utils import Observer

import identifies

class SerialWidget(Observer, QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.build()
    
    def build(self):

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        communication_section = QVBoxLayout()
        self.logger = QLogger()
        communication_section.addWidget(self.logger, 5)
        self.serial_input = QPlainTextEdit()
        communication_section.addWidget(self.serial_input, 1)
        main_layout.addLayout(communication_section, 10)

        pressure_layout = QGridLayout()
        for i in range(3):
            for j in range(3):
                pressure_value = PressureMonitor()
                pressure_value.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
                pressure_layout.addWidget(pressure_value, i, j)
                
        main_layout.addLayout(pressure_layout, 10)
        self.pressure_layout = pressure_layout
    
    def update(self, data):
        data_type = data[identifies.SERIAL_DATA_TYPE]
        if data_type == identifies.SERIAL_DATA_TYPE_DATA:
            messages: list[str] = data[identifies.SERIAL_DATA_STRING]
            self.logger.add_message(*messages)
            
            for numeric_data in data[identifies.SERIAL_DATA_NUMERIC]:
                for i in range(3):
                    for j in range(3):
                        index = i*3+j
                        monitor: PressureMonitor = self.pressure_layout.itemAt(index).widget()
                        pressure_value = numeric_data[index]
                        monitor.add_pressure(pressure_value)

        elif data_type == identifies.SERIAL_DATA_TYPE_EXIT:
            pass