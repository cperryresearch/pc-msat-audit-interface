import "./App.css";
import PCMAWShell from "./components/PCMAWShell";
import { sampleArtifacts } from "./data/sampleArtifacts";

const activeArtifact = sampleArtifacts.test_trace_001_v0;

export default function App() {
  return <PCMAWShell activeArtifact={activeArtifact} />;
}