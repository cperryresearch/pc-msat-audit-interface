import argparse
import json
import math
from pathlib import Path
from typing import Any


DEFAULT_WINDOW_SIZES = [5, 25, 50, 100, 250, 500, 1000]

COMBINED_CANDIDATE_MIN_PATH_LENGTH = 1.0
COMBINED_CANDIDATE_MIN_HEADING_SWEEP = 1.0
COMBINED_CANDIDATE_MAX_DISPLACEMENT_RATIO = 0.9


def load_artifact(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def get_points(artifact: dict[str, Any]) -> list[dict[str, Any]]:
    points = artifact.get("points", [])

    if not isinstance(points, list):
        raise ValueError("Artifact points field is not a list.")

    if len(points) == 0:
        raise ValueError("Artifact contains no points.")

    return points


def finite_number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None

    if isinstance(value, (int, float)) and math.isfinite(value):
        return float(value)

    return None


def point_heading_delta_abs(point: dict[str, Any]) -> float:
    value = finite_number(point.get("heading_delta"))
    return abs(value) if value is not None else 0.0


def point_heading_delta_sign(point: dict[str, Any]) -> int | None:
    value = point.get("heading_delta_sign")

    if value in (-1, 0, 1):
        return int(value)

    return None


def summarize_same_sign_rotational_runs(
    points: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    runs: list[dict[str, Any]] = []
    active_sign: int | None = None
    active_start: int | None = None
    active_cumulative = 0.0

    for index, point in enumerate(points):
        sign = point_heading_delta_sign(point)
        abs_delta = point_heading_delta_abs(point)

        if sign is None or sign == 0:
            if active_sign is not None and active_start is not None:
                runs.append(
                    {
                        "sign": active_sign,
                        "start_index": active_start,
                        "end_index": index - 1,
                        "length": index - active_start,
                        "cumulative_abs_heading_delta": active_cumulative,
                    }
                )

            active_sign = None
            active_start = None
            active_cumulative = 0.0
            continue

        if active_sign is None:
            active_sign = sign
            active_start = index
            active_cumulative = abs_delta
            continue

        if sign == active_sign:
            active_cumulative += abs_delta
            continue

        if active_start is not None:
            runs.append(
                {
                    "sign": active_sign,
                    "start_index": active_start,
                    "end_index": index - 1,
                    "length": index - active_start,
                    "cumulative_abs_heading_delta": active_cumulative,
                }
            )

        active_sign = sign
        active_start = index
        active_cumulative = abs_delta

    if active_sign is not None and active_start is not None:
        runs.append(
            {
                "sign": active_sign,
                "start_index": active_start,
                "end_index": len(points) - 1,
                "length": len(points) - active_start,
                "cumulative_abs_heading_delta": active_cumulative,
            }
        )

    return runs


def containing_rotational_run(
    runs: list[dict[str, Any]],
    start_index: int,
    end_index: int,
) -> dict[str, Any] | None:
    for run in runs:
        run_start = run.get("start_index")
        run_end = run.get("end_index")

        if (
            isinstance(run_start, int)
            and isinstance(run_end, int)
            and run_start <= start_index
            and run_end >= end_index
        ):
            return run

    return None


def fit_circle(points: list[dict[str, Any]]) -> dict[str, Any]:
    coordinates: list[tuple[float, float]] = []

    for point in points:
        x = finite_number(point.get("x"))
        y = finite_number(point.get("y"))

        if x is None or y is None:
            return {"fit_status": "unfit", "reason": "missing_coordinate"}

        coordinates.append((x, y))

    if len(coordinates) < 3:
        return {"fit_status": "unfit", "reason": "insufficient_points"}

    mean_x = sum(x for x, _ in coordinates) / len(coordinates)
    mean_y = sum(y for _, y in coordinates) / len(coordinates)

    centered = [(x - mean_x, y - mean_y) for x, y in coordinates]

    suu = sum(u * u for u, _ in centered)
    suv = sum(u * v for u, v in centered)
    svv = sum(v * v for _, v in centered)
    suuu = sum(u * u * u for u, _ in centered)
    svvv = sum(v * v * v for _, v in centered)
    suvv = sum(u * v * v for u, v in centered)
    svuu = sum(v * u * u for u, v in centered)

    determinant = suu * svv - suv * suv

    if abs(determinant) < 1e-12:
        return {"fit_status": "unfit", "reason": "near_collinear"}

    rhs_u = 0.5 * (suuu + suvv)
    rhs_v = 0.5 * (svvv + svuu)

    center_u = (rhs_u * svv - rhs_v * suv) / determinant
    center_v = (suu * rhs_v - suv * rhs_u) / determinant

    center_x = mean_x + center_u
    center_y = mean_y + center_v

    radii = [math.hypot(x - center_x, y - center_y) for x, y in coordinates]
    radius = sum(radii) / len(radii)

    if radius <= 1e-12:
        return {"fit_status": "unfit", "reason": "near_zero_radius"}

    residuals = [abs(r - radius) for r in radii]
    mean_residual = sum(residuals) / len(residuals)
    max_residual = max(residuals)

    return {
        "fit_status": "fit",
        "center_x": center_x,
        "center_y": center_y,
        "radius": radius,
        "mean_radial_residual_ratio": mean_residual / radius,
        "max_radial_residual_ratio": max_residual / radius,
    }


def summarize_window(
    points: list[dict[str, Any]],
    start_index: int,
    end_index: int,
    rotational_runs: list[dict[str, Any]],
) -> dict[str, Any] | None:
    window = points[start_index : end_index + 1]

    if len(window) < 2:
        return None

    path_length = 0.0

    for previous, current in zip(window, window[1:]):
        previous_x = finite_number(previous.get("x"))
        previous_y = finite_number(previous.get("y"))
        current_x = finite_number(current.get("x"))
        current_y = finite_number(current.get("y"))

        if (
            previous_x is None
            or previous_y is None
            or current_x is None
            or current_y is None
        ):
            return None

        path_length += math.hypot(current_x - previous_x, current_y - previous_y)

    first_x = finite_number(window[0].get("x"))
    first_y = finite_number(window[0].get("y"))
    last_x = finite_number(window[-1].get("x"))
    last_y = finite_number(window[-1].get("y"))

    if first_x is None or first_y is None or last_x is None or last_y is None:
        return None

    net_displacement = math.hypot(last_x - first_x, last_y - first_y)
    displacement_ratio = None if path_length <= 0 else net_displacement / path_length

    heading_sweep = sum(point_heading_delta_abs(point) for point in window)
    circle = fit_circle(window)
    rotational_run = containing_rotational_run(rotational_runs, start_index, end_index)

    return {
        "start_index": start_index,
        "end_index": end_index,
        "length": len(window),
        "t_start": window[0].get("t"),
        "t_end": window[-1].get("t"),
        "heading_sweep": heading_sweep,
        "path_length": path_length,
        "net_displacement": net_displacement,
        "displacement_ratio": displacement_ratio,
        "circle_fit_status": circle.get("fit_status"),
        "mean_radial_residual_ratio": circle.get("mean_radial_residual_ratio"),
        "max_radial_residual_ratio": circle.get("max_radial_residual_ratio"),
        "inside_rotational_run": rotational_run is not None,
        "rotational_run_length": None
        if rotational_run is None
        else rotational_run.get("length"),
        "rotational_run_cumulative_abs_heading_delta": None
        if rotational_run is None
        else rotational_run.get("cumulative_abs_heading_delta"),
    }


def compact_window(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "start_index": row["start_index"],
        "end_index": row["end_index"],
        "length": row["length"],
        "t_start": row["t_start"],
        "t_end": row["t_end"],
        "heading_sweep": round(row["heading_sweep"], 6),
        "path_length": round(row["path_length"], 6),
        "net_displacement": round(row["net_displacement"], 6),
        "displacement_ratio": None
        if row["displacement_ratio"] is None
        else round(row["displacement_ratio"], 6),
        "circle_fit_status": row["circle_fit_status"],
        "mean_radial_residual_ratio": None
        if row["mean_radial_residual_ratio"] is None
        else row["mean_radial_residual_ratio"],
        "max_radial_residual_ratio": None
        if row["max_radial_residual_ratio"] is None
        else row["max_radial_residual_ratio"],
        "inside_rotational_run": row["inside_rotational_run"],
        "rotational_run_length": row["rotational_run_length"],
        "rotational_run_cumulative_abs_heading_delta": row[
            "rotational_run_cumulative_abs_heading_delta"
        ],
    }


def review_window_size(
    points: list[dict[str, Any]],
    rotational_runs: list[dict[str, Any]],
    window_size: int,
    step: int,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    if len(points) < window_size:
        return rows

    for start_index in range(0, len(points) - window_size + 1, step):
        end_index = start_index + window_size - 1
        summary = summarize_window(points, start_index, end_index, rotational_runs)

        if summary is not None:
            rows.append(summary)

    return rows


def get_fit_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        row
        for row in rows
        if row.get("circle_fit_status") == "fit"
        and row.get("displacement_ratio") is not None
    ]


def get_combined_candidates(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    combined_candidates = [
        row
        for row in rows
        if row["inside_rotational_run"]
        and row["path_length"] >= COMBINED_CANDIDATE_MIN_PATH_LENGTH
        and row["heading_sweep"] >= COMBINED_CANDIDATE_MIN_HEADING_SWEEP
        and row["displacement_ratio"] is not None
        and row["displacement_ratio"] <= COMBINED_CANDIDATE_MAX_DISPLACEMENT_RATIO
    ]

    return sorted(
        combined_candidates,
        key=lambda row: (
            row["displacement_ratio"],
            -row["heading_sweep"],
            row["mean_radial_residual_ratio"]
            if row["mean_radial_residual_ratio"] is not None
            else float("inf"),
        ),
    )


def build_review_thresholds() -> dict[str, Any]:
    return {
        "fit_row_screen": {
            "requires_circle_fit_status": "fit",
            "requires_displacement_ratio": True,
        },
        "combined_candidate_screen": {
            "requires_inside_rotational_run": True,
            "min_path_length": COMBINED_CANDIDATE_MIN_PATH_LENGTH,
            "min_heading_sweep": COMBINED_CANDIDATE_MIN_HEADING_SWEEP,
            "requires_displacement_ratio": True,
            "max_displacement_ratio": COMBINED_CANDIDATE_MAX_DISPLACEMENT_RATIO,
        },
    }


def build_no_emission_boundary() -> dict[str, bool]:
    return {
        "review_only": True,
        "modifies_artifact": False,
        "emits_candidate_state": False,
        "emits_final_state": False,
        "changes_run_summary": False,
        "changes_pc_maw_admission": False,
        "changes_playback_behavior": False,
    }


def build_review_report(
    artifact_path: Path,
    artifact: dict[str, Any],
    points: list[dict[str, Any]],
    rotational_runs: list[dict[str, Any]],
    window_sizes: list[int],
    step: int,
    summary_only: bool,
) -> dict[str, Any]:
    strongest_rotational_run = (
        max(
            rotational_runs,
            key=lambda run: run.get("cumulative_abs_heading_delta", 0.0),
        )
        if rotational_runs
        else None
    )

    window_size_summaries: list[dict[str, Any]] = []

    for window_size in window_sizes:
        rows = review_window_size(points, rotational_runs, window_size, step)
        fit_rows = get_fit_rows(rows)
        combined_candidates = get_combined_candidates(fit_rows)

        window_size_summaries.append(
            {
                "window_size": window_size,
                "windows_evaluated": len(rows),
                "fit_windows": len(fit_rows),
                "combined_candidate_count": len(combined_candidates),
                "best_combined_candidate": combined_candidates[0]
                if combined_candidates
                else None,
                "top_combined_candidates": combined_candidates[:3],
            }
        )

    return {
        "schema_name": "orb_support_window_scale_review",
        "schema_version": "review_v0",
        "review_metadata": {
            "artifact_path": str(artifact_path),
            "artifact_id": artifact.get("artifact", {}).get("artifact_id"),
            "points": len(points),
            "window_sizes": window_sizes,
            "step": step,
            "summary_only": summary_only,
        },
        "no_emission_boundary": build_no_emission_boundary(),
        "review_thresholds": build_review_thresholds(),
        "strongest_rotational_run": strongest_rotational_run,
        "window_size_summaries": window_size_summaries,
    }


def print_ranked(title: str, rows: list[dict[str, Any]], limit: int = 8) -> None:
    print(f"\n{title}")

    for row in rows[:limit]:
        print(" ", compact_window(row))



def print_summary_for_window_size(
    window_size: int,
    rows: list[dict[str, Any]],
    fit_rows: list[dict[str, Any]],
    combined_candidates: list[dict[str, Any]],
) -> None:
    print("\n" + "=" * 88)
    print("WINDOW SIZE:", window_size)
    print("windows_evaluated:", len(rows))
    print("fit_windows:", len(fit_rows))
    print("combined_candidate_count:", len(combined_candidates))

    print("\nbest_combined_candidate:")
    if combined_candidates:
        print(" ", compact_window(combined_candidates[0]))
    else:
        print("  None")

    print("\ntop_3_combined_candidates:")
    if combined_candidates:
        for row in combined_candidates[:3]:
            print(" ", compact_window(row))
    else:
        print("  None")


def print_full_for_window_size(
    window_size: int,
    rows: list[dict[str, Any]],
    fit_rows: list[dict[str, Any]],
    combined_candidates: list[dict[str, Any]],
) -> None:
    print("\n" + "=" * 88)
    print("WINDOW SIZE:", window_size)
    print("windows_evaluated:", len(rows))
    print("fit_windows:", len(fit_rows))

    if not fit_rows:
        return

    by_heading = sorted(
        fit_rows,
        key=lambda row: row["heading_sweep"],
        reverse=True,
    )
    by_low_displacement = sorted(
        fit_rows,
        key=lambda row: row["displacement_ratio"],
    )
    by_circle = sorted(
        fit_rows,
        key=lambda row: row["mean_radial_residual_ratio"]
        if row["mean_radial_residual_ratio"] is not None
        else float("inf"),
    )

    print_ranked("Top by heading_sweep:", by_heading)
    print_ranked("Top by low displacement_ratio:", by_low_displacement)
    print_ranked("Top by circle mean residual:", by_circle)
    print_ranked(
        "Combined review candidates "
        "(inside rotational run, path>=1, heading_sweep>=1, displacement_ratio<=0.9):",
        combined_candidates,
    )

def print_summary_from_report_entry(entry: dict[str, Any]) -> None:
    print("\n" + "=" * 88)
    print("WINDOW SIZE:", entry["window_size"])
    print("windows_evaluated:", entry["windows_evaluated"])
    print("fit_windows:", entry["fit_windows"])
    print("combined_candidate_count:", entry["combined_candidate_count"])

    print("\nbest_combined_candidate:")
    if entry["best_combined_candidate"] is not None:
        print(" ", entry["best_combined_candidate"])
    else:
        print("  None")

    print("\ntop_3_combined_candidates:")
    if entry["top_combined_candidates"]:
        for row in entry["top_combined_candidates"]:
            print(" ", row)
    else:
        print("  None")


def print_report_summary(report: dict[str, Any]) -> None:
    for entry in report["window_size_summaries"]:
        print_summary_from_report_entry(entry)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Review alternate Orb support window scales without modifying Constructor v0 behavior."
    )
    parser.add_argument(
        "--artifact",
        required=True,
        help="Path to a Constructor v0 state-segmented trace output JSON.",
    )
    parser.add_argument(
        "--window-sizes",
        default=",".join(str(size) for size in DEFAULT_WINDOW_SIZES),
        help="Comma-separated point-count window sizes to review.",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=5,
        help="Sliding-window step size in points.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only concise per-window-size summaries.",
    )

    parser.add_argument(
        "--summary-output",
        help="Optional path to write a full-precision JSON summary report.",
    )

    args = parser.parse_args()

    artifact_path = Path(args.artifact)
    window_sizes = [
        int(value.strip())
        for value in args.window_sizes.split(",")
        if value.strip()
    ]

    artifact = load_artifact(artifact_path)
    points = get_points(artifact)
    rotational_runs = summarize_same_sign_rotational_runs(points)

    report = build_review_report(
        artifact_path=artifact_path,
        artifact=artifact,
        points=points,
        rotational_runs=rotational_runs,
        window_sizes=window_sizes,
        step=args.step,
        summary_only=args.summary_only,
    )

    print("Orb support window-scale review")
    print("artifact:", artifact_path)
    print("points:", len(points))
    print("window_sizes:", window_sizes)
    print("step:", args.step)
    print("summary_only:", args.summary_only)
    print("review_only:", True)
    print("modifies_artifact:", False)
    print("emits_candidate_state:", False)
    print("emits_final_state:", False)

    if rotational_runs:
        strongest_rotational_run = max(
            rotational_runs,
            key=lambda run: run.get("cumulative_abs_heading_delta", 0.0),
        )
        print("\nStrongest rotational run:")
        print(" ", strongest_rotational_run)
    else:
        print("\nStrongest rotational run:")
        print("  None")

    if args.summary_only:
        print_report_summary(report)
    else:
        for window_size in window_sizes:
            rows = review_window_size(points, rotational_runs, window_size, args.step)
            fit_rows = get_fit_rows(rows)
            combined_candidates = get_combined_candidates(fit_rows)

            print_full_for_window_size(
                window_size,
                rows,
                fit_rows,
                combined_candidates,
            )

    if args.summary_output:
        summary_output_path = Path(args.summary_output)
        summary_output_path.parent.mkdir(parents=True, exist_ok=True)
        summary_output_path.write_text(
            json.dumps(report, indent=2),
            encoding="utf-8",
        )
        print("\nWrote summary output:", summary_output_path)


if __name__ == "__main__":

    main()