# Module: SOFILOAD — Actions and Load Cases

## Purpose
SOFILOAD defines action types (permanent, variable, etc.), opens load cases, and applies geometry-referenced loads to the structural model via POIN, LINE, AREA, and VOLU records. It also handles self-weight via gravity factors on the LC record, load copying and combination scaling via COPY, load take-down redistribution via LTD, and tributary area distribution via TRB. Element-level loads (BEAM, QUAD, etc.), wind, traffic, and dynamic/seismic commands are documented in separate sub-files.

## Load this file when
The user needs to define action types (ACT), open load cases (LC), apply geometry-referenced loads (POIN/LINE/AREA/VOLU), copy and scale loads between load cases (COPY), or use load take-down (LTD) or tributary areas (TRB).

## Module block template
```
+PROG SOFILOAD urs:5

HEAD Loads - ULS and SLS

$ --- Define action types ---
ACT TYPE G TITL 'Self-weight'
ACT TYPE G_2 TITL 'Superimposed dead load'
ACT TYPE Q PSI0 0.7  PSI1 0.5  PSI2 0.3 TITL 'Live load'

$ --- Load case 1: self-weight (gravity via FACD) ---
LC 1 TYPE G FACD 1.0 TITL 'G - Self-weight'

$ --- Load case 2: area load via geometry polygon ---
LC 2 TYPE G_2 TITL 'G2 - Superimposed dead load'
  AREA REF AUTO TYPE PZP $$
     P1 -1.5 X1 0.0 Y1 0.0 Z1 0.0 $$
     P2 -1.5 X2 6.0 Y2 0.0 Z2 0.0 $$
     P3 -1.5 X3 6.0 Y3 5.0 Z3 0.0 $$
     P4 -1.5 X4 0.0 Y4 5.0 Z4 0.0

END
```

> `+PROG SOFILOAD urs:<n>` — the `urs` run number must be unique in the `.dat` file and greater than any SOFIMSHC urs number.
> All loads defined below an `LC` record belong to that load case until the next `LC` record or `END`.
> Actions (ACT) must be defined before they are referenced by LC TYPE.
> Self-weight is activated by setting DLX/DLY/DLZ on the LC record.
> SOFILOAD runs after SOFIMSHC (mesh generation) and before ASE (analysis).

---

## Commands

| Command | Purpose |
|---------|---------|
| `HEAD`  | Module title line stored in the database |
| `ECHO`  | Control output verbosity per category |
| `CTRL`  | Module-level control flags and tolerances |
| `GRP`   | Override group properties for load generation |
| `ACT`   | Define an action type with safety and combination factors |
| `LC`    | Open a load case — all load records below apply to it |
| `POIN`  | Geometry-referenced point load at a coordinate |
| `LINE`  | Geometry-referenced line load along a path |
| `AREA`  | Geometry-referenced area load over a polygon |
| `VOLU`  | Geometry-referenced volume load in a region |
| `LAR`   | Define a named load area for reference by AREA/LINE |
| `COPY`  | Copy loads from existing load cases with optional scaling |
| `LTD`   | Load take-down: transfer reactions as loads to a sub-model |
| `LTDG`  | Geometry polygon for LTD selection |
| `GUID`  | Geometric guide line for LTD matching |
| `TRB`   | Define a tributary area for load distribution |
| `TRBA`  | Add a four-point polygon to a tributary area |
| `TRBS`  | Add supports (beams) to a tributary area |
| `END`   | End of SOFILOAD program block |

---

### HEAD — Module Title

One-sentence description: stores a descriptive title in the database for the current SOFILOAD run.

**Syntax:**
```
HEAD text
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `text`    | string | —    | —       | Free text title, up to 70 characters |

**Typical usage:**
```
HEAD Wind and Live Loads - SLS
```

---

### ECHO — Output Verbosity Control

Controls which categories of input and output are printed to the report.

**Syntax:**
```
ECHO OPT VAL
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `OPT`     | enum   | —    | —       | Output category to control |
| `VAL`     | enum   | —    | YES     | Verbosity level |

**OPT — category:**

| Value  | Meaning |
|--------|---------|
| `FULL` | All output categories |
| `ACT`  | Action type records |
| `LOAD` | Load records |
| `LANE` | Lane/traffic records |
| `FUNC` | Time function records |
| `WIND` | Wind generation output |
| `LC`   | Load case headers |
| `STAT` | Statistics summary |
| `COPY` | COPY command output |
| `LTD`  | Load take-down output |
| `TAG`  | Loads with tag markers |
| `TRB`  | Tributary area output |

**VAL — level:**

| Value  | Meaning |
|--------|---------|
| `OFF`  | Suppress output for this category |
| `NO`   | Suppress (same as OFF) |
| `YES`  | Normal output (default) |
| `FULL` | Extended output |
| `EXTR` | Extreme detail |

**Typical usage:**
```
ECHO LOAD YES
ECHO STAT FULL
```

---

### CTRL — Module Control Flags

Sets tolerances and global behavior switches for the load generator.

**Syntax:**
```
CTRL OPT VAL V2 V3 V4 V5 V6
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `OPT`     | enum   | —    | —       | Control option keyword |
| `VAL`     | float  | —    | *       | Primary value for the option |
| `V2`–`V6` | float  | —    | *       | Additional values (option-dependent) |

**OPT — control options (most common):**

| Value  | Meaning |
|--------|---------|
| `COMP` | Compatibility mode (version number) |
| `TOLG` | Geometric tolerance for element search |
| `TOLS` | Station tolerance for beam load positioning |
| `DIST` | Distance tolerance for free-load projection |
| `SDIV` | Subdivisions for load integration |
| `WIND` | Wind load generation flags |
| `COPY` | COPY command behavior flags (bit mask) |
| `SUML` | Print load resultant summary |
| `LAR`  | Load area behavior flags |
| `GTOL` | Global search tolerance |
| `STOL` | Station tolerance |
| `TRBD` | Tributary area debug flags |
| `TRBS` | Tributary area stiffness factor |

> Defaults are program-internal; only override when specifically needed.
> `CTRL COPY 256` enables recursive copying of free loads (use with caution — see warning 171).

**Typical usage:**
```
CTRL TOLG 0.01   $ geometric search tolerance 10mm
CTRL SDIV 4      $ 4 integration points per element
```

---

### GRP — Group Properties for Load Generation

Overrides wind and wave properties for a specific element group.

**Syntax:**
```
GRP NO VAL CS WIND CW CFR WAVE
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `NO`      | int    | —    | —       | Group number |
| `VAL`     | float  | [-]  | *       | Load factor for self-weight |
| `CS`      | int    | —    | *       | Cross-section number override |
| `WIND`    | enum   | —    | *       | Wind load mode for this group |
| `CW`      | float  | [-]  | *       | Wind drag coefficient |
| `CFR`     | float  | [-]  | *       | Friction coefficient |
| `WAVE`    | float  | [-]  | *       | Wave load coefficient |

**WIND — wind mode:**

| Value  | Meaning |
|--------|---------|
| `OFF`  | Suppress wind loading on this group |
| `YES`  | Apply wind loading (default) |
| `FULL` | Full detailed wind analysis |

**Typical usage:**
```
GRP 1 WIND OFF   $ no wind on group 1
GRP 2 CW 1.3     $ override drag coefficient for group 2
```

---

### ACT — Define an Action Type

Defines an action with its safety and combination factors. Addressing an action reinitialises it with defaults from the design-code INI-file; values GAMU through PS1S override those defaults. With the specification of ACT all subsequent load cases in SOFILOAD will have this action type as default.

As type of the action one may use any literal with up to 4 characters, however some combinations are reserved for special purpose defined in the corresponding INI-files following the designation of the selected design code. Furthermore, each action can be subdivided into categories by appending an underscore and a character from A–Z (e.g. `Q_B`). Each category has its own combination values and load cases, but selecting the generic name (e.g. `Q`) also selects all its categories.

**Syntax:**
```
ACT TYPE
    GAMU GAMF PSI0 PSI1 PSI2 PS1S GAMA
    PART SUP
    TITL text
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `TYPE`    | lit4   | —     | !       | Designation of action or of its category (required) |
| `GAMU`    | float  | [-]   | *       | Unfavourable partial safety factor γ_u |
| `GAMF`    | float  | [-]   | *       | Favourable partial safety factor γ_f |
| `PSI0`    | float  | [-]   | *       | Combination coefficient rare ψ₀ |
| `PSI1`    | float  | [-]   | *       | Combination coefficient frequent ψ₁ |
| `PSI2`    | float  | [-]   | *       | Combination coefficient quasi-permanent ψ₂ |
| `PS1S`    | float  | [-]   | *       | Combination coefficient infrequent ψ₁,infq |
| `GAMA`    | float  | [-]   | *       | Partial safety factor accidental γ_a |
| `PART`    | lit    | —     | *       | Partition of the action group (see table below) |
| `SUP`     | lit    | —     | *       | Handling of load cases within the action (see table below) |
| `TITL`    | lit24  | —     | *       | Designation of action |

**Standard action type designations:**

| Type | Description |
|------|-------------|
| `G`, `G_1`, `G_2` | Dead load (primary / secondary) |
| `P`, `C`    | Prestress; creep and shrinkage |
| `Q`, `Q_A`…`Q_H` | Variable payload for buildings (categories A–H per EN 1990) |
| `L`, `L_T`, `L_U` | Live (traffic) loads; tandem axle / UDL for bridges |
| `W`, `ZW`   | Wind (use ZW for bridges) |
| `S`, `S_L`, `S_H` | Snow (low / high elevation) |
| `R`         | Earth pressure, water pressure |
| `F`         | Settlements |
| `T`         | Temperature |
| `A`         | Accidental |
| `B`         | Construction, maintenance |
| `E`, `ZE`, `SE` | Seismic (service / design) |
| `NONE`, `-` | For LC only: not assigned to an action |

> The actions in the table are used only as preset actions, provided they are available in the INI-file of the selected design code. The user should verify the defaults in all cases. Deviations of the PSI-values for wind and temperature are especially expected for bridges and other non-building structures as all values are "boxed values".
> If the design code NORM or its category CAT is changed in AQUA, all actions should be redefined. `ACT INIT` deletes all defined actions and superposition rules in SOFILOAD.

**PART — action group:**

| Value     | Meaning |
|-----------|---------|
| `G`       | Permanent action group (e.g. dead load) |
| `P`       | Action group for prestress and creep |
| `Q`       | Variable action group |
| `Q_1`…`Q_99` | Variable action load groups 1–99 (mutually exclusive within an action) |
| `A`       | Accidental action group |
| `E`       | Seismic action group |

PART must be specified for user-defined actions; otherwise PART Q is used as default. All categories of one action must share the same PART value; only load groups Q_1…Q_99 of a variable action may differ.

**SUP — superposition rule for load cases within the action:**

| Value  | Meaning |
|--------|---------|
| `PERM` | Permanent with uniform factor — one partial safety factor for the entire action |
| `PERC` | Permanent with individual factors — partial safety factor evaluated load-case-wise |
| `COND` | Conditional (only if unfavourable) |
| `EXCL` | Mutually exclusive within category |
| `EXEX` | Mutually exclusive within the entire action (inclusive categories) |
| `UNSI` | Conditional with changing sign (e.g. seismic) |
| `USEX` | EXCL with changing sign |
| `ALEX` | Permanent but exclusive within action (always one load case used) |

The default SUP is derived from the type designation: actions beginning with `G` → PERM, beginning with `Q` → COND, others → EXCL.

**Typical usage:**
```
!*! Standard building action definitions
ACT TYPE G TITL 'Self-weight'

ACT TYPE G_2 TITL 'Superimposed dead load'

ACT TYPE Q TITL 'Office live load'

ACT TYPE W TITL 'Wind'

$ User-defined action with explicit PART and SUP
ACT TYPE 'MY_A'  GAMU 1.4  PSI0 0.6  PSI1 0.4  PSI2 0.2  PART Q_1  SUP EXCL TITL 'Special load group A'
```

---

### LC — Open a Load Case

Defines or selects a load case for further treatment. All load records following an `LC` record belong to that load case until the next `LC` or `END`. Only predefined or explicitly defined actions (see ACT) may be used for TYPE.

**Syntax:**
```
LC NO TYPE FACT FACD DLX DLY DLZ
   GAMU GAMF PSI0 PSI1 PSI2 PS1S GAMA
   CRIT CRI1 CRI2 CRI3
   TITL text
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `NO`      | int    | —     | 0       | Number of load case |
| `TYPE`    | lit4   | —     | *       | Type / action of load case |
| `FACT`    | float  | [-]   | 1.0     | Factor of load case |
| `FACD`    | float  | [-]   | 0.0     | Factor of structural dead weight |
| `DLX`     | float  | [-]   | *       | Component of dead weight in X-direction |
| `DLY`     | float  | [-]   | *       | Component of dead weight in Y-direction |
| `DLZ`     | float  | [-]   | *       | Component of dead weight in Z-direction |
| `GAMU`    | float  | [-]   | *       | Unfavourable safety factor (overrides action default) |
| `GAMF`    | float  | [-]   | *       | Favourable safety factor (overrides action default) |
| `PSI0`    | float  | [-]   | *       | Combination coefficient standard (overrides action default) |
| `PSI1`    | float  | [-]   | *       | Combination coefficient frequent (overrides action default) |
| `PSI2`    | float  | [-]   | *       | Combination coefficient quasi-permanent (overrides action default) |
| `PS1S`    | float  | [-]   | *       | Combination coefficient non-frequent (overrides action default) |
| `GAMA`    | float  | [-]   | *       | Safety factor accidental (overrides action default) |
| `CRIT`    | float  | [sec] | 0       | Time criteria |
| `CRI1`    | float  | [-]   | 0       | User criteria I (free parameter, e.g. strength reduction) |
| `CRI2`    | float  | [-]   | 0       | User criteria II |
| `CRI3`    | float  | [-]   | 0       | User criteria III |
| `TITL`    | lit32  | —     | —       | Title of load case |

**Levels of operation:** There are distinct levels at which SOFILOAD processes an LC record:

- **Modify action parameters** — If no load case number is given, the safety factors and combination coefficients of the action TYPE are redefined without creating or modifying a load case.
- **Modify load case parameters** — Values TYPE, FACT, CRIT–CRI3, and TITL may be changed for an existing load case. No dead-load factors or other loading may be defined in this mode.
- **Load generation (REST)** — Via load type REST all generated loading will be deleted and re-established from the load generators. For a load case containing COPY commands, all loads are deleted and all COPY commands are repeated.
- **Explicit definition** — If dead-weight factors or any other loading is defined after the LC record, all previous loads for that load case are deleted and the load case is redefined from scratch.
- **Explicit deletion** — Specifying TYPE DEL immediately deletes the load case and all its data.

**Notes on FACT:** The factor FACT has no specific influence during SOFILOAD input (except for the wind load generator) and may be changed at any time. Loads are multiplied by FACT only when used in the analysis itself. FACT affects all forces and moments but **not** temperature, strain, or prestress loads, and also **not** the dead-weight factors FACD, DLX, DLY, or DLZ.

**Notes on dead weight:** The components DLX, DLY, DLZ act in the positive direction of the respective global axis — enter the correct sign. Specifying only FACD applies dead weight in the gravity direction defined for the system. Defining any dead-weight factor automatically deletes all previously defined loads for this load case.

**TYPE — special values:**

| Value  | Meaning |
|--------|---------|
| `DEL`  | Delete this load case immediately |
| `REST` | Regenerate all generated loads from source generators |
| `IMP`  | Imperfection load case (for second-order theory combinations) |
| `EINF` | Influence line load case |

**Parenthesised TYPE for pre-combined load cases:**

When a load case is built manually via `COPY` (i.e. a user-assembled combination rather than an action-based primary load case), the result-type literal **must be enclosed in parentheses** to distinguish it from an action name reference. The parentheses tell SOFiSTiK that this load case is a pre-combined result, not a reference to an `ACT` definition.

| Syntax | Meaning |
|--------|---------|
| `LC 101 TYPE Q ...` | Primary load case belonging to action Q |
| `LC 101 TYPE (D) ...` | Pre-combined ULS design combination |
| `LC 201 TYPE (R) ...` | Pre-combined SLS rare combination |

The parenthesised TYPE controls how downstream modules (MAXIMA, AQB, BEMESS) interpret the load case — for example, `(D)` triggers ULS design checks, `(R)` triggers SLS stress checks, `(P)` triggers long-term deflection checks, and `(F)` triggers crack width checks.

**Result-type literals for pre-combined load cases:**

| TYPE literal | Combination type | Typical use |
|-------------|-----------------|-------------|
| `(D)`  | Ultimate design (fundamental) | ULS bending, shear, capacity checks |
| `(A)`  | Ultimate accidental | Accidental design situations |
| `(E)`  | Ultimate earthquake | Seismic design combinations |
| `(R)`  | Service: rare (characteristic) | SLS stress limitation |
| `(N)`  | Service: non-frequent | SLS checks per EC1-3 |
| `(F)`  | Service: frequent | SLS crack width verification |
| `(P)`  | Service: quasi-permanent | SLS deflection, long-term effects |
| `(H)`  | Principal loading | Superposition of principal loads |
| `(HZ)` | Principal + supplemental | Extended superposition |
| `(PT)` | Permanent (timber) | Timber permanent load duration |
| `(LT)` | Long-term (timber) | Timber long-term load duration |
| `(MT)` | Medium-term (timber) | Timber medium-term load duration |
| `(ST)` | Short-term (timber) | Timber short-term load duration |
| `(VT)` | Very short-term (timber) | Timber instantaneous load duration |

**Typical usage of parenthesised TYPE:**
```
$ ULS fundamental combination with explicit factors
LC 101 TYPE (D) TITL 'ULS 6.10 — G + Q full'
  COPY NO 1  FACT 1.35    $ G  self-weight
  COPY NO 2  FACT 1.35    $ G2 superimposed dead
  COPY NO 11 FACT 1.50    $ Q  live load (leading)

$ SLS rare (characteristic) combination
LC 201 TYPE (R) TITL 'SLS rare — G + Q'
  COPY NO 1  FACT 1.00
  COPY NO 2  FACT 1.00
  COPY NO 11 FACT 1.00

$ SLS frequent combination using PSI1 literal
LC 211 TYPE (F) TITL 'SLS frequent — G + psi1*Q'
  COPY NO 1  FACT 1.00
  COPY NO 2  FACT 1.00
  COPY NO 11 FACT PSI1

$ SLS quasi-permanent combination
LC 301 TYPE (P) TITL 'SLS quasi-perm — G + psi2*Q'
  COPY NO 1  FACT 1.00
  COPY NO 2  FACT 1.00
  COPY NO 11 FACT PSI2

$ Timber short-term combination
LC 401 TYPE (ST) TITL 'Timber ST — G + Q snow'
  COPY NO 1  FACT 1.00
  COPY NO 2  FACT 1.00
  COPY NO 4  FACT 1.00
```

> Values GAMU to PS1S belong to the action TYPE in general but may be given individual values per load case. Starting with version 2010, only explicitly specified values are stored per load case; all other values adopt to those of the action when the action is changed.
> CRI1–CRI3 are free parameters usable for postprocessing via DBVIEW (e.g. a system dimension or a strength reduction). TALPA uses CRI1 for the Fellenius safety factor.

**Typical usage:**
```
!*! Load cases
LC 1 TYPE G FACD 1.0 TITL 'G - Self-weight'

LC 2 TYPE G_2 TITL 'G2 - Superimposed dead load'
AREA REF AUTO TYPE PZP $$
     P1 -1.5 X1 0.0 Y1 0.0 Z1 0.0 $$
     P2 -1.5 X2 6.0 Y2 0.0 Z2 0.0 $$
     P3 -1.5 X3 6.0 Y3 5.0 Z3 0.0 $$
     P4 -1.5 X4 0.0 Y4 5.0 Z4 0.0

LC 11 TYPE Q TITL 'Q1 - Office live load'
AREA REF AUTO TYPE PZP $$
     P1 -3.0 X1 0.0 Y1 0.0 Z1 0.0 $$
     P2 -3.0 X2 6.0 Y2 0.0 Z2 0.0 $$
     P3 -3.0 X3 6.0 Y3 5.0 Z3 0.0 $$
     P4 -3.0 X4 0.0 Y4 5.0 Z4 0.0
```

---

### POIN — Free Point Load

Applies a single point load (or similar load type) at a specified coordinate, independent from the element mesh. The program searches for the points, lines, or regions where to apply the load according to the REF type.

POIN loads are not singular loads with a stress singularity at the tip, but energetically equivalent loads in the vicinity of a mesh node. If the mesh is refined under a POIN load, singularities become more visible. As the transverse loading of a plate or shell may always be spread to the mid-surface, the following rule applies: **POIN loads may be used without concerns if the element size is larger than the plate thickness. Below that size, all loading must be defined as areal loading with true dimensions.**

If the reference is NODE with an explicit number, the default coordinates are those of that node, and eccentricities generate moments at the node. For REF SLN/BGRP, eccentricities are copied to beam loading or transformed to moments. For REF SAR/QGRP, the load is always converted to up to four nodal loads without eccentricities.

**Syntax:**
```
POIN REF NO TITL PROJ WIDE NREF TYPE P X Y Z
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `REF`     | lit    | —     | AUTO    | Reference type for load projection |
| `NO`      | int    | —     | —       | Reference or group number |
| `TITL`    | lit12  | —     | —       | Short title of loading |
| `PROJ`    | lit    | —     | N       | Projection of load point |
| `WIDE`    | float  | [m]   | 0.0     | Range in direction of projection (only if specific PROJ selected) |
| `NREF`    | int    | —     | —       | Reference node for coordinate values |
| `TYPE`    | lit    | —     | PG      | Load type and direction |
| `P`       | float  | *     | 0.      | Load value |
| `X`       | float  | [m]   | 0.      | Global X coordinate of loading |
| `Y`       | float  | [m]   | 0.      | Global Y coordinate of loading |
| `Z`       | float  | [m]   | 0.      | Global Z coordinate of loading |

**REF — reference type:**

| Value  | Meaning |
|--------|---------|
| `AUTO` | Automatic — program searches points, lines, then areas |
| `MOVE` | Automatic moving load |
| `LAR`  | Load distribution area |
| `SLN`  | Structural line |
| `SAR`  | Structural area |
| `GFA`  | Surface number of BRICs |
| `NODE` | Generated node |
| `BGRP` | Group of beam / cable / truss elements |
| `QGRP` | Group of QUAD elements |
| `VGRP` | Group of BRIC elements |

**PROJ — projection direction of load point:**

| Value  | Meaning |
|--------|---------|
| `N`    | Normal of reference area (SAR) |
| `XX`   | Projection in global X-direction |
| `YY`   | Projection in global Y-direction |
| `ZZ`   | Projection in global Z-direction |

**TYPE — forces and moments:**

| TYPE | Description | Unit |
|------|-------------|------|
| `PG`  | Load in gravity direction (not: self-weight loading) | [kN] |
| `PX`  | Load in local x-direction | [kN] |
| `PY`  | Load in local y-direction (note: local system depends on REF) | [kN] |
| `PZ`  | Load in local z-direction | [kN] |
| `PXX` | Load in global X-direction | [kN] |
| `PYY` | Load in global Y-direction | [kN] |
| `PZZ` | Load in global Z-direction | [kN] |
| `MX`  | Moment about local x-direction | [kNm] |
| `MY`  | Moment about local y-direction | [kNm] |
| `MZ`  | Moment about local z-direction | [kNm] |
| `MXX` | Moment about global X-direction | [kNm] |
| `MYY` | Moment about global Y-direction | [kNm] |
| `MZZ` | Moment about global Z-direction | [kNm] |
| `MB`  | Warping moment (only for REF SPT/SLN) | [kNm²] |

**TYPE — support displacements (only for REF GPT/NODE):**

| TYPE | Description | Unit |
|------|-------------|------|
| `WXX` | Displacement in global X-direction | [mm] |
| `WYY` | Displacement in global Y-direction | [mm] |
| `WZZ` | Displacement in global Z-direction | [mm] |
| `DXX` | Rotational displacement about global X | [mrad] |
| `DYY` | Rotational displacement about global Y | [mrad] |
| `DZZ` | Rotational displacement about global Z | [mrad] |

Support displacements in local directions are not possible.

**TYPE — influence values for beam elements (for REF SLN/BGRP):**

| TYPE | Description | Unit |
|------|-------------|------|
| `WX` | Jump of displacement in local x-direction | [mm] |
| `WY` | Jump of displacement in local y-direction | [mm] |
| `WZ` | Jump of displacement in local z-direction | [mm] |
| `DX` | Bend of displacement about local x-direction | [mrad] |
| `DY` | Bend of displacement about local y-direction | [mrad] |
| `DZ` | Bend of displacement about local z-direction | [mrad] |

**TYPE — influence values for QUAD elements (for REF SAR/QGRP):**

| TYPE  | Description | Unit |
|-------|-------------|------|
| `IMXX` | Influence area for moment m-xx | [-] |
| `IMYY` | Influence area for moment m-yy | [-] |
| `IMXY` | Influence area for moment m-xy | [-] |
| `IVX`  | Influence area for shear v-xx | [-] |
| `IVY`  | Influence area for shear v-yy | [-] |
| `INXX` | Influence area for membrane force n-xx | [-] |
| `INYY` | Influence area for membrane force n-yy | [-] |
| `INXY` | Influence area for membrane force n-xy | [-] |

> For the influence area types, the loading generates a Dirac-delta strain in the element centre. Set P to 1.0; the resulting deformation field is the required influence area. Directly at the point of interest, the FE approach will smooth out the theoretical singularity. If several elements qualify, the one with the lowest number is loaded.

**Typical usage:**
```
$ 100 kN downward at X=5, Y=3 — automatic projection to nearest node
POIN REF AUTO TYPE PZZ P -100.0 X 5.0 Y 3.0 Z 0.0

$ Point load on specific structural line
POIN REF SLN NO 5 TYPE PZZ P -50.0 X 3.0 Y 0.0 Z 0.0

$ Prescribed nodal settlement
POIN REF NODE NO 101 TYPE WZZ P -5.0  $ 5 mm settlement at node 101
```

---

### LINE — Free Line Loading

LINE and CURV describe a polygon or a smooth curved line load applied independent from the element mesh. The load can follow a sequence of elements (LINE without geometry), a mesh-independent polygon (LINE with geometry), or a mesh-independent curve (CURV with geometry). Distribution of load values may be explicit or obtained from a spline along the defined load direction.

If the reference SLN, EDG, or BGRP is used with an explicit number NO, coordinates may be omitted — the load is then uniform along the whole line. If a SLN has been subdivided only partially with beam elements, the load is applied only on those generated beams. To load the total line, either define coordinates explicitly or use REF EDG to generate nodal loads.

It is possible to define up to 63 load points. As only 6 are allowed per record, additional points must be specified in continuation records with TYPE CONT. When using CONT, none of the records must contain generation or list expressions.

Beam loadings may be applied at or relative to a specific point within the cross-section by appending a string to NO, e.g. `@Z+` for the lower edge, `@Y-` for the left edge, `@Y+Z+` for a corner, or `@NAME` for a named stress point or polygon vertex.

**Syntax:**
```
LINE REF NO TITL PROJ WIDE NREF TYPE
     P1 X1 Y1 Z1  [P2 X2 Y2 Z2]  ...  [P6 X6 Y6 Z6]
     [TYPE CONT P1 ... P6]   $ continuation for points 7–12, etc.
```

| Parameter  | Type   | Unit  | Default | Description |
|------------|--------|-------|---------|-------------|
| `REF`      | lit    | —     | AUTO    | Reference type |
| `NO`       | int    | —     | —       | Reference or group number |
| `TITL`     | lit12  | —     | —       | Short title of loading |
| `PROJ`     | lit    | —     | N       | Projection of loading line |
| `WIDE`     | float  | [m]   | 0.0     | Range in direction of projection (only if specific PROJ selected) |
| `NREF`     | int    | —     | —       | Reference node for coordinate values |
| `TYPE`     | lit    | —     | PG      | Load type and direction |
| `P1`–`P6`  | float  | *     | 0.      | Load value at each point |
| `X1`–`Z1`  | float  | [m]   | 0.      | Coordinates of first point (or SPT for X1, point number for Y1, or S/SX + ordinate for SLN) |
| `X6`–`Z6`  | float  | [m]   | X5/Y5/Z5 | Coordinates of sixth point |

**REF — reference type:**

| Value  | Meaning |
|--------|---------|
| `AUTO` | Automatic |
| `MOVE` | Automatic moving load |
| `LAR`  | Load distribution area |
| `SLN`  | Structural line |
| `SAR`  | Structural area |
| `GFA`  | Surface number of BRICs |
| `EDG`  | Nodal sequence (polygonal geometry) |
| `BGRP` | Group of beam / cable / truss elements |
| `QGRP` | Group of QUAD elements |
| `VGRP` | Group of BRIC elements |

**PROJ — projection of loading line:**

| Value  | Meaning |
|--------|---------|
| `N`    | Normal of reference area (SAR) |
| `XX`   | Projection in global X-direction |
| `YY`   | Projection in global Y-direction |
| `ZZ`   | Projection in global Z-direction |
| `XXL`  | As XX, with sign for local component |
| `YYL`  | As YY, with sign for local component |
| `ZZL`  | As ZZ, with sign for local component |
| `LOAD` | As N, without eccentricities |

**TYPE — most common load types:**

| TYPE   | Description | Unit |
|--------|-------------|------|
| `PG`   | Load in gravity direction | [-] |
| `PX`   | Load in local x-direction | [kN/m] |
| `PY`   | Load in local y-direction | [kN/m] |
| `PZ`   | Load in local z-direction | [kN/m] |
| `PXX`  | Load in global X-direction | [kN/m] |
| `PYY`  | Load in global Y-direction | [kN/m] |
| `PZZ`  | Load in global Z-direction | [kN/m] |
| `PXP`  | Load in global X referenced on projected length | [kN/m] |
| `PYP`  | Load in global Y referenced on projected length | [kN/m] |
| `PZP`  | Load in global Z referenced on projected length | [kN/m] |
| `MX`   | Moment about local x | [kNm/m] |
| `MY`   | Moment about local y | [kNm/m] |
| `MZ`   | Moment about local z | [kNm/m] |
| `MXX`  | Moment about global X | [kNm/m] |
| `MYY`  | Moment about global Y | [kNm/m] |
| `MZZ`  | Moment about global Z | [kNm/m] |
| `MB`   | Warping bimoment | [kNm²/m] |
| `CONT` | Continuation record (points 7–12, 13–18, …) | — |

**Typical usage:**
```
$ Uniform 10 kN/m edge load along Y=0
LINE REF AUTO TYPE PZZ $$
     P1 -10.0 X1 0.0  Y1 0.0 Z1 0.0 $$
     P2 -10.0 X2 12.0 Y2 0.0 Z2 0.0

$ Linearly varying line load (8 → 12 kN/m)
LINE REF AUTO TYPE PZZ $$
     P1 -8.0  X1 0.0  Y1 0.0  Z1 3.0 $$
     P2 -12.0 X2 0.0  Y2 10.0 Z2 3.0 $$

$ Uniform load on entire structural line 5 (no coordinates needed)
LINE REF SLN NO 5 TYPE PZZ P1 -5.0 $$

$ More than 6 points using continuation records
LINE REF SLN NO 1 TYPE PX P1 1.0 X1 0. Y1 0. Z1 0.  P2 2.0 X2 1. Y2 0. Z2 0.  $ points 1–2 (abbreviated)
                  TYPE CONT P1 3.0 X1 2. Y1 0. Z1 0.                             $ point 3 onwards
```

---

### AREA — Free Area Loading

AREA describes general polygon loading areas applied independent from the element mesh. The load does not need to be specified in all points; missing values are interpolated with a least-squares distribution accounting for the projection definition. Up to four suitably placed points yield a bilinear (4-coefficient) distribution; more points allow quadratic (6 coefficients) or bicubic (10 coefficients) distributions, but sufficient points must be defined in at least two directions.

If a constant load on all elements of an area is required, define only the reference number NO and the load value P1 with REF SAR/LAR/QGRP/TRB — all coordinates may be omitted. Kinks in load values must be modelled via separate load areas.

It is possible to define up to 63 corner points. As only 6 are allowed per record, additional points are specified in continuation records with TYPE CONT. When using CONT, none of the records must contain generation or list expressions.

For load areas from the 2nd point onward, entering one of `DXY`, `DYZ`, or `DZX` for the X-value interprets the remaining two coordinates as increments from the first point. Defining only two points with this shorthand creates a rectangle in the corresponding coordinate plane.

Loading on beam elements is best done via load distribution areas (LAR) or real QUAD elements. If neither is present, SOFILOAD establishes a main girder direction and distributes the load transversely onto beams fully or partially within the loading area. Moment loading is not considered when using REF LAR.

For projection rules: explicit references to an area are always unique. Without a number, all areas are checked — only those where the load falls completely within the element volume are used. For SAR with PROJ N, all interpolations occur on the (possibly curved) surface; load points should lie on that surface. For global projections the loading area may be situated some distance away from the real structure. For automatic references, the program first searches load distribution areas, then QUAD elements and structural areas, and finally beam elements.

**Syntax:**
```
AREA REF NO TITL PROJ WIDE NREF TYPE
     P1 X1 Y1 Z1  [P2 X2 Y2 Z2]  ...  [P6 X6 Y6 Z6]
     [TYPE CONT P1 ... P6]   $ continuation for points 7–12, etc.
```

| Parameter  | Type   | Unit  | Default | Description |
|------------|--------|-------|---------|-------------|
| `REF`      | lit    | —     | AUTO    | Reference type |
| `NO`       | int    | —     | —       | Reference or group number |
| `TITL`     | lit12  | —     | —       | Short title or ident of loading |
| `PROJ`     | lit    | —     | N       | Projection of loading area |
| `WIDE`     | float  | [m]   | 0.0     | Range in direction of projection (only if specific PROJ selected) |
| `NREF`     | int    | —     | —       | Reference node for coordinate values |
| `TYPE`     | lit    | —     | PG      | Load type and direction |
| `P1`–`P6`  | float  | *     | 0.      | Load value at each corner point |
| `X1`–`Z1`  | float  | [m]   | 0.      | Coordinates of first corner (or GPT for X1, point number for Y1) |
| `X6`–`Z6`  | float  | [m]   | X5/Y5/Z5 | Coordinates of sixth corner |

**REF — reference type:**

| Value  | Meaning |
|--------|---------|
| `AUTO` | Automatic |
| `MOVE` | Automatic moving load |
| `LAR`  | Load distribution area (stiffness-based) |
| `TRB`  | Tributary area (geometrical) |
| `SAR`  | Structural area |
| `GFA`  | Surface number of BRICs |
| `BGRP` | Group of beam elements |
| `QGRP` | Group of QUAD elements |
| `VGRP` | Group of BRIC elements |

**PROJ — projection of loading area:**

| Value  | Meaning |
|--------|---------|
| `N`    | Normal of reference area (SAR) |
| `XX`   | Projection in global X-direction |
| `YY`   | Projection in global Y-direction |
| `ZZ`   | Projection in global Z-direction |
| `XXL`  | As XX, with sign for local component |
| `YYL`  | As YY, with sign for local component |
| `ZZL`  | As ZZ, with sign for local component |
| `LOAD` | As N, without eccentricities |

**TYPE — full list of area load types:**

| TYPE   | Description | Unit |
|--------|-------------|------|
| `WIND` | Wind loading factor | [-] |
| `PCFD` | Pressure and wall shear stress from flow analysis (see CTRL CFDL) | [-] |
| `SNOW` | Snow load shape factor | [-] |
| `PG`   | Loading in gravity direction | [kN/m²] |
| `PX`   | Loading in local x-direction (load value per element area) | [kN/m²] |
| `PY`   | Loading in local y-direction | [kN/m²] |
| `PZ`   | Loading in local z-direction | [kN/m²] |
| `PXX`  | Loading in global X-direction (per element area) | [kN/m²] |
| `PYY`  | Loading in global Y-direction (per element area) | [kN/m²] |
| `PZZ`  | Loading in global Z-direction (per element area, e.g. self weight) | [kN/m²] |
| `PXP`  | Loading in global X referenced to projected area (e.g. snow) | [kN/m²] |
| `PYP`  | Loading in global Y referenced to projected area | [kN/m²] |
| `PZP`  | Loading in global Z referenced to projected area | [kN/m²] |
| `PXY`  | Load in the normal direction of the area projected into global XY-plane | [kN/m²] |
| `PYZ`  | Load in the normal direction of the area projected into global YZ-plane | [kN/m²] |
| `PZX`  | Load in the normal direction of the area projected into global ZX-plane | [kN/m²] |
| `PXYS` | As PXY but load value referenced to element area | [kN/m²] |
| `PYZS` | As PYZ but load value referenced to element area | [kN/m²] |
| `PZXS` | As PZX but load value referenced to element area | [kN/m²] |
| `PXYP` | As PXY but load value referenced to projected area | [kN/m²] |
| `PYZP` | As PYZ but load value referenced to projected area | [kN/m²] |
| `PZXP` | As PZX but load value referenced to projected area | [kN/m²] |
| `PXXx`…`PZPz` | Load in local direction `x/y/z` derived from global `X/Y/Z` projection (e.g. `PXPZ`); see also PROJ XXL/YYL/ZZL | [kN/m²] |
| `MX`   | Moment loading about local x-axis | [kNm/m²] |
| `MY`   | Moment loading about local y-axis | [kNm/m²] |
| `MZ`   | Moment loading about local z-axis | [kNm/m²] |
| `MXX`  | Moment loading about global X-axis | [kNm/m²] |
| `MYY`  | Moment loading about global Y-axis | [kNm/m²] |
| `MZZ`  | Moment loading about global Z-axis | [kNm/m²] |
| `DTXY` | Temperature difference in the xy-plane | [K] |
| `DTZ`  | Temperature difference in local z-direction | [K] |
| `EX`   | Strain in local x | [‰] |
| `EY`   | Strain in local y | [‰] |
| `KX`   | Curvature in local x | [1/km] |
| `KY`   | Curvature in local y | [1/km] |
| `WZ`   | Settlement in local z | [mm] |
| `PMXX` | Prestress moment m-xx | [kNm/m] |
| `PMYY` | Prestress moment m-yy | [kNm/m] |
| `PMXY` | Prestress moment m-xy | [kNm/m] |
| `PVX`  | Prestress shear q-x | [kN/m] |
| `PVY`  | Prestress shear q-y | [kN/m] |
| `PNXX` | Prestress membrane force n-x | [kN/m] |
| `PNYY` | Prestress membrane force n-y | [kN/m] |
| `PNXY` | Prestress membrane force n-xy | [kN/m] |

> The difference between PXX and PXP is that PXX is referenced to the true element area (e.g. dead weight) while PXP is referenced to the projection of the element area (e.g. snow). For planar systems there is no difference. The component loadings (PXY etc.) define a load direction derived from projecting the area normal into the specified global plane (e.g. diverting forces of tendons or earthquake loads on tank fillings). With PROJ XXL/YYL/ZZL the sign of the load value is applied to the local component instead of the global component, making the load act uniformly inward/outward everywhere.
> For load types P and M, equivalent nodal forces are established by integrating element shape functions. For initial-stress load types (temperature, strain etc.), element loads are generated using the element centre for selection; irregular meshes may therefore yield less than 100% loaded area.

**Typical usage:**
```
$ Uniform live load over rectangular bay (projected)
LC 1 TYPE G
AREA REF AUTO TYPE PZP $$
     P1 -3.0 X1 0.0 Y1 0.0 Z1 0.0 $$
     P2 -3.0 X2 6.0 Y2 0.0 Z2 0.0 $$
     P3 -3.0 X3 6.0 Y3 5.0 Z3 0.0 $$
     P4 -3.0 X4 0.0 Y4 5.0 Z4 0.0

$ Constant load on structural area 3 — no coordinates required
LC 2 TYPE Q
AREA REF SAR NO 3 TYPE PZP P1 -2.0

$ Rectangle shorthand using DXY increment
LC 3 TYPE Q
AREA REF AUTO TYPE PZP $$
     P1 -3.0 X1 0.0 Y1 0.0 Z1 0.0 $$
     P2 -3.0 X2 DXY Y2 6.0 Z2 5.0  $ 6 m in X, 5 m in Y from point 1

$ Linearly varying soil pressure on basement wall
LC 4 TYPE Q
AREA REF SAR NO 5 TYPE PZZ $$
     P1  0.0  X1 0.0 Y1 0.0 Z1  0.0 $$
     P2  0.0  X2 8.0 Y2 0.0 Z2  0.0 $$
     P3 -40.0 X3 8.0 Y3 0.0 Z3 -4.0 $$
     P4 -40.0 X4 0.0 Y4 0.0 Z4 -4.0 $$
```

---

### VOLU — Geometry-Referenced Volume Load

Applies loads within a 3D volume region defined by up to 6 points.

**Syntax:**
```
VOLU REF NO TITL PROJ WIDE A/U TYPE
     P  X  Y  Z   P1 X1 Y1 Z1
     P2 X2 Y2 Z2  P3 X3 Y3 Z3
     P4 X4 Y4 Z4  P5 X5 Y5 Z5
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `REF`     | enum   | —     | *       | Reference geometry type |
| `NO`      | int    | —     | *       | Reference entity number |
| `TITL`    | string | —     | *       | Label |
| `PROJ`    | float  | —     | *       | Projection |
| `WIDE`    | float  | [m]   | *       | Projection width |
| `A/U`     | float  | —     | *       | Area/volume factor |
| `TYPE`    | enum   | —     | —       | Load component type |
| `P`–`P5`  | float  | *     | *       | Load values at corners |
| `X`–`Z5`  | float  | [m]   | *       | Corner coordinates |

**REF values:** LAR, GFA, SAR, SVO, FGRP, QGRP, VGRP.

**Typical usage:**
```
VOLU REF AUTO TYPE PZZ P -10.0  $ volume body force 10 kN/m³
  X 0.0 Y 0.0 Z 0.0
  P1 -10.0 X1 5.0 Y1 0.0 Z1 0.0
  P2 -10.0 X2 5.0 Y2 5.0 Z2 0.0
  P3 -10.0 X3 0.0 Y3 5.0 Z3 0.0
```

---

### LAR — Define a Named Load Area

Defines a named load area (LAR) that can be referenced by POIN, LINE, AREA, and VOLU with `REF LAR NO <n>`. Load areas describe geometric regions for projecting loads onto structural elements.

**Syntax:**
```
LAR NO
    NAR GRP GRP1 GRP2 GRP3 M N
    T  X1 Y1 Z1  X2 Y2 Z2  X3 Y3 Z3  X4 Y4 Z4
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `NO`      | int    | —     | —       | Load area number |
| `NAR`     | int    | —     | *       | Reference area number |
| `GRP`     | int    | —     | *       | Primary group to search within |
| `GRP1`–`GRP3` | int | —   | *       | Additional groups |
| `M`       | int    | —     | *       | Number of subdivisions in local x |
| `N`       | int    | —     | *       | Number of subdivisions in local y |
| `T`       | int    | —     | *       | Coordinate system type |
| `X1`–`Z4` | float  | [m]   | *       | Corner coordinates of load area |

> `DEL` keyword on a sub-record deletes a previously defined LAR.
> Tributary area definition can reference a LAR via TRB.
> Planar LAR regions must be convex — see warnings 071–075.

**Typical usage:**
```
LAR 1
    GRP 3
    T 0  X1 0.0 Y1 0.0 Z1 0.0
         X2 6.0 Y2 0.0 Z2 0.0
         X3 6.0 Y3 8.0 Z3 0.0
         X4 0.0 Y4 8.0 Z4 0.0
$ Define load area 1 over 6×8m rectangle, group 3
```

---

### COPY — Loads from Other Sources

COPY transfers loading from another load case or action into the current load case. All types of loading definitions including loads generated by other programs are copied. The self-weight defined by DLX–DLZ of record LC is copied only if not yet defined in the current load case directly or by another COPY command. The source load case may have been created in a previous or the same input block.

When copying, the source of the loading is remembered so that a restart (`LC nn REST`) repeats the copy and uses the current load definitions. Use `CTRL COPY 256` to suppress this and treat the copied loads as explicitly defined. Load functions cannot be copied, as every load case must have a unique load function.

Specifying an action name for NO copies all load cases of that action. Without a PROJ database name, loads are read from the current database; with a name, from that external database.

With a literal for FACT the user may build load case combinations for nonlinear analysis using safety factors and combination coefficients directly. This is **not** a superposition like MAXIMA — the user must specify load cases in the correct sequence and selection.

**Syntax:**
```
COPY NO FACT TYPE FROM TO INC
     REF LEV DX DY DZ ALPH WIDE YEX
     CASE NRE XABS XCON XV1 [XV2 ... XV15]
     PROJ
```

| Parameter | Type      | Unit  | Default | Description |
|-----------|-----------|-------|---------|-------------|
| `NO`      | int/lit   | —     | !       | Number of source load case, or name of an action |
| `FACT`    | float/lit | [-]   | 1.0     | Factor for loading, or combination type literal (see below) |
| `TYPE`    | lit       | —     | ALL     | Selector for elements / load types to copy |
| `FROM`    | int       | —     | —       | Number of first element or node (range filter) |
| `TO`      | int       | —     | —       | Number of last element or node |
| `INC`     | int/lit   | —     | —       | Increment of element/node numbers, or load pattern literal |
| `REF`     | int       | —     | —       | Reference number of an axis or lane |
| `LEV`     | float     | [m]   | 0.0     | Select only nodes at this ordinate in gravity direction |
| `DX`      | float     | [m]   | 0.0     | Global or local shift of loading in X |
| `DY`      | float     | [m]   | 0.0     | Global or local shift of loading in Y |
| `DZ`      | float     | [m]   | 0.0     | Global or local shift of loading in Z |
| `ALPH`    | float     | [°]   | 0.0     | Rotation applied before shifting |
| `WIDE`    | float     | [m]   | 0.0     | Projection depth of generated loading |
| `YEX`     | float     | [m]   | *       | Eccentricity for load trains |
| `CASE`    | int       | —     | 1       | Evaluation case in ELLA |
| `NRE`     | int/lit   | —     | 1       | Ident of element / influence line |
| `XABS`    | float     | [m]   | 0.0     | Section for beam elements |
| `XCON`    | float     | [m]   | —       | Explicit value of convoy distance |
| `XV1`…`XV15` | float  | [m]   | —       | Explicit values for variable lengths in load train |
| `PROJ`    | lit255    | —     | —       | Name of an external database |

**TYPE — element/load type selector:**

| Value  | Meaning |
|--------|---------|
| `ALL`  | All loading input (default) |
| `POIN` | Free point loading |
| `LINE` | Free line loading |
| `AREA` | Free area loading |
| `VOLU` | Free volume loading |
| `PSUP` | Supporting point loads (reactions) |
| `SUPP` | Vector of supporting loads (reactions including moments) |
| `TRAI` | Load train loading |
| `ELLA` | Load train as positioned in ELLA |
| `INTE` | All generated analysis nodal loads (requires prior ASE run) |
| `NODE` | Nodal loading (including generated) |
| `BEAM` | Beam loading (including generated) |
| `TRUS` | Truss loading |
| `CABL` | Cable loading |
| `QUAD` | QUAD loading |
| `BRIC` | BRIC loading |
| `WIND` | Wind pressure coefficients |

> Appending `:E` to the type (e.g. `BEAM:E`) restricts copying to user-defined loads only, excluding generated loads.
> For large systems it may be considerably faster to copy only NODE and BEAM loads rather than ALL.
> Selecting INTE copies only the generated nodal analysis loads; elemental loads (temperature, prestress) cannot be copied this way, and a prior ASE run is required.

**FACT — combination type literals** (instead of a numeric factor):

| Literal      | Combination | Formula |
|--------------|-------------|---------|
| `DESI`/`DESF` | ULS fundamental, unfavourable / favourable | γ_g·G_k + γ_q,1·Q_k,1 + Σγ_q,i·ψ₀,i·Q_k,i |
| `ACCI`/`ACCF` | Accidental, unfavourable / favourable | γ_g,A·ψ₀,g·G_k + γ_A·A_d + ψ₁,i·Q_k,1 + Σψ₂,i·Q_k,i |
| `RARE`        | SLS rare (characteristic) | G_k + Q_k,1 + Σψ₀,i·Q_k,i |
| `FREQ`        | SLS frequent | G_k + ψ₁,i·Q_k,1 + Σψ₂,i·Q_k,i |
| `NONF`        | SLS non-frequent (EC1-3) | G_k + ψ'₁·Q_k,1 + Σψ₁,i·Q_k,i |
| `PERM`        | SLS quasi-permanent | G_k + Σψ₂,i·Q_k,i |
| `COMB`        | Use combination factors saved by MAXIMA (specify combination number in NO) | — |

For variable actions Q, the **first** load case listed in a COPY sequence receives the leading-action coefficient; all others receive the accompanying coefficient. Example:
```
LC 101 ; COPY  1,2,3,4 DESI   $ LC 1 is leading variable action
LC 102 ; COPY  2,3,4,1 DESI   $ LC 2 is leading variable action
```

**FACT — individual coefficient literals:**

| Literal | Applied factor |
|---------|---------------|
| `GAMU` / `GAMF` | Safety factor unfavourable / favourable |
| `PSIU` / `PSIF` | γ_u × ψ₀ / γ_f × ψ₀ |
| `PSI0` / `PSI1` / `PSI2` / `PS1S` | Combination coefficients ψ₀, ψ₁, ψ₂, ψ'₁ |
| `PS1U` / `PS1F` | γ_u × ψ₁ / γ_f × ψ₁ |
| `PS2U` / `PS2F` | γ_u × ψ₂ / γ_f × ψ₂ |
| `P1SU` / `P1SF` | γ_u × ψ'₁ / γ_f × ψ'₁ |

**Support forces (TYPE PSUP / SUPP):** Reaction forces (and with SUPP also moments) at nodes are converted to free POIN loads. The reference type defaults to AUTO so loads are applied within the WIDE range in any suitable way; a negative WIDE switches to projection N, placing loads exactly at their true locations. With DX, DY, or DZ a specific coordinate value filters the nodes; with LEV only nodes at that gravity-direction ordinate are used, and DX/DY/DZ then become shifts — useful for transferring floor reactions from one storey down to a lower level.

**Typical usage:**
```
$ Simple scaled copy
LC 101 TYPE (D) TITL 'ULS - 1.35G + 1.5Q'
  COPY NO 1 FACT 1.35    $ G self-weight
  COPY NO 2 FACT 1.35    $ G2 superimposed dead
  COPY NO 11 FACT 1.5    $ Q1 live load as leading action

$ Code combination using DESI literal
LC 102 TYPE (D) TITL 'ULS DESI - auto combination factors'
  COPY 1,2,11 DESI       $ LC 11 is first = leading variable

$ SLS rare using individual coefficient
LC 201 TYPE (R) TITL 'SLS rare'
  COPY NO 1 FACT 1.0
  COPY NO 2 FACT 1.0
  COPY NO 11 FACT PSI0   $ apply ψ₀ factor from action definition

$ Copy only area and line loads (filter by type)
LC 301
COPY NO 11 FACT 1.0 TYPE AREA
COPY NO 11 FACT 1.0 TYPE LINE

$ Copy with geometric offset (e.g. shifted snow load)
COPY NO 21 FACT 1.0 DX 3.0 DY 0.0 DZ 0.0
```

---

### LTD — Load Take-Down

Transfers support reactions from a source analysis database as applied loads in the current model. Used when a global model's reactions are to be applied as loads on a detailed sub-model.

**Syntax:**
```
LTD OPT SRLC SRCT SRC TRGT TRG LMAX TRGM DZ TYPE FACT DIR HMOM FROM
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `OPT`     | enum   | —     | —       | Task type |
| `SRLC`    | int    | —     | *       | Source load case number |
| `SRCT`    | enum   | —     | *       | Source geometry type |
| `SRC`     | string | —     | *       | Source geometry name/number |
| `TRGT`    | enum   | —     | *       | Target geometry type |
| `TRG`     | string | —     | *       | Target geometry name/number |
| `LMAX`    | float  | [m]   | *       | Maximum transfer distance |
| `TRGM`    | enum   | —     | *       | Target distribution mode |
| `DZ`      | float  | [m]   | *       | Vertical offset |
| `TYPE`    | enum   | —     | *       | Load type for transferred loads |
| `FACT`    | float  | [-]   | *       | Scale factor |
| `DIR`     | string | —     | *       | Direction filter |
| `HMOM`    | string | —     | *       | Include moments from horizontal loads |
| `FROM`    | string | —     | *       | Source database path |

**OPT:**

| Value  | Meaning |
|--------|---------|
| `TASK` | Define a new take-down task |
| `SEL`  | Select geometry for this task |
| `IGN`  | Ignore specific geometry |
| `MOD`  | Modify a task |

**SRCT / TRGT — geometry types:**

| Value  | Meaning |
|--------|---------|
| `SLN`  | Structural line |
| `SPT`  | Structural point |
| `GRP`  | Element group |
| `GUID` | Guide line |
| `ALL`  | All geometry |

**TRGM — distribution mode:**

| Value  | Meaning |
|--------|---------|
| `INDI` | Individual load cases |
| `COMB` | Combined into one LC |

**Typical usage:**
```
!*! Load take-down from global to local model
LC 10 TYPE PERM TITL 'LTD reactions from global model LC 1'
LTD OPT TASK SRLC 1 SRCT SLN TRGT SLN TRGM INDI FACT 1.0
    FROM 'global_model.cdb'
```

---

### LTDG — LTD Geometry Polygon

Defines a polygon region that filters which reactions are transferred in an LTD task.

**Syntax:**
```
LTDG X1 Y1 Z1 X2 Y2 Z2 X3 Y3 Z3 TITL GUID
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `X1`–`Z3` | float  | [m]   | *       | Corner coordinates of the polygon |
| `TITL`    | string | —     | *       | Label |
| `GUID`    | string | —     | *       | Guide line reference name |

> Must follow an `LTD OPT TASK` record — warning 414.

---

### GUID — Geometric Guide Line

Defines a named guide line used by LTD for matching structural lines between source and target models.

**Syntax:**
```
GUID ID TAG
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `ID`      | string | —    | —       | Guide line identifier |
| `TAG`     | string | —    | *       | Tag for matching |

---

### TRB — Tributary Area Definition

Defines a tributary area for distributing surface loads to supporting beams via a plate-on-elastic-foundation analogy.

**Syntax:**
```
TRB NO SAR TYPE REFI CCAV
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `NO`      | int    | —    | —       | Tributary area number (> 0) |
| `SAR`     | int    | —    | *       | Structural area (SAR) reference |
| `TYPE`    | enum   | —    | *       | Mesh type |
| `REFI`    | int    | —    | *       | Reference item |
| `CCAV`    | enum   | —    | *       | Concave corner handling |

**TYPE:**

| Value  | Meaning |
|--------|---------|
| `FULL` | Full tributary area |
| `CONP` | Conservative with points |
| `CONS` | Conservative |

**Typical usage:**
```
TRB 1 SAR 1 TYPE FULL
TRBA M 4 N 4
     X1 0.0 Y1 0.0 Z1 0.0
     X2 6.0 Y2 0.0 Z2 0.0
     X3 6.0 Y3 5.0 Z3 0.0
     X4 0.0 Y4 5.0 Z4 0.0
TRBS SELT GRP SEL 1   $ supporting beams in group 1
```

---

### TRBA — Tributary Area Polygon

Adds a four-point polygon region to a tributary area (TRB). Must follow a TRB record.

**Syntax:**
```
TRBA M N X1 Y1 Z1 X2 Y2 Z2 X3 Y3 Z3 X4 Y4 Z4
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `M`       | int    | —     | *       | Subdivisions in local x |
| `N`       | int    | —     | *       | Subdivisions in local y |
| `X1`–`Z4` | float  | [m]   | *       | Corner coordinates |

---

### TRBS — Tributary Area Supports

Defines the supporting beams for a tributary area. Must follow a TRB record.

**Syntax:**
```
TRBS SELT SEL ... MODE FTYP FFIX FANG FANT STIF
```

| Parameter | Type   | Unit   | Default | Description |
|-----------|--------|--------|---------|-------------|
| `SELT`    | enum   | —      | *       | Selection type |
| `SEL`     | string | —      | *       | Selection name/number |
| `MODE`    | float  | —      | *       | Distribution mode |
| `FTYP`    | float  | [m/s²] | *       | Foundation type factor |
| `FFIX`    | float  | [m/s²] | *       | Fixed boundary stiffness |
| `FANG`    | float  | [°]    | *       | Filter angle (0°–90°) |
| `FANT`    | float  | —      | *       | Anti-symmetry factor |
| `STIF`    | float  | —      | *       | Support stiffness |

**SELT:**

| Value  | Meaning |
|--------|---------|
| `AUTO` | Automatic beam detection |
| `SLN`  | Structural lines |
| `SPT`  | Structural points |
| `GRP`  | Element group |
| `GUID` | Guide lines |

---

### END — End of SOFILOAD Block

Closes the SOFILOAD program block. Required as the last record.

**Syntax:**
```
END
```

---

## Complete SOFILOAD Block Example

Full example: a six-storey reinforced concrete office building. Defines actions using standard code designations, dead and live load cases with geometry-referenced AREA loads, and COPY for ULS/SLS combinations.

```
+PROG SOFILOAD urs:5

HEAD Six-storey office building - Load definition

$ ============================================================
!*! Action definitions (code defaults from AQUA NORM)
$ ============================================================
ACT G TITL 'Self-weight G'

ACT G_2 TITL 'Superimposed dead load G2'

ACT Q PSI0 0.7  PSI1 0.5  PSI2 0.3 TITL 'Office live load Q1'

$ ============================================================
!*! Load case 1: Self-weight (gravity via FACD)
$ ============================================================
LC 1 TYPE G FACD 1.0 TITL 'G - Self-weight'

$ ============================================================
!*! Load case 2: Superimposed dead load via area polygon
$ ============================================================
LC 2 TYPE G_2 TITL 'G2 - Superimposed dead load'
AREA REF AUTO TYPE PZP $$
     P1 -1.5 X1  0.0 Y1  0.0 Z1 3.0 $$
     P2 -1.5 X2 24.0 Y2  0.0 Z2 3.0 $$
     P3 -1.5 X3 24.0 Y3 12.0 Z3 3.0 $$
     P4 -1.5 X4  0.0 Y4 12.0 Z4 3.0
$ repeat area records for each floor level as needed

$ ============================================================
!*! Load case 11: Office live load (full floor)
$ ============================================================
LC 11 TYPE Q TITL 'Q1 - Office live load - full'
AREA REF AUTO TYPE PZP $$
     P1 -3.0 X1  0.0 Y1  0.0 Z1 3.0 $$
     P2 -3.0 X2 24.0 Y2  0.0 Z2 3.0 $$
     P3 -3.0 X3 24.0 Y3 12.0 Z3 3.0 $$
     P4 -3.0 X4  0.0 Y4 12.0 Z4 3.0

$ ============================================================
!*! Load case 12: Roof imposed load via polygon
$ ============================================================
LC 12 TYPE Q TITL 'Q1r - Roof imposed load'
AREA REF AUTO TYPE PZP $$
     P1 -1.5 X1  0.0 Y1  0.0 Z1 18.0 $$
     P2 -1.5 X2 24.0 Y2  0.0 Z2 18.0 $$
     P3 -1.5 X3 24.0 Y3 12.0 Z3 18.0 $$
     P4 -1.5 X4  0.0 Y4 12.0 Z4 18.0

$ ============================================================
!*! Load case 101: ULS fundamental - G + Q (EN 1990 6.10)
$ ============================================================
LC 101 TYPE (D) TITL 'ULS - 1.35G + 1.5Q'
COPY NO 1  FACT 1.35   $ G self-weight
COPY NO 2  FACT 1.35   $ G2 superimposed dead
COPY NO 11 FACT 1.50   $ Q1 live load (leading variable action)

$ Alternatively, use the DESI combination literal:
$ COPY 1,2,11 DESI      (LC 11 first = leading action)

$ ============================================================
!*! Load case 201: SLS rare combination
$ ============================================================
LC 201 TYPE (R) TITL 'SLS rare - G + Q'
COPY NO 1  FACT 1.0
COPY NO 2  FACT 1.0
COPY NO 11 FACT PSI0   $ apply ψ₀ factor from Q action definition

END
```

---

## Unit Summary for SOFILOAD

| Quantity | Unit | Parameters |
|----------|------|------------|
| Coordinates | [m] | All X, Y, Z positions in POIN/LINE/AREA/VOLU/LAR |
| Concentrated force | [kN] | POIN P |
| Line load | [kN/m] | LINE P1–P6 |
| Area surface load | [kN/m²] | AREA P1–P6 |
| Volume body force | [kN/m³] | VOLU P |
| Moment | [kNm] | POIN MX/MY/MZ |
| Bimoment | [kNm²] | TYPE MB |
| Projection width | [m] | POIN/LINE/AREA WIDE |
| Factors / ratios | [-] | FACT, PSI0–PS1S, GAMU, GAMF on ACT/LC |
