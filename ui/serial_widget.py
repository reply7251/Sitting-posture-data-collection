
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget
from .pressure_monitor import PressureMonitor

from .q_logger import QLogger

from utils import event


class SerialWidget(event.Listener, QWidget, threaded=True):
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

        pressure_layout = QVBoxLayout()
        monitors = QGridLayout()
        for j in range(3):
            for i in range(3):
                pressure_value = PressureMonitor()
                pressure_value.setFrameStyle(QFrame.Shape.Panel | QFrame.Shadow.Sunken)
                monitors.addWidget(pressure_value, 3-i, 3-j)
        
        pressure_layout.addLayout(monitors, 5)

        self.freeze_button = QPushButton("freeze")
        self.freeze_button.clicked.connect(self.freeze_btn_click)
        self.freeze = False
        self.was_freeze = False

        pressure_layout.addWidget(self.freeze_button)
                
        main_layout.addLayout(pressure_layout, 10)
        self.pressure_layout = monitors
    
    def freeze_btn_click(self):
        self.freeze = self.freeze_button.text() == "freeze"
        if self.freeze:
            self.was_freeze = True
            self.freeze_button.setText("unfreeze")
        else:
            self.freeze_button.setText("freeze")
    
    @event.listen()
    def numeric_received(self, event: event.SerialNumericReceiveEvent):
        if self.freeze:
            return
        
        numeric_data = event.data
        for i in range(3):
            for j in range(3):
                index = i*3+j
                monitor: PressureMonitor = self.pressure_layout.itemAt(index).widget()
                pressure_value = numeric_data[index]
                monitor.add_pressure(pressure_value, self.was_freeze)
        self.was_freeze = False
    
    @event.listen()
    def string_received(self, event: event.SerialStringReceiveEvent):
        self.logger.add_message(event.data)
