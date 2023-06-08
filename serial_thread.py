from PyQt5 import QtCore
import threading
import serial
import math
import time

import utils.wifi as wifi

import socket
from utils import event

class SerialThread(QtCore.QThread):
    def __init__(self) -> None:
        super().__init__()
        self.running = True
    
    def run(self):
        pass
    
    def stop(self):
        self.running = False

class Mega2560SerialThread(SerialThread):
    def __init__(self, port, baud) -> None:
        super().__init__()
        self.port = port
        self.baud = baud
    
    def run(self):
        while self.running:
            try:
                with serial.Serial(self.port, self.baud) as self.serial:
                    try:
                        message = self.serial.readline()
                        message = message.decode()
                    except:
                        message = str(message)
                    numeric = []
                    for sub in message.split(","):
                        sub = sub.strip()
                        try:
                            numeric.append(float(sub))
                        except:
                            break
                    else:
                        event.SerialNumericReceiveEvent(numeric).fire()
                        continue
                    event.SerialStringReceiveEvent(message).fire()
            except:
                time.sleep(1)
    
    def stop(self):
        super().stop()
        if self.serial:
            self.serial.cancel_read()

class WifiThread(SerialThread):
    def __init__(self, mega_SSID, mega_pwd) -> None:
        super().__init__()
        self.mega_ssid = mega_SSID
        self.mega_pwd = mega_pwd
        self.target_ssid = None
        self.target_pwd = ""
    
    def run(self):
        success = False

        local_ip = "???"
        local_port = 8888

        while not success:
            connections = wifi.Wifi.get_connections()
            for connection in connections:
                if connection.ssid == self.mega_ssid: #if connect to mega
                    success = True
                    break
            else:
                if self.target_ssid: # after save ap, disconnect and connect to mega
                    wifi.Wifi.connect(self.mega_ssid, self.mega_pwd)
                elif connections: # starts with this and save ap
                    profile = wifi.Wifi.get_profile(connections[0].ssid)
                    self.target_ssid = profile.ssid
                    self.target_pwd = profile.pwd
                    local_ip = socket.gethostbyname(socket.gethostname())
                else: #if using pc as ap, not implements
                    pass 

            time.sleep(1)
        
        port = 8888
        ip_address = "ip address"

        success = False

        while not success:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect((ip_address, port))

                    sock.sendall("ping".encode())
                    response = self.wait_message(connection)
                    if not response.decode().startswith("pong"):
                        continue

                    sock.sendall(f"APdata:\n{self.target_ssid}\n{self.target_pwd}\n{local_ip}\n{local_port}".encode())
                    response = self.wait_message(connection)
                    if not response.decode().startswith("received"):
                        success = True
            except:
                pass
            
            time.sleep(1)
        
        success = False
        while not success:
            connections = wifi.Wifi.get_connections()
            for connection in connections:
                if connection.ssid == self.target_ssid: #if connect to ap
                    success = True
                    break
            else:
                wifi.Wifi.connect(self.target_ssid, self.target_pwd) # connect to ap
            
            time.sleep(1)
        
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.bind((local_ip, local_port))
                    sock.listen(1)
                    conn, addr = sock.accept()
                    with conn:
                        while self.running:
                            data = self.wait_message(conn)
                            if not data:
                                break
                            self.handle_data(data)
            except:
                pass
        
    def wait_message(self, connection: socket.socket, timeout=0.5):
        history = b''
        time_past = 0
        while time_past < timeout:
            time.sleep(0.01)
            time_past += 0.01
            data = connection.recv(1024)
            if data:
                history += data
            else:
                if not history:
                    return history
        return history
        
    def handle_data(self, data: bytes):
        try:
            message = data.decode()
        except:
            message = str(message)
        for line in message.splitlines():
            self.handle_line(line)

    def handle_line(self, message: str):
        numeric = []
        for sub in message.split(","):
            sub = sub.strip()
            try:
                numeric.append(float(sub))
            except:
                break
        else:
            event.SerialNumericReceiveEvent(numeric).fire()
            return
        event.SerialStringReceiveEvent(message).fire()
    
        



class TestSerialThread(SerialThread):
    def __init__(self) -> None:
        super().__init__()
        self.counter = 0
    
    def run(self):
        while self.running:
            event.SerialStringReceiveEvent(f"test {self.counter}").fire()
            
            numeric = [math.sin(self.counter*math.pi/256 + (i*math.pi/4.5))*512+512 for i in range(9)]
            event.SerialNumericReceiveEvent(numeric).fire()
            self.counter += 1
            self.counter %= 1024
            time.sleep(0.01)



