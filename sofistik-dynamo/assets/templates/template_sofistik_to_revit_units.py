"""Template: Write SOFiSTiK results back into Revit element parameters,
with the correct unit conversions at the boundary.

Scenario: read normal force (N, in kN) from SOFiSTiK column results, and
write it onto the Revit physical column as a parameter "SOF_N_kN" (a
Number-type project parameter).

Pattern:
  active view → SOFiSTiK Model → ColumnResults → Python (filter + match
  by Guid) → Python (transactional write with UnitUtils conversion).

Two Player inputs (loadcase id, target parameter name).
"""
import sys
sys.path.insert(0, '/path/to/sofistik-dynamo/scripts')
from build_dyn import DynGraph

g = DynGraph(name="Write SOF Normal Force to Column",
             description="Write SOFiSTiK column normal force into a Revit parameter.")

# === INPUTS ===
lc_id = g.add_integer_slider(value=1, min_value=1, max_value=999,
                             label="Load case Id",
                             x=-550, y=0, player_input=True)

param_name = g.add_string_input("SOF_N_kN",
                                label="Target Revit parameter name",
                                x=-550, y=200, player_input=True)

# === PROCESSING — SOFiSTiK ===
model = g.add_zero_touch(
    "SOFiSTiK.Analysis.Model.CreateByActiveView",
    in_ports=[],
    out_ports=[("Model", "SOFiSTiK Model")],
    description="Open SOFiSTiK Model from active view",
    x=-100, y=0, sofistik=True,
    label="Model.CreateByActiveView")

# Wrap loadcase int into a single-element list, since GetColumnResults wants List<int>.
wrap_lc = g.add_python(code='OUT = [int(IN[0])]', n_inputs=1, x=-100, y=200,
                       label="Wrap LC into List")
g.connect(lc_id, "", wrap_lc, "IN[0]")

loc_str = g.add_string_input("EndPoints",
                             label="Result location",
                             x=-100, y=350)

col_results = g.add_zero_touch(
    "SOFiSTiK.Analysis.Results.GetColumnResults@SOFiSTiK.Analysis.Model,System.Collections.Generic.List`1[[System.Int32]],string",
    in_ports=[("model", "Model"),
              ("loadCaseIds", "Loadcase Ids"),
              ("locations", "Result location")],
    out_ports=[("Results", "Loadcase Id, Guid, Id, Xi, N, My, Mz, Vz, Vy")],
    description="Get column results",
    x=300, y=100, sofistik=True,
    label="Results.GetColumnResults")
g.connect(model, "Model", col_results, "model")
g.connect(wrap_lc, "OUT", col_results, "loadCaseIds")
g.connect(loc_str, "", col_results, "locations")

# === PROCESSING — Revit selection ===
cat = g.add_categories("OST_StructuralColumns", x=-100, y=550, label="Columns")
eoc = g.add_elements_of_category(x=200, y=550)
g.connect(cat, "Category", eoc, "Category")

# === PROCESSING — Match by Guid + write with conversion ===
write_code = '''import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from Autodesk.Revit.DB import UnitUtils, UnitTypeId
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument

results    = IN[0]   # 2-D list from GetColumnResults: rows of [LcId,Guid,Id,Xi,N,My,Mz,Vz,Vy]
elements   = IN[1] if isinstance(IN[1], list) else [IN[1]]
param_name = IN[2]

# Build a quick lookup: Guid -> max |N| over the rows for this column.
# SOFiSTiK results are in kN; we will convert to Revit internal at write time.
n_by_guid = {}
for row in results or []:
    if not row or len(row) < 5:
        continue
    guid = str(row[1])
    n_kn = float(row[4])
    prev = n_by_guid.get(guid)
    if prev is None or abs(n_kn) > abs(prev):
        n_by_guid[guid] = n_kn

written, skipped = 0, 0

TransactionManager.Instance.EnsureInTransaction(doc)
try:
    for item in elements:
        el = UnwrapElement(item)
        guid = el.UniqueId  # Revit unique id matches SOFiSTiK Guid for analytical-physical pairs
        if guid not in n_by_guid:
            skipped += 1
            continue
        p = el.LookupParameter(param_name)
        if p is None or p.IsReadOnly:
            skipped += 1
            continue
        # Boundary conversion: SOFiSTiK kN -> Revit internal force units.
        n_internal = UnitUtils.ConvertToInternalUnits(n_by_guid[guid], UnitTypeId.Kilonewtons)
        p.Set(n_internal)
        written += 1
finally:
    TransactionManager.Instance.TransactionTaskDone()

OUT = "Wrote N for {} column(s); skipped {}".format(written, skipped)
'''

writer = g.add_python(code=write_code, n_inputs=3,
                      x=700, y=300,
                      label="Write Normal Force (with unit conversion)")
g.connect(col_results, "Results", writer, "IN[0]")
g.connect(eoc, "Elements", writer, "IN[1]")
g.connect(param_name, "", writer, "IN[2]")

# === OUTPUT ===
w = g.add_watch(label="Status", x=1100, y=300, player_output=True)
g.connect(writer, "OUT", w, "")

# === GROUPS ===
g.group("Inputs", [lc_id, param_name], color="input")
g.group("SOFiSTiK results", [model, wrap_lc, loc_str, col_results], color="sofistik")
g.group("Revit selection", [cat, eoc], color="processing")
g.group("Write to Revit (with UnitUtils conversion)", [writer], color="processing")
g.group("Output", [w], color="output")

issues = g.validate()
assert issues == [], issues
g.save("/mnt/user-data/outputs/write_sof_normal_force.dyn")
