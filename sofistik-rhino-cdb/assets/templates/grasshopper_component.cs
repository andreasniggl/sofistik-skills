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

// Starter template for reading a SOFiSTiK CDB in the Grasshopper C# Script
// component. As written it imports nodes as points - run it first to confirm the
// plumbing (assembly reference, path, database opens) before adding logic.
//
// KEEP THIS BLOCK BELOW #endregion. The #r directive must appear within roughly
// the first 31 lines of the script or the SOFiSTiK namespace will not resolve;
// a header comment above the usings is what pushes it out of range.
//
// Component inputs to create:
//   relPath   string   path to the .cdb, relative to this .gh file
// Component outputs:
//   points    node coordinates          [model units, normally m]
//   ids       matching node numbers

public class Script_Instance : GH_ScriptInstance
{
    private void RunScript(
        string relPath,
        ref object points,
        ref object ids)
    {
        // --- resolve the cdb relative to the Grasshopper document -------------
        if (string.IsNullOrEmpty(GrasshopperDocument.FilePath))
            throw new InvalidOperationException(
                "Save the Grasshopper definition first - the CDB path is resolved relative to it.");

        var baseDirection = Path.GetDirectoryName(GrasshopperDocument.FilePath);
        var filepath = Path.Combine(baseDirection ?? string.Empty, relPath);

        using (var database = new SOFiSTiK.Analysis.Database.DataAccess())
        {
            // --- open, and fail loudly if it did not work ---------------------
            // Open returns false for a missing file, and for a CDB still held by
            // SSD or a running analysis. Without this check every read below
            // comes back empty and looks like "no results in the model".
            if (!database.Open(filepath))
                throw new InvalidOperationException(
                    $"Could not open CDB: {filepath}. Check the path, and that SSD "
                    + "or a running analysis is not holding the file open.");

            // --- read each key once, into a list ------------------------------
            // ReadData hits the database; never call it inside a per-element loop.
            var nodes = database.ReadData(20, 0).OfType<CdbNode>().ToList();

            // --- build the outputs --------------------------------------------
            var pts = new List<Point3d>();
            var nrs = new List<int>();

            foreach (var node in nodes)
            {
                // Xyz is float[3] in metres; widen where you do maths on it
                pts.Add(new Point3d(node.Xyz[0], node.Xyz[1], node.Xyz[2]));
                nrs.Add(node.Nr);
            }

            // --- assign, still inside the using block --------------------------
            // Materialised lists, not lazy sequences: Grasshopper would otherwise
            // enumerate them after the database has been disposed.
            points = pts;
            ids = nrs;
        }
    }
}
