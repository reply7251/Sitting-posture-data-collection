from PyQt5.QtWidgets import QLabel, QListWidget, QCheckBox, QLineEdit, QVBoxLayout, QHBoxLayout, QListWidgetItem, QWidget, QLayout
from PyQt5 import QtCore

from utils import Wifi

from configparser import SectionProxy

from .sync_widget import SyncLineEdit
import identifies

class WifiSetting(QWidget):
    def __init__(self, section: SectionProxy) -> None:
        super().__init__()

        self.section = section
        self.selected_wifi = section[identifies.CONFIG_WIFI_SSID]

        self.build()
        self.pwd_inp.setText(section[identifies.CONFIG_WIFI_PWD])
    
    def build(self):
        self.ssid_label = QLabel("Select Wifi:")
        self.wifi_list = QListWidget()
        self.pwd_label = QLabel("password:")
        self.show_pwd_btn = QCheckBox("show password")
        def callback(value):
            self.section[identifies.CONFIG_WIFI_PWD] = value
        self.pwd_inp = SyncLineEdit(callback)

        self.pwd_inp.setEchoMode(QLineEdit.EchoMode.Password)

        self.show_pwd_btn.clicked.connect(self.show_pwd_toggle)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        main_layout.addWidget(self.ssid_label)
        main_layout.addWidget(self.wifi_list, 10)

        self.wifi_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.wifi_list.itemClicked.connect(self.wifi_select)
        
        pwd1 = QHBoxLayout()
        pwd1.addWidget(self.pwd_label)
        pwd1.addWidget(self.pwd_inp, 10)
        main_layout.addLayout(pwd1)
        main_layout.addWidget(self.show_pwd_btn)

        self.rescan_timer = QtCore.QTimer()
        self.rescan_timer.setInterval(10 * 1000)
        self.rescan_timer.timeout.connect(self.update_wifi)
        self.rescan_timer.start()

        self.update_wifi()
    
    @property
    def password(self):
        return self.pwd_inp.text()

    def update_wifi(self):
        scanned_wifi = Wifi.scan()
        self.wifi_list.clear()
        for wifi_name in scanned_wifi:
            item = QListWidgetItem(wifi_name)
            self.wifi_list.addItem(item)

    def wifi_select(self):
        selected = self.wifi_list.selectedItems()[0]
        self.selected_wifi = selected.text()
        self.ssid_label.setText("Select Wifi: " + self.selected_wifi)
        self.section[identifies.CONFIG_WIFI_SSID] = self.selected_wifi
        
    def show_pwd_toggle(self):
        self.pwd_inp.setEchoMode(QLineEdit.EchoMode.Normal if self.show_pwd_btn.isChecked() else QLineEdit.EchoMode.Password)