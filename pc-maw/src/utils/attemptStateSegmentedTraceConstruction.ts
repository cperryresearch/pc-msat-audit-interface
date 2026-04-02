import type { ExtractedPlanarTrajectory } from "../types/trajectoryExtractionTypes";
import type { StateSegmentedTrace } from "../types/pcmawTypes";
import type { ConstructionResult } from "../types/stateSegmentedTraceConstructionTypes";

function buildConstructionFailure(
  category: string,
  message: string,
  failureStage:
    | "input_trajectory_structure"
    | "construction_processing"
    | "candidate_artifact_structure",
): ConstructionResult {
  return {
    is_constructed: false,
    failure_stage: failureStage,
    errors: [
      {
        category,
        message,
      },
    ],
    candidateArtifact: null,
  };
}

export function attemptStateSegmentedTraceConstruction(
  extractedTrajectory: ExtractedPlanarTrajectory,
): ConstructionResult {
  if (
    extractedTrajectory === null ||
    typeof extractedTrajectory !== "object" ||
    Array.isArray(extractedTrajectory)
  ) {
    return buildConstructionFailure(
      "input_trajectory_invalid",
      "Constructor input must be an ExtractedPlanarTrajectory object.",
      "input_trajectory_structure",
    );
  }

  if (
    typeof extractedTrajectory.trajectory_id !== "string" ||
    extractedTrajectory.trajectory_id.trim() === ""
  ) {
    return buildConstructionFailure(
      "trajectory_id_invalid",
      "Constructor input trajectory_id must be a non-empty string.",
      "input_trajectory_structure",
    );
  }

  if (
    extractedTrajectory.provenance === null ||
    typeof extractedTrajectory.provenance !== "object" ||
    Array.isArray(extractedTrajectory.provenance)
  ) {
    return buildConstructionFailure(
      "provenance_invalid",
      "Constructor input provenance must be an object.",
      "input_trajectory_structure",
    );
  }

  if (!Array.isArray(extractedTrajectory.points)) {
    return buildConstructionFailure(
      "points_invalid",
      "Constructor input points must be an array.",
      "input_trajectory_structure",
    );
  }

  if (extractedTrajectory.points.length < 3) {
    return buildConstructionFailure(
      "points_too_short",
      "Constructor input points must contain at least 3 entries.",
      "input_trajectory_structure",
    );
  }

  for (let index = 0; index < extractedTrajectory.points.length; index += 1) {
    const point = extractedTrajectory.points[index];

    if (
      point === null ||
      typeof point !== "object" ||
      typeof point.t !== "number" ||
      typeof point.x !== "number" ||
      typeof point.y !== "number"
    ) {
      return buildConstructionFailure(
        "point_entry_invalid",
        `Constructor input points[${index}] must contain numeric t, x, and y values.`,
        "input_trajectory_structure",
      );
    }
  }

  for (let index = 1; index < extractedTrajectory.points.length; index += 1) {
    if (extractedTrajectory.points[index].t <= extractedTrajectory.points[index - 1].t) {
      return buildConstructionFailure(
        "time_not_strictly_increasing",
        `Constructor input points[${index}].t must be greater than points[${index - 1}].t.`,
        "input_trajectory_structure",
      );
    }
  }

  try {
    const points = extractedTrajectory.points;
    const candidateArtifact: StateSegmentedTrace = {
      artifact: {
        artifact_id: `${extractedTrajectory.trajectory_id}_state_segmented_trace`,
        artifact_type: "state_segmented_trace",
        ruleset_version: "v0",
      },
      provenance: {
        source_id: extractedTrajectory.provenance.source_id,
        input_path: `${extractedTrajectory.provenance.source_type}:${extractedTrajectory.provenance.source_id}`,
        output_path: `constructed:${extractedTrajectory.trajectory_id}_state_segmented_trace`,
      },
      input_spec: {
        projection: "planar",
        cadence_seconds:
          points.length >= 2 ? points[1].t - points[0].t : 0,
        n_points: points.length,
      },
      processing: {
        smoothing: {
          method: "unapplied",
          window: 0,
        },
        derivatives: {
          method: "unapplied",
        },
        masking: {
          speed_min_for_curvature: 0,
        },
        persistence: {
          min_run: 0,
        },
      },
      state_model: {},
      run_summary: {
        candidate_state_runs: [],
        state_runs: [],
      },
      points: points.map((point) => ({
        t: point.t,
        x: point.x,
        y: point.y,
        x_smooth: point.x,
        y_smooth: point.y,
        dx: null,
        dy: null,
        speed: null,
        curvature: null,
        curvature_masked: false,
        candidate_state: null,
        state: null,
        support_status: null,
      })),
    };

    if (
      candidateArtifact === null ||
      typeof candidateArtifact !== "object" ||
      !Array.isArray(candidateArtifact.points)
    ) {
      return buildConstructionFailure(
        "candidate_artifact_invalid",
        "Constructed candidate artifact failed basic structural assembly.",
        "candidate_artifact_structure",
      );
    }

    return {
      is_constructed: true,
      failure_stage: null,
      errors: [],
      candidateArtifact,
    };
  } catch (error) {
    return buildConstructionFailure(
      "construction_exception",
      error instanceof Error
        ? error.message
        : "Unknown constructor processing failure.",
      "construction_processing",
    );
  }
}