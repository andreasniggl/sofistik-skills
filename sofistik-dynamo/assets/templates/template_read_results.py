"""Template: Read SOFiSTiK support reactions from the active view.

Pattern: SOFiSTiK Model from active view → GetSupportForces → Watch.
No Player inputs, one Player output.
"""
import sys
sys.path.insert(0, '/path/to/sofistik-dynamo/scripts')
from build_dyn import DynGraph

g = DynGraph(name="Read Support Reactions",
             description="Read all support reactions from the active analysis view.")

# === INPUTS ===
# (none — Model.CreateByActiveView needs no arguments)

# Empty load case list — pass [] to get all loadcases
empty_lcs = g.add_python(code="OUT = []", n_inputs=0,
                         x=-200, y=200, label="All Load Cases ([])")

force_type = g.add_string_input("Resultants",
                                label="Force type (Resultants|NodalForces|Distributed|Averaged)",
                                x=-200, y=400)

# === PROCESSING ===
model = g.add_zero_touch(
    "SOFiSTiK.Analysis.Model.CreateByActiveView",
    in_ports=[],
    out_ports=[("Model", "SOFiSTiK Model")],
    description="Create SOFiSTiK Model from active view",
    x=200, y=0, sofistik=True,
    label="Model.CreateByActiveView")

reactions = g.add_zero_touch(
    "SOFiSTiK.Analysis.Results.GetSupportForces@SOFiSTiK.Analysis.Model,System.Collections.Generic.List`1[[System.Int32]],string",
    in_ports=[("model", "SOFiSTiK Model"),
              ("loadCaseIds", "Loadcase Ids (empty=all)"),
              ("forceType", "Force type")],
    out_ports=[("SupportPointForces", "Point support forces"),
               ("SupportLineForces",  "Line support forces"),
               ("SupportAreaForces",  "Area support forces")],
    description="Returns support forces of point/line/area supports",
    x=600, y=200, sofistik=True,
    label="Results.GetSupportForces")

g.connect(model,      "Model",      reactions, "model")
g.connect(empty_lcs,  "OUT",        reactions, "loadCaseIds")
g.connect(force_type, "",           reactions, "forceType")

# === OUTPUTS ===
w_pt = g.add_watch(label="Point Support Forces", x=1100, y=0,   player_output=True)
w_ln = g.add_watch(label="Line Support Forces",  x=1100, y=300, player_output=True)
w_ar = g.add_watch(label="Area Support Forces",  x=1100, y=600, player_output=True)

g.connect(reactions, "SupportPointForces", w_pt, "")
g.connect(reactions, "SupportLineForces",  w_ln, "")
g.connect(reactions, "SupportAreaForces",  w_ar, "")

# === GROUPS ===
g.group("Inputs", [empty_lcs, force_type], color="input")
g.group("SOFiSTiK", [model, reactions], color="sofistik")
g.group("Outputs", [w_pt, w_ln, w_ar], color="output")

issues = g.validate()
assert issues == [], issues
g.save("/mnt/user-data/outputs/read_support_reactions.dyn")
