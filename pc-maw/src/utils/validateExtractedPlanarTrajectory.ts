import type {
  ExtractedPlanarTrajectory,
  ExtractionError,
  ExtractionFailureStage,
  ExtractionResult,
} from "../types/trajectoryExtractionTypes";

function buildFailureResult(
  failureStage: ExtractionFailureStage,
  errors: ExtractionError[],
): ExtractionResult {
  return {
    is_extracted: false,
    failure_stage: failureStage,
    errors,
    extractedTrajectory: null,
  };
}

export function validateExtractedPlanarTrajectory(
  candidateTrajectory: unknown,
): ExtractionResult {
  if (
    candidateTrajectory === null ||
    typeof candidateTrajectory !== "object" ||
    Array.isArray(candidateTrajectory)
  ) {
    return buildFailureResult("trajectory_object_structure", [
      {
        category: "trajectory_object_invalid",
        message: "Extracted trajectory must be an object.",
      },
    ]);
  }

  const trajectoryRecord = candidateTrajectory as Record<string, unknown>;

  if (
    typeof trajectoryRecord.trajectory_id !== "string" ||
    trajectoryRecord.trajectory_id.trim() === ""
  ) {
    return buildFailureResult("trajectory_object_structure", [
      {
        category: "trajectory_id_invalid",
        message: "trajectory_id must be a non-empty string.",
      },
    ]);
  }

  if (
    trajectoryRecord.provenance === null ||
    typeof trajectoryRecord.provenance !== "object" ||
    Array.isArray(trajectoryRecord.provenance)
  ) {
    return buildFailureResult("trajectory_object_structure", [
      {
        category: "provenance_invalid",
        message: "provenance must be an object.",
      },
    ]);
  }

  const provenanceRecord = trajectoryRecord.provenance as Record<string, unknown>;

  if (
    provenanceRecord.source_type !== "video" &&
    provenanceRecord.source_type !== "image_sequence"
  ) {
    return buildFailureResult("trajectory_object_structure", [
      {
        category: "source_type_invalid",
        message:
          'provenance.source_type must be either "video" or "image_sequence".',
      },
    ]);
  }

  if (
    typeof provenanceRecord.source_id !== "string" ||
    provenanceRecord.source_id.trim() === ""
  ) {
    return buildFailureResult("trajectory_object_structure", [
      {
        category: "source_id_invalid",
        message: "provenance.source_id must be a non-empty string.",
      },
    ]);
  }

  if (!Array.isArray(trajectoryRecord.points)) {
    return buildFailureResult("trajectory_points_structure", [
      {
        category: "points_invalid",
        message: "points must be an array.",
      },
    ]);
  }

  if (trajectoryRecord.points.length < 3) {
    return buildFailureResult("trajectory_points_structure", [
      {
        category: "points_too_short",
        message: "points must contain at least 3 entries.",
      },
    ]);
  }

  const points = trajectoryRecord.points;

  for (let index = 0; index < points.length; index += 1) {
    const point = points[index];

    if (point === null || typeof point !== "object" || Array.isArray(point)) {
      return buildFailureResult("trajectory_points_structure", [
        {
          category: "point_entry_invalid",
          message: `points[${index}] must be an object.`,
        },
      ]);
    }

    const pointRecord = point as Record<string, unknown>;

    if (
      typeof pointRecord.t !== "number" ||
      typeof pointRecord.x !== "number" ||
      typeof pointRecord.y !== "number"
    ) {
      return buildFailureResult("trajectory_points_structure", [
        {
          category: "point_fields_invalid",
          message: `points[${index}] must contain numeric t, x, and y values.`,
        },
      ]);
    }
  }

  for (let index = 1; index < points.length; index += 1) {
    const previousPoint = points[index - 1] as Record<string, number>;
    const currentPoint = points[index] as Record<string, number>;

    if (currentPoint.t <= previousPoint.t) {
      return buildFailureResult("trajectory_ordering", [
        {
          category: "time_not_strictly_increasing",
          message: `points[${index}].t must be greater than points[${
            index - 1
          }].t.`,
        },
      ]);
    }
  }

  return {
    is_extracted: true,
    failure_stage: null,
    errors: [],
    extractedTrajectory: candidateTrajectory as ExtractedPlanarTrajectory,
  };
}