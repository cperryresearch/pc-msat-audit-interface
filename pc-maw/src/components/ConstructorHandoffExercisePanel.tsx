import { useMemo, useState } from "react";
import {
  DEFAULT_SAMPLE_EXTRACTED_TRAJECTORY_ID,
  sampleExtractedTrajectories,
} from "../data/sampleExtractedTrajectories";
import { buildConstructorInputFromExtractionResult } from "../utils/buildConstructorInputFromExtractionResult";
import { attemptTrajectoryExtraction } from "../utils/attemptTrajectoryExtraction";

export default function ConstructorHandoffExercisePanel() {
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

    return attemptTrajectoryExtraction(
      selectedTrajectoryEntry.candidateTrajectory,
    );
  }, [selectedTrajectoryEntry]);

  const handoffResult = useMemo(() => {
    if (!extractionResult) {
      return null;
    }

    return buildConstructorInputFromExtractionResult(extractionResult);
  }, [extractionResult]);

  return (
    <section className="extractor-exercise-panel">
      <h2>Constructor Handoff Exercise</h2>

      <div className="candidate-selector-row">
        <label htmlFor="constructor-handoff-selector">
          Sample extracted trajectory
        </label>
        <select
          id="constructor-handoff-selector"
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

      {handoffResult && (
        <div className="parent-status-block">
          <p>handoffStatus: {handoffResult.can_handoff ? "ready" : "blocked"}</p>
          <p>
            Constructor input present:{" "}
            {handoffResult.constructorInput ? "Yes" : "No"}
          </p>
          <p>
            Last handoff decision:{" "}
            {handoffResult.can_handoff ? "Allowed" : "Refused"}
          </p>

          {handoffResult.errors.length > 0 && (
            <div className="parent-error-block">
              {handoffResult.errors.map((error, index) => (
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