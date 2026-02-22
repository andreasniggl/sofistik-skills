# Module: SOFIMSHC — Structural Model and Meshing

## Purpose
SOFIMSHC defines the complete structural geometry: coordinate system, groups, structural points (nodes), structural lines (beams/trusses), structural areas (slabs/shells), and mesh generation settings. It must always precede any analysis module.

## Load this file when
Any structural model is being created (required for every analysis).

## Module block template
```
+PROG SOFIMSHC urs:<n>
HEAD <description>

SYST 3D GDIR NEGZ GDIV -1000   $ system type and gravity direction

!*!Label Control Values
CTRL MESH 2                     $ activate meshing (beams + shells)
CTRL HMIN 0.5[m]                $ target mesh size
CTRL TOLG 0.01[m]               $ geometric intersection tolerance

!*!Label Groups
GRP ...

!*!Label Structural Points
SPT ...

!*!Label Structural Lines
SLN ...

!*!Label Structural Areas
SAR ...

END
```

---

## Commands

---

### ECHO — Output Control

Controls which data is printed in the module report.

**Syntax:**
```
ECHO 'OPT' VAL X Y Z
```

| Parameter | Type   | Unit | Description |
|-----------|--------|------|-------------|
| `OPT`     | enum   | —    | Output category (4-char string in single quotes) |
| `VAL`     | float  | —    | Optional output level value |
| `X`       | float  | —    | Optional x-value |
| `Y`       | float  | —    | Optional y-value |
| `Z`       | float  | —    | Optional z-value |

**OPT values:**
`FULL` | `MAT` | `SECT` | `GEOM` | `NODE` | `QUAD` | `BRIC` | `BEAM` | `BOUN` | `SYST` | `STAT` | `WARN`

---

### CTRL — Control of Analysis

Sets global program control options for the topological analysis, geometry healing, mesh generation, element generation, and system initialisation. Each `CTRL` record sets one option. Related commands: `SPT`, `SLN`, `SAR`.

**Syntax:**
```
CTRL 'OPT' VAL V2 V3 V4
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `OPT`     | enum   | —    | **req** | Control option identifier — mandatory literal from the list below |
| `VAL`     | varies | —    | —       | Primary value — type and unit depend on `OPT` |
| `V2`      | varies | —    | —       | Second value (required by some options) |
| `V3`      | varies | —    | —       | Third value (required by some options) |
| `V4`      | varies | —    | —       | Fourth value (required by some options) |

---

**Topological analysis and structural model**

In the first processing step before meshing, SOFiMSHC reads the model, intersects all structural elements with each other, and constructs a mechanically consistent system. The following options control this process.

**CTRL TOPO** — topological decomposition and intersection (default `ON`)

| VAL literal | V2 | Description |
|-------------|-----|-------------|
| `ON`        | key | Stores the input model at reference key `V2` and activates structural analysis and intersection |
| `OFF`       | —   | Deactivates import and analysis entirely — mesh generation is also suppressed even if `CTRL MESH` is set. Use only for debugging when the model was already imported in a previous run. |
| `DEL`       | key | Deletes structural elements stored at reference key `V2`. Normally not needed — the database is initialised automatically when `SYST` is processed. |
| `GAXP`      | bitmask | Controls generation of structural elements from axis placements (default `+3`): `+1` = generate SPT at placements; `+2` = generate SLN between placements where a section is defined; `+4` = generate SLN between all placements regardless of section |
| `SARB`      | bitmask | Controls classification of implicitly defined interior boundary edges (default `+8`): `+1` = assume edges are already sorted (CAD import); `+4` = treat as opening boundary; `+8` = treat as internal region boundary; `+12` = treat as constraining edges |
| `XFLG`      | bitmask | Global intersection control (default `+1`): `+1` = two explicitly numbered structural points at the same position are never merged |

**CTRL TOLG** `VAL[m]` — geometric intersection tolerance (default `−0.01`)

Structural elements (points, lines, areas) closer than this tolerance are merged.
- `VAL > 0` — absolute distance in `[m]`
- `VAL < 0` — relative factor scaled by characteristic model dimensions (default `−0.01` = 1% of model size)

**CTRL NODE** `VAL` — start index for automatically assigned element numbers (default `1000`)

During topological analysis, new structural elements are created automatically and numbered from this index upward. When multiple `SOFIMSHC` blocks run in one project, increase this value to separate auto-generated from explicitly defined numbers.

**CTRL DELN** `VAL` — deletion of unused structural lines (default `1`)

- `0` — keep all structural lines, including those not connected to any other element
- `1` — delete structural lines with no stiffness (no section) that are not connected to the model. Set to `0` when lines are used as helper/reference geometry or for later reuse (e.g. load takedown workflows, extrusion paths).

---

**Geometry healing**

Models from external CAD systems often have geometric inconsistencies. The following options repair them before meshing.

**CTRL HEAL JOIN** `V2[m]` `V3[°]` — join short adjacent structural lines

Two adjacent lines are joined into one if: their length is below `V2`, the angle between them is less than `V3`, they have no branching connection (no Y-junction), and their boundary / cross-section properties are identical.

**CTRL HEAL DELO** `V2[m²]` — delete small openings

Openings (holes in structural areas) with a surface area below `V2` are removed.

---

**Meshing control**

**CTRL MESH** `VAL` — activate mesh generation (default `0`)

| VAL | Description |
|-----|-------------|
| `0` | Deactivate meshing |
| `1` | Mesh beam structures only |
| `2` | Mesh beam and shell structures |
| `3` | Mesh beam, shell and/or volume structures |

Additional flags (add to base value):

| Flag  | Description |
|-------|-------------|
| `+16` | Keep explicitly defined old elements |
| `+32` | Triangular elements only |
| `+64` | Quadrilateral elements only |
| `+128`| Disable duplicate run with background mesh |
| `+256`| Post-processing only (partitioning, optimisation) |

> `CTRL MESH` automatically activates `CTRL TOPO ON`.

**CTRL HMIN** `VAL[m]` — global maximum element edge length (default `1.0`)

Sets the upper bound for element edge length for all beam, shell, and volume elements. Local geometric features may force smaller elements. Can be overridden individually per structural object via `SAR H1`, `SLN SDIV`.

**CTRL FINE** `VAL` — mesh size at area corners (default `HMIN`)

- `VAL > 0` — absolute mesh size at corners in `[m]`
- `VAL < 0` — factor applied to `HMIN` (e.g. `−0.5` = half the global mesh size at corners)

Reducing the corner mesh size generally improves element quality.

**CTRL EFAC** `VAL` — mesh density scaling near short edges (default `1.4`)

Controls local mesh refinement in the neighbourhood of structural edges shorter than `HMIN`. The factor describes the ratio: `"local mesh size" / "short edge length"`. Higher values reduce refinement (fewer elements, possibly lower quality). Set to `0` to deactivate entirely — useful for long narrow areas where edge-end refinement causes irregular meshes.

**CTRL PROG** `VAL` — mesh density progression factor (default `1.5`)

Maximum allowed ratio of edge length between two adjacent quad elements. Controls the rate at which mesh density transitions from a refined zone back to the global density.

---

**Element generation and boundary conditions**

**CTRL BSEC** `VAL` — automatic generation of design sections (default `0`)

- `0` — disabled
- `1` — generate sections at support faces along beam girders (at connections to columns below, crossing walls, or `SPT` with `BX`/`BY` dimensions). Used to enable moment rounding at supports in AQB design.

**CTRL LOCA** `VAL` — local beam coordinate system convention (default `1`)

Controls which local axis is aligned to gravity and how user-defined orientations are interpreted:

| VAL | Default z-axis direction | User orientation applies to |
|-----|--------------------------|----------------------------|
| `0` | Gravity direction (y-axis if beam || gravity) | Local y-axis |
| `1` | Gravity direction (first horizontal if beam || gravity) | Local z-axis — **default** |
| `2` | Global Z (global X if beam || Z) | Local z-axis (IFC convention) |
| `3` | Global Z (global Y if beam || Z) | Local y-axis (GENF convention) |

**CTRL TOLN** `VAL` — FE node merge tolerance (default `1e-6`)

Relative factor (scaled internally by model dimensions) controlling when two FE nodes are considered identical and merged. Applied after meshing.

**CTRL PSUP** `VAL` — point support mesh macro (default `0`)

Controls the special mesh macro generated at point supports (`SPT` with column head geometry via `SPTP`):

| VAL | Description |
|-----|-------------|
| `−1` | No special action — single node only |
| `0`  | Generate 4 rectangular quad elements around the support point — **default** |
| `1`  | Increase element thickness at support centre |
| `2`  | Kinematic constraints of mid points |
| `4`  | Kinematic constraints of corner points |
| `8`  | Additional centre node for constraints |
| `16` | Deactivate minimum mesh size correction |

Column head dimensions and voute geometry are defined locally via `SPTP`.

**CTRL LSUP** `VAL` — line support / boundary element generation (default `1`)

Controls when boundary elements (distributed supports) are generated along structural lines:

| VAL | Description |
|-----|-------------|
| `0`  | Only when elastic support or group number > 0 without a section |
| `1`  | Also for lines with rigid support in gravity direction — **default** |
| `2`  | Whenever any type of support is given |
| `3`  | For all structural line edges |
| `+16`| Generate elastic spring elements instead of boundary elements |

---

**Equation numbering optimisation**

**CTRL OPTI** `VAL` — equation renumbering algorithm (default `49`)

| VAL  | Description |
|------|-------------|
| `0`  | Deactivate optimisation |
| `1`  | Standard bandwidth optimisation (use with `SOLV 1` or `SOLV 2`) |
| `2`  | Extensive bandwidth optimisation (use with `SOLV 1`) |
| `49` | Fill-in reducing ordering — **default** (use with `SOLV 3`) |

An incorrect setting may adversely affect solver performance or memory usage.

---

**Initialisation and warnings**

**CTRL INIT** `VAL` (bitmask, default `+12`) — controls which data is deleted on SOFiMSHC startup

On startup SOFiMSHC deletes and reinitialises the model in the database (except for `SYST REST`). The bitmask controls which data is affected:

| Bit  | Data deleted |
|------|-------------|
| `+1` | Geometric axes (`GAX`) |
| `+2` | Geometric areas (`GAR`) |
| `+4` | Structural elements (`SPT`, `SLN`, `SAR`, …) |
| `+8` | Storey level information (`SLVL`) |
| `+16`| Design elements (`DECREATOR`: `DSLN`) |
| `+32`| Secondary groups |

**CTRL WARN** `VAL` — suppress a specific warning message number

---

**Typical usage:**
```
SYST 3D GDIR NEGZ GDIV -1000

$ --- Mesh control
CTRL MESH 2          $ mesh beams and shells
CTRL HMIN 0.5[m]     $ global max element size 500 mm
CTRL FINE -0.5       $ corners at 50% of HMIN
CTRL EFAC 1.4        $ default short-edge refinement factor

$ --- Intersection and tolerance
CTRL TOLG -0.01      $ relative tolerance 1% of model size
CTRL NODE 10000      $ auto-numbers start at 10000

$ --- Element generation
CTRL LOCA 1          $ z-axis to gravity (default)
CTRL PSUP 0          $ 4-quad column head mesh macro
CTRL LSUP 1          $ boundary elements at gravity supports

$ --- Join short imported edges (CAD import healing)
CTRL HEAL JOIN 0.05[m] 5   $ join lines < 50 mm with angle < 5°
```

---

### SYST — System Definition

Defines the global coordinate system, model type, gravity direction, and group numbering scheme. Must appear before any structural entity definitions.

**Syntax:**
```
SYST 'TYPE' GDIV 'GDIR' 'FIX' XREF YREF ZREF T11 T21 T31 T12 T22 T32 T13 T23 T33
```

| Parameter | Type  | Unit | Description |
|-----------|-------|------|-------------|
| `TYPE`    | enum  | —    | Model type (4-char string in single quotes) — **required** |
| `GDIV`    | int   | —    | Group divisor for automatic element numbering. Use `-1000` for 1000 elements per group |
| `GDIR`    | enum  | —    | Direction of gravity (self-weight) |
| `FIX`     | enum  | —    | Global default fixity condition |
| `XREF`    | float | —    | X-coordinate of reference origin |
| `YREF`    | float | —    | Y-coordinate of reference origin |
| `ZREF`    | float | —    | Z-coordinate of reference origin |
| `T11`…`T33` | float | —  | Transformation matrix components |

**TYPE enum values:**

| Value  | Description |
|--------|-------------|
| `3D`   | Full 3D model — **standard choice for most analyses** |
| `2D`   | 2D plane model |
| `SPAC` | 3D space frame |
| `GIRD` | Grillage model |
| `SLAB` | Slab / plate model |
| `PSLA` | Plate-slab combined |
| `2DSL` | 2D slab |
| `PLAN` | Plane stress / plane strain |
| `2DSS` | 2D plane stress |
| `2DSN` | 2D plane strain |
| `FRAM` | 2D frame |
| `AXIA` | Axisymmetric |
| `INIT` | Re-initialise (clear previous data) |
| `REST` | Restart from previous run |
| `SECT` | Section only (no meshing) |

**GDIR enum values:**

| Value  | Description |
|--------|-------------|
| `NEGZ` | Gravity in −Z direction — **standard for horizontal slabs** |
| `NEGY` | Gravity in −Y direction |
| `NEGX` | Gravity in −X direction |
| `POSX/POSY/POSZ` | Gravity in positive axis direction |
| `NONE` | No gravity direction defined |
| `XX/YY/ZZ` | Gravity along specified axis (both directions) |

**Typical usage:**
```
SYST 3D GDIR NEGZ GDIV -1000   $ 3D model, gravity downward (−Z), 1000 elements per group
```

---

### GRP — Group Definition

Defines element groups used to organise structural members. Groups control element numbering, construction stages, and post-processing selections.

**Syntax:**
```
GRP NO REF BASE ICS ICE "title"
```

| Parameter | Type   | Unit | Description |
|-----------|--------|------|-------------|
| `NO`      | int    | —    | Group number (optional if sequential) |
| `REF`     | int    | —    | Reference group number |
| `BASE`    | int    | —    | Base element number for this group (used when `GDIV=0`) |
| `ICS`     | int    | —    | Construction stage at which group becomes active |
| `ICE`     | int    | —    | Construction stage at which group is deactivated |
| `TITL`    | string | —    | Group description (variable-length string in double quotes) |

**Typical usage:**
```
GRP 1 TITL "Bottom chord"
GRP 2 TITL "Top chord"
GRP 3 TITL "Verticals"
```

---

### SPT — Structural Point

Defines a structural point with coordinates, a local coordinate system, and optional boundary conditions. Related sub-records: `SPTP`, `SPTS`, `SPTL`, `SPTF`, `SPTH`.

**Syntax:**
```
SPT NO X Y Z 'REF' NREF 'FIX' BX BY T NX NY NZ SX SY SZ MREF "title"
```

| Parameter  | Type   | Unit   | Default | Description |
|------------|--------|--------|---------|-------------|
| `NO`       | int    | —      | auto    | Point number. If omitted, a new number is assigned automatically — but only if no existing point lies at the same XYZ position. A **negative** number modifies an already existing point. |
| `X`        | float  | `[m]`  | 0.0     | X-coordinate (GEO_LENGTH) |
| `Y`        | float  | `[m]`  | 0.0     | Y-coordinate (GEO_LENGTH) |
| `Z`        | float  | `[m]`  | 0.0     | Z-coordinate (GEO_LENGTH) |
| `REF`      | enum   | —      | —       | Coordinate reference / projection mode (4-char string in single quotes) |
| `NREF`     | int    | —      | —       | Identifier of the projection target (axis, area, or reference point ID) |
| `FIX`      | enum   | —      | —       | Support condition (up to 16-char literal, see below) |
| `BX`       | float  | `[m]`  | —       | Width of support / mesh region in local x-direction (GEO_LENGTH) |
| `BY`       | float  | `[m]`  | —       | Width of support / mesh region in local y-direction (GEO_LENGTH) |
| `T`        | float  | `[mm]` | —       | Plate thickness override when point lies inside a SAR (GEO_THICKNESS) |
| `NX NY NZ` | float  | —      | *       | Z-axis of the local coordinate system (normal direction) |
| `SX SY SZ` | float  | —      | *       | X-axis of the local coordinate system |
| `MREF`     | int    | —      | —       | Second reference ID — used only with `REF AXAX` (axis/axis intersection) or `REF AXAR` (axis/area intersection) |
| `XFLG`     | enum   | —      | —       | Disable automatic superposition — combinable: `P` = not replaced by coincident points; `L` = does not subdivide intersecting lines; `A` = not embedded as constraint inside a structural area |
| `TITL`     | string | —      | —       | Point description (variable-length string in double quotes) |

**REF — coordinate reference and projection mode:**

| Value  | Description |
|--------|-------------|
| `PT`   | Cartesian relative coordinates — X/Y/Z relative to reference point at `NREF` |
| `PCYL` | Cylindrical relative coordinates — X = radius, Y = rotation angle [°], Z = height |
| `PPOL` | Polar (spherical) relative coordinates — X = radius, Y = azimuth [°], Z = polar angle [°] |
| `AX`   | Project point onto geometry axis / structural line at `NREF` |
| `AXXY` | Project onto axis, constrained to the global XY-plane |
| `AXZX` | Project onto axis, constrained to the global ZX-plane |
| `AXYZ` | Project onto axis, constrained to the global YZ-plane |
| `AR`   | Project point onto geometry surface / structural area at `NREF` |
| `ARXY` | Project onto surface, constrained to XY-plane |
| `ARZX` | Project onto surface, constrained to ZX-plane |
| `ARYZ` | Project onto surface, constrained to YZ-plane |
| `AXAX` | Place point at intersection of two axes — first axis at `NREF`, second at `MREF` |
| `AXAR` | Place point at intersection of axis (`NREF`) and area (`MREF`) |

> When `REF PT/PCYL/PPOL` is used, the point inherits the local coordinate system of the reference point. The new point's coordinates are always given in the *local* coordinate system of the reference point.

**FIX — support condition:**

FIX codes are built by combining direction fixity characters. The prefix `P` = translation, `M` = rotation; suffix `X/Y/Z` = axis direction. A leading `L` switches to local directions; `G` restores global directions.

| FIX code  | Restrained DOF          | Typical use               |
|-----------|------------------------|---------------------------|
| `PP`      | All translations       | 3D pinned support         |
| `FF`      | All 6 DOF              | Fully fixed support       |
| `PZ`      | Z-translation only     | Vertical roller           |
| `PX`      | X-translation only     | Horizontal roller (X)     |
| `PY`      | Y-translation only     | Horizontal roller (Y)     |
| `PXPYPZ`  | All translations       | Explicit 3D pin           |
| `PPMX`    | Translations + rot. X  | Column base pin           |
| `MX`      | Rotation about X       | Moment fixity (X-axis)    |

> Kinematic coupling: if `FIX` contains `->n`, the DOF of the current node is coupled to node number `n`. Example: `FIX PXPY->4` couples X and Y displacements to node 4. Coupling can also be defined via the `SPTP` sub-record.

**Sub-records for SPT** (must follow immediately after the `SPT` record):
- `SPTP` — additional geometric properties or kinematic constraints (column head, coupling)
- `SPTS` — elastic spring / bedding element at the point
- `SPTL` — link element connecting two structural points
- `SPTF` — foundation geometry properties (see Advanced Commands)
- `SPTH` — halfspace pile properties (see Advanced Commands)

**Typical usage:**
```
!*!Label Structural Points with support conditions
SPT NO 1 X 0[m]  Y 0[m] Z 0[m] FIX PP        $ pinned support
SPT NO 2 X 5[m]  Y 0[m] Z 0[m] FIX PZ        $ vertical roller
SPT NO 3 X 10[m] Y 0[m] Z 0[m]               $ free node

$ Point defined relative to point 1 in local coordinates
SPT NO 4 REF PT 1 X 2.5[m] Y 0[m] Z 0[m]

$ Point projected onto geometry axis 'GAX1' in plan view
SPT NO 5 X 4[m] Y 1[m] Z 0[m] REF AXXY NREF 1
```

---

### SPTS — Spring Element at Point (sub-record of SPT)

Defines elastic spring / bedding elements at a structural point. Multiple `SPTS` records may follow a single `SPT`, allowing springs in different directions or groups. Related commands: `SPT`, `SPTL`.

**Syntax:**
```
SPTS NO REF 'TYPE' CP CQ CM DX DY DZ GRP MNO AR
     PRE GAP CRAC YIEL MUE COH DIL GAPT
```

| Parameter  | Type  | Unit         | Default | Description |
|------------|-------|--------------|---------|-------------|
| `NO`       | int   | —            | —       | Spring number |
| `REF`      | int   | —            | —       | Number of a second reference point — if given, the spring connects the current point to this reference point |
| `TYPE`     | enum  | —            | `C`     | Direction type of the spring (4-char, single quotes) |
| `CP`       | float | `[kN/m³]`    | 0.0     | Axial (principal) spring stiffness — bedding stiffness per area, scaled by `AR` (MAT_ELSUP_P3) |
| `CQ`       | float | `[kN/m³]`    | 0.0     | Isotropic lateral spring stiffness — acts equally in all directions perpendicular to axial, scaled by `AR` (MAT_ELSUP_P3) |
| `CM`       | float | `[kNm/rad]`  | 0.0     | Rotational spring stiffness about the principal axis (MAT_ELSUP_M1) |
| `DX DY DZ` | float | —            | —       | Explicit direction vector for `TYPE C` |
| `GRP`      | int   | —            | —       | Group number |
| `MNO`      | int   | —            | —       | Number of a non-linear stress-strain curve or material (from AQUA) |
| `AR`       | float | `[m²]`       | 1.0     | Reference area — scales `CP`/`CQ` from bedding stiffness [kN/m³] to point stiffness [kN/m] (GEO_AREA) |
| `PRE`      | float | `[kN/m²]`    | —       | Prestress force — spring exerts force at rest position; shifts failure and yield loads (MAT_ELSUP_P2) |
| `GAP`      | float | `[m]`        | —       | Slip gap — spring only activates after deformation exceeds this value (GEO_LENGTH) |
| `CRAC`     | float | `[kN/m²]`    | —       | Failure load — spring fails in both axial and lateral direction upon reaching this tensile force (MAT_ELSUP_P2) |
| `YIEL`     | float | `[kN/m²]`    | —       | Yield load — deformation increases without force increase beyond this value (MAT_ELSUP_P2) |
| `MUE`      | float | —            | —       | Friction coefficient — limits lateral force to `MUE × compressive_force + COH` |
| `COH`      | float | `[kN/m²]`    | —       | Cohesion for the lateral friction limit (MAT_ELSUP_P2) |
| `DIL`      | float | —            | —       | Dilatancy — a lateral displacement generates an additional axial displacement component |
| `GAPT`     | float | `[m]`        | —       | Tension gap (GEO_LENGTH) |

**TYPE — spring direction:**

| Value  | Description |
|--------|-------------|
| `CX`   | Along local x-axis of the structural point |
| `CY`   | Along local y-axis of the structural point |
| `CZ`   | Along local z-axis — **default when no direction is given** |
| `CXX`  | Along global X-axis (independent of point local system) |
| `CYY`  | Along global Y-axis |
| `CZZ`  | Along global Z-axis |
| `C`    | Along explicitly given direction vector `DX DY DZ`, or toward `REF` point if given |

**Stiffness scaling via AR:**

`CP` and `CQ` are defined as bedding stiffness per area [kN/m³]. Actual point spring stiffness [kN/m] = `CP × AR`. With the default `AR = 1.0 m²`, the values are used directly as point stiffness in [kN/m].

**Multiple springs per point — CADINP value list shorthand:**
```
SPTS TYPE CX,CY,CZ  CP 1000[kN/m3], 2000[kN/m3], 3000[kN/m3]
$ creates three orthogonal springs with individual stiffness values in one record
```

**Typical usage:**
```
$ Vertical spring foundation (Winkler spring)
SPT NO 1 X 0[m] Y 0[m] Z 0[m]
  SPTS TYPE CZZ CP 5000[kN/m3] AR 4.0[m2]   $ total stiffness = 20 000 kN/m

$ Spring between two points
SPT NO 10 X 5[m] Y 0[m] Z 0[m]
  SPTS REF 11 TYPE C CP 1000[kN/m3]

$ From the examples — directional spring with explicit vector
SPT NO 1000 X 0[m] Y 0[m] Z 0[m] FIX PXPYPZ
  SPTS DX 1 DY 0 DZ 0 CP 3000[kN/m3] CQ 0 CM 0
```

---

### SPTP — Structural Point Properties (sub-record of SPT)

Defines additional geometric properties or kinematic constraints at a structural point. Must follow immediately after the parent `SPT` record. Primarily used to model column head geometry in slab models. Related command: `SPT`.

**Syntax:**
```
SPTP 'TYPE' X Y Z REF VAL GRP
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `TYPE`    | enum   | —     | **req** | Type of property (4-char, single quotes — mandatory) |
| `X`       | float  | `[m]` | 0.0     | Local dimension or direction X (GEO_LENGTH) |
| `Y`       | float  | `[m]` | 0.0     | Local dimension Y — for `SUPP/VOUT/PNCH`: column head dimension (GEO_LENGTH) |
| `Z`       | float  | `[m]` | 0.0     | Local dimension Z (GEO_LENGTH) |
| `REF`     | int    | —     | —       | Number of a reference (coupled) structural point — required for kinematic coupling types |
| `VAL`     | float  | —     | 0.0     | Property value (e.g. plate thickness) |
| `GRP`     | int    | —     | 0       | Group number — allows multiple `SPTP` records with different group assignments |

**TYPE values:**

| Value  | Description |
|--------|-------------|
| `SUPP` | Column head support — describes the rectangular dimensions (X, Y) of a column head supporting a slab point |
| `VOUT` | Haunch — describes the dimensions of a voute region around the column head |
| `PNCH` | Punching perimeter — optionally defines custom dimensions for punching shear design |
| `KPPx`, `KPPy`, etc. | Kinematic coupling conditions — couples specific DOF of this point to the reference point at `REF` |

> For `SUPP`, `VOUT`, and `PNCH`: the mesh macro for the column head region is only generated if the point is well inside the slab and not too close to any structural edge. The number of `*` characters appended to `FIX` on the parent `SPT` controls the support modelling approach (monolithic vs. hinged).

**Typical usage:**
```
$ Column head in a flat slab
SPT NO 5 X 3[m] Y 3[m] Z 0[m] FIX PP
  SPTP TYPE SUPP X 0.4[m] Y 0.4[m]    $ 400×400 mm column head
  SPTP TYPE VOUT X 0.8[m] Y 0.8[m]    $ voute extends to 800×800 mm
```

---

### SPTL — Link Element at Point (sub-record of SPT)

Defines a link element connecting a structural point to a second reference point. The link can be assigned an arbitrary local coordinate system and a non-linear material. Must follow immediately after the parent `SPT` record. Related commands: `SPT`, `SPTS`.

**Syntax:**
```
SPTL NO REF 'TYPE' MNO GRP AREA DXX DXY DXZ DZX DZY DZZ
```

| Parameter     | Type  | Unit | Default | Description |
|---------------|-------|------|---------|-------------|
| `NO`          | int   | —    | —       | Link number |
| `REF`         | int   | —    | —       | Number of the second reference point the link connects to |
| `TYPE`        | enum  | —    | —       | Element type (4-char literal, from AQUA element type definitions) |
| `MNO`         | int   | —    | —       | Number of a stress-strain curve or material (from AQUA) |
| `GRP`         | int   | —    | —       | Group number |
| `AREA`        | float | —    | 1.0     | Reference area for stiffness scaling |
| `DXX DXY DXZ` | float | —   | *       | X-axis of the link's local coordinate system — given as a direction vector, or one of the literals: `POSX/POSY/POSZ`, `NEGX/NEGY/NEGZ`, `LOCX/LOCY/LOCZ` |
| `DZX DZY DZZ` | float | —   | *       | Z-axis of the link's local coordinate system — vector or same literals as above |

---

### SLN — Structural Line

Defines a structural line (beam, truss, cable, or area boundary edge). Start and end points can be given explicitly via `NPA`/`NPE` referencing previously defined `SPT` records, or implicitly through subsequent `SLNB`/`SLNP` sub-records, in which case structural points are created automatically at the endpoints if none exist there yet. Related sub-records: `SLNB`, `SLNP`, `SLNS`.

**Syntax:**
```
SLN NO NPA NPE REF FIX SDIV GRP 'STYP' SNO NP KR DRX DRY DRZ DROT
    EXA EYA EZA EXE EYE EZE FIXA FIXE FIMA FIME XFLG "title"
```

| Parameter      | Type   | Unit  | Default | Description |
|----------------|--------|-------|---------|-------------|
| `NO`           | int    | —     | auto    | Line number. If omitted, assigned automatically. A **negative** number modifies an existing line — only the specified parameters are changed, all others remain. |
| `NPA`          | int    | —     | —       | Start point number (references `SPT NO`) |
| `NPE`          | int    | —     | —       | End point number (references `SPT NO`) |
| `REF`          | enum   | —     | —       | Reference to a geometry axis (`GAX`) — the line geometry is taken from the referenced axis |
| `FIX`          | enum   | —     | —       | Boundary / support condition along the full line length (up to 16-char literal). Use `->n` suffix to couple DOF to reference line `n`. |
| `SDIV`         | float  | `[m]` | —       | Mesh control: **positive** = maximum element edge length [m]; **negative integer** = exact number of elements to generate. If omitted, inherits from connected SAR or global `CTRL HMIN`. |
| `GRP`          | int    | —     | —       | Group number |
| `STYP`         | string | —     | `SE`    | Two-character code: first char = element type, second char = subdivision kind (see tables below) |
| `SNO`          | int    | —     | —       | Cross-section number (from AQUA). Use `'1.2'` notation for linearly tapered section between section 1 and section 2. |
| `NP`           | int    | —     | —       | Number of bedding / bore profile |
| `KR`           | enum   | —     | —       | Local coordinate system direction specifier — literal or `PT`/`LN`/`AR` reference (see below) |
| `DRX DRY DRZ`  | float  | —     | 0.0     | Explicit direction vector for the local z- (or y-) axis of the beam coordinate system |
| `DROT`         | float  | `[°]` | 0.0     | Additional rotation of the local coordinate system about the beam axis |
| `EXA EYA EZA`  | float  | `[m]` | 0.0     | Eccentricity in global coordinates at the **start** of the line (GEO_LENGTH) |
| `EXE EYE EZE`  | float  | `[m]` | 0.0     | Eccentricity in global coordinates at the **end** of the line (GEO_LENGTH) |
| `FIXA`         | enum   | —     | —       | Hinge / release condition at the **start** node |
| `FIXE`         | enum   | —     | —       | Hinge / release condition at the **end** node |
| `FIMA`         | enum   | —     | —       | Hinge condition at **all interior start** nodes (e.g. for a hinged chain) |
| `FIME`         | enum   | —     | —       | Hinge condition at **all interior end** nodes |
| `XFLG`         | enum   | —     | —       | Intersection control — `P`/`L`/`A` to disable intersections, or hinge literals for moment release at crossing members |
| `TITL`         | string | —     | —       | Line description (variable-length, double quotes) |

**STYP — element type (first character):**

| Char | Description |
|------|-------------|
| `N`  | Centric beam — cross-section at barycenter |
| `B`  | Beam with reference axis — section at section origin |
| `O`  | Centric column — section at barycenter |
| `L`  | Column with reference axis — section at section origin |
| `T`  | Truss element (axial force only, no bending) |
| `C`  | Cable element (tension only; intersection with other elements disabled by default) |
| `S`  | Use element type defined at the cross-section — **default** |

**STYP — subdivision kind (second character):**

| Char | Description |
|------|-------------|
| `E`  | Subdivide into individual elements connected to surrounding FE-mesh — **default** |
| `X`  | Subdivide into elements without connecting to surrounding FE-mesh |
| `Y`  | Create one single element **with** beam sections |
| `Z`  | Create one single element **without** beam sections (forced for truss `T`) |

> Default `STYP SE` means: use section-defined element type, subdivide and connect to mesh.

**Local coordinate system — KR and DRX/DRY/DRZ:**

The local x-axis is always tangent to the line. The orientation of the perpendicular z-axis (or y-axis, controlled by `CTRL LOCA`) is set by:

| KR value | Description |
|----------|-------------|
| `POSX` `POSY` `POSZ` | Align local axis with positive global X/Y/Z direction |
| `NEGX` `NEGY` `NEGZ` | Align local axis with negative global X/Y/Z direction |
| `XY` `YX` | Align within global XY-plane in X- resp. Y-direction |
| `YZ` `ZY` | Align within global YZ-plane in Y- resp. Z-direction |
| `ZX` `XZ` | Align within global ZX-plane in Z- resp. X-direction |
| `PT` + NO | Align toward a structural point (NO = point number) |
| `LN` + NO | Align toward a structural line (NO = line number) |
| `AR` + NO | Align toward a structural area (NO = area number) |

If `DRX DRY DRZ` are given directly, they define the direction vector. `DROT` adds an additional rotation about the beam axis in degrees.

**Hinge conditions — FIXA, FIXE, FIMA, FIME:**

These release specific force components at the specified location. Literals define what is **released**:

| Literal | Released DOF |
|---------|-------------|
| `N`     | Normal force |
| `VY`    | Shear force Y |
| `VZ`    | Shear force Z |
| `MT`    | Torsional moment |
| `MY`    | Bending moment Y |
| `MZ`    | Bending moment Z |
| `MB`    | Warping bimoment |
| `PP`    | = N + VY + VZ |
| `MM`    | = MT + MY + MZ |

Literals can be combined freely (e.g. `MYMZ` to release both bending moments). A positive integer at `FIXA`/`FIXE` instead of a literal references a non-linear force–work law defined in AQUA (`SFLA` record).

**Intersection control — XFLG:**

- `P` — disable subdivision by structural points
- `L` — disable subdivision/replacement by other structural lines
- `A` — disable subdivision by structural areas and prevent embedding as constraining line
- Combine freely: `XFLG PLA` disables all intersections
- Hinge literals (e.g. `XFLG MM`) insert moment releases at all crossing members — applies only to internal intersections, not to endpoints

**Sub-records for SLN** (follow immediately after the parent `SLN` record):
- `SLNB` — geometry by explicit points / arc definition
- `SLNP` — freeform curve control points (spline / NURBS)
- `SLNN` — prescribed intermediate mesh nodes
- `SLNS` — supports, couplings, elastic beddings along the line
- `SLSC` — cross-section modification at a specific position

**Typical usage:**
```
!*!Label Structural Lines
$ Simple beam defined by previously created structural points
SLN NO 1 NPA 1 NPE 2 SNO 1 GRP 1

$ Truss member with explicit geometry
SLN NO 101 GRP 1 SNO 1 STYP TE            $ truss, one element
  SLNB X1 0[m] Y1 0[m] Z1 0[m] X2 2.25[m] Y2 0[m] Z2 0[m]

$ Beam with pinned ends (releases MY and MZ at both ends)
SLN NO 5 NPA 3 NPE 4 SNO 2 GRP 1 FIXA MM FIXE MM

$ Tapered beam (section 1 at start, section 2 at end)
SLN NO 10 NPA 5 NPE 6 SNO '1.2' GRP 1

$ Line with local z-axis aligned toward point 99 (e.g. for curved members)
SLN NO 20 NPA 7 NPE 8 SNO 3 KR PT 99
```

---

### SLNB — Straights and Circular Arcs (sub-record of SLN)

Defines straight lines, full circles, or circular arcs as the geometry of the preceding `SLN`. Multiple `SLNB` records can follow one `SLN` to define polycurves (chains of connected segments). Related commands: `SLN`, `SPT`.

**Syntax:**
```
SLNB X1 Y1 Z1 X2 Y2 Z2 R NX NY NZ XM YM ZM X3 Y3 Z3
```

| Parameter    | Type  | Unit  | Default | Description |
|--------------|-------|-------|---------|-------------|
| `X1 Y1 Z1`   | float | `[m]` | 0.0     | Start point coordinates (GEO_LENGTH) |
| `X2 Y2 Z2`   | float | `[m]` | 0.0     | End point coordinates (GEO_LENGTH) |
| `R`          | float | `[m]` | —       | Arc radius — omit for a straight line (GEO_LENGTH) |
| `NX NY NZ`   | float | —     | —       | Normal direction vector of the circle / arc plane |
| `XM YM ZM`   | float | `[m]` | —       | Centre point coordinates of a full circle or arc (GEO_LENGTH) |
| `X3 Y3 Z3`   | float | `[m]` | —       | Third point on arc — alternative to specifying `R` and `NX/NY/NZ` (GEO_LENGTH) |

**Geometry definition modes:**

| What to define | Required parameters |
|----------------|---------------------|
| Straight line | `X1 Y1 Z1` and `X2 Y2 Z2` |
| Full circle | `XM YM ZM` (centre) + `R` (radius) + `NX NY NZ` (plane normal) |
| Circular arc — by radius | `X1 Y1 Z1` + `X2 Y2 Z2` + `R` + `NX NY NZ` (or `XM YM ZM`) |
| Circular arc — by three points | `X1 Y1 Z1` (start) + `X2 Y2 Z2` (end) + `X3 Y3 Z3` (intermediate point on arc) |

> When building polycurves with multiple `SLNB` records, transitions between segments should have continuous tangents. Kinks are possible but can produce incorrect meshes — it is better to define two separate structural lines with a structural point at the kink location.

**Typical usage:**
```
$ Vertical post (straight line)
SLN NO 301 GRP 3 SNO 3
  SLNB X1 0[m] Y1 0[m] Z1 0[m] X2 0[m] Y2 0[m] Z2 3[m]

$ Diagonal brace
SLN NO 401 GRP 4 SNO 4
  SLNB X1 0[m] Y1 0[m] Z1 0[m] X2 4.5[m] Y2 0[m] Z2 2.5[m]

$ Circular arc defined by start, end and third point
SLN NO 50 GRP 1 SNO 1
  SLNB X1 0[m] Y1 0[m] Z1 0[m] X2 10[m] Y2 0[m] Z2 0[m] X3 5[m] Y3 2[m] Z3 0[m]
```

---

### SLNP — 3D Curve Point Data (sub-record of SLN)

Defines freeform curve geometry for the preceding `SLN` using characteristic data points. Each `SLNP` record contributes one point; multiple records form the full curve. The `TYPE` parameter set on the first `SLNP` record governs interpolation for all subsequent points of that line. Related commands: `SLN`, `SPT`.

**Syntax:**
```
SLNP X Y Z W S DX DY DZ NX NY NZ 'TYPE'
```

| Parameter  | Type  | Unit  | Default | Description |
|------------|-------|-------|---------|-------------|
| `X Y Z`    | float | `[m]` | 0.0     | 3D coordinates of the control / data point (GEO_LENGTH) |
| `W`        | float | —     | 1.0     | NURBS weight — weights ≠ 1.0 create a rational NURBS capable of representing exact circles and ellipses |
| `S`        | float | —     | —       | Explicit station (chainage) along the curve for `SPLI` and `HINT` interpolation. If omitted, SOFiMSHC assigns parametrisation automatically to minimise oscillations. |
| `DX DY DZ` | float | —     | —       | Tangential direction at this point — only used with `TYPE HINT` |
| `NX NY NZ` | float | —     | —       | Direction of the local z-axis at this point |
| `TYPE`     | enum  | —     | —       | Curve type — set once on the first `SLNP`, applies to all control points of this line |

**TYPE — curve interpolation modes:**

| Value  | Description |
|--------|-------------|
| `POLY` | Polygonal sequence — straight line segments between consecutive data points |
| `SPLI` | Cubic B-Spline interpolation — C²-continuous (curvature-continuous) at data points. Parametrisation can be set explicitly via `S`. |
| `HINT` | Hermite interpolation — piecewise cubic, C¹-continuous (tangent-continuous). Tangent directions can be set explicitly via `DX DY DZ`. |
| `NURB` | NURBS curve — control points at `X Y Z`, weights at `W`. Curve degree is set in the `SLNN` record. Supports exact circles and ellipses when `W ≠ 1.0`. |

**Typical usage:**
```
$ NURBS curve (e.g. curved top chord of a truss)
SLN NO 201 GRP 2 SNO 2
  SLNP X 0[m]    Y 0[m] Z 2.0[m] TYPE NURB
  SLNP X 2.25[m] Y 0[m] Z 2.25[m]
  SLNP X 4.50[m] Y 0[m] Z 2.50[m]
  SLNP X 6.75[m] Y 0[m] Z 2.75[m]
  SLNP X 9.00[m] Y 0[m] Z 3.00[m]

$ Spline with explicit station values
SLN NO 30 GRP 1 SNO 1
  SLNP X 0[m] Y 0[m] Z 0[m] S 0.0 TYPE SPLI
  SLNP X 3[m] Y 1[m] Z 0[m] S 3.2
  SLNP X 6[m] Y 0[m] Z 0[m] S 6.0
```

---

### SLNN — Prescribed Intermediate Node (sub-record of SLN)

Forces a mesh node at a specific position along a structural line. Used to ensure nodes at load application points or intersections.

**Syntax:**
```
SLNN S MUL DEGR
```

| Parameter | Type  | Unit | Description |
|-----------|-------|------|-------------|
| `S`       | float | `[m]`| Station (distance along line) where node is required |
| `MUL`     | float | —    | Multiplier for parametric position |
| `DEGR`    | int   | —    | Polynomial degree at this node |

**Typical usage:**
```
SLN NO 101 GRP 1 SNO 1
  SLNN S 0.0[m]    DEGR 1    $ node at start
  SLNN S 2.25[m]             $ intermediate node
  SLNN S 4.50[m]
  SLNN S 9.00[m]             $ node at end
```

---

### SLNS — Supports and Kinematic Couplings on a SLN (sub-record of SLN)

Defines boundary conditions, elastic supports/beddings, kinematic couplings, or interface elements along the preceding `SLN`. Multiple `SLNS` records may follow a single `SLN` to combine different conditions (e.g. elastic bedding and a fixed support simultaneously). Related commands: `SLN`, `SLNP`.

**Syntax:**
```
SLNS GRP FIX 'REFT' REF MNO CA CL CD KR DRX DRY DRZ DROT D BFIX FCTA FCTE 'TYPE'
```

| Parameter    | Type  | Unit           | Default  | Description |
|--------------|-------|----------------|----------|-------------|
| `GRP`        | int/enum | —           | `AUTO`   | Group number, or `AUTO` to detect automatically |
| `FIX`        | enum  | —              | —        | Boundary / coupling condition (up to 28-char literal). Prefix `L` (e.g. `LPXPY`) to interpret in the line's local coordinate system. Use `->n` to couple DOF to reference element `n`. |
| `REFT`       | enum  | —              | `>FIX`   | Support type / reference mode (see table below) |
| `REF`        | int   | —              | —        | Number of the referenced element (point, line, or area) |
| `MNO`        | int/enum | —           | —        | Material / work-law number from AQUA for non-linear spring stiffness. Use `AUTO` to automatically take the material from the adjacent structural area. A negative value forces reference to a material when a work-law with the same number also exists. |
| `CA`         | float | `[kN/m³]`      | 0.0      | Axial bedding stiffness — acts along the spring direction (MAT_ELSUP_P3) |
| `CL`         | float | `[kN/m³]`      | 0.0      | Lateral (transverse) bedding stiffness — acts in all directions perpendicular to the spring axis (MAT_ELSUP_P3) |
| `CD`         | float | `[kNm/m/rad]`  | 0.0      | Torsional (rotational) bedding stiffness about the spring axis (MAT_ELSUP_M2) |
| `KR`         | enum  | —              | —        | Direction specifier for the spring / bedding orientation (see table below) |
| `DRX DRY DRZ`| float | —              | 0.0      | Explicit global direction vector for the spring / bedding axis |
| `DROT`       | float | `[°]`          | 0.0      | Additional rotation about the structural line axis |
| `D`          | float | `[m]`          | 0.0      | Distance (gap) to the interface element — only relevant for `REFT +SAR / -SAR / *SAR` (GEO_LENGTH) |
| `BFIX`       | float | `[m]`          | 0.0      | Width of support — used to scale material bedding parameters to the actual support width (GEO_LENGTH) |
| `FCTA`       | float | —              | 1.0      | Bedding factor at the start of the line |
| `FCTE`       | float | —              | 1.0      | Bedding factor at the end of the line |
| `TYPE`       | enum  | —              | —        | Type of generated boundary element |

**REFT — support reference mode:**

| Value   | Description |
|---------|-------------|
| `>FIX`  | Absolute support — fixed to the global system — **default** |
| `>SPT`  | Kinematic coupling relative to a structural **point** at `REF` |
| `>SLN`  | Kinematic coupling relative to a structural **line** at `REF` — both lines are subdivided with equal node counts and corresponding nodes are coupled |
| `+SAR`  | Interface edge in **positive** z-direction of the line |
| `-SAR`  | Interface edge in **negative** z-direction of the line |
| `*SAR`  | Interface edges in **both** z-directions |

**KR — spring / bedding direction:**

| KR value | Description |
|----------|-------------|
| `POSX` `POSY` `POSZ` | Align along positive global X/Y/Z |
| `NEGX` `NEGY` `NEGZ` | Align along negative global X/Y/Z |
| `PT` + NO | Align toward a structural point |
| `LN` + NO | Align toward a structural line |
| `AR` + NO | Align toward a structural area |
| `LOCX`   | Along local x-axis of the line (tangential) — **default when no KR given** |
| `LOCY`   | Along local y-axis of the line (perpendicular) |
| `LOCZ`   | Along local z-axis of the line (perpendicular) — `LOCY`/`LOCZ` only valid for spring elements |

**TYPE — generated element type:**

| Value  | Description |
|--------|-------------|
| `BOUN` | Boundary element — continuous distributed bedding interpolating displacements between nodes. Generated automatically when only linear stiffness parameters are given. |
| `SPRI` | Spring elements — discrete springs at each node. Generated when non-linear parameters (from material at `MNO`) or coupled lines are used. |
| `INTF` | Rigid frictional interface elements — for non-linear contact in geotechnics (TALPA module) |

**Elastic bedding notes:**

- `CA`, `CL`, `CD` all reference an explicit direction set via `KR` / `DRX/DRY/DRZ`. If no direction is given, springs align tangentially to the line axis.
- Linear parameters → SOFiMSHC generates boundary elements (`BOUN`) by default.
- Non-linear material at `MNO`, or a coupling to another line via `REF` + `REFT >SLN` → spring elements (`SPRI`) are generated.
- A negative value at `CA`/`CL`/`CD` scales the stiffness values calculated from the material.

**Interface element notes (REFT +SAR / -SAR / *SAR):**

SOFiMSHC automatically disconnects the adjacent structural regions and creates spring elements between the coupled interface edges. The spring direction is always perpendicular to the coupled lines. A gap between the line and the interface can be specified at `D`.

**Typical usage:**
```
$ Fixed support along a line (all translations)
SLN NO 1 NPA 1 NPE 2 SNO 1 GRP 1 TITL "First support"
  SLNS FIX PP

$ Winkler elastic bedding (vertical springs, global Z)
SLN NO 10 NPA 5 NPE 6 SNO 1 GRP 2
  SLNS CA 5000[kN/m3] KR POSZ

$ Coupling two parallel lines with equal Z-displacement
SLN NO 20 NPA 7 NPE 8 SNO 1 GRP 3
  SLNS FIX PZ REFT >SLN REF 21

$ Interface along a construction joint
SLN NO 30 NPA 9 NPE 10 GRP 4
  SLNS REFT *SAR CA 500[kN/m3]
```

---

### SLSC — Beam Section Modification (sub-record of SLN)

Defines a modified cross-section property at a specific position along a structural line. Used for haunch definitions or shear checks.

**Syntax:**
```
SLSC 'REF' S 'TYPM' 'TYPT'
```

| Parameter | Type  | Unit | Description |
|-----------|-------|------|-------------|
| `REF`     | enum  | —    | Reference point for position `S` |
| `S`       | int   | —    | Station position (integer parameter) |
| `TYPM`    | enum  | —    | Section modification type (main) |
| `TYPT`    | enum  | —    | Section modification type (target) |

**REF enum values:** `STRT` (from start) | `END` (from end) | `MID` (from midpoint) | `XI` (parametric)

**TYPM / TYPT enum values:** `SECT` | `CFAC` | `HFAC` | `IFAC` | `SHEA`

---

### SAR — Structural Area

Defines a two-dimensional structural region that is meshed with quadrilateral or triangular shell/plate/membrane elements. The boundary is defined by subsequent `SARB` sub-records. If no number is given, SOFiMSHC assigns one automatically. A **negative** number modifies an existing area definition. Related sub-records: `SARB`, `SARR`, `SARS`.

**Syntax:**
```
SAR NO FIX GRP MNO MRF REF NX NY NZ NRA QREF KR DRX DRY DRZ DROT
    T TX TY TXY TD CB CT MCTL H1 H2 H3 XFLG "title"
```

| Parameter     | Type   | Unit     | Default | Description |
|---------------|--------|----------|---------|-------------|
| `NO`          | int/enum | —      | auto    | Area number, or one of the special literals `PROP` / `VOID` (see below) |
| `FIX`         | enum   | —        | *       | Boundary / support condition applied uniformly within the area (up to 8-char literal) |
| `GRP`         | int    | —        | 0       | Group number of elements in the area. For `PROP` regions: a 4-character text string assigns elements to a secondary group. |
| `MNO`         | int    | —        | 0       | Material number of QUAD elements (from AQUA) |
| `MRF`         | int    | —        | 0       | Material number for reinforcement (from AQUA) |
| `REF`         | enum   | —        | —       | Reference to a geometric surface `GAR` — if given, the area geometry is derived from this surface |
| `NX NY NZ`    | float  | —        | *       | Approximate normal direction — defines the local z-axis of plane elements (opposite side of normal). SOFiMSHC calculates the exact direction from geometry; only the intended side needs to be specified. |
| `NRA`         | int    | —        | 0/7     | **Element formulation bitmask** (0 for PROP/VOID, 7 for regular areas): `0` = geometry only (no stiffness), `+1` = plate action, `+2` = membrane action, `+4` = in-plane bending. Combine: `7` = full shell (plate + membrane + in-plane bending). |
| `QREF`        | enum   | —        | `CENT`  | Reference position for elements (see table below) |
| `KR`          | enum   | —        | *       | Local x-axis direction specifier for area elements (see table below) |
| `DRX DRY DRZ` | float  | —        | —       | Explicit direction vector for local x-axis alignment. When `KR PT/LN/AR`, `DRX` holds the referenced element number. |
| `DROT`        | float  | `[°]`    | 0.0     | Additional rotation of the element local coordinate system about the area normal |
| `T`           | float  | `[mm]`   | *       | Constant thickness override (GEO_THICKNESS). If omitted defaults to 1.0 m. Set to `0.0` to activate variable thickness from `SPT T` values or `SARB T` values. |
| `TX`          | float  | `[mm]`   | T       | Orthotropic thickness in local x-direction (GEO_THICKNESS) |
| `TY`          | float  | `[mm]`   | T       | Orthotropic thickness in local y-direction (GEO_THICKNESS) |
| `TXY`         | float  | `[mm]`   | T       | Orthotropic shear thickness (GEO_THICKNESS) |
| `TD`          | float  | `[mm]`   | T       | Orthotropic torsional thickness (GEO_THICKNESS). When orthotropic values are used, also set the average `T` for mass calculations. |
| `CB`          | float  | `[kN/m³]`| −1      | Normal subgrade bedding modulus — or a negative factor scaling the standard bedding (MAT_ELSUP_P3) |
| `CT`          | float  | `[kN/m³]`| −1      | Transverse subgrade bedding modulus — or a negative scaling factor (MAT_ELSUP_P3) |
| `MCTL`        | enum   | —        | `AUTO`  | Mesh generation control (see table below) |
| `H1`          | float  | `[m]`    | —       | Maximum element edge length within the region — overrides global `CTRL HMIN` (GEO_LENGTH) |
| `H2`          | float  | `[m]`    | —       | Mesh refinement size around structural points inside the region (GEO_LENGTH) |
| `H3`          | float  | `[m]`    | —       | Minimum element thickness of the structured boundary layer mesh at `SARB DFIX` edges (GEO_LENGTH) |
| `XFLG`        | enum   | —        | —       | Disable automatic intersection (see below) |
| `TITL`        | string | —        | —       | Area description (variable-length, double quotes) |

**NO — special area types:**

| Value  | Description |
|--------|-------------|
| *int*  | Regular structural area — meshed with shell/plate elements |
| `PROP` | Attribute region — overlaid on existing areas to change selected properties locally (MNO, MRF, T, GRP, etc.) in the intersected zone. Not meshed independently. |
| `VOID` | Opening — cuts a hole into intersected structural areas. Not meshed. |

**QREF — element reference position:**

| Value  | Description |
|--------|-------------|
| `CENT` | Elements centred on the area mid-plane — **default** |
| `ABOV` | Elements offset in negative z-direction (top face at area plane) |
| `BELO` | Elements offset in positive z-direction (bottom face at area plane) |

**KR — local element x-axis direction:**

| KR value | Description |
|----------|-------------|
| `POSX` `POSY` `POSZ` | Align local x with positive global X/Y/Z |
| `NEGX` `NEGY` `NEGZ` | Align local x with negative global X/Y/Z |
| `XY` `YX` | Align within global XY-plane in X- resp. Y-direction |
| `YZ` `ZY` | Align within global YZ-plane |
| `ZX` `XZ` | Align within global ZX-plane |
| `PT` + DRX | Align toward structural point (number given at `DRX`) |
| `LN` + DRX | Align toward structural line (number given at `DRX`) |
| `AR` + DRX | Align toward structural area (number given at `DRX`) |
| `RADI`     | When combined with `DRX/DRY/DRZ` vector: align the **radial** axis |
| `TANG`     | When combined with `DRX/DRY/DRZ` vector: align the **tangential** axis |

**MCTL — mesh generation control:**

| Value  | Description |
|--------|-------------|
| `AUTO` | Automatic unstructured mesh of quads and triangles — **default** |
| `REGM` | Regular (structured) mesh — attempted for 4-edge regions with near-rectangular shape |
| `SNGQ` | Single quad element — useful for load distribution areas with `NRA 0` (no stiffness) |
| `OFF`  | Deactivate meshing for this region |

**XFLG — disable automatic intersection:**

- `P` — structural points will no longer be added automatically as constraining points to this area
- `L` — other structural lines will no longer be added automatically as constraining lines
- `A` — this area will not be intersected with other structural areas (no automatic intersection lines)
- Combine freely: `XFLG PLA` disables all automatic intersections

> XFLG applies only to the **interior** of the area. Boundary edges and points are always processed. Use `SARB CONS` to explicitly add selected internal constraints regardless of XFLG.

**Variable thickness:**

Two approaches for non-constant thickness:
1. Set `T` values at `SARB` boundary edges — SOFiMSHC interpolates using a least-squares method across the region.
2. Place `SPT ... T value` structural points within or on the boundary of the region — requires `T 0.0` on the `SAR` record to activate.

**Sub-records for SAR** (follow immediately after the `SAR` record):
- `SARB` — boundary edge definitions (required — forms the closed outer loop and optional inner loops)
- `SARR` — rotational or sweep surface geometry
- `SARS` — distributed surface support / Winkler bedding
- `SARP` — freeform surface point data (see Advanced Commands)

**Typical usage:**
```
!*!Label Structural Areas

$ Two-span flat slab
SAR NO 1 T 220[mm] MNO 1 MRF 2 GRP 1 TITL "First span"
  SARB NL 1                  $ SOFiMSHC sorts edge orientation automatically
  SARB NL 4
  SARB NL 2
  SARB NL 6

SAR NO 2 T 250[mm] MNO 1 MRF 2 GRP 1 TITL "Second span"
  SARB NL 5
  SARB NL 3
  SARB NL 7
  SARB NL 2                  $ shared edge with area 1

$ Slab with opening
SAR NO 3 T 200[mm] MNO 1 MRF 2 GRP 1 TITL "Slab with hole"
  SARB OUT NL 10
  SARB OUT NL 11
  SARB OUT NL 12
  SARB OUT NL 13
  SARB IN  NL 20             $ inner boundary = hole
  SARB IN  NL 21
  SARB IN  NL 22
  SARB IN  NL 23

$ Attribute region overriding thickness locally
SAR NO PROP T 300[mm] TITL "Thickened zone"
  SARB NL 30
  SARB NL 31
  SARB NL 32
  SARB NL 33

$ Shell with full formulation, regular mesh, orthotropic thickness
SAR NO 10 MNO 5 GRP 2 NRA 7 MCTL REGM
    T 180[mm] TX 200[mm] TY 160[mm] TITL "Orthotropic slab"
  SARB NL 40
  SARB NL 41
  SARB NL 42
  SARB NL 43
```

---

### SARB — Structural Area Boundaries and Constraints (sub-record of SAR)

Defines one edge of the outer or inner boundary, or an internal constraint, of the preceding `SAR`. A valid area requires at least one closed outer boundary loop. Multiple `SARB` records after a single `SAR` build up the complete boundary. Related commands: `SAR`, `SLN`.

**Syntax:**
```
SARB 'TYPE' NL NP NA NE T MNO FIX DFIX CA CL CD VAXI
     CX CY CZ CMX CMY CMZ
```

| Parameter     | Type   | Unit           | Default | Description |
|---------------|--------|----------------|---------|-------------|
| `TYPE`        | enum   | —              | `OUT`   | Boundary role (see table below) |
| `NL`          | int    | —              | 0       | Number of a structural line (`SLN`) forming this edge |
| `NP`          | int    | —              | 0       | Number of a structural point (`SPT`) — used for point constraints with `TYPE CONS` |
| `NA`          | int    | —              | *       | Start point number of the edge (alternative to referencing an SLN) |
| `NE`          | int    | —              | *       | End point number of the edge |
| `T`           | float/string | `[mm]`  | *       | Thickness at this boundary edge for variable thickness interpolation (GEO_THICKNESS). Requires `T 0.0` on the parent `SAR`. Can also be a literal name of an axis variable when `VAXI` is set. |
| `MNO`         | int    | —              | 0       | Material number at boundary — for non-linear spring/bedding conditions |
| `FIX`         | enum   | —              | —       | Hinge condition releasing specific DOF along this edge. Combinable literals: `PX` `PY` `PZ` `MX` `MY` `MZ` |
| `DFIX`        | float  | `[m]`          | 0       | Distance from boundary — when set, additional internal edges are created offset into the region by this amount |
| `CA`          | float  | `[kN/m²]`      | 0       | Axial edge bedding stiffness — spring direction along the edge (MAT_ELSUP_P2) |
| `CL`          | float  | `[kN/m²]`      | 0       | Lateral edge bedding stiffness — acts equally in both local y and local z directions (MAT_ELSUP_P2) |
| `CD`          | float  | `[kNm/m/rad]`  | 0       | Torsional bedding about the edge axis (MAT_ELSUP_M2) |
| `VAXI`        | string | —              | —       | Name of an axis (4-char literal) along which a variable thickness is defined. When set, `T` holds the axis-variable name instead of a numeric value. |
| `CX`          | float  | `[kN/m²]`      | 0       | Spring stiffness along the edge (local x of the edge) — first of three independent spring sets (MAT_ELSUP_P2) |
| `CY`          | float  | `[kN/m²]`      | 0       | Spring stiffness in the area's **in-plane** direction (pointing outward from the area, local y) (MAT_ELSUP_P2) |
| `CZ`          | float  | `[kN/m²]`      | 0       | Spring stiffness in the area's **out-of-plane** direction (normal to area, local z) (MAT_ELSUP_P2) |
| `CMX`         | float  | `[kNm/m/rad]`  | 0       | Rotational spring about the edge axis (MAT_ELSUP_M2) |
| `CMY`         | float  | `[kNm/m/rad]`  | 0       | Rotational spring about the in-plane direction (MAT_ELSUP_M2) |
| `CMZ`         | float  | `[kNm/m/rad]`  | 0       | Rotational spring about the area normal (MAT_ELSUP_M2) |

**TYPE — boundary role:**

| Value  | Description |
|--------|-------------|
| `OUT`  | Outer boundary edge — forms the exterior perimeter of the area — **default** |
| `IN`   | Inner boundary edge — defines a hole or opening within the area |
| `CONS` | Internal constraint — adds a structural point (`NP`) or line (`NL`) in the interior as a mesh constraint without forming a boundary |

> **Edge ordering:** `SARB` records can be entered in any sequence and orientation. SOFiMSHC sorts and connects edges automatically, as long as common endpoints exist and a closed loop can be assembled.

> **Inner boundary (holes):** Add `SARB IN NL ...` records after the outer boundary edges. Each hole must form its own closed loop.

> **Explicit geometry not always required:** For rotational and freeform surfaces defined via `SARR` / `SARP`, SOFiMSHC can create boundary edges automatically. Explicit `SARB` records are only needed when openings, specific constraints, or edge conditions differ from the geometric extent.

**Edge spring sets — CA/CL/CD vs CX/CY/CZ:**

Two alternative approaches for edge bedding:
- `CA`/`CL`/`CD` — one spring set; `CA` acts axially along the edge, `CL` acts equally in both in-plane and out-of-plane directions.
- `CX`/`CY`/`CZ` (+ `CMX`/`CMY`/`CMZ`) — three independent spring sets; direction of `CX`/`CMX` is derived from `CY`/`CZ` orientation.

**Typical usage:**
```
$ Standard slab boundary — TYPE defaults to OUT
SAR NO 1 T 220[mm] MNO 1 MRF 2 GRP 1
  SARB NL 1
  SARB NL 4
  SARB NL 2
  SARB NL 6

$ Slab with inner hole and elastic edge support on south edge
SAR NO 2 T 200[mm] MNO 1 MRF 2 GRP 1
  SARB OUT NL 10                          $ south edge
  SARB OUT NL 11 CA 5000[kN/m2]          $ east edge — elastic spring
  SARB OUT NL 12
  SARB OUT NL 13
  SARB IN  NL 20                          $ hole boundary (closed inner loop)
  SARB IN  NL 21
  SARB IN  NL 22
  SARB IN  NL 23

$ Variable thickness — T=0 on SAR activates per-edge thickness values
SAR NO 3 T 0[mm] MNO 1 GRP 1
  SARB NL 30 T 300[mm]
  SARB NL 31 T 250[mm]
  SARB NL 32 T 200[mm]
  SARB NL 33 T 250[mm]

$ Explicit column head constraint inside a slab
SAR NO 4 T 220[mm] MNO 1 GRP 1
  SARB NL 40
  SARB NL 41
  SARB NL 42
  SARB NL 43
  SARB CONS NP 5                          $ column head point as interior constraint
```

---

### SARR — Rotational and Sweep Surfaces (sub-record of SAR)

Defines the geometry of a surface of revolution or a sweep surface for the preceding `SAR`. Only one `SARR` per structural area is allowed. When `SARR` is present, boundary edges are created automatically by SOFiMSHC — explicit `SARB` records are only needed for openings or when the boundary differs from the surface extent. Related command: `SAR`.

**Syntax:**
```
SARR 'TYPE' GID1 GID2 X Y Z NX NY NZ UMIN UMAX VMIN VMAX
```

| Parameter  | Type      | Unit  | Default | Description |
|------------|-----------|-------|---------|-------------|
| `TYPE`     | enum      | —     | `ROTA`  | Surface geometry type |
| `GID1`     | int/enum  | —     | *       | First generating curve — number of a structural line (`SLN`) or geometry curve (`GAX`) |
| `GID2`     | int/enum  | —     | —       | Second generating curve (trajectory) — only for `TYPE SWEE` |
| `X Y Z`    | float     | `[m]` | 0.0     | Reference point on the rotation axis (`ROTA`) or start point (`SWEE`) (GEO_LENGTH) |
| `NX NY NZ` | float     | —     | *       | Direction vector — rotation axis for `ROTA`, sweep direction for `SWEE` (if no `GID2`) |
| `UMIN`     | float     | —     | *       | Start parameter along the generating curve `GID1` |
| `UMAX`     | float     | —     | *       | End parameter along the generating curve `GID1`. If omitted, the whole curve is used. |
| `VMIN`     | float     | `[°]` | 0.0     | Start angle (`ROTA`) or start parameter along trajectory `GID2` (`SWEE`) |
| `VMAX`     | float     | `[°]` | *       | End angle (`ROTA`, default 180°) or end parameter along `GID2` (`SWEE`) |

**TYPE — surface geometry modes:**

| Value  | Description |
|--------|-------------|
| `ROTA` | **Surface of revolution** — generating curve `GID1` is rotated about the axis defined by point `X Y Z` and direction `NX NY NZ`. Rotation angle range: `VMIN` to `VMAX` [°]. |
| `SWEE` | **Sweep surface** — generating curve `GID1` is swept along trajectory curve `GID2`, or along direction vector `NX NY NZ` if no `GID2` is given. |

> **Closed surfaces of revolution:** Never define a full 360° rotation (e.g. 0° to 360°) as a single area — this causes numerical ambiguities. Instead, create two half-shells: one from 0° to 180° and one from 0° to −180°.

**Typical usage:**
```
$ Cylindrical shell (half-shell, 180° rotation of a vertical line)
SLN NO 100 GRP 1                         $ geometry-only line — no cross-section
  SLNB X1 5[m] Y1 0[m] Z1 0[m] X2 5[m] Y2 0[m] Z2 4[m]

SAR NO 10 MNO 1 GRP 1 NRA 7 T 200[mm] TITL "Cylindrical shell (half)"
  SARR TYPE ROTA GID1 100 X 0[m] Y 0[m] Z 0[m]
       NX 0 NY 0 NZ 1 VMIN 0 VMAX 180

$ Sweep surface along a trajectory curve
SAR NO 20 MNO 2 GRP 2 T 150[mm] TITL "Swept surface"
  SARR TYPE SWEE GID1 101 GID2 102
```

---

### SARS — Area Surface Support (sub-record of SAR)

Assigns distributed elastic support (e.g. Winkler foundation) over the full area or a portion of it. Must immediately follow the parent `SAR` record.

**Syntax:**
```
SARS 'REFT' REF 'FIX' CA CL GRP MNO D
```

| Parameter | Type  | Unit      | Default | Description |
|-----------|-------|-----------|---------|-------------|
| `REFT`    | enum  | —         | `>FIX`  | Reference type for support region (same values as `SLNS REFT`) |
| `REF`     | int   | —         | —       | Reference element ID |
| `FIX`     | enum  | —         | —       | Boundary / support condition |
| `CA`      | float | `[kN/m³]` | 0.0     | Spring stiffness normal to the surface (MAT_ELSUP_P3) |
| `CL`      | float | `[kN/m³]` | 0.0     | Spring stiffness lateral to the surface (MAT_ELSUP_P3) |
| `GRP`     | int   | —         | 0       | Group number |
| `MNO`     | int   | —         | 0       | Material number (from AQUA) |
| `D`       | float | `[m]`     | 0.0     | Gap to interface element (GEO_LENGTH) |

---

### SLVL — Structural Level

Defines a named horizontal level (storey) at a given elevation. Used for storey-based output and model organisation.

**Syntax:**
```
SLVL NO ZLVL "title"
```

| Parameter | Type   | Unit  | Description |
|-----------|--------|-------|-------------|
| `NO`      | int    | —     | Level number (optional) |
| `ZLVL`    | float  | `[m]` | Elevation of the level (GEO_ELEVATION) |
| `TITL`    | string | —     | Level description (variable-length, double quotes) |

**Typical usage:**
```
SLVL NO 1 ZLVL  0.0[m] TITL "Ground floor"
SLVL NO 2 ZLVL  3.5[m] TITL "First floor"
SLVL NO 3 ZLVL  7.0[m] TITL "Second floor"
```

---

## Advanced Commands (reference only)

The following commands exist in SOFIMSHC but are only required for specialised modelling scenarios. Do not include them unless specifically requested.

| Command | Description |
|---------|-------------|
| `SPTF`  | Foundation geometry at a structural point (type, dimensions, eccentricities) — used by the FOOTING design module |
| `SPTH`  | Halfspace pile at a structural point (cross-section, length, skin friction parameters) — used by the HASE module |
| `GAX`   | Geometry axis definition (for road/rail alignment modelling) |
| `GAXA/GAXH/GAXB/GAXC/GAXD/GAXN` | Geometry axis segment sub-records |
| `GAXP`  | Placement on geometry axis |
| `GAXS`  | Section placement on axis |
| `GAXV`  | Variable definition along axis |
| `GAR`   | Geometry surface (NURBS surface) |
| `GARA/GARC/GARS` | Geometry surface sub-records |
| `COOR`  | Coordinate system definition |
| `SVO`   | Structural volume (3D solid elements) |
| `SVOB/SVOS` | Volume boundary and surface sub-records |
| `TOWR`  | Tower/pylon geometry definition |
| `SRES`  | Support result reference |
| `XSUB`  | Sub-structure definition |
| `XCON`  | Sub-structure connection |
| `BBOX`  | Bounding box filter |
| `EVAL`  | Geometry evaluation |
| `GUID`  | Guide line reference |
| `MATT`  | Material topology mapping |

---

## Unit Summary for SOFIMSHC

| Quantity | Unit | Parameters |
|----------|------|------------|
| Coordinates, lengths, mesh sizes | `[m]` | `X Y Z`, `X1 Y1 Z1`, `HMIN`, `TOLG`, `ZLVL` |
| Slab/plate thickness | `[mm]` | `T`, `TX`, `TY`, `TXY`, `TD` on `SAR`; `T` on `SPT`, `SARB` |
| Cross-section dimensions | `[mm]` | Defined in AQUA, referenced by `SNO` |
| Elastic support (volume, per m³) | `[kN/m³]` | `CP`, `CQ`, `CA`, `CL` on `SPTS`, `SLNS`, `SARS` |
| Elastic support (area, per m²) | `[kN/m²]` | `CA`, `CL`, `CX`, `CY`, `CZ` on `SARB` |
| Rotational spring per length | `[kNm/m/rad]` | `CD`, `CMX`, `CMY`, `CMZ` on `SARB`, `SLNS` |
| Angles | `[°]` | `DROT`, `VMIN`, `VMAX` on `SARR` |
| Dimensionless relative factors | `—` | `TOLN` (FE node merge tolerance), `EFAC`, `PROG` |
