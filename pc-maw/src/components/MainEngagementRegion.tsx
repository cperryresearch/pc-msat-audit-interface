import type { MainEngagementRegionProps } from "../types/pcmawTypes";
import PlaybackPane from "./PlaybackPane";
import AuditPane from "./AuditPane";

export default function MainEngagementRegion({
  playbackReadyTrace,
  activeArtifact,
}: MainEngagementRegionProps) {
  return (
    <section className="pcmaw-main-engagement-region">
      <div className="pcmaw-main-engagement-layout">
        <PlaybackPane trace={playbackReadyTrace} />
        <AuditPane artifact={activeArtifact} />
      </div>
    </section>
  );
}