import type { MainEngagementRegionProps } from "../types/pcmawTypes";
import PlaybackPane from "./PlaybackPane";
import AuditPane from "./AuditPane";

export default function MainEngagementRegion({
  playbackReadiness,
  playbackReadyTrace,
  activeArtifact,
}: MainEngagementRegionProps) {
  return (
    <section className="pcmaw-main-engagement-region">
      <div className="pcmaw-main-engagement-layout">
        {playbackReadiness.isPlaybackReady && playbackReadyTrace ? (
          <PlaybackPane trace={playbackReadyTrace} />
        ) : (
          <div className="pcmaw-playback-unavailable">
            <h2>Playback</h2>
            <p>Playback is unavailable for the current admitted artifact.</p>

            {playbackReadiness.failureStage && (
              <p>
                playback_failure_stage: {playbackReadiness.failureStage}
              </p>
            )}

            {playbackReadiness.errors.length > 0 && (
              <div className="parent-error-block">
                {playbackReadiness.errors.map((error, index) => (
                  <p key={`main-engagement-playback-${error.category}-${index}`}>
                    {error.category}: {error.message}
                  </p>
                ))}
              </div>
            )}
          </div>
        )}

        <AuditPane artifact={activeArtifact} />
      </div>
    </section>
  );
}