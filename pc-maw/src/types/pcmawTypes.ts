export type MotionState = "Straight" | "Turn" | "Hover" | "Orb";

export type PlaybackDisplayState =
  | "Straight"
  | "Turn"
  | "Hover"
  | "Orb"
  | "Unassigned";

export type SupportStatus = "supported" | "unsupported" | "withheld" | null;

export type StateSegmentedTracePoint = {
  t: number;
  x: number;
  y: number;
  x_smooth: number;
  y_smooth: number;
  dx: number | null;
  dy: number | null;
  speed: number | null;
  curvature: number | null;
  curvature_masked: boolean;
  candidate_state: MotionState | null;
  state: MotionState | null;
  support_status: SupportStatus;
};

export type RunSummaryEntry = {
  field: "candidate_state" | "state";
  value: MotionState;
  start_index: number;
  end_index: number;
  length: number;
};

export type StateSegmentedTrace = {
  artifact: Record<string, unknown>;
  provenance: Record<string, unknown>;
  input_spec: Record<string, unknown>;
  processing: Record<string, unknown>;
  state_model: Record<string, unknown>;
  points: StateSegmentedTracePoint[];
  run_summary: {
    candidate_state_runs: RunSummaryEntry[];
    state_runs: RunSummaryEntry[];
  };
};

export type PlaybackReadyTracePoint = {
  x: number;
  y: number;
  state: PlaybackDisplayState;
};

export type OrientationSummary = {
  workspaceTitle: string;
  artifactIdentity: string;
  artifactType: string;
  provenanceSummary: string;
  statusLabel: string;
};

export type PCMAWShellProps = {
  activeArtifact: StateSegmentedTrace;
};

export type OrientationRegionProps = OrientationSummary;

export type PlaybackPaneProps = {
  trace: PlaybackReadyTracePoint[];
};

export type AuditPaneProps = {
  artifact: StateSegmentedTrace;
};

export type MainEngagementRegionProps = {
  playbackReadyTrace: PlaybackReadyTracePoint[];
  activeArtifact: StateSegmentedTrace;
};

export type SupportingDetailRegionProps = {
  artifact: StateSegmentedTrace;
};