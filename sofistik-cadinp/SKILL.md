---
name: sofistik-cadinp
description: >
  Generate syntactically correct SOFiSTiK structural analysis input files in the
  CADINP language (.dat files). Covers materials and sections (AQUA), structural
  modelling and meshing (SOFIMSHC), load definition (SOFILOAD), linear,
  nonlinear, eigenvalue and dynamic analysis (ASE), superposition and envelopes
  of load cases (MAXIMA), RC/steel/timber cross-section design (AQB), and member
  and slab design (DECREATOR, BEAM, COLUMN, BEMESS). Use this skill whenever the
  user asks to create, edit, or review SOFiSTiK input, or mentions .dat files,
  CADINP, or SOFiSTiK FEA.
---

# SOFiSTiK CADINP Input File Generation Skill

## Purpose
This skill enables Claude to generate syntactically correct SOFiSTiK input files in the CADINP language format (*.dat). Files produced by this skill can be executed directly in SOFiSTiK Analysis Software.

## How to use this skill
Before generating any input file:
1. Read this master file fully.
2. Identify which analysis modules are required for the requested task (see Module Registry below).
3. Load **only the relevant module sub-files** from the `modules/` directory.
4. Apply the CADINP language rules from `CADINP_LANGUAGE_RULES.md` throughout the entire file.

**Always read `CADINP_LANGUAGE_RULES.md` before writing any input file — language rules apply globally.**

## Mandatory Pre-Flight Protocol

Before writing ANY line of CADINP input, Claude MUST complete the following steps in order.
Skipping or partially reading any step is not permitted.

0. **Clarify the workflow with the user when design or load combinations are involved.**
   - If the task needs load case combinations (any ULS/SLS verification, any design module),
     **ask the user how the superposition load cases shall be built** — see
     *Superposition Strategy* below. Do not choose silently.
   - If the task is a section design (AQB), ask whether it is a **stand-alone section design**
     with given internal forces (AQUA + AQB) or a **section design on a full system**
     (AQUA + SOFIMSHC + SOFILOAD + ASE + combinations + AQB), unless the request makes this obvious.
   - Skip a question only if the user has already answered it explicitly in the request.

1. **Read `CADINP_LANGUAGE_RULES.md` in full.**
   Confirm: unit annotation rules, continuation marker `$$`, sub-record indentation,
   NO uniqueness rule, strict parameter compliance rule, and common pitfalls list.

2. **Read every required module file in full** (as determined by the Module Selection Guide),
   and `SUPERPOSITION_STRATEGY.md` whenever load case combinations are involved.
   For each module, confirm before moving on:
   - All command syntaxes and parameter tables for commands you will use
   - All sub-record rules (e.g. SLNS for line supports, SARB boundary-only role)
   - All typical usage examples
   - All warning/note blocks (marked with `>`)

3. **Plan the complete file structure before writing.**
   List every `+PROG` block, every entity (SPT, SLN, SAR, LC, …), and every
   support/load condition. Verify cross-references are consistent before writing.

4. **Write the file strictly from the parameter tables.**
   Never use a parameter that does not appear in the parameter table of that command.
   Never transfer parameters between commands based on similarity.
   Never guess — if unsure, re-read the relevant module section.

5. **Self-review before submitting.**
   Check every command against its parameter table one final time.
   Verify: correct NORM pairing, supports via SLNS not SARB FIX, units annotated,
   urs sequence gapless, all +PROG blocks closed with END.

---

## Module Registry

Each module is a `+PROG` block in the generated file. Load only the sub-files needed.

| Module Name   | Sub-file                        | Purpose                                             | Required for                                      |
|---------------|---------------------------------|-----------------------------------------------------|---------------------------------------------------|
| AQUA          | `modules/AQUA.md`               | Materials, cross-sections, section properties       | Any structural analysis                           |
| SOFIMSHC      | `modules/SOFIMSHC.md`           | Structural model geometry, meshing                  | Any structural analysis                           |
| SOFILOAD      | `modules/SOFILOAD.md`           | Actions, load cases, load application               | Any analysis with external loads                  |
| ASE           | `modules/ASE.md`                | Linear/non-linear FEM analysis of load cases        | All load case analysis                            |
| MAXIMA        | `modules/MAXIMA.md`             | Automatic superposition / envelopes of linear load cases per design code | Linear workflows with code combinations (user choice, see Superposition Strategy) |
| DECREATOR     | `modules/DECREATOR.md`          | Design element creation for beam/column members     | RC beam/column design checks                      |
| AQB           | `modules/AQB.md`                | Cross-section design: RC reinforcement (bending, axial force, shear), crack width, stresses, steel/timber section checks | RC/steel/timber section design — stand-alone or on beam members of a full system |
| BEAM          | `modules/BEAM.md`               | RC beam design checks (bending, shear, reinforcement) | RC beam design                                 |
| COLUMN        | `modules/COLUMN.md`             | RC column design checks (axial + biaxial bending)   | RC column design                                  |
| BEMESS        | `modules/BEMESS.md`             | RC slab design checks (area reinforcement)          | RC slab design                                    |

> Additional modules will be added in subsequent steps (e.g., DYNA for dynamics).

---

## Module Selection Guide

Use the following decision logic to select the required modules:

```
Any model          → AQUA + SOFIMSHC
Has external loads → + SOFILOAD
Static analysis    → + ASE
Load combinations  → ask the user (see Superposition Strategy):
                       automatic envelopes (linear)      → + MAXIMA (after ASE)
                       explicit combination load cases   → SOFILOAD LC ... TYPE (D) + COPY, analysed in ASE
RC/steel section design, forces given     → AQUA + AQB
RC/steel section design on a full system  → AQUA + SOFIMSHC + SOFILOAD + ASE + (MAXIMA) + AQB
RC beam design     → + DECREATOR + BEAM
RC column design   → + DECREATOR + COLUMN
RC slab design     → + BEMESS
```

Note: DECREATOR is required before BEAM or COLUMN, as it creates the design elements those modules operate on. BEMESS works directly on mesh elements from SOFIMSHC and does not require DECREATOR. AQB designs beam elements directly (or DECREATOR design elements with `BEAM TYPE DSLN`); it does not design QUAD elements — use BEMESS for slabs and walls.

---

## Superposition Strategy (mandatory question)

**Before generating any file that needs load case combinations, ask the user which method to use** and state the recommendation:

> *"How should the load case combinations be built? (A) Automatic superposition of linear results with MAXIMA according to the design code — recommended for linear analysis; or (B) explicit combination load cases defined in SOFILOAD and analysed in ASE — required for non-linear analysis."*

Once the user has chosen, read **`SUPERPOSITION_STRATEGY.md`** in full (option details, combination types for the design modules, load case numbering, code fragments).

---

## Output File Structure

A complete SOFiSTiK input file follows this structure:

```
!*** File header / description block ***

+PROG AQUA urs:1        ← always first: materials & sections
...
END

+PROG SOFIMSHC urs:2    ← structural geometry
...
END

+PROG SOFILOAD urs:3    ← loads (if applicable); explicit combination LCs for option B
...
END

+PROG ASE urs:4         ← FEM analysis (if applicable)
...
END

+PROG DECREATOR urs:5   ← design elements for beams/columns (if applicable)
...
END

+PROG MAXIMA urs:6      ← automatic superposition / envelopes (option A only)
...
END

+PROG AQB urs:7         ← cross-section design (if applicable)
...
END

+PROG BEAM urs:8        ← RC beam design checks (if applicable)
...
END

+PROG COLUMN urs:9      ← RC column design checks (if applicable)
...
END

+PROG BEMESS urs:10     ← RC slab design checks (if applicable)
...
END
```

> DECREATOR must precede MAXIMA only when MAXIMA superposes design element results (`SUPP ... ETYP DSLN`); otherwise MAXIMA may follow ASE directly.
> A stand-alone section design consists only of `+PROG AQUA urs:1` and one or more `+PROG AQB` blocks with forces defined by `S`.

Only include the modules relevant to the task. The `urs:n` counter must always be sequential with no gaps — renumber accordingly when modules are omitted.

---

## General Output Quality Rules

- Always include a descriptive file header using `!` comment lines.
- Always include a `HEAD` line after each `+PROG` declaration.
- Use `!*!Label <text>` annotations to group logically related commands within a module.
- Use `$` inline comments to explain non-obvious parameter choices.
- Always use explicit unit annotations. Apply the following conventions without exception:
  - `[m]` — all general geometry: node coordinates, span lengths, member lengths
  - `[mm]` — cross-sectional geometry (height, width, flange thickness, diameter, wall thickness) and slab/plate thickness parameters
  - `[kN]` — point loads; `[kN/m]` — line loads; `[kN/m2]` — area loads
  - `[cm2]` — reinforcement cross-sectional areas
- Number IDs consistently: use simple integers for small models, grouped integers (e.g., 1xx, 2xx) for complex models with distinct structural families.
- Always include the SOFIMSHC control block (`CTRL MESH`, `CTRL HMIN`, `CTRL TOLG`) in every generated model — it is part of the mandatory template.
- In `SYST 3D` beam-only models, restrain out-of-plane translation (PY) and torsional rotation (MX) at all supports to prevent rigid-body instability. Use `FIX PPMX` for pinned supports, `FIX PZPYMX` for roller supports.
- Reinforcing and prestressing steel `CLAS` values do not include the TYPE prefix — use numeric grade only (e.g. `CLAS 500A`, `CLAS 500B` for rebar; `CLAS 1860S7`, `CLAS 1050` for prestressing). The letter belongs in `TYPE B`/`TYPE Y`/`TYPE YC`, not in `CLAS`.
- Truss members should be modelled as standard beam elements with moment releases at both ends (`SLN ... FIXA MYMZ FIXE MYMZ`), not as truss elements (`STYP T`). This preserves full beam output (shear, moments from self-weight) and avoids numerical issues with pure truss formulations. Use `STYP T` only if the user explicitly requests true truss elements.
- Use the `$$` line continuation marker only when a single record exceeds 100 characters. Keep shorter commands on one line. Do not use `$$` between a parent command and its sub-records (e.g. `SLN` → `SLNB`, `SAR` → `SARB`/`SARR`).
