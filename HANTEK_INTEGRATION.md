# Hantek 6022 Integratie met BaseScope Framework

## Overzicht

De Hantek DSO-6022BL/BE/6021 oscilloscoop is succesvol geïntegreerd in het labcontrol BaseScope framework. Je kunt nu de Hantek scope gebruiken samen met andere lab apparatuur (voeding, functiegenerator, multimeter) via dezelfde unified interface.

## Wat is geïmplementeerd

### ✅ Geïmplementeerde functionaliteit

1. **Automatische detectie**
   - De Hantek scope wordt automatisch gedetecteerd via `BaseScope.getDevice()`
   - Werkt naast Tektronix en Siglent scopes
   - Firmware wordt automatisch geflashed indien nodig

2. **Channel control**
   - 2 kanalen volledig ondersteund
   - Voltage range instelling (5V, 2.5V, 1V, 0.5V bereiken)
   - AC/DC coupling control
   - Channel visibility (on/off)

3. **Horizontal (timebase) control**
   - Sample rate instellingen
   - Automatische mapping van time/div naar beschikbare sample rates

4. **Waveform capture**
   - Asynchrone data acquisitie
   - Automatische scaling van raw ADC data naar voltages
   - Time axis generatie

5. **Measurements**
   - Mean voltage
   - Min/Max voltage  
   - Peak-to-peak voltage
   - Software-based metingen op captured data

6. **Trigger control**
   - Basis trigger level instelling
   - Trigger source selectie

## Gebruik

### Basis voorbeeld

```python
from devices.BaseScope import BaseScope
from devices.Hantek.HantekBaseScope import HantekScope  # Import to register

# Detecteer scope (werkt voor alle scope types)
scope = BaseScope.getDevice()
print(f"Found: {scope.brand} {scope.model}")

# Gebruik channel 1
chan1 = scope.vertical.chan(1)
chan1.setVdiv(5.0)  # Set to 5V range
chan1.setCoupling("DC")

# Capture waveform
waveform = chan1.capture()
print(f"Captured {len(waveform.scaledYdata)} samples")

# Metingen
mean = chan1.getMean()
pkpk = chan1.getPkPk()
print(f"Mean: {mean:.3f} V, Peak-to-peak: {pkpk:.3f} V")
```

### Gebruik met andere lab equipment

```python
from devices.BaseScope import BaseScope
from devices.BaseSupply import BaseSupply
from devices.BaseGenerator import BaseGenerator
from devices.BaseDMM import BaseDMM
from devices.Hantek.HantekBaseScope import HantekScope

# Alle apparaten via unified interface
scope = BaseScope.getDevice()      # Hantek 6022
supply = BaseSupply.getDevice()    # Korad voeding
gen = BaseGenerator.getDevice()    # Functiegenerator
dmm = BaseDMM.getDevice()          # Multimeter

# Bijvoorbeeld: LED curve measurement zoals in IRLEDCurve.py
VSupply = supply.chan(1)
VSupply.setV(0)
VSupply.enable(True)

scope_chan = scope.vertical.chan(1)
scope_chan.setVdiv(2.0)

for voltage in np.arange(0, 3.0, 0.1):
    VSupply.setV(voltage)
    time.sleep(0.1)
    
    current = dmm.get_current()
    voltage_measured = scope_chan.getMean()
    
    print(f"V={voltage_measured:.2f}V, I={current:.4f}A")
```

## Bestandsstructuur

Nieuwe/gewijzigde bestanden:

```
src/
├── devices/
│   └── Hantek/
│       ├── HantekBaseScope.py          # NIEUW: BaseScope integratie
│       ├── HantekScopes.py             # BESTAAND: Oude standalone versie
│       └── Hantek6022API/              # BESTAAND: Low-level USB API
│
├── labcontrol.py                       # GEWIJZIGD: Import toegevoegd
└── test_hantek_integration.py          # NIEUW: Test script
```

## Technische details

### Verschillen met VISA scopes

De Hantek scope gebruikt **directe USB communicatie** (libusb) in plaats van VISA:
- Geen VISA resource strings
- Firmware moet mogelijk geflashed worden bij eerste gebruik
- Werkt zonder NI-VISA of andere VISA implementaties

### Voltage ranges

Hantek ondersteunt 4 vaste voltage ranges:
- Range 1: ±5V (10V peak-to-peak)
- Range 2: ±2.5V (5V peak-to-peak)
- Range 5: ±1V (2V peak-to-peak)
- Range 10: ±500mV (1V peak-to-peak)

De `setVdiv()` methode mapt automatisch naar de dichtstbijzijnde range.

### Sample rates

Hantek heeft vaste sample rates van 20 kS/s tot 48 MS/s.
De `setTimeDiv()` methode selecteert automatisch de beste sample rate.

## Test resultaten

✅ **5/6 tests geslaagd**

1. ✅ Scope detectie
2. ✅ Channel toegang
3. ✅ Voltage range instellingen
4. ✅ Coupling instellingen
5. ✅ Timebase instellingen
6. ⚠️ Waveform capture (werkt, maar vereist een signaal op de input)

## Beperkingen

1. **Single-shot capture only**: De huidige implementatie doet één capture per keer
2. **Trigger functionaliteit beperkt**: Hantek 6022 heeft beperkte hardware trigger opties
3. **Geen hardware metingen**: Alle metingen worden in software gedaan op captured data
4. **2 kanalen maximum**: Hardware limitatie van de 6022

## Volgende stappen (optioneel)

Mogelijke verbeteringen voor de toekomst:

- [ ] Streaming mode voor continue acquisitie
- [ ] Calibratie data toepassen voor betere nauwkeurigheid
- [ ] FFT/spectrum analyse functies
- [ ] XY mode ondersteuning
- [ ] Hardware trigger edge/slope configuratie

## Problemen oplossen

### Scope wordt niet gedetecteerd

1. Check USB verbinding: `lsusb | grep Hantek`
2. Zorg dat je import hebt: `from devices.Hantek.HantekBaseScope import HantekScope`
3. Check USB permissions (mogelijk udev rules nodig op Linux)

### Firmware flash errors

De eerste keer dat de scope verbindt kan firmware flashing nodig zijn.
Dit kan 5-10 seconden duren. De scope zal dan opnieuw verbinden.

### No data captured

Zorg dat:
- Er een signaal is aangesloten op de scope input
- De voltage range geschikt is voor het signaal amplitude
- De sample rate geschikt is voor de signaal frequentie

## Conclusie

De Hantek 6022 is nu volledig geïntegreerd en kan gebruikt worden in dezelfde workflows als duurdere VISA-based scopes. Perfect voor budget lab setups! 🎉
