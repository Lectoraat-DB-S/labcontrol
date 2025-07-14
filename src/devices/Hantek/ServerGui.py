import sys
from pathlib import Path
from devices.Hantek.HantekServer import ServerWorker as Worker
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QTextEdit,
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


class MainWindow(QMainWindow):
    def runLongTask(self):
        # Step 2: Create a QThread object
        self.thread:QThread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        self.worker.setScopeObject(self.worker.getScopeObject())
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.worker.progress.connect(self.reportProgress)
        self.worker.msg.connect(lambda msg:self.addMessage(msg))
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

    def addMessage(self, msg):
        self.textArea.append(msg)
        

    def __init__(self):
        
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

        self.textArea = self.findChild(QTextEdit, "textEdit")
        self.show()

    def starter(self):
        self.textArea.append('START GEDRUKT')
        if self.thread  == None:
            self.textArea.append("creating thread for server")
            self.runLongTask()

    def stopper(self):
        self.worker.stopIt()
        print('STOP GEDRUKT')
        self.close()

def createApp():
    app = QApplication(sys.argv)
    UIWindow = MainWindow()
    app.exec()