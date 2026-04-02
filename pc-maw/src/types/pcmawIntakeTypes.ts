import type { StateSegmentedTrace } from "./pcmawTypes";

export type CanonicalMotionState = "Straight" | "Turn" | "Hover" | "Orb";

export type IntakeStatus = "idle" | "active" | "intake_failed";

export type FailureStage =
  | "top_level_structure"
  | "run_summary_structure"
  | "points_structure"
  | "point_entry_structure"
  | "run_entry_structure";

export interface IntakeError {
  category: string;
  message: string;
}

export interface IntakeResult {
  is_admissible: boolean;
  failure_stage: FailureStage | null;
  errors: IntakeError[];
}

export interface ParentIntakeState {
  activeArtifact: StateSegmentedTrace | null;
  intakeStatus: IntakeStatus;
  lastIntakeResult: IntakeResult | null;
}