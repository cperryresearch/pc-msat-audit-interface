# PC-MSAT Sandbox

> This directory contains the **PC-MSAT Sandbox**, a bounded experimental workspace used to explore how the PC-MSAT audit interface behaves under varied motion trace conditions.
>
> For the canonical audit interface and reference artifacts, see the repository front door:
>
> `../README.md`

## Overview

The **PC-MSAT Sandbox** is a bounded experimental workspace used to explore how the existing PC-MSAT audit interface behaves when applied to varied motion traces under fixed constraints.

This environment allows controlled experimentation with input traces while preserving the integrity of the canonical PC-MSAT artifacts.

The sandbox operates under the governance defined in:

`SANDBOX_CHARTER.md`

Users should review the charter before conducting sandbox experiments.

---

## Purpose

The sandbox supports:

- Exploration of edge cases and boundary conditions
- Inspection of persistence behavior across varied traces
- Pedagogical demonstrations of audit outcomes
- Controlled experimentation with non-canonical input traces

The sandbox exists to answer the question:

> *How does the existing PC-MSAT audit interface behave when applied to this trace?*

---

## Repository Structure

```
sandbox/
│
├── SANDBOX_CHARTER.md
├── README.md
│
├── sandbox_data/
│   └── (experimental input traces)
│
└── sandbox_outputs/
    └── (generated audit artifacts)
```

### `sandbox_data/`

Contains experimental motion traces used for sandbox exploration.

These traces are **non-canonical** and may include:

- Synthetic examples
- Boundary-condition traces
- Pedagogical demonstrations
- Exploratory motion structures

### `sandbox_outputs/`

Contains generated audit sheets produced during sandbox experimentation.

Outputs generated here are **exploratory artifacts only** and carry no canonical status.

---

## Use of the Canonical Renderer

All sandbox experiments must use the **canonical PC-MSAT audit renderer** defined in the repository:

`renderer/render_pcmsat_audit.py`

The sandbox must **not introduce alternative renderer logic**.

Sandbox experimentation is limited to varying **input traces**, not modifying the audit mechanism itself.

---

## Constraints

Sandbox work must preserve the methodological posture defined in the PC-MSAT framework:

- Geometry-first evaluation
- Fixed persistence thresholds
- Explicit withholding when criteria are not satisfied
- No smoothing or reinterpretation of canonical signals

If a trace does not satisfy the conditions required for a **PROCEED** outcome, the expected result is **WITHHOLD**.

---

## Relationship to Canonical Artifacts

Artifacts produced in the sandbox are **exploratory only**.

They do not replace or modify the canonical materials contained elsewhere in the repository, including:

- The formal specification
- The canonical audit renderer
- The reference demonstration artifacts
- The documented audit protocol

Promotion of any sandbox artifact to canonical status must occur through a separate, explicit revision process.

---

## Current Sandbox Demonstration Suite

The sandbox currently includes a small demonstration set used to illustrate how the PC-MSAT audit interface behaves across different motion structures.

| Trace | Structure | Purpose | Expected Outcome |
|------|-----------|---------|------------------|
| Trace 001 | Straight persistent | Real trajectory baseline | PROCEED |
| Trace 002 | Persistent curved motion | Demonstrates curvature with persistence | PROCEED |
| Trace 003 | Straight → Turn → Straight | Persistence across regime transitions | PROCEED |
| Trace 004 | Fragmented short runs | Insufficient persistence example | WITHHOLD |
| Trace 005 | Ordered short runs | Near-threshold persistence failure | WITHHOLD |

These traces form a minimal teaching sequence demonstrating how persistence governs the audit decision.

Additional sandbox traces may be introduced to explore further edge cases or instructional examples.

---

## Summary

The sandbox provides a safe workspace for exploring how the PC-MSAT audit interface behaves under varied trace conditions while preserving the integrity of the canonical system.

Sandbox experimentation should always prioritize clarity, restraint, and methodological discipline.