import type {
  OrientationSummary,
  PlaybackReadyTracePoint,
  StateSegmentedTrace,
} from "../types/pcmawTypes";

/**
 * Safely extract a string field from a broad metadata block.
 */
function getStringField(
  block: Record<string, unknown> | undefined,
  key: string
): string | null {
  if (!block) return null;
  const value = block[key];
  return typeof value === "string" ? value : null;
}

/**
 * Build the bounded child payload for Playback.
 *
 * Locked v0 policy:
 * - preserve point order exactly
 * - include only x, y, and display state
 * - map canonical null state -> "Unassigned"
 * - do not mutate the parent-owned artifact
 */
export function buildPlaybackReadyTrace(
  activeArtifact: StateSegmentedTrace
): PlaybackReadyTracePoint[] {
  return activeArtifact.points.map((point) => ({
    x: point.x,
    y: point.y,
    state: point.state ?? "Unassigned",
  }));
}

/**
 * Build the compact parent-facing orientation summary.
 *
 * Locked v0 policy:
 * - workspaceTitle = "PC-MAW"
 * - artifactIdentity = artifact.artifact_id ?? provenance.source_id ?? "Unnamed artifact"
 * - artifactType = artifact.artifact_type ?? "state_segmented_trace"
 * - provenanceSummary = provenance.source_id ? `Source: ...` : "Source unavailable"
 * - statusLabel = "Active artifact"
 */
export function buildOrientationSummary(
  activeArtifact: StateSegmentedTrace
): OrientationSummary {
  const artifactId = getStringField(activeArtifact.artifact, "artifact_id");
  const artifactTypeField = getStringField(
    activeArtifact.artifact,
    "artifact_type"
  );
  const sourceId = getStringField(activeArtifact.provenance, "source_id");

  const artifactIdentity = artifactId ?? sourceId ?? "Unnamed artifact";
  const artifactType = artifactTypeField ?? "state_segmented_trace";
  const provenanceSummary = sourceId
    ? `Source: ${sourceId}`
    : "Source unavailable";

  return {
    workspaceTitle: "PC-MAW",
    artifactIdentity,
    artifactType,
    provenanceSummary,
    statusLabel: "Active artifact",
  };
}