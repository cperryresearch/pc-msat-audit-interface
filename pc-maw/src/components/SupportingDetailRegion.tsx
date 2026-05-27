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

function formatBoolean(value: unknown): string {
  if (value === true) {
    return "Yes";
  }

  if (value === false) {
    return "No";
  }

  return "Unavailable";
}

function formatNumber(value: unknown): string {
  if (typeof value === "number" && Number.isFinite(value)) {
    return String(value);
  }

  return "Unavailable";
}

function formatText(value: unknown): string {
  if (typeof value === "string" && value.length > 0) {
    return value;
  }

  return "Unavailable";
}

function asRecord(value: unknown): Record<string, unknown> | null {
  if (value !== null && typeof value === "object" && !Array.isArray(value)) {
    return value as Record<string, unknown>;
  }

  return null;
}

function asRecordArray(value: unknown): Record<string, unknown>[] {
  if (!Array.isArray(value)) {
    return [];
  }

  return value
    .map((item) => asRecord(item))
    .filter((item): item is Record<string, unknown> => item !== null);
}

function getOrbCandidateSupport(
  processing: Record<string, unknown>
): Record<string, unknown> | null {
  const diagnostics = asRecord(processing.diagnostics);

  if (!diagnostics) {
    return null;
  }

  return asRecord(diagnostics.orb_candidate_support);
}

function OrbCandidateSupportDetail({
  orbCandidateSupport,
}: {
  orbCandidateSupport: Record<string, unknown> | null;
}) {
  if (!orbCandidateSupport) {
    return (
      <div className="pcmaw-supporting-detail-block">
        <h3>Orb candidate support</h3>
        <p>No orb candidate support diagnostic is present.</p>
      </div>
    );
  }

  const supportWindows = asRecordArray(orbCandidateSupport.support_windows);
  const withheldReasons = Array.isArray(orbCandidateSupport.withheld_reasons)
    ? orbCandidateSupport.withheld_reasons
    : [];

  const firstSupportWindow = supportWindows[0] ?? null;
  const firstHeadingSweep = asRecord(firstSupportWindow?.heading_sweep);
  const firstSpatialContainment = asRecord(
    firstSupportWindow?.spatial_containment
  );
  const firstFittedCircleCoherence = asRecord(
    firstSupportWindow?.fitted_circle_coherence
  );
  const firstRotationalRun = asRecord(firstSupportWindow?.rotational_run);

  return (
    <div className="pcmaw-supporting-detail-block">
      <h3>Orb candidate support</h3>
      <ul className="pcmaw-detail-list">
        <li>
          <strong>Support status:</strong>{" "}
          {formatText(orbCandidateSupport.support_status)}
        </li>
        <li>
          <strong>Support windows:</strong>{" "}
          {formatNumber(orbCandidateSupport.support_window_count)}
        </li>
        <li>
          <strong>Strict overlap required:</strong>{" "}
          {formatBoolean(orbCandidateSupport.strict_overlap_required)}
        </li>
        <li>
          <strong>Same window required:</strong>{" "}
          {formatBoolean(orbCandidateSupport.same_window_required)}
        </li>
        <li>
          <strong>Emits candidate state:</strong>{" "}
          {formatBoolean(orbCandidateSupport.emits_candidate_state)}
        </li>
        <li>
          <strong>Emits final state:</strong>{" "}
          {formatBoolean(orbCandidateSupport.emits_final_state)}
        </li>
      </ul>

      {withheldReasons.length > 0 && (
        <>
          <h4>Withheld reasons</h4>
          <ul className="pcmaw-detail-list">
            {withheldReasons.map((reason, index) => (
              <li key={`${String(reason)}-${index}`}>
                {formatMetadataValue(reason)}
              </li>
            ))}
          </ul>
        </>
      )}

      {firstSupportWindow && (
        <>
          <h4>First support window preview</h4>
          <ul className="pcmaw-detail-list">
            <li>
              <strong>Window span:</strong>{" "}
              {formatNumber(firstSupportWindow.start_index)} →{" "}
              {formatNumber(firstSupportWindow.end_index)}
            </li>
            <li>
              <strong>Window length:</strong>{" "}
              {formatNumber(firstSupportWindow.length)}
            </li>
            <li>
              <strong>Heading sweep:</strong>{" "}
              {formatNumber(firstHeadingSweep?.value)}
            </li>
            <li>
              <strong>Path length:</strong>{" "}
              {formatNumber(firstSpatialContainment?.path_length)}
            </li>
            <li>
              <strong>Displacement ratio:</strong>{" "}
              {formatNumber(firstSpatialContainment?.displacement_ratio)}
            </li>
            <li>
              <strong>Circle radius:</strong>{" "}
              {formatNumber(firstFittedCircleCoherence?.radius)}
            </li>
            <li>
              <strong>Mean radial residual ratio:</strong>{" "}
              {formatNumber(
                firstFittedCircleCoherence?.mean_radial_residual_ratio
              )}
            </li>
            <li>
              <strong>Max radial residual ratio:</strong>{" "}
              {formatNumber(
                firstFittedCircleCoherence?.max_radial_residual_ratio
              )}
            </li>
            <li>
              <strong>Rotational run span:</strong>{" "}
              {formatNumber(firstRotationalRun?.start_index)} →{" "}
              {formatNumber(firstRotationalRun?.end_index)}
            </li>
            <li>
              <strong>Rotational run cumulative heading delta:</strong>{" "}
              {formatNumber(
                firstRotationalRun?.cumulative_abs_heading_delta
              )}
            </li>
          </ul>
        </>
      )}

      <p>
        This diagnostic is read-only in PC-MAW. It does not emit Orb, alter
        point states, alter run summaries, or affect playback.
      </p>
    </div>
  );
}

export default function SupportingDetailRegion({
  artifact,
}: SupportingDetailRegionProps) {
  const artifactEntries = Object.entries(artifact.artifact);
  const inputSpecEntries = Object.entries(artifact.input_spec);
  const provenanceEntries = Object.entries(artifact.provenance);
  const processingEntries = Object.entries(artifact.processing);
  const orbCandidateSupport = getOrbCandidateSupport(artifact.processing);

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

        <OrbCandidateSupportDetail
          orbCandidateSupport={orbCandidateSupport}
        />
      </div>
    </section>
  );
}