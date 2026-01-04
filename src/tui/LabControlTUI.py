#!/usr/bin/env python3
"""
LabControl TUI - Terminal User Interface
Minimal black terminal interface using Textual framework
"""

import asyncio
import csv
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import numpy as np
from rich import box
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Static, ProgressBar

from devices.BaseDMM import BaseDMM
from devices.BaseGenerator import BaseGenerator
from devices.BaseScope import BaseScope
from devices.BaseSupply import BaseSupply
from devices.Hantek.HantekBaseScope import HantekScope


# Thread pool for device operations
_executor = ThreadPoolExecutor(max_workers=2)


class MeasurementRunner:
    """Runs measurements in background thread with progress callbacks"""

    def __init__(self, scope=None, supply=None, dmm=None, generator=None):
        self.scope = scope
        self.supply = supply
        self.dmm = dmm
        self.generator = generator
        self._stop = False
        self.progress_callback = None
        self.data_x = []
        self.data_y = []

    def stop(self):
        self._stop = True

    def run_led_curve(self) -> tuple:
        """LED I-V curve measurement"""
        if not self.supply or not self.dmm or not self.scope:
            raise RuntimeError("Need supply, DMM, and scope")

        WAITTIME = 0.2
        Vd, Id = [], []

        VSupplied = self.supply.chan(1)
        VledMeas = self.scope.vertical.chan(1)

        VSupplied.setV(0)
        VSupplied.enable(True)

        voltages = list(np.arange(0, 1.3, 0.02))  # Coarser steps for speed
        total = len(voltages)

        for i, v in enumerate(voltages):
            if self._stop:
                VSupplied.enable(False)
                return None, None

            VSupplied.setV(v)
            time.sleep(WAITTIME)
            curr = self.dmm.get_current()
            volt = VledMeas.getMean()

            Vd.append(volt)
            Id.append(curr)

            if self.progress_callback:
                self.progress_callback(i + 1, total, f"V={v:.2f}")

        VSupplied.enable(False)
        return np.array(Vd), np.array(Id)

    def run_freq_response(self) -> tuple:
        """Frequency response sweep"""
        if not self.scope or not self.generator:
            raise RuntimeError("Need scope and generator")

        scopeVert = self.scope.vertical
        genChan1 = self.generator.chan(1)
        scopeChan1 = scopeVert.chan(1)
        scopeChan2 = scopeVert.chan(2)

        startFreq = 500
        stopFreq = 500000
        nrOfFreqPerDec = 3
        WAITTIME = 0.1

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
        scopeChan1.setCoupling("AC")
        scopeChan2.setCoupling("AC")

        time.sleep(WAITTIME)
        genChan1.enableOutput(True)

        myFreqs = self.generator.createFreqArray(startFreq, stopFreq, nrOfFreqPerDec, 'DEC')
        total = len(myFreqs)

        measFreqs, gains = [], []

        for i, freq in enumerate(myFreqs):
            if self._stop:
                genChan1.enableOutput(False)
                return None, None

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
            gain = val2 / val1 if val1 > 0 else 0
            gains.append(gain)

            scopeChan1.setVdiv(val1 / 4)
            scopeChan2.setVdiv(val2 / 4)

            if self.progress_callback:
                self.progress_callback(i + 1, total, f"f={freq:.0f}Hz")

        genChan1.enableOutput(False)
        return np.array(measFreqs), np.array(gains)

    def run_bjt_curve(self) -> tuple:
        """BJT curve tracer"""
        if not self.supply or not self.dmm or not self.scope:
            raise RuntimeError("Need supply, DMM, and scope")

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

        base_vol, coll_curr = [], []
        voltages = list(np.arange(0, 3, 0.2))  # Coarser for speed
        total = len(voltages)

        for i, v in enumerate(voltages):
            if self._stop:
                collControl.enable(False)
                baseControl.enable(False)
                return None, None

            baseControl.setV(v)
            time.sleep(0.5)
            curr = self.dmm.get_current()
            time.sleep(0.3)
            coll_curr.append(curr)
            basevol = basechan.getMean()
            base_vol.append(basevol)

            if self.progress_callback:
                self.progress_callback(i + 1, total, f"Vb={v:.1f}V")

        collControl.enable(False)
        baseControl.enable(False)
        return np.array(base_vol), np.array(coll_curr)


class DeviceStatusWidget(Static):
    """Display connection status of all devices"""

    def __init__(self):
        super().__init__()
        self.devices = {
            'scope': {'name': 'Scope', 'connected': False, 'info': ''},
            'supply': {'name': 'Supply', 'connected': False, 'info': ''},
            'generator': {'name': 'Generator', 'connected': False, 'info': ''},
            'dmm': {'name': 'DMM', 'connected': False, 'info': ''}
        }

    def render(self) -> RenderableType:
        table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
        table.add_column("Device")
        table.add_column("Status")
        table.add_column("Info")

        for dev_id, dev in self.devices.items():
            status = "[green]OK[/]" if dev['connected'] else "[dim]-[/]"
            info = dev['info'] if dev['connected'] else ""
            table.add_row(dev['name'], status, info)

        return table

    def update_device(self, device_id: str, connected: bool, info: str = ""):
        if device_id in self.devices:
            self.devices[device_id]['connected'] = connected
            self.devices[device_id]['info'] = info
            self.refresh()


class WaveformWidget(Static):
    """ASCII waveform display"""

    def __init__(self):
        super().__init__()
        self.samples = []

    def render(self) -> RenderableType:
        if not self.samples:
            return Text("No waveform - press 'c' to capture", style="dim")

        width = 70
        height = 12

        y_data = np.array(self.samples)
        y_min, y_max = y_data.min(), y_data.max()
        y_range = y_max - y_min if y_max != y_min else 1

        # Resample
        if len(y_data) > width:
            indices = np.linspace(0, len(y_data)-1, width, dtype=int)
            y_plot = y_data[indices]
        else:
            y_plot = y_data

        # Build plot
        lines = []
        for row in range(height):
            threshold = y_max - row * y_range / height
            line = ""
            for val in y_plot:
                if abs(val - threshold) < y_range / height:
                    line += "*"
                elif val > threshold:
                    line += "|"
                else:
                    line += " "
            lines.append(line)

        plot = "\n".join(lines)
        return Text(f"{y_max:+.2f}V\n{plot}\n{y_min:+.2f}V  [{len(self.samples)} samples]")

    def update_waveform(self, waveform):
        if waveform and hasattr(waveform, 'scaledYdata'):
            self.samples = waveform.scaledYdata
            self.refresh()


class MeasurementWidget(Static):
    """Measurement results"""

    def __init__(self):
        super().__init__()
        self.measurements = []

    def render(self) -> RenderableType:
        if not self.measurements:
            return Text("No measurements", style="dim")

        table = Table(box=box.SIMPLE, show_header=True, padding=(0, 1))
        table.add_column("Time")
        table.add_column("Mean", justify="right")
        table.add_column("Pk-Pk", justify="right")

        for m in self.measurements[-8:]:
            table.add_row(
                m['time'].strftime('%H:%M:%S'),
                f"{m['mean']:.3f}V",
                f"{m['pkpk']:.3f}V"
            )

        return table

    def add_measurement(self, meas):
        self.measurements.append(meas)
        self.refresh()


class ResultPlotWidget(Static):
    """ASCII plot for measurement results"""

    def __init__(self):
        super().__init__()
        self.x_data = []
        self.y_data = []
        self.title = ""
        self.x_label = "X"
        self.y_label = "Y"

    def render(self) -> RenderableType:
        if not self.x_data or not self.y_data:
            return Text("No measurement data", style="dim")

        width = 60
        height = 10

        x = np.array(self.x_data)
        y = np.array(self.y_data)

        y_min, y_max = y.min(), y.max()
        y_range = y_max - y_min if y_max != y_min else 1

        # Resample to width
        if len(y) > width:
            indices = np.linspace(0, len(y)-1, width, dtype=int)
            y_plot = y[indices]
        else:
            y_plot = y

        # Build ASCII plot
        lines = []
        for row in range(height):
            threshold = y_max - row * y_range / height
            line = ""
            for val in y_plot:
                if abs(val - threshold) < y_range / height:
                    line += "o"
                elif val > threshold:
                    line += "|"
                else:
                    line += " "
            lines.append(line)

        header = f"{self.title} ({len(self.x_data)} points)"
        plot = "\n".join(lines)
        footer = f"{self.y_label}: {y_min:.3f} - {y_max:.3f}"

        return Text(f"{header}\n{y_max:.2f}\n{plot}\n{y_min:.2f}\n{footer}")

    def set_data(self, x, y, title="", x_label="X", y_label="Y"):
        self.x_data = list(x) if x is not None else []
        self.y_data = list(y) if y is not None else []
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.refresh()


class LabControlTUI(App):
    """Main TUI Application - Minimal black theme"""

    CSS = """
    Screen {
        background: black;
    }
    Header {
        background: black;
        color: white;
        text-style: bold;
    }
    Footer {
        background: #111;
        color: #888;
    }
    Static {
        background: black;
        color: #ccc;
    }
    Button {
        background: #222;
        color: #ccc;
        border: none;
        margin: 0 1;
        min-width: 10;
    }
    Button:hover {
        background: #333;
    }
    Button:focus {
        background: #444;
    }
    Button.-running {
        background: #500;
    }
    #sidebar {
        width: 28;
        background: black;
        border-right: solid #333;
        padding: 1;
    }
    #main {
        background: black;
        padding: 1;
    }
    #waveform {
        height: 16;
        border-bottom: solid #333;
    }
    #results {
        height: 14;
        border-bottom: solid #333;
    }
    #measurements {
        height: 1fr;
    }
    #buttons {
        height: auto;
    }
    .title {
        text-style: bold;
        color: white;
        padding: 0 0 1 0;
    }
    .status {
        color: #888;
        padding: 1 0;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("c", "capture", "Capture"),
        Binding("d", "discover", "Discover"),
        Binding("e", "export", "Export"),
        Binding("l", "led_curve", "LED"),
        Binding("f", "freq_resp", "Freq"),
        Binding("b", "bjt_curve", "BJT"),
        Binding("s", "stop", "Stop"),
        Binding("h", "help", "Help"),
    ]

    TITLE = "LabControl"

    def __init__(self):
        super().__init__()
        self.scope = None
        self.supply = None
        self.generator = None
        self.dmm = None
        self._measurement_runner = None
        self._measurement_type = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=False)

        with Container():
            with Vertical(id="sidebar"):
                yield Static("DEVICES", classes="title")
                self.device_status = DeviceStatusWidget()
                yield self.device_status

                yield Static("")
                yield Static("ACTIONS", classes="title")
                with Vertical(id="buttons"):
                    with Horizontal():
                        yield Button("c Capture", id="btn_capture")
                        yield Button("d Discover", id="btn_discover")
                    with Horizontal():
                        yield Button("l LED", id="btn_led")
                        yield Button("f Freq", id="btn_freq")
                    with Horizontal():
                        yield Button("b BJT", id="btn_bjt")
                        yield Button("s Stop", id="btn_stop")
                    with Horizontal():
                        yield Button("e Export", id="btn_export")

                self.status_label = Static("Ready", classes="status")
                yield self.status_label

            with Vertical(id="main"):
                yield Static("WAVEFORM", classes="title")
                with Container(id="waveform"):
                    self.waveform_widget = WaveformWidget()
                    yield self.waveform_widget

                yield Static("MEASUREMENT RESULT", classes="title")
                with Container(id="results"):
                    self.result_widget = ResultPlotWidget()
                    yield self.result_widget

                yield Static("HISTORY", classes="title")
                with Container(id="measurements"):
                    self.measurement_widget = MeasurementWidget()
                    yield self.measurement_widget

        yield Footer()

    async def on_mount(self) -> None:
        """Start device discovery in background on mount"""
        self.sub_title = "Starting..."
        # Run discovery in background thread to not block UI
        self.run_worker(self._discover_devices_async, exclusive=True)

    async def _discover_devices_async(self) -> dict:
        """Run device discovery in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._discover_devices_sync)

    def _discover_devices_sync(self) -> dict:
        """Synchronous device discovery (runs in thread)"""
        results = {}

        # Scope
        try:
            scope = BaseScope.getDevice()
            if scope:
                results['scope'] = (True, f"{scope.brand} {scope.model}", scope)
            else:
                results['scope'] = (False, "", None)
        except Exception as e:
            results['scope'] = (False, str(e)[:15], None)

        # Supply
        try:
            supply = BaseSupply.getDevice()
            results['supply'] = (True, "OK", supply) if supply else (False, "", None)
        except Exception:
            results['supply'] = (False, "", None)

        # Generator
        try:
            generator = BaseGenerator.getDevice()
            results['generator'] = (True, "OK", generator) if generator else (False, "", None)
        except Exception:
            results['generator'] = (False, "", None)

        # DMM
        try:
            dmm = BaseDMM.getDevice()
            results['dmm'] = (True, "OK", dmm) if dmm else (False, "", None)
        except Exception:
            results['dmm'] = (False, "", None)

        return results

    def on_worker_state_changed(self, event) -> None:
        """Handle worker completion"""
        if event.state.name == "SUCCESS" and event.worker.result:
            results = event.worker.result

            # Update devices
            if 'scope' in results:
                connected, info, device = results['scope']
                self.scope = device
                self.device_status.update_device('scope', connected, info)

            if 'supply' in results:
                connected, info, device = results['supply']
                self.supply = device
                self.device_status.update_device('supply', connected, info)

            if 'generator' in results:
                connected, info, device = results['generator']
                self.generator = device
                self.device_status.update_device('generator', connected, info)

            if 'dmm' in results:
                connected, info, device = results['dmm']
                self.dmm = device
                self.device_status.update_device('dmm', connected, info)

            # Update subtitle
            count = sum(1 for r in results.values() if r[0])
            self.sub_title = f"{count} device(s)"

    def action_discover(self) -> None:
        """Rediscover devices"""
        self.sub_title = "Discovering..."
        self.run_worker(self._discover_devices_async, exclusive=True)

    def action_capture(self) -> None:
        """Capture waveform"""
        if not self.scope:
            self.notify("No scope", severity="warning")
            return

        try:
            chan1 = self.scope.vertical.chan(1)
            waveform = chan1.capture()

            self.waveform_widget.update_waveform(waveform)

            meas = {
                'time': datetime.now(),
                'mean': chan1.getMean(),
                'min': chan1.getMin(),
                'max': chan1.getMax(),
                'pkpk': chan1.getPkPk()
            }
            self.measurement_widget.add_measurement(meas)
            self.notify(f"Captured {len(waveform.scaledYdata)} samples")

        except Exception as e:
            self.notify(f"Error: {e}", severity="error")

    def action_export(self) -> None:
        """Export to CSV"""
        # Export measurement results if available
        if self.result_widget.x_data and self.result_widget.y_data:
            try:
                filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['X', 'Y'])
                    for x, y in zip(self.result_widget.x_data, self.result_widget.y_data):
                        writer.writerow([x, y])
                self.notify(f"Saved: {filename}")
                return
            except Exception as e:
                self.notify(f"Export failed: {e}", severity="error")
                return

        # Fall back to measurement history
        if not self.measurement_widget.measurements:
            self.notify("No data", severity="warning")
            return

        try:
            filename = f"meas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Time', 'Mean', 'Min', 'Max', 'PkPk'])
                for m in self.measurement_widget.measurements:
                    writer.writerow([m['time'], m['mean'], m['min'], m['max'], m['pkpk']])
            self.notify(f"Saved: {filename}")
        except Exception as e:
            self.notify(f"Export failed: {e}", severity="error")

    def action_help(self) -> None:
        """Show help"""
        self.notify("c=capture d=discover l=LED f=Freq b=BJT s=stop e=export q=quit")

    def action_led_curve(self) -> None:
        """Run LED I-V curve measurement"""
        self._run_measurement('led_curve')

    def action_freq_resp(self) -> None:
        """Run frequency response measurement"""
        self._run_measurement('freq_response')

    def action_bjt_curve(self) -> None:
        """Run BJT curve measurement"""
        self._run_measurement('bjt_curve')

    def action_stop(self) -> None:
        """Stop running measurement"""
        if self._measurement_runner:
            self._measurement_runner.stop()
            self.status_label.update("Stopping...")
            self.notify("Stopping measurement...")

    def _run_measurement(self, meas_type: str) -> None:
        """Start a measurement in background"""
        if self._measurement_runner:
            self.notify("Measurement already running", severity="warning")
            return

        self._measurement_type = meas_type
        self._measurement_runner = MeasurementRunner(
            scope=self.scope,
            supply=self.supply,
            dmm=self.dmm,
            generator=self.generator
        )

        names = {'led_curve': 'LED I-V', 'freq_response': 'Freq Response', 'bjt_curve': 'BJT Curve'}
        self.status_label.update(f"Running {names.get(meas_type, meas_type)}...")
        self.sub_title = f"Running {names.get(meas_type, meas_type)}..."

        # Run in background
        self.run_worker(self._execute_measurement, exclusive=False)

    async def _execute_measurement(self) -> tuple:
        """Execute measurement in thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, self._run_measurement_sync)

    def _run_measurement_sync(self) -> tuple:
        """Synchronous measurement execution"""
        runner = self._measurement_runner
        meas_type = self._measurement_type

        # Set up progress callback
        def progress(current, total, status):
            # Can't directly update UI from thread, but we can store progress
            pass

        runner.progress_callback = progress

        try:
            if meas_type == 'led_curve':
                return ('led_curve', *runner.run_led_curve())
            elif meas_type == 'freq_response':
                return ('freq_response', *runner.run_freq_response())
            elif meas_type == 'bjt_curve':
                return ('bjt_curve', *runner.run_bjt_curve())
        except Exception as e:
            return ('error', str(e), None)

        return (None, None, None)

    def on_worker_state_changed(self, event) -> None:
        """Handle worker completion"""
        if event.state.name == "SUCCESS" and event.worker.result:
            result = event.worker.result

            # Check if this is discovery result (dict) or measurement result (tuple)
            if isinstance(result, dict):
                # Device discovery result
                self._handle_discovery_result(result)
            elif isinstance(result, tuple) and len(result) == 3:
                # Measurement result
                self._handle_measurement_result(result)

    def _handle_discovery_result(self, results: dict) -> None:
        """Handle device discovery results"""
        if 'scope' in results:
            connected, info, device = results['scope']
            self.scope = device
            self.device_status.update_device('scope', connected, info)

        if 'supply' in results:
            connected, info, device = results['supply']
            self.supply = device
            self.device_status.update_device('supply', connected, info)

        if 'generator' in results:
            connected, info, device = results['generator']
            self.generator = device
            self.device_status.update_device('generator', connected, info)

        if 'dmm' in results:
            connected, info, device = results['dmm']
            self.dmm = device
            self.device_status.update_device('dmm', connected, info)

        count = sum(1 for r in results.values() if r[0])
        self.sub_title = f"{count} device(s)"
        self.status_label.update("Ready")

    def _handle_measurement_result(self, result: tuple) -> None:
        """Handle measurement results"""
        meas_type, x_data, y_data = result
        self._measurement_runner = None

        if meas_type == 'error':
            self.notify(f"Error: {x_data}", severity="error")
            self.status_label.update("Error")
            self.sub_title = "Error"
            return

        if x_data is None or y_data is None:
            self.notify("Measurement stopped")
            self.status_label.update("Stopped")
            self.sub_title = "Stopped"
            return

        # Update result plot
        titles = {
            'led_curve': ('LED I-V Curve', 'Vd (V)', 'Id (mA)'),
            'freq_response': ('Frequency Response', 'Freq (Hz)', 'Gain'),
            'bjt_curve': ('BJT Curve', 'Vbe (V)', 'Ic (mA)')
        }
        title, x_label, y_label = titles.get(meas_type, ('Result', 'X', 'Y'))

        # Scale current to mA for display
        if meas_type in ['led_curve', 'bjt_curve']:
            y_data = y_data * 1000

        self.result_widget.set_data(x_data, y_data, title, x_label, y_label)

        self.notify(f"Done: {len(x_data)} points")
        self.status_label.update("Ready")
        self.sub_title = f"{title} complete"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn_capture":
            self.action_capture()
        elif event.button.id == "btn_discover":
            self.action_discover()
        elif event.button.id == "btn_export":
            self.action_export()
        elif event.button.id == "btn_led":
            self.action_led_curve()
        elif event.button.id == "btn_freq":
            self.action_freq_resp()
        elif event.button.id == "btn_bjt":
            self.action_bjt_curve()
        elif event.button.id == "btn_stop":
            self.action_stop()


def main():
    """Run the TUI"""
    app = LabControlTUI()
    app.run()


if __name__ == "__main__":
    main()
