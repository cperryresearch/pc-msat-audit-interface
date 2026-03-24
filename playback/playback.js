let currentIndex = 0;
let playbackTimer = null;

const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const playBtn = document.getElementById("playBtn");
const pauseBtn = document.getElementById("pauseBtn");
const replayBtn = document.getElementById("replayBtn");
const timelineSlider = document.getElementById("timelineSlider");

const ALLOWED_STATES = ["Straight", "Turn", "Hover", "Orb"];

const PLAYBACK_CONFIG = {
  canvasPadding: 40,
  playbackIntervalMs: 500,
  startMarkerRadius: 4,
  startMarkerColor: "#444",
  lineWidth: 2,
  messageFont: "16px sans-serif",
  messageColor: "#444",
  messageInvalidTrace: "Invalid trace data",
  messageLoadFailure: "Failed to load trace data",
  stateColors: {
    Straight: "#4A90E2", // muted blue
    Turn: "#E3A008", // amber
    Hover: "#2E9F6B", // green
    Orb: "#7E6E9E", // muted violet
  },
};

function drawCenteredMessage(message) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.font = PLAYBACK_CONFIG.messageFont;
  ctx.fillStyle = PLAYBACK_CONFIG.messageColor;
  ctx.textAlign = "center";
  ctx.fillText(message, canvas.width / 2, canvas.height / 2);
}

function isValidTrace(trace) {
  if (!Array.isArray(trace)) {
    return false;
  }

  if (trace.length === 0) {
    return false;
  }

  for (const point of trace) {
    if (typeof point.x !== "number" || !Number.isFinite(point.x)) {
      return false;
    }

    if (typeof point.y !== "number" || !Number.isFinite(point.y)) {
      return false;
    }

    if (!ALLOWED_STATES.includes(point.state)) {
      return false;
    }
  }

  return true;
}

function getTraceBounds(trace) {
  const xs = trace.map((p) => p.x);
  const ys = trace.map((p) => p.y);

  return {
    minX: Math.min(...xs),
    maxX: Math.max(...xs),
    minY: Math.min(...ys),
    maxY: Math.max(...ys),
  };
}

function createPointMapper(bounds, canvasWidth, canvasHeight, padding) {
  const { minX, maxX, minY, maxY } = bounds;

  const width = canvasWidth - padding * 2;
  const height = canvasHeight - padding * 2;

  const dataWidth = maxX - minX;
  const dataHeight = maxY - minY;

  const safeDataWidth = dataWidth === 0 ? 1 : dataWidth;
  const safeDataHeight = dataHeight === 0 ? 1 : dataHeight;

  const scale = Math.min(width / safeDataWidth, height / safeDataHeight);

  const offsetX = padding + (width - dataWidth * scale) / 2;
  const offsetY = padding + (height - dataHeight * scale) / 2;

  return function mapPoint(p) {
    return {
      x: offsetX + (p.x - minX) * scale,
      y: canvasHeight - (offsetY + (p.y - minY) * scale),
    };
  };
}

function getStateColor(state) {
  const color = PLAYBACK_CONFIG.stateColors[state];

  if (!color) {
    throw new Error(`Unexpected state in getStateColor: ${state}`);
  }

  return color;
}

function bindControls(draw, traceLength) {
  timelineSlider.oninput = () => {
    pausePlayback();
    currentIndex = Number(timelineSlider.value);
    draw();
  };

  playBtn.onclick = () => {
    startPlayback(draw, traceLength);
  };

  pauseBtn.onclick = () => {
    pausePlayback();
  };

  replayBtn.onclick = () => {
    currentIndex = 0;
    draw();
    startPlayback(draw, traceLength);
  };
}

function initializePlayback(trace) {
  if (!isValidTrace(trace)) {
    drawCenteredMessage(PLAYBACK_CONFIG.messageInvalidTrace);
    return;
  }

  currentIndex = 0;
  pausePlayback();

  timelineSlider.max = trace.length - 1;
  timelineSlider.value = 0;

  const bounds = getTraceBounds(trace);
  const mapPoint = createPointMapper(
    bounds,
    canvas.width,
    canvas.height,
    PLAYBACK_CONFIG.canvasPadding
  );

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    timelineSlider.value = currentIndex;

    if (currentIndex === 0) {
      const p = mapPoint(trace[0]);

      ctx.beginPath();
      ctx.arc(p.x, p.y, PLAYBACK_CONFIG.startMarkerRadius, 0, Math.PI * 2);
      ctx.fillStyle = PLAYBACK_CONFIG.startMarkerColor;
      ctx.fill();
      return;
    }

    for (let i = 1; i <= currentIndex; i++) {
      const p0 = mapPoint(trace[i - 1]);
      const p1 = mapPoint(trace[i]);

      ctx.beginPath();
      ctx.moveTo(p0.x, p0.y);
      ctx.lineTo(p1.x, p1.y);

      ctx.strokeStyle = getStateColor(trace[i].state);
      ctx.lineWidth = PLAYBACK_CONFIG.lineWidth;
      ctx.stroke();
    }
  }

  bindControls(draw, trace.length);

  draw();
  startPlayback(draw, trace.length);
}

function startPlayback(draw, traceLength) {
  pausePlayback();

  playbackTimer = setInterval(() => {
    if (currentIndex < traceLength - 1) {
      currentIndex++;
      draw();
    } else {
      pausePlayback();
    }
  }, PLAYBACK_CONFIG.playbackIntervalMs);
}

function pausePlayback() {
  if (playbackTimer) {
    clearInterval(playbackTimer);
    playbackTimer = null;
  }
}

function loadTrace() {
  fetch("./trace.json")
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Failed to load trace.json: ${response.status}`);
      }
      return response.json();
    })
    .then((trace) => {
      initializePlayback(trace);
    })
    .catch((error) => {
      drawCenteredMessage(PLAYBACK_CONFIG.messageLoadFailure);
      console.error(error);
    });
}

// Standalone mode loads trace data from local trace.json.
// Embedded mode receives precomputed trace data from a parent interface.

function startStandalonePlayback() {
  loadTrace();
}

function startEmbeddedPlayback(trace) {
  initializePlayback(trace);
}

startStandalonePlayback();