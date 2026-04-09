import type {
  CanonicalMotionState,
  FailureStage,
  IntakeError,
  IntakeResult,
} from "../types/pcmawIntakeTypes";

const ALLOWED_CANONICAL_STATES: CanonicalMotionState[] = [
  "Straight",
  "Turn",
  "Hover",
  "Orb",
];

const ALLOWED_SUPPORT_STATUSES = [
  "accepted",
  "withheld",
  "unassigned",
] as const;

type AllowedSupportStatus = (typeof ALLOWED_SUPPORT_STATUSES)[number];

function isPlainObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value);
}

function isAllowedPointState(value: unknown): value is CanonicalMotionState | null {
  return value === null || ALLOWED_CANONICAL_STATES.includes(value as CanonicalMotionState);
}

function isAllowedRunValue(value: unknown): value is CanonicalMotionState {
  return ALLOWED_CANONICAL_STATES.includes(value as CanonicalMotionState);
}

function isAllowedSupportStatus(value: unknown): value is AllowedSupportStatus {
  return ALLOWED_SUPPORT_STATUSES.includes(value as AllowedSupportStatus);
}

function buildFailureResult(
  failureStage: FailureStage,
  errors: IntakeError[],
): IntakeResult {
  return {
    is_admissible: false,
    failure_stage: failureStage,
    errors,
  };
}

function buildSuccessResult(): IntakeResult {
  return {
    is_admissible: true,
    failure_stage: null,
    errors: [],
  };
}

export function runArtifactIntakeCheck(candidateArtifact: unknown): IntakeResult {
  const topLevelErrors: IntakeError[] = [];

  if (!isPlainObject(candidateArtifact)) {
    return buildFailureResult("top_level_structure", [
      {
        category: "invalid_candidate",
        message: "Candidate artifact must be a non-null object.",
      },
    ]);
  }

  const requiredTopLevelBlocks = [
    "artifact",
    "provenance",
    "input_spec",
    "processing",
    "state_model",
    "points",
    "run_summary",
  ] as const;

  for (const block of requiredTopLevelBlocks) {
    if (!(block in candidateArtifact)) {
      topLevelErrors.push({
        category: "missing_top_level_block",
        message: `Missing required top-level block: ${block}.`,
      });
      continue;
    }

    if (block === "points") {
      if (!Array.isArray(candidateArtifact.points)) {
        topLevelErrors.push({
          category: "invalid_points_container",
          message: "points must be an array.",
        });
      }
      continue;
    }

    if (block === "run_summary") {
      if (!isPlainObject(candidateArtifact.run_summary)) {
        topLevelErrors.push({
          category: "invalid_run_summary_container",
          message: "run_summary must be an object.",
        });
      }
      continue;
    }

    if (!isPlainObject(candidateArtifact[block])) {
      topLevelErrors.push({
        category: "invalid_top_level_block_type",
        message: `${block} must be an object.`,
      });
    }
  }

  if (topLevelErrors.length > 0) {
    return buildFailureResult("top_level_structure", topLevelErrors);
  }

  const runSummary = candidateArtifact.run_summary;
  const runSummaryErrors: IntakeError[] = [];

  if (!isPlainObject(runSummary)) {
    return buildFailureResult("run_summary_structure", [
      {
        category: "invalid_run_summary_container",
        message: "run_summary must be an object.",
      },
    ]);
  }

  if (!("candidate_state_runs" in runSummary)) {
    runSummaryErrors.push({
      category: "missing_run_summary_child",
      message: "run_summary.candidate_state_runs is required.",
    });
  } else if (!Array.isArray(runSummary.candidate_state_runs)) {
    runSummaryErrors.push({
      category: "invalid_run_summary_child_type",
      message: "run_summary.candidate_state_runs must be an array.",
    });
  }

  if (!("state_runs" in runSummary)) {
    runSummaryErrors.push({
      category: "missing_run_summary_child",
      message: "run_summary.state_runs is required.",
    });
  } else if (!Array.isArray(runSummary.state_runs)) {
    runSummaryErrors.push({
      category: "invalid_run_summary_child_type",
      message: "run_summary.state_runs must be an array.",
    });
  }

  if (runSummaryErrors.length > 0) {
    return buildFailureResult("run_summary_structure", runSummaryErrors);
  }

  const points = candidateArtifact.points;
  const pointsErrors: IntakeError[] = [];

  if (!Array.isArray(points)) {
    return buildFailureResult("points_structure", [
      {
        category: "invalid_points_container",
        message: "points must be an array.",
      },
    ]);
  }

  if (points.length === 0) {
    pointsErrors.push({
      category: "zero_point_artifact",
      message: "A parent-admissible artifact must contain at least one point.",
    });
  }

  if (pointsErrors.length > 0) {
    return buildFailureResult("points_structure", pointsErrors);
  }

  const pointEntryErrors: IntakeError[] = [];

  points.forEach((point, index) => {
    if (!isPlainObject(point)) {
      pointEntryErrors.push({
        category: "invalid_point_entry",
        message: `points[${index}] must be an object.`,
      });
      return;
    }

    if (typeof point.t !== "number") {
      pointEntryErrors.push({
        category: "invalid_point_field_type",
        message: `points[${index}].t must be a number.`,
      });
    }

    if (typeof point.x !== "number") {
      pointEntryErrors.push({
        category: "invalid_point_field_type",
        message: `points[${index}].x must be a number.`,
      });
    }

    if (typeof point.y !== "number") {
      pointEntryErrors.push({
        category: "invalid_point_field_type",
        message: `points[${index}].y must be a number.`,
      });
    }

    if (!("candidate_state" in point)) {
      pointEntryErrors.push({
        category: "missing_point_field",
        message: `points[${index}].candidate_state is required.`,
      });
    } else if (!isAllowedPointState(point.candidate_state)) {
      pointEntryErrors.push({
        category: "invalid_candidate_state",
        message: `points[${index}].candidate_state must be Straight, Turn, Hover, Orb, or null.`,
      });
    }

    if (!("state" in point)) {
      pointEntryErrors.push({
        category: "missing_point_field",
        message: `points[${index}].state is required.`,
      });
    } else if (point.state === "Unassigned") {
      pointEntryErrors.push({
        category: "display_state_not_admissible",
        message: `points[${index}].state may not be "Unassigned" at artifact level.`,
      });
    } else if (!isAllowedPointState(point.state)) {
      pointEntryErrors.push({
        category: "invalid_point_state",
        message: `points[${index}].state must be Straight, Turn, Hover, Orb, or null.`,
      });
    }

    if (!("support_status" in point)) {
      pointEntryErrors.push({
        category: "missing_point_field",
        message: `points[${index}].support_status is required.`,
      });
    } else if (!isAllowedSupportStatus(point.support_status)) {
      pointEntryErrors.push({
        category: "invalid_support_status",
        message: `points[${index}].support_status must be accepted, withheld, or unassigned.`,
      });
    }
  });

  if (pointEntryErrors.length > 0) {
    return buildFailureResult("point_entry_structure", pointEntryErrors);
  }

  const runEntryErrors: IntakeError[] = [];

  const runGroups = [
    {
      label: "run_summary.candidate_state_runs",
      expectedField: "candidate_state",
      entries: runSummary.candidate_state_runs,
    },
    {
      label: "run_summary.state_runs",
      expectedField: "state",
      entries: runSummary.state_runs,
    },
  ] as const;

  runGroups.forEach(({ label, expectedField, entries }) => {
    if (!Array.isArray(entries)) {
      runEntryErrors.push({
        category: "invalid_run_group",
        message: `${label} must be an array.`,
      });
      return;
    }

    entries.forEach((entry, index) => {
      if (!isPlainObject(entry)) {
        runEntryErrors.push({
          category: "invalid_run_entry",
          message: `${label}[${index}] must be an object.`,
        });
        return;
      }

      if (typeof entry.field !== "string") {
        runEntryErrors.push({
          category: "invalid_run_field_type",
          message: `${label}[${index}].field must be a string.`,
        });
      } else if (entry.field !== expectedField) {
        runEntryErrors.push({
          category: "unexpected_run_field_value",
          message: `${label}[${index}].field must be "${expectedField}".`,
        });
      }

      if (!isAllowedRunValue(entry.value)) {
        runEntryErrors.push({
          category: "invalid_run_value",
          message: `${label}[${index}].value must be Straight, Turn, Hover, or Orb.`,
        });
      }

      if (!isInteger(entry.start_index)) {
        runEntryErrors.push({
          category: "invalid_run_index_type",
          message: `${label}[${index}].start_index must be an integer.`,
        });
      }

      if (!isInteger(entry.end_index)) {
        runEntryErrors.push({
          category: "invalid_run_index_type",
          message: `${label}[${index}].end_index must be an integer.`,
        });
      }

      if (!isInteger(entry.length)) {
        runEntryErrors.push({
          category: "invalid_run_length_type",
          message: `${label}[${index}].length must be an integer.`,
        });
      }

      if (isInteger(entry.start_index) && entry.start_index < 0) {
        runEntryErrors.push({
          category: "invalid_run_index_value",
          message: `${label}[${index}].start_index must be >= 0.`,
        });
      }

      if (
        isInteger(entry.start_index) &&
        isInteger(entry.end_index) &&
        entry.end_index < entry.start_index
      ) {
        runEntryErrors.push({
          category: "invalid_run_index_order",
          message: `${label}[${index}].end_index must be >= start_index.`,
        });
      }

      if (isInteger(entry.length) && entry.length < 1) {
        runEntryErrors.push({
          category: "invalid_run_length_value",
          message: `${label}[${index}].length must be >= 1.`,
        });
      }
    });
  });

  if (runEntryErrors.length > 0) {
    return buildFailureResult("run_entry_structure", runEntryErrors);
  }

  return buildSuccessResult();
}