# PC-MSAT Paired Demo Data Selection Protocol

## Purpose

This document defines the selection protocol used to construct the
PC-MSAT demonstration pair:

- one **WITHHOLD** case
- one **PROCEED** case

The purpose of the paired demonstration is to illustrate the behavior
of the PC-MSAT audit interface under identical rendering rules and
threshold parameters.

The paired examples are not intended to demonstrate performance or
optimize results. They are intended only to illustrate the decision
logic of the audit interface.

---

# Selection Requirements

The paired demo must satisfy the following conditions.

## 1. Same renderer rules

Both examples must use identical renderer parameters:

- identical persistence rule
- identical MIN_RUN threshold
- identical panel layout
- identical curvature computation
- identical color palette

The only difference between the examples is the **motion structure
present in the trace**.

---

## 2. Clear persistence outcome

The traces must produce clearly distinguishable persistence outcomes.

WITHHOLD case:

```
max_run < MIN_RUN
```

PROCEED case:

```
max_run ≥ MIN_RUN
```

No manual override of the decision rule is allowed.

---

## 3. No synthetic manipulation

The demonstration traces must not be:

- artificially constructed
- state-edited
- threshold-tuned

The audit result must arise naturally from the motion structure present
in the trace.

---

## 4. Comparable scale

Where possible, the paired traces should have similar:

- observation counts
- sampling cadence
- trajectory scale

This helps ensure the comparison highlights **persistence structure**
rather than dataset differences.

---

# Demonstration Philosophy

The paired demo intentionally emphasizes restraint.

The WITHHOLD case demonstrates that the audit interface will refuse
promotion when persistence support is insufficient.

The PROCEED case demonstrates the condition under which the audit
interface allows downstream processing to continue.

Together, the two examples illustrate the operational boundary of the
PC-MSAT audit layer.

---

# Example Demonstration Pair

Example structure:

WITHHOLD case

```
Trace ID: barn_swallow_vi_b_2350-21095
Cadence: 600 s
MIN_RUN: 3
Outcome: WITHHOLD
```

PROCEED case

```
Trace ID: [example trace]
Cadence: [matching cadence if possible]
MIN_RUN: 3
Outcome: PROCEED
```

The paired artifacts must be rendered using the same renderer blueprint
defined in:

```
spec/renderer-blueprint.md
```

---

# Output Artifacts

The paired demonstration produces two primary artifacts.

```
visuals/pcmsat_audit_withhold.png
visuals/pcmsat_audit_proceed.png
```

Optional context figures may also be provided.

```
visuals/pcmsat_context_full_withhold.png
visuals/pcmsat_context_full_proceed.png
```

---

# Integrity Check

Before publication, the following must be verified:

1. Renderer parameters identical for both cases
2. Persistence rule applied automatically
3. CASE_LABEL matches computed result
4. Artifacts produced by the same renderer configuration

This ensures the paired demo remains a faithful illustration of the
PC-MSAT audit interface.