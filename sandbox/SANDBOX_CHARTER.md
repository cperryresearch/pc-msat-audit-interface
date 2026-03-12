# PC-MSAT Sandbox Charter

## Purpose

The **PC-MSAT Sandbox** is a bounded experimental workspace contained within the `pc-msat-audit-interface` repository. Its purpose is to allow controlled exploration of how the existing PC-MSAT audit interface behaves when applied to varied motion traces under fixed constraints.

The sandbox supports:

- inspection of edge cases and boundary conditions  
- pedagogical examples illustrating audit outcomes  
- controlled experimentation with input traces  
- improved understanding of audit behavior under varied motion structures  

All experimentation conducted within the sandbox operates strictly within the constraints of the existing PC-MSAT audit framework.

---

## Scope

The sandbox provides an environment for generating exploratory audit outputs using the **canonical renderer and fixed decision criteria** already defined within the repository.

The sandbox may introduce **new input traces** for examination but must not alter:

- the canonical renderer  
- the audit decision rules  
- persistence thresholds  
- geometric signal definitions  
- the structure of the audit interface  

The sandbox therefore functions as a **trace exploration workspace**, not a method development environment.

---

## Non-Goals

The PC-MSAT Sandbox is **not** intended to serve as:

- a second implementation of PC-MSAT  
- a tuning or parameter optimization environment  
- a location for modifying canonical audit behavior  
- a classifier development framework  
- a mechanism for revising the formal specification  

The sandbox must not become a pathway for indirect modification of the PC-MSAT method.

---

## Relationship to Canonical Artifacts

All canonical artifacts defined in the repository remain authoritative. These include:

- the formal specification  
- the canonical audit renderer  
- the reference demonstration artifacts  
- the documented audit protocol  

Sandbox outputs are **exploratory artifacts only** and carry no canonical status unless explicitly promoted through a separate, deliberate revision process.

---

## Governing Principle

All sandbox exploration operates under the same methodological constraints that govern the broader **Structured Orb Dynamics** and **PC-MSAT** ecosystem:

> **Geometry-first evaluation, methodological restraint, and explicit withholding where motion structure does not support inference.**

Sandbox experimentation must preserve this posture.

A **WITHHOLD** result is considered a valid and expected outcome when the persistence criteria required for a **PROCEED** decision are not satisfied.

---

## Summary

In practical terms, the PC-MSAT Sandbox exists to answer the question:

> *“How does the existing audit interface behave when applied to this trace?”*

It does **not** attempt to change the audit method in order to produce a preferred outcome.
