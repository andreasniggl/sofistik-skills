# Module: BEMESS — RC Slab and Shell Design

## Purpose

BEMESS designs reinforced concrete slabs, shells, and disks (plane stress elements) at the element level. It computes required area reinforcement (cm2/m) for bending, shear, and membrane forces from QUAD element results, performs punching shear checks at column supports, and carries out SLS verifications (crack width, stress range, fatigue). BEMESS works directly on the FE mesh — no design elements from DECREATOR are needed.

**Supported design codes:** All Eurocode national annexes supported by SOFiSTiK (EN, DIN, OEN, BS, NF, SIA, etc.), plus ACI, CSA, GB, IS, and others as configured in AQUA NORM.

## Load this file when

The user needs to design RC slabs, flat slabs, shells, or walls for area reinforcement (ULS bending + shear), punching at column heads, or SLS crack width checks.

## Prerequisites

Before running BEMESS, the following modules must have been executed:
1. **AQUA** — materials (concrete + reinforcement steel)
2. **SOFIMSHC** — structural model with SAR elements (slabs/shells meshed as QUADs)
3. **SOFILOAD** — load definition
4. **ASE** — structural analysis
5. **MAXIMA** (optional) — load case superposition for ULS/SLS envelopes

> BEMESS operates on QUAD elements directly. It does not require DECREATOR or design elements.
> The design is typically run in two passes: first a PARA run to store design parameters (cover, diameters, crack widths per group), then one or more design runs with specific load cases.

## Module block template

```
+PROG BEMESS urs:<n>
HEAD <description>

!*!Label Design Parameters
GEOM HA 35[mm] DHA 10[mm] HB 35[mm] DHB 10[mm]
PARA NOG - DU 10[mm] WKU 0.3[mm] DL 10[mm] WKL 0.3[mm]

END

+PROG BEMESS urs:<n+1>
HEAD <description>

!*!Label ULS Design
CTRL LCR 1
LC DESI

!*!Label SLS Crack Check
CRAC WK PARA

!*!Label Punching
PUNC YES

END
```

> **Key rules:**
> - BEMESS uses a two-layer reinforcement model: upper (U) and lower (L), each with main and transverse directions.
> - Design parameters (PARA) should be defined once in a separate BEMESS block and are stored in the database for subsequent runs.
> - Load cases are selected with `LC` using superposition literals from MAXIMA (e.g. `LC DESI` for ULS, `LC RARE` for SLS).
> - Reinforcement results are stored per design case number (`CTRL LCR`). Use `CTRL RMOD SUPE` to envelope across multiple runs.
> - Punching checks require support reactions in the database (from ASE).

---

## Commands

| Command | Purpose |
|---------|---------|
| `ECHO`  | Control output verbosity |
| `CTRL`  | Design task, save mode, design procedure, shear/punching parameters |
| `GEOM`  | Cross-section geometry (cover distances) |
| `DIRE`  | Reinforcement directions (angle of main reinforcement) |
| `PARA`  | Design parameters per group (diameters, crack widths, minimum reinforcement) |
| `LAY`   | Multi-layer reinforcement definition |
| `LC`    | Select design load cases |
| `GRP`   | Select groups for design |
| `ELEM`  | Select individual elements for design |
| `NODE`  | Select individual nodes for design |
| `MAT`   | Override material properties for design |
| `CRAC`  | Crack width control parameters |
| `NSTR`  | SLS stress checks (stress range, fatigue, decompression) |
| `PUNC`  | Punching shear design at column supports |
| `SELE`  | Selection/exclusion of punching nodes |
| `REIN`  | Title of the design case |
| `MREI`  | Minimum reinforcement control |

---

### ECHO — Output Control

Controls the extent of printed output.

**Syntax:**
```
ECHO OPT VAL
```

| Parameter | Type | Unit | Default | Description |
|-----------|------|------|---------|-------------|
| `OPT`    | enum | —    | `FULL`  | Output category |
| `VAL`    | enum | —    | —       | Output extent |

**OPT — output categories:**

| Value  | Description | Default |
|--------|-------------|---------|
| `FULL` | All options | — |
| `PARA` | Design parameters | `FULL` |
| `MAT`  | Material (same as PARA) | `FULL` |
| `REIN` | Reinforcement design results | elements with max values |
| `NSTR` | Strains, stress range, concrete stress (SLS) | elements with max values |
| `PUNC` | Punching checks (YES=max node FULL, FULL=all nodes) | `YES` |
| `RTAB` | Reinforcement compilation table | `NO` |
| `DMOM` | Design internal forces | `NO` |
| `STRE` | Linear stress determination | `YES` |
| `ELEM` | Print only these element numbers | — |
| `NODE` | Print only these node numbers | — |

**VAL — output extent:**

| Value  | Description |
|--------|-------------|
| `NO`   | No output |
| `YES`  | Regular output (elements/nodes with maximum results, no plots) |
| `FULL` | Extensive output (all elements/nodes, with plots) |
| `EXTR` | Extreme output (all load cases, strain details) |

**Typical usage:**
```
ECHO FULL YES               $ standard output
ECHO REIN FULL              $ all elements with reinforcement
ECHO PUNC FULL              $ all punching nodes
```

---

### DIRE — Reinforcement Direction

Defines the angle of the orthogonal two-course reinforcement mesh for upper and lower layers. The transverse reinforcement is always perpendicular to the main direction. Remains effective until another `DIRE` record is given.

**Syntax:**
```
DIRE UPP LOW X Y Z
```

| Parameter | Type  | Unit    | Default | Description |
|-----------|-------|---------|---------|-------------|
| `UPP`     | float | `[deg]` | 0       | Angle between upper main reinforcement direction and local x-axis (0–180°) |
| `LOW`     | float/enum | `[deg]` | 0  | Angle between lower main reinforcement direction and local x-axis (0–180°). Special values: `SYM` = symmetric reinforcement; `CENT` = centric (upper only, no lower). |
| `X`       | float | `[m]`   | —       | X-coordinate of centre for circular plate reinforcement |
| `Y`       | float | `[m]`   | —       | Y-coordinate of centre |
| `Z`       | float | `[m]`   | —       | Z-coordinate of centre (defines axis for 3D systems) |

> Clockwise angles are positive, measured from the local x-axis of the element.
> For plane problems the local x-axis is identical to the global X-axis.
> For disk systems (`SYST FRAM`), `LOW` is ignored — only `UPP` is used for both sides.
> `DIRE LOW SYM` designs with symmetric reinforcement (upper = lower) — useful for thin shells where both layers are close together.
> `DIRE LOW CENT` designs with only upper (centric) reinforcement and no lower layer.
> When `X`/`Y`/`Z` are given, a circular mesh reinforcement is defined: `UPP 0` places radial reinforcement outside, `UPP 90` places tangential reinforcement outside.

**Typical usage:**
```
$ Standard: main reinforcement parallel to local x-axis, both layers
DIRE UPP 0 LOW 0

$ Rotated reinforcement (45°)
DIRE UPP 45 LOW 45

$ Symmetric reinforcement for thin shells
DIRE UPP 0 LOW SYM

$ Circular plate reinforcement about centre (0, 0)
DIRE UPP 0 LOW 0 X 0.0 Y 0.0 Z 0.0
```

---

### CTRL — Control of the Design

Sets the design task, save mode, design method, and global parameters.

**Syntax:**
```
CTRL OPT VAL
```

The most important CTRL options for typical slab design are listed below. BEMESS has many additional advanced options — only the commonly needed ones are documented here.

**OPT — primary design control:**

| OPT    | Description | Default | VAL values |
|--------|-------------|---------|------------|
| `TYPE` | Design task | auto | `ULTI` = ULS design (loads on ULS level); `ACCI` = accidental; `EARQ` = earthquake; `SLS` = serviceability checks; `STRE` = linear stress calculation |
| `RMOD` | Save mode for reinforcement | `SAVE` (ULS), `SUPE` (SLS) | `SING` = single calculation, no save; `SAVE` = save, overwrite; `SUPE` = save maximum of calculated and stored; `DELE` = delete (use with LCR) |
| `LAY`  | Design procedure | `0` (ULS) / `1` (stress) | `0` = Baumann method (ULS) / Capra-Maury (SLS); `1` = layer design (strain iteration); `2` = sandwich model per draft EN 1992-1-1 Annex G |
| `LCR`  | Reinforcement distribution number (design case) | `1` | integer — identifies where results are stored in the database |
| `LCRI` | Envelope from multiple design runs | — | integer — takes maximum from LCR and LCRI |

**OPT — shear design:**

| OPT    | Description | Default | VAL values |
|--------|-------------|---------|------------|
| `RO_V` | Maximum longitudinal reinforcement ratio for shear in slab regions | `0.2%` | percentage. Use V2 for upper reinforcement limit. |
| `COTT` | Limitation of cot(theta) for shear design | code default | value between 1.0 and 3.0 |
| `VLEV` | Maximum lever arm for shear design | code default | e.g. `0.9` = max lever arm 0.9*d |
| `MINS` | Minimum shear reinforcement factor per EC2 9.3.1 | `0.6` (DE/OEN), `1.0` (others) | factor on beam minimum shear reinforcement |

**OPT — punching parameters:**

| OPT    | Description | Default |
|--------|-------------|---------|
| `BETA` | Eccentricity factor beta per EC2 6.4.3 | `0` (EN), `10` (DE/OEN) |
| `WINT` | Punching force integration at wall corners/ends | `0` (slab shear force integration) |
| `RADP` | Factor for check radius in punching | `6.0` |

**OPT — other:**

| OPT    | Description | Default |
|--------|-------------|---------|
| `WALL` | Deep beam / wall minimum reinforcement | `YES` for disks, `NO` for shells |
| `TENS` | Reduction of concrete compression at transverse tension | `25%` |
| `REDN` | Factor for design with reduced normal force | `1.0` |
| `REDM` | Factor for design with reduced bending moment | `1.0` |
| `BRIC` | Design of volume elements (0 = no BRIC design) | — |

> `CTRL TYPE` is usually set automatically based on the load cases selected with `LC`.
> `CTRL RMOD SUPE` is essential when combining ULS and SLS results — it keeps the maximum reinforcement from all runs.
> `CTRL LCR` must be consistent across runs that should be enveloped.

**Typical usage:**
```
$ ULS design, save as design case 1
CTRL LCR 1

$ SLS crack check, envelope onto existing results
CTRL TYPE SLS
CTRL RMOD SUPE
CTRL LCR 1

$ Delete a design case
CTRL RMOD DELE LCR 5
```

---

### GEOM — Cross-Section Geometry

Defines cover distances for the reinforcement layers. Values are typically set once in a PARA run and stored in the database.

**Syntax:**
```
GEOM H HA DHA HB DHB DDHA DDHB HPRE
```

| Parameter | Type  | Unit   | Default | Description |
|-----------|-------|--------|---------|-------------|
| `H`       | float | `[mm]` | from DB | Plate thickness override (use only in special cases) |
| `HA`      | float | `[mm]` | 35      | Centre distance of upper main reinforcement from upper face |
| `DHA`     | float | `[mm]` | 10      | Centre distance of upper transverse reinforcement from main reinforcement |
| `HB`      | float | `[mm]` | HA      | Centre distance of lower main reinforcement from lower face |
| `DHB`     | float | `[mm]` | DHA     | Centre distance of lower transverse reinforcement from main reinforcement |
| `DDHA`    | float | `[mm]` | DHA     | Centre distance of upper inner reinforcement from middle reinforcement |
| `DDHB`    | float | `[mm]` | DHB     | Centre distance of lower inner reinforcement from middle reinforcement |
| `HPRE`    | float | `[mm]` | —       | Compression zone thickness limit (for bubble/hollow decks) |

> GEOM values are usually set in a separate BEMESS PARA run. They are stored in the database and reused in subsequent design runs.
> `H` should normally not be overridden — the thickness comes from the SAR definition in SOFIMSHC.

**Typical usage:**
```
$ Exposure class XC1 (25mm cover + 10mm half-bar)
GEOM HA 35[mm] DHA 10[mm] HB 35[mm] DHB 10[mm]

$ Exposure class XC4 (40mm cover)
GEOM HA 50[mm] DHA 10[mm] HB 50[mm] DHB 10[mm]
```

---

### PARA — Design Parameters per Group

Defines bar diameters, crack widths, minimum reinforcement, and steel stresses per element group. Must follow a `GEOM` (and optionally `DIRE`) record to close the definition for a group. The first PARA record serves as default for all groups.

**Syntax:**
```
PARA NOG NOEL DU DU2 DU3 DL DL2 DL3
     WKU WKU2 WKU3 WKL WKL2 WKL3
     SSU SSU2 SSU3 SSL SSL2 SSL3
     ASU ASU2 ASU3 ASL ASL2 ASL3
     TYPE
     XMIN XMAX YMIN YMAX ZMIN ZMAX ROT
```

| Parameter | Type   | Unit      | Default | Description |
|-----------|--------|-----------|---------|-------------|
| `NOG`     | int/string | —     | all groups | Group number, SAR number, secondary group name, or `-` for all |
| `NOEL`    | int    | —         | —       | Specific element number (or SAR number when using SAR) |
| `DU`      | float  | `[mm]`    | 10      | Bar diameter upper 1st layer. `DU 0` = do not design this group. |
| `DU2`     | float  | `[mm]`    | DU      | Bar diameter upper 2nd layer |
| `DU3`     | float  | `[mm]`    | DU2     | Bar diameter upper 3rd layer |
| `DL`      | float  | `[mm]`    | DU      | Bar diameter lower 1st layer |
| `DL2`     | float  | `[mm]`    | DL      | Bar diameter lower 2nd layer |
| `DL3`     | float  | `[mm]`    | DL2     | Bar diameter lower 3rd layer |
| `WKU`     | float  | `[mm]`    | —       | Crack width upper 1st layer |
| `WKU2`    | float  | `[mm]`    | WKU     | Crack width upper 2nd layer |
| `WKL`     | float  | `[mm]`    | WKU     | Crack width lower 1st layer |
| `WKL2`    | float  | `[mm]`    | WKL     | Crack width lower 2nd layer |
| `ASU`     | float  | `[cm2/m]` | —       | Minimum reinforcement upper 1st layer |
| `ASL`     | float  | `[cm2/m]` | —       | Minimum reinforcement lower 1st layer |
| `TYPE`    | enum   | —         | —       | `MOD` = overwrite only the explicitly given values (no defaults applied) |

> The first PARA record (without NOG or with `NOG -`) sets defaults for all groups.
> Subsequent PARA records override values for specific groups.
> `PARA NOG ... DU 0` excludes a group from design entirely.
> Crack widths (WKU/WKL) are used by the `CRAC WK PARA` command for per-element crack checks.

**Typical usage:**
```
$ Default for all groups: d10, crack width 0.3mm
GEOM HA 35[mm] DHA 10[mm] HB 35[mm] DHB 10[mm]
PARA NOG - DU 10[mm] WKU 0.3[mm] DL 10[mm] WKL 0.3[mm]

$ Group 3: different cover, d20, crack width 0.2mm
GEOM HA 50[mm] DHA 10[mm] HB 50[mm] DHB 10[mm]
PARA NOG 3 DU 20[mm] WKU 0.2[mm] DL 20[mm] WKL 0.2[mm]

$ Override diameter for specific elements only
PARA NOEL 20710,20711 DU 16[mm] DL 14[mm] DL2 14[mm] TYPE MOD
```

---

### LC — Selection of Design Load Cases

Selects load cases for which the design is performed. Typically uses superposition results from MAXIMA.

**Syntax:**
```
LC NO PERC FACT SELE
```

| Parameter | Type    | Unit  | Default | Description |
|-----------|---------|-------|---------|-------------|
| `NO`      | int/enum| —     | —       | Load case number(s), or superposition literal |
| `PERC`    | float   | `[%]` | 100     | Factor of permanent load for SLS checks |
| `FACT`    | float   | `[-]` | —       | Factor for individual load cases |

**NO — superposition literals (from MAXIMA):**

| Value  | Description |
|--------|-------------|
| `DESI` or `(D)` | ULS design combination |
| `ACCI` or `(A)` | Accidental combination |
| `EARQ` or `(E)` | Earthquake combination |
| `PERM` or `(P)` | SLS quasi-permanent combination |
| `RARE` or `(R)` | SLS rare (characteristic) combination |
| `FREQ` or `(F)` | SLS frequent combination |
| `NONF` or `(N)` | SLS non-frequent combination |

> `LC DESI` automatically selects all ULS superposition load cases from MAXIMA.
> `LC RARE` selects SLS rare combinations for crack checks.
> Multiple `LC` records can be given in one BEMESS run.
> For punching checks, the load cases with maximum support reactions must be included.

**Typical usage:**
```
$ ULS design with MAXIMA superposition
LC DESI

$ SLS rare combination for crack check
LC RARE

$ Specific load case numbers
LC 1001,1002,1003

$ SLS with permanent factor
LC PERM PERC 100
```

---

### GRP — Selection of Groups

Selects element groups for design. Replaces ELEM and NODE selection.

**Syntax:**
```
GRP NO SAR CS
```

| Parameter | Type    | Unit | Default | Description |
|-----------|---------|------|---------|-------------|
| `NO`      | int/string | — | all     | Group number or secondary group name |
| `SAR`     | int     | —    | —       | Structural area number (alternative to NO) |
| `CS`      | int     | —    | 9998    | Construction stage for tendon activation |

> Without GRP input, all groups are designed.
> `GRP NO ... DU 0` in PARA is a cleaner way to exclude groups.

**Typical usage:**
```
$ Design only group 1 and 3
GRP 1
GRP 3

$ Design by structural area
GRP SAR 1
```

---

### CRAC — Crack Width Control

Controls the crack width verification per EN 1992-1-1, Ch. 7.3.

**Syntax:**
```
CRAC WK BOND BET1 BET2 WKB XMIN SAND AIMA CODE
```

| Parameter | Type    | Unit   | Default | Description |
|-----------|---------|--------|---------|-------------|
| `WK`      | float/enum | `[mm]` | — | Crack width value or control mode |
| `BOND`    | enum    | —      | `RIB`   | Bond quality: `RIB` = ribbed steel; `PROF` = profiled; `PLAI` = plain |
| `BET1`    | float   | `[-]`  | from BOND | Bond coefficient (1.0 for RIB, 0.75 for PROF, 0.5 for PLAI) |
| `BET2`    | enum    | —      | `STAT`  | Load duration: `STAT` = long-term (kt=0.4); `SHOR` = short-term (kt=0.6) |
| `WKB`     | float   | `[mm]` | WK      | Crack width for lower side (if different from upper) |
| `XMIN`    | float   | `[mm]` | 0       | Minimum compression zone thickness |
| `SAND`    | int     | —      | 0       | Sandwich model interaction of reinforcement directions (0=off, 1/2=on) |
| `CODE`    | int     | —      | —       | Override country code for crack width (1=EN, 2=DE, 3=BS, etc.) |

**WK — control mode:**

| Value   | Description |
|---------|-------------|
| `TAB`   | Simplified check using table of limiting diameters (from PARA) |
| `> 0`   | Direct crack width calculation with this value as limit |
| `999`   | Only calculate crack width for graphical output (no reinforcement increase) |
| `PARA`  | Use crack width values defined in PARA per group/element |

> `CRAC WK PARA` is the recommended approach — it uses the per-group crack widths defined in PARA.
> The crack check increases reinforcement if necessary to satisfy the crack width limit.
> `CRAC WK TAB` uses the simplified table method per EC2 7.3.3 (Table 7.2N / 7.3N).

**Typical usage:**
```
$ Direct crack width calculation with 0.3mm limit
CRAC WK 0.3

$ Use per-group values from PARA
CRAC WK PARA

$ Simplified table check
CRAC WK TAB
```

---

### NSTR — SLS Stress Checks

Controls SLS verifications for stress range (fatigue), concrete compression stress, and steel stress limits.

**Syntax:**
```
NSTR SIGS SIGT SIGP CHKC CHKR DECO
```

| Parameter | Type  | Unit      | Default | Description |
|-----------|-------|-----------|---------|-------------|
| `SIGS`    | float | `[N/mm2]` | —       | Allowable stress range for longitudinal reinforcement. Reinforcement increased if exceeded. Use `999` for check only. |
| `SIGT`    | float | `[N/mm2]` | 0.454*SIGS | Allowable stress range for shear reinforcement. Default accounts for small bending diameter. |
| `SIGP`    | float | `[N/mm2]` | —       | Allowable stress range for prestressing steel |
| `CHKC`    | float | `[-]`/`[N/mm2]` | 0 | Max concrete compression: `0.45` = check to 0.45*fck; `0` = no check; `>1.5` = direct value in N/mm2 |
| `CHKR`    | float | `[-]`/`[N/mm2]` | 0 | Max steel stress: `0.8` = check to 0.8*fyk; `0` = no check; `>1.5` = direct value |
| `DECO`    | float | `[mm]`    | —       | Decompression check distance (default 100mm from INI file) |

> Using SIGS, SIGT, CHKR increases reinforcement to satisfy the check.
> Punching shear reinforcement is NOT increased by SIGT.
> Stress range checks require load cases from MAXIMA that represent the with/without traffic load scenarios.

**Typical usage:**
```
$ Fatigue check with 162.5 N/mm2 stress range
NSTR SIGS 162.5

$ Concrete compression stress check
NSTR CHKC 0.45

$ Combined SLS checks
NSTR SIGS 162.5 CHKC 0.45 CHKR 0.8
```

---

### PUNC — Punching Shear Design

Controls punching design at column support nodes per EN 1992-1-1, Ch. 6.4.

**Syntax:**
```
PUNC TYPE X Y Z D B HEAD DHEA RO_V RO_M RO_L LC_P VPD MMOM HRED BETA KPU
```

| Parameter | Type    | Unit   | Default | Description |
|-----------|---------|--------|---------|-------------|
| `TYPE`    | enum    | —      | `YES`   | Punching type (see table below) |
| `X Y Z`   | float  | `[m]`  | —       | Coordinates of punching node (if number not known) |
| `D`       | float   | `[mm]` | from DB | Column or wall thickness (usually from SOFiPLUS) |
| `B`       | float   | `[mm]` | from DB | Column width. B=0 = circular column with diameter D. |
| `HEAD`    | enum    | —      | —       | `CHEK` = only check (no reinforcement increase); `OFF` = exclude this node |
| `DHEA`    | float   | `[mm]` | 0       | Total thickness at enlarged column head |
| `RO_V`    | float   | `[%]`  | 1.5     | Max bending reinforcement ratio from shear. If exceeded, switches to shear links. |
| `RO_M`    | float   | `[%]`  | —       | Max longitudinal reinforcement ratio for punching. If exceeded, punching marked as failed. |
| `RO_L`    | float   | `[%]`  | —       | Minimum longitudinal reinforcement when punching shear links are required |
| `LC_P`    | int     | —      | —       | Load case of max soil pressure (for foundation slabs, TYPE FOUN only) |
| `VPD`     | float   | `[kN]` | —       | Shear force component of tendons |
| `MMOM`    | float   | `[-]`  | 1.0     | Factor on minimum design moments. 0.0 = switch off minimum moments + collapse reinforcement. |
| `HRED`    | float   | `[mm]` | —       | Plate thickness reduction for punching check |
| `BETA`    | float   | `[-]`  | —       | Eccentricity factor override (can only increase, not decrease) |
| `KPU`     | float   | `[-]`  | —       | Factor on VRd,max for stud rails (typically 1.96 per ETA approvals) |

**TYPE — punching type:**

| Value  | Description |
|--------|-------------|
| `NO`   | No punching design |
| `CHEK` | Check only (reinforcement increase only by minimum moment MMOM) |
| `YES`  | Design for column nodes — **default** |
| `COL`  | Same as YES: input for columns |
| `WALL` | Input for wall ends and corners |
| `FOUN` | Input for foundation slabs |
| *int*  | Specific node number for following data |

> Without a node number or coordinates, PUNC data applies to all punching nodes of the given TYPE.
> Individual nodes can be excluded with `PUNC <no> HEAD OFF` or `SELE <no> 0`.
> Collapse reinforcement per EC2 9.4.1(3) is applied automatically (can be switched off with MMOM 0).

**Typical usage:**
```
$ Standard punching design for all column nodes
PUNC YES

$ No punching design
PUNC NO

$ Foundation slab with soil pressure reduction
PUNC FOUN LC_P 1

$ Exclude specific node from punching
PUNC 317 HEAD OFF

$ Stud rails with factor 1.96
PUNC YES KPU 1.96
```

---

### SELE — Selection of Punching Points

Includes or excludes specific nodes from the punching check.

**Syntax:**
```
SELE NO TYPE GRP
```

| Parameter | Type | Unit | Default | Description |
|-----------|------|------|---------|-------------|
| `NO`      | int  | —    | —       | Node number |
| `TYPE`    | int  | —    | 1       | `0` = exclude; `1` = include |
| `GRP`     | int  | —    | —       | Group number (alternative to NO) |

> The first SELE with TYPE 1 switches off all nodes, then switches on only the listed ones.
> `SELE <no> 0` excludes a specific node. `PUNC <no> HEAD OFF` achieves the same.

**Typical usage:**
```
$ Only check node 253
SELE 253

$ Exclude nodes 251 and 255
SELE 251,255 0

$ Exclude all punching nodes from group 3
SELE TYPE 0 GRP 3
```

---

### REIN — Design Case Title

Assigns a title to the stored design case.

**Syntax:**
```
REIN TITL
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `TITL`    | string | —    | —       | Title of the design case (stored with LCR number) |

**Typical usage:**
```
CTRL LCR 7
REIN TITL "ULS envelope all floors"
```

---

## Complete BEMESS Block Examples

### Example 1 — Design parameter definition (separate run)

```
+PROG BEMESS urs:7
HEAD Design parameters for flat slab

!*!Label Default cover and diameters
GEOM HA 35[mm] DHA 10[mm] HB 35[mm] DHB 10[mm]
PARA NOG - DU 10[mm] WKU 0.3[mm] DL 10[mm] WKL 0.3[mm]

!*!Label Group 3: thicker cover (exposure XC4)
GEOM HA 50[mm] DHA 10[mm] HB 50[mm] DHB 10[mm]
PARA NOG 3 DU 12[mm] WKU 0.2[mm] DL 12[mm] WKL 0.2[mm]

END
```

### Example 2 — ULS design with punching

```
+PROG BEMESS urs:8
HEAD ULS design — flat slab

CTRL LCR 1
REIN TITL "ULS design"

LC DESI

PUNC YES

END
```

### Example 3 — SLS crack width check (envelope onto ULS results)

```
+PROG BEMESS urs:9
HEAD SLS crack check — flat slab

CTRL TYPE SLS
CTRL RMOD SUPE
CTRL LCR 1

LC RARE

CRAC WK PARA

END
```

### Example 4 — Combined ULS + SLS in sequence

```
$ --- Step 1: Design parameters ---
+PROG BEMESS urs:7
HEAD Design parameters

GEOM HA 35[mm] DHA 10[mm] HB 35[mm] DHB 10[mm]
PARA NOG - DU 10[mm] WKU 0.3[mm] DL 10[mm] WKL 0.3[mm]

END

$ --- Step 2: ULS bending + shear + punching ---
+PROG BEMESS urs:8
HEAD ULS design

CTRL LCR 1
REIN TITL "ULS + SLS envelope"

LC DESI
PUNC YES

END

$ --- Step 3: SLS crack check (envelope) ---
+PROG BEMESS urs:9
HEAD SLS crack check

CTRL TYPE SLS
CTRL RMOD SUPE
CTRL LCR 1

LC RARE
CRAC WK PARA

END
```

---

## Worked Example — Single-Span Slab with Nonlinear Deflection

The following blocks are part of a complete single-span slab workflow: 6.0 × 2.0 m, t = 260 mm, C30/37, B500A, simply supported on two opposite edges. The workflow covers: (1) define design parameters with base reinforcement, (2) ULS bending + shear design, (3) nonlinear deflection analysis in ASE using the BEMESS reinforcement results.

### Step 1 — Design parameters and base reinforcement

A separate BEMESS run stores the cover, bar diameters, reinforcement directions, and a uniform base reinforcement (d10/150 both layers, both directions) for all groups.

```
+PROG BEMESS urs:7
HEAD Define Reinforcement Layout

!*!Label Section Geometry
GEOM - HA 35[mm] DHA 10[mm] HB 35[mm] DHB 10[mm]

!*!Label Reinforcement Direction
DIRE UPP 0 LOW 0                     $ main direction 0° for both layers

!*!Label Base Reinforcement (d10/150 = 5.24 cm2/m)
PARA NOG - DU 10[mm] ASU 5.24[cm2/m] 5.24[cm2/m] ASL 5.24[cm2/m] 5.24[cm2/m]

END
```

### Step 2 — ULS reinforcement design

The ULS design run uses the pre-combined load case 101 (1.35G + 1.5Q). Punching is set to check-only mode.

```
+PROG BEMESS urs:8
HEAD ULS Reinforcement Design

CTRL LCR 10                           $ store results in design case 10
CTRL RO_V 0.20                        $ max reinforcement ratio for shear

PUNC CHEK RO_V 1.50                   $ punching: check only, no reinforcement increase

LC 101                                 $ ULS combination

END
```

### Step 3 — Nonlinear deflection analysis (in ASE)

After BEMESS has stored the required reinforcement, ASE can perform a full nonlinear layered-shell analysis to compute deflections including cracking, tension stiffening, and creep+shrinkage effects. The `REIQ` command imports the reinforcement from the BEMESS design case into the nonlinear analysis.

```
+PROG ASE urs:10
HEAD Deflection Analysis — Nonlinear Method

SYST PROB NONL NMAT YES ITER 300 TOL -0.5

CREP 1                                 $ activate creep analysis
REIQ LCR 10 FACT 1.0 LCRS 91          $ import reinforcement from BEMESS design case 10

$ Creep and shrinkage parameters
GRP - PHI 2.0 EPS -0.0004             $ phi=2.0, eps_cs=0.4 permille

LC 311 FACD 1.0 TITL "NONL: 1.0G + 0.3Q"
  LCC 211                             $ copy quasi-permanent combination

END
```

> This nonlinear ASE approach serves as a reference solution for slab deflections. It uses layered shell elements with material nonlinearity (`NMAT YES`) and applies creep (`PHI`) and shrinkage (`EPS`) via `GRP`.
> `REIQ LCR 10` reads the BEMESS reinforcement from design case 10 and applies it to the nonlinear analysis.
> `CREP 1` activates the creep law for the time-dependent analysis.

---

## Unit Summary for BEMESS

| Quantity | Unit | Parameters |
|----------|------|------------|
| Cover distances | `[mm]` | `HA`/`DHA`/`HB`/`DHB` on `GEOM` |
| Plate thickness | `[mm]` | `H` on `GEOM`; `HRED`/`DHEA` on `PUNC` |
| Bar diameter | `[mm]` | `DU`/`DL` etc. on `PARA`; `D` on `LAY` |
| Crack width | `[mm]` | `WKU`/`WKL` on `PARA`; `WK` on `CRAC` |
| Reinforcement area | `[cm2/m]` | `ASU`/`ASL` on `PARA`; `AS` on `LAY` |
| Stress | `[N/mm2]` | `SIGS`/`SIGT`/`CHKC`/`CHKR` on `NSTR`; `SSU`/`SSL` on `PARA` |
| Column dimensions | `[mm]` | `D`/`B` on `PUNC` |
| Coordinates | `[m]` | `X`/`Y`/`Z` on `PUNC` |
| Shear force | `[kN]` | `VPD` on `PUNC` |
| Decompression distance | `[mm]` | `DECO` on `NSTR` |
| Reinforcement ratio | `[%]` | `RO_V`/`RO_M`/`RO_L` on `PUNC`/`CTRL` |
