# SOFiSTiK Skills for Claude

A collection of Claude skills for working with [SOFiSTiK](https://www.sofistik.com/) structural engineering software. Each skill is a self-contained folder of Markdown reference files — plus, where useful, helper scripts and starter templates — that Claude reads before performing a task, ensuring correct syntax, valid parameters, and professional-quality output.

## Skills

| Skill | Folder | Description |
|-------|--------|-------------|
| **CADINP File Generation** | [`sofistik-cadinp/`](sofistik-cadinp/) | Generate syntactically correct SOFiSTiK analysis input files in the CADINP language (`.dat` files). Covers materials & sections (AQUA), structural modelling & meshing (SOFIMSHC), load definition (SOFILOAD), linear/nonlinear/eigenvalue/dynamic analysis (ASE), design element creation (DECREATOR), and RC design checks for beams (BEAM), columns (COLUMN), and slabs (BEMESS). |
| **Revit Dynamo Script Generation** | [`sofistik-dynamo/`](sofistik-dynamo/) | Build Revit Dynamo scripts (`.dyn`) for Revit 2026 / Dynamo 3.6 that evaluate or modify Revit models and read SOFiSTiK FEA results via the SOFiSTiK Analysis + Design Dynamo package. Includes a Python builder library, a quick-reference for the SOFiSTiK Zero-Touch nodes, runnable starter templates, and built-in lints for the Revit 2024+ `ElementId.Value` / `UnitTypeId` API and SOFiSTiK ↔ Revit unit conversions. |
| **Rhino / Grasshopper CDB Access** | [`sofistik-rhino-cdb/`](sofistik-rhino-cdb/) | Write C# scripts for the Grasshopper C# Script component and the Rhino script editor that read a SOFiSTiK CDB (`.cdb`) through the `SOFiSTiK.Analysis.Database` assembly shipped with the SOFiSTiK Rhino Interface (2026 and newer). Covers mesh and beam geometry, nodal displacements and support reactions, beam and quad forces and stresses, cross-section polygons, tendons and axes. Includes a generated KWH/KWL → type index for the whole database, a units reference covering the CDB ↔ Rhino document-unit boundary, and starter templates for both scripting hosts. Plans each script for approval before writing any C#. |

## How to add a skill to Claude

### Claude Desktop or claude.ai — Customize menu (recommended)

The simplest way to use a skill. Works identically on Claude Desktop and claude.ai, on all plans (Free, Pro, Max, Team, Enterprise). Skills require **code execution** to be enabled in your settings.

1. Download the skill folder (e.g. `sofistik-cadinp/`, `sofistik-dynamo/`, or `sofistik-rhino-cdb/`) and package it as a **ZIP file**. The skill folder must be the root of the archive — i.e. the ZIP contains `sofistik-cadinp/SKILL.md`, not `some-wrapper/sofistik-cadinp/SKILL.md`.
2. In Claude, open **Customize → Skills**.
3. Click the **+** button, choose **Create skill**, then **Upload a skill**, and select the ZIP file.
4. The skill appears in your skills list — toggle it on or off as needed.

That's it. Claude automatically detects when the skill is relevant based on the `description` in the YAML frontmatter of `SKILL.md` and loads the appropriate module files.

> **Updating:** To update a skill, remove the old one and upload the updated ZIP again.

> **Team / Enterprise:** Organization Owners can provision skills for all users so that individual team members don't need to add skills themselves.

### Claude Code

Place the skill folder — keeping its own name, with `SKILL.md` directly inside it — in one of these locations:

| Scope | Path | Available in |
|-------|------|--------------|
| Personal | `~/.claude/skills/sofistik-cadinp/SKILL.md` | all your projects |
| Project | `.claude/skills/sofistik-cadinp/SKILL.md` | that project only (commit it to share with the team) |

Claude Code discovers skills from these locations automatically — no install command. It also watches them, so adding or editing a skill takes effect in the running session; only creating a top-level `skills/` directory that didn't exist at startup requires a restart.

Claude loads a skill on its own when the task matches its `description`, or you can invoke it explicitly by name, e.g. `/sofistik-cadinp`.

### General tips

- Each skill folder is self-contained — you only need the files inside it.
- `SKILL.md` is always the entry point. Claude reads it first, then loads the specific module files needed for the task.
- Skills can be combined. `sofistik-cadinp` generates the analysis input; `sofistik-rhino-cdb` and `sofistik-dynamo` read the results back out into Rhino/Grasshopper and Revit respectively. Any combination can be active in the same conversation when a workflow spans several of these stages.
- Skills that ship helper scripts (`sofistik-dynamo`, `sofistik-rhino-cdb`) need Python available in the environment running Claude. The generated scripts themselves have no Python dependency.

## Notes on `sofistik-rhino-cdb`

- **Requires the SOFiSTiK Rhino Interface at runtime.** `SOFiSTiK.Analysis.Database.DataAccess` is provided by that plug-in and is not available from a plain Rhino or SSD installation.
- **Regenerating the type index.** After a SOFiSTiK version upgrade, run `python scripts/build_type_index.py <path-to>/SOFiSTiK.Analysis.Database.xml` to rebuild `references/cdb_type_index.md` from the new assembly documentation.

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
