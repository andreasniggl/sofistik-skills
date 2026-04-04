# Module: DECREATOR — Design Element Creation

## Purpose

DECREATOR generates Design Elements along structural members. Design Elements are independent of the Finite Element discretisation and define design sections at any chosen position along a structural line. They collect and integrate forces from beam and quad elements into member-level internal forces (N, V_y, V_z, M_y, M_z, M_t) at specific design sections. DECREATOR enhances subsequent design procedures (BEAM, COLUMN, AQB) by transferring FE results to design sections.

## Load this file when

The user needs to create design elements for RC beam, column, or member design checks. DECREATOR is required before running BEAM or COLUMN modules.

## Module block template

```
+PROG DECREATOR urs:<n>
HEAD <description>

!*!Label Control
CTRL TEND AUTO

!*!Label Design Elements
DSLN NO 1 NCS 2 HDIV 0.5[m] FREF SC TITL 'Beam B1'
  DGEO SLN 1,2,3
  DSLC REF STRT S 0.0 TYPM SUPP
  DSLC REF STRT S 0.20[m] TYPM HFAC
  DSLC REF STRT S 0.94[m] TYPM SHEA
  DSLC REF END  S 0.20[m] TYPM HFAC
  DSLC REF END  S 0.94[m] TYPM SHEA
  DSLC REF END  S 0.0 TYPM SUPP
  DSEL BEAM

!*!Label Load Cases
LC (1 10 1)

END
```

> **Key rules:**
> - `DSLN` creates the design element definition only. Load cases via `LC` must also be specified to trigger force calculation.
> - Sub-records `DGEO`, `DSLC`, and `DSEL` are attributes of the preceding `DSLN` and must follow it immediately.
> - If no `DGEO` is given, DECREATOR tries to use the structural line with the same number as the design element.
> - If no `DSEL` is given, the default is `DSEL BEAM` — beam elements along the structural line.
> - Design sections are automatically created at start and end points and at all intermediate structural points (supports). Explicit `DSLC` records add additional sections.

---

## Commands

| Command | Purpose |
|---------|---------|
| `CTRL`  | Module-level control options (tendon effects, interpolation, warping) |
| `DSLN`  | Define a design element along a structural member |
| `DGEO`  | Define geometry of the design element (sub-record of DSLN) |
| `DSLC`  | Define explicit design sections along the design element (sub-record of DSLN) |
| `DSEL`  | Select finite elements for force transfer (sub-record of DSLN) |
| `LC`    | Select load cases for force calculation |
| `GRP`   | Assign design elements to secondary groups |
| `DSID`  | List design element IDs belonging to a group (sub-record of GRP) |
| `DDEL`  | Delete design elements from the database |
| `ECHO`  | Control output verbosity |
| `EXPO`  | Export design element definitions to a .dat file |
| `FPLT`  | Control force plot output |

---

### CTRL — Control of Calculation

Sets global control options that apply to all subsequent design element definitions.

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
| `GAUS` | Source of quad element forces for interpolation | `NO` | `YES` = use Gauss point forces; `NO` = use nodal forces |
| `TEND` | Consider tendon effects in quad elements | `AUTO` | `AUTO` = consider tendon effects for prestressing load cases only; `YES` = consider for all load cases; `NO` = do not consider tendon effects |
| `CINT` | Cross-section interpolation for beam elements | `NO` | `YES` = interpolate cross sections along variable-section beams; `NO` = do not interpolate |
| `WARP` | Warping moments from quad elements | `NO` | `YES` = calculate warping moment integration; `NO` = do not calculate |

> CTRL must be defined before the design elements it applies to.
> `CTRL TEND AUTO` assumes that CSM difference load cases are labelled accordingly — for prestressing and creep+shrinkage load cases only concrete stresses are considered (tendon forces omitted); for all other load cases tendon forces are integrated with quads.
> `CTRL CINT YES` requires `DSLN FREF SC` to be useful. Interpolated cross-section IDs are numbered from 2000 upward.

**Typical usage:**
```
CTRL GAUS YES
CTRL TEND YES
CTRL CINT YES
```

---

### DSLN — Design Element Definition

Creates and stores the definition of a design element. The number `NO` also serves as a reference to a structural line whenever one exists with the same number. If a design element with the same number already exists, all its previous results are removed before the new one is stored.

> This command creates only the definition. Force calculation requires a mandatory `LC` record.

**Syntax:**
```
DSLN NO NCS NCS2 HDIV FREF TITL GRP TYPE
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `NO`      | int    | —     | **req** | Number of the design element (required) |
| `NCS`     | int    | —     | —       | Number of primary cross-section (from AQUA). If omitted and `DSEL BEAM` is active, cross-section IDs are transferred from beam elements automatically. |
| `NCS2`    | int    | —     | —       | Number of secondary cross-section for linearly varying sections. Assigned to the end point; NCS is assigned to the start. Both must be of the same type. |
| `HDIV`    | float  | `[m]` | —       | Maximum distance for intermediate section subdivision. Intermediate sections are for plotting only — no design is performed at them. Minimum value: 0.01 m. |
| `FREF`    | enum   | —     | `*`     | Reference axis for integrated forces (see table below) |
| `TITL`    | string | —     | —       | Designation of the design element (up to 32 characters) |
| `GRP`     | string | —     | —       | Secondary group name (1–4 characters, must start with a letter). The group must already exist in SOFiMSHC or will be created. |
| `TYPE`    | enum   | —     | `GENE`  | Type of structural member intended for design (see table below) |

**FREF — force reference axis:**

| Value | Description |
|-------|-------------|
| `SC`  | Cross-sectional centres — forces are transferred to the centroid/barycentre of the assigned cross-section. **Default when NCS is given or beam elements have sections.** |
| `GC`  | Geometric centre of sectional cuts — centroid of the intersection geometry. **Default when no cross-section is assigned and finite elements are intersected.** |
| `REF` | Reference axis of the design element itself. **Default in all other cases.** |

**TYPE — design element type:**

| Value  | Description |
|--------|-------------|
| `GENE` | General structural member — **default** |
| `CORE` | Intended for building core. The x-axis must be vertical (parallel to gravity ± 0.5°). Requires NCS. |
| `SHRW` | Intended for building shear wall. The x-axis must be vertical. |
| `COMP` | Intended for composite bridge girders. Cross-sections are taken from beams on the design element (DGEO AXIS/SLN/BEAM). Requires thin-walled composite sections. Explicit design sections are not necessary — all intermediate sections are checked. |
| `COLU` | Intended for column design |
| `BEAM` | Intended for beam design |

> When `NCS` and `NCS2` are both given, cross-sections are linearly interpolated between start and end for each design section. Both must be of the same type (e.g. both rectangular, not one rectangular and one polygon).
> When `HDIV` is not a factor of the distance between two explicit design sections, the interval is adjusted to the closest value not exceeding HDIV.

**Sub-records for DSLN** (must follow immediately after the `DSLN` record):
- `DGEO` — geometry of the design element
- `DSLC` — explicit design sections along the design element
- `DSEL` — finite element selection for force transfer

**Typical usage:**
```
$ Simple beam design element along SLN 1
DSLN NO 1 HDIV 0.5[m] TITL 'Beam span 1'

$ Design element with explicit cross-section
DSLN NO 2 NCS 3 FREF SC TITL 'Main girder'

$ Column design element
DSLN NO 10 NCS 4 TYPE COLU TITL 'Column C1'

$ Variable cross-section (tapered beam)
DSLN NO 5 NCS 1 NCS2 2 FREF SC TITL 'Tapered beam'
```

---

### DGEO — Geometry of Design Element (sub-record of DSLN)

Defines the geometry of a design element. Must follow immediately after the parent `DSLN` record.

**Syntax:**
```
DGEO OPT ID X1 Y1 Z1 X2 Y2 Z2 KR DRX DRY DRZ SA SE
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `OPT`     | enum   | —     | `SLN`   | Type of geometry (see table below) |
| `ID`      | int    | —     | —       | Reference number(s) — structural line, beam element, truss element, or axis number depending on OPT |
| `X1`      | float  | `[m]` | —       | X-coordinate of start point (for OPT LINE) |
| `Y1`      | float  | `[m]` | —       | Y-coordinate of start point |
| `Z1`      | float  | `[m]` | —       | Z-coordinate of start point |
| `X2`      | float  | `[m]` | —       | X-coordinate of end point (for OPT LINE) |
| `Y2`      | float  | `[m]` | —       | Y-coordinate of end point |
| `Z2`      | float  | `[m]` | —       | Z-coordinate of end point |
| `KR`      | enum   | —     | —       | Direction of the local z-axis (see table below) |
| `DRX`     | float  | —     | —       | X-component of direction vector of the local z-axis |
| `DRY`     | float  | —     | —       | Y-component of direction vector of the local z-axis |
| `DRZ`     | float  | —     | —       | Z-component of direction vector of the local z-axis |
| `SA`      | float  | `[m]` | —       | Start station along an axis (for OPT AXIS, unitless station parameter) |
| `SE`      | float  | `[m]` | —       | End station along an axis (for OPT AXIS, unitless station parameter) |

**OPT — geometry type:**

| Value  | Description |
|--------|-------------|
| `SLN`  | Derive geometry from one or more connected structural lines. ID takes a list of up to 1000 SLN numbers. **Default.** |
| `BEAM` | Construct geometry from a connected sequence of beam elements. ID takes a list of up to 1000 beam element numbers. |
| `TRUS` | Similar to BEAM, but for truss elements. |
| `LINE` | Form a straight line from two points in global coordinates. Requires X1/Y1/Z1 and X2/Y2/Z2. The local z-axis direction must also be specified via DRX/DRY/DRZ. |
| `AXIS` | Geometry based on a primary or secondary axis. Use SA/SE to trim the geometry to specific stations. |
| `GUID` | Geometry based on a guide line |

**KR — local z-axis direction:**

| Value  | Description |
|--------|-------------|
| `POSX` | Positive global X |
| `POSY` | Positive global Y |
| `POSZ` | Positive global Z |
| `NEGX` | Negative global X |
| `NEGY` | Negative global Y |
| `NEGZ` | Negative global Z |

> For `OPT SLN` and `OPT BEAM`: the design element inherits the local coordinate system of the referenced elements. At connection angles < 10° a smooth curve joins consecutive segments; at > 10° a kink with double sections is created.
> For `OPT LINE`: the local x-axis is the line from point 1 to point 2. The local z-axis is defined by DRX/DRY/DRZ. If not given, it is computed from the cross-product of local x with global Y (or global Z if parallel).
> If no `DGEO` is given, DECREATOR attempts to create a design element along the structural line with the same number as the `DSLN NO`.
> Connected sequences need not be listed in order — DECREATOR rearranges them automatically. However, they must form a connected geometry without gaps.

**Typical usage:**
```
$ Design element along structural lines 11, 12, 13
DSLN NO 1
  DGEO SLN 11,12,13

$ Design element along beam elements
DSLN NO 2
  DGEO BEAM (1001 1010 1)

$ Design element along a user-defined straight line
DSLN NO 3
  DGEO LINE X1 0.0 Y1 0.0 Z1 0.0 X2 8.0 Y2 0.0 Z2 0.0 DRX 0 DRY 0 DRZ 1

$ Design element along an axis with trimmed stations
DSLN NO 4
  DGEO AXIS 1 SA 0.0 SE 50.0
```

---

### DSLC — Design Sections (sub-record of DSLN)

Defines explicit design sections along the design element at which properties and forces are interpolated from the analysis. Must follow immediately after the parent `DSLN` record (or after other sub-records of the same DSLN).

**Syntax:**
```
DSLC REF S TYPM TYPT
```

| Parameter | Type   | Unit       | Default | Description |
|-----------|--------|------------|---------|-------------|
| `REF`     | enum   | —          | `STRT`  | Reference point for the position S (see table below) |
| `S`       | float  | `[m]`/`[-]`| 0.0    | Distance or relative position on the DSLN axis. Unit is `[m]` for REF STRT/END/MID; dimensionless `[0–1]` for REF XI. |
| `TYPM`    | enum   | —          | `SECT`  | Type of section for main bending (see table below) |
| `TYPT`    | enum   | —          | `SECT`  | Type of section for transverse bending (see table below) |

**REF — reference point:**

| Value  | Description |
|--------|-------------|
| `STRT` | Distance measured from start of the design element — **default** |
| `END`  | Distance measured from end of the design element |
| `MID`  | Distance measured from middle of the design element |
| `XI`   | Relative position between start (0) and end (1) of the design element |

**TYPM / TYPT — section type:**

| Value  | Description |
|--------|-------------|
| `SECT` | Standard design section — **default** |
| `CFAC` | Face of clamped (rigid/monolithic) support. In BEAM: triggers moment reduction per EC2 5.3.2.2 (3). |
| `HFAC` | Face of hinged (non-monolithic) support. In BEAM: triggers moment reduction per EC2 5.3.2.2 (4). |
| `IFAC` | Face of indirect support. In BEAM: triggers moment reduction for indirect supports per EC2 5.3.2.2 (3). |
| `SHEA` | Main and cross shear section. In BEAM/AQB: triggers shear force reduction at support faces. |
| `SUPP` | Manual identification of a support location. Required for AQB/BEAM to identify span ends when no SPT is detected along the DSLN axis. |

> Explicit design sections are also created automatically by DECREATOR at the start and end points, and at all intermediate structural points (supports detected from SPT along the DGEO SLN geometry).
> When explicit sections coincide with intermediate sections from HDIV, they are merged.
> Double sections are created automatically at positions where abrupt changes in cross-section or internal forces occur, or where the DSLN axis has a kink > 5%.
> Multiple REF values can be combined: `DSLC REF STRT,END S 0.20[m] TYPM HFAC` creates sections at both start+0.20 and end-0.20.

**Typical usage:**
```
$ Support faces and shear sections for a simply supported beam
DSLN NO 1
  DSLC REF STRT S 0.0 TYPM SUPP          $ start support
  DSLC REF STRT S 0.15[m] TYPM HFAC      $ face of hinged support (left)
  DSLC REF STRT S 0.95[m] TYPM SHEA      $ shear section (left)
  DSLC REF END  S 0.15[m] TYPM HFAC      $ face of hinged support (right)
  DSLC REF END  S 0.95[m] TYPM SHEA      $ shear section (right)
  DSLC REF END  S 0.0 TYPM SUPP          $ end support

$ Mid-span section
  DSLC REF MID  S 0.0

$ Relative position
  DSLC REF XI S 0.25
```

---

### DSEL — Element Selection (sub-record of DSLN)

Selects finite elements from which design element results are computed. Must follow immediately after the parent `DSLN` record (or other sub-records). Multiple `DSEL` records can be combined with AND logic.

**Syntax:**
```
DSEL OPT NO YMIN ZMIN YMAX ZMAX
```

| Parameter | Type  | Unit  | Default    | Description |
|-----------|-------|-------|------------|-------------|
| `OPT`     | enum  | —     | `BEAM`     | Type of selection (see table below) |
| `NO`      | int   | —     | —          | Reference number for QSAR, SEC, or GRP |
| `YMIN`    | float | `[m]` | −1000000   | Minimum local y-coordinate of bounding box |
| `ZMIN`    | float | `[m]` | −1000000   | Minimum local z-coordinate of bounding box |
| `YMAX`    | float | `[m]` | +1000000   | Maximum local y-coordinate of bounding box |
| `ZMAX`    | float | `[m]` | +1000000   | Maximum local z-coordinate of bounding box |

**OPT — selection type:**

| Value  | Description |
|--------|-------------|
| `BEAM` | Select beam elements along the structural line referenced by the design element geometry. Also automatically transfers cross-section IDs from beam elements. **Default.** |
| `QSAR` | Select quad elements on a structural area. NO = structural area number. |
| `QSEC` | Select elements within the bounding box of the cross-section assigned at NCS. |
| `SEC`  | Select elements within the outer rectangular bounding box of the cross-section at NCS. Applies to beam, quad, hex and tet elements. |
| `BOX`  | Select elements within a user-defined bounding frame in local y-z coordinates. Requires YMIN/ZMIN/YMAX/ZMAX. |
| `GRP`  | Additional filter by primary group number(s). Must be combined with other selection options. NO = group number(s). |
| `QGRP` | Select quad elements by group number |
| `QBOX` | Select quad elements within a bounding box |

> Combinations of options use AND logic — for example, `DSEL BOX` followed by `DSEL GRP 3` selects elements within the box AND in group 3.
> If no `DSEL` is given at all, `DSEL BEAM` is used as default, attempting to collect beam elements along the structural line.
> Maximum of 1024 DSEL definitions.

**Typical usage:**
```
$ Default: beam elements along SLN
DSLN NO 1
  DSEL BEAM

$ Select quad elements on structural area 5
DSLN NO 2
  DGEO LINE X1 0 Y1 0 Z1 0 X2 8 Y2 0 Z2 0 DRX 0 DRY 0 DRZ 1
  DSEL QSAR 5

$ Select elements within a bounding box, filtered by group
DSLN NO 3
  DGEO LINE X1 0 Y1 0 Z1 0 X2 0 Y2 0 Z2 10 DRX 1 DRY 0 DRZ 0
  DSEL BOX YMIN -6 ZMIN -3 YMAX +6 ZMAX +3
  DSEL GRP 3,4

$ Select within cross-section bounding box
DSLN NO 4 NCS 2
  DSEL SEC
```

---

### LC — Load Case Selection

Selects load cases for force calculation. This is mandatory for DECREATOR to compute and store forces. If not specified, only the design element definition is created without forces.

**Syntax:**
```
LC NO
```

| Parameter | Type    | Unit | Default | Description |
|-----------|---------|------|---------|-------------|
| `NO`      | int/enum| —    | —       | Number(s) of load case(s). Use SOFiSTiK list syntax, e.g. `(1 10 1)` for LC 1 to 10. |

**NO — special values:**

| Value  | Description |
|--------|-------------|
| `ALL`  | All valid load cases (characteristic loads, natural frequency, and buckling modes) |
| `NONE` | Reset load case selection |

> LC affects all preceding DSLN definitions in the same DECREATOR block.
> Valid load case types: characteristic loads (linear and nonlinear), natural frequency modes, and buckling modes.
> DECREATOR can be run in two separate passes: first for definition (DSLN only), then for force calculation (LC only on existing definitions).

**Typical usage:**
```
$ Load cases 1 to 10
LC (1 10 1)

$ All valid load cases
LC ALL

$ Specific load cases
LC 1,2,5,11
```

---

### ECHO — Output Control

Controls the amount of data printed in the output.

**Syntax:**
```
ECHO OPT VAL POS
```

| Parameter | Type  | Unit  | Default | Description |
|-----------|-------|-------|---------|-------------|
| `OPT`     | enum  | —     | —       | Output category |
| `VAL`     | enum  | —     | —       | Output extent |
| `POS`     | float | `[m]` | —       | Section position for detail output (only with OPT DETL) |

**OPT — output category:**

| Value  | Description | Default |
|--------|-------------|---------|
| `DSLN` | Design element definitions | `YES` |
| `FORC` | Forces | `NO` |
| `TND`  | Tendons | `NO` |
| `DISP` | Displacements | `NO` |
| `LOAD` | Loads | `NO` |
| `SPLT` | Sectional plot (intersection details at each design section) | `NO` |
| `LPLT` | Longitudinal plot (internal forces along design element axis) | `NO` |
| `DETL` | Detail sectional output (intermediate results from each FE) | `NO` |
| `FULL` | All the above options | — |

**VAL — output extent:**

| Value  | Description |
|--------|-------------|
| `NO`   | No output |
| `YES`  | Regular output |
| `FULL` | Extensive output |
| `EXTR` | Extreme output |

> If the same ECHO command is defined multiple times, only the last one is considered.
> `ECHO DETL YES POS 3.5` prints integrated forces from each FE at position 3.5 m. `FULL` adds interpolated/transformed forces. `EXTR` adds outer cut geometry polygon.
> `ECHO LPLT FULL` shows contributions from each finite element type in the longitudinal plot.

**Typical usage:**
```
ECHO DSLN YES
ECHO FORC YES
ECHO SPLT YES
ECHO LPLT YES
```

---

### GRP — Assignment of Groups

Assigns a secondary group to one or more design elements. Must be followed by a `DSID` sub-record listing the design element IDs.

**Syntax:**
```
GRP NO TITL
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `NO`      | string | —    | —       | Name of secondary group (1–4 characters, must start with a letter) |
| `TITL`    | string | —    | —       | Description of the group |

**Sub-record: DSID**

```
DSID NO
```

| Parameter | Type | Unit | Default | Description |
|-----------|------|------|---------|-------------|
| `NO`      | int  | —    | —       | List of design element IDs to be grouped |

> Maximum 1000 design elements per group.
> Group assignment at `DSLN GRP` is a shorter alternative for assigning a single group per design element.
> If the group does not exist in SOFiMSHC, it will be created.
> Only secondary groups can be assigned to design elements.

**Typical usage:**
```
GRP 'BM1' TITL 'Floor beams level 1'
  DSID 1,2,3

GRP 'COL' TITL 'Columns'
  DSID 10,11,12
```

---

### DDEL — Design Element Deletion

Removes all information belonging to the listed design element(s) from the database, including all associated results and interpolated cross-sections.

**Syntax:**
```
DDEL NO
```

| Parameter | Type    | Unit | Default | Description |
|-----------|---------|------|---------|-------------|
| `NO`      | int/enum| —    | —       | ID(s) of design element(s) to delete |

**NO — special values:**

| Value | Description |
|-------|-------------|
| `ALL` | Delete all design elements |

**Typical usage:**
```
$ Delete specific design elements
DDEL NO 1,2,3

$ Delete all design elements
DDEL ALL
```

---

### EXPO — Export Design Element Definitions

Exports design element definitions from the database as CADINP to a .dat file. Only definitions are exported — LC, ECHO, and CTRL settings are not included.

**Syntax:**
```
EXPO TO DSLN
```

| Parameter | Type    | Unit | Default | Description |
|-----------|---------|------|---------|-------------|
| `TO`      | string  | —    | —       | Target file name (include `.dat` extension). If omitted, the project name with suffix `_dln` is used. |
| `DSLN`    | int/enum| —    | `ALL`   | ID(s) of design element(s) to export |

**DSLN — special values:**

| Value | Description |
|-------|-------------|
| `ALL` | Export all existing design elements |

**Typical usage:**
```
EXPO TO "target_file.dat" DSLN 1,2
EXPO DSLN ALL
```

---

### FPLT — Force Plot Control

Controls which force components are plotted in the output.

**Syntax:**
```
FPLT OPT VAL
```

| Parameter | Type | Unit | Default | Description |
|-----------|------|------|---------|-------------|
| `OPT`     | enum | —    | `FULL`  | Force component to control |
| `VAL`     | enum | —    | —       | Output level |

**OPT — force components:**

| Value  | Description |
|--------|-------------|
| `FULL` | All force components |
| `N`    | Normal force |
| `VY`   | Shear force V_y |
| `VZ`   | Shear force V_z |
| `T`    | Torsional moment M_t |
| `MY`   | Bending moment M_y |
| `MZ`   | Bending moment M_z |

**VAL — output level:**

| Value  | Description |
|--------|-------------|
| `OFF`  | No output |
| `NO`   | No output |
| `YES`  | Regular output |
| `FULL` | Extensive output |

---

## Complete DECREATOR Block Examples

### Example 1 — Simple beam with support face sections

```
+PROG DECREATOR urs:5
HEAD Design elements for floor beams

!*!Label Design Elements
DSLN NO 1 NCS 2 HDIV 0.5[m] FREF SC TITL 'Beam B1'
  DSLC REF STRT S 0.0 TYPM SUPP
  DSLC REF STRT S 0.15[m] TYPM HFAC         $ face of hinged support (left)
  DSLC REF STRT S 0.95[m] TYPM SHEA         $ shear section (left)
  DSLC REF END  S 0.15[m] TYPM HFAC         $ face of hinged support (right)
  DSLC REF END  S 0.95[m] TYPM SHEA         $ shear section (right)
  DSLC REF END  S 0.0 TYPM SUPP

!*!Label Load Cases
LC (1 10 1)

END
```

### Example 2 — Two-span continuous beam with intermediate support

```
+PROG DECREATOR urs:5
HEAD Design element for two-span beam

DSLN NO 10 NCS 3 HDIV 0.5[m] FREF SC TITL 'Continuous beam'
  DGEO SLN 1,2                              $ two spans from SLN 1 and 2

  $ Start support
  DSLC REF STRT S 0.0 TYPM SUPP

  $ Left of intermediate support
  DSLC REF STRT S 7.0-0.20[m] TYPM HFAC    $ face of support
  DSLC REF STRT S 7.0-(0.20+0.74)[m] TYPM SHEA

  $ Intermediate support
  DSLC REF STRT S 7.0[m] TYPM SUPP

  $ Right of intermediate support
  DSLC REF STRT S 7.0+0.20[m] TYPM HFAC
  DSLC REF STRT S 7.0+(0.20+0.74)[m] TYPM SHEA

  $ End support
  DSLC REF END  S 0.0 TYPM SUPP

LC (1 10 1)

END
```

### Example 3 — Column design element with quad selection

```
+PROG DECREATOR urs:5
HEAD Design element for RC column

DSLN NO 20 NCS 4 TYPE COLU TITL 'Column C1'
  DGEO LINE X1 3.0 Y1 3.0 Z1 0.0 X2 3.0 Y2 3.0 Z2 3.5 DRX 1 DRY 0 DRZ 0
  DSEL BOX YMIN -0.5 ZMIN -0.5 YMAX 0.5 ZMAX 0.5
  DSEL GRP 5

LC ALL

END
```

### Example 4 — Separation of definition and force calculation

```
$ --- First run: definition only ---
+PROG DECREATOR urs:5
HEAD Definition of design elements
DSLN 1 NCS 1 HDIV 0.5[m]
  DSLC REF MID
DSLN 2 NCS 1 HDIV 0.5[m]
  DSLC REF MID
END

$ --- Second run: force calculation ---
+PROG DECREATOR urs:6
HEAD Force calculation for existing design elements
LC 1,2,3,4,5
END
```

---

## Worked Example — Two-Span Continuous RC Beam

The following DECREATOR block is part of a complete two-span continuous beam workflow (AQUA → SOFIMSHC → SOFILOAD → ASE → DECREATOR → BEAM). Two 6 m spans, simply supported on three hinged supports, C30/37 concrete with B500B rebar, rectangular section 300 x 600 mm.

The design element spans both structural lines (SLN 1 and SLN 2). Support face sections (HFAC) are placed at 125 mm from each support axis (half of a 250 mm support width). Shear sections (SHEA) are placed at 800 mm from start/end and at 5200/6800/11200 mm from start — approximately one effective depth (d ≈ 540 mm) from the support faces. Intermediate sections at HDIV 0.25 m provide smooth force plots.

```
+PROG DECREATOR urs:5
HEAD Design Elements Definition

DSLN 1 HDIV 0.25 TYPE BEAM
  DGEO SLN 1
  DGEO SLN 2

  $ Start support (pinned)
  DSLC REF STRT S 0.0 TYPM SUPP
    DSLC REF STRT S 0.125 TYPM HFAC         $ face of support A
    DSLC REF STRT S 0.8 TYPM SHEA           $ shear section left of span 1

    DSLC REF STRT S 5.2 TYPM SHEA           $ shear section right of span 1
    DSLC REF STRT S 5.875 TYPM HFAC         $ face of support B (left)

  $ Intermediate support B
  DSLC REF STRT S 6.0 TYPM SUPP
    DSLC REF STRT S 6.125 TYPM HFAC         $ face of support B (right)
    DSLC REF STRT S 6.8 TYPM SHEA           $ shear section left of span 2

    DSLC REF STRT S 11.2 TYPM SHEA          $ shear section right of span 2
    DSLC REF STRT S 11.875 TYPM HFAC        $ face of support C

  $ End support C
  DSLC REF STRT S 12 TYPM SUPP

LC ALL                                       $ transfer all load cases

END
```

---

## Unit Summary for DECREATOR

| Quantity | Unit | Parameters |
|----------|------|------------|
| Distances along design element | `[m]` | `HDIV`, `S` on `DSLC`, `SA`/`SE` on `DGEO` |
| Coordinates | `[m]` | `X1`/`Y1`/`Z1`/`X2`/`Y2`/`Z2` on `DGEO` |
| Bounding box extents | `[m]` | `YMIN`/`ZMIN`/`YMAX`/`ZMAX` on `DSEL` |
| Direction vectors | `—` | `DRX`/`DRY`/`DRZ` on `DGEO` |
| Relative position | `[-]` | `S` on `DSLC` when `REF XI` |
