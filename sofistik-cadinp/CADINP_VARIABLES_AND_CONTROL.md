# CADINP Variables, Expressions and Control Flow

This file covers the programming features of CADINP: variables (`LET#`, `STO#`), arithmetic expressions, functions, loops, conditions, database access and parametric input with a `+PROG TEMPLATE` block.

**Read this file whenever the input uses variables, expressions, loops or conditions, when the user asks for a parametric input file, or when values are read back from the database.** The basic record syntax in `CADINP_LANGUAGE_RULES.md` applies in addition.

Source: SOFiSTiK CADINP manual, chapter *Introduction to CADINP* (sections LET/STO, Arithmetic Expressions, FUN, LOOP, IF, @CDB/@KEY/@(), Parametric Input).

---

## 1. Two Processing Stages

A SOFiSTiK input file is processed in two stages. Do not mix up the two kinds of placeholders:

| Stage | Who | Placeholder | What happens |
|-------|-----|-------------|--------------|
| 1. Parsing | SPS / WPS (Teddy) | `$(name)` | Pure **text substitution** before any program runs. No arithmetic. Blocks may be inserted or skipped. |
| 2. Execution | CADINP processor of each program (AQUA, SOFIMSHC, …) | `#name` | **Numeric variables** evaluated with arithmetic. |

Because stage 1 is text substitution, `$(A)*3` with `A = "2+2"` yields `2+2*3 = 8`, whereas `($(A))*3` yields `12`. Generated files should use `#` variables; use `$(name)` only when the user explicitly asks for SPS/WPS text parameters.

---

## 2. LET# and STO# — Scope

| Command | Scope |
|---------|-------|
| `LET#name value` | **Local to the current `+PROG` block.** The variable is lost at `END`. |
| `STO#name value` | Defines the variable like `LET#` **and saves it in the project database (CDB)**. It is available in every later `+PROG` block and in later runs on the same database. |

> **Rule:** any variable that is used in more than one `+PROG` block must be defined with `STO#`. A `LET#` variable from an earlier block is **not** available in a later block — referencing it there is an error.

- `STO#name` without a value saves the current value of an existing variable.
- A `LET#name` in a later block with the same name as a stored variable only overrides it locally in that block; the stored value is unchanged.
- `DEL#name` removes a stored variable from the database. Wildcards are allowed: `DEL#OPT*`, `DEL#A?00`. Do not use `DEL#` inside a `LOOP` or `IF` block (unexpected results).
- Stored variables stay in the database after the parameter is removed from the input. Use `DEL#name` to clean up a parameter that is no longer used.
- `RCL#` re-reads stored values:

| Command | Effect |
|---------|--------|
| `RCL#ALL` | Read all named variables from the database |
| `RCL#name` | Read one named variable / array |
| `RCL#name(3)` | Read one array element |
| `RCL#name cdbfile` | Read the variable from another CDB |

---

## 3. Parametric Input with a TEMPLATE Block

When the user asks for a **parametric** input file (or for parameters defined "at the top", "as variables", "with #sto"), put all parameters into a `+PROG TEMPLATE` block at the very beginning of the file — **before `+PROG AQUA`**.

- `TEMPLATE` is a placeholder module. It performs no analysis; it is used to define the project parameters and to print them in the report.
- Define every parameter with `STO#` so it is available in all following blocks.
- Give every dimensional parameter an explicit unit (`STO#L 8.0[m]`, `STO#H 600[mm]`) — see §5. The value is then converted immediately and the variable can be used in any block regardless of the block's default unit (e.g. mm in AQUA, m in SOFIMSHC).
- Use one `!*!Label` group per topic (geometry, sections, materials, loads).
- Derived values that are needed in several blocks are also computed and stored in TEMPLATE (`STO#LTOT #NSPAN*#L`). Values needed only inside one block may be `LET#` variables in that block.
- Parameter names: meaningful, up to 16 characters, first character a letter (e.g. `#L_SPAN`, `#H_BEAM`, `#Q_LIVE`). Never use reserved names (§10) or function names (`SIN`, `SQR`, …).

```
+PROG TEMPLATE
HEAD Project parameters

!*!Label Geometry
STO#NSPAN 3                  $ number of spans [-]
STO#L     8.0[m]             $ span length

!*!Label Section and material
STO#H     600[mm]            $ beam height
STO#B     300[mm]            $ beam width
STO#FCK   30                 $ concrete strength class f_ck [N/mm2]

!*!Label Loads
STO#Q     15.0[kN/m]         $ live load on all spans

TXB Continuous beam with #(NSPAN,2.0) spans of L = #(L,6.2) m
TXB Live load q = #(Q,6.2) kN/m
END

+PROG AQUA
HEAD Materials and sections
NORM DC EN NDC 199X-200X
CONC NO 1 TYPE C FCN #FCK TITL 'Concrete'
STEE NO 2 TYPE B CLAS 500B TITL 'B500B'
SREC NO 1 H #H B #B MNO 1 MRF 2 TITL 'Beam'
END

+PROG SOFIMSHC
HEAD Structural model
SYST 3D GDIR NEGZ GDIV -1000
CTRL MESH 1
CTRL HMIN 0.5[m]
CTRL TOLG 0.01[m]

!*!Label Structural points
LOOP#I #NSPAN+1
  IF #I==0
    SPT NO #I+1 X #I*#L Y 0[m] Z 0[m] FIX PPMX       $ pinned
  ELSE
    SPT NO #I+1 X #I*#L Y 0[m] Z 0[m] FIX PZPYMX     $ roller
  ENDIF
ENDLOOP

!*!Label Structural lines
LOOP#I #NSPAN
  SLN NO #I+1 NPA #I+1 NPE #I+2 SNO 1 GRP 1
ENDLOOP
END

+PROG SOFILOAD
HEAD Loads
LC 1 TYPE G FACD 1.0 TITL 'G - Self-weight'
LC 2 TYPE Q TITL 'Q - Live load'
LOOP#I #NSPAN
  LINE REF SLN NO #I+1 TYPE PZZ P1 -#Q
ENDLOOP
END
```

> The variables `#NSPAN`, `#L`, `#H`, … are stored in TEMPLATE and used in AQUA, SOFIMSHC and SOFILOAD. The loop index `#I` is a local `LET#`-type variable of each block.

---

## 4. Variable Names, Values and Arrays

```
LET#name value        $ local
STO#name value        $ stored
```

- The name follows `LET#` / `STO#` **directly, without a blank**. Up to 16 alphanumeric characters (underscores allowed), first character a letter. Case-insensitive.
- A separation character (blank) follows the name, then the value: a number, an expression, a list, a generation or a literal in quotes.
- Every assignment needs its own `LET#` / `STO#` prefix — the record name is **not** repeated implicitly like for other records.
- Legacy: pure numbers `#1` … `#9999` are local scalar variables (`LET#1 12.4`). They are still supported but use named variables in generated files (except as short loop counters if it improves readability).
- If an expression is assigned, it is evaluated first and the resulting value is stored.

**Arrays** (index starts at 0). A list or generation assigns consecutive elements:

```
LET#A 4,5,6 7,8,9      $ A(0:5) = 4,5,6,7,8,9
LET#A(2) 5.1           $ single element
LET#A(0:10) 0.0        $ same value for elements 0..10
LET#A(#I1:#I2) 1.0     $ index range from variables
LET#A(3) 7,8           $ elements 3 and 4
LET#V #A               $ #A without index = first element A(0)
LET#V #A(#I)           $ element with index #I
LET#V =A(1)            $ leading '=': unidentified names are variables
LET#B #A(:)            $ copy all elements to B
LET#B #A(3:)           $ copy elements 3..end
LET#B #A(2:4)          $ copy 3 elements starting at 2
LET#B #A(2:3) #A(5:6)  $ new array from two slices (lists of sub-arrays are not allowed)
LET#C #A(#11)          $ index taken from legacy variable 11
```

- For large arrays define the element with the largest index first (`LET#A(999) 0`) to avoid repeated reallocation.
- A **fractional index interpolates linearly**: with `A(1)=14`, `A(2)=16`, `#A(1.3)` = 14.6.

---

## 5. Units of Variables

- A variable **without** a unit takes the unit of the context where it is used. Therefore the same unitless variable cannot be used for a section dimension in AQUA (mm) and a coordinate in SOFIMSHC (m).
- A variable **with** a unit (`LET#B 20[mm]`) is converted immediately and can be used everywhere. CADINP checks that the resulting unit is allowed at the position where it is used.
- The unit is inherited by expressions: `LET#B 20[mm]`, `LET#D 1.5[m]` → `LET#A #B*#D` is `0.03[m2]`.
- A constant added to or subtracted from a variable is taken in the same unit as the variable.
- Strip the unit from an expression with `[-]`: `LET#X #B*#D[-]`.
- An array has the unit of its element 0 for all elements.
- Do not append a unit to the *reference* of a variable that already has a unit (`H #H`, not `H #H[mm]`). The general "always annotate units" rule of `SKILL.md` is satisfied by the unit in the variable definition.

---

## 6. Arithmetic Expressions

An expression may be used wherever a number is expected (also inside lists and generations). **An expression must not contain blanks** — `#A+#B`, not `#A + #B`. Parentheses are allowed.

| Operator | Meaning |
|----------|---------|
| `+` `-` | Addition, subtraction |
| `*` `/` | Multiplication, division (no operator between two operands = multiplication: `3(5.0+4.0)`) |
| `**` or `^` | Exponentiation |
| `==` `<>` | Equal / not equal → 1.0 (true) or 0.0 (false) |
| `>=` `<=` `>` `<` | Relational → 1.0 or 0.0 |
| `&` `\|` | Bitwise AND / OR on the integer part |

The logical operators all have the same precedence — **always use parentheses** in combined conditions: `(#A>0)&(#B<5)`.

**Functions** (exact names — `SQRT`, `ATAN`, `LOG10`, `INT` do **not** exist):

| Function | Meaning |
|----------|---------|
| `SIN(x)` `COS(x)` `TAN(x)` | Trigonometric functions (angle unit: degrees by default) |
| `ASIN(x)` `ACOS(x)` | Arc sine, arc cosine |
| `ATN(x)`, `ATN(y,x)` | Arc tangent of x, or of y/x |
| `ARC(x)` | Convert angle to radians (arc) |
| `SQR(x)` | Square root |
| `ABS(x)` | Absolute value |
| `EXP(x)` | e^x |
| `LOG(x)` | Natural logarithm |
| `LGT(x)` | Base-10 logarithm |
| `DIV(x,y)`, `xDIVy` | Integer part of x/y |
| `MOD(x,y)`, `xMODy` | Remainder of x/y |
| `MIN(x,y,..)` `MAX(x,y,..)` | Minimum / maximum |
| `RANDOM(x)` | Random value 0..1 (`x=0` re-initialises the seed) |
| `IIF(expr,v1,v2)` | `v1` if `expr` ≠ 0, else `v2` |

- Angle mode: `DEG`, `GON` or `RAD` may precede an argument, separated by a comma: `SIN(RAD,2.435)`. An assignment containing only the mode name sets it permanently: `LET#0 RAD`.
- Examples: `SIN(30.)+3*COS(45.)`, `100.+MOD(354,32)`, `345*#K+#A(2)`, `IIF(#L>10,0.8,1.0)`.
- Floating point comparisons with `==` are unreliable for fractional values — use a tolerance: `ABS(#A-0.35)<0.001`.

---

## 7. Text Variables and Variables in Literals

**Text variables** — quotes are mandatory:

```
LET#TXT 'ABCDEFGHIJK'
```

- Text is stored in blocks of 8 characters: `#TXT(1)` is `'IJK     '`.
- Substrings: `#TXT(3:7)` = characters 3 to 7 (indices may be expressions).
- Convert text to numbers with `VAL()`: `LET#TXT '1.23,1.48'` then `LET#V VAL(#TXT)` → `#V(0)=1.23`, `#V(1)=1.48`.
- Text comparisons in `IF` only with `==` and `!=`; case-sensitive; no parentheses around the strings.

**Variables inside literal items** (e.g. a title or a literal parameter):

1. A quoted literal starting with `=` is passed to the program unchanged without the leading `=` (only for items that accept formulas).
2. If the variable holds a literal, its text is inserted.
3. If the variable holds a number, the number is formatted and inserted.

- In an item that accepts a literal instead of a number, only the plain form `#name` is allowed: `A#N` with `#N=25` yields `A25`. `#X/2` yields the literal `"25/2"`; prefix `=` to get a number: `=#X/2`.
- Inside a real literal (titles, text) use the format function `#(expr,w.d)`: total width `w`, `d` decimals. The first argument may be any expression: `TITL 'Span #(#I+1,2.0)'`, `'alpha = #(#ALPHA,8.3)'`.

**Printing values in the report** — in `TXB`, `TXE` and `<TEXT>` lines, write `#(name,w.d)`:

```
TXB HEIGHT       RADIUS
TXB    0.0    #(R1,9.1)
TXB PARAMETER ZZ = #(ZZ,9.3)
```

---

## 8. FUN — User Functions and TAB — Interpolation Tables

**User function** — a literal starting with `=FUN(`, a formal parameter name and an expression:

```
LET#X 0                                   $ formal parameter must be initialised before the first call
LET#F '=FUN(X,3*#X**3-2*#X**2+5*#X)'
LET#Y #F(1.234)
```

The formal parameter is not changed by a call. Recursive calls are allowed.

**Interpolation table** — two arrays of equal length (X and Y) connected by a `TAB` literal:

```
LET#X 0.0,2.0,3.5
LET#Y 0.0,100.0,100.0
LET#SIG 'TAB(X,Y)'          $ #SIG(1.73) interpolates linearly
LET#DY -,0,-
LET#SIG 'TAB(X,Y,DY)'       $ with derivatives: quadratic / cubic spline interpolation
```

---

## 9. Control Flow

### 9.1 LOOP / ENDLOOP

```
LOOP#I n          $ n repetitions, #I = 0, 1, …, n-1
  ...
ENDLOOP [cond]    $ optional: leave the loop as soon as cond <= 0
```

- `n` may be an expression (`LOOP#I #NSPAN+1`). Without `n` the loop runs at most 9999 times — then an `ENDLOOP` condition is required.
- The index variable (`#I`) starts at **0**. It may be changed inside the loop but is restored after the condition check of each cycle.
- `LOOP#I A` (array **name without `#`**) loops over all elements of array `A`. `LOOP#I #A` would use the value of `A(0)` as the count.
- `LOOP#I DEF(A)` loops only over the defined elements of `A`.
- Loops can be nested up to 32 levels. One loop body must not exceed 255 lines; for longer loops set `LET#LOOPSIZE <lines>` before the first `LOOP`.
- Indent the loop body by 2 spaces.

```
LET#XS 10,22,34,55,76,83
LOOP#I XS                          $ name only
  SPT NO #I+1 X #XS(#I) Y 0[m] Z 0[m]
ENDLOOP

LET#ANG 0
LOOP                               $ open loop with end condition
  ...
  LET#ANG #ANG+30
ENDLOOP #ANG<=180
```

### 9.2 IF / ELSEIF / ELSE / ENDIF

The block is executed if the expression is **greater than zero**. There is no `GOTO`.

```
IF (#A<0.3)
  LET#VAL 0.50
ELSEIF (#A>1.0)
  LET#VAL 0.70
ELSE
  LET#VAL 0.50+0.20*(#A-0.3)
ENDIF
```

- Use relational expressions (`#N==12`, `ABS(#A-0.35)<0.001`).
- Version-dependent input: `IF (#VERSION>=2024)`.

---

## 10. Reserved Variables

| Variable | Content |
|----------|---------|
| `#PI` | 3.141593 (preset) |
| `#VERSION(0..2)` | Release version, service pack, intermediate release |
| `#GRP_MASS`, `#SCT_MASS`, `#MAT_MASS` | Masses per group / section / material after system statistics; index 0 = total |
| `#GRP_REIN`, `#SCT_REIN` | Reinforcement per group / section; index 0 = total |
| `#ASE_ITER(0..2)` | ASE: first LC, last LC, last achieved load factor |
| `#AQB_USAGE` | AQB: usage factors of the design tasks of the last input block |
| `#OPT_*` | Reserved for OPTIMA |
| `#CDB_IER`, `#CDB_LEN` | Database access status (§11) |
| `#COOR_X(n)`, `#COOR_Y(n)`, `#COOR_Z(n)` | Nodal coordinates (§11) |
| `#0` | Used by `DBG#` |

Program-generated variables start with the first three letters of the program and an underscore — do not use this pattern for own variables.

---

## 11. Reading from the Database (@CDB, @KEY, @())

Values from the project database (results of earlier blocks) can be read into variables. The record names (KWH) and item names come from the CDBASE description (`cdbase.chm`). **Never guess record or item names** — use only names given by the user or known from the documentation.

| Syntax | Meaning |
|--------|---------|
| `@CDB filename` | Select another database `filename.cdb`. Default: the project database (it may not be selected explicitly). |
| `@KEY KWH [KWL SEL1 … SEL6 IERR]` | Select a record index, e.g. `@KEY SECT_EFF 5`. Unused selectors = `-1`. |
| `@(name)`, `@(no,name)` | Read item `name` from the next record matching the key (`no` = value of the last selector). |
| `LET#v KWL(key)` | Array of all defined KWL numbers of a key, e.g. `KWL(MAT)`, `KWL(SECT)`, `KWL(LC_CTRL)`, `KWL(GPT)`, `KWL(GLN)`, `KWL(GAR)`, `KWL(DSLN_DEF)` |
| `LIT(@item)` | Read a text item |

- `#CDB_IER` (if defined ≥ 0) receives the status instead of an error message: 0 = ok, 1 = record too short, 2 = end of file, 3 = key not defined. `#CDB_LEN` receives the record length. Define `LET#CDB_IER 0` before loops over records to avoid an infinite loop.
- `#COOR_X(n)`, `#COOR_Y(n)`, `#COOR_Z(n)` give nodal coordinates in modules that initialise the nodes (SOFILOAD, ASE, …) — not in SOFIMSHC during its own input.

```
@KEY SECT_EFF 5                     $ effective Iy of section 5
LET#IY @(IY)

@KEY LC_CTRL 101                    $ action and title of load case 101
LET#ACT LIT(@ITYP)
LET#TXT LIT(@RTEX)

LET#MATS KWL(MAT)                   $ list all materials
LOOP#M MATS
  TXB #MATS(#M)
ENDLOOP

LET#CDB_IER 0                       $ loop over all support reactions of LC 12
@KEY N_DISP 12
LOOP
  LET#R @NR,@PX,@PY,@PZ
  IF (#CDB_IER<2)&(#R<>0)
    ...
  ENDIF
ENDLOOP #CDB_IER<2
```

---

## 12. Debugging

| Command | Effect |
|---------|--------|
| `PRT#name` | Print a variable (name directly after `#`) |
| `DBG#0` | No test output |
| `DBG#1` | Print the generated input records |
| `DBG#2` | Additionally print all value assignments |
| `DBG#3` | Additionally print selected CDB structures |
| `DBG#-2` | Stop the program run immediately |

`DBG#4`/`DBG#8` (console output / interactive input) are for interactive use only — do not write them into generated files.

---

## 13. Common Pitfalls

1. **`LET#` across blocks** — a `LET#` variable is lost at `END`. Use `STO#` for anything a later block needs.
2. **Blank after `#` or inside an expression** — `LET# A 5` and `X #A + 2` are wrong; write `LET#A 5`, `X #A+2`.
3. **Wrong function names** — `SQR` (not `SQRT`), `ATN` (not `ATAN`), `LGT` (not `LOG10`), `DIV` (not `INT`).
4. **Unitless parameters used in blocks with different default units** — give dimensional `STO#` parameters an explicit unit.
5. **Loop over an array with `#`** — `LOOP#I A`, not `LOOP#I #A`.
6. **Loop index starts at 0** — entity numbers are usually `#I+1`.
7. **Exact comparison of fractional values** — use `ABS(#A-x)<tol`.
8. **Expressions across lines** — `$$` cannot split an expression or a list.
9. **Unparenthesised logical expressions** — all logical operators have equal precedence.
10. **Parameters in AQUA instead of TEMPLATE** — for parametric files, all project parameters belong in the leading `+PROG TEMPLATE` block.
