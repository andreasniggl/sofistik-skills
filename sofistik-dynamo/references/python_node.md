# Python Script nodes — CPython3 in Dynamo 3.6 / Revit 2026

Engine is **CPython3** (Dynamo 3.6 default). All Python nodes built by this skill must set `"Engine": "CPython3"`.

## Standard boilerplate

Use this header whenever the script touches the Revit document. Trim what you don't need.

```python
# Standard library
import sys
import clr

# Revit API
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('RevitServices')

import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *

import RevitServices
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager  # only if writing to the doc

doc   = DocumentManager.Instance.CurrentDBDocument
uiapp = DocumentManager.Instance.CurrentUIApplication
uidoc = uiapp.ActiveUIDocument

# .NET generics, when you need typed lists for Revit API calls
from System.Collections.Generic import List
```

If you only do pure-Python data work (regex, joins, math, list reshaping), drop everything except `import sys`, `import re`, etc.

For DesignScript geometry (creating points/lines that flow into other Dynamo nodes):

```python
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *
```

## Inputs / outputs

- Input ports are named `IN[0]`, `IN[1]`, … and are accessed exactly that way: `IN[0]`, `IN[1]`.
- A list-input port arrives as a Python `list`; a scalar arrives as the bare value. If a port may be either, normalize with:
  ```python
  items = IN[0] if isinstance(IN[0], list) else [IN[0]]
  ```
- The output is a single value bound to `OUT`. To return multiple values, return a list (or a list of lists for tabular).

## UnwrapElement (mandatory for Revit element inputs)

When `IN[i]` is a Revit element (or a list of them), every element must be unwrapped before calling Revit API methods on it. Dynamo wraps elements in `Revit.Elements.Element`; the underlying `Autodesk.Revit.DB.Element` is what the Revit API expects.

```python
# Single element
el = UnwrapElement(IN[0])
el_id = el.Id  # works only after UnwrapElement

# List of elements → typed .NET list of ElementIds
ids = List[ElementId]()
for item in IN[0]:
    ids.Add(UnwrapElement(item).Id)
uidoc.Selection.SetElementIds(ids)
OUT = ids
```

## Transactions (writing to the model)

Any modification of a Revit element must be wrapped in a transaction. Dynamo provides one helper transaction per node run; use it.

```python
TransactionManager.Instance.EnsureInTransaction(doc)
try:
    for item in IN[0]:
        el = UnwrapElement(item)
        p = el.LookupParameter(IN[1])  # parameter name
        if p and not p.IsReadOnly:
            p.Set(IN[2])  # value
    OUT = "Updated {} element(s)".format(len(IN[0]))
finally:
    TransactionManager.Instance.TransactionTaskDone()
```

Reading parameters does **not** need a transaction.

## Revit 2024+ API breaking changes (Revit 2026 / Dynamo 3.6)

The Revit 2024 API changed `ElementId` storage from 32-bit to 64-bit. Scripts written against older Revit versions (or copied from older Dynamo examples) will fail at runtime in Revit 2026 with errors like:

```
AttributeError : 'ElementId' object has no attribute 'IntegerValue'
```

Always use the new property and constructor:

| Old (≤ Revit 2023) — **do not use**       | New (Revit 2024+) — **required**           |
|--------------------------------------------|---------------------------------------------|
| `el.Id.IntegerValue`                       | `el.Id.Value`                               |
| `ElementId(int_id)`                        | `ElementId(System.Int64(int_id))`           |
| variable typed as `int` for an ID          | variable typed as `Int64` / Python `int`    |

Notes:
- `ElementId.Value` returns a 64-bit integer (`System.Int64`). In Python this just looks like an `int` and works in comparisons and `dict` keys without conversion.
- `IntegerValue` is technically still present as `[Obsolete]` but **throws** if the underlying id exceeds 32 bits — and modern Revit projects routinely produce ids that do. Treat it as removed.
- When constructing an `ElementId` from a literal in Python, wrap the integer:
  ```python
  from System import Int64
  eid = ElementId(Int64(123456))
  ```
- Built-in enums (`BuiltInCategory`, `BuiltInParameter`) are also 64-bit-backed now. They still work with `ElementId(BuiltInCategory.OST_Walls)` etc., but never assume an enum value fits in a 32-bit int.

If you see `AttributeError: 'ElementId' object has no attribute 'IntegerValue'` in a script you didn't write, the only fix is to replace every `IntegerValue` with `Value`.

## Units — converting between SOFiSTiK and Revit

Every Python node that reads or writes a numeric quantity through the Revit API has to deal with two unit systems:

| Source                         | Length              | Force | Mass    | Angle   | Temperature |
|--------------------------------|---------------------|-------|---------|---------|-------------|
| **Revit internal** (read/write via API) | decimal feet | kip-ft/s² (non-standard) | kg | radians | Kelvin |
| **SOFiSTiK `.cdb`** (Zero-Touch results) | meters         | kN    | t       | rad     | °C          |

These are different. If you read a `Wall.Height` from Revit, you get feet. If you read a SOFiSTiK `GetStructuralWalls` row, the height is in metres. Mixing them silently produces results that are off by a factor of ~3.28 (or worse for forces). Always convert at the boundary.

### The right API for Revit 2021+

Use `UnitUtils.ConvertToInternalUnits` when **writing** a value into Revit and `UnitUtils.ConvertFromInternalUnits` when **reading** a value out of Revit. The unit identifier is a `ForgeTypeId` from the `UnitTypeId` class. (The old `DisplayUnitType` enum was removed in Revit 2022 — never use it.)

```python
import clr
clr.AddReference('RevitAPI')
from Autodesk.Revit.DB import UnitUtils, UnitTypeId

# READ from Revit (internal feet → metres for SOFiSTiK comparison)
length_m = UnitUtils.ConvertFromInternalUnits(wall.WallHeight, UnitTypeId.Meters)

# WRITE to Revit (a SOFiSTiK metre value → internal feet)
height_ft = UnitUtils.ConvertToInternalUnits(height_in_m, UnitTypeId.Meters)
param.Set(height_ft)
```

### Common `UnitTypeId` values for SOFiSTiK ↔ Revit work

| SOFiSTiK quantity                         | `UnitTypeId.…`                       |
|--------------------------------------------|--------------------------------------|
| Length (m)                                 | `Meters`                             |
| Length (mm) — section dimensions           | `Millimeters`                        |
| Area (m²)                                  | `SquareMeters`                       |
| Volume (m³)                                | `CubicMeters`                        |
| Force (kN) — reactions, normal force       | `Kilonewtons`                        |
| Moment (kNm)                               | `KilonewtonMeters`                   |
| Distributed line load (kN/m)               | `KilonewtonsPerMeter`                |
| Distributed area load (kN/m²)              | `KilonewtonsPerSquareMeter`          |
| Stress / pressure (kN/m² = kPa)            | `Kilopascals` *(equivalent)*         |
| Stress (MPa) — material strengths          | `Megapascals`                        |
| Mass density (kg/m³)                       | `KilogramsPerCubicMeter`             |
| Angle (rad)                                | `Radians` *(no conversion needed)*   |
| Angle (deg)                                | `Degrees`                            |

### Boundary-conversion pattern

Convert exactly once, at the boundary. Don't sprinkle conversions through arithmetic — keep one variable per quantity in one named system and convert when you cross.

```python
# SOFiSTiK side: metres, kN
sof_height_m   = sof_wall_row[5]              # from GetStructuralWalls, col 5 (Height)
sof_reaction_kn = sup_row[5]                  # from GetSupportPointForces, PZ in kN

# Convert to Revit internal at the boundary
height_revit  = UnitUtils.ConvertToInternalUnits(sof_height_m,    UnitTypeId.Meters)
reaction_revit = UnitUtils.ConvertToInternalUnits(sof_reaction_kn, UnitTypeId.Kilonewtons)

# Now you can write into Revit safely
TransactionManager.Instance.EnsureInTransaction(doc)
try:
    p_height.Set(height_revit)
    p_react.Set(reaction_revit)
finally:
    TransactionManager.Instance.TransactionTaskDone()
```

And for the read direction:

```python
# Read length from Revit, then compare against the SOFiSTiK metre value
revit_length_ft = el.LookupParameter("Length").AsDouble()
revit_length_m  = UnitUtils.ConvertFromInternalUnits(revit_length_ft, UnitTypeId.Meters)

if abs(revit_length_m - sof_length_m) > 1e-3:
    OUT = "MISMATCH: Revit={:.3f} m, SOFiSTiK={:.3f} m".format(revit_length_m, sof_length_m)
```

### When you don't need to convert

- **Pure SOFiSTiK pipeline.** If the data comes from `Model.Get*` / `Results.Get*` and only ever feeds back into another SOFiSTiK call (or into Excel via `Export.ResultsToExcel`), you stay in metric units throughout — no conversion needed.
- **Reading a Revit string parameter or an `ElementId`** — only numeric physical quantities need conversion.
- **Writing a unit-less integer or string parameter.**

### When in doubt

Add a Watch node after the conversion step and verify against a hand calculation on one element before running the script over the whole model. Off-by-3.28 errors are the single most common cause of "wrong" Dynamo scripts.

## Classifying analytical elements by StructuralRole

`AnalyticalMember` and `AnalyticalPanel` both inherit from `AnalyticalElement` and both expose the property **`StructuralRole`**, which returns an `Autodesk.Revit.DB.Structure.AnalyticalStructuralRole` enum. This is the canonical way to tell beams / columns / walls / slabs apart — do **not** infer from element category name or from panel geometry (normal vector).

### The `AnalyticalStructuralRole` enum (Revit 2024+)

Member names are stable across Revit 2024–2026 (verified in API docs and the SDK samples). Integer values below come from empirical inspection — Autodesk does not publish them — so if classification stops working after a Revit upgrade, dump `int(role)` once to confirm the mapping still holds.

| Member name            | Int value | Typical meaning                          |
|------------------------|-----------|------------------------------------------|
| `Unset`                | -1        | No structural role assigned (skip)       |
| `StructuralRoleBeam`   | 0         | Beam                                     |
| `StructuralRoleColumn` | 1         | Column                                   |
| `StructuralRoleMember` | 3         | Generic member (brace / other) — skip    |
| `StructuralRoleGirder` | 4         | Girder — **treat as beam**               |
| `StructuralRoleFloor`  | 5         | Floor / slab (there is no `Slab` member) |
| `StructuralRoleWall`   | 6         | Wall                                     |
| `StructuralRolePanel`  | 7         | Generic panel — skip                     |

### Rules

1. **Classify by integer value, not by string.** In Dynamo 3.6's CPython3 the `str()` of a .NET enum is not guaranteed to be just the member name — it can include the namespace (`Autodesk.Revit.DB.Structure.AnalyticalStructuralRole.StructuralRoleBeam`) or vary across runtimes. `int(role)` is stable.
2. **Skip generics.** `StructuralRoleMember (3)`, `StructuralRolePanel (7)` and `Unset (-1)` are generic / uninitialised — skip them and count the skip in your summary so the user can see how many didn't classify.
3. **Guard the property read.** Wrap access in `try/except` and record the first exception to surface in the Watch — without a guard, a single broken element silently kills the whole classification.
4. **Always surface diagnostics.** When a classifier returns `None` for every element, it is impossible to debug without a histogram of the role values actually seen. Include one in the summary (`name (int) -> count`), at least during development.

### Canonical snippet

```python
# Integer-keyed role map — the only safe way to classify analytical
# elements across Dynamo runtimes. Values come from
# Autodesk.Revit.DB.Structure.AnalyticalStructuralRole.
ROLE_MAP = {
    0: "beam",    # StructuralRoleBeam
    1: "column",  # StructuralRoleColumn
    4: "beam",    # StructuralRoleGirder   — treat as beam
    5: "slab",    # StructuralRoleFloor    — the enum has no "Slab"
    6: "wall",    # StructuralRoleWall
    # -1 Unset, 3 StructuralRoleMember, 7 StructuralRolePanel -> skip
}

_role_hist = {}                       # "<name> (<int>)" -> count
_role_first_error = [None]            # boxed so the inner function can write to it

def classify_by_role(el):
    """Return 'beam' | 'column' | 'wall' | 'slab' | None."""
    try:
        role = el.StructuralRole       # may raise on broken / wrong-type elements
        rint = int(role)
    except Exception as e:
        if _role_first_error[0] is None:
            _role_first_error[0] = "{}: {}".format(type(e).__name__, e)
        return None
    key = "{} ({})".format(role, rint)
    _role_hist[key] = _role_hist.get(key, 0) + 1
    return ROLE_MAP.get(rint)
```

Append the histogram to the Watch / summary output so the user can see what the model actually contains:

```
Observed StructuralRole values (name (int) -> count):
  StructuralRoleBeam (0)   -> 412
  StructuralRoleColumn (1) -> 286
  StructuralRoleWall (6)   -> 150
  StructuralRoleFloor (5)  -> 64
  Unset (-1)               -> 5
```

## Common pitfalls

- **Returning `None` from `OUT`** — Dynamo treats this as "no output", and downstream nodes break. If your script logically has nothing to return, set `OUT = []` or a status string.
- **Mutating the input list** — fine in Python, but if downstream nodes share the same data, you may see odd cascading. Build a new list instead.
- **`.LookupParameter` vs `.get_Parameter(BuiltInParameter…)`** — `LookupParameter` is by display name and locale-sensitive; for built-in parameters prefer `el.get_Parameter(BuiltInParameter.SOMETHING)`.
- **`IN[i]` arriving as a single item when you expected a list** — happens when the input port is wired to a scalar source. Always normalize.
- **Forgetting `clr.AddReference` for `RevitServices`** — leads to `ModuleNotFoundError` at run time, not at script load.
- **Levels and lacing** — port-level "Use Levels" / "Keep List Structure" affect how Dynamo presents data to your IN[i]. The builder defaults to `Level: 2, UseLevels: false, KeepListStructure: false` which gives you the natural list. Only change it on user request.

## Pure-Python data utility example (bool mask from regex)

From the example graphs — this is the recommended shape for filtering helpers:

```python
import re

values  = IN[0]      # list of parameter values (may include None)
pattern = IN[1]      # regex string

mask = []
for v in values:
    if v is None:
        mask.append(False)
    else:
        mask.append(bool(re.search(pattern, str(v), re.I)))

OUT = mask
```

The `mask` then feeds a `List.FilterByBoolMask` Zero-Touch node.

## When NOT to use a Python node

Don't reach for Python when there is a one-call equivalent:

- Joining two 2-D lists by a key column → `Utils.TableLeftJoin` / `RightJoin` / `InnerJoin`.
- Concatenating lists → `List.Join` (`DSCore.List.Join`).
- Reading or setting a single parameter → `Parameter.ParameterByName` + `Parameter.Value` / `Element.SetParameterByName`.
- Selecting the physical counterpart of an analytical element → `Utils.GetPhysicalCounterpart`.

Use Python when: you need iteration, conditional logic, regex, transactional writes to many elements, or when chaining 4+ pure-data nodes for one logical operation.
