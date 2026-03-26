import type { PlaybackPaneProps } from "../types/pcmawTypes";

export default function PlaybackPane({ trace }: PlaybackPaneProps) {
  return (
    <section className="pcmaw-playback-pane">
      <h2>Playback</h2>
      <p>Playback-ready points: {trace.length}</p>
      <div className="pcmaw-playback-placeholder">
        Playback region scaffold
      </div>
    </section>
  );
}