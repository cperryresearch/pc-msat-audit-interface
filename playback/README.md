# Playback Tool v1

Visualization-only viewer for precomputed state-segmented motion traces.

## Purpose

Playback Tool v1 provides progressive visual playback of an already-computed state-segmented trace. It exists strictly downstream of trace generation and is intended for bounded demonstration and trace inspection only.

## Scope Boundaries

This viewer is read-only and visualization-only. It does not perform:

- classification
- inference
- persistence evaluation
- audit logic
- smoothing
- interpolation
- state generation or reassignment
- PROCEED/WITHHOLD decision display

All displayed structure is derived solely from the supplied precomputed trace artifact.

## Current Structure

- `index.html` — minimal viewer shell
- `playback.js` — playback and rendering logic
- `trace.json` — precomputed input trace

## Usage

Serve the folder locally and open `index.html` through a local server environment so `trace.json` can be fetched correctly.

Example:
- VS Code Live Server

## Mode Entry Points

- Standalone mode: `startStandalonePlayback()` loads `trace.json`
- Embedded mode: `startEmbeddedPlayback(trace)` accepts precomputed trace data from a parent interface

## Rendering Notes

- fixed equal-aspect geometric presentation
- segment color determined by the terminating point’s assigned state
- neutral marker shown only at the initial observation
- no persistence panel or audit output is shown