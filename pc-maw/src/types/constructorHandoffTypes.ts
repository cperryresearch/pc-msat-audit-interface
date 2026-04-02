import type { ExtractedPlanarTrajectory } from "./trajectoryExtractionTypes";

export type ExtractionToConstructorHandoffError = {
  category: string;
  message: string;
};

export type ExtractionToConstructorHandoffResult = {
  can_handoff: boolean;
  errors: ExtractionToConstructorHandoffError[];
  constructorInput: ExtractedPlanarTrajectory | null;
};