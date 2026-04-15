# SOFiSTiK Skills for Claude

A collection of Claude skills for working with [SOFiSTiK](https://www.sofistik.com/) structural engineering software. Each skill is a self-contained folder of Markdown reference files that Claude reads before performing a task — ensuring correct syntax, valid parameters, and professional-quality output.

## Skills

| Skill | Folder | Description |
|-------|--------|-------------|
| **CADINP File Generation** | [`sofistik-cadinp/`](sofistik-cadinp/) | Generate syntactically correct SOFiSTiK analysis input files in the CADINP language (`.dat` files). Covers materials & sections (AQUA), structural modelling & meshing (SOFIMSHC), load definition (SOFILOAD), linear/nonlinear/eigenvalue/dynamic analysis (ASE), design element creation (DECREATOR), and RC design checks for beams (BEAM), columns (COLUMN), and slabs (BEMESS). |
| **Revit Dynamo Script Generation** | [`sofistik-dynamo/`](sofistik-dynamo/) | Build Revit Dynamo scripts (`.dyn`) for Revit 2026 / Dynamo 3.6 that evaluate or modify Revit models and read SOFiSTiK FEA results via the SOFiSTiK Analysis + Design Dynamo package. Includes a Python builder library, a quick-reference for the SOFiSTiK Zero-Touch nodes, runnable starter templates, and built-in lints for the Revit 2024+ `ElementId.Value` / `UnitTypeId` API and SOFiSTiK ↔ Revit unit conversions. |

## How to add a skill to Claude

### Claude Desktop or claude.ai — Customize menu (recommended)

The simplest way to use a skill. Works identically on Claude Desktop and claude.ai (requires a Pro, Max, Team, or Enterprise plan).

1. Download the skill folder (e.g. `sofistik-cadinp/` or `sofistik-dynamo/`).
2. In Claude, click the **Customize** icon (sliders icon in the bottom-left of the chat window).
3. Under **Skills**, click **Add skill** and select the skill folder. Claude will detect the `SKILL.md` entry point automatically.
4. The skill appears in your skills list — toggle it on or off as needed.

That's it. Claude automatically detects when the skill is relevant based on the `description` in the YAML frontmatter of `SKILL.md` and loads the appropriate module files.

> **Updating:** To update a skill, remove the old one and add the updated folder again.

> **Team / Enterprise:** Organization Owners can provision skills for all users so that individual team members don't need to add skills themselves.

### Claude Code

1. Place the skill folder in `~/.claude/skills/` or in your project directory.
2. Claude Code discovers skills automatically from these locations via the filesystem.

### General tips

- Each skill folder is self-contained — you only need the files inside it.
- `SKILL.md` is always the entry point. Claude reads it first, then loads the specific module files needed for the task.
- Skills can be combined. For example, `sofistik-cadinp` (input file generation) and `sofistik-dynamo` (Revit-side automation) can be active in the same conversation when a workflow spans both the analysis input and the Revit model.


## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
