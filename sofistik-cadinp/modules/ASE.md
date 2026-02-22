# Module: ASE — Advanced Solution Engine

## Purpose

ASE performs static and dynamic structural analysis on the finite element model stored in the SOFiSTiK database. It solves linear and nonlinear systems (material and geometric nonlinearity), computes eigenvalues and buckling loads, and executes time-step dynamic integration. ASE reads loads, materials, and geometry from the database (defined by AQUA, SOFIMSHC, SOFILOAD) and writes displacements, internal forces, support reactions, and stresses back.

## Load this file when

The user needs to run a structural analysis (static, nonlinear, eigenvalue, buckling, or dynamic).

## Module block template

```
+PROG ASE urs:<n>
HEAD <description>

!*!Label Analysis
ECHO ...
CTRL ...
SYST ...
GRP  ...
LC   ...
LCC  ...
EIGE ...
STEP ...

END
```

> ASE requires a model in the database (from SOFIMSHC) and materials/sections (from AQUA) before execution.
> Loads are typically defined with SOFILOAD prior to the ASE block; ASE can also define dead load factors inline via LC.
> For nonlinear analysis (PROB NONL/TH2/TH3), iteration parameters are set in SYST and CTRL.

---

## Commands

| Command | Purpose |
|---------|---------|
| `ECHO`  | Control output verbosity per result category |
| `CTRL`  | Global analysis control options (solver, iteration, element behaviour) |
| `SYST`  | Define system type, analysis problem, tolerances, primary load case |
| `LC`    | Activate a load case with dead load factors, action type, and safety factors |
| `LCC`   | Copy loads from an existing load case into the current analysis |
| `GRP`   | Select groups, set stiffness factors, creep/shrinkage, construction stages |
| `EIGE`  | Request eigenvalue or buckling analysis |
| `STEP`  | Request time-step dynamic analysis (Newmark-Wilson integration) |

---

### ECHO — Output Control

Controls the extent of printed and stored output per result category.

**Syntax:**
```
ECHO OPT VAL
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `OPT`    | enum   | —    | `*`     | Output category to control |
| `VAL`    | enum   | —    | `*`     | Output extent |

**OPT — output category:**

| Value  | Meaning |
|--------|---------|
| `FULL` | All categories (first 20 lines if > 200) |
| `NODE` | Nodal values |
| `GRP`  | Group parameters |
| `MAT`  | Material parameters |
| `ELEM` | Element values |
| `LOAD` | Loads |
| `DISP` | Displacements |
| `FORC` | Internal forces and moments |
| `SPRI` | Spring and cable results (additive) |
| `NOST` | Internal forces at nodes |
| `BEDD` | Foundation stresses |
| `REAC` | Support reactions |
| `LINE` | Distributed support reactions |
| `PLAB` | T-beam component statistics |
| `EIGE` | Eigenvalues |
| `STEP` | Nonlinear stress print every VAL iterations |
| `RESI` | Residual forces during iteration |
| `ERIN` | Error estimates |
| `STAT` | Statistics, groups, plots |
| `NNR`  | Nodal displacements during iterations |
| `ENR`  | Element stresses during iterations |
| `LSUM` | Sum of loads, statistics, storey |
| `TEND` | Tendon group stresses |
| `BDEF` | Local beam deformations |
| `STOR` | Database storage info |

> Additional AQB-related options: `STRE`, `NSTR`, `DESI`, `REIN`, `SHEA`, `LC`, `BSEC`, `CRAC`, `C2T`, `USEP` — see AQB manual.

**VAL — output extent:**

| Value  | Meaning |
|--------|---------|
| `OFF`  | No calculation / no output |
| `NO`   | No output |
| `YES`  | Regular output |
| `FULL` | Extensive output |
| `EXTR` | Extreme output |

> The record name `ECHO` should be repeated in every ECHO record to avoid confusion.
> ECHO SPRI activates only spring/cable result printing — useful in nonlinear analysis. ECHO FORC also activates this.
> ECHO NNR xxx prints displacements of node xxx after each iteration (max 10 nodes). Only the displacement component of the current step is output (without PLC component).
> ECHO BDEF EXTR forces storage of local beam deformations; ECHO BDEF 7 also for CSM with primary load case.
> Strain energy of groups is printed only with both ECHO STAT FULL and ECHO GRP FULL. In time-step analysis ECHO GRP YES is sufficient.

**Defaults:**

```
ECHO LOAD               YES
ECHO DISP,FORC,REAC,NOST,BEDD,BDEF  NO
$ and NO for NODE and MAT, YES for all other
$
$ For small beam systems < 1000 nodes additionally:
ECHO LOAD               FULL
ECHO DISP,FORC,NOST,BEDD  NO
ECHO REAC               YES
$
$ For very small beam systems < 100 nodes additionally:
ECHO DISP,FORC          YES
```

**Typical usage:**
```
$ Suppress all output except reactions
ECHO FULL NO
ECHO REAC YES
```

---

### CTRL — Control of the Calculation

Sets global analysis control options: solver type, iteration method, element behaviour, and advanced features.

**Syntax:**
```
CTRL OPT VAL V2 V3 V4 V5 V6 V7 V8 V9 GRP V10 V11 V12 V13 V14
```

| Parameter   | Type  | Unit | Default | Description |
|-------------|-------|------|---------|-------------|
| `OPT`       | enum  | —    | —       | Control option keyword |
| `VAL`       | float | —    | —       | Primary value of the option |
| `V2`–`V9`   | float | —    | —       | Additional values (option-dependent) |
| `GRP`       | int   | —    | —       | Group number (only for CTRL CABL and CTRL SPRI) |
| `V10`–`V14` | float | —    | —       | Further values (continuation) |

**OPT — control option (primary set):**

| Value  | Meaning | Default |
|--------|---------|---------|
| `SOLV` | Solver options; 0 = suppress solution (check loads only); 999 = prevent stiffness rebuild in LC loop | — |
| `ITER` | Iteration method for residual force elimination | see below |
| `AFIX` | Handling of movable degrees of freedom | 1 |
| `SPRI` | Consideration of eccentricity of coupling springs | 8+4 |
| `CABL` | Cable sag handling for TH3 | 1 |
| `BEAM` | Beam element formulation | 3 (TH3: 5) |
| `WARP` | Warping torsion (7th DOF per node) | 0 |
| `BRIC` | BRIC element control | 4 |
| `QTYP` | QUAD + TENDON element formulation | 1 |
| `CONC` | Concrete in cracked condition (QUAD/BRIC) | — |
| `NLAY` | Number of layers for QUAD fire analysis | — |
| `ILAY` | Store inner layer stresses for WINGRAF | — |
| `FRIC` | Max shear stress for QUAD concrete rule | FBD from AQUA |
| `STII` | Linear beam stiffness factor in nonlinear analysis | 1.0 (grillage: 0.25) |
| `PLAB` | T-beam component philosophy | 7 |
| `INPL` | Inplane stiffnesses: beam-to-QUAD connection | 1 |
| `CANT` | Cantilever construction / primary displacements | 0 |
| `FIXZ` | Global/local XY constraint, membrane formfinding | 6 |
| `STEA` | Normal force stiffness component of beams (formfinding) | — |
| `QUEA` | EA part of QUAD elements (formfinding) | — |
| `DIFF` | Save difference forces between LC and PLC | — |
| `SOFT` | Replace rigid supports with soft springs | 5E7 |
| `MCON` | Consistent mass matrix activation | 2 |
| `UNRE` | BEAM prestress from TENDON: 0=both, 1=determinate, -1=indeterminate | 0 |
| `GIT`  | Nonlinear torsional stiffness reduction | — |
| `COUP` | Replace KF couplings with rigid beams (default in time-step dynamics) | — |
| `BUCK` | Auto-buckling check on TH3 instability | 1 |
| `MSTE` | Runge-Kutta steps for BRIC nonlinear material | 4 |
| `WARN` | Switch off specific error messages | — |
| `ELLA` | Compact d2 file storage control | — |
| `GRAN` | Old GRAN material model for BRIC | — |

> Additional AQB-related options: `AXIA`, `EIGE`, `AMAX`, `AGEN`, `ETOL`, `IMAX`, `SVRF`, `VRED`, `SMOO`, `VM`, `PIIA`, `INTE`, `USEP`, `VERT`, `COUN`, `ELIM`, `NLIM`, `ED` — see AQB manual.

**CTRL ITER — Iteration method:**

| VAL | Meaning |
|-----|---------|
| `0` | Crisfield method |
| `1` | Linesearch method |
| `+2`| Update tangential stiffness if required |
| `3` | Linesearch + tangential stiffness update |

> Default: PROB NONL → 0; PROB NONL with nonlinear springs → 3; PROB TH3 → 3.
> V2: stiffness update interval (V2 1 = every step). V3: AQB stiffness update interval. V4: smooth first x iterations. V5: Crisfield acceleration bits. V6: spring stiffness damping (0/1/2, default 2).

**CTRL AFIX — Movable DOF handling:**

| VAL | Meaning |
|-----|---------|
| `0` | Error on exactly movable DOF, abort |
| `1` | Error on numerically movable DOF, abort + instability check |
| `2` | Warning on exactly movable DOF, continue |
| `3` | Warning on numerically movable DOF, continue |
| `4`–`7` | As 0–3, but undefined DOF get rigid support |

> Default: 1. If solver detects instability, 6 diagnostic load cases and 3 eigenforms are computed automatically. Input ≠ 1 disables this check.

**CTRL SPRI — Spring eccentricity:**

| VAL | Meaning |
|-----|---------|
| `0` | No eccentricity, coupling springs change direction on TH3 |
| `+1`| Apply eccentricity in all cases |
| `+4`| Coupling springs keep direction on TH3 (recommended for bridge bearings) |
| `+8`| Automatic: no eccentricity for BRIC/inplane-QUAD connections |

> Default: 8+4. VAL can be set per group. V4: sliding vs stiction friction factor. V5: offset moment control for roller bearings.

**CTRL CABL — Cable handling:**

| VAL | Meaning |
|-----|---------|
| `0` | No inner cable sag |
| `1` | Cable sag on TH3 and NONB (not TH2) |
| `-1`| Cables can take compression on TH3 (CSM OPTI) |

> Default: 1. Can be defined per group.

**CTRL BEAM — Beam element:**

| VAL | Meaning |
|-----|---------|
| `2` | Simple haunched beams without implicit spring hinges |
| `3` | Complex eccentric beam with haunches, cuts, hinges, warping, tendon prestress |
| `5` | Simple prismatic beams faster; normal beams as BEAM 3 |

> Default: 3 (TH3: 5). V2: plastic interaction exponent (default 1.70).

**CTRL CONC — Concrete cracked condition:**

| VAL | Meaning |
|-----|---------|
| `0.2` | Tensile descending branch length = 0.2 ‰ |
| `0`   | Length from tensile failure energy (unlimited) |

> V2: max compressive stress limit (0=no limit, 1=uniaxial). V3: tensile strength fct for tension stiffening. V4: fctk for pure concrete layers. V5: tension stiffening method (525=EC2, 400=old). V6: transverse tension reduction (%). V7: singular punching node handling. V8: nonlinear creep. V9: skew crack width.

**CTRL CANT — Cantilever construction:**

| VAL | Meaning |
|-----|---------|
| `0` | No action |
| `1` | Consider displacements only |
| `2` | Consider displacements and rotations (tangential cantilevering) |
| `3` | Adapt new segment in shop shape (CSM only) |
| `4` | Fit final segment |
| `5`–`7` | As 1–3 but retain XY position |
| `11`–`12` | As 1–2 but add nodes individually (in-situ slab on deformed grillage) |
| `21`–`22` | As 11–12 without couplings |

> Default: 0. CANT > 0 sets CTRL INPL to 0.

**Typical usage:**
```
$ Nonlinear iteration with stiffness update
CTRL ITER 3 V2 1
$
$ Activate warping torsion
CTRL WARP 1
$
$ Concrete cracked with tension stiffening
CTRL CONC 0.2
```

---

### SYST — Global Control Parameters

Defines the analysis system type, problem class, iteration limits, primary load case, and material nonlinearity.

**Syntax:**
```
SYST TYPE PROB ITER TOL FMAX FMIN EMAX EMIN PLC FACV VMAX NMAT STOR
     CAMB TOL4 TOL8 POST FMA4 FMA8
```

| Parameter | Type  | Unit              | Default | Description |
|-----------|-------|-------------------|---------|-------------|
| `TYPE`    | enum  | —                 | `*`     | System type (taken from generation program) |
| `PROB`    | enum  | —                 | `LINE`  | Analysis problem type |
| `ITER`    | int   | —                 | `90`    | Maximum number of iterations |
| `TOL`     | float | `[-]`             | `0.001` | Iteration tolerance (relative to max load; negative = absolute in kN) |
| `TOL4`    | float | `[-]`             | `*`     | Tolerance after 40 % of iterations |
| `TOL8`    | float | `[-]`             | `*`     | Tolerance after 80 % of iterations |
| `FMAX`    | float | `[-]`             | `4.00`  | Max f-value Crisfield method (> 0.25) |
| `FMIN`    | float | `[-]`             | `0.25`  | Min f-value Crisfield method (> 0.1) |
| `EMAX`    | float | `[-]`             | `*`     | Max e-value Crisfield method |
| `EMIN`    | float | `[-]`             | `*`     | Min e-value Crisfield method |
| `PLC`     | int   | —                 | `*`     | Primary load case number |
| `FACV`    | float | `[-]`             | `*`     | Factor for PLC displacements (default 1.0; buckling: 0.0) |
| `VMAX`    | float | `[-]`             | `*`     | Imperfection scaling factor |
| `NMAT`    | enum  | —                 | `NO`    | Nonlinear material for QUAD and BRIC elements |
| `STOR`    | enum  | —                 | `NO`    | Geometry update mode |
| `CAMB`    | float | —                 | `*`     | Precamber (CSM connection) |
| `POST`    | float | —                 | `0`     | Post-iteration (1 = re-iterate on converged result) |
| `FMA4`    | float | `[-]`             | `*`     | Lower FMAX from 0.4·ITER to 0.6·ITER |
| `FMA8`    | float | `[-]`             | `*`     | Lower FMAX after 0.8·ITER |

**TYPE — system type:**

| Value  | Meaning |
|--------|---------|
| `*`    | Taken from generation program (default) |
| `SPAC` | 3D space system |
| `FRAM` | Frame system |
| `PLAN` | Plane system |
| `GIRD` | Grillage system |

**PROB — analysis problem type:**

| Value  | Meaning |
|--------|---------|
| `LINE` | Linear analysis |
| `NONL` | Material nonlinear: springs, cable failure, bedding cutoff. Cracked QUAD/BRIC require additional NMAT YES |
| `NONB` | As NONL + cables with inner sag (cable-stayed bridges) |
| `TH2`  | Second-order theory (P-Δ for columns and frames) |
| `TH3`  | Full geometric nonlinear: equilibrium in deformed shape, buckling, snap-through |
| `TH3B` | Limited TH3: full nonlinear only for cables, trusses, springs; beams and QUADs use TH2 |
| `LIFT` | Plates with lifting corners (nonlinear supports) |

**NMAT — material nonlinearity:**

| Value | Meaning |
|-------|---------|
| `NO`  | QUAD and BRIC material behaves linear |
| `YES` | Nonlinear material used if available (QUAD: concrete/steel/textile; BRIC: soil) |

**STOR — geometry update:**

| Value  | Meaning |
|--------|---------|
| `NO`   | No geometry update |
| `YES`  | Store deformed mesh; local QUAD axes rotated by PLC rotations |
| `NEW`  | Redefine local coordinate systems; update beam lengths for loading |
| `XX`, `YY`, `ZZ` | Preset local x-axis direction for new QUAD coordinate systems |
| `NEGX`, `NEGY`, `NEGZ` | Negative axis presets |
| `UX`, `UY`, `UZ` | Update only specific displacement component |
| `ACAD` | Export deformed mesh as DXF file |
| `CUTT` | Export membrane cutting pattern as DXF |

> Caution: geometry update deletes all displacement results — save the database before! STOR=NEW deletes all results because local directions change.
> Imperfection: SYST PLC 101 FACV - VMAX 0.05 sets PLC 101 displacements with max 5 cm spatial deformation. FACV -1/-2/-3 controls scaling direction.

**Typical usage:**
```
$ Linear analysis
SYST PROB LINE

$ Second-order analysis on primary load case 1
SYST PROB TH2 PLC 1

$ Full geometric nonlinear with material nonlinearity
SYST PROB TH3 ITER 50 TOL 0.01 NMAT YES
```

---

### LC — Load Case and Masses

Activates a load case for analysis with optional dead load factors, load case title, action type and safety factors for later superposition.

**Syntax:**
```
LC   NO  FACT FACD DLX DLY DLZ BET2
     TITL
     TYPE GAMU GAMF PSI0 PSI1 PSI2 PS1S GAMA CRI1 CRI2 CRI3
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `NO`      | int    | —    | —       | Load case number |
| `FACT`    | float  | `[-]`| `1.0`   | Factor for all loads (not temperature/strain/prestress/dead load) |
| `FACD`    | float  | `[-]`| `0.0`   | Factor dead load in gravity direction (like SOFILOAD) |
| `DLX`     | float  | `[-]`| `0.0`   | Factor dead load in global X (earthquake) |
| `DLY`     | float  | `[-]`| `0.0`   | Factor dead load in global Y |
| `DLZ`     | float  | `[-]`| `0.0`   | Factor dead load in gravity direction Z (input positive!) |
| `BET2`    | float  | `[-]`| `0.5`   | Coefficient for crack width: 0.5 = long-term, 1.0 = short-term |
| `TITL`    | string | —    | `*`     | Load case designation (auto-generated from DL factors if omitted) |
| `TYPE`    | enum   | —    | `*`     | Action type for superposition with MAXIMA |
| `GAMU`    | float  | `[-]`| `*`     | Unfavourable safety factor γ_sup |
| `GAMF`    | float  | `[-]`| `*`     | Favourable safety factor γ_inf |
| `PSI0`    | float  | `[-]`| `*`     | Combination coefficient ψ₀ (rare) |
| `PSI1`    | float  | `[-]`| `*`     | Combination coefficient ψ₁ (frequent) |
| `PSI2`    | float  | `[-]`| `*`     | Combination coefficient ψ₂ (quasi-permanent) |
| `PS1S`    | float  | `[-]`| `*`     | Non-frequent combination coefficient |
| `GAMA`    | float  | `[-]`| `*`     | Accidental safety factor |
| `CRI1`    | float  | `[-]`| `0`     | Criterion 1 (nonlinear: iterations count; eigenvalue: modal rotation mass X) |
| `CRI2`    | float  | `[-]`| `0`     | Criterion 2 (nonlinear: max residual force) |
| `CRI3`    | float  | `[-]`| `0`     | Criterion 3 (nonlinear: energy) |

**NO — special values:**

| Value  | Meaning |
|--------|---------|
| `ALL`  | Calculate all load cases in database (LC 1–9999) |
| `TEST` | Run instability test |
| `ITER` | All load cases from CSM-OPTI |

> LC activates a load case. All loads input after the LC record are assigned to this load case.
> FACT does not affect temperature, strain, prestress, or dead load factors (DLX/DLY/DLZ/FACD). Loads are saved in the database without factor.
> Use FACD for dead load — it works like SOFILOAD (positive = gravity direction). DLZ requires positive input even if Z-axis points upward.
> If only NO is input (no factors, no loads after LC), loads from SOFILOAD are used. If factors or new loads are defined, all existing loads for that LC are deleted and redefined.
> For eigenvalue analysis, dead load masses are always included from material γ — no DLZ input needed.
> TYPE, GAMU–PS1S define action type and superposition factors for MAXIMA. If defined in SOFILOAD/MAXIMA, omit here.

**Typical usage:**
```
$ Simple dead load case
LC 1 FACD 1.0 TITL 'Dead load'

$ Dead load + imposed load from SOFILOAD
LC 1 FACD 1.0
LC 2

$ Define action type for superposition
LC 1 TYPE G   GAMU 1.35 GAMF 1.00

$ Calculate all existing load cases
LC ALL
```

---

### LCC — Copy of Loads

Copies loads from an already defined load case into the current analysis. Also controls ultimate load iteration and temperature/strain load filtering.

**Syntax:**
```
LCC NO FACT NOG NFRO NTO NINC ULTI PLC
```

| Parameter | Type  | Unit | Default | Description |
|-----------|-------|------|---------|-------------|
| `NO`      | int   | —    | —       | Number of an already defined load case |
| `FACT`    | float | `[-]`| `1.0`   | Load factor |
| `NOG`     | float | —    | `*`     | Group number filter |
| `NFRO`    | float | —    | `*`     | From load case number (range) |
| `NTO`     | float | —    | `*`     | To load case number (range) |
| `NINC`    | float | —    | `*`     | Load case increment (range) |
| `ULTI`    | enum  | —    | `YES`   | Ultimate load iteration factor |
| `PLC`     | int   | —    | `NEW`   | Temperature/strain load handling for PLC |

**NO — special values:**

| Value  | Meaning |
|--------|---------|
| `ITER` | All load cases from CSM-OPTI |

**ULTI — ultimate load iteration:**

| Value | Meaning |
|-------|---------|
| `YES` | Load is increased during ultimate load iteration |
| `OFF` | Load is not increased |
| `ALL` | All loads including temperature/prestress/settlements are increased |

**PLC — temperature/strain loads for primary load cases:**

| Value | Meaning |
|-------|---------|
| `YES` | Filter out temperature/strain loads (LC was already active in PLC) |
| `NEW` | Use all loads (load acts for the first time) |

> LCC copies loads from other load cases into the current LC. Prestress loads from TENDON are included.
> Copied load cases should not include dead weight factors — use LC DLX/DLY/DLZ/FACD instead.
> If a load case was already in the PLC, use PLC YES to filter temperature/strain loads (they would act twice otherwise).
> In dynamic time-step analysis, SOFILOAD time functions are applied using the time at the end of the current interval.

**Typical usage:**
```
$ Copy load case 1 with factor 1.0
LCC 1

$ Copy with load increase disabled (pushover)
LCC 1 ULTI OFF

$ Copy with temperature filtering (already in PLC)
LCC 1 PLC YES
```

---

### GRP — Group Selection Elements

Selects participating element groups, defines stiffness factors, primary stress state, creep/shrinkage parameters, and construction stage settings.

**Syntax:**
```
GRP NO VAL FACS PLC GAM H K SIGN SIGH FACL FACD FACP FACT
    HW GAMA RADA RADB MODD CS PREX PREY PHI EPS RELZ PHIF PHIS
    T1 HING FACB CSDL MNO
```

| Parameter | Type   | Unit        | Default   | Description |
|-----------|--------|-------------|-----------|-------------|
| `NO`      | int    | —           | `*`       | Group number (- or omit = all groups) |
| `VAL`     | enum   | —           | `FULL`    | Group selection mode |
| `FACS`    | float  | `[-]`       | `*`       | Factor for group stiffness |
| `PLC`     | float  | —           | `*`       | Primary load case number (default from SYST) |
| `GAM`     | float  | `[kN/m³]`   | `0`       | Additional analytical primary state: unit weight |
| `H`       | float  | `[m]`       | `0`       | Analytical primary state: reference height |
| `K`       | float  | `[-]`       | `1`       | Lateral earth pressure coefficient |
| `SIGN`    | int    | `[kN/m²]`   | `0`       | σ_z = GAM·(Z−H) + SIGN |
| `SIGH`    | float  | `[kN/m²]`   | `0`       | σ_x = σ_y = K·σ_z + SIGH |
| `FACL`    | float  | `[-]`       | `1`       | Factor for stresses from PLC |
| `FACD`    | float  | `[-]`       | `0`       | Factor dead weight in gravity direction |
| `HW`      | float  | `[m]`       | `±99999`  | Ground water level ordinate |
| `GAMA`    | float  | `[kN/m³]`   | `γ−10`    | Submerged unit weight |
| `RADA`    | float  | `[1/s]`     | `0`       | Rayleigh damping: mass-proportional factor |
| `RADB`    | float  | `[s]`       | `0`       | Rayleigh damping: stiffness-proportional factor |
| `CS`      | int    | —           | `*`       | Construction stage number for sections + tendons |
| `PREX`    | float  | `[kN,m]`    | `0`       | Element prestress in local x (kN for beams, kN/m for QUADs) |
| `PREY`    | float  | `[kN,m]`    | `0`       | QUAD prestress in local y direction |
| `PHI`     | float  | `[-]`       | `0`       | Creep coefficient |
| `EPS`     | float  | `[-]`       | `0`       | Shrinkage coefficient |
| `RELZ`    | float  | `[-]`       | `0`       | Prestressing steel relaxation (0.03 = 3 % loss; AUTO = automatic) |
| `PHIF`    | float  | `[-]`       | `PHI`     | Creep coefficient for springs, bedding, FLEX, HASE |
| `PHIS`    | float  | `[-]`       | `0`       | Creep coefficient for non-concrete elements (composite) |
| `T1`      | float  | `[days]`    | `*`       | Modified concrete age for stiffness development |
| `HING`    | enum   | —           | `ACTI`    | Beam pin-joint activation |
| `FACB`    | float  | `[-]`       | `FACS`    | Factor for pile and QUAD bedding |
| `CSDL`    | float  | —           | `*`       | Dead load of a later construction stage |
| `MNO`     | float  | —           | `*`       | Material number for PHI/EPS (mixed groups in CSM) |

**VAL — group selection:**

| Value  | Meaning |
|--------|---------|
| `OFF`  | Group not used |
| `YES`  | Group used but not printed |
| `FULL` | Group used and printed |
| `LIN`  | YES, but material linear |
| `LINE` | FULL, but material linear (TH2/TH3 unaffected) |
| `GLIN` | Geometric linear (special) |

**CS — construction stage (special values):**

| Value  | Meaning |
|--------|---------|
| `BOND` | Tendons bonded if possible (= CS 9998) |
| `NONE` | Without tendon area, unbonded (= CS 9999) |

**HING — beam pin-joint:**

| Value  | Meaning |
|--------|---------|
| `ACTI` | Pin-joints active |
| `FIX`  | Pin-joints fixed (rigid connection) |

> GRP - or GRP without number = defaults for all groups. Following GRP records for specific groups overwrite these defaults.
> GRP prestress (PREX/PREY) acts also in linear analysis and eigenvalue analysis.
> PREX/PREY: kN for beams/trusses/cables/springs, kN/m for QUADs.
> For composite systems: concrete elements use PHI/EPS; springs/bedding use PHIF; non-concrete elements use PHIS with shrinkage = EPS·PHIS/PHI.
> RELZ AUTO with time input T in CREP record determines prestressing steel relaxation automatically.

**Typical usage:**
```
$ All groups active, dead load factor 1.0
GRP - FULL FACD 1.0

$ Deactivate group 3
GRP 3 OFF

$ Creep and shrinkage
GRP - PHI 2.0 EPS -0.0005

$ Construction stage with stiffness reduction
GRP 5 FACS 0.5 CS 10
```

---

### EIGE — Eigenvalues and Eigenvectors

Requests eigenvalue or buckling analysis and stores mode shapes as load cases.

**Syntax:**
```
EIGE NEIG ETYP NITE MITE LMIN SAVE LC UNIF OPT
```

| Parameter | Type  | Unit            | Default | Description |
|-----------|-------|-----------------|---------|-------------|
| `NEIG`    | int   | —               | —       | Number of sought eigenvalues (required) |
| `ETYP`    | enum  | —               | `LANC`  | Eigenvalue solver method |
| `NITE`    | int   | —               | `*`     | Number of iteration / Lanczos vectors (default: min(NEIG+2, n_unknowns)) |
| `MITE`    | int   | —               | `*`     | Maximum number of iterations |
| `LMIN`    | float | `[-]` or `[rad²/s²]` | `0`| Eigenvalue shift (AUTO = find first positive buckling eigenvalue) |
| `SAVE`    | float | —               | `*`     | Number of generated load cases |
| `LC`      | int   | —               | `2001`  | Load case number of the smallest eigenmode shape |
| `UNIF`    | enum  | —               | `*`     | Unit/format options |
| `OPT`     | float | —               | `*`     | Options (1 = include missing mass, see DYNA) |

**ETYP — eigenvalue solver:**

| Value  | Meaning |
|--------|---------|
| `LANC` | Lanczos method (recommended for dynamic eigenvalues) |
| `SIMU` | Simultaneous vector iteration |
| `BUCK` | Buckling eigenvalue — simultaneous vector iteration |

> EIGE triggers eigenvalue/buckling analysis. Mode shapes are stored as consecutive load cases starting from LC.
> For dynamic eigenvalues, masses from dead load γ are always included. Additional masses via MASS record.
> SYST PLC adds geometric stiffness to dynamic eigenvalue analysis.
> LMIN AUTO is used for buckling analysis to find the first positive eigenvalue when only negative ones appear.
> For dynamic eigenvalues, do not change ETYP — LANC is usually optimal. Increase NITE for better accuracy with small NEIG.

**Typical usage:**
```
$ 10 dynamic eigenvalues
EIGE 10

$ 6 buckling eigenvalues starting at LC 3001
EIGE 6 ETYP BUCK LC 3001

$ Buckling with automatic shift to find first positive
EIGE 6 ETYP BUCK LMIN AUTO
```

---

### STEP — Time Step Method Dynamics

Defines a time-step dynamic analysis segment using direct Newmark-Wilson integration.

**Syntax:**
```
STEP N DT INT ALF DEL THE LCST SELE DIV BET ALF2 ALF3 LCSM
```

| Parameter | Type   | Unit   | Default | Description |
|-----------|--------|--------|---------|-------------|
| `N`       | int    | —      | —       | Number of time steps (required) |
| `DT`      | float  | `[s]`  | —       | Time step size (required) |
| `INT`     | int    | —      | `1`     | Output interval (every INT steps) |
| `BET`     | float  | `[-]`  | `0.40`  | Newmark β parameter |
| `DEL`     | float  | `[-]`  | `0.55`  | Newmark δ parameter |
| `THE`     | float  | `[-]`  | `1.0`   | Alpha method parameter (Hilber-Hughes-Taylor: THE = 1−|α|) |
| `LCST`    | int    | —      | `*`     | Storage load case number (CONT = append on PLC sequence) |
| `SELE`    | int    | —      | `*`     | Bitmask for result selection (default: all) |
| `DIV`     | int    | —      | `0`     | Time step division control |
| `ALF`     | float  | `[-]`  | `*`     | Old input — use BET instead |
| `ALF2`    | float  | `[-]`  | `*`     | Alpha 2 (not commonly used) |
| `ALF3`    | float  | `[-]`  | `*`     | Alpha 3 (not commonly used) |
| `LCSM`    | int    | —      | `*`     | Storage LC for min/max envelope of all steps |

**LCST — special values:**

| Value  | Meaning |
|--------|---------|
| `CONT` | Append results on PLC load case sequence |

**SELE — result selection bitmask:**

| Bit    | Value   | Result type |
|--------|---------|-------------|
| +1     | `1`     | Displacements |
| +2     | `2`     | Support reactions |
| +3     | `4`     | Velocities |
| +4     | `8`     | Accelerations |
| +5     | `16`    | Beam internal forces |
| +6     | `32`    | Nonlinear beam results |
| +7     | `64`    | Spring results |
| +8     | `128`   | Truss + cable + boundary results |
| +9     | `256`   | QUAD results |
| +10    | `512`   | QUAD results in nodes |
| +11    | `1024`  | Nonlinear QUAD results |
| +12    | `2048`  | Foundation results |
| +13    | `4096`  | BRIC results |
| +14    | `8192`  | BRIC results in nodes |
| +15    | `16384` | Loads |

**DIV — time step division:**

| Value    | Meaning |
|----------|---------|
| `0`      | No division |
| `1`–`9`  | Divide up to DIV times; output for original steps only |
| `11`–`19`| Divide and store all sub-steps (variable Δt in LC sequence) |
| negative | Continue after reaching smallest step even without equilibrium |

> STEP triggers Newmark-Wilson direct integration over N·DT seconds.
> Default BET/DEL/THE provides numerical damping of high frequencies for nonlinear analysis.
> Recommended for nonlinear dynamics: THE 0.70 or BET 0.40 DEL 0.55 THE 1.0.
> Original Newmark (no damping): BET 0.25 DEL 0.50 THE 1.0.
> Damping parameters are set per group in GRP (RADA, RADB).
> To avoid huge databases: LCST controls storage. With N > 1 and LCST, only two alternating LCs are used internally; important results go to LCST via SELE bitmask.
> LCSM stores min/max envelope: base-100 number (e.g. 9900) stores with corresponding values; non-100 number (e.g. 9901) stores mixed extremes.
> Typically: compute static state first as separate LC, then use as PLC for dynamic analysis.

**Typical usage:**
```
$ 100 time steps of 0.01s, store to LC 1001
SYST PLC 1
STEP 100 DT 0.01 LCST 1001
LC 2 FACD 1.0

$ Nonlinear dynamics with HHT-alpha
STEP 200 DT 0.005 THE 0.70 LCST 2001

$ Store only displacements and reactions
STEP 50 DT 0.02 LCST 3001 SELE 3

$ Time step division for convergence
STEP 100 DT 0.01 LCST 1001 DIV -2
```

---

## Complete ASE Block Example

```
+PROG ASE urs:1
HEAD 'Linear static analysis — dead load and imposed load'

!*!Label Output Control
ECHO FULL NO
ECHO REAC FULL
ECHO FORC YES
ECHO DISP YES

!*!Label System
SYST PROB LINE

!*!Label Groups
GRP - FULL

!*!Label Load Cases
LC 1 FACD 1.0 TITL 'Dead load'
LC 2              $ Imposed load from SOFILOAD

END
```

```
+PROG ASE urs:2
HEAD 'Second-order analysis with primary load case'

!*!Label Output
ECHO FULL NO
ECHO REAC YES
ECHO FORC YES
ECHO DISP YES

!*!Label System
SYST PROB TH2 PLC 1

!*!Label Groups
GRP - FULL

!*!Label Load Cases
LC 10 FACD 1.0
LCC 2

END
```

```
+PROG ASE urs:3
HEAD 'Eigenvalue analysis — 10 dynamic modes'

ECHO EIGE FULL

SYST PROB LINE

EIGE 10 ETYP LANC LC 2001

END
```

---

## Unit Summary for ASE

| Quantity | Unit | Parameters |
|----------|------|------------|
| Stiffness factor | `[-]` | FACS, FACL, FACD, FACB, FACT, FACV |
| Tolerance | `[-]` | TOL, TOL4, TOL8 |
| Unit weight | `[kN/m³]` | GAM, GAMA |
| Height / elevation | `[m]` | H, HW |
| Stress | `[kN/m²]` | SIGN, SIGH |
| Prestress | `[kN]` or `[kN/m]` | PREX, PREY |
| Damping (mass) | `[1/s]` | RADA |
| Damping (stiffness) | `[s]` | RADB |
| Time | `[s]` | DT |
| Age | `[days]` | T1 |
| Creep / shrinkage | `[-]` | PHI, EPS, RELZ, PHIF, PHIS |
| Combination factors | `[-]` | GAMU, GAMF, PSI0, PSI1, PSI2, PS1S, GAMA |
| Eigenvalue shift | `[-]` or `[rad²/s²]` | LMIN |
