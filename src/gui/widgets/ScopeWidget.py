"""Scope Control Widget with live waveform display and full oscilloscope control"""

import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class ScopeWidget(QWidget):
    """Widget for oscilloscope control and waveform display with full functionality"""

    # Signals
    settingsChanged = pyqtSignal()
    channelVisibilityChanged = pyqtSignal(int, bool)  # channel_num, visible
    triggerSettingsChanged = pyqtSignal()
    acquisitionStateChanged = pyqtSignal(str)  # "RUN", "STOP", "SINGLE"
    measurementUpdated = pyqtSignal(dict)  # {"ch1": {...}, "ch2": {...}}

    # Constants - V/div values in Volts
    VDIV_VALUES = [0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100]

    # Time/div values in seconds
    TDIV_VALUES = [
        5e-9, 10e-9, 25e-9, 50e-9, 100e-9, 250e-9, 500e-9,
        1e-6, 2.5e-6, 5e-6, 10e-6, 25e-6, 50e-6, 100e-6, 250e-6, 500e-6,
        1e-3, 2.5e-3, 5e-3, 10e-3, 25e-3, 50e-3, 100e-3, 250e-3, 500e-3,
        1, 2.5, 5
    ]

    PROBE_VALUES = [1, 10, 20, 50, 100, 500, 1000]
    COUPLING_OPTIONS = ["DC", "AC", "GND"]
    TRIGGER_COUPLING_OPTIONS = ["AC", "DC", "HFREJ", "LFREJ"]
    TRIGGER_SLOPE_OPTIONS = ["POS", "NEG", "WINDOW"]
    TRIGGER_MODE_OPTIONS = ["AUTO", "NORM", "SINGLE", "STOP"]
    TRIGGER_SOURCE_OPTIONS = ["CH1", "CH2", "EXT", "LINE"]
    ACQ_MODE_OPTIONS = ["SAMPLING", "PEAK_DETECT", "AVERAGE", "HIGH_RES"]
    AVG_COUNT_OPTIONS = [4, 16, 32, 64, 128, 256, 512, 1024]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scope = None
        self._capabilities = {}
        self._measurement_timer = QTimer()
        self.initUI()
        self._connectInternalSignals()

    def initUI(self):
        """Initialize complete UI with all panels"""
        layout = QVBoxLayout(self)
        layout.setSpacing(5)

        # Plot widget
        self._createPlotWidget()
        layout.addWidget(self.plot_widget)

        # Scroll area for controls
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMaximumHeight(400)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(5)

        # Create panels
        self._createAcquisitionPanel(scroll_layout)
        self._createChannelPanel(1, scroll_layout)
        self._createChannelPanel(2, scroll_layout)
        self._createHorizontalPanel(scroll_layout)
        self._createTriggerPanel(scroll_layout)
        self._createMeasurementsPanel(scroll_layout)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # Bottom buttons
        self._createBottomButtons(layout)

        # Status label
        self.info_label = QLabel("No scope connected")
        self.info_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.info_label)

    def _createPlotWidget(self):
        """Create enhanced plot widget with trigger level indicator"""
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('k')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLabel('left', 'Voltage', units='V')
        self.plot_widget.setLabel('bottom', 'Time', units='s')
        self.plot_widget.setMinimumHeight(250)

        # Channel curves
        self.curve_ch1 = self.plot_widget.plot(pen=pg.mkPen('y', width=2), name='CH1')
        self.curve_ch2 = self.plot_widget.plot(pen=pg.mkPen('c', width=2), name='CH2')

        # Trigger level indicator (horizontal line)
        self.trigger_line = pg.InfiniteLine(
            pos=0, angle=0, pen=pg.mkPen('r', style=Qt.DashLine, width=1)
        )
        self.plot_widget.addItem(self.trigger_line)

    def _createAcquisitionPanel(self, parent_layout):
        """Create acquisition control panel"""
        group = QGroupBox("Acquisition")
        layout = QGridLayout(group)

        # Run/Stop/Single buttons
        self.btn_run = QPushButton("Run")
        self.btn_run.setStyleSheet("background-color: #4CAF50; color: white;")
        self.btn_stop = QPushButton("Stop")
        self.btn_stop.setStyleSheet("background-color: #f44336; color: white;")
        self.btn_single = QPushButton("Single")
        self.btn_single.setStyleSheet("background-color: #2196F3; color: white;")
        layout.addWidget(self.btn_run, 0, 0)
        layout.addWidget(self.btn_stop, 0, 1)
        layout.addWidget(self.btn_single, 0, 2)

        # Acquisition mode
        layout.addWidget(QLabel("Mode:"), 1, 0)
        self.acq_mode_combo = QComboBox()
        self.acq_mode_combo.addItems(self.ACQ_MODE_OPTIONS)
        layout.addWidget(self.acq_mode_combo, 1, 1)

        # Average count (visible only in AVERAGE mode)
        self.avg_count_label = QLabel("Avg:")
        self.avg_count_combo = QComboBox()
        self.avg_count_combo.addItems([str(x) for x in self.AVG_COUNT_OPTIONS])
        self.avg_count_label.setVisible(False)
        self.avg_count_combo.setVisible(False)
        layout.addWidget(self.avg_count_label, 1, 2)
        layout.addWidget(self.avg_count_combo, 1, 3)

        parent_layout.addWidget(group)

    def _createChannelPanel(self, channel_num, parent_layout):
        """Create channel control panel (CH1 or CH2)"""
        group = QGroupBox(f"Channel {channel_num}")
        group.setCheckable(True)
        group.setChecked(channel_num == 1)  # CH1 visible by default
        layout = QGridLayout(group)

        # V/div selector
        layout.addWidget(QLabel("V/div:"), 0, 0)
        vdiv_combo = QComboBox()
        vdiv_combo.addItems([self._formatVoltage(v) for v in self.VDIV_VALUES])
        vdiv_combo.setCurrentIndex(self.VDIV_VALUES.index(1))  # Default 1V
        layout.addWidget(vdiv_combo, 0, 1)

        # Coupling
        layout.addWidget(QLabel("Coupling:"), 0, 2)
        coupling_combo = QComboBox()
        coupling_combo.addItems(self.COUPLING_OPTIONS)
        layout.addWidget(coupling_combo, 0, 3)

        # Probe attenuation
        layout.addWidget(QLabel("Probe:"), 1, 0)
        probe_combo = QComboBox()
        probe_combo.addItems([f"{p}X" for p in self.PROBE_VALUES])
        probe_combo.setCurrentIndex(1)  # Default 10X
        layout.addWidget(probe_combo, 1, 1)

        # Position (offset)
        layout.addWidget(QLabel("Position:"), 1, 2)
        position_spin = QDoubleSpinBox()
        position_spin.setRange(-10, 10)
        position_spin.setSuffix(" div")
        position_spin.setSingleStep(0.5)
        position_spin.setValue(0)
        layout.addWidget(position_spin, 1, 3)

        parent_layout.addWidget(group)

        # Store references
        if channel_num == 1:
            self.ch1_group = group
            self.ch1_vdiv = vdiv_combo
            self.ch1_coupling = coupling_combo
            self.ch1_probe = probe_combo
            self.ch1_position = position_spin
        else:
            self.ch2_group = group
            self.ch2_vdiv = vdiv_combo
            self.ch2_coupling = coupling_combo
            self.ch2_probe = probe_combo
            self.ch2_position = position_spin

    def _createHorizontalPanel(self, parent_layout):
        """Create horizontal/timebase control panel"""
        group = QGroupBox("Horizontal")
        layout = QGridLayout(group)

        # Time/div selector
        layout.addWidget(QLabel("Time/div:"), 0, 0)
        self.time_div_combo = QComboBox()
        self.time_div_combo.addItems([self._formatTime(t) for t in self.TDIV_VALUES])
        # Default to 1ms
        default_idx = next((i for i, t in enumerate(self.TDIV_VALUES) if t >= 1e-3), 0)
        self.time_div_combo.setCurrentIndex(default_idx)
        layout.addWidget(self.time_div_combo, 0, 1)

        # Sample rate display (read-only)
        layout.addWidget(QLabel("Sample Rate:"), 0, 2)
        self.sample_rate_label = QLabel("-- Sa/s")
        self.sample_rate_label.setStyleSheet("font-weight: bold; color: #2196F3;")
        layout.addWidget(self.sample_rate_label, 0, 3)

        # Capture size selector
        layout.addWidget(QLabel("Capture:"), 1, 0)
        self.capture_size_combo = QComboBox()
        self.CAPTURE_SIZES = [256, 512, 1024, 2048, 4096, 6144]
        self.capture_size_combo.addItems([f"{s}" for s in self.CAPTURE_SIZES])
        self.capture_size_combo.setCurrentIndex(2)  # Default 1024
        layout.addWidget(self.capture_size_combo, 1, 1)

        # Horizontal position
        layout.addWidget(QLabel("Position:"), 1, 2)
        self.h_position_spin = QDoubleSpinBox()
        self.h_position_spin.setRange(-5, 5)
        self.h_position_spin.setSuffix(" div")
        self.h_position_spin.setSingleStep(0.5)
        layout.addWidget(self.h_position_spin, 1, 3)

        parent_layout.addWidget(group)

    def _createTriggerPanel(self, parent_layout):
        """Create trigger control panel"""
        group = QGroupBox("Trigger")
        layout = QGridLayout(group)

        # Source
        layout.addWidget(QLabel("Source:"), 0, 0)
        self.trig_source = QComboBox()
        self.trig_source.addItems(self.TRIGGER_SOURCE_OPTIONS)
        layout.addWidget(self.trig_source, 0, 1)

        # Level
        layout.addWidget(QLabel("Level:"), 0, 2)
        self.trig_level = QDoubleSpinBox()
        self.trig_level.setRange(-100, 100)
        self.trig_level.setSuffix(" V")
        self.trig_level.setSingleStep(0.1)
        self.trig_level.setDecimals(2)
        layout.addWidget(self.trig_level, 0, 3)

        # Slope
        layout.addWidget(QLabel("Slope:"), 1, 0)
        self.trig_slope = QComboBox()
        self.trig_slope.addItems(self.TRIGGER_SLOPE_OPTIONS)
        layout.addWidget(self.trig_slope, 1, 1)

        # Mode
        layout.addWidget(QLabel("Mode:"), 1, 2)
        self.trig_mode = QComboBox()
        self.trig_mode.addItems(self.TRIGGER_MODE_OPTIONS)
        layout.addWidget(self.trig_mode, 1, 3)

        # Coupling
        layout.addWidget(QLabel("Coupling:"), 2, 0)
        self.trig_coupling = QComboBox()
        self.trig_coupling.addItems(self.TRIGGER_COUPLING_OPTIONS)
        layout.addWidget(self.trig_coupling, 2, 1)

        parent_layout.addWidget(group)

    def _createMeasurementsPanel(self, parent_layout):
        """Create measurements display panel"""
        group = QGroupBox("Measurements")
        layout = QGridLayout(group)

        # Header
        headers = ["", "Mean", "Max", "Min", "PkPk", "RMS", "Freq"]
        for col, header in enumerate(headers):
            lbl = QLabel(header)
            lbl.setStyleSheet("font-weight: bold;")
            layout.addWidget(lbl, 0, col)

        # CH1 measurements
        layout.addWidget(QLabel("CH1:"), 1, 0)
        self.ch1_meas = {}
        self.ch1_meas['mean'] = QLabel("--")
        self.ch1_meas['max'] = QLabel("--")
        self.ch1_meas['min'] = QLabel("--")
        self.ch1_meas['pkpk'] = QLabel("--")
        self.ch1_meas['rms'] = QLabel("--")
        self.ch1_meas['freq'] = QLabel("--")
        col = 1
        for label in self.ch1_meas.values():
            label.setStyleSheet("font-family: monospace; color: #FFEB3B;")  # Yellow for CH1
            layout.addWidget(label, 1, col)
            col += 1

        # CH2 measurements
        layout.addWidget(QLabel("CH2:"), 2, 0)
        self.ch2_meas = {}
        self.ch2_meas['mean'] = QLabel("--")
        self.ch2_meas['max'] = QLabel("--")
        self.ch2_meas['min'] = QLabel("--")
        self.ch2_meas['pkpk'] = QLabel("--")
        self.ch2_meas['rms'] = QLabel("--")
        self.ch2_meas['freq'] = QLabel("--")
        col = 1
        for label in self.ch2_meas.values():
            label.setStyleSheet("font-family: monospace; color: #00BCD4;")  # Cyan for CH2
            layout.addWidget(label, 2, col)
            col += 1

        parent_layout.addWidget(group)

    def _createBottomButtons(self, parent_layout):
        """Create bottom action buttons"""
        btn_layout = QHBoxLayout()

        self.apply_btn = QPushButton("Apply Settings")
        self.apply_btn.setStyleSheet("font-weight: bold;")
        self.apply_btn.clicked.connect(self.applySettings)
        btn_layout.addWidget(self.apply_btn)

        self.refresh_meas_btn = QPushButton("Refresh Measurements")
        self.refresh_meas_btn.clicked.connect(self.refreshMeasurements)
        btn_layout.addWidget(self.refresh_meas_btn)

        self.auto_meas_cb = QCheckBox("Auto-refresh")
        self.auto_meas_cb.toggled.connect(self._toggleAutoMeasurement)
        btn_layout.addWidget(self.auto_meas_cb)

        parent_layout.addLayout(btn_layout)

    # === Device connection and capability detection ===

    def setDevice(self, scope):
        """Set scope device and detect capabilities"""
        self.scope = scope
        if scope:
            self._detectCapabilities()
            self._updateUIFromDevice()
            brand = getattr(scope, 'brand', 'Unknown')
            model = getattr(scope, 'model', 'Scope')
            self.info_label.setText(f"Connected: {brand} {model}")
            self.info_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            # Auto-start continuous acquisition
            self._onRunClicked()
        else:
            self._resetUI()
            self.info_label.setText("No scope connected")
            self.info_label.setStyleSheet("color: #888; font-style: italic;")

    def _detectCapabilities(self):
        """Detect which features the connected scope supports"""
        self._capabilities = {
            'dual_channel': False,
            'ext_trigger': False,
            'hfrej_coupling': False,
            'window_trigger': False,
            'trigger': False,
            'acquisition': False,
        }

        if not self.scope:
            return

        # Check for dual channel
        try:
            if hasattr(self.scope, 'vertical') and self.scope.vertical:
                ch2 = self.scope.vertical.chan(2)
                if ch2 is not None:
                    self._capabilities['dual_channel'] = True
        except:
            pass

        # Check trigger features
        if hasattr(self.scope, 'trigger') and self.scope.trigger is not None:
            self._capabilities['trigger'] = True
            trig = self.scope.trigger
            if hasattr(trig, 'TRIG_COUPLING_OPTIONS'):
                opts = str(trig.TRIG_COUPLING_OPTIONS)
                self._capabilities['hfrej_coupling'] = 'HFREJ' in opts
            if hasattr(trig, 'TRIG_SLOPE_OPTIONS'):
                opts = str(trig.TRIG_SLOPE_OPTIONS)
                self._capabilities['window_trigger'] = 'WINDOW' in opts
            if hasattr(trig, 'TRIG_SRC_OPTIONS'):
                opts = str(trig.TRIG_SRC_OPTIONS)
                self._capabilities['ext_trigger'] = 'EX' in opts

        # Check acquisition features
        if hasattr(self.scope, 'acquisition') and self.scope.acquisition is not None:
            self._capabilities['acquisition'] = True

        # Update UI based on capabilities
        self._updateUICapabilities()

    def _updateUICapabilities(self):
        """Enable/disable UI elements based on detected capabilities"""
        # Handle CH2 panel visibility
        if hasattr(self, 'ch2_group'):
            self.ch2_group.setEnabled(self._capabilities.get('dual_channel', False))
            if not self._capabilities.get('dual_channel', False):
                self.ch2_group.setChecked(False)

        # Disable unsupported trigger slope options
        if not self._capabilities.get('window_trigger', False):
            idx = self.trig_slope.findText('WINDOW')
            if idx >= 0:
                model = self.trig_slope.model()
                if model:
                    item = model.item(idx)
                    if item:
                        item.setEnabled(False)

        # Disable unsupported trigger coupling options
        if not self._capabilities.get('hfrej_coupling', False):
            for opt in ['HFREJ', 'LFREJ']:
                idx = self.trig_coupling.findText(opt)
                if idx >= 0:
                    model = self.trig_coupling.model()
                    if model:
                        item = model.item(idx)
                        if item:
                            item.setEnabled(False)

        # Disable EXT/LINE trigger if not supported
        if not self._capabilities.get('ext_trigger', False):
            for opt in ['EXT', 'LINE']:
                idx = self.trig_source.findText(opt)
                if idx >= 0:
                    model = self.trig_source.model()
                    if model:
                        item = model.item(idx)
                        if item:
                            item.setEnabled(False)

    def _updateUIFromDevice(self):
        """Read current settings from device and update UI"""
        if not self.scope:
            return

        # Could read current settings from device here
        # For now, we just use defaults

    def _resetUI(self):
        """Reset UI to default state"""
        self.ch1_group.setChecked(True)
        self.ch2_group.setChecked(False)
        self._clearMeasurements()

    def _clearMeasurements(self):
        """Clear all measurement displays"""
        for label in self.ch1_meas.values():
            label.setText("--")
        for label in self.ch2_meas.values():
            label.setText("--")

    # === Settings application ===

    def applySettings(self):
        """Apply all settings to the scope"""
        if not self.scope:
            return

        try:
            self._applyChannelSettings(1)
            if self._capabilities.get('dual_channel') and self.ch2_group.isChecked():
                self._applyChannelSettings(2)
            self._applyHorizontalSettings()
            self._applyTriggerSettings()
            self._applyAcquisitionSettings()

            self.settingsChanged.emit()
        except Exception as e:
            print(f"Error applying settings: {e}")

    def _applyChannelSettings(self, channel_num):
        """Apply settings for a single channel"""
        if not hasattr(self.scope, 'vertical') or self.scope.vertical is None:
            return

        chan = self.scope.vertical.chan(channel_num)
        if chan is None:
            return

        if channel_num == 1:
            visible = self.ch1_group.isChecked()
            vdiv_idx = self.ch1_vdiv.currentIndex()
            coupling = self.ch1_coupling.currentText()
            probe_idx = self.ch1_probe.currentIndex()
            position = self.ch1_position.value()
        else:
            visible = self.ch2_group.isChecked()
            vdiv_idx = self.ch2_vdiv.currentIndex()
            coupling = self.ch2_coupling.currentText()
            probe_idx = self.ch2_probe.currentIndex()
            position = self.ch2_position.value()

        self._safeCall(chan, 'setVisible', visible)
        self._safeCall(chan, 'setVdiv', self.VDIV_VALUES[vdiv_idx])
        self._safeCall(chan, 'setCoupling', coupling)
        self._safeCall(chan, 'probe', self.PROBE_VALUES[probe_idx])
        self._safeCall(chan, 'position', position)

    def _applyHorizontalSettings(self):
        """Apply horizontal/timebase settings"""
        if not hasattr(self.scope, 'horizontal') or self.scope.horizontal is None:
            return

        tdiv_idx = self.time_div_combo.currentIndex()
        self._safeCall(self.scope.horizontal, 'setTimeDiv', self.TDIV_VALUES[tdiv_idx])

    def _applyTriggerSettings(self):
        """Apply trigger settings"""
        if not self._capabilities.get('trigger'):
            return

        trig = self.scope.trigger

        # Source
        source_text = self.trig_source.currentText()
        if source_text == "CH1":
            self._safeCall(trig, 'setSource', 1)
        elif source_text == "CH2":
            self._safeCall(trig, 'setSource', 2)

        # Level
        self._safeCall(trig, 'setLevel', self.trig_level.value())

        # Slope
        self._safeCall(trig, 'setSlope', self.trig_slope.currentText())

        # Mode
        mode = self.trig_mode.currentText()
        self._safeCall(trig, 'setMode', mode)

        # Coupling
        self._safeCall(trig, 'setCoupling', self.trig_coupling.currentText())

        self.triggerSettingsChanged.emit()

    def _applyAcquisitionSettings(self):
        """Apply acquisition settings"""
        if not self._capabilities.get('acquisition'):
            return

        acq = self.scope.acquisition

        mode = self.acq_mode_combo.currentText()
        self._safeCall(acq, 'mode', mode)

        if mode == "AVERAGE":
            avg_count = int(self.avg_count_combo.currentText())
            self._safeCall(acq, 'averaging', avg_count)

    # === Acquisition control buttons ===

    def _onRunClicked(self):
        """Handle Run button click - starts continuous acquisition"""
        if not self.scope:
            return
        if self._capabilities.get('acquisition'):
            self._safeCall(self.scope.acquisition, 'state', "RUN")
        # Start continuous capture timer
        if not self._measurement_timer.isActive():
            try:
                self._measurement_timer.timeout.disconnect()
            except:
                pass
            self._measurement_timer.timeout.connect(self.refreshMeasurements)
            self._measurement_timer.start(250)  # 4 Hz refresh rate - less CPU intensive
        self.acquisitionStateChanged.emit("RUN")

    def _onStopClicked(self):
        """Handle Stop button click - stops continuous acquisition"""
        if self._capabilities.get('acquisition'):
            self._safeCall(self.scope.acquisition, 'state', "STOP")
        # Stop capture timer
        self._measurement_timer.stop()
        try:
            self._measurement_timer.timeout.disconnect()
        except:
            pass
        self.acquisitionStateChanged.emit("STOP")

    def _onSingleClicked(self):
        """Handle Single button click"""
        if self._capabilities.get('trigger'):
            self._safeCall(self.scope.trigger, 'single')
            self.acquisitionStateChanged.emit("SINGLE")

    # === Measurements ===

    def refreshMeasurements(self):
        """Refresh all measurements from the scope"""
        if not self.scope:
            return

        measurements = {'ch1': {}, 'ch2': {}}

        # CH1 measurements
        if self.ch1_group.isChecked() and hasattr(self.scope, 'vertical') and self.scope.vertical:
            chan1 = self.scope.vertical.chan(1)
            if chan1:
                # Capture new data first if channel has capture method
                try:
                    if hasattr(chan1, 'capture'):
                        waveform = chan1.capture()
                        self.updateWaveform(waveform, channel=1)
                except Exception as e:
                    print(f"CH1 capture error: {e}")
                measurements['ch1'] = self._getMeasurementsForChannel(chan1)
                self._updateMeasurementLabels(self.ch1_meas, measurements['ch1'])

        # CH2 measurements
        if self._capabilities.get('dual_channel') and self.ch2_group.isChecked():
            chan2 = self.scope.vertical.chan(2)
            if chan2:
                # Capture new data first if channel has capture method
                try:
                    if hasattr(chan2, 'capture'):
                        waveform = chan2.capture()
                        self.updateWaveform(waveform, channel=2)
                except Exception as e:
                    print(f"CH2 capture error: {e}")
                measurements['ch2'] = self._getMeasurementsForChannel(chan2)
                self._updateMeasurementLabels(self.ch2_meas, measurements['ch2'])

        self.measurementUpdated.emit(measurements)

    def _getMeasurementsForChannel(self, channel):
        """Get all measurements for a channel"""
        meas = {}

        methods = [
            ('mean', 'getMean'),
            ('max', 'getMax'),
            ('min', 'getMin'),
            ('pkpk', 'getPkPk'),
            ('rms', 'getRMS'),
            ('freq', 'getFrequency')
        ]

        for key, method_name in methods:
            meas[key] = self._safeCall(channel, method_name, default=None)

        return meas

    def _updateMeasurementLabels(self, labels_dict, measurements):
        """Update measurement display labels"""
        formats = {
            'mean': ('V', 3),
            'max': ('V', 3),
            'min': ('V', 3),
            'pkpk': ('V', 3),
            'rms': ('V', 3),
            'freq': ('Hz', 2)
        }

        for key, (unit, decimals) in formats.items():
            val = measurements.get(key)
            if val is not None:
                try:
                    if key == 'freq':
                        labels_dict[key].setText(self._formatFreq(float(val)))
                    else:
                        labels_dict[key].setText(f"{float(val):.{decimals}f}{unit}")
                except (ValueError, TypeError):
                    labels_dict[key].setText("--")
            else:
                labels_dict[key].setText("--")

    def _toggleAutoMeasurement(self, enabled):
        """Toggle automatic measurement refresh"""
        if enabled:
            self._measurement_timer.timeout.connect(self.refreshMeasurements)
            self._measurement_timer.start(500)  # Refresh every 500ms
        else:
            self._measurement_timer.stop()
            try:
                self._measurement_timer.timeout.disconnect(self.refreshMeasurements)
            except:
                pass

    # === Waveform display ===

    def updateWaveform(self, waveform, channel=1):
        """Update waveform display for a channel"""
        if waveform is None:
            return

        y_data = getattr(waveform, 'scaledYdata', None)
        x_data = getattr(waveform, 'scaledXdata', None)

        if y_data is not None and x_data is not None:
            x_arr = np.array(x_data)
            y_arr = np.array(y_data)

            if channel == 1:
                self.curve_ch1.setData(x_arr, y_arr)
            else:
                self.curve_ch2.setData(x_arr, y_arr)

    def updateTriggerLevel(self, level):
        """Update trigger level indicator on plot"""
        self.trigger_line.setPos(level)

    # === Helper methods ===

    def _safeCall(self, obj, method_name, *args, default=None):
        """Safely call a method that may not exist or may fail"""
        if obj is None:
            return default
        if not hasattr(obj, method_name):
            return default
        try:
            method = getattr(obj, method_name)
            if callable(method):
                return method(*args)
            return method
        except Exception as e:
            print(f"Warning: {method_name} failed: {e}")
            return default

    def _formatVoltage(self, value):
        """Format voltage value for display"""
        if value >= 1:
            return f"{value:.0f} V"
        elif value >= 0.001:
            return f"{value*1000:.0f} mV"
        else:
            return f"{value*1e6:.0f} uV"

    def _formatTime(self, value):
        """Format time value for display"""
        if value >= 1:
            return f"{value:.1f} s"
        elif value >= 1e-3:
            return f"{value*1e3:.1f} ms"
        elif value >= 1e-6:
            return f"{value*1e6:.1f} us"
        else:
            return f"{value*1e9:.1f} ns"

    def _formatFreq(self, value):
        """Format frequency value for display"""
        if value is None:
            return "--"
        try:
            value = float(value)
            if value >= 1e6:
                return f"{value/1e6:.2f} MHz"
            elif value >= 1e3:
                return f"{value/1e3:.2f} kHz"
            else:
                return f"{value:.2f} Hz"
        except (ValueError, TypeError):
            return "--"

    def _connectInternalSignals(self):
        """Connect internal widget signals"""
        # Acquisition buttons
        self.btn_run.clicked.connect(self._onRunClicked)
        self.btn_stop.clicked.connect(self._onStopClicked)
        self.btn_single.clicked.connect(self._onSingleClicked)

        # Show/hide average count based on mode
        self.acq_mode_combo.currentTextChanged.connect(self._onAcqModeChanged)

        # Update trigger level line when level changes
        self.trig_level.valueChanged.connect(self.updateTriggerLevel)

        # Channel visibility changes
        self.ch1_group.toggled.connect(lambda v: self._onChannelVisibilityChanged(1, v))
        self.ch2_group.toggled.connect(lambda v: self._onChannelVisibilityChanged(2, v))

        # CH1 settings - apply immediately on change
        self.ch1_vdiv.currentIndexChanged.connect(lambda: self._applyChannelSetting(1, 'vdiv'))
        self.ch1_coupling.currentTextChanged.connect(lambda: self._applyChannelSetting(1, 'coupling'))
        self.ch1_probe.currentIndexChanged.connect(lambda: self._applyChannelSetting(1, 'probe'))
        self.ch1_position.valueChanged.connect(lambda: self._applyChannelSetting(1, 'position'))

        # CH2 settings - apply immediately on change
        self.ch2_vdiv.currentIndexChanged.connect(lambda: self._applyChannelSetting(2, 'vdiv'))
        self.ch2_coupling.currentTextChanged.connect(lambda: self._applyChannelSetting(2, 'coupling'))
        self.ch2_probe.currentIndexChanged.connect(lambda: self._applyChannelSetting(2, 'probe'))
        self.ch2_position.valueChanged.connect(lambda: self._applyChannelSetting(2, 'position'))

        # Time/div - apply immediately
        self.time_div_combo.currentIndexChanged.connect(self._applyTimeDivSetting)

        # Capture size - apply immediately
        self.capture_size_combo.currentIndexChanged.connect(self._applyCaptureSize)

    def _onAcqModeChanged(self, mode):
        """Handle acquisition mode change"""
        is_avg = mode == "AVERAGE"
        self.avg_count_label.setVisible(is_avg)
        self.avg_count_combo.setVisible(is_avg)

    def _onChannelVisibilityChanged(self, channel, visible):
        """Handle channel visibility toggle"""
        if channel == 1:
            self.curve_ch1.setVisible(visible)
        else:
            self.curve_ch2.setVisible(visible)
        self.channelVisibilityChanged.emit(channel, visible)

    def _applyChannelSetting(self, channel, setting_type):
        """Apply a channel setting immediately to the scope"""
        if not self.scope or not hasattr(self.scope, 'vertical'):
            return

        chan = self.scope.vertical.chan(channel)
        if not chan:
            return

        try:
            if channel == 1:
                vdiv_combo, coupling_combo, probe_combo, position_spin = \
                    self.ch1_vdiv, self.ch1_coupling, self.ch1_probe, self.ch1_position
            else:
                vdiv_combo, coupling_combo, probe_combo, position_spin = \
                    self.ch2_vdiv, self.ch2_coupling, self.ch2_probe, self.ch2_position

            if setting_type == 'vdiv':
                vdiv_idx = vdiv_combo.currentIndex()
                if vdiv_idx >= 0 and vdiv_idx < len(self.VDIV_VALUES):
                    vdiv = self.VDIV_VALUES[vdiv_idx]
                    # Apply probe attenuation
                    probe_idx = probe_combo.currentIndex()
                    probe = self.PROBE_VALUES[probe_idx] if probe_idx >= 0 else 1
                    self._safeCall(chan, 'setVdiv', vdiv * probe)

            elif setting_type == 'coupling':
                coupling = coupling_combo.currentText()
                self._safeCall(chan, 'setCoupling', coupling)

            elif setting_type == 'probe':
                # Re-apply vdiv with new probe attenuation
                self._applyChannelSetting(channel, 'vdiv')

            elif setting_type == 'position':
                position = position_spin.value()
                self._safeCall(chan, 'setPosition', position)

        except Exception as e:
            print(f"Error applying {setting_type} to CH{channel}: {e}")

    def _applyTimeDivSetting(self):
        """Apply time/div setting immediately to the scope"""
        if not self.scope or not hasattr(self.scope, 'horizontal'):
            return

        try:
            tdiv_idx = self.time_div_combo.currentIndex()
            if tdiv_idx >= 0 and tdiv_idx < len(self.TDIV_VALUES):
                tdiv = self.TDIV_VALUES[tdiv_idx]
                self._safeCall(self.scope.horizontal, 'setTimeDiv', tdiv)
        except Exception as e:
            print(f"Error applying time/div: {e}")

    def _applyCaptureSize(self):
        """Apply capture size setting to the scope"""
        if not self.scope:
            return

        try:
            idx = self.capture_size_combo.currentIndex()
            if idx >= 0 and idx < len(self.CAPTURE_SIZES):
                size = self.CAPTURE_SIZES[idx]
                # Store capture size on scope_obj for channels to use
                if hasattr(self.scope, 'scope_obj'):
                    self.scope.scope_obj._capture_size = size
                self.scope._capture_size = size
                print(f"Capture size set: {size} samples")
        except Exception as e:
            print(f"Error applying capture size: {e}")

    def getCaptureSize(self):
        """Get current capture size setting"""
        idx = self.capture_size_combo.currentIndex()
        if idx >= 0 and idx < len(self.CAPTURE_SIZES):
            return self.CAPTURE_SIZES[idx]
        return 1024
