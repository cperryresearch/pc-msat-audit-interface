import type { StateSegmentedTrace } from "../types/pcmawTypes";
import type {
  PlaybackReadinessError,
  PlaybackReadinessFailureStage,
  PlaybackReadinessResult,
} from "../types/pcmawPlaybackReadinessTypes";

const ALLOWED_ARTIFACT_LEVEL_STATES = new Set([
  "Straight",
  "Turn",
  "Hover",
  "Orb",
]);

function buildFailureResult(
  failureStage: PlaybackReadinessFailureStage,
  errors: PlaybackReadinessError[]
): PlaybackReadinessResult {
  return {
    isPlaybackReady: false,
    failureStage,
    errors,
  };
}

export function evaluatePlaybackReadiness(
  artifact: StateSegmentedTrace | null
): PlaybackReadinessResult {
  if (artifact === null) {
    return buildFailureResult("no_artifact", [
      {
        category: "playback_readiness",
        message: "No active artifact is available for playback evaluation.",
      },
    ]);
  }

  if (!("points" in artifact)) {
    return buildFailureResult("points_missing", [
      {
        category: "playback_readiness",
        message: "Artifact is missing required points array for playback.",
      },
    ]);
  }

  if (!Array.isArray(artifact.points)) {
    return buildFailureResult("points_missing", [
      {
        category: "playback_readiness",
        message: "Artifact points field is not an array.",
      },
    ]);
  }

  if (artifact.points.length < 1) {
    return buildFailureResult("points_empty", [
      {
        category: "playback_readiness",
        message: "Artifact points array is empty and cannot support playback.",
      },
    ]);
  }

  let previousT: number | null = null;

  for (let index = 0; index < artifact.points.length; index += 1) {
    const point = artifact.points[index];

    if (typeof point !== "object" || point === null || Array.isArray(point)) {
      return buildFailureResult("point_not_object", [
        {
          category: "playback_readiness",
          message: `Point at index ${index} is not a valid point object.`,
        },
      ]);
    }

    if (
      typeof point.t !== "number" ||
      Number.isNaN(point.t) ||
      typeof point.x !== "number" ||
      Number.isNaN(point.x) ||
      typeof point.y !== "number" ||
      Number.isNaN(point.y)
    ) {
      return buildFailureResult("point_core_field_invalid", [
        {
          category: "playback_readiness",
          message: `Point at index ${index} has invalid playback core field(s); t, x, and y must be numbers.`,
        },
      ]);
    }

    const stateIsValid =
      point.state === null || ALLOWED_ARTIFACT_LEVEL_STATES.has(point.state);

    if (!stateIsValid) {
      return buildFailureResult("point_state_invalid", [
        {
          category: "playback_readiness",
          message: `Point at index ${index} has invalid artifact-level state for playback.`,
        },
      ]);
    }

    if (previousT !== null && point.t < previousT) {
      return buildFailureResult("point_time_order_unusable", [
        {
          category: "playback_readiness",
          message: `Point at index ${index} has time value ${point.t} which is less than prior point time ${previousT}.`,
        },
      ]);
    }

    previousT = point.t;
  }

  return {
    isPlaybackReady: true,
    failureStage: null,
    errors: [],
  };
}