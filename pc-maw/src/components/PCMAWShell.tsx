import type { PCMAWShellProps } from "../types/pcmawTypes";
import {
  buildOrientationSummary,
  buildPlaybackReadyTrace,
} from "../utils/pcmawDerivations";

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
 * - derive playback_ready_trace
 * - pass full artifact to audit-facing/supporting regions
 * - preserve parent/child boundaries
 */
export default function PCMAWShell({
  activeArtifact,
}: PCMAWShellProps) {
  const orientationSummary = buildOrientationSummary(activeArtifact);
  const playbackReadyTrace = buildPlaybackReadyTrace(activeArtifact);

  return (
    <div className="pcmaw-shell">
      <OrientationRegion {...orientationSummary} />

      <MainEngagementRegion
        playbackReadyTrace={playbackReadyTrace}
        activeArtifact={activeArtifact}
      />

      <SupportingDetailRegion artifact={activeArtifact} />
    </div>
  );
}