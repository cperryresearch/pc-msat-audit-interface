export type SampleCandidateEntry = {
  id: string;
  label: string;
  description: string;
  candidateArtifact: unknown;
};

const validMinimalTraceArtifact = {
  artifact: {
    artifact_id: "sample_trace_valid_minimal",
    artifact_type: "state_segmented_trace",
    ruleset_version: "v0",
  },
  provenance: {
    source_id: "sample_source_valid_minimal",
    input_path: "sample/input/valid-minimal-trace.csv",
    output_path: "sample/output/valid-minimal-trace.json",
  },
  input_spec: {
    projection: "planar",
    cadence_seconds: 1,
    n_points: 6,
  },
  processing: {
    smoothing: {
      method: "moving_average",
      window: 3,
    },
    derivatives: {
      method: "finite_difference",
    },
    masking: {
      speed_min_for_curvature: 0.05,
    },
    persistence: {
      min_run: 3,
    },
  },
  state_model: {},
  run_summary: {
    candidate_state_runs: [
      {
        field: "candidate_state",
        value: "Straight",
        start_index: 0,
        end_index: 2,
        length: 3,
      },
      {
        field: "candidate_state",
        value: "Turn",
        start_index: 3,
        end_index: 5,
        length: 3,
      },
    ],
    state_runs: [
      {
        field: "state",
        value: "Straight",
        start_index: 0,
        end_index: 2,
        length: 3,
      },
      {
        field: "state",
        value: "Turn",
        start_index: 3,
        end_index: 5,
        length: 3,
      },
    ],
  },
  points: [
    {
      t: 0,
      x: 0,
      y: 0,
      x_smooth: 0,
      y_smooth: 0,
      dx_dt: 1,
      dy_dt: 0,
      speed: 1,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Straight",
      support_status: "accepted",
    },
    {
      t: 1,
      x: 1,
      y: 0,
      x_smooth: 1,
      y_smooth: 0,
      dx_dt: 1,
      dy_dt: 0,
      speed: 1,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Straight",
      support_status: "accepted",
    },
    {
      t: 2,
      x: 2,
      y: 0,
      x_smooth: 2,
      y_smooth: 0,
      dx_dt: 1,
      dy_dt: 0,
      speed: 1,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Straight",
      support_status: "accepted",
    },
    {
      t: 3,
      x: 3,
      y: 1,
      x_smooth: 3,
      y_smooth: 1,
      dx_dt: 1,
      dy_dt: 1,
      speed: 1.41,
      d2x_dt2: 0,
      d2y_dt2: 1,
      curvature: 0.2,
      curvature_masked: false,
      candidate_state: "Turn",
      state: "Turn",
      support_status: "accepted",
    },
    {
      t: 4,
      x: 4,
      y: 2,
      x_smooth: 4,
      y_smooth: 2,
      dx_dt: 1,
      dy_dt: 1,
      speed: 1.41,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0.2,
      curvature_masked: false,
      candidate_state: "Turn",
      state: "Turn",
      support_status: "accepted",
    },
    {
      t: 5,
      x: 5,
      y: 3,
      x_smooth: 5,
      y_smooth: 3,
      dx_dt: 1,
      dy_dt: 1,
      speed: 1.41,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0.2,
      curvature_masked: false,
      candidate_state: "Turn",
      state: "Turn",
      support_status: "accepted",
    },
  ],
};

const missingRunSummaryCandidateArtifact = {
  artifact: {
    artifact_id: "sample_trace_missing_run_summary",
    artifact_type: "state_segmented_trace",
    ruleset_version: "v0",
  },
  provenance: {
    source_id: "sample_source_missing_run_summary",
    input_path: "sample/input/missing-run-summary.csv",
    output_path: "sample/output/missing-run-summary.json",
  },
  input_spec: {
    projection: "planar",
    cadence_seconds: 1,
    n_points: 3,
  },
  processing: {
    smoothing: {
      method: "moving_average",
      window: 3,
    },
    derivatives: {
      method: "finite_difference",
    },
    masking: {
      speed_min_for_curvature: 0.05,
    },
    persistence: {
      min_run: 3,
    },
  },
  state_model: {},
  points: [
    {
      t: 0,
      x: 0,
      y: 0,
      x_smooth: 0,
      y_smooth: 0,
      dx_dt: 1,
      dy_dt: 0,
      speed: 1,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Straight",
      support_status: "accepted",
    },
    {
      t: 1,
      x: 1,
      y: 0,
      x_smooth: 1,
      y_smooth: 0,
      dx_dt: 1,
      dy_dt: 0,
      speed: 1,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Straight",
      support_status: "accepted",
    },
    {
      t: 2,
      x: 2,
      y: 0,
      x_smooth: 2,
      y_smooth: 0,
      dx_dt: 1,
      dy_dt: 0,
      speed: 1,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Straight",
      support_status: "accepted",
    },
  ],
};

const zeroPointCandidateArtifact = {
  artifact: {
    artifact_id: "sample_trace_zero_point",
    artifact_type: "state_segmented_trace",
    ruleset_version: "v0",
  },
  provenance: {
    source_id: "sample_source_zero_point",
    input_path: "sample/input/zero-point.csv",
    output_path: "sample/output/zero-point.json",
  },
  input_spec: {
    projection: "planar",
    cadence_seconds: 1,
    n_points: 0,
  },
  processing: {
    smoothing: {
      method: "moving_average",
      window: 3,
    },
    derivatives: {
      method: "finite_difference",
    },
    masking: {
      speed_min_for_curvature: 0.05,
    },
    persistence: {
      min_run: 3,
    },
  },
  state_model: {},
  run_summary: {
    candidate_state_runs: [],
    state_runs: [],
  },
  points: [],
};

const artifactLevelUnassignedCandidateArtifact = {
  artifact: {
    artifact_id: "sample_trace_artifact_level_unassigned",
    artifact_type: "state_segmented_trace",
    ruleset_version: "v0",
  },
  provenance: {
    source_id: "sample_source_artifact_level_unassigned",
    input_path: "sample/input/artifact-level-unassigned.csv",
    output_path: "sample/output/artifact-level-unassigned.json",
  },
  input_spec: {
    projection: "planar",
    cadence_seconds: 1,
    n_points: 3,
  },
  processing: {
    smoothing: {
      method: "moving_average",
      window: 3,
    },
    derivatives: {
      method: "finite_difference",
    },
    masking: {
      speed_min_for_curvature: 0.05,
    },
    persistence: {
      min_run: 3,
    },
  },
  state_model: {},
  run_summary: {
    candidate_state_runs: [
      {
        field: "candidate_state",
        value: "Straight",
        start_index: 0,
        end_index: 2,
        length: 3,
      },
    ],
    state_runs: [],
  },
  points: [
    {
      t: 0,
      x: 0,
      y: 0,
      x_smooth: 0,
      y_smooth: 0,
      dx_dt: 1,
      dy_dt: 0,
      speed: 1,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Straight",
      support_status: "accepted",
    },
    {
      t: 1,
      x: 1,
      y: 0,
      x_smooth: 1,
      y_smooth: 0,
      dx_dt: 1,
      dy_dt: 0,
      speed: 1,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Unassigned",
      support_status: "accepted",
    },
    {
      t: 2,
      x: 2,
      y: 0,
      x_smooth: 2,
      y_smooth: 0,
      dx_dt: 1,
      dy_dt: 0,
      speed: 1,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Straight",
      support_status: "accepted",
    },
  ],
};

const invalidRunCoherenceCandidateArtifact = {
  artifact: {
    artifact_id: "sample_trace_invalid_run_coherence",
    artifact_type: "state_segmented_trace",
    ruleset_version: "v0",
  },
  provenance: {
    source_id: "sample_source_invalid_run_coherence",
    input_path: "sample/input/invalid-run-coherence.csv",
    output_path: "sample/output/invalid-run-coherence.json",
  },
  input_spec: {
    projection: "planar",
    cadence_seconds: 1,
    n_points: 3,
  },
  processing: {
    smoothing: {
      method: "moving_average",
      window: 3,
    },
    derivatives: {
      method: "finite_difference",
    },
    masking: {
      speed_min_for_curvature: 0.05,
    },
    persistence: {
      min_run: 3,
    },
  },
  state_model: {},
  run_summary: {
    candidate_state_runs: [
      {
        field: "candidate_state",
        value: "Straight",
        start_index: 0,
        end_index: 2,
        length: 3,
      },
    ],
    state_runs: [
      {
        field: "state",
        value: "Straight",
        start_index: 2,
        end_index: 1,
        length: 1,
      },
    ],
  },
  points: [
    {
      t: 0,
      x: 0,
      y: 0,
      x_smooth: 0,
      y_smooth: 0,
      dx_dt: 1,
      dy_dt: 0,
      speed: 1,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Straight",
      support_status: "accepted",
    },
    {
      t: 1,
      x: 1,
      y: 0,
      x_smooth: 1,
      y_smooth: 0,
      dx_dt: 1,
      dy_dt: 0,
      speed: 1,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Straight",
      support_status: "accepted",
    },
    {
      t: 2,
      x: 2,
      y: 0,
      x_smooth: 2,
      y_smooth: 0,
      dx_dt: 1,
      dy_dt: 0,
      speed: 1,
      d2x_dt2: 0,
      d2y_dt2: 0,
      curvature: 0,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Straight",
      support_status: "accepted",
    },
  ],
};

export const DEFAULT_SAMPLE_CANDIDATE_ID = "valid-minimal-trace";

export const sampleCandidateArtifacts: SampleCandidateEntry[] = [
  {
    id: "valid-minimal-trace",
    label: "Valid minimal trace",
    description:
      "Admissible development-time candidate artifact for normal parent intake exercise.",
    candidateArtifact: validMinimalTraceArtifact,
  },
  {
    id: "missing-run-summary",
    label: "Missing run_summary",
    description:
      "Refusal candidate missing the required top-level run_summary block.",
    candidateArtifact: missingRunSummaryCandidateArtifact,
  },
  {
    id: "zero-point-artifact",
    label: "Zero-point artifact",
    description: "Refusal candidate with points present as an empty array.",
    candidateArtifact: zeroPointCandidateArtifact,
  },
  {
    id: "artifact-level-unassigned",
    label: 'Artifact-level "Unassigned"',
    description:
      'Refusal candidate using "Unassigned" as an artifact-level point state value.',
    candidateArtifact: artifactLevelUnassignedCandidateArtifact,
  },
  {
    id: "invalid-run-coherence",
    label: "Invalid run coherence",
    description:
      "Refusal candidate with a run entry coherence violation where end_index is less than start_index.",
    candidateArtifact: invalidRunCoherenceCandidateArtifact,
  },
];