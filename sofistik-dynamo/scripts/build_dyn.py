"""
build_dyn.py — Construct valid Dynamo 3.x .dyn files programmatically.

Designed for Revit 2026 / Dynamo 3.6, targeting the Dynamo Player workflow.

Typical usage:

    from build_dyn import DynGraph

    g = DynGraph(name="0-1 Copy Parameter from Analytical to Physical",
                 description="Copies an analytical parameter value to its physical counterpart.")

    # --- Inputs group ---
    cat_dd = g.add_categories(selected="OST_AnalyticalMember", x=-550, y=-50)
    eoc    = g.add_elements_of_category(x=-220, y=-50)
    g.connect(cat_dd, "Category", eoc, "Category")

    src_param = g.add_string_input("SOFiSTiK_Name",
                                   label="Parameter on Analytical Element",
                                   x=-10, y=440, player_input=True)
    dst_param = g.add_string_input("Kennzeichen",
                                   label="Parameter on Physical Counterpart",
                                   x=1020, y=-45, player_input=True)

    # --- Processing group ---
    par_by_name = g.add_zero_touch(
        "Revit.Elements.Parameter.ParameterByName@Revit.Elements.Element,string",
        in_ports=[("element", "Element"), ("name", "string")],
        out_ports=[("Parameter", "Parameter")],
        description="Get Element's Parameter by Name",
        x=560, y=410)

    par_value = g.add_zero_touch(
        "Revit.Elements.Parameter.Value",
        in_ports=[("parameter", "Parameter")],
        out_ports=[("var[]..[]", "var[]..[]")],
        description="Get the value of the parameter",
        x=930, y=410)

    counterpart = g.add_zero_touch(
        "SOFiSTiK.Analysis.Utils.GetPhysicalCounterpart@Revit.Elements.Element[]",
        in_ports=[("elements", "Element[]")],
        out_ports=[("Element[]", "Element[]")],
        description="Returns the physical counterpart",
        x=610, y=-65,
        sofistik=True)

    setp = g.add_zero_touch(
        "Revit.Elements.Element.SetParameterByName@string,var",
        in_ports=[("element", "Element"), ("parameterName", "string"), ("value", "var")],
        out_ports=[("Element", "Element")],
        description="Set parameter by name",
        x=1570, y=-80)

    g.connect(eoc, "Elements", par_by_name, "element")
    g.connect(eoc, "Elements", counterpart, "elements")
    g.connect(src_param, "", par_by_name, "name")
    g.connect(par_by_name, "Parameter", par_value, "parameter")
    g.connect(par_value, "var[]..[]", setp, "value")
    g.connect(counterpart, "Element[]", setp, "element")
    g.connect(dst_param, "", setp, "parameterName")

    # --- Groups (visual) ---
    g.group("Input: all analytical elements", [cat_dd, eoc], color="input")
    g.group("Get Parameter on analytical model",
            [par_by_name, par_value, src_param], color="processing")
    g.group("SOFiSTiK Analysis + Design", [counterpart], color="sofistik")
    g.group("Set Parameter on Physical Counterpart",
            [dst_param, setp], color="output")

    g.save("/mnt/user-data/outputs/0-1_Copy_Parameter.dyn")

The resulting file opens in Dynamo 3.6 and runs without modification.
"""

from __future__ import annotations
import json
import uuid
from dataclasses import dataclass, field
from typing import Any


# ---------- ID helpers ----------

def new_id() -> str:
    """32-char lowercase hex, matching the format Dynamo writes."""
    return uuid.uuid4().hex


def new_guid() -> str:
    """Standard GUID with dashes (used for top-level Uuid and annotation Ids)."""
    return str(uuid.uuid4())


# ---------- Group color palette ----------

GROUP_COLORS = {
    "input":      "#FFC1D676",  # green
    "processing": "#FFB9F9E1",  # mint
    "output":     "#FFFFC999",  # orange
    "sofistik":   "#FF48B9FF",  # blue
    "neutral":    "#FFE8E8E8",
}


# ---------- Revit 2024+ API lint ----------

def _lint_python_for_revit_2024(code: str) -> list[str]:
    """Scan Python node code for Revit ≤2023 patterns that fail at runtime
    in Revit 2024+. Returns a list of human-readable problem descriptions
    (empty list = clean).

    Currently checks:
      - `.IntegerValue` on ElementId  → use `.Value` (Int64) in Revit 2024+.
        The deprecated property throws on ids > 32-bit.

    Add new hard-error checks here as further breaking changes surface."""
    import re
    problems: list[str] = []
    for ln_no, line in enumerate(code.splitlines(), start=1):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if re.search(r"\.IntegerValue\b", line):
            problems.append(
                f"line {ln_no}: '.IntegerValue' is removed-in-effect in Revit 2024+; "
                f"use '.Value' (returns Int64). Offending line: {line.strip()!r}"
            )
        # DisplayUnitType was removed in Revit 2022. Hard error.
        if re.search(r"\bDisplayUnitType\b", line):
            problems.append(
                f"line {ln_no}: 'DisplayUnitType' was removed in Revit 2022; "
                f"use 'UnitTypeId' (a ForgeTypeId) with UnitUtils.ConvertToInternalUnits / "
                f"ConvertFromInternalUnits. Offending line: {line.strip()!r}"
            )
    return problems


def _lint_python_for_units(code: str) -> list[str]:
    """Scan Python node code for likely missing unit conversions when reading
    or writing Revit element data. Returns a list of WARNINGS (not errors) —
    these are heuristics that may have false positives.

    Heuristics:
      - Code calls a Revit setter that takes a numeric quantity (Parameter.Set,
        Element.SetParameterByName) but never calls UnitUtils.* — likely a
        missing ConvertToInternalUnits.
      - Code reads a numeric Revit property (.AsDouble(), .Length, .Volume, .Area,
        .Height, .Width) but never calls UnitUtils.* — likely a missing
        ConvertFromInternalUnits before comparing to SOFiSTiK metric values.
      - Code references SOFiSTiK results (sof_, cdb, GetStructural, GetSupport,
        GetBeam, GetColumn, GetWall, GetArea results) AND writes to Revit
        without UnitUtils — strong signal of a unit boundary crossing without
        conversion.

    These are heuristics. Pass `strict=False` to add_python to skip."""
    import re
    warnings: list[str] = []
    has_unit_utils = bool(re.search(r"\bUnitUtils\.(Convert(To|From)InternalUnits|Convert)\b", code))
    if has_unit_utils:
        return warnings  # script handles units explicitly — trust it

    # Strip comments for the substantive checks
    body_lines = []
    for ln in code.splitlines():
        s = ln.lstrip()
        if s.startswith("#"):
            continue
        body_lines.append(ln)
    body = "\n".join(body_lines)

    writes_numeric = bool(re.search(
        r"(\.Set\s*\(|SetParameterByName|\.Set_Parameter|SetValue\s*\()", body))
    reads_numeric = bool(re.search(
        r"(\.AsDouble\s*\(|\.LookupParameter\([^)]+\)\.AsDouble"
        r"|\.Length\b|\.Volume\b|\.Area\b|\.Height\b|\.Width\b|\.Thickness\b)",
        body))
    touches_sofistik = bool(re.search(
        r"(SOFiSTiK|\.cdb\b|GetStructural\w+|GetSupport\w+|GetBeamResults"
        r"|GetColumnResults|GetWallResultants|GetAreaResults|GetDesignElement)",
        body))

    if writes_numeric:
        if touches_sofistik:
            warnings.append(
                "Script writes to a Revit element AND references SOFiSTiK data "
                "but never calls UnitUtils.ConvertToInternalUnits. SOFiSTiK values "
                "are in metres / kN; Revit internal units are feet / non-standard. "
                "Wrap the value at the boundary, e.g. "
                "`UnitUtils.ConvertToInternalUnits(sof_value_m, UnitTypeId.Meters)`."
            )
        else:
            warnings.append(
                "Script writes to a Revit element but never calls "
                "UnitUtils.ConvertToInternalUnits. If the value is a numeric physical "
                "quantity (length, force, area, ...) you almost certainly need to "
                "convert. Skip this warning only if the value is a string, an integer "
                "count, or already in Revit internal units."
            )
    if reads_numeric and touches_sofistik and not writes_numeric:
        warnings.append(
            "Script reads a numeric Revit property AND references SOFiSTiK data "
            "but never calls UnitUtils.ConvertFromInternalUnits. To compare values "
            "against SOFiSTiK (metric), convert the Revit value first, e.g. "
            "`UnitUtils.ConvertFromInternalUnits(revit_value_ft, UnitTypeId.Meters)`."
        )
    return warnings


# ---------- Port / Node containers ----------

def _port(name: str, description: str = "", port_id: str | None = None) -> dict:
    return {
        "Id": port_id or new_id(),
        "Name": name,
        "Description": description or name,
        "UsingDefaultValue": False,
        "Level": 2,
        "UseLevels": False,
        "KeepListStructure": False,
    }


@dataclass
class Node:
    """In-memory node. We store the full dict ready for serialization plus
    the layout and Player flags separately (they live in View.NodeViews)."""
    node_dict: dict
    x: float = 0.0
    y: float = 0.0
    display_name: str = ""
    is_player_input: bool = False
    is_player_output: bool = False
    excluded: bool = False
    show_geometry: bool = True
    # for top-level Inputs/Outputs declarations
    player_input_type: str = "string"          # string | boolean | number | filename
    player_input_value: Any = ""
    player_input_description: str = ""
    is_sofistik: bool = False                  # tracked for NodeLibraryDependencies

    @property
    def id(self) -> str:
        return self.node_dict["Id"]

    def output_port_id(self, name: str) -> str:
        outs = self.node_dict.get("Outputs", [])
        if not outs:
            raise ValueError(f"Node {self.id[:8]} has no output ports")
        if name == "" or name is None:
            return outs[0]["Id"]
        for p in outs:
            if p["Name"] == name:
                return p["Id"]
        # fall back to positional first port if name not found
        raise KeyError(f"Output port '{name}' not found on node {self.id[:8]}. "
                       f"Available: {[p['Name'] for p in outs]}")

    def input_port_id(self, name: str) -> str:
        ins = self.node_dict.get("Inputs", [])
        if not ins:
            raise ValueError(f"Node {self.id[:8]} has no input ports")
        if name == "" or name is None:
            return ins[0]["Id"]
        for p in ins:
            if p["Name"] == name:
                return p["Id"]
        raise KeyError(f"Input port '{name}' not found on node {self.id[:8]}. "
                       f"Available: {[p['Name'] for p in ins]}")


# ---------- DynGraph ----------

class DynGraph:
    def __init__(self,
                 name: str,
                 description: str = "",
                 sofistik_package_version: str = "2026.5.0"):
        self.uuid = new_guid()
        self.name = name
        self.description = description
        self.sofistik_package_version = sofistik_package_version
        self.nodes: list[Node] = []
        self.connectors: list[dict] = []
        self.annotations: list[dict] = []
        # external file deps (Filename node id -> filename label)
        self.external_files: list[tuple[str, str]] = []  # (node_id, label)

    # ---------- node builders ----------

    def _register(self, node: Node) -> Node:
        self.nodes.append(node)
        return node

    def add_string_input(self,
                         value: str,
                         label: str = "String",
                         x: float = 0, y: float = 0,
                         player_input: bool = False,
                         description: str = "Creates a string") -> Node:
        nid = new_id()
        out_port = _port("", "String")
        d = {
            "ConcreteType": "CoreNodeModels.Input.StringInput, CoreNodeModels",
            "Id": nid,
            "NodeType": "StringInputNode",
            "Inputs": [],
            "Outputs": [out_port],
            "Replication": "Disabled",
            "Description": description,
            "InputValue": value,
        }
        node = Node(node_dict=d, x=x, y=y,
                    display_name=label,
                    is_player_input=player_input,
                    player_input_type="string",
                    player_input_value=value,
                    player_input_description=description)
        return self._register(node)

    def add_filename(self,
                     value: str = "",
                     hint_path: str = "",
                     label: str = "File Path",
                     x: float = 0, y: float = 0,
                     player_input: bool = False,
                     external_label: str | None = None,
                     description: str = "Allows you to select a file on the system and returns its file path") -> Node:
        nid = new_id()
        out_port = _port("", "File path")
        d = {
            "ConcreteType": "CoreNodeModels.Input.Filename, CoreNodeModels",
            "Id": nid,
            "NodeType": "ExtensionNode",
            "Inputs": [],
            "Outputs": [out_port],
            "Replication": "Disabled",
            "Description": description,
            "HintPath": hint_path,
            "InputValue": value,
        }
        node = Node(node_dict=d, x=x, y=y,
                    display_name=label,
                    is_player_input=player_input,
                    player_input_type="filename",
                    player_input_value=value,
                    player_input_description=description)
        self._register(node)
        if external_label:
            self.external_files.append((nid, external_label))
        return node

    def add_boolean(self, value: bool = False,
                    label: str = "Boolean",
                    x: float = 0, y: float = 0,
                    player_input: bool = False) -> Node:
        nid = new_id()
        out_port = _port("", "Boolean")
        d = {
            "ConcreteType": "CoreNodeModels.Input.BoolSelector, CoreNodeModels",
            "Id": nid,
            "NodeType": "BooleanInputNode",
            "Inputs": [],
            "Outputs": [out_port],
            "Replication": "Disabled",
            "Description": "Enables selection between True and False",
            "InputValue": bool(value),
        }
        node = Node(node_dict=d, x=x, y=y,
                    display_name=label,
                    is_player_input=player_input,
                    player_input_type="boolean",
                    player_input_value=bool(value),
                    player_input_description="Boolean")
        return self._register(node)

    def add_integer_slider(self, value: int = 0,
                           min_value: int = 0, max_value: int = 100, step: int = 1,
                           label: str = "Integer",
                           x: float = 0, y: float = 0,
                           player_input: bool = False) -> Node:
        nid = new_id()
        out_port = _port("", "Int64")
        d = {
            "ConcreteType": "CoreNodeModels.Input.IntegerSlider64Bit, CoreNodeModels",
            "NumberType": "Integer",
            "MaximumValue": int(max_value),
            "MinimumValue": int(min_value),
            "StepValue": int(step),
            "InputValue": int(value),
            "Id": nid,
            "NodeType": "NumberInputNode",
            "Inputs": [],
            "Outputs": [out_port],
            "Replication": "Disabled",
            "Description": "Produces integer values",
        }
        node = Node(node_dict=d, x=x, y=y,
                    display_name=label,
                    is_player_input=player_input,
                    player_input_type="number",
                    player_input_value=int(value),
                    player_input_description="Integer")
        return self._register(node)

    def add_zero_touch(self,
                       function_signature: str,
                       in_ports: list[tuple[str, str]],
                       out_ports: list[tuple[str, str]],
                       description: str = "",
                       x: float = 0, y: float = 0,
                       replication: str = "Auto",
                       sofistik: bool = False,
                       label: str | None = None) -> Node:
        """Generic Zero-Touch (.NET) function call.

        in_ports / out_ports: list of (name, description-or-type) tuples.
        Set sofistik=True for any SOFiSTiK.* signature so it gets added to
        NodeLibraryDependencies.
        """
        nid = new_id()
        d = {
            "ConcreteType": "Dynamo.Graph.Nodes.ZeroTouch.DSFunction, DynamoCore",
            "Id": nid,
            "NodeType": "FunctionNode",
            "Inputs":  [_port(n, desc) for (n, desc) in in_ports],
            "Outputs": [_port(n, desc) for (n, desc) in out_ports],
            "FunctionSignature": function_signature,
            "Replication": replication,
            "Description": description or function_signature,
        }
        # default display name: "Type.Method"
        if label is None:
            sig = function_signature.split("@")[0]
            parts = sig.split(".")
            label = ".".join(parts[-2:]) if len(parts) >= 2 else sig
        return self._register(Node(node_dict=d, x=x, y=y,
                                   display_name=label,
                                   is_sofistik=sofistik))

    def add_zero_touch_varargs(self,
                               function_signature: str,
                               in_ports: list[tuple[str, str]],
                               out_ports: list[tuple[str, str]],
                               description: str = "",
                               x: float = 0, y: float = 0,
                               sofistik: bool = False,
                               label: str | None = None) -> Node:
        """Variadic Zero-Touch function (e.g. List.Join). in_ports must be the
        materialized port list — typically [(\"list0\", ...), (\"list1\", ...), ...]."""
        nid = new_id()
        d = {
            "ConcreteType": "Dynamo.Graph.Nodes.ZeroTouch.DSVarArgFunction, DynamoCore",
            "FunctionSignature": function_signature,
            "FunctionType": "VariableArgument",
            "Id": nid,
            "NodeType": "FunctionNode",
            "Inputs":  [_port(n, desc) for (n, desc) in in_ports],
            "Outputs": [_port(n, desc) for (n, desc) in out_ports],
            "Replication": "Disabled",
            "Description": description or function_signature,
        }
        if label is None:
            sig = function_signature.split("@")[0]
            parts = sig.split(".")
            label = ".".join(parts[-2:]) if len(parts) >= 2 else sig
        return self._register(Node(node_dict=d, x=x, y=y,
                                   display_name=label,
                                   is_sofistik=sofistik))

    def add_python(self,
                   code: str,
                   n_inputs: int = 1,
                   x: float = 0, y: float = 0,
                   label: str = "Python Script",
                   description: str = "Runs an embedded Python script.",
                   strict: bool = True) -> Node:
        """CPython3 Python Script node.

        `code` should be the raw script (use plain \\n line endings; the
        builder normalizes to \\r\\n on serialization).

        If `strict` is True (default), the code is scanned for known
        Revit 2024+ API breaking changes and raises ValueError on a hit.
        Pass `strict=False` to skip the check (only do this if you are
        intentionally targeting an older Revit API).

        Units warnings (potential missing UnitUtils conversion at the
        SOFiSTiK ↔ Revit boundary) are printed to stderr but do not block
        the build. They are heuristics; review them and either add the
        conversion or accept the warning if it's a false positive."""
        import sys as _sys
        if strict:
            problems = _lint_python_for_revit_2024(code)
            if problems:
                raise ValueError(
                    "Python code uses deprecated Revit API:\n  - "
                    + "\n  - ".join(problems)
                    + "\nSee references/python_node.md → 'Revit 2024+ API breaking changes'."
                )
            unit_warnings = _lint_python_for_units(code)
            for w in unit_warnings:
                print(f"[build_dyn] WARNING in '{label}': {w}", file=_sys.stderr)
        nid = new_id()
        # normalize line endings to \r\n (matches what Dynamo writes)
        normalized = code.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
        d = {
            "ConcreteType": "PythonNodeModels.PythonNode, PythonNodeModels",
            "Code": normalized,
            "Engine": "CPython3",
            "VariableInputPorts": True,
            "Id": nid,
            "NodeType": "PythonScriptNode",
            "Inputs": [_port(f"IN[{i}]", f"Input #{i}") for i in range(n_inputs)],
            "Outputs": [_port("OUT", "Result of the python script")],
            "Replication": "Disabled",
            "Description": description,
        }
        return self._register(Node(node_dict=d, x=x, y=y, display_name=label))

    def add_watch(self,
                  label: str = "Watch",
                  x: float = 0, y: float = 0,
                  player_output: bool = False) -> Node:
        nid = new_id()
        d = {
            "ConcreteType": "CoreNodeModels.Watch, CoreNodeModels",
            "WatchWidth": 200.0,
            "WatchHeight": 200.0,
            "Id": nid,
            "NodeType": "ExtensionNode",
            "Inputs":  [_port("", "Node to show output from")],
            "Outputs": [_port("", "Node output")],
            "Replication": "Disabled",
            "Description": "Visualizes a node's output",
        }
        return self._register(Node(node_dict=d, x=x, y=y,
                                   display_name=label,
                                   is_player_output=player_output))

    def add_categories(self, selected: str = "OST_AnalyticalMember",
                       x: float = 0, y: float = 0,
                       label: str = "Categories") -> Node:
        """Categories dropdown. `selected` is the OST_* string."""
        nid = new_id()
        d = {
            "ConcreteType": "DSRevitNodesUI.Categories, DSRevitNodesUI",
            "SelectedIndex": 0,   # Revit ignores this if SelectedString matches
            "SelectedString": selected,
            "Id": nid,
            "NodeType": "ExtensionNode",
            "Inputs": [],
            "Outputs": [_port("Category", "The selected category")],
            "Replication": "Disabled",
            "Description": "All built-in categories.",
        }
        return self._register(Node(node_dict=d, x=x, y=y, display_name=label))

    def add_elements_of_category(self, x: float = 0, y: float = 0,
                                 label: str = "All Elements of Category") -> Node:
        nid = new_id()
        d = {
            "ConcreteType": "DSRevitNodesUI.ElementsOfCategory, DSRevitNodesUI",
            "Id": nid,
            "NodeType": "ExtensionNode",
            "Inputs":  [_port("Category", "The Category")],
            "Outputs": [_port("Elements", "An element class.")],
            "Replication": "Disabled",
            "Description": "Get all elements of the specified category from the model.",
        }
        return self._register(Node(node_dict=d, x=x, y=y, display_name=label))

    def add_select_model_elements(self, category: str = "OST_AnalyticalMember",
                                  x: float = 0, y: float = 0,
                                  label: str = "Select Model Elements By Category",
                                  excluded: bool = False) -> Node:
        nid = new_id()
        d = {
            "ConcreteType": "Dynamo.ComboNodes.DSModelElementsByCategorySelection, DSRevitNodesUI",
            "SelectedIndex": 0,
            "SelectedString": category,
            "NodeType": "ExtensionNode",
            "InstanceId": [],
            "Id": nid,
            "Inputs": [],
            "Outputs": [_port("Elements", "The selected elements")],
            "Replication": "Disabled",
            "Description": "Select multiple elements from the Revit document filtered by Category.",
        }
        node = Node(node_dict=d, x=x, y=y, display_name=label, excluded=excluded)
        return self._register(node)

    # ---------- connectors ----------

    def connect(self, src: Node, src_port: str, dst: Node, dst_port: str) -> dict:
        c = {
            "Start": src.output_port_id(src_port),
            "End":   dst.input_port_id(dst_port),
            "Id":    new_id(),
            "IsHidden": "False",
        }
        self.connectors.append(c)
        return c

    # ---------- groups ----------

    def group(self, title: str, nodes: list[Node],
              color: str = "neutral",
              description: str = "") -> dict:
        """Create a group annotation enclosing the given nodes. The bounding
        box is computed from node coordinates with margin for the title bar."""
        if not nodes:
            raise ValueError("Group must contain at least one node")
        bg = GROUP_COLORS.get(color, color if color.startswith("#") else GROUP_COLORS["neutral"])
        # Approximate node footprint: ~330 wide, ~120 tall (Dynamo defaults).
        # Title bar adds ~110 px on top.
        node_w, node_h = 330.0, 120.0
        margin_x, margin_y = 30.0, 30.0
        title_bar = 110.0
        xs = [n.x for n in nodes]
        ys = [n.y for n in nodes]
        left   = min(xs) - margin_x
        top    = min(ys) - margin_y - title_bar
        right  = max(xs) + node_w + margin_x
        bottom = max(ys) + node_h + margin_y
        ann = {
            "Id": new_guid(),
            "Title": title,
            "DescriptionText": description,
            "IsExpanded": True,
            "WidthAdjustment": 0.0,
            "HeightAdjustment": 0.0,
            "Nodes": [n.id for n in nodes],
            "HasNestedGroups": False,
            "Left": left,
            "Top":  top,
            "Width":  right - left,
            "Height": bottom - top,
            "FontSize": 36.0,
            "GroupStyleId": "00000000-0000-0000-0000-000000000000",
            "InitialTop":    min(ys),
            "InitialHeight": (bottom - top) - title_bar,
            "TextblockHeight": title_bar,
            "Background": bg,
        }
        self.annotations.append(ann)
        return ann

    # ---------- player flag toggles ----------

    def mark_player_input(self, node: Node, label: str | None = None,
                          description: str | None = None) -> None:
        node.is_player_input = True
        if label is not None:
            node.display_name = label
        if description is not None:
            node.player_input_description = description

    def mark_player_output(self, node: Node, label: str | None = None) -> None:
        node.is_player_output = True
        if label is not None:
            node.display_name = label

    # ---------- serialization ----------

    def _build_top_level_inputs(self) -> list[dict]:
        out = []
        for n in self.nodes:
            if not n.is_player_input:
                continue
            out.append({
                "Id":   n.id,
                "Name": n.display_name,
                "Type":  n.player_input_type,
                "Type2": n.player_input_type,
                "Value": n.player_input_value if n.player_input_value is not None else "",
                "Description": n.player_input_description or "",
            })
        return out

    def _build_top_level_outputs(self) -> list[dict]:
        out = []
        for n in self.nodes:
            if not n.is_player_output:
                continue
            out.append({
                "Id":   n.id,
                "Name": n.display_name,
                "Type": "unknown",
                "InitialValue": "",
                "Description": "Visualizes a node's output",
            })
        return out

    def _build_node_views(self) -> list[dict]:
        return [{
            "Id":   n.id,
            "Name": n.display_name or n.node_dict.get("Description", ""),
            "IsSetAsInput":  n.is_player_input,
            "IsSetAsOutput": n.is_player_output,
            "Excluded": n.excluded,
            "ShowGeometry": n.show_geometry,
            "X": float(n.x),
            "Y": float(n.y),
        } for n in self.nodes]

    def _build_dependencies(self) -> list[dict]:
        deps: list[dict] = []
        sof_nodes = [n.id for n in self.nodes if n.is_sofistik]
        if sof_nodes:
            deps.append({
                "Name": "SOFiSTiK Analysis + Design",
                "Version": self.sofistik_package_version,
                "ReferenceType": "Package",
                "Nodes": sof_nodes,
            })
        for nid, label in self.external_files:
            deps.append({
                "Name": label,
                "ReferenceType": "External",
                "Nodes": [nid],
            })
        return deps

    def to_dict(self) -> dict:
        return {
            "Uuid": self.uuid,
            "IsCustomNode": False,
            "Description": self.description,
            "Name": self.name,
            "ElementResolver": {"ResolutionMap": {}},
            "Inputs":  self._build_top_level_inputs(),
            "Outputs": self._build_top_level_outputs(),
            "Nodes": [n.node_dict for n in self.nodes],
            "Connectors": self.connectors,
            "Dependencies": [],
            "NodeLibraryDependencies": self._build_dependencies(),
            "EnableLegacyPolyCurveBehavior": True,
            "Thumbnail": "",
            "GraphDocumentationURL": None,
            "ExtensionWorkspaceData": [
                {"ExtensionGuid": "28992e1d-abb9-417f-8b1b-05e053bee670",
                 "Name": "Properties", "Version": "3.3", "Data": {}},
                {"ExtensionGuid": "DFBD9CC0-DB40-457A-939E-8C8555555A9D",
                 "Name": "Generative Design", "Version": "8.2", "Data": {}},
            ],
            "Author": "",
            "Linting": {
                "activeLinter": "None",
                "activeLinterId": "7b75fb44-43fd-4631-a878-29f4d5d8399a",
                "warningCount": 0, "errorCount": 0,
            },
            "Bindings": [],
            "View": {
                "Dynamo": {
                    "ScaleFactor": 1.0,
                    "HasRunWithoutCrash": True,
                    "IsVisibleInDynamoLibrary": True,
                    "Version": "3.2.2.5494",
                    "RunType": "Manual",
                    "RunPeriod": "1000",
                },
                "Camera": {
                    "Name": "_Background Preview",
                    "EyeX": -17.0, "EyeY": 24.0, "EyeZ": 50.0,
                    "LookX": 12.0, "LookY": -13.0, "LookZ": -58.0,
                    "UpX": 0.0, "UpY": 1.0, "UpZ": 0.0,
                },
                "ConnectorPins": [],
                "NodeViews": self._build_node_views(),
                "Annotations": self.annotations,
                "X": 100.0, "Y": 400.0, "Zoom": 0.5,
            },
        }

    def save(self, path: str) -> None:
        import os
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    # ---------- self-validation ----------

    def validate(self) -> list[str]:
        """Returns a list of warning/error strings. Empty list means OK.
        Run before save() during development to catch obvious issues."""
        problems: list[str] = []
        # 1. Every Inputs/Outputs port id is unique
        port_ids: dict[str, str] = {}
        for n in self.nodes:
            for p in n.node_dict.get("Inputs", []) + n.node_dict.get("Outputs", []):
                if p["Id"] in port_ids:
                    problems.append(f"Duplicate port id {p['Id'][:8]} on nodes "
                                    f"{port_ids[p['Id']][:8]} and {n.id[:8]}")
                port_ids[p["Id"]] = n.id
        # 2. Every connector references existing port ids
        for c in self.connectors:
            if c["Start"] not in port_ids:
                problems.append(f"Connector {c['Id'][:8]} Start port {c['Start'][:8]} unknown")
            if c["End"] not in port_ids:
                problems.append(f"Connector {c['Id'][:8]} End   port {c['End'][:8]} unknown")
        # 3. Annotation node refs exist
        node_ids = {n.id for n in self.nodes}
        for a in self.annotations:
            for nid in a["Nodes"]:
                if nid not in node_ids:
                    problems.append(f"Annotation '{a['Title']}' references unknown node {nid[:8]}")
        # 4. Every Player input has both flag + top-level entry (built lazily, so just sanity)
        for n in self.nodes:
            if n.is_player_input and not n.display_name:
                problems.append(f"Player input node {n.id[:8]} has empty display name")
            if n.is_player_output and not n.display_name:
                problems.append(f"Player output node {n.id[:8]} has empty display name")
        return problems
