import "./App.css";
import PCMAWShell from "./components/PCMAWShell";
import type { StateSegmentedTrace } from "./types/pcmawTypes";

const sampleArtifact: StateSegmentedTrace = {
  artifact: {
    artifact_id: "test_trace_001_v0",
    artifact_type: "state_segmented_trace",
  },
  provenance: {
    source_id: "test_trace_001",
  },
  input_spec: {},
  processing: {},
  state_model: {},
  points: [
    {
      x: 0,
      y: 0,
      x_smooth: 0,
      y_smooth: 0,
      dx: null,
      dy: null,
      speed: null,
      curvature: null,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Straight",
      support_status: null,
    },
    {
      x: 1,
      y: 0.2,
      x_smooth: 1,
      y_smooth: 0.2,
      dx: 1,
      dy: 0.2,
      speed: 1.02,
      curvature: 0.01,
      curvature_masked: false,
      candidate_state: "Straight",
      state: "Straight",
      support_status: null,
    },
    {
      x: 2,
      y: 0.9,
      x_smooth: 2,
      y_smooth: 0.9,
      dx: 1,
      dy: 0.7,
      speed: 1.22,
      curvature: 0.2,
      curvature_masked: false,
      candidate_state: "Turn",
      state: null,
      support_status: null,
    },
    {
      x: 3,
      y: 0.4,
      x_smooth: 3,
      y_smooth: 0.4,
      dx: 1,
      dy: -0.5,
      speed: 1.12,
      curvature: 0.3,
      curvature_masked: false,
      candidate_state: "Turn",
      state: "Turn",
      support_status: null,
    },
  ],
  run_summary: {
    candidate_state_runs: [
      {
        field: "candidate_state",
        value: "Straight",
        start_index: 0,
        end_index: 1,
        length: 2,
      },
      {
        field: "candidate_state",
        value: "Turn",
        start_index: 2,
        end_index: 3,
        length: 2,
      },
    ],
    state_runs: [
      {
        field: "state",
        value: "Straight",
        start_index: 0,
        end_index: 1,
        length: 2,
      },
      {
        field: "state",
        value: "Turn",
        start_index: 3,
        end_index: 3,
        length: 1,
      },
    ],
  },
};

export default function App() {
  return <PCMAWShell activeArtifact={sampleArtifact} />;
}