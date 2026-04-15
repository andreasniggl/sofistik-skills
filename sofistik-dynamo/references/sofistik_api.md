# SOFiSTiK Analysis + Design — Zero-Touch Node Quick Reference

Package: `SOFiSTiK Analysis + Design`, version `2026.5.0` (declare in `NodeLibraryDependencies`).

`FunctionSignature` strings are exact — copy them verbatim into `DSFunction` nodes. Argument types use the `@type1,type2` suffix. Methods with no arguments have **no** `@` suffix.

Return tuples: each `Results.*` node returns a 2-D list (rows × columns). The column index after each name is the position used when the user accesses it via `List.GetItemAtIndex` or in Python (`row[i]`).

---

## `SOFiSTiK.Analysis.Analyze` — running calculations

| Method | Signature | Notes |
|---|---|---|
| `Calculate` | `SOFiSTiK.Analysis.Analyze.Calculate@string` | Run a `.dat` file headlessly. |
| `CalculateMainSystem` | `SOFiSTiK.Analysis.Analyze.CalculateMainSystem@string,int,bool,bool,string` | Args: viewName, selfWeightNo, analyzeLoads, calculateImmediately, additionalIncludeFile. Returns the generated `.dat` path. |
| `CalculateSubsystems` | `SOFiSTiK.Analysis.Analyze.CalculateSubsystems@System.Collections.Generic.List\`1[[System.String]],bool,int,bool,bool` | Args: viewNames, planar2D, selfWeightNo, loadTransfer, calculateImmediately. |

## `SOFiSTiK.Analysis.Model` — open the SOFiSTiK database

| Method | Signature | Returns |
|---|---|---|
| `CreateByPath` | `SOFiSTiK.Analysis.Model.CreateByPath@string` | Model |
| `CreateByViewName` | `SOFiSTiK.Analysis.Model.CreateByViewName@string` | Model |
| `CreateByActiveView` | `SOFiSTiK.Analysis.Model.CreateByActiveView` | Model — most common entry point. |
| `GetMaterialIds` | `SOFiSTiK.Analysis.Model.GetMaterialIds` | List[int] |
| `GetMaterialProperties` | `SOFiSTiK.Analysis.Model.GetMaterialProperties@System.Collections.Generic.List\`1[[System.Int32]]` | Cols: Id(0), Type(1), Name(2), E[kN/m²](3), G(4), ν(5), γ[kN/m³](6), fcd(7) |
| `GetMaterialPropertiesGWP` | `...@List<int>,string` | Cols: Id(0), Type(1), Name(2), Phase(3), DimType(4), GWP(5) |
| `GetSectionIds` | `SOFiSTiK.Analysis.Model.GetSectionIds` | List[int] |
| `GetSectionProperties` | `...@List<int>` | Cols: Id(0), Name(1), MatId(2), ReinfId(3), A(4), Ay(5), Az(6), It(7), Iy(8), Iz(9), Iyz(10), ys(11), zs(12), ysc(13), zsc(14), E(15), G(16), γ(17) |
| `GetSectionGeometry` | `...@int` | Two outputs: OuterBounds (Lines), InnerBounds (Lines), Reinforcements (Layer Id, Bar Diameter, Position) |
| `GetAllStructuralElements` | `SOFiSTiK.Analysis.Model.GetAllStructuralElements` | Cols: SOFiSTiK Id(0), Guid(1), Name(2) |
| `GetStructuralColumns` | `SOFiSTiK.Analysis.Model.GetStructuralColumns` | Cols: Id(0), Guid(1), Name(2), SectionId(3), StartNode(4), EndNode(5), Area[m²](6), γ(7) |
| `GetStructuralBeams` | `SOFiSTiK.Analysis.Model.GetStructuralBeams` | Cols: Id(0), Guid(1), Name(2), SectionId(3), StartNode(4), EndNode(5), Area(6), γ(7) |
| `GetStructuralWalls` | `SOFiSTiK.Analysis.Model.GetStructuralWalls` | Cols: Id(0), Guid(1), Name(2), Thickness(3), Width(4), Height(5), MatId(6), ReinfId(7) |
| `GetStructuralSlabs` | `SOFiSTiK.Analysis.Model.GetStructuralSlabs` | Cols: Id(0), Guid(1), Name(2), Thickness(3), Width(4), Height(5), MatId(6), ReinfId(7) |
| `GetStoreyLevelData` | `SOFiSTiK.Analysis.Model.GetStoreyLevelData` | Cols: Id(0), Guid(1), Name(2), StoreyType(3), TowerId(4), Elev(5), H(6), COM(7), COR(8), XMin(9), XMax(10), YMin(11), YMax(12), Mass(13), RotMass(14), StfX(15), StfY(16) |
| `GetSecondaryGroupAssignments` | `...` | Cols: GroupId(0), GroupName(1), GroupType(2), ElementGuid(3), ElementType(4), ElementId(5) |
| `GetDesignElements` | `...` | Three outputs: DesignElements (Id,Guid,Name,SectionId,Length,LocalZ x/y/z), MemberGuids, DesignSections (Xi normalized 0–1) |
| `GetMesh` | `...@List<string>` | guids → mesh points |
| `GetMeshPointsIndices` | `...@string` | guid → (Points, IndexGroups of 4) |
| `GetTendons` | `...` | TendonGeometry, GeometryDefinitionPoints, TendonData |
| `GetPrestressingSystems` | `...` | GeneralInformation, TendonProperties, DuctGeometryData |
| `GetStructuralPoints`, `GetStructuralLines`, `GetStructuralAreas` | `...@string` (cdbPath) | Geometry of analytical entities. |

## `SOFiSTiK.Analysis.Results` — read results

All take `Model` first. `loadCaseIds` is `List<int>` — pass empty list `[]` to get all.

`locations` for beam/column/wall/design: one of `"StartPoints"`, `"EndPoints"`, `"StartEndPoints"`, `"StartEndMaxPoints"`, `"AllPoints"`.

| Method | Signature | Cols |
|---|---|---|
| `GetLoadCases` | `SOFiSTiK.Analysis.Results.GetLoadCases@SOFiSTiK.Analysis.Model,string` | Id(0), Name(1), Action(2), Type(3), DLFactor(4), CSStart(5), CSEnd(6). `type` filter: `All`, `Linear`, `Nonlinear`, `Superposition`, `InfluenceLine`, `NaturalFrequency`, `BucklingMode`, `TrainLoadDefinition` |
| `GetColumnResults` | `...@Model,List<int>,string` | LcId(0), Guid(1), Id(2), Xi(3), N(4), My(5), Mz(6), Vz(7), Vy(8) |
| `GetBeamResults` | `...@Model,List<int>,string` | same cols as columns |
| `GetWallResultants` | `...@Model,List<int>,string` | same cols as columns; Xi runs bottom→top |
| `GetAreaResults` | `...@Model,List<int>,string` | LcId(0), Guid(1), Id(2), NXX(3), NYY(4), NXY(5), MXX(6), MYY(7), MXY(8), VX(9), VY(10), center(11), localX(12), localZ(13). `forceType="NodalValues"` |
| `GetSupportForces` | `...@Model,List<int>,string` | Returns three sub-tables (point/line/area). `forceType`: `Resultants`, `NodalForces`, `Distributed`, `Averaged` |
| `GetSupportPointForces` | `...@Model,List<int>` | LcId(0), Guid(1), Id(2), PX(3), PY(4), PZ(5), MX(6), MY(7), MZ(8) |
| `GetSupportLineForces` | `...@Model,List<int>,string` | adds Xi, LocalZ. forceType: `Resultants`, `NodalForces`, `PartialResultants`, `Distributed`, `Averaged` |
| `GetSupportAreaForces` | `...@Model,List<int>,string` | as point forces; forceType: `Resultants`, `NodalForces`, `Distributed`, `Averaged` |
| `GetStoreyLevelResults` | `...@Model,List<int>` | LcId(0), Guid(1), StoreyId(2), Type(3), TowerId(4), Elev(5), H(6), PXYZ(7-9), MXYZ(10-12), UXYZ(13-15), RZ(16), DX(17), DY(18), DRZ(19), DXMAX(20), DYMAX(21) |
| `GetDesignElementsResults` | `...@Model,List<int>,string` | LcId(0), Guid(1), DesElemId(2), SectionId(3), Xi(4), N(5), My(6), Mz(7), Vz(8), Vy(9) |
| `GetPunchingPeriphery` | `...@Model` | NodeId, Periphery (list of Points) |
| `GetPunchingResults` | `...@Model` | NodeId(0), Force[kN](1), Perim_u0(2), RedFactor(3), SlabGuid(4), SlabThk(5), MemberGuid(6), Beta(7), Type(8) |

## `SOFiSTiK.Analysis.Reinforcement`

| Method | Signature | Cols |
|---|---|---|
| `GetDesignCases` | `SOFiSTiK.Analysis.Reinforcement.GetDesignCases@SOFiSTiK.Analysis.Model` | DesignCaseId(0), Title(1), Type(2) |
| `GetAreaReinforcement` | `...@Model,List<int>` | Guid(0), DesignCase(1), Id(2), Node(3), TopMaj(4), TopMin(5), BotMaj(6), BotMin(7), Shear(8), Determ(9) |
| `GetBeamReinforcement` | `...@Model,List<int>` | Guid(0), CaseId(1), Id(2), Xi(3), LongBot(4), LongTop(5), LongLat(6), Shear(7), Influence(8) |
| `GetColumnReinforcement` | `...@Model,List<int>` | Guid(0), CaseId(1), Id(2), Xi(3), Long(4), Constructive(5), Shear(6), Influence(7) |
| `GetDesignElementReinforcement` | `...@Model,List<int>` | Guid(0), CaseId(1), Id(2), Xi(3), LongAs1(4), LongAs2(5), Shear(6), Influence(7) |

## `SOFiSTiK.Analysis.Design`

| Method | Signature |
|---|---|
| `CalculateInteractionSurface` | `...@Model,int,double,double,double,int,int` (sectionId, mscale, reinf_value, fcd, n_pts, n_alph) → List of List of Points |
| `CalculateRequiredReinforcementColumn` | `...@Model,int,List<List<double>>,double` (sectionId, forces=[N,My,Mz] rows, ProvReinf) → List of [Required As, Capacity Ratio] |

## `SOFiSTiK.Analysis.Utils`

| Method | Signature | Returns |
|---|---|---|
| `GetProjectPath` | `SOFiSTiK.Analysis.Utils.GetProjectPath@string` | Path to current Revit doc + optional appended filename |
| `GetSubsystemViewNames` | `SOFiSTiK.Analysis.Utils.GetSubsystemViewNames` | List[string] |
| `GetMainSystemViewName` | `SOFiSTiK.Analysis.Utils.GetMainSystemViewName` | string |
| `GetPhysicalCounterpart` | `SOFiSTiK.Analysis.Utils.GetPhysicalCounterpart@Revit.Elements.Element[]` | Physical Element[] for analytical input |
| `TableLeftJoin` | `SOFiSTiK.Analysis.Utils.TableLeftJoin@System.Collections.Generic.IList\`1[[System.Collections.Generic.IList\`1[[System.Object]]]],System.Collections.Generic.IList\`1[[System.Collections.Generic.IList\`1[[System.Object]]]],int,int` | Merged 2-D list, left order preserved |
| `TableRightJoin` | (same shape with Right) | Right order preserved |
| `TableInnerJoin` | (same shape with Inner) | Common keys only |

## `SOFiSTiK.Analysis.Dynamo.Export`

| Method | Signature |
|---|---|
| `ResultsToExcel` | `SOFiSTiK.Analysis.Dynamo.Export.ResultsToExcel@string,string,bool,bool,bool,bool,bool` |

Args: dataBasePath (`.cdb`), pathToExcelFile, beams, columns, walls, supports, allSOFiSTiKLoadcases.

---

## Common patterns

**Read support reactions for the active view:**

```
[CreateByActiveView] → [GetSupportForces (Model, [], "Resultants")]
                                              ↓
                                            Watch
```

**Get the physical Revit element from an analytical element:**

```
[All Elements of Category: OST_AnalyticalMember]
            ↓
[Utils.GetPhysicalCounterpart]
            ↓
[Element.SetParameterByName] ← name + value
```

**Filter elements by parameter value (regex):** combine `Parameter.ParameterByName` → `Parameter.Value` → Python (regex match) → `List.FilterByBoolMask`.

**Notes on units:** Geometry from `Model.Get*` is in **meters** (Revit Dynamo nodes typically return feet — convert if combining). Forces are kN, moments kNm, stresses kN/m² unless documented otherwise.
