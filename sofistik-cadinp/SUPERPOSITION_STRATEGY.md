# Superposition Strategy — Building Load Case Combinations

## Purpose

SOFiSTiK offers two ways to build the load case combinations required for ULS/SLS verifications. This file describes both options, when to use which, how the resulting combination load cases are numbered and addressed by the design modules, and gives end-to-end code fragments.

## Load this file when

The generated input needs load case combinations (any ULS/SLS verification, any design module) — **after** the user has answered the superposition question in `SKILL.md`.

---

## The Two Options

| Option | Method | Recommended when | Modules |
|--------|--------|------------------|---------|
| **A — Automatic result combination (MAXIMA)** | Primary load cases are analysed **linearly** in ASE; MAXIMA combines the results automatically into max/min envelopes according to the design code (`COMB ... EXTR DESI/RARE/FREQ/PERM` + `SUPP`) | **Linear** workflows (default for linear static analysis with many load cases) | SOFILOAD (actions + primary LCs) → ASE (linear) → **MAXIMA** → design module |
| **B — Explicit combination load cases (SOFILOAD)** | The combinations are defined manually as new load cases in SOFILOAD (`LC 101 TYPE (D)` + `COPY NO … FACT …`, or `COPY … DESI`) and each combination is analysed in ASE | **Non-linear** analysis (material non-linearity, second-order theory, cables, contact, non-linear springs) — superposition of non-linear results is not valid; also when only a few specific combinations are needed | SOFILOAD (actions + primary LCs + combination LCs) → ASE (combination LCs, linear or non-linear) → design module |

> If the user requests a non-linear analysis (e.g. ASE `SYST PROB NONL` or `TH2`/`TH3`), recommend option B and explain that MAXIMA superposition is only valid for linear results. In non-linear ASE analysis each combination load case needs its own `+PROG ASE` block (see `modules/ASE.md`).
> Option A details (combination rules, result load case suffixes, output control): `modules/MAXIMA.md`. Option B details (`LC ... TYPE (D)`, `COPY` with factors or combination literals): `modules/SOFILOAD.md`.

---

## Combination Types in the Design Modules

Both options deliver combination load cases with a combination type that the design modules use to select them:

| Limit state | MAXIMA `COMB ... TYPE` (option A) | SOFILOAD `LC ... TYPE` (option B) | Selection in design modules |
|-------------|-----------------------------------|-----------------------------------|-----------------------------|
| ULS fundamental | `DESI` | `(D)` | AQB `LC TYPE (D)`, BEMESS `LC DESI`, BEAM `COMB LC ... TYPE (D)` |
| ULS accidental (incl. fire) | `ACCI` | `(A)` | AQB `LC TYPE (A)`, BEMESS `LC ACCI` |
| ULS seismic | `EARQ` | `(E)` | AQB `LC TYPE (E)`, BEMESS `LC EARQ` |
| SLS characteristic | `RARE` | `(R)` | AQB `LC TYPE (R)`, BEMESS `LC RARE` |
| SLS frequent | `FREQ` | `(F)` | AQB `LC TYPE (F)`, BEMESS `LC FREQ` |
| SLS infrequent | `NONF` | `(N)` | AQB `LC TYPE (N)`, BEMESS `LC NONF` |
| SLS quasi-permanent | `PERM` | `(P)` | AQB `LC TYPE (P)`, BEMESS `LC PERM` |
| Timber load duration | `PT`/`LT`/`MT`/`ST`/`VT` | `(PT)`/`(LT)`/`(MT)`/`(ST)`/`(VT)` | AQB `LC TYPE (PT),(LT),(MT)` |

> Design modules must only receive load cases of the matching limit state: ULS design (AQB `DESI STAT ULTI`, BEMESS `LC DESI`) only with `(D)`/`(A)`/`(E)` combinations; SLS checks (AQB `NSTR KMOD SERV`, crack width) only with `(R)`/`(F)`/`(P)` combinations.
> Timber (EN 1995): with option A assign the load duration class via `COMB ... TYPE PT/LT/MT/ST/VT` so AQB can select k_mod; with option B use `LC ... TYPE (PT)`, `(LT)`, … in SOFILOAD.

---

## Load Case Numbering

- Keep load case number ranges separate:
  - primary load cases: 1–99
  - explicit combination load cases (option B): 101–999
  - MAXIMA result load cases (option A): via `COMB ... BASE` 2100, 2200, …
- Never let MAXIMA results overwrite primary or combination load cases.
- Option A: always use `COMB ... BASE nn00` so the result load case numbers are predictable (`BASE + suffix`, e.g. BASE 2100: max/min MY of beams = 2129/2130; see `modules/MAXIMA.md`), and reference exactly these numbers — or the combination type — in the design module.

---

## Option A — Fragment (ASE → MAXIMA → AQB)

```
+PROG ASE urs:4
HEAD Linear analysis of all primary load cases
LC ALL
END

+PROG MAXIMA urs:5
HEAD ULS envelopes
ECHO FULL NO
COMB NO 1 EXTR DESI BASE 2100 TITL 'ULS fundamental'
  ACT TYPE G
  ACT TYPE Q
SUPP COMB 1 EXTR MAMI ETYP BEAM TYPE N,VZ,MY    $ results 2121/2122, 2125/2126, 2129/2130
END

+PROG AQB urs:6
HEAD ULS design
LC TYPE (D)                                     $ or explicitly: LC 2121,2122,2125,2126,2129,2130
REIN MOD SECT RMOD SAVE LCR 1
DESI STAT ULTI
END
```

## Option B — Fragment (SOFILOAD Combination LCs → ASE → AQB)

```
+PROG SOFILOAD urs:4
HEAD Combination load cases
LC 101 TYPE (D) TITL 'ULS 1.35G + 1.5Q'
  COPY NO 1 FACT 1.35
  COPY NO 2 FACT 1.50
END

+PROG ASE urs:5
HEAD Analysis of the combination load case (linear or non-linear)
LC 101
END

+PROG AQB urs:6
HEAD ULS design
LC 101
REIN MOD SECT RMOD SAVE LCR 1
DESI STAT ULTI
END
```
