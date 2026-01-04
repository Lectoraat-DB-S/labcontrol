# GUI Hantek Scope Fix - Samenvatting

## Problemen die opgelost zijn

### 1. LIBUSB_ERROR_BUSY [-6]
**Oorzaak:** De USB device werd al geopend tijdens device discovery en werd niet correct vrijgegeven voor hergebruik.

**Oplossing:**
- `HantekBaseScope.py`: Aangepast om USB handle correct te sluiten en te heropenen
- Toegevoegd: automatische cleanup van bestaande handles voordat een nieuwe wordt geopend
- Toegevoegd: retry logica met USB reset bij failures

### 2. Scope niet zichtbaar aan rechterkant van GUI
**Oorzaak:** De GUI toonde alleen een label met "No scope detected" en schakelde nooit over naar de echte scope plot widget.

**Oplossing:**
- `MainWindow.py`: QStackedWidget toegevoegd om te wisselen tussen "no scope" boodschap en scope plot
- Bij succesvolle detectie wordt nu de scope plot widget automatisch getoond
- Bij errors worden gebruiksvriendelijke instructies getoond

## Bestanden aangepast

### src/devices/Hantek/HantekBaseScope.py
1. **getScopeClass()**: Verwijderd `setup()` call om dubbele USB open te voorkomen
2. **__init__()**: Toegevoegd USB cleanup en retry logica:
   - Sluit eerst bestaande handle
   - Probeert dan opnieuw te openen met delay
   - Betere error handling

### src/gui/MainWindow.py
1. **createVisualizationPanel()**: 
   - QStackedWidget toegevoegd voor scope view
   - Pagina 0: "No scope" label
   - Pagina 1: Echte scope plot widget

2. **discoverDevices()**:
   - Voegt scope plot widget toe aan stack bij detectie
   - Schakelt automatisch naar de juiste view
   - Verbeterde error messages met specifieke instructies

## Nieuwe bestanden

### src/reset_hantek_usb.py
Een hulpprogramma om de Hantek USB verbinding te resetten zonder fysiek uit te pluggen.

**Gebruik:**
```bash
python src/reset_hantek_usb.py
```

Dit script:
- Zoekt naar alle Hantek devices
- Released USB interfaces
- Sluit handles correct af
- Geeft duidelijke feedback

## Hoe te testen

1. **Start de GUI:**
   ```bash
   python src/launch_gui.py
   ```

2. **Klik op "Discover Devices" of druk F5**

3. **Verwacht resultaat:**
   - Linkerpaneel: Scope wordt getoond als "🟢 Hantek DSO-6022BL" (of uw model)
   - Rechterpaneel: Scope plot widget wordt getoond met grid
   - Status bar: "Found scope: Hantek DSO-6022BL"

4. **Klik op "📸 Capture" om een waveform te zien**

## Bij problemen

### Als je nog steeds LIBUSB_ERROR_BUSY krijgt:

**Optie 1: Fysiek reset (snelst):**
1. Unplug de Hantek scope
2. Wacht 3 seconden
3. Plug het terug in
4. Klik "Discover Devices"

**Optie 2: Software reset:**
```bash
python src/reset_hantek_usb.py
```

**Optie 3: Kill alle processen:**
```bash
pkill -f hantek
pkill -f Hantek
```

### Als de scope niet wordt gedetecteerd:

1. Check USB verbinding:
   ```bash
   lsusb | grep -i "04b5\|04b4"
   ```
   
2. Check USB permissions:
   ```bash
   ls -l /dev/bus/usb/*/*
   ```

3. Run het test script:
   ```bash
   python src/test_hantek_integration.py
   ```

## Wayland compositor crash

De error "The Wayland connection broke. Did the Wayland compositor die?" is meestal een gevolg van de LIBUSB_ERROR_BUSY. Na de fix hierboven zou dit niet meer moeten gebeuren.

Als het nog steeds crasht:
- Probeer de applicatie te draaien met X11 in plaats van Wayland:
  ```bash
  QT_QPA_PLATFORM=xcb python src/launch_gui.py
  ```

## Technische details

### USB Handle Management Flow
1. `getScopeClass()` - Detecteert alleen, opent NIET
2. `__init__()` - Sluit bestaande handle → Opent nieuwe handle
3. Bij capture - Gebruikt bestaande handle
4. Bij `__del__()` - Sluit handle netjes af

### GUI View Stack
- Index 0: "No scope" label (default)
- Index 1: Scope plot widget (bij succesvolle detectie)
- Switcht automatisch op basis van discovery result

### Error Recovery
- Try bestaande handle sluiten (kan falen, wordt genegeerd)
- Sleep 0.5s voor USB stabilisatie
- Open nieuwe handle
- Bij failure: duidelijke instructies in GUI
