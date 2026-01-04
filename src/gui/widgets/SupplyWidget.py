"""Power Supply Control Widget"""
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class SupplyWidget(QWidget):
    outputChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.supply = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        group = QGroupBox("Power Supply Control")
        grid = QGridLayout(group)

        grid.addWidget(QLabel("Voltage:"), 0, 0)
        self.voltage_spin = QDoubleSpinBox()
        self.voltage_spin.setRange(0, 30)
        self.voltage_spin.setSuffix(" V")
        grid.addWidget(self.voltage_spin, 0, 1)

        grid.addWidget(QLabel("Current Limit:"), 1, 0)
        self.current_spin = QDoubleSpinBox()
        self.current_spin.setRange(0, 5)
        self.current_spin.setSuffix(" A")
        grid.addWidget(self.current_spin, 1, 1)

        self.output_check = QCheckBox("Output ON")
        grid.addWidget(self.output_check, 2, 0, 1, 2)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.applySettings)
        grid.addWidget(apply_btn, 3, 0, 1, 2)

        layout.addWidget(group)
        layout.addStretch()

        self.info_label = QLabel("No supply connected")
        layout.addWidget(self.info_label)

    def setDevice(self, supply):
        self.supply = supply
        if supply:
            self.info_label.setText(f"Connected")

    def applySettings(self):
        if self.supply:
            try:
                ch1 = self.supply.chan(1)
                ch1.setV(self.voltage_spin.value())
                ch1.setI(self.current_spin.value())
                ch1.enable(self.output_check.isChecked())
                self.outputChanged.emit()
            except Exception as e:
                print(f"Error: {e}")
