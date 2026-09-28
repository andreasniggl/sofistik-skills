# sofistik-cadinp

A Claude skill for generating syntactically correct SOFiSTiK structural analysis input files in the CADINP language (`.dat` files).

## What it does

When loaded as a skill, Claude reads the reference files in this folder before writing any SOFiSTiK input — ensuring the generated `.dat` files are syntactically correct and immediately executable in SOFiSTiK FEA.

## Supported modules

| Module | File | Description |
|--------|------|-------------|
| AQUA | `modules/AQUA.md` | Materials and cross-sections |
| SOFIMSHC | `modules/SOFIMSHC.md` | Structural model geometry and meshing |
| SOFILOAD | `modules/SOFILOAD.md` | Actions, load cases, and load application |
| ASE | `modules/ASE.md` | Linear, nonlinear, eigenvalue, and dynamic analysis |
| MAXIMA | `modules/MAXIMA.md` | Superposition and envelopes of linear load cases per design code |
| DECREATOR | `modules/DECREATOR.md` | Design element creation for beam/column members |
| AQB | `modules/AQB.md` | Cross-section design: RC reinforcement, crack width, stresses, steel/timber checks |
| BEAM | `modules/BEAM.md` | RC beam design checks (bending, shear, reinforcement) |
| COLUMN | `modules/COLUMN.md` | RC column design checks (axial + biaxial bending) |
| BEMESS | `modules/BEMESS.md` | RC slab design checks (area reinforcement) |

## Repository structure

```
sofistik-cadinp/
├── README.md                   ← this file
├── SKILL.md                    ← entry point — module registry and output rules
├── MASTER_HANDOVER.md          ← session history, lessons learned, how to extend
├── CADINP_LANGUAGE_RULES.md    ← CADINP syntax rules (global)
├── SUPERPOSITION_STRATEGY.md   ← MAXIMA vs. SOFILOAD combinations, LC numbering, fragments
├── ERR_FILE_FORMAT.md          ← .err source file format reference
├── journal.txt                 ← development log
└── modules/
    ├── AQUA.md                 ← materials & sections (814 lines)
    ├── SOFIMSHC.md             ← structural model & meshing (1323 lines)
    ├── SOFILOAD.md             ← actions & loads (1312 lines)
    ├── ASE.md                  ← analysis engine (910 lines)
    ├── MAXIMA.md               ← superposition & envelopes (799 lines)
    ├── DECREATOR.md            ← design element creation (725 lines)
    ├── AQB.md                  ← cross-section design (1189 lines)
    ├── BEAM.md                 ← RC beam design (785 lines)
    ├── COLUMN.md               ← RC column design, NCM (645 lines)
    └── BEMESS.md               ← RC slab/shell design (784 lines)
```

## How to use

1. In Claude, open the **Customize** menu (click the sliders icon in the bottom-left of the chat window).
2. Under **Skills**, click **Add skill** and select this folder (`sofistik-cadinp/`). Claude will detect the `SKILL.md` entry point automatically.
3. Ask Claude to generate a SOFiSTiK input file for your structure.
4. Claude will read `SKILL.md`, identify the required modules, load the relevant `.md` files, and produce a `.dat` file.

## How to extend

See `MASTER_HANDOVER.md` for detailed instructions on adding new modules from SOFiSTiK `.err` source files. Use `AQUA.md` as the structural template for new module files.

## Design code support

The skill supports all design codes available in SOFiSTiK, including Eurocodes with national annexes (DIN, BS, OEN, SIA, etc.), US codes (ACI, AISC), and others. The `NORM` command in `AQUA.md` documents all DC/NDC combinations.

## License

This skill is provided as-is for use with Anthropic's Claude. SOFiSTiK is a registered trademark of SOFiSTiK AG.
