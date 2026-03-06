# PC-MSAT
### Pre-Classification Motion Structure Audit Tool

PC-MSAT is a **protocol for auditing motion traces before analysis**.

It provides a **pre-classification audit protocol for motion traces**, ensuring geometric persistence exists before downstream interpretation.

The purpose of PC-MSAT is to determine whether a motion trace contains sufficient **geometric persistence** to justify downstream interpretation.

Rather than performing classification, the protocol evaluates motion structure and produces a simple audit outcome:

- **Proceed** — the trace exhibits sufficient persistence for further analysis
- **Withhold** — the trace lacks persistent geometric structure

---

## The Audit Sheet

PC-MSAT audits are presented as a four-panel sheet:

1. **State-Segmented Motion Trace**
2. **Raw Curvature Signal κ(t)**
3. **Persistence Panel** (run-length evaluation)
4. **Audit Result** (Proceed / Withhold)

This structure allows motion traces to be evaluated consistently before interpretation.

---

## Role in the Analysis Pipeline

PC-MSAT sits between motion-trace generation and downstream interpretation.

```text
Trajectory Data
      ↓
Segmentation (SOD or other)
      ↓
PC-MSAT Audit
      ↓
Proceed / Withhold
      ↓
Downstream Analysis
```

This framing preserves the distinction between trace generation and trace auditing. PC-MSAT is not a segmentation framework and not a classifier; it is a protocol for determining whether a motion trace is structurally sufficient to justify further analysis.

---

## Example Audits

### Withhold Example

![Withhold Demo](visuals/withhold_demo.png)

### Proceed Example

![Proceed Demo](visuals/proceed_demo.png)

---

## Repository

Full specification, renderer, and example artifacts:
**[https://github.com/cperryresearch/pc-msat-audit-interface](https://github.com/cperryresearch/pc-msat-audit-interface)**

Part of the Structured Orb Dynamics research ecosystem.