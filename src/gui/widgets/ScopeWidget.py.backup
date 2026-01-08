"""Scope Control Widget with live waveform display"""

import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ScopeWidget(QWidget):
    """Widget for oscilloscope control and waveform display"""

    settingsChanged = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scope = None
        self.initUI()

    def initUI(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)

        # Scope plot with grid
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Voltage', units='V')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.plot_widget.setMinimumHeight(300)

        # Create plot curves
        self.curve_ch1 = self.plot_widget.plot(pen=pg.mkPen('y', width=2), name='CH1')
        self.curve_ch2 = self.plot_widget.plot(pen=pg.mkPen('c', width=2), name='CH2')

        layout.addWidget(self.plot_widget)

        # Controls
        controls = QGroupBox("Scope Controls")
        controls_layout = QGridLayout(controls)

        # Channel 1 V/div
        controls_layout.addWidget(QLabel("CH1 V/div:"), 0, 0)
        self.ch1_vdiv = QDoubleSpinBox()
        self.ch1_vdiv.setRange(0.001, 100)
        self.ch1_vdiv.setValue(5.0)
        self.ch1_vdiv.setSuffix(" V")
        controls_layout.addWidget(self.ch1_vdiv, 0, 1)

        # Time/div
        controls_layout.addWidget(QLabel("Time/div:"), 1, 0)
        self.time_div = QDoubleSpinBox()
        self.time_div.setRange(0.000001, 10)
        self.time_div.setValue(0.001)
        self.time_div.setSuffix(" s")
        controls_layout.addWidget(self.time_div, 1, 1)

        # Coupling
        controls_layout.addWidget(QLabel("Coupling:"), 2, 0)
        self.coupling = QComboBox()
        self.coupling.addItems(["DC", "AC"])
        controls_layout.addWidget(self.coupling, 2, 1)

        # Apply button
        apply_btn = QPushButton("Apply Settings")
        apply_btn.clicked.connect(self.applySettings)
        controls_layout.addWidget(apply_btn, 3, 0, 1, 2)

        layout.addWidget(controls)

        # Info label
        self.info_label = QLabel("No scope connected")
        self.info_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.info_label)

    def setDevice(self, scope):
        """Set the scope device"""
        self.scope = scope
        if scope:
            self.info_label.setText(f"Connected: {scope.brand} {scope.model}")
            self.info_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
        else:
            self.info_label.setText("No scope connected")
            self.info_label.setStyleSheet("color: #888; font-style: italic;")

    def applySettings(self):
        """Apply settings to scope"""
        if not self.scope:
            return

        try:
            chan1 = self.scope.vertical.chan(1)
            chan1.setVdiv(self.ch1_vdiv.value())
            chan1.setCoupling(self.coupling.currentText())

            self.scope.horizontal.setTimeDiv(self.time_div.value())

            self.settingsChanged.emit()
        except Exception as e:
            print(f"Error applying settings: {e}")

    def updateWaveform(self, waveform):
        """Update waveform display"""
        if waveform and waveform.scaledYdata:
            x_data = np.array(waveform.scaledXdata)
            y_data = np.array(waveform.scaledYdata)
            self.curve_ch1.setData(x_data, y_data)
