# PC-MSAT Audit Interface

## Overview

PC-MSAT (Pre-Classification Motion Structure Audit Tool) is a **disclosure-oriented audit interface** for inspecting the outputs of geometry-first, state-segmented motion analysis.

This repository contains **documentation and visual artifacts only**.  
It contains **no code**, **no classifiers**, and **no decision logic**.

PC-MSAT is designed to expose whether motion structure is **geometrically and persistently supported** under fixed criteria, or whether such support is **insufficient and therefore withheld**.

---

## What PC-MSAT Is

PC-MSAT is:

- an **interface**, not a model  
- an **audit surface**, not a detector  
- a **disclosure mechanism**, not an interpretation system  

Specifically, PC-MSAT presents **State-Segmented Motion Traces** together with a **single supporting geometric signal**, allowing an observer to assess whether sufficient persistence exists to justify *proceeding* to downstream analysis — or whether restraint (*withholding*) is required.

Audit outcomes are **binary and conservative**:

- **Withhold** — insufficient geometric support  
- **Proceed** — sufficient geometric support under fixed criteria  

These outcomes are **not** success or failure states.

---

## What PC-MSAT Is Not

PC-MSAT is **explicitly not**:

- a classifier  
- a predictor  
- a detector  
- a decision system  
- a recommendation engine  

PC-MSAT does **not**:

- assert physical cause  
- infer intent or behavior  
- optimize parameters  
- evaluate performance  
- justify downstream action  

When motion structure is ambiguous or insufficiently persistent, PC-MSAT **withholds** rather than forcing interpretation.

---

## Relationship to Structured Orb Dynamics (SOD)

PC-MSAT operates **on outputs** produced by the Structured Orb Dynamics (SOD) framework.

- SOD defines a **geometry-first, state-based method** for motion analysis.  
- PC-MSAT defines **how those outputs are exposed and audited**.

PC-MSAT introduces **no new inference** beyond what is already present in the State-Segmented Motion Trace.  
Its purpose is to demonstrate how restraint and withholding can be preserved at the interface level.

---

## Visual Artifacts in This Repository

This repository contains a **paired set of audit visuals**:

- **Withhold Visual**  
  A State-Segmented Motion Trace in which no contiguous segment satisfies conservative geometric and persistence criteria.

- **Proceed Visual**  
  A State-Segmented Motion Trace in which a contiguous segment satisfies the same fixed criteria.

Both visuals:

- are rendered under identical constraints  
- use the same renderer contract  
- include one supporting geometric signal (raw curvature)  
- differ **only** in audit outcome  

These visuals are provided for **inspection**, not persuasion.

---

## Scope and Limitations

PC-MSAT is intentionally narrow in scope.

It does not attempt to:

- resolve ambiguity  
- explain motion origin  
- rank hypotheses  
- replace downstream systems  

Its sole function is to answer a constrained question:

> *Is there sufficient, persistence-supported geometric structure to justify proceeding — or should interpretation be withheld?*

---

## Licensing

All documentation, text, and visual artifacts in this repository are licensed under:

**Creative Commons Attribution–NonCommercial–NoDerivatives 4.0 International  
(CC BY-NC-ND 4.0)**

See the `LICENSE` file for full terms.

---

## Citation and Use

PC-MSAT materials may be shared and cited for **non-commercial, non-derivative** purposes with attribution.

Use of these materials does not imply endorsement, correctness, or applicability to any specific domain or downstream system.

---

## Status

PC-MSAT is provided as a **stable reference interface**.  
It is not a software project and is not intended to evolve rapidly.

Any changes will be deliberate and documented.
