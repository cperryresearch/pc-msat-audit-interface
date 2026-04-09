import type { PCMAWShellProps } from "../types/pcmawTypes";
import { buildOrientationSummary } from "../utils/pcmawDerivations";

import OrientationRegion from "./OrientationRegion";
import MainEngagementRegion from "./MainEngagementRegion";
import SupportingDetailRegion from "./SupportingDetailRegion";

/**
 * PCMAWShell
 *
 * Top-level parent shell for a single active state_segmented_trace artifact.
 *
 * Locked responsibilities:
 * - retain parent-level ownership of the active artifact
 * - derive orientation summary
 * - receive parent-approved playback readiness + playback-ready trace
 * - pass full artifact to audit-facing/supporting regions
 * - preserve parent/child boundaries
 */
export default function PCMAWShell({
  activeArtifact,
  playbackReadiness,
  playbackReadyTrace,
}: PCMAWShellProps) {
  const orientationSummary = buildOrientationSummary(activeArtifact);

  return (
    <div className="pcmaw-shell">
      <OrientationRegion {...orientationSummary} />

      <MainEngagementRegion
        playbackReadiness={playbackReadiness}
        playbackReadyTrace={playbackReadyTrace}
        activeArtifact={activeArtifact}
      />

      <SupportingDetailRegion artifact={activeArtifact} />
    </div>
  );
}