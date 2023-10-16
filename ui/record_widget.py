
import typing
from PyQt5 import QtCore, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget

from configparser import SectionProxy

import csv

import identifies

from .flex_box import VBox, HBox
from .sync_widget import SyncLineEdit

from utils.other import is_number

from utils import event
import time

RECORD_INTERVAL = 3

class RecordWidget(event.Listener, QWidget, threaded=True):
    def __init__(self, postures: SectionProxy, file_config: SectionProxy) -> None:
        super().__init__()

        self.buffer = ""
        self.postures: SectionProxy = postures

        self.selected_posture = None
        self.recording = False

        self.file_config = file_config
        self.last_open = None
        self.file = None
        self.csv_writer = None

        self.last_record_tick = time.time()

        self.build()
        self.update_buttons()
    
    def build(self):
        self.user_height_label = QLabel("height:")
        self.user_weight_label = QLabel("weight:")
        self.user_height_inp = SyncLineEdit(self.update_buttons)
        self.user_weight_inp = SyncLineEdit(self.update_buttons)
        self.bmi_label = QLabel("BMI: ???")

        self.add_posture_label = QLabel("add posture")
        self.posture_list = QListWidget()
        self.add_posture_inp = QLineEdit()

        self.record_btn = QPushButton("Start record")
        self.stop_btn = QPushButton("Stop record")

        main_layout = VBox()
        self.setLayout(main_layout)

        main_layout.with_layout(
            HBox()
                .with_widget(self.user_height_label)
                .with_widget(self.user_height_inp, 10)
        )
        main_layout.with_layout(
            HBox()
                .with_widget(self.user_weight_label)
                .with_widget(self.user_weight_inp, 10)
        )
        main_layout.with_widget(self.bmi_label)
        main_layout.with_layout(
            HBox()
                .with_widget(self.add_posture_label)
                .with_widget(self.add_posture_inp, 10)
        )
        main_layout.with_widget(self.posture_list, 10)

        main_layout.with_layout(
            HBox()
                .with_widget(self.record_btn)
                .with_widget(self.stop_btn)
        , 2)
        
        self.record_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.stop_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self.record_btn.clicked.connect(self.record)
        self.stop_btn.clicked.connect(self.stop)

        self.add_posture_inp.returnPressed.connect(self.add_posture)
        self.posture_list.itemClicked.connect(self.posture_selected)
        def keyPressEvent(e: QtGui.QKeyEvent) -> None:
            if e.key() == QtCore.Qt.Key.Key_Delete:
                self.postures.pop(self.posture_list.selectedItems()[0].text())
                self.posture_list.takeItem(self.posture_list.selectedIndexes()[0].row())
                self.selected_posture = None
                self.update_buttons()
        self.posture_list.keyPressEvent = keyPressEvent
        self.posture_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        for posture in self.postures.keys():
            self.posture_list.addItem(posture)
    
    def posture_selected(self):
        self.selected_posture = self.posture_list.selectedItems()[0].text()
        self.update_buttons()

    def add_posture(self):
        posture = self.add_posture_inp.text()
        if not self.posture_list.findItems(posture, QtCore.Qt.MatchFlag.MatchExactly):
            self.posture_list.addItem(posture)
            self.postures[posture] = ""
    
    def update_buttons(self, *_):
        self.record_btn.setDisabled(self.recording or not self.is_height_weight_valid() or not self.is_posture_valid())
        self.stop_btn.setDisabled(not self.recording)
        if self.is_height_weight_valid():
            self.bmi_label.setText(f"BMI: {self.BMI() :.1f}")
        else:
            self.bmi_label.setText(f"BMI: ???")
    
    def BMI(self):
        try:
            height = float(self.user_height_inp.text()) / 100
            weight = float(self.user_weight_inp.text())
            return weight / height / height
        except:
            return -1
    
    def is_posture_valid(self):
        return self.selected_posture != None
    
    def is_height_weight_valid(self):
        return is_number(self.user_height_inp.text()) and is_number(self.user_weight_inp.text())

    def get_height_weight(self):
        return float(self.user_height_inp.text()), float(self.user_weight_inp.text())

    def record(self):
        self.recording = True
        self.update_buttons()

    def stop(self):
        self.recording = False
        if self.file:
            self.file.close()
            self.file = None

        self.update_buttons()
    
    def prepare_csv(self):
        save_file_path = self.file_config[identifies.CONFIG_FILES_SAVE]
        if save_file_path and (self.last_open != save_file_path or self.file == None):
            if self.file:
                self.file.close()
            self.last_open = save_file_path
            self.file = open(save_file_path, "a", newline="")
            self.csv_writer = csv.writer(self.file)
    
    @event.listen()
    def serial_numeric_received(self, event: event.SerialNumericReceiveEvent):
        if self.recording and time.time() - self.last_record_tick > RECORD_INTERVAL:
            self.prepare_csv()
            self.csv_writer.writerow(list(self.get_height_weight()) + [self.selected_posture] + event.data[:-2])
            self.last_record_tick = time.time()
    
    @event.listen()
    def on_exit(self, event: event.ExitEvent):
        if self.file:
            self.file.close()