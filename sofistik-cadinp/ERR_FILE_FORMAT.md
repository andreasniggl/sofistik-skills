# SOFiSTiK *.err File Format — Syntax Reference

## Overview

Each SOFiSTiK module ships a companion `<module>.err` file that defines its complete CADINP command syntax, parameter lists, enum values, default units, and diagnostic messages. The parser reads this file to validate input. The format is fixed-column plain text (Windows CRLF, ANSI or UTF-8 BOM).

---

## File Structure

An `.err` file has four distinct sections in order:

```
1.  File header          (0000 lines)
2.  Command definitions  (-10 / -20 / -* lines)
3.  Diagnostic messages  (NNNx(...) lines)
4.  Output text strings  (NNN<text> lines)
```

---

## Section 1 — File Header

```
0000<MODULE>   SOFiSTiK AG
0000VERSION         <build> ANSI
```

| Field | Width | Description |
|-------|-------|-------------|
| `0000` | 4 | Literal tag |
| `<MODULE>` | — | Module name in uppercase (e.g. `SOFIMSHC`, `AQUA`) |
| `SOFiSTiK AG` | — | Vendor string — always literal |
| `VERSION` | — | Literal keyword |
| `<build>` | 6 | Numeric build identifier (e.g. `250370`) |
| `ANSI` | — | Character set tag |

**Example:**
```
0000SOFIMSHC   SOFiSTiK AG
0000VERSION         250370 ANSI
```

---

## Section 2 — Command Definitions

### Column layout

Every definition line follows a fixed column layout:

| Columns | Width | Content |
|---------|-------|---------|
| 0–3     | 4     | Line type code (see below) |
| 4–7     | 4     | Command name (blank on continuation lines) |
| 8+      | 5 each | Parameter tokens in fixed 5-character blocks |

### Line type codes

The first four characters form the **line type code**:

```
-<language><type><index>
```

| Position | Values | Meaning |
|----------|--------|---------|
| col 0 | `-` | Always a dash — identifies a definition line |
| col 1 | `1` `2` `*` | Language: `1`=German, `2`=English, `*`=language-independent |
| col 2 | `0`–`9` `A`–`Z` | Line type (see table below) |
| col 3 | space, `0`–`9`, `A`–`Z` | Parameter position index (for enum/unit lines) or space |

### Line type codes (col 2)

| Code | Meaning |
|------|---------|
| `0`  | Main parameter line for a command or its continuation |
| `1`  | Enum value list for the parameter at the position given by col 3 |
| `2`  | Unit/default values line — column-aligned with the immediately preceding parameter line |
| `3`  | Error reference (cross-reference to another command's messages) |
| `7`  | Human-readable syntax summary line (printed in error output) |

### Parameter position index (col 3 on enum lines)

On enum lines (type `1`), col 3 encodes the **1-indexed position** of the parameter that receives the enum values. Counting includes `XXXX` placeholder slots:

| Col 3 | Position (1-indexed) |
|-------|---------------------|
| `1`   | 1st parameter |
| `2`   | 2nd parameter |
| …     | … |
| `9`   | 9th parameter |
| `A`   | 10th parameter |
| `B`   | 11th parameter |
| …     | … |
| `Z`   | 35th parameter |

**Example:** For command SAR with parameters `'NO "FIX XXXX XXXX XXXX 'GRP MNO MRF "REF NX NY NZ NRA "QREF ...`, the line `-21E ABOV CENT BELO` assigns enums `ABOV`, `CENT`, `BELO` to the parameter at position `E` (14th) = `QREF`.

### Language version pairing

Command records always appear in pairs: a version-1 (German) line and a version-2 (English) line with identical structure but language-specific parameter names.

```
-10 SPT 'NR  X    Y    Z   "REF 'NREF XXXX"FIX  ...
-20 SPT 'NO  X    Y    Z   "REF 'NREF XXXX"FIX  ...
```

The parser uses version-2 (`-2x`) names for all modern input. Version-1 (`-1x`) names remain accepted for backwards compatibility.

Language-independent lines (`-*x`) apply to both versions simultaneously.

---

### Main parameter lines (`-10`, `-20`, `-*0`)

```
-20 SAR 'NO  "FIX  XXXX XXXX XXXX'GRP  MNO  MRF "REF  NX   NY   NZ
```

**Field layout:**

| Columns | Content |
|---------|---------|
| 0–3     | Line type: `-20 ` |
| 4–7     | Command name: `SAR ` (4 chars, space-padded) |
| 8–12    | 1st parameter: `'NO  ` (5-char block) |
| 13–17   | 2nd parameter: `"FIX ` (5-char block) |
| 18–22   | 3rd parameter: `XXXX ` (5-char block) |
| …       | subsequent 5-char blocks |

Each **parameter token** occupies exactly 5 characters (4 content + 1 space padding). The leading character is a **type prefix**:

| Prefix | Type | Input accepted |
|--------|------|----------------|
| `'`    | Integer | Whole number |
| `"`    | Keyword / enum | Literal string from enum list |
| `` ` ``| String / title | Quoted or unquoted text |
| `=`    | Reference | Number referencing another element |
| `!`    | Variable name | Identifier string |
| `+`    | Additive flag | Value added to running total |
| *(none)*| Float | Real number, optionally with unit suffix |
| `XXXX` | Placeholder | Reserved position — value accepted but currently unused |

Note: a parameter may accept values of multiple types. For example, `'NO` (integer) may also accept enum values assigned to its position via enum lines.

#### Continuation lines

When a command has more parameters than fit on one line, they continue on subsequent `-*0` lines. The command name slot (columns 4–7) is blank, and parameters continue in 5-char blocks from column 8:

```
-20 SAR 'NO  "FIX  XXXX XXXX XXXX'GRP  MNO  MRF "REF  NX   NY   NZ
-*0      NRA "QREF'KR  'DRX  DRY  DRZ  DROT T    TX   TY   TXY  TD   CB   CT
-*0     'MCTL H1   H2   H3  'XFLG
```

A `-*0` line is a **continuation** of the current command's parameters (not a new command) when the command name slot is blank — even if the first parameter token looks like a command name (e.g. `NRA`).

A `-*0` line defines a **sub-command** only when the first token starts with the parent command's prefix (e.g. `SARB` under `SAR`, `GAXH` under `GAX`).

---

### Unit/default lines (`-*2`)

Immediately follows the parameter line it annotates. Each 5-char column block is **aligned with the corresponding parameter** on the preceding line. A blank block means no unit constraint.

```
-20 SAR 'NO  "FIX  XXXX XXXX XXXX'GRP  MNO  MRF "REF  NX   NY   NZ
-*0      NRA "QREF'KR  'DRX  DRY  DRZ  DROT T    TX   TY   TXY  TD   CB   CT
-*2                                    0005 1010 1010 1010 1010 1010 9999 9999
-*0     'MCTL H1   H2   H3  'XFLG
-*2           1001 1001 1001
```

In this example, the `-*2` on line 3 annotates the `-*0` on line 2. The `0005` in column block 6 (counting from 0) aligns with `DROT`, assigning it the unit code for degrees.

The `-*2` on line 5 annotates the `-*0` on line 4. The `1001` values align with `H1`, `H2`, `H3`, assigning them the unit code for metres.

Unit codes are 4-digit identifiers defined in `docs/Implicit_Units.txt`. Common codes:

| Code | CDBASE unit | Description |
|------|-------------|-------------|
| `1001` | m | Geometric length |
| `1010` | m | Thickness |
| `1011` | mm | Cross-section dimension |
| `1012` | m2 | Cross-section area |
| `1014` | m4 | 4th order section area |
| `1020` | cm2 | Reinforcement area |
| `1023` | mm | Reinforcement diameter |
| `1024` | mm | Cover / static distance |
| `1090` | N/mm2 | Material modulus |
| `1092` | N/mm2 | Material stress |
| `1095` | kN/m | Elastic support (force/deformation) |
| `1096` | kN/m2 | Elastic support (force/deformation/length) |
| `1097` | kN/m3 | Elastic support (force/deformation/area) |
| `1098` | kNm/rad | Elastic support (moment/rotation) |
| `1101` | kN | Beam normal force |
| `1104` | kNm | Beam bending moment |
| `1111` | kN/m | Plate membrane force |
| `1114` | kNm/m | Plate bending moment |
| `1200` | ° | Angle |
| `1215` | °C | Temperature |
| `1290` | sec | Time |
| `0005` | ° | Degrees (legacy code) |
| `9999` | - | Maximum allowed value / dimensionless |

See `docs/Implicit_Units.txt` for the complete mapping.

---

### Enum value lines (`-*1X`, `-11X`, `-21X`)

List the valid literal values for the parameter at position `X` (encoded in col 3). Up to 10 values per line, each in a 5-character block. Use `....` as a placeholder for a reserved but unassigned position.

```
-*11     PROP VOID
-11E     OBEN MITT UNTE
-21E     ABOV CENT BELO
-*1R     AUTO REGM SNGQ OFF
```

In this example (from SAR):
- `-*11` → position `1` (1st param = `NO`) receives enums `PROP`, `VOID`
- `-21E` → position `E` (14th param = `QREF`) receives English enums `ABOV`, `CENT`, `BELO`
- `-11E` → same position, German enums `OBEN`, `MITT`, `UNTE`
- `-*1R` → position `R` (27th param = `MCTL`) receives enums `AUTO`, `REGM`, `SNGQ`, `OFF`

Multiple lines with the same subtype extend the enum list. Language-specific lines (`-11X` / `-21X`) provide German / English synonyms for the same enum slots. Language-independent lines (`-*1X`) apply to both.

---

### Syntax summary lines (`-17`, `-27`)

One human-readable line describing the command syntax, used in error output. No machine-parsed content.

```
-17 STEU [MESH|SDIV|NODE|TOPO|OPTI|BSEC|PSUP|LSUP|WARN|LOCA|HMIN|FEIN|PROG|EFAK|TOLG|TOLN|HEAL] WERT ...
-27 CTRL [MESH|SDIV|NODE|TOPO|OPTI|BSEC|PSUP|LSUP|WARN|LOCA|HMIN|FINE|PROG|EFAC|TOLG|TOLN|HEAL] VAL  ...
```

---

### Command aliases (`=` lines)

Alias definitions that register a command name the module accepts. These appear near the top of the file and define commands with no parameters of their own (the command simply enables a feature or inherits parameters from elsewhere).

```
-10=KOPF
-20=HEAD
-10=BETO
-20=CONC
-*0=MAT
```

Format: `-<language>=<NAME>` or `-*0=<NAME>`.

German/English pairs (e.g. `BETO`/`CONC`) register both names. Language-independent aliases (`-*0=MAT`) register a single name for both languages.

---

## Section 3 — Diagnostic Messages

Each message occupies one or more lines. Format:

```
NNNx('text with format specs', format_args)
NNNx 'continuation text'
```

| Field | Description |
|-------|-------------|
| `NNN` | 3-digit message number |
| `x`   | Language / severity code (see table below) |
| `(...)` | Fortran-style format string with message text and argument descriptors |

### Language / severity codes

| Code | Meaning |
|------|---------|
| `D`  | German text (Deutsch) |
| `E`  | English text |
| `L`  | German warning / log message |
| `M`  | English warning / log message |
| `T`  | German terminating error |
| `U`  | English terminating error |

Each message always has both a `D`/`L`/`T` (German) and an `E`/`M`/`U` (English) variant with the same number.

### Format argument descriptors

| Descriptor | Meaning |
|------------|---------|
| `I` | Integer |
| `F10.3` | Floating-point, 10 wide, 3 decimal places |
| `A` or `An` | Character string of length n |
| `'literal'` | Literal text in output |
| `/` | Line break in output |
| `,` | Separator |

**Multi-line messages** use a repeated number + code on each line:

```
693L('Generierung von Dreieck',I,' erzwingt Verschieben von fixen Randknoten. '/
693L 'An Strukturkante',I,' sollte die Elementgröße verringert werden.')
693M('Conversion of triangle',I,' enforces movement of fixed nodes on the boundary. '/
693M 'Mesh size on structural edge',I,' should be reduced.')
```

### Special message numbers

| Number | Meaning |
|--------|---------|
| `001`  | General structural generation summary |
| `999`  | Placeholder — "NO MESSAGE" |
| `000`  | Comment / separator (text ignored by parser) |

---

## Section 4 — Output Text Strings

Short localised text strings used in printed output tables. Format:

```
NNNtext<
```

| Field | Description |
|-------|-------------|
| `NNN` | 3-digit string number |
| `text`| The string literal, no quoting |
| `<`   | End-of-string delimiter |

Optional suffix after `<`:

| Suffix | Meaning |
|--------|---------|
| `*S`   | Section header with automatic separator line |

**Example:**
```
280Structural Lines<*S
291Structural Areas<*S
320with Section Properties<
401Bearing Point<
999SOFIMSHC - STRUCTURAL ELEMENTS AND GEOMETRY
```

The German and English blocks are separated by `000 ***...***` comment lines:

```
000 *******************************************************************
000 *  DEUTSCHSPRACHIGE AUSGABETEXTE                                  *
000 *******************************************************************
101Initialisierung des Systems..........................:<
...
000 *******************************************************************
000 * AUSGABETEXTE ENGLISCHE VERSION                                  *
000 *******************************************************************
101Initialise the system................................:<
```

---

## Complete Minimal Example

```
0000MYMOD      SOFiSTiK AG
0000VERSION         250370 ANSI
-10=KOPF
-20=HEAD
-10=ENDE
-20=END
-10 MYCD'NR  "TYP  VAL  `BEZ
-20 MYCD'NO  "TYPE VAL  `TITL
-*2           1001
-*11     A    B    C
-17 MYCD [A|B|C] VAL ...
-27 MYCD [A|B|C] VAL ...

001D('Modul mit',I,' Fehlern beendet')
001E('Module finished with',I,' errors')
002L('Unbekannter Typ',I)
002M('Unknown type',I)
999 ('--- NO MESSAGE ---')
000 *******************************************************************
000 *  DEUTSCHSPRACHIGE AUSGABETEXTE                                  *
000 *******************************************************************
101Verarbeitung der Eingabe:<
999MYMOD - MEIN MODUL
000 *******************************************************************
000 * AUSGABETEXTE ENGLISCHE VERSION                                  *
000 *******************************************************************
101Processing input:<
999MYMOD - MY MODULE
```

---

## Notes

- Line endings are Windows CRLF (`\r\n`).
- The file may begin with a UTF-8 BOM (`\xEF\xBB\xBF`) or have no BOM (ANSI).
- The fixed column layout is: 4 chars line type, 4 chars command name, then 5-char parameter blocks.
- `XXXX` parameter slots are syntactically valid but semantically reserved — the parser accepts a value but the module ignores it.
- The `0000` header section must appear before any `-` command lines.
- Message number `000` with any severity code is always treated as a comment and never emitted.
- A `-*0` continuation line is distinguished from a new command by context: if the command name slot (cols 4–7) is blank and a current command exists, it is a continuation.
- Enum values can be assigned to any parameter type, not just keyword (`"`) parameters. The position index determines the target parameter.
- Unit codes reference the implicit unit system defined in `docs/Implicit_Units.txt`.
