import type { ExtractionResult } from "../types/trajectoryExtractionTypes";
import { validateExtractedPlanarTrajectory } from "./validateExtractedPlanarTrajectory";

export function attemptTrajectoryExtraction(
  candidateSource: unknown,
): ExtractionResult {
  return validateExtractedPlanarTrajectory(candidateSource);
}