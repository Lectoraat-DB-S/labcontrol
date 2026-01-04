"""Function Generator Widget"""
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class GeneratorWidget(QWidget):
    waveformChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.generator = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        group = QGroupBox("Function Generator")
        grid = QGridLayout(group)

        grid.addWidget(QLabel("Waveform:"), 0, 0)
        self.waveform_combo = QComboBox()
        self.waveform_combo.addItems(["Sine", "Square", "Triangle"])
        grid.addWidget(self.waveform_combo, 0, 1)

        grid.addWidget(QLabel("Frequency:"), 1, 0)
        self.freq_spin = QDoubleSpinBox()
        self.freq_spin.setRange(1, 1000000)
        self.freq_spin.setValue(1000)
        self.freq_spin.setSuffix(" Hz")
        grid.addWidget(self.freq_spin, 1, 1)

        grid.addWidget(QLabel("Amplitude:"), 2, 0)
        self.amp_spin = QDoubleSpinBox()
        self.amp_spin.setRange(0, 10)
        self.amp_spin.setValue(1.0)
        self.amp_spin.setSuffix(" V")
        grid.addWidget(self.amp_spin, 2, 1)

        apply_btn = QPushButton("Apply")
        apply_btn.clicked.connect(self.applySettings)
        grid.addWidget(apply_btn, 3, 0, 1, 2)

        layout.addWidget(group)
        layout.addStretch()

        self.info_label = QLabel("No generator connected")
        layout.addWidget(self.info_label)

    def setDevice(self, generator):
        self.generator = generator
        if generator:
            self.info_label.setText("Connected")

    def applySettings(self):
        if self.generator:
            try:
                ch1 = self.generator.chan(1)
                ch1.setFrequency(self.freq_spin.value())
                ch1.setAmplitude(self.amp_spin.value())
                self.waveformChanged.emit()
            except Exception as e:
                print(f"Error: {e}")
