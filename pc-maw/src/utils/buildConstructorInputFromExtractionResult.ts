import type { ExtractionResult } from "../types/trajectoryExtractionTypes";
import type { ExtractionToConstructorHandoffResult } from "../types/constructorHandoffTypes";

function buildHandoffFailure(
  category: string,
  message: string,
): ExtractionToConstructorHandoffResult {
  return {
    can_handoff: false,
    errors: [
      {
        category,
        message,
      },
    ],
    constructorInput: null,
  };
}

export function buildConstructorInputFromExtractionResult(
  extractionResult: ExtractionResult,
): ExtractionToConstructorHandoffResult {
  if (!extractionResult.is_extracted) {
    return buildHandoffFailure(
      "extraction_not_successful",
      "Constructor handoff requires a successful extraction result.",
    );
  }

  if (extractionResult.extractedTrajectory === null) {
    return buildHandoffFailure(
      "extracted_trajectory_missing",
      "Constructor handoff requires a non-null extractedTrajectory.",
    );
  }

  return {
    can_handoff: true,
    errors: [],
    constructorInput: extractionResult.extractedTrajectory,
  };
}