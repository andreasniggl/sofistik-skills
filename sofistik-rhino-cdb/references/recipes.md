# Recipes

Verified snippets per record. Field names below are confirmed against working
scripts and `cdbase.txt`; anything not listed here, look up with
`scripts/lookup_record.py` before using it.

All snippets assume `database` is an open `DataAccess` and the usings from
`references/environments.md` are in place.

**If a property name does not compile**, the record almost certainly has it under
a slightly different spelling - `cdbase.txt` occasionally abbreviates. Dump the
real members from inside the script rather than guessing again:

```csharp
var members = string.Join("\n", typeof(CdbBeam_for)
    .GetFields()
    .Select(f => $"{f.Name} : {f.FieldType.Name}"));
// send `members` to an output, or RhinoApp.WriteLine(members)
```

Contents: [explicit type dispatcher](#the-explicit-type-dispatcher) -
[load cases](#load-cases) - [groups](#groups) -
[nodes and beams](#nodes-and-beams) - [nodal displacements and reactions](#nodal-displacements-and-support-reactions) -
[beam forces](#beam-forces) - [beam stresses](#beam-stresses) -
[quads](#quad-elements-and-results) - [cross sections](#cross-section-polygons) -
[tendons](#tendon-geometry) - [springs](#springs)

---

## The explicit type dispatcher

`ReadData(kwh, kwl)` resolves which managed type each raw record becomes through
an internal lookup table keyed by kwh/kwl. Not every key is registered. An
unregistered key throws

> *"For the given kwh/kwl combination …, type dispatcher must be defined explicitly."*

and the fix is the third overload, which takes the mapping as a lambda:

```csharp
public List<ICdbElement> ReadData(int kwh, int kwl, Func<int, int, Type> elementTypeFactory)
```

The lambda receives the record's **first two integers** (`id0`, `id1`) and
returns the concrete `Cdb*` type to marshal the record into - or `null` to skip
the record entirely. These two integers are exactly the *selectors* in
`cdb_type_index.md`, so the selector column tells you how to write the lambda:

```csharp
// 170/00 holds only CdbSpri - constant mapping
var springs = database
    .ReadData(170, 0, (id0, id1) => typeof(CdbSpri))
    .OfType<CdbSpri>()
    .ToList();

// A key with selector 0 and selector + records - switch on id0,
// mirroring the internal table's own dispatchers:
var results = database.ReadData(kwh, lc, (id0, id1) =>
{
    switch (id0)
    {
        case 0:                     return typeof(CdbSpri_re0);   // selector 0
        case int i when (i > 0):    return typeof(CdbSpri_res);   // selector +
        default:                    return null;                  // skip
    }
});
```

Keep the trailing `.OfType<T>()` even with a constant lambda: the overload
returns `List<ICdbElement>`, and the filter also drops any record the lambda
mapped to a different type.

Three rules for writing the lambda:

- **Derive it from the selector column** of `cdb_type_index.md`, never from
  guesswork. `+` means `id0 > 0`, `0` means `id0 == 0`, `-` means `id0 < 0`,
  `Z!` any non-zero, a second selector constrains `id1` the same way.
- **Return `null` for anything you did not ask for.** A wrong type here does not
  fail loudly - it marshals the bytes into the wrong struct layout and produces
  plausible-looking garbage numbers.
- **If the mapping is not obvious** - the selector column is ambiguous, the key
  is missing from the index, or several types overlap - **ask the user how the
  id0/id1 → type mapping should look** rather than inventing one. They can read
  it off the internal table or the `cdbase.txt` record description.

There is also a generic `ReadData<T>(kwh, kwl)` in the assembly, but it is
`internal` - scripts cannot call it. The lambda overload is the public route.

Known keys that need the explicit dispatcher: `170/0` (`CdbSpri` - spring
definitions; at KWH 170 the kwl doubles as the load case of the result records,
so kwl 0 is ambiguous to the internal table).

---

## Load cases

Results are keyed by load case, so this is usually the first component in a
definition: it feeds a dropdown that drives everything else.

`GetSecondaryKeysOf(kwh)` lists the KWLs that actually exist under a KWH, so ask
the *result* key you care about - that way the list only contains load cases that
have those results:

```csharp
var beamForceLoadcases = database.GetSecondaryKeysOf(102);  // beam forces
var nodalLoadcases     = database.GetSecondaryKeysOf(24);   // displacements/reactions
var stressLoadcases    = database.GetSecondaryKeysOf(105);  // beam stresses
```

`12/LC` holds the description. `CdbLc_ctrl.Rtex` is the load case name as a
string, which makes a far better dropdown than a bare number:

```csharp
var labels = new List<string>();
var numbers = new List<int>();

foreach (int lc in database.GetSecondaryKeysOf(102))
{
    var info = database.ReadData(12, lc).OfType<CdbLc_ctrl>().FirstOrDefault();
    numbers.Add(lc);
    labels.Add(info != null ? $"{lc} - {info.Rtex}" : lc.ToString());
}
```

`CdbLc_ctrl` also carries `Kind` (0 linear, 1 nonlinear, 2 superposition,
4 eigenmode, 5 buckling, 6 design) and `Fact`, the load case factor.

**Trap:** use `FirstOrDefault`, not `Single`. `12/LC` can hold several records
under one load case.

---

## Groups

`11/0` -> `CdbGrp`. One record per (group, element type) pair, which is how you
restrict an import to one part of the model.

| Field | Meaning |
|---|---|
| `Ng` | group number |
| `Typ` | element type: 20 nodes, 100 beams, 150 truss, 160 cable, 170 spring, 180 boundary, 190 link, 200 quad, 300 bric |
| `Num` | number of elements of this type |
| `Min`, `Max` | lowest / highest element number in the group |
| `Mnr`, `Mbw` | material and reinforcement material number |

```csharp
var group = database.ReadData(11, 0).OfType<CdbGrp>()
    .FirstOrDefault(g => g.Typ == 100 && g.Ng == groupId);

if (group == null)
    throw new InvalidOperationException($"No beam group {groupId} in this model.");

var beamsInGroup = database.ReadData(100, 0).OfType<CdbBeam>()
    .Where(b => b.Nr >= group.Min && b.Nr <= group.Max)
    .ToList();
```

**Trap:** `Min`/`Max` is a *range*, not a list - numbering inside it has gaps.
Filter or `TryGetValue` rather than looping `for (id = Min; id <= Max; id++)` and
assuming every id resolves. And guard the lookup: filtering a list down to
nothing and then taking `[0]` throws.

---

## Nodes and beams

`20/0` -> `CdbNode`, `100/0` -> `CdbBeam` (plus `CdbBeam_sct`, the section
assignments, at the same key).

| Type | Field | Meaning | Unit |
|---|---|---|---|
| `CdbNode` | `Nr` | node number | - |
| | `Inr` | internal number; 0 means the node is inactive | - |
| | `Kfix` | support condition bit code: 1 uX, 2 uY, 4 uZ, 8 phiX, 16 phiY, 32 phiZ, 64 warping | - |
| | `Xyz[3]` | global coordinates | m |
| `CdbBeam` | `Nr` | beam number | - |
| | `Node[2]` | start / end node number | - |
| | `Dl` | beam length | m |
| | `T[9]` | transformation matrix, three column vectors | - |
| | `Ex[6]` | eccentricity, local xyz at start then at end | m |
| | `Nref` | reference axis number | - |
| | `Spar[2]` | station of start / end along the reference axis | - |

```csharp
var nodesByNr = database.ReadData(20, 0).OfType<CdbNode>().ToDictionary(n => n.Nr);
var beams     = database.ReadData(100, 0).OfType<CdbBeam>().ToList();

var lines = new List<Line>();
var ids   = new List<int>();

foreach (var beam in beams)
{
    if (!nodesByNr.TryGetValue(beam.Node[0], out var n0)) continue;
    if (!nodesByNr.TryGetValue(beam.Node[1], out var n1)) continue;

    lines.Add(new Line(
        new Point3d(n0.Xyz[0], n0.Xyz[1], n0.Xyz[2]),
        new Point3d(n1.Xyz[0], n1.Xyz[1], n1.Xyz[2])));
    ids.Add(beam.Nr);
}
```

### The T matrix

Nine floats, **three column vectors**, each a local axis expressed in global
coordinates:

- `T[0..2]` local x - the beam axis
- `T[3..5]` local y
- `T[6..8]` local z

To place a point given in beam-local coordinates into the global frame:

```csharp
double gx = n0.Xyz[0] + x * beam.T[0] + y * beam.T[3] + z * beam.T[6];
double gy = n0.Xyz[1] + x * beam.T[1] + y * beam.T[4] + z * beam.T[7];
double gz = n0.Xyz[2] + x * beam.T[2] + y * beam.T[5] + z * beam.T[8];
```

`Ex` (eccentricity from the nodes to the beam axis) is ignored above. It is zero
in most models; if the model uses it, add `Ex[0..2]` at the start, `Ex[3..5]` at
the end, interpolated by `x / beam.Dl`.

**Local z is down-positive.** A point at local `z = +0.3` sits 0.3 m *below* the
beam axis.

---

## Nodal displacements and support reactions

`24/LC` -> `CdbN_disp`. One record per node per load case, but **only for nodes
that have something to report**.

| Field | Meaning | Unit |
|---|---|---|
| `Nr` | node number | - |
| `Ux`, `Uy`, `Uz` | displacement, global | **m** |
| `Urx`, `Ury`, `Urz` | rotation, global | **rad** |
| `Px`, `Py`, `Pz` | support reaction force | kN |
| `Mx`, `My`, `Mz` | support reaction moment | kNm |

Displacements are in metres even though SOFiSTiK prints millimetres. Multiply by
1000 for mm.

Deformed shape:

```csharp
var dispByNr = database.ReadData(24, loadcase).OfType<CdbN_disp>()
    .ToDictionary(d => d.Nr);

Point3d Deformed(CdbNode n)
{
    double dx = 0, dy = 0, dz = 0;
    if (dispByNr.TryGetValue(n.Nr, out var d))
    {
        dx = d.Ux * scale;
        dy = d.Uy * scale;
        dz = d.Uz * scale;
    }
    return new Point3d(n.Xyz[0] + dx, n.Xyz[1] + dy, n.Xyz[2] + dz);
}
```

Support reactions - keep only nodes that actually carry one:

```csharp
var reactions = database.ReadData(24, loadcase).OfType<CdbN_disp>()
    .Where(r => r.Nr != 0 && Math.Abs(r.Pz) > 1e-9)
    .ToList();
```

**Traps.** The `Nr == 0` record is a summary row, not a node - always exclude it.
A node with no record is undeformed, not an error, so `TryGetValue` with a zero
fallback rather than `Single()`. And the reaction fields are only meaningful at
supported nodes; elsewhere they are zero or absent.

For the extreme values across all nodes, `24/LC:0` -> `CdbN_dispc` holds the
maxima directly - cheaper than scanning.

---

## Beam forces

`102/LC` -> `CdbBeam_for`. Several records per beam: one per output section along
its length.

| Field | Meaning | Unit |
|---|---|---|
| `Nr` | beam number | - |
| `X` | distance from the beam start | m |
| `N` | normal force | kN |
| `Vy`, `Vz` | shear force | kN |
| `Mt`, `Mt2` | torsional moment, secondary torsion | kNm |
| `My`, `Mz` | bending moment | kNm |
| `Mb` | warping bimoment | kNm2 |
| `Ux`, `Uy`, `Uz` | displacement in **local** beam coordinates | m |

```csharp
var beamsByNr = database.ReadData(100, 0).OfType<CdbBeam>().ToDictionary(b => b.Nr);
var nodesByNr = database.ReadData(20, 0).OfType<CdbNode>().ToDictionary(n => n.Nr);

var forces = database.ReadData(102, loadcase).OfType<CdbBeam_for>()
    .Where(f => f.Nr > 0)
    .OrderBy(f => f.Nr).ThenBy(f => f.X)
    .ToList();

var pts = new List<Point3d>();
var my  = new List<double>();

foreach (var f in forces)
{
    if (!beamsByNr.TryGetValue(f.Nr, out var beam)) continue;
    if (!nodesByNr.TryGetValue(beam.Node[0], out var n0)) continue;

    // walk f.X along the beam axis = first column of T
    pts.Add(new Point3d(
        n0.Xyz[0] + f.X * beam.T[0],
        n0.Xyz[1] + f.X * beam.T[1],
        n0.Xyz[2] + f.X * beam.T[2]));
    my.Add(f.My);
}
```

**Traps.** A negative `Nr` marks the left side of a discontinuity - two records
share one station, one per side of a jump. Filter to `Nr > 0` for a plain
diagram, keep both when the jump is the point. Sort by `(Nr, X)`; storage order
is not guaranteed. For extremes only, `102/LC:0` -> `CdbBeam_foc` has them
precomputed.

`112/LC` -> `CdbBeam_ftr` is the same layout without plate contributions - for a
T-beam in a slab, `102` includes the plate part and `112` does not.

---

## Beam stresses

`105/LC` -> `CdbBeam_str`. Several records per beam section, one per stress point
or material part.

| Field | Meaning | Unit |
|---|---|---|
| `Nr` | beam number | - |
| `Mnr` | material number, **or** a maxima flag - see below | - |
| `X` | distance from the beam start | m |
| `Sigc` | compressive (minimum) stress | **kN/m2** |
| `Sigt` | tensile (maximum) stress | **kN/m2** |
| `Tau` | shear stress | kN/m2 |
| `Sigv` | reference / comparison stress | kN/m2 |
| `Si`, `Sii` | principal tensile / compressive stress | kN/m2 |

Stresses are stored in kN/m2. Divide by 1000 for N/mm2 (= MPa), which is what
anyone reading the output expects.

`Mnr` is overloaded: normally the material number, but these values flag
precomputed maxima:

- `1024` - maximum values for the solid section material
- `2048` - maximum values for tendons
- `3072` - maximum values for reinforcement

So filtering to the solid-section envelope means selecting on those flags:

```csharp
var stresses = database.ReadData(105, loadcase).OfType<CdbBeam_str>()
    .Where(s => s.Mnr >= 1024 && s.Mnr <= 2048)
    .ToList();

var atStart = stresses.FirstOrDefault(s => s.Nr == beamId && Math.Abs(s.X) < 1e-6);
if (atStart != null)
{
    double sigMinMPa = atStart.Sigc / 1000.0;
    double sigMaxMPa = atStart.Sigt / 1000.0;
}
```

**Trap:** `X` is a `float`. Comparing `s.X == beam.Dl` to find the far end fails
exactly where the beam length is not representable - use a tolerance, or take
`OrderBy(s => s.X).Last()`.

---

## Quad elements and results

`200/0` -> `CdbQuad`; `210/LC` -> `CdbQuad_for`; `220/LC` -> `CdbQuad_str`.

| Type | Field | Meaning | Unit |
|---|---|---|---|
| `CdbQuad` | `Nr` | element number | - |
| | `Node[4]` | corner nodes | - |
| | `Mat`, `Mrf` | material, reinforcement material | - |
| | `Thick[]` | thickness | m |
| | `T[9]` | local axes, same layout as beams | - |
| `CdbQuad_for` | `Mxx`, `Myy` | bending moment | kNm/m |
| | `Mxy` | torsional moment | kNm/m |
| | `Vx`, `Vy` | shear force | kN/m |
| | `Nx`, `Ny`, `Nxy` | membrane force | kN/m |

Quad results are **per unit width**, unlike beam results. Values are at the
element centre; `CdbQuad_for` also carries Gauss-point values, but for shear the
documentation is explicit that the centre value should be used for the whole
element.

```csharp
var mesh = new Mesh();
var nodeIndex = new Dictionary<int, int>();

foreach (var n in database.ReadData(20, 0).OfType<CdbNode>())
{
    nodeIndex[n.Nr] = mesh.Vertices.Add(n.Xyz[0], n.Xyz[1], n.Xyz[2]);
}

foreach (var q in database.ReadData(200, 0).OfType<CdbQuad>())
{
    if (!q.Node.Take(4).All(nodeIndex.ContainsKey)) continue;

    int a = nodeIndex[q.Node[0]], b = nodeIndex[q.Node[1]],
        c = nodeIndex[q.Node[2]], d = nodeIndex[q.Node[3]];

    // triangles are stored as degenerate quads with Node[3] == Node[2]
    if (q.Node[3] == q.Node[2]) mesh.Faces.AddFace(a, b, c);
    else                        mesh.Faces.AddFace(a, b, c, d);
}

mesh.Normals.ComputeNormals();
mesh.Compact();
```

Building one shared vertex pool as above - rather than four vertices per face -
is what makes shading, welding and false-colour display work.

---

## Cross-section polygons

`9/NR` where NR is the **section number** -> among others `CdbSect_ppt`, the
polygon points. Enumerate the available sections with
`database.GetSecondaryKeysOf(9)`.

`Idp` packs two things:

```
polygonNumber = Idp / 256        flagBits = Idp & 0xFF
```

Flag bits: `1` inner boundary, `64` generated point, `128` duplicate of the first
vertex closing the loop. Keep only real vertices with `(Idp & (64 | 128)) == 0`.

```csharp
var polygons = database.ReadData(9, sectionId).OfType<CdbSect_ppt>()
    .GroupBy(p => p.Idp / 256)
    .OrderBy(g => g.Key)
    .Select(g => g.Where(p => (p.Idp & (64 | 128)) == 0)
                  .Select(p => new Point3d(p.Y, -p.Z, 0))   // z is down-positive
                  .ToList())
    .Where(pts => pts.Count >= 3)
    .ToList();
```

Section-local coordinates are `(y, z)` with **y right-positive and z
down-positive**, so negate `z` to draw the section the right way up in Rhino's
XY plane.

A box section returns an outer polygon plus one or more holes, with reverse
winding. Filtering *points* by the generated flag (64) also removes the phantom
"generated inner" polygon, which is cleaner than trying to classify polygons by
the inner-boundary bit.

---

## Tendon geometry

`100/5` -> `CdbBeam_tnd`. Records give the tendon position in the cross-section
system of each beam it passes through.

| Field | Meaning | Unit |
|---|---|---|
| `Nr` | beam number | - |
| `Nrs` | **tendon number** - group by this | - |
| `X` | distance along the beam axis, 0..`beam.Dl` | m |
| `Y`, `Z` | ordinates in the cross-section system | m |
| `Zz` | tensioning force | kN |
| `Mnr` | tendon material + 1000 * section material | - |

At least two records per (beam, tendon): entry and exit.

```csharp
var beamsByNr = database.ReadData(100, 0).OfType<CdbBeam>().ToDictionary(b => b.Nr);
var nodesByNr = database.ReadData(20, 0).OfType<CdbNode>().ToDictionary(n => n.Nr);

var records = database.ReadData(100, 5).OfType<CdbBeam_tnd>()
    .Where(t => t.Nrs == tendonId)
    .ToList();

var segments = new List<Curve>();

foreach (var perBeam in records.GroupBy(r => r.Nr))
{
    if (!beamsByNr.TryGetValue(perBeam.Key, out var beam)) continue;
    if (!nodesByNr.TryGetValue(beam.Node[0], out var n0)) continue;

    var ordered = perBeam.OrderBy(r => r.X).ToList();
    if (ordered.Count < 2) continue;

    var pts = ordered.Select(r => new Point3d(
        n0.Xyz[0] + r.X * beam.T[0] + r.Y * beam.T[3] + r.Z * beam.T[6],
        n0.Xyz[1] + r.X * beam.T[1] + r.Y * beam.T[4] + r.Z * beam.T[7],
        n0.Xyz[2] + r.X * beam.T[2] + r.Y * beam.T[5] + r.Z * beam.T[8])).ToList();

    for (int i = 0; i < pts.Count - 1; i++)
        segments.Add(new LineCurve(pts[i], pts[i + 1]));
}

var joined = Curve.JoinCurves(segments, 1.0e-3, true);
var tendon = (joined != null && joined.Length > 0) ? joined.ToList() : segments;
```

**Use the T matrix.** A shortcut like `Xyz[1] + r.Y` / `Xyz[2] - r.Z` happens to
be correct for a beam running along global X with default orientation - it is the
T-matrix formula with T equal to the identity apart from the sign on local z. It
silently produces wrong geometry on any skewed, sloping or curved girder. The
general form costs nothing.

**Select records by ordering, not by value.** `r.X == 0` and `r.X == beam.Dl` are
float comparisons; on a beam where the tendon starts partway along, or where the
length is not exactly representable, they drop the segment entirely. `OrderBy(r =>
r.X)` and take what is there.

### Station-based (elevation) view

For a longitudinal section along the bridge axis, do **not** transform to global.
Plot `Y` or `Z` directly against the station, interpolated from the beam's `Spar`:

```csharp
double fraction = beam.Dl > 1e-12 ? r.X / beam.Dl : 0.0;
double station  = beam.Spar[0] + fraction * (beam.Spar[1] - beam.Spar[0]);
var pt = new Point3d(station, -r.Z, 0);   // z down-positive -> negate
```

Using local ordinates is what makes the bridge axis come out as a straight
horizontal line at 0, independent of the plan curvature. Transform to global
first and a curved bridge produces a curved "axis", which is wrong for a design
elevation.

---

## Springs

`170/0` -> `CdbSpri`, one record per spring element. **This key needs the
[explicit type dispatcher](#the-explicit-type-dispatcher)** - the plain
`ReadData(170, 0)` throws, because at KWH 170 the kwl doubles as the load case
number of the result records and the internal table cannot resolve kwl 0.

| Field | Meaning | Unit |
|---|---|---|
| `Nr` | spring number | - |
| `Node[0]`, `Node[1]` | start / end node; end is 0 for a spring to ground | - |
| `T` | direction of the spring axis, global components | - |
| `Cp`, `Cq`, `Cm` | axial / transverse / rotational stiffness | kN/m, kNm/rad |
| `Pre` | prestress | kN |

```csharp
var springs = database
    .ReadData(170, 0, (id0, id1) => typeof(CdbSpri))
    .OfType<CdbSpri>()
    .ToList();

// which spring supports which node - springs to ground sit on their start node
var springByNode = new Dictionary<int, int>();
foreach (var s in springs)
{
    if (s.Node[0] > 0 && !springByNode.ContainsKey(s.Node[0]))
        springByNode[s.Node[0]] = s.Nr;
}
```

**Traps.** Several springs can share a node (e.g. one per direction from a
point support with independent stiffnesses); decide whether first-wins or a
list-per-node is right for the job and say so in the plan. Spring *results* live
at `170/LC` (`CdbSpri_res`, selector `+`; `CdbSpri_re0` maxima at selector `0`)
and need a switching dispatcher - the example in the dispatcher section above is
exactly that key.
