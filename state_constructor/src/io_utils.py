from __future__ import annotations

import csv
import json
from pathlib import Path


def ensure_required_paths_exist(input_path: Path, config_path: Path) -> None:
    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_path}")

    if not config_path.exists():
        raise FileNotFoundError(f"Config JSON not found: {config_path}")


def load_config_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_trace_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def parse_trace_rows_as_floats(trace_rows: list[dict]) -> list[dict]:
    parsed_rows: list[dict] = []

    for idx, row in enumerate(trace_rows, start=1):
        try:
            parsed_row = {
                "t": float(row["t"]),
                "x": float(row["x"]),
                "y": float(row["y"]),
            }
        except ValueError as exc:
            raise ValueError(
                f"Non-numeric CSV value at row {idx} in one of: t, x, y"
            ) from exc

        parsed_rows.append(parsed_row)

    return parsed_rows


def validate_required_config_fields(config: dict) -> None:
    required_top_level = [
        "artifact_id",
        "source_id",
        "cadence_seconds",
        "projection",
        "ruleset_version",
        "smoothing",
        "derivatives",
        "masking",
        "state_logic",
        "persistence",
    ]

    for key in required_top_level:
        if key not in config:
            raise ValueError(f"Missing required config field: {key}")

    smoothing = config["smoothing"]
    derivatives = config["derivatives"]
    masking = config["masking"]
    state_logic = config["state_logic"]
    persistence = config["persistence"]

    if "method" not in smoothing:
        raise ValueError("Missing required config field: smoothing.method")
    if "window" not in smoothing:
        raise ValueError("Missing required config field: smoothing.window")

    if "method" not in derivatives:
        raise ValueError("Missing required config field: derivatives.method")

    if "speed_min_for_curvature" not in masking:
        raise ValueError(
            "Missing required config field: masking.speed_min_for_curvature"
        )

    if "straight_curvature_epsilon" not in state_logic:
        raise ValueError(
            "Missing required config field: state_logic.straight_curvature_epsilon"
        )

    if "min_run" not in persistence:
        raise ValueError("Missing required config field: persistence.min_run")

    if config["projection"] != "planar":
        raise ValueError("Invalid config value: projection must be 'planar' in v0")

    if config["ruleset_version"] != "v0":
        raise ValueError("Invalid config value: ruleset_version must be 'v0'")

    if config["cadence_seconds"] <= 0:
        raise ValueError("Invalid config value: cadence_seconds must be > 0")

    if smoothing["window"] < 1:
        raise ValueError("Invalid config value: smoothing.window must be >= 1")

    if masking["speed_min_for_curvature"] < 0:
        raise ValueError(
            "Invalid config value: masking.speed_min_for_curvature must be >= 0"
        )

    if state_logic["straight_curvature_epsilon"] < 0:
        raise ValueError(
            "Invalid config value: state_logic.straight_curvature_epsilon must be >= 0"
        )

    if persistence["min_run"] < 1:
        raise ValueError("Invalid config value: persistence.min_run must be >= 1")


def validate_trace_csv_fields(trace_rows: list[dict]) -> None:
    if not trace_rows:
        raise ValueError("Input CSV contains no data rows")

    required_columns = ["t", "x", "y"]

    first_row = trace_rows[0]
    for column in required_columns:
        if column not in first_row:
            raise ValueError(f"Missing required CSV column: {column}")

    for idx, row in enumerate(trace_rows, start=1):
        for column in required_columns:
            value = row.get(column)
            if value is None or str(value).strip() == "":
                raise ValueError(
                    f"Missing required CSV value at row {idx}, column '{column}'"
                )


def validate_parsed_trace_points(trace_points: list[dict]) -> None:
    if len(trace_points) < 3:
        raise ValueError("Parsed trace must contain at least 3 rows")

    for idx in range(1, len(trace_points)):
        prev_t = trace_points[idx - 1]["t"]
        curr_t = trace_points[idx]["t"]

        if curr_t <= prev_t:
            raise ValueError(
                f"Time values must be strictly increasing; violation at parsed row {idx + 1}"
            )


def write_json(data: dict, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
