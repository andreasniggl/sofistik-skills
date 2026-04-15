"""Template: Modify Revit elements via a transactional Python node.

Pattern: Select elements → set parameter on each, inside a transaction.
Player input: which parameter to set + the value.
"""
import sys
sys.path.insert(0, '/path/to/sofistik-dynamo/scripts')
from build_dyn import DynGraph

g = DynGraph(name="Bulk Set Parameter",
             description="Set a parameter to a fixed value on all selected elements.")

# === INPUTS ===
cat = g.add_categories("OST_StructuralFraming", x=-550, y=-50, label="Category")
eoc = g.add_elements_of_category(x=-220, y=-50)
g.connect(cat, "Category", eoc, "Category")

p_name = g.add_string_input("Comments",
                            label="Parameter name",
                            x=-550, y=200, player_input=True)

p_val = g.add_string_input("Set by Dynamo",
                           label="Value to write",
                           x=-550, y=350, player_input=True)

# === PROCESSING ===
py_code = '''import clr
clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from Autodesk.Revit.DB import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument

elements = IN[0] if isinstance(IN[0], list) else [IN[0]]
param_name = IN[1]
value      = IN[2]

# Units note: this template writes a string. No UnitUtils conversion needed.
# If you adapt this to write a numeric quantity (length, force, ...), wrap
# the value with UnitUtils.ConvertToInternalUnits(value, UnitTypeId.Meters)
# (or whichever UnitTypeId fits) before calling p.Set(...).

updated, skipped = 0, 0

TransactionManager.Instance.EnsureInTransaction(doc)
try:
    for item in elements:
        el = UnwrapElement(item)
        p = el.LookupParameter(param_name)
        if p is None or p.IsReadOnly:
            skipped += 1
            continue
        p.Set(value)
        updated += 1
finally:
    TransactionManager.Instance.TransactionTaskDone()

OUT = "Updated {} element(s); skipped {}".format(updated, skipped)
'''

py = g.add_python(code=py_code, n_inputs=3,
                  x=200, y=100,
                  label="Set Parameter (Transactional)")

g.connect(eoc,    "Elements", py, "IN[0]")
g.connect(p_name, "",         py, "IN[1]")
g.connect(p_val,  "",         py, "IN[2]")

# === OUTPUTS ===
w = g.add_watch(label="Status", x=700, y=100, player_output=True)
g.connect(py, "OUT", w, "")

# === GROUPS ===
g.group("Inputs", [cat, eoc, p_name, p_val], color="input")
g.group("Set parameter (transactional)", [py], color="processing")
g.group("Output", [w], color="output")

assert g.validate() == [], g.validate()
g.save("/mnt/user-data/outputs/bulk_set_parameter.dyn")
