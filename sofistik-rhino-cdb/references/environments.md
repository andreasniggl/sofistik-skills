# The two scripting environments

Both host C#, both use the same `SOFiSTiK.Analysis.Database` API, and the
boilerplate around them is *not* interchangeable. Pick one before writing.

| | Grasshopper C# Script component | Rhino script editor |
|---|---|---|
| Header | `// Grasshopper Script Instance` | `// #! csharp` |
| Usings | wrapped in `#region Usings` | plain, no region |
| `#r` position | inside the region, after the Rhino/GH usings | after the usings |
| Entry point | `RunScript` method on `Script_Instance : GH_ScriptInstance` | top-level statement block in braces |
| Document handle | `GrasshopperDocument` | `__rhino_doc__` |
| Data in | typed `RunScript` parameters (component inputs) | hard-coded, or prompted from the user |
| Data out | `ref object` parameters | objects added to the document, or `RhinoApp.WriteLine` |
| Helper types | nested in `Script_Instance`, or after it | declared after the main block |

## Grasshopper C# Script component

```csharp
// Grasshopper Script Instance
#region Usings
using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;

using Rhino.Geometry;

using Grasshopper;
using Grasshopper.Kernel.Types;

#r "SOFiSTiK.Analysis.Database.dll"
using SOFiSTiK.Analysis.Database;
using SOFiSTiK.Analysis.Database.Types;
#endregion

// Component documentation goes here, below #endregion - see the #r line limit
// under "Both environments" at the end of this file.

public class Script_Instance : GH_ScriptInstance
{
    private void RunScript(
        string relPath,
        int loadcase,
        ref object values,
        ref object ids)
    {
        // resolve the cdb relative to the Grasshopper document
        var baseDirection = Path.GetDirectoryName(GrasshopperDocument.FilePath);
        var filepath = Path.Combine(baseDirection ?? string.Empty, relPath);

        using (var database = new SOFiSTiK.Analysis.Database.DataAccess())
        {
            if (!database.Open(filepath))
                throw new InvalidOperationException(
                    $"Could not open CDB: {filepath}. " +
                    "Check the path, and that SSD or a running analysis is not holding it open.");

            // read once, into lists
            var nodesCdb = database.ReadData(20, 0).OfType<CdbNode>().ToList();

            // ... build outputs ...

            values = new List<double>();
            ids = new List<int>();
        }
    }
}
```

### Inputs

Declare them as typed `RunScript` parameters and set the matching type hint on
the component. `string relPath` for the database, `int loadcase`, `List<int>`
for a set of element ids, `bool`/`double` for toggles and scale factors.

The user's convention: **the CDB path is relative to the Grasshopper document**.
`GrasshopperDocument.FilePath` is empty for an unsaved definition, and
`Path.GetDirectoryName` returns `null` for it - hence the `?? string.Empty`,
which quietly resolves against the working directory. If that matters, check
explicitly:

```csharp
if (string.IsNullOrEmpty(GrasshopperDocument.FilePath))
    throw new InvalidOperationException("Save the Grasshopper definition first - "
        + "the CDB path is resolved relative to it.");
```

### Outputs

Assign a `List<T>` to each `ref object`. Grasshopper flattens it into a flat list
on the output, which is what we want here. Keep parallel lists aligned - if you
`continue` past a beam, skip it in *every* output list, or values and ids drift
out of step and every downstream match is silently wrong.

Name outputs for their unit when they carry one: `momentsKNm`, `dispMM`.

## Rhino script editor

```csharp
// #! csharp
// Reads beams from the associated SOFiSTiK database and draws them as lines.

using System;
using System.Collections.Generic;
using System.Linq;

using Rhino;
using Rhino.Geometry;
using Rhino.Commands;

// add assembly reference to SOFiSTiK database interface
#r "SOFiSTiK.Analysis.Database.dll"
// add SOFiSTiK types
using SOFiSTiK.Analysis.Database;
using SOFiSTiK.Analysis.Database.Types;

// main script
{
    RhinoDoc doc = __rhino_doc__;

    if (string.IsNullOrEmpty(doc.Path))
    {
        RhinoApp.WriteLine("Save the Rhino document first - the CDB is located next to it.");
        return;
    }

    // the cdb normally sits next to the .3dm with the same stem
    string databasePath = System.IO.Path.ChangeExtension(doc.Path, "cdb");

    var beams = CdbReader.GetBeams(databasePath);

    foreach (var beam in beams)
    {
        var p0 = new Point3d(beam.StartXyz[0], beam.StartXyz[1], beam.StartXyz[2]);
        var p1 = new Point3d(beam.EndXyz[0], beam.EndXyz[1], beam.EndXyz[2]);
        doc.Objects.Add(new LineCurve(p0, p1));
    }

    doc.Views.Redraw();
    RhinoApp.WriteLine($"{beams.Count()} beams imported.");
}

/// <summary>Beam with resolved start and end coordinates.</summary>
public class BeamGeometry
{
    public int BeamId { get; set; }
    public double[] StartXyz { get; set; }
    public double[] EndXyz { get; set; }
    public double Length { get; set; }
}

public static class CdbReader
{
    public static IEnumerable<BeamGeometry> GetBeams(string databasePath)
    {
        using (var db = new DataAccess())
        {
            if (!db.Open(databasePath))
                throw new InvalidOperationException($"Failed to open database {databasePath}");

            var nodeDict = db.ReadData(20, 0).OfType<CdbNode>().ToDictionary(n => n.Nr);
            var beams = db.ReadData(100, 0).OfType<CdbBeam>();

            return beams.Select(beam => new BeamGeometry
            {
                BeamId   = beam.Nr,
                StartXyz = ToXyz(nodeDict[beam.Node[0]]),
                EndXyz   = ToXyz(nodeDict[beam.Node[1]]),
                Length   = beam.Dl,
            }).ToList();   // materialise inside the using block
        }
    }

    private static double[] ToXyz(CdbNode n) =>
        new double[] { n.Xyz[0], n.Xyz[1], n.Xyz[2] };
}
```

### The lazy-enumeration trap

`ReadData(...).OfType<T>()` is lazy, and `Select` on top of it is lazy too. If a
method returns that sequence out of a `using (var db = ...)` block, the database
is disposed before anything is enumerated and the caller gets an exception or an
empty result. **Materialise with `ToList()` inside the `using` block** whenever
the data crosses a method boundary - as above.

The same applies in Grasshopper: assigning a lazy sequence to a `ref object`
output means Grasshopper enumerates it after `RunScript` has returned and the
`using` has closed the database.

### Locating the CDB

`Path.ChangeExtension(doc.Path, "cdb")` assumes the CDB is the SOFiSTiK project
matching the .3dm, which is the normal Rhino Interface layout. When it is not,
prompt instead:

```csharp
string databasePath = Rhino.UI.Dialogs.ShowOpenFileDialog(
    "Select SOFiSTiK database", "SOFiSTiK database (*.cdb)|*.cdb||", null, out _)
    ? /* selected path */ : null;
```

or take a path relative to `doc.Path`'s folder, mirroring the Grasshopper form.

## Both environments

- `#r` takes the **file name only**. The Rhino Interface makes the assembly
  resolvable; a full path is version- and machine-specific and will break.
- **`#r` must appear within roughly the first 31 lines.** The script host only
  scans the top of the file for directives; beyond that the directive is silently
  ignored and compilation fails with *"the namespace SOFiSTiK could not be
  found"*. That error names the assembly, so it reads like a missing
  installation - the actual cause is that the directive sat too far down.

  Everything above `#r` counts, comments included. Put the component's
  documentation **after** `#endregion`, just before the class declaration:

  ```csharp
  // Grasshopper Script Instance     <- line 1, nothing else above the region
  #region Usings
  ...
  #r "SOFiSTiK.Analysis.Database.dll"   <- around line 13, comfortable margin
  ...
  #endregion

  // What this component does, its inputs, its outputs, their units.
  // As long as it needs to be - nothing below #endregion affects the directive.

  public class Script_Instance : GH_ScriptInstance
  ```

  The confirmed limit is in the Grasshopper C# Script component. The Rhino script
  editor uses a different host and may be more permissive, but the same layout
  costs nothing and removes the question.
- The `#r` directive must sit with the other directives at the top, before any
  type declaration.
- `DataAccess`'s constructor probes for an installed SOFiSTiK environment and
  throws if it cannot find one. In Grasshopper that surfaces as a red component;
  a clear message beats the raw exception.
- Both hosts run on .NET with Rhino's process, x64. Nothing extra to configure.
