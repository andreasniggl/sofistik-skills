---
name: sofistik-rhino-cdb
description: Write C# scripts for the Grasshopper C# Script component or the Rhino script editor that read a SOFiSTiK CDB database (*.cdb) through the SOFiSTiK.Analysis.Database assembly - geometry, analysis results, cross sections, tendons and axes. Use this skill whenever the user wants to pull FEA data into Rhino or Grasshopper, mentions a .cdb file, DataAccess, ReadData, KWH/KWL keys, any Cdb* type (CdbNode, CdbBeam, CdbQuad, CdbN_disp, CdbBeam_for, CdbSect_ppt, ...), load cases, support reactions, beam forces, quad stresses, or the SOFiSTiK Rhino Interface. Trigger it even for partial requests like "get the support reactions into Grasshopper", "show me the deformed shape", "which KWH holds beam stresses" or "why is my displacement 1000x too small" - anything that ends in C# touching a CDB.
---

# SOFiSTiK CDB access from Rhino / Grasshopper C#

Read a `.cdb` with the managed `SOFiSTiK.Analysis.Database` assembly that ships
with the SOFiSTiK Rhino Interface, and turn the records into Rhino geometry and
flat lists. Targets **SOFiSTiK 2026 and newer**.

## The mental model

The CDB is an index-sequential store addressed by two integer keys:

- **KWH** - primary key. The category: nodes are 20, beams 100, beam forces 102,
  nodal results 24, quads 200.
- **KWL** - secondary key. Either a fixed number (usually 0 for model data) or,
  **for every result record, the load case number**.

`db.ReadData(kwh, kwl)` returns a heterogeneous `IEnumerable<ICdbElement>`,
because one key can hold several record types at once. `.OfType<T>()` is what
picks the one you want - it is load-bearing, not tidiness:

```csharp
// 100/0 holds BOTH beams and their section assignments
var beams    = db.ReadData(100, 0).OfType<CdbBeam>().ToList();
var sections = db.ReadData(100, 0).OfType<CdbBeam_sct>().ToList();
```

The type name tells you the mnemonic in the SOFiSTiK documentation:
`CdbBeam_for` is the `BEAM_FOR` record, `CdbN_disp` is `N_DISP`. Field names are
the documented item names in PascalCase - `UX` -> `Ux`, `SPAR` -> `Spar`,
`MNR` -> `Mnr`.

## Workflow

Not every request needs a script. "Which KWH holds beam stresses?", "what unit is
`Sigc` in?", "why is my displacement 1000x too small?" are answered from
`references/cdb_type_index.md`, `references/units.md` and
`scripts/lookup_record.py` directly - answer them and stop. The steps below are
for when the user wants code.

**No C# before the plan is approved.** Steps 1-3 are cheap and catch the
expensive mistakes - a record that does not hold what the user assumed, a unit
that is off by 1000, an output shape that does not fit what they want to do next.
Those are all far cheaper to fix in a five-line plan than in a written component
the user has already pasted into Grasshopper.

### 1. Capture intent

Ask only for what you cannot infer:

- **What is being read?** Forces, displacements, reactions, stresses, geometry,
  sections, tendons.
- **Which environment?** Grasshopper component or Rhino script editor. "In
  Grasshopper" or a mention of inputs and outputs means the component; "in
  Rhino", "as a command", or adding objects to the document means the editor.
- **What does the user do with the result?** Display it, tag it, colour it,
  export it, drive downstream geometry. This decides the output shape more than
  anything else.
- **Scoped to part of the model?** A group, a list of element ids, one load case
  or several.

If the request already answers these, go straight to step 2.

### 2. Find the record and confirm its fields

Look up the type and its KWH/KWL in `references/cdb_type_index.md`. The quick
table at the top covers most requests; grep the full index for anything else
(`grep -i tendon references/cdb_type_index.md`). Never read that file whole - it
is ~950 lines.

Then confirm the fields, before planning and before writing code:

```bash
python scripts/lookup_record.py CdbBeam_for     # or 102/LC, or BEAM_FOR
```

That prints the record's item table straight out of `cdbase.txt`, with the unit
code for every float. Decode the codes with `references/units.md`. This step takes
seconds and prevents the two most common failures: a property that does not exist
(the script will not compile) and a value that is silently 1000x off.

If a field still looks ambiguous, put that in the plan as an open question rather
than inventing a meaning.

### 3. Propose the plan, then stop

Write the plan in this format and **end the turn**. Do not write any C# yet.

```
## Plan: <script name>

**Job:** <one sentence>
**Environment:** Grasshopper C# component | Rhino script editor

**Reads**
- <KWH/KWL -> Type: what it provides>   e.g. 102/LC -> CdbBeam_for: N, Vy, Vz, My, Mz per output section
- <...>

**Inputs**
- <name (type): meaning>

**Outputs**
- <name: what it is, its length (per beam / per section / scalar), its unit>

**Units:** <what is stored, what the outputs will be in, any conversion applied>

**Assumptions:** <only the ones that could be wrong - eccentricity ignored,
Rhino document in metres, sign convention, which records get filtered out>

**Open questions:** <only if any>
```

Then ask whether it looks right before building.

Two things earn their place in almost every plan, because they are the ones that
come back as rework:

- **Output shape and length.** A per-element list and a per-section list cannot
  share one flat list. State which is which, and say what each output is *for*.
- **Units, explicitly.** "Displacements are stored in m; output in mm" is one
  line and settles the most common source of silent wrongness.

For anything large - several components, or a job the user calls tricky - offer a
TODO list in the plan and build it a step at a time rather than all at once.

### 4. Build it, after approval

Copy the right skeleton from `assets/templates/` rather than reconstructing it;
`references/environments.md` explains how the two differ and why. Follow
`references/recipes.md` for the record being read - it has a verified snippet, the
units, and the specific trap for each of the common ones.

Build what the plan said. If something in the plan turns out to be wrong while
writing, say so rather than silently substituting.

### 5. Deliver both ways

Print the full script in the response **and** save it as a `.cs` file in
`/mnt/user-data/outputs/`, then present it. The user pastes from chat when it is
small and opens the file when it is not. Name the file after what it does:
`Import_Beam_Forces.cs`, not `script.cs`.

Close with which inputs the component needs, what the outputs are, the units of
any numeric output, and any limitation worth knowing.

### Iterating on an approved script

Changes to a script the user has already accepted do not need the full plan
again. State the change in a line or two, confirm it if it affects the inputs,
outputs or units, then make it. A new script, or a change that turns it into a
different job, goes back through step 3.

## Rules that keep scripts working

These are the things that break a CDB script in ways that are slow to diagnose.

**Plan before code, every time.** The pull towards answering a well-specified
request by writing the script immediately is strong, and it is what produces
components with the wrong output shape. Step 3 exists to be used even when the
request seems complete enough to skip it.

**`#r "SOFiSTiK.Analysis.Database.dll"` by name, never by path.** The Rhino
Interface puts the DLL where the script host can find it. A hard-coded path
breaks on every other machine and on the next version upgrade.

**Keep `#r` inside the first ~31 lines.** The script host only scans the top of
the file for directives. Past that line the directive is ignored and the script
fails with *"the namespace SOFiSTiK could not be found"* - which reads like a
broken installation, not a layout problem. So the script's documentation header
goes **after** `#endregion`, immediately before `public class Script_Instance`,
never above the usings. This is a trap that scales the wrong way: the more a
component deserves explaining, the longer the header, the more likely it breaks.
Put only `// Grasshopper Script Instance` above `#region Usings`.

**Resolve the CDB path relative to the host document.** Take a `relPath` string
input and combine it with the Grasshopper document folder, or derive it from the
Rhino document name. Never bake in an absolute path. See
`references/environments.md` for both forms, including the unsaved-document guard.

**`GetSecondaryKeysOf(kwh)`, not `GetKeysOfKwh(kwh)`.** In 2026 only
`GetSecondaryKeysOf` exists. Use it to enumerate load cases:
`db.GetSecondaryKeysOf(102)` gives every load case with beam forces. Note that
some published SOFiSTiK examples use the other name; they target a later version.

**Check what `Open` returns.** It returns `bool`. A missing file, or a CDB still
locked by SSD or a running analysis, returns `false`, and every subsequent
`ReadData` comes back empty - which reads like "the model has no results" rather
than "the file never opened". Fail loudly instead.

**One process at a time.** The CDB is a single file with a single writer. If SSD
or an analysis has it open, Rhino cannot read it. Worth saying in the hand-off
when the user is iterating between analysis and Grasshopper.

**Numeric fields are `float`.** `Xyz`, `T`, `Dl`, `X`, `Y`, `Z`, forces, stresses
- all `Single`. Widen to `double` when you do maths on them, and never compare
them with `==`. `r.X == beam.Dl` fails on the beam where it matters most; use a
tolerance.

**Convert units deliberately, in two steps.** CDB storage units are metres,
kN, kNm, rad, kN/m2 - *not* what SOFiSTiK's dialogs display. Then, separately,
Rhino's document units may not be metres. `references/units.md` covers both.
Whichever you do, put the resulting unit in the output name or a comment.

**Read each key once.** `ReadData` hits the database; calling it inside a loop
over elements is what makes a component feel hung on a real model. Read into a
`List<T>` up front and index with `ToDictionary(x => x.Nr)`.

**Guard the joins.** Not every node has a result in every load case, and not
every referenced element exists. `Single()` and `First()` throw and take the whole
component down with a red bubble; prefer `TryGetValue` / `FirstOrDefault` with a
`continue`, or fail with a message that names the missing id.

## Reference files

- `references/cdb_type_index.md` - every KWH/KWL and the managed type it returns,
  generated from the assembly XML. Start here to find a record. Grep it.
- `references/units.md` - what each unit code means, what is actually stored
  versus what SOFiSTiK displays, and the Rhino document-unit boundary.
- `references/environments.md` - Grasshopper component vs Rhino script editor:
  boilerplate, path resolution, inputs and outputs, what differs and why.
- `references/recipes.md` - verified snippets per record type, with units and
  per-record traps. Read the relevant section before writing.
- `scripts/lookup_record.py` - field definitions for any record, out of the
  bundled `cdbase.txt`. Use it in step 2, every time.
- `scripts/build_type_index.py` - regenerates the type index from a newer
  `SOFiSTiK.Analysis.Database.xml` after a version upgrade.
- `assets/templates/` - `grasshopper_component.cs` and `rhino_script.cs`, ready
  to copy and fill in.

## Not this skill

Writing *to* the CDB (`WriteData`), building SOFiSTiK input with CADINP, or
driving the SOFiSTiK Grasshopper components themselves. This skill is about
reading a CDB from C#.

If the user wants CADINP input files, that is the `sofistik-cadinp` skill; for
Revit-side automation reading the same results, `sofistik-dynamo`. Both can be
active in the same conversation when a workflow spans analysis input and
post-processing. Say which one applies rather than improvising a read-only
workaround here.
