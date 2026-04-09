import type { MotionState } from "./pcmawTypes";

export type PlaybackReadableState = MotionState | null;

export type PlaybackReadinessFailureStage =
  | "no_artifact"
  | "points_missing"
  | "points_empty"
  | "point_not_object"
  | "point_core_field_invalid"
  | "point_state_invalid"
  | "point_time_order_unusable";

export type PlaybackReadinessError = {
  category: string;
  message: string;
};

export type PlaybackReadinessResult = {
  isPlaybackReady: boolean;
  failureStage: PlaybackReadinessFailureStage | null;
  errors: PlaybackReadinessError[];
};

export type PlaybackReadyPointLike = {
  t: number;
  x: number;
  y: number;
  state: PlaybackReadableState;
};