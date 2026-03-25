from __future__ import annotations


def build_artifact_header(
    config: dict,
    input_path: str,
    output_path: str,
    n_points: int,
) -> dict:
    return {
        "artifact": {
            "artifact_id": config["artifact_id"],
            "artifact_type": "state_segmented_trace",
            "ruleset_version": config["ruleset_version"],
        },
        "provenance": {
            "source_id": config["source_id"],
            "input_path": input_path,
            "output_path": output_path,
        },
        "input_spec": {
            "projection": config["projection"],
            "cadence_seconds": config["cadence_seconds"],
            "n_points": n_points,
        },
        "processing": {
            "smoothing": {
                "method": config["smoothing"]["method"],
                "window": config["smoothing"]["window"],
            },
            "derivatives": {
                "method": config["derivatives"]["method"],
            },
            "masking": {
                "speed_min_for_curvature": config["masking"]["speed_min_for_curvature"],
            },
            "persistence": {
                "min_run": config["persistence"]["min_run"],
            },
        },
        "state_model": {
            "activated_states": ["Straight", "Turn"],
            "deferred_states": ["Hover", "Orb"],
        },
    }


def build_point_record(point: dict) -> dict:
    return {
        "t": point["t"],
        "x": point["x"],
        "y": point["y"],
        "x_smooth": point["x_smooth"],
        "y_smooth": point["y_smooth"],
        "dx_dt": point["dx_dt"],
        "dy_dt": point["dy_dt"],
        "speed": point["speed"],
        "d2x_dt2": point["d2x_dt2"],
        "d2y_dt2": point["d2y_dt2"],
        "curvature": point["curvature"],
        "curvature_masked": point["curvature_masked"],
        "candidate_state": None,
        "state": None,
        "support_status": "unassigned",
    }


def build_point_records(points: list[dict]) -> list[dict]:
    return [build_point_record(point) for point in points]


def assemble_state_segmented_trace(
    artifact_header: dict,
    point_records: list[dict],
) -> dict:
    return {
        **artifact_header,
        "points": point_records,
    }
