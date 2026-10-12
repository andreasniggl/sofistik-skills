# CADINP Language Rules

This file defines the syntax rules for the SOFiSTiK CADINP input language. These rules apply globally to every module and must be followed in all generated *.dat files.

---

## 1. File and Module Structure

### 1.1 Program Blocks
Every analysis task is organised into program (`PROG`) blocks. Each block begins with a `+PROG` declaration and ends with `END`.

```
+PROG <MODULE_NAME>
HEAD <description>
...commands...
END
```

- The `+` prefix before `PROG` is recommended and should always be included for clarity.
- `urs:<n>` (e.g. `+PROG AQUA urs:1`) is the block's ID. The SOFiSTiK editor Teddy assigns it automatically before each calculation; the Report Browser and error messages refer to blocks by this number. It does **not** control the execution order — blocks always run in file order.
  - **New file:** omit `urs` — write `+PROG AQUA`, not `+PROG AQUA urs:1`. Teddy numbers the blocks.
  - **Editing an existing file:** keep every existing `urs:n` exactly as it is. Never renumber, remove or add numbers on existing blocks — that breaks the link to existing results in the Report Browser.
  - **Adding or copying a block in an existing file:** write the new block without `urs`. When copying a block, remove its `urs:n` so the copy does not duplicate the number; Teddy assigns the next free one.
  - Never reorder blocks to match their urs numbers — that changes the execution order.

  ```
  +PROG SOFILOAD urs:3 $ existing block: number kept
  HEAD Loads
  ...
  END

  +PROG SOFILOAD       $ new block: no urs, Teddy assigns it
  HEAD Additional snow load
  ...
  END
  ```
- `HEAD <description>` immediately follows the `+PROG` line and provides a human-readable title for the block. It is mandatory in generated files.
- `END` terminates the block. It is case-insensitive (`end` is equally valid) but use uppercase `END` for consistency.

### 1.2 Sequential Ordering
Modules must be ordered so that outputs of earlier modules are available as inputs to later ones. The canonical order is:

```
(TEMPLATE) → AQUA → SOFIMSHC → SOFILOAD → ASE → DECREATOR → MAXIMA → AQB → BEAM → COLUMN → BEMESS
```

The order is defined by the position of the blocks in the file, not by their `urs` numbers.

`+PROG TEMPLATE` is a placeholder module without analysis. In parametric input files it comes first and defines all project parameters with `STO#` (see §9 and `CADINP_VARIABLES_AND_CONTROL.md` §3).

A stand-alone cross-section design uses only `AQUA → AQB`. The same module may appear in several `+PROG` blocks (e.g. two AQB blocks for ULS design and SLS crack width).

---

## 2. Comments

CADINP supports two comment styles that serve distinct purposes:

### 2.1 Exclamation Mark Comments (`!`)
Used for block-level comments and file headers. The `!` character comments out the remainder of the line.

```
! This is a full-line comment
!***************************
! File: my_model.dat
!***************************
```

### 2.2 Dollar Sign Comments (`$`)
Used for inline comments following a command on the same line.

```
CTRL MESH 1        $ activate meshing
CONC NO 1 TYPE C FCN 25 $ concrete grade C 25
```

The `$` may also appear within a `+PROG` declaration line:
```
+PROG SOFILOAD $ Load Definition
```

- `//` is a third comment marker with the same effect as `!` and `$`.
- Separate every comment marker from the data and from the comment text by a blank.
- On a `+PROG` line only `$` is allowed as comment. A `+SYS` line must not contain any comment.
- A `$` inside text data must be quoted (`'A$B'`), otherwise it starts a comment.

### 2.3 Label Annotations (`!*!Label`)
A special comment form used to create named, collapsible groups in the SOFiSTiK Teddy editor. Always place immediately before the group of commands it describes.

```
!*!Label Structural Points
SPT NO 1 X 0 Y 0 Z 0
SPT NO 2 X 5 Y 0 Z 0
```

Use `!*!Label` annotations freely to document logical sections within each module block.

---

## 3. Command Syntax

### 3.1 General Form
Every CADINP command follows the pattern:

```
KEYWORD [PARAM_KEY VALUE] [PARAM_KEY VALUE] ...
```

- `KEYWORD` is the command name (e.g., `SPT`, `SLN`, `LC`, `CONC`).
- Parameters are key–value pairs: the parameter keyword immediately precedes its value.
- Parameter order within a command is generally free (positional exceptions exist — see module files).
- Commands are case-insensitive. Use **uppercase** for all keywords and parameter keys in generated files.

### 3.2 Parameter Value Types

| Type        | Syntax                         | Examples                              |
|-------------|--------------------------------|---------------------------------------|
| Integer     | Plain integer                  | `NO 1`, `GRP 3`                       |
| Real number | Decimal or integer             | `X 4.50`, `P1 1.0`                   |
| String      | Double quotes `"..."` preferred; single quotes `'...'` also valid | `TITL "Dead load"`, `TYPE 'G'`  |
| Keyword     | Unquoted identifier            | `TYPE C`, `FIX PP`, `PROB LINE`       |
| With unit   | Value followed by `[unit]`     | `T 220[mm]`, `P1 5.0[kN/m2]`         |

### 3.3 Unit Annotations
Units can be appended directly to a numeric value using square brackets with no space:

```
CTRL TOLG 0.01[m]
CTRL HMIN 0.5[m]
T 220[mm]
P1 15.0[kN/m]
AS 9.43[cm2]
```

Supported unit tokens include: `m`, `mm`, `cm`, `kN`, `kN/m`, `kN/m2`, `cm2`, `MN`, and others as defined per module. When a value is given without a unit, the module's default unit system applies (typically SI: metres, kilonewtons).

### 3.4 The `NO` Parameter
Most entity-defining commands use `NO` to assign a unique integer identifier:

```
SPT NO 1 X 0 Y 0 Z 0
SLN NO 4 NPA 1 NPE 3
LC NO 2 TYPE Q TITL "Live load"
```

`NO` may be omitted when it is the first positional argument and the context makes it unambiguous, but explicit `NO` is preferred in generated files.

### 3.5 Literals
- Literal values (keywords such as `TYPE C`) are significant only in their first four characters; they are converted to uppercase unless quoted.
- Quote a literal if it contains blanks, `,`, `;` or `$`, or if it could be confused with a number, a record name or a parameter name (`'1.45'`, `'A B'`).
- Line length: at most 255 characters per line.

### 3.6 Record Syntax Features
These features are part of the CADINP language and valid in every module. Prefer explicit, readable records in generated files; use the features below where they make the input clearly shorter without hiding its meaning.

| Feature | Syntax | Meaning |
|---------|--------|---------|
| Named items | `SPT NO 1 X 0 Z 3` | Value by parameter name, independent of position — always preferred |
| Default value | `-` | Use the default for this position. **Avoid** — positions may change between releases; omit the item or name the others instead. |
| Repeat value | `=` | Same value as in the preceding record (same record name only) |
| Repeat all | `==` | All remaining values as in the preceding record |
| Increment | `++` / `--` | Value of the preceding record ±1 (numbers, literals, lists, generations) |
| Several records per line | `;` | `LC 101 ; COPY 1,2,3 DESI` (not for text records such as `HEAD`) |
| List of values | `1,2,7,9` | No blanks inside; cannot span lines; all lists of a record must have the same length |
| Primary generation | `(start end incr)` | Generates one record per value; once per record |
| Secondary generation | `(start incr)` | Increments another item in step with the primary generation |

`=`, `==`, `++`, `--` and `-` must be surrounded by blanks.

Generation example (`NODE` of SOFIMSHA, from the CADINP manual):
```
NODE (1 5 1) 0 (0.5 -0.1)
```
generates `NODE 1 0 0.5`, `NODE 2 0 0.4`, … `NODE 5 0 0.1`. More than 9999 generated records or an end value that is not reached exactly is an error. For anything beyond a simple series use `LOOP` (see `CADINP_VARIABLES_AND_CONTROL.md` §9).

**Tables.** A record consisting only of parameter names defines a table header; the following lines contain values without record name. A header item may redefine the default with `NAME=value` (no blanks) and a default unit with `NAME=[unit]`:
```
LC  NO  TYPE  TITL
    1   G     'Self-weight'
    2   Q     'Live load'

SPT NO  X=[m]  Y=0[m]  Z=0[m]
    1   0.0
    2   5.0
```
The table is valid until a new record name appears or the same record name is repeated.

---

## 4. Sub-Records (Child Commands)

Some commands have associated sub-records that provide additional detail. Sub-records appear on subsequent lines, indented with 2–3 spaces, and belong to the immediately preceding parent command.

```
SPT NO 1000 X 0.0 Y 0.0 Z 0.0 FIX PXPYPZ
  SPTS DX 1 DY 0 DZ 0 CP 3000          $ spring sub-record

SLN NO 101 GRP 1 SNO 1
  SLNN S 0.0 DEGR 1                     $ node at position S=0
  SLNN S 2.25                           $ node at position S=2.25
  SLNP X 18.0 0.0 0.0 TYPE NURB        $ point definition

SAR NO 1 T 220[mm] MNO 1 MRF 2
  SARB OUT NL 1                         $ boundary line 1
  SARB OUT NL 4                         $ boundary line 4
```

Sub-record keywords are module-specific (see individual module files). Always indent sub-records relative to their parent command.

---

## 5. Special Commands

### 5.1 `LC ALL`
Instructs a module to process all previously defined load cases. Used in both SOFILOAD and ASE contexts:

```
LC ALL
```

### 5.2 `SYST`
Defines global system properties for a module. Syntax varies per module (see module files).

```
SYST 3D GDIR NEGZ GDIV -1000   $ in SOFIMSHC: 3D model, gravity direction
SYST PROB LINE                  $ in ASE: linear analysis
```

### 5.3 `CTRL`
Sets control parameters that govern module behaviour. Always `CTRL <KEY> <VALUE>`:

```
CTRL MESH 1
CTRL HMIN 0.5[m]
CTRL TOLG 0.01[m]
CTRL SMOO YES
CTRL AXIA UNIA
```

### 5.4 `HEAD`
Provides a human-readable title for the current module block. Place immediately after `+PROG`:

```
+PROG SOFILOAD
HEAD Actions and Loads
```

### 5.5 `PAGE`
Controls output formatting for the module's report. Commonly used to set unit display:

```
PAGE UNII 0
```

### 5.6 `NORM`
Sets the design standard/code for the analysis:

```
NORM DC DIN NDC "EN199x-200x"
```

---

## 6. Identifiers and Numbering Conventions

- All entity identifiers (`NO`) are positive integers.
- For simple models use sequential integers starting at 1.
- For models with distinct structural families (e.g., bottom chord, top chord, verticals, diagonals in a truss), use grouped numbering with a common hundreds prefix (e.g., 101–109 for one chord, 201–209 for another).
- Cross-references between entities use the same integer IDs (e.g., `SLN` references `SPT` via `NPA`/`NPE`, `SAR` references `SLN` via `SARB`).

---

## 7. Case Sensitivity

CADINP keywords and parameter names are **case-insensitive**. However, **always use uppercase** in generated files for consistency and readability. String values in quotes preserve their case.

---

## 8. Continuation and Line Length

- Each command is typically on a single line.
- Use `$$` as continuation only when a record exceeds 100 characters.
- `$$` must be preceded by a blank. Text after `$$` is a comment.
- An expression or a list of values cannot be split across lines with `$$`.
- Sub-records are placed on new lines with indentation — this is the primary mechanism for structuring complex definitions.

---

## 9. Variables and Expressions (LET# / STO#) — Summary

CADINP has numeric and text variables, arithmetic expressions, loops and conditions. This section lists the rules that apply to every file. **For anything beyond simple variables — and always for parametric input — read `CADINP_VARIABLES_AND_CONTROL.md`.**

### 9.1 Scope: LET# vs. STO#

| Command | Scope |
|---------|-------|
| `LET#name value` | Local to the **current `+PROG` block** — lost at `END` |
| `STO#name value` | Like `LET#`, and additionally **saved in the database** — available in all later `+PROG` blocks |

> A `LET#` variable is **not** available in a later `+PROG` block. Every variable used in more than one block must be defined with `STO#`.

### 9.2 Syntax

```
LET#name value
STO#name expression
```

- No blank between `LET#`/`STO#` and the name; one blank between name and value.
- Names: up to 16 alphanumeric characters (underscores allowed), first character a letter, case-insensitive (e.g. `#D`, `#AS`, `#H_SLAB`). Do not use function names or reserved names (`#PI`, `#VERSION`, names of the form `XXX_…` created by programs).
- Every assignment needs its own `LET#`/`STO#` prefix.
- Reference a variable with `#name` wherever a number is expected.
- **No blanks inside an expression:** `#A*#B+2`, not `#A * #B + 2`.
- Operators: `+ - * /`, `**` or `^`, comparisons `== <> >= <= > <` (result 1 or 0), `&` `|`.
- Functions (exact names): `SIN COS TAN ASIN ACOS ATN SQR ABS EXP LOG` (natural) `LGT` (base 10) `DIV MOD MIN MAX IIF ARC RANDOM`. There is **no** `SQRT`, `ATAN`, `LOG10` or `INT`.
- Dimensional values in variables: give the unit in the definition (`STO#H 600[mm]`), then reference the variable without a unit (`H #H`).

```
LET#D  10                        $ bar diameter [mm]
LET#A  0.15                      $ bar spacing [m]
LET#AS 0.0025*#D*#D*#PI/#A       $ reinforcement area per metre (#PI is preset)
```

### 9.3 Parametric Input — TEMPLATE Block

When the user requests a parametric input file, define all project parameters with `STO#` in a `+PROG TEMPLATE` block at the very beginning of the file, before `+PROG AQUA`:

```
+PROG TEMPLATE
HEAD Project parameters
STO#L     8.0[m]          $ span length
STO#H     600[mm]         $ beam height
STO#KDEF  0.6             $ deformation coefficient k_def (timber)
END

+PROG AQUA
...
SREC NO 1 H #H B 300[mm] MNO 1 MRF 2
END

+PROG MAXIMA
...
  ACT TYPE G
    LC 0 FACT #KDEF
...
END
```

See `CADINP_VARIABLES_AND_CONTROL.md` §3 for the complete pattern and a worked example.

---

## 10. Unique Entity Numbers

**Each entity number (`NO`) must be used only once per command type within a module block.** Defining the same command (e.g. `SLN`, `SPT`, `SAR`, `LC`) with the same `NO` a second time is an error. All properties for an entity — geometry, section, support conditions, and any other parameters — must be specified together on a single command line. Do not split an entity's definition across multiple records with the same `NO`.

> Exception: a **negative** `NO` value is the deliberate mechanism for modifying an already-defined entity (e.g. `SAR NO -1` to update area 1). This is the only valid reason to reference an existing number again.

---

## 11. Strict Parameter Compliance

**Only parameters explicitly listed in the parameter table of a command may be used.** Before writing any command, consult the parameter table in the relevant module file and include only parameters that appear there. Do not infer, guess, or transfer parameters from similarly named commands in other modules. For example, `SNO` is valid on `SLN` but does not appear in the `SAR` parameter table and must never be used on `SAR`.

---

## 12. Common Pitfalls to Avoid

1. **Missing END**: Every `+PROG` block must be closed with `END`.
2. **Touching urs numbers**: Omit `urs` in new files. In an existing file, never renumber existing `urs:n`, and never copy a block together with its `urs:n` (duplicate number).
3. **Referencing undefined entities**: Cross-references (e.g., `MNO`, `MRF`, `NPA`, `NPE`) must point to IDs previously defined in the same or an earlier module.
4. **Mixing unit systems**: Be explicit with `[unit]` suffixes when mixing mm/m or kN/kN/m to avoid silent scaling errors.
5. **String quoting**: Use double quotes `"..."` for `TITL` and class values. Single quotes are valid but less common.
6. **Sub-records without parent**: Sub-record keywords (e.g., `SARB`, `SLNN`, `SLNP`, `SPTS`, `DSLC`) are invalid without a preceding parent command.
7. **Unlisted parameters**: Never use a parameter on a command unless it appears in that command's parameter table. Parameters valid for one command are not transferable to another, even within the same module.
8. **Duplicate entity numbers**: Never define the same `NO` for the same command type more than once. Combine all parameters — geometry, supports, section — into the single defining record. Use a negative `NO` only when intentionally modifying an existing entity.
9. **LET# variables across blocks**: A `LET#` variable is lost at the `END` of its block. Use `STO#` for every variable needed in a later block; in parametric files define all parameters in a leading `+PROG TEMPLATE` block.
10. **Blanks inside expressions**: `#A+#B` is one value, `#A + #B` is three. Never put a blank inside an expression or after `LET#`/`STO#`.
