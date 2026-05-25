"""
Support logic helpers for Constructor v0.

This module evaluates higher-level support evidence across already-derived
diagnostic families.

Boundary:
- Does not compute raw geometry.
- Does not assign candidate_state.
- Does not assign final state.
- Does not modify run_summary.
- Does not emit Orb as a state.

Current use:
- Diagnostic-only Orb candidate support under processing.diagnostics.
"""

from __future__ import annotations

from typing import Any, Optional


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


def first_present(mapping: dict[str, Any], keys: list[str], default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


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


def window_length_from_span(start_index: int, end_index: int) -> int:
    return end_index - start_index + 1


def window_length(item: dict[str, Any]) -> Optional[int]:
    explicit = as_int(first_present(item, ["length", "window_length", "window_size_points"]))
    if explicit is not None:
        return explicit

    start, end = window_span(item)
    if start is not None and end is not None and end >= start:
        return window_length_from_span(start, end)

    return None


def has_any_key(item: dict[str, Any], keys: list[str]) -> bool:
    return any(key in item for key in keys)


def extract_span_records(block: Any, required_value_keys: list[str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    for item in recursive_dicts(block):
        start, end = window_span(item)
        if start is None or end is None:
            continue
        if not has_any_key(item, required_value_keys):
            continue
        records.append(item)

    return records


def extract_rotational_runs(rotational_persistence: dict[str, Any]) -> list[dict[str, Any]]:
    records = extract_span_records(
        rotational_persistence,
        [
            "cumulative_abs_heading_delta",
            "run_cumulative_abs_heading_delta",
            "abs_heading_delta_sum",
            "heading_delta_sign",
            "sign",
            "run_sign",
        ],
    )

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


def extract_heading_windows(windowed_heading_sweep: dict[str, Any]) -> list[dict[str, Any]]:
    return extract_span_records(
        windowed_heading_sweep,
        [
            "heading_sweep",
            "window_heading_sweep",
            "cumulative_abs_heading_delta",
            "value",
        ],
    )


def extract_spatial_windows(spatial_containment: dict[str, Any]) -> list[dict[str, Any]]:
    return extract_span_records(
        spatial_containment,
        [
            "path_length",
            "net_displacement",
            "displacement_ratio",
            "radial_dispersion",
        ],
    )


def extract_circle_windows(fitted_circle_coherence: dict[str, Any]) -> list[dict[str, Any]]:
    records = extract_span_records(
        fitted_circle_coherence,
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


def build_span_map(
    records: list[dict[str, Any]],
    value_keys: list[str],
    mode: str,
) -> dict[tuple[int, int], dict[str, Any]]:
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


def span_inside(inner_start: int, inner_end: int, outer_start: int, outer_end: int) -> bool:
    return inner_start >= outer_start and inner_end <= outer_end


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


def is_hover_dominated_window(
    *,
    points: list[dict[str, Any]],
    start_index: int,
    end_index: int,
) -> bool:
    window_points = points[start_index : end_index + 1]
    if not window_points:
        return False

    hover_count = 0
    for point in window_points:
        if point.get("candidate_state") == "Hover" or point.get("state") == "Hover":
            hover_count += 1

    return hover_count > (len(window_points) / 2)


def get_rotational_run_cumulative_abs_heading_delta(run: dict[str, Any]) -> Optional[float]:
    return as_number(
        first_present(
            run,
            [
                "cumulative_abs_heading_delta",
                "run_cumulative_abs_heading_delta",
                "abs_heading_delta_sum",
            ],
        )
    )


def get_rotational_run_sign(run: dict[str, Any]) -> Any:
    return first_present(run, ["sign", "heading_delta_sign", "run_sign"])


def build_shared_window_rows(
    *,
    rotational_runs: list[dict[str, Any]],
    heading_windows: list[dict[str, Any]],
    spatial_windows: list[dict[str, Any]],
    circle_windows: list[dict[str, Any]],
    points: list[dict[str, Any]],
    exclude_hover_dominated_windows: bool,
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
        best_run = containing_runs[0] if containing_runs else None

        hover_dominated = False
        if exclude_hover_dominated_windows:
            hover_dominated = is_hover_dominated_window(
                points=points,
                start_index=start,
                end_index=end,
            )

        row: dict[str, Any] = {
            "start_index": start,
            "end_index": end,
            "length": window_length_from_span(start, end),
            "heading_sweep": first_present(
                heading,
                ["heading_sweep", "window_heading_sweep", "cumulative_abs_heading_delta", "value"],
            ),
            "path_length": first_present(spatial, ["path_length"]),
            "net_displacement": first_present(spatial, ["net_displacement"]),
            "displacement_ratio": first_present(spatial, ["displacement_ratio"]),
            "radial_dispersion": first_present(spatial, ["radial_dispersion"]),
            "circle_radius": first_present(circle, ["radius"]),
            "mean_radial_residual_ratio": first_present(
                circle,
                ["mean_radial_residual_ratio", "full_window_mean_radial_residual_ratio"],
            ),
            "max_radial_residual_ratio": first_present(
                circle,
                ["max_radial_residual_ratio", "full_window_max_radial_residual_ratio"],
            ),
            "inside_rotational_run": best_run is not None,
            "hover_dominated": hover_dominated,
            "rotational_run": None,
        }

        if best_run is not None:
            run_start, run_end = window_span(best_run)
            if run_start is not None and run_end is not None:
                row["rotational_run"] = {
                    "start_index": run_start,
                    "end_index": run_end,
                    "length": window_length_from_span(run_start, run_end),
                    "sign": get_rotational_run_sign(best_run),
                    "cumulative_abs_heading_delta": (
                        get_rotational_run_cumulative_abs_heading_delta(best_run)
                    ),
                }

        rows.append(row)

    return rows


def evaluate_row_against_config(
    row: dict[str, Any],
    config: dict[str, Any],
) -> list[str]:
    failed_reasons: list[str] = []

    if row.get("hover_dominated") is True:
        failed_reasons.append("hover_dominated")

    rotational_run = row.get("rotational_run")
    if not isinstance(rotational_run, dict):
        failed_reasons.append("no_window_inside_qualifying_rotational_run")
        failed_reasons.append("no_qualifying_rotational_persistence")
    else:
        rotational_run_length = as_int(rotational_run.get("length"))
        rotational_delta = as_number(rotational_run.get("cumulative_abs_heading_delta"))

        min_rotational_run_length = as_int(
            config.get("min_rotational_run_length_points")
        )
        min_rotational_delta = as_number(
            config.get("min_rotational_run_cumulative_abs_heading_delta")
        )

        if min_rotational_run_length is not None:
            if rotational_run_length is None or rotational_run_length < min_rotational_run_length:
                failed_reasons.append("no_qualifying_rotational_persistence")

        if min_rotational_delta is not None:
            if rotational_delta is None or rotational_delta < min_rotational_delta:
                failed_reasons.append("no_qualifying_rotational_persistence")

    heading_sweep = as_number(row.get("heading_sweep"))
    min_heading_sweep = as_number(config.get("min_window_heading_sweep"))
    if min_heading_sweep is not None:
        if heading_sweep is None or heading_sweep < min_heading_sweep:
            failed_reasons.append("insufficient_heading_sweep")

    path_length = as_number(row.get("path_length"))
    min_path_length = as_number(config.get("min_path_length"))
    if min_path_length is not None:
        if path_length is None or path_length < min_path_length:
            failed_reasons.append("insufficient_path_length")

    displacement_ratio = as_number(row.get("displacement_ratio"))
    max_displacement_ratio = as_number(config.get("max_displacement_ratio"))
    if max_displacement_ratio is not None:
        if displacement_ratio is None or displacement_ratio > max_displacement_ratio:
            failed_reasons.append("insufficient_spatial_containment")

    mean_residual_ratio = as_number(row.get("mean_radial_residual_ratio"))
    max_mean_residual_ratio = as_number(config.get("max_mean_radial_residual_ratio"))
    if max_mean_residual_ratio is not None:
        if mean_residual_ratio is None or mean_residual_ratio > max_mean_residual_ratio:
            failed_reasons.append("insufficient_circle_coherence")

    max_residual_ratio = as_number(row.get("max_radial_residual_ratio"))
    max_max_residual_ratio = as_number(config.get("max_max_radial_residual_ratio"))
    if max_max_residual_ratio is not None:
        if max_residual_ratio is None or max_residual_ratio > max_max_residual_ratio:
            failed_reasons.append("insufficient_circle_coherence")

    return list(dict.fromkeys(failed_reasons))


def support_window_from_row(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "start_index": row["start_index"],
        "end_index": row["end_index"],
        "length": row["length"],
        "rotational_run": row["rotational_run"],
        "heading_sweep": {
            "value": row.get("heading_sweep"),
        },
        "spatial_containment": {
            "path_length": row.get("path_length"),
            "net_displacement": row.get("net_displacement"),
            "displacement_ratio": row.get("displacement_ratio"),
            "radial_dispersion": row.get("radial_dispersion"),
        },
        "fitted_circle_coherence": {
            "radius": row.get("circle_radius"),
            "mean_radial_residual_ratio": row.get("mean_radial_residual_ratio"),
            "max_radial_residual_ratio": row.get("max_radial_residual_ratio"),
        },
        "support_status": "accepted",
        "withheld_reasons": [],
    }


def summarize_withheld_reasons(
    *,
    rotational_runs: list[dict[str, Any]],
    heading_windows: list[dict[str, Any]],
    spatial_windows: list[dict[str, Any]],
    circle_windows: list[dict[str, Any]],
    shared_window_rows: list[dict[str, Any]],
    row_failure_reasons: list[str],
) -> list[str]:
    reasons: list[str] = []

    if not rotational_runs:
        reasons.append("no_qualifying_rotational_persistence")

    if not heading_windows or not spatial_windows or not circle_windows:
        reasons.append("diagnostics_missing")

    if not shared_window_rows:
        reasons.append("no_same_window_overlap")

    any_shared_window_inside_rotational_run = any(
        row.get("inside_rotational_run") is True for row in shared_window_rows
    )

    for reason in row_failure_reasons:
        if (
            reason == "no_window_inside_qualifying_rotational_run"
            and any_shared_window_inside_rotational_run
        ):
            continue

        reasons.append(reason)

    return list(dict.fromkeys(reasons))


def summarize_orb_candidate_support(
    *,
    rotational_persistence: dict[str, Any],
    windowed_heading_sweep: dict[str, Any],
    spatial_containment: dict[str, Any],
    fitted_circle_coherence: dict[str, Any],
    points: list[dict[str, Any]],
    config: dict[str, Any],
) -> dict[str, Any]:
    """
    Summarize diagnostic-only Orb candidate support.

    This helper is no-emission by design. It returns a diagnostic block only.
    It must not mutate points, candidate_state, state, or run_summary.
    """

    strict_overlap_required = bool(config.get("strict_overlap_required", True))
    same_window_required = bool(config.get("same_window_required", True))
    exclude_hover_dominated_windows = bool(
        config.get("exclude_hover_dominated_windows", True)
    )

    rotational_runs = extract_rotational_runs(rotational_persistence)
    heading_windows = extract_heading_windows(windowed_heading_sweep)
    spatial_windows = extract_spatial_windows(spatial_containment)
    circle_windows = extract_circle_windows(fitted_circle_coherence)

    shared_window_rows = build_shared_window_rows(
        rotational_runs=rotational_runs,
        heading_windows=heading_windows,
        spatial_windows=spatial_windows,
        circle_windows=circle_windows,
        points=points,
        exclude_hover_dominated_windows=exclude_hover_dominated_windows,
    )

    support_windows: list[dict[str, Any]] = []
    row_failure_reasons: list[str] = []

    for row in shared_window_rows:
        failed_reasons = evaluate_row_against_config(row, config)
        if failed_reasons:
            row_failure_reasons.extend(failed_reasons)
            continue

        support_windows.append(support_window_from_row(row))

    support_status = "accepted" if support_windows else "withheld"

    withheld_reasons: list[str] = []
    if support_status == "withheld":
        withheld_reasons = summarize_withheld_reasons(
            rotational_runs=rotational_runs,
            heading_windows=heading_windows,
            spatial_windows=spatial_windows,
            circle_windows=circle_windows,
            shared_window_rows=shared_window_rows,
            row_failure_reasons=row_failure_reasons,
        )

    return {
        "support_status": support_status,
        "support_window_count": len(support_windows),
        "support_windows": support_windows,
        "withheld_reasons": withheld_reasons,
        "strict_overlap_required": strict_overlap_required,
        "same_window_required": same_window_required,
        "emits_candidate_state": bool(config.get("emits_candidate_state", False)),
        "emits_final_state": bool(config.get("emits_final_state", False)),
    }