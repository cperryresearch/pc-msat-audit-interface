import { useMemo, useState } from "react";
import {
  DEFAULT_SAMPLE_EXTRACTED_TRAJECTORY_ID,
  sampleExtractedTrajectories,
} from "../data/sampleExtractedTrajectories";
import { buildConstructorInputFromExtractionResult } from "../utils/buildConstructorInputFromExtractionResult";
import { attemptStateSegmentedTraceConstruction } from "../utils/attemptStateSegmentedTraceConstruction";
import { attemptTrajectoryExtraction } from "../utils/attemptTrajectoryExtraction";

export default function ConstructorConstructionExercisePanel() {
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

  const constructionResult = useMemo(() => {
    if (!handoffResult || !handoffResult.can_handoff || !handoffResult.constructorInput) {
      return null;
    }

    return attemptStateSegmentedTraceConstruction(
      handoffResult.constructorInput,
    );
  }, [handoffResult]);

  return (
    <section className="extractor-exercise-panel">
      <h2>Constructor Construction Exercise</h2>

      <div className="candidate-selector-row">
        <label htmlFor="constructor-construction-selector">
          Sample extracted trajectory
        </label>
        <select
          id="constructor-construction-selector"
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

      {handoffResult && !handoffResult.can_handoff && (
        <div className="parent-status-block">
          <p>constructionStatus: construction_blocked</p>
          <p>Candidate artifact present: No</p>
          <p>Last construction decision: Refused</p>

          <div className="parent-error-block">
            {handoffResult.errors.map((error, index) => (
              <p key={`${error.category}-${index}`}>
                {error.category}: {error.message}
              </p>
            ))}
          </div>
        </div>
      )}

      {constructionResult && (
        <div className="parent-status-block">
          <p>
            constructionStatus:{" "}
            {constructionResult.is_constructed ? "constructed" : "construction_failed"}
          </p>
          <p>
            Candidate artifact present:{" "}
            {constructionResult.candidateArtifact ? "Yes" : "No"}
          </p>
          <p>
            Last construction decision:{" "}
            {constructionResult.is_constructed ? "Accepted" : "Refused"}
          </p>

          {constructionResult.failure_stage && (
            <p>failure_stage: {constructionResult.failure_stage}</p>
          )}

          {constructionResult.errors.length > 0 && (
            <div className="parent-error-block">
              {constructionResult.errors.map((error, index) => (
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