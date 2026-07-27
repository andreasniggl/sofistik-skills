# CDB type index (KWH / KWL -> managed type)

Generated from `SOFiSTiK.Analysis.Database.xml` by `scripts/build_type_index.py`. Do not hand-edit.

## How to read this table

Every row is one managed type and the database address it lives at:

```
kwh / kwl [: selector1 [: selector2]]
```

- **kwh** - primary key, passed as the first argument to `ReadData`.
- **kwl** - secondary key, passed as the second argument. A literal number means exactly that value. `LC` means *any load case number*, `NR` *any element/section number*, `ID` a 4-character string key (use the `ReadData(int, string)` overload).
- **selector** - the value of the record's first (and sometimes second) integer item. This is what distinguishes several types stored at the *same* key. `+` positive, `-` negative, `0` zero, `Z!` any non-zero, `*` anything, `?` a wildcard digit.

You never pass the selector to `ReadData`. It is resolved for you by `.OfType<T>()`, which is why filtering is mandatory rather than cosmetic:

```csharp
// 100/00 holds BOTH CdbBeam (selector +) and CdbBeam_sct (selector 0)
var beams    = db.ReadData(100, 0).OfType<CdbBeam>().ToList();
var sections = db.ReadData(100, 0).OfType<CdbBeam_sct>().ToList();
```

For results, the load case number *is* the KWL:

```csharp
var forces = db.ReadData(102, loadcase).OfType<CdbBeam_for>().ToList();
```

## Quick reference - the records you will actually use

| Type | KWH/KWL | What it is |
|---|---|---|
| `CdbSyst` | `10/00` | SystemInfo |
| `CdbGrp` | `11/00` | Primary group data |
| `CdbLc_ctrl` | `12/LC:?` | Information on loadcase LC |
| `CdbNode` | `20/00` | Nodes |
| `CdbN_disp` | `24/LC:+` | Displacements and support forces of nodes |
| `CdbN_dispc` | `24/LC:0` | Max. Displacements and support forces |
| `CdbBeam` | `100/00:+` | Beams |
| `CdbBeam_sct` | `100/00:0` | Beams sections |
| `CdbBeam_tnd` | `100/05` | tendons of beams |
| `CdbBeam_for` | `102/LC:Z!` | Total Beam forces and deformations |
| `CdbBeam_foc` | `102/LC:0` | Maximum of Total Beam forces and deformations |
| `CdbBeam_str` | `105/LC:Z!` | Stresses in cross-section of beams |
| `CdbBeam_stc` | `105/LC:0` | Maximum stresses in cross-section of beams |
| `CdbTrus` | `150/00` | trusselements |
| `CdbTrus_res` | `152/LC:+` | results of truss elements |
| `CdbCabl` | `160/00` | cable elements |
| `CdbCabl_res` | `162/LC:+` | results of cables |
| `CdbSpri` | `170/00` | Spring-elements |
| `CdbSpri_res` | `170/LC:+` | results of spring-elements |
| `CdbBoun` | `180/00:+` | Boundary elements |
| `CdbBoun_res` | `180/LC:Z!` | results of boundary elements |
| `CdbQuad` | `200/00` | QuadElements |
| `CdbQuad_for` | `210/LC:+` | forces of Quad-elements |
| `CdbQuad_foc` | `210/LC:0` | maximum forces of Quad elements |
| `CdbQuad_str` | `220/LC:+` | stresses of Quad-element |
| `CdbQuad_stc` | `220/LC:0` | maximum Quad-stress |
| `CdbBric` | `300/00` | Bric-elements |
| `CdbBric_str` | `310/LC:+` | 3D-stresses in Bric-elements |
| `CdbSect` | `9/NR:0` | SectionalValues (total section) |
| `CdbSect_ppt` | `9/NR:101` | SectionPolygonPoint (POLY/QPOL) |
| `CdbSect_spt` | `9/NR:100` | SectionStressPoint (SPT/QSP) |
| `CdbAxis` | `3/ID:0` | Geometric Axis |
| `CdbAxis_geo` | `3/ID:??` | Geometric properties |
| `CdbTendon` | `44/NR:0` | Tendons |
| `CdbTendaxis` | `40/NR:0` | Reference axis |
| `CdbMat` | `1/NR:0` | MaterialTitle |

## Full index by KWH

### -999--1 &mdash; Internal / index records

| KWH/KWL | Type | Description |
|---|---|---|
| `-999/-997` | `CdbDesc_kw` | description string to group |
| `-999/-998` | `CdbRec_indx` | Sorted index on structure names |
| `-999/-999` | `CdbRec_vers` | Revision number of generating cdbase.txt |
| `-999/-999:1` | `CdbRec_pub` | public REC |
| `-999/-999:101` | `CdbRec_defi` | additional defines |
| `-999/-999:11` | `CdbRec_mix` | mixinfo of a record |
| `-999/-999:12` | `CdbRec_mhd` | mixinfo of a record header |
| `-999/-999:2` | `CdbRec_int` | internal REC |
| `-999/-999:3` | `CdbRec_dad` | public DAD |
| `-999/-999:4` | `CdbRec_desc` | description string to last entry or item |
| `-999/-999:6` | `CdbRec_item` | item of a record |
| `-1/NS:0` | `CdbIl_ctrl0` | Headder of a location |
| `-1/NS:1` | `CdbIl_ctrl1` | Headder of a bending result |
| `-1/NS:1????` | `CdbIl_data1` | Influence values for INT 0,1,2 |
| `-1/NS:1??????` | `CdbIl_data2` | Influence values for INT > 2 |
| `-1/NS:2` | `CdbIl_ctrl2` | Headder of a shear result |
| `-1/NS:?` | `CdbIl_ctrlx` | Headder of transverse evaluation data |

### 0-9 &mdash; Global control, materials, soil, axes, areas, sections

| KWH/KWL | Type | Description |
|---|---|---|
| `0/01:101` | `CdbCtrl_obj` | involved objects |
| `0/01:102` | `CdbCtrl_oid` | GUId |
| `0/01:999` | `CdbCtrl_010` | AccessInfo Last Program |
| `0/01:?` | `CdbCtrl_011` | Messages |
| `0/100` | `CdbCtrl_var` | Global_CADINP_Variable |
| `0/101` | `CdbCtrl_dim` | Unit definitions |
| `0/91:*` | `CdbCtrl_d` | Control for Element stiffness $D1 and $D2 |
| `0/92:*` | `CdbCtrl_c` | Control for Element stiffness $C1 and $C2 |
| `0/93:*` | `CdbCtrl_h` | Control for Element stiffness $H1 and $H2 |
| `0/96:1` | `CdbSsd_spe` | SSD-Spezial |
| `0/97:0` | `CdbVis_lc0` | active Loadcase |
| `0/97:1` | `CdbVis_lc` | Loadcase visualisation |
| `0/99:*` | `CdbCtrl` | PrintControl |
| `0/99:0` | `CdbCtrl_0` | AccessInfo |
| `0/99:1` | `CdbCtrl_1` | AccessTitle |
| `1/NR:0` | `CdbMat` | MaterialTitle |
| `1/NR:1` | `CdbMat_bric` | MaterialBrickwork |
| `1/NR:1` | `CdbMat_conc` | MaterialConcrete |
| `1/NR:1` | `CdbMat_cons` | MaterialConstants |
| `1/NR:1` | `CdbMat_flui` | MaterialConstants |
| `1/NR:1` | `CdbMat_stee` | MaterialSteel |
| `1/NR:1` | `CdbMat_timb` | MaterialTimber |
| `1/NR:10??` | `CdbMat_user` | Information on user input |
| `1/NR:14` | `CdbMat_undr` | Undrained soil parameters |
| `1/NR:15` | `CdbMat_faul` | Fault/Shear plane |
| `1/NR:16` | `CdbMat_swel` | Swelling parameters |
| `1/NR:2` | `CdbMat_serv` | StressStrainLaw (Servicability) |
| `1/NR:3` | `CdbMat_ulti` | StressStrainLaw (Ultimate Limit state) |
| `1/NR:4` | `CdbMat_nonl` | StressStrainLaw (Nonlinear Mean Values) |
| `1/NR:7` | `CdbMat_bed` | MaterialBedding |
| `1/NR:8` | `CdbMat_lay` | MaterialLayerStructure |
| `1/NR:9` | `CdbMat_hyd` | MaterialConductivity |
| `1/NR:90` | `CdbMat_cre` | ExplicitCreepCurve |
| `1/NR:90` | `CdbMat_shr` | ExplicitShrinkageCurve |
| `1/NR:90` | `CdbMat_spe` | MaterialSpecial |
| `1/NR:91` | `CdbMat_gwp` | Global Warming Potential (CO2 Equivalents) |
| `2/NR:0` | `CdbBore` | SoilProfile |
| `2/NR:1` | `CdbBore_lay` | Soillayer |
| `2/NR:10` | `CdbBore_tab` | SoilTabdefinition |
| `2/NR:1001` | `CdbBore_bax` | BoreProfileAxial |
| `2/NR:1002` | `CdbBore_bla` | BoreProfileTransverse |
| `2/NR:1003` | `CdbBore_bam` | BoreProfileMoment |
| `2/NR:1011` | `CdbBore_dya` | BoreProfileAxialDynamic |
| `2/NR:1012` | `CdbBore_dyl` | BoreProfileTransverseDynamic |
| `2/NR:11` | `CdbBore_tad` | SoilTabvalues |
| `3/ID:-` | `CdbAxis_ref` | Reference to another Geometry |
| `3/ID:0` | `CdbAxis` | Geometric Axis |
| `3/ID:101` | `CdbAxis_atb` | Geometric segments of axis plan view |
| `3/ID:10104` | `CdbAxis_itm` | Secondary axis parameter mapping |
| `3/ID:10107` | `CdbAxis_opt` | Placement options |
| `3/ID:102` | `CdbAxis_vtb` | Definition of vertical alignment |
| `3/ID:103` | `CdbAxis_itb` | Placement at axis position (obsolete) |
| `3/ID:104` | `CdbAxis_its` | Secondary axis definition |
| `3/ID:105` | `CdbAxis_psm` | Prestress method |
| `3/ID:106` | `CdbAxis_psp` | Prestress placements |
| `3/ID:107` | `CdbAxis_plc` | Placement at axis position |
| `3/ID:110` | `CdbAxis_prp` | General properties of axis |
| `3/ID:121` | `CdbGaxd_atb` | Geometric segments of axis plan view (double precision) |
| `3/ID:122` | `CdbGaxd_vtb` | Geometric properties for axis heights (double precision) |
| `3/ID:18?` | `CdbGaxd_geo` | Geometric properties |
| `3/ID:190` | `CdbGaxd_nkn` | Knots of a Nurb |
| `3/ID:191` | `CdbGaxd_cpt` | Control point of a Nurb |
| `3/ID:192` | `CdbGaxd_pt` | Data point on curve |
| `3/ID:193` | `CdbGaxd_arc` | Circular Arc |
| `3/ID:300` | `CdbAxis_trl` | Properties for train loading |
| `3/ID:90` | `CdbAxis_nkn` | Knots of a Nurb |
| `3/ID:91` | `CdbAxis_cpt` | Control point of a Nurb |
| `3/ID:92` | `CdbAxis_pt` | Data point on curve |
| `3/ID:93` | `CdbAxis_arc` | Circular Arc |
| `3/ID:97` | `CdbAxis_spt` | Station point on a Nurb |
| `3/ID:98` | `CdbAxis_viz` | Data points for visualisation |
| `3/ID:99` | `CdbAxis_obb` | Oriented Boundig Box |
| `3/ID:??` | `CdbAxis_geo` | Geometric properties |
| `4/ID:0` | `CdbTend` | Prestressing Schemes |
| `4/ID:1` | `CdbTend_1` | Tendon of Prestressing Schemes |
| `4/ID:2` | `CdbTend_2` | Anchor of Prestressing Schemes |
| `4/ID:3` | `CdbTend_3` | Jack of Prestressing Schemes |
| `4/ID:4` | `CdbTend_4` | Presets for friction calculation |
| `5/ID:0` | `CdbArea` | Geometric Area |
| `5/ID:10` | `CdbArea_cpt` | Control points of area |
| `5/ID:11` | `CdbArea_pts` | AreaPointonSurface |
| `5/ID:12` | `CdbArea_cpi` | COONsPatchInfo |
| `5/ID:290` | `CdbGard_pts` | AreaPointonSurface |
| `5/ID:291` | `CdbGard_nku` | Knots of a Nurb |
| `5/ID:292` | `CdbGard_nkv` | Knots of a Nurb |
| `5/ID:9?` | `CdbArea_nkn` | Knots of a Nurb |
| `8/ID:0` | `CdbCon_0` | Connection Headder |
| `8/ID:1` | `CdbCon_bol` | Definition of Bolts |
| `8/ID:10` | `CdbCon_mem` | Connected Member data |
| `8/ID:11` | `CdbCon_end` | Endplate of Beam |
| `8/ID:12` | `CdbCon_pin` | Pinned plate of Beam |
| `8/ID:2` | `CdbCon_wel` | Definition of Weldings |
| `8/ID:20` | `CdbCon_plt` | Additional plates in connection |
| `8/ID:3` | `CdbCon_cle` | Definition of Cleats (Angle/Latch) |
| `9/NR:-` | `CdbSect_err` | Invalid section, visualisation only |
| `9/NR:0` | `CdbSect` | SectionalValues (total section) |
| `9/NR:1` | `CdbSect_eff` | SectionalValues (effective section) |
| `9/NR:10` | `CdbSect_rec` | Standard Rectangular, T-Beam (SREC) |
| `9/NR:100` | `CdbSect_spt` | SectionStressPoint (SPT/QSP) |
| `9/NR:100002` | `CdbSect_ins` | structural database contents |
| `9/NR:1009` | `CdbSect_sub` | SectionalSubDataBlock |
| `9/NR:101` | `CdbSect_ppt` | SectionPolygonPoint (POLY/QPOL) |
| `9/NR:102` | `CdbSect_cir` | SectionCircle (CIRC/KREI) |
| `9/NR:103` | `CdbSect_pan` | SectionPanel (PLAT,WALL) |
| `9/NR:104` | `CdbSect_wel` | SectionWeld (WELD) |
| `9/NR:11` | `CdbSect_ann` | Standard Circle, Annular (SCIT) |
| `9/NR:11` | `CdbSect_cab` | Cable (CABL) |
| `9/NR:11` | `CdbSect_tub` | Standard Tube (TUBE) |
| `9/NR:110` | `CdbSect_per` | SectionPeriphery |
| `9/NR:12` | `CdbSect_pro` | Standard rolled steel shapes (PROF) |
| `9/NR:13` | `CdbSect_shw` | Standard shear wall (SHRW) |
| `9/NR:14` | `CdbSect_edb` | Standard Edge Beam (EDGB) |
| `9/NR:18` | `CdbSect_iba` | ConstructionStage (CS/BA) |
| `9/NR:18` | `CdbSect_tba` | List of construction stages |
| `9/NR:19` | `CdbSect_txt` | SectionText |
| `9/NR:190` | `CdbSect_ner` | SectionNonEffectiveRectangle (NEFF) |
| `9/NR:191` | `CdbSect_nep` | Partial non effective polygons |
| `9/NR:2` | `CdbSect_par` | SectionalValues (total part of section) |
| `9/NR:200` | `CdbSect_prf` | SectionPointReinforcement (RF/BEW) |
| `9/NR:201` | `CdbSect_lrf` | SectionLineReinforcement (LRF/LBEW) |
| `9/NR:202` | `CdbSect_crf` | SectionCircularReinforcement (CRF/KBEW) |
| `9/NR:210` | `CdbSect_urf` | SectionPeriphericReinforcement (CURF,UBEW) |
| `9/NR:211` | `CdbSect_lrp` | SectionLineReinforcement in Points |
| `9/NR:212` | `CdbSect_crp` | SectionCircularReinforcement in Points |
| `9/NR:220` | `CdbSect_usl` | SectionPeriphericShearLink |
| `9/NR:221` | `CdbSect_lsl` | SectionShearLink |
| `9/NR:222` | `CdbSect_csl` | SectionHelicalShearLink |
| `9/NR:3` | `CdbSect_pef` | SectionalValues (effective part of section) |
| `9/NR:300` | `CdbSect_cpt` | SectionCutStressPoint |
| `9/NR:301` | `CdbSect_cut` | ShearCut (CUT) |
| `9/NR:310` | `CdbSect_ptc` | PartialIntegrationPoint of shear cut |
| `9/NR:311` | `CdbSect_cpl` | Partial polygons of shear cut |
| `9/NR:312` | `CdbSect_ncp` | Partial non effective polygons for partial cut polygon |
| `9/NR:313` | `CdbSect_apl` | Partial polygons of AKT crack area |
| `9/NR:314` | `CdbSect_bpl` | Polygon of Bredt area |
| `9/NR:320` | `CdbSect_pcp` | SectionPointReinforcement for partial cut polygon |
| `9/NR:321` | `CdbSect_lcp` | SectionLineReinforcement for partial cut polygon |
| `9/NR:4` | `CdbSect_add` | SectionalValuesShear , Temperature |
| `9/NR:5` | `CdbSect_war` | SectionalValuesWarping |
| `9/NR:6` | `CdbSect_pla` | SectionalPlasticForces |
| `9/NR:6?` | `CdbSect_wls` | SectionWorklaw Serviceability Analysis |
| `9/NR:7` | `CdbSect_des` | SectionalValuesDesign |
| `9/NR:7?` | `CdbSect_wlu` | SectionWorklaw Ultimate Analysis |
| `9/NR:8` | `CdbSect_gv` | SectionalGeometricValues |
| `9/NR:8` | `CdbSect_pre` | SectionalForcesPrestress |
| `9/NR:8` | `CdbSect_tra` | SectionalAppliedTransformation |
| `9/NR:80` | `CdbSect_cw` | Hydrodynamic coefficients (WIND/Wave loading) |
| `9/NR:81` | `CdbSect_wpa` | SectionWindParameters for Wind loading (WPAR) |
| `9/NR:82` | `CdbSect_wde` | SectionWindDerivativa for Wind loading (WIND) |
| `9/NR:9` | `CdbSect_lay` | SectionalReinforcementLayer (LAY) |
| `9/NR:90` | `CdbSect_usr` | SectionUserValues (SV/QW) |
| `9/NR:900` | `CdbSect_hyd` | SectionalHydraulics total section |
| `9/NR:903` | `CdbSect_hyp` | SectionalHydraulics partial section |
| `9/NR:904` | `CdbSect_hya` | SectionalHydraulicsAddval |
| `9/NR:91` | `CdbSect_mat` | SectionalMaterial list |
| `9/NR:910` | `CdbSect_hys` | SectionalHydraulicsPolygon |
| `9/NR:97` | `CdbSect_vad` | SectionVarDefaults |
| `9/NR:98` | `CdbSect_var` | SectionVarValues |
| `9/NR:99` | `CdbSect_ref` | SectionReference |

### 10-19 &mdash; System, groups, load cases, construction stages, masses

| KWH/KWL | Type | Description |
|---|---|---|
| `10/00` | `CdbSyst` | SystemInfo |
| `10/1:0` | `CdbSyst_des` | SystemDesignCode |
| `10/1:1` | `CdbSyst_act` | Predefined Actions from INI-file |
| `10/1:2` | `CdbSyst_com` | Possible Combination of actions |
| `10/1:3` | `CdbSyst_c_a` | Actions for Possible Combination of actions |
| `11/00` | `CdbGrp` | Primary group data |
| `12/LC:011` | `CdbLc_eval` | Evaluation request |
| `12/LC:012` | `CdbLc_copy` | Loads from other loadcases |
| `12/LC:013` | `CdbLc_copi` | Loads from other loadcases |
| `12/LC:10?` | `CdbLc_poin` | Free point loads |
| `12/LC:11?` | `CdbLc_line` | Free line loads |
| `12/LC:12?` | `CdbLc_area` | Free area loads |
| `12/LC:13?` | `CdbLc_volu` | Free volume loads |
| `12/LC:14?` | `CdbLc_curv` | Free spline loads |
| `12/LC:199` | `CdbGlc_guid` | Unique identifier of loading member |
| `12/LC:2` | `CdbLc_supe` | Superposition load case |
| `12/LC:2?` | `CdbLc_mbody` | Rotation of Body |
| `12/LC:300` | `CdbLc_trai` | Train loading |
| `12/LC:301` | `CdbLc_tral` | Individual loads of Train loading |
| `12/LC:4` | `CdbLc_eige` | Eigenmode load case |
| `12/LC:400` | `CdbLc_wind` | wind loading |
| `12/LC:401` | `CdbLc_wtop` | Wind environment |
| `12/LC:402` | `CdbLc_wrou` | Roughness (wind) |
| `12/LC:410` | `CdbLc_wspe` | wind spectrum |
| `12/LC:411` | `CdbLc_wtst` | wind coherence test requests |
| `12/LC:420` | `CdbLc_wprc` | wind profile control values |
| `12/LC:420` | `CdbLc_wpro` | wind profile distinct values |
| `12/LC:430` | `CdbLc_whis0` | wind history control values |
| `12/LC:500` | `CdbLc_wave` | Wave Loading |
| `12/LC:600` | `CdbLc_macro` | Marks begin/end of macro generated loads |
| `12/LC:80` | `CdbLc_cact0` | Group of Actions for SUPP-task |
| `12/LC:81` | `CdbLc_cact1` | current action member |
| `12/LC:82` | `CdbLc_cact2` | current loadcase of action |
| `12/LC:89` | `CdbLc_lres` | Explicit factors for selected results |
| `12/LC:90` | `CdbLc_lpos` | Position of Load trains |
| `12/LC:91` | `CdbLc_lpo1` | Individual position of Point load |
| `12/LC:92` | `CdbLc_lpo2` | Individual position of Block load |
| `12/LC:93` | `CdbLc_lpo3` | Individual residual loadings |
| `12/LC:99` | `CdbLc_lpox` | Spandefinitions from ELLA |
| `12/LC:?` | `CdbLc_ctrl` | Information on loadcase LC |
| `13/LC:0` | `CdbLc_hist` | TimeHistoryTitle |
| `13/LC:11` | `CdbLc_fsin` | Harmonic function additive |
| `13/LC:12` | `CdbLc_fstp` | Periodic stepping function additive |
| `13/LC:13` | `CdbLc_fina` | Aperiodic function additive |
| `13/LC:21` | `CdbLc_fsinm` | Harmonic function multiplier |
| `13/LC:22` | `CdbLc_fstpm` | Periodic stepping function multiplier |
| `13/LC:23` | `CdbLc_finm` | Aperiodic function multiplier |
| `13/LC:8` | `CdbLc_stat` | Statistics and extended data for time series |
| `13/LC:8?` | `CdbLc_ftval` | Visualisation functions and spectra |
| `13/LC:9` | `CdbLc_damp` | Damping values |
| `13/LC:9?` | `CdbLc_fmodc` | Explicit modal coordinates |
| `13/LC:9??` | `CdbLc_resw` | Response spectra wind |
| `13/LC:?0` | `CdbLc_fval` | Discrete function values |
| `13/LC:???` | `CdbLc_resp` | Response seismic spectra |
| `13/LC:????` | `CdbLc_fref` | Discrete reference function values |
| `14/-1` | `CdbAcc_task` | Accumulated superposition task commands |
| `14/0` | `CdbAct_rule` | Superposition commands (old Version) |
| `14/0` | `CdbAct_task` | Current superposition task commands |
| `14/ID:1` | `CdbLc_act` | Action defaults |
| `14/NR:1` | `CdbLc_act1` | Action member |
| `14/NR:1?` | `CdbLc_act_r` | Response Spectra |
| `14/NR:2` | `CdbLc_act_l` | loadcase of action |
| `14/NR:Z-` | `CdbLc_act0` | Group of Actions for SUPP-task |
| `15/-1` | `CdbCsm_grp` | Construction Stage Group Definitions |
| `15/-10` | `CdbCsg_cs` | CSG |
| `15/-103` | `CdbAse_stex` | CSM ASE-Steifigkeitsdatei ist nicht verwendar see CSM_IN_OUT1( |
| `15/-104` | `CdbBem_tena` | BEMESS-anrechenbaren Spannstahlflaeche see CSM_IN_OUT1() |
| `15/-105` | `CdbAse_ush` | ASE PUSH CONT see CSM_IN_OUT1() |
| `15/-106` | `CdbAse_lfsp` | ASE STEP LFSP see CSM_IN_OUT1() |
| `15/-107` | `CdbAse_actb` | ASE active bending see CSM_IN_OUT1() |
| `15/-108` | `CdbBem_sigt` | BEMESS Spannstahl Bemessungsspannung see CSM_IN_OUT1() |
| `15/-109` | `CdbAse_q8x8` | ASE Q8x8 8X8 Matrix fr Holzplatten see CSM_IN_OUT1() |
| `15/-11` | `CdbCsg_cgrp` | CSG |
| `15/-110` | `CdbAse_kopn` | ASE CTRL COUP Normalforce of couplings |
| `15/-12` | `CdbCsg_clas` | CSG |
| `15/-13` | `CdbCsg_csys` | CSG |
| `15/-14` | `CdbCsg_ccrl` | CSG |
| `15/-15` | `CdbCsg_cgw` | CSG |
| `15/-16` | `CdbCsg_echo` | CSG |
| `15/-17` | `CdbCsm_used` | CSM Design USED_Y_DESI(0 |
| `15/-18` | `CdbCsm_lanc` | CSM LAN_CSM Eingabesprache |
| `15/-19` | `CdbCsm_cscr` | CSM Creep construction stages header record |
| `15/-19` | `CdbCsm_dphi` | CSM Creep coefficient increments for creep stages by group and |
| `15/-2` | `CdbCsm_lc` | Construction Stage Loadcase Definitions |
| `15/-20` | `CdbCsm_cssh` | CSM Shrinkage construction stages header record |
| `15/-20` | `CdbCsm_deps` | CSM Shrinkage strain increments for stages by group and materia |
| `15/-21` | `CdbCsm_eq21` | CSM Formfinding Optimisation EQU... see CSM_IN_OUT1() |
| `15/-24` | `CdbCsm_eq24` | CSM Formfinding Optimisation EQU... see CSM_IN_OUT1() |
| `15/-25` | `CdbCsm_eq25` | CSM Formfinding Optimisation EQU... see CSM_IN_OUT1() |
| `15/-26` | `CdbCsm_eq26` | CSM Formfinding Optimisation EQU... see CSM_IN_OUT1() |
| `15/-3` | `CdbCsm_cs` | Construction Stage Table |
| `15/-31` | `CdbCsm_quea` | CSM GRP2 QUEA QEMX see CSM_IN_OUT1() |
| `15/-32` | `CdbCsm_movs` | CSM Moving Springs see CSM_IN_OUT1() |
| `15/-33` | `CdbCsm_cabl` | CSM Cable info see CSM_IN_OUT1() |
| `15/-34` | `CdbCsm_qcut` | CSM QCUT see CSM_IN_OUT1() |
| `15/-35` | `CdbCsm_grba` | CSM Gruppeninfo je BA fuer ASE GRUP-BA-20 see CSM_IN_OUT1() |
| `15/-36` | `CdbCsm_plex` | CSM PLEX see CSM_IN_OUT1() |
| `15/-37` | `CdbCsm_kink` | CSM KINK see CSM_IN_OUT1() |
| `15/-38` | `CdbCsm_rset` | CSM RSET see CSM_IN_OUT1() |
| `15/-39` | `CdbCsm_dess` | CSM DESI Steuerungen see CSM_IN_OUT1() |
| `15/-4` | `CdbCsm_cree` | creep+shrink values for manual input |
| `15/-45` | `CdbCsm_ibaf` | CSM IBA_first_beam_CSM fuer _desi.dat see CSM_IN_OUT1() |
| `15/-46` | `CdbCsm_urs1` | CSM Texte fuer URS1_desi see CSM_IN_OUT1() |
| `15/-47` | `CdbCsm_coaa` | CSM COMB_AASHTO_desi see CSM_IN_OUT1() |
| `15/-5` | `CdbCsm_ctrl` | CSM CTRL control parameter see CSM_IN_OUT1() |
| `15/-54` | `CdbCsm_cont` | CSM EQLF-CONT see CSM_IN_OUT1() |
| `15/-6` | `CdbCsm_wait` | CSM_WAIT parameter see CSM_IN_OUT1() |
| `15/-61` | `CdbCsm_aset` | CSM C1 Texte fuer ASE |
| `15/-7` | `CdbCsm_d_ep` | CSM D_EPS parameter see CSM_IN_OUT1() |
| `15/-71` | `CdbCsm_spei` | CSM STEU SPEI 1 W3 20,36 see CSM_IN_OUT1() |
| `15/-72` | `CdbCsm_boul` | CSM later activated boundaries see CSM_IN_OUT1() |
| `15/-73` | `CdbCsm_uebe` | CSM UEBE precamber analysis see CSM_IN_OUT1() |
| `15/-8` | `CdbCsm_boxu` | CSM BOXUNIT parameter see CSM_IN_OUT1() |
| `15/-9` | `CdbCsm_runi` | CSM RUNIT_CSM parameter see CSM_IN_OUT1() |
| `15/LC:1` | `CdbCsm_lc1` | CSM loadcase parameters Group members |
| `15/LC:2` | `CdbCsm_lc2` | CSM loadcase parameters quad-tendon members |
| `16/0:0` | `CdbPerf_cat` | Definition of performance categories (=sets of performance crit |
| `16/0:1` | `CdbPerf_crt` | Definition of performance criterion |
| `16/0:173` | `CdbPlim_lnk` | Definition of link/spring/hinge element performance thresholds |
| `16/LC` | `CdbPerf_res` | Performance status of elements |
| `17/00` | `CdbMtot_ctl` | Control of total mass calculation |
| `17/01:-1` | `CdbMtot` | Total mass |
| `17/01:0` | `CdbMtot_elm` | Total masses of FE elements |
| `17/02` | `CdbMtot_mat` | Masses per material |
| `17/03` | `CdbMtot_grp` | Masses per group |
| `17/04` | `CdbMtot_sgr` | Masses per secondary group |
| `17/05` | `CdbMtot_sec` | Masses per cross section |
| `17/101:-1` | `CdbMlca` | Total masses of life cycle assessment per phase |
| `17/101:-1` | `CdbMlca_tot` | Total mass of of life cycle assessment |
| `17/102:Z+` | `CdbMlca_ma0` | Total masses of life cycle assessment per material |
| `17/102:Z+` | `CdbMlca_mat` | Masses of life cycle assessment per material and phase |
| `17/103:Z+` | `CdbMlca_gr0` | Total masses of Life cycle assessment per group |
| `17/103:Z+` | `CdbMlca_grp` | Masses of Life cycle assessment per group and phase |
| `17/104:chr` | `CdbMlca_sg0` | Total masses of Life cycle assessment per secondary group |
| `17/104:chr` | `CdbMlca_sgr` | Masses of Life cycle assessment per secondary group and phase |
| `17/114:chr` | `CdbMlca_ds0` | Total masses of Life cycle assessment of design elements per se |
| `17/114:chr` | `CdbMlca_dsg` | Masses of Life cycle assessment of design elements per secondar |
| `17/116:Z+` | `CdbMlca_dt0` | Masses of Life cycle assessment of design elements per structur |
| `17/116:Z+` | `CdbMlca_dtp` | Masses of Life cycle assessment of design elements per structur |
| `17/14` | `CdbMtot_dsg` | Masses of design elements per secondary group |
| `17/15` | `CdbMtot_dsc` | Masses of design elements per cross section |
| `17/16` | `CdbMtot_dtp` | Masses of design elements per structural member |
| `18/-1` | `CdbView` | View definitions (Exchange ANIMATOR-WINGRAF) |
| `18/-101:1` | `CdbAni_sele` | Dialogbox Animator selection request |
| `18/-101:2` | `CdbAni_ctrl` | Dialogbox Animator drawing controls |
| `18/-103` | `CdbAni_sres` | Selection result from Animator |
| `18/-2` | `CdbView_sel` | currently selected elements in WINGRAF |
| `18/-3` | `CdbView_sre` | currently selected results in WINGRAF |
| `18/-4:+` | `CdbMtxt_elm` | Definition of manufacturing elements |
| `18/-4:-` | `CdbMtxt_nod` | Definition of new nodes |
| `18/-4:0` | `CdbMtxt_0` | Header for membrane manufacturing |
| `18/-5` | `CdbView_mco` | Colour of material |
| `18/-6` | `CdbView_gco` | Colour of group |
| `18/LCD` | `CdbLc_self` | Self weight loading of elements from ASE |
| `19/LC` | `CdbGrp_bil` | Bilances of Flow in HYDRA |

### 20-29 &mdash; Nodes and nodal results

| KWH/KWL | Type | Description |
|---|---|---|
| `20/00` | `CdbNode` | Nodes |
| `20/001` | `CdbNode_edg` | node edge lists |
| `20/11:+` | `CdbNode_grp` | Nodegroups |
| `20/11:0` | `CdbNode_grc` | number of Nodegroups |
| `21/00:+` | `CdbNode_kin` | Standard kinematic constraint |
| `21/00:0` | `CdbNode_kic` | Info on kinematic constraints |
| `21/00:?????99` | `CdbNode_kif` | general constraints (factor list) |
| `21/00:?????99` | `CdbNode_kig` | general constraints (equation list) |
| `21/09` | `CdbNode_kih` | Hydraulic couplings |
| `22/LC:+` | `CdbNode_kfo` | Constraining forces |
| `22/LC:0` | `CdbNode_kfc` | Max. Constraining Forces |
| `23/LC:*` | `CdbNode_acc` | Base acceleration |
| `23/LC:*` | `CdbNode_aci` | Base acceleration info |
| `23/LC:*` | `CdbNode_l` | Nodal_loads |
| `23/LC:*` | `CdbNode_lw` | prescribed support displacements |
| `23/LC:*` | `CdbNode_roi` | Rotation of Body information |
| `23/LC:*` | `CdbNode_rot` | Rotation of Body |
| `23/LC:+` | `CdbNode_la` | prescribed nodal accelerations |
| `24/LC:+` | `CdbN_disp` | Displacements and support forces of nodes |
| `24/LC:0` | `CdbN_dispc` | Max. Displacements and support forces |
| `25/LC:+` | `CdbN_velo` | velocitys and acceleration of nodes |
| `25/LC:0` | `CdbN_veloc` | Max. velocities and accelerations of nodes |
| `26/LC:+` | `CdbN_dispi` | Displacement increments and residual forces |
| `26/LC:0` | `CdbN_dispic` | Max. Displacement and forces increments |
| `27/LC:+` | `CdbN_dispt` | Cooordinate offsets |
| `27/LC:0` | `CdbN_disptc` | Max. Cooordinate offsets |
| `28/LC:+` | `CdbN_flow` | Flow values in nodes |
| `28/LC:0` | `CdbN_flowt` | Flow values in nodes Time Value |
| `29/LC` | `CdbN_mphyst` | Skalar physical values in all nodes (Multiphysic) |

### 30-49 &mdash; Structural elements (points/lines/areas/volumes), design elements, tendons

| KWH/KWL | Type | Description |
|---|---|---|
| `30/NR:0` | `CdbGpt` | Structural points |
| `30/NR:1` | `CdbGpt_coh` | Dimension of column head |
| `30/NR:10` | `CdbGpt_spr` | Elastic Spring support |
| `30/NR:1005` | `CdbGpt_frr` | Footing required reinforcement |
| `30/NR:1006` | `CdbGpt_slp` | Sleeve foundation properties |
| `30/NR:11` | `CdbGpt_kin` | Kinematic Constraint |
| `30/NR:12` | `CdbGpt_spc` | Elastic Spring connection (obsoleted) |
| `30/NR:13` | `CdbGpt_sres` | Predefined result set |
| `30/NR:14` | `CdbGpt_lnk` | Link Element at Structural Point |
| `30/NR:2` | `CdbGpt_hau` | Dimension of voute |
| `30/NR:3` | `CdbGpt_pun` | Dimension of punching perimeter |
| `30/NR:4` | `CdbGpt_col` | Connecting columns |
| `30/NR:5` | `CdbGpt_foo` | Footing instance definition |
| `30/NR:6` | `CdbGpt_hpi` | Halfspace pile |
| `30/NR:8` | `CdbGpt_con` | Steelconnection reference |
| `30/NR:997` | `CdbSpt_attr` | Attributes of structural member |
| `30/NR:998` | `CdbGpt_dads` | List of origin ids the structural member has been created from |
| `30/NR:999` | `CdbSpt_guid` | Unique identifier of structural point |
| `31/0:+` | `CdbGln_matc` | Heritage of Structural Lines |
| `31/0:0` | `CdbGln_mat0` | Header of heritage of Structural Lines |
| `31/NR:-` | `CdbGln_ref` | Reference to another Geometry |
| `31/NR:0` | `CdbGln` | Structural lines |
| `31/NR:100` | `CdbGln_beam` | Properties of beams (obsoleted) |
| `31/NR:101` | `CdbGln_bpro` | Properties of beams |
| `31/NR:102` | `CdbGln_supp` | Support of Structural lines |
| `31/NR:120` | `CdbGln_exyz` | Explicit nodes on lines |
| `31/NR:121` | `CdbGln_elnr` | Elements generated on lines |
| `31/NR:130` | `CdbGln_sct` | Beams sections |
| `31/NR:997` | `CdbSln_attr` | Attributes of structural member |
| `31/NR:998` | `CdbGln_dads` | Ids of items being an anchestor |
| `31/NR:999` | `CdbSln_guid` | Unique identifier of structural line |
| `31/NR:??` | `CdbGln_geo` | Geometric properties |
| `32/0:+` | `CdbGar_matc` | Heritage of Structural Areas |
| `32/0:0` | `CdbGar_mat0` | Header of heritage of Structural Areas |
| `32/NR:-` | `CdbGar_ref` | Reference to another Geometry |
| `32/NR:0` | `CdbGar` | Structural area |
| `32/NR:1` | `CdbGar_boun` | Outer Boundary of Area |
| `32/NR:10` | `CdbGar_geo` | Geometry of surface |
| `32/NR:11` | `CdbGar_surf` | UserPointonSurface |
| `32/NR:12` | `CdbGar_coon` | COONsPatchInfo |
| `32/NR:121` | `CdbGar_elnr` | Generated elements from area |
| `32/NR:2` | `CdbGar_hole` | Inner Boundary of Area |
| `32/NR:220` | `CdbGar_exyz` | Explicit QUAD nodes on area |
| `32/NR:221` | `CdbGar_supp` | Support and coupling of structural areas |
| `32/NR:3` | `CdbGar_con3` | Prescribed Edges/Points |
| `32/NR:4` | `CdbGar_con4` | Domain-Subdivision-Edges |
| `32/NR:9` | `CdbGar_mesh` | Prescribed Mesh size |
| `32/NR:997` | `CdbSar_attr` | Attributes of structural member |
| `32/NR:998` | `CdbGar_dads` | Ids of items being an anchestor |
| `32/NR:999` | `CdbSar_guid` | Unique identifier of structural area |
| `33/NR:+` | `CdbGvo_surf` | Involved Surfaces |
| `33/NR:0` | `CdbGvo` | StructuralVolume |
| `34/ID:1` | `CdbTbas_def` | Tower Base definition |
| `34/ID:2` | `CdbTowr_def` | Tower definition |
| `34/ID:999` | `CdbTowr_gui` | Unique identifier of tower |
| `34/NR:0` | `CdbSlvl_def` | Storey Level definition |
| `34/NR:999` | `CdbSlvl_gui` | Unique identifier of storey |
| `35/ID:0` | `CdbDsln_def` | Design Element Definition |
| `35/ID:1` | `CdbDgeo_def` | Design Element Geometry |
| `35/ID:2` | `CdbDslc_def` | Design Sections |
| `35/ID:3` | `CdbDsel_ids` | Selection of finite elements |
| `35/ID:4` | `CdbDsel_box` | Selection of elements with Box |
| `35/ID:5` | `CdbDsln_grp` | Secondary groups of design element |
| `35/ID:999` | `CdbDsln_uid` | Unique identifier of design element |
| `37/ID:0` | `CdbSgrp` | Secondary groups |
| `37/ID:0???` | `CdbSgrp_lis` | Calculated Selective Element List |
| `37/ID:1` | `CdbSgrp_box` | Selective Basic-Volume |
| `37/ID:1???` | `CdbSgrp_add` | Selecting Element List |
| `37/ID:2` | `CdbSgrp_pol` | Selective Polyeder-Volume |
| `37/ID:2???` | `CdbSgrp_sub` | Excluding Element List |
| `37/ID:3` | `CdbSgrp_pro` | Optional Additional Properties |
| `37/ID:3???` | `CdbSgrp_sel` | Property-Values |
| `38/NR:0` | `CdbGlar_0` | Load distribution areas Header |
| `38/NR:1` | `CdbGlar_nod` | Node of load distribution area |
| `38/NR:10?` | `CdbGlar_l` | Load distribution areas Beamloads |
| `38/NR:1?` | `CdbGlar_p` | Load distribution areas Pointloads |
| `38/NR:2` | `CdbGlar_qua` | QUAD of load distribution area |
| `38/NR:3` | `CdbGlar_seg` | BEAM segments within area |
| `39/NR:0` | `CdbSpt` | Structural points |
| `39/NR:1` | `CdbSpt_coh` | Dimension of column head |
| `39/NR:10` | `CdbSpt_spr` | Elastic Spring support |
| `39/NR:100` | `CdbSln` | Structural lines |
| `39/NR:101` | `CdbSln_beam` | Properties of beams |
| `39/NR:102` | `CdbSln_supp` | Support of Structural lines |
| `39/NR:11` | `CdbSpt_kin` | Kinematic Constraint |
| `39/NR:12` | `CdbSpt_spc` | Elastic Spring connection (obsoleted) |
| `39/NR:120` | `CdbSln_exyz` | Explicit nodes on lines |
| `39/NR:13` | `CdbSpt_sres` | Predefined result set |
| `39/NR:130` | `CdbSln_sct` | Beams sections |
| `39/NR:14` | `CdbSpt_lnk` | Link Element at Structural Point |
| `39/NR:190` | `CdbSaxd_nkn` | Knots of a Nurb |
| `39/NR:191` | `CdbSaxd_cpt` | Control point of a Nurb |
| `39/NR:192` | `CdbSaxd_pt` | Data point on curve |
| `39/NR:193` | `CdbSaxd_arc` | Circular Arc |
| `39/NR:2` | `CdbSpt_hau` | Dimension of voute |
| `39/NR:200` | `CdbSar` | Structural area |
| `39/NR:201` | `CdbSar_boun` | Outer Boundary of Area |
| `39/NR:202` | `CdbSar_hole` | Inner Boundary of Area |
| `39/NR:203` | `CdbSar_con3` | Prescribed Edges/Points |
| `39/NR:204` | `CdbSar_con4` | Prescribed Edges/Points |
| `39/NR:210` | `CdbSar_inf` | GeometricAreaInfo |
| `39/NR:211` | `CdbSar_pts` | AreaPointonSurface |
| `39/NR:212` | `CdbSar_cpi` | COONsPatchInfo |
| `39/NR:220` | `CdbSar_exyz` | Explicit QUAD nodes on area |
| `39/NR:221` | `CdbSar_supp` | Support and coupling of structural areas |
| `39/NR:290` | `CdbSard_pts` | AreaPointonSurface |
| `39/NR:291` | `CdbSard_nku` | Knots of a Nurb |
| `39/NR:292` | `CdbSard_nkv` | Knots of a Nurb |
| `39/NR:3` | `CdbSpt_pun` | Dimension of punching perimeter |
| `39/NR:300` | `CdbSvo` | StructuralVolume |
| `39/NR:30?` | `CdbSvo_surf` | Involved Surfaces |
| `39/NR:4` | `CdbSpt_col` | Connecting columns |
| `39/NR:5` | `CdbSpt_foo` | Footing instance definition |
| `39/NR:6` | `CdbSpt_hpi` | Halfspace pile |
| `39/NR:8` | `CdbSpt_con` | Steelconnection reference |
| `39/NR:90` | `CdbSln_nkn` | Knots of a Nurb |
| `39/NR:91` | `CdbSln_cpt` | Control point of a Nurb |
| `39/NR:910` | `CdbSgr2_def` | Secondary Group Definition |
| `39/NR:911` | `CdbSgr2_sid` | Secondary Group by ID |
| `39/NR:912` | `CdbSgr2_uid` | Secondary Group by GUID |
| `39/NR:913` | `CdbSgr2_box` | Secondary Group by Bounding-Box |
| `39/NR:92` | `CdbSln_pt` | Data point on curve |
| `39/NR:93` | `CdbSln_arc` | Circular Arc |
| `39/NR:997` | `CdbSmb_attr` | Attributes of structural member |
| `39/NR:999` | `CdbSmb_guid` | Unique identifier of structural member |
| `40/NR:0` | `CdbTendaxis` | Reference axis |
| `40/NR:1` | `CdbTendax_1` | Reference axis stations |
| `40/NR:5` | `CdbTndaxdef` | Reference axis definition |
| `41/NR:0` | `CdbTendspli` | Duct curves |
| `41/NR:110` | `CdbTendints` | Duct curve intersections |
| `41/NR:112` | `CdbDuctgrps` | Element groups for duct intersections |
| `41/NR:999` | `CdbTgeoguid` | Unique identifier of TGEO (aka tendon spline or duct curve) |
| `41/NR:??` | `CdbTendsp_i` | Input points |
| `43/NR` | `CdbTendtopp` | Tendon toppoints |
| `44/NR:0` | `CdbTendon` | Tendons |
| `44/NR:1` | `CdbTendjack` | Tendon jacking data |
| `44/NR:2` | `CdbTendfact` | Tendon jacking factors |
| `44/NR:5` | `CdbTenddef1` | Tendon definition for tendon 2.0 |
| `44/NR:7` | `CdbTendres1` | Tendon result 1 |
| `44/NR:8` | `CdbTendres2` | Tendon result 2 |
| `44/NR:999` | `CdbTendguid` | Unique identifier of the tendon |

### 61-99 &mdash; Design cases, design status, time history, storeys

| KWH/KWL | Type | Description |
|---|---|---|
| `61/LC:0` | `CdbDc_beam` | DesignCaseDefintionBeam |
| `61/LC:1` | `CdbDc1_beam` | DesignCaseMaterialBeam |
| `62/LC:0` | `CdbDc_dsln` | DesignCaseDefintionDsln |
| `62/LC:1` | `CdbDc1_dsln` | DesignCaseMaterialDsln |
| `64/LC:0` | `CdbDc_bsct` | DesignCaseDefintionBsct |
| `64/LC:1` | `CdbDc1_bsct` | DesignCaseMaterialBsct |
| `65/LC:0` | `CdbDc_trus` | DesignCaseDefintionTrus |
| `65/LC:1` | `CdbDc1_trus` | DesignCaseMaterialTrus |
| `66/LC:0` | `CdbDc_cabl` | DesignCaseDefintionCabl |
| `66/LC:1` | `CdbDc1_cabl` | DesignCaseMaterialCabl |
| `67/LC:0` | `CdbDc_quad` | DesignCaseDefintionQuad |
| `67/LC:1` | `CdbDc1_quad` | DesignCaseMaterialQuad |
| `68/LC:0` | `CdbDc_bric` | DesignCaseDefintionBric |
| `68/LC:1` | `CdbDc1_bric` | DesignCaseMaterialBric |
| `69/NR:1` | `CdbDst_memb` | DesignStatusMember |
| `69/NR:2` | `CdbDst_chck` | DesignStatusCheck |
| `69/NR:3` | `CdbDst_resu` | DesignStatusResult |
| `69/NR:30` | `CdbDst_locp` | DesignStatusLocationPoint |
| `69/NR:31` | `CdbDst_locl` | DesignStatusLocationLine |
| `69/NR:32` | `CdbDst_loca` | DesignStatusLocationArea |
| `69/NR:35` | `CdbDst_lcin` | DesignStatusLoadCaseInfo |
| `69/NR:901` | `CdbDst_guid` | Unique identifier of design status member |
| `80/HC:-1??` | `CdbHist_hed` | TimeHistoryTitle |
| `80/HC:-2??` | `CdbHist_ext` | TimeHistoryExtended |
| `80/HC:-9??` | `CdbHist_par` | IterationParameters |
| `80/HC:-??` | `CdbHist` | Identification of history elements |
| `80/HC:Z+` | `CdbHist_val` | Transient data |
| `87/0:+` | `CdbSlvl_dat` | Storey Level Data |
| `87/0:chr` | `CdbTbas_dat` | Tower Base Data |
| `87/LC:+` | `CdbSlvl_res` | Structural Storey Level Results |

### 100-119 &mdash; Beams: geometry, loads, forces, stresses, reinforcement

| KWH/KWL | Type | Description |
|---|---|---|
| `100/00:+` | `CdbBeam` | Beams |
| `100/00:0` | `CdbBeam_sct` | Beams sections |
| `100/01` | `CdbBeam_tra` | transformation matrix |
| `100/03` | `CdbBeam_trs` | Info about dynamic moving beams (TREX) |
| `100/05` | `CdbBeam_tnd` | tendons of beams |
| `101/LC:*` | `CdbBeam_cl` | cubic beamloads |
| `101/LC:*` | `CdbBeam_dl` | distributed beam loading on reference |
| `101/LC:*` | `CdbBeam_sl` | single beam loads |
| `101/LC:*` | `CdbBeam_tl` | distributed beam loading on reference |
| `101/LC:*` | `CdbBeam_wl` | dynamic wind loads |
| `102/0` | `CdbBeam_fox` | Total External Beam forces |
| `102/LC:0` | `CdbBeam_foc` | Maximum of Total Beam forces and deformations |
| `102/LC:Z!` | `CdbBeam_for` | Total Beam forces and deformations |
| `103/LC` | `CdbBeam_sti` | Stiffness of beams |
| `104/LC:0` | `CdbBeam_crc` | Parameter of creep interval for each material |
| `104/LC:Z!` | `CdbBeam_crf` | resulting forces of redistribution |
| `104/LC:Z!` | `CdbBeam_crp` | forces on sectional parts per material |
| `104/LC:Z!` | `CdbBeam_crt` | changes of tendon force |
| `104/LC:Z!` | `CdbBeam_tsn` | thermal eigen stress per material |
| `105/LC:+` | `CdbBeam_stt` | stresses in tendons |
| `105/LC:+` | `CdbBeam_tst` | thermal eigen stress per material |
| `105/LC:0` | `CdbBeam_stc` | Maximum stresses in cross-section of beams |
| `105/LC:Z!` | `CdbBeam_str` | Stresses in cross-section of beams |
| `106/DC:+` | `CdbBeam_rfc` | reinforcement of beams |
| `106/DC:+` | `CdbBeam_rfi` | info of reinforcement of beams |
| `106/DC:0` | `CdbBeam_rf0` | max. values of reinforcement |
| `107/LC:0` | `CdbBeam_de0` | max. values of Ultimate/Plastic Design results |
| `107/LC:Z!` | `CdbBeam_des` | Ultimate/Plastic Design results |
| `108/LC` | `CdbBeam_pif` | reducing factors of stiffness |
| `111/LC:+` | `CdbBeam_hrc` | Implicit Hinge Reactions |
| `111/LC:0` | `CdbBeam_hr0` | Maximum of Implicit Hinge Reactions |
| `112/LC:0` | `CdbBeam_ftc` | Maximum of Beam forces without plate components |
| `112/LC:Z!` | `CdbBeam_ftr` | Beam forces without plate components |
| `115/LC:+` | `CdbBeam_mpt` | Cross-sectional material point reactions |
| `115/LC:0` | `CdbBeam_mp0` | Extremal values of cross-sectional material point reactions |
| `116/LC:0` | `CdbBeam_tf0` | Maximum of tendon forces in beams |
| `116/LC:Z!` | `CdbBeam_tf` | Tendon forces in beams |

### 120-139 &mdash; Design elements (DSLN)

| KWH/KWL | Type | Description |
|---|---|---|
| `120/00:+` | `CdbDsln` | Design elements |
| `120/00:0` | `CdbDsln_sct` | Design element sections |
| `120/05` | `CdbDsln_tnd` | tendons of design elements |
| `121/LC:*` | `CdbDsln_dl` | distributed design element loading on reference axis |
| `121/LC:*` | `CdbDsln_sl` | single loads on design element |
| `121/LC:*` | `CdbDsln_tl` | distributed design element loading on reference axis |
| `122/LC:0` | `CdbDsln_ftc` | Maximum of Design element forces without plate components |
| `122/LC:Z!` | `CdbDsln_ftr` | Design element forces without plate components |
| `123/LC` | `CdbDsln_sti` | Stiffness of design elements |
| `124/LC:0` | `CdbDsln_crc` | Parameter of creep interval for each material |
| `124/LC:Z!` | `CdbDsln_crf` | resulting forces of redistribution |
| `124/LC:Z!` | `CdbDsln_crp` | forces on sectional parts per material |
| `124/LC:Z!` | `CdbDsln_crt` | changes of tendon force |
| `124/LC:Z!` | `CdbDsln_tsn` | thermal eigen stress per material |
| `125/LC:+` | `CdbDsln_stt` | stresses in tendons |
| `125/LC:+` | `CdbDsln_tst` | thermal eigen stress per material |
| `125/LC:0` | `CdbDsln_stc` | Maximum stresses in cross-section of design elements |
| `125/LC:Z!` | `CdbDsln_str` | Stresses in cross-section of design elements |
| `126/DC:+` | `CdbDsln_rfc` | reinforcement of design elements |
| `126/DC:+` | `CdbDsln_rfi` | info of reinforcement of design elements |
| `126/DC:0` | `CdbDsln_rf0` | max. values of reinforcement |
| `126/DC:Z+` | `CdbDsln_rfs` | results of shear wall design |
| `127/LC:0` | `CdbDsln_de0` | max. values of Ultimate/Plastic Design results |
| `127/LC:Z!` | `CdbDsln_des` | Ultimate/Plastic Design results |
| `136/LC:0` | `CdbDsln_tf0` | Maximum of tendon forces in design elements |
| `136/LC:Z!` | `CdbDsln_tf` | Tendon forces in design elements |

### 140-149 &mdash; External sections (BSCT)

| KWH/KWL | Type | Description |
|---|---|---|
| `140/00:+` | `CdbBsct` | External sections |
| `140/00:0` | `CdbBsct_sct` | External sections |
| `140/05` | `CdbBsct_tnd` | tendons of external sections |
| `142/0` | `CdbBsct_fox` | Total External Forces for external sections |
| `142/LC:0` | `CdbBsct_foc` | Maximum of External sections forces |
| `142/LC:Z!` | `CdbBsct_for` | External sections forces |
| `143/LC` | `CdbBsct_sti` | Stiffness of external sections |
| `144/LC:0` | `CdbBsct_crc` | Parameter of creep interval for each material |
| `144/LC:Z!` | `CdbBsct_crf` | resulting forces of redistribution |
| `144/LC:Z!` | `CdbBsct_crp` | forces on sectional parts per material |
| `144/LC:Z!` | `CdbBsct_crt` | changes of tendon force |
| `144/LC:Z!` | `CdbBsct_tsn` | thermal eigen stress per material |
| `145/LC:+` | `CdbBsct_stt` | stresses in tendons |
| `145/LC:+` | `CdbBsct_tst` | thermal eigen stress per material |
| `145/LC:0` | `CdbBsct_stc` | Maximum stresses in cross-section of external sections |
| `145/LC:Z!` | `CdbBsct_str` | Stresses in cross-section of external sections |
| `146/DC:+` | `CdbBsct_rfc` | reinforcement of external sections |
| `146/DC:+` | `CdbBsct_rfi` | info of reinforcement of external sections |
| `146/DC:0` | `CdbBsct_rf0` | max. values of reinforcement |
| `147/LC:0` | `CdbBsct_de0` | max. values of Ultimate/Plastic Design results |
| `147/LC:Z!` | `CdbBsct_des` | Ultimate/Plastic Design results |

### 150-199 &mdash; Trusses, cables, springs, dampers, masses, boundaries, links

| KWH/KWL | Type | Description |
|---|---|---|
| `150/00` | `CdbTrus` | trusselements |
| `151/LC` | `CdbTrus_loa` | Loads on truss elements |
| `151/LC:*` | `CdbTrus_wl` | dynamic wind loads |
| `152/LC:+` | `CdbTrus_res` | results of truss elements |
| `152/LC:0` | `CdbTrus_re0` | maximum of results of truss elements |
| `155/LC:+` | `CdbTrus_str` | truss stress (AQB) |
| `155/LC:0` | `CdbTrus_st0` | checked truss stresses |
| `156/DC:+` | `CdbTrus_rfc` | reinforcement of truss |
| `156/DC:+` | `CdbTrus_rfi` | info of reinforcement of truss |
| `156/DC:0` | `CdbTrus_rf0` | max. values of reinforcement |
| `157/LC:0` | `CdbTrus_de0` | max. values of Ultimate/Plastic Design results |
| `157/LC:Z!` | `CdbTrus_des` | Ultimate/Plastic Design results |
| `160/00` | `CdbCabl` | cable elements |
| `161/LC` | `CdbCabl_loa` | loads on cables |
| `161/LC:*` | `CdbCabl_wl` | dynamic wind loads |
| `162/LC:+` | `CdbCabl_res` | results of cables |
| `162/LC:0` | `CdbCabl_re0` | maximum results of cables |
| `163/00` | `CdbCabl_slp` | slip cables |
| `165/LC:+` | `CdbCabl_str` | cable stresses (AQB) |
| `165/LC:0` | `CdbCabl_st0` | checked cable stresses |
| `166/DC:+` | `CdbCabl_rfc` | reinforcement of cables |
| `166/DC:+` | `CdbCabl_rfi` | info of reinforcement of cables |
| `166/DC:0` | `CdbCabl_rf0` | max. values of reinforcement |
| `170/00` | `CdbSpri` | Spring-elements |
| `170/LC:+` | `CdbSpri_res` | results of spring-elements |
| `170/LC:0` | `CdbSpri_re0` | maximum of results of spring-elements |
| `171/00` | `CdbDamp` | Damping elements (DYNA) |
| `172/00` | `CdbMass` | Persistent Nodal masses |
| `172/01` | `CdbMass_add` | non persistent additional nodal masses |
| `172/LD:-` | `CdbMass_efc` | Effective consistent masses |
| `172/LD:Z+` | `CdbMass_eff` | Effective nodal masses |
| `173/NR:+` | `CdbSpri_wl` | force-displacement / moment-rotation work law |
| `173/NR:0` | `CdbSpri_wl0` | (Nonlinear) Material for Link elements, Spring elements and Bea |
| `173/NR:5?` | `CdbLink_fpb` | Friction pendulum bearing parameters |
| `173/NR:9??` | `CdbSpri_wlp` | Optional performance limits for force-displacement / moment-rot |
| `174/00` | `CdbSpri_mov` | Moving Springs |
| `175/00` | `CdbS_matrix` | General systemmatrices |
| `180/00:+` | `CdbBoun` | Boundary elements |
| `180/LC:0` | `CdbBoun_rec` | maximum results of boundary elements |
| `180/LC:Z!` | `CdbBoun_res` | results of boundary elements |
| `181/LC` | `CdbBoun_sum` | resultant of boundary results |
| `183/LC` | `CdbBoun_lc` | Info on loading on boundaries |
| `187/LC` | `CdbSpri_sum` | Sum of forces of support springs |
| `188/00:+` | `CdbRset` | Sets of results |
| `188/00:0` | `CdbRset_itm` | Member of result set |
| `188/LC` | `CdbRset_dat` | Result-values for sets of results |
| `190/00:+` | `CdbLink` | Link elements |
| `190/LC:+` | `CdbLink_res` | Link Element Reactions |

### 200-299 &mdash; QUAD elements: geometry, loads, forces, stresses, reinforcement

| KWH/KWL | Type | Description |
|---|---|---|
| `200/00` | `CdbQuad` | QuadElements |
| `200/10` | `CdbQuad_p` | Quad-P-elements |
| `200/1:-` | `CdbQuad_nom` | unified Quad-node mapping to elements |
| `200/1:0` | `CdbQuad_noh` | header of unified properties of Quad-nodes |
| `200/1:Z+` | `CdbQuad_nod` | unified properties of Quad-nodes |
| `200/2:+` | `CdbQuad_edg` | Edges of Quad-elements |
| `200/2:0` | `CdbQuad_edh` | Edges of Quad-elements |
| `200/5` | `CdbQuad_ten` | tendons of Quad-elements |
| `200/6` | `CdbQuad_rim` | Prescribed Reinforcements of Quad-elements |
| `200/7:+` | `CdbQuad_ril` | Reinforcement Layers of Quad-elements |
| `200/7:0` | `CdbQuad_rid` | Reinforcement Definitions of Quad-elements |
| `200/8:+` | `CdbQcut_dir` | Material direction |
| `200/8:+` | `CdbQcut_in` | Geometry inner lines |
| `200/8:+` | `CdbQcut_new` | New cutting area |
| `200/8:+` | `CdbQcut_out` | Vertex of geometric boundary |
| `200/8:+` | `CdbQcut_war` | element warp direction |
| `200/8:0` | `CdbQcut_0` | Header for fabrication areas |
| `200/9` | `CdbTextile` | definition of cutting lines |
| `202/LC` | `CdbQuad_loa` | Quad-element loads |
| `202/LC:*` | `CdbQuad_ltn` | Quad-element prestressing tendon loads |
| `203/LC:*` | `CdbQuad_lai` | Free area loads on Quad-elements |
| `203/LC:*` | `CdbQuad_lli` | internal line loads of Quad-elements |
| `203/LC:*` | `CdbQuad_lpi` | internal single loads on Quad-elements |
| `206/NR` | `CdbQuad_lt` | Temperature load profiles for QUADs |
| `210/LC:+` | `CdbQuad_for` | forces of Quad-elements |
| `210/LC:0` | `CdbQuad_foc` | maximum forces of Quad elements |
| `211/0:-` | `CdbQuad_ngm` | grouped Quad-node mapping to elements |
| `211/0:0` | `CdbQuad_ngh` | header of grouped properties of Quad-nodes |
| `211/0:Z+` | `CdbQuad_ngd` | grouped properties of Quad-nodes |
| `211/LC:0` | `CdbQuad_nfc` | maximum forces in nodes |
| `211/LC:Z+` | `CdbQuad_nfo` | Nodal Quad forces |
| `212/LC:+` | `CdbQuad_efo` | error estimates for Quad-elements |
| `212/LC:0` | `CdbQuad_efc` | maximum error estimates for Quad-elements |
| `213/LC:+` | `CdbQuad_bed` | bedding stresses and results |
| `213/LC:0` | `CdbQuad_bec` | bedding stresses and results |
| `214/LC` | `CdbQuad_rfx` | additional information for primary loadcases |
| `215/LC:+` | `CdbQuad_rno` | nonlinear results of Quad-element |
| `215/LC:-` | `CdbQuad_rng` | nonlinear results of Quad-Gauss points |
| `215/LC:0` | `CdbQuad_rnc` | nonlinear results of Quad-element |
| `216/LC:+` | `CdbQuad_inp` | Inplane spring reaktion forces quad-element |
| `217/LC:+` | `CdbQuad_pea` | Quad peak smoothing - CTRL CONC V7 |
| `218/LC:1` | `CdbQmem_mod` | (Enhanced) Membrane modes |
| `218/LC:2` | `CdbQdrl_mod` | (Enhanced) Ansatz for membrane drilling stiffness |
| `218/LC:3` | `CdbQplt_mod` | (Enhanced) Ansatz for plate action |
| `219/LC:Z!` | `CdbBeam_plx` | T-beam TBEX - negative quad part |
| `220/LC:+` | `CdbQuad_str` | stresses of Quad-element |
| `220/LC:-` | `CdbQuad_stp` | Nonlinear QUAD-stress Headder |
| `220/LC:0` | `CdbQuad_stc` | maximum Quad-stress |
| `221/LC:0` | `CdbQuad_nsc` | maximum stresses in nodes |
| `221/LC:Z+` | `CdbQuad_nst` | stresses in Quad-nodes |
| `222/LC:+` | `CdbQuad_est` | error estimates of Quad-element stresses |
| `222/LC:0` | `CdbQuad_esc` | max. errors in nodes |
| `225/LC:+` | `CdbQuad_rla` | Layer-stresses of Quads |
| `225/LC:+` | `CdbQuad_rlb` | Layer-reinforcement stresses of Quads MNR=-1 |
| `225/LC:0` | `CdbQuad_rlc` | max Quad-Layer-results |
| `229/LC:+` | `CdbQuad_ser` | stresses of sectional Quad-elements |
| `229/LC:-` | `CdbQuad_seq` | location of sectional results in master |
| `229/LC:0` | `CdbQuad_sec` | maximum Quad-sectional stress |
| `230/LC:+` | `CdbQuad_rts` | tendon stresses in two integration points |
| `230/LC:0` | `CdbQuad_rt0` | maximum of tendon stresses |
| `250/DC:+` | `CdbQuad_dst` | design stresses in Quad-elements |
| `250/DC:0` | `CdbQuad_dsc` | maximum design stresses in Quad-elements |
| `251/DC:0` | `CdbQuad_ndc` | maximum design stresses in Quad-nodes |
| `251/DC:Z+` | `CdbQuad_nds` | design stresses in Quad-nodes |
| `260/DC:+` | `CdbQuad_rei` | reinforcement in Quad-elements |
| `260/DC:0` | `CdbQuad_ric` | maximum reinforcement in Quad-elements |
| `261/DC:0` | `CdbQuad_nrc` | maximum reinforcement in Quad-nodes |
| `261/DC:Z+` | `CdbQuad_nri` | reinforcement in Quad-nodes |
| `262/DC:+` | `CdbQuad_nrp` | punching reinforcement in nodes |
| `262/DC:0` | `CdbQuad_pu1` | punching parameters |
| `262/DC:0` | `CdbQuad_pun` | punching periphery |
| `265/DC:+` | `CdbQuad_rtd` | tendon stress in the design |
| `265/DC:0` | `CdbQuad_rd0` | maximum of tendon stresses in the design |
| `270/0:+` | `CdbQuad_rel` | Evaluated Reinforcement Definitions of Elements |
| `270/0:0` | `CdbQuad_red` | Evaluated Reinforcement Definitions of Elements |
| `270/DC:0` | `CdbQuad_ree` | maximum design values in Quad-elements |
| `270/DC:0` | `CdbQuad_rem` | maximum reinforcement results in Quad-elements |
| `270/DC:Z+` | `CdbQuad_rea` | General Concrete Design Results |
| `270/DC:Z+` | `CdbQuad_rer` | Reinforcement Layer Design Results |
| `271/0:+` | `CdbQuad_rnl` | Evaluated Reinforcement Definitions of Nodes |
| `271/0:0` | `CdbQuad_rnd` | Evaluated Reinforcement Definitions of Nodes |
| `271/DC:0` | `CdbQuad_rne` | maximum design values in Nodes of Quad-elements |
| `271/DC:0` | `CdbQuad_rnm` | maximum reinforcement results in Nodes |
| `271/DC:Z+` | `CdbQuad_rna` | General Concrete Design Results in Nodes |
| `271/DC:Z+` | `CdbQuad_rnr` | Reinforcement Layer Design Results in Nodes |
| `290/LC` | `CdbQuad_cfd` | Fluid flow results in Quad-elements |
| `291/LC` | `CdbQuad_tmp` | Temperature Results in Quad-elements |
| `291/LC:0` | `CdbQuad_tm` | Maximum of Temperature Results in Quads |

### 300-399 &mdash; BRIC elements

| KWH/KWL | Type | Description |
|---|---|---|
| `300/00` | `CdbBric` | Bric-elements |
| `300/02:+` | `CdbBric_sur` | Surfaces and Neighbours of Bric-elements |
| `300/02:0` | `CdbBric_su` | Surfaces and Neighbours of Bric-elements |
| `300/10` | `CdbBric_p` | Bric-P-Elements |
| `300/6` | `CdbBric_rim` | Prescribed Reinforcements of Bric-elements |
| `302/LC` | `CdbBric_loa` | loads of Bric-elements |
| `310/LC:+` | `CdbBric_str` | 3D-stresses in Bric-elements |
| `310/LC:-` | `CdbBric_stp` | Nonlinear BRIC-stress Headder |
| `310/LC:0` | `CdbBric_stc` | maximum stress in BRICs |
| `311/LC:0` | `CdbBric_nsc` | maximum nodal 3D stress |
| `311/LC:Z+` | `CdbBric_nst` | 3D-stresses in Bric-nodes |
| `312/LC:+` | `CdbBric_est` | 3D-error estimates in Bric-Elements |
| `312/LC:0` | `CdbBric_esc` | max. errors of Bric-stresses |
| `319/LC` | `CdbBric_tcm` | damage in Bric-elements LADE |
| `325/LC` | `CdbBric_nor` | Bric nonlinear reinforcement results |
| `360/DC:+` | `CdbBric_rei` | reinforcement in Bric-elements |
| `360/DC:0` | `CdbBric_rec` | maximum reinforcement in Bric-elements |
| `361/DC:0` | `CdbBric_nrc` | maximum reinforcement in Bric-nodes |
| `361/DC:Z+` | `CdbBric_nri` | reinforcement in Bric-nodes |
| `390/LC` | `CdbBric_cfd` | Fluid flow results in BRIC-elements |
| `391/LC` | `CdbBric_tmp` | Temperature Results in BRIC-elements |
| `391/LC:0` | `CdbBric_tm` | Maximum Temperature Results in BRICs |

### 400-999 &mdash; Piles, pipes, hydraulic links, segments

| KWH/KWL | Type | Description |
|---|---|---|
| `404/NR:+` | `CdbHase_pil` | HASE-Piles in Half-space |
| `404/NR:0` | `CdbHase_pih` | HASE-Piles in Half-space |
| `490/00` | `CdbPipe` | pipes / armatures |
| `490/LC` | `CdbPipe_res` | results of pipes |
| `491/00` | `CdbHlnk` | link elements (hydraulic/ thermal) |
| `900/00` | `CdbSeg_def` | Segmentdefinition |

### 1000-9999 &mdash; Sub-data and extended result records

| KWH/KWL | Type | Description |
|---|---|---|
| `1009/NR:-` | `CdbSsct_cs` | Construction stage start in sub data |
| `1009/NR:100` | `CdbSsct_spt` | SectionFemPoint |
| `1009/NR:1009` | `CdbSsct_sub` | SectionalSubDataBlock |
| `1009/NR:101` | `CdbSsct_ppt` | SectionFemPolygonPoint |
| `1009/NR:111` | `CdbSsct_snz` | SectionNeffZones |
| `1009/NR:112` | `CdbSsct_fem` | SectionFemTopology |
| `1009/NR:113` | `CdbSsct_nod` | SectionFemNode |
| `1009/NR:310` | `CdbSsct_ptc` | PartialCutIntegrationPoint of shear cut |
| `1009/NR:320` | `CdbSsct_pcp` | SectionCutPointReinforcement for partial cut polygon |
| `1009/NR:321` | `CdbSsct_lcp` | SectionCutLineReinforcement for partial cut polygon |
| `1038/NR:0` | `CdbTrb` | Tributary areas - Header |
| `1038/NR:1` | `CdbTrb_supp` | Tributary areas - Supports |
| `1038/NR:2` | `CdbTrb_node` | Tributary areas - Nodes |
| `1038/NR:3` | `CdbTrb_tri` | Tributary areas - Triangles |
| `1105/LC:Z!` | `CdbBeam_cst` | Composite stresses in cross-section of beams |
| `1107/LC:0` | `CdbBeam_uc0` | Maximum utilisations in cross-section of beams |
| `1107/LC:Z!` | `CdbBeam_ucd` | Composite design utilisations in cross-section of beams |
| `1125/LC:Z!` | `CdbDsln_cst` | Composite stresses in cross-section of design elements |
| `1127/LC:0` | `CdbDsln_uc0` | Maximum utilisations in cross-section of design elements |
| `1127/LC:Z!` | `CdbDsln_ucd` | Composite design utilisations in cross-section of design elemen |
