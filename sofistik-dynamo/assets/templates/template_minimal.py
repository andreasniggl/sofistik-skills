"""Template: Minimal script with one Player input, one Watch output.

Pattern: input → processing (Python) → Watch.
"""
import sys
sys.path.insert(0, '/path/to/sofistik-dynamo/scripts')  # adjust
from build_dyn import DynGraph

g = DynGraph(name="Minimal Template",
             description="One input, one Python step, one watched output.")

# === INPUTS ===
in1 = g.add_string_input("hello",
                         label="Input string",
                         x=-500, y=0,
                         player_input=True)

# === PROCESSING ===
py = g.add_python(code='''text = IN[0]
OUT = text.upper() if text else ""
''',
                  n_inputs=1,
                  x=0, y=0,
                  label="Uppercase")
g.connect(in1, "", py, "IN[0]")

# === OUTPUTS ===
w = g.add_watch(label="Result", x=400, y=0, player_output=True)
g.connect(py, "OUT", w, "")

# === GROUPS ===
g.group("Inputs",     [in1], color="input")
g.group("Processing", [py],  color="processing")
g.group("Output",     [w],   color="output")

assert g.validate() == [], g.validate()
g.save("/mnt/user-data/outputs/minimal.dyn")
