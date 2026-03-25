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
