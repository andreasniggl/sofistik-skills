# Module: AQB — Design of Cross-Sections

## Purpose

AQB performs cross-section design for reinforced concrete, prestressed concrete, structural steel, composite and timber sections defined in AQUA. It evaluates elastic stresses (`STRE`), required reinforcement for bending, axial force and shear (`DESI`), non-linear stresses and strains including crack width and fatigue (`NSTR`), internal stresses from creep and shrinkage (`EIGE`, AQBS only) and sectional capacities / interaction diagrams (`CAPA`). The internal forces are either taken from the database (results of ASE, superpositions of MAXIMA, combination load cases from SOFILOAD) or defined directly with the `S` record for a stand-alone section check. The design code is always taken from the `NORM` record in AQUA — AQB has no NORM record of its own.

## Load this file when

The user requests an RC, prestressed, steel, composite or timber **section design / section check** — either for a single cross-section with given internal forces (AQUA + AQB) or, most commonly, for the members of a full structural system (AQUA + SOFIMSHC + SOFILOAD + ASE + MAXIMA + AQB).

## Prerequisites

| Workflow | Required modules before AQB |
|----------|-----------------------------|
| **Stand-alone section design** (forces known) | **AQUA** — `NORM`, materials, cross-section with reinforcement layout (`SREC` with `MRF`, cover `SO`/`SU`, or `SECT` with reinforcement layers) |
| **Section design on a full system** (default case) | **AQUA** → **SOFIMSHC** → **SOFILOAD** → **ASE** → load combinations (**MAXIMA** superposition *or* combination load cases defined in **SOFILOAD** and analysed in **ASE**) |

> AQB designs the **beam elements** of the database (default `BEAM TYPE BEAM`), design elements (`DSLN`/`DBEA`/`DCOL`, created by DECREATOR) or external sections. It does **not** design shell (QUAD) elements — use BEMESS for slabs and walls.

> Before generating a full-system AQB workflow, the superposition strategy must be agreed with the user (question in `SKILL.md`, details in `SUPERPOSITION_STRATEGY.md`): automatic envelopes with **MAXIMA** (linear analysis) or explicit combination load cases in **SOFILOAD** (required for non-linear analysis).

## Module block template

```
+PROG AQB urs:<n>
HEAD <description>

!*!Label Output Control
ECHO FULL NO
ECHO DESI YES

!*!Label Control
CTRL VM STD                        $ shift rule offset for tensile force envelope

!*!Label Load Case Selection
LC TYPE (D)                        $ all ULS design combination load cases

!*!Label Reinforcement Case
REIN MOD SECT RMOD SAVE LCR 1      $ save as global minimum reinforcement

!*!Label Design
DESI STAT ULTI                     $ ULS bending, axial force and shear design

END
```

> **Key rules:**
> - AQB uses the design code from AQUA `NORM` — never write a `NORM` record in AQB.
> - **Every design task (`DESI`, `NSTR`, `STRE`, `EIGE`, `CAPA`) acts on the load cases / combinations selected before it.** Place `BEAM`, `LC`, `S`, `COMB`, `REIN` and `CTRL` records **before** the design task record.
> - `DESI STAT ULTI` requires **factored** (design) internal forces. Select only ULS combination load cases (e.g. `LC TYPE (D)`, MAXIMA results of `COMB ... EXTR DESI`, SOFILOAD combinations with `TYPE (D)`), or build factored combinations with AQB `COMB`.
> - If no `LC` record is given, AQB designs **all** load cases in the database individually — always select load cases explicitly.
> - The record name `ECHO` must be repeated for every ECHO record (no ECHO continuation lines) to avoid ambiguity with record names.
> - Only one element type can be processed per AQB block (`BEAM` type selection); define `BEAM` before `LC`.
> - Serviceability checks (`NSTR` crack width) need a reinforcement: run the ULS design first with `REIN ... RMOD SAVE LCR n` and perform `NSTR` in a **subsequent** `+PROG AQB` block.
> - Use a separate `+PROG AQB` block for each design step (ULS design, SLS crack width, stress check). This keeps the load case selection unambiguous.

---

## Commands

| Command | Purpose |
|---------|---------|
| `ECHO`  | Control of the extent of output |
| `CTRL`  | Control of the calculation (design type, forces, analysis options) |
| `TVAR`  | Temporary values of national parameters (boxed values) for the design |
| `BEAM`  | Selection of elements / sections to be designed; construction stages; given reinforcement |
| `TEND`  | Tendons for external sections (AQBS only) |
| `LC`    | Selection of the load cases to be designed |
| `S`     | Internal forces and moments for a stand-alone design |
| `COMB`  | Definition of load case combinations inside AQB |
| `EIGE`  | Internal stresses from creep, shrinkage and relaxation (AQBS only) |
| `STRE`  | Linear (elastic) stresses and plastic resistances (steel, timber, prestressed checks) |
| `REIN`  | Specification of the reinforcement case (LCR) and its distribution |
| `DESI`  | Reinforced concrete design — bending, axial force and shear |
| `NSTR`  | Non-linear stresses and strains, crack width, fatigue, stiffness |
| `CAPA`  | Sectional capacity evaluation (N–M interaction, moment–curvature) |

---

### ECHO — Control of the Extent of Output

Controls the volume of printed output per result category.

**Syntax:**
```
ECHO OPT VAL SELE
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `OPT`     | enum   | —    | `FULL`  | Output category (see table below) |
| `VAL`     | enum   | —    | `FULL`  | Output extent (see table below) |
| `SELE`    | string | —    | `*`     | Output mask (up to 4 characters, wildcards `*` and `?`) for section parts marked in AQUA |

**OPT — output categories:**

| Value  | Meaning |
|--------|---------|
| `SECT` | Static properties of section |
| `FORC` | Forces and moments |
| `COMB` | Combinations and their forces |
| `STRE` | Elastic stresses |
| `DESI` | Design |
| `NSTR` | Non-linear stresses |
| `EIGE` | Internal stresses (creep and shrinkage) |
| `SHEA` | Shear design |
| `CRAC` | Limitation of crack width |
| `FAT`  | Fatigue design |
| `C2T`  | c/t slenderness ratio (steel plates) |
| `USEP` | Used utilisation factors |
| `REIN` | Reinforcements |
| `TABS` | Tabular summaries of stresses (bit-coded: `TEND` 1, `SIG` 2, `TAU` 4, `FAT` 8) |
| `SSUM` | Maximum forces and moments per section |
| `LC`   | Individual load cases |
| `BSEC` | Sections |
| `STAT` | Overview of CPU time |
| `FULL` | All options except `LC` and `BSEC` |

**VAL — output extent:**

| Value  | Meaning |
|--------|---------|
| `OFF`  | Nothing computed / printed |
| `NO`   | No output |
| `YES`  | Standard output (default in general) |
| `FULL` | Full output |
| `EXTR` | Extended output |

> Special values exist for some options: `ECHO FORC COMP` (composite, AQBS), `ECHO STRE ELEM|FAT|ALL`, `ECHO NSTR ELEM|COMP|STIF|SEFF|SHEA`, `ECHO FAT ELEM`.
> `ECHO LC NO` prints only extreme values; `YES` prints load case 0 and combination load cases; `FULL` prints all single load cases.
> `ECHO REIN YES` prints the table of maximum reinforcement; `FULL` adds the individual designs; `EXTR` adds the reinforcement per layer for crack width.
> `ECHO SHEA YES` prints only maximum shear values; `FULL` prints all sections.

**Typical usage:**
```
ECHO FULL NO           $ suppress all standard tables
ECHO DESI YES          $ design table
ECHO REIN FULL         $ maximum and individual reinforcement
ECHO SHEA YES          $ maximum shear values only
```

---

### CTRL — Control of the Calculation

Sets global control options for the design tasks of the current block.

**Syntax:**
```
CTRL OPT VAL VAL2 VAL3 VAL4
```

| Parameter | Type      | Unit | Default | Description |
|-----------|-----------|------|---------|-------------|
| `OPT`     | enum      | —    | —       | Name of the option (required, see table below) |
| `VAL`     | enum/float| —    | —       | Value of the option |
| `VAL2`    | float     | —    | —       | Optional second value |
| `VAL3`    | float     | —    | —       | Optional third value |
| `VAL4`    | float     | —    | —       | Optional fourth value |

**OPT — control options:**

| OPT    | Meaning | VAL (default) |
|--------|---------|---------------|
| `MSEL` | Type of design — restrict design to one material class | `CONC` (EN 1992), `STEE` (EN 1993), `COMP` (EN 1994), `TIMB` (EN 1995), `ALUM` (EN 1999). Default: all material types |
| `AXIA` | Type of bending | `-2` biaxial bending (default); `+1` uniaxial (M_z = V_y = 0, no principal axes rotation); `-1` suppress rotation of principal axes; `+2` biaxial |
| `ACT`  | Groups of actions for AQB `COMB` | `0` each basic action identifier is an own action; `1` actions of same category grouped (default); `2` actions within one row of `LC` are one action |
| `SMOO` | Smoothing of moments at supports (bit-coded) | `0` none; `1` principal bending only (default); `2` principal + lateral; `4` also prestress moments; `8` also reduce prestress shear forces; `+128` no reference systems; `+256` no conversion of shear at inclined axis; `+512` no conversion of moments at inclined axis |
| `VRED` | Maximum inclination for conversion of shear force in haunches | `0.3333`; `0.0` = no conversion |
| `VERT` | Maximum deviation of beam axis from horizontal for a bending member | `0.3333` |
| `NLIM` | Lower limit of axial force relative to plastic axial force for compression members | `0.001` |
| `ED`   | Relative eccentricity limit between compression and bending members | `3.5` |
| `FEM`  | Usage of the FE mesh of the section | `0` classical polygon data (default); `1` use FE section, do not save results; `2` use FE section and save FE results |
| `USEP` | Utilisation level above which a check is marked | code default |
| `EIGE` | Options for internal stresses (AQBS only, bit-coded) | `0` none (default); `1` creep loads for statically indeterminate analysis; `2` losses also for unbonded tendons; `4` secondary effects proportional to primary; `64` do not activate reinforcement; `512` no factorisation of creep factors. Literals: `SAFE`, `RCRE`, `TENS`, `NONL` (with VAL2 0/1), `SUM`, `EN10`, `MC90`, `MC10` |
| `DESV` | Method for shear design of cracked sections | `1` (default): `0` sectional values only; `1` longitudinal force differences for flanges; `2` for all shear cuts; `3` max of 0 and 2; `4`–`7` as `0`–`3` without uncracked fall-back; `NRIL` inclination per German Nachrechnungsrichtlinie. VAL2 = tolerance [%] (default 10) |
| `SVRF` | Factor for considering the non-prestressed reinforcement of AQUA in the section properties | `0.0` (or AQUA `CTRL RFCS`) |
| `INTE` | Non-linear axial strain effects and shear/axial stress interaction | `0` none; `1` isotropic reduction; `2` Prandtl flow rule (default for steel); `3` preference of shear stress; `N` non-linear axial strain effects (VAL2 0/1). Prefix `CONC`, `STEE`, `TIMB` restricts to material type; VAL3 = shear strength factor |
| `REIN` | Treatment of reinforcements | `CAPA` FIX without warnings; `REQU` no minimum reinforcement from AQUA; `FIX` no increase of any reinforcement; `FIXL` no increase of longitudinal reinforcement; `FIXS` no increase of shear links; `FIXM` symmetric minimum reinforcement from AQUA (default); `FIXT` torsion options in VAL2 (0–3, default 3) |
| `PIIA` | Parameters of cracked condition (experienced users only) — VAL for DESI, VAL2 for NSTR | `7` / `5`. Bits: 1, 2, 4, 8, 16, 32, 64; literals `N10`, `MY10`, `MZ10`, `REST` |
| `VM`   | Shift rule — longitudinal forces from shear force (VAL) and torsion (VAL2) | `0.0` not considered (default); `>0` explicit cot θ; `x[%]` factor on shift rule; `STD` offset of shift rule only without changing reinforcement |
| `CNOM` | Fixed value of cover for all sections | — |
| `ELIM` | Threshold strain for design [‰] | `0.002` |
| `ETOL` | Precision for internal forces iteration | `0.0001` |
| `IMAX` | Maximum number of iterations | `50` |
| `AMAX` | Maximum factor for line-search | `1000` |
| `AGEN` | Relative precision of line-search | `0.2` |

> Iteration parameters `ETOL`, `IMAX`, `AMAX`, `AGEN` should only be changed in exceptional cases.
> `CTRL VM STD` is the recommended setting for RC beam design according to EN 1992 when the tensile force envelope must be shifted (a_l).
> Only options listed in this table may be used. The `.err` file contains further internal options (`CS`, `PLC`, `COUN`) without documented meaning — do not use them.

**Typical usage:**
```
CTRL VM STD            $ shift rule offset for tensile force envelope
CTRL AXIA -1           $ suppress rotation of principal axes
CTRL MSEL CONC         $ design only concrete sections
CTRL REIN FIX          $ check of existing structure: no increase of reinforcement
```

---

### TVAR — Temporary Boxed Values

Defines temporary values of national parameters (boxed values of the Eurocodes) for the design. The names and scopes are listed in the file `master.ini`.

**Syntax:**
```
TVAR NAME VAL SCOP CMNT
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `NAME`    | string | —    | —       | Name of the variable (Lit16, required) |
| `VAL`     | string/float | — | —   | Value of the variable or expression in the format `"=expression"` (Lit64, required) |
| `SCOP`    | string | —    | `*`     | Scope of the variable — **must be set to `DESI` in AQB** |
| `CMNT`    | string | —    | —       | Comment (Lit32) |

**Frequently used names (scope DESI):**

| NAME | Typical value | Meaning |
|------|---------------|---------|
| `GAM-C`  | 1.50 | Safety coefficient concrete |
| `GAM-CE` | 1.20 | Safety coefficient concrete elasticity |
| `GAM-B`  | 1.15 | Safety coefficient reinforcing steel |
| `GAM-Y`  | 1.15 | Safety coefficient prestressing steel |
| `GAM-S`  | 1.10 | Safety coefficient structural steel |
| `GAM-A`  | 1.30 | Safety coefficient structural aluminium |
| `ALF-CC` | 1.00 | Long-term reduction of concrete compressive strength (EN 1992 3.1.6 (1)) |
| `ALF-CT` | 1.00 | Long-term reduction of concrete tensile strength (EN 1992 3.1.6 (2)) |
| `ALF-CE` | 0.85 | Reduction of E-modulus for the calculatoric (CALC) stress-strain curve (DIN only) |
| `AS-MAX` | 8.00 | Maximum longitudinal reinforcement ratio [% of Ac] |
| `AS-MINB`| 0.13 | Minimum reinforcement ratio in bending members [% of Ac] |
| `AS-MINC`| 0.20 | Minimum reinforcement ratio in compression members [% of Ac] |
| `TANMIN` | 0.40 | Minimum inclination (tan) of compression struts in the web |
| `TANMAX` | 1.00 | Maximum inclination (tan) of compression struts in the web |

> Boxed values are normally defined in AQUA (`TVAR`) or via the INI-file. Use AQB `TVAR` only for special cases.

**Typical usage:**
```
TVAR NAME "ALF-CE" VAL 0.85 SCOP DESI
TVAR NAME "GAM-CE" VAL 1.25 SCOP DESI
```

---

### BEAM — Selection of the Elements to be Designed

Selects the beam elements, structural lines, design elements or external sections to be designed, and optionally assigns construction stages or an existing reinforcement.

**Syntax:**
```
BEAM FROM TO INC TYPE X XE NCS
     BETA BETS STYP PRED LAMS LAMT LAML LAMC LAMM
     CS CS0 CS1 ... CS31
```

| Parameter | Type      | Unit    | Default | Description |
|-----------|-----------|---------|---------|-------------|
| `FROM`    | int/enum  | —       | 1       | First element number, or `GRP` (group), `SLN` (structural line), `REF` (primary geometric axis) |
| `TO`      | int/string| —       | `FROM`  | Last element number, or group number / SLN number / axis name when FROM is a selector |
| `INC`     | int       | —       | 1       | Increment of element number (no meaning with selectors) |
| `TYPE`    | enum      | —       | `BEAM`  | Element type (see table below) |
| `X`       | float     | `[m]`   | —       | X value of beam section or station on axis |
| `XE`      | float     | `[m]`   | —       | Second value to define an interval (no input = all sections) |
| `NCS`     | int       | —       | (!)     | Section number (for external sections) |
| `BETA`    | float     | `[-]`   | `*`     | Coefficient of effective / buckling length (positive values enable buckling design) |
| `BETS`    | float     | `[-]`   | `BETA`  | Same for secondary transverse bending |
| `STYP`    | int       | —       | —       | Bit pattern of section properties: `1` = discontinuity for EIGE loads |
| `PRED`    | float     | `[-]`   | —       | Reduction factor of tendon areas (e.g. corrosion) |
| `LAMS`    | float     | `[-]`   | 1.0     | Coefficient equivalent stress range reinforcements (fatigue) |
| `LAMT`    | float     | `[-]`   | 1.0     | Coefficient equivalent stress range tendons |
| `LAML`    | float     | `[-]`   | 1.0     | Coefficient equivalent stress range shear links |
| `LAMC`    | float     | `[-]`   | 1.0     | Coefficient equivalent stress range concrete |
| `LAMM`    | float     | `[-]`   | 1.0     | Coefficient equivalent stress range other materials |
| `CS`      | enum      | —       | `NUM`   | Content of the CSi data (see table below) |
| `CS0`–`CS31` | int/float | — / `[cm²]` | — | Construction stage numbers — or reinforcement values per layer when `CS AS` / `CS ASV` |

**TYPE — element types:**

| Value  | Meaning |
|--------|---------|
| `BEAM` | Beam elements of the database |
| `FLEX` | Beam elements as bending members |
| `COMP` | Beam elements as compression members |
| `TRUS` | Truss elements |
| `CABL` | Cable elements |
| `DSLN` | Results at design elements (DECREATOR) |
| `DBEA` | Design elements as beams |
| `DCOL` | Design elements as columns |
| `SECT` | External section in bending members |
| `SCOM` | External section in compression members |
| `FACE` | Support face |
| `HFAC` | Support face, hinged support |
| `IFAC` | Support face, indirect support |
| `SHEA` | External section, shear section |

**CS — content of CSi data:**

| Value  | Meaning |
|--------|---------|
| `NUM`  | Explicit construction stage numbers (default) |
| `AUTO` | Construction stages as defined in the AQUA section |
| `AUTX` | Extended stages from section (+0, +1, +5) |
| `AS`   | Given longitudinal reinforcement per layer, `CSi` = area of layer i `[cm²]` |
| `ASV`  | Given shear link reinforcement per layer, `CSi` = area of layer i `[cm²/m]` |

> The group, structural line or axis designation is given at `TO` when `FROM` is `GRP`, `SLN` or `REF`; `INC` has no meaning then. For `REF` only primary axes are supported.
> Only one type of element can be processed in one input block: {BEAM, FLEX, COMP}, {DSLN, DBEA, DCOL}, {TRUS}, {CABL} or {SECT … SHEA}. Define `BEAM` **before** the `LC` records.
> `FLEX` / `COMP` override the automatic distinction between bending and compression members (based on gravity direction, eccentricity `CTRL ED` and axial force `CTRL NLIM`). This matters for minimum reinforcement rules.
> If only `TYPE` is given, all elements of that type are selected. Without `X`/`XE` all sections are designed.
> With `CS AS` / `CS ASV` a given reinforcement can be specified (e.g. for existing structures or non-linear analysis). Missing x-values are interpolated. The reinforcement case must then be addressed with `REIN`.

**Typical usage:**
```
$ Design all beams of structural line 1
BEAM FROM SLN TO 1

$ Design all beams of group 2 as compression members
BEAM FROM GRP TO 2 TYPE COMP

$ Buckling length coefficient for a column (Eurocode additional moments)
BEAM FROM GRP TO 3 TYPE COMP BETA 2.0

$ Given longitudinal reinforcement along structural line 1
BEAM FROM SLN TO 1 X 0.0  XE 5.0  CS AS CS1 5[cm2]
BEAM FROM SLN TO 1 X 5.0  XE 20.0 CS AS CS1 20[cm2]
BEAM FROM SLN TO 1 X 20.0 XE 25.0 CS AS CS1 5[cm2]
REIN RMOD SAVE
```

---

### TEND — Tendons (AQBS only)

Defines tendons directly for external sections. Tendons are generally defined with program TENDON; use TEND only for special cases.

**Syntax:**
```
TEND NO NOB MNO ICS1 ICS2 ICS3
     X Y Z ZZ AZ NY NZ YHR ZHR AHR DZ AR UZ TEMP
```

| Parameter | Type  | Unit    | Default | Description |
|-----------|-------|---------|---------|-------------|
| `NO`      | int   | —       | 1       | Beam number |
| `NOB`     | int   | —       | 1       | Tendon number |
| `MNO`     | int   | —       | 1       | Material number of tendon + 1000 · number of deductional material |
| `ICS1`    | int   | —       | 0       | Prestress stage building-in |
| `ICS2`    | int/enum | —    | 1       | Prestress stage extrusion (grouting); `0` = immediate bond; `NONE` or `9999` = without bond |
| `ICS3`    | int   | —       | 0       | Prestress stage removal |
| `X`       | float | `[m]`   | 0       | x value on beam axis (precision 1 mm) |
| `Y`       | float | `[mm]`  | 0       | y value in section coordinate system |
| `Z`       | float | `[mm]`  | 0       | z value in section coordinate system |
| `ZZ`      | float | `[kN]`  | 0       | Tension force |
| `AZ`      | float | `[mm²]` | 0       | Area of tendon |
| `NY`      | float | `[-]`   | 0       | Gradient of tendon in y direction (dY/dX) |
| `NZ`      | float | `[-]`   | 0       | Gradient of tendon in z direction (dZ/dX) |
| `YHR`     | float | `[mm]`  | `Y`     | y value of centre point of duct |
| `ZHR`     | float | `[mm]`  | `Z`     | z value of centre point of duct |
| `AHR`     | float | `[mm²]` | `AZ`    | Area of duct |
| `DZ`      | float | `[mm]`  | `*`     | Effective diameter |
| `AR`      | float | `[m²]`  | —       | Reference area for design of crack width |
| `UZ`      | float/enum | `[mm]` | `*` | Circumference of tendon for crack width; `BUND` = 1.6 · π · √AZ |
| `TEMP`    | float | `[°C]`  | 0       | Temperature for a hot design |

> Tendons must be entered in order of beams and beam sections. TEND cannot be combined with forces defined by `S` in load case 0.
> For post-tensioning specify `ICS2 > ICS1`.

---

### LC — Selection of the Load Case to be Designed

Selects the load cases or combination load cases to be designed and optionally redefines their action properties temporarily.

**Syntax:**
```
LC NO TYPE CST REF TITL
   GAMU GAMF PSI0 PSI1 PSI2 PS1S GAMA APAR SUP
   FAT
```

| Parameter | Type      | Unit | Default | Description |
|-----------|-----------|------|---------|-------------|
| `NO`      | int/string| —    | —       | Load case number, wildcard expression (e.g. `'1??00'`) or name of a load case type |
| `TYPE`    | string    | —    | —       | Name of action / load case type (e.g. `G`, `Q`, `(D)`) |
| `CST`     | int/enum  | —    | `*`     | Cross-section type for stresses: construction stage number, `GROS`, `CS0` … `CS255` |
| `REF`     | enum      | —    | `PART`  | Reference point of stored forces: `STD` current section, `GROS` final gross section, `EFFE` final effective section, `PART` construction stage section, `NULL` origin of section coordinates |
| `TITL`    | string    | —    | —       | Name of the load case (Lit24) |
| `GAMU`    | float     | `[-]`| `*`     | Unfavourable safety factor |
| `GAMF`    | float     | `[-]`| `*`     | Favourable safety factor |
| `PSI0`    | float     | `[-]`| `*`     | Combination coefficient standard |
| `PSI1`    | float     | `[-]`| `*`     | Combination coefficient frequent |
| `PSI2`    | float     | `[-]`| `*`     | Combination coefficient quasi-permanent |
| `PS1S`    | float     | `[-]`| `*`     | Combination coefficient infrequent |
| `GAMA`    | float     | `[-]`| `*`     | Safety factor accidental |
| `APAR`    | enum      | —    | `*`     | Partition of action: `G`, `P`, `Q`, `A`, `E` |
| `SUP`     | enum      | —    | `*`     | Superposition within action: `PERM`, `PERC`, `COND`, `EXCL`, `UNSI`, `USEX`, `ALEX`, `EXEX` |
| `FAT`     | enum      | —    | —       | Special enlargement for fatigue: `DIN` = per DIN FB 102 A 106.2 |

**Load case types for combination load cases (selection by `TYPE`):**

| Type   | Meaning |
|--------|---------|
| `(D)`  | Ultimate design combination |
| `(A)`  | Ultimate accidental combination |
| `(E)`  | Ultimate earthquake combination |
| `(P)`  | Service: quasi-permanent combination |
| `(F)`  | Service: frequent combination |
| `(N)`  | Service: infrequent combination |
| `(R)`  | Service: characteristic (rare) combination |
| `(H)`  | Combination of principal loading |
| `(HZ)` | Combination of principal + supplemental loading |
| `(PT)`, `(LT)`, `(MT)`, `(ST)`, `(VT)` | Timber: permanent, long-term, medium-term, short-term, very short-term |
| `(-)`  | Temporary classification without an action |

> MAXIMA result load cases get their type from `COMB ... TYPE`: `DESI` → `(D)`, `ACCI` → `(A)`, `EARQ` → `(E)`, `RARE` → `(R)`, `FREQ` → `(F)`, `NONF` → `(N)`, `PERM` → `(P)`, `PT`/`LT`/`MT`/`ST`/`VT` → `(PT)`/`(LT)`/`(MT)`/`(ST)`/`(VT)`. Several types can be selected in one record as a list: `LC TYPE (PT),(LT),(MT)`.

> **Using load cases:**
> 1. No `LC` record → all load cases in the database are designed individually; `S` forces are processed as load case 0.
> 2. `LC` only → only the selected load cases are designed.
> 3. `LC` followed by `S` → the forces are stored under this load case (external sections or additional forces); `TITL` names the new load case.
> 4. `LC` and `COMB` → only the combinations are designed; the load case types are evaluated within the combination rules.
> Safety factors and combination coefficients given in AQB are only temporary. APAR and SUP: if only one of them is specified, the other is reset to its default.
> Prestress is only considered when a load case of that action type is selected.
> The default `CST` is CS1 for all load case types except G1 and PR (CS0). Without CS values in `BEAM`, all load cases act on the gross section.

**Typical usage:**
```
$ All ULS design combinations (from MAXIMA COMB EXTR DESI or SOFILOAD TYPE (D))
LC TYPE (D)

$ Explicit MAXIMA result load cases (max/min VZ and MY)
LC 2125,2126,2129,2130

$ Timber: select combinations by load duration
LC TYPE (PT),(LT),(MT)

$ Primary load cases for an AQB combination
LC 1 TYPE G
LC 2 TYPE Q
LC 3 TYPE Q
```

---

### S — Internal Forces and Moments

Defines internal forces and moments for a stand-alone design of a cross-section (no system analysis required).

**Syntax:**
```
S NCS NO X N VY VZ MT MY MZ MB MT2 Y Z REF
```

| Parameter | Type   | Unit     | Default | Description |
|-----------|--------|----------|---------|-------------|
| `NCS`     | int    | —        | —       | Cross-section number (AQUA) |
| `NO`      | int    | —        | 1       | Element number (identification of output) |
| `X`       | float  | `[m]`    | 0       | X value (negative = measured from beam end) |
| `N`       | float  | `[kN]`   | 0       | Axial force |
| `VY`      | float  | `[kN]`   | 0       | Shear force y |
| `VZ`      | float  | `[kN]`   | 0       | Shear force z |
| `MT`      | float  | `[kNm]`  | 0       | Total torsional moment |
| `MY`      | float  | `[kNm]`  | 0       | Bending moment y |
| `MZ`      | float  | `[kNm]`  | 0       | Bending moment z |
| `MB`      | float  | `[kNm²]` | 0       | Warping moment |
| `MT2`     | float  | `[kNm]`  | 0       | Secondary torsional moment |
| `Y`       | float  | `[mm]`   | `*`     | Reference coordinate y |
| `Z`       | float  | `[mm]`   | `*`     | Reference coordinate z |
| `REF`     | string | —        | —       | Designation of a sectional point (Lit8) as reference |

> S is implemented for BEAM elements only. Without a preceding `LC`, the forces are stored as **load case 0**; NO and X are then only used for identification of the output.
> After an `LC` record the forces are stored under that load case (existing results of that load case are deleted).
> Forces must be entered in increasing order of element number and x value; multiple definitions for the same location are not possible.
> N and M refer to the centroid, V and MT to the shear centre, unless Y/Z or REF is given.
> For `DESI STAT ULTI` the S values must be **design (factored) values**.

**Typical usage:**
```
$ ULS design forces for section 1
S NCS 1 NO 1 X 0.0 N -250 VZ 180 MY 320

$ Forces for several sections of a stand-alone check
S NCS 1 NO 1 X 0.0 MY 150
S NCS 2 NO 2 X 0.0 MY 150
```

---

### COMB — Definition of Load Case Combinations

Defines load case combinations inside AQB (e.g. for prestressed concrete or divided safety factors). It supplements the MAXIMA superposition.

**Syntax:**
```
COMB EXTR SCOM SFAC
     LC1 F1 LC2 F2 LC3 F3 LC4 F4 LC5 F5 LC6 F6
     LCST CST TITL
```

| Parameter | Type      | Unit | Default | Description |
|-----------|-----------|------|---------|-------------|
| `EXTR`    | enum      | —    | `MAMI`  | Extreme value type of the combination (see table below) |
| `SCOM`    | enum      | —    | `MY`    | Internal force for extreme value: `N`, `VY`, `VZ`, `MT`, `MY`, `MZ`, `MB`, `MT2`, `SIG`, `TAU` |
| `SFAC`    | float     | `[-]`| 1.0     | Factor for the internal force (decision factor for favourable/unfavourable) |
| `LC1`–`LC6` | int/string | — | —      | Load case number or load type (action name, e.g. `G`, `Q`, `L`, `MCR`, `DMR`) |
| `F1`–`F6` | float/enum| `[-]`| `*`     | Factor for LCi, or a factor literal (see below) |
| `LCST`    | int       | —    | —       | Load case number for storing the results of the combination |
| `CST`     | int/enum  | —    | `*`     | Section type for EIGE/DESI/NSTR: `GROS`, construction stage number, `CS0` … `CS255` |
| `TITL`    | string    | —    | `*`     | Name of the combination (Lit24) |

**EXTR — extreme value types:**

| Value | Meaning |
|-------|---------|
| `SOLO` | Individual without checks |
| `MAX` / `MIN` / `MAMI` | Maximum / minimum / maximum and minimum |
| `SUM`  | Add all values together |
| `AND`  | Continuation — add further load cases (more than 6) |
| `LOSS` | Loss of prestress in preceding combination |
| `LINE` | Separation line for ECHO TABS |
| `GMAX` / `GMIN` | Store maximum / minimum of all results of the block under LCST |
| `SMAX` / `SMIN` / `SMAM` | Extreme values (special) |
| `MAXD` / `MIND` / `MAMD` / `SUMD` | ULS design combination with safety factors and combination coefficients |
| `MAXA` / `MINA` / `MAMA` / `SUMA` | Accidental design combination |
| `MAXE` / `MINE` / `MAME` / `SUME` | Seismic design combination |
| `MAXR` / `MINR` / `MAMR` / `SUMR` | Characteristic (rare) combination |
| `MAXF` / `MINF` / `MAMF` / `SUMF` | Frequent combination |
| `MAXN` / `MINN` / `MAMN` / `SUMN` | Infrequent combination |
| `MAXP` / `MINP` / `MAMP` / `SUMP` | Quasi-permanent combination |
| `FSUM` / `FMAX` / `FMIN` / `FMAM` / `FSOL` | As SUM/MAX/MIN/MAMI/SOLO but SFAC also acts on the combination forces |

**F1–F6 — factor literals:**

| Literal | Factor | Literal | Factor |
|---------|--------|---------|--------|
| `GAM`  | γ_u / γ_f | `GAMA` | γ_a |
| `GAMU` | γ_u | `GAMF` | γ_f |
| `PSI0` | ψ₀ | `PSI1` | ψ₁ |
| `PSI2` | ψ₂ | `PS1S` | ψ₁,infq |
| `PSIG` | γ_u/γ_f · ψ₀ | `PSIA` | γ_a · ψ₀ |
| `PSIU` | γ_u · ψ₀ | `PSIF` | γ_f · ψ₀ |
| `PS1G` | γ_u/γ_f · ψ₁ | `PS1A` | γ_a · ψ₁ |
| `PS1U` | γ_u · ψ₁ | `PS1F` | γ_f · ψ₁ |
| `PS2G` | γ_u/γ_f · ψ₂ | `PS2A` | γ_a · ψ₂ |
| `PS2U` | γ_u · ψ₂ | `PS2F` | γ_f · ψ₂ |
| `P1SG` | γ_u/γ_f · ψ₁,infq | `P1SA` | γ_a · ψ₁,infq |
| `P1SU` | γ_u · ψ₁,infq | `P1SF` | γ_f · ψ₁,infq |
| `KFI`  | k_fi (EN 1990 Tab. B.3) | `XSI` | ξ (EN 1990 eq. 6.10b) |
| `XSIG` | ξ · γ_u/γ_f | `XSIA` | ξ · γ_a |
| `XSIU` | ξ · γ_u | `XSIF` | ξ · γ_f |
| `KFG`  | k_fi · γ_u/γ_f | `XKFI` | ξ · k_fi |
| `KFG0` | k_fi · ψ₀ · γ_u/γ_f | `KFG1` | k_fi · ψ₁ · γ_u/γ_f |
| `KFG2` | k_fi · ψ₂ · γ_u/γ_f | `KFGS` | k_fi · ψ₁,infq · γ_u/γ_f |
| `XKFG` | k_fi · ξ · γ_u/γ_f | `XKGA` | k_fi · ξ · γ_a |
| `XKGU` | k_fi · ξ · γ_u | `XKGF` | k_fi · ξ · γ_f |

> Combinations must be input **before** the design task and stay in effect for later tasks until redefined.
> If a load type (action) is given at LCi, all load cases of this type are combined according to the action definition: G1, G2, P, C are always added (permanent); Q, S, F are added if unfavourable; for all other types only the most unfavourable load case of that type is used.
> For MAXD/MAXR/… the first variable load case Q is treated as leading action. **The leading action is not selected automatically as in MAXIMA** — for full envelopes over many load cases use MAXIMA.
> An explicit factor always overwrites any default factor.
> Results (combined forces, stresses, non-linear results) are stored only when `LCST` is given.

**Typical usage:**
```
$ ULS combination 1.35 G + 1.5 L with extreme value of MY
COMB MAMI MY LC1 G F1 1.35 LC2 L F2 1.50

$ Characteristic combination and storage under LC 501
COMB EXTR MAMR SCOM MY LC1 G LC2 Q LCST 501 TITL 'rare G+Q'

$ Store max/min of all results of the block
COMB GMAX LCST 201 TITL 'extremal values'
```

---

### EIGE — Determination of Internal Stresses (AQBS only)

Calculates redistributions of internal stresses due to creep, shrinkage and relaxation (prestressed and composite sections).

**Syntax:**
```
EIGE MNO PHI EPS REL T RH TEMP T0 TS GRP EXP
```

| Parameter | Type       | Unit      | Default | Description |
|-----------|------------|-----------|---------|-------------|
| `MNO`     | int        | —         | —       | Material number (required) |
| `PHI`     | float/enum | `[-]`     | `*`     | Creep factor, consistency class `KS`/`KP`/`KR`, `EC` (switch to Eurocode formulas), or 1000 h relaxation factor for prestressing steel |
| `EPS`     | float      | `[-]`     | `*`     | Shrinkage coefficient (negative sign!) |
| `REL`     | float      | `[-]`     | 0.80    | Relaxation factor according to Trost |
| `T`       | float/enum | `[days]`  | 0.0     | Duration of period (`NONE`; negative = apply time evolution to explicit PHI/EPS) |
| `RH`      | float/enum | `[%]`     | 40      | Relative humidity or `ARID` (45 %), `INTE` (50 %), `TEMP` (55 %), `TROP` (67 %) |
| `TEMP`    | float      | `[°C]`    | 20      | Concrete temperature during creep step (negative = thermal treatment before) |
| `T0`      | float      | `[days]`  | 7       | Minimum age at loading |
| `TS`      | float      | `[days]`  | 0       | Age at start of drying |
| `GRP`     | int        | —         | all     | Group number |
| `EXP`     | string     | —         | —       | Exposition class for explicit creep curves defined with MEXT (Lit4) |

> The results (secondary strains and stresses) are stored under the load case or under `LCST` of the preceding `COMB`. They are deleted when forces are redefined with `S` for this load case.
> If PHI or EPS are not defined, they are calculated from humidity, temperature, age at loading, cement class and effective thickness according to the material's design code.
> With `CTRL EIGE 1` curvature loads for the statically indeterminate effects are stored (requires multiple creep stages in ASE).

---

### STRE — Linear Stresses and Plastic Forces

Evaluates elastic stresses and — for steel, aluminium and timber sections — the utilisation from plastic sectional resistances. Also used for prestressed concrete stress limitations.

**Syntax:**
```
STRE SMOD STYP
     SC ST SBC SBT SBBC SBBT SI SII
     TAU SV TAUS SSTM SSEM SSKM SSER SSKR
     CC CBC CBBC LIMA ZMAX ZDIF SDIF TDIF SCMG
```

| Parameter | Type      | Unit      | Default | Description |
|-----------|-----------|-----------|---------|-------------|
| `SMOD`    | enum/int  | —         | `E`     | Type of check or material number (see table below) |
| `STYP`    | enum      | —         | —       | Tabulated limiting stresses (literal, see below) |
| `SC`      | float     | `[N/mm²]` | —       | Max. normal stress compression |
| `ST`      | float     | `[N/mm²]` | `SC`    | Max. normal stress tension |
| `SBC`     | float     | `[N/mm²]` | `SC`    | Max. edge stress bending compression |
| `SBT`     | float     | `[N/mm²]` | `ST`    | Max. edge stress bending tension |
| `SBBC`    | float     | `[N/mm²]` | `SBC`   | Max. corner stress bending compression |
| `SBBT`    | float     | `[N/mm²]` | `SBT`   | Max. corner stress bending tension |
| `SI`      | float     | `[N/mm²]` | —       | Max. principal tensile stress |
| `SII`     | float     | `[N/mm²]` | —       | Max. principal compressive stress |
| `TAU`     | float     | `[N/mm²]` | —       | Max. shear stress |
| `SV`      | float     | `[N/mm²]` | —       | Max. equivalent (von Mises) stress |
| `TAUS`    | float     | `[N/mm²]` | —       | Max. shear stress longitudinal welds |
| `SSTM`    | float     | `[N/mm²]` | `TAU`   | Max. shear/tension torsion middle area |
| `SSEM`    | float     | `[N/mm²]` | `TAU`   | Max. shear/tension separate middle area |
| `SSKM`    | float     | `[N/mm²]` | `TAU`   | Max. shear/tension combined middle area |
| `SSER`    | float     | `[N/mm²]` | `TAU`   | Max. shear/tension edge |
| `SSKR`    | float     | `[N/mm²]` | `TAU`   | Max. shear/tension combined edge |
| `CC`      | float     | `[N/mm²]` | (SC)    | Max. normal stress compressive zone |
| `CBC`     | float     | `[N/mm²]` | (CC)    | Max. edge stress compressive zone |
| `CBBC`    | float     | `[N/mm²]` | (CBC)   | Max. corner stress compressive zone |
| `LIMA`    | float     | `[N/mm²]` | `*`     | Limit for decompression or zone a/b |
| `ZMAX`    | float     | `[N/mm²]` | `*`     | Max. prestressing steel stress |
| `ZDIF`    | float     | `[N/mm²]` | —       | Max. stress range prestressing steel |
| `SDIF`    | float     | `[N/mm²]` | —       | Stress range limit (listed in `.err`, not described in the manual — do not use) |
| `TDIF`    | float     | `[N/mm²]` | —       | Stress range limit (listed in `.err`, not described in the manual — do not use) |
| `SCMG`    | float     | `[-]`     | —       | Global safety class factor, multiplied with the selected safety factors |

**SMOD — type of check:**

| Value | Meaning |
|-------|---------|
| `E`   | Elastic stresses: maximum, principal and von Mises stresses in all section points (default) |
| `B`   | Utilisation for every individual force component and linear superposition of the utilisation |
| `C`   | Utilisation for every individual component and complex interaction (EN 1993 / EN 1999, section class 1 and 2) |
| `D`   | Suggested dimensions (estimate of required section size); `DE` uses only allowable stresses |
| `DG`  | Select section from a group of sections (consecutive section numbers); `DGE` uses only allowable stresses |
| `U`   | Uncracked shear check (German Nachrechnungsrichtlinie, DIN 4227) — used as `STRE U` or `STRE E UL` |
| *n*   | Material number: define permissible stresses for material *n* only (`0` = all materials); does not start a check |

**STYP — literals for structural steel and aluminium:**

| Value | Meaning |
|-------|---------|
| `F`   | Yield strength with safety factor (e.g. γ = 1.1 or `TVAR GAM-S`) |
| `FF`  | Full yield strength without safety factor |
| `C`   | Characteristic values of strength / yield stress |
| `M0`  | Strength / yield stress for sectional design (γ_M0) |
| `M1`  | Strength / yield stress for stability member design (γ_M1) |
| `H` / `HZ` / `S` / `SZ` | Permissible stresses DIN 18800 / ÖNORM B 4600 / DIN 4113 (load case H, HZ; increased corner values) |

**STYP — literals for concrete (EN 1992 / DIN FB 102):**

| Value | Meaning |
|-------|---------|
| `VH`  | Limit tensile stresses; with `LIMA 0.0` decompression check |
| `BH`  | Characteristic (rare) or infrequent combination: 0.60 f_ck concrete, 0.80 f_yk reinforcement, 0.75 f_pk tendons (EC) |
| `VZ`  | Quasi-permanent actions: 0.45 f_ck concrete (creep), 0.65 f_pk tendons (DIN) |
| `BZ`  | Characteristic actions: f_ctm for tensile stresses (DIN), otherwise as BH |
| `BX`  | Principal tensile stress under frequent combination against f_ctk,0.05 (FB 102) |
| `RL`  | Minimum reinforcement for crack control (EN 1992-1-1 7.3.2) — used as `STRE E RL` |

> Cable steel: `S` (0.45 f_pu/γ_r), `SZ` (0.55 f_pu), `SS` (0.60 f_pu). Timber: all admissible stresses are defined with the material in AQUA; use `STRE E F` (design strength, EN 1995) — AQB selects k_mod from the load duration type of the combination (`(PT)`, `(LT)`, …).
> The elastic stress is always evaluated, as it determines the section class. Class 3 sections are checked against allowable stresses, class 1/2 sections against plastic resistances (`SMOD B` linear, `SMOD C` interaction).
> Stresses of combinations are stored if `LCST` is specified in `COMB`; without COMB the stresses of single load cases with a design type (e.g. `(D)`) are stored.
> A preceding `COMB GMAX LCST n` stores the extreme stresses / utilisations of the block.

**Typical usage:**
```
$ Steel section: elastic stresses with design yield strength (gamma_M0)
STRE E M0

$ Steel section: plastic resistance with interaction (class 1/2)
STRE C M0

$ Timber section EN 1995: design strengths incl. k_mod
STRE E F

$ Prestressed concrete: decompression check
STRE E VH LIMA 0.0
```

---

### REIN — Specification for Determining Reinforcement

Defines the reinforcement case (LCR) under which the designed reinforcement is saved and how constant reinforcement is spread.

**Syntax:**
```
REIN MOD RMOD LCR ZGRP SFAC P6 P7 P8 P9 P10 P11 P12 TITL
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `MOD`     | enum   | —    | `SECT`  | Spread of constant reinforcement (see table below) |
| `RMOD`    | enum   | —    | `SING`  | Type of reinforcement case LCR (see table below) |
| `LCR`     | int    | —    | 1       | Number of reinforcement distribution |
| `ZGRP`    | int    | —    | 0       | Grouping of prestressing tendons (0 = tendons are minimum reinforcement) |
| `SFAC`    | float  | `[-]`| 1.0     | Factor for continuous reinforcement |
| `P6`–`P10`| float  | `[-]`| `*`     | Parameters for determining reinforcement (P7 weighting of moments, default 5; P8 weighting of dimensions, default -2; P9/P10 reference point factors, default 1.0) — normally not changed |
| `P11`     | float  | `[-]`| 0.20    | Factor for preference of outer reinforcement (1.0 biaxial, 0.0 uniaxial) |
| `P12`     | float  | `[-]`| `*`     | Parameter for determining reinforcement |
| `TITL`    | string | —    | —       | Title of the design case (Lit24) |

**MOD — spread of constant reinforcement:**

| Value  | Meaning |
|--------|---------|
| `SECT` | Only in section (default) |
| `BEAM` | In beam or structural line (same id) |
| `SPAN` | In span |
| `GLOB` | In all active beams |
| `TOTL` | In all beams |

**RMOD — type of reinforcement case:**

| Value  | Meaning |
|--------|---------|
| `SING` | Single calculation — the global minimum reinforcement (LCR 0) is not changed (default) |
| `SAVE` | Save as global minimum reinforcement — overwrites LCR 0 with the current reinforcement (AQUA minimum reinforcement remains) |
| `SUPE` | Superposition with the global minimum reinforcement |
| `ACCU` | The existing LCR reinforcement is taken as minimum reinforcement (accumulation) |
| `NEW`  | New definition (special cases only) |

> The last defined LCR is used to save the reinforcement for graphics and non-linear analysis. LCR 0 is reserved for the global minimum reinforcement and cannot be addressed directly.
> **Standard RC workflow:** ULS design with `REIN MOD SECT RMOD SAVE LCR 1` → the reinforcement becomes the minimum reinforcement for the subsequent SLS check (`NSTR`) in the next AQB block, which uses `REIN ... RMOD SING LCR 2` (possible increases for crack width are saved under LCR 2).
> `SUPE` cannot be used during an iteration (ASE/STAR2 ignore it until convergence).
> With `CTRL REIN FIX/FIXL` the reinforcement is not increased (existing structures).

**Typical usage:**
```
REIN MOD SECT RMOD SAVE LCR 1 TITL 'ULS reinforcement'
REIN MOD BEAM RMOD SING LCR 2 TITL 'SLS crack width'
```

---

### DESI — Reinforced Concrete Design, Bending, Axial Force, Shear

Determines the required reinforcement (or the relative load capacity of unreinforced sections) for bending with axial force and the shear / torsion reinforcement.

**Syntax:**
```
DESI STAT KSV KSB AM1 AM2 AM3 AM4 AMAX
     SC1 SC2 SCS SS1 SS2 SS0 C1 C2 S1 S2 Z1 Z2
     SMOD TVS KTAU TTOL TANA TANB MSCD SCL DELR
```

| Parameter | Type       | Unit      | Default | Description |
|-----------|------------|-----------|---------|-------------|
| `STAT`    | enum       | —         | `*`     | Load condition (see table below) |
| `KSV`     | enum       | —         | `*`     | Material law of the cross-section (see table below) — only for special cases |
| `KSB`     | enum       | —         | `*`     | Material law of the reinforcements — only for special cases |
| `AM1`     | float      | `[%]`     | `*`     | Minimum reinforcement for beams (absolute [cm²] or % of section area) |
| `AM2`     | float      | `[%]`     | `*`     | Minimum reinforcement for columns |
| `AM3`     | float      | `[%]`     | `*`     | Minimum reinforcement of statically required cross-section |
| `AM4`     | float      | `[-]`     | `*`     | Factor for minimum reinforcement depending on normal force (EN 1992-1-1 9.5.2 / 9.6.2; negative = columns only) |
| `AMAX`    | float/enum | `[%]`     | `*`     | Maximum reinforcement, or `FIX` / `FIXL` / `FIXS` = current (longitudinal / shear) reinforcement fixed as maximum |
| `SC1`     | float      | `[-]`     | `*`     | Safety coefficient concrete bending |
| `SC2`     | float      | `[-]`     | `*`     | Safety coefficient concrete compression |
| `SCS`     | float      | `[-]`     | `*`     | Safety coefficient concrete shear |
| `SS1`     | float/enum | `[-]`     | `*`     | Safety coefficient reinforcing steel; `NRIL` = German Nachrechnungsrichtlinie |
| `SS2`     | float      | `[-]`     | `*`     | Safety coefficient tendon steel |
| `SS0`     | float      | `[-]`     | `*`     | Safety coefficient structural steel |
| `C1`      | float      | `[‰]`     | `*`     | Maximum compressive strain |
| `C2`      | float      | `[‰]`     | `*`     | Maximum centric compressive strain (positive = also limit strain in flange centres) |
| `S1`      | float      | `[‰]`     | `*`     | Optimum tensile strain (limit for symmetric reinforcement, ductility; negative = derived from DELR) |
| `S2`      | float      | `[‰]`     | `*`     | Maximum tensile strain |
| `Z1`      | float      | `[‰]`     | `*`     | Maximum effective strain of tendons |
| `Z2`      | float      | `[‰]`     | `*`     | Maximum effective tensional strain increment of tendons |
| `SMOD`    | enum       | —         | `*`     | Shear design mode: `YES` = shear design, `NO` = no shear design |
| `TVS`     | float      | `[N/mm²]` | `*`     | Deductional shear stress / stress limit |
| `KTAU`    | float/enum | —         | `*`     | Shear design for plates: `K1`, `K2`, `K1S`, `K2S` (DIN 1045), numeric k for EC2, `0.0` = no shear check |
| `TTOL`    | float      | `[-]`     | 0.02    | Tolerance for the limit values |
| `TANA`    | float      | `[-]`     | `*`     | Lower limit of strut inclination — **should be specified with TVAR (TANMIN) instead** |
| `TANB`    | float      | `[-]`     | `*`     | Upper limit of strut inclination — **should be specified with TVAR (TANMAX) instead** |
| `MSCD`    | float      | `[N/mm²]` | `*`     | Maximum tensile longitudinal stress σ_pc for shear capacity of tension members (default f_ctm) |
| `SCL`     | int        | —         | 3       | Plasticity control for steel and composite sections: `1` no limits; `2` outermost compressive yield strain limited; `3` compressive strain limited to yield value; `4` yield strain limit in tension and compression |
| `DELR`    | float      | `[-]`     | 1.0     | Redistribution δ for ductility x/d limit |

**STAT — load condition:**

| Value  | Meaning |
|--------|---------|
| `NO`   | Save reinforcement only |
| `SERV` | Serviceability loads |
| `ULTI` | Ultimate loads (standard ULS design) |
| `ACCI` | Accidental combination |
| `FIRE` | Fire design |
| `NONL` | Non-linear analysis combination |

**KSV / KSB — material laws:**

| Value | Meaning |
|-------|---------|
| `EL` / `ELD` | Linear elastic (no concrete tension) / with material safety factor |
| `SL` / `SLD` | Serviceability / with material safety factor |
| `UL` / `ULD` | Ultimate without / with material safety factor |
| `CAL` / `CALD` | Calculatoric mean values / with safety factors |
| `PL` / `PLD` | Plastic nominal / plastic design |
| `PLB` / `PLBD` | As PL / PLD but concrete with stress block |

> The internal forces must already contain the load factors (ULS combinations). The safety factors and stress-strain laws are preset from the INI-file of the design code depending on STAT — override SC1…SS0 and KSV/KSB only in special cases.
> The relevant minimum reinforcement is the maximum of AM1/AM2, the minimum reinforcement of the statically required section, the minimum reinforcement defined in AQUA and the reinforcement stored in the database.
> The statically determined part of prestress is deducted automatically from the design forces.
> With `BETA` in `BEAM` additional moments from slenderness are applied (compression members); the design is then always biaxial.
> The ratio V_Ed/V_Rd,max and the shift a_l are saved to the database.

**Typical usage:**
```
$ Standard ULS design (bending + shear)
DESI STAT ULTI

$ ULS design without shear design
DESI STAT ULTI SMOD NO

$ Accidental design situation
DESI STAT ACCI
```

---

### NSTR — Non-linear Stress and Strain

Determines non-linear stresses, strains and stiffnesses in cracked condition. Performs crack width checks, decompression checks, stress/strain limit checks and fatigue checks for RC; non-linear resistance checks for steel sections.

**Syntax:**
```
NSTR KMOD KSV KSB KMIN KMAX ALPH FMAX
     CRAC CW BB HMIN HMAX CW- FFCT
     CHKC CHKT CHKR CHKS FAT SIGS TANS TANC DUMP
```

| Parameter | Type       | Unit      | Default | Description |
|-----------|------------|-----------|---------|-------------|
| `KMOD`    | enum       | —         | —       | Load condition and stiffness evaluation (required, see table below) |
| `KSV`     | enum       | —         | `*`     | Material law of the cross-section (same values as DESI) |
| `KSB`     | enum       | —         | `*`     | Material law of reinforcements and tension stiffening |
| `KMIN`    | float      | `[-]`     | 0.01    | Minimum stiffness (relative to elastic) |
| `KMAX`    | float      | `[-]`     | 4.00    | Maximum stiffness |
| `ALPH`    | float      | `[-]`     | 0.4     | Numerical damping factor |
| `FMAX`    | float      | `[-]`     | 5.0     | Numerical acceleration factor |
| `CRAC`    | enum       | —         | `NO`    | Design for crack width / decompression (see table below) |
| `CW`      | float      | `[mm]`    | `*`     | Crack width w_k (default from INI, typically 0.2–0.3), or height of decompression zone for DECO; `999` = no increase of reinforcement |
| `BB`      | float      | `[-]`     | `*`     | Duration coefficient (EN 1992: k_t = 0.2 + 0.4·BB, BB 0.5 long-term / 1.0 short-term; code-specific meanings) |
| `HMIN`    | float      | `[mm]`    | 0.0     | Minimum height of zone (nominal cover, BS/IS) |
| `HMAX`    | float      | `[mm]`    | 800     | Maximum height of tension zone |
| `CW-`     | float      | `[mm]`    | `CW`    | Crack width or factor for the top side ("above") |
| `FFCT`    | float      | `[-]`     | —       | Factor on mean tensile strength |
| `CHKC`    | float      | `[-]`/`[N/mm²]` | — | Strain/stress to be checked for concrete |
| `CHKT`    | float      | `[-]`/`[N/mm²]` | — | Strain/stress to be checked for tendons |
| `CHKR`    | float      | `[-]`/`[N/mm²]` | — | Strain/stress to be checked for reinforcement |
| `CHKS`    | float      | `[-]`/`[N/mm²]` | — | Strain/stress to be checked for structural steel |
| `FAT`     | enum       | —         | —       | Fatigue design check: `EN92` (EN 1992 6.8), `DINF` (DIN / DIN FB) |
| `SIGS`    | float      | `[N/mm²]` | `*`     | Allowable stress range for reinforcement (fatigue) or allowable steel stress for TAB |
| `TANS`    | float      | `[-]`     | 0.756   | Inclination of struts for reinforcement (fatigue) |
| `TANC`    | float      | `[-]`     | 0.571   | Inclination of struts for concrete stress (fatigue) |
| `DUMP`    | string     | —         | —       | File name for the history of non-linear stresses of dynamic load cases (Lit96) |

**KMOD — load condition / stiffness method:**

| Value  | Meaning |
|--------|---------|
| `SERV` | Serviceability — stress evaluation without change of stiffness |
| `ULTI` | Ultimate limit state (steel: non-linear resistance check) |
| `ACCI` | Accidental combination |
| `FIRE` | Fire |
| `NONL` | Non-linear analysis combination |
| `S0` / `S1` / `SN` | Secant stiffness without iteration / from given curvatures / from given moments |
| `K0` / `K1` / `KN` | Plastic strains without iteration / from given curvatures / from given moments |
| `T0` / `T1` / `TN` | Tangent stiffness without iteration / from given curvatures / from given moments |

> The stiffness methods may be prefixed with the load condition `S`, `U`, `A`, `F` or `N` (e.g. `US1`, `SS1`). Stiffness iterations (other than S0) are only meaningful when NSTR is used inside ASE for a non-linear analysis.

**CRAC — crack width / decompression:**

| Value  | Meaning |
|--------|---------|
| `NO`   | No check (default) |
| `YES`  | Calculate crack width (increase reinforcement if needed) |
| `TAB`  | Limitation of steel stress with tabulated values (EN 1992 Tab. 7.2/7.3) |
| `DECO` | Decompression around tendons (CW = distance to duct perimeter) |

> NSTR needs the actual reinforcement: from AQUA (minimum/basic reinforcement), from `BEAM ... CS AS`, or from a preceding `DESI` saved with `REIN ... RMOD SAVE`.
> Unless `CTRL REIN FIX/FIXL` is set, AQB increases the reinforcement to fulfil crack width / fatigue requirements.
> Default material laws: Serviceability KSV = KSB = SL; ULS from INI-file; ACCI SL; NONL CAL.
> CHK values: absolute strain with unit `[‰]`, explicit stress in `[MPa]`, or relative to material strength (+ f_y/f_c, − f_t/f_ck).

**Typical usage:**
```
$ Crack width check w_k = 0.3 mm (EN 1992)
NSTR KMOD SERV CRAC YES CW 0.3

$ Crack control by limitation of steel stress (tabulated)
NSTR KMOD SERV CRAC TAB CW 0.2

$ Non-linear resistance check of a steel section
NSTR KMOD ULTI

$ Fatigue check EN 1992
NSTR KMOD SERV FAT EN92
```

---

### CAPA — Sectional Capacity Evaluation

Creates single values or diagrams of sectional capacities (N–M interaction, moment–curvature, strains for given forces).

**Syntax:**
```
CAPA NCS CS TASK STAT
     N VY VZ MT MY MZ MB MT2
     AS0 AS1 ... AS9 CMNT
```

| Parameter | Type   | Unit     | Default | Description |
|-----------|--------|----------|---------|-------------|
| `NCS`     | int    | —        | —       | Cross-section number (required) |
| `CS`      | int    | —        | 0       | Construction stage |
| `TASK`    | enum   | —        | `STR`   | Task to perform (see table below) |
| `STAT`    | enum   | —        | `ULTI`  | State and safety factors: `NONE` (characteristic), `SERV`, `ULTI`, `ACCI`, or material law `EL`/`ELD`, `SL`/`SLD`, `UL`/`ULD`, `CALC`/`CALD`, `PL`/`PLD`, `PLB`/`PLBD` |
| `N`       | float  | `[kN]`   | 0       | Axial force / axial strain |
| `VY`      | float  | `[kN]`   | 0       | Shear force / shear strain |
| `VZ`      | float  | `[kN]`   | 0       | Shear force / shear strain |
| `MT`      | float  | `[kNm]`  | 0       | Total torsional moment / strain |
| `MY`      | float  | `[kNm]`  | 0       | Bending moment / curvature |
| `MZ`      | float  | `[kNm]`  | 0       | Bending moment / curvature |
| `MB`      | float  | `[kNm²]` | 0       | Warping moment |
| `MT2`     | float  | `[kNm]`  | 0       | Secondary torsional moment |
| `AS0`–`AS9` | float | `[cm²]` | `*`     | Reinforcement of layer 0…9 (absolute [cm²] or factor [-] on section values) |
| `CMNT`    | string | —        | `*`     | Short comment (Lit16) |

**TASK — tasks:**

| Value  | Meaning |
|--------|---------|
| `STR`  | Evaluation for given strains (default) |
| `STRN` | Evaluation of strains for given forces |
| `DESI` | Evaluation of required reinforcement |
| `MC`   | Moment–curvature relation for given N |
| `NM`   | Normal force / moment interaction |
| `NMS`  | Normal force / moment / shear interaction |
| `NM2`  | Complete NM with alternating moments |
| `NMS2` | Complete NMS with alternating moments |

> Forces may be given as values, as factors `[-]` on the single-value capacity, or as strains with explicit unit `[‰]`. Curvatures are differences of strains across the section height.

**Typical usage:**
```
$ N-M interaction diagram of section 1 in ULS
CAPA NCS 1 TASK NM STAT ULTI MY 1.0[-]

$ Moment-curvature relation for N = -500 kN
CAPA NCS 1 TASK MC STAT ULTI N -500 MY 1.0[-]
```

---

## Complete AQB Block Examples

### Example 1a — Stand-alone RC section design, ULS only (AQUA + AQB)

The simplest case: design forces given with `S` (stored as load case 0) and one design task.

```
+PROG AQUA urs:1
HEAD Materials and cross-section

!*!Label Design Code
NORM DC EN NDC 199X-200X

!*!Label Materials
CONC NO 1 TYPE C FCN 30 TITL 'C30/37'
STEE NO 2 TYPE B CLAS 500B TITL 'B500B'

!*!Label Cross-Section
SREC NO 1 H 600 B 300 MNO 1 MRF 2 SO 50 SU 50 TITL 'Beam 300/600'

END

+PROG AQB urs:2
HEAD ULS design of section 1 for given design forces

!*!Label Output Control
ECHO FULL NO
ECHO DESI YES
ECHO REIN FULL

!*!Label Design Forces (factored, load case 0)
S NCS 1 NO 1 X 0.0 N -250 VZ 180 MY 320

!*!Label ULS Design
DESI STAT ULTI

END
```

### Example 1b — Stand-alone RC section, ULS design + SLS crack width (external section)

When ULS and SLS forces differ, define an **external section** (`BEAM ... TYPE SECT`) so that the forces can be stored under explicit load cases and the reinforcement is kept for the SLS block. The external system is reactivated in later blocks with `BEAM TYPE SECT`. (AQUA block as in Example 1a.)

```
+PROG AQB urs:2
HEAD ULS design of external section

ECHO FULL NO
ECHO DESI YES

!*!Label External Section: element 1, x = 0, cross-section 1
BEAM FROM 1 X 0.0 NCS 1 TYPE SECT

!*!Label ULS Design Forces
LC NO 101 TYPE (D) TITL 'ULS design'
S NCS 1 NO 1 X 0.0 N -250 VZ 180 MY 320

!*!Label Reinforcement Case
REIN MOD SECT RMOD SAVE LCR 1

!*!Label ULS Design
DESI STAT ULTI

END

+PROG AQB urs:3
HEAD SLS crack width check of external section

ECHO FULL NO
ECHO CRAC YES

!*!Label Reactivate External System
BEAM TYPE SECT

!*!Label Frequent Combination Forces
LC NO 201 TYPE (F) TITL 'SLS frequent'
S NCS 1 NO 1 X 0.0 N -150 MY 190

!*!Label Reinforcement Case
REIN MOD SECT RMOD SING LCR 2

!*!Label Crack Width w_k = 0.3 mm
NSTR KMOD SERV CRAC YES CW 0.3

END
```

### Example 2 — Section design on a full system (AQB part)

Continuous RC beam analysed with ASE; ULS and SLS envelopes created with MAXIMA (see `MAXIMA.md`, Complete Block Example: `COMB 1 EXTR DESI BASE 2100`, `COMB 3 EXTR FREQ BASE 2300`, `SUPP ... ETYP BEAM TYPE VZ,MY`).

```
+PROG AQB urs:6
HEAD ULS bending and shear design of all beams

!*!Label Output Control
ECHO FULL NO
ECHO DESI YES
ECHO REIN YES

!*!Label Control
CTRL VM STD                    $ shift rule offset of tensile force envelope

!*!Label ULS Envelopes from MAXIMA (max/min VZ, max/min MY)
LC 2125,2126,2129,2130

!*!Label Reinforcement Case
REIN MOD SECT RMOD SAVE LCR 1 TITL 'ULS reinforcement'

!*!Label ULS Design
DESI STAT ULTI

END

+PROG AQB urs:7
HEAD SLS crack width check of all beams

ECHO FULL NO
ECHO CRAC YES

!*!Label SLS Frequent Envelopes from MAXIMA (max/min MY)
LC 2329,2330

!*!Label Reinforcement Case
REIN MOD SECT RMOD SING LCR 2 TITL 'SLS reinforcement'

!*!Label Crack Width
NSTR KMOD SERV CRAC YES CW 0.3

END
```

> Alternative selection by combination type: `LC TYPE (D)` selects all ULS design combination load cases (MAXIMA `EXTR DESI` results or SOFILOAD combination load cases with `TYPE (D)`).
> When the combinations were built as explicit load cases in SOFILOAD (`LC 101 TYPE (D)` + `COPY`) and analysed in ASE, select them directly: `LC 101,102,103` or `LC TYPE (D)`.

### Example 3 — Steel section check

```
+PROG AQB urs:6
HEAD Steel section check EN 1993

ECHO FULL NO
ECHO STRE YES
ECHO C2T YES

LC TYPE (D)

STRE C M0                     $ plastic resistance with interaction, gamma_M0

END
```

### Example 4 — Timber stress check EN 1995 with load duration classes

MAXIMA combinations with assigned load duration (`COMB 11 EXTR DESI TYPE PT BASE 3100`, `COMB 12 … TYPE LT BASE 3200`, `COMB 13 … TYPE MT BASE 3300`, see `MAXIMA.md`). AQB selects k_mod from the load duration type of each result load case. The material is defined in AQUA with service class, e.g. `TIMB NO 1 TYPE GL CLAS 24:1` (GL24, service class 1).

```
+PROG AQB urs:7
HEAD Timber stress check for all ULS combinations

!*!Label Load Cases: all load duration classes
LC TYPE (PT),(LT),(MT)

!*!Label Store extreme values of the block as LC 201
COMB GMAX LCST 201 TITL 'extremal values'

!*!Label Stress Check with design strengths (k_mod, gamma_M)
STRE E F
ECHO STRE YES

END

+PROG AQB urs:8
HEAD Timber stress check for fire (accidental combination)

ECHO STRE YES
LC TYPE (A)                   $ results of MAXIMA COMB ... EXTR ACCI TYPE ACCI
COMB GMAX LCST 209 TITL 'extreme values of fire'
STRE E F                      $ gamma_M = 1.0 via AQUA TIMB ... SCM 1.0; k_mod,fi = 1.0 (no load duration)

END
```

> One AQB block per load-duration selection is possible as well (e.g. `LC TYPE (LT)` only) to check a single load duration class separately; use a different `LCST` in each block.
> The combination load case stored with `COMB GMAX LCST` contains the governing stresses / utilisations of the block and is used for graphical evaluation.

---

## Unit Summary for AQB

| Quantity | Unit | Parameters |
|----------|------|------------|
| Positions along beam | `[m]` | `X`, `XE` (BEAM, S, TEND) |
| Section coordinates | `[mm]` | `Y`, `Z` (S, TEND), `YHR`, `ZHR` |
| Forces | `[kN]` | `N`, `VY`, `VZ` (S, CAPA), `ZZ` (TEND) |
| Moments | `[kNm]` | `MT`, `MY`, `MZ`, `MT2` |
| Warping moment | `[kNm²]` | `MB` |
| Stresses | `[N/mm²]` | STRE `SC`…`ZDIF`; DESI `TVS`, `MSCD`; NSTR `SIGS` |
| Strains | `[‰]` | DESI `C1`, `C2`, `S1`, `S2`, `Z1`, `Z2`; CTRL `ELIM` |
| Crack width / zone heights | `[mm]` | NSTR `CW`, `CW-`, `HMIN`, `HMAX` |
| Reinforcement ratios | `[%]` | DESI `AM1`, `AM2`, `AM3`, `AMAX` |
| Reinforcement areas | `[cm²]`, `[cm²/m]` | BEAM `CSi` with `CS AS` / `CS ASV`; CAPA `AS0`–`AS9` |
| Tendon / duct areas | `[mm²]` | TEND `AZ`, `AHR` |
| Time | `[days]` | EIGE `T`, `T0`, `TS` |
| Temperature | `[°C]` | EIGE `TEMP`, TEND `TEMP` |
| Humidity | `[%]` | EIGE `RH` |
| Dimensionless factors | `[-]` | `BETA`, `BETS`, `LAM*`, `SFAC`, `F1`–`F6`, `GAMU`…`GAMA`, `KMIN`, `KMAX`, `ALPH`, `FMAX`, `BB`, `DELR`, `SC1`…`SS0` |
