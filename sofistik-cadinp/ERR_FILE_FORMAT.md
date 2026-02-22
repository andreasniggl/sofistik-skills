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

### Line type codes

The first four characters of every command definition line form a **line type code** with the structure:

```
-<version><subtype>
```

| Position | Values | Meaning |
|----------|--------|---------|
| col 1 | `-` | Always a dash — identifies a definition line |
| col 2 | `1` `2` `*` | Language version: `1`=German, `2`=English, `*`=language-independent |
| col 3 | `0`–`9` `A`–`F` | Subtype (see table below) |
| col 4 | space | Separator (or part of subtype for two-digit subtypes) |

> Lines beginning with any other character are not definition lines (they are messages or output text).

### Subtype codes

| Code | Meaning |
|------|---------|
| `0 ` | Main parameter line for a command or its continuation |
| `2 ` | Default values line — column-aligned with the preceding `*0` or `10`/`20` line |
| `7 ` | Human-readable syntax summary line (printed in error output) |
| `11` | Enum value list — one set per line, 10 values per line |
| `12` | Secondary enum list (bitmask flags or alternative sets) |
| `13` | Tertiary enum list |
| `14` | Quaternary enum list |
| `15` | Quinary enum list |
| `16` | Senary enum list |
| `17` | Septenary enum list |
| `18` | Octonary enum list |
| `19` | Nonary enum list |
| `1B` | Geometry sub-type enum (curves, surfaces) |
| `1C` | Curve type enum continuation |
| `1E` | Position / reference enum |
| `1R` | Mode enum (e.g. mesh control modes) |
| `1L` | Line-based type list |

### Language version pairing

Command records always appear in pairs: a version-1 (German, historical) line and a version-2 (English, current) line with identical structure but language-specific parameter names.

```
-10 SPT  NR   X    Y    Z   "REF 'NREF XXXX"FIX  ...
-20 SPT  NO   X    Y    Z   "REF 'NREF XXXX"FIX  ...
```

The parser uses version-2 (`-2x`) names for all modern input. Version-1 (`-1x`) names remain accepted for backwards compatibility.

Language-independent lines (`-*x`) apply to both versions simultaneously.

---

### Main parameter lines (`-10`, `-20`, `-*0`)

```
-20 CMD 'P1  "P2  P3  `P4  =P5  !P6  XXXX P7
```

**Field layout (free-column after line type):**

| col 1–3 | col 4 | col 5–8 | col 9 onward |
|---------|-------|---------|--------------|
| `-20` | space | `CMD ` | space-separated parameter tokens |

Each **parameter token** is exactly 4 or 5 characters wide (space-padded). The leading character is a **type prefix**:

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

#### Continuation lines

When a command has more parameters than fit on one line, they continue on subsequent `-*0` lines (no command name, just parameters):

```
-20 SAR 'NO  "FIX  XXXX XXXX XXXX'GRP  MNO  MRF "REF  NX   NY   NZ
-*0      NRA "QREF'KR  'DRX  DRY  DRZ  DROT T    TX   TY   TXY  TD   CB   CT
-*0     'MCTL H1   H2   H3  'XFLG
```

---

### Default values lines (`-*2`)

Immediately follows the parameter line(s) it annotates. Each token is column-aligned with its corresponding parameter above and encodes the **unit** or **maximum** for that parameter using a 4-digit code:

```
-*2           1001 1001 1001                                    1001 1001 1010
```

Blank columns mean no constraint or unit. Defined codes:

| Code | Meaning |
|------|---------|
| `9999` | Maximum allowed value |
| `1001` | Unit: metres `[m]` |
| `1010` | Unit: millimetres `[mm]` |
| `1002` | Unit: dimensionless area ratio |
| `1006` | Unit: metres (level / elevation) `[m]` |
| `1024` | Unit: metres (area dimension) |
| `1096` | Unit: spring stiffness `[kN/m]` |
| `1097` | Unit: rotational spring `[kNm/rad]` |
| `1098` | Unit: spring stiffness per area |
| `1099` | Unit: torsional spring |
| `0005` | Unit: degrees `[°]` |
| `0062` | Integer count |

---

### Enum value lines (`-*11`, `-111`, `-211`, etc.)

List the valid literal values for the most recently defined keyword (`"`) parameter. Up to 10 values per line, each 4–5 characters wide, space-padded. Use `....` as a placeholder for a reserved but unassigned position.

```
-*11     MESH ADAP BSEC SDIV RELA .... EDRL DELN NODE TOPO
-*11     OPTI PSUP LSUP PART SUB  WARN NUM  INIT LOCA REST
-111     HMIN FEIN PROG HFAK EFAK TOLG TOLN .... .... HEAL
-211     HMIN FINE PROG HFAC EFAC TOLG TOLN .... .... HEAL
```

Multiple `*11` lines extend the enum list. `111` / `211` lines are language-specific synonyms for the same positions (German / English names for the same enum slots).

Subtypes `12` through `19`, `1B`, `1C`, `1E`, `1R`, `1L` follow the same value-list structure but apply to secondary enum parameters — their association with a specific `"` parameter is positional within the command block.

---

### Syntax summary lines (`-17`, `-27`)

One human-readable line describing the command syntax, used in error output. No machine-parsed content.

```
-17 STEU [MESH|SDIV|NODE|TOPO|OPTI|BSEC|PSUP|LSUP|WARN|LOCA|HMIN|FEIN|PROG|EFAK|TOLG|TOLN|HEAL] WERT ...
-27 CTRL [MESH|SDIV|NODE|TOPO|OPTI|BSEC|PSUP|LSUP|WARN|LOCA|HMIN|FINE|PROG|EFAC|TOLG|TOLN|HEAL] VAL  ...
```

---

### Command aliases (`=` lines)

Short alias or translation mappings at the top of the file:

```
-10=KOPF
-20=HEAD
-10=ENDE
-20=END
```

Format: `-<version>=<ALIAS>` — the parser treats the alias as equivalent to the full command name that follows.

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
- Column alignment of parameter tokens is by convention 5 characters (4 + 1 space); the parser is whitespace-tolerant on continuation lines.
- `XXXX` parameter slots are syntactically valid but semantically reserved — the parser accepts a value but the module ignores it.
- The `0000` header section must appear before any `-` command lines.
- Message number `000` with any severity code is always treated as a comment and never emitted.
