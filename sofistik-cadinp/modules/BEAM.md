# Module: BEAM — RC Beam Design

## Purpose

BEAM analyses and designs a continuous reinforced concrete beam in the Ultimate Limit State (ULS) and Serviceability Limit State (SLS). It performs bending design, shear design (including shear flange design for T-beams), crack control, and deflection checks according to Eurocode 2. The module works on design elements created by DECREATOR, collecting all information from the database and producing a compact printout of required reinforcement and SLS verifications.

**Supported design codes:** EN 1992-1-1:2004, DIN EN 1992-1-1:2011 (NA:2013), NF EN 1992-1-1:2005 (NA:2016), BS EN 1992-1-1:2004. If the selected code is not supported, EN 1992-1-1:2004 is used as fallback.

## Load this file when

The user needs to design RC beams (bending, shear, crack width, deflection) for continuous girders or single-span beams.

## Prerequisites

Before running BEAM, the following modules must have been executed:
1. **AQUA** — materials and cross-sections (SREC for rectangular/T-beam sections)
2. **SOFIMSHC** — structural model
3. **SOFILOAD** — load definition
4. **ASE** — structural analysis
5. **DECREATOR** — design element creation with `LC` for force transfer

> BEAM works exclusively with design elements from DECREATOR. The design sections, support face conditions (HFAC, CFAC, IFAC), and shear sections (SHEA) defined in DECREATOR control the moment smoothing, shear reduction, and design section placement in BEAM.

## Module block template

```
+PROG BEAM urs:<n>
HEAD <description>

!*!Label Output Control
ECHO FULL YES

!*!Label Control
CTRL SMOO YES
CTRL AXIA UNIA

!*!Label Design Element Selection
DSLN NO 1

!*!Label Position Annotation
POS TITL "Pos 1" PLAC "Level 1" TEXT "Beam b/h=300/600"
  LPOS X  0.0 TITL "A"
  LPOS X  7.0 TITL "B"
  LPOS X 14.0 TITL "C"

!*!Label Load Case Combinations
COMB LC 1001 TYPE (D)
COMB LC 1002 TYPE (D)
COMB LC 2001 TYPE (P)
COMB LC 2002 TYPE (F)

!*!Label Design Parameters
DESI TETA VAR TETB VAR

END
```

> **Key rules:**
> - BEAM requires design elements with transferred forces (DECREATOR must have run with `LC`).
> - Cross-sections must be rectangular (SREC) or T-beam shapes. BEAM does not consider torsional moments.
> - Load case combinations must be assigned to limit states: `(D)` for ULS, `(P)`/`(F)`/`(R)` for SLS.
> - BEAM internally uses AQB for bending and shear design calculations.

---

## Commands

| Command | Purpose |
|---------|---------|
| `ECHO`  | Control output verbosity per result category |
| `CTRL`  | Module-level control options |
| `DGRP`  | Define a design group of identical beams |
| `DSLN`  | Select a design element for design |
| `POS`   | Position annotation for printout header |
| `LPOS`  | Position labels along the beam axis (sub-record of POS) |
| `COMB`  | Define or reference load case combinations |
| `COPY`  | Copy load cases with factors into a combination (sub-record of COMB) |
| `DESI`  | Control shear design parameters (strut angle, shift rule) |
| `DELR`  | Ductile elastic moment redistribution |
| `LRF`   | Longitudinal reinforcement distribution for SLS |
| `SRF`   | Shear reinforcement distribution for SLS |
| `DEFL`  | Deflection calculation parameters (creep, shrinkage) |
| `CRCK`  | Crack control parameters |
| `BDEL`  | Remove design groups from the database |

---

### ECHO — Output Control

Controls the extent of printed output per result category.

**Syntax:**
```
ECHO OPT VAL
```

| Parameter | Type | Unit | Default | Description |
|-----------|------|------|---------|-------------|
| `OPT`    | enum | —    | —       | Output category |
| `VAL`    | enum | —    | —       | Output extent |

**OPT — output categories:**

| Value  | Description | Default |
|--------|-------------|---------|
| `FULL` | All decisive sections | `YES` |
| `MAT`  | Material information | `YES` |
| `NCS`  | Cross-section (YES=plot, FULL=plot+table, EXTR=plot+detailed table) | `YES` |
| `SYST` | System and plot | `YES` |
| `SUP`  | Support conditions table | `YES` |
| `ULS`  | Ultimate Limit State design | `YES` |
| `SLS`  | Serviceability Limit State design | `YES` |
| `FACT` | Factors for action design | `YES` |
| `FORC` | Characteristic forces (YES=plot, FULL=plot+table decisive, EXTR=all sections) | `YES` |
| `FORP` | Force plots for characteristic forces (design groups only) | `YES` |
| `COMB` | Design load case combinations (YES=decisive, FULL=all, EXTR=all+all sections) | `YES` |
| `RFC`  | Reinforcement results (YES/FULL=decisive sections, EXTR=all sections) | `YES` |
| `CRCK` | Crack control (YES/FULL=compact table, EXTR=stresses+minimum reinforcement) | `YES` |
| `DEFL` | Deflection control (YES/FULL=decisive sections+figure, EXTR=all sections) | `YES` |
| `SUM`  | Design summary table | `NO` |

**VAL — output extent:**

| Value  | Description |
|--------|-------------|
| `NO`   | No output |
| `YES`  | Standard printout (decisive design sections) |
| `FULL` | Full printout (all design sections) |
| `EXTR` | Extended printout with additional graphics and tables |

**Typical usage:**
```
ECHO FULL YES          $ standard compact printout
ECHO FULL FULL         $ full printout with all sections
ECHO CRCK EXTR         $ detailed crack control output
```

---

### CTRL — Control of Calculation

Sets global control options for the beam design.

**Syntax:**
```
CTRL OPT VAL
```

| Parameter | Type | Unit | Default | Description |
|-----------|------|------|---------|-------------|
| `OPT`    | enum | —    | —       | Control option keyword |
| `VAL`    | enum | —    | —       | Value for the option |

**OPT — control options:**

| OPT    | Description | Default | VAL values |
|--------|-------------|---------|------------|
| `SMOO` | Smoothing/reduction of support moments | `YES` | `YES` = reduce/smooth column moments per EC2 5.3.2.2; `NO` = no reduction |
| `SHRD` | Shear force reduction at supports | `YES` | `YES` = reduce shear force at support faces; `NO` = do not reduce |
| `AXIA` | Bending design mode | `UNIA` | `UNIA` = uniaxial design (only M_y, V_z); `BIAX` = biaxial design (includes M_z, V_y) |
| `NETT` | Cross-section area for design | `NO` | `YES` = design with net area (deduct ducts); `NO` = design with gross area |
| `PICT` | Force diagram style | `AREA` | `AREA` = filled colour diagrams; `LINE` = outline only |
| `DEFL` | Combination for deflection Zeta-interpolation | `(P)` | `(P)` = permanent; `(F)` = frequent; `(R)` = rare; `I` = plot elastic state I; `II` = plot nonlinear state II |
| `EPCS` | Consider creep and shrinkage in deflection | `YES` | `YES` = consider; `NO` = deactivate |
| `AMIN` | Minimum longitudinal reinforcement | `NO` | `YES` = use basic reinforcement from cross-section as minimum; `NO` = use zero as minimum |
| `LSWC` | Switch reinforcement layers automatically | `NO` | `YES` = switch layers 1 and 2 for negative M_y; `NO` = do not switch |
| `CURV` | Method of curvature calculation for deflection | `ANA` | `ANA` = analytical method; `NUM` = numerical method |

> `CTRL SMOO YES` applies moment smoothing at support faces based on the support type defined in DECREATOR (HFAC/CFAC/IFAC). Hinged supports get parabolic smoothing per EC2 5.3.2.2 (4); clamped supports get linear reduction per EC2 5.3.2.2 (3).
> `CTRL SHRD YES` reduces shear forces at design sections marked as TYPM SHEA in DECREATOR to the support axis value.
> `CTRL AXIA UNIA` ignores M_z and V_y — recommended for standard beam design. Use `BIAX` only when biaxial bending is significant.

**Typical usage:**
```
CTRL SMOO YES
CTRL AXIA UNIA
CTRL EPCS YES
CTRL AMIN NO
```

---

### DGRP — Define Design Group

Groups multiple beams with identical cross-sections and spans for envelope design. The envelope reinforcement across all elements in the group is saved as a separate design case.

**Syntax:**
```
DGRP NO TITL
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `NO`      | string | —    | —       | Identification of the design group (must start with a letter) |
| `TITL`    | string | —    | —       | Description of the design group |

> The group is stored as a secondary group in the database.
> Reinforcement per element and envelope reinforcement across all elements are saved in different design cases.
> All beams in a group must have identical cross-sections and span configurations.

**Typical usage:**
```
DGRP NO GRB1 TITL 'Floor beams level 1'
```

---

### DSLN — Select Design Element

Selects a design element (previously created by DECREATOR) for design in the current BEAM run.

**Syntax:**
```
DSLN NO TITL Z0 LEV
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `NO`      | int    | —     | —       | Number of the design element (must match a DECREATOR DSLN NO) |
| `TITL`    | string | —     | —       | Designation of the beam (overrides DECREATOR title in printout) |
| `Z0`      | float  | `[m]` | —       | Elevation of beam (for printout annotation) |
| `LEV`     | string | —     | —       | Level mark of beam (for printout annotation) |

**Typical usage:**
```
DSLN NO 1
DSLN NO 10 TITL 'Main girder axis A'
```

---

### POS — Position Annotation

Provides printout header information for the beam position. Purely for documentation in the output — no effect on calculations.

**Syntax:**
```
POS TITL PLAC TEXT KOTE
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `TITL`    | string | —     | —       | Position number / identifier |
| `PLAC`    | string | —     | —       | Place and axis description |
| `TEXT`    | string | —     | —       | Component description |
| `KOTE`    | float  | `[m]` | —       | Elevation of beam |

**Typical usage:**
```
POS TITL "Pos 1" PLAC "5.OG Axis A-C" TEXT "Continuous beam b/h=300/800"
```

---

### LPOS — Position Label Along Beam (sub-record of POS)

Labels specific positions along the beam axis for the system plot. Must follow a `POS` record. Only has effect on system plots when the position matches a support location.

**Syntax:**
```
LPOS X TITL
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `X`       | float  | `[m]` | —       | Coordinate along the beam axis |
| `TITL`    | string | —     | —       | Location / axis label |

**Typical usage:**
```
POS TITL "Pos 1" PLAC "Level 1"
  LPOS X  0.0 TITL "A"
  LPOS X  7.0 TITL "B"
  LPOS X 14.0 TITL "C"
```

---

### COMB — Load Case Combinations

Defines or references load case combinations for ULS and SLS design. Combinations can be manually built with subsequent `COPY` commands, referenced from the database (SOFILOAD/MAXIMA), or generated automatically.

**Syntax:**
```
COMB LC TYPE TITL FORC
```

| Parameter | Type    | Unit | Default | Description |
|-----------|---------|------|---------|-------------|
| `LC`      | int/enum| —    | —       | Load case number, or `ALL` for MAXIMA superpositions, or `AUTO` for automatic generation |
| `TYPE`    | enum    | —    | `(D)`   | Type of load combination (see table below) |
| `TITL`    | string  | —    | —       | Title of the load case combination |
| `FORC`    | string  | —    | `MYVZ`  | Forces to maximise when using LC AUTO (see below) |

**LC — special values:**

| Value  | Description |
|--------|-------------|
| `ALL`  | Use all superposition load cases from MAXIMA |
| `AUTO` | Automatic generation of combinations from action definitions |

**TYPE — combination type:**

| Value | Description |
|-------|-------------|
| `(D)` | ULS fundamental design — **default** |
| `(A)` | ULS accidental design |
| `(P)` | SLS quasi-permanent combination |
| `(R)` | SLS rare (characteristic) combination |
| `(F)` | SLS frequent combination |

**FORC — forces to maximise (for LC AUTO):**

Combine force identifiers: `N` (normal force), `MY` (bending moment y), `VZ` (shear force z), `MZ` (bending moment z), `VY` (shear force y), `MT` (torsional moment), `ALL` (all forces). Default: `MYVZ`. Optionally append `:n` for stress points to maximise (default 0).

> When using `COMB LC ALL`, BEAM reads superposition results from MAXIMA. Ductile elastic redistribution is automatically deactivated in this mode.
> When defining new combinations with `COPY`, the factors are applied linearly to the characteristic load cases.
> Database combinations are used as combination rules — load case numbers and factors are taken over and recalculated linearly.

**Typical usage:**
```
$ Reference existing combinations from database
COMB LC 1001 TYPE (D)
COMB LC 2001 TYPE (P)

$ Use all MAXIMA superpositions
COMB LC ALL TYPE (D)

$ Automatic combination generation
COMB LC AUTO FORC MYVZ

$ Build new combination with COPY
COMB LC 1001 TYPE (D) TITL "1.35G + 1.5Q"
  COPY NO 1 FACT 1.35
  COPY NO 2 FACT 1.5
```

---

### COPY — Load Case Copy with Factors (sub-record of COMB)

Copies existing load cases from the database with a combination factor. Must follow a `COMB` command. Maximum 256 COPY commands per COMB.

**Syntax:**
```
COPY NO FACT
```

| Parameter | Type  | Unit | Default | Description |
|-----------|-------|------|---------|-------------|
| `NO`      | int   | —    | —       | Load case number(s) to copy |
| `FACT`    | float | `[-]`| —       | Combination factor |

**Typical usage:**
```
COMB LC 1001 TYPE (D) TITL "1.35G(1) + 1.5Q(2+9)"
  COPY NO 1 FACT 1.35
  COPY NO 2,9 FACT 1.5
```

---

### DESI — Shear Design Parameters

Controls compression strut angle limits and shift rule for shear design.

**Syntax:**
```
DESI TETA TETB TYPE FDX DC DG SHFT
```

| Parameter | Type       | Unit    | Default | Description |
|-----------|------------|---------|---------|-------------|
| `TETA`    | float/enum | `[deg]` | `VAR`   | Lower limit of compression strut angle. `VAR` = from design code rules. |
| `TETB`    | float/enum | `[deg]` | `VAR`   | Upper limit of compression strut angle. `VAR` = from design code rules. |
| `TYPE`    | enum       | —       | `WEB`   | Part of cross-section: `WEB` = compression strut for the web |
| `FDX`     | int        | —       | 2       | Factor for subdividing shear flange design intervals (higher = more sections) |
| `DC`      | int        | —       | 1       | Design case number for required reinforcement per beam |
| `DG`      | int        | —       | 3       | Design case number for envelope reinforcement per group |
| `SHFT`    | enum       | —       | `NO`    | Shift rule: `NO` = deactivate; `YES` = activate (adds tensile force N_Vd = |V_Ed| * cot(theta)) |

> When shift rule is activated (`SHFT YES`), it is highly recommended to fix TETA and TETB to a specific value (e.g. `TETA 45 TETB 45`).
> `FDX` controls the subdivision of shear flange design intervals per EC2 6.2.4 (3). Increase for more detailed shear flange design.

**Typical usage:**
```
$ Use code-determined strut angles
DESI TETA VAR TETB VAR

$ Fixed strut angle with shift rule
DESI TETA 45 TETB 45 SHFT YES

$ Increased shear flange subdivision
DESI FDX 4
```

---

### DELR — Ductile Elastic Moment Redistribution

Controls the ductile elastic redistribution of bending moments per EN 1992-1-1, Ch. 5.5. Redistribution is only applied for uniaxial design. The rotational capacity is checked against code limits.

**Syntax:**
```
DELR DELT TYPE VAL
```

| Parameter | Type       | Unit  | Default | Description |
|-----------|------------|-------|---------|-------------|
| `DELT`    | float      | `[-]` | 1.0     | Ratio of redistributed moment to elastic bending moment (delta). Values < 1.0 reduce support moments. |
| `TYPE`    | enum       | —     | `ALL`   | Location for redistribution |
| `VAL`     | float      | `[m]` | —       | X-coordinate from start of beam (only for TYPE X) |

**TYPE — location:**

| Value | Description |
|-------|-------------|
| `ALL` | Apply redistribution at all valid support locations — **default** |
| `X`   | Apply redistribution at the specific coordinate given in VAL |

> Redistribution is automatically deactivated when MAXIMA superposition load cases are used (`COMB LC ALL`), because the associated individual load cases cannot be evaluated.
> Only valid support moments are redistributed; edge support moments are never redistributed.
> Span-to-depth ratio conditions per EC2 5.5 (4) are checked automatically.

**Typical usage:**
```
$ 15% redistribution at all supports
DELR DELT 0.85 TYPE ALL

$ 15% redistribution at specific location
DELR DELT 0.85 TYPE X 8.0

$ No redistribution (default)
DELR DELT 1.0
```

---

### LRF — Longitudinal Reinforcement Distribution

Defines the distribution of longitudinal reinforcement along the beam axis for SLS checks. Multiple calls for the same layer add additional reinforcement. Uses layers 1 (bottom) and 2 (top).

**Syntax:**
```
LRF LAY X1 X2 AS D MRF
```

| Parameter | Type  | Unit     | Default | Description |
|-----------|-------|----------|---------|-------------|
| `LAY`     | int   | —        | 0       | Layer number (0–9). Use 1 for bottom, 2 for top. |
| `X1`      | float | `[m]`    | —       | Start position along beam axis |
| `X2`      | float | `[m]`    | —       | End position along beam axis |
| `AS`      | float | `[cm2]`  | —       | Reinforcement area. Use `[-]` unit for bar count instead of area. |
| `D`       | float | `[mm]`   | —       | Diameter of reinforcement bar |
| `MRF`     | int   | —        | —       | Material number of reinforcement (from AQUA) |

> If no LRF is defined, BEAM applies a simplified reinforcement distribution using the maximum span and support reinforcement from ULS.
> Layer 1 = bottom (tension in sagging), Layer 2 = top (tension in hogging).
> For design groups, one reinforcement distribution is defined for the entire group.

**Typical usage:**
```
$ Bottom reinforcement: 2 x d20 over full length
LRF LAY 1 X1 0.0 X2 14.0 AS 2[-] D 20 MRF 2

$ Top reinforcement: 3 x d25 over support region
LRF LAY 2 X1 3.0 X2 11.0 AS 3[-] D 25 MRF 2
```

---

### SRF — Shear Reinforcement Distribution

Defines the distribution of shear reinforcement (stirrups) along the beam axis for SLS checks.

**Syntax:**
```
SRF LAY X1 X2 ASW SW D NRFB MRF
```

| Parameter | Type  | Unit       | Default | Description |
|-----------|-------|------------|---------|-------------|
| `LAY`     | int   | —          | 1       | Reinforcement layer. 1 = web shear reinforcement; 2 = flange shear reinforcement. |
| `X1`      | float | `[m]`      | 0.0     | Start position along beam axis |
| `X2`      | float | `[m]`      | 0.0     | End position along beam axis |
| `ASW`     | float | `[cm2/m]`  | —       | Shear reinforcement area per metre (alternative to SW) |
| `SW`      | float | `[m]`      | —       | Spacing of stirrups (alternative to ASW) |
| `D`       | float | `[mm]`     | 12      | Diameter of stirrup bar |
| `NRFB`    | int   | —          | 1       | Number of stirrup legs (cuts) |
| `MRF`     | int   | —          | —       | Material number of reinforcement (from AQUA) |

> Specify either `ASW` (area per metre) or `SW` (spacing) — not both.
> Layer 1 = web shear reinforcement; Layer 2 = flange connection reinforcement.

**Typical usage:**
```
$ Stirrups d8/200 with 2 legs over full length
SRF LAY 1 X1 0.0 X2 14.0 ASW 3.14[cm2/m] D 8 NRFB 2 MRF 2

$ Alternative: specify by spacing
SRF LAY 1 X1 0.0 X2 14.0 SW 0.20 D 8 NRFB 2 MRF 2
```

---

### DEFL — Deflection Calculation Parameters

Controls creep and shrinkage parameters for the deflection check per EN 1992-1-1, Ch. 7.4.3.

**Syntax:**
```
DEFL PHI EPCS T RH TEMP T0 TS BETA
```

| Parameter | Type  | Unit    | Default | Description |
|-----------|-------|---------|---------|-------------|
| `PHI`     | float | `[-]`   | 0.0     | Final creep coefficient. If 0.0, calculated automatically per EC2 Annex B.1. |
| `EPCS`    | float | `[permil]`| 0.20  | Free shrinkage strain. If 0.0, calculated automatically from remaining parameters. |
| `T`       | float | `[days]`| 3650    | Duration of loading period |
| `RH`      | float | `[%]`   | 80      | Relative air humidity |
| `TEMP`    | float | `[deg C]`| 20     | Temperature |
| `T0`      | float | `[days]`| 28      | Minimum age of concrete at time of loading |
| `TS`      | float | `[days]`| 7       | Age at start of drying |
| `BETA`    | float | `[-]`   | 0.5     | Duration factor: 0.5 = long-term loading; 1.0 = short-term loading |

> When `PHI` = 0.0, BEAM calculates the creep coefficient automatically using the formula: phi_0 = phi_RH * beta(f_cm) * beta(t_0).
> When `EPCS` = 0.0, BEAM calculates the shrinkage strain from the other parameters.
> The DIN NA (Heft 600 DAfStb) uses additional investigation with rare and frequent combinations for the Zeta-interpolation factor.
> Ensure DECREATOR HDIV provides at least 5–10 sections per span for accurate deflection integration.

**Typical usage:**
```
$ Automatic creep/shrinkage with default humidity
DEFL PHI 0.0 EPCS 0.0 RH 50 T0 28

$ Explicit creep coefficient
DEFL PHI 2.5 EPCS 0.25 BETA 0.5

$ Office building: 10 years, loading at 28 days
DEFL T 3650 T0 28 TS 7 RH 50
```

---

### CRCK — Crack Control Parameters

Sets parameters for crack width verification per EN 1992-1-1, Ch. 7.3.

**Syntax:**
```
CRCK WK FCTE
```

| Parameter | Type  | Unit      | Default | Description |
|-----------|-------|-----------|---------|-------------|
| `WK`      | float | `[mm]`    | 0.3     | Allowable crack width |
| `FCTE`    | float | `[N/mm2]` | 3.0     | Mean tensile strength of concrete (f_ct,eff) |

> BEAM performs three crack checks: (1) minimum reinforcement for crack control, (2) simplified check comparing limit diameter with selected diameters, (3) crack width calculation per EC2 7.3.4 with k_t = 0.4 (long-term loading).

**Typical usage:**
```
$ Standard crack width limit
CRCK WK 0.3

$ Reduced crack width for aggressive environment
CRCK WK 0.2
```

---

### BDEL — Remove Design Groups

Removes all design groups created by BEAM from the database.

**Syntax:**
```
BDEL OPT
```

| Parameter | Type | Unit | Default | Description |
|-----------|------|------|---------|-------------|
| `OPT`     | enum | —    | —       | `DGRP` = remove all design groups |

**Typical usage:**
```
BDEL DGRP
```

---

## Complete BEAM Block Examples

### Example 1 — Simple two-span beam with explicit combinations

```
+PROG BEAM urs:6
HEAD RC beam design — two-span continuous beam

!*!Label Output Control
ECHO FULL YES

!*!Label Control
CTRL SMOO YES
CTRL AXIA UNIA

!*!Label Design Element
DSLN NO 1

!*!Label Position
POS TITL "Pos 1" PLAC "Level 1, Axis A-C" TEXT "Beam b/h=300/600"
  LPOS X  0.0 TITL "A"
  LPOS X  7.0 TITL "B"
  LPOS X 14.0 TITL "C"

!*!Label ULS Combinations
COMB LC 1001 TYPE (D) TITL "1.35G + 1.5Q(span1)"
  COPY NO 1 FACT 1.35
  COPY NO 2 FACT 1.5

COMB LC 1002 TYPE (D) TITL "1.35G + 1.5Q(span2)"
  COPY NO 1 FACT 1.35
  COPY NO 3 FACT 1.5

COMB LC 1003 TYPE (D) TITL "1.35G + 1.5Q(both)"
  COPY NO 1 FACT 1.35
  COPY NO 2 FACT 1.5
  COPY NO 3 FACT 1.5

!*!Label SLS Combinations
COMB LC 2001 TYPE (P) TITL "G + 0.3Q(both)"
  COPY NO 1 FACT 1.0
  COPY NO 2 FACT 0.3
  COPY NO 3 FACT 0.3

!*!Label Design Parameters
DESI TETA VAR TETB VAR

!*!Label Deflection
DEFL PHI 0.0 EPCS 0.0 RH 50 T0 28

!*!Label Crack Width
CRCK WK 0.3

END
```

### Example 2 — Beam with MAXIMA superposition

```
+PROG BEAM urs:7
HEAD RC beam design using MAXIMA results

ECHO FULL YES
CTRL SMOO YES
CTRL AXIA UNIA

DSLN NO 10

!*!Label Use all MAXIMA combinations
COMB LC ALL TYPE (D)

END
```

### Example 3 — Beam with moment redistribution and reinforcement layout

```
+PROG BEAM urs:6
HEAD RC beam design with redistribution

ECHO FULL FULL
CTRL SMOO YES
CTRL AXIA UNIA

DSLN NO 99

POS TITL "Pos 1" PLAC "5.OG" KOTE +20.0
  LPOS X  0.0 TITL "A1"
  LPOS X  7.0 TITL "B1"
  LPOS X 14.0 TITL "C1"

!*!Label ULS Combinations
COMB LC 1001 TYPE (D) TITL "1.35G(1)"
COMB LC 1002 TYPE (D) TITL "1.35G(1)+1.5Q(2)"
COMB LC 1003 TYPE (D) TITL "1.35G(1)+1.5Q(3)"
COMB LC 1004 TYPE (D) TITL "1.35G(1)+1.5Q(2+3)"

!*!Label SLS Combinations
COMB LC 1005 TYPE (P) TITL "1.0G(1)+0.3Q(2)"
COMB LC 1006 TYPE (P) TITL "1.0G(1)+0.3Q(3)"
COMB LC 1007 TYPE (P) TITL "1.0G(1)+0.3Q(2+3)"

!*!Label Moment Redistribution (15%)
DELR DELT 0.85 TYPE ALL

!*!Label Longitudinal Reinforcement
LRF LAY 1 X1 0.0 X2 14.0 AS 2[-] D 20 MRF 2       $ bottom, full length
LRF LAY 1 X1 3.5 X2 10.5 AS 2[-] D 20 MRF 2       $ bottom, mid-span
LRF LAY 2 X1 3.0 X2 11.0 AS 3[-] D 25 MRF 2       $ top, over support
LRF LAY 2 X1 0.0 X2 14.0 AS 2[-] D 12 MRF 2       $ top, minimum

!*!Label Shear Reinforcement
SRF LAY 1 X1 0.0 X2  7.0 ASW 3.14[cm2/m] D 8 NRFB 2 MRF 2
SRF LAY 1 X1 7.0 X2 14.0 ASW 3.14[cm2/m] D 8 NRFB 2 MRF 2

END
```

---

## Worked Example — Two-Span Continuous RC Beam

The following BEAM block completes the design for the two-span continuous beam (see DECREATOR worked example). The beam (2 x 6 m, C30/37, B500B, 300 x 600 mm) is designed for ULS bending and shear, and checked for SLS deflection and crack width. Three ULS combinations cover the load patterns (both spans, left only, right only). Three SLS quasi-permanent combinations are used for deflection and cracking. A longitudinal reinforcement layout is provided for the SLS verification.

```
+PROG BEAM urs:6
HEAD Beam Design

ECHO SUM YES                                 $ show design summary table

!*!Label Control
CTRL SMOO YES                                $ smooth support moments per EC2 5.3.2.2
CTRL AXIA UNIA                               $ uniaxial design (M_y and V_z only)
CTRL AMIN NO                                 $ do not use basic reinforcement as minimum
CTRL DEFL I,II                               $ plot deflection curves for state I and II

!*!Label Design Element
DSLN NO 1 TITL "Continous Beam"

!*!Label ULS Combinations
COMB 1001 TYPE (D) TITL "1.35G(1)+1.5Q(2)+1.5Q(3)"
  COPY NO 1 FACT 1.350
  COPY NO 2 FACT 1.500
  COPY NO 3 FACT 1.500
COMB 1002 TYPE (D) TITL "1.35G(1)+1.5Q(2)"
  COPY NO 1 FACT 1.350
  COPY NO 2 FACT 1.500
COMB 1003 TYPE (D) TITL "1.35G(1)+1.5Q(3)"
  COPY NO 1 FACT 1.350
  COPY NO 3 FACT 1.500

!*!Label SLS Combinations (quasi-permanent)
COMB 2001 TYPE (P) TITL "1G(1)+0.3Q(2)+0.3Q(3)"
  COPY NO 1 FACT 1.000
  COPY NO 2 FACT 0.300
  COPY NO 3 FACT 0.300
COMB 2002 TYPE (P) TITL "1G(1)+0.3Q(2)"
  COPY NO 1 FACT 1.000
  COPY NO 2 FACT 0.300
COMB 2003 TYPE (P) TITL "1G(1)+0.3Q(3)"
  COPY NO 1 FACT 1.000
  COPY NO 3 FACT 0.300

!*!Label Longitudinal Reinforcement for SLS
LRF LAY 1 X1 0[m] X2 12[m] AS 8.04[cm2] D 16 MRF 2       $ bottom base reinforcement
LRF LAY 2 X1 0[m] X2 12[m] AS 4.02[cm2] D 16 MRF 2       $ top base reinforcement
LRF LAY 1 X1 1.2[m] X2 4.2[m] AS 4.02[cm2] D 16 MRF 2    $ bottom additional — span 1
LRF LAY 1 X1 7.8[m] X2 10.8[m] AS 4.02[cm2] D 16 MRF 2   $ bottom additional — span 2
LRF LAY 2 X1 4.2[m] X2 7.8[m] AS 12.57[cm2] D 20 MRF 2   $ top additional — over support B

END
```

---

## Unit Summary for BEAM

| Quantity | Unit | Parameters |
|----------|------|------------|
| Positions along beam | `[m]` | `X` on `LPOS`; `X1`/`X2` on `LRF`/`SRF`; `VAL` on `DELR` |
| Elevation | `[m]` | `KOTE` on `POS`; `Z0` on `DSLN` |
| Reinforcement area | `[cm2]` | `AS` on `LRF` |
| Bar count | `[-]` | `AS` on `LRF` with unit `[-]` |
| Shear reinforcement | `[cm2/m]` | `ASW` on `SRF` |
| Stirrup spacing | `[m]` | `SW` on `SRF` |
| Bar diameter | `[mm]` | `D` on `LRF`/`SRF` |
| Strut angle | `[deg]` | `TETA`/`TETB` on `DESI` |
| Crack width | `[mm]` | `WK` on `CRCK` |
| Tensile strength | `[N/mm2]` | `FCTE` on `CRCK` |
| Shrinkage strain | `[permil]` | `EPCS` on `DEFL` |
| Time | `[days]` | `T`/`T0`/`TS` on `DEFL` |
| Humidity | `[%]` | `RH` on `DEFL` |
| Redistribution ratio | `[-]` | `DELT` on `DELR` |
| Combination factor | `[-]` | `FACT` on `COPY` |
