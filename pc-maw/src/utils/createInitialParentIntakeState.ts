import type { ParentIntakeState } from "../types/pcmawIntakeTypes";

export function createInitialParentIntakeState(): ParentIntakeState {
  return {
    activeArtifact: null,
    intakeStatus: "idle",
    lastIntakeResult: null,
  };
}