import { useEffect, useState } from "react";
import "./App.css";
import PCMAWShell from "./components/PCMAWShell";
import { sampleArtifacts } from "./data/sampleArtifacts";
import type { ParentIntakeState } from "./types/pcmawIntakeTypes";
import { createInitialParentIntakeState } from "./utils/createInitialParentIntakeState";
import { attemptArtifactAdmission } from "./utils/attemptArtifactAdmission";

export default function App() {
  const candidateArtifact = sampleArtifacts.test_trace_001_v0;

  const [parentIntakeState, setParentIntakeState] =
    useState<ParentIntakeState>(createInitialParentIntakeState);

  useEffect(() => {
    setParentIntakeState((currentState) => {
      const { nextState } = attemptArtifactAdmission(
        currentState,
        candidateArtifact,
      );

      return nextState;
    });
  }, [candidateArtifact]);

  const lastIntakeResult = parentIntakeState.lastIntakeResult;
  const hasActiveArtifact = parentIntakeState.activeArtifact !== null;

  if (!parentIntakeState.activeArtifact) {
    return (
      <div className="pcmaw-shell">
        <div className="panel">
          <h2>Artifact Intake Failed</h2>
          <p>
            No active artifact is available because the candidate artifact was
            not admitted by the bounded parent intake check.
          </p>

          <div className="panel-section">
            <p>
              <strong>Intake status:</strong> {parentIntakeState.intakeStatus}
            </p>
            <p>
              <strong>Active artifact present:</strong>{" "}
              {hasActiveArtifact ? "Yes" : "No"}
            </p>
            <p>
              <strong>Last intake decision:</strong>{" "}
              {lastIntakeResult?.is_admissible ? "Admitted" : "Refused"}
            </p>

            {lastIntakeResult?.failure_stage && (
              <p>
                <strong>Failure stage:</strong> {lastIntakeResult.failure_stage}
              </p>
            )}
          </div>

          {lastIntakeResult?.errors?.length ? (
            <ul>
              {lastIntakeResult.errors.map((error, index) => (
                <li key={`${error.category}-${index}`}>
                  <strong>{error.category}:</strong> {error.message}
                </li>
              ))}
            </ul>
          ) : null}
        </div>
      </div>
    );
  }

  return (
    <div className="pcmaw-shell">
      <div className="panel">
        <h2>Parent Intake Status</h2>
        <p>
          <strong>Intake status:</strong> {parentIntakeState.intakeStatus}
        </p>
        <p>
          <strong>Active artifact present:</strong>{" "}
          {hasActiveArtifact ? "Yes" : "No"}
        </p>
        <p>
          <strong>Last intake decision:</strong>{" "}
          {lastIntakeResult?.is_admissible ? "Admitted" : "Refused"}
        </p>
      </div>

      <PCMAWShell activeArtifact={parentIntakeState.activeArtifact} />
    </div>
  );
}