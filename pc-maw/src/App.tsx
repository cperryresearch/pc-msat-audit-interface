import { useEffect, useMemo, useState } from "react";
import "./App.css";
import PCMAWShell from "./components/PCMAWShell";
import {
  DEFAULT_SAMPLE_CANDIDATE_ID,
  sampleCandidateArtifacts,
} from "./data/sampleArtifacts";
import type { ParentIntakeState } from "./types/pcmawIntakeTypes";
import { createInitialParentIntakeState } from "./utils/createInitialParentIntakeState";
import { attemptArtifactAdmission } from "./utils/attemptArtifactAdmission";
import TrajectoryExtractionExercisePanel from "./components/TrajectoryExtractionExercisePanel";
import ConstructorHandoffExercisePanel from "./components/ConstructorHandoffExercisePanel";
import ConstructorConstructionExercisePanel from "./components/ConstructorConstructionExercisePanel";

export default function App() {
  const [selectedCandidateId, setSelectedCandidateId] = useState<string>(
    DEFAULT_SAMPLE_CANDIDATE_ID,
  );

  const selectedCandidateEntry = useMemo(() => {
    return (
      sampleCandidateArtifacts.find(
        (entry) => entry.id === selectedCandidateId,
      ) ?? sampleCandidateArtifacts[0]
    );
  }, [selectedCandidateId]);

  const [parentIntakeState, setParentIntakeState] =
    useState<ParentIntakeState>(createInitialParentIntakeState);

  useEffect(() => {
    if (!selectedCandidateEntry) {
      return;
    }

    setParentIntakeState((currentState) => {
      const { nextState } = attemptArtifactAdmission(
        currentState,
        selectedCandidateEntry.candidateArtifact,
      );

      return nextState;
    });
  }, [selectedCandidateEntry]);

  const lastIntakeResult = parentIntakeState.lastIntakeResult;
  const hasActiveArtifact = parentIntakeState.activeArtifact !== null;

  return (
    <div className="app-shell">
            <TrajectoryExtractionExercisePanel />
            <ConstructorHandoffExercisePanel />
            <ConstructorConstructionExercisePanel />

      <section className="parent-intake-panel">
        <h1>PC-MAW</h1>

        <div className="candidate-selector-row">
          <label htmlFor="candidate-selector">Development candidate</label>
          <select
            id="candidate-selector"
            value={selectedCandidateId}
            onChange={(event) => setSelectedCandidateId(event.target.value)}
          >
            {sampleCandidateArtifacts.map((entry) => (
              <option key={entry.id} value={entry.id}>
                {entry.label}
              </option>
            ))}
          </select>
        </div>

        <p className="candidate-description">
          {selectedCandidateEntry?.description ?? "No candidate selected."}
        </p>

        <div className="parent-status-block">
          <p>intakeStatus: {parentIntakeState.intakeStatus}</p>
          <p>Active artifact present: {hasActiveArtifact ? "Yes" : "No"}</p>
          <p>
            Last intake decision:{" "}
            {lastIntakeResult === null
              ? "None"
              : lastIntakeResult.is_admissible
                ? "Admitted"
                : "Refused"}
          </p>

          {lastIntakeResult?.failure_stage && (
            <p>failure_stage: {lastIntakeResult.failure_stage}</p>
          )}

          {lastIntakeResult && lastIntakeResult.errors.length > 0 && (
            <div className="parent-error-block">
              {lastIntakeResult.errors.map((error, index) => (
                <p key={`${error.category}-${index}`}>
                  {error.category}: {error.message}
                </p>
              ))}
            </div>
          )}
        </div>
      </section>

      {parentIntakeState.activeArtifact ? (
        <PCMAWShell activeArtifact={parentIntakeState.activeArtifact} />
      ) : null}
    </div>
  );
}