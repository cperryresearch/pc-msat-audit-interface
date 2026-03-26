import type { OrientationRegionProps } from "../types/pcmawTypes";

export default function OrientationRegion({
  workspaceTitle,
  artifactIdentity,
  artifactType,
  provenanceSummary,
  statusLabel,
}: OrientationRegionProps) {
  return (
    <section className="pcmaw-orientation-region">
      <div className="pcmaw-orientation-layer-a">
        <h1>{workspaceTitle}</h1>
      </div>

      <div className="pcmaw-orientation-layer-b">
        <div>
          <strong>{artifactIdentity}</strong>
        </div>
        <div>{artifactType}</div>
        <div>{provenanceSummary}</div>
        <div>{statusLabel}</div>
      </div>
    </section>
  );
}