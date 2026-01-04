# LabControl GUI - Unified Lab Equipment Control

## 🎯 Overzicht

De LabControl GUI is een moderne, gebruiksvriendelijke interface voor het besturen van al je lab apparatuur vanuit één applicatie.

### ✨ Key Features

- **🔍 Auto-Discovery**: Automatische detectie van alle aangesloten apparaten
- **📊 Live Visualization**: Real-time oscilloscoop waveform display
- **⚡ Unified Control**: Alle apparaten (scope, voeding, generator, DMM) in één interface
- **🎨 Dark/Light Theme**: Oogvriendelijk donker thema (standaard) met light mode optie
- **📸 One-Click Measurements**: Snelle metingen met voorgedefinieerde presets
- **💾 Data Export**: Direct exporteren naar CSV voor verdere analyse
- **🔄 Auto-Refresh**: Optionele automatische data refresh
- **⚙️ Device Presets**: Sla complete test setups op

## 🚀 Quick Start

### Installatie

```bash
# Installeer benodigde packages (als nog niet gedaan)
pip install PyQt5 pyqtgraph

# Navigeer naar de src directory
cd /home/tom/labcontrol/labcontrol/src

# Start de GUI
python3 launch_gui.py

# Of gebruik de executable:
./launch_gui.py
```

### Eerste Gebruik

1. **Start de applicatie**
   ```bash
   ./launch_gui.py
   ```

2. **Discover Devices**
   - Klik op "🔍 Discover" in de toolbar
   - Of druk F5
   - Wacht tot alle apparaten gedetecteerd zijn

3. **Begin met meten!**
   - Selecteer een apparaat tab (Scope, Supply, etc.)
   - Pas instellingen aan
   - Klik "Apply Settings"
   - Voor scope: klik "📸 Capture" voor een waveform

## 📱 Interface Layout

```
┌────────────────────────────────────────────────────────────┐
│  LabControl                                   [Menu] [▣][×] │
├────────────────────────────────────────────────────────────┤
│  🔍 Discover │ 📸 Capture │ ▶ Auto Refresh │ 💾 Export     │ Toolbar
├──────────────────────┬─────────────────────────────────────┤
│                      │                                      │
│  Device Status       │        Live Scope View              │
│  ┌─────────────┐    │   ┌────────────────────────────┐   │
│  │📊 Scope  🟢│    │   │                             │   │
│  │⚡ Supply 🟢│    │   │   [Waveform Display]       │   │
│  │〰️ Gen    🔴│    │   │                             │   │
│  │🔢 DMM    🔴│    │   └────────────────────────────┘   │
│  └─────────────┘    │                                      │
│                      │   Measurements                       │
│  Device Controls     │   ┌────────────────────────────┐   │
│  ┌─────────────┐    │   │Time  │Mean│Min│Max│Pk-Pk  │   │
│  │             │    │   │10:30│2.5V│0V │5V │5V     │   │
│  │  [Scope]    │    │   └────────────────────────────┘   │
│  │  [Supply]   │    │                                      │
│  │  [Generator]│    │                                      │
│  │  [DMM]      │    │                                      │
│  └─────────────┘    │                                      │
│                      │                                      │
│  Quick Actions       │                                      │
│  ┌─────────────┐    │                                      │
│  │📈 LED Curve │    │                                      │
│  │📉 Freq Resp │    │                                      │
│  └─────────────┘    │                                      │
└──────────────────────┴─────────────────────────────────────┘
│ Devices: 2 connected │ 🟢 Connected                        │ Status
└────────────────────────────────────────────────────────────┘
```

## 🎛️ Device Controls

### Oscilloscope Tab
- **CH1 V/div**: Voltage per divisie (0.001V - 100V)
- **Time/div**: Tijd per divisie (1µs - 10s)
- **Coupling**: AC of DC
- **Apply Settings**: Pas instellingen toe op scope

### Power Supply Tab
- **Voltage**: Output spanning instellen (0-30V)
- **Current Limit**: Stroom limiet (0-5A)
- **Output ON/OFF**: Schakel uitgang aan/uit
- **Apply**: Activeer instellingen

### Function Generator Tab
- **Waveform**: Sine, Square, Triangle
- **Frequency**: 1Hz - 1MHz
- **Amplitude**: 0-10V
- **Apply**: Genereer signaal

### Multimeter Tab
- **Live Reading**: Automatische update van meting
- **Large LCD Display**: Duidelijk afleesbaar

## ⚡ Quick Actions

Voorgedefinieerde metingen met één klik:

### 📈 LED I-V Curve
- Automatische sweep van LED karakteristiek
- Gebruikt: Voeding + Scope + DMM
- Output: Grafiek en CSV data

### 📉 Frequency Response
- AC sweep voor frequentie response
- Gebruikt: Generator + Scope
- Meet amplitude en fase

### 🔌 BJT Curve
- Transistor curve tracer
- Gebruikt: Voeding (2 kanalen) + DMM

### 📸 Single Capture
- Enkele waveform capture
- Direct naar measurement panel
- Inclusief statistieken

## ⌨️ Keyboard Shortcuts

| Shortcut | Actie |
|----------|-------|
| `F5` | Discover Devices |
| `Ctrl+E` | Export Measurements |
| `Ctrl+T` | Toggle Theme (Dark/Light) |
| `Ctrl+Q` | Quit Application |

## 💡 Tips & Tricks

### Efficiënt Werken

1. **Auto-Refresh voor DMM**
   - Schakel "▶ Auto Refresh" in voor continue metingen
   - Handig bij het trimmen van circuits

2. **Meerdere Captures**
   - Klik herhaaldelijk op "📸 Capture"
   - Alle metingen worden opgeslagen in de tabel
   - Export alles in één keer naar CSV

3. **Dark Theme voor Lange Sessies**
   - Standaard dark theme is oogvriendelijk
   - Toggle met Ctrl+T indien gewenst

4. **Device Status Monitor**
   - Houd de status widget in de gaten
   - 🟢 = Connected & Ready
   - 🔴 = Niet gedetecteerd
   - Grijs = Error

### Troubleshooting

**Geen devices gedetecteerd?**
- Check USB verbindingen
- Klik op F5 om opnieuw te zoeken
- Check permissions (Linux: mogelijk udev rules nodig)

**Scope capture faalt?**
- Zorg dat er een signaal is op de input
- Check voltage range instelling
- Check coupling (AC/DC)

**GUI start niet?**
```bash
# Check dependencies
pip list | grep PyQt5
pip list | grep pyqtgraph

# Installeer indien nodig
pip install PyQt5 pyqtgraph
```

## 🔧 Uitbreidingen

De GUI is modulair opgezet en makkelijk uit te breiden:

### Nieuwe Widget Toevoegen

```python
# In gui/widgets/MyWidget.py
from PyQt5.QtWidgets import QWidget

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Your implementation

# In MainWindow.py
from gui.widgets.MyWidget import MyWidget

# Add to tabs
self.my_widget = MyWidget()
self.device_tabs.addTab(self.my_widget, "My Device")
```

### Nieuwe Quick Action

```python
# In MainWindow.py
def createQuickActionsPanel(self):
    # ...
    btn_my_action = QPushButton("🔬 My Measurement")
    btn_my_action.clicked.connect(self.runMyMeasurement)
    layout.addWidget(btn_my_action)

def runMyMeasurement(self):
    # Your measurement code
    pass
```

## 📊 Data Export

Exported CSV formaat:

```csv
Timestamp,Mean (V),Min (V),Max (V),Pk-Pk (V)
10:30:15,2.500,0.100,4.900,4.800
10:30:16,2.498,0.105,4.895,4.790
```

Perfect voor import in:
- Excel / LibreOffice Calc
- Matlab / Octave
- Python (pandas)
- Jupyter notebooks

## 🎨 Thema's

### Dark Theme (Default)
- Zwarte achtergrond (#2b2b2b)
- Hoog contrast
- Minder oogvermoeiend bij langdurig gebruik

### Light Theme
- Witte achtergrond
- Standaard OS styling
- Toggle met Ctrl+T

## 🚀 Future Features

Geplande uitbreidingen:
- [ ] Waveform zoom & pan
- [ ] Cursor measurements
- [ ] FFT analysis
- [ ] Automated test sequences
- [ ] Remote control via web interface
- [ ] Multi-scope support
- [ ] Protocol analyzers (SPI, I2C)
- [ ] Screenshot capture

## 🐛 Known Issues

- pyqtgraph installatie is optioneel maar aanbevolen voor scope viz
- Eerste firmware flash van Hantek kan 5-10s duren
- DMM auto-refresh werkt alleen als DMM gedetecteerd is

## 📝 Changelog

### Version 1.0 (Current)
- ✅ Initial release
- ✅ Auto device discovery
- ✅ Scope, Supply, Generator, DMM support
- ✅ Dark theme
- ✅ CSV export
- ✅ Quick action presets
- ✅ Hantek 6022 integration

## 💬 Support

Voor vragen, bugs of feature requests:
- Check de bestaande TODO comments in de code
- Raadpleeg de device-specifieke documentatie
- Test met test_hantek_integration.py voor troubleshooting

## 🎓 Voor Developers

De GUI is gebouwd volgens PyQt5 best practices:

**Architecture:**
- `MainWindow.py`: Main application window
- `widgets/`: Modular device widgets
- Signals/Slots voor event handling
- MVC pattern voor data/UI separation

**Adding Features:**
1. Create widget in `gui/widgets/`
2. Import in `MainWindow.py`
3. Add to appropriate tab or panel
4. Connect signals as needed

**Styling:**
- CSS-like Qt stylesheets
- Centralized in `applyTheme()`
- Easy to customize

Happy measuring! 🔬⚡📊
