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
| 1 | `state_constructor/input/barn_swallow_2019-06-18_constructor_input.csv` | input CSV | small real-world/biological sample constructor input referenced by PC-MAW sample artifact data | 354 bytes / 12 lines; simple `t,x,y` trajectory fixture with 11 points; minimal in size, but commit history identifies it as a real artifact candidate and frontend sample usage requires provenance/sample-fixture review before durable public fixture approval | keep temporarily grandfathered pending larger review | keep temporarily grandfathered pending provenance/sample-fixture review | Do not remove in this step. Review together with paired generated output and `pc-maw/src/data/sampleArtifacts.ts`. |  
| 2 | `state_constructor/input/test_trace_001.csv` | input CSV | small synthetic/general constructor fixture used by sample artifact data and constructor validation tests | 115 bytes / 11 lines; simple `t,x,y` fixture; minimal synthetic input with existing test and sample references | keep tracked as minimal fixture | keep tracked as minimal fixture | Retain as baseline synthetic constructor fixture. |
| 3 | `state_constructor/input/test_trace_hover_001.csv` | input CSV | small synthetic hover/control fixture used by Orb support regression tests | 175 bytes / 11 lines; minimal synthetic near-stationary control fixture; useful for withholding/negative-control behavior | keep tracked as minimal fixture | keep tracked as minimal fixture | Retain as synthetic control fixture. |
| 4 | `state_constructor/input/test_trace_orb_like_001.csv` | input CSV | small synthetic orb-like diagnostic fixture used by Orb support regression tests and frontend sample artifact data | 236 bytes / 14 lines; minimal synthetic circular/orb-like probe; useful for diagnostic support testing, but naming must remain bounded as synthetic/orb-like and not real-world Orb evidence | keep tracked as minimal fixture | keep tracked as minimal synthetic diagnostic fixture | Retain with bounded synthetic/orb-like framing only. |
| 5 | `state_constructor/input/test_trace_turn_001.csv` | input CSV | small synthetic turn/control fixture used by Orb support regression tests | 209 bytes / 13 lines; minimal synthetic turn fixture; useful as ordinary-turn control against over-admission | keep tracked as minimal fixture | keep tracked as minimal fixture | Retain as synthetic control fixture. |
| 6 | `state_constructor/input/uci_pedestrians_in_traffic_oid_39406.csv` | input CSV | external-derived/local sample input used in bounded 39406 proof path and referenced by PC-MAW sample artifact data | simple `t,x,y` trajectory fixture with 198 points; no interpretive language observed, but external-derived provenance and frontend sample usage require separate provenance/public-sample review before treating as durable public fixture | keep temporarily grandfathered pending larger review | keep temporarily grandfathered pending provenance/public-sample review | Do not remove in this step. Review together with paired generated output and `pc-maw/src/data/realUciPedestriansInTrafficOid39406Artifact.ts`. |  
| 7 | `state_constructor/output/.gitkeep` | output placeholder | keeps output directory tracked | low risk, but output directory tracking should be reconsidered | pending | pending |  |
| 8 | `state_constructor/output/barn_swallow_2019-06-18_constructor_input_state_segmented_trace.json` | generated output JSON | small generated state-segmented output paired to barn swallow input | 7,316 bytes / 252 lines; generated from real-world/biological sample input; provenance points back to tracked CSV; activated states are Straight/Turn with Hover/Orb deferred; no Orb support emission fields observed in targeted search; generated-output retention and sample provenance require review before durable public fixture approval | keep temporarily grandfathered pending larger review | keep temporarily grandfathered pending generated-output and provenance/sample-fixture review | Do not remove in this step. Review together with barn swallow input CSV, frontend sample artifact data, and possible regenerated/synthetic fixture strategy. |  
| 9 | `state_constructor/output/orb_support_window_scale_review_summary.md` | generated/review markdown | support-window-scale review summary for internal Orb diagnostic development | contains useful review-only boundary language, but also discusses Orb-adjacent evidence, scale sensitivity, biological anchors, and engineered aerial anchors; should not be treated as public-facing release evidence while Orb candidacy policy is still developing | keep temporarily grandfathered pending larger review | keep private/internal for now | Preserve for internal development. Revisit alongside Orb candidacy terminology, diagnostic contract boundaries, and public/private release policy. |  
| 10 | `state_constructor/output/test_trace_001_state_segmented_trace.json` | generated output JSON | state-segmented output paired to test trace | possible golden fixture; verify necessity | pending | pending |  |
| 11 | `state_constructor/output/test_trace_hover_001_state_segmented_trace.json` | generated output JSON | state-segmented output paired to hover control | possible golden/control fixture; verify necessity | pending | pending |  |
| 12 | `state_constructor/output/test_trace_orb_like_001_state_segmented_trace.json` | generated output JSON | state-segmented output paired to orb-like synthetic input | naming/interpretation risk; verify necessity | pending | pending |  |
| 13 | `state_constructor/output/test_trace_turn_001_state_segmented_trace.json` | generated output JSON | state-segmented output paired to turn control | possible golden/control fixture; verify necessity | pending | pending |  |
| 14 | `state_constructor/output/uci_pedestrians_in_traffic_oid_39406_state_segmented_trace.json` | generated output JSON | large generated state-segmented output paired to UCI-derived input; used as a bounded 39406 proof-path artifact, regression/control anchor, and review-tool input | 573,049 bytes / 15,071 lines; repeatedly updated across Constructor v0 diagnostic milestones; referenced by orb support regression tests, scale-review fixture, anchor diagnostic tooling, and review summary; Orb diagnostic boundary observed as withheld/no-emission; external-derived provenance and generated-output retention require larger review before durable public fixture approval | keep temporarily grandfathered pending larger review | keep temporarily grandfathered pending generated-output, regression-anchor, and provenance/public-sample review | Do not remove in this step. Review together with UCI input CSV, frontend sample artifact, regression tests, and possible smaller/synthetic replacement strategy. |  

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