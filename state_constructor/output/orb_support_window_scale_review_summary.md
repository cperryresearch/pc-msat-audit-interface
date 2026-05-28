# Orb Support Window-Scale Review Summary

## Purpose

This review summary records the first use of `state_constructor/tools/review_orb_support_window_scales.py`.

The helper is review tooling only. It does not modify Constructor v0 behavior, does not emit Orb, does not change `candidate_state`, does not change `state`, and does not alter `run_summary`, PC-MAW admission, or Playback behavior.

## Review Helper

Helper path:

`state_constructor/tools/review_orb_support_window_scales.py`

Primary purpose:

Compare alternate point-count support-window sizes against existing Constructor v0 output artifacts to determine whether Orb-adjacent evidence appears at scales other than the current fixed 5-point diagnostic window.

The helper reports, per window size:

- windows evaluated
- fit windows
- combined candidate count
- best combined candidate
- top 3 combined candidates

Combined review candidates are review-only. They are not state emissions.

## Key Finding

The fixed 5-point Orb support diagnostic is conservative and cadence-limited.

The scale-review helper did not over-admit Hover, ordinary Turn, or UCI 39406 controls. It preserved the expected synthetic orb-like signal. It also revealed scale-dependent Orb-adjacent evidence in the TII drone ellipse segments and white stork review anchors.

This means the issue is not simply that thresholds are too narrow or that Orb support is invalid. The better interpretation is:

Orb candidate support is scale-sensitive. Larger review windows can reveal evidence that fixed 5-point windows miss, especially for high-frequency telemetry.

## Control Anchor Results

### Hover

Artifact:

`state_constructor/output/test_trace_hover_001_state_segmented_trace.json`

Result:

- points: 10
- strongest rotational run: none
- combined candidate count: 0 across reviewed window sizes

Interpretation:

Hover remains cleanly withheld under scale review.

### Ordinary Turn

Artifact:

`state_constructor/output/test_trace_turn_001_state_segmented_trace.json`

Result:

- points: 12
- strongest rotational run length: 11
- strongest rotational cumulative heading delta: approximately 0.660853
- combined candidate count: 0 across reviewed window sizes

Interpretation:

Ordinary Turn remains cleanly withheld under scale review.

### Synthetic Orb-Like Probe

Artifact:

`state_constructor/output/test_trace_orb_like_001_state_segmented_trace.json`

Result:

- points: 13
- strongest rotational run length: 12
- strongest rotational cumulative heading delta: approximately 5.057817
- 5-point combined candidate count: 1
- best 5-point window: 5-9
- heading sweep: approximately 2.617997
- path length: approximately 2.070536
- displacement ratio: approximately 0.836517
- inside rotational run: true

Interpretation:

The existing synthetic orb-like diagnostic probe remains supported at the current 5-point scale.

### UCI 39406 Pedestrian Anchor

Artifact:

`state_constructor/output/uci_pedestrians_in_traffic_oid_39406_state_segmented_trace.json`

Result:

- points: 198
- strongest rotational run length: 7
- strongest rotational cumulative heading delta: approximately 0.625231
- combined candidate count: 0 across reviewed window sizes

Interpretation:

UCI 39406 remains cleanly withheld under scale review.

## Biological Aerial Review Anchors

### White Stork Candidate A

Artifact:

`state_constructor/output/white_stork_nils_2014-08-10_140015_60pt_state_segmented_trace.json`

Result:

- points: 60
- strongest rotational run length: 47
- strongest rotational cumulative heading delta: approximately 7.244777
- 5-point combined candidate count: 0
- 25-point combined candidate count: 4
- best 25-point window: 20-44
- heading sweep: approximately 3.603856
- path length: approximately 253.306608
- displacement ratio: approximately 0.507077
- inside rotational run: true

Interpretation:

Candidate A is not merely a negative example under scale review. It shows Orb-adjacent evidence at a larger 25-point window scale, while remaining withheld under the current fixed 5-point constructor diagnostic.

### White Stork Candidate B

Artifact:

`state_constructor/output/white_stork_nils_2014-08-07_113020_60pt_state_segmented_trace.json`

Result:

- points: 60
- strongest rotational run length: 30
- strongest rotational cumulative heading delta: approximately 4.997839
- 5-point combined candidate count: 0
- 25-point combined candidate count: 1
- best 25-point window: 25-49
- heading sweep: approximately 4.509962
- path length: approximately 263.434413
- displacement ratio: approximately 0.311005
- inside rotational run: true

Interpretation:

Candidate B also shows scale-dependent Orb-adjacent evidence at a 25-point window scale.

## Engineered Aerial Review Anchors

### TII Short Ellipse Segment

Artifact:

`state_constructor/output/tii_flight_01a_ellipse_cam_ts_1460_1579_state_segmented_trace.json`

Result:

- points: 120
- strongest rotational run length: 118
- strongest rotational cumulative heading delta: approximately 3.023850
- 5-point combined candidate count: 0
- 25-point combined candidate count: 2
- 50-point combined candidate count: 6
- 100-point combined candidate count: 3

Best 100-point window:

- window: 10-109
- heading sweep: approximately 2.928787
- path length: approximately 9.290448
- displacement ratio: approximately 0.307989
- inside rotational run: true

Interpretation:

The short TII ellipse segment was withheld under the fixed 5-point diagnostic but shows meaningful support at larger review scales.

### TII 1000-Point Ellipse Segment

Artifact:

`state_constructor/output/tii_flight_01a_ellipse_cam_ts_950_1949_state_segmented_trace.json`

Result:

- points: 1000
- strongest rotational run length: 678
- strongest rotational cumulative heading delta: approximately 12.321393
- 5-point combined candidate count: 0
- 25-point combined candidate count: 3
- 50-point combined candidate count: 26
- 100-point combined candidate count: 55
- 250-point combined candidate count: 85
- 500-point combined candidate count: 35
- 750-point combined candidate count: 0
- 1000-point combined candidate count: 0

Best 250-point window:

- window: 285-534
- heading sweep: approximately 3.656836
- path length: approximately 32.308128
- displacement ratio: approximately 0.060229
- inside rotational run: true

Interpretation:

The TII 1000-point ellipse strongly supports the scale-sensitivity finding. Evidence is absent at 5 points, emerges at 25-50 points, is strongest around 100-250 points, remains present at 500 points, and disappears again at 750-1000 points. This suggests a support band rather than a simple rule of “larger is always better.”

## Design Interpretation

The current fixed 5-point Orb support diagnostic is conservative and useful, but it is not cadence-general.

Scale review suggests that Orb-adjacent evidence may emerge only when the support window is appropriate to the trace cadence and maneuver scale.

However, larger-window support must be interpreted carefully. Both engineered UAV ellipse segments and biological white stork segments can show larger-window Orb-adjacent evidence. Therefore, future cadence-aware support must preserve restraint and must not equate larger-window containment with Orb emission.

## Current Boundary

No constructor behavior should be changed based on this review alone.

Do not yet change:

- `candidate_state`
- `state`
- `run_summary`
- `state_model.activated_states`
- PC-MAW admission logic
- Playback behavior
- existing fixed 5-point `orb_candidate_support`

## Recommended Next Step

Keep the helper as review tooling and run additional comparisons before proposing constructor contract changes.

A future design phase may consider a separate diagnostic such as:

`processing.diagnostics.orb_candidate_support_scale_review`

or:

`processing.diagnostics.orb_candidate_support_time_window_review`

Such a diagnostic should remain review-only until a separate contract is drafted.
