import typing
from PyQt5.QtWidgets import QLabel, QListWidget, QCheckBox, QLineEdit, QVBoxLayout, QHBoxLayout, QListWidgetItem, QWidget, QLayout, QStackedWidget
from PyQt5 import QtCore

import configparser

from .sync_widget import SyncLineEdit
from .wifi_setting import WifiSetting

import identifies

class Setting(QWidget):
    def __init__(self, config: configparser.ConfigParser) -> None:
        super().__init__()

        self.config = config

        self.build()

    def build(self):
        self.section_list = QListWidget()
        self.section_list.itemClicked.connect(self.item_selected)
        self.section_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)

        #self.sections = []
        self.setting_part = QStackedWidget()
        main_layout = QHBoxLayout()

        self.setLayout(main_layout)

        main_layout.addWidget(self.section_list, 2)
        main_layout.addWidget(self.setting_part, 10)

        self.build_for_section(identifies.CONFIG_FILES)
        self.section_list.setCurrentRow(0)

        self.section_list.addItem(identifies.CONFIG_WIFI)
        self.setting_part.addWidget(WifiSetting(self.config[identifies.CONFIG_WIFI]))
        #self.sections.append(WifiSetting(self.config["wifi"]))
    
    def set_section(self, index):
        self.section_list.setCurrentRow(index)
        self.item_selected()
    
    def set_section_by_tag(self, tag):
        self.section_list.setCurrentItem(self.section_list.findItems(tag, QtCore.Qt.MatchFlag.MatchExactly)[0])
        self.item_selected()
    
    def item_selected(self):
        self.setting_part.setCurrentIndex(self.section_list.selectedIndexes()[0].row())

    def build_for_section(self, section_name):
        self.section_list.addItem(section_name)

        section = self.config[section_name]
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        #label = QLabel(section_name)
        #layout.addWidget(label)
        for key in section.keys():
            layout.addLayout(self.build_for_section_item(section, key),5)

        self.setting_part.addWidget(widget)
        #self.sections.append(layout)
        return layout

    def build_for_section_item(self, section, key):
        line = QHBoxLayout()

        label = QLabel(key)

        def callback(result):
            section[key] = result
        inp = SyncLineEdit(callback, section[key])

        line.addWidget(label)
        line.addWidget(inp)

        return line