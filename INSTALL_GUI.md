# LabControl GUI - Installatie Instructies

## 📦 Vereiste Packages

De GUI heeft de volgende Python packages nodig:

```bash
# Essentieel (VERPLICHT)
pip install PyQt5

# Aanbevolen (voor mooie scope plots)
pip install pyqtgraph

# Al geïnstalleerd via je labcontrol setup:
# - numpy
# - pyvisa
# - matplotlib
```

## 🚀 Snelle Installatie

### Optie 1: Alles tegelijk installeren

```bash
# In je virtual environment
cd /home/tom/labcontrol/labcontrol
source labcontrol/bin/activate

# Installeer GUI dependencies
pip install PyQt5 pyqtgraph

# Test de installatie
cd src
python3 launch_gui.py
```

### Optie 2: requirements file gebruiken

```bash
# Maak requirements_gui.txt (of gebruik bestaande)
cd /home/tom/labcontrol/labcontrol/src
echo "PyQt5>=5.15.0" > requirements_gui.txt
echo "pyqtgraph>=0.12.0" >> requirements_gui.txt

# Installeer
pip install -r requirements_gui.txt
```

## ✅ Verificatie

Test of alles werkt:

```bash
cd /home/tom/labcontrol/labcontrol/src

# Test imports
python3 << 'EOF'
try:
    import PyQt5
    print("✓ PyQt5 installed")
except:
    print("✗ PyQt5 missing - run: pip install PyQt5")

try:
    import pyqtgraph
    print("✓ pyqtgraph installed")
except:
    print("⚠ pyqtgraph missing - run: pip install pyqtgraph (optional)")

print("\nReady to launch GUI!")
EOF
```

## 🎬 GUI Starten

```bash
cd /home/tom/labcontrol/labcontrol/src

# Methode 1: Via launcher script
python3 launch_gui.py

# Methode 2: Direct
python3 -m gui.MainWindow

# Methode 3: Als executable
chmod +x launch_gui.py
./launch_gui.py
```

## 🐧 Linux Specifieke Setup

### USB Permissions (voor niet-root access)

Als je apparaten niet gedetecteerd worden, zijn waarschijnlijk udev rules nodig:

```bash
# Maak udev rule voor Hantek 6022
sudo nano /etc/udev/rules.d/99-hantek.rules

# Voeg toe:
# Hantek DSO-6022
SUBSYSTEM=="usb", ATTR{idVendor}=="04b5", ATTR{idProduct}=="602a", MODE="0666"
SUBSYSTEM=="usb", ATTR{idVendor}=="04b4", ATTR{idProduct}=="6022", MODE="0666"

# Herlaad rules
sudo udevadm control --reload-rules
sudo udevadm trigger

# Plug je Hantek uit en weer in
```

### Desktop Entry (optioneel)

Maak een desktop launcher:

```bash
# Maak .desktop file
cat > ~/.local/share/applications/labcontrol.desktop << 'EOF'
[Desktop Entry]
Version=1.0
Type=Application
Name=LabControl
Comment=Lab Equipment Control
Exec=/home/tom/labcontrol/labcontrol/labcontrol/bin/python3 /home/tom/labcontrol/labcontrol/src/launch_gui.py
Icon=applications-electronics
Terminal=false
Categories=Science;Electronics;
EOF

# Nu kun je LabControl vinden in je applicatiemenu!
```

## ⚠️ Troubleshooting

### "No module named 'PyQt5'"

```bash
# Check of je in de juiste virtual environment zit
which python3
# Should show: /home/tom/labcontrol/labcontrol/labcontrol/bin/python3

# Zo niet, activeer:
source /home/tom/labcontrol/labcontrol/labcontrol/bin/activate

# Installeer PyQt5
pip install PyQt5
```

### "No module named 'gui'"

```bash
# Zorg dat je in de src directory bent
cd /home/tom/labcontrol/labcontrol/src
python3 launch_gui.py
```

### GUI start niet / crash

```bash
# Check dependencies
python3 -c "import PyQt5.QtWidgets; print('PyQt5 OK')"
python3 -c "import pyqtgraph; print('pyqtgraph OK')"

# Check Qt platform
export QT_DEBUG_PLUGINS=1
python3 launch_gui.py

# Als je een headless server gebruikt (geen X11):
# Je hebt een display server nodig (Xvfb, VNC, of physical display)
```

### Apparaten niet gedetecteerd

1. **Check USB verbindingen**
   ```bash
   lsusb | grep -i hantek
   lsusb | grep -i korad
   ```

2. **Check permissions**
   ```bash
   # Test of je USB kunt lezen
   python3 -c "import usb.core; print(list(usb.core.find(find_all=True)))"
   ```

3. **In GUI: druk F5**
   - Device discovery opnieuw uitvoeren

## 📊 Features na Installatie

Na succesvolle installatie kun je:

✅ **Auto-discover** alle aangesloten apparaten (F5)  
✅ **Live scope** waveforms visualiseren  
✅ **Control** voeding, generator, scope vanuit GUI  
✅ **Quick actions** voor veel gebruikte metingen  
✅ **Export** data naar CSV met één klik  
✅ **Dark theme** voor comfortabel werken  

## 🎓 First Launch Checklist

Na eerste keer opstarten:

1. ✅ Sluit je apparaten aan (USB/Ethernet)
2. ✅ Start de GUI: `python3 launch_gui.py`
3. ✅ Klik "🔍 Discover" of druk F5
4. ✅ Check "Device Status" panel - moet 🟢 tonen
5. ✅ Test een capture: klik "📸 Capture"
6. ✅ Klaar om te meten!

## 💡 Tips

- **Virtual Environment**: Altijd activeren voor dependencies
  ```bash
  source /home/tom/labcontrol/labcontrol/labcontrol/bin/activate
  ```

- **Alias maken** voor snel starten:
  ```bash
  echo 'alias labcontrol="cd /home/tom/labcontrol/labcontrol/src && python3 launch_gui.py"' >> ~/.bashrc
  source ~/.bashrc
  
  # Nu kun je overal typen:
  labcontrol
  ```

- **Auto-start** bij boot (systemd service):
  ```bash
  # Voor gevorderde gebruikers
  # Maak /etc/systemd/system/labcontrol.service
  ```

## 🔄 Updates

Als je de GUI update (nieuwe features):

```bash
cd /home/tom/labcontrol/labcontrol/src
git pull  # Als je git gebruikt

# GUI restart
python3 launch_gui.py
```

Dependencies updaten:

```bash
pip install --upgrade PyQt5 pyqtgraph
```

## 📝 Volgende Stappen

Na installatie, zie:
- `GUI_README.md` - Gebruikershandleiding
- `HANTEK_INTEGRATION.md` - Hantek scope details
- Test scripts in `src/` voor troubleshooting

Veel plezier met je nieuwe GUI! 🎉
