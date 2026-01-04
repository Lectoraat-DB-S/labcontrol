#!/usr/bin/env python3
"""
LabControl - Unified GUI for Lab Equipment Control
Main Window with device panels, live visualization, and automation
"""

import sys
import time
from datetime import datetime
from threading import Thread

import numpy as np
import usb1
from PyQt5.QtCore import QObject, Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDockWidget,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from devices.BaseDMM import BaseDMM
from devices.BaseGenerator import BaseGenerator

# Import device managers
from devices.BaseScope import BaseScope
from devices.BaseSupply import BaseSupply
from devices.Hantek.HantekBaseScope import HantekScope  # Register Hantek
from gui.widgets.DeviceStatusWidget import DeviceStatusWidget
from gui.widgets.DMMWidget import DMMWidget
from gui.widgets.GeneratorWidget import GeneratorWidget
from gui.widgets.MeasurementPanel import MeasurementPanel

# Import GUI widgets
from gui.widgets.ScopeWidget import ScopeWidget
from gui.widgets.SupplyWidget import SupplyWidget


class MeasurementWorker(QThread):
    """Worker thread for running measurements to prevent Wayland crashes"""

    # Signals for measurement progress and results
    started = pyqtSignal(str)  # measurement_type
    progress = pyqtSignal(int, int, str)  # current, total, status_message
    dataPoint = pyqtSignal(float, float)  # x, y data point for live plotting
    finished = pyqtSignal(str, object, object)  # measurement_type, x_data, y_data
    error = pyqtSignal(str, str)  # measurement_type, error_message

    def __init__(self, measurement_type: str, scope=None, supply=None, dmm=None, generator=None):
        super().__init__()
        self.measurement_type = measurement_type
        self.scope = scope
        self.supply = supply
        self.dmm = dmm
        self.generator = generator
        self._stop_requested = False

    def requestStop(self):
        """Request the measurement to stop"""
        self._stop_requested = True

    def run(self):
        """Run the measurement in background thread"""
        self.started.emit(self.measurement_type)

        try:
            if self.measurement_type == 'led_curve':
                self._runLEDCurve()
            elif self.measurement_type == 'freq_response':
                self._runFrequencyResponse()
            elif self.measurement_type == 'bjt_curve':
                self._runBJTCurve()
            elif self.measurement_type == 'single_capture':
                self._runSingleCapture()
        except Exception as e:
            self.error.emit(self.measurement_type, str(e))

    def _runLEDCurve(self):
        """Run LED I-V curve measurement"""
        import numpy as np

        WAITTIME = 0.2
        Vd = []
        Id = []

        if not self.supply or not self.dmm or not self.scope:
            self.error.emit('led_curve', 'Missing devices: need supply, DMM, and scope')
            return

        VSupplied = self.supply.chan(1)
        VledMeas = self.scope.vertical.chan(1)

        VSupplied.setV(0)
        VSupplied.enable(True)

        voltages = list(np.arange(0, 1.3, 0.01))
        total = len(voltages)

        for i, x in enumerate(voltages):
            if self._stop_requested:
                VSupplied.enable(False)
                return

            VSupplied.setV(x)
            time.sleep(WAITTIME)
            ledCurr = self.dmm.get_current()
            ledVolt = VledMeas.getMean()

            Vd.append(ledVolt)
            Id.append(ledCurr)

            self.progress.emit(i + 1, total, f'V={x:.2f}V, I={ledCurr*1000:.2f}mA')
            self.dataPoint.emit(ledVolt, ledCurr)

        VSupplied.enable(False)
        self.finished.emit('led_curve', np.array(Vd), np.array(Id))

    def _runFrequencyResponse(self):
        """Run frequency response sweep"""
        import numpy as np

        if not self.scope or not self.generator:
            self.error.emit('freq_response', 'Missing devices: need scope and generator')
            return

        scopeVert = self.scope.vertical
        genChan1 = self.generator.chan(1)
        scopeChan1 = scopeVert.chan(1)
        scopeChan2 = scopeVert.chan(2)

        startFreq = 50e1
        stopFreq = 5e6
        nrOfFreqPerDec = 5
        WAITTIME = 100e-3

        # Setup scope
        self.scope.display.format("YT")
        self.scope.display.persist(0)
        self.scope.acquisition.mode(acqMode=3)
        self.scope.acquisition.averaging(16)

        genChan1.setfreq(startFreq)
        genChan1.setAmp(4)
        self.scope.acquire("RUN")
        scopeChan1.setVisible(True)
        scopeChan2.setVisible(True)
        scopeChan1.probe(1)
        scopeChan2.probe(1)
        scopeChan1.setVdiv(0.5)
        scopeChan2.setVdiv(0.5)
        scopeChan1.position(0)
        scopeChan2.position(0)
        scopeChan1.setCoupling("AC")
        scopeChan2.setCoupling("AC")

        time.sleep(WAITTIME)
        genChan1.enableOutput(True)

        myFreqs = self.generator.createFreqArray(startFreq, stopFreq, nrOfFreqPerDec, 'DEC')
        total = len(myFreqs)

        measFreqs = []
        maxAmpIN = []
        maxAmpOUT = []

        for i, freq in enumerate(myFreqs):
            if self._stop_requested:
                genChan1.enableOutput(False)
                return

            genChan1.setfreq(freq)
            divtime = 1 / (15 * freq)
            self.scope.horizontal.setTimeDiv(divtime)
            time.sleep(WAITTIME)

            scopeChan1.capture()
            scopeChan2.capture()
            time.sleep(WAITTIME)

            val1 = scopeChan1.getPkPk() / 2
            val2 = scopeChan2.getPkPk() / 2
            measFreqs.append(freq)
            maxAmpIN.append(val1)
            maxAmpOUT.append(val2)

            scopeChan1.setVdiv(val1 / 4)
            scopeChan2.setVdiv(val2 / 4)

            self.progress.emit(i + 1, total, f'f={freq:.0f}Hz')
            self.dataPoint.emit(freq, val2 / val1 if val1 > 0 else 0)

        genChan1.enableOutput(False)
        self.finished.emit('freq_response', np.array(measFreqs), np.array(maxAmpOUT) / np.array(maxAmpIN))

    def _runBJTCurve(self):
        """Run BJT curve tracer"""
        import numpy as np

        if not self.supply or not self.dmm or not self.scope:
            self.error.emit('bjt_curve', 'Missing devices: need supply, DMM, and scope')
            return

        baseControl = self.supply.chan(2)
        collControl = self.supply.chan(1)

        collControl.setV(15)
        baseControl.setV(0)
        collControl.setI(1)
        baseControl.setI(0.5)

        baseControl.enable(True)
        collControl.enable(True)
        time.sleep(0.5)

        basechan = self.scope.vertical.chan(1)
        collchan = self.scope.vertical.chan(2)

        base_vol = []
        coll_curr = []

        voltages = list(np.arange(0, 3, 0.1))
        total = len(voltages)

        for i, x in enumerate(voltages):
            if self._stop_requested:
                collControl.enable(False)
                baseControl.enable(False)
                return

            baseControl.setV(x)
            time.sleep(0.5)
            val = self.dmm.get_current()
            time.sleep(0.5)
            coll_curr.append(val)
            basevolval = basechan.getMean()
            base_vol.append(basevolval)

            self.progress.emit(i + 1, total, f'Vb={x:.2f}V, Ic={val*1000:.2f}mA')
            self.dataPoint.emit(basevolval, val)

        collControl.enable(False)
        baseControl.enable(False)
        self.finished.emit('bjt_curve', np.array(base_vol), np.array(coll_curr))

    def _runSingleCapture(self):
        """Run single waveform capture"""
        import numpy as np

        if not self.scope:
            self.error.emit('single_capture', 'No scope connected')
            return

        chan1 = self.scope.vertical.chan(1)
        waveform = chan1.capture()

        self.progress.emit(1, 1, f'Captured {len(waveform.scaledYdata)} samples')
        self.finished.emit('single_capture', waveform.scaledXdata, waveform.scaledYdata)


class DeviceDiscoveryWorker(QThread):
    """Worker thread for USB device discovery to prevent Wayland crashes"""

    # Signals to communicate results back to main thread
    scopeFound = pyqtSignal(object, str, str)  # scope, brand, model
    scopeError = pyqtSignal(str, str)  # error_type, error_message
    supplyFound = pyqtSignal(object)
    supplyError = pyqtSignal(str)
    generatorFound = pyqtSignal(object)
    generatorError = pyqtSignal(str)
    dmmFound = pyqtSignal(object)
    dmmError = pyqtSignal(str)
    discoveryComplete = pyqtSignal(int)  # device_count

    def run(self):
        """Run device discovery in background thread"""
        device_count = 0

        # Discover scope
        try:
            scope = BaseScope.getDevice()
            if scope:
                self.scopeFound.emit(scope, scope.brand, scope.model)
                device_count += 1
            else:
                self.scopeError.emit('not_found', 'Not found')
        except usb1.USBErrorNoDevice as e:
            self.scopeError.emit('usb_no_device', str(e))
        except usb1.USBErrorBusy as e:
            self.scopeError.emit('usb_busy', str(e))
        except usb1.USBError as e:
            self.scopeError.emit('usb_error', str(e))
        except RuntimeError as e:
            self.scopeError.emit('runtime_error', str(e))
        except Exception as e:
            self.scopeError.emit('unexpected', str(e))

        # Discover supply
        try:
            supply = BaseSupply.getDevice()
            if supply:
                self.supplyFound.emit(supply)
                device_count += 1
        except Exception as e:
            self.supplyError.emit(str(e))

        # Discover generator
        try:
            generator = BaseGenerator.getDevice()
            if generator:
                self.generatorFound.emit(generator)
                device_count += 1
        except Exception as e:
            self.generatorError.emit(str(e))

        # Discover DMM
        try:
            dmm = BaseDMM.getDevice()
            if dmm:
                self.dmmFound.emit(dmm)
                device_count += 1
        except Exception as e:
            self.dmmError.emit(str(e))

        self.discoveryComplete.emit(device_count)


class LabControlMainWindow(QMainWindow):
    """Main application window for LabControl"""

    # Signals for device events
    devicesChanged = pyqtSignal()
    measurementComplete = pyqtSignal(dict)

    def __init__(self):
        super().__init__()

        # Device instances (will be populated by discovery)
        self.scope = None
        self.supply = None
        self.generator = None
        self.dmm = None

        # Application state
        self.dark_mode = True
        self.auto_refresh = True
        self.refresh_rate = 500  # ms

        # Discovery worker thread
        self._discovery_worker = None
        self._discovery_device_count = 0

        # Measurement worker thread
        self._measurement_worker = None
        self._measurement_data_x = []
        self._measurement_data_y = []

        self.initUI()
        self.setupMenuBar()
        self.setupToolBar()
        self.setupStatusBar()
        self.connectSignals()

        # Start device discovery
        self.discoverDevices()

        # Setup refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refreshData)
        if self.auto_refresh:
            self.refresh_timer.start(self.refresh_rate)

    def initUI(self):
        """Initialize the user interface"""
        self.setWindowTitle('LabControl - Equipment Control & Automation')
        self.setGeometry(100, 100, 1600, 900)

        # Central widget with main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Create main splitter (horizontal split)
        main_splitter = QSplitter(Qt.Horizontal)

        # Left panel: Device Controls
        left_panel = self.createDeviceControlPanel()
        main_splitter.addWidget(left_panel)

        # Right panel: Visualization & Measurements
        right_panel = self.createVisualizationPanel()
        main_splitter.addWidget(right_panel)

        # Set initial splitter sizes (40% left, 60% right)
        main_splitter.setSizes([640, 960])

        main_layout.addWidget(main_splitter)

        # Apply dark theme
        self.applyTheme()

    def createDeviceControlPanel(self):
        """Create the left panel with device control widgets"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Device status widget at top
        self.device_status = DeviceStatusWidget()
        layout.addWidget(self.device_status)

        # Tabbed widget for different device types
        self.device_tabs = QTabWidget()
        self.device_tabs.setTabPosition(QTabWidget.West)

        # Create widgets for each device type
        self.scope_widget = ScopeWidget()
        self.supply_widget = SupplyWidget()
        self.generator_widget = GeneratorWidget()
        self.dmm_widget = DMMWidget()

        # Add tabs
        self.device_tabs.addTab(self.scope_widget, "📊 Scope")
        self.device_tabs.addTab(self.supply_widget, "⚡ Supply")
        self.device_tabs.addTab(self.generator_widget, "〰️ Generator")
        self.device_tabs.addTab(self.dmm_widget, "🔢 Multimeter")

        layout.addWidget(self.device_tabs)

        # Quick actions panel at bottom
        quick_actions = self.createQuickActionsPanel()
        layout.addWidget(quick_actions)

        return panel

    def createVisualizationPanel(self):
        """Create the right panel with visualization and measurements"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Create vertical splitter for scope and measurements
        viz_splitter = QSplitter(Qt.Vertical)

        # Top: Scope visualization (larger)
        scope_viz_container = QGroupBox("Live Scope View")
        scope_viz_layout = QVBoxLayout(scope_viz_container)

        # Create a stacked widget to switch between "no scope" message and plot
        from PyQt5.QtWidgets import QStackedWidget
        self.scope_view_stack = QStackedWidget()

        # Page 0: No scope message
        self.scope_plot_label = QLabel("No scope detected. Connect a scope and click 'Discover Devices'")
        self.scope_plot_label.setAlignment(Qt.AlignCenter)
        self.scope_plot_label.setMinimumHeight(400)
        self.scope_plot_label.setStyleSheet("QLabel { background-color: #1e1e1e; color: #888; }")
        self.scope_view_stack.addWidget(self.scope_plot_label)

        # Page 1: Actual scope plot (use the ScopeWidget's plot)
        # We'll add the scope_widget's plot here later when scope is detected

        scope_viz_layout.addWidget(self.scope_view_stack)

        viz_splitter.addWidget(scope_viz_container)

        # Bottom: Measurement panel (smaller)
        self.measurement_panel = MeasurementPanel()
        viz_splitter.addWidget(self.measurement_panel)

        # Set sizes (70% scope, 30% measurements)
        viz_splitter.setSizes([500, 200])

        layout.addWidget(viz_splitter)

        return panel

    def createQuickActionsPanel(self):
        """Create quick action buttons for common tasks"""
        panel = QGroupBox("Quick Actions")
        layout = QGridLayout(panel)

        # Common measurement presets
        btn_led_curve = QPushButton("📈 LED I-V Curve")
        btn_led_curve.setToolTip("Run IR LED curve measurement")
        btn_led_curve.clicked.connect(self.runLEDCurveMeasurement)
        layout.addWidget(btn_led_curve, 0, 0)

        btn_freq_response = QPushButton("📉 Freq Response")
        btn_freq_response.setToolTip("Run AC frequency response sweep")
        btn_freq_response.clicked.connect(self.runFrequencyResponse)
        layout.addWidget(btn_freq_response, 0, 1)

        btn_bjt_curve = QPushButton("🔌 BJT Curve")
        btn_bjt_curve.setToolTip("Run transistor curve tracer")
        btn_bjt_curve.clicked.connect(self.runBJTCurve)
        layout.addWidget(btn_bjt_curve, 1, 0)

        btn_capture = QPushButton("📸 Single Capture")
        btn_capture.setToolTip("Capture single waveform from scope")
        btn_capture.clicked.connect(self.captureWaveform)
        layout.addWidget(btn_capture, 1, 1)

        # Stop measurement button
        self.btn_stop_measurement = QPushButton("⏹ Stop Measurement")
        self.btn_stop_measurement.setToolTip("Stop the currently running measurement")
        self.btn_stop_measurement.clicked.connect(self.stopMeasurement)
        self.btn_stop_measurement.setEnabled(False)
        layout.addWidget(self.btn_stop_measurement, 2, 0)

        # Export button
        btn_export = QPushButton("💾 Export Data")
        btn_export.setToolTip("Export current measurements to CSV")
        btn_export.clicked.connect(self.exportData)
        layout.addWidget(btn_export, 2, 1)

        return panel

    def setupMenuBar(self):
        """Setup application menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu('&File')

        # Export action
        export_action = QAction('&Export Measurements...', self)
        export_action.setShortcut('Ctrl+E')
        export_action.triggered.connect(self.exportData)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        # Exit action
        exit_action = QAction('E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Devices menu
        devices_menu = menubar.addMenu('&Devices')

        # Discover devices
        discover_action = QAction('&Discover Devices', self)
        discover_action.setShortcut('F5')
        discover_action.triggered.connect(self.discoverDevices)
        devices_menu.addAction(discover_action)

        # Reset devices
        reset_action = QAction('&Reset All', self)
        reset_action.triggered.connect(self.resetDevices)
        devices_menu.addAction(reset_action)

        # View menu
        view_menu = menubar.addMenu('&View')

        # Toggle dark mode
        theme_action = QAction('Toggle &Theme', self)
        theme_action.setShortcut('Ctrl+T')
        theme_action.triggered.connect(self.toggleTheme)
        view_menu.addAction(theme_action)

        # Tools menu
        tools_menu = menubar.addMenu('&Tools')

        # Settings
        settings_action = QAction('&Settings...', self)
        settings_action.triggered.connect(self.showSettings)
        tools_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu('&Help')

        about_action = QAction('&About LabControl', self)
        about_action.triggered.connect(self.showAbout)
        help_menu.addAction(about_action)

    def setupToolBar(self):
        """Setup main toolbar"""
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Discover devices button
        discover_btn = QAction('🔍 Discover', self)
        discover_btn.setToolTip('Discover connected devices (F5)')
        discover_btn.triggered.connect(self.discoverDevices)
        toolbar.addAction(discover_btn)

        toolbar.addSeparator()

        # Single capture
        capture_btn = QAction('📸 Capture', self)
        capture_btn.setToolTip('Capture waveform')
        capture_btn.triggered.connect(self.captureWaveform)
        toolbar.addAction(capture_btn)

        # Auto refresh toggle
        self.refresh_btn = QAction('▶ Auto Refresh', self)
        self.refresh_btn.setToolTip('Toggle automatic refresh')
        self.refresh_btn.setCheckable(True)
        self.refresh_btn.setChecked(self.auto_refresh)
        self.refresh_btn.triggered.connect(self.toggleAutoRefresh)
        toolbar.addAction(self.refresh_btn)

        toolbar.addSeparator()

        # Export
        export_btn = QAction('💾 Export', self)
        export_btn.setToolTip('Export data to CSV')
        export_btn.triggered.connect(self.exportData)
        toolbar.addAction(export_btn)

    def setupStatusBar(self):
        """Setup status bar"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Device count label
        self.devices_label = QLabel("Devices: 0 connected")
        self.statusBar.addPermanentWidget(self.devices_label)

        # Connection status
        self.connection_label = QLabel("⚫ Disconnected")
        self.statusBar.addPermanentWidget(self.connection_label)

        self.statusBar.showMessage('Ready - Click "Discover Devices" to start')

    def connectSignals(self):
        """Connect widget signals"""
        # Connect device widget signals
        self.scope_widget.settingsChanged.connect(self.onScopeSettingsChanged)
        self.supply_widget.outputChanged.connect(self.onSupplyOutputChanged)
        self.generator_widget.waveformChanged.connect(self.onGeneratorChanged)

        # Connect measurement panel
        self.measurement_panel.measurementRequested.connect(self.runMeasurement)

    def discoverDevices(self):
        """Discover all connected devices using a background thread"""
        # Prevent multiple concurrent discoveries
        if self._discovery_worker is not None and self._discovery_worker.isRunning():
            self.statusBar.showMessage('Discovery already in progress...')
            return

        self.statusBar.showMessage('Discovering devices...')
        self._discovery_device_count = 0

        # Create worker thread
        self._discovery_worker = DeviceDiscoveryWorker()

        # Connect signals
        self._discovery_worker.scopeFound.connect(self._onScopeFound)
        self._discovery_worker.scopeError.connect(self._onScopeError)
        self._discovery_worker.supplyFound.connect(self._onSupplyFound)
        self._discovery_worker.supplyError.connect(self._onSupplyError)
        self._discovery_worker.generatorFound.connect(self._onGeneratorFound)
        self._discovery_worker.generatorError.connect(self._onGeneratorError)
        self._discovery_worker.dmmFound.connect(self._onDmmFound)
        self._discovery_worker.dmmError.connect(self._onDmmError)
        self._discovery_worker.discoveryComplete.connect(self._onDiscoveryComplete)

        # Start discovery in background
        self._discovery_worker.start()

    def _onScopeFound(self, scope, brand, model):
        """Handle scope found signal from worker thread"""
        self.scope = scope
        self.scope_widget.setDevice(self.scope)
        self.device_status.setDeviceStatus('scope', True, f"{brand} {model}")
        self.statusBar.showMessage(f'Found scope: {brand} {model}')

        # Add the scope plot widget to the visualization stack if not already added
        if self.scope_view_stack.count() == 1:
            self.scope_view_stack.addWidget(self.scope_widget.plot_widget)

        # Switch to showing the plot
        self.scope_view_stack.setCurrentIndex(1)

    def _onScopeError(self, error_type, error_msg):
        """Handle scope error signal from worker thread"""
        if error_type == 'not_found':
            self.device_status.setDeviceStatus('scope', False, 'Not found')
            self.scope_plot_label.setText("No scope detected. Connect a scope and click 'Discover Devices'")
            self.scope_plot_label.setStyleSheet("QLabel { background-color: #1e1e1e; color: #888; }")
        elif error_type == 'usb_no_device':
            self.device_status.setDeviceStatus('scope', False, "USB device disconnected")
            help_text = (
                "USB Device Lost During Initialization\n\n"
                "The device disconnected.\n"
                "This can happen if:\n"
                "- The USB cable is loose\n"
                "- The device is faulty\n"
                "- USB power is insufficient\n\n"
                "Fix:\n"
                "1. Unplug the Hantek scope\n"
                "2. Wait 5 seconds\n"
                "3. Plug it into a different USB port\n"
                "4. Click 'Discover Devices' again"
            )
            self.scope_plot_label.setText(help_text)
            self.scope_plot_label.setStyleSheet("QLabel { background-color: #1e1e1e; color: #f44336; font-size: 11px; }")
        elif error_type == 'usb_busy':
            self.device_status.setDeviceStatus('scope', False, "USB device is busy")
            help_text = (
                "USB Device Busy\n\n"
                "Another program is using the scope.\n\n"
                "Fix:\n"
                "1. Close any other scope software\n"
                "2. Unplug the Hantek scope\n"
                "3. Wait 3 seconds\n"
                "4. Plug it back in\n"
                "5. Click 'Discover Devices' again"
            )
            self.scope_plot_label.setText(help_text)
            self.scope_plot_label.setStyleSheet("QLabel { background-color: #1e1e1e; color: #ff9800; font-size: 11px; }")
        elif error_type == 'runtime_error':
            self.device_status.setDeviceStatus('scope', False, f'Error: {error_msg}')
            if "firmware flash" in error_msg.lower():
                help_text = (
                    "Firmware Flash Required\n\n"
                    "Your Hantek scope needs firmware.\n"
                    "For stability, this must be done outside the GUI.\n\n"
                    "Steps:\n"
                    "1. Close this GUI\n"
                    "2. Open a terminal\n"
                    "3. Run: python src/flash_hantek_firmware.py\n"
                    "4. Follow the on-screen instructions\n"
                    "5. Restart the GUI\n\n"
                    "This only needs to be done once."
                )
                color = "#ff9800"
            elif "BUSY" in error_msg or "busy" in error_msg:
                help_text = (
                    "USB Device Busy Error\n\n"
                    "Quick fix:\n"
                    "1. Unplug your Hantek scope\n"
                    "2. Wait 3 seconds\n"
                    "3. Plug it back in\n"
                    "4. Click 'Discover Devices' again\n\n"
                    "Or run: python src/reset_hantek_usb.py"
                )
                color = "#f44336"
            else:
                help_text = f"Scope Error: {error_msg}\n\nTry reconnecting the device"
                color = "#f44336"
            self.scope_plot_label.setText(help_text)
            self.scope_plot_label.setStyleSheet(f"QLabel {{ background-color: #1e1e1e; color: {color}; font-size: 11px; }}")
        else:
            self.device_status.setDeviceStatus('scope', False, f'Error: {error_msg}')
            self.scope_plot_label.setText(f"Error: {error_msg}\n\nTry reconnecting the device")
            self.scope_plot_label.setStyleSheet("QLabel { background-color: #1e1e1e; color: #f44336; font-size: 11px; }")

        self.scope_view_stack.setCurrentIndex(0)
        print(f"Scope discovery error: {error_type} - {error_msg}")

    def _onSupplyFound(self, supply):
        """Handle supply found signal from worker thread"""
        self.supply = supply
        self.supply_widget.setDevice(self.supply)
        self.device_status.setDeviceStatus('supply', True, 'Connected')

    def _onSupplyError(self, error_msg):
        """Handle supply error signal from worker thread"""
        self.device_status.setDeviceStatus('supply', False, f'Error: {error_msg}')
        print(f"Supply discovery error: {error_msg}")

    def _onGeneratorFound(self, generator):
        """Handle generator found signal from worker thread"""
        self.generator = generator
        self.generator_widget.setDevice(self.generator)
        self.device_status.setDeviceStatus('generator', True, 'Connected')

    def _onGeneratorError(self, error_msg):
        """Handle generator error signal from worker thread"""
        self.device_status.setDeviceStatus('generator', False, f'Error: {error_msg}')
        print(f"Generator discovery error: {error_msg}")

    def _onDmmFound(self, dmm):
        """Handle DMM found signal from worker thread"""
        self.dmm = dmm
        self.dmm_widget.setDevice(self.dmm)
        self.device_status.setDeviceStatus('dmm', True, 'Connected')

    def _onDmmError(self, error_msg):
        """Handle DMM error signal from worker thread"""
        self.device_status.setDeviceStatus('dmm', False, f'Error: {error_msg}')
        print(f"DMM discovery error: {error_msg}")

    def _onDiscoveryComplete(self, device_count):
        """Handle discovery complete signal from worker thread"""
        self.devices_label.setText(f"Devices: {device_count} connected")
        if device_count > 0:
            self.connection_label.setText("🟢 Connected")
            self.statusBar.showMessage(f'Discovery complete: {device_count} device(s) found')
        else:
            self.connection_label.setText("🔴 No devices")
            self.statusBar.showMessage('No devices found')

        self.devicesChanged.emit()

    def resetDevices(self):
        """Reset all connected devices to safe state"""
        reply = QMessageBox.question(self, 'Reset Devices',
            'Reset all devices to safe state?\n\nThis will:\n- Turn off all outputs\n- Set voltages to 0V\n- Stop waveform generation',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                if self.supply:
                    for i in range(1, self.supply.nrOfChan + 1):
                        ch = self.supply.chan(i)
                        ch.setV(0)
                        ch.enable(False)

                if self.generator:
                    for i in range(1, self.generator.nrOfChan + 1):
                        ch = self.generator.chan(i)
                        ch.enableOutput(False)

                self.statusBar.showMessage('All devices reset to safe state')
            except Exception as e:
                QMessageBox.critical(self, 'Reset Error', f'Error resetting devices: {str(e)}')

    def captureWaveform(self):
        """Capture single waveform from scope"""
        if not self.scope:
            QMessageBox.warning(self, 'No Scope', 'No oscilloscope connected')
            return

        self._startMeasurement('single_capture')

    def refreshData(self):
        """Periodic refresh of device data"""
        if self.auto_refresh:
            # Update DMM reading if present
            if self.dmm:
                try:
                    self.dmm_widget.updateReading()
                except:
                    pass

    def toggleAutoRefresh(self, checked):
        """Toggle automatic data refresh"""
        self.auto_refresh = checked
        if checked:
            self.refresh_timer.start(self.refresh_rate)
            self.refresh_btn.setText('▶ Auto Refresh')
        else:
            self.refresh_timer.stop()
            self.refresh_btn.setText('⏸ Auto Refresh')

    def applyTheme(self):
        """Apply color theme to application"""
        if self.dark_mode:
            # Dark theme stylesheet
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QWidget {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QGroupBox {
                    border: 1px solid #555;
                    border-radius: 5px;
                    margin-top: 10px;
                    font-weight: bold;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QPushButton {
                    background-color: #3d3d3d;
                    border: 1px solid #555;
                    border-radius: 3px;
                    padding: 5px 10px;
                    color: #ffffff;
                }
                QPushButton:hover {
                    background-color: #4d4d4d;
                }
                QPushButton:pressed {
                    background-color: #2d2d2d;
                }
                QTabWidget::pane {
                    border: 1px solid #555;
                    background-color: #2b2b2b;
                }
                QTabBar::tab {
                    background-color: #3d3d3d;
                    border: 1px solid #555;
                    padding: 8px 12px;
                    color: #ffffff;
                }
                QTabBar::tab:selected {
                    background-color: #4a90e2;
                }
                QStatusBar {
                    background-color: #1e1e1e;
                    color: #aaa;
                }
                QMenuBar {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QMenuBar::item:selected {
                    background-color: #4a90e2;
                }
                QMenu {
                    background-color: #2b2b2b;
                    color: #ffffff;
                    border: 1px solid #555;
                }
                QMenu::item:selected {
                    background-color: #4a90e2;
                }
            """)
        else:
            # Light theme
            self.setStyleSheet("")

    def toggleTheme(self):
        """Toggle between dark and light theme"""
        self.dark_mode = not self.dark_mode
        self.applyTheme()

    # Measurement automation methods
    def _startMeasurement(self, measurement_type: str):
        """Start a measurement in a background thread"""
        # Prevent multiple concurrent measurements
        if self._measurement_worker is not None and self._measurement_worker.isRunning():
            QMessageBox.warning(self, 'Measurement Running',
                'A measurement is already in progress. Please wait or stop it first.')
            return

        # Clear previous data
        self._measurement_data_x = []
        self._measurement_data_y = []

        # Create worker with current devices
        self._measurement_worker = MeasurementWorker(
            measurement_type,
            scope=self.scope,
            supply=self.supply,
            dmm=self.dmm,
            generator=self.generator
        )

        # Connect signals
        self._measurement_worker.started.connect(self._onMeasurementStarted)
        self._measurement_worker.progress.connect(self._onMeasurementProgress)
        self._measurement_worker.dataPoint.connect(self._onMeasurementDataPoint)
        self._measurement_worker.finished.connect(self._onMeasurementFinished)
        self._measurement_worker.error.connect(self._onMeasurementError)

        # Start measurement
        self._measurement_worker.start()

    def _onMeasurementStarted(self, measurement_type: str):
        """Handle measurement started signal"""
        names = {
            'led_curve': 'LED I-V Curve',
            'freq_response': 'Frequency Response',
            'bjt_curve': 'BJT Curve',
            'single_capture': 'Single Capture'
        }
        self.statusBar.showMessage(f'Running {names.get(measurement_type, measurement_type)}...')
        self.btn_stop_measurement.setEnabled(True)

    def _onMeasurementProgress(self, current: int, total: int, status: str):
        """Handle measurement progress signal"""
        self.statusBar.showMessage(f'Measurement: {current}/{total} - {status}')

    def _onMeasurementDataPoint(self, x: float, y: float):
        """Handle live data point from measurement"""
        self._measurement_data_x.append(x)
        self._measurement_data_y.append(y)
        # Could update a live plot here if desired

    def _onMeasurementFinished(self, measurement_type: str, x_data, y_data):
        """Handle measurement finished signal"""
        import matplotlib.pyplot as plt

        self.btn_stop_measurement.setEnabled(False)

        names = {
            'led_curve': 'LED I-V Curve',
            'freq_response': 'Frequency Response',
            'bjt_curve': 'BJT Curve',
            'single_capture': 'Waveform Capture'
        }
        self.statusBar.showMessage(f'{names.get(measurement_type, measurement_type)} complete')

        # Plot results based on measurement type
        plt.figure()

        if measurement_type == 'led_curve':
            plt.plot(x_data, y_data * 1000, 'o-')
            plt.title("IR LED I-V Characteristic")
            plt.xlabel('$V_d$ (V)')
            plt.ylabel('$I_d$ (mA)')
            plt.grid(True)

        elif measurement_type == 'freq_response':
            plt.semilogx(x_data, 20 * np.log10(y_data))
            plt.title("Frequency Response")
            plt.xlabel('Frequency (Hz)')
            plt.ylabel('Magnitude (dB)')
            plt.grid(True)

        elif measurement_type == 'bjt_curve':
            plt.plot(x_data, y_data * 1000, 'o-')
            plt.title("BJT Curve")
            plt.xlabel('$V_{BE}$ (V)')
            plt.ylabel('$I_C$ (mA)')
            plt.grid(True)

        elif measurement_type == 'single_capture':
            plt.plot(x_data, y_data)
            plt.title("Captured Waveform")
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage (V)')
            plt.grid(True)

        plt.show()

    def _onMeasurementError(self, measurement_type: str, error_msg: str):
        """Handle measurement error signal"""
        self.btn_stop_measurement.setEnabled(False)
        self.statusBar.showMessage(f'Measurement failed: {error_msg}')
        QMessageBox.critical(self, 'Measurement Error', f'{measurement_type}: {error_msg}')

    def stopMeasurement(self):
        """Stop the currently running measurement"""
        if self._measurement_worker is not None and self._measurement_worker.isRunning():
            self._measurement_worker.requestStop()
            self.statusBar.showMessage('Stopping measurement...')
            self.btn_stop_measurement.setEnabled(False)

    def runLEDCurveMeasurement(self):
        """Run LED I-V curve measurement"""
        self._startMeasurement('led_curve')

    def runFrequencyResponse(self):
        """Run frequency response measurement"""
        self._startMeasurement('freq_response')

    def runBJTCurve(self):
        """Run BJT curve tracer"""
        self._startMeasurement('bjt_curve')

    def runMeasurement(self, measurement_type):
        """Run requested measurement"""
        # Placeholder for future expansion
        pass

    def exportData(self):
        """Export measurement data to CSV"""
        self.measurement_panel.exportToCSV()

    def showSettings(self):
        """Show settings dialog"""
        QMessageBox.information(self, 'Settings', 'Settings dialog coming soon!')

    def showAbout(self):
        """Show about dialog"""
        QMessageBox.about(self, 'About LabControl',
            '<h2>LabControl</h2>'
            '<p>Unified laboratory equipment control and automation</p>'
            '<p><b>Version:</b> 1.0</p>'
            '<p><b>Supported Equipment:</b></p>'
            '<ul>'
            '<li>Oscilloscopes: Hantek 6022, Tektronix TDS, Siglent SDS</li>'
            '<li>Power Supplies: Korad KA3305P</li>'
            '<li>Function Generators: OWON, Siglent SDG</li>'
            '<li>Multimeters: Siglent SDM</li>'
            '</ul>'
            '<p>Built with PyQt5 and Python</p>')

    def onScopeSettingsChanged(self):
        """Handle scope settings changes"""
        pass

    def onSupplyOutputChanged(self):
        """Handle supply output changes"""
        pass

    def onGeneratorChanged(self):
        """Handle generator changes"""
        pass

    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(self, 'Exit LabControl',
            'Are you sure you want to exit?\n\nAll devices will remain in their current state.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Stop timers
            if self.refresh_timer:
                self.refresh_timer.stop()

            # Stop discovery worker if running
            if self._discovery_worker is not None and self._discovery_worker.isRunning():
                self._discovery_worker.quit()
                self._discovery_worker.wait(2000)  # Wait max 2 seconds

            # Stop measurement worker if running
            if self._measurement_worker is not None and self._measurement_worker.isRunning():
                self._measurement_worker.requestStop()
                self._measurement_worker.quit()
                self._measurement_worker.wait(2000)  # Wait max 2 seconds

            # Clean up USB devices properly to prevent BUSY errors on next run
            try:
                if self.scope is not None and hasattr(self.scope, 'scope_obj'):
                    self.scope.scope_obj.close_handle()
            except Exception as e:
                print(f"Cleanup warning during close: {e}")

            event.accept()
        else:
            event.ignore()


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName('LabControl')
    app.setOrganizationName('LabControl')

    # Set application font
    font = QFont("Segoe UI", 9)
    app.setFont(font)

    # Create and show main window
    main_window = LabControlMainWindow()
    main_window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
