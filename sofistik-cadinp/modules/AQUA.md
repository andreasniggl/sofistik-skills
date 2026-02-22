# Module: AQUA — Materials and Cross-Sections

## Purpose
AQUA defines all materials and cross-sections for a SOFiSTiK project. It must always run as the first `+PROG` block, before SOFIMSHC and any analysis module. All cross-section geometry is in **millimetres (mm)**; material strengths in **N/mm²**; unit weights in **kN/m³**.

## Load this file when
Any structural analysis is being performed (required for every analysis).

## Module block template
```
+PROG AQUA urs:1
HEAD <description>

!*!Label Design Code
NORM DC DIN NDC EN199X-200X       $ design code — must be first

!*!Label Concrete Materials
CONC NO 1 TYPE C FCN 30 TITL 'C30/37'

!*!Label Steel Materials
STEE NO 11 TYPE B CLAS 500B TITL 'B500B'

!*!Label Cross-Sections
SREC NO 1 H 250 MNO 1 MRF 11 SO 35 SU 35 TITL 'Slab 250mm'

END
```

> **Key rules:**
> - `NORM` must appear **first** — it controls all material defaults, partial factors, and INI-file settings.
> - Material numbers share a single namespace: concrete, steel, and timber all use the same range 1–999.
> - A `SREC` or `PROF` with a given `NO` replaces any previously defined section with that number.

---

## Commands

| Command | Purpose |
|---------|---------|
| `NORM`  | Select design code and country |
| `CONC`  | Define concrete material |
| `STEE`  | Define steel / metal material |
| `TIMB`  | Define timber / fibre material |
| `SREC`  | Rectangular / T-beam / plate cross-section |
| `PROF`  | Rolled steel profile (I, H, U, L, T, …) |
| `CIRC`  | Circular element within a `SECT` polygon section |
| `CABL`  | Cable / rope cross-section |

---

### NORM — Design Code Selection

Selects the design code family and country. Must be the **first record** in any AQUA block. All material defaults, partial factors, load combination coefficients, and INI-file settings depend on this record.

**Syntax:**
```
NORM DC NDC COUN CAT LON LAT ALT G WIND SNOW SEIS WCAT UNIT LANG
```

| Parameter | Type   | Unit   | Default | Description |
|-----------|--------|--------|---------|-------------|
| `DC`      | enum   | —      | `DIN`   | Design code family (see table below) |
| `NDC`     | string | —      | —       | Specific sub-code within the family (e.g. `EN199X-200X`). The INI-file loaded is `DC_NDC.INI`. |
| `COUN`    | string | —      | `*`     | Country code for EN boxed values — `00` = general EN, `HK` = Hong Kong deviations to BS 8110/5400 |
| `CAT`     | string | —      | —       | Category or class (code-dependent). Use `USER` for historic codes without INI-file. |
| `LON`     | float  | `[°]`  | 0       | Geographic longitude |
| `LAT`     | float  | `[°]`  | 45      | Geographic latitude |
| `ALT`     | float  | `[m]`  | 0.0     | Altitude above sea level |
| `G`       | float  | `[m/s²]` | `*`   | Gravity acceleration — set only when the true local value is required; otherwise the code default applies (EN: 10 m/s²; US/CSA: 9.80665 m/s²) |
| `WIND`    | enum   | —      | `*`     | Wind zone — specify `NONE` to suppress |
| `SNOW`    | enum   | —      | `*`     | Snow zone — specify `NONE` to suppress |
| `SEIS`    | enum   | —      | `*`     | Seismic zone — specify `NONE` to suppress |
| `WCAT`    | enum   | —      | `*`     | Terrain category for wind |
| `UNIT`    | enum   | —      | `*`     | Global unit set — only evaluated in AQUA or TEMPLATE |
| `LANG`    | enum   | —      | `*`     | Default output language — only evaluated in AQUA or TEMPLATE |

**DC — design code families:**

| Value | Standard |
|-------|----------|
| `EN`  | Eurocodes (no national annex) |
| `DIN` | German Standard |
| `OEN` | Austrian Standard |
| `SIA` | Swiss Standard |
| `BS`  | British Standard |
| `AS`  | Australian Standard |
| `NZS` | New Zealand Standard |
| `US`  | US Standards (ACI etc.) |
| `CSA` | Canadian Standard |
| `GB`  | Chinese Building Codes |
| `IS`  | Indian Standard |
| `NF`  | French Standard |
| `UNI` | Italian Standard |
| `UNE` | Spanish Standard |
| `SS`  | Swedish Standard |
| `DS`  | Danish Standard |
| `NS`  | Norwegian Standard |
| `SP`  | Russian Standard |
| `SFS` | Finnish Standard |
| `NEN` | Netherlands Standard |
| `NBN` | Belgian Standard |
| `NBR` | Brazilian Standard |
| `ZA`  | South African Standard |
| `IL`  | Israeli Standard |

**Eurocode with National Annex — preferred DC / NDC combinations:**

To activate a national annex, use the country's DC (not `EN`) together with the Eurocode NDC. The NDC string should be set as `EN199X-200X` denoting that it includes all material variants.

| Country | DC | NDC |
|---------|----|-----|
| Germany | `DIN` | `EN199X-200X` |
| Austria | `OEN` | `EN199X-200X` |
| UK | `BS` | `EN199X-200X` |
| France | `NF` | `EN199X-200X` |
| Sweden | `SS` | `EN199X-200X` |
| Denmark | `DS` | `EN199X-200X` |
| Norway | `NS` | `EN199X-200X` |
| Finland | `SFS` | `EN199X-200X` |
| Netherlands | `NEN` | `EN199X-200X` |
| Belgium | `NBN` | `EN199X-200X` |

**Other common DC / NDC combinations:**

| Country | DC | NDC | Description |
|---------|----|-----|-------------|
| Swizerland    | `SIA` | `26X` | SIA 262,263 — all swiss design codes |
| United-States | `US`  | `ACI-318-19` | ACI 318-19 — American standard building code for structural concrete |
| Canada | `CSA` | `S6-19` | CSA S6-19 — Canadian Highway bridge design code |
| India | `IS`  | `456` | IS 456 — Indian standard concrete |
| Italy | `UNI`  | `DM-2018` | Decreto Ministeriale 2018 |

> Do not redefine `NORM` after actions or load cases have been defined. A temporary redefinition for design (e.g. switching between concrete and steel code) is allowed only if the action side does not change.
> Boxed values can be adjusted manually with `TVAR`.

**Typical usage:**
```
$ Eurocode with German National Annex (all material variants)
NORM DC DIN NDC EN199X-200X

$ Eurocode with British National Annex (all material variants)
NORM DC BS NDC EN199X-200X

$ Plain Eurocode without national annex
NORM DC EN NDC 199X-200X COUN 00

$ Swiss concrete standard SIA 262
NORM DC SIA NDC 26X

$ US ACI 318-19
NORM DC US NDC ACI-318-19
```

---

### CONC — Concrete Material

Defines a concrete material. Properties not explicitly given are derived from `FCN` and the active design code INI-file.

**Syntax:**
```
CONC NO TYPE FCN FC FCT FCTK EC MUE GAM ALFA SCM TYPR FCR ECR FBD
     FFAT FCTD FEQR FEQT GMOD KMOD RHO GF MUEC SCM0 SCM1 SCM2 TITL
```

| Parameter | Type   | Unit     | Default | Description |
|-----------|--------|----------|---------|-------------|
| `NO`      | int    | —        | 1       | Material number (1–999) |
| `TYPE`    | enum   | —        | `*`     | Concrete type (code-dependent — see table below) |
| `FCN`     | float  | `[N/mm²]`| `*`     | Nominal strength class: f_ck / f_cwk / f_c' (cylindrical unless the active code uses cube strength) |
| `FC`      | float  | `[N/mm²]`| `*`     | Compressive design strength — derived from FCN if omitted |
| `FCT`     | float  | `[N/mm²]`| `*`     | Mean tensile strength — derived from FCN if omitted |
| `FCTK`    | float  | `[N/mm²]`| `*`     | Lower fractile tensile strength f_ctk,0.05 |
| `EC`      | float  | `[N/mm²]`| `*`     | Elastic modulus (secant E_cm) — derived from FCN if omitted |
| `MUE`     | float  | —        | 0.2     | Poisson's ratio |
| `GAM`     | float  | `[kN/m³]`| 25      | Unit weight |
| `ALFA`    | float  | `[1/K]`  | 1E-5    | Thermal expansion coefficient |
| `SCM`     | float  | —        | `*`     | Material safety factor (prefer `SCM0`/`SCM1`/`SCM2` instead) |
| `TYPR`    | enum   | —        | `*`     | Serviceability stress-strain line: `LINE` (constant E), `A` or `B` (short time, EN 1992) |
| `FCR`     | float  | `[N/mm²]`| `*`     | Concrete strength for non-linear analysis |
| `ECR`     | float  | `[N/mm²]`| `*`     | Elastic modulus for serviceability / non-linear analysis. May be given as a factor with unit `[-]` (e.g. `ECR 0.85 [-]` per DAfStB Heft 600). |
| `FBD`     | float  | `[N/mm²]`| `*`     | Design bond strength |
| `FFAT`    | float  | `[N/mm²]`| `*`     | Fatigue strength f_cd,fat |
| `FCTD`    | float  | `[N/mm²]`| `*`     | Design tensile strength (explicit, e.g. for steel-fibre concrete) |
| `FEQR`    | float  | `[N/mm²]`| 0.0     | Equivalent tensile strength after cracking (steel fibre). Tensile concrete participates in design only when non-zero. |
| `FEQT`    | float  | `[N/mm²]`| 0.0     | Ultimate tensile strength (steel fibre) |
| `GMOD`    | float  | `[N/mm²]`| `*`     | Shear modulus |
| `KMOD`    | float  | `[N/mm²]`| `*`     | Bulk modulus |
| `RHO`     | float  | `[kg/m³]`| `*`     | Density — required for light-weight concrete. When given, GAM and EC are automatically adjusted: E_cml = E_cm · (ρ/2200)². |
| `GF`      | float  | `[N/mm]` | `*`     | Fracture energy (MC 2010, 5.1.5.2) |
| `MUEC`    | float  | —        | `*`     | Friction coefficient in cracks |
| `SCM0`    | float  | —        | `*`     | Material safety factor for serviceability stress-strain curve |
| `SCM1`    | float  | —        | `*`     | Material safety factor for ultimate limit stress-strain curve |
| `SCM2`    | float  | —        | `*`     | Material safety factor for calculatoric stress-strain curve. Defaults to 1.5 for EN codes (1.6 in Italy). |
| `TITL`    | string | —        | `*`     | Material designation (up to 32 characters) |

**TYPE — concrete type by design code:**

| Code family | TYPE | Meaning |
|-------------|------|---------|
| EN / DIN 1045-1 / OEN / SIA 262 / IRC 112 | `C` | Regular concrete (cylindrical f_ck) |
| EN / OEN / SIA 262 | `LC` | Light-weight concrete |
| DIN 1045 old / DIN 4227 | `B` | Regular concrete |
| DIN 4227 | `SB` | Prestressed concrete |
| DIN 4227 LW | `LB` | Light-weight concrete |
| BS 8110 | `BS` | Normal weight concrete |
| ACI 318M | `ACI` | Normal weight concrete |
| ACI 318M LW | `LACI` | Light-weight concrete |
| CSA A23.3 | `CSA` | Normal weight concrete |
| CSA LW | `LCSA` | Light-weight concrete |
| GB 50010 | `GB` | Standard / high-strength concrete |
| Italian NTC | `CAN` / `CAL` | Regular / lightweight (2008/2018) |
| AS 3600 | `AS` | Australian standard |
| NZS 3101 | `NZS` | New Zealand standard |
| IS 456 | `IS` | Indian standard |
| SP (Russia) | `SNIP` / `LSNI` | Normal / lightweight |
| Israeli SI 466 | `IL` | Standard concrete |
| Linear elastic (no tension) | `CE` | Elastic-no-tension model |

Cement type suffix (append to TYPE for creep/shrinkage analysis): `N` (normal), `S` (slow), `R` (rapid). For fire design add `C` for calcareous aggregates: `NC`, `SC`, `RC`.

**Default derivations (EN 1992):**

| Property | Formula |
|----------|---------|
| `FC`   | 0.85 · f_ck (or α_cc · f_ck per national annex) |
| `FCT`  | 0.3 · f_ck^(2/3) for f_ck ≤ 55; 2.12 · ln((f_ck+8)/10+1) otherwise |
| `EC`   | 22000 · (f_cm/10)^0.3 |
| `FBD`  | 2.25 · f_ct,0.05 / γ |

**Typical usage:**
```
$ C30/37 Eurocode concrete
CONC NO 1 TYPE C FCN 30 TITL 'C30/37'

$ C25/30
CONC NO 2 TYPE C FCN 25 TITL 'C25/30'

$ Light-weight concrete LC20/22
CONC NO 3 TYPE LC FCN 20 RHO 1800

$ Linear-elastic concrete (no tension), fc = 12 N/mm²
CONC NO 10 TYPE CE FCN 12

$ BS 8110 concrete, cube strength 40
CONC NO 1 TYPE BS FCN 40

$ ACI concrete, f'c = 28 MPa
CONC NO 1 TYPE ACI FCN 28
```

---

### STEE — Steel / Metal Material

Defines structural steel, reinforcing steel, prestressing steel, or aluminium alloy. The `TYPE` controls which cross-section and reinforcement usage is permitted.

**Syntax:**
```
STEE NO TYPE CLAS FY FT FP ES MUE GAM ALFA EPSY EPST REL1 REL2
     R K1 FDYN FYC FTC TMAX GMOD KMOD SCM0 SCM1 SCM2 TITL
```

| Parameter | Type   | Unit     | Default | Description |
|-----------|--------|----------|---------|-------------|
| `NO`      | int    | —        | 1       | Material number (1–999) |
| `TYPE`    | enum   | —        | `*`     | Material type (see table below) |
| `CLAS`    | string | —        | `*`     | Steel class or quality grade (code-dependent, e.g. `355`, `500B`, `Y1860S7`) |
| `FY`      | float  | `[N/mm²]`| `*`     | Yield strength (f_0.01 or f_0.02) |
| `FT`      | float  | `[N/mm²]`| `*`     | Tensile strength |
| `FP`      | float  | `[N/mm²]`| `*`     | Elastic limit (proportionality limit) |
| `ES`      | float  | `[N/mm²]`| `*`     | Elastic modulus. EN default: 210000 N/mm². |
| `MUE`     | float  | —        | 0.3     | Poisson's ratio |
| `GAM`     | float  | `[kN/m³]`| `*`     | Unit weight. EN default: 78.5 kN/m³. |
| `ALFA`    | float  | `[1/K]`  | `*`     | Thermal expansion coefficient. EN default: 1.2×10⁻⁵ 1/K. |
| `EPSY`    | float  | `[‰]`    | `*`     | Permanent strain at yield FY. Negative = relative to FP/ES; positive = absolute. |
| `EPST`    | float  | `[‰]`    | `*`     | Ultimate strain ε_uk |
| `REL1`    | float  | `[%]`    | `*`     | Relaxation coefficient at 0.70 f_pk |
| `REL2`    | float  | `[%]`    | 0       | Relaxation coefficient at 0.55 f_pk |
| `R`       | float  | —        | `*`     | Relative bond strength |
| `K1`      | float  | —        | 0.8/R   | Bond coefficient for crack width (EN 1992) |
| `FDYN`    | float  | `[N/mm²]`| `*`     | Allowed stress range (fatigue) |
| `FYC`     | float  | `[N/mm²]`| FY      | Compressive yield strength (f_0.02) |
| `FTC`     | float  | `[N/mm²]`| FT      | Compressive strength |
| `TMAX`    | float  | `[mm]`   | `*`     | Maximum plate thickness (structural steel) or bar diameter (rebar/prestress) for thickness-dependent values and FDYN |
| `GMOD`    | float  | `[N/mm²]`| `*`     | Shear modulus |
| `KMOD`    | float  | `[N/mm²]`| `*`     | Bulk modulus |
| `SCM0`    | float  | —        | `*`     | Safety factor for sectional design |
| `SCM1`    | float  | —        | `*`     | Safety factor for stability design |
| `SCM2`    | float  | —        | `*`     | Safety factor for rupture design |
| `TITL`    | string | —        | `*`     | Material name (up to 32 characters) |

**TYPE — steel / metal types:**

| Value | Meaning |
|-------|---------|
| `S`   | Structural steel — permitted for cross-sections only |
| `B`   | Reinforcing steel |
| `Y`   | Prestressing steel |
| `YC`  | Prestressing steel for cables |
| `AW`  | Aluminium alloy |

> Structural steel types (`S`, `AW`) are only allowed for cross-sections. Prestressing steel (`Y`, `YC`) is only for reinforcements, cables, and tendons.

**Common EN 1993-1-1 structural steel grades (t ≤ 40 mm):**

| CLAS   | FY `[N/mm²]` | FT `[N/mm²]` |
|--------|--------------|--------------|
| `S235` | 235 | 360 |
| `S275` | 275 | 430 |
| `S355` | 355 | 490 |
| `S450` | 440 | 550 |
| `S460N`| 460 | 540 |

Append `T` to the grade for t = 40–80 mm (e.g. `S355T`). For high-strength grades from EN 10025-6 specify `TMAX` to get thickness-dependent values.

**Typical usage:**
```
$ S355 structural steel (EN)
STEE NO 10 TYPE S CLAS 355

$ B500B reinforcing steel (EN 1992)
STEE NO 11 TYPE B CLAS 500B

$ Y1860 prestressing strand
STEE NO 12 TYPE Y CLAS 1860S7

$ Prestressing steel for cables
STEE NO 13 TYPE YC CLAS 1570

$ Custom structural steel, explicit values
STEE NO 20 TYPE S FY 275 FT 430 ES 210000 GAM 78.5 TITL 'S275 custom'
```

---

### TIMB — Timber and Fibre Material

Defines timber, glued-laminated timber, plywood, CLT, or composite fibre materials. Properties are orthotropic.

**Syntax:**
```
TIMB NO TYPE CLAS EP G E90 QH QH90 GAM ALFA SCM FM FT0 FT90 FC0 FC90
     FV FVR FVB FM90 G90 OAL OAF KMOD KMO1 KMO2 KMO3 KMO4 KDEF TMAX RHO TITL
```

| Parameter | Type   | Unit     | Default | Description |
|-----------|--------|----------|---------|-------------|
| `NO`      | int    | —        | 1       | Material number (1–999) |
| `TYPE`    | enum   | —        | `*`     | Material type (see table below) |
| `CLAS`    | string | —        | `*`     | Strength class or quality (e.g. `C24`, `GL28h`). Append service class with colon: `C24:2`. |
| `EP`      | float  | `[N/mm²]`| `*`     | Elastic modulus parallel to fibre |
| `G`       | float  | `[N/mm²]`| `*`     | Shear modulus |
| `E90`     | float  | `[N/mm²]`| `*`     | Elastic modulus normal to fibre |
| `QH`      | float  | —        | `*`     | Poisson's ratio yz (plywood panels) |
| `QH90`    | float  | —        | `*`     | Poisson's ratio xy / xz (solid wood) |
| `GAM`     | float  | `[kN/m³]`| `*`     | Unit weight |
| `ALFA`    | float  | `[1/K]`  | 0.0     | Temperature elongation coefficient |
| `SCM`     | float  | —        | 1.3/`*` | Material safety factor |
| `FM`      | float  | `[N/mm²]`| `*`     | Bending strength (characteristic) |
| `FT0`     | float  | `[N/mm²]`| `*`     | Tensile strength parallel to fibre |
| `FT90`    | float  | `[N/mm²]`| `*`     | Tensile strength normal to fibre |
| `FC0`     | float  | `[N/mm²]`| `*`     | Compressive strength parallel to fibre |
| `FC90`    | float  | `[N/mm²]`| `*`     | Compressive strength normal to fibre |
| `FV`      | float  | `[N/mm²]`| `*`     | Shear strength at centre (shear force). Specify as k_cr · f_v (crack-reduced). |
| `FVR`     | float  | `[N/mm²]`| `*`     | Shear strength at edge (torsion) |
| `FVB`     | float  | `[N/mm²]`| `*`     | Shear strength for plate bending |
| `FM90`    | float  | `[N/mm²]`| `*`     | Bending strength normal to fibres |
| `G90`     | float  | `[N/mm²]`| `*`     | Shear modulus for plate bending |
| `OAL`     | float  | `[°]`    | 0.0     | Meridian angle of anisotropy |
| `OAF`     | float  | `[°]`    | 0.0     | Descent angle of anisotropy |
| `KMOD`    | float  | —        | `*`     | Strength modification factor for permanent loading |
| `KMO1`    | float  | —        | `*`     | Strength modification factor for long-term loading |
| `KMO2`    | float  | —        | `*`     | Strength modification factor for medium-term loading |
| `KMO3`    | float  | —        | `*`     | Strength modification factor for short-term loading |
| `KMO4`    | float  | —        | `*`     | Strength modification factor for very short-term loading |
| `KDEF`    | float  | —        | `*`     | Modification factor for long-term deflections |
| `TMAX`    | float  | `[mm]`   | `*`     | Maximum thickness for plates (thickness-dependent properties) |
| `RHO`     | float  | `[kg/m³]`| `*`     | Characteristic density |
| `TITL`    | string | —        | `*`     | Material designation (up to 32 characters) |

**TYPE — timber and fibre material types:**

| TYPE   | CLAS examples    | Description |
|--------|-----------------|-------------|
| `C`    | 14…50           | Solid softwood (EN 338 / EN 1995) |
| `D`    | 30…70           | Solid hardwood |
| `GL`   | 24, 28, 32, 36 / 24C, 28C… | Homogeneous / combined glulam |
| `PLY`  | 25, 40, 50, 60  | Plywood |
| `PART` | 1, 4–7          | Particle board |
| `OSB`  | 2, 3, 4         | Oriented strand board |
| `FIB`  | HB, MHB, MDF, SB | Fibre board |
| `GFK`  | —               | Glass fibre composite |
| `CFK`  | —               | Carbon fibre composite |
| `SFK`  | —               | Synthetic fibre composite |
| `EP`   | —               | Epoxy resin (E=40000/5000) |
| `UP`   | —               | Unsaturated polyester resin |
| `VE`   | —               | Vinyl ester resin |

> Use standard CLASS designations from EN 1995 (e.g. `C24`, `GL24h`) whenever possible — defaults are read from the INI-file. All strength values are characteristic values; safety factor and k_mod are applied at design. Fibre composite materials (`GFK`, `CFK`, `SFK`) require explicit strength values — no INI-file defaults exist.

**Typical usage:**
```
$ Solid timber C24 per EN 1995
TIMB NO 5 TYPE C CLAS 24

$ Glulam GL28h
TIMB NO 6 TYPE GL CLAS 28h

$ C24 service class 2 (colon notation)
TIMB NO 7 TYPE C CLAS 24:2

$ Custom timber, explicit values
TIMB NO 8 TYPE C FM 24 FT0 14 FC0 21 FV 2.5 EP 11000 G 690 GAM 5.0 SCM 1.3
```

---

### SREC — Rectangular, T-Beam, and Plate Section

Defines a solid rectangular cross-section, a T-beam, or a plate slab section. The section type is inferred from the combination of parameters given.

| Parameters given | Section type |
|-----------------|--------------|
| `H` only | Plate (implied width 1 m, or `BO`) |
| `H`, `B` | Rectangular cross-section |
| `H`, `B`, `HO`, `BO` | T-beam cross-section |

**Syntax:**
```
SREC NO H B HO BO SO SU SS MNO MRF MRFL RTYP ASO ASU DASO DASU DASS
     A AMIN AMAX ASL INCL REF YM ZM IT AY AZ BCYZ SPT INTE CINT MUE
     BEFF BDL TITL
```

| Parameter | Type   | Unit     | Default | Description |
|-----------|--------|----------|---------|-------------|
| `NO`      | int    | —        | 1       | Cross-section number |
| `H`       | float  | `[mm]`   | —       | Total height |
| `B`       | float  | `[mm]`   | 1000    | Width (rectangular section or T-beam web width) |
| `HO`      | float  | `[mm]`   | 0       | Thickness of upper flange (T-beam) |
| `BO`      | float  | `[mm]`   | 0       | Effective width of upper flange (T-beam) |
| `SO`      | float  | `[mm]`   | H/10    | Cover offset of top reinforcement |
| `SU`      | float  | `[mm]`   | SO      | Cover offset of bottom reinforcement |
| `SS`      | float  | `[mm]`   | SO      | Cover offset of side reinforcement |
| `MNO`     | int    | —        | `*`     | Material number |
| `MRF`     | int    | —        | `*`     | Material number of reinforcement |
| `MRFL`    | int    | —        | `*`     | Material number of link reinforcement |
| `RTYP`    | enum   | —        | `*`     | Reinforcement distribution subtype (see table below) |
| `ASO`     | float  | `[cm²]`  | 0       | Basic reinforcement area — top. Use unit `[-]` to specify bar count instead of area. |
| `ASU`     | float  | `[cm²]`  | 0       | Basic reinforcement area — bottom |
| `DASO`    | float  | `[mm]`   | `*`     | Diameter of top reinforcement. Defaults to MinBarDiameterC from INI-file (typically 12 mm). |
| `DASU`    | float  | `[mm]`   | DASO    | Diameter of bottom reinforcement |
| `DASS`    | float  | `[mm]`   | DASO    | Diameter of side reinforcement |
| `A`       | float  | `[mm]`   | `*`     | Bar spacing |
| `AMIN`    | float  | `[mm]`   | `*`     | Minimum bar spacing |
| `AMAX`    | float  | `[mm]`   | `*`     | Maximum bar spacing |
| `ASL`     | float  | `[cm²/m]`| `*`     | Area of shear link reinforcement |
| `INCL`    | float  | `[°]`    | 0       | Inclination of shear links (cot or degrees) |
| `REF`     | enum   | —        | `C`     | Location of local coordinate origin (see table below) |
| `YM`      | float  | `[mm]`   | —       | Explicit Y offset relative to mid point |
| `ZM`      | float  | `[mm]`   | —       | Explicit Z offset (mid point = H/2, independent of REF) |
| `IT`      | float  | `[m⁴]`   | `*`     | Torsional moment of inertia (or factor `[-]`) |
| `AY`      | float  | `[m²]`   | `*`     | Shear deformation area for VY (or factor `[-]`) |
| `AZ`      | float  | `[m²]`   | `*`     | Shear deformation area for VZ (or factor `[-]`) |
| `BCYZ`    | enum   | —        | `*`     | Buckling curve selector |
| `SPT`     | enum   | —        | 0       | Number of stress points (0/2/4/6); add 1 for shear in flanges; 8 for torsion plate rebar |
| `INTE`    | enum   | —        | —       | Interface type between web and flange (see table below) |
| `CINT`    | float  | —        | `*`     | Roughness coefficient of interface |
| `MUE`     | float  | —        | `*`     | Friction coefficient of interface |
| `BEFF`    | float  | `[mm]`   | `*`     | Width of equivalent hollow section |
| `BDL`     | float  | `[mm]`   | BO, B   | Total plate width for T-beams — includes full slab dead weight while keeping BO/B for stiffness |
| `TITL`    | string | —        | `*`     | Cross-section designation (up to 32 characters) |

**RTYP — reinforcement distribution subtypes:**

| Value    | Meaning |
|----------|---------|
| `CORN`   | Single bars at corners |
| `CORN:n` | n bars per corner (1 ≤ n ≤ 7) |
| `CORN:nZ`| As `CORN:n`, bars oriented left/right |
| `CORN:nB`| As `CORN:n`, with bar bundles |
| `CU`     | Perimetric (circumferential) reinforcement |
| `SYM`    | Symmetrical top/bottom; intermediate bars added if spacing > MaxBarDistance |
| `SZM`    | Symmetrical left/right |
| `ASYM`   | Asymmetrical: ASU at bottom (layer 1), ASO at top (layer 2), optional side bars (layer 3) |
| `ASZM`   | As `ASYM` but right (layer 1) and left (layer 2) |

Append `:F` to any `RTYP` value to allow layer 3 (side) reinforcement to be varied freely by the design module (e.g. `ASYM:F`).

**REF — coordinate origin location:**

| Value          | Meaning |
|----------------|---------|
| `C`            | Elastic centre — **default** |
| `SC`           | Shear centre |
| `Y+` / `Y-` / `M` | Right / left / middle in beam direction |
| `Y+Z-` / `Y-Z-` / `Z-` | Top right / left / middle |
| `Y+Z+` / `Y-Z+` / `Z+` | Bottom right / left / middle |
| `Y+P` / `Y-P` / `PM`   | Plate right / left / middle |

**INTE — interface types (web–flange connection):**

| Value  | Meaning |
|--------|---------|
| `INDE` | Indented shear joint |
| `ROUG` | Rough shear joint |
| `EVEN` | Even shear joint |
| `SMOO` | Smooth (very even) shear joint |

> When `H` or `B` is given as a negative value, only that dimension will be optimised by AQB. `BDL` is used for T-beams to include the full slab weight in dead load while keeping BO/B for stiffness.

**Typical usage:**
```
$ Plate section 200 mm thick, C30 concrete
SREC NO 1 H 200 MNO 1

$ Rectangular beam 300 × 600 mm, C30 / B500B
SREC NO 2 H 600 B 300 MNO 1 MRF 11 SO 50 SU 50

$ T-beam: web 300×800, flange 150 thick × 1500 wide
SREC NO 3 H 800 B 300 HO 150 BO 1500 MNO 1 MRF 11 SO 55 SU 55

$ Column 400×400 with perimetric reinforcement
SREC NO 4 H 400 B 400 MNO 1 MRF 11 SO 40 RTYP CU

$ Plate with explicit shear reinforcement
SREC NO 5 H 250 MNO 1 MRF 11 SO 35 SU 35 ASL 5.0
```

---

### PROF — Rolled Steel Profile

Defines a cross-section from a standard rolled steel shape table. Can be used standalone (creates a section with number `NO`) or inside a `SECT` block to add a shape to a composite section.

**Syntax:**
```
PROF NO TYPE Z1 Z2 Z3 MNO ALPH YM ZM REFP REFD REFS REFR DTYP SYM REF
     MATI VD VB VS VT VR1 VR2 VB2 VT2 BCYZ
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `NO`      | string | —     | `*`     | Section / shape number (Lit4) |
| `TYPE`    | enum   | —     | `IPE`   | Profile type (see table below) |
| `Z1`      | float  | —     | `*`     | Primary shape identifier — section height for I-beams, height for L-sections |
| `Z2`      | float  | —     | —       | Additional identifier — width for L, HL sections |
| `Z3`      | float  | —     | —       | Additional identifier — thickness for L, special profiles |
| `MNO`     | int    | —     | `*`     | Material number |
| `ALPH`    | float  | `[°]` | 0       | Rotation angle about the section reference point |
| `YM`      | float  | `[mm]`| 0       | Explicit Y-coordinate of reference point |
| `ZM`      | float  | `[mm]`| 0       | Explicit Z-coordinate of reference point |
| `REFP`    | string | —     | —       | Reference point for the total shape (Lit8) |
| `REFD`    | string | —     | —       | Polar direction of reference point (Lit8) |
| `REFS`    | string | —     | —       | Reference initial coordinates for templates (Lit8) |
| `REFR`    | string | —     | —       | Reference point for rotation (Lit4) |
| `DTYP`    | enum   | —     | `S`     | Representation type (see table below) |
| `SYM`     | enum   | —     | —       | Symmetry option for shape duplication (see table below) |
| `REF`     | enum   | —     | `*`     | Location of shape's reference point (see table below) |
| `MATI`    | int    | —     | 0       | Material number of filling for hollow sections |
| `VD`      | float  | —     | —       | Explicit height D |
| `VB`      | float  | —     | —       | Explicit width B |
| `VS`      | float  | —     | —       | Explicit web thickness S |
| `VT`      | float  | —     | —       | Explicit flange thickness T |
| `VR1`     | float  | —     | —       | Explicit root radius R1 |
| `VR2`     | float  | —     | —       | Explicit root radius R2 |
| `VB2`     | float  | —     | —       | Explicit lower width B2 |
| `VT2`     | float  | —     | —       | Explicit lower flange thickness T2 |
| `BCYZ`    | enum   | —     | `*`     | Explicit buckling curve selector |

**TYPE — common European profile types:**

| TYPE | Shape description | Z1 | Z2 | Z3 |
|------|-------------------|----|----|----|
| `HEAA` / `HEA` / `HEB` / `HEM` | HE wide-flange I-section (EN 10635) | size | — | — |
| `HE` | HE section with suffix (e.g. HEB 300, HEA 400) | size | — | suffix |
| `IPE` | IPE parallel-flange I-section (EN 10365) | size | — | — |
| `IPN` | IPN tapered-flange I-section | size | — | — |
| `UPE` / `UPN` | U-channel sections | size | — | — |
| `L`  | Equal/unequal leg angle | height | width | thickness |
| `T`  | T-section | size | — | — |
| `RO` | Circular hollow section (CHS) | diameter | — | thickness |
| `QR` | Rectangular hollow section (RHS) | height | width | thickness |
| `SHS`| Square hollow section | size | — | thickness |
| `HD` | HD column section | size | — | — |
| `HP` | HP pile section | size | — | — |
| `HL` | HL heavy wide-flange | size | width | — |

> `Z1`–`Z3` values are independent of units. Use `VD`–`VT2` for custom geometry. Incomplete input prints the available shape list. Default orientation: y-axis = larger moment of inertia; U-channels open to the right; L-sections standing like the letter "L".

**DTYP — representation type:**

| Value | Meaning |
|-------|---------|
| `S`   | Solid cross-section — **default** |
| `T`   | Thin-walled representation |
| `SP`  | Solid, positive z ordinates only |
| `TP`  | Thin-walled, positive z ordinates only |

**SYM — symmetry duplication:**

| Value  | Meaning |
|--------|---------|
| `o-o`  | Duplicate symmetrically about origin |
| `y-y`  | Duplicate symmetrically about y-axis |
| `z-z`  | Duplicate symmetrically about z-axis |
| `QUAD` | All three symmetry options |
| `YFLP` | Mirror at y-axis only |
| `ZFLP` | Mirror at z-axis only |

**REF — reference point location:**

| Value              | Meaning |
|--------------------|---------|
| `C`                | Elastic centre |
| `SC`               | Shear centre |
| `Y+Z-` / `Y-Z-` / `Z-` | Top right / left / middle |
| `Y+` / `Y-` / `M` | Right / left / middle |
| `Y+Z+` / `Y-Z+` / `Z+` | Bottom right / left / middle |

**Typical usage:**
```
$ IPE 300, S355 steel
PROF NO 20 TYPE IPE Z1 300 MNO 10

$ HEB 200
PROF NO 21 TYPE HEB Z1 200 MNO 10

$ L 150×100×10 angle
PROF NO 22 TYPE L Z1 150 Z2 100 Z3 10 MNO 10

$ CHS 219.1 × 8.0
PROF NO 23 TYPE RO Z1 219.1 Z2 8.0 MNO 10

$ RHS 200 × 100 × 8
PROF NO 24 TYPE QR Z1 200 Z2 100 Z3 8 MNO 10

$ HEB 300, rotated 90°
PROF NO 25 TYPE HEB Z1 300 MNO 10 ALPH 90
```

---

### CIRC — Circular Cross-Section Element

Defines a circular element within a `SECT` polygon section. Used to add solid circles (e.g. rebar, round voids) or holes to a composite section. When `CIRC` overlaps another material region, the overlap area is automatically treated as a hole in that material.

> Must be used within a `SECT` block.

**Syntax:**
```
CIRC NO Y Z R MNO EXP REFP REFD REFS REFR
```

| Parameter | Type   | Unit  | Default     | Description |
|-----------|--------|-------|-------------|-------------|
| `NO`      | string | —     | auto        | Designation of the circular element (Lit4) |
| `Y`       | float  | `[mm]`| 0           | Y-coordinate of the centre point |
| `Z`       | float  | `[mm]`| 0           | Z-coordinate of the centre point |
| `R`       | float  | `[mm]`| —           | Radius of the circle |
| `MNO`     | int    | —     | (from SECT) | Material number — `0` = hole |
| `EXP`     | string | —     | —           | Exposure class literal, or degree of air contact (0.0–1.0) |
| `REFP`    | string | —     | —           | Reference point for centre (Lit8) |
| `REFD`    | string | —     | —           | Reference direction point (Lit8) |
| `REFS`    | string | —     | —           | Reference initial coordinates (Lit8) |
| `REFR`    | string | —     | —           | Reference radius point (Lit8) |

> `MNO 0` defines a circular hole. Internal sequential numbering applies when `NO` is omitted.

**Typical usage:**
```
$ Circular concrete pillar section (R = 300 mm)
SECT NO 30 MNO 1
CIRC Y 0 Z 0 R 300

$ Hollow circular pile: outer R=300, inner hole R=200
SECT NO 31 MNO 1
CIRC Y 0 Z 0 R 300
CIRC Y 0 Z 0 R 200 MNO 0

$ Two steel rebar circles in a concrete section
SECT NO 32 MNO 1
POLY ...             $ outer concrete boundary
CIRC Y 0 Z -250 R 16 MNO 11   $ bottom rebar
CIRC Y 0 Z  250 R 16 MNO 11   $ top rebar
```

---

### CABL — Cable / Rope Cross-Section

Defines a cable or rope cross-section from standard catalogues (EN 12385-4, DIN 3051 etc.) or with explicit factors. The material must be defined as `STEE TYPE YC` (prestressing steel for cables).

**Syntax:**
```
CABL NO D TYPE INL MNO F K W KE REF GAMR TITL
```

| Parameter | Type   | Unit  | Default | Description |
|-----------|--------|-------|---------|-------------|
| `NO`      | int    | —     | 1       | Section number |
| `D`       | float  | `[mm]`| —       | Nominal diameter |
| `TYPE`    | enum   | —     | —       | Cable type designation (see table below). Omit for a plain round bar. |
| `INL`     | enum   | —     | `FE`    | Inlay type (see table below) |
| `MNO`     | int    | —     | 1       | Material number — must reference a `STEE TYPE YC` material |
| `F`       | float  | —     | `*`     | Fill factor, or metallic cross-section area `[mm²]` |
| `K`       | float  | —     | `*`     | Rupture factor, or characteristic breaking load `[kN]` |
| `W`       | float  | —     | `*`     | Weight factor (kg/m/mm² × 100), or weight per metre `[kg/m]` |
| `KE`      | float  | —     | 1.0     | Loss factor (clamping of endpoints etc.) |
| `REF`     | enum   | —     | `*`     | Reference standard for F/K/W factors |
| `GAMR`    | float  | —     | 1       | Partial factor γ_R per EN 1993-1-11 Table 6.2 |
| `TITL`    | string | —     | `*`     | Cross-section designation (up to 32 characters) |

**INL — inlay types:**

| Value | Meaning |
|-------|---------|
| `FE`  | Fibre inlay — **default** |
| `FEN` | Fibre inlay variant N |
| `FEC` | Fibre inlay variant C |
| `SE`  | Steel inlay |
| `SES` | Steel inlay S |
| `SEL` | Steel inlay L |

**REF — reference standard for F/K/W factors:**

| Value | Meaning |
|-------|---------|
| `DIN` | According to DIN 3051 |
| `EN`  | According to EN 12385-4 |

**Standard cable types (selection):**

EN 12385-4 stranded cables: `6x7`, `8x7`, `6x19`, `8x19`, `6x36`, `8x36`, `6x35N`, `6x19M`, `6x37M`, `17x7`, `18x7`, `34x7`, `35x7`

DIN spiral cables (1×n wires): `1x7`, `1x19`, `1x37`, `1x61`, … up to `1x547`

DIN 3051–3071 types: `3052` (1×7), `3053` (1×19), `3054` (1×37), `3055` (6×7), `3056` (8×7), `3057`–`3071` (various stranded)

Locked coil / stay cables: `VVS` (Pfeifer full locked coil) and manufacturer-specific designations.

> F, K, W can be given as absolute values rather than code-derived factors. An incomplete input prints the available cable type list.

**Typical usage:**
```
$ Plain round prestressing bar d=32 mm
STEE NO 13 TYPE YC CLAS 1050
CABL NO 50 D 32 MNO 13

$ EN 12385-4 stranded cable 6×19, d=40 mm
STEE NO 13 TYPE YC
CABL NO 51 D 40 TYPE 6x19 MNO 13 REF EN

$ Locked coil stay cable d=85 mm
CABL NO 52 D 85 TYPE VVS MNO 13 TITL 'Stay cable D85'

$ Cable with explicit breaking load
CABL NO 53 D 55 TYPE 6x36 MNO 13 K 1800   $ K in kN
```

---

## Complete AQUA Block Example

```
+PROG AQUA urs:1
HEAD Bridge deck — materials and sections

!*!Label Design Code
NORM DC DIN NDC EN199X-200X

!*!Label Concrete Materials
CONC NO 1 TYPE C FCN 35 TITL 'C35/45'      $ deck concrete
CONC NO 2 TYPE C FCN 30 TITL 'C30/37'      $ pier concrete

!*!Label Steel Materials
STEE NO 10 TYPE S  CLAS 355    TITL 'S355'     $ structural steel
STEE NO 11 TYPE B  CLAS 500B   TITL 'B500B'    $ reinforcement
STEE NO 12 TYPE YC CLAS 1860   TITL 'Y1860'    $ stay cable steel

!*!Label Cross-Sections
SREC NO 1 H 300  MNO 1 MRF 11 SO 45 SU 45        TITL 'Deck slab'
SREC NO 2 H 1200 B 600 HO 300 BO 2500 MNO 1 MRF 11 SO 60 SU 60 TITL 'Main girder'
SREC NO 3 H 700  B 700 MNO 2 MRF 11 SO 50 RTYP CU TITL 'Column'
PROF NO 20 TYPE IPE Z1 600 MNO 10
CABL NO 50 D 65 TYPE 6x36 MNO 12 REF EN        TITL 'Stay D65'

END
```

---

## Unit Summary for AQUA

| Quantity | Unit | Parameters |
|----------|------|------------|
| Cross-section geometry | `[mm]` | `H`, `B`, `HO`, `BO`, `SO`, `SU`, `D`, `R`, `Y`, `Z`, `Z1`, `Z2`, `Z3` |
| Reinforcement cover | `[mm]` | `SO`, `SU`, `SS`, `DASO`, `DASU`, `DASS` |
| Reinforcement area | `[cm²]` | `ASO`, `ASU`; `[cm²/m]` for `ASL` |
| Material strengths | `[N/mm²]` | `FCN`, `FC`, `FY`, `FT`, `EC`, `ES`, `FM`, `FV`, … |
| Unit weight | `[kN/m³]` | `GAM` on `CONC`, `STEE`, `TIMB` |
| Density | `[kg/m³]` | `RHO` on `CONC`, `TIMB` |
| Elastic modulus | `[N/mm²]` | `EC`, `ES`, `EP`, `E90` |
| Thermal expansion | `[1/K]` | `ALFA` |
| Strain | `[‰]` | `EPSY`, `EPST` |
| Angles | `[°]` | `ALPH`, `OAL`, `OAF`, `INCL` |
| Dimensionless factors | `—` | `MUE`, `SCM`, `SCM0`–`SCM2`, `KMOD`, `KMO1`–`KMO4`, `KDEF` |
