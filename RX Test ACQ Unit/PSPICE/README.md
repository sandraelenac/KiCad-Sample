# KiCad-Sample

> A collection of electronic circuit design examples, simulation projects, and hardware revisions developed using **Cadence OrCAD Capture** and **PSpice**

---

## Overview

This repository contains a variety of electronic circuit design projects ranging from simple schematic examples to complete analog circuit implementations and hardware revisions. The projects demonstrate circuit capture, SPICE simulation, component library management, and iterative hardware development.

---

# Repository Structure

```
KiCad-Sample/
│
├── DESIGN1/
├── DESIGN2/
├── LVDS/
├── TESTLV/
├── TIA_LMH669_1/
├── A26545-ND/
├── REX/
│
└── README.md
```

---

# Projects

## DESIGN1

Basic OrCAD Capture schematic project demonstrating introductory circuit capture techniques.

### Files

- `DESIGN1.DSN` — Main schematic
- `DESIGN1.OPJ` — OrCAD project

---

## DESIGN2

Second example project containing an additional schematic and simulation configuration.

### Files

- `DESIGN2.DSN`
- `DESIGN2.OPJ`

---

## LVDS

Low Voltage Differential Signaling (LVDS) reference design demonstrating differential communication and signal integrity.

### Files

- `LVDS.DSN`
- `LVDS.OPJ`

### Simulation Folder

```
LVDS-PSpiceFiles/
```

Contains generated simulation files including:

- Netlists
- Simulation profiles
- Probe files
- Output reports
- Property files

---

## TESTLV

Experimental project used during circuit validation and testing.

### Files

- `TESTLV.DSN`
- `TESTLV.OPJ`

---

## TIA_LMH669_1

High-speed Transimpedance Amplifier (TIA) design utilizing the Texas Instruments LMH669 amplifier family.

### Files

- `TIA_LMH669_1.DSN`
- `TIA_LMH669_1.OPJ`
- `TIA_LMH669_1.DBK`

### Simulation Folder

```
TIA_LMH669_1-PSpiceFiles/
```

Contains generated simulation data including:

- Netlists
- Output reports
- Probe files
- Simulation profiles

---

## A26545-ND

Imported component library.

Contains:

- Component symbols
- Library project
- XML metadata

---

## REX

Primary hardware development project.

Contains multiple hardware revisions including:

- Alpha Revision
- Beta Revision
- Intermediate development revisions
- Simulation data
- Design backups

Each revision generally contains:

- Schematic
- Project
- Backup
- Simulation outputs

---

# Common File Types

| Extension | Description |
|-----------|-------------|
| `.DSN` | OrCAD Capture schematic |
| `.OPJ` | OrCAD project |
| `.DBK` | Project backup |
| `.OLB` | Component library |
| `.XML` | Library metadata |
| `.NET` | Generated SPICE netlist |
| `.CIR` | SPICE circuit |
| `.OUT` | Simulation output |
| `.ALS` | Alias file |
| `.SIM` | Simulation profile |
| `.MRK` | Probe marker |
| `.PRP` | Project properties |

---

# Software Requirements

- Cadence OrCAD Capture
- Cadence PSpice
- Windows 10/11
- KiCad 9+
- ngspice

---

# Getting Started

Clone the repository

```bash
git clone https://github.com/sandraelenac/KiCad-Sample.git
```

Navigate into the project

```bash
cd KiCad-Sample
```

Open any project by launching its corresponding `.OPJ` file in OrCAD Capture.

---

# Repository Purpose

This repository serves as:

- Electronic circuit design examples
- PSpice simulation examples
- Analog circuit reference designs
- Differential signaling demonstrations
- Hardware revision tracking
- Educational learning material
- Future KiCad migration projects

---

# Author

**Sandra Castrejon**

Electrical & Computer Engineer