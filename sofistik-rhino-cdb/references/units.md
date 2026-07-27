# Units in the CDB

Every float item in `cdbase.txt` carries a unit code in brackets, e.g.

```
@1:  N    [1101]  |normal force
@1:  UX   [1003]  |displacement
```

Look the code up in the table below. The column that matters is **CDBASE** -
that is the unit the number is *actually stored in*. The **Default** column is
only what SOFiSTiK's own printouts and dialogs display, after converting.

## The short version

For a default (metric) unit set, values you read out of the CDB are in **base SI
engineering units**:

| Quantity | Stored as | Common codes |
|---|---|---|
| Lengths, coordinates, beam length, station | **m** | 1000, 1001, 1006, 1010, 1011 |
| Displacements | **m** (not mm!) | 1003 |
| Rotations | **rad** (not mrad!) | 1004, 1200 |
| Forces, reactions, normal/shear force | **kN** | 1101, 1102, 1151, 1190 |
| Moments | **kNm** | 1103, 1104, 1152, 1194 |
| Plate/shell forces | **kN/m** | 1111, 1112 |
| Plate/shell moments | **kNm/m** | 1113, 1114 |
| Stresses (materials) | **kN/m2** | 1092, 1093, 1090 |
| Areas | **m2** | 1002, 1012 |
| Reinforcement areas | **m2** (not cm2!) | 1020, 1021, 1022 |

The three that catch people out are displacements (m, displayed in mm),
rotations (rad, displayed in mrad) and reinforcement areas (m2, displayed in
cm2). A displacement that reads `0.0123` is 12.3 mm, not 0.0123 mm.

## Two conversions, not one

There are two independent unit boundaries in a Grasshopper script, and they are
easy to conflate:

1. **CDB storage unit -> the number you want.** Governed by the unit code and
   the model's unit set. Multiply by 1000 to show displacements in mm, and so
   on.
2. **Metres -> Rhino document units.** A Rhino document set to millimetres will
   draw a node at `Xyz = (10, 0, 0)` 10 mm from the origin, not 10 m. Read
   `RhinoDoc.ActiveDoc.ModelUnitSystem` and scale, or state the assumption in
   the component description.

SOFiSTiK's own documentation flags this: CDB values follow the unit settings
defined in the SSD, which may differ from the Rhino document units.

## Non-default unit sets

The table below is the metric default. A model configured for a different unit
set (see the environment list in `cdbase.txt` topic 126: bridges use MN,
mechanical engineering uses mm, imperial sets use ft/in/kip) stores different
numbers for the same code. `CdbCtrl_dim` (`0/101`) holds per-code overrides and
`CdbSyst` (`10/00`) the system info. If a model might not be metric-default,
read those rather than assuming - or expose a scale factor as a component input
and let the user set it.

## Full implicit unit table

Codes below 1000 are explicit units (fixed meaning); codes above 1000 are
implicit and behave as described above. Reproduced from `cdbase.txt` topic 126.

```
 Id-No     Short Text        Description                  Notation CDBASE    Default
  1000     GEO_DISTANCE      Long distances                      D (m)       (km)
  1001 (!) GEO_LENGTH        Geometric length in the model       l (m)       (m)
  1002 (*) GEO_AREA          Geometric areas in the model        A (m2)      (m2)
  1003     GEO_DEFORMATION   Deformations                        u (m)       (mm)
  1004     GEO_ROTATION      Rotational deformations           phi (rad)     (mrad)
  1005     GEO_DISTORTION    Distortion (Verwindungen)           u (1/m)     (1/km)
  1006     GEO_ELEVATION     Geometric elevation                 H (m)       (m)
  1007     GEO_GAREA         Geometric areas in the model        A (m2)      (m2)
  1008     GEO_VOLUME        Geometric volumes in the model      V (m3)      (m3)
  1009     GEO_CURVATURE     Curvature in Geometry               k (1/m)     (1/km)
  1010 (!) GEO_THICKNESS     Thickness                           t (m)       (m)

  1011 (!) SECT_LENGTH       Dimension of cross sections       b,h (m)       (mm)
  1012     SECT_AREA         Area of cross sections              A (m2)      (m2)
  1013     SECT_AREA_3       3rd order area of cross sections    W (m3)      (m3)
  1014 (*) SECT_AREA_4       4th order area of cross sections    I (m4)      (m4)
  1015 (*) SECT_AREA_5       5th order area of cross sections    A (m5)      (m5)
  1016 (*) SECT_AREA_6       6th order area of cross sections   Cm (m6)      (m6)
  1017     SECT_RESI_2       Resistance of sections            1/W (1/m2)    (1/m2)
  1018     SECT_RESI_3       Resistance of sections            1/W (1/m3)    (1/m3)
  1019 (*) SECT_AREA_LENG    Surface area per length             - (m2/m)    (m2/m)

  1020 (*) REINF_AREA        Reinforcement area As              As (m2)      (cm2)
  1021 (*) REINF_AREA_L      Reinforcement area As per length   As (m2/m)    (cm2/m)
  1022 (*) REINF_AREA_A      Reinforcement area As per area     As (m2/m2)   (cm2/m2)
  1023     REINF_DIAMETER    Diameter of Reinforcement           D (m)       (mm)
  1024     REINF_COVER       Cover resp. static distance         d (m)       (mm)
  1025     MAT_THICKNESS     Thickness for a material         tmax (m)       (mm)
  1026     REINF_CRACKW      Crackwidth for reinforcements       w (m)       (mm)
  1027     TENDON_AREA       Tendon or duct area                At (m2)      (mm2)
  1028     TENDON_FORCE      Tendon Force                        Z (kN)      (kN)
  1029 (*) REINF_AREA_G      Generalized Reinforcement area     As (m2 or m2/m) (cm2 or cm2/m) depending on context
  1030     REINF_TOTAL       Total Reinforcement weight          G (t)       (kg)       without G
  1031     ROUGHNESS         Roughness of a surface              k (m)       (mm)
  1032     TENDON_ELONG      Tendon elongation                   s (m)       (mm)
  1033     TENDON_ANGLE      Tendon imclination                 ^a (rad)     (°)
  1034     TENDON_CURV       Tendon curvature                   ^b (1/m)     (°/m)

  1080     PRESSURE          Pressure                            p (kPa)     (bar)
  1081     STRAIN            Strain                             ^e (-)       (o/oo)
  1082     STRAIN_R          Twist                              ^k (1/m)     (1/km)
  1083     THERMAL_EXP       Thermal expansion factor           ^a (1/K)     (1/°)

  1086     SOIL_MASS_LINE    Mass distribution for lines         m (t/m)     (t/m)      without G
  1087     SOIL_MASS_AREA    Mass distribution for areas         m (t/m2)    (t/m2)     without G
  1088     SOIL_MODULE       Soil Elastizity or Shear modulus    E (kN/m2)   (kN/m2)
  1089     SOIL_STRESS       Stress of soil materials            f (kN/m2)   (kN/m2)
  1090     MAT_MODULE        Elastizity or Shear modulus         E (kN/m2)   (N/mm2)
                             Variants MPa, N/mm2, MN/m2
  1091     NOM_WEIGHT        nominal weight converted to mass  gam (kN/m3)   (kN/m3)    with G=10.0
  1092  *  MAT_STRESS        Stress of materials                ^s (kN/m2)   (N/mm2)
  1093  *  MAT_SHEAR         Stress of materials                ^t (kN/m2)   (N/mm2)
  1094     MAT_ENERGY        Material deformation energy         - (kNm)     (kNm)
  1095  *  MAT_ELSUP_P1      Elastic support force/deformation   C (kN/m)    (kN/m)
  1096     MAT_ELSUP_P2      Elastic support force/deform/length C (kN/m2)   (kN/m2)
  1097     MAT_ELSUP_P3      Elastic support force/deform/area   C (kN/m3)   (kN/m3)
  1098     MAT_ELSUP_M1      Elastic support moment/rotation     C (kNm/rad) (kNm/rad)
  1099     MAT_ELSUP_M2      Elastic support moment/rotat/length C (kNm/m/rad) (kNm/m/rad)
  1100     MAT_ELSUP_M3      Elastic support moment/rotat/area   C (kNm/m2/rad)(kNm/m2/rad)
                             for more see 1157-1159

  1101  *  BEAM_NFORCE       Normal force in beam/truss/cable    N (kN)      (kN)
  1102  *  BEAM_SFORCE       Shear force in beams               Vy (kN)      (kN)
  1103  *  BEAM_TORSION      Torsional moment in beams          Mt (kNm)     (kNm)
  1104  *  BEAM_BENDING      Bending moment in beams            My (kNm)     (kNm)
  1105  *  BEAM_BIMOMENT     Warping bimoment in beams          Mb (kNm2)    (kNm2)

  1111     PLATE_NFORCE      Membran forces in plates/coques  n-xx (kN/m)    (kN/m)
  1112     PLATE_SFORCE      Shear forces in plates/coques     v-x (kN/m)    (kN/m)
  1113     PLATE_TORSION     Torsional moment plates/coques   m-xy (kNm/m)   (kNm/m)
  1114     PLATE_BENDING     Bending moment in plates/coques  m-xx (kNm/m)   (kNm/m)

  1151  *  SUPP_POINT        Supporting force in a point         P (kN)      (kN)
  1152  *  SUPP_MOMENT       Supporting moment in a point        M (kNm)     (kNm)
  1153  *  SUPP_LINE         Supporting force per length         p (kN/m)    (kN/m)
  1154  *  SUPP_LMOMENT      Supporting moment per length        m (kNm/m)   (kNm/m)
  1155     SUPP_AREA         Supporting force per area           p (kN/m2)   (kN/m2)
  1156     SUPP_AMOMENT      Supporting moment per area          m (kNm/m2)  (kNm/m2)

  1157     MAT_ELSUP_M0      Elastic Support force/rotation      C (kN/rad)  (kN/rad)
  1158     MAT_ELSUP_MB1     Elastic Support warp/deformation    C           (kNm2/m)
  1159     MAT_ELSUP_MB2     Elastic Support warp/twist          C (kNm3)    (kNm3)
  1160     VISCOSITY_P2      Damping force / area                D (kNsec/m3)(kNsec/m3)
  1161     VISCOSITY_M2      Damping moment / area               D (kNsec/m) (kNsec/m)

  1180     MASS_POINT        Point mass                          M (t)       (t)       without G
  1181     MASS_LINE         massdistribution per length         m (t/m)     (t/m)     without G
  1182     INERTIA_POINT     Rotational mass                    ^T (tm2)     (t*m2)    without G
  1183     INERTIA_LINE      Rotational mass per length         ^t (tm2/m)   (t*m)     without G
  1184     INERTIA_DISTR     massdistribution per area           i (t/m2)    (t/m2)    without G
  1188     DENS_LINE         massdistribution per length         g (kN/m)    (kg/m)    with G=10.0
  1189     DENSITY           density of materials               ^r (kN/m3)   (kg/m3)   with G=10.0

  1190     LOAD_POINT        Single point load                   P (kN)      (kN)
  1191     LOAD_LINE         Line load                           p (kN/m)    (kN/m)
  1192     LOAD_AREA         Surface load                        p (kN/m2)   (kN/m2)
  1193     LOAD_VOLUME       Volume load                         p (kN/m3)   (kN/m3)
  1194     LOAD_MOMENT       Point moment                        M (kNm)     (kNm)
  1195     LOAD_LMOMENT      Line moment loading                 m (kNm/m)   (kNm/m)
  1196     LOAD_AMOMENT      Area moment loading                 m (kNm/m2)  (kNm/m2)

           Others:
  1200     ANGLE             any angle or orientation           ^a (rad)     (°)
  1201     VELOCITY          Velocity of structural components   v (m/sec)   (m/sec)
  1202     ACCELERATION      Acceleration of structures          a (m/sec2)  (m/sec2)
  1203     SPEED             Velocity of a vehicle               v (m/sec)   (km/h)
  1204     Viscosity_P       Damping coefficient                 D (kNsec/m) (kNsec/m)
  1205     Viscosity_M       Rotational dmaping coefficient      D (kNsecm)  (kNsecm)
  1206     A_VELOCITY        Angular velocity                    v (rad/sec) (rad/sec)
  1207     A_ACCELERATION    Angular acceleration                a (rad/sec2)(rad/sec2)
  1208     T_VELOCITY        Twisting velocity                   v (1/msec)  (1/msec)
  1209     T_ACCELERATION    Twisting acceleration               a (1/msec2) (1/msec2)
  1210     PIEZO_HEAD        Piezometric Head                    H (m)       (m)
  1211     FLUID_FLUX        Flux of fluids                      q           (l/sec)
  1212     FLUID_VELO        velocity of fluids                v,u (m/sec)   (m/sec)
  1213     FLUID_VELO_L      velocity of fluids  per length                  (l/sec/m)
  1214     FLUID_VELO_A      velocity of fluids  per area                    (l/sec/m2)
  1215     TEMPERATUR        Temperatur                          T           (grad Celsius)
  1216     HEAT_FLUX         Heat Flux of heat                   Q           (W)
  1217     HEAT_FLUX_L       Heat Flux density per length        q           (W/m)
  1218     HEAT_FLUX_A       Heat Flux density per area          q           (W/m2)
  1219     ENTHALPY          Enthalpy                            h           (Wsec/kg)
  1220     VISCOSITY         Dynamic Viscosity                  ^i           (kNsec/m2)
  1221     K_VISCOSITY       Kinematic Vicosity                 ^n           (m2/sec)
  1222     TURB_ENERGY       Turbulent Energy                    k           (m2/sec2)
  1223     ENERGYRATE        Turbulent Energy rate/loss          ê           (m2/sec3)
  1224     CONCENTRAT        Mass fractions / concentrations    ^r           (kg/m3)       without G
  1225     MASS_FLOW         Mass flow                           q           (kg/sec)
  1226     MASS_FLOW_L       Mass flow per length                q           (kg/sec/m)
  1227     MASS_FLOW_A       Mass flow per area                  q           (kg/sec/m2)
  1228     MASS_FLOW_V       Mass flow per volume                q           (kg/sec/m3)
  1229     FLUID_FLOW_V      Fluid flow per volume               q           (l/sec/m3)
  1230     HEAT_FLOW_V       Heat flow per volume                q           (W/m3)
  1231     HEAT_CONDUCT      Heat conductivity                   ^l          (W/K/m)
  1232     HEAT_CAPACITY     Heat capacity per volume            S           (kJ/K/m3)
  1233     FLOW_CAPACITY     Storage capacity per volume         S           (m³/m)
  1234     MASS_CAPACITY     Storage capacity per volume         S           (kg/Pa)
  1235     TEMP_GRADIENT     Temperature gradient                g           (°/m)
  1236     FLUID_DENSITY     Physical density                  rho           (kg/m3)       without G
  1237     TEMP_DIFF         Temperaturdifferenz                 T           (grad Celsius)
  1238     CO2E_EQUIVALENT   CO2 Equivalent                      -           (tCO2e)
  1239     CO2E_PER_MASS     CO2 Equivalent per mass             -           (kgCO2e/kg)   without G
  1240     CO2E_PER_VOLUME   CO2 Equivalent per volume           -           (kgCO2e/m3)
  1250     FREQUENCY         Frequency                           - (Hz)      (Hz)

  Conversion to X-Items (m,kg,sec,K)

  1280  X  X-PRESSURE        Pressure                            p           (bar)
  1281  X  X-TEMPERATURE     Temperature                         T           (K)
  1282  X  X-HEAT_FLUX       Heat Flux of heat                   Q           (W)
  1283  X  X-HEAT_FLUXD      Heat Flux density                   q           (W/m2)
  1284  X  X-HEAT_RESIST     Resistance of Heat-Flow             r           (Km2/W)
  1285  X  X-ENERGY          Total Energy                        E           (Wsec)

  1290     TIME              Time                                t           (sec)
  1291     TIME/FREQU.       Time or Frequency selectable

  1299     FACTOR            Scalar                              - (-)       (-)

  1300     FFA_IMPULSE       Impulse for Footfall Analysis       -           (kNsec)
```

