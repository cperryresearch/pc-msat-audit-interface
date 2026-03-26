import type { AuditPaneProps } from "../types/pcmawTypes";

export default function AuditPane({ artifact }: AuditPaneProps) {
  const artifactId =
    typeof artifact.artifact?.artifact_id === "string"
      ? artifact.artifact.artifact_id
      : "Unnamed artifact";

  return (
    <section className="pcmaw-audit-pane">
      <h2>PC-MSAT</h2>
      <p>Artifact: {artifactId}</p>
      <p>Points: {artifact.points.length}</p>
      <div className="pcmaw-audit-placeholder">Audit region scaffold</div>
    </section>
  );
}