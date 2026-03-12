# sandbox_trace_005 metadata

## Trace ID
sandbox_trace_005

## Type
Synthetic

## Purpose
Near-threshold failure case demonstrating ordered short runs that do not satisfy persistence.

## Design Logic
This trace is intentionally structured and visually orderly, but every contiguous state run has length 2.

Run structure:
Straight, Straight
Turn, Turn
Straight, Straight
Turn, Turn

## Threshold Context
MIN_RUN = 3

Maximum contiguous run length = 2

## Expected Audit Result
WITHHOLD

## Interpretation Note
This trace demonstrates that visible structure alone is not sufficient for PROCEED.
The audit decision depends on persistence crossing the threshold, not on whether the trajectory appears organized.