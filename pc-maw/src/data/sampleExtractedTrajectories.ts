export type SampleExtractedTrajectoryEntry = {
  id: string;
  label: string;
  description: string;
  candidateTrajectory: unknown;
};

const validExtractedTrajectory = {
  trajectory_id: "extracted_trace_valid_minimal",
  provenance: {
    source_type: "video",
    source_id: "sample_video_valid_001",
  },
  points: [
    { t: 0, x: 0, y: 0 },
    { t: 1, x: 1, y: 0 },
    { t: 2, x: 2, y: 0 },
    { t: 3, x: 3, y: 1 },
  ],
};

const invalidProvenanceExtractedTrajectory = {
  trajectory_id: "extracted_trace_invalid_provenance",
  provenance: {
    source_type: "audio",
    source_id: "",
  },
  points: [
    { t: 0, x: 0, y: 0 },
    { t: 1, x: 1, y: 0 },
    { t: 2, x: 2, y: 0 },
  ],
};

const shortPointsExtractedTrajectory = {
  trajectory_id: "extracted_trace_short_points",
  provenance: {
    source_type: "video",
    source_id: "sample_video_short_points_001",
  },
  points: [
    { t: 0, x: 0, y: 0 },
    { t: 1, x: 1, y: 0 },
  ],
};

const nonIncreasingTimeExtractedTrajectory = {
  trajectory_id: "extracted_trace_non_increasing_time",
  provenance: {
    source_type: "image_sequence",
    source_id: "sample_image_sequence_non_increasing_001",
  },
  points: [
    { t: 0, x: 0, y: 0 },
    { t: 1, x: 1, y: 0 },
    { t: 1, x: 2, y: 0 },
    { t: 2, x: 3, y: 1 },
  ],
};

export const DEFAULT_SAMPLE_EXTRACTED_TRAJECTORY_ID = "valid-extracted-trajectory";

export const sampleExtractedTrajectories: SampleExtractedTrajectoryEntry[] = [
  {
    id: "valid-extracted-trajectory",
    label: "Valid extracted trajectory",
    description:
      "Constructor-eligible extracted planar trajectory with valid provenance and strictly increasing time.",
    candidateTrajectory: validExtractedTrajectory,
  },
  {
    id: "invalid-provenance",
    label: "Invalid provenance",
    description:
      "Refusal trajectory with invalid provenance fields for source_type and source_id.",
    candidateTrajectory: invalidProvenanceExtractedTrajectory,
  },
  {
    id: "short-points",
    label: "Short points array",
    description:
      "Refusal trajectory with fewer than 3 trajectory points.",
    candidateTrajectory: shortPointsExtractedTrajectory,
  },
  {
    id: "non-increasing-time",
    label: "Non-increasing time",
    description:
      "Refusal trajectory with a duplicate timestamp that violates strict time ordering.",
    candidateTrajectory: nonIncreasingTimeExtractedTrajectory,
  },
];