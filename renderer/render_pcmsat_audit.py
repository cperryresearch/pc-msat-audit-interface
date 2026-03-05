#!/usr/bin/env python3
"""
PC-MSAT v0 Reference Renderer
- Produces a single PC-MSAT audit sheet PNG from a state-segmented motion trace.
- Spec-first: deterministic layout, no tuning, no smoothing, no inference beyond run-length rule.

Input CSV must contain columns:
    t, x, y, state

Allowed states:
    Straight, Turn, Hover, Orb
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


ALLOWED_STATES = ("Straight", "Turn", "Hover", "Orb")

# SOD palette (muted; adjust once globally if you later formalize exact hex codes)
SOD_COLORS: Dict[str, str] = {
    "Straight": "#3B6EA8",  # muted blue
    "Turn": "#D08B2C",  # amber
    "Hover": "#3C8D5A",  # muted green
    "Orb": "#7A728C",  # neutral gray-violet
}

RESULT_COLORS: Dict[str, str] = {
    "WITHHOLD": "#6B6B6B",  # neutral gray
    "PROCEED": "#2F7D4A",  # muted green
}


@dataclass(frozen=True)
class Meta:
    trace_id: str
    source: str
    case_label: str  # "WITHHOLD" or "PROCEED"
    cadence: str
    n_shown: int
    window_rule: str
    projection: str
    min_run: int


def require_columns(df: pd.DataFrame, cols: List[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def validate_states(states: np.ndarray) -> None:
    bad = sorted(set(states) - set(ALLOWED_STATES))
    if bad:
        raise ValueError(
            f"Unknown state labels: {bad}. Allowed: {list(ALLOWED_STATES)}"
        )


def window_first_n(df: pd.DataFrame, n: int) -> pd.DataFrame:
    if len(df) < n:
        raise ValueError(f"Trace has only {len(df)} rows; cannot take first n={n}.")
    return df.iloc[:n].copy()


def compute_signed_curvature(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Raw signed curvature estimate from discrete points.
    Uses central differences and computes:
        kappa = (x' y'' - y' x'') / ( (x'^2 + y'^2)^(3/2) )
    No smoothing, no filtering.
    """
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)

    if len(x) < 3:
        raise ValueError("Need at least 3 points to compute curvature.")

    dx = np.gradient(x)
    dy = np.gradient(y)
    ddx = np.gradient(dx)
    ddy = np.gradient(dy)

    denom = np.power(dx * dx + dy * dy, 1.5)

    with np.errstate(divide="ignore", invalid="ignore"):
        kappa = (dx * ddy - dy * ddx) / denom

    kappa = np.where(np.isfinite(kappa), kappa, 0.0)
    kappa = np.where(denom > 0, kappa, 0.0)
    return kappa


def contiguous_runs(states: np.ndarray) -> List[Tuple[int, str, int, int]]:
    """
    Returns list of runs:
        (run_index, state_label, start_idx, length)
    """
    runs: List[Tuple[int, str, int, int]] = []
    if len(states) == 0:
        return runs

    run_idx = 0
    start = 0
    current = states[0]

    for i in range(1, len(states)):
        if states[i] != current:
            length = i - start
            runs.append((run_idx, current, start, length))
            run_idx += 1
            start = i
            current = states[i]

    runs.append((run_idx, current, start, len(states) - start))
    return runs


def compute_result(
    runs: List[Tuple[int, str, int, int]], min_run: int
) -> Tuple[str, int]:
    max_run = max((length for (_, _, _, length) in runs), default=0)
    result = "PROCEED" if max_run >= min_run else "WITHHOLD"
    return result, max_run


def state_boundaries(states: np.ndarray) -> List[int]:
    """Boundary indices where state changes."""
    b: List[int] = []
    for i in range(1, len(states)):
        if states[i] != states[i - 1]:
            b.append(i)
    return b


def draw_state_colored_trajectory(
    ax, x: np.ndarray, y: np.ndarray, states: np.ndarray
) -> None:
    runs = contiguous_runs(states)

    for run_idx, s, start, length in runs:
        end = start + length

        # draw trajectory segment
        ax.plot(x[start:end], y[start:end], color=SOD_COLORS[s], linewidth=2)

        # compute midpoint for index label
        mid = start + length // 2
        xm = x[mid]
        ym = y[mid]

        # run index marker
        ax.text(
            xm,
            ym,
            str(run_idx + 1),
            fontsize=9,
            ha="center",
            va="center",
            color="#111111",
            bbox=dict(
                boxstyle="circle,pad=0.25",
                facecolor="white",
                edgecolor="#333333",
                linewidth=0.8,
                alpha=0.9,
            ),
            zorder=6,
        )

    # start marker
    ax.scatter([x[0]], [y[0]], s=45, color="#222222", zorder=5)

    # end marker
    ax.scatter(
        [x[-1]],
        [y[-1]],
        s=55,
        facecolors="none",
        edgecolors="#222222",
        linewidths=1.6,
        zorder=5,
    )

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.tick_params(axis="both", labelsize=9)


def draw_curvature_panel(ax, kappa: np.ndarray, boundaries: List[int]) -> None:
    n = len(kappa)
    idx = np.arange(n)

    ax.grid(axis="y", linestyle="-", linewidth=0.6, alpha=0.18)
    ax.axhline(0.0, linestyle="-", linewidth=0.9, alpha=0.35)

    for b in boundaries:
        ax.axvline(b, linestyle="-", linewidth=0.7, alpha=0.30)

    ax.plot(idx, kappa, linewidth=1.4, color="#222222")

    m = float(np.max(np.abs(kappa))) if n else 1.0
    if m == 0:
        m = 1.0
    ax.set_ylim(-1.1 * m, 1.1 * m)

    ax.set_xlim(0, n - 1)
    ax.set_ylabel("κ(t)")
    ax.set_xlabel("observation index")
    ax.tick_params(axis="both", labelsize=9)


def draw_persistence_panel(
    ax_top, ax_bottom, runs: List[Tuple[int, str, int, int]], min_run: int
) -> None:
    def _annotate_barh(ax, x: float, y: float, text: str, pad: float = 0.08) -> None:
        """
        Place a small label just to the right of a bar end.
        Assumes x-limits are already set to include some breathing room.
        """
        ax.text(x + pad, y, text, va="center", ha="left", fontsize=8, alpha=0.9)

    # Shared x-limit so both panels align and annotations have room.
    run_lengths = [length for (_, _, _, length) in runs]
    max_len = max(run_lengths, default=0)
    xmax = max(max_len, min_run) + 1.25  # breathing room for labels
    if xmax <= 0:
        xmax = 1.5

    # -----------------------------
    # Decision layer (state-agnostic)
    # -----------------------------
    y = np.arange(len(run_lengths))

    colors = ["#2F7D4A" if length >= min_run else "#444444" for length in run_lengths]

    ax_top.barh(y, run_lengths, color=colors, alpha=0.9)
    ax_top.axvline(min_run, color="#444444", linewidth=1.0, alpha=0.6)
    ax_top.set_xlim(0, xmax)

    ax_top.set_yticks(y)
    ax_top.set_yticklabels([f"Run {i+1}" for i in y], fontsize=8)
    ax_top.set_xlabel("run length (observations)")
    ax_top.set_title(
        f"Contiguous Run Lengths (Decision Layer) — MIN_RUN = {min_run}",
        fontsize=10,
        loc="left",
    )
    ax_top.grid(axis="x", linestyle="-", linewidth=0.6, alpha=0.15)
    ax_top.invert_yaxis()

    # ----------------------------------------
    # Diagnostic layer (state-typed; context only)
    # Grouped by state for readability; raw runs preserved.
    # ----------------------------------------
    by_state: Dict[str, List[int]] = {s: [] for s in ALLOWED_STATES}
    for _, s, _, length in runs:
        by_state[s].append(length)

    diag_states: List[str] = []
    diag_lengths: List[int] = []
    diag_labels: List[str] = []

    for s in ALLOWED_STATES:
        lengths = by_state[s]
        if not lengths:
            continue

        for i, length in enumerate(lengths):
            diag_states.append(s)
            diag_lengths.append(length)
            diag_labels.append(s if i == 0 else "")

        # spacer row between state groups (transparent)
        diag_states.append("Straight")  # placeholder; will be fully transparent
        diag_lengths.append(0)
        diag_labels.append("")

    # drop trailing spacer
    if diag_lengths and diag_lengths[-1] == 0:
        diag_states.pop()
        diag_lengths.pop()
        diag_labels.pop()

    y2 = np.arange(len(diag_lengths))

    colors: List[str] = []
    alphas: List[float] = []
    for s, length in zip(diag_states, diag_lengths):
        if length == 0:
            colors.append("#FFFFFF")
            alphas.append(0.0)
        else:
            colors.append(SOD_COLORS[s])
            alphas.append(0.95)

    bars = ax_bottom.barh(y2, diag_lengths, color=colors)
    for bar, a in zip(bars, alphas):
        bar.set_alpha(a)

    ax_bottom.axvline(min_run, color="#444444", linewidth=1.0, alpha=0.6)
    ax_bottom.set_xlim(0, xmax)

    ax_bottom.set_yticks(y2)
    ax_bottom.set_yticklabels(diag_labels, fontsize=8)
    ax_bottom.set_xlabel("run length (observations)")
    ax_bottom.set_title(
        f"Diagnostic Persistence (same runs grouped by state — non-decisional) — MIN_RUN = {min_run}",
        fontsize=10,
        loc="left",
    )
    ax_bottom.grid(axis="x", linestyle="-", linewidth=0.6, alpha=0.15)
    ax_bottom.invert_yaxis()

    # ---- NEW: annotate run lengths on diagnostic bars (skip spacer rows) ----
    for yi, length in zip(y2, diag_lengths):
        if length > 0:
            _annotate_barh(ax_bottom, float(length), float(yi), str(int(length)))

    ax_bottom.text(
        0.0,
        -0.35,
        "Decision uses contiguous run length only. Diagnostic layer preserves raw runs (grouped by state for readability).",
        transform=ax_bottom.transAxes,
        fontsize=8,
        va="top",
        ha="left",
        alpha=0.85,
    )


def render_audit_sheet(df: pd.DataFrame, meta: Meta, out_path: Path) -> None:
    require_columns(df, ["t", "x", "y", "state"])
    df = df.copy()

    df["x"] = pd.to_numeric(df["x"], errors="raise")
    df["y"] = pd.to_numeric(df["y"], errors="raise")
    df["state"] = df["state"].astype(str)

    states = df["state"].to_numpy()
    validate_states(states)

    if meta.n_shown < meta.min_run:
        raise ValueError(
            f"n_shown ({meta.n_shown}) must be >= MIN_RUN ({meta.min_run})."
        )

    dfw = window_first_n(df, meta.n_shown)

    x = dfw["x"].to_numpy(dtype=float)
    y = dfw["y"].to_numpy(dtype=float)
    states_w = dfw["state"].to_numpy(dtype=str)

    if not (np.isfinite(x).all() and np.isfinite(y).all()):
        raise ValueError("x/y contain non-finite values (NaN or inf).")

    kappa = compute_signed_curvature(x, y)
    runs = contiguous_runs(states_w)
    result, max_run = compute_result(runs, meta.min_run)

    if meta.case_label.upper() not in ("WITHHOLD", "PROCEED"):
        raise ValueError("CASE_LABEL must be WITHHOLD or PROCEED.")

    if result != meta.case_label.upper():
        raise ValueError(
            f"CASE_LABEL mismatch: declared={meta.case_label.upper()} computed={result} "
            f"(max_run={max_run}, MIN_RUN={meta.min_run})"
        )

    boundaries = state_boundaries(states_w)

    plt.close("all")
    fig = plt.figure(figsize=(10, 12), dpi=200)

    gs = GridSpec(
        nrows=5,
        ncols=1,
        height_ratios=[0.9, 4, 2, 2, 1],
        hspace=0.55,
    )

    ax_header = fig.add_subplot(gs[0])
    ax_header.axis("off")

    header_text = (
        "PC-MSAT Audit Sheet\n\n"
        f"Trace ID: {meta.trace_id}   Source: {meta.source}   Case: {meta.case_label.upper()}\n"
        f"Cadence: {meta.cadence}   Observations shown: {meta.n_shown} ({meta.window_rule})\n"
        f"Projection: {meta.projection}   Signal: raw signed curvature κ(t) (no smoothing)\n"
        f"Persistence rule: MIN_RUN = {meta.min_run} contiguous observations\n"
        "Decision basis: contiguous run length only (state-typed breakdown is diagnostic)"
    )
    ax_header.text(
        0.0, 1.0, header_text, va="top", ha="left", fontsize=9, family="monospace"
    )

    ax1 = fig.add_subplot(gs[1])
    ax1.set_title("State-Segmented Motion Trace", fontsize=11, loc="left")
    draw_state_colored_trajectory(ax1, x, y, states_w)

    ax2 = fig.add_subplot(gs[2])
    ax2.set_title("Raw Signed Curvature κ(t)", fontsize=11, loc="left")
    draw_curvature_panel(ax2, kappa, boundaries)

    gs_p3 = gs[3].subgridspec(2, 1, height_ratios=[1, 1], hspace=0.7)
    ax3a = fig.add_subplot(gs_p3[0])
    ax3b = fig.add_subplot(gs_p3[1])

    ax3a.set_title("Persistence Analysis", fontsize=11, loc="left", pad=14)

    draw_persistence_panel(ax3a, ax3b, runs, meta.min_run)

    ax4 = fig.add_subplot(gs[4])
    ax4.axis("off")
    ax4.set_title("Audit Outcome", fontsize=11, loc="left")
    ax4.text(
        0.5,
        0.45,
        result,
        fontsize=28,
        fontweight="bold",
        ha="center",
        va="center",
        color=RESULT_COLORS[result],
    )
    ax4.text(
        0.5,
        0.10,
        "(binary, conservative)",
        fontsize=9,
        ha="center",
        va="center",
        alpha=0.75,
    )

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    p = argparse.ArgumentParser(
        description="Render a PC-MSAT audit sheet from a state-segmented trace CSV."
    )
    p.add_argument(
        "--csv", required=True, help="Path to input trace CSV (columns: t,x,y,state)."
    )
    p.add_argument(
        "--out",
        required=True,
        help="Path to output PNG (e.g., visuals/pcmsat_audit_withhold.png).",
    )

    p.add_argument("--trace-id", required=True)
    p.add_argument("--source", required=True)
    p.add_argument("--case", required=True, choices=["WITHHOLD", "PROCEED"])
    p.add_argument("--cadence", required=True)
    p.add_argument("--n-shown", type=int, default=90)
    p.add_argument("--window-rule", default="first 90 observations")
    p.add_argument("--projection", default="planar")
    p.add_argument("--min-run", type=int, default=3)

    args = p.parse_args()
    df = pd.read_csv(args.csv)

    meta = Meta(
        trace_id=args.trace_id,
        source=args.source,
        case_label=args.case,
        cadence=args.cadence,
        n_shown=args.n_shown,
        window_rule=args.window_rule,
        projection=args.projection,
        min_run=args.min_run,
    )

    render_audit_sheet(df, meta, Path(args.out))


if __name__ == "__main__":
    main()
