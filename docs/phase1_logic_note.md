# PC-MSAT Phase 1 Logic Note
*Method clarification note*

## Purpose

This note consolidates the foundational logic of PC-MSAT established during Phase 1 clarification work. Its purpose is to preserve the conceptual boundaries of the method before additional experiments, visual interfaces, or implementation layers expand around it.

PC-MSAT is treated here as a deterministic, geometry-first audit, not an interpretive engine, exploratory viewer, or adaptive scoring system.

---

## North Star

> **PC-MSAT is a deterministic, geometry-first audit that determines whether a state-segmented motion trace exhibits sufficient contiguous geometric persistence to justify interpretation; when sustained persistence is absent, interpretation is explicitly withheld.**

This statement governs the method as a whole.

---

## Method Structure

PC-MSAT is organized as a layered system:

- **North Star** — guiding principle
- **Load-Bearing Axioms** — method-defining commitments
- **Supporting Assumptions** — implementation-level choices that may evolve
- **Method Logic** — the audit rule and its application
- **Artifacts** — renderer, audit sheets, sandbox traces
- **Future Interfaces** — tools that expose the rule without changing it

Authority flows downward from method to artifact, never upward from tool to definition.

---

## Load-Bearing Axioms

The following commitments define the method itself:

1. **Geometry-first posture**  
   Motion structure is assessed through geometric behavior in the trace.

2. **Persistence requirement**  
   Interpretation requires sustained geometric persistence.

3. **Contiguous run definition**  
   Persistence is operationalized through contiguous runs of consistent geometric state.

4. **Deterministic rule**  
   Audit outcomes follow a fixed rule rather than discretionary judgment.

5. **Interpretation restraint**  
   When sufficient persistence support is absent, interpretation is withheld.

6. **Binary audit outcome**  
   PC-MSAT produces only:
   - **PROCEED**
   - **WITHHOLD**

PC-MSAT does not generate interpretations. It determines whether interpretation is justified.

---

## Supporting Assumptions

The current implementation relies on several assumptions that support the method without defining it:

- state-segmented trace input
- a fixed persistence threshold such as `MIN_RUN`
- curvature or similar signals as supporting geometric context
- a standardized audit sheet layout for communication

These may evolve without changing the core logic of PC-MSAT.

---

## Persistence Ladder v1

The **Persistence Ladder** is a descriptive logic aid used to characterize how strongly a trace exhibits contiguous geometric support. It does not replace the binary audit rule.

### Level 0 — Noise / No Coherent Support
No meaningful contiguous state structure supports interpretation.  
**Outcome:** WITHHOLD

### Level 1 — Fragmentation
Recognizable geometric structure appears locally but repeatedly breaks before becoming sustained.  
**Outcome:** WITHHOLD

### Level 2 — Near-Persistence
The trace approaches persistence support but still fails the criterion.  
**Outcome:** WITHHOLD

### Level 3 — Sustained Persistence
At least one contiguous run exhibits sufficient support to satisfy the persistence criterion.  
**Outcome:** PROCEED

The ladder is descriptive, not decisional. Levels 0–2 remain WITHHOLD; only Level 3 permits PROCEED.

---

## Fragmentation vs Persistence

Both fragmentation and persistence may contain real geometric structure. The distinction is not between order and disorder, but between **interrupted structure** and **sustained structure**.

> **Fragmentation** is the repeated interruption of otherwise recognizable geometric state structure before it reaches sufficient contiguous persistence to support interpretation.

> **Persistence** is the contiguous maintenance of a geometric state for long enough to satisfy the audit’s minimum structural support requirement.

Fragmentation is therefore **not the absence of structure**. It is the absence of **sufficiently sustained** structure.

PC-MSAT grants interpretive permission only to persistence, not to fragmentation.

---

## Cadence Considerations

PC-MSAT evaluates sampled traces, not continuous motion directly. For that reason, cadence affects how geometric structure becomes visible in the observed trace.

> **Cadence affects the visibility of persistence, not the definition of persistence.**

Coarser cadence may obscure or compress structure. Finer cadence may reveal sustained runs, but it may also expose interruptions that coarse sampling had hidden. Cadence therefore changes the observational form of the evidence, not the audit rule itself.

Persistence is never inferred simply because a different cadence might have shown more.

---

## Playback Invariant

A separate playback viewer may exist as a downstream visualization-only companion. Its role is strictly limited.

> **The playback tool is a read-only visualization of precomputed state-segmented traces and does not compute, represent, or imply persistence. Persistence remains defined exclusively by contiguous run structure relative to MIN_RUN within the PC-MSAT audit logic.**

This preserves the distinction between what is **seen** and what is **methodologically defined**.

---

## Logic / Program Alignment

PC-MSAT development proceeds through two coordinated lanes:

### Logic Lane
- concept clarification
- definition refinement
- failure analysis
- methodological reasoning

### Program Lane
- renderer artifacts
- sandbox traces
- demonstrations
- visual tools

Working cycle:

```text
logic question
↓
program experiment
↓
artifact inspection
↓
logic refinement

## Core Summary

PC-MSAT is a deterministic, geometry-first audit that permits interpretation only when a state-segmented trace exhibits sufficient contiguous persistence. It distinguishes visible structure from sustained structural support, treats fragmentation as interrupted rather than absent structure, and treats cadence as affecting observability rather than meaning. All artifacts remain subordinate to the fixed audit rule, and downstream visualization tools are explicitly denied methodological authority.