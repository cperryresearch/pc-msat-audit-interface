export type ExtractedTrajectorySourceType = "video" | "image_sequence";

export type ExtractedPlanarTrajectoryPoint = {
  t: number;
  x: number;
  y: number;
};

export type ExtractedPlanarTrajectory = {
  trajectory_id: string;
  provenance: {
    source_type: ExtractedTrajectorySourceType;
    source_id: string;
  };
  points: ExtractedPlanarTrajectoryPoint[];
};

export type ExtractionFailureStage =
  | "source_input_structure"
  | "target_selection"
  | "trajectory_object_structure"
  | "trajectory_points_structure"
  | "trajectory_ordering";

export type ExtractionError = {
  category: string;
  message: string;
};

export type ExtractionResult = {
  is_extracted: boolean;
  failure_stage: ExtractionFailureStage | null;
  errors: ExtractionError[];
  extractedTrajectory: ExtractedPlanarTrajectory | null;
};