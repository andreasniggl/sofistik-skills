# Module: COLUMN — RC Column Design (Nominal Curvature Method)

## Purpose

COLUMN designs reinforced concrete columns in the Ultimate Limit State using the Nominal Curvature Method (NCM) per EN 1992-1-1, Ch. 5.8.8. The method calculates second-order effects through an approximate bending moment based on linearisation of the interaction diagram. COLUMN determines the required reinforcement considering imperfections, slenderness, creep, and biaxial bending per EN 1992-1-1, Ch. 5.8.9.

**Supported design codes:** EN 1992-1-1:2004 and national annexes (DIN, OEN, UNI, NF, BS). If the specified code is not supported, EN 1992-1-1:2004 is used as fallback.

> This skill file covers only the **Nominal Curvature Method** (`CTRL NCM`). The general method (`CTRL TH2`) with full second-order theory is not documented here.

## Load this file when

The user needs to design RC columns for axial load with uniaxial or biaxial bending, using the simplified nominal curvature method.

## Prerequisites

Before running COLUMN, the following modules must have been executed:
1. **AQUA** — materials and cross-sections (SREC with symmetric reinforcement, e.g. RTYP CU)
2. **SOFIMSHC** — structural model (columns as vertical SLN elements)
3. **SOFILOAD** — load definition
4. **ASE** — structural analysis
5. **DECREATOR** — design element creation with `LC` for force transfer (when using DSLN)

> COLUMN can work with structural lines directly (`SLN`) or with design elements from DECREATOR (`DSLN`). Using `DSLN` allows integrating forces from quad-element models (e.g. wall-like columns).
> Cross-sections should have symmetric reinforcement distribution (RTYP CU or CORN). COLUMN checks both y- and z-axis buckling and decides uniaxial or biaxial design per EC2 5.8.9 Eq. 5.38.

## Module block template

```
+PROG COLUMN urs:<n>
HEAD <description>

!*!Label Control
CTRL NCM                            $ nominal curvature method
CTRL DCNO 1                         $ design case number

!*!Label Position Annotation
POS TITL "S1" PLAC "A/1" TEXT "Column 300x300"

!*!Label Design Group
DGRP NO GRP1 TITL "Ground floor columns"

!*!Label Column Selection
SLN 101 AXIS "A/1" LEV "GF" TITL "Column C1"
SLN 102 AXIS "A/2" LEV "GF" TITL "Column C2"

!*!Label Geometry and Buckling
GEOM BETY 1.0 BETZ 1.0 CY 10 CZ 10

!*!Label Imperfections
IMP AMXY 1 AMXZ 1

!*!Label Creep
CREP PHI 2.5

!*!Label Load Combinations
COMB LC AUTO FORC ALL

END
```

> **Key rules:**
> - `CTRL NCM` activates the Nominal Curvature Method. Without it, the general method (TH2) is used.
> - The NCM is restricted to single-storey columns (pin-ended or cantilever). It cannot design columns spanning multiple storeys.
> - Cross-sections should be rectangular, circular, or elliptical with symmetric reinforcement.
> - Multiple columns can be grouped with `DGRP` — all columns in a group must have identical cross-sections. **Only one `DGRP` per `+PROG COLUMN` block.** Use separate blocks for multiple groups, then a final block with `ECHO DGRP FULL` for the summary.
> - COLUMN reads characteristic forces from the database (from ASE via SLN, or from DECREATOR via DSLN).

---

## Commands

| Command | Purpose |
|---------|---------|
| `ECHO`  | Control output verbosity per result category |
| `CTRL`  | Module-level control (method selection, design options) |
| `POS`   | Position annotation for printout header |
| `DGRP`  | Define a design group of similar columns |
| `SLN`   | Select a structural line (column) for design |
| `DSLN`  | Select a design element (column) for design — NCM only |
| `GEOM`  | Column geometry: length, effective length coefficients, curvature |
| `IMP`   | Imperfection parameters |
| `BUCK`  | Buckling boundary conditions |
| `CREP`  | Creep coefficient |
| `COMB`  | Define or reference load case combinations |
| `COPY`  | Copy load cases with factors into a combination (sub-record of COMB) |
| `CDEL`  | Remove design groups from the database |

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
| `FULL` | All output categories | — |
| `MAT`  | Materials | `YES` |
| `SECT` | Cross-section elements | `YES` |
| `SYST` | System (YES=decisive column, FULL=every column) | `YES` |
| `ACT`  | Actions | `YES` |
| `LOAD` | Loading (YES=table+decisive graphic, FULL=all graphics, EXTR=table+all) | `EXTR` |
| `COMB` | Combinations (YES=decisive, FULL=all, EXTR=extended+reactions) | `FULL` |
| `REAC` | Support reactions (YES=characteristic, FULL=combinations, EXTR=both) | `YES` |
| `FORC` | Internal forces (YES=decisive, FULL=all combinations) | `YES` |
| `DEFO` | Deformations (YES=decisive, FULL=all combinations) | `YES` |
| `REIN` | Reinforcement / NCM results (YES=required, FULL=decisive combo, EXTR=all combos) | `YES` |
| `PICT` | Reinforcement sketch (YES=predefined, FULL=optimised/recommended) | `FULL` |
| `TERM` | Thermal properties for fire design | `YES` |
| `DGRP` | Summary of design groups — NCM only (YES=decisive column, FULL=all columns) | `YES` |
| `INTE` | Interaction diagram — NCM only | `NO` |

**VAL — output extent:**

| Value  | Description |
|--------|-------------|
| `NO`   | No output |
| `YES`  | Output of decisive combination |
| `FULL` | Output of all combinations |
| `EXTR` | Extended output |

> `ECHO DGRP` is used in a dedicated `+PROG COLUMN` block to print a summary table across **all** design groups that were analysed in previous COLUMN blocks. It does not perform any design itself.
> `ECHO DEFO` and `ECHO REAC` are not valid for the nominal curvature method.

**Typical usage:**
```
ECHO FULL YES
ECHO REIN FULL
ECHO PICT FULL
```

---

### CTRL — Control of Calculation

Sets the design method and global control options.

**Syntax:**
```
CTRL OPT VAL
```

| Parameter | Type    | Unit | Default | Description |
|-----------|---------|------|---------|-------------|
| `OPT`    | enum    | —    | —       | Control option keyword |
| `VAL`    | varies  | —    | —       | Value for the option |

**OPT — control options relevant to NCM:**

| OPT    | Description | Default | VAL values |
|--------|-------------|---------|------------|
| `NCM`  | Activate Nominal Curvature Method per EC2 5.8.8 | — | (no value needed) |
| `DCNO` | Design case number for required reinforcement per column | `1` | integer |
| `DGNO` | Design case number for maximum reinforcement per group | `3` | integer |
| `NETT` | Design with net cross-section (deduct ducts) | — | (no value needed — activates net section) |
| `WALL` | Design as wall element | — | (no value needed) |
| `EMIN` | Minimum eccentricity per EC2 6.1 (4) | — | `1` = activate; `0` = deactivate |
| `CANT` | Define cantilever column | — | `XY` = cantilever in XY-plane; `XZ` = cantilever in XZ-plane |
| `DESI` | Print summary of design results | — | (no value needed) |

> `CTRL NCM` is mandatory for the nominal curvature method. Without it, the general method (TH2) with full second-order analysis is used.
> `CTRL DCNO` and `CTRL DGNO` control where reinforcement results are stored in the database. Use these consistently when running multiple design groups.
> `CTRL WALL` should be combined with uniaxial design about the weak axis.
> `CTRL EMIN 1` activates the minimum eccentricity check per EC2 6.1 (4) — only valid for NCM.

**Typical usage:**
```
$ Standard NCM design
CTRL NCM
CTRL DCNO 1

$ Wall-like column
CTRL NCM
CTRL WALL

$ Cantilever column in XZ-plane
CTRL NCM
CTRL CANT XZ
```

---

### POS — Position Annotation

Provides printout header information. Purely for documentation — no effect on calculations.

**Syntax:**
```
POS TITL PLAC TEXT
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `TITL`    | string | —    | —       | Position name / identifier |
| `PLAC`    | string | —    | —       | Place of the position (e.g. axis reference) |
| `TEXT`    | string | —    | —       | Description text |

**Typical usage:**
```
POS TITL "S1" PLAC "A/1" TEXT "Column 300x300 mm"
```

---

### DGRP — Design Group

Groups multiple columns with identical cross-sections for envelope design. The envelope reinforcement across all columns in the group is saved as a separate design case.

**Syntax:**
```
DGRP NO TITL
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `NO`      | string | —    | —       | Group identification (must start with a letter, 1–4 characters) |
| `TITL`    | string | —    | —       | Description of the design group |

> The group is stored as a secondary group in the database.
> Only columns with identical cross-sections and materials may be grouped.
> `SLN` or `DSLN` records following a `DGRP` record belong to that group.
> **Only one design group can be analysed per `+PROG COLUMN` block.** To design multiple groups, use separate COLUMN blocks — one per group.
> After all groups have been designed, use a final dedicated COLUMN block with `ECHO DGRP FULL` to print a summary table across all previously analysed groups.

**Typical usage:**
```
DGRP NO GRP1 TITL "Ground floor columns 300x300"
  SLN 101 AXIS "A/1" LEV "GF"
  SLN 102 AXIS "A/2" LEV "GF"
  SLN 103 AXIS "B/1" LEV "GF"
```

---

### SLN — Structural Line Selection

Selects a structural line (column element) for design. The column length, cross-section, and characteristic forces are read from the database.

**Syntax:**
```
SLN NO Z0 AXIS LEV TITL
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `NO`      | int    | —     | —       | Structural line number (must reference an existing SLN from SOFIMSHC) |
| `Z0`      | float  | `[m]` | —       | Bottom elevation of the column (optional — overrides the value from the structural line) |
| `AXIS`    | string | —     | —       | Axis label in the floor plan (for printout) |
| `LEV`     | string | —     | —       | Level / storey label (for printout) |
| `TITL`    | string | —     | —       | Title of the column (for printout) |

> `SLN` works for both the NCM and the general method.
> Multiple `SLN` records can follow one `DGRP` to group columns.

**Typical usage:**
```
SLN 101 AXIS "A/1" LEV "1.OG" TITL "Column 300x300"
SLN 102 AXIS "A/2" LEV "1.OG" TITL "Column 300x300"
```

---

### DSLN — Design Element Selection (NCM only)

Selects a design element (from DECREATOR) for column design. This is the alternative to `SLN` and allows integrating forces from quad-element models (e.g. wall-like columns).

**Syntax:**
```
DSLN NO Z0 AXIS LEV TITL
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `NO`      | int    | —     | —       | Design element number (must match a DECREATOR DSLN NO) |
| `Z0`      | float  | `[m]` | —       | Bottom elevation of the column (optional — overrides DECREATOR value) |
| `AXIS`    | string | —     | —       | Axis label in the floor plan |
| `LEV`     | string | —     | —       | Level / storey label |
| `TITL`    | string | —     | —       | Title of the column |

> `DSLN` can only be used with the Nominal Curvature Method (`CTRL NCM`).
> Requires DECREATOR to have been run with force transfer (`LC`) prior to COLUMN.

**Typical usage:**
```
DGRP NO S101 TITL "Cantilever columns"
  DSLN 1001 AXIS "A/1" LEV "1.OG" TITL "Column 300x300"
  DSLN 1002 AXIS "A/2" LEV "1.OG" TITL "Column 300x300"
```

---

### GEOM — Column Geometry for NCM

Defines the column length, effective length coefficients, and curvature distribution coefficients for the nominal curvature method.

**Syntax:**
```
GEOM L BETY BETZ CY CZ
```

| Parameter | Type  | Unit  | Default | Description |
|-----------|-------|-------|---------|-------------|
| `L`       | float | `[m]` | —       | Column length (optional). If omitted, each column uses its individual geometric length from the model. |
| `BETY`    | float | `[-]` | 1.0     | Effective length coefficient for buckling about local y-axis (beta_y). Effective length = BETY * L. |
| `BETZ`    | float | `[-]` | 1.0     | Effective length coefficient for buckling about local z-axis (beta_z). Effective length = BETZ * L. |
| `CY`      | float | `[-]` | 10      | Curvature distribution coefficient in local y-direction for the calculation of additional deflection e_2 per EC2 5.8.8.2 (4) |
| `CZ`      | float | `[-]` | 10      | Curvature distribution coefficient in local z-direction |

> `L` overrides the geometric length for all selected columns. If columns have different lengths and `L` is not given, each column is designed with its own length.
> Typical effective length coefficients: 1.0 for pin-ended, 0.7 for fixed-free, 0.5 for fixed-fixed, 2.0 for cantilever.
> `CY`/`CZ` = 10 is the standard value per EC2 5.8.8.2 (4) for a sinusoidal curvature distribution (pi^2 ≈ 10).

**Typical usage:**
```
$ Pin-ended column, default curvature
GEOM BETY 1.0 BETZ 1.0

$ Cantilever column (effective length = 2 * L)
GEOM BETY 2.0 BETZ 2.0

$ Explicit column length override
GEOM L 3.50 BETY 0.7 BETZ 0.7
```

---

### IMP — Imperfection

Defines geometric imperfections for the column design. If not given, imperfections are calculated automatically per EC2 5.2 Eq. 5.1 and 5.2.

**Syntax:**
```
IMP EIXY EIXZ AMXY AMXZ
```

| Parameter | Type  | Unit  | Default | Description |
|-----------|-------|-------|---------|-------------|
| `EIXY`    | float | `[m]` | —       | Explicit imperfection e_i in local y-direction. If omitted, calculated as theta_i * L_0 / 2 per EC2 5.2. |
| `EIXZ`    | float | `[m]` | —       | Explicit imperfection e_i in local z-direction |
| `AMXY`    | int   | —     | 1       | Number of vertical members contributing to building stiffness in y-direction (factor alpha_m per EC2 5.2 (5)) |
| `AMXZ`    | int   | —     | 1       | Number of vertical members contributing to building stiffness in z-direction |

> When no `IMP` is given, COLUMN calculates: theta_i = theta_0 * alpha_h * alpha_m, where theta_0 = 1/200, alpha_h = 2/sqrt(L) <= 1.0, alpha_m = sqrt(0.5*(1+1/m)).
> For single-storey pin-ended columns, use `AMXY 1 AMXZ 1` (alpha_m = 1.0).
> If columns with different lengths are designed together, imperfections are calculated individually unless `GEOM L` sets a common length.

**Typical usage:**
```
$ Automatic imperfection (single column)
IMP AMXY 1 AMXZ 1

$ Building with 4 contributing columns
IMP AMXY 4 AMXZ 4

$ Explicit imperfection
IMP EIXY 0.015 EIXZ 0.015
```

---

### BUCK — Buckling Boundaries

Defines buckling bracing conditions. By default, buckling is checked in both directions.

**Syntax:**
```
BUCK FIX
```

| Parameter | Type | Unit | Default | Description |
|-----------|------|------|---------|-------------|
| `FIX`     | enum | —    | —       | Plane in which the column is braced against buckling |

**FIX — bracing plane:**

| Value | Description |
|-------|-------------|
| `XY`  | Braced in the local XY-plane (no buckling check in this plane) |
| `XZ`  | Braced in the local XZ-plane (no buckling check in this plane) |

> If `BUCK` is not used, design is applied in both directions (default).
> Use `BUCK XY` when the column is braced in the XY-plane, so only XZ-buckling is checked.

**Typical usage:**
```
$ Only check buckling in XZ-plane (braced in XY)
BUCK XY
```

---

### CREP — Creep Coefficient

Defines the final creep coefficient for the nominal curvature method.

**Syntax:**
```
CREP PHI
```

| Parameter | Type  | Unit  | Default | Description |
|-----------|-------|-------|---------|-------------|
| `PHI`     | float | `[-]` | —       | Final creep coefficient phi(infinity, t_0) per EC2 3.1.4 |

> For the NCM, the effective creep coefficient per EC2 5.8.4 is calculated internally for each load combination from the ratio M_0Eqp / M_0Ed.
> A typical value is PHI = 2.5 for standard conditions.

**Typical usage:**
```
CREP PHI 2.5
```

---

### COMB — Load Case Combinations

Defines or references load case combinations for ULS design. Works identically to the BEAM module COMB command.

**Syntax:**
```
COMB LC TYPE TITL FORC
```

| Parameter | Type    | Unit | Default | Description |
|-----------|---------|------|---------|-------------|
| `LC`      | int/enum| —    | —       | Load case number, or `AUTO` for automatic generation |
| `TYPE`    | enum    | —    | `(D)`   | Combination type |
| `TITL`    | string  | —    | —       | Title of the combination |
| `FORC`    | string  | —    | `ALL`   | Forces to maximise when using LC AUTO. Default for COLUMN is ALL (all forces + 5 stress points). |

**TYPE — combination type:**

| Value | Description |
|-------|-------------|
| `(D)` | ULS fundamental design — **default** |
| `(A)` | ULS accidental design |
| `(E)` | Earthquake design |
| `(AB)` | Fire action |

> COLUMN defaults to `FORC ALL` (all force components), unlike BEAM which defaults to `FORC MYVZ`.
> `COMB LC AUTO` generates all possible ULS combinations from the action definitions.

**Typical usage:**
```
$ Automatic combinations
COMB LC AUTO FORC ALL

$ Reference existing combinations
COMB LC 1001 TYPE (D)
COMB LC 1002 TYPE (D)

$ New combination with COPY
COMB LC 1001 TYPE (D) TITL "1.35G + 1.5Q"
  COPY NO 1 FACT 1.35
  COPY NO 2 FACT 1.5
```

---

### COPY — Load Case Copy with Factors (sub-record of COMB)

Copies existing load cases with combination factors. Must follow a `COMB` command. Maximum 256 per COMB.

**Syntax:**
```
COPY NO FACT
```

| Parameter | Type  | Unit | Default | Description |
|-----------|-------|------|---------|-------------|
| `NO`      | int   | —    | —       | Load case number(s) |
| `FACT`    | float | `[-]`| —       | Combination factor |

**Typical usage:**
```
COMB LC 1001 TYPE (D) TITL "1.35G(1) + 1.5Q(2)"
  COPY NO 1 FACT 1.35
  COPY NO 2 FACT 1.5
```

---

### CDEL — Remove Design Groups

Removes all design groups created by COLUMN from the database.

**Syntax:**
```
CDEL OPT
```

| Parameter | Type | Unit | Default | Description |
|-----------|------|------|---------|-------------|
| `OPT`     | enum | —    | —       | `DGRP` = remove all design groups |

**Typical usage:**
```
CDEL DGRP
```

---

## Complete COLUMN Block Examples

### Example 1 — Single column with automatic combinations (NCM)

```
+PROG COLUMN urs:6
HEAD Column design — NCM single column

!*!Label Control
CTRL NCM
CTRL DCNO 1

!*!Label Position
POS TITL "S1" PLAC "A/1" TEXT "Column 400x400 mm"

!*!Label Column
SLN 101

!*!Label Geometry
GEOM BETY 1.0 BETZ 1.0 CY 10 CZ 10

!*!Label Imperfection
IMP AMXY 1 AMXZ 1

!*!Label Creep
CREP PHI 2.5

!*!Label Combinations
COMB LC AUTO FORC ALL

END
```

### Example 2 — Two design groups in separate blocks + summary (NCM)

Each design group must be in its own `+PROG COLUMN` block. A final block prints the summary.

```
$ --- Group 1: ground floor columns 300x300 ---
+PROG COLUMN urs:6
HEAD Column design — GF 300x300

CTRL NCM
CTRL DCNO 1

DGRP NO GRP1 TITL "GF columns 300x300"
  SLN 101 AXIS "A/1" LEV "GF" TITL "Column C1"
  SLN 102 AXIS "A/2" LEV "GF" TITL "Column C2"

GEOM BETY 1.0 BETZ 1.0
IMP AMXY 2 AMXZ 2
CREP PHI 2.5

COMB LC AUTO FORC ALL

END

$ --- Group 2: ground floor columns 400x400 ---
+PROG COLUMN urs:7
HEAD Column design — GF 400x400

CTRL NCM
CTRL DCNO 1

DGRP NO GRP2 TITL "GF columns 400x400"
  SLN 201 AXIS "B/1" LEV "GF" TITL "Column C5"
  SLN 202 AXIS "B/2" LEV "GF" TITL "Column C6"

GEOM BETY 1.0 BETZ 1.0
IMP AMXY 2 AMXZ 2
CREP PHI 2.5

COMB LC AUTO FORC ALL

END

$ --- Summary of all design groups ---
+PROG COLUMN urs:8
HEAD Design group summary

ECHO DGRP FULL
CTRL NCM
CTRL DCNO 1

END
```

### Example 3 — Column using design elements (DSLN) with explicit combinations

```
+PROG COLUMN urs:7
HEAD Column design via design elements

CTRL NCM
CTRL DCNO 1

DGRP NO S101 TITL "Cantilever columns level 1"
  DSLN 1001 AXIS "A/1" LEV "1.OG" TITL "Column 300x300"
  DSLN 1002 AXIS "A/2" LEV "1.OG" TITL "Column 300x300"

GEOM BETY 2.0 BETZ 2.0           $ cantilever effective length
CTRL CANT XZ

IMP AMXY 1 AMXZ 1
CREP PHI 2.5

COMB LC 1001 TYPE (D) TITL "1.35G + 1.5Q"
  COPY NO 1 FACT 1.35
  COPY NO 2 FACT 1.5
COMB LC 1002 TYPE (D) TITL "1.35G + 1.5W"
  COPY NO 1 FACT 1.35
  COPY NO 3 FACT 1.5

END
```

---

## Unit Summary for COLUMN

| Quantity | Unit | Parameters |
|----------|------|------------|
| Column length | `[m]` | `L` on `GEOM` |
| Elevation | `[m]` | `Z0` on `SLN`/`DSLN` |
| Imperfection | `[m]` | `EIXY`/`EIXZ` on `IMP` |
| Effective length coefficient | `[-]` | `BETY`/`BETZ` on `GEOM` |
| Curvature coefficient | `[-]` | `CY`/`CZ` on `GEOM` |
| Creep coefficient | `[-]` | `PHI` on `CREP` |
| Number of members | `[-]` | `AMXY`/`AMXZ` on `IMP` |
| Combination factor | `[-]` | `FACT` on `COPY` |
| Design case number | `[-]` | `DCNO`/`DGNO` on `CTRL` |
