from __future__ import annotations


def assign_local_candidate_states(
    points: list[dict],
    straight_curvature_epsilon: float,
) -> list[dict]:
    candidate_points: list[dict] = []

    for point in points:
        curvature = point["curvature"]
        curvature_masked = point["curvature_masked"]

        if curvature_masked or curvature is None:
            candidate_state = None
        elif abs(curvature) <= straight_curvature_epsilon:
            candidate_state = "Straight"
        else:
            candidate_state = "Turn"

        candidate_points.append(
            {
                **point,
                "candidate_state": candidate_state,
            }
        )

    return candidate_points


def apply_persistence_acceptance(
    candidate_points: list[dict],
    min_run: int,
) -> list[dict]:
    if min_run < 1:
        raise ValueError("min_run must be >= 1")

    resolved_points = [dict(point) for point in candidate_points]

    run_start = 0

    while run_start < len(resolved_points):
        run_candidate = resolved_points[run_start].get("candidate_state")
        run_end = run_start + 1

        while run_end < len(resolved_points):
            next_candidate = resolved_points[run_end].get("candidate_state")
            if next_candidate != run_candidate:
                break
            run_end += 1

        run_length = run_end - run_start

        for idx in range(run_start, run_end):
            if run_candidate is None:
                resolved_points[idx]["state"] = None
                resolved_points[idx]["support_status"] = "unassigned"
            elif run_length >= min_run:
                resolved_points[idx]["state"] = run_candidate
                resolved_points[idx]["support_status"] = "accepted"
            else:
                resolved_points[idx]["state"] = None
                resolved_points[idx]["support_status"] = "withheld"

        run_start = run_end

    return resolved_points


def summarize_contiguous_runs(
    points: list[dict],
    field_name: str,
) -> list[dict]:
    if not points:
        return []

    runs: list[dict] = []
    run_start = 0

    while run_start < len(points):
        run_value = points[run_start].get(field_name)
        run_end = run_start + 1

        while run_end < len(points):
            next_value = points[run_end].get(field_name)
            if next_value != run_value:
                break
            run_end += 1

        runs.append(
            {
                "field": field_name,
                "value": run_value,
                "start_index": run_start,
                "end_index": run_end - 1,
                "length": run_end - run_start,
            }
        )

        run_start = run_end

    return runs
