# Baseline Artifact Review — state_constructor

Status: internal review manifest  
Public release allowed: false  
Applies to: grandfathered tracked artifacts currently allowed by `tools/check_artifact_tracking_policy.py`

## Purpose

This manifest records review status for the 14 grandfathered baseline artifacts currently tracked under `state_constructor/input/` and `state_constructor/output/`.

These artifacts are allowed by the artifact tracking policy guard only as pre-existing baseline artifacts pending review. Their presence in the repository does not imply public release approval, Orb candidacy support, physical-origin interpretation, emission permission, or release readiness.

## Review categories

Recommended classifications:

- keep tracked as minimal fixture
- replace with smaller/synthetic fixture
- move/archive privately
- remove from tracking later
- keep temporarily grandfathered pending larger review

## Review table

| # | Path | Artifact class | Known/provisional role | Risk notes | Provisional classification | Final decision | Notes |
|---:|---|---|---|---|---|---|---|
| 1 | `state_constructor/input/barn_swallow_2019-06-18_constructor_input.csv` | input CSV | real-world/sample constructor input | external/real-world-derived provenance requires review | pending | pending |  |
| 2 | `state_constructor/input/test_trace_001.csv` | input CSV | test fixture input | likely synthetic/minimal, verify size and role | pending | pending |  |
| 3 | `state_constructor/input/test_trace_hover_001.csv` | input CSV | control fixture input | likely synthetic/minimal, verify role | pending | pending |  |
| 4 | `state_constructor/input/test_trace_orb_like_001.csv` | input CSV | synthetic orb-like fixture input | naming may imply more than intended; verify restraint language | pending | pending |  |
| 5 | `state_constructor/input/test_trace_turn_001.csv` | input CSV | control/turn fixture input | likely synthetic/minimal, verify role | pending | pending |  |
| 6 | `state_constructor/input/uci_pedestrians_in_traffic_oid_39406.csv` | input CSV | external-derived/local sample input used in bounded 39406 proof path and referenced by PC-MAW sample artifact data | simple `t,x,y` trajectory fixture with 198 points; no interpretive language observed, but external-derived provenance and frontend sample usage require separate provenance/public-sample review before treating as durable public fixture | keep temporarily grandfathered pending larger review | keep temporarily grandfathered pending provenance/public-sample review | Do not remove in this step. Review together with paired generated output and `pc-maw/src/data/realUciPedestriansInTrafficOid39406Artifact.ts`. |  |
| 7 | `state_constructor/output/.gitkeep` | output placeholder | keeps output directory tracked | low risk, but output directory tracking should be reconsidered | pending | pending |  |
| 8 | `state_constructor/output/barn_swallow_2019-06-18_constructor_input_state_segmented_trace.json` | generated output JSON | state-segmented output paired to barn swallow input | generated real-world/sample-derived output; review before retaining | pending | pending |  |
| 9 | `state_constructor/output/orb_support_window_scale_review_summary.md` | generated/review markdown | support-window-scale review summary for internal Orb diagnostic development | contains useful review-only boundary language, but also discusses Orb-adjacent evidence, scale sensitivity, biological anchors, and engineered aerial anchors; should not be treated as public-facing release evidence while Orb candidacy policy is still developing | keep temporarily grandfathered pending larger review | keep private/internal for now | Preserve for internal development. Revisit alongside Orb candidacy terminology, diagnostic contract boundaries, and public/private release policy. |  |
| 10 | `state_constructor/output/test_trace_001_state_segmented_trace.json` | generated output JSON | state-segmented output paired to test trace | possible golden fixture; verify necessity | pending | pending |  |
| 11 | `state_constructor/output/test_trace_hover_001_state_segmented_trace.json` | generated output JSON | state-segmented output paired to hover control | possible golden/control fixture; verify necessity | pending | pending |  |
| 12 | `state_constructor/output/test_trace_orb_like_001_state_segmented_trace.json` | generated output JSON | state-segmented output paired to orb-like synthetic input | naming/interpretation risk; verify necessity | pending | pending |  |
| 13 | `state_constructor/output/test_trace_turn_001_state_segmented_trace.json` | generated output JSON | state-segmented output paired to turn control | possible golden/control fixture; verify necessity | pending | pending |  |
| 14 | `state_constructor/output/uci_pedestrians_in_traffic_oid_39406_state_segmented_trace.json` | generated output JSON | large generated state-segmented output paired to UCI-derived input; used as a bounded 39406 proof-path artifact, regression/control anchor, and review-tool input | 573,049 bytes / 15,071 lines; repeatedly updated across Constructor v0 diagnostic milestones; referenced by orb support regression tests, scale-review fixture, anchor diagnostic tooling, and review summary; Orb diagnostic boundary observed as withheld/no-emission; external-derived provenance and generated-output retention require larger review before durable public fixture approval | keep temporarily grandfathered pending larger review | keep temporarily grandfathered pending generated-output, regression-anchor, and provenance/public-sample review | Do not remove in this step. Review together with UCI input CSV, frontend sample artifact, regression tests, and possible smaller/synthetic replacement strategy. |  |

## Initial review order

1. `state_constructor/output/orb_support_window_scale_review_summary.md`
2. `state_constructor/input/uci_pedestrians_in_traffic_oid_39406.csv`
3. `state_constructor/output/uci_pedestrians_in_traffic_oid_39406_state_segmented_trace.json`
4. `state_constructor/input/barn_swallow_2019-06-18_constructor_input.csv`
5. `state_constructor/output/barn_swallow_2019-06-18_constructor_input_state_segmented_trace.json`
6. synthetic/control test traces and paired generated outputs
7. `.gitkeep`

## Current boundary

Do not remove, untrack, replace, or reclassify these artifacts solely because they appear in this manifest.

This manifest is a review aid only. Any later change to tracked artifacts, fixture structure, or the guard baseline allowlist should be made in a separate deliberate step after review.