#!/usr/bin/env python3
"""Pull the field definitions for a CDB record out of cdbase.txt.

cdbase.txt is ~25k lines, so never read it whole. Query it instead:

    python lookup_record.py 102/LC        # by key
    python lookup_record.py CdbBeam_for   # by managed type name
    python lookup_record.py BEAM_FOR      # by cdbase mnemonic
    python lookup_record.py 24            # every record under KWH 24
    python lookup_record.py --list 200    # just the headers under KWH 200

Output is the record header(s) plus the item table, with the SOFiSTiK
help-file markup stripped. Item lines look like:

    @1:  N   [1101] |normal force

    @n=  identifier integer     @n#  integer        @n:  float
    @n+  float, additive on merge              @n~  float, averaged on merge
    [1101] etc. are unit codes - see references/units.md
    2[int] / 3[-,-,-] etc. are arrays; the managed type exposes them as
    fixed-length arrays (CdbBeam.Node[2], CdbBeam.T[9], CdbNode.Xyz[3])
"""

import argparse
import os
import re
import sys

DEFAULT_CDBASE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "cdbase.txt",
)

MARKUP = re.compile(r"\{/?(?:red|blue|green|link|-link|version)\}")
REC_RE = re.compile(r"@Rec::?\s*(-?\d+|ANY)/(\S+)\s+([A-Z0-9_]+)?")


def load(path):
    with open(path, encoding="cp1252", errors="replace") as fh:
        return fh.read().replace("\r", "").split("\n")


def blocks(lines):
    """Yield (header_specs, start, end) for every {red}-delimited record block."""
    starts = [i for i, l in enumerate(lines) if l.startswith("{red}")]
    for a, b in zip(starts, starts[1:] + [len(lines)]):
        specs = []
        for i in range(a, b):
            line = lines[i]
            if "@Rec:" not in line:
                continue
            m = REC_RE.search(line)
            if m:
                kwh, kwl, mnem = m.group(1), m.group(2), m.group(3) or ""
                specs.append((kwh, kwl, mnem, line.strip()))
        if specs:
            yield specs, a, b


def norm_kwh(k):
    try:
        return str(int(k))
    except ValueError:
        return k.upper()


def type_to_mnemonic(q):
    """CdbBeam_for -> BEAM_FOR"""
    return q[3:].upper() if q.lower().startswith("cdb") else q.upper()


def matches(specs, query, loose=False):
    q = query.strip()
    qm = type_to_mnemonic(q)

    # key query: 102, 102/LC, 024/LC:+
    key = q.replace(" ", "")
    if re.match(r"^-?\d+(/|$)", key):
        want_kwh, _, want_kwl = key.partition("/")
        want_kwh = norm_kwh(want_kwh)
        for kwh, kwl, mnem, _raw in specs:
            if norm_kwh(kwh) != want_kwh:
                continue
            if not want_kwl:
                return True
            if kwl.upper().startswith(want_kwl.upper()):
                return True
        return False

    # mnemonic / type-name query. Exact first; the loose pass only runs when
    # nothing matched exactly, which covers mnemonics the managed type truncates
    # (CdbMat_flui -> MAT_FLUID) and bare-prefix exploration (BEAM -> BEAM_*).
    for _kwh, _kwl, mnem, _raw in specs:
        if not mnem:
            continue
        if mnem == qm:
            return True
        if loose and (mnem.startswith(qm) or qm.startswith(mnem)):
            return True
    return False


def clean(segment):
    out = []
    for line in segment:
        line = MARKUP.sub("", line).rstrip()
        if line.strip() in ("", ";"):
            if out and out[-1] == "":
                continue
            out.append("")
        else:
            out.append(line)
    while out and out[-1] == "":
        out.pop()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", help="KWH, KWH/KWL, mnemonic, or CdbType name")
    ap.add_argument("--cdbase", default=DEFAULT_CDBASE,
                    help="path to cdbase.txt (defaults to the bundled copy)")
    ap.add_argument("--list", action="store_true",
                    help="print only the matching record headers, not the fields")
    ap.add_argument("--max-blocks", type=int, default=12,
                    help="stop after this many matching blocks")
    args = ap.parse_args()

    if not os.path.exists(args.cdbase):
        sys.exit(
            f"cdbase.txt not found at {args.cdbase}. It ships with this skill at "
            "assets/cdbase.txt - restore it, or pass --cdbase <path>."
        )

    lines = load(args.cdbase)
    all_blocks = list(blocks(lines))

    for loose in (False, True):
        hits = [blk for blk in all_blocks if matches(blk[0], args.query, loose)]
        if hits:
            break

    if not hits:
        sys.exit(f"no record matched {args.query!r}")

    if loose:
        print(f"; no exact match for {args.query!r} - showing near matches\n")

    for n, (specs, a, b) in enumerate(hits, 1):
        if n > args.max_blocks:
            print(f"\n... {len(hits) - args.max_blocks} more matches suppressed "
                  f"(--max-blocks)")
            break
        if args.list:
            for _kwh, _kwl, _mnem, raw in specs:
                print(MARKUP.sub("", raw))
        else:
            print("\n".join(clean(lines[a:b])))
            print("\n" + "-" * 72 + "\n")


if __name__ == "__main__":
    main()
