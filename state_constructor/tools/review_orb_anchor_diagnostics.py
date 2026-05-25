#!/usr/bin/env python3
"""
Review Orb-adjacent diagnostic evidence across Constructor v0 anchor outputs.

This script is diagnostic-review only.
It does not modify constructor behavior, candidate_state, state, run_summary,
PC-MAW admission, or Playback.

Purpose:
- Extract worksheet data for Orb Candidate Support threshold review.
- Compare rotational persistence, windowed heading sweep, spatial containment,
  and fitted-circle coherence by anchor.
- List shared start_index/end_index windows across heading sweep,
  spatial containment, and fitted-circle coherence.
- Help determine whether same-window strict overlap is plausible before choosing
  numeric Orb support thresholds.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Optional


DEFAULT_ANCHORS = [
    "test_trace_hover_001_state_segmented_trace.json",
    "test_trace_turn_001_state_segmented_trace.json",
    "test_trace_orb_like_001_state_segmented_trace.json",
    "uci_pedestrians_in_traffic_oid_39406_state_segmented_trace.json",
]

THRESHOLD_PROBES: dict[str, dict[str, Any]] = {
    "orb_candidate_support_thresholds_conservative_probe_v0": {
        "metadata": {
            "status": "provisional",
            "basis": "anchor-derived",
            "emission_posture": "no-emission",
            "validation_maturity": "not mature validation",
        },
        "thresholds": {
            "min_rotational_run_length_points": 5,
            "min_rotational_run_cumulative_abs_heading_delta": 1.5,
            "min_window_heading_sweep": 1.5,
            "min_path_length": 1.0,
            "max_displacement_ratio": 0.90,
            "max_mean_radial_residual_ratio": 0.00005,
            "max_max_radial_residual_ratio": 0.0001,
        },
    }
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    if not isinstance(payload, dict):
        raise ValueError(f"Expected top-level JSON object in {path}")

    return payload


def get_nested(payload: dict[str, Any], keys: list[str], default: Any = None) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def first_present(mapping: dict[str, Any], keys: list[str], default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def as_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return None


def as_int(value: Any) -> Optional[int]:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return None


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def recursive_dicts(value: Any) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []

    if isinstance(value, dict):
        found.append(value)
        for child in value.values():
            found.extend(recursive_dicts(child))

    elif isinstance(value, list):
        for item in value:
            found.extend(recursive_dicts(item))

    return found


def window_span(item: dict[str, Any]) -> tuple[Optional[int], Optional[int]]:
    start = as_int(first_present(item, ["start_index", "window_start_index", "start"]))
    end = as_int(first_present(item, ["end_index", "window_end_index", "end"]))
    return start, end


def window_length(item: dict[str, Any]) -> Optional[int]:
    explicit = as_int(first_present(item, ["length", "window_length", "window_size_points"]))
    if explicit is not None:
        return explicit

    start, end = window_span(item)
    if start is not None and end is not None and end >= start:
        return end - start + 1

    return None


def has_any_key(item: dict[str, Any], keys: list[str]) -> bool:
    return any(key in item for key in keys)


def extract_span_records(block: Any, required_value_keys: list[str]) -> list[dict[str, Any]]:
    """
    Recursively extracts dictionaries that look like window/run records:
    - must have a usable start_index/end_index span
    - must contain at least one required value key
    """
    records: list[dict[str, Any]] = []

    for item in recursive_dicts(block):
        start, end = window_span(item)
        if start is None or end is None:
            continue
        if not has_any_key(item, required_value_keys):
            continue
        records.append(item)

    return records


def find_best_max(
    items: list[dict[str, Any]],
    value_keys: list[str],
) -> tuple[Optional[dict[str, Any]], Optional[float]]:
    best_item: Optional[dict[str, Any]] = None
    best_value: Optional[float] = None

    for item in items:
        value = as_number(first_present(item, value_keys))
        if value is None:
            continue
        if best_value is None or value > best_value:
            best_value = value
            best_item = item

    return best_item, best_value


def find_best_min(
    items: list[dict[str, Any]],
    value_keys: list[str],
) -> tuple[Optional[dict[str, Any]], Optional[float]]:
    best_item: Optional[dict[str, Any]] = None
    best_value: Optional[float] = None

    for item in items:
        value = as_number(first_present(item, value_keys))
        if value is None:
            continue
        if best_value is None or value < best_value:
            best_value = value
            best_item = item

    return best_item, best_value


def extract_existing_state_behavior(payload: dict[str, Any]) -> dict[str, Any]:
    run_summary = payload.get("run_summary", {})
    points = payload.get("points", [])

    candidate_runs = run_summary.get("candidate_state_runs", [])
    state_runs = run_summary.get("state_runs", [])

    first_accepted_state = None
    if isinstance(state_runs, list) and state_runs:
        first_run = state_runs[0]
        if isinstance(first_run, dict):
            first_accepted_state = first_present(first_run, ["value", "state"])

    orb_emissions: list[int] = []
    if isinstance(points, list):
        for index, point in enumerate(points):
            if not isinstance(point, dict):
                continue
            if point.get("state") == "Orb" or point.get("candidate_state") == "Orb":
                orb_emissions.append(index)

    return {
        "candidate_runs": len(candidate_runs) if isinstance(candidate_runs, list) else "n/a",
        "state_runs": len(state_runs) if isinstance(state_runs, list) else "n/a",
        "first_accepted_state": first_accepted_state,
        "orb_emissions_found": orb_emissions,
    }


def extract_rotational_runs(payload: dict[str, Any]) -> list[dict[str, Any]]:
    block = get_nested(payload, ["processing", "diagnostics", "rotational_persistence"], {})

    candidate_keys = [
        "cumulative_abs_heading_delta",
        "run_cumulative_abs_heading_delta",
        "abs_heading_delta_sum",
        "heading_delta_sign",
        "sign",
        "run_sign",
    ]

    records = extract_span_records(block, candidate_keys)

    # Keep only records that are plausibly runs, not unrelated windows.
    runs: list[dict[str, Any]] = []
    for record in records:
        sign = first_present(record, ["sign", "heading_delta_sign", "run_sign"])
        cumulative = first_present(
            record,
            [
                "cumulative_abs_heading_delta",
                "run_cumulative_abs_heading_delta",
                "abs_heading_delta_sum",
            ],
        )
        length = window_length(record)

        if sign is None and cumulative is None and length is None:
            continue

        runs.append(record)

    return runs


def extract_rotational_persistence(payload: dict[str, Any]) -> dict[str, Any]:
    block = get_nested(payload, ["processing", "diagnostics", "rotational_persistence"], {})
    runs = extract_rotational_runs(payload)

    aggregate_max_length = first_present(
        block if isinstance(block, dict) else {},
        ["max_same_sign_run_length", "max_same_sign_run_length_points", "max_run_length"],
    )

    aggregate_max_cumulative = first_present(
        block if isinstance(block, dict) else {},
        [
            "max_cumulative_abs_heading_delta",
            "max_same_sign_run_cumulative_abs_heading_delta",
            "max_run_cumulative_abs_heading_delta",
        ],
    )

    strongest_run, strongest_value = find_best_max(
        runs,
        [
            "cumulative_abs_heading_delta",
            "run_cumulative_abs_heading_delta",
            "abs_heading_delta_sum",
        ],
    )

    if strongest_run is None:
        strongest_run, _ = find_best_max(runs, ["length", "run_length"])

    start, end = window_span(strongest_run or {})
    length = window_length(strongest_run or {})
    sign = first_present(strongest_run or {}, ["sign", "heading_delta_sign", "run_sign"])

    return {
        "max_same_sign_run_length": aggregate_max_length if aggregate_max_length is not None else length,
        "max_same_sign_run_cumulative_abs_heading_delta": (
            aggregate_max_cumulative if aggregate_max_cumulative is not None else strongest_value
        ),
        "strongest_run_start_index": start,
        "strongest_run_end_index": end,
        "strongest_run_sign": sign,
        "run_count_with_spans": len(runs),
        "runs": runs,
    }


def extract_heading_windows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    block = get_nested(payload, ["processing", "diagnostics", "windowed_heading_sweep"], {})
    return extract_span_records(
        block,
        [
            "heading_sweep",
            "window_heading_sweep",
            "cumulative_abs_heading_delta",
            "value",
        ],
    )


def extract_windowed_heading_sweep(payload: dict[str, Any]) -> dict[str, Any]:
    block = get_nested(payload, ["processing", "diagnostics", "windowed_heading_sweep"], {})
    windows = extract_heading_windows(payload)

    best_window, best_value = find_best_max(
        windows,
        [
            "heading_sweep",
            "window_heading_sweep",
            "cumulative_abs_heading_delta",
            "value",
        ],
    )

    aggregate_max = first_present(
        block if isinstance(block, dict) else {},
        ["max_window_heading_sweep", "max_heading_sweep"],
    )

    aggregate_start = first_present(
        block if isinstance(block, dict) else {},
        ["max_window_heading_sweep_start_index", "max_heading_sweep_start_index"],
    )

    aggregate_end = first_present(
        block if isinstance(block, dict) else {},
        ["max_window_heading_sweep_end_index", "max_heading_sweep_end_index"],
    )

    start, end = window_span(best_window or {})

    return {
        "window_size_points": first_present(
            block if isinstance(block, dict) else {},
            ["window_size_points", "heading_sweep_window_size_points"],
        ),
        "max_window_heading_sweep": aggregate_max if aggregate_max is not None else best_value,
        "strongest_window_start_index": aggregate_start if aggregate_start is not None else start,
        "strongest_window_end_index": aggregate_end if aggregate_end is not None else end,
        "window_count_with_spans": len(windows),
        "windows": windows,
    }


def extract_spatial_windows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    block = get_nested(payload, ["processing", "diagnostics", "spatial_containment"], {})
    return extract_span_records(
        block,
        [
            "path_length",
            "net_displacement",
            "displacement_ratio",
            "radial_dispersion",
        ],
    )


def extract_spatial_containment(payload: dict[str, Any]) -> dict[str, Any]:
    block = get_nested(payload, ["processing", "diagnostics", "spatial_containment"], {})
    windows = extract_spatial_windows(payload)

    best_window, best_ratio = find_best_min(windows, ["displacement_ratio"])

    aggregate_min = first_present(
        block if isinstance(block, dict) else {},
        ["min_displacement_ratio", "best_displacement_ratio"],
    )

    aggregate_start = first_present(
        block if isinstance(block, dict) else {},
        ["min_displacement_ratio_start_index", "best_displacement_ratio_start_index"],
    )

    aggregate_end = first_present(
        block if isinstance(block, dict) else {},
        ["min_displacement_ratio_end_index", "best_displacement_ratio_end_index"],
    )

    start, end = window_span(best_window or {})

    return {
        "window_size_points": first_present(
            block if isinstance(block, dict) else {},
            ["window_size_points", "spatial_containment_window_size_points"],
        ),
        "min_displacement_ratio": aggregate_min if aggregate_min is not None else best_ratio,
        "corresponding_path_length": first_present(best_window or {}, ["path_length"]),
        "corresponding_net_displacement": first_present(best_window or {}, ["net_displacement"]),
        "corresponding_window_start_index": aggregate_start if aggregate_start is not None else start,
        "corresponding_window_end_index": aggregate_end if aggregate_end is not None else end,
        "window_count_with_spans": len(windows),
        "windows": windows,
    }


def extract_circle_windows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    block = get_nested(payload, ["processing", "diagnostics", "fitted_circle_coherence"], {})

    records = extract_span_records(
        block,
        [
            "fit_status",
            "status",
            "radius",
            "mean_radial_residual_ratio",
            "max_radial_residual_ratio",
        ],
    )

    fit_records: list[dict[str, Any]] = []
    for record in records:
        status = first_present(record, ["fit_status", "status"])
        if status is not None and status != "fit":
            continue

        # Keep records with actual circle-fit evidence.
        if not has_any_key(
            record,
            [
                "radius",
                "mean_radial_residual_ratio",
                "max_radial_residual_ratio",
            ],
        ):
            continue

        fit_records.append(record)

    return fit_records


def extract_fitted_circle_coherence(payload: dict[str, Any]) -> dict[str, Any]:
    block = get_nested(payload, ["processing", "diagnostics", "fitted_circle_coherence"], {})
    windows = extract_circle_windows(payload)

    all_records = extract_span_records(
        block,
        ["fit_status", "status", "radius", "mean_radial_residual_ratio", "max_radial_residual_ratio"],
    )

    fit_windows = [
        item for item in all_records if first_present(item, ["fit_status", "status"]) == "fit"
    ]
    unfit_windows = [
        item for item in all_records if first_present(item, ["fit_status", "status"]) == "unfit"
    ]

    best_window, best_mean = find_best_min(
        windows,
        ["mean_radial_residual_ratio", "full_window_mean_radial_residual_ratio"],
    )

    aggregate_best_mean = first_present(
        block if isinstance(block, dict) else {},
        ["best_full_window_mean_radial_residual_ratio"],
    )
    aggregate_best_mean_start = first_present(
        block if isinstance(block, dict) else {},
        ["best_full_window_mean_radial_residual_ratio_start_index"],
    )
    aggregate_best_mean_end = first_present(
        block if isinstance(block, dict) else {},
        ["best_full_window_mean_radial_residual_ratio_end_index"],
    )

    aggregate_best_max = first_present(
        block if isinstance(block, dict) else {},
        ["best_full_window_max_radial_residual_ratio"],
    )
    aggregate_best_max_start = first_present(
        block if isinstance(block, dict) else {},
        ["best_full_window_max_radial_residual_ratio_start_index"],
    )
    aggregate_best_max_end = first_present(
        block if isinstance(block, dict) else {},
        ["best_full_window_max_radial_residual_ratio_end_index"],
    )

    start, end = window_span(best_window or {})

    return {
        "window_size_points": first_present(
            block if isinstance(block, dict) else {},
            ["window_size_points", "fitted_circle_window_size_points"],
        ),
        "fit_window_count": first_present(
            block if isinstance(block, dict) else {},
            ["fit_window_count"],
            len(fit_windows),
        ),
        "unfit_window_count": first_present(
            block if isinstance(block, dict) else {},
            ["unfit_window_count"],
            len(unfit_windows),
        ),
        "best_full_window_mean_radial_residual_ratio": (
            aggregate_best_mean if aggregate_best_mean is not None else best_mean
        ),
        "best_full_window_max_radial_residual_ratio": aggregate_best_max,
        "corresponding_full_window_start_index": (
            aggregate_best_mean_start if aggregate_best_mean_start is not None else start
        ),
        "corresponding_full_window_end_index": (
            aggregate_best_mean_end if aggregate_best_mean_end is not None else end
        ),
        "best_max_ratio_window_start_index": aggregate_best_max_start,
        "best_max_ratio_window_end_index": aggregate_best_max_end,
        "window_count_with_spans": len(windows),
        "windows": windows,
    }


def same_span(a_start: Any, a_end: Any, b_start: Any, b_end: Any) -> bool:
    return (
        a_start is not None
        and a_end is not None
        and b_start is not None
        and b_end is not None
        and a_start == b_start
        and a_end == b_end
    )


def span_inside(inner_start: Any, inner_end: Any, outer_start: Any, outer_end: Any) -> Optional[bool]:
    if None in [inner_start, inner_end, outer_start, outer_end]:
        return None
    return int(inner_start) >= int(outer_start) and int(inner_end) <= int(outer_end)


def build_span_map(
    records: list[dict[str, Any]],
    value_keys: list[str],
    mode: str,
) -> dict[tuple[int, int], dict[str, Any]]:
    """
    Builds a map keyed by (start_index, end_index).

    If duplicate records exist for a span, keeps:
    - max value for mode='max'
    - min value for mode='min'
    - first usable record for mode='first'
    """
    span_map: dict[tuple[int, int], dict[str, Any]] = {}

    for record in records:
        start, end = window_span(record)
        if start is None or end is None:
            continue

        span = (start, end)

        if span not in span_map:
            span_map[span] = record
            continue

        if mode == "first":
            continue

        current_value = as_number(first_present(span_map[span], value_keys))
        new_value = as_number(first_present(record, value_keys))

        if new_value is None:
            continue

        if current_value is None:
            span_map[span] = record
            continue

        if mode == "max" and new_value > current_value:
            span_map[span] = record
        elif mode == "min" and new_value < current_value:
            span_map[span] = record

    return span_map


def record_value(record: dict[str, Any], keys: list[str]) -> Any:
    return first_present(record, keys)


def find_containing_rotational_runs(
    start_index: int,
    end_index: int,
    rotational_runs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    containing: list[dict[str, Any]] = []

    for run in rotational_runs:
        run_start, run_end = window_span(run)
        if run_start is None or run_end is None:
            continue

        if span_inside(start_index, end_index, run_start, run_end):
            containing.append(run)

    return containing


def build_shared_window_rows(
    heading_windows: list[dict[str, Any]],
    spatial_windows: list[dict[str, Any]],
    circle_windows: list[dict[str, Any]],
    rotational_runs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    heading_by_span = build_span_map(
        heading_windows,
        ["heading_sweep", "window_heading_sweep", "cumulative_abs_heading_delta", "value"],
        mode="max",
    )

    spatial_by_span = build_span_map(
        spatial_windows,
        ["displacement_ratio"],
        mode="min",
    )

    circle_by_span = build_span_map(
        circle_windows,
        ["mean_radial_residual_ratio", "full_window_mean_radial_residual_ratio"],
        mode="min",
    )

    shared_spans = sorted(
        set(heading_by_span.keys())
        & set(spatial_by_span.keys())
        & set(circle_by_span.keys())
    )

    rows: list[dict[str, Any]] = []

    for start, end in shared_spans:
        heading = heading_by_span[(start, end)]
        spatial = spatial_by_span[(start, end)]
        circle = circle_by_span[(start, end)]
        containing_runs = find_containing_rotational_runs(start, end, rotational_runs)

        if containing_runs:
            inside_rotational_run: Any = True
            best_run = containing_runs[0]
        elif rotational_runs:
            inside_rotational_run = False
            best_run = None
        else:
            inside_rotational_run = "n/a"
            best_run = None

        row = {
            "start_index": start,
            "end_index": end,
            "length": end - start + 1,
            "heading_sweep": record_value(
                heading,
                ["heading_sweep", "window_heading_sweep", "cumulative_abs_heading_delta", "value"],
            ),
            "path_length": record_value(spatial, ["path_length"]),
            "net_displacement": record_value(spatial, ["net_displacement"]),
            "displacement_ratio": record_value(spatial, ["displacement_ratio"]),
            "mean_radial_residual_ratio": record_value(
                circle,
                ["mean_radial_residual_ratio", "full_window_mean_radial_residual_ratio"],
            ),
            "max_radial_residual_ratio": record_value(
                circle,
                ["max_radial_residual_ratio", "full_window_max_radial_residual_ratio"],
            ),
            "circle_radius": record_value(circle, ["radius"]),
            "inside_rotational_run": inside_rotational_run,
            "rotational_run_start_index": None,
            "rotational_run_end_index": None,
            "rotational_run_sign": None,
            "rotational_run_cumulative_abs_heading_delta": None,
        }

        if best_run is not None:
            run_start, run_end = window_span(best_run)
            row["rotational_run_start_index"] = run_start
            row["rotational_run_end_index"] = run_end
            row["rotational_run_sign"] = first_present(best_run, ["sign", "heading_delta_sign", "run_sign"])
            row["rotational_run_cumulative_abs_heading_delta"] = first_present(
                best_run,
                [
                    "cumulative_abs_heading_delta",
                    "run_cumulative_abs_heading_delta",
                    "abs_heading_delta_sum",
                ],
            )

        rows.append(row)

    return rows


def analyze_anchor(path: Path) -> dict[str, Any]:
    payload = load_json(path)

    state = extract_existing_state_behavior(payload)
    rotational = extract_rotational_persistence(payload)
    heading = extract_windowed_heading_sweep(payload)
    spatial = extract_spatial_containment(payload)
    circle = extract_fitted_circle_coherence(payload)

    heading_matches_spatial = same_span(
        heading["strongest_window_start_index"],
        heading["strongest_window_end_index"],
        spatial["corresponding_window_start_index"],
        spatial["corresponding_window_end_index"],
    )

    heading_matches_circle = same_span(
        heading["strongest_window_start_index"],
        heading["strongest_window_end_index"],
        circle["corresponding_full_window_start_index"],
        circle["corresponding_full_window_end_index"],
    )

    same_window_match = heading_matches_spatial and heading_matches_circle

    shared_inside_rotational_run = None
    if same_window_match:
        shared_inside_rotational_run = span_inside(
            heading["strongest_window_start_index"],
            heading["strongest_window_end_index"],
            rotational["strongest_run_start_index"],
            rotational["strongest_run_end_index"],
        )

    shared_window_rows = build_shared_window_rows(
        heading["windows"],
        spatial["windows"],
        circle["windows"],
        rotational["runs"],
    )

    return {
        "anchor_name": path.name,
        "path": str(path),
        "state": state,
        "rotational": rotational,
        "heading": heading,
        "spatial": spatial,
        "circle": circle,
        "same_window": {
            "heading_matches_spatial": heading_matches_spatial,
            "heading_matches_circle": heading_matches_circle,
            "same_window_match": same_window_match,
            "shared_window_inside_strongest_rotational_run": shared_inside_rotational_run,
        },
        "shared_window_rows": shared_window_rows,
    }


def likely_expected_support(anchor_name: str) -> str:
    lower = anchor_name.lower()
    if "hover" in lower:
        return "withheld"
    if "turn" in lower and "orb_like" not in lower:
        return "withheld"
    if "orb_like" in lower:
        return "accepted if clean; final state remains unchanged"
    if "39406" in lower or "uci" in lower:
        return "withheld / manual review if any support appears"
    return "review"


def render_shared_window_table(rows: list[dict[str, Any]], max_rows: int) -> str:
    if not rows:
        return "\n".join(
            [
                "### Shared diagnostic windows",
                "",
                "No shared start_index/end_index windows were found across heading sweep, spatial containment, and fitted-circle coherence.",
                "",
            ]
        )

    visible_rows = rows[:max_rows]
    truncated = len(rows) > max_rows

    lines = [
        "### Shared diagnostic windows",
        "",
        (
            "| Window | heading_sweep | path_length | displacement_ratio | "
            "mean_radial_residual_ratio | max_radial_residual_ratio | inside_rotational_run | rotational_run |"
        ),
        "|---|---:|---:|---:|---:|---:|---|---|",
    ]

    for row in visible_rows:
        window = f"{row['start_index']}–{row['end_index']}"
        rotational_run = "n/a"
        if row["rotational_run_start_index"] is not None and row["rotational_run_end_index"] is not None:
            rotational_run = f"{row['rotational_run_start_index']}–{row['rotational_run_end_index']}"

        lines.append(
            f"| {window} "
            f"| {fmt(row['heading_sweep'])} "
            f"| {fmt(row['path_length'])} "
            f"| {fmt(row['displacement_ratio'])} "
            f"| {fmt(row['mean_radial_residual_ratio'])} "
            f"| {fmt(row['max_radial_residual_ratio'])} "
            f"| {fmt(row['inside_rotational_run'])} "
            f"| {rotational_run} |"
        )

    if truncated:
        lines.extend(
            [
                "",
                f"_Showing first {max_rows} shared windows out of {len(rows)}._",
            ]
        )
    else:
        lines.extend(
            [
                "",
                f"_Shared window count: {len(rows)}._",
            ]
        )

    lines.append("")
    return "\n".join(lines)

def number_or_none(value: Any) -> Optional[float]:
    return as_number(value)


def sort_lowest_displacement(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            number_or_none(row.get("displacement_ratio")) is None,
            number_or_none(row.get("displacement_ratio")) if number_or_none(row.get("displacement_ratio")) is not None else float("inf"),
        ),
    )


def sort_highest_heading_sweep(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            number_or_none(row.get("heading_sweep")) is None,
            -(number_or_none(row.get("heading_sweep")) or 0.0),
        ),
    )


def sort_best_circle_coherence(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            number_or_none(row.get("mean_radial_residual_ratio")) is None,
            number_or_none(row.get("mean_radial_residual_ratio"))
            if number_or_none(row.get("mean_radial_residual_ratio")) is not None
            else float("inf"),
            number_or_none(row.get("max_radial_residual_ratio"))
            if number_or_none(row.get("max_radial_residual_ratio")) is not None
            else float("inf"),
        ),
    )


def sort_preliminary_combined_screen(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Review-only sort.

    This does NOT declare Orb support.
    It simply brings the most Orb-adjacent shared windows toward the top by preferring:
    - windows inside a rotational-persistence run
    - higher heading sweep
    - lower displacement ratio
    - lower mean radial residual ratio
    - lower max radial residual ratio
    """
    return sorted(
        rows,
        key=lambda row: (
            row.get("inside_rotational_run") is not True,
            -(number_or_none(row.get("heading_sweep")) or 0.0),
            number_or_none(row.get("displacement_ratio"))
            if number_or_none(row.get("displacement_ratio")) is not None
            else float("inf"),
            number_or_none(row.get("mean_radial_residual_ratio"))
            if number_or_none(row.get("mean_radial_residual_ratio")) is not None
            else float("inf"),
            number_or_none(row.get("max_radial_residual_ratio"))
            if number_or_none(row.get("max_radial_residual_ratio")) is not None
            else float("inf"),
        ),
    )

def evaluate_threshold_probe_for_row(
    row: dict[str, Any],
    probe: dict[str, Any],
) -> dict[str, Any]:
    thresholds = probe["thresholds"]
    failed_reasons: list[str] = []

    if row.get("inside_rotational_run") is not True:
        failed_reasons.append("not_inside_rotational_run")

    rotational_run_start = row.get("rotational_run_start_index")
    rotational_run_end = row.get("rotational_run_end_index")
    rotational_run_length = None
    if rotational_run_start is not None and rotational_run_end is not None:
        rotational_run_length = int(rotational_run_end) - int(rotational_run_start) + 1

    if rotational_run_length is None:
        failed_reasons.append("missing_rotational_run_length")
    elif rotational_run_length < thresholds["min_rotational_run_length_points"]:
        failed_reasons.append("insufficient_rotational_run_length")

    rotational_delta = number_or_none(row.get("rotational_run_cumulative_abs_heading_delta"))
    if rotational_delta is None:
        failed_reasons.append("missing_rotational_run_cumulative_abs_heading_delta")
    elif rotational_delta < thresholds["min_rotational_run_cumulative_abs_heading_delta"]:
        failed_reasons.append("insufficient_rotational_run_cumulative_abs_heading_delta")

    heading_sweep = number_or_none(row.get("heading_sweep"))
    if heading_sweep is None:
        failed_reasons.append("missing_heading_sweep")
    elif heading_sweep < thresholds["min_window_heading_sweep"]:
        failed_reasons.append("insufficient_heading_sweep")

    path_length = number_or_none(row.get("path_length"))
    if path_length is None:
        failed_reasons.append("missing_path_length")
    elif path_length < thresholds["min_path_length"]:
        failed_reasons.append("insufficient_path_length")

    displacement_ratio = number_or_none(row.get("displacement_ratio"))
    if displacement_ratio is None:
        failed_reasons.append("missing_displacement_ratio")
    elif displacement_ratio > thresholds["max_displacement_ratio"]:
        failed_reasons.append("insufficient_spatial_containment")

    mean_residual_ratio = number_or_none(row.get("mean_radial_residual_ratio"))
    if mean_residual_ratio is None:
        failed_reasons.append("missing_mean_radial_residual_ratio")
    elif mean_residual_ratio > thresholds["max_mean_radial_residual_ratio"]:
        failed_reasons.append("insufficient_mean_circle_coherence")

    max_residual_ratio = number_or_none(row.get("max_radial_residual_ratio"))
    if max_residual_ratio is None:
        failed_reasons.append("missing_max_radial_residual_ratio")
    elif max_residual_ratio > thresholds["max_max_radial_residual_ratio"]:
        failed_reasons.append("insufficient_max_circle_coherence")

    return {
        "would_pass_threshold_screen": len(failed_reasons) == 0,
        "failed_threshold_reasons": failed_reasons,
    }


def apply_threshold_probe_to_rows(
    rows: list[dict[str, Any]],
    probe_name: str,
) -> list[dict[str, Any]]:
    probe = THRESHOLD_PROBES[probe_name]
    screened_rows: list[dict[str, Any]] = []

    for row in rows:
        screened_row = dict(row)
        screened_row["threshold_probe"] = probe_name
        screened_row.update(evaluate_threshold_probe_for_row(row, probe))
        screened_rows.append(screened_row)

    return screened_rows


def sort_threshold_screen_passes_first(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        rows,
        key=lambda row: (
            row.get("would_pass_threshold_screen") is not True,
            -(number_or_none(row.get("heading_sweep")) or 0.0),
            number_or_none(row.get("displacement_ratio"))
            if number_or_none(row.get("displacement_ratio")) is not None
            else float("inf"),
            number_or_none(row.get("mean_radial_residual_ratio"))
            if number_or_none(row.get("mean_radial_residual_ratio")) is not None
            else float("inf"),
        ),
    )


def render_ranked_rows_table(
    title: str,
    rows: list[dict[str, Any]],
    max_rows: int,
) -> str:
    if not rows:
        return "\n".join(
            [
                f"#### {title}",
                "",
                "No shared windows available for this ranking.",
                "",
            ]
        )

    visible_rows = rows[:max_rows]

    lines = [
        f"#### {title}",
        "",
        (
            "| Rank | Window | heading_sweep | path_length | displacement_ratio | "
            "mean_radial_residual_ratio | max_radial_residual_ratio | inside_rotational_run | rotational_run |"
        ),
        "|---:|---|---:|---:|---:|---:|---:|---|---|",
    ]

    for rank, row in enumerate(visible_rows, start=1):
        window = f"{row['start_index']}–{row['end_index']}"
        rotational_run = "n/a"
        if row["rotational_run_start_index"] is not None and row["rotational_run_end_index"] is not None:
            rotational_run = f"{row['rotational_run_start_index']}–{row['rotational_run_end_index']}"

        lines.append(
            f"| {rank} "
            f"| {window} "
            f"| {fmt(row['heading_sweep'])} "
            f"| {fmt(row['path_length'])} "
            f"| {fmt(row['displacement_ratio'])} "
            f"| {fmt(row['mean_radial_residual_ratio'])} "
            f"| {fmt(row['max_radial_residual_ratio'])} "
            f"| {fmt(row['inside_rotational_run'])} "
            f"| {rotational_run} |"
        )

    lines.append("")
    return "\n".join(lines)


def render_ranked_shared_window_summary(
    rows: list[dict[str, Any]],
    max_rows: int,
) -> str:
    lines = [
        "### Ranked shared-window summary",
        "",
        "These rankings are review-only. They do not declare Orb support.",
        "",
        render_ranked_rows_table(
            "Lowest displacement_ratio windows",
            sort_lowest_displacement(rows),
            max_rows,
        ),
        render_ranked_rows_table(
            "Highest heading_sweep windows",
            sort_highest_heading_sweep(rows),
            max_rows,
        ),
        render_ranked_rows_table(
            "Best circle-coherence windows",
            sort_best_circle_coherence(rows),
            max_rows,
        ),
        render_ranked_rows_table(
            "Best preliminary combined screen",
            sort_preliminary_combined_screen(rows),
            max_rows,
        ),
    ]

    return "\n".join(lines)

def render_threshold_probe_summary(
    rows: list[dict[str, Any]],
    probe_name: str,
    max_rows: int,
) -> str:
    probe = THRESHOLD_PROBES[probe_name]
    screened_rows = apply_threshold_probe_to_rows(rows, probe_name)
    passing_rows = [
        row for row in screened_rows if row.get("would_pass_threshold_screen") is True
    ]
    ranked_rows = sort_threshold_screen_passes_first(screened_rows)[:max_rows]

    lines = [
        "### Threshold probe summary",
        "",
        f"- probe_name: `{probe_name}`",
        f"- status: {probe['metadata']['status']}",
        f"- basis: {probe['metadata']['basis']}",
        f"- emission_posture: {probe['metadata']['emission_posture']}",
        f"- validation_maturity: {probe['metadata']['validation_maturity']}",
        f"- passing_shared_window_count: {len(passing_rows)}",
        "",
        "#### Threshold values",
        "",
        "| Threshold | Value |",
        "|---|---:|",
    ]

    for key, value in probe["thresholds"].items():
        lines.append(f"| {key} | {fmt(value)} |")

    lines.extend(
        [
            "",
            "#### Threshold-screen ranked rows",
            "",
            (
                "| Rank | Window | pass | failed_threshold_reasons | heading_sweep | "
                "path_length | displacement_ratio | mean_radial_residual_ratio | "
                "max_radial_residual_ratio | inside_rotational_run | rotational_run |"
            ),
            "|---:|---|---|---|---:|---:|---:|---:|---:|---|---|",
        ]
    )

    if not ranked_rows:
        lines.append("| n/a | n/a | n/a | no_shared_windows | n/a | n/a | n/a | n/a | n/a | n/a | n/a |")
    else:
        for rank, row in enumerate(ranked_rows, start=1):
            window = f"{row['start_index']}–{row['end_index']}"
            rotational_run = "n/a"
            if row["rotational_run_start_index"] is not None and row["rotational_run_end_index"] is not None:
                rotational_run = f"{row['rotational_run_start_index']}–{row['rotational_run_end_index']}"

            failed_reasons = row.get("failed_threshold_reasons", [])
            failed_reasons_text = ", ".join(failed_reasons) if failed_reasons else "[]"

            lines.append(
                f"| {rank} "
                f"| {window} "
                f"| {row.get('would_pass_threshold_screen')} "
                f"| {failed_reasons_text} "
                f"| {fmt(row.get('heading_sweep'))} "
                f"| {fmt(row.get('path_length'))} "
                f"| {fmt(row.get('displacement_ratio'))} "
                f"| {fmt(row.get('mean_radial_residual_ratio'))} "
                f"| {fmt(row.get('max_radial_residual_ratio'))} "
                f"| {fmt(row.get('inside_rotational_run'))} "
                f"| {rotational_run} |"
            )

    lines.append("")
    return "\n".join(lines)


def render_anchor_markdown(
    result: dict[str, Any],
    max_shared_rows: int,
    max_ranked_rows: int,
) -> str:
    name = result["anchor_name"]
    state = result["state"]
    rotational = result["rotational"]
    heading = result["heading"]
    spatial = result["spatial"]
    circle = result["circle"]
    same = result["same_window"]

    orb_emissions = state["orb_emissions_found"]
    orb_emissions_text = "[]" if not orb_emissions else str(orb_emissions)

    lines = [
        f"## Anchor: {name}",
        "",
        "### Existing state behavior",
        f"- candidate_runs: {fmt(state['candidate_runs'])}",
        f"- state_runs: {fmt(state['state_runs'])}",
        f"- first accepted state: {fmt(state['first_accepted_state'])}",
        f"- Orb emissions found: {orb_emissions_text}",
        "",
        "### Rotational persistence",
        f"- max_same_sign_run_length: {fmt(rotational['max_same_sign_run_length'])}",
        (
            "- max_same_sign_run_cumulative_abs_heading_delta: "
            f"{fmt(rotational['max_same_sign_run_cumulative_abs_heading_delta'])}"
        ),
        f"- strongest run start_index: {fmt(rotational['strongest_run_start_index'])}",
        f"- strongest run end_index: {fmt(rotational['strongest_run_end_index'])}",
        f"- strongest run sign: {fmt(rotational['strongest_run_sign'])}",
        f"- run_count_with_spans: {fmt(rotational['run_count_with_spans'])}",
        "",
        "### Windowed heading sweep",
        f"- window_size_points: {fmt(heading['window_size_points'])}",
        f"- max_window_heading_sweep: {fmt(heading['max_window_heading_sweep'])}",
        f"- strongest window start_index: {fmt(heading['strongest_window_start_index'])}",
        f"- strongest window end_index: {fmt(heading['strongest_window_end_index'])}",
        f"- window_count_with_spans: {fmt(heading['window_count_with_spans'])}",
        "",
        "### Spatial containment",
        f"- window_size_points: {fmt(spatial['window_size_points'])}",
        f"- min_displacement_ratio: {fmt(spatial['min_displacement_ratio'])}",
        f"- corresponding path_length: {fmt(spatial['corresponding_path_length'])}",
        f"- corresponding net_displacement: {fmt(spatial['corresponding_net_displacement'])}",
        f"- corresponding window start_index: {fmt(spatial['corresponding_window_start_index'])}",
        f"- corresponding window end_index: {fmt(spatial['corresponding_window_end_index'])}",
        f"- window_count_with_spans: {fmt(spatial['window_count_with_spans'])}",
        "",
        "### Fitted-circle coherence",
        f"- window_size_points: {fmt(circle['window_size_points'])}",
        f"- fit_window_count: {fmt(circle['fit_window_count'])}",
        f"- unfit_window_count: {fmt(circle['unfit_window_count'])}",
        f"- window_count_with_spans: {fmt(circle['window_count_with_spans'])}",
        (
            "- best_full_window_mean_radial_residual_ratio: "
            f"{fmt(circle['best_full_window_mean_radial_residual_ratio'])}"
        ),
        (
            "- best_full_window_max_radial_residual_ratio: "
            f"{fmt(circle['best_full_window_max_radial_residual_ratio'])}"
        ),
        (
            "- corresponding full-window start_index: "
            f"{fmt(circle['corresponding_full_window_start_index'])}"
        ),
        (
            "- corresponding full-window end_index: "
            f"{fmt(circle['corresponding_full_window_end_index'])}"
        ),
        "",
        "### Strongest-window overlap check",
        f"- Does the strongest heading-sweep window match the strongest containment window? {same['heading_matches_spatial']}",
        f"- Does it match the strongest fitted-circle window? {same['heading_matches_circle']}",
        (
            "- Does the shared strongest window lie inside the strongest rotational-persistence run? "
            f"{same['shared_window_inside_strongest_rotational_run']}"
        ),
        f"- Same-window match across strongest heading/containment/circle windows: {same['same_window_match']}",
        "",
        render_shared_window_table(result["shared_window_rows"], max_shared_rows),
        render_ranked_shared_window_summary(result["shared_window_rows"], max_ranked_rows),
        render_threshold_probe_summary(
            result["shared_window_rows"],
            probe_name="orb_candidate_support_thresholds_conservative_probe_v0",
            max_rows=max_ranked_rows,
        ),
        "### Expected Orb support result",
        f"- expected: {likely_expected_support(name)}",
        "- likely withheld reason(s): review after threshold selection",
        "- notes:",
        "",
    ]

    return "\n".join(lines)


def render_comparison_table(results: list[dict[str, Any]]) -> str:
    lines = [
        "## Compact comparison table",
        "",
        (
            "| Anchor | Rotational persistence | Heading sweep | Containment | "
            "Circle coherence | Strongest-window overlap | Shared windows | Expected support |"
        ),
        "|---|---:|---:|---:|---:|---|---:|---|",
    ]

    for result in results:
        name = result["anchor_name"]
        rotational = result["rotational"]
        heading = result["heading"]
        spatial = result["spatial"]
        circle = result["circle"]
        same = result["same_window"]
        shared_rows = result["shared_window_rows"]

        rotational_value = fmt(rotational["max_same_sign_run_cumulative_abs_heading_delta"])
        heading_value = fmt(heading["max_window_heading_sweep"])
        containment_value = fmt(spatial["min_displacement_ratio"])
        circle_value = fmt(circle["best_full_window_mean_radial_residual_ratio"])
        overlap_value = str(same["same_window_match"])
        shared_count = str(len(shared_rows))
        expected = likely_expected_support(name)

        lines.append(
            f"| {name} | {rotational_value} | {heading_value} | "
            f"{containment_value} | {circle_value} | {overlap_value} | {shared_count} | {expected} |"
        )

    return "\n".join(lines)


def render_markdown(
    results: list[dict[str, Any]],
    max_shared_rows: int,
    max_ranked_rows: int,
) -> str:
    sections = [
        "# PC-MAW / Constructor v0 — Orb Anchor Diagnostic Review",
        "",
        "This worksheet is generated from existing Constructor v0 output JSON files.",
        "",
        "No constructor behavior is modified by this review.",
        "",
        "The shared-window tables list windows where heading sweep, spatial containment, and fitted-circle coherence share the same start_index/end_index.",
        "",
        "The ranked shared-window summaries are review-only and do not declare Orb support.",
        "",
        render_comparison_table(results),
        "",
    ]

    for result in results:
        sections.append(
            render_anchor_markdown(
                result,
                max_shared_rows=max_shared_rows,
                max_ranked_rows=max_ranked_rows,
            )
        )

    return "\n".join(sections)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract Orb-adjacent diagnostic worksheet data from Constructor v0 anchor outputs."
    )

    parser.add_argument(
        "--output-dir",
        default="state_constructor/output",
        help="Directory containing Constructor v0 output JSON files.",
    )

    parser.add_argument(
        "--anchors",
        nargs="*",
        default=DEFAULT_ANCHORS,
        help="Anchor JSON filenames to review.",
    )

    parser.add_argument(
        "--write-markdown",
        default="state_constructor/output/orb_anchor_diagnostic_review.md",
        help="Path for the generated Markdown review file.",
    )

    parser.add_argument(
        "--max-shared-rows",
        type=int,
        default=40,
        help="Maximum shared diagnostic windows to print per anchor in the Markdown output.",
    )

    parser.add_argument(
        "--max-ranked-rows",
        type=int,
        default=8,
        help="Maximum ranked shared-window rows to print per ranking section.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    output_dir = Path(args.output_dir)
    anchor_paths = [output_dir / anchor for anchor in args.anchors]

    missing = [path for path in anchor_paths if not path.exists()]
    if missing:
        print("Missing expected anchor output file(s):")
        for path in missing:
            print(f"  - {path}")
        raise SystemExit(1)

    results = [analyze_anchor(path) for path in anchor_paths]
    markdown = render_markdown(
    results,
    max_shared_rows=args.max_shared_rows,
    max_ranked_rows=args.max_ranked_rows,
)

    write_path = Path(args.write_markdown)
    write_path.parent.mkdir(parents=True, exist_ok=True)
    write_path.write_text(markdown, encoding="utf-8")

    print(markdown)
    print("")
    print(f"Wrote Markdown review to: {write_path}")


if __name__ == "__main__":
    main()