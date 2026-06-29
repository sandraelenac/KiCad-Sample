# TAU Hardware Design (KiCad)

> KiCad hardware design repository containing multiple revisions of the **TAU PCB**, including schematics, PCB layouts, fabrication files, and project backups.

---

## Overview

This repository contains the KiCad design files for the **TAU PCB** hardware project. It includes multiple hardware revisions documenting the evolution of the board throughout the design cycle.

Each revision contains:

- Complete schematic
- PCB layout
- Manufacturing Gerbers
- Drill files
- Pick-and-place files
- Automatic KiCad backups

---

## Repository Structure

```text
KICAD/
│
├── TAU REV F/
│   ├── TAU REV F.kicad_pro
│   ├── TAU REV F.kicad_sch
│   ├── TAU REV F.kicad_pcb
│   ├── Gebers→Fab/
│   └── TAU REV F-backups/
│
├── TAU_REVG/
│   ├── TAU_REVG.kicad_pro
│   ├── TAU_REVG.kicad_sch
│   ├── TAU_REVG.kicad_pcb
│   ├── GerberFab_TAU_RevG/
│   └── TAU_REVG-backups/
│
└── README.md
```

---

## Project Revisions

### TAU REV F

Revision F represents a previous hardware revision of the TAU PCB.

| File | Description |
|------|-------------|
| `TAU REV F.kicad_pro` | KiCad project configuration |
| `TAU REV F.kicad_sch` | Electrical schematic |
| `TAU REV F.kicad_pcb` | PCB layout |
| `TAU REV F.kicad_prl` | Local project settings |

Manufacturing outputs are located in:

```text
Gebers→Fab/
```

---

### TAU REV G

Revision G is the latest hardware revision of the TAU PCB.

| File | Description |
|------|-------------|
| `TAU_REVG.kicad_pro` | KiCad project configuration |
| `TAU_REVG.kicad_sch` | Electrical schematic |
| `TAU_REVG.kicad_pcb` | PCB layout |
| `TAU_REVG.kicad_prl` | Local project settings |

Manufacturing outputs are located in:

```text
GerberFab_TAU_RevG/
```

---

## Manufacturing Outputs

The manufacturing folders include files typically required for PCB fabrication and assembly:

- Gerber files
- NC drill files
- Pick-and-place files
- Gerber job files
- Fabrication reports

---

## KiCad File Types

| Extension | Description |
|----------|-------------|
| `.kicad_pro` | KiCad project configuration |
| `.kicad_sch` | Schematic file |
| `.kicad_pcb` | PCB layout file |
| `.kicad_prl` | Local project settings |
| `.gbr` | Gerber manufacturing layer |
| `.gbrjob` | Gerber job file |
| `.drl` | Drill file |
| `.pos` | Pick-and-place file |
| `.zip` | KiCad backup archive |

---

## Opening the Project

Open the latest revision in KiCad:

```text
TAU_REVG/TAU_REVG.kicad_pro
```

Or open the previous revision:

```text
TAU REV F/TAU REV F.kicad_pro
```

---

## Software Requirements

- KiCad 6 or newer
- KiCad 7 or newer recommended
- Windows, macOS, or Linux

---

## Version History

| Revision | Status |
|----------|--------|
| Rev F | Previous hardware revision |
| Rev G | Current hardware revision |

---
## Future Improvements

Planned additions include:

- PCB screenshots
- 3D renderings
- Design change log
- Release notes for each hardware revision

---

## Author

**Sandra Castrejon**
