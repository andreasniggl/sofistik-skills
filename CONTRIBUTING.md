# Contributing — Extending the SOFiSTiK Skills

Contributions are welcome. This guide focuses on the most common request: **adding a new SOFiSTiK module to the `sofistik-cadinp` skill** (e.g. DYNA, TENDON, CSM, TALPA, BDK, …). The same principles — source everything from official documentation, never invent syntax, validate in SOFiSTiK — apply to the other skills as well.

You do **not** need access to SOFiSTiK internals. Everything described here works with a regular SOFiSTiK installation and its official PDF manuals.

---

## 1. How the `sofistik-cadinp` Skill Works

```
sofistik-cadinp/
├── SKILL.md                    ← entry point: module registry, selection guide, mandatory questions, output rules
├── CADINP_LANGUAGE_RULES.md    ← global CADINP syntax rules (units, comments, continuation, variables)
├── SUPERPOSITION_STRATEGY.md   ← how load case combinations are built (MAXIMA vs. SOFILOAD)
├── ERR_FILE_FORMAT.md          ← how to read SOFiSTiK *.err files (the syntax source)
└── modules/
    ├── AQUA.md, SOFIMSHC.md, SOFILOAD.md, ASE.md, MAXIMA.md,
    └── DECREATOR.md, AQB.md, BEAM.md, COLUMN.md, BEMESS.md
```

When Claude generates an input file it reads `SKILL.md`, selects the required modules, reads `CADINP_LANGUAGE_RULES.md` and **only** the relevant `modules/*.md` files, and writes the `.dat` file strictly from the parameter tables in those files.

Consequence for contributors: **a module file is a contract.** Claude will use exactly the commands, parameters, enum values and defaults written there — no more, no less. Any error in a module file becomes an error in every generated input file.

---

## 2. What You Need

| Source | Where to find it | What it provides |
|--------|------------------|------------------|
| **`<module>.err` file** | In the program directory of your SOFiSTiK installation (search for `*.err`, e.g. `aqb.err`, `dyna.err`) | The authoritative, complete command syntax: all commands, parameter names and order, enum values, unit/default codes |
| **PDF manual of the module** | Installed with SOFiSTiK (documentation folder / help) or from the SOFiSTiK online documentation. Use the **English** version (typically suffix `_1`, e.g. `aqb_1.pdf`) | Meaning of every parameter, defaults, behavioural rules, examples. The relevant chapter is usually called *"Description of Input"* / *"Input Description"* |
| **Example files** | Tutorials and examples shipped with the installation, or your own verified projects | Realistic usage patterns to cross-check the module file |
| **A SOFiSTiK licence** | — | To **run** the examples you write and prove they work |

> **Copyright:** The `.err` files, PDF manuals and example files are SOFiSTiK property. **Do not commit them to this repository.** Module files must be your own structured summary of the syntax, not copied manual text. Keep them in a local working folder only.

Read `sofistik-cadinp/ERR_FILE_FORMAT.md` before you start — it explains how to read the `.err` file.

---

## 3. Step-by-Step: Adding a New Module

### Step 1 — Check the scope

- Is the module needed often enough to justify a file? (Rule of thumb: it appears as its own `+PROG` block in typical workflows.)
- Where does it sit in the workflow? Decide its position in the canonical module order (see `CADINP_LANGUAGE_RULES.md` §1.2) and which modules must run before it.
- Open an issue first if you are unsure — it avoids duplicate work.

### Step 2 — Extract the syntax from the `.err` file

The `.err` file is the **single source of truth for syntax**. From it, collect for every command:

| `.err` line | Gives you |
|-------------|-----------|
| `-20 CMD  …` (and `-*0` continuation lines) | English command name and **all parameter names in order** |
| `-*2` / `-22` | Unit and default codes, column-aligned with the parameter line |
| `-21n` / `-*1n` | Enum literals for the parameter at position `n` (1–9, then A–Z) |
| `-27` | Human-readable syntax summary |

Rules:
- Always use the **English** names (`-2x` lines), never the German `-1x` names.
- Take enum values **exactly** as written in the `.err` file — never from memory or general knowledge (e.g. `NDC 199X-200X`, not `EN1992-2004`).
- Parameters that exist in the `.err` file but are **not described** in the manual: list them with the note *"not documented — do not use"* instead of guessing a meaning.

### Step 3 — Take meanings and rules from the PDF manual

For every command, read the input description in the PDF manual and add:
- a one-line description per parameter, its unit and default,
- the meaning of each enum value,
- behavioural rules, restrictions and interactions with other commands (these become `>` note blocks),
- when the command is required, optional or mutually exclusive with others.

Where the manual and the `.err` file disagree on a name or enum, **the `.err` file wins** for syntax; note the discrepancy in the file.

### Step 4 — Write the module file

Create `sofistik-cadinp/modules/<MODULE>.md` following the structure standard in §4. Use `modules/AQUA.md` (materials/sections), `modules/AQB.md` (design module) or `modules/MAXIMA.md` (post-processing module) as structural references.

### Step 5 — Validate the examples

This is the step that makes the skill reliable:

1. **Parameter check:** every parameter used in every example (typical usage and complete example) must exist in that command's parameter table. Remove anything that does not.
2. **Run it:** assemble a complete input file (AQUA → … → your module) from the skill, run it in SOFiSTiK (SSD / Teddy) and check that it runs **without errors**, and without warnings you cannot explain.
3. **Cross-check with official examples:** compare your module file against at least one tutorial/example of the module. Everything the example does should be expressible with your file — if not, the file is incomplete or wrong.
4. **Test with Claude:** install your modified skill (see `README.md`), ask Claude for a typical task of the new module, run the result in SOFiSTiK. Fix the module file — not the generated input — until the output runs.

### Step 6 — Register the module

| File | What to update |
|------|----------------|
| `sofistik-cadinp/SKILL.md` | `description` in the YAML frontmatter (mention the module), **Module Registry** table, **Module Selection Guide**, **Output File Structure** (block position) |
| `sofistik-cadinp/CADINP_LANGUAGE_RULES.md` | Canonical module order (§1.2) |
| `sofistik-cadinp/README.md` | *Supported modules* table and repository structure |
| `README.md` (repository root) | Skill description in the *Skills* table |
| Other modules | Cross-references where workflows connect (e.g. "Prerequisites", "Load this file when") |

If the module needs a decision from the user (like the superposition strategy for MAXIMA), add it as a **mandatory question** in the *Pre-Flight Protocol* of `SKILL.md` — keep it short there and move details into a separate topic file.

### Step 7 — Open a pull request

See the checklist in §7.

---

## 4. Module File Structure Standard

Every module file follows this structure. **Do not deviate** — Claude relies on it to find information.

### File header

````markdown
# Module: <NAME> — <Title>

## Purpose
<one paragraph: what the module does, what it reads from / writes to the database>

## Load this file when
<one line: the user request that triggers this module>

## Prerequisites
<modules that must run before, and what they must provide>

## Module block template
```
+PROG <NAME> urs:<n>
HEAD <description>

!*!Label <Group>
...

END
```

> **Key rules:**
> - <the 3–8 rules that most often cause errors>
````

### Commands index

```markdown
## Commands

| Command | Purpose |
|---------|---------|
| `CMD`   | One-line description |
```

### Each command

````markdown
### CMD — Short Title

One-sentence purpose.

**Syntax:**
```
CMD PARAM1 PARAM2 PARAM3 ...
```

| Parameter | Type   | Unit     | Default | Description |
|-----------|--------|----------|---------|-------------|
| `PARAM1`  | int    | —        | 1       | ... |
| `PARAM2`  | float  | `[m]`    | `*`     | ... |
| `PARAM3`  | enum   | —        | —       | ... |

**PARAM3 — <enum name>:**

| Value | Meaning |
|-------|---------|
| `A`   | ... |

> Notes as blockquotes — behavioural rules, warnings, cross-references.

**Typical usage:**
```
$ comment
CMD ...
```
````

### Footer

````markdown
## Complete <NAME> Block Example

```
+PROG <NAME> urs:1
HEAD ...
...
END
```

## Unit Summary for <NAME>

| Quantity | Unit | Parameters |
|----------|------|------------|
| ...      | ...  | ...        |
````

### Parameter table conventions

| Field | Allowed values |
|-------|----------------|
| Type | `int`, `float`, `enum`, `string` (combinations like `int/enum` allowed) |
| Unit | `[m]`, `[mm]`, `[kN]`, `[kN/m]`, `[kN/m²]`, `[kNm]`, `[N/mm²]`, `[°]`, `[‰]`, `[%]`, `[cm²]`, `[-]` (dimensionless factor), `—` (no unit) |
| Default `*` | Code-derived or program default — do not specify unless overriding |
| Default `—` | Required — no default exists (the manual marks these with `!`) |

---

## 5. Quality Rules (Lessons Learned)

These rules come from real errors found while building the existing modules:

| Rule | Example of the error it prevents |
|------|----------------------------------|
| **Never add a parameter that is not in the `.err` file** — not even an "obvious" one | `PROF ... TITL` fails: PROF has no `TITL` |
| **Take enum and string values verbatim from the `.err` file** | `NORM ... NDC EN1992-2004` fails — correct is the wildcard `199X-200X` |
| **Use English (`-20`) names only** | `FACH` is the old German name of the truss type |
| **Check literal formats of class values in examples** | `STEE TYPE B CLAS B500A` fails — correct is `CLAS 500A` |
| **Prefer explicit forms over shortcuts** if the manual offers both | Write `FIX PZPYMX`, not combined shortcuts |
| **Document hidden dependencies between modules** as `>` notes | MAXIMA `SUPP ETYP BEAM TYPE UZ` needs `ECHO BDEF EXTR` in ASE |
| **Document physical/engineering restrictions**, not only syntax | MAXIMA superposition is invalid for non-linear results |
| **Mark undocumented `.err` options as "do not use"** instead of omitting or guessing them | — |
| **Every example must run in SOFiSTiK** | — |

If you discover a new pitfall while testing, add it as a `>` note in the affected module file so Claude sees it at generation time.

---

## 6. Working with Claude to Build a Module

Claude can do most of the drafting if you give it the right sources. A proven workflow:

1. Put the `.err` file and the **input-description chapter** of the English PDF manual into a local working folder (not the repository). Large PDFs: extract only the input-description pages — Claude reads PDFs in chunks of about 20 pages.
2. Open the repository with Claude (Claude Code or a Claude project with the files attached).
3. Use a prompt along these lines:

   > Read `CONTRIBUTING.md` and `sofistik-cadinp/ERR_FILE_FORMAT.md`. Then read `<module>.err` and the attached English manual chapter *Description of Input* of `<MODULE>`. Create `sofistik-cadinp/modules/<MODULE>.md` following the module file structure standard, using `modules/AQB.md` as reference. Take syntax, parameter order and enum values only from the `.err` file, meanings and rules only from the manual. Mark parameters that exist only in the `.err` file as "not documented — do not use". Finally check that every parameter used in the examples exists in its parameter table, and register the module in `SKILL.md`, `CADINP_LANGUAGE_RULES.md` and both READMEs.

4. Review the result yourself against the manual — Claude can misread tables in PDFs, especially multi-column parameter tables.
5. Run the examples in SOFiSTiK (Step 5) and feed any errors back to Claude with the error message from the SOFiSTiK output.

---

## 7. Pull Request Checklist

- [ ] New module file `sofistik-cadinp/modules/<MODULE>.md` follows the structure standard (§4)
- [ ] All syntax taken from the `.err` file, all meanings from the official manual; version of SOFiSTiK stated in the PR description
- [ ] Every parameter used in the examples exists in the corresponding parameter table
- [ ] Complete example was run in SOFiSTiK without errors (mention version and design code used)
- [ ] Module registered in `SKILL.md` (frontmatter, registry, selection guide, output structure)
- [ ] Module order updated in `CADINP_LANGUAGE_RULES.md`
- [ ] `sofistik-cadinp/README.md` and root `README.md` updated
- [ ] No `.err` files, PDF manuals or other SOFiSTiK-copyrighted files committed
- [ ] Existing modules not changed — or changes explained in the PR (corrections to existing files are very welcome, please describe the error found)

Contributions are licensed under the repository's [MIT License](LICENSE).
