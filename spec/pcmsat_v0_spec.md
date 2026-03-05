PC-MSAT v0 — Pre-Classification Motion Structure Audit Tool

Reference Specification

1. Purpose

PC-MSAT (Pre-Classification Motion Structure Audit Tool) is a geometry-first audit interface designed to evaluate whether a motion trace contains sufficient contiguous persistence to justify downstream classification or analysis.

PC-MSAT does not classify, identify, or interpret motion.
It performs a pre-classification structural audit and returns a binary outcome:

PROCEED or WITHHOLD.

The tool is intentionally conservative.

2. Conceptual Position in a Motion Analysis Pipeline

PC-MSAT operates upstream of classification systems.

Example pipeline position:

Raw Observational Trace
        ↓
State Segmentation (SOD or equivalent)
        ↓
PC-MSAT Structural Audit
        ↓
Proceed → downstream analysis permitted
Withhold → insufficient persistence

PC-MSAT does not alter the trace, estimate parameters, or perform inference.

3. Required Input

A state-segmented motion trace with the following columns:

t
x
y
state

Where:

Column	Meaning
t	observation index or timestamp
x,y	planar position
state	discrete motion state label

Allowed states in the reference implementation:

Straight
Turn
Hover
Orb

4. Core Decision Rule

PC-MSAT evaluates contiguous run length within the state-segmented trace.

Define:

MIN_RUN = minimum contiguous observations required

Let:

max_run = longest contiguous run in the trace

Decision rule:

if max_run ≥ MIN_RUN
    → PROCEED
else
    → WITHHOLD

The rule is intentionally state-agnostic.

5. Diagnostic Context (Non-Decisional)

PC-MSAT may display state-typed diagnostic information to help contextualize runs.

However:

State type never affects the decision rule.

Diagnostic displays exist only for interpretive context.

6. Reference Audit Sheet Layout

The reference renderer produces a deterministic audit sheet consisting of four panels:

Panel 1 — State-Segmented Motion Trace

Trajectory colored by motion state.

Panel 2 — Raw Signed Curvature κ(t)

Curvature computed directly from discrete coordinates.

No smoothing or filtering is applied.

Panel 3 — Persistence Analysis

Two layers:

Decision Layer

contiguous run lengths

MIN_RUN threshold marker

Diagnostic Layer

state-typed run grouping (context only)

Panel 4 — Audit Outcome

Binary output:

PROCEED
WITHHOLD

7. Integrity Safeguard

The reference renderer verifies that:

declared CASE_LABEL == computed audit result

If the values disagree, rendering fails.

This prevents mis-labeled artifacts.

8. Design Principles

PC-MSAT follows the core principles of Structured Orb Dynamics:

• Geometry-first evaluation
• No forced inference
• Conservative withholding preferred over over-interpretation
• Deterministic rendering
• No tuning or optimization

9. Reference Implementation

Reference renderer:

renderer/render_pcmsat_audit.py

Example artifacts:

visuals/withhold_demo.png
visuals/proceed_demo.png

10. Version
PC-MSAT Specification v0
Reference demonstration release