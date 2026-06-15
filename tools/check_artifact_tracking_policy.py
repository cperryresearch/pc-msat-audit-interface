#!/usr/bin/env python3
"""
Check that new generated/private artifact paths are not tracked by Git.

This guard is baseline-aware. Some state-constructor sample inputs and
historical generated fixtures are already tracked in the repository. Those
files are explicitly allowed pending separate artifact-policy review.

The guard fails if additional protected generated/private artifact paths become
tracked later.

It does not inspect artifact contents, interpret review outputs, or make any
claim about candidacy, emission, release readiness, or physical origin.
"""

from __future__ import annotations

import fnmatch
import subprocess
import sys
from pathlib import PurePosixPath


DISALLOWED_TRACKED_PATTERNS = (
    "private_tools/*",
    "private_output/*",
    "state_constructor/input/*.csv",
    "state_constructor/input/export_*_runtime_csv.py",
    "state_constructor/output/*",
)


ALLOWED_BASELINE_TRACKED_ARTIFACTS = {
    "state_constructor/input/barn_swallow_2019-06-18_constructor_input.csv",
    "state_constructor/input/test_trace_001.csv",
    "state_constructor/input/test_trace_hover_001.csv",
    "state_constructor/input/test_trace_orb_like_001.csv",
    "state_constructor/input/test_trace_turn_001.csv",
    "state_constructor/input/uci_pedestrians_in_traffic_oid_39406.csv",
    "state_constructor/output/.gitkeep",
    "state_constructor/output/barn_swallow_2019-06-18_constructor_input_state_segmented_trace.json",
    "state_constructor/output/orb_support_window_scale_review_summary.md",
    "state_constructor/output/test_trace_001_state_segmented_trace.json",
    "state_constructor/output/test_trace_hover_001_state_segmented_trace.json",
    "state_constructor/output/test_trace_orb_like_001_state_segmented_trace.json",
    "state_constructor/output/test_trace_turn_001_state_segmented_trace.json",
    "state_constructor/output/uci_pedestrians_in_traffic_oid_39406_state_segmented_trace.json",
}


def git_ls_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return [
        str(PurePosixPath(line.strip()))
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def matches_protected_pattern(path: str) -> str | None:
    for pattern in DISALLOWED_TRACKED_PATTERNS:
        if fnmatch.fnmatch(path, pattern):
            return pattern
    return None


def find_policy_violations(paths: list[str]) -> list[tuple[str, str]]:
    violations: list[tuple[str, str]] = []

    for path in paths:
        matched_pattern = matches_protected_pattern(path)

        if matched_pattern is None:
            continue

        if path in ALLOWED_BASELINE_TRACKED_ARTIFACTS:
            continue

        violations.append((path, matched_pattern))

    return violations


def main() -> int:
    tracked_paths = git_ls_files()
    violations = find_policy_violations(tracked_paths)

    if not violations:
        print("Artifact tracking policy check passed.")
        print("No new protected generated/private artifact paths are tracked.")
        print(
            f"Baseline allowed protected artifacts: "
            f"{len(ALLOWED_BASELINE_TRACKED_ARTIFACTS)}"
        )
        return 0

    print("Artifact tracking policy check failed.", file=sys.stderr)
    print(
        "The following non-baseline protected generated/private artifact paths "
        "are tracked:",
        file=sys.stderr,
    )

    for path, pattern in violations:
        print(f"- {path}  matched pattern: {pattern}", file=sys.stderr)

    print(
        "\nIf any listed file is intentionally tracked, it requires separate "
        "artifact-policy review before being added to the baseline allowlist.",
        file=sys.stderr,
    )

    return 1


if __name__ == "__main__":
    raise SystemExit(main())