import type { SupportingDetailRegionProps } from "../types/pcmawTypes";

function formatMetadataValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "Unavailable";
  }

  if (
    typeof value === "string" ||
    typeof value === "number" ||
    typeof value === "boolean"
  ) {
    return String(value);
  }

  return "Structured data";
}

export default function SupportingDetailRegion({
  artifact,
}: SupportingDetailRegionProps) {
  const artifactEntries = Object.entries(artifact.artifact);
  const inputSpecEntries = Object.entries(artifact.input_spec);
  const provenanceEntries = Object.entries(artifact.provenance);
  const processingEntries = Object.entries(artifact.processing);

  return (
    <section className="pcmaw-supporting-detail-region">
      <h2>Supporting Detail</h2>
      <p>Total points: {artifact.points.length}</p>

      <div className="pcmaw-supporting-detail-grid">
        <div className="pcmaw-supporting-detail-block">
          <h3>Artifact</h3>
          {artifactEntries.length === 0 ? (
            <p>No artifact fields present.</p>
          ) : (
            <ul className="pcmaw-detail-list">
              {artifactEntries.map(([key, value]) => (
                <li key={key}>
                  <strong>{key}:</strong> {formatMetadataValue(value)}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="pcmaw-supporting-detail-block">
          <h3>Input spec</h3>
          {inputSpecEntries.length === 0 ? (
            <p>No input spec fields present.</p>
          ) : (
            <ul className="pcmaw-detail-list">
              {inputSpecEntries.map(([key, value]) => (
                <li key={key}>
                  <strong>{key}:</strong> {formatMetadataValue(value)}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="pcmaw-supporting-detail-block">
          <h3>Provenance</h3>
          {provenanceEntries.length === 0 ? (
            <p>No provenance fields present.</p>
          ) : (
            <ul className="pcmaw-detail-list">
              {provenanceEntries.map(([key, value]) => (
                <li key={key}>
                  <strong>{key}:</strong> {formatMetadataValue(value)}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="pcmaw-supporting-detail-block">
          <h3>Processing</h3>
          {processingEntries.length === 0 ? (
            <p>No processing fields present.</p>
          ) : (
            <ul className="pcmaw-detail-list">
              {processingEntries.map(([key, value]) => (
                <li key={key}>
                  <strong>{key}:</strong> {formatMetadataValue(value)}
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="pcmaw-supporting-detail-block">
          <h3>Run summary</h3>
          <ul className="pcmaw-detail-list">
            <li>
              <strong>Candidate runs:</strong>{" "}
              {artifact.run_summary.candidate_state_runs.length}
            </li>
            <li>
              <strong>State runs:</strong>{" "}
              {artifact.run_summary.state_runs.length}
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
}