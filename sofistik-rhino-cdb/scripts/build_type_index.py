#!/usr/bin/env python3
"""Regenerate references/cdb_type_index.md from SOFiSTiK.Analysis.Database.xml.

The assembly XML documents every Cdb* type with a summary of the form

    <kwh>/<kwl>[:sel1[:sel2]]  <description>

which is effectively the address book for the whole database: it tells you
which managed type comes back from ReadData(kwh, kwl) and which selector
distinguishes it from the other types stored at the same key.

Usage:
    python build_type_index.py <path-to-xml> [-o <output.md>]
"""

import argparse
import re
import xml.etree.ElementTree as ET
from collections import defaultdict

# KWH blocks, in the order SOFiSTiK groups them. (low, high, title)
BLOCKS = [
    (-999, -1, "Internal / index records"),
    (0, 9, "Global control, materials, soil, axes, areas, sections"),
    (10, 19, "System, groups, load cases, construction stages, masses"),
    (20, 29, "Nodes and nodal results"),
    (30, 49, "Structural elements (points/lines/areas/volumes), design elements, tendons"),
    (61, 99, "Design cases, design status, time history, storeys"),
    (100, 119, "Beams: geometry, loads, forces, stresses, reinforcement"),
    (120, 139, "Design elements (DSLN)"),
    (140, 149, "External sections (BSCT)"),
    (150, 199, "Trusses, cables, springs, dampers, masses, boundaries, links"),
    (200, 299, "QUAD elements: geometry, loads, forces, stresses, reinforcement"),
    (300, 399, "BRIC elements"),
    (400, 999, "Piles, pipes, hydraulic links, segments"),
    (1000, 9999, "Sub-data and extended result records"),
]

# Types worth surfacing in the quick-reference table at the top.
QUICK = [
    "CdbSyst", "CdbGrp", "CdbLc_ctrl",
    "CdbNode", "CdbN_disp", "CdbN_dispc",
    "CdbBeam", "CdbBeam_sct", "CdbBeam_tnd", "CdbBeam_for", "CdbBeam_foc",
    "CdbBeam_str", "CdbBeam_stc",
    "CdbTrus", "CdbTrus_res", "CdbCabl", "CdbCabl_res",
    "CdbSpri", "CdbSpri_res", "CdbBoun", "CdbBoun_res",
    "CdbQuad", "CdbQuad_for", "CdbQuad_foc", "CdbQuad_str", "CdbQuad_stc",
    "CdbBric", "CdbBric_str",
    "CdbSect", "CdbSect_ppt", "CdbSect_spt",
    "CdbAxis", "CdbAxis_geo", "CdbTendon", "CdbTendaxis",
    "CdbMat",
]

SUMMARY_RE = re.compile(r"^(-?\d+)/(\S+)\s*(.*)$")


def parse(xml_path):
    """Return {short_type_name: (kwh, kwl_spec, description)}."""
    root = ET.parse(xml_path).getroot()
    out = {}
    for member in root.iter("member"):
        name = member.get("name", "")
        if not name.startswith("T:"):
            continue
        short = name.split(".")[-1]
        summary = " ".join((member.findtext("summary") or "").split())
        m = SUMMARY_RE.match(summary)
        if not m:
            continue  # DataAccess itself, and a handful of prose-only summaries
        out[short] = (int(m.group(1)), m.group(2), m.group(3))
    return out


def split_kwl(kwl_spec):
    """'00:+' -> ('00', '+');  'LC:Z!' -> ('LC', 'Z!');  'NR' -> ('NR', '')."""
    head, _, sel = kwl_spec.partition(":")
    return head, sel


def render(types):
    by_kwh = defaultdict(list)
    for short, (kwh, kwl_spec, desc) in types.items():
        by_kwh[kwh].append((kwl_spec, short, desc))

    L = []
    L.append("# CDB type index (KWH / KWL -> managed type)\n")
    L.append(
        "Generated from `SOFiSTiK.Analysis.Database.xml` by "
        "`scripts/build_type_index.py`. Do not hand-edit.\n"
    )
    L.append("## How to read this table\n")
    L.append(
        "Every row is one managed type and the database address it lives at:\n\n"
        "```\nkwh / kwl [: selector1 [: selector2]]\n```\n\n"
        "- **kwh** - primary key, passed as the first argument to `ReadData`.\n"
        "- **kwl** - secondary key, passed as the second argument. A literal number "
        "means exactly that value. `LC` means *any load case number*, `NR` *any "
        "element/section number*, `ID` a 4-character string key (use the "
        "`ReadData(int, string)` overload).\n"
        "- **selector** - the value of the record's first (and sometimes second) "
        "integer item. This is what distinguishes several types stored at the *same* "
        "key. `+` positive, `-` negative, `0` zero, `Z!` any non-zero, `*` anything, "
        "`?` a wildcard digit.\n\n"
        "You never pass the selector to `ReadData`. It is resolved for you by "
        "`.OfType<T>()`, which is why filtering is mandatory rather than cosmetic:\n\n"
        "```csharp\n"
        "// 100/00 holds BOTH CdbBeam (selector +) and CdbBeam_sct (selector 0)\n"
        "var beams    = db.ReadData(100, 0).OfType<CdbBeam>().ToList();\n"
        "var sections = db.ReadData(100, 0).OfType<CdbBeam_sct>().ToList();\n"
        "```\n\n"
        "For results, the load case number *is* the KWL:\n\n"
        "```csharp\n"
        "var forces = db.ReadData(102, loadcase).OfType<CdbBeam_for>().ToList();\n"
        "```\n"
    )

    L.append("## Quick reference - the records you will actually use\n")
    L.append("| Type | KWH/KWL | What it is |")
    L.append("|---|---|---|")
    for short in QUICK:
        if short not in types:
            continue
        kwh, kwl_spec, desc = types[short]
        L.append(f"| `{short}` | `{kwh}/{kwl_spec}` | {desc} |")
    L.append("")

    L.append("## Full index by KWH\n")
    seen = set()
    for lo, hi, title in BLOCKS:
        keys = sorted(k for k in by_kwh if lo <= k <= hi and k not in seen)
        if not keys:
            continue
        seen.update(keys)
        L.append(f"### {lo}-{hi} &mdash; {title}\n")
        L.append("| KWH/KWL | Type | Description |")
        L.append("|---|---|---|")
        for kwh in keys:
            for kwl_spec, short, desc in sorted(by_kwh[kwh]):
                L.append(f"| `{kwh}/{kwl_spec}` | `{short}` | {desc} |")
        L.append("")

    leftover = sorted(k for k in by_kwh if k not in seen)
    if leftover:
        L.append("### Unclassified\n")
        L.append("| KWH/KWL | Type | Description |")
        L.append("|---|---|---|")
        for kwh in leftover:
            for kwl_spec, short, desc in sorted(by_kwh[kwh]):
                L.append(f"| `{kwh}/{kwl_spec}` | `{short}` | {desc} |")
        L.append("")

    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("xml")
    ap.add_argument("-o", "--output", default="references/cdb_type_index.md")
    args = ap.parse_args()

    types = parse(args.xml)
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(render(types))
    print(f"{len(types)} types -> {args.output}")


if __name__ == "__main__":
    main()
