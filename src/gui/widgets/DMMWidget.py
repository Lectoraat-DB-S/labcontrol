"""Digital Multimeter Widget"""
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGroupBox, QLabel, QLCDNumber, QVBoxLayout, QWidget


class DMMWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dmm = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        group = QGroupBox("Multimeter Reading")
        group_layout = QVBoxLayout(group)

        self.lcd = QLCDNumber()
        self.lcd.setDigitCount(8)
        self.lcd.setSegmentStyle(QLCDNumber.Flat)
        self.lcd.display("0.000")
        self.lcd.setMinimumHeight(60)
        group_layout.addWidget(self.lcd)

        self.unit_label = QLabel("VDC")
        self.unit_label.setAlignment(Qt.AlignCenter)
        self.unit_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        group_layout.addWidget(self.unit_label)

        layout.addWidget(group)
        layout.addStretch()

        self.info_label = QLabel("No multimeter connected")
        layout.addWidget(self.info_label)

    def setDevice(self, dmm):
        self.dmm = dmm
        if dmm:
            self.info_label.setText("Connected")

    def updateReading(self):
        if self.dmm:
            try:
                reading = self.dmm.getVoltage()
                self.lcd.display(f"{reading:.3f}")
            except:
                pass
