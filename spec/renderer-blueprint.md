# PC-MSAT Renderer Blueprint

## Purpose

This document defines the reference rendering pipeline used to produce a PC-MSAT audit sheet from a state-segmented motion trace.

The renderer is intended to produce a **deterministic visual audit artifact** from motion data processed under the Structured Orb Dynamics (SOD) framework.

The renderer:

- does **not** perform classification
- does **not** perform prediction
- does **not** infer physical cause or intent

It produces a **visual disclosure artifact** illustrating motion geometry, supporting signals, and persistence structure.

---

# Renderer Inputs

Each audit sheet is generated from a single trace input file.

## Required Input Fields

The renderer expects the following columns:

| Field | Description |
|-------|-------------|
| `t` | observation index or timestamp |
| `x` | projected x coordinate |
| `y` | projected y coordinate |
| `state` | SOD state label |

Allowed state labels:

```
Straight
Turn
Hover
Orb
```

The renderer will refuse to process traces containing unknown state labels.

---

# Renderer Configuration Parameters

Each artifact also includes metadata parameters.

Required parameters:

```
TRACE_ID
SOURCE_OR_DATASET
CASE_LABEL
CADENCE
N_SHOWN
WINDOW_RULE
PROJECTION
MIN_RUN
```

Example configuration:

```
TRACE_ID: barn_swallow_vi_b_2350-21095
SOURCE_OR_DATASET: SOD VI-B Barn Swallow GPS
CASE_LABEL: WITHHOLD
CADENCE: 600 s
N_SHOWN: 90
WINDOW_RULE: first 90 observations
PROJECTION: planar
MIN_RUN: 3
```

---

# Order of Operations

The renderer must execute the following steps in order:

1. Load trace data
2. Apply observation window rule
3. Compute curvature signal κ(t)
4. Extract contiguous state runs
5. Evaluate persistence rule
6. Determine audit result
7. Render audit sheet
8. Export artifact

Window selection must occur **before** persistence evaluation.

---

# Derived Quantities

## Curvature Signal

The renderer computes **raw signed curvature κ(t)**.

Constraints:

- no smoothing
- no filtering
- no normalization

The curvature panel includes a faint reference line at:

```
κ = 0
```

This allows directional curvature to be visually interpreted.

---

## Persistence Runs

From the state sequence the renderer extracts contiguous runs.

Example run structure:

```
run_index
state_label
run_length
```

The persistence decision is based solely on **contiguous run length**.

Diagnostic breakdown by state type may be shown but does not influence the decision.

---

# Persistence Rule

```
IF max_run ≥ MIN_RUN
→ PROCEED
ELSE
→ WITHHOLD
```

The renderer must verify:

```
computed_result == CASE_LABEL
```

If a mismatch occurs the renderer must **refuse to render the artifact**.

This prevents manual override or mislabeling.

---

# Audit Sheet Layout

The renderer produces a four-panel figure.

Panel height ratios:

```
Panel 1 : Panel 2 : Panel 3 : Panel 4
4 : 2 : 2 : 1
```

---

## Panel 1 — State-Segmented Motion Trace

Displays the spatial trajectory.

Features:

- equal-aspect projection
- x/y axes visible
- state-colored trajectory segments
- start marker (●)
- end marker (○)

State color mapping follows the SOD palette.

---

## Panel 2 — Raw Signed Curvature κ(t)

Displays the curvature signal over the observation index.

Features:

- signed curvature
- faint zero reference line
- no smoothing or filtering

---

## Panel 3 — Persistence Panel

Displays contiguous run lengths relative to the persistence threshold.

Features:

- run-length bars
- vertical reference line at MIN_RUN
- optional state-typed diagnostic breakdown

The persistence decision is based only on **run length**, not state type.

---

## Panel 4 — Audit Result

Displays the final audit outcome.

Formatting:

```
PROCEED  → muted green text
WITHHOLD → neutral gray text
```

No icons or badges are used.

---

# Metadata Header

Each audit sheet includes a metadata header block.

Example:

```
PC-MSAT Audit Sheet

Trace ID:             barn_swallow_vi_b_2350-21095
Source:               SOD VI-B Barn Swallow GPS
Case:                 WITHHOLD

Cadence:              600 s
Observations shown:   90 (first 90 observations)

Projection:           planar
Signal:               raw signed curvature κ(t) (no smoothing)

Persistence rule:     MIN_RUN = 3 contiguous observations
Decision basis:       contiguous run length only
```

---

# Renderer Outputs

Primary artifacts:

```
visuals/pcmsat_audit_withhold.png
visuals/pcmsat_audit_proceed.png
```

Optional context figures:

```
visuals/pcmsat_context_full_withhold.png
visuals/pcmsat_context_full_proceed.png
```

---

# Reproducibility

The renderer must produce identical outputs given identical:

- input trace
- renderer parameters
- environment

All renderer assumptions are defined in this document to ensure the PC-MSAT audit interface remains reproducible and transparent.
