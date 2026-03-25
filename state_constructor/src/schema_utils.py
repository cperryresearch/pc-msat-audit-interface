from __future__ import annotations


class ArtifactValidationError(Exception):
    """
    Canonical v0 caller-side failure surface for structural artifact invalidity.
    """

    def __init__(self, summary, errors):
        super().__init__(summary)
        self.summary = summary
        self.errors = errors


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
        "candidate_state": point.get("candidate_state"),
        "state": point.get("state"),
        "support_status": point.get("support_status", "unassigned"),
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


def validate_artifact_consistency_v0(artifact_dict: dict) -> list[dict]:
    errors: list[dict] = []

    required_top_level_blocks = [
        "artifact",
        "provenance",
        "input_spec",
        "processing",
        "state_model",
        "points",
        "run_summary",
    ]

    for block_name in required_top_level_blocks:
        if block_name not in artifact_dict:
            errors.append(
                {
                    "category": "missing_top_level_block",
                    "message": f"Missing required top-level block: {block_name}",
                }
            )

    required_point_fields = [
        "t",
        "x",
        "y",
        "x_smooth",
        "y_smooth",
        "dx_dt",
        "dy_dt",
        "speed",
        "d2x_dt2",
        "d2y_dt2",
        "curvature",
        "curvature_masked",
        "candidate_state",
        "state",
        "support_status",
    ]

    points = artifact_dict.get("points")
    if isinstance(points, list):
        for point_index, point in enumerate(points):
            if not isinstance(point, dict):
                continue

            for field_name in required_point_fields:
                if field_name not in point:
                    errors.append(
                        {
                            "category": "missing_point_field",
                            "message": (
                                f"Point at index {point_index} is missing required field: "
                                f"{field_name}"
                            ),
                        }
                    )

    allowed_candidate_states = {"Straight", "Turn", None}
    allowed_states = {"Straight", "Turn", None}
    allowed_support_statuses = {"accepted", "withheld", "unassigned"}

    points = artifact_dict.get("points")
    if isinstance(points, list):
        for point_index, point in enumerate(points):
            if not isinstance(point, dict):
                continue

            if "candidate_state" in point:
                if point["candidate_state"] not in allowed_candidate_states:
                    errors.append(
                        {
                            "category": "invalid_vocabulary_value",
                            "message": (
                                f"Point at index {point_index} has invalid candidate_state: "
                                f"{point['candidate_state']}"
                            ),
                        }
                    )

            if "state" in point:
                if point["state"] not in allowed_states:
                    errors.append(
                        {
                            "category": "invalid_vocabulary_value",
                            "message": (
                                f"Point at index {point_index} has invalid state: "
                                f"{point['state']}"
                            ),
                        }
                    )

            if "support_status" in point:
                if point["support_status"] not in allowed_support_statuses:
                    errors.append(
                        {
                            "category": "invalid_vocabulary_value",
                            "message": (
                                f"Point at index {point_index} has invalid support_status: "
                                f"{point['support_status']}"
                            ),
                        }
                    )

    required_run_entry_fields = {
        "field",
        "value",
        "start_index",
        "end_index",
        "length",
    }

    run_summary = artifact_dict.get("run_summary")
    if isinstance(run_summary, dict):
        for run_list_name in ["candidate_state_runs", "state_runs"]:
            run_list = run_summary.get(run_list_name)

            if not isinstance(run_list, list):
                continue

            for run_index, run_entry in enumerate(run_list):
                if not isinstance(run_entry, dict):
                    errors.append(
                        {
                            "category": "invalid_run_entry",
                            "message": (
                                f"Run entry at index {run_index} in {run_list_name} "
                                f"is not a dictionary"
                            ),
                        }
                    )
                    continue

                missing_fields = required_run_entry_fields - set(run_entry.keys())
                extra_fields = set(run_entry.keys()) - required_run_entry_fields

                if missing_fields or extra_fields:
                    details = []
                    if missing_fields:
                        details.append(
                            "missing fields: " + ", ".join(sorted(missing_fields))
                        )
                    if extra_fields:
                        details.append(
                            "unexpected fields: " + ", ".join(sorted(extra_fields))
                        )

                    errors.append(
                        {
                            "category": "invalid_run_entry",
                            "message": (
                                f"Run entry at index {run_index} in {run_list_name} "
                                f"has invalid shape ({'; '.join(details)})"
                            ),
                        }
                    )

    points = artifact_dict.get("points")
    run_summary = artifact_dict.get("run_summary")

    if isinstance(points, list) and isinstance(run_summary, dict):
        max_point_index = len(points) - 1

        for run_list_name in ["candidate_state_runs", "state_runs"]:
            run_list = run_summary.get(run_list_name)

            if not isinstance(run_list, list):
                continue

            for run_index, run_entry in enumerate(run_list):
                if not isinstance(run_entry, dict):
                    continue

                required_fields = {"start_index", "end_index"}
                if not required_fields.issubset(run_entry.keys()):
                    continue

                start_index = run_entry["start_index"]
                end_index = run_entry["end_index"]

                if not isinstance(start_index, int) or not isinstance(end_index, int):
                    errors.append(
                        {
                            "category": "run_index_out_of_bounds",
                            "message": (
                                f"Run entry at index {run_index} in {run_list_name} "
                                f"has non-integer index bounds"
                            ),
                        }
                    )
                    continue

                if start_index < 0 or end_index < 0:
                    errors.append(
                        {
                            "category": "run_index_out_of_bounds",
                            "message": (
                                f"Run entry at index {run_index} in {run_list_name} "
                                f"has negative index bounds: "
                                f"start_index={start_index}, end_index={end_index}"
                            ),
                        }
                    )
                    continue

                if start_index > end_index:
                    errors.append(
                        {
                            "category": "run_index_out_of_bounds",
                            "message": (
                                f"Run entry at index {run_index} in {run_list_name} "
                                f"has start_index greater than end_index: "
                                f"start_index={start_index}, end_index={end_index}"
                            ),
                        }
                    )
                    continue

                if start_index > max_point_index or end_index > max_point_index:
                    errors.append(
                        {
                            "category": "run_index_out_of_bounds",
                            "message": (
                                f"Run entry at index {run_index} in {run_list_name} "
                                f"exceeds point bounds: "
                                f"start_index={start_index}, end_index={end_index}, "
                                f"max_point_index={max_point_index}"
                            ),
                        }
                    )
    points = artifact_dict.get("points")
    run_summary = artifact_dict.get("run_summary")

    if isinstance(points, list) and isinstance(run_summary, dict):

        def reconstruct_runs_from_points(
            points_list: list[dict], field_name: str
        ) -> list[dict]:
            reconstructed_runs: list[dict] = []
            run_start = None
            run_value = None

            for point_index, point in enumerate(points_list):
                if not isinstance(point, dict):
                    continue

                value = point.get(field_name)

                if value is None:
                    if run_start is not None:
                        reconstructed_runs.append(
                            {
                                "field": field_name,
                                "value": run_value,
                                "start_index": run_start,
                                "end_index": point_index - 1,
                                "length": point_index - run_start,
                            }
                        )
                        run_start = None
                        run_value = None
                    continue

                if run_start is None:
                    run_start = point_index
                    run_value = value
                    continue

                if value != run_value:
                    reconstructed_runs.append(
                        {
                            "field": field_name,
                            "value": run_value,
                            "start_index": run_start,
                            "end_index": point_index - 1,
                            "length": point_index - run_start,
                        }
                    )
                    run_start = point_index
                    run_value = value

            if run_start is not None:
                reconstructed_runs.append(
                    {
                        "field": field_name,
                        "value": run_value,
                        "start_index": run_start,
                        "end_index": len(points_list) - 1,
                        "length": len(points_list) - run_start,
                    }
                )

            return reconstructed_runs

        expected_candidate_runs = reconstruct_runs_from_points(
            points, "candidate_state"
        )
        actual_candidate_runs = run_summary.get("candidate_state_runs")
        if isinstance(actual_candidate_runs, list):
            if actual_candidate_runs != expected_candidate_runs:
                errors.append(
                    {
                        "category": "candidate_run_mismatch",
                        "message": (
                            "run_summary['candidate_state_runs'] does not match contiguous "
                            "non-None candidate_state runs reconstructed from points"
                        ),
                    }
                )

        expected_state_runs = reconstruct_runs_from_points(points, "state")
        actual_state_runs = run_summary.get("state_runs")
        if isinstance(actual_state_runs, list):
            if actual_state_runs != expected_state_runs:
                errors.append(
                    {
                        "category": "state_run_mismatch",
                        "message": (
                            "run_summary['state_runs'] does not match contiguous non-None "
                            "state runs reconstructed from points"
                        ),
                    }
                )

    return errors
