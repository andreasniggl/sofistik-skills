---
name: sofistik-dynamo
description: Build Revit Dynamo scripts (.dyn) for Revit 2026 / Dynamo 3.6 that evaluate or modify Revit models and read SOFiSTiK FEA results via the SOFiSTiK Analysis + Design Dynamo package. Use this skill whenever the user asks to create, scaffold, edit, or troubleshoot a Dynamo graph, especially when they mention SOFiSTiK results, the .cdb database, analytical/physical members, the Dynamo Player, Zero-Touch nodes, or want to combine Revit element queries with Python. Trigger this even for partial requests like "I need a Dynamo script that exports support reactions" or "give me the python for unwrapping these analytical elements" — anything that ends up in a .dyn file or its embedded Python.
---

# SOFiSTiK Dynamo Script Builder

Build Dynamo `.dyn` graphs that target the **Revit Dynamo Player** workflow: input nodes feed parameters at the top, the graph runs, output (Watch) nodes display the result. Simple data flow lives in Dynamo nodes; non-trivial logic lives in CPython3 Python Script nodes inside the graph.

## Core principles

1. **Plan first, then build.** Never start emitting JSON before the user has approved a plan. Dynamo graphs cannot be partially fixed in chat — a wrong shape means the file won't open in Revit.
2. **One graph = one job.** If the user describes two unrelated jobs (e.g. "select walls AND export reactions"), suggest splitting them.
3. **Logic in Python, plumbing in nodes.** Use Zero-Touch nodes for selection, package calls (SOFiSTiK), parameter reads/writes, and Watch outputs. Use a Python Script node any time logic exceeds a single function call (filtering, transforming, transactional Revit modifications, regex, joins beyond `Utils.TableLeftJoin`, anything iterative).
4. **Player-friendly.** Inputs that the user is meant to set in the Dynamo Player must be marked `IsSetAsInput: true` — but **only** when the user explicitly asks for that parameter to be a Player input. By default, leave `IsSetAsInput: false`. Watch nodes that should display in Player are marked `IsSetAsOutput: true`.
5. **Always unwrap.** Inside Python nodes, every Revit element coming through `IN[i]` must be passed through `UnwrapElement(...)` before `.Id`, `.get_Parameter`, etc.
6. **Revit 2024+ `ElementId`.** Always use `el.Id.Value` (Int64), never `el.Id.IntegerValue` — the latter was deprecated in Revit 2024 and throws on modern projects. The builder's `add_python` rejects code containing `.IntegerValue`. See `references/python_node.md` → "Revit 2024+ API breaking changes" for the full migration table.
7. **Convert units at the SOFiSTiK ↔ Revit boundary.** Revit stores lengths in feet, forces in non-standard internal units, etc. SOFiSTiK `.cdb` results come in metres and kilonewtons. Any Python node that *writes* a SOFiSTiK value to a Revit element must wrap it in `UnitUtils.ConvertToInternalUnits(value, UnitTypeId.Meters/Kilonewtons/...)`; any node that *reads* a Revit value to compare with SOFiSTiK must use `ConvertFromInternalUnits`. The builder's `add_python` warns when a script touches Revit element data without any conversion call. See `references/python_node.md` → "Units — converting between SOFiSTiK and Revit" for the unit table and patterns.

## Workflow — follow these steps in order

### Step 1: Capture intent

Ask only what's necessary. The minimum you need before drafting a plan:

- **What is the script's job?** One sentence. Read / modify / export?
- **What's the input?** Selection in Revit, all elements of a category, a path to a `.cdb` or `.xlsx`, a parameter name, etc.
- **What's the output?** A modified model, a Watch that shows a list, an Excel file, a created Revit element?
- **Which inputs should appear in the Dynamo Player?** Don't assume — ask. The user told you their convention: `IsSetAsInput` is set **only on request**, per parameter.
- **Does it touch SOFiSTiK results?** If yes, where does the `.cdb` come from — currently active view, a fixed path, or a user-supplied path?

If the user's prompt already contains all of this, skip to Step 2.

### Step 2: Propose a plan and wait for approval

Write a plan in this exact format and stop. Do not write any `.dyn` JSON yet.

```
## Plan: <script name>

**Job:** <one sentence>

**Input group** (left side of graph)
- <node 1 — e.g. "String input 'Parameter name' (Player input: yes)">
- <node 2 — e.g. "File path to .cdb (Player input: yes)">

**Processing group** (middle)
- <node — e.g. "All Elements of Category: OST_AnalyticalMember">
- <Python node: <what it does in one line>>
- <SOFiSTiK call: Model.CreateByActiveView → Results.GetSupportForces>

**Output group** (right)
- <Watch node "Filtered elements" (Player output)>

**Files this skill will produce:** `<name>.dyn` (and a separate `<name>.py` reference copy of any Python code longer than ~30 lines, for easier review)

**Open questions:** <only if any>
```

Then ask: *"Does this plan look right? Any changes before I build the .dyn?"*

For complex graphs (more than ~10 nodes, multiple Python nodes, or anything the user calls out as tricky), instead of building everything at once, present a **TODO list** in the plan and offer to walk through it step-by-step. Example:

```
This is a larger graph. I suggest building it in steps:
- [ ] Step 1: Set up inputs (paths, parameter names) and the SOFiSTiK Model node
- [ ] Step 2: Pull support forces and join with element GUIDs
- [ ] Step 3: Python filter for max reactions per support type
- [ ] Step 4: Watch outputs and Player input flags

Which step should we tackle first, or shall I draft step 1?
```

### Step 3: Build the `.dyn`

After approval, use the build helper rather than hand-writing JSON. See `scripts/build_dyn.py` and the canonical schema in `references/dyn_schema.md`.

Workflow:

1. Read `references/dyn_schema.md` once if it isn't already in context — it is the source of truth for the Dynamo 3.x JSON shape.
2. For any SOFiSTiK call, look up the exact `FunctionSignature` and port names in `references/sofistik_api.md`.
3. For Python nodes, start from the boilerplate in `references/python_node.md` (Revit imports, DocumentManager, transaction pattern, `UnwrapElement`).
4. Pick the closest template in `assets/templates/`, copy it to `/home/claude/<workspace>/build_<n>.py`, and adapt. Builder API:
   - `g = DynGraph(name=..., description=...)` — start a graph.
   - `g.add_string_input(value, label, x, y, player_input=False)` — string input. Set `player_input=True` only when the user explicitly asked for that parameter to appear in the Player.
   - `g.add_filename(value, hint_path, label, x, y, player_input=False, external_label="my.xlsx")` — file path input. `external_label` adds it to `NodeLibraryDependencies` as External.
   - `g.add_boolean(...)`, `g.add_integer_slider(...)` — other Player inputs.
   - `g.add_zero_touch(function_signature, in_ports=[(name, desc), ...], out_ports=[...], x, y, sofistik=True/False)` — any .NET function call. Set `sofistik=True` for any `SOFiSTiK.*` signature.
   - `g.add_zero_touch_varargs(...)` — for `List.Join` and similar variadic functions.
   - `g.add_python(code, n_inputs, x, y, label)` — CPython3 Python node. Pass `code` with normal `\n` line breaks; the builder normalizes.
   - `g.add_watch(label, x, y, player_output=False)` — Watch. `player_output=True` makes it a Player output.
   - `g.add_categories(selected="OST_...")`, `g.add_elements_of_category()`, `g.add_select_model_elements(category=...)` — common Revit selectors.
   - `g.connect(src_node, "src_port", dst_node, "dst_port")` — wire two ports. For single-port nodes (StringInput, Watch) pass `""`.
   - `g.group("Title", [nodes...], color="input"|"processing"|"output"|"sofistik")` — group annotation with the convention from `dyn_schema.md`.
   - `g.mark_player_input(node, label)`, `g.mark_player_output(node, label)` — toggle Player flags after the fact.
   - `g.validate()` returns a list of structural problems; should be `[]` before saving.
   - `g.save(path)` writes the `.dyn`.
5. Run the build script. Always assert `g.validate() == []` before `g.save(...)` — catches unwired ports, unknown port refs, missing display names.
6. Save to `/mnt/user-data/outputs/<n>.dyn`. If any embedded Python is longer than ~30 lines, also save a standalone `<n>.py` next to it so the user can review/edit Python without opening the JSON.
7. Present the file(s) with `present_files`.

### Step 4: Hand off

End with a short summary of:
- What the script does
- Which nodes are Player inputs/outputs (be explicit if none)
- Any manual step the user must do in Revit (e.g. "open the script in Revit, click 'Run' once to verify, then it will show in Dynamo Player")
- Known limitations (e.g. "the SOFiSTiK package version is pinned to 2026.5.0 in NodeLibraryDependencies — adjust if your install differs")

## Reference files

Read these as needed; they are the source of truth.

- `references/dyn_schema.md` — Dynamo 3.x `.dyn` JSON schema: top-level keys, node `ConcreteType`s, port/connector wiring, NodeView geometry, group annotations, the `IsSetAsInput`/`IsSetAsOutput` mechanism, the Inputs/Outputs declarations.
- `references/sofistik_api.md` — Quick reference for the SOFiSTiK Analysis + Design Zero-Touch nodes: `Analyze`, `Model`, `Results`, `Reinforcement`, `Design`, `Utils`, `Export`. Lists exact `FunctionSignature` strings and return-tuple column indices.
- `references/python_node.md` — CPython3 boilerplate for Python Script nodes: Revit API imports, DocumentManager pattern, transaction handling, `UnwrapElement`, common pitfalls (level changes, list-vs-single inputs, returning `OUT`).
- `scripts/build_dyn.py` — Python builder. Use this rather than hand-writing JSON. Has docstrings for every method.
- `assets/templates/` — Four runnable starter scripts that exercise every feature of the builder. Read the one closest to the user's task, copy it, then adapt:
  - `template_minimal.py` — one Player input → Python → Watch (the "hello world").
  - `template_read_results.py` — `Model.CreateByActiveView` → `Results.GetSupportForces` → 3 Watch outputs (the canonical SOFiSTiK results-reading pattern, no unit conversion needed because data stays inside SOFiSTiK).
  - `template_modify_revit.py` — bulk parameter set with a transactional Python node (the canonical write-to-Revit pattern, including `UnwrapElement` and `TransactionManager`; sets a string parameter so no unit conversion is needed — see the inline note for how to adapt to numeric values).
  - `template_sofistik_to_revit_units.py` — read column normal force from SOFiSTiK and write it onto the matching Revit column with the **correct `UnitUtils.ConvertToInternalUnits` boundary conversion**. This is the canonical SOFiSTiK-results → Revit pattern; copy this whenever a Python node needs to push a numeric SOFiSTiK value back into Revit.

## Triggering anti-patterns

Don't use this skill for:
- Pure Revit API questions with no Dynamo involved (just answer them directly).
- Reading existing `.dyn` files to explain them — you can do that with `view`/`bash` directly without the builder.

Do use it for:
- Anything that ends with "...and save it as a .dyn".
- Iterating on an existing `.dyn` the user uploaded — read it, propose a diff plan, then rebuild affected sections with the builder.
