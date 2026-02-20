# Labcontrol V2 - CLI-first Instrument Configuration

CLI tool voor snelle oscilloscope configuratie via YAML presets, met ingebouwde capture en plot functionaliteit.

## Installatie

```bash
cd labcontrol
python3 -m venv venv
```

Activeer de virtual environment:

```bash
# Linux / macOS (bash/zsh)
source venv/bin/activate

# Linux / macOS (fish)
source venv/bin/activate.fish

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate.bat
```

Installeer het pakket:

```bash
pip install -e ".[dev]"
```

## Commands

### Apparaten

```bash
labcontrol devices              # Detecteer aangesloten apparaten
```

### Presets

```bash
labcontrol list                 # Toon beschikbare presets
labcontrol show <preset>        # Details van een preset bekijken
labcontrol load <preset>        # Preset laden naar scope
```

Presets staan in `presets/examples/`. Eigen presets toevoegen als YAML bestanden in `presets/user/`.

### Scope configuratie

```bash
labcontrol scope status         # Huidige scope instellingen
labcontrol scope set ch1.vdiv=0.5 ch2.coupling=AC timebase=1ms
```

### Capture & Export

```bash
labcontrol scope capture                        # Samenvatting in terminal (min/max/avg)
labcontrol scope capture --save snapshot.png    # Plot opslaan als PNG/SVG
labcontrol scope capture --csv data.csv         # Data exporteren als CSV
labcontrol scope capture --samples 2048         # Aantal samples instellen
labcontrol scope capture --duration 0.05        # 50ms capture (past sample rate aan)
labcontrol scope capture --interval 0.00005     # 50us interval (= 20 kS/s)
labcontrol scope capture --title "RC Filter"    # Plot titel meegeven
```

Opties zijn combineerbaar:

```bash
labcontrol scope capture --save plot.png --csv data.csv --samples 2048 --title "Meting 1"
labcontrol scope capture --duration 0.1 --save capture.png --csv capture.csv
```

### OpenHantek

```bash
labcontrol openhantek           # Start OpenHantek (disconnect scope automatisch)
```

## Workflow

1. `labcontrol load basic_scope` - Configureer scope via preset
2. `labcontrol scope capture --save meting.png --csv meting.csv` - Capture + export
3. `labcontrol openhantek` - Optioneel: OpenHantek voor realtime analyse

## Ondersteunde hardware

| Apparaat | Model | Protocol |
|----------|-------|----------|
| Oscilloscope | Hantek DSO-6022BL/BE | USB (libusb) |

## Preset voorbeeld

```yaml
name: basic_scope
title: "Basis scope setup"
description: "Standaard dual-channel configuratie"
scope:
  timebase: 1ms
  channels:
    1:
      vdiv: 1.0
      coupling: DC
    2:
      vdiv: 1.0
      coupling: DC
```

## Tests

```bash
pytest tests/ -v
```
