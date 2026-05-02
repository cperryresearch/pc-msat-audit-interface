import type { AuditPaneProps, RunSummaryEntry } from "../types/pcmawTypes";

function formatRunLabel(run: RunSummaryEntry): string {
  return `${run.value} (${run.start_index}-${run.end_index}, len ${run.length})`;
}

type MetricCardProps = {
  label: string;
  value: string | number;
};

function MetricCard({ label, value }: MetricCardProps) {
  return (
    <div className="pcmaw-audit-metric-card">
      <span className="pcmaw-audit-metric-label">{label}</span>
      <strong className="pcmaw-audit-metric-value">{value}</strong>
    </div>
  );
}

type RunListProps = {
  runs: RunSummaryEntry[];
  emptyMessage: string;
};

function RunList({ runs, emptyMessage }: RunListProps) {
  if (runs.length === 0) {
    return <p className="pcmaw-audit-empty-state">{emptyMessage}</p>;
  }

  return (
    <ul className="pcmaw-audit-run-list">
      {runs.map((run, index) => (
        <li key={`${run.field}-${run.value}-${run.start_index}-${run.end_index}-${index}`} className="pcmaw-audit-run-item">
          {formatRunLabel(run)}
        </li>
      ))}
    </ul>
  );
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
      <div className="pcmaw-audit-header">
        <div>
          <h2>PC-MSAT</h2>
          <p className="pcmaw-audit-subtitle">
            Structural audit view for the active admitted trace artifact.
          </p>
        </div>
      </div>

      <div className="pcmaw-audit-overview">
        <MetricCard label="Artifact" value={artifactId} />
        <MetricCard label="Type" value={artifactType} />
        <MetricCard label="Points" value={artifact.points.length} />
        <MetricCard label="Candidate runs" value={candidateRuns.length} />
        <MetricCard label="Accepted runs" value={stateRuns.length} />
      </div>

      <div className="pcmaw-audit-summary-block">
        <div className="pcmaw-audit-section-heading">
          <h3>Accepted state summary</h3>
          <span>{stateRuns.length} runs</span>
        </div>

        <div className="pcmaw-audit-detail-box">
          <RunList runs={stateRuns} emptyMessage="No accepted state runs present." />
        </div>
      </div>

      <div className="pcmaw-audit-comparison-block">
        <div className="pcmaw-audit-section-heading">
          <h3>Candidate vs accepted runs</h3>
          <span>
            {candidateRuns.length} candidate / {stateRuns.length} accepted
          </span>
        </div>

        <div className="pcmaw-audit-comparison-grid">
          <div className="pcmaw-audit-comparison-column">
            <div className="pcmaw-audit-column-heading">
              <h4>Candidate runs</h4>
              <span>{candidateRuns.length}</span>
            </div>

            <div className="pcmaw-audit-detail-box pcmaw-audit-detail-box-tall">
              <RunList runs={candidateRuns} emptyMessage="No candidate runs present." />
            </div>
          </div>

          <div className="pcmaw-audit-comparison-column">
            <div className="pcmaw-audit-column-heading">
              <h4>Accepted state runs</h4>
              <span>{stateRuns.length}</span>
            </div>

            <div className="pcmaw-audit-detail-box pcmaw-audit-detail-box-tall">
              <RunList runs={stateRuns} emptyMessage="No accepted state runs present." />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}