# Labcontrol V2 - Configuratie Orchestrator

## Visie

Labcontrol wordt een **CLI-first configuratie tool** voor lab equipment.
Geen live visualisatie - gebruik dedicated software (OpenHantek, etc.) daarvoor.

## Architectuur

```
labcontrol/
├── labcontrol/                 # Python package
│   ├── __init__.py
│   ├── cli.py                  # Click-based CLI
│   ├── config.py               # Settings, device discovery
│   ├── preset.py               # Preset loading/saving/validation
│   │
│   ├── devices/                # Device drivers (bestaand, opschonen)
│   │   ├── __init__.py
│   │   ├── base.py             # BaseDevice interface
│   │   ├── scope.py            # Hantek, etc.
│   │   ├── supply.py           # Korad, etc.
│   │   ├── generator.py        # MP751062, etc.
│   │   └── dmm.py              # Multimeters
│   │
│   ├── automation/             # Fase 2: geautomatiseerde metingen
│   │   ├── __init__.py
│   │   ├── sweep.py            # Frequency sweeps
│   │   ├── curve.py            # I-V curves, etc.
│   │   └── logger.py           # Data logging
│   │
│   └── gui/                    # Fase 3: optionele simpele GUI
│       └── ...
│
├── presets/                    # Preset library
│   ├── examples/
│   │   ├── rc_filter.yaml
│   │   └── led_test.yaml
│   └── user/                   # Gebruiker presets
│
└── pyproject.toml              # Modern Python packaging
```

## Fase 1: CLI + Presets (Primair)

### Preset Formaat (YAML)

```yaml
# presets/examples/rc_filter.yaml
name: "RC Laagdoorlaatfilter"
description: "Lab 3 - RC filter analyse bij verschillende frequenties"
author: "Tom"
version: 1

devices:
  scope:
    channels:
      1:
        enabled: true
        vdiv: 1.0          # Volt per divisie
        coupling: DC
        probe: 10          # 10x probe
      2:
        enabled: true
        vdiv: 1.0
        coupling: DC
        probe: 10
    timebase: 1ms          # Of: "1e-3" of "0.001"
    trigger:
      source: CH1
      level: 0
      slope: rising

  generator:
    channel: 1
    waveform: sine
    frequency: 1kHz        # Of: 1000
    amplitude: 2.0Vpp      # Of: 2.0
    offset: 0

  supply:
    voltage: 5.0
    current_limit: 0.1
    output: on             # Auto-enable output
```

### CLI Commands

```bash
# Apparaten
labcontrol devices                    # Lijst gevonden apparaten
labcontrol devices --scan             # Opnieuw scannen

# Presets
labcontrol list                       # Lijst beschikbare presets
labcontrol show <preset>              # Toon preset details
labcontrol load <preset>              # Laad preset naar apparaten
labcontrol save <name>                # Sla huidige config op als preset

# Individuele apparaten
labcontrol scope status               # Huidige scope settings
labcontrol scope set ch1.vdiv=0.5     # Individuele setting
labcontrol supply set voltage=3.3

# Helpers
labcontrol openhantek                 # Start OpenHantek
labcontrol edit <preset>              # Open preset in $EDITOR
```

### Voorbeeld Sessie

```bash
$ labcontrol devices
Gevonden apparaten:
  scope:     Hantek DSO-6022BL (USB)
  supply:    Korad KA3005P (/dev/ttyUSB0)
  generator: Niet gevonden

$ labcontrol load rc_filter
Laden: RC Laagdoorlaatfilter

Scope:
  ✓ CH1: 1V/div, DC, 10x probe
  ✓ CH2: 1V/div, DC, 10x probe
  ✓ Timebase: 1ms/div
  ✓ Trigger: CH1, 0V, rising

Generator:
  ⚠ Niet aangesloten - overslaan

Supply:
  ✓ 5.0V, 100mA limit
  ✓ Output ingeschakeld

Klaar! Open OpenHantek voor live view: labcontrol openhantek
```

## Fase 2: Geautomatiseerde Metingen

### Sweep Command

```bash
# Frequency response meting
labcontrol sweep freq \
  --start 100 \
  --stop 10k \
  --points 20 \
  --measure scope.ch2.vpp \
  --output bode.csv

# I-V curve
labcontrol sweep supply.voltage \
  --start 0 \
  --stop 5 \
  --step 0.1 \
  --measure dmm.current \
  --output iv_curve.csv
```

### Script Mode

```python
# scripts/bode_plot.py
from labcontrol import devices, measure

scope = devices.scope()
gen = devices.generator()

results = []
for freq in logspace(100, 10000, 20):
    gen.set_frequency(freq)
    time.sleep(0.1)

    vin = scope.ch1.measure_vpp()
    vout = scope.ch2.measure_vpp()

    results.append({
        'freq': freq,
        'gain_db': 20 * log10(vout / vin)
    })

export_csv(results, 'bode.csv')
plot_bode(results)
```

```bash
$ labcontrol run scripts/bode_plot.py
```

## Fase 3: Optionele GUI

Simpele GUI als wrapper om CLI:

```
┌─────────────────────────────────────────────┐
│  LABCONTROL                            [×]  │
├─────────────────────────────────────────────┤
│ Apparaten     Presets      Automation       │
├─────────────────────────────────────────────┤
│                                             │
│  [Scan Devices]                             │
│                                             │
│  ✓ Scope:     Hantek DSO-6022BL            │
│  ✓ Supply:    Korad KA3005P                │
│  ✗ Generator: Niet gevonden                │
│  ✗ DMM:       Niet gevonden                │
│                                             │
├─────────────────────────────────────────────┤
│                                             │
│  Preset: [RC Filter Lab 3      ▼]          │
│                                             │
│  ┌───────────────────────────────────────┐ │
│  │ scope:                                │ │
│  │   ch1: 1V/div, DC                     │ │
│  │   timebase: 1ms                       │ │
│  │ supply:                               │ │
│  │   voltage: 5.0V                       │ │
│  └───────────────────────────────────────┘ │
│                                             │
│  [Load Preset]  [Save Current]              │
│                                             │
│  [Open OpenHantek]                          │
│                                             │
└─────────────────────────────────────────────┘
```

## Implementatie Volgorde

### Fase 1A: Core CLI (eerst)
1. [ ] `pyproject.toml` + moderne packaging
2. [ ] `cli.py` met Click framework
3. [ ] `preset.py` - YAML laden/valideren
4. [ ] `devices` - opschonen bestaande drivers
5. [ ] Commands: `devices`, `list`, `load`, `show`

### Fase 1B: Device Drivers (opschonen)
1. [ ] Simpele `BaseDevice` interface
2. [ ] Hantek driver vereenvoudigen (alleen config, geen capture)
3. [ ] Korad supply driver
4. [ ] MP751062 generator driver
5. [ ] DMM driver (indien aanwezig)

### Fase 2: Automation
1. [ ] `sweep` command
2. [ ] `measure` functies per device
3. [ ] CSV export
4. [ ] Script runner

### Fase 3: GUI (optioneel)
1. [ ] Simpele PyQt/Tkinter wrapper
2. [ ] Preset selector
3. [ ] Device status
4. [ ] Launch external tools

## Wat te verwijderen

Huidige code die niet meer nodig is:
- `src/gui/widgets/ScopeWidget.py` (complexe scope view)
- `src/gui/MainWindow.py` (huidige complexe GUI)
- Alle live capture/waveform code
- Measurement worker threads

## Dependencies

```toml
[project]
dependencies = [
    "click",           # CLI framework
    "pyyaml",          # Preset files
    "pyusb",           # USB devices
    "pyserial",        # Serial devices
    "pyvisa",          # VISA instruments
    "rich",            # Pretty terminal output
]

[project.optional-dependencies]
automation = [
    "numpy",
    "pandas",
    "matplotlib",
]
gui = [
    "PyQt5",
]
```

## Migratie Strategie

1. Maak nieuwe `labcontrol/` package naast bestaande `src/`
2. Port device drivers één voor één
3. Test CLI grondig
4. Verwijder oude code pas als CLI werkt
5. GUI later als wrapper

## Vragen voor beslissing

1. Welke apparaten heb je nu fysiek beschikbaar voor testen?
2. Wil je presets in `~/.config/labcontrol/` of in project folder?
3. Heb je voorkeur voor preset formaat (YAML vs TOML vs JSON)?
