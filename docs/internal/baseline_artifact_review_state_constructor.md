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
| 6 | `state_constructor/input/uci_pedestrians_in_traffic_oid_39406.csv` | input CSV | external-derived/local sample input | higher provenance and public-use risk; review carefully | pending | pending |  |
| 7 | `state_constructor/output/.gitkeep` | output placeholder | keeps output directory tracked | low risk, but output directory tracking should be reconsidered | pending | pending |  |
| 8 | `state_constructor/output/barn_swallow_2019-06-18_constructor_input_state_segmented_trace.json` | generated output JSON | state-segmented output paired to barn swallow input | generated real-world/sample-derived output; review before retaining | pending | pending |  |
| 9 | `state_constructor/output/orb_support_window_scale_review_summary.md` | generated/review markdown | support-window-scale review summary for internal Orb diagnostic development | contains useful review-only boundary language, but also discusses Orb-adjacent evidence, scale sensitivity, biological anchors, and engineered aerial anchors; should not be treated as public-facing release evidence while Orb candidacy policy is still developing | keep temporarily grandfathered pending larger review | keep private/internal for now | Preserve for internal development. Revisit alongside Orb candidacy terminology, diagnostic contract boundaries, and public/private release policy. |
| 10 | `state_constructor/output/test_trace_001_state_segmented_trace.json` | generated output JSON | state-segmented output paired to test trace | possible golden fixture; verify necessity | pending | pending |  |
| 11 | `state_constructor/output/test_trace_hover_001_state_segmented_trace.json` | generated output JSON | state-segmented output paired to hover control | possible golden/control fixture; verify necessity | pending | pending |  |
| 12 | `state_constructor/output/test_trace_orb_like_001_state_segmented_trace.json` | generated output JSON | state-segmented output paired to orb-like synthetic input | naming/interpretation risk; verify necessity | pending | pending |  |
| 13 | `state_constructor/output/test_trace_turn_001_state_segmented_trace.json` | generated output JSON | state-segmented output paired to turn control | possible golden/control fixture; verify necessity | pending | pending |  |
| 14 | `state_constructor/output/uci_pedestrians_in_traffic_oid_39406_state_segmented_trace.json` | generated output JSON | state-segmented output paired to UCI-derived input | higher provenance/output-retention risk; review carefully | pending | pending |  |

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