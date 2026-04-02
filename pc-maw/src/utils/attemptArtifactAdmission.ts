import type {
  IntakeResult,
  ParentIntakeState,
} from "../types/pcmawIntakeTypes";
import type { StateSegmentedTrace } from "../types/pcmawTypes";
import { runArtifactIntakeCheck } from "./runArtifactIntakeCheck";

export interface AttemptArtifactAdmissionOutcome {
  nextState: ParentIntakeState;
  intakeResult: IntakeResult;
}

export function attemptArtifactAdmission(
  _currentState: ParentIntakeState,
  candidateArtifact: unknown,
): AttemptArtifactAdmissionOutcome {
  const intakeResult = runArtifactIntakeCheck(candidateArtifact);

  if (intakeResult.is_admissible) {
    return {
      nextState: {
        activeArtifact: candidateArtifact as StateSegmentedTrace,
        intakeStatus: "active",
        lastIntakeResult: intakeResult,
      },
      intakeResult,
    };
  }

  return {
    nextState: {
      activeArtifact: null,
      intakeStatus: "intake_failed",
      lastIntakeResult: intakeResult,
    },
    intakeResult,
  };
}