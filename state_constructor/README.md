# State-Segmented Trace Constructor v0

## Purpose

The State-Segmented Trace Constructor v0 is a bounded upstream SOD unit that converts one clean, time-ordered planar trajectory into one canonical, structurally validated, parent-owned `state_segmented_trace` artifact under the minimal v0 rule set.

It is the smallest faithful coded SOD bridge currently implemented for the PC-MAW ecosystem.

## Scope

In v0, the constructor is responsible only for trace construction and canonical artifact assembly/validation.

Current active state scope is limited to:

- `Straight`
- `Turn`

The following states remain present in the canonical schema vocabulary but are not yet activated in v0:

- `Hover`
- `Orb`

## Input

The constructor accepts:

- one clean, time-ordered planar trajectory
- minimal configuration required for bounded v0 construction

## Output

The constructor emits exactly one canonical `state_segmented_trace` artifact.

This artifact is structurally validated before successful completion.

Point-level records are authoritative.  
`run_summary` is derived from and subordinate to the ordered point records.

## Responsibilities

The constructor:

- ingests a clean ordered planar trajectory
- applies the bounded v0 construction process
- assembles the canonical artifact structure
- validates post-assembly structural consistency against the canonical v0 contract
- returns a valid artifact or raises the canonical validation failure surface

## Non-goals

The constructor does not perform:

- audit decisions
- persistence judgment
- PROCEED / WITHHOLD outcomes
- playback or visualization
- workflow or interface orchestration
- interpretive analysis
- full PC-MAW application behavior

## Relationship to adjacent components

The constructor sits upstream of downstream parent-owned PC-MAW uses:

`raw planar trajectory -> State-Segmented Trace Constructor v0 -> canonical parent-owned state_segmented_trace artifact -> downstream parent context`

Examples of downstream parent context may later include playback, audit presentation, persistence analysis, or broader PC-MAW workflow logic.

## Validation boundary

Post-assembly artifact validation is part of the constructor boundary in canonical v0.

If structural validation succeeds, the constructor completes normally.

If structural validation fails, the constructor raises `ArtifactValidationError` with the fixed summary:

`Canonical v0 artifact validation failed.`

## Status

This is a minimal, bounded v0 implementation. It should be described as a trace-construction unit, not as a full audit system or full PC-MAW application.