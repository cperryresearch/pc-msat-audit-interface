#!/usr/bin/env python3
"""
Validate an orb_candidacy_review JSON artifact as candidate-support evidence.

This helper is review-only.

It may accept a structurally valid orb_candidacy_review artifact as
candidate-support evidence for downstream review.

It never permits Orb emission.

It does not:
- modify the source artifact
- emit candidate_state: Orb
- emit final state: Orb
- change run_summary
- change PC-MAW admission
- change Playback behavior
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


SCHEMA_NAME = "orb_candidacy_acceptance_result"
SCHEMA_VERSION = "review_v0"

EXPECTED_INPUT_SCHEMA_NAME = "orb_candidacy_review"
EXPECTED_INPUT_SCHEMA_VERSION = "review_v0"

ACCEPTED_SUPPORT_STATUSES = {
    "limited_window_support",
    "multi_window_support",
    "multi_scale_support",
    "strong_multi_scale_candidate_review",
}

WITHHELD_STATUSES = {
    "withheld",
    "no_support",
}

REQUIRED_TOP_LEVEL_FIELDS = {
    "schema_name",
    "schema_version",
    "source_review",
    "review_metadata",
    "no_emission_boundary",
    "review_thresholds",
    "control_withholding_summary",
    "trace_review_status",
    "trace_review_summary",
    "qualifying_windows",
    "withheld_reasons",
    "input_errors",
}

REQUIRED_NO_EMISSION_FLAGS = {
    "review_only": True,
    "modifies_artifact": False,
    "emits_candidate_state": False,
    "emits_final_state": False,
    "changes_run_summary": False,
    "changes_pc_maw_admission": False,
    "changes_playback_behavior": False,
}


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def default_output_path(input_path: Path, output_dir: Optional[Path]) -> Path:
    name = input_path.name.replace(
        "_orb_candidacy_review.json",
        "_orb_candidacy_acceptance_result.json",
    )

    if name == input_path.name:
        name = input_path.stem + "_orb_candidacy_acceptance_result.json"

    if output_dir:
        return output_dir / name

    return input_path.with_name(name)


def add_failure(
    failures: List[str],
    details: List[str],
    code: str,
    detail: str,
) -> None:
    failures.append(code)
    details.append(f"{code}: {detail}")


def validate_top_level_structure(
    data: Dict[str, Any],
    failures: List[str],
    details: List[str],
) -> None:
    missing = sorted(REQUIRED_TOP_LEVEL_FIELDS - set(data.keys()))
    for field in missing:
        add_failure(
            failures,
            details,
            "missing_required_top_level_field",
            f"Missing top-level field: {field}",
        )


def validate_schema_identity(
    data: Dict[str, Any],
    failures: List[str],
    details: List[str],
) -> None:
    schema_name = data.get("schema_name")
    schema_version = data.get("schema_version")

    if schema_name != EXPECTED_INPUT_SCHEMA_NAME:
        add_failure(
            failures,
            details,
            "wrong_schema_name",
            f"Expected {EXPECTED_INPUT_SCHEMA_NAME!r}, got {schema_name!r}.",
        )

    if schema_version != EXPECTED_INPUT_SCHEMA_VERSION:
        add_failure(
            failures,
            details,
            "unsupported_schema_version",
            f"Expected {EXPECTED_INPUT_SCHEMA_VERSION!r}, got {schema_version!r}.",
        )


def validate_source_review(
    data: Dict[str, Any],
    failures: List[str],
    details: List[str],
) -> None:
    source_review = data.get("source_review")

    if not isinstance(source_review, dict):
        add_failure(
            failures,
            details,
            "missing_source_review_provenance",
            "source_review must be an object.",
        )
        return

    source_schema = source_review.get("schema_name")
    source_version = source_review.get("schema_version")

    if not source_schema:
        add_failure(
            failures,
            details,
            "missing_source_review_schema",
            "source_review.schema_name is missing.",
        )

    if not source_version:
        add_failure(
            failures,
            details,
            "missing_source_review_version",
            "source_review.schema_version is missing.",
        )

    if source_schema != "orb_support_window_scale_review":
        add_failure(
            failures,
            details,
            "unexpected_source_review_schema",
            f"Expected upstream schema 'orb_support_window_scale_review', got {source_schema!r}.",
        )


def validate_review_metadata(
    data: Dict[str, Any],
    failures: List[str],
    details: List[str],
) -> Tuple[Optional[str], Optional[int]]:
    metadata = data.get("review_metadata")

    if not isinstance(metadata, dict):
        add_failure(
            failures,
            details,
            "missing_review_metadata",
            "review_metadata must be an object.",
        )
        return None, None

    artifact_id = metadata.get("artifact_id")
    point_count = metadata.get("point_count")
    window_sizes = metadata.get("review_window_sizes")

    if not artifact_id:
        add_failure(
            failures,
            details,
            "missing_artifact_id",
            "review_metadata.artifact_id is missing.",
        )

    if not isinstance(point_count, int) or point_count < 0:
        add_failure(
            failures,
            details,
            "invalid_point_count",
            f"review_metadata.point_count must be a non-negative integer, got {point_count!r}.",
        )

    if not isinstance(window_sizes, list) or not window_sizes:
        add_failure(
            failures,
            details,
            "missing_review_window_sizes",
            "review_metadata.review_window_sizes must be a non-empty list.",
        )

    return artifact_id if isinstance(artifact_id, str) else None, point_count if isinstance(point_count, int) else None


def validate_no_emission_boundary(
    data: Dict[str, Any],
    failures: List[str],
    details: List[str],
) -> bool:
    boundary = data.get("no_emission_boundary")

    if not isinstance(boundary, dict):
        add_failure(
            failures,
            details,
            "missing_no_emission_boundary",
            "no_emission_boundary must be an object.",
        )
        return False

    verified = True

    for flag, expected in REQUIRED_NO_EMISSION_FLAGS.items():
        actual = boundary.get(flag)
        if actual is not expected:
            verified = False
            add_failure(
                failures,
                details,
                "no_emission_boundary_violation",
                f"{flag} must be {expected!r}, got {actual!r}.",
            )

    return verified


def validate_review_thresholds(
    data: Dict[str, Any],
    failures: List[str],
    details: List[str],
) -> None:
    thresholds = data.get("review_thresholds")

    if not isinstance(thresholds, dict) or not thresholds:
        add_failure(
            failures,
            details,
            "missing_review_thresholds",
            "review_thresholds must be a non-empty object.",
        )


def validate_input_errors(
    data: Dict[str, Any],
    failures: List[str],
    details: List[str],
) -> None:
    input_errors = data.get("input_errors")

    if not isinstance(input_errors, list):
        add_failure(
            failures,
            details,
            "missing_input_errors",
            "input_errors must be a list.",
        )
        return

    if input_errors:
        add_failure(
            failures,
            details,
            "source_review_input_errors_present",
            f"input_errors must be empty for acceptance, got {input_errors!r}.",
        )


def determine_control_preservation_status(
    data: Dict[str, Any],
    allow_provisional_controls: bool,
    failures: List[str],
    details: List[str],
) -> str:
    summary = data.get("control_withholding_summary")

    if not isinstance(summary, dict):
        add_failure(
            failures,
            details,
            "missing_control_withholding_summary",
            "control_withholding_summary must be an object.",
        )
        return "failed"

    controls_preserved = summary.get("controls_preserved")

    if controls_preserved is True:
        return "verified"

    if controls_preserved is False:
        add_failure(
            failures,
            details,
            "control_preservation_failed",
            "control_withholding_summary.controls_preserved is false.",
        )
        return "failed"

    if allow_provisional_controls:
        return "provisional"

    add_failure(
        failures,
        details,
        "control_preservation_not_checked",
        "controls_preserved is not true. Use --allow-provisional-controls only when control preservation has been checked separately.",
    )
    return "not_checked"


def validate_trace_review_status(
    data: Dict[str, Any],
    failures: List[str],
    details: List[str],
) -> Tuple[Optional[str], Optional[str]]:
    status = data.get("trace_review_status")
    summary = data.get("trace_review_summary")

    if not isinstance(status, str):
        add_failure(
            failures,
            details,
            "missing_trace_review_status",
            "trace_review_status must be a string.",
        )
        return None, None

    if not isinstance(summary, dict):
        add_failure(
            failures,
            details,
            "missing_trace_review_summary",
            "trace_review_summary must be an object.",
        )
        return status, None

    characterization = summary.get("support_characterization")
    total_count = summary.get("total_qualifying_window_count")
    scales = summary.get("qualifying_window_scales")

    if not isinstance(characterization, str):
        add_failure(
            failures,
            details,
            "missing_support_characterization",
            "trace_review_summary.support_characterization must be a string.",
        )

    if not isinstance(total_count, int) or total_count < 0:
        add_failure(
            failures,
            details,
            "invalid_total_qualifying_window_count",
            f"total_qualifying_window_count must be a non-negative integer, got {total_count!r}.",
        )
        total_count = None

    if not isinstance(scales, list):
        add_failure(
            failures,
            details,
            "invalid_qualifying_window_scales",
            "qualifying_window_scales must be a list.",
        )
        scales = None

    if status in WITHHELD_STATUSES:
        add_failure(
            failures,
            details,
            "trace_review_status_withheld",
            f"Status {status!r} is not candidate-support evidence.",
        )
        return status, None

    if status not in ACCEPTED_SUPPORT_STATUSES:
        add_failure(
            failures,
            details,
            "unsupported_trace_review_status",
            f"Status {status!r} is not accepted candidate-support evidence.",
        )
        return status, None

    if characterization != status:
        add_failure(
            failures,
            details,
            "status_characterization_mismatch",
            f"trace_review_status {status!r} does not match support_characterization {characterization!r}.",
        )

    if isinstance(total_count, int) and total_count <= 0:
        add_failure(
            failures,
            details,
            "candidate_support_without_qualifying_windows",
            "Candidate-support status requires total_qualifying_window_count > 0.",
        )

    if isinstance(scales, list) and len(scales) <= 0:
        add_failure(
            failures,
            details,
            "candidate_support_without_qualifying_scales",
            "Candidate-support status requires at least one qualifying window scale.",
        )

    if status == "limited_window_support":
        if total_count != 1:
            add_failure(
                failures,
                details,
                "limited_window_support_count_mismatch",
                f"limited_window_support expects exactly 1 qualifying window, got {total_count!r}.",
            )
        if isinstance(scales, list) and len(scales) != 1:
            add_failure(
                failures,
                details,
                "limited_window_support_scale_mismatch",
                f"limited_window_support expects exactly one qualifying scale, got {scales!r}.",
            )

    elif status == "multi_window_support":
        if isinstance(total_count, int) and total_count <= 1:
            add_failure(
                failures,
                details,
                "multi_window_support_count_mismatch",
                f"multi_window_support expects more than one qualifying window, got {total_count!r}.",
            )
        if isinstance(scales, list) and len(scales) != 1:
            add_failure(
                failures,
                details,
                "multi_window_support_scale_mismatch",
                f"multi_window_support expects exactly one qualifying scale, got {scales!r}.",
            )

    elif status in {"multi_scale_support", "strong_multi_scale_candidate_review"}:
        if isinstance(scales, list) and len(scales) <= 1:
            add_failure(
                failures,
                details,
                "multi_scale_support_scale_mismatch",
                f"{status} expects more than one qualifying scale, got {scales!r}.",
            )

    return status, status if status in ACCEPTED_SUPPORT_STATUSES else None


def validate_qualifying_windows(
    data: Dict[str, Any],
    accepted_support_level: Optional[str],
    failures: List[str],
    details: List[str],
) -> None:
    windows = data.get("qualifying_windows")

    if not isinstance(windows, list):
        add_failure(
            failures,
            details,
            "missing_qualifying_windows",
            "qualifying_windows must be a list.",
        )
        return

    if accepted_support_level and not windows:
        add_failure(
            failures,
            details,
            "candidate_support_without_qualifying_window_records",
            "Candidate-support status requires at least one qualifying window record.",
        )


def validate_orb_candidacy_acceptance(
    data: Dict[str, Any],
    *,
    source_path: Optional[Path] = None,
    allow_provisional_controls: bool = False,
) -> Dict[str, Any]:
    failures: List[str] = []
    failure_details: List[str] = []
    warnings: List[str] = []

    validate_top_level_structure(data, failures, failure_details)
    validate_schema_identity(data, failures, failure_details)
    validate_source_review(data, failures, failure_details)
    artifact_id, _point_count = validate_review_metadata(data, failures, failure_details)
    no_emission_boundary_verified = validate_no_emission_boundary(data, failures, failure_details)
    validate_review_thresholds(data, failures, failure_details)
    validate_input_errors(data, failures, failure_details)

    control_status = determine_control_preservation_status(
        data,
        allow_provisional_controls,
        failures,
        failure_details,
    )

    trace_review_status, accepted_support_level = validate_trace_review_status(
        data,
        failures,
        failure_details,
    )

    validate_qualifying_windows(data, accepted_support_level, failures, failure_details)

    if control_status == "provisional":
        warnings.append(
            "Control preservation was accepted provisionally. Verify controls across the anchor set before using this as stronger candidate-support evidence."
        )

    is_valid = not failures and accepted_support_level is not None

    return {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "artifact_id": artifact_id,
        "source_candidacy_review_path": str(source_path) if source_path else None,
        "source_trace_review_status": trace_review_status,
        "is_valid_candidate_support_evidence": is_valid,
        "accepted_support_level": accepted_support_level if is_valid else None,
        "blocking_failures": sorted(set(failures)),
        "blocking_failure_details": failure_details,
        "warnings": warnings,
        "no_emission_boundary_verified": no_emission_boundary_verified,
        "control_preservation_status": control_status,
        "emission_permitted": False,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an orb_candidacy_review JSON as review-only candidate-support evidence."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to one *_orb_candidacy_review.json file.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output JSON path. If omitted, writes beside the input file.",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Optional output directory. Ignored if --output is provided.",
    )
    parser.add_argument(
        "--allow-provisional-controls",
        action="store_true",
        help="Allow provisional acceptance when control preservation is documented outside the single input artifact.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir) if args.output_dir else None
    output_path = Path(args.output) if args.output else default_output_path(input_path, output_dir)

    data = load_json(input_path)
    result = validate_orb_candidacy_acceptance(
        data,
        source_path=input_path,
        allow_provisional_controls=args.allow_provisional_controls,
    )
    write_json(output_path, result)

    print("Orb candidacy acceptance validation")
    print(f"input : {input_path}")
    print(f"output: {output_path}")
    print(f"artifact_id: {result.get('artifact_id')}")
    print(
        "is_valid_candidate_support_evidence:",
        result.get("is_valid_candidate_support_evidence"),
    )
    print("accepted_support_level:", result.get("accepted_support_level"))
    print("control_preservation_status:", result.get("control_preservation_status"))
    print("no_emission_boundary_verified:", result.get("no_emission_boundary_verified"))
    print("emission_permitted:", result.get("emission_permitted"))

    failures = result.get("blocking_failures") or []
    if failures:
        print("blocking_failures:", failures)

    warnings = result.get("warnings") or []
    if warnings:
        print("warnings:", warnings)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())