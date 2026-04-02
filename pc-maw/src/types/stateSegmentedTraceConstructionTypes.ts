import type { StateSegmentedTrace } from "./pcmawTypes";

export type ConstructionFailureStage =
  | "input_trajectory_structure"
  | "construction_processing"
  | "candidate_artifact_structure";

export type ConstructionError = {
  category: string;
  message: string;
};

export type ConstructionResult = {
  is_constructed: boolean;
  failure_stage: ConstructionFailureStage | null;
  errors: ConstructionError[];
  candidateArtifact: StateSegmentedTrace | null;
};