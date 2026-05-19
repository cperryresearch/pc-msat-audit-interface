from __future__ import annotations

import math


def compute_centered_moving_average_xy(
    trace_points: list[dict],
    window: int,
) -> list[dict]:
    if window < 1:
        raise ValueError("window must be >= 1")

    if window % 2 == 0:
        raise ValueError("window must be odd for centered moving average")

    half_window = window // 2
    smoothed_points: list[dict] = []

    for idx, point in enumerate(trace_points):
        start = max(0, idx - half_window)
        end = min(len(trace_points), idx + half_window + 1)

        window_points = trace_points[start:end]
        avg_x = sum(p["x"] for p in window_points) / len(window_points)
        avg_y = sum(p["y"] for p in window_points) / len(window_points)

        smoothed_points.append(
            {
                "t": point["t"],
                "x": point["x"],
                "y": point["y"],
                "x_smooth": avg_x,
                "y_smooth": avg_y,
            }
        )

    return smoothed_points


def compute_first_derivatives_xy(smoothed_points: list[dict]) -> list[dict]:
    if len(smoothed_points) < 2:
        raise ValueError("At least 2 points are required to compute first derivatives")

    derived_points: list[dict] = []

    for idx, point in enumerate(smoothed_points):
        if idx == 0:
            next_point = smoothed_points[idx + 1]
            dt = next_point["t"] - point["t"]
            dx_dt = (next_point["x_smooth"] - point["x_smooth"]) / dt
            dy_dt = (next_point["y_smooth"] - point["y_smooth"]) / dt

        elif idx == len(smoothed_points) - 1:
            prev_point = smoothed_points[idx - 1]
            dt = point["t"] - prev_point["t"]
            dx_dt = (point["x_smooth"] - prev_point["x_smooth"]) / dt
            dy_dt = (point["y_smooth"] - prev_point["y_smooth"]) / dt

        else:
            prev_point = smoothed_points[idx - 1]
            next_point = smoothed_points[idx + 1]
            dt = next_point["t"] - prev_point["t"]
            dx_dt = (next_point["x_smooth"] - prev_point["x_smooth"]) / dt
            dy_dt = (next_point["y_smooth"] - prev_point["y_smooth"]) / dt

        derived_points.append(
            {
                **point,
                "dx_dt": dx_dt,
                "dy_dt": dy_dt,
            }
        )

    return derived_points


def compute_speed_from_derivatives(derived_points: list[dict]) -> list[dict]:
    speed_points: list[dict] = []

    for point in derived_points:
        speed = math.sqrt(point["dx_dt"] ** 2 + point["dy_dt"] ** 2)

        speed_points.append(
            {
                **point,
                "speed": speed,
            }
        )

    return speed_points

def compute_heading_from_derivatives(speed_points: list[dict]) -> list[dict]:
    heading_points: list[dict] = []

    for point in speed_points:
        dx_dt = point["dx_dt"]
        dy_dt = point["dy_dt"]

        heading = math.atan2(dy_dt, dx_dt)

        heading_points.append(
            {
                **point,
                "heading": heading,
            }
        )

    return heading_points

def wrap_angle_delta(angle_delta: float) -> float:
    return (angle_delta + math.pi) % (2 * math.pi) - math.pi


def compute_heading_delta(heading_points: list[dict]) -> list[dict]:
    heading_delta_points: list[dict] = []

    for idx, point in enumerate(heading_points):
        if idx == 0:
            heading_delta = None
        else:
            previous_heading = heading_points[idx - 1]["heading"]
            current_heading = point["heading"]
            heading_delta = wrap_angle_delta(current_heading - previous_heading)

        heading_delta_points.append(
            {
                **point,
                "heading_delta": heading_delta,
            }
        )

    return heading_delta_points

def compute_heading_delta_sign(
    heading_delta_points: list[dict],
    epsilon: float,
) -> list[dict]:
    heading_delta_sign_points: list[dict] = []

    for point in heading_delta_points:
        heading_delta = point["heading_delta"]

        if heading_delta is None:
            heading_delta_sign = None
        elif abs(heading_delta) <= epsilon:
            heading_delta_sign = 0
        elif heading_delta > 0:
            heading_delta_sign = 1
        else:
            heading_delta_sign = -1

        heading_delta_sign_points.append(
            {
                **point,
                "heading_delta_sign": heading_delta_sign,
            }
        )

    return heading_delta_sign_points

def summarize_same_sign_heading_delta_runs(points: list[dict]) -> list[dict]:
    same_sign_runs: list[dict] = []

    active_sign: int | None = None
    run_start_index: int | None = None
    cumulative_abs_heading_delta = 0.0

    def close_active_run(end_index: int) -> None:
        nonlocal active_sign
        nonlocal run_start_index
        nonlocal cumulative_abs_heading_delta

        if active_sign is None or run_start_index is None:
            return

        length = end_index - run_start_index + 1

        same_sign_runs.append(
            {
                "sign": active_sign,
                "start_index": run_start_index,
                "end_index": end_index,
                "length": length,
                "cumulative_abs_heading_delta": cumulative_abs_heading_delta,
                "mean_abs_heading_delta": cumulative_abs_heading_delta / length,
            }
        )

        active_sign = None
        run_start_index = None
        cumulative_abs_heading_delta = 0.0

    for point_index, point in enumerate(points):
        heading_delta_sign = point["heading_delta_sign"]
        heading_delta = point["heading_delta"]

        if heading_delta_sign not in {-1, 1}:
            close_active_run(point_index - 1)
            continue

        if active_sign is None:
            active_sign = heading_delta_sign
            run_start_index = point_index
            cumulative_abs_heading_delta = abs(heading_delta)
            continue

        if heading_delta_sign != active_sign:
            close_active_run(point_index - 1)
            active_sign = heading_delta_sign
            run_start_index = point_index
            cumulative_abs_heading_delta = abs(heading_delta)
            continue

        cumulative_abs_heading_delta += abs(heading_delta)

    close_active_run(len(points) - 1)

    return same_sign_runs

def summarize_windowed_heading_sweep(
    points: list[dict],
    window_size_points: int,
) -> dict:
    if window_size_points < 1:
        raise ValueError("window_size_points must be >= 1")

    windows: list[dict] = []

    max_window_heading_sweep = 0.0
    max_window_start_index: int | None = None
    max_window_end_index: int | None = None

    for end_index in range(len(points)):
        start_index = max(0, end_index - window_size_points + 1)
        window_points = points[start_index : end_index + 1]

        heading_delta_values = [
            abs(point["heading_delta"])
            for point in window_points
            if point.get("heading_delta") is not None
        ]

        heading_sweep = sum(heading_delta_values)
        heading_delta_count = len(heading_delta_values)

        if heading_delta_count == 0:
            mean_abs_heading_delta = 0.0
        else:
            mean_abs_heading_delta = heading_sweep / heading_delta_count

        window_entry = {
            "start_index": start_index,
            "end_index": end_index,
            "length": len(window_points),
            "heading_delta_count": heading_delta_count,
            "heading_sweep": heading_sweep,
            "mean_abs_heading_delta": mean_abs_heading_delta,
        }

        windows.append(window_entry)

        if (
            max_window_start_index is None
            or heading_sweep > max_window_heading_sweep
        ):
            max_window_heading_sweep = heading_sweep
            max_window_start_index = start_index
            max_window_end_index = end_index

    return {
        "mode": "trailing_point_count",
        "window_size_points": window_size_points,
        "windows": windows,
        "max_window_heading_sweep": max_window_heading_sweep,
        "max_window_start_index": max_window_start_index,
        "max_window_end_index": max_window_end_index,
    }

def summarize_windowed_spatial_containment(
    points: list[dict],
    window_size_points: int,
) -> dict:
    if window_size_points < 1:
        raise ValueError("window_size_points must be >= 1")

    path_length_epsilon = 1e-12

    windows: list[dict] = []

    min_displacement_ratio: float | None = None
    min_displacement_ratio_start_index: int | None = None
    min_displacement_ratio_end_index: int | None = None

    min_net_displacement: float | None = None
    min_net_displacement_start_index: int | None = None
    min_net_displacement_end_index: int | None = None

    max_path_length: float | None = None
    max_path_length_start_index: int | None = None
    max_path_length_end_index: int | None = None

    max_radius_range: float | None = None
    max_radius_range_start_index: int | None = None
    max_radius_range_end_index: int | None = None

    for end_index in range(len(points)):
        start_index = max(0, end_index - window_size_points + 1)
        window_points = points[start_index : end_index + 1]

        x_values = [point["x"] for point in window_points]
        y_values = [point["y"] for point in window_points]

        min_x = min(x_values)
        max_x = max(x_values)
        min_y = min(y_values)
        max_y = max(y_values)

        width = max_x - min_x
        height = max_y - min_y
        diagonal = math.sqrt(width**2 + height**2)

        path_length = 0.0
        for idx in range(1, len(window_points)):
            previous_point = window_points[idx - 1]
            current_point = window_points[idx]

            dx = current_point["x"] - previous_point["x"]
            dy = current_point["y"] - previous_point["y"]
            path_length += math.sqrt(dx**2 + dy**2)

        first_point = window_points[0]
        last_point = window_points[-1]
        net_dx = last_point["x"] - first_point["x"]
        net_dy = last_point["y"] - first_point["y"]
        net_displacement = math.sqrt(net_dx**2 + net_dy**2)

        if path_length <= path_length_epsilon:
            displacement_ratio = None
        else:
            displacement_ratio = net_displacement / path_length

        centroid_x = sum(x_values) / len(window_points)
        centroid_y = sum(y_values) / len(window_points)

        radius_values = []
        for point in window_points:
            radius_dx = point["x"] - centroid_x
            radius_dy = point["y"] - centroid_y
            radius_values.append(math.sqrt(radius_dx**2 + radius_dy**2))

        mean_radius = sum(radius_values) / len(radius_values)
        min_radius = min(radius_values)
        max_radius = max(radius_values)
        radius_range = max_radius - min_radius

        radius_variance = (
            sum((radius - mean_radius) ** 2 for radius in radius_values)
            / len(radius_values)
        )
        radius_std = math.sqrt(radius_variance)

        window_entry = {
            "start_index": start_index,
            "end_index": end_index,
            "length": len(window_points),
            "min_x": min_x,
            "max_x": max_x,
            "min_y": min_y,
            "max_y": max_y,
            "width": width,
            "height": height,
            "diagonal": diagonal,
            "path_length": path_length,
            "net_displacement": net_displacement,
            "displacement_ratio": displacement_ratio,
            "centroid_x": centroid_x,
            "centroid_y": centroid_y,
            "mean_radius": mean_radius,
            "min_radius": min_radius,
            "max_radius": max_radius,
            "radius_range": radius_range,
            "radius_std": radius_std,
        }

        windows.append(window_entry)

        if displacement_ratio is not None and (
            min_displacement_ratio is None
            or displacement_ratio < min_displacement_ratio
        ):
            min_displacement_ratio = displacement_ratio
            min_displacement_ratio_start_index = start_index
            min_displacement_ratio_end_index = end_index

        if (
            min_net_displacement is None
            or net_displacement < min_net_displacement
        ):
            min_net_displacement = net_displacement
            min_net_displacement_start_index = start_index
            min_net_displacement_end_index = end_index

        if max_path_length is None or path_length > max_path_length:
            max_path_length = path_length
            max_path_length_start_index = start_index
            max_path_length_end_index = end_index

        if max_radius_range is None or radius_range > max_radius_range:
            max_radius_range = radius_range
            max_radius_range_start_index = start_index
            max_radius_range_end_index = end_index

    return {
        "mode": "trailing_point_count",
        "window_size_points": window_size_points,
        "windows": windows,
        "min_displacement_ratio": min_displacement_ratio,
        "min_displacement_ratio_start_index": min_displacement_ratio_start_index,
        "min_displacement_ratio_end_index": min_displacement_ratio_end_index,
        "min_net_displacement": min_net_displacement,
        "min_net_displacement_start_index": min_net_displacement_start_index,
        "min_net_displacement_end_index": min_net_displacement_end_index,
        "max_path_length": max_path_length,
        "max_path_length_start_index": max_path_length_start_index,
        "max_path_length_end_index": max_path_length_end_index,
        "max_radius_range": max_radius_range,
        "max_radius_range_start_index": max_radius_range_start_index,
        "max_radius_range_end_index": max_radius_range_end_index,
    }

def summarize_windowed_fitted_circle_coherence(
    points: list[dict],
    window_size_points: int,
) -> dict:
    if window_size_points < 1:
        raise ValueError("window_size_points must be >= 1")

    collinearity_epsilon = 1e-12
    radius_epsilon = 1e-12

    windows: list[dict] = []

    fit_window_count = 0
    unfit_window_count = 0

    best_mean_radial_residual_ratio: float | None = None
    best_mean_radial_residual_ratio_start_index: int | None = None
    best_mean_radial_residual_ratio_end_index: int | None = None

    best_max_radial_residual_ratio: float | None = None
    best_max_radial_residual_ratio_start_index: int | None = None
    best_max_radial_residual_ratio_end_index: int | None = None

    best_full_window_mean_radial_residual_ratio: float | None = None
    best_full_window_mean_radial_residual_ratio_start_index: int | None = None
    best_full_window_mean_radial_residual_ratio_end_index: int | None = None

    best_full_window_max_radial_residual_ratio: float | None = None
    best_full_window_max_radial_residual_ratio_start_index: int | None = None
    best_full_window_max_radial_residual_ratio_end_index: int | None = None

    mean_radial_residual_ratios: list[float] = []

    def solve_3x3(matrix: list[list[float]], vector: list[float]) -> list[float] | None:
        augmented = [
            [matrix[row][0], matrix[row][1], matrix[row][2], vector[row]]
            for row in range(3)
        ]

        for pivot_index in range(3):
            pivot_row = max(
                range(pivot_index, 3),
                key=lambda row: abs(augmented[row][pivot_index]),
            )

            pivot_value = augmented[pivot_row][pivot_index]

            if abs(pivot_value) <= collinearity_epsilon:
                return None

            if pivot_row != pivot_index:
                augmented[pivot_index], augmented[pivot_row] = (
                    augmented[pivot_row],
                    augmented[pivot_index],
                )

            for column_index in range(pivot_index, 4):
                augmented[pivot_index][column_index] /= pivot_value

            for row in range(3):
                if row == pivot_index:
                    continue

                factor = augmented[row][pivot_index]
                for column_index in range(pivot_index, 4):
                    augmented[row][column_index] -= (
                        factor * augmented[pivot_index][column_index]
                    )

        return [augmented[row][3] for row in range(3)]

    def median(values: list[float]) -> float | None:
        if not values:
            return None

        sorted_values = sorted(values)
        midpoint = len(sorted_values) // 2

        if len(sorted_values) % 2 == 1:
            return sorted_values[midpoint]

        return (sorted_values[midpoint - 1] + sorted_values[midpoint]) / 2

    for end_index in range(len(points)):
        start_index = max(0, end_index - window_size_points + 1)
        window_points = points[start_index : end_index + 1]

        base_window_entry = {
            "start_index": start_index,
            "end_index": end_index,
            "length": len(window_points),
        }

        if len(window_points) < 3:
            windows.append(
                {
                    **base_window_entry,
                    "fit_status": "unfit",
                    "failure_reason": "insufficient_points",
                }
            )
            unfit_window_count += 1
            continue

        x_values = [point["x"] for point in window_points]
        y_values = [point["y"] for point in window_points]

        x_origin = sum(x_values) / len(x_values)
        y_origin = sum(y_values) / len(y_values)

        centered_points = [
            {
                "x": point["x"] - x_origin,
                "y": point["y"] - y_origin,
            }
            for point in window_points
        ]

        sum_xx = sum(point["x"] ** 2 for point in centered_points)
        sum_yy = sum(point["y"] ** 2 for point in centered_points)
        sum_xy = sum(point["x"] * point["y"] for point in centered_points)

        spread_determinant = (sum_xx * sum_yy) - (sum_xy**2)

        if abs(spread_determinant) <= collinearity_epsilon:
            windows.append(
                {
                    **base_window_entry,
                    "fit_status": "unfit",
                    "failure_reason": "near_collinear",
                }
            )
            unfit_window_count += 1
            continue

        # Algebraic circle fit in centered local coordinates:
        # x^2 + y^2 = a*x + b*y + c
        # local_center_x = a / 2
        # local_center_y = b / 2
        # radius = sqrt(c + local_center_x^2 + local_center_y^2)
        normal_matrix = [[0.0, 0.0, 0.0] for _ in range(3)]
        normal_vector = [0.0, 0.0, 0.0]

        for point in centered_points:
            x = point["x"]
            y = point["y"]
            row = [x, y, 1.0]
            target = (x**2) + (y**2)

            for row_index in range(3):
                normal_vector[row_index] += row[row_index] * target

                for column_index in range(3):
                    normal_matrix[row_index][column_index] += (
                        row[row_index] * row[column_index]
                    )

        solution = solve_3x3(normal_matrix, normal_vector)

        if solution is None:
            windows.append(
                {
                    **base_window_entry,
                    "fit_status": "unfit",
                    "failure_reason": "numerically_unstable",
                }
            )
            unfit_window_count += 1
            continue

        a_coefficient, b_coefficient, c_coefficient = solution

        local_center_x = a_coefficient / 2
        local_center_y = b_coefficient / 2
        radius_squared = (
            c_coefficient + (local_center_x**2) + (local_center_y**2)
        )

        if radius_squared <= 0 or not math.isfinite(radius_squared):
            windows.append(
                {
                    **base_window_entry,
                    "fit_status": "unfit",
                    "failure_reason": "numerically_unstable",
                }
            )
            unfit_window_count += 1
            continue

        radius = math.sqrt(radius_squared)

        if radius <= radius_epsilon:
            windows.append(
                {
                    **base_window_entry,
                    "fit_status": "unfit",
                    "failure_reason": "near_zero_radius",
                }
            )
            unfit_window_count += 1
            continue

        center_x = x_origin + local_center_x
        center_y = y_origin + local_center_y

        if (
            not math.isfinite(center_x)
            or not math.isfinite(center_y)
            or not math.isfinite(radius)
        ):
            windows.append(
                {
                    **base_window_entry,
                    "fit_status": "unfit",
                    "failure_reason": "numerically_unstable",
                }
            )
            unfit_window_count += 1
            continue

        point_radii = []
        radial_residuals = []

        for point in window_points:
            dx = point["x"] - center_x
            dy = point["y"] - center_y
            point_radius = math.sqrt((dx**2) + (dy**2))
            radial_residual = abs(point_radius - radius)

            if (
                not math.isfinite(point_radius)
                or not math.isfinite(radial_residual)
            ):
                point_radii = []
                radial_residuals = []
                break

            point_radii.append(point_radius)
            radial_residuals.append(radial_residual)

        if not point_radii or not radial_residuals:
            windows.append(
                {
                    **base_window_entry,
                    "fit_status": "unfit",
                    "failure_reason": "numerically_unstable",
                }
            )
            unfit_window_count += 1
            continue

        mean_point_radius = sum(point_radii) / len(point_radii)
        min_point_radius = min(point_radii)
        max_point_radius = max(point_radii)
        point_radius_range = max_point_radius - min_point_radius

        point_radius_variance = (
            sum((point_radius - mean_point_radius) ** 2 for point_radius in point_radii)
            / len(point_radii)
        )
        point_radius_std = math.sqrt(point_radius_variance)

        mean_radial_residual = sum(radial_residuals) / len(radial_residuals)
        max_radial_residual = max(radial_residuals)

        radial_residual_variance = (
            sum(
                (radial_residual - mean_radial_residual) ** 2
                for radial_residual in radial_residuals
            )
            / len(radial_residuals)
        )
        radial_residual_std = math.sqrt(radial_residual_variance)

        mean_radial_residual_ratio = mean_radial_residual / radius
        max_radial_residual_ratio = max_radial_residual / radius

        if (
            not math.isfinite(mean_radial_residual_ratio)
            or not math.isfinite(max_radial_residual_ratio)
        ):
            windows.append(
                {
                    **base_window_entry,
                    "fit_status": "unfit",
                    "failure_reason": "numerically_unstable",
                }
            )
            unfit_window_count += 1
            continue

        window_entry = {
            **base_window_entry,
            "fit_status": "fit",
            "failure_reason": None,
            "center_x": center_x,
            "center_y": center_y,
            "radius": radius,
            "mean_point_radius": mean_point_radius,
            "min_point_radius": min_point_radius,
            "max_point_radius": max_point_radius,
            "point_radius_range": point_radius_range,
            "point_radius_std": point_radius_std,
            "mean_radial_residual": mean_radial_residual,
            "max_radial_residual": max_radial_residual,
            "radial_residual_std": radial_residual_std,
            "mean_radial_residual_ratio": mean_radial_residual_ratio,
            "max_radial_residual_ratio": max_radial_residual_ratio,
        }

        windows.append(window_entry)
        fit_window_count += 1
        mean_radial_residual_ratios.append(mean_radial_residual_ratio)

        if (
            best_mean_radial_residual_ratio is None
            or mean_radial_residual_ratio < best_mean_radial_residual_ratio
        ):
            best_mean_radial_residual_ratio = mean_radial_residual_ratio
            best_mean_radial_residual_ratio_start_index = start_index
            best_mean_radial_residual_ratio_end_index = end_index

        if (
            best_max_radial_residual_ratio is None
            or max_radial_residual_ratio < best_max_radial_residual_ratio
        ):
            best_max_radial_residual_ratio = max_radial_residual_ratio
            best_max_radial_residual_ratio_start_index = start_index
            best_max_radial_residual_ratio_end_index = end_index

        if len(window_points) == window_size_points:
            if (
                best_full_window_mean_radial_residual_ratio is None
                or mean_radial_residual_ratio
                < best_full_window_mean_radial_residual_ratio
            ):
                best_full_window_mean_radial_residual_ratio = (
                    mean_radial_residual_ratio
                )
                best_full_window_mean_radial_residual_ratio_start_index = start_index
                best_full_window_mean_radial_residual_ratio_end_index = end_index

            if (
                best_full_window_max_radial_residual_ratio is None
                or max_radial_residual_ratio
                < best_full_window_max_radial_residual_ratio
            ):
                best_full_window_max_radial_residual_ratio = max_radial_residual_ratio
                best_full_window_max_radial_residual_ratio_start_index = start_index
                best_full_window_max_radial_residual_ratio_end_index = end_index

    return {
        "mode": "trailing_point_count",
        "window_size_points": window_size_points,
        "windows": windows,
        "fit_window_count": fit_window_count,
        "unfit_window_count": unfit_window_count,
        "best_mean_radial_residual_ratio": best_mean_radial_residual_ratio,
        "best_mean_radial_residual_ratio_start_index": (
            best_mean_radial_residual_ratio_start_index
        ),
        "best_mean_radial_residual_ratio_end_index": (
            best_mean_radial_residual_ratio_end_index
        ),
        "best_max_radial_residual_ratio": best_max_radial_residual_ratio,
        "best_max_radial_residual_ratio_start_index": (
            best_max_radial_residual_ratio_start_index
        ),
        "best_max_radial_residual_ratio_end_index": (
            best_max_radial_residual_ratio_end_index
        ),
        "best_full_window_mean_radial_residual_ratio": (
            best_full_window_mean_radial_residual_ratio
        ),
        "best_full_window_mean_radial_residual_ratio_start_index": (
            best_full_window_mean_radial_residual_ratio_start_index
        ),
        "best_full_window_mean_radial_residual_ratio_end_index": (
            best_full_window_mean_radial_residual_ratio_end_index
        ),
        "best_full_window_max_radial_residual_ratio": (
            best_full_window_max_radial_residual_ratio
        ),
        "best_full_window_max_radial_residual_ratio_start_index": (
            best_full_window_max_radial_residual_ratio_start_index
        ),
        "best_full_window_max_radial_residual_ratio_end_index": (
            best_full_window_max_radial_residual_ratio_end_index
        ),
        "median_mean_radial_residual_ratio": median(mean_radial_residual_ratios),
    }

def compute_cumulative_heading_sweep(
    heading_delta_points: list[dict],
) -> list[dict]:
    cumulative_heading_sweep_points: list[dict] = []
    cumulative_heading_sweep = 0.0

    for point in heading_delta_points:
        heading_delta = point["heading_delta"]

        if heading_delta is not None:
            cumulative_heading_sweep += abs(heading_delta)

        cumulative_heading_sweep_points.append(
            {
                **point,
                "cumulative_heading_sweep": cumulative_heading_sweep,
            }
        )

    return cumulative_heading_sweep_points


def compute_second_derivatives_xy(speed_points: list[dict]) -> list[dict]:
    if len(speed_points) < 3:
        raise ValueError("At least 3 points are required to compute second derivatives")

    accel_points: list[dict] = []

    for idx, point in enumerate(speed_points):
        if idx == 0:
            next_point = speed_points[idx + 1]
            dt = next_point["t"] - point["t"]
            d2x_dt2 = (next_point["dx_dt"] - point["dx_dt"]) / dt
            d2y_dt2 = (next_point["dy_dt"] - point["dy_dt"]) / dt

        elif idx == len(speed_points) - 1:
            prev_point = speed_points[idx - 1]
            dt = point["t"] - prev_point["t"]
            d2x_dt2 = (point["dx_dt"] - prev_point["dx_dt"]) / dt
            d2y_dt2 = (point["dy_dt"] - prev_point["dy_dt"]) / dt

        else:
            prev_point = speed_points[idx - 1]
            next_point = speed_points[idx + 1]
            dt = next_point["t"] - prev_point["t"]
            d2x_dt2 = (next_point["dx_dt"] - prev_point["dx_dt"]) / dt
            d2y_dt2 = (next_point["dy_dt"] - prev_point["dy_dt"]) / dt

        accel_points.append(
            {
                **point,
                "d2x_dt2": d2x_dt2,
                "d2y_dt2": d2y_dt2,
            }
        )

    return accel_points


def compute_curvature(accel_points: list[dict]) -> list[dict]:
    curvature_points: list[dict] = []

    for point in accel_points:
        dx_dt = point["dx_dt"]
        dy_dt = point["dy_dt"]
        d2x_dt2 = point["d2x_dt2"]
        d2y_dt2 = point["d2y_dt2"]

        numerator = (dx_dt * d2y_dt2) - (dy_dt * d2x_dt2)
        denominator = (dx_dt**2 + dy_dt**2) ** 1.5

        if denominator == 0:
            curvature = None
        else:
            curvature = numerator / denominator

        curvature_points.append(
            {
                **point,
                "curvature": curvature,
            }
        )

    return curvature_points


def apply_low_speed_curvature_mask(
    curvature_points: list[dict],
    speed_min_for_curvature: float,
) -> list[dict]:
    masked_points: list[dict] = []

    for point in curvature_points:
        curvature = point["curvature"]
        speed = point["speed"]

        if speed < speed_min_for_curvature:
            masked_curvature = None
            curvature_masked = True
        else:
            masked_curvature = curvature
            curvature_masked = False

        masked_points.append(
            {
                **point,
                "curvature": masked_curvature,
                "curvature_masked": curvature_masked,
            }
        )

    return masked_points
