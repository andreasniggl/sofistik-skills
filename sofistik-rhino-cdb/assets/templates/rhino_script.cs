// #! csharp
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

// Starter template for reading a SOFiSTiK CDB in the Rhino C# script editor.
// As written it imports nodes as point objects into the document - run it first
// to confirm the plumbing (assembly reference, path, database opens) before
// adding logic.
//
// Keep descriptive comments below the usings, not above them: in the Grasshopper
// component the #r directive must land within roughly the first 31 lines or the
// SOFiSTiK namespace fails to resolve. Same layout here for consistency.
//
// Assumes the .cdb sits next to the .3dm with the same name, which is the normal
// SOFiSTiK Rhino Interface layout.

// main script
{
    RhinoDoc doc = __rhino_doc__;

    if (string.IsNullOrEmpty(doc.Path))
    {
        RhinoApp.WriteLine("Save the Rhino document first - the CDB is located next to it.");
        return;
    }

    string databasePath = System.IO.Path.ChangeExtension(doc.Path, "cdb");

    var nodes = CdbReader.GetNodes(databasePath);

    foreach (var n in nodes)
        doc.Objects.AddPoint(new Point3d(n.Xyz[0], n.Xyz[1], n.Xyz[2]));

    doc.Views.Redraw();
    RhinoApp.WriteLine($"{nodes.Count} nodes imported from {databasePath}.");
}

/// <summary>Node number and its global coordinates, detached from the database.</summary>
public class NodePoint
{
    public int Nr { get; set; }
    public double[] Xyz { get; set; }
}

public static class CdbReader
{
    public static List<NodePoint> GetNodes(string databasePath)
    {
        using (var db = new DataAccess())
        {
            if (!db.Open(databasePath))
                throw new InvalidOperationException(
                    $"Failed to open database {databasePath}. Check the path, and that "
                    + "SSD or a running analysis is not holding the file open.");

            // ToList() inside the using block: ReadData/OfType are lazy, and the
            // database is disposed the moment this method returns.
            return db.ReadData(20, 0).OfType<CdbNode>()
                .Select(n => new NodePoint
                {
                    Nr = n.Nr,
                    Xyz = new double[] { n.Xyz[0], n.Xyz[1], n.Xyz[2] },
                })
                .ToList();
        }
    }
}
