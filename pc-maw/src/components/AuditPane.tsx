import type { AuditPaneProps, RunSummaryEntry } from "../types/pcmawTypes";

function formatRunLabel(run: RunSummaryEntry): string {
  return `${run.value} (${run.start_index}-${run.end_index}, len ${run.length})`;
}

export default function AuditPane({ artifact }: AuditPaneProps) {
  const artifactId =
    typeof artifact.artifact?.artifact_id === "string"
      ? artifact.artifact.artifact_id
      : "Unnamed artifact";

  const artifactType =
    typeof artifact.artifact?.artifact_type === "string"
      ? artifact.artifact.artifact_type
      : "state_segmented_trace";

  const candidateRuns = artifact.run_summary.candidate_state_runs;
  const stateRuns = artifact.run_summary.state_runs;

  return (
    <section className="pcmaw-audit-pane">
      <h2>PC-MSAT</h2>
      <p>Artifact: {artifactId}</p>
      <p>Type: {artifactType}</p>
      <p>Points: {artifact.points.length}</p>
      <p>Candidate runs: {candidateRuns.length}</p>
      <p>State runs: {stateRuns.length}</p>

      <div className="pcmaw-audit-summary-block">
        <h3>State run summary</h3>

        {stateRuns.length === 0 ? (
          <p>No accepted state runs present.</p>
        ) : (
          <ul className="pcmaw-audit-run-list">
            {stateRuns.map((run, index) => (
              <li key={index} className="pcmaw-audit-run-item">
                {formatRunLabel(run)}
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}