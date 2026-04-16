import socket
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from pathlib import Path
from devices.Hantek.HantekScopes import Hantek6022Scope
import sys
from time import sleep
import threading
from PyQt5.QtCore import QSize, Qt
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDateEdit,
    QDateTimeEdit,
    QDial,
    QDoubleSpinBox,
    QFontComboBox,
    QLabel,
    QLCDNumber,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QSpinBox,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

clientSocket = None
############
# settings #
############
#
channels     = 2
downsample   = 1
sample_rate  = 20
sample_time  = 1
ch1gain      = 1
ch2gain      = 1

keepRunning = True

HOST = "0.0.0.0"  # Luistert op alle interfaces
PORT = 5025  # Standaard SCPI poort

class ServerWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    msg     = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.scope = Hantek6022Scope()
        self.keepRunning = True
        self.server = None
        
        
    def setScopeObject(self,scopeObj):
        self.scope = scopeObj

    def getScopeObject(self):
        return self.scope
    
    def stopIt(self):
        
        self.keepRunning = False
        mykillsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mykillsocket.connect( ("127.0.0.1", PORT))
        #self.server.close()
        mykillsocket.close()

    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((HOST, PORT))
        self.server.listen(5)
        self.progress.emit(1)
        self.msg.emit(f"SCPI Server luistert op {HOST}:{PORT}")
        
        while self.keepRunning:
            clientSocket, addr = self.server.accept()
            if self.keepRunning:
                clientIP, clientPort = clientSocket.getpeername()
                self.msg.emit(f"SCPI Server heeft connectie met een client geaccepteerd")
                self.msg.emit(f"Client IP: {clientIP}, client poortnr: {clientPort}")
                clientThread = threading.Thread(target=handle_client, args=(clientSocket, addr, self.scope))
                clientThread.start()
            else:
                print("terminating server")
                break

        self.finished.emit()
        print("Server: bye bye")

class ClientWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)
    msg     = pyqtSignal(str)

    def __init__(self, conn, addr, scope: Hantek6022Scope= None):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.scope = scope

    def run(self):
        if self.conn == None:
            self.msg.emit("No client connection. Quitting QlientWorker.......")
            sys.exit(-1)
        if self.scope == None:
            self.msg.emit("No Handtek scope object available. Quitting Quitting QlientWorker.......")
            sys.exit(-1)
        
        while True:
            try:
                data = self.conn.recv(1024).decode("utf-8").strip()
                if not data:
                    break
                print(f"Ontvangen: {data}")
                
                if data == "*IDN?":
                    self.conn.sendall(b"Hantek,6022BL,123456,1.0\n")
                elif data == "CAPTURE?":
                    wave_data = self.scope.read_data()
                    ch1_data_tuple = wave_data[0]
                    ch1_samples = ch1_data_tuple.tobytes()
                    nrOfBytes = len(ch1_samples)
                    hlength = str(nrOfBytes)
                    hlength = hlength
                    str2send = hlength.encode()
                    self.conn.sendall(b'#')
                    self.conn.sendall(b'4')
                    self.conn.sendall(str2send)
                    #conn.sendall(b'\0')
                    self.conn.sendall(ch1_samples)
                    self.conn.sendall(b'\0')
                    self.conn.sendall(b'\n')
                elif data == "EXIT":
                    self.msg.emit("Received EXIT from clienting. ClientWorker will exit now.")
                    self.conn.sendall(b"Bye\n")
                    break
                else:
                    self.conn.sendall(b"ERROR: Unknown command\n")
            except Exception as e:
                print(f"Fout: {e}")
                break
        self.conn.close()
        self.msg.emit("Connection with client closed.")

        

def handle_client(conn: socket.socket, addr, scope: Hantek6022Scope= None):
        if conn == None:
            print("No client connection. Quitting.......")
            sys.exit(-1)
        if scope == None:
            print("No Handtek scope object available. Quitting.......")
            sys.exit(-1)
        
        while True:
            try:
                data = conn.recv(1024).decode("utf-8").strip()
                if not data:
                    break
                print(f"Ontvangen: {data}")
                
                if data == "*IDN?":
                    conn.sendall(b"Hantek,6022BL,123456,1.0\n")
                elif data == "CAPTURE?":
                    wave_data = scope.read_data()
                    ch1_data_tuple = wave_data[0]
                    ch1_samples = ch1_data_tuple.tobytes()
                    nrOfBytes = len(ch1_samples)
                    hlength = str(nrOfBytes)
                    hlength = hlength
                    str2send = hlength.encode()
                    conn.sendall(b'#')
                    conn.sendall(b'4')
                    conn.sendall(str2send)
                    #conn.sendall(b'\0')
                    conn.sendall(ch1_samples)
                    conn.sendall(b'\0')
                    conn.sendall(b'\n')
                elif data == "EXIT":
                    conn.sendall(b"Bye\n")
                    break
                else:
                    conn.sendall(b"ERROR: Unknown command\n")
            except Exception as e:
                print(f"Fout: {e}")
                break
        conn.close()
