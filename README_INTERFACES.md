# LabControl - User Interfaces Overview 🚀

Je hebt nu **TWEE complete interfaces** voor je lab equipment!

## 🎯 Welke Interface Kiezen?

### 🖥️ PyQt5 GUI - Grafisch

**Gebruik wanneer:**
- Je high-quality waveform plots wilt
- Je met muis werkt
- Je lokaal op desktop werkt
- Je visual feedback wilt

**Starten:**
```bash
cd /home/tom/labcontrol/labcontrol/src
pip install PyQt5 pyqtgraph  # Eenmalig
./launch_gui.py
```

### ⌨️ Textual TUI - Terminal

**Gebruik wanneer:**
- Je van keyboard shortcuts houdt
- Je via SSH werkt (remote lab!)
- Je minimaal resources wilt (50MB vs 200MB)
- Je in tmux/screen werkt
- Je cool wilt zijn 😎

**Starten:**
```bash
cd /home/tom/labcontrol/labcontrol/src
pip install textual rich  # Eenmalig
./launch_tui.py
```

## 📊 Vergelijking

| Feature | PyQt5 GUI | Textual TUI |
|---------|-----------|-------------|
| **Waveform Quality** | ★★★★★ (PyQtGraph) | ★★★☆☆ (ASCII) |
| **Speed** | ★★★★☆ | ★★★★★ |
| **Memory** | 200MB+ | ~50MB |
| **SSH Support** | ❌ | ✅ |
| **Keyboard-driven** | ★★★☆☆ | ★★★★★ |
| **Setup Time** | 5 min | 2 min |
| **Cool Factor** | ★★★★☆ | ★★★★★ |

## 🎨 Features (beide interfaces)

### Gemeenschappelijk

✅ **Auto-Discovery** - Druk F5 (GUI) of 'd' (TUI)  
✅ **Live Status** - Zie welke apparaten verbonden zijn  
✅ **Scope Capture** - Waveform acquisitie  
✅ **Measurements** - Mean, Min, Max, Pk-Pk  
✅ **CSV Export** - Data export  
✅ **Dark Theme** - Oogvriendelijk  

### GUI Exclusief

🎨 **PyQtGraph Plots** - Professional quality  
🖱️ **Mouse Control** - Point & click  
📊 **Tabbed Interface** - Device panels  
🎯 **Visual Settings** - Spinboxes, sliders  

### TUI Exclusief

⚡ **Ultra-Fast** - Keyboard only  
🔌 **SSH Ready** - Remote access  
📟 **ASCII Art** - Waveforms in terminal  
🎹 **Vim-like** - hjkl navigation (optioneel)  
📱 **Lightweight** - Raspberry Pi ready  

## 🚀 Quick Start

### Eerste Keer Setup

```bash
# 1. Activeer virtual environment
cd /home/tom/labcontrol/labcontrol
source labcontrol/bin/activate

# 2. Installeer GUI dependencies
pip install PyQt5 pyqtgraph

# 3. Installeer TUI dependencies  
pip install textual rich

# 4. Test Hantek (als je LIBUSB_ERROR_BUSY krijgt)
cd src
./fix_usb_busy.sh
# Unplug en plug Hantek terug in

# 5. Start interface naar keuze
./launch_gui.py   # GUI
./launch_tui.py   # TUI
```

## ⌨️ Keyboard Shortcuts

### GUI (PyQt5)
- `F5` - Discover Devices
- `Ctrl+E` - Export CSV
- `Ctrl+T` - Toggle Theme
- `Ctrl+Q` - Quit

### TUI (Textual)
- `d` - Discover Devices
- `c` - Capture Waveform
- `e` - Export CSV
- `r` - Refresh
- `h` - Help
- `q` - Quit

## 🐛 Troubleshooting

### LIBUSB_ERROR_BUSY (Hantek)

```bash
# Run fix script
./fix_usb_busy.sh

# Manually:
# 1. Unplug Hantek
# 2. Kill all Python processes:
pkill -9 python
# 3. Plug Hantek back in
# 4. Try again
```

### GUI Niet Starten

```bash
# Check PyQt5
python3 -c "import PyQt5; print('OK')"

# Installeer indien nodig
pip install PyQt5 pyqtgraph
```

### TUI Import Errors

```bash
# Check textual
python3 -c "import textual; print('OK')"

# Installeer indien nodig
pip install textual rich
```

### Geen Devices Gevonden

```bash
# Check USB
lsusb | grep -i hantek

# Check permissions (Linux)
# Mogelijk udev rules nodig (zie INSTALL_GUI.md)
```

## 📚 Documentatie

Gedetailleerde guides:

- **`GUI_README.md`** - PyQt5 GUI gebruikershandleiding
- **`TUI_README.md`** - Terminal UI met SSH tips
- **`INSTALL_GUI.md`** - Installatie instructies
- **`HANTEK_INTEGRATION.md`** - Hantek scope details

## 💡 Pro Tips

### GUI Tips

**1. Dark Theme Permanently**
- Staat standaard aan, maar toggle met Ctrl+T

**2. Desktop Shortcut**
```bash
# Maak .desktop file (Linux)
cat > ~/.local/share/applications/labcontrol-gui.desktop << 'EOF'
[Desktop Entry]
Name=LabControl GUI
Exec=/home/tom/labcontrol/labcontrol/src/launch_gui.py
Type=Application
Terminal=false
EOF
```

**3. Auto-Refresh DMM**
- Schakel in voor continue metingen
- Handig bij trimmen

### TUI Tips

**1. SSH Alias**
```bash
# In .bashrc:
alias labtui='ssh -t labserver "cd labcontrol/src && ./launch_tui.py"'

# Nu vanaf laptop:
labtui
```

**2. Tmux Integration**
```bash
# Start persistent session
tmux new -s lab
./launch_tui.py
# Ctrl+B, D to detach
# SSH disconnect = TUI keeps running!
```

**3. Quick Measure & Exit**
```bash
# Automation script
#!/usr/bin/expect
spawn ./launch_tui.py
expect "LabControl TUI"
send "c\r"
sleep 2
send "e\r"
send "q\r"
```

## 🎓 Advanced Usage

### Remote Lab (TUI)

```bash
# Thuis op laptop:
ssh lab@192.168.1.100

# Op lab server:
cd labcontrol/src
./launch_tui.py

# Bestur lab vanaf je bank! 🛋️
```

### Dual Monitor (GUI)

```bash
# Terminal op monitor 1
./launch_gui.py

# Jupyter op monitor 2
jupyter lab

# Best of both worlds!
```

### Automation (beide)

```python
# automation.py
from devices.BaseScope import BaseScope
from devices.Hantek.HantekBaseScope import HantekScope

scope = BaseScope.getDevice()
# ... your automation
```

## 🆚 Use Case Matrix

| Scenario | Best Interface |
|----------|----------------|
| Quick daily checks | TUI |
| Detailed waveform analysis | GUI |
| Remote via SSH | TUI |
| Presentation/demo | GUI |
| Automation scripting | Both (Python API) |
| Learning electronics | GUI (visual) |
| Production testing | TUI (fast) |
| Long measurements | TUI (tmux) |

## 🎯 Wat Nu?

### Beginners
```bash
# Start met GUI
./launch_gui.py
# Druk F5
# Klik "Capture"
# Experiment!
```

### Gevorderden
```bash
# Try TUI
./launch_tui.py
# Learn shortcuts ('h' for help)
# Setup SSH access
# Automate!
```

### Experts
```bash
# Beide gebruiken:
# - TUI voor quick checks
# - GUI voor analysis
# - Python scripts voor automation
```

## 🚀 Features Roadmap

Beide interfaces krijgen:
- [ ] FFT/Spectrum analysis
- [ ] Protocol decoders (I2C, SPI)
- [ ] Multi-scope support
- [ ] Waveform templates
- [ ] Cloud sync (optional)

## 📞 Support

**GUI Issues**: Check `GUI_README.md`  
**TUI Issues**: Check `TUI_README.md`  
**Hantek Issues**: Check `HANTEK_INTEGRATION.md`  
**USB Issues**: Run `./fix_usb_busy.sh`

## 🎉 Final Words

Je hebt nu **twee production-ready interfaces**:

✅ **PyQt5 GUI** - Beautiful, visual, powerful  
✅ **Textual TUI** - Fast, remote-ready, modern  

**Kies wat past bij je workflow, of gebruik beide!**

Veel plezier met je moderne lab setup! 🔬⚡

---

*Both interfaces built with ❤️ and modern Python*

**GUI**: PyQt5 + pyqtgraph  
**TUI**: Textual + Rich  
**Backend**: Unified device APIs
