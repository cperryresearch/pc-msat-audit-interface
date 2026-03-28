import "./App.css";
import PCMAWShell from "./components/PCMAWShell";
import { sampleArtifact } from "./data/sampleArtifact";

export default function App() {
  return <PCMAWShell activeArtifact={sampleArtifact} />;
}