import { useMemo, useState } from "react";
import {
  DEFAULT_SAMPLE_EXTRACTED_TRAJECTORY_ID,
  sampleExtractedTrajectories,
} from "../data/sampleExtractedTrajectories";
import { validateExtractedPlanarTrajectory } from "../utils/validateExtractedPlanarTrajectory";

export default function TrajectoryExtractionExercisePanel() {
  const [selectedTrajectoryId, setSelectedTrajectoryId] = useState<string>(
    DEFAULT_SAMPLE_EXTRACTED_TRAJECTORY_ID,
  );

  const selectedTrajectoryEntry = useMemo(() => {
    return (
      sampleExtractedTrajectories.find(
        (entry) => entry.id === selectedTrajectoryId,
      ) ?? sampleExtractedTrajectories[0]
    );
  }, [selectedTrajectoryId]);

  const extractionResult = useMemo(() => {
    if (!selectedTrajectoryEntry) {
      return null;
    }

    return validateExtractedPlanarTrajectory(
      selectedTrajectoryEntry.candidateTrajectory,
    );
  }, [selectedTrajectoryEntry]);

  return (
    <section className="extractor-exercise-panel">
      <h2>Trajectory Extraction Exercise</h2>

      <div className="candidate-selector-row">
        <label htmlFor="extracted-trajectory-selector">
          Sample extracted trajectory
        </label>
        <select
          id="extracted-trajectory-selector"
          value={selectedTrajectoryId}
          onChange={(event) => setSelectedTrajectoryId(event.target.value)}
        >
          {sampleExtractedTrajectories.map((entry) => (
            <option key={entry.id} value={entry.id}>
              {entry.label}
            </option>
          ))}
        </select>
      </div>

      <p className="candidate-description">
        {selectedTrajectoryEntry?.description ?? "No extracted trajectory selected."}
      </p>

      {extractionResult && (
        <div className="parent-status-block">
          <p>
            extractionStatus:{" "}
            {extractionResult.is_extracted ? "extracted" : "extraction_failed"}
          </p>
          <p>
            Extracted trajectory present:{" "}
            {extractionResult.extractedTrajectory ? "Yes" : "No"}
          </p>
          <p>
            Last extraction decision:{" "}
            {extractionResult.is_extracted ? "Accepted" : "Refused"}
          </p>

          {extractionResult.failure_stage && (
            <p>failure_stage: {extractionResult.failure_stage}</p>
          )}

          {extractionResult.errors.length > 0 && (
            <div className="parent-error-block">
              {extractionResult.errors.map((error, index) => (
                <p key={`${error.category}-${index}`}>
                  {error.category}: {error.message}
                </p>
              ))}
            </div>
          )}
        </div>
      )}
    </section>
  );
}