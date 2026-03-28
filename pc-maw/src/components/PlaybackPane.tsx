import { useEffect, useRef, useState } from "react";
import type { PlaybackPaneProps, PlaybackDisplayState } from "../types/pcmawTypes";

const CANVAS_WIDTH = 520;
const CANVAS_HEIGHT = 320;
const CANVAS_PADDING = 32;
const START_MARKER_RADIUS = 4;
const CURRENT_MARKER_RADIUS = 5;
const LINE_WIDTH = 2;
const PLAYBACK_INTERVAL_MS = 500;

const STATE_COLORS: Record<PlaybackDisplayState, string> = {
  Straight: "#4A90E2",
  Turn: "#E3A008",
  Hover: "#2E9F6B",
  Orb: "#7E6E9E",
  Unassigned: "#888888",
};

type Bounds = {
  minX: number;
  maxX: number;
  minY: number;
  maxY: number;
};

function getTraceBounds(trace: PlaybackPaneProps["trace"]): Bounds {
  const xs = trace.map((point) => point.x);
  const ys = trace.map((point) => point.y);

  return {
    minX: Math.min(...xs),
    maxX: Math.max(...xs),
    minY: Math.min(...ys),
    maxY: Math.max(...ys),
  };
}

function createPointMapper(bounds: Bounds) {
  const { minX, maxX, minY, maxY } = bounds;

  const drawableWidth = CANVAS_WIDTH - CANVAS_PADDING * 2;
  const drawableHeight = CANVAS_HEIGHT - CANVAS_PADDING * 2;

  const dataWidth = maxX - minX;
  const dataHeight = maxY - minY;

  const safeDataWidth = dataWidth === 0 ? 1 : dataWidth;
  const safeDataHeight = dataHeight === 0 ? 1 : dataHeight;

  const scale = Math.min(
    drawableWidth / safeDataWidth,
    drawableHeight / safeDataHeight
  );

  const offsetX = CANVAS_PADDING + (drawableWidth - dataWidth * scale) / 2;
  const offsetY = CANVAS_PADDING + (drawableHeight - dataHeight * scale) / 2;

  return function mapPoint(point: { x: number; y: number }) {
    return {
      x: offsetX + (point.x - minX) * scale,
      y: CANVAS_HEIGHT - (offsetY + (point.y - minY) * scale),
    };
  };
}

export default function PlaybackPane({ trace }: PlaybackPaneProps) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const playbackTimerRef = useRef<number | null>(null);

  const [currentIndex, setCurrentIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    setCurrentIndex(0);
    setIsPlaying(false);
  }, [trace]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

    if (trace.length === 0) {
      ctx.font = "16px sans-serif";
      ctx.fillStyle = "#444";
      ctx.textAlign = "center";
      ctx.fillText(
        "No playback-ready trace loaded.",
        CANVAS_WIDTH / 2,
        CANVAS_HEIGHT / 2
      );
      return;
    }

    const bounds = getTraceBounds(trace);
    const mapPoint = createPointMapper(bounds);

    const startPoint = mapPoint(trace[0]);
    ctx.beginPath();
    ctx.arc(startPoint.x, startPoint.y, START_MARKER_RADIUS, 0, Math.PI * 2);
    ctx.fillStyle = "#444";
    ctx.fill();

    if (trace.length === 1) {
      return;
    }

    for (let index = 1; index <= currentIndex; index++) {
      const previousPoint = mapPoint(trace[index - 1]);
      const currentPoint = mapPoint(trace[index]);

      ctx.beginPath();
      ctx.moveTo(previousPoint.x, previousPoint.y);
      ctx.lineTo(currentPoint.x, currentPoint.y);
      ctx.strokeStyle = STATE_COLORS[trace[index].state];
      ctx.lineWidth = LINE_WIDTH;
      ctx.stroke();
    }

    const currentPoint = mapPoint(trace[currentIndex]);
    ctx.beginPath();
    ctx.arc(currentPoint.x, currentPoint.y, CURRENT_MARKER_RADIUS, 0, Math.PI * 2);
    ctx.fillStyle = "#ffffff";
    ctx.fill();
  }, [trace, currentIndex]);

  useEffect(() => {
    if (!isPlaying || trace.length <= 1) {
      if (playbackTimerRef.current !== null) {
        window.clearInterval(playbackTimerRef.current);
        playbackTimerRef.current = null;
      }
      return;
    }

    playbackTimerRef.current = window.setInterval(() => {
      setCurrentIndex((previousIndex) => {
        if (previousIndex >= trace.length - 1) {
          setIsPlaying(false);
          return previousIndex;
        }

        return previousIndex + 1;
      });
    }, PLAYBACK_INTERVAL_MS);

    return () => {
      if (playbackTimerRef.current !== null) {
        window.clearInterval(playbackTimerRef.current);
        playbackTimerRef.current = null;
      }
    };
  }, [isPlaying, trace]);

  function handlePlay() {
    if (trace.length <= 1) return;
    if (currentIndex >= trace.length - 1) {
      setCurrentIndex(0);
    }
    setIsPlaying(true);
  }

  function handlePause() {
    setIsPlaying(false);
  }

  function handleReplay() {
    if (trace.length === 0) return;
    setCurrentIndex(0);
    setIsPlaying(trace.length > 1);
  }

  function handleSliderChange(event: React.ChangeEvent<HTMLInputElement>) {
    setIsPlaying(false);
    setCurrentIndex(Number(event.target.value));
  }

  return (
    <section className="pcmaw-playback-pane">
      <h2>Playback</h2>
      <p>Playback-ready points: {trace.length}</p>

      <div className="pcmaw-playback-canvas-wrap">
        <canvas
          ref={canvasRef}
          width={CANVAS_WIDTH}
          height={CANVAS_HEIGHT}
          className="pcmaw-playback-canvas"
        />
      </div>

      <div className="pcmaw-playback-controls">
        <button type="button" onClick={handlePlay}>
          Play
        </button>
        <button type="button" onClick={handlePause}>
          Pause
        </button>
        <button type="button" onClick={handleReplay}>
          Replay
        </button>
      </div>

      <div className="pcmaw-playback-slider-wrap">
        <input
          type="range"
          min={0}
          max={Math.max(trace.length - 1, 0)}
          step={1}
          value={currentIndex}
          onChange={handleSliderChange}
          className="pcmaw-playback-slider"
        />
      </div>

      <p className="pcmaw-playback-status">
        Current index: {currentIndex} / {Math.max(trace.length - 1, 0)}
      </p>
    </section>
  );
}