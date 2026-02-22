# SOFiSTiK Skills for Claude

A collection of Claude skills for working with [SOFiSTiK](https://www.sofistik.com/) structural engineering software. Each skill is a self-contained folder of Markdown reference files that Claude reads before performing a task — ensuring correct syntax, valid parameters, and professional-quality output.

## Skills

| Skill | Folder | Description |
|-------|--------|-------------|
| **CADINP File Generation** | [`sofistik-cadinp/`](sofistik-cadinp/) | Generate syntactically correct SOFiSTiK analysis input files in the CADINP language (`.dat` files). Covers materials & sections (AQUA), structural modelling & meshing (SOFIMSHC), load definition (SOFILOAD), and linear/nonlinear/eigenvalue/dynamic analysis (ASE). |

## How to add a skill to Claude

### Claude Desktop or claude.ai — Skill upload (recommended)

The simplest way to use a skill. Works identically on Claude Desktop and claude.ai (requires a Pro, Max, Team, or Enterprise plan).

1. Download the skill folder as a `.zip` file (e.g. `sofistik-cadinp.zip`). The zip must contain the skill folder as its root, with `SKILL.md` inside it.
2. Open **Settings → Capabilities**.
3. Under **Skills**, click **Upload skill** and select the `.zip` file.
4. The skill appears in your skills list — toggle it on or off as needed.

That's it. Claude automatically detects when the skill is relevant based on the `description` in the YAML frontmatter of `SKILL.md` and loads the appropriate module files.

> **Updating:** To update a skill, re-zip the folder and upload it again. If the name matches an existing skill, it overwrites the previous version.

> **Team / Enterprise:** Organization Owners can provision skills for all users so that individual team members don't need to upload the zip themselves.

### Claude Desktop or claude.ai — Project knowledge (alternative)

If you prefer to use **Projects** instead of the skill upload:

1. Create a new **Project**.
2. Go to **Project Knowledge** and upload the files from the skill folder.
3. Optionally add a custom instruction such as:
   ```
   Before generating any SOFiSTiK input, read the SKILL.md file from the project knowledge.
   ```
4. Start a conversation within the project.

### Claude Code

1. Place the skill folder in `~/.claude/skills/` or in your project directory.
2. Claude Code discovers skills automatically from these locations via the filesystem — no `.zip` packaging needed.

### General tips

- Each skill folder is self-contained — you only need the files inside it.
- `SKILL.md` is always the entry point. Claude reads it first, then loads the specific module files needed for the task.
- Skills can be combined. For example, a future result-processing skill could work alongside `sofistik-cadinp` in the same conversation.


## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.