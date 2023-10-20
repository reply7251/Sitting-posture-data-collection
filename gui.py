import sys
import os

sys.path.append(os.getcwd())

import typing
from PyQt5.QtCore import QObject, pyqtSlot
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QAction, QWidget


from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *

import serial
import glob

import math
import time

from serial_thread import *
from ui import *
import ctypes

import configparser

import identifies

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


# UAC重开
def uac_reload():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

#uac_reload()


bauds = (110, 300, 600, 1200, 2400, 4800, 9600, 14400, 19200, 38400, 57600, 115200, 128000, 256000)

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result: list[str] = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result



        

class SelectCOMMenu(QMenu):
    def __init__(self, parent = None, callback=None):
        super().__init__("select COM", parent)
        self.callback = callback
        self.update_ports()
        
    def update_ports(self):
        self.clear()
        self.addAction("")
        for port in serial_ports():
            action = QAction(port)
            if self.callback:
                action.triggered.connect(self.callback)
            self.addAction(action)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.resize(800, 600)
        self.com = None
        self.baud = 115200
        
        self.load_config()

        self.build()

        self.show()

    def load_config(self):
        self.config = configparser.ConfigParser()
        self.config.read_dict(identifies.DEFAULT_CONFIG)
        if os.path.exists(identifies.CONFIG_PATH):
            self.config.read(identifies.CONFIG_PATH)
            

    
    def build(self):
        self.setting_window = Setting(self.config)

        self.build_menu()

        main_layout = QHBoxLayout()
        self.setCentralWidget(QWidget())
        self.centralWidget().setLayout(main_layout)

        self.serial_widget = SerialWidget()
        main_layout.addWidget(self.serial_widget,5)
        #self.add_observer(self.serial_widget)

        self.record_widget = RecordWidget(self.config[identifies.CONFIG_POSTURES], self.config[identifies.CONFIG_FILES])
        main_layout.addWidget(self.record_widget,2)
        #self.add_observer(self.record_widget)

        self.serial_data = {identifies.SERIAL_DATA_NUMERIC:[0]*9, identifies.SERIAL_DATA_STRING:[]}
        self.serial_thread = TestSerialThread()
        self.serial_thread.start()
    
    def build_menu(self):
        menu = self.menuBar()

        self.serial_setting_menu = menu.addMenu("Serial setting")

        self.select_COM_menu = self.serial_setting_menu.addMenu("COM")
        self.select_COM_menu.aboutToShow.connect(self.update_coms)
        self.select_baud_menu = self.serial_setting_menu.addMenu("baud")

        action = self.serial_setting_menu.addAction("monitor")
        action.triggered.connect(self.show_monitor)

        for baud in bauds:
            action = self.select_baud_menu.addAction(str(baud))
            action.triggered.connect(self.baud_select)
        
        self.wifi_menu = menu.addMenu("wifi")
        action = self.wifi_menu.addAction("setting")
        action.triggered.connect(self.wifi_popup)

        action = self.wifi_menu.addAction("try connect")
        action.triggered.connect(self.try_connect)

        self.setting_btn = menu.addAction("setting")
        self.setting_btn.triggered.connect(self.setting_popup)
    
    def setting_popup(self):
        self.setting_window.show()
        pass
    
    def show_monitor(self):
        self.monitor = SerialWidget()

    
    def try_connect(self):
        if self.serial_thread:
            self.serial_thread.stop()
        self.serial_thread = WifiThread(
            self.config[identifies.CONFIG_WIFI][identifies.CONFIG_WIFI_SSID],
            self.config[identifies.CONFIG_WIFI][identifies.CONFIG_WIFI_PWD]
            )
        self.serial_thread.start()

    def wifi_popup(self):
        self.setting_window.set_section_by_tag(identifies.CONFIG_WIFI)
        self.setting_window.show()
    
    def update_coms(self):
        ports = serial_ports()
        self.select_COM_menu.clear()
        self.select_COM_menu.addAction("test").triggered.connect(self.COM_selected)
        for port in ports:
            action = self.select_COM_menu.addAction(port)
            action.triggered.connect(self.COM_selected)
    
    def baud_select(self):
        action: QAction = self.sender()
        self.baud = int(action.text())
        self.connect_com()
        
    def COM_selected(self):
        action: QAction = self.sender()
        self.com = action.text()
        self.connect_com()

    def connect_com(self):
        if self.serial_thread:
            self.serial_thread.stop()
        if self.com == "test":
            self.serial_thread = TestSerialThread()
            self.serial_thread.start()
        else:
            self.serial_thread = Mega2560SerialThread(self.com, self.baud)
            self.serial_thread.start()
    
        
    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        event.ExitEvent().fire()
        
        with open(identifies.CONFIG_PATH, 'w') as config_file:
            self.config.write(config_file)

        return super().closeEvent(a0)
        
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = MainWindow()
    sys.exit(app.exec_())