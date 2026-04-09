#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

from geometry_utils import (
    apply_low_speed_curvature_mask,
    compute_centered_moving_average_xy,
    compute_curvature,
    compute_first_derivatives_xy,
    compute_second_derivatives_xy,
    compute_speed_from_derivatives,
)
from io_utils import (
    ensure_required_paths_exist,
    load_config_json,
    load_trace_csv,
    parse_trace_rows_as_floats,
    validate_parsed_trace_points,
    validate_required_config_fields,
    validate_trace_csv_fields,
    write_json,
)

from schema_utils import (
    assemble_state_segmented_trace,
    build_artifact_header,
    build_point_records,
    validate_artifact_consistency_v0,
)

from state_logic import (
    apply_persistence_acceptance,
    assign_local_candidate_states,
    summarize_contiguous_runs,
)


def validate_v0_point_vocab(points: list[dict]) -> None:
    allowed_candidate_states = {"Straight", "Turn", None}
    allowed_final_states = {"Straight", "Turn", None}
    allowed_support_status = {"accepted", "withheld", "unassigned"}

    for idx, point in enumerate(points):
        candidate_state = point.get("candidate_state")
        final_state = point.get("state")
        support_status = point.get("support_status")

        if candidate_state not in allowed_candidate_states:
            raise ValueError(
                f"Invalid candidate_state at point index {idx}: {candidate_state!r}"
            )

        if final_state not in allowed_final_states:
            raise ValueError(f"Invalid state at point index {idx}: {final_state!r}")

        if support_status not in allowed_support_status:
            raise ValueError(
                f"Invalid support_status at point index {idx}: {support_status!r}"
            )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="State-Segmented Trace Constructor v0")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input trajectory CSV file.",
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to constructor config JSON file.",
    )
    parser.add_argument(
        "--output",
        required=False,
        help="Optional explicit output JSON path.",
    )
    return parser.parse_args()


def derive_output_path(input_path: Path, output_arg: str | None) -> Path:
    if output_arg:
        return Path(output_arg)

    repo_root = Path.cwd()
    filename = f"{input_path.stem}_state_segmented_trace.json"
    return repo_root / "state_constructor" / "output" / filename


class StateSegmentedTraceConstructionError(Exception):
    def __init__(self, summary: str, errors: list[dict] | None = None):
        super().__init__(summary)
        self.summary = summary
        self.errors = errors or []


class ConstructorInputValidationError(StateSegmentedTraceConstructionError):
    """Raised when extracted trajectory input is not structurally usable by the constructor."""

    pass


class ConstructorProcessingError(StateSegmentedTraceConstructionError):
    """Raised when real constructor-stage processing fails during execution."""

    pass


class ConstructedArtifactValidationError(StateSegmentedTraceConstructionError):
    """Raised when a constructed candidate artifact fails constructor-side validation."""

    pass


def construct_state_segmented_trace_v0(
    extracted_trajectory: dict,
    config: dict,
) -> dict:
    try:
        if not isinstance(extracted_trajectory, dict):
            raise ConstructorInputValidationError(
                "Constructor input validation failed.",
                [
                    {
                        "category": "input_trajectory_structure",
                        "message": "extracted_trajectory must be a dictionary.",
                    }
                ],
            )

        if not isinstance(config, dict):
            raise ConstructorInputValidationError(
                "Constructor input validation failed.",
                [
                    {
                        "category": "input_trajectory_structure",
                        "message": "config must be a dictionary.",
                    }
                ],
            )

        trajectory_id = extracted_trajectory.get("trajectory_id")
        provenance = extracted_trajectory.get("provenance")
        input_points = extracted_trajectory.get("points")

        if not isinstance(trajectory_id, str) or not trajectory_id.strip():
            raise ConstructorInputValidationError(
                "Constructor input validation failed.",
                [
                    {
                        "category": "input_trajectory_structure",
                        "message": "extracted_trajectory['trajectory_id'] must be a non-empty string.",
                    }
                ],
            )

        if not isinstance(provenance, dict):
            raise ConstructorInputValidationError(
                "Constructor input validation failed.",
                [
                    {
                        "category": "input_trajectory_structure",
                        "message": "extracted_trajectory['provenance'] must be a dictionary.",
                    }
                ],
            )

        source_type = provenance.get("source_type")
        source_id = provenance.get("source_id")
        source_label = provenance.get("source_label")

        if source_type not in {"video", "image_sequence", "trajectory_csv"}:
            raise ConstructorInputValidationError(
                "Constructor input validation failed.",
                [
                    {
                        "category": "input_trajectory_structure",
                        "message": "extracted_trajectory['provenance']['source_type'] must be 'video', 'image_sequence', or 'trajectory_csv'.",
                    }
                ],
            )

        if not isinstance(source_id, str) or not source_id.strip():
            raise ConstructorInputValidationError(
                "Constructor input validation failed.",
                [
                    {
                        "category": "input_trajectory_structure",
                        "message": "extracted_trajectory['provenance']['source_id'] must be a non-empty string.",
                    }
                ],
            )

        if not isinstance(input_points, list) or len(input_points) < 3:
            raise ConstructorInputValidationError(
                "Constructor input validation failed.",
                [
                    {
                        "category": "input_trajectory_structure",
                        "message": "extracted_trajectory['points'] must be a list with at least 3 points.",
                    }
                ],
            )

        validate_required_config_fields(config)

        trace_points = input_points

        window = config["smoothing"]["window"]
        smoothed_points = compute_centered_moving_average_xy(trace_points, window)
        derived_points = compute_first_derivatives_xy(smoothed_points)
        speed_points = compute_speed_from_derivatives(derived_points)
        accel_points = compute_second_derivatives_xy(speed_points)
        curvature_points = compute_curvature(accel_points)

        speed_min_for_curvature = config["masking"]["speed_min_for_curvature"]
        masked_points = apply_low_speed_curvature_mask(
            curvature_points,
            speed_min_for_curvature,
        )

        artifact_header = build_artifact_header(
            config=config,
            trajectory_id=trajectory_id,
            source_type=source_type,
            source_id=source_id,
            source_label=source_label,
            n_points=len(masked_points),
        )

        straight_curvature_epsilon = config["state_logic"]["straight_curvature_epsilon"]
        min_run = config["persistence"]["min_run"]

        candidate_points = assign_local_candidate_states(
            masked_points,
            straight_curvature_epsilon,
        )

        resolved_points = apply_persistence_acceptance(candidate_points, min_run)
        validate_v0_point_vocab(resolved_points)

        candidate_runs = summarize_contiguous_runs(candidate_points, "candidate_state")
        state_runs = summarize_contiguous_runs(resolved_points, "state")

        point_records = build_point_records(resolved_points)

        artifact = assemble_state_segmented_trace(
            artifact_header=artifact_header,
            point_records=point_records,
        )

        artifact["run_summary"] = {
            "candidate_state_runs": candidate_runs,
            "state_runs": state_runs,
        }

        validation_errors = validate_artifact_consistency_v0(artifact)

        if validation_errors:
            raise ConstructedArtifactValidationError(
                "Constructed candidate artifact validation failed.",
                validation_errors,
            )

        return artifact

    except (
        ConstructorInputValidationError,
        ConstructedArtifactValidationError,
    ):
        raise
    except Exception as exc:
        raise ConstructorProcessingError(
            "Constructor processing failed.",
            [{"category": "construction_processing", "message": str(exc)}],
        ) from exc


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    config_path = Path(args.config)
    output_path = derive_output_path(input_path, args.output)

    ensure_required_paths_exist(input_path, config_path)

    config = load_config_json(config_path)
    trace_rows = load_trace_csv(input_path)
    validate_trace_csv_fields(trace_rows)
    trace_points = parse_trace_rows_as_floats(trace_rows)
    validate_parsed_trace_points(trace_points)

    extracted_trajectory = {
        "trajectory_id": input_path.stem,
        "provenance": {
            "source_type": "trajectory_csv",
            "source_id": str(input_path),
            "source_label": input_path.name,
        },
        "points": trace_points,
    }
    artifact = construct_state_segmented_trace_v0(
        extracted_trajectory,
        config,
    )

    write_json(artifact, output_path)

    artifact_id = artifact["artifact"].get("artifact_id", "[missing artifact_id]")
    first_point = trace_points[0]
    artifact_points = artifact["points"]
    first_point_record = artifact_points[0]
    artifact_points_count = len(artifact_points)
    output_exists = output_path.exists()

    candidate_runs = artifact["run_summary"]["candidate_state_runs"]
    state_runs = artifact["run_summary"]["state_runs"]

    first_candidate_run = candidate_runs[0] if candidate_runs else None
    first_state_run = state_runs[0] if state_runs else None

    print("State-Segmented Trace Constructor v0")
    print(f"Input CSV     : {input_path}")
    print(f"Config JSON   : {config_path}")
    print(f"Output JSON   : {output_path}")
    print(f"Artifact ID   : {artifact_id}")
    print(f"Trace Rows    : {len(trace_rows)}")
    print(f"Parsed Rows   : {len(trace_points)}")
    print("First Point   :")
    print(f"  t = {first_point['t']}")
    print(f"  x = {first_point['x']}")
    print(f"  y = {first_point['y']}")

    print("Artifact Header Preview :")
    print(f"  artifact_id   = {artifact['artifact']['artifact_id']}")
    print(f"  artifact_type = {artifact['artifact']['artifact_type']}")
    print(f"  ruleset       = {artifact['artifact']['ruleset_version']}")
    print(f"  n_points      = {artifact['input_spec']['n_points']}")

    print("Run Summary Preview :")
    print(f"  candidate_runs = {len(candidate_runs)}")
    print(f"  state_runs     = {len(state_runs)}")

    if first_candidate_run is not None:
        print("  First Candidate Run :")
        print(f"    value       = {first_candidate_run['value']}")
        print(f"    start_index = {first_candidate_run['start_index']}")
        print(f"    end_index   = {first_candidate_run['end_index']}")
        print(f"    length      = {first_candidate_run['length']}")

    if first_state_run is not None:
        print("  First State Run :")
        print(f"    value       = {first_state_run['value']}")
        print(f"    start_index = {first_state_run['start_index']}")
        print(f"    end_index   = {first_state_run['end_index']}")
        print(f"    length      = {first_state_run['length']}")

    print("Point Record Preview :")
    print(f"  t               = {first_point_record['t']}")
    print(f"  x               = {first_point_record['x']}")
    print(f"  y               = {first_point_record['y']}")
    print(f"  x_smooth        = {first_point_record['x_smooth']}")
    print(f"  y_smooth        = {first_point_record['y_smooth']}")
    print(f"  dx_dt           = {first_point_record['dx_dt']}")
    print(f"  dy_dt           = {first_point_record['dy_dt']}")
    print(f"  speed           = {first_point_record['speed']}")
    print(f"  d2x_dt2         = {first_point_record['d2x_dt2']}")
    print(f"  d2y_dt2         = {first_point_record['d2y_dt2']}")
    print(f"  curvature       = {first_point_record['curvature']}")
    print(f"  curvature_masked= {first_point_record['curvature_masked']}")
    print(f"  candidate_state = {first_point_record['candidate_state']}")
    print(f"  state           = {first_point_record['state']}")
    print(f"  support_status  = {first_point_record['support_status']}")

    print("Full Artifact Preview :")
    print(f"  top_level_keys = {list(artifact.keys())}")
    print(f"  points_count   = {artifact_points_count}")

    print("Written Output Preview :")
    print(f"  output_exists  = {output_exists}")
    print(f"  output_path    = {output_path}")


if __name__ == "__main__":
    try:
        main()
    except StateSegmentedTraceConstructionError as exc:
        print(exc.summary)
        for error in exc.errors:
            print(error)
        raise SystemExit(1)
