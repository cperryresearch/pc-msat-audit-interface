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


def main() -> None:
    args = parse_args()

    input_path = Path(args.input)
    config_path = Path(args.config)
    output_path = derive_output_path(input_path, args.output)

    ensure_required_paths_exist(input_path, config_path)

    config = load_config_json(config_path)
    validate_required_config_fields(config)

    trace_rows = load_trace_csv(input_path)
    validate_trace_csv_fields(trace_rows)
    trace_points = parse_trace_rows_as_floats(trace_rows)
    validate_parsed_trace_points(trace_points)

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
        input_path=str(input_path),
        output_path=str(output_path),
        n_points=len(masked_points),
    )

    point_records = build_point_records(masked_points)

    artifact = assemble_state_segmented_trace(
        artifact_header=artifact_header,
        point_records=point_records,
    )

    write_json(artifact, output_path)

    artifact_id = config.get("artifact_id", "[missing artifact_id]")
    first_point = trace_points[0]
    first_masked_point = masked_points[0]
    first_point_record = point_records[0]
    artifact_points_count = len(artifact["points"])
    output_exists = output_path.exists()

    print("State-Segmented Trace Constructor v0")
    print(f"Input CSV     : {input_path}")
    print(f"Config JSON   : {config_path}")
    print(f"Output JSON   : {output_path}")
    print(f"Artifact ID   : {artifact_id}")
    print(f"Trace Rows    : {len(trace_rows)}")
    print(f"Parsed Rows   : {len(trace_points)}")
    print(f"Smooth Window : {window}")
    print("First Point   :")
    print(f"  t = {first_point['t']}")
    print(f"  x = {first_point['x']}")
    print(f"  y = {first_point['y']}")
    print(f"Speed Mask   : {speed_min_for_curvature}")
    print("First Masked Point :")
    print(f"  t                = {first_masked_point['t']}")
    print(f"  x                = {first_masked_point['x']}")
    print(f"  y                = {first_masked_point['y']}")
    print(f"  x_smooth         = {first_masked_point['x_smooth']}")
    print(f"  y_smooth         = {first_masked_point['y_smooth']}")
    print(f"  dx_dt            = {first_masked_point['dx_dt']}")
    print(f"  dy_dt            = {first_masked_point['dy_dt']}")
    print(f"  speed            = {first_masked_point['speed']}")
    print(f"  d2x_dt2          = {first_masked_point['d2x_dt2']}")
    print(f"  d2y_dt2          = {first_masked_point['d2y_dt2']}")
    print(f"  curvature        = {first_masked_point['curvature']}")
    print(f"  curvature_masked = {first_masked_point['curvature_masked']}")

    print("Artifact Header Preview :")
    print(f"  artifact_id   = {artifact_header['artifact']['artifact_id']}")
    print(f"  artifact_type = {artifact_header['artifact']['artifact_type']}")
    print(f"  ruleset       = {artifact_header['artifact']['ruleset_version']}")
    print(f"  n_points      = {artifact_header['input_spec']['n_points']}")

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
    main()
