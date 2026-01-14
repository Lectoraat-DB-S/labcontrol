# LabControl - Modern Lab Equipment Control System

**Control all your electronic measurement equipment from your laptop with Python**

LabControl is a unified Python framework for controlling oscilloscopes, power supplies, function generators, and multimeters. It provides a standardized interface across different manufacturers, making lab automation simple and consistent.

## ✨ Key Features

- 🔌 **Auto-Discovery** - Automatically detect connected lab equipment
- 🎯 **Unified API** - Same interface for Tektronix, Siglent, Hantek, Korad, and more
- 🖥️ **Two Modern Interfaces** - PyQt5 GUI for visual work, Textual TUI for remote/SSH access
- 📊 **Real-time Visualization** - Live waveform capture and measurements
- 🐍 **Pure Python** - Easy to extend and automate
- 🌐 **Multi-Protocol** - Supports VISA (USB/TCPIP/GPIB), HiSLIP, Serial, and direct USB (libusb)

## 🎯 Quick Start

### Installation

```bash
# Clone repository
git clone -b development --recurse-submodules https://github.com/Lectoraat-DB-S/labcontrol.git
cd labcontrol

# Quick setup (recommended)
./setup.sh          # Linux/Mac
# setup.bat         # Windows
```

<details>
<summary>Manual installation</summary>

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install dependencies
pip install -r src/requirements.txt

# Install Hantek6022 driver (from submodule)
pip install -e src/devices/Hantek6022API
```
</details>

### Launch GUI

```bash
cd src
python launch_gui.py
```

Press **F5** to discover devices, then start capturing waveforms!

### Launch TUI (Terminal Interface)

```bash
cd src
python launch_tui.py
```

Press **d** to discover, **c** to capture, **h** for help.

## 🎨 Two Powerful Interfaces

### 🖥️ PyQt5 GUI - Graphical Interface

Perfect for desktop work with high-quality visualizations:

- **Professional waveform plots** using pyqtgraph
- **Mouse-driven controls** with intuitive layout
- **Live measurements** with visual feedback
- **CSV export** for data analysis
- **Dark theme** for comfortable viewing

**Best for**: Detailed analysis, presentations, learning electronics

### ⌨️ Textual TUI - Terminal Interface

Modern terminal UI for power users and remote work:

- **Keyboard-driven** workflow (vim-like shortcuts)
- **SSH-ready** - control your lab remotely
- **Lightweight** - only 50MB RAM
- **ASCII waveforms** in your terminal
- **Tmux/Screen compatible** for persistent sessions

**Best for**: Remote labs, automation, production testing, SSH access

[📖 Compare Interfaces →](README_INTERFACES.md)

## 🔧 Supported Equipment

### Oscilloscopes

| Manufacturer     | Models                  | Protocol         | Status         |
| ---------------- | ----------------------- | ---------------- | -------------- |
| **Tektronix**    | TDS2xxx, TDS1xxx series | VISA (USB/TCPIP) | ✅ Tested      |
| **Siglent**      | SDS1000, SDS2000 series | VISA (USB/TCPIP) | ✅ Tested      |
| **Hantek**       | DSO-6022BL/BE/21        | USB (libusb)     | ✅ Tested      |
| **Generic SCPI** | Most LXI scopes         | HiSLIP, VISA     | ✅ Should work |

### Power Supplies

| Manufacturer | Models           | Protocol      | Status    |
| ------------ | ---------------- | ------------- | --------- |
| **Korad**    | KA3005P, KD3005P | Serial (VISA) | ✅ Tested |

### Function Generators

| Manufacturer     | Models               | Protocol | Status             |
| ---------------- | -------------------- | -------- | ------------------ |
| **Generic SCPI** | Most SCPI generators | VISA     | ⚠️ Framework ready |

### Multimeters (DMM)

| Manufacturer     | Models         | Protocol | Status             |
| ---------------- | -------------- | -------- | ------------------ |
| **Generic SCPI** | Most SCPI DMMs | VISA     | ⚠️ Framework ready |

## 📚 Project Structure

```
labcontrol/
├── src/
│   ├── devices/           # Device drivers
│   │   ├── BaseScope.py   # Oscilloscope base class
│   │   ├── BaseSupply.py  # Power supply base class
│   │   ├── BaseGenerator.py
│   │   ├── BaseDMM.py
│   │   ├── tektronix/     # Tektronix scopes
│   │   ├── siglent/       # Siglent scopes
│   │   ├── Hantek/        # Hantek USB scopes
│   │   └── Korad/         # Korad supplies
│   ├── gui/               # PyQt5 GUI
│   │   ├── MainWindow.py
│   │   └── widgets/
│   ├── tui/               # Textual TUI
│   │   └── LabControlTUI.py
│   ├── launch_gui.py      # GUI launcher
│   ├── launch_tui.py      # TUI launcher
│   └── labcontrol.py      # Main library
├── docs/
│   ├── GUI_README.md      # GUI user guide
│   ├── TUI_README.md      # TUI user guide
│   ├── INSTALL_GUI.md     # Installation guide
│   └── HANTEK_INTEGRATION.md
└── README_INTERFACES.md   # Interface comparison
```

## 🚀 Usage Examples

### Auto-Discovery

```python
from devices.BaseScope import BaseScope
from devices.BaseSupply import BaseSupply

# Automatically find connected devices
scope = BaseScope.getDevice()
supply = BaseSupply.getDevice()

if scope:
    print(f"Found scope: {scope.idn}")
if supply:
    print(f"Found supply: {supply.idn}")
```

### Capture Waveform

```python
# Capture from channel 1
scope.verticals[0].setScale(1.0)  # 1V/div
scope.horizontal.setScale(0.001)  # 1ms/div

# Trigger setup
scope.trigger.setLevel(0.5)
scope.trigger.setSource(scope.channels[0])

# Acquire waveform
data = scope.getWaveform(scope.channels[0])
print(f"Captured {len(data)} points")
```

### Control Power Supply

```python
# Set voltage and current limit
supply.setVoltage(5.0)  # 5V
supply.setCurrent(1.0)  # 1A limit
supply.setOutput(True)  # Turn on

# Read measurements
voltage = supply.measureVoltage()
current = supply.measureCurrent()
print(f"Output: {voltage}V @ {current}A")
```

## 🔌 Architecture

LabControl uses a **factory pattern** for device discovery:

1. **Base Classes** (`BaseScope`, `BaseSupply`, etc.) define standard interfaces
2. **Device Drivers** inherit from base classes and register automatically
3. **Auto-Discovery** tries each registered driver until a device is found
4. **Unified API** ensures consistent behavior across manufacturers

```python
# Example: Adding a new scope
class MyCustomScope(BaseScope):
    @classmethod
    def getScopeClass(cls, rm, urls, host=None, scopeConfig=None):
        # Try to connect to your scope
        # Return (cls, device, config) if found
        # Return (None, None, None) if not found
        pass
```

The base class automatically registers your custom scope via `__init_subclass__`.

## 🐛 Troubleshooting

### LIBUSB_ERROR_BUSY (Hantek Scopes)

If you see `LIBUSB_ERROR_BUSY` when using Hantek scopes:

```bash
cd src
./fix_usb_busy.sh
```

Then unplug and replug your Hantek scope.

### No Devices Found

```bash
# Check USB connections
lsusb | grep -i "tektronix\|siglent\|hantek"

# Check VISA resources
python3 -c "import pyvisa; rm = pyvisa.ResourceManager('@py'); print(rm.list_resources())"
```

### Permission Denied (Linux)

Add udev rules for USB devices:

```bash
# See INSTALL_GUI.md for detailed instructions
sudo nano /etc/udev/rules.d/99-labcontrol.rules
```

### Import Errors

```bash
# Install all dependencies
pip install -r requirements.txt

# For GUI
pip install PyQt5 pyqtgraph

# For TUI
pip install textual rich

# For VISA
pip install pyvisa pyvisa-py pyusb
```

## 📖 Documentation

- **[GUI_README.md](docs/GUI_README.md)** - Complete GUI user guide
- **[TUI_README.md](docs/TUI_README.md)** - Terminal interface guide with SSH tips
- **[README_INTERFACES.md](README_INTERFACES.md)** - Compare GUI vs TUI
- **[INSTALL_GUI.md](docs/INSTALL_GUI.md)** - Detailed installation instructions
- **[HANTEK_INTEGRATION.md](docs/HANTEK_INTEGRATION.md)** - Hantek scope technical details

## 🌐 Remote Lab Access

Control your lab equipment from anywhere using the TUI:

```bash
# On lab computer
ssh lab@192.168.1.100
cd labcontrol/src
tmux new -s lab
./launch_tui.py

# Detach with Ctrl+B, D
# SSH disconnect won't kill your session!
```

## 🎓 Advanced Features

### Multi-Channel Measurements

```python
# Capture multiple channels simultaneously
ch1_data = scope.getWaveform(scope.channels[0])
ch2_data = scope.getWaveform(scope.channels[1])

# Calculate measurements
from statistics import mean, stdev
print(f"CH1 Mean: {mean(ch1_data):.3f}V")
print(f"CH2 StdDev: {stdev(ch2_data):.3f}V")
```

### Automated Testing

```python
# Automated power supply sweep
for voltage in range(0, 13):
    supply.setVoltage(voltage)
    time.sleep(0.5)
    current = supply.measureCurrent()
    print(f"{voltage}V -> {current}A")
```

### CSV Export

Both GUI and TUI support CSV export:

```bash
# GUI: Ctrl+E or click Export button
# TUI: Press 'e'
# Creates timestamped CSV: waveform_20231215_143022.csv
```

## 🔬 Technical Stack

- **Python 3.8+**
- **PyVISA** - VISA instrument control
- **pyvisa-py** - Pure Python VISA backend
- **PyUSB / libusb** - USB communication for Hantek
- **PySerial** - Serial communication for Korad
- **PyQt5** - GUI framework
- **pyqtgraph** - Fast plotting library
- **Textual** - Modern TUI framework
- **Rich** - Terminal formatting

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Additional device drivers (Rigol, Keysight, etc.)
- [ ] FFT/Spectrum analysis
- [ ] Protocol decoders (I2C, SPI, UART)
- [ ] Waveform math (add, subtract, multiply channels)
- [ ] Save/load measurement sessions
- [ ] Multi-scope support

## 📝 License

[Add your license here]

## 🙏 Acknowledgments

Built with:

- **WinPython** - Self-contained Python distribution
- **PyVISA** - Instrument control library
- **Hantek 6022** - Community drivers
- **PyQt5** & **Textual** - Interface frameworks

## 📞 Support

- **Issues**: Use GitHub issue tracker
- **Documentation**: See `docs/` folder
- **USB Troubleshooting**: Run `./fix_usb_busy.sh`

## 🎯 What's Next?

### For Beginners

```bash
# Start with the GUI
./launch_gui.py
# Press F5 to discover devices
# Click "Capture" to see waveforms
```

### For Advanced Users

```bash
# Try the TUI
./launch_tui.py
# Learn keyboard shortcuts (press 'h')
# Set up SSH access for remote control
```

### For Developers

```python
# Use LabControl as a library
from devices.BaseScope import BaseScope
scope = BaseScope.getDevice()
# Build your own automation scripts
```

---

**LabControl** - Modern lab equipment control made simple

_Control your oscilloscope, power supply, generator, and multimeter with a unified Python API_

🔬 **Happy Measuring!** ⚡
