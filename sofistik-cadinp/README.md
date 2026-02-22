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

ASE (analysis), DECREATOR, BEAM, COLUMN, and BEMESS modules are planned but not yet documented.

## Repository structure

```
sofistik-cadinp/
├── README.md                   ← this file
├── SKILL.md                    ← entry point — module registry and output rules
├── MASTER_HANDOVER.md          ← session history, lessons learned, how to extend
├── CADINP_LANGUAGE_RULES.md    ← CADINP syntax rules (global)
├── ERR_FILE_FORMAT.md          ← .err source file format reference
├── journal.txt                 ← development log
└── modules/
    ├── AQUA.md                 ← materials & sections (811 lines)
    ├── SOFIMSHC.md             ← structural model & meshing (1318 lines)
    └── SOFILOAD.md             ← actions & loads (1263 lines)
```

## How to use

1. Add this folder as a Claude skill (e.g. via the project knowledge or skill upload mechanism).
2. Ask Claude to generate a SOFiSTiK input file for your structure.
3. Claude will read `SKILL.md`, identify the required modules, load the relevant `.md` files, and produce a `.dat` file.

## How to extend

See `MASTER_HANDOVER.md` for detailed instructions on adding new modules from SOFiSTiK `.err` source files. Use `AQUA.md` as the structural template for new module files.

## Design code support

The skill supports all design codes available in SOFiSTiK, including Eurocodes with national annexes (DIN, BS, OEN, SIA, etc.), US codes (ACI, AISC), and others. The `NORM` command in `AQUA.md` documents all DC/NDC combinations.

## License

This skill is provided as-is for use with Anthropic's Claude. SOFiSTiK is a registered trademark of SOFiSTiK AG.
