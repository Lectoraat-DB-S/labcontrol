import socket
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from pathlib import Path
from devices.Hantek6022API.PyHT6022.LibUsbScope import Oscilloscope
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


scope = None
clientSocket = None


class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        self.keepRunning = True
        self.server = None
        self.myScope = None
        
    def setScopeObject(self,scopeObj):
        self.myScope = scopeObj
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
        self.progress.emit(f"SCPI Server luistert op {HOST}:{PORT}")
        print(f"SCPI Server luistert op {HOST}:{PORT}")
        
        while self.keepRunning:
            clientSocket, addr = self.server.accept()
            if self.keepRunning:
                print('clientconnected')
                self.progress.emit(f"SCPI Server heeft connectie met een client geaccepteerd")
                clientThread = threading.Thread(target=handle_client, args=(clientSocket, addr, self.myScope))
                clientThread.start()
            else:
                print("terminating server")
                break

        self.finished.emit()
        print("Server: bye bye")


        



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

def handle_client(conn, addr, scope):
    print(f"Verbonden met {addr}")
    #conn.sendall(b"Hantek 6022BL SCPI Server\n")
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

class MainWindow(QMainWindow):
    def runLongTask(self):
        # Step 2: Create a QThread object
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        self.worker.setScopeObject(self.scope)
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        # Step 6: Start the thread
        self.thread.start()

        self.startButton.setEnabled(False)
        self.thread.finished.connect(
            lambda: self.startButton.setEnabled(True)
        )
        self.thread.finished.connect(
            lambda: self.connectedBox.setChecked(False)
        )
    def reportProgress(self):
        self.connectedBox.setChecked(True)

    def __init__(self):
        self.scope = Oscilloscope()
        self.scope.setup()
        if not self.scope.open_handle():
            sys.exit( -1 )

    # upload correct firmware into device's RAM
        if (not self.scope.is_device_firmware_present):
            self.scope.flash_firmware()

    # read calibration values from EEPROM
        calibration = self.scope.get_calibration_values()

    # set interface: 0 = BULK, >0 = ISO, 1=3072,2=2048,3=1024 bytes per 125 us
        self.scope.set_interface( 0 ) # use BULK unless you have specific need for ISO xfer

        self.scope.set_num_channels( channels )
        self.scope.set_sample_rate(1)
        self.scope.set_ch1_voltage_range(1)
        self.scope.set_ch2_voltage_range(1)



        super(MainWindow, self).__init__()
        formpath = Path("C:\\github\\labcontrol\\src\\devices\\Hantek\\form.ui")
        uic.loadUi(formpath,self)
        self.startButton = self.findChild(QPushButton, "startButton")
        self.startButton.clicked.connect(self.starter)
        self.thread  = None

        self.stopButton = self.findChild(QPushButton, "stopButton")
        self.stopButton.clicked.connect(self.stopper)

        self.connectedBox = self.findChild(QCheckBox, "connectedBox")
        self.connectedBox.setChecked(False)
        self.show()

    def starter(self):
        print('START GEDRUKT')
        if self.thread  == None:
            print("creating thread for server")
            self.runLongTask()

    def stopper(self):
        self.worker.stopIt()
        print('STOP GEDRUKT')
        self.close()


        #killServer()



def createApp():
    app = QApplication(sys.argv)
    UIWindow = MainWindow()
    app.exec()