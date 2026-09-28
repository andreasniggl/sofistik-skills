# Module: MAXIMA — Superposition and Envelopes of Load Cases

## Purpose

MAXIMA combines the results of **linearly analysed** load cases into governing envelopes (maximum / minimum values with all corresponding results) according to the combination rules of the selected design code. A combination rule (`COMB`) collects the actions (`ACT` or `ADD`/`ADA`) or load cases (`LC`) that take part; the superposition (`SUPP`) then determines, for every element and every requested result value, the most unfavourable combination and stores it as a result load case in the database. These result load cases are then used by the design modules (AQB, BEMESS, BEAM, COLUMN) and for graphical evaluation. The design code (partial safety factors, combination coefficients) is taken from the database — set by `NORM` in AQUA; the actions must have been defined in SOFILOAD (`ACT`).

## Load this file when

Linear results must be combined **automatically** into envelopes according to a design code (ULS fundamental / accidental / seismic, SLS characteristic / frequent / quasi-permanent), typically between ASE and the design modules (AQB, BEMESS, BEAM, COLUMN). Only use MAXIMA after the user has chosen automatic superposition (question in `SKILL.md`, details in `SUPERPOSITION_STRATEGY.md`).

## Prerequisites

1. **AQUA** — `NORM` (design code, provides safety factors and combination coefficients)
2. **SOFIMSHC** — structural model
3. **SOFILOAD** — actions (`ACT`) and primary load cases assigned to these actions (`LC ... TYPE`)
4. **ASE** — **linear** analysis of all primary load cases

> MAXIMA superposition is only valid for **linear** results. Load cases from non-linear analyses (non-linear material, second-order theory, cable/contact non-linearity) must not be superimposed — for non-linear workflows build the combinations explicitly as load cases in SOFILOAD (`LC ... TYPE (D)` + `COPY`) and analyse them in ASE. The only exception is `COMB ... EXTR NONL`, which **selects** the governing load case among already non-linearly analysed combination load cases (no superposition).

## Module block template

```
+PROG MAXIMA urs:<n>
HEAD <description>

!*!Label Output Control
ECHO FULL NO
ECHO TABS YES

!*!Label Combination Rules
COMB NO 1 EXTR DESI BASE 2100 TITL 'ULS fundamental'
  ACT TYPE G
  ACT TYPE Q

COMB NO 2 EXTR RARE BASE 2200 TITL 'SLS characteristic'
  ACT TYPE G
  ACT TYPE Q

!*!Label Superpositions
SUPP COMB 1 EXTR MAMI ETYP BEAM TYPE N,VZ,MY
SUPP COMB 1 EXTR MAMI ETYP NODE TYPE PZ
SUPP COMB 2 EXTR MAMI ETYP BEAM TYPE MY

END
```

> **Key rules:**
> - The actions used in `ACT` / `ADD` / `ADA` must already exist in the database (SOFILOAD `ACT`). MAXIMA **cannot define new actions**; `ACT` in MAXIMA only selects an action and may modify its factors temporarily for this combination.
> - The `ACT`, `ADD`, `ADA` and `LC` records belonging to a combination rule must follow **directly after** their `COMB` record.
> - Code combinations (`EXTR DESI`, `ACCI`, `EARQ`, `RARE`, `FREQ`, `PERM`, `NONF`) require `ACT` records. `EXTR EXPL` requires `ADD` (+ `ADA`) records — `ACT` is **not allowed** after `COMB ... EXTR EXPL`. `EXTR STAN` / `NONL` require `LC` records.
> - Always give `BASE` (multiple of 100, ≥ 100) in `COMB` — result load case numbers are then generated semi-automatically as `BASE + two-digit suffix` (see *Result Load Case Numbers* in SUPP). Fully automatic numbering is no longer supported.
> - `ECHO` records controlling the output of a superposition must be placed **before** the `SUPP` record. Repeat the record name `ECHO` for every ECHO record.
> - Define `ETYP` and `TYPE` explicitly in every `SUPP` — select only the element types and result values needed by the subsequent design (e.g. `BEAM` N, VZ, MY for AQB; `QUAD` M, VX, VY for BEMESS; `NODE` PZ for support reactions).
> - Combination tracing (`TRAC`) must be done in its **own** MAXIMA run after the superposition.
> - Superposition of **beam deformations** (`SUPP ... ETYP BEAM TYPE UZ`) requires that ASE stored the local beam deformations: add `ECHO BDEF EXTR` in the ASE block. Nodal displacements (`ETYP NODE TYPE UZ`) need no extra ASE option.
> - Several MAXIMA blocks may follow each other (e.g. one per limit state, or a later block that combines result load cases of an earlier block with `COMB ... EXTR STAN`).

---

## Commands

| Command | Purpose |
|---------|---------|
| `CTRL`  | Control of the calculation (INI default combinations, saving, deletion) |
| `ECHO`  | Extent of the output |
| `COMB`  | Combination rule (type of combination, base number, result type) |
| `ACT`   | Selection of an action for a code combination (temporary modification of factors) |
| `LC`    | Selection of load cases for an action or a load case combination |
| `ADD`   | Actions / action groups with factors for an explicit combination (`EXTR EXPL`) |
| `ADA`   | Selection of actions for an action group of `ADD` |
| `SUPP`  | Definition of the superposition (extreme value, element type, result value, result load cases) |
| `SUM`   | Sums of results with manually defined factors (`EXTR STAN` only) |
| `EXPO`  | Export of combination rules from the database |
| `TRAC`  | Combination tracing of a result load case |

---

### CTRL — Method of Calculation

Controls the usage of the default combination rules from the INI-file and the storage of results.

**Syntax:**
```
CTRL OPT VAL
```

| Parameter | Type | Unit | Default | Description |
|-----------|------|------|---------|-------------|
| `OPT`     | enum | —    | —       | Name of the option (see table below) |
| `VAL`     | enum/int | — | `*`    | Value of the option: `YES` / `NO` (or 1 / 0) |

**OPT — options:**

| OPT    | Meaning | Default |
|--------|---------|---------|
| `COMB` | Use the combination rules for the default action combinations from the INI-file of the design code (`YES` / `NO`) | `NO` |
| `SUPP` | Calculate the superpositions for the preset action combinations from the INI-file (`YES` / `NO`) | `NO` |
| `SAVE` | Saving of results: `0` print only; `1` store results in the database | `1` |
| `DELE` | Deletion of load cases: `0` do not delete newly defined load cases; `1` delete newly defined load cases | `1` |

> `CTRL COMB YES` + `CTRL SUPP YES` generates **all** default combinations of the design code (stored as `EXTR EXPL` combination rules, BASE numbers from the INI-file) and their superpositions. Only default actions / categories defined in SOFILOAD are used; user-defined actions are ignored.
> `CTRL COMB YES` + `CTRL SUPP NO` generates the combination rules only; the superpositions can then be defined manually with `SUPP` in a second MAXIMA run.

**Typical usage:**
```
$ All default combinations and superpositions of the design code (own MAXIMA block)
+PROG MAXIMA urs:6
HEAD Default action combinations
CTRL COMB YES          $ generate the default combination rules of the INI-file
CTRL SUPP YES          $ generate the associated default superpositions
ECHO TABS YES
ECHO LC   YES
END
```

> The default combinations only cover the default actions of the design code (e.g. `G`, `Q_B`, `S`). Use an own MAXIMA block for them; explicit `COMB`/`SUPP` input follows in a separate block.

---

### ECHO — Extent of the Output

Controls the printed output. Must be placed before the `SUPP` record it refers to.

**Syntax:**
```
ECHO OPT VAL VAL2
```

| Parameter | Type | Unit | Default | Description |
|-----------|------|------|---------|-------------|
| `OPT`     | enum | —    | —       | Output option (see table below) |
| `VAL`     | enum | —    | `*`     | Value of the output option (see table below) |
| `VAL2`    | enum | —    | `NO`    | Additional value for `ECHO TABS FULL` without superpositions: `NO`, `ACT` (action combination rules), `LC` (load case combination rules STAN/NONL), `FULL` (ACT + LC) |

**OPT — output options:**

| Value  | Meaning | Default |
|--------|---------|---------|
| `NO`   | No printed output | — |
| `TABS` | General tables of the combinations | `YES` |
| `LC`   | General table of the generated load cases | `YES` |
| `CHCK` | Output of the decisive point of the superposition | — |
| `FULL` | Full output | — |
| `LOAD` | Used load cases | — |
| `FACT` | Load case contribution factors | — |
| `SUM`  | Result combinations, determined load case combinations | — |
| `NODE` | Nodal displacements / forces | — |
| `BOUN` | Single values of boundary elements | — |
| `BOUS` | Support sums of boundary elements | — |
| `BEAM` | Beam elements | — |
| `DSLN` | Design elements | — |
| `TRUS` | Truss elements | — |
| `CABL` | Cable elements | — |
| `SPRI` | Spring elements | — |
| `CFM`  | Forces of kinematic constraints | — |
| `QUAD` | Plane elements | — |
| `QNOD` | Plane elements, values in nodes | — |
| `BRIC` | Solid elements | — |
| `BNOD` | Solid elements, values in nodes | — |
| `QBED` | Bedding values | — |
| `BSEC` | Beam element sections | — |
| `RSET` | Result sets | — |
| `SLVL` | Storey results of the seismic design | — |
| `LINK` | Link elements | — |

**VAL — output values:**

| Value  | Meaning |
|--------|---------|
| `NO`   | No printed output |
| `YES`  | Regular output |
| `P`    | Nodes: output of forces or stresses |
| `V`    | Nodes: output of displacements |
| `FULL` | Extensive output (= P + V) |
| `CSAV` | Only with `CHCK`: save the load case factors of each relevant value as combination rule with the number of the result load case (result load cases must be 1–999) |

> `ECHO FACT YES` (1) prints the resulting sums and factors, `2` only non-zero sums/factors, `FULL` (3) all factors in detail.
> For large systems check results only for selected elements (`SUPP ... FROM`) with `ECHO LOAD,FACT` or `ECHO CHCK` — `ECHO FULL FULL` for all elements leads to very long computation times and output files.

**Typical usage:**
```
ECHO FULL NO           $ suppress the result tables
ECHO TABS YES          $ print the combination tables
ECHO LOAD,FACT YES     $ check contributing load cases and factors
```

---

### COMB — Combination Rule

Defines a combination rule for actions or load cases. The corresponding `ACT` / `ADD` / `ADA` / `LC` records follow directly.

**Syntax:**
```
COMB NO EXTR BASE TYPE COMC TITL
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `NO`      | int    | —    | 1       | Number of the combination rule (1–999); preset combinations from the INI-file use NO 100 and following |
| `EXTR`    | enum   | —    | —       | Type of the combination rule (required, see table below) |
| `BASE`    | int    | —    | `*`     | Base load case number for the result load cases — multiple of 100, minimum 100, maximum 999900 |
| `TYPE`    | enum   | —    | `*`     | Assignment (type) of the result load cases (see table below); default depends on EXTR |
| `COMC`    | int    | —    | —       | Copy an existing combination rule into this new one (allows changes of EXTR and BASE) |
| `TITL`    | string | —    | `*`     | Designation of the combination (Lit32) |

**EXTR — combination rules:**

| Value    | Meaning | Default TYPE |
|----------|---------|--------------|
| `DESI`   | ULS design fundamental combination (EN 1990 6.10 / 6.10a,b) | `DESI` |
| `ACCI`   | ULS accidental combination with leading variable action ψ₁,₁·Q_k,1 | `ACCI` |
| `EARQ`   | ULS seismic combination | `EARQ` |
| `RARE`   | SLS characteristic (rare) combination | `RARE` |
| `FREQ`   | SLS frequent combination | `FREQ` |
| `PERM`   | SLS quasi-permanent combination | `PERM` |
| `NONF`   | SLS infrequent combination | `NONF` |
| `EXPL`   | Explicitly defined action combination with `ADD` / `ADA` — TYPE required | — |
| `DESI-V` | Simplified design combination (DIN 18800) | `DESI` |
| `ACCI-V` | Simplified accidental combination (DIN 18800, ÖNORM 4300) | `ACCI` |
| `RARE-V` | Simplified characteristic combination | `RARE` |
| `STAN`   | Standard load case combination with `LC` only (no actions, no partial safety factors), or combination of already combined load cases | — |
| `NONL`   | Selection of the governing load case among non-linearly analysed load cases (`LC` only, treated as TYPE AG1) — TYPE required | — |

**TYPE — assignment of the result load cases:**

| Value | Meaning | Load case type in design modules |
|-------|---------|-----------------------------------|
| `DESI` | ULS design combination | `(D)` |
| `ACCI` | ULS accidental combination | `(A)` |
| `EARQ` | ULS seismic combination | `(E)` |
| `RARE` | SLS characteristic combination | `(R)` |
| `FREQ` | SLS frequent combination | `(F)` |
| `NONF` | SLS infrequent combination | `(N)` |
| `PERM` | SLS quasi-permanent combination | `(P)` |
| `STAN` | Standard combination | — |
| `PT` / `LT` / `MT` / `ST` / `VT` | Timber (EN 1995): permanent / long / medium / short / very short term | `(PT)` … `(VT)` |
| `FIRE` | Accidental combination fire | — |
| `H` / `HZ` | Old codes: principal / principal + additional loads | `(H)` / `(HZ)` |
| `NONE` | Result load cases are not assigned to any type | — |
| *action* | Type of an existing action or category (defined in SOFILOAD `ACT`) — for further superposition | — |

> MAXIMA takes the design code from the database (AQUA `NORM`). Which EXTR literals are allowed depends on the INI-file of the design code.
> With `EXTR EXPL` and `EXTR NONL` the TYPE of the result load cases **must** be given explicitly.
> The result load case type decides how the design modules use the results (e.g. AQB `LC TYPE (D)`, `DESI STAT ULTI`; SLS checks with `(R)`, `(F)`, `(P)`).

**Typical usage:**
```
COMB NO 1 EXTR DESI BASE 2100 TITL 'ULS fundamental'
COMB NO 2 EXTR RARE BASE 2200 TITL 'SLS characteristic'
COMB NO 3 EXTR FREQ BASE 2300 TITL 'SLS frequent'
COMB NO 4 EXTR PERM BASE 2400 TITL 'SLS quasi-permanent'
COMB NO 5 EXTR STAN BASE 2500 TYPE DESI TITL 'Standard combination'

$ Timber EN 1995: ULS combinations with assigned load duration (k_mod in AQB)
COMB NO 11 EXTR DESI TYPE PT BASE 3100 TITL 'ULS permanent'
COMB NO 12 EXTR DESI TYPE LT BASE 3200 TITL 'ULS long term'
COMB NO 13 EXTR DESI TYPE MT BASE 3300 TITL 'ULS medium term'

$ Accidental combination (e.g. fire) -> AQB LC TYPE (A)
COMB NO 31 EXTR ACCI TYPE ACCI BASE 3900 TITL 'ULS fire'
```

> The load duration class (TYPE PT/LT/MT/ST/VT) is chosen by the user from the actions included in the combination, e.g. only G → `PT`; G + storage load → `LT`; G + office load → `MT`.

---

### ACT — Selection of an Action

Selects an action (defined in SOFILOAD) for the current code combination and optionally modifies its factors **temporarily for this combination only**.

**Syntax:**
```
ACT TYPE GAMU GAMF PSI0 PSI1 PSI2 PS1S GAMA PART SUP TITL
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `TYPE`    | string | —    | —       | Designation of the action or of its category (Lit4, e.g. `G`, `Q`, `Q_B`) — required |
| `GAMU`    | float  | `[-]`| `*`     | Unfavourable partial safety factor γ_u |
| `GAMF`    | float  | `[-]`| `*`     | Favourable partial safety factor γ_f |
| `PSI0`    | float  | `[-]`| `*`     | Combination coefficient rare ψ₀ |
| `PSI1`    | float  | `[-]`| `*`     | Combination coefficient frequent ψ₁ |
| `PSI2`    | float  | `[-]`| `*`     | Combination coefficient quasi-permanent ψ₂ |
| `PS1S`    | float  | `[-]`| `*`     | Combination coefficient infrequent ψ₁,infq |
| `GAMA`    | float  | `[-]`| `*`     | Partial safety factor accidental γ_a |
| `PART`    | enum   | —    | `*`     | Partition of the action group: `G` permanent, `P` prestress and creep, `Q` variable, `Q_1`…`Q_99` variable load groups, `A` accidental, `E` seismic |
| `SUP`     | enum   | —    | `*`     | Handling of load cases within the action: `PERM`, `PERC`, `COND`, `EXCL`, `EXEX`, `UNSI`, `USEX`, `ALEX` |
| `TITL`    | string | —    | `*`     | Designation of action (Lit24) |

> ACT is only allowed with code combinations (`EXTR DESI`, `ACCI`, `EARQ`, `RARE`, `FREQ`, `PERM`, `NONF`, `…-V`) — not with `EXTR EXPL` (use `ADD`).
> If only one of PART / SUP is modified, the other is reset to its default.
> Selecting the generic action name (e.g. `Q`) also selects all its categories (`Q_A`, `Q_B`, …). Do not additionally select the categories — they would be considered twice.
> Without following `LC` records, all load cases of the action are used (default `LC 0` / `LC -1`, see LC).

**Typical usage:**
```
COMB NO 1 EXTR DESI BASE 2100
  ACT TYPE G
  ACT TYPE Q
  ACT TYPE W
  ACT TYPE S
```

---

### LC — Selection of Load Cases

Assigns load cases to the preceding action (`ACT` / `ADD`) or — for `EXTR STAN` / `NONL` — directly to the combination.

**Syntax:**
```
LC NO TYPE FACT
```

| Parameter | Type      | Unit | Default | Description |
|-----------|-----------|------|---------|-------------|
| `NO`      | int       | —    | `*`     | Load case number; `0` = all load cases of the action incl. categories; `-1` = all load cases of the category |
| `TYPE`    | enum      | —    | `*`     | Type of the load case within the combination (see table below); default derived from `SUP` of the action |
| `FACT`    | float/enum| `[-]`| 1.0     | Factor applied to the results of the load case before superposition, or a factor literal (see ADD) |

**TYPE — load case type:**

| Value | Meaning |
|-------|---------|
| `PERM` or `G` | Always (permanent); partial safety factor action-wise |
| `PERC` | Always (permanent) with variable factors; partial safety factor load-case-wise |
| `COND` or `Q` | Conditional, only if unfavourable |
| `UNSI` or `W` | Alternating load case used positive or negative, whichever is unfavourable (e.g. seismic) |
| `ALEX` / `AG1`…`AG99` | Permanent alternative load case group — always exactly one load case of the group (exclusive within one action) |
| `EXCL` / `A1`…`A99` | Alternative load case group — the most unfavourable one, only if unfavourable |
| `USEX` / `X1`…`X99` | Alternative load case group with changing sign |
| `F` | Follow-up load case — added to the previous main load case only if the main load case is used |

> Default TYPE from SUP of the action: PERM → G, COND → Q, EXCL → A1, UNSI → W, USEX → X1, ALEX → AG1, PERC → PERC. For `EXTR STAN` the default is G for the first load case and Q for all others. Prefer the defaults from the action definition.
> A negative FACT (e.g. -1.0) reverses the sign of the results before superposition.
> Non-linear load cases may only be used with TYPE AG1 (automatically with `COMB ... EXTR NONL`).
> After an action group in `ADD` (e.g. `{QI}`) no LC record is allowed.

**Typical usage:**
```
$ Code combination: load cases of the actions
COMB NO 1 EXTR DESI BASE 2100
  ACT TYPE G
    LC 1
  ACT TYPE Q
    LC 2,3,4

$ Wind: alternative directions, only the most unfavourable one
  ACT TYPE W
    LC 11 TYPE A1
    LC 12 TYPE A1

$ Standard combination with explicit factors (no actions)
COMB NO 5 EXTR STAN BASE 2500 TYPE DESI
  LC 1 TYPE PERM FACT 1.35
  LC 2 TYPE COND FACT 1.50

$ All load cases of action G, and all load cases of category Q_E only
COMB NO 12 EXTR DESI TYPE LT BASE 3200
  ACT TYPE G
    LC 0
  ACT TYPE Q_E
    LC -1

$ Factor from a CADINP variable (e.g. creep deformation k_def)
STO#KDEF 0.6
COMB NO 22 EXTR PERM BASE 4200
  ACT TYPE G
    LC 0 FACT #KDEF
  ACT TYPE Q
    LC 0 FACT #KDEF

$ Later MAXIMA block: combine result load cases of earlier superpositions
$ (max/min UZ of RARE 4175/4176 + max/min UZ of creep part 4275/4276)
COMB NO 23 EXTR STAN BASE 4300
  LC 4175,4176 TYPE A1        $ exactly one of each group is used (if unfavourable)
  LC 4275,4276 TYPE A2
SUPP COMB 23 EXTR MAMI ETYP BEAM TYPE UZ      $ results 4375/4376
```

> Result load cases (max and min of the same value) are combined as alternative groups (`A1`, `A2`, …) so that only one of each pair enters the new superposition.

---

### ADD — Actions for an Explicitly Defined Combination

Defines the actions or action groups and their factors for `COMB ... EXTR EXPL`.

**Syntax:**
```
ADD TYPE FACU FACF
```

| Parameter | Type      | Unit | Default | Description |
|-----------|-----------|------|---------|-------------|
| `TYPE`    | string    | —    | —       | Designation of an action / category, or an action group: `{G}` permanent, `{P}` prestress and creep, `{Q1}` / `{Q2}` / `{Q3}` first / second / third leading variable action, `{QI}` other (remaining) variable actions, `{A}` accidental, `{E}` seismic — required |
| `FACU`    | float/enum| `[-]`| —       | Unfavourable factor, factor literal, or formula `'=factor*literal'` — required |
| `FACF`    | float/enum| `[-]`| —       | Favourable factor, factor literal, or formula — required unless FACU is a collective literal |

**Factor literals:**

| Literal | Factor | Usage |
|---------|--------|-------|
| `GAM` / `GAMM` | γ_u or γ_f | FACU only (collective) |
| `PSIG` | γ_u·ψ₀ or γ_f·ψ₀ | FACU only (collective) |
| `PS1G` | γ_u·ψ₁ or γ_f·ψ₁ | FACU only (collective) |
| `PS2G` | γ_u·ψ₂ or γ_f·ψ₂ | FACU only (collective) |
| `P1SG` | γ_u·ψ₁,infq or γ_f·ψ₁,infq | FACU only (collective) |
| `KFG`, `KFG0`, `KFG1`, `KFG2`, `KFGS` | K_Fi·γ_u, K_Fi·ψ₀·γ_u, K_Fi·ψ₁·γ_u, K_Fi·ψ₂·γ_u, K_Fi·ψ₁,infq·γ_u | FACU (γ_f used for FACF automatically) |
| `XSIG`, `XKFG` | ξ·γ_u, ξ·K_Fi·γ_u | FACU (γ_f used for FACF automatically) |
| `GAMU`, `GAMF`, `GAMA` | γ_u, γ_f, γ_a | FACU and FACF |
| `PSI0`, `PSI1`, `PSI2`, `PS1S` | ψ₀, ψ₁, ψ₂, ψ₁,infq | FACU and FACF |
| `PSIU`, `PSIF`, `PS1U`, `PS1F`, `PS2U`, `PS2F`, `P1SU`, `P1SF` | γ_u·ψ₀, γ_f·ψ₀, γ_u·ψ₁, γ_f·ψ₁, γ_u·ψ₂, γ_f·ψ₂, γ_u·ψ₁,infq, γ_f·ψ₁,infq | FACU and FACF |
| `PSIA`, `PS1A`, `PS2A`, `PSSA` | γ_a·ψ₀, γ_a·ψ₁, γ_a·ψ₂, γ_a·ψ₁,infq | FACU and FACF |
| `KFI`, `XSI`, `XKFI` | K_Fi (EN 1990 Tab. B.3), ξ (EN 1990 6.10b), ξ·K_Fi | FACU and FACF |
| `XSIU`, `XSIF`, `XKGU`, `XSIA`, `XKGA` | ξ·γ_u, ξ·γ_f, ξ·K_Fi·γ_u, ξ·γ_a, ξ·K_Fi·γ_a | FACU and FACF |
| `RHO`, `RHOU`, `RHOF` | ρ (EN 1990:2023 eq. 8.8), ρ·γ_u, ρ·γ_f | FACU and FACF |

> ADD is only allowed with `COMB ... EXTR EXPL`. The assignment of an action to an action group is controlled by PART of the action (SOFILOAD `ACT`).
> If a numerical value or a non-collective literal is given for FACU, FACF **must** also be given (also if 0.0).
> A specific action may be defined as leading action explicitly, the remaining ones via action groups.
> Formulas are allowed only as `'=UserFactor*Literal'` with UserFactor between 0.0 and 10.0.

**Typical usage:**
```
$ EN 1990 eq. 6.10 as explicit combination
COMB NO 1 EXTR EXPL TYPE DESI BASE 2100 TITL 'ULS 6.10'
  ADD {G}  FACU GAMU FACF GAMF
  ADD {Q1} FACU GAMU FACF 0.0
  ADD {QI} FACU PSIU FACF 0.0

$ Wind as leading action
COMB NO 2 EXTR EXPL TYPE DESI BASE 2200 TITL 'ULS wind leading'
  ADD {G}  FACU GAMU FACF GAMF
  ADD W    FACU GAMU FACF 0.0
  ADD {QI} FACU PSIU FACF 0.0

$ SLS quasi-permanent as explicit combination (single action G + all variable actions)
COMB NO 3 EXTR EXPL BASE 3100 TYPE PERM TITL 'SLS PERM'
  ADD TYPE G    FACU 1.0  FACF 1.0      $ permanent action G
  ADD TYPE {QI} FACU PSI2 FACF 0        $ all variable actions with psi2
```

> The keyword form `ADD TYPE G …` and the positional form `ADD G …` are equivalent.

---

### ADA — Selection of Actions for an Action Group

Restricts the action group of the preceding `ADD` record to the listed actions. Without ADA all actions of the group available in the database are used.

**Syntax:**
```
ADA TYPE
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `TYPE`    | string | —    | —       | Designation of the action from the selected action group (Lit4) — required |

> ADA may only follow an `ADD` record with an action group (`{G}`, `{Q1}`, `{QI}`, …) within `COMB ... EXTR EXPL`.

**Typical usage:**
```
COMB NO 1 EXTR EXPL TYPE DESI BASE 2100
  ADD {G}  FACU GAMU FACF GAMF
    ADA G
  ADD {Q1} FACU GAMU FACF 0.0
    ADA Q,S,W
  ADD {QI} FACU PSIU FACF 0.0
    ADA Q,S,W
```

---

### SUPP — Definition of the Superposition

Performs the superposition for a combination rule and stores the extreme values (with all corresponding results) as result load cases.

**Syntax:**
```
SUPP COMB EXTR ETYP TYPE FROM TO INC X SELE LC TITL OPT
```

| Parameter | Type      | Unit     | Default | Description |
|-----------|-----------|----------|---------|-------------|
| `COMB`    | int       | —        | 1       | Number of the combination rule |
| `EXTR`    | enum      | —        | `MAMI`  | Extreme value condition: `MAX`, `MIN`, `MAMI` (max and min), `SRSS` (square root of sum of squares, `STAN` only), `SRSE` (SRSS maintaining the sign) |
| `ETYP`    | enum      | —        | `AUTO`  | Element type (see table below) |
| `TYPE`    | enum/string | —      | `AUTO`  | Superposition value (see tables below), a comma-separated list, or an objective function in quotes (e.g. `'SQR(VX**2+VY**2)'`) |
| `FROM`    | int/enum  | —        | `*`     | Start number, or `GRP` (group), `SLN` (for BEAM, TRUS, CABL, BOUN), `SAR` (for QUAD), result set ID for RSET |
| `TO`      | int/string| —        | `*`     | End number, or group number / name, SLN number, SAR number |
| `INC`     | int       | —        | `*`     | Increment for element selection |
| `X`       | float     | `[m]`    | —       | X value on the beam / design element axis for a specific section (`[m]`, or relative with `[-]`, `[o/o]`, `[o/oo]`) |
| `SELE`    | int/string| —        | —       | Group number for QNOD / BNOD, or cross-section point for BEAM / DSLN (e.g. `Z+`, `Y+Z+`) |
| `LC`      | int       | —        | `*`     | First result load case number (only without BASE, LC ≥ 100) |
| `TITL`    | string    | —        | `*`     | Designation of the superposition load cases (max. 18 characters used) |
| `OPT`     | enum      | —        | —       | `S` = selective superposition only of the elements defined at FROM TO INC |

**ETYP — element types:**

| Value  | Meaning |
|--------|---------|
| `AUTO` | All element types available in the system |
| `NODE` | Nodes (support reactions, displacements) |
| `SPAC` | Nodal velocities / accelerations (`STAN` / `NONL` only) |
| `BOUN` | Boundary elements |
| `BOUS` | Sums of boundary elements |
| `BEAM` | Beams |
| `DSLN` | Design elements (DECREATOR) |
| `BSCT` | External beam sections (SIR) |
| `TRUS` | Trusses |
| `CABL` | Cables |
| `SPRI` | Springs |
| `CFM`  | Kinematic constraints |
| `QUAD` | Plane elements (shells, slabs, walls) |
| `QNOD` | Nodes of plane elements |
| `QBED` | Bedding of plane elements |
| `BRIC` | Volume elements |
| `BNOD` | Nodes of volume elements |
| `RSET` | Result sets |
| `SLVL` | Storey results (seismic) |
| `LINK` | Link elements |

**TYPE and default result load case suffix (max / min) — ETYP BEAM, DSLN, BSCT:**

| TYPE | Meaning | Suffix max/min |
|------|---------|----------------|
| `N`   | Normal force | 21 / 22 |
| `VY`  | Shear force V_y | 23 / 24 |
| `VZ`  | Shear force V_z | 25 / 26 |
| `MT`  | Torsional moment | 27 / 28 |
| `MY`  | Bending moment M_y | 29 / 30 |
| `MZ`  | Bending moment M_z | 31 / 32 |
| `MB`  | Warping moment | 33 / 34 |
| `MT2` | Secondary torsional moment | 35 / 36 |
| `UX` / `UY` / `UZ` | Displacements | 71/72, 73/74, 75/76 |
| `URX` / `URY` / `URZ` | Rotations | 77/78, 79/80, 81/82 |
| `URB` | Rotation due to warping | 93 / 94 |
| `SIG` / `TAU` | Normal / shear stress in cross-section point `SELE` (BEAM, DSLN) | 11/12, 15/16 |
| `PA` / `PTY` / `PTZ` | Pile bedding (BEAM only) | 37/38, 95/96, 97/98 |

**ETYP NODE:**

| TYPE | Meaning | Suffix max/min |
|------|---------|----------------|
| `PX` / `PY` / `PZ` | Support reactions | 51/52, 53/54, 55/56 |
| `P`  | All support reactions (PX … MZ) | — |
| `MX` / `MY` / `MZ` | Support moments | 57/58, 59/60, 61/62 |
| `MB` | Support warping moment | 91 / 92 |
| `UX` / `UY` / `UZ` | Nodal displacements | 71/72, 73/74, 75/76 |
| `URX` / `URY` / `URZ` | Nodal rotations | 77/78, 79/80, 81/82 |
| `URB` | Nodal rotation due to warping | 83 / 84 |

**ETYP QUAD / QNOD:**

| TYPE | Meaning | Suffix max/min |
|------|---------|----------------|
| `MXX` / `MYY` / `MXY` | Bending moments m_xx, m_yy, torsional moment m_xy | 01/02, 03/04, 05/06 |
| `M`  | All bending moments | — |
| `VX` / `VY` | Shear forces v_x, v_y | 07/08, 09/10 |
| `NXX` / `NYY` / `NXY` | Membrane forces (shells) | 11/12, 13/14, 15/16 |
| `N`  | All membrane forces | — |
| `SX` / `SY` / `SXY` / `SZ` | Stresses in disks (2D) | 11/12, 13/14, 15/16, 17/18 |
| `SXT`, `SYT`, `SXYT` / `SXB`, `SYB`, `SXYB` | Shell stresses top / bottom | 71/72 … 81/82 |
| `S`  | All stresses | — |
| `SIGT` | Stress increment (prestress, QUAD only) | — |

**Other element types:**

| ETYP | TYPE (suffix max/min) |
|------|------------------------|
| `BOUN` | `PX` 63/64, `PY` 65/66, `PZ` 67/68, `P`, `M` 69/70 |
| `BOUS` | `PX` 83/84, `PY` 85/86, `PZ` 87/88, `P`, `M` 89/90 |
| `TRUS` | `N` 41/42 |
| `CABL` | `N` 43/44 |
| `SPRI` | `P` 45/46, `PTX` 93/94, `PTY` 95/96, `PTZ` 97/98, `M` 47/48, `U` 49/50, `UTX` 73/74, `UTY` 75/76, `UTZ` 77/78, `UR` 51/52 |
| `CFM`  | `PX` 51/52, `PY` 53/54, `PZ` 55/56, `P`, `MX` 57/58, `MY` 59/60, `MZ` 61/62, `MB` 91/92 |
| `QBED` | `P` 17/18, `PTX` 93/94, `PTY` 95/96, `PTZ` 97/98 |
| `BRIC` / `BNOD` | `SX` 11/12, `SY` 13/14, `SXY` 15/16, `SZ` 17/18, `SYZ` 07/08, `SXZ` 09/10, `S` |
| `SPAC` | `VX` 51/52, `VY` 53/54, `VZ` 55/56, `AX` 57/58, `AY` 59/60, `AZ` 61/62 |
| `SLVL` | `PX` 51/52, `PY` 53/54, `PZ` 55/56, `MX` 59/60, `MY` 61/62, `MZ` 63/64, `UX` 71/72, `UY` 73/74, `UZ` 75/76, `RZ` 79/80, `DX` 81/82, `DY` 83/84, `DR` 87/88 |
| `LINK` | `PX` 51/52, `PY` 53/54, `PZ` 55/56, `MX` 57/58, `MY` 59/60, `MZ` 61/62, `UX` 71/72, `UY` 73/74, `UZ` 75/76, `URX` 77/78, `URY` 79/80, `URZ` 81/82 |

**Result load case numbers:**

| Input | Result load case number |
|-------|-------------------------|
| `BASE` in COMB (≥ 100), no `LC` in SUPP — **semi-automatic (recommended)** | `BASE + suffix` (e.g. BASE 2100, BEAM MY max → **2129**, min → **2130**) |
| No `BASE` (or 0) in COMB, `LC` ≥ 100 in SUPP — manual | `LC` for the first result, following results numbered continuously; one LC per TYPE may be given as comma list (e.g. `TYPE N,VZ,MY LC 121,131,141`) |

> Result load case numbers should be ≥ 100 and must not coincide with primary load cases. Several `SUPP` records may generate the same result load case numbers only if they use the same combination rule.
> For QUAD and QNOD superpositions the same TYPE values (and the same result load cases, if defined manually) must be used.
> Superposition with SIG / TAU at cross-section points: SELE may be an AQUA stress point or `Y+`, `Y-`, `Z+`, `Z-`, `Y+Z+`, `Y-Z+`, `Y-Z-`, `Y+Z-` (corners / edge centres of the enclosing rectangle).
> An objective function combines several superposition values of **one** element type; the result load case number must then be given manually, and the result must be checked by the user (`ECHO LOAD,FACT`).
> For RSET the result set ID is given at FROM and the single set IDs at TYPE; with BASE the result sets are numbered from BASE+1.

**Typical usage:**
```
$ Beam envelopes for AQB (N, VZ, MY): 2121/2122, 2125/2126, 2129/2130
SUPP COMB 1 EXTR MAMI ETYP BEAM TYPE N,VZ,MY

$ Slab envelopes for BEMESS
SUPP COMB 1 EXTR MAMI ETYP QUAD TYPE M,VX,VY
SUPP COMB 1 EXTR MAMI ETYP QNOD TYPE M,VX,VY

$ Support reactions
SUPP COMB 1 EXTR MAMI ETYP NODE TYPE PZ

$ Beam stresses at the bottom and top edge
SUPP COMB 2 EXTR MAMI ETYP BEAM TYPE SIG SELE Z+,Z-

$ Objective function: resultant shear force of plates (manual LC number)
SUPP COMB 1 EXTR MAMI ETYP QUAD TYPE 'SQR(VX**2+VY**2)' LC 101

$ Output control per superposition: ECHO before each SUPP it applies to
ECHO LOAD,FACT NO
SUPP COMB 1 EXTR MAMI ETYP BEAM TYPE VZ,MY TITL 'Forces and moments'
ECHO LOAD,FACT                                          $ detailed check printout on
SUPP COMB 2 EXTR MAMI ETYP BEAM TYPE VZ,MY FROM 10010 X 1[-] TITL 'Forces and moments'
ECHO LOAD,FACT NO

$ Stress at edge point, printout and superposition only for the end of beam 10005
SUPP COMB 2 EXTR MAMI ETYP BEAM TYPE SIG SELE Z+ FROM 10005 X 1[-] OPT S
```

> `FROM`/`X` without `OPT S` only restrict the **printout** (all elements are still superposed); with `OPT S` only the selected elements are superposed.
> Beam element numbers generated by SOFIMSHC follow `group number × GDIV + running number` (e.g. `SYST ... GDIV 10000`, two 10 m spans in `GRP 1` meshed with 1 m elements: beams 10001–10020, end of span 1 = beam 10010 at `X 1[-]`) — use these numbers at `FROM` / `TRAC ELEM`. Alternatively select by structural line: `FROM SLN TO 1`.

---

### SUM — Definition of Sums for Results

Determines sums of results of individual load cases with manually defined factors (all load cases are always added, even if favourable).

**Syntax:**
```
SUM COMB LC TITL
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `COMB`    | int    | —    | 1       | Number of the combination rule |
| `LC`      | int    | —    | —       | Load case number for the results (required) |
| `TITL`    | string | —    | —       | Designation of the superposition load case (Lit32, 28 characters used) |

> SUM is only allowed with `COMB ... EXTR STAN` whose load cases are all TYPE PERM. `BASE` is not allowed for that combination. A combination can use either `SUPP` or `SUM`, not both. The combination rule is deleted after the calculation (no `TRAC` possible).

**Typical usage:**
```
COMB NO 7 EXTR STAN TYPE DESI
  LC 1 TYPE PERM FACT 1.35
  LC 2 TYPE PERM FACT 1.50
SUM COMB 7 LC 701 TITL 'ULS 1.35G+1.5Q'
```

---

### EXPO — Export of Combination Rules

Exports the combination rules of the database or INI-file to a MAXIMA input file.

**Syntax:**
```
EXPO OPT TO PASS
```

| Parameter | Type   | Unit | Default | Description |
|-----------|--------|------|---------|-------------|
| `OPT`     | int    | —    | 63      | Data to export |
| `TO`      | string | —    | `*`     | Name of the file to write to (Lit96); default `project_MAX.DAT` |
| `PASS`    | string | —    | —       | Password of the database (Lit16) |

---

### TRAC — Combination Tracing

Traces a result load case and prints all contributing input load cases with their factors for a specific element. Optionally saves them as a new combination rule (for SOFILOAD `COPY ... COMB`).

**Syntax:**
```
TRAC LC ETYP ELEM X SELE OPT CSAV
```

| Parameter | Type      | Unit     | Default | Description |
|-----------|-----------|----------|---------|-------------|
| `LC`      | int       | —        | —       | Result load case number of a previous MAXIMA run (required) |
| `ETYP`    | enum      | —        | —       | Element type (same values as SUPP ETYP, without AUTO) — required |
| `ELEM`    | int/string| —        | —       | Element / node number or result set ID — required |
| `X`       | float     | `[m]`/`[-]` | —    | X value on the beam / design element axis (required for BEAM) |
| `SELE`    | int/string| —        | —       | Cross-section point (BEAM/DSLN), group number (QNOD/BNOD) or node number (BOUN) |
| `OPT`     | string    | —        | `IEF`   | Tracing options: `I` trace intermediate superpositions, `E` do not resolve envelopes of pre-superpositions, `F` filter out non-contributing load cases |
| `CSAV`    | int       | —        | —       | Save the determined load cases and factors as new combination number (1–999) |

> TRAC must be used in an **individual MAXIMA run** — it cannot coexist with COMB / SUPP input.
> A combination saved with CSAV can be turned into a real load case in SOFILOAD with `LC nnn TYPE NONE` + `COPY <CSAV> COMB`, and analysed in ASE (e.g. non-linear re-analysis of the governing combination).

**Typical usage:**
```
+PROG MAXIMA urs:8
HEAD Tracing of the governing ULS combination
TRAC LC 2129 ETYP BEAM ELEM 1003 X 1[-] OPT 'IF'
TRAC LC 2155 ETYP NODE ELEM 12 OPT 'IF' CSAV 55
END
```

---

## Complete MAXIMA Block Example

Continuous RC beam (SOFIMSHC structural line, beam elements), actions G and Q defined in SOFILOAD, all primary load cases analysed linearly in ASE. The envelopes are used by AQB (see `AQB.md`, Example 2).

```
+PROG MAXIMA urs:5
HEAD Superposition ULS and SLS envelopes

!*!Label Output Control
ECHO FULL NO
ECHO TABS YES

!*!Label ULS Fundamental Combination (results 21xx)
COMB NO 1 EXTR DESI BASE 2100 TITL 'ULS fundamental'
  ACT TYPE G
  ACT TYPE Q

!*!Label SLS Characteristic Combination (results 22xx)
COMB NO 2 EXTR RARE BASE 2200 TITL 'SLS characteristic'
  ACT TYPE G
  ACT TYPE Q

!*!Label SLS Frequent Combination (results 23xx)
COMB NO 3 EXTR FREQ BASE 2300 TITL 'SLS frequent'
  ACT TYPE G
  ACT TYPE Q

!*!Label SLS Quasi-Permanent Combination (results 24xx)
COMB NO 4 EXTR PERM BASE 2400 TITL 'SLS quasi-permanent'
  ACT TYPE G
  ACT TYPE Q

!*!Label ULS Superpositions: beam forces and support reactions
SUPP COMB 1 EXTR MAMI ETYP BEAM TYPE N,VZ,MY     $ 2121/2122, 2125/2126, 2129/2130
SUPP COMB 1 EXTR MAMI ETYP NODE TYPE PZ          $ 2155/2156

!*!Label SLS Superpositions: bending moments and deflections
SUPP COMB 2 EXTR MAMI ETYP BEAM TYPE MY          $ 2229/2230
SUPP COMB 3 EXTR MAMI ETYP BEAM TYPE MY          $ 2329/2330
SUPP COMB 4 EXTR MAMI ETYP BEAM TYPE MY,UZ       $ 2429/2430, 2475/2476 (UZ needs ASE ECHO BDEF EXTR)

END
```

### Example 2 — Explicit combination rules (EXTR EXPL)

Two-span RC girder (SOFIMSHC `GDIV 10000`, beams 10001–10020 in GRP 1); actions `G`, `Q_B`, `S` defined in SOFILOAD.

```
+PROG MAXIMA urs:6
HEAD Explicit action combinations and superpositions

!*!Label SLS quasi-permanent (results 31xx)
COMB NO 1 EXTR EXPL BASE 3100 TYPE PERM TITL 'SLS PERM'
  ADD TYPE G    FACU 1.0  FACF 1.0              $ permanent action G
  ADD TYPE {QI} FACU PSI2 FACF 0                $ all variable actions

!*!Label ULS fundamental combination (results 41xx)
COMB NO 2 EXTR EXPL BASE 4100 TYPE DESI TITL 'ULS fundamental'
  ADD TYPE G    FACU GAMU FACF GAMF             $ permanent action G
  ADD TYPE {Q1} FACU GAMU FACF 0                $ leading variable action
    ADA Q_B,S
  ADD TYPE {QI} FACU PSIU FACF 0                $ accompanying variable actions
    ADA Q_B,S

!*!Label Superpositions
ECHO LOAD,FACT NO
SUPP COMB 1 EXTR MAMI ETYP BEAM TYPE VZ,MY TITL 'Forces and moments'   $ 3125/3126, 3129/3130
SUPP COMB 1 EXTR MAMI ETYP NODE TYPE UZ    TITL 'Displacements'        $ 3175/3176
SUPP COMB 2 EXTR MAMI ETYP BEAM TYPE VZ,MY TITL 'Forces and moments'   $ 4125/4126, 4129/4130
SUPP COMB 2 EXTR MAMI ETYP NODE TYPE PZ    TITL 'Support reactions'    $ 4155/4156

!*!Label Edge stresses at the inner support (end of beam 10010)
ECHO LOAD,FACT
SUPP COMB 2 EXTR MAMI ETYP BEAM TYPE SIG SELE Z- FROM 10010 X 1[-] OPT S

END
```

---

## Unit Summary for MAXIMA

| Quantity | Unit | Parameters |
|----------|------|------------|
| Position along beam / design element | `[m]` or relative `[-]`, `[o/o]`, `[o/oo]` | SUPP `X`, TRAC `X` |
| Partial safety factors | `[-]` | ACT `GAMU`, `GAMF`, `GAMA` |
| Combination coefficients | `[-]` | ACT `PSI0`, `PSI1`, `PSI2`, `PS1S` |
| Load case factors | `[-]` | LC `FACT`, ADD `FACU`, `FACF` |
| Numbers / identifiers | — | COMB `NO`, `BASE`; SUPP `LC`, `FROM`, `TO`, `INC`; SUM `LC`; TRAC `LC`, `ELEM`, `CSAV` |
