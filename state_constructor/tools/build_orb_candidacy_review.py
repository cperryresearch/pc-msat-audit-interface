#!/usr/bin/env python3
"""
Build orb_candidacy_review JSON summaries from existing
orb_support_window_scale_review JSON outputs.

This helper is review-only.

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
from typing import Any, Dict, List, Optional


SCHEMA_NAME = "orb_candidacy_review"
SCHEMA_VERSION = "review_v0"

STRONG_MULTI_SCALE_MIN_TOTAL_WINDOWS = 25


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
        f.write("\n")


def require_review_input(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if data.get("schema_name") != "orb_support_window_scale_review":
        errors.append("Input schema_name is not orb_support_window_scale_review.")

    if "review_metadata" not in data or not isinstance(data["review_metadata"], dict):
        errors.append("Missing review_metadata object.")

    if "window_size_summaries" not in data or not isinstance(data["window_size_summaries"], list):
        errors.append("Missing window_size_summaries list.")

    if "no_emission_boundary" not in data or not isinstance(data["no_emission_boundary"], dict):
        errors.append("Missing no_emission_boundary object.")

    if "review_thresholds" not in data or not isinstance(data["review_thresholds"], dict):
        errors.append("Missing review_thresholds object.")

    return errors


def get_qualifying_summaries(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    qualifying: List[Dict[str, Any]] = []

    for summary in data.get("window_size_summaries", []):
        count = int(summary.get("combined_candidate_count") or 0)
        if count > 0:
            qualifying.append(summary)

    return qualifying


def flatten_top_windows(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    windows: List[Dict[str, Any]] = []

    for summary in data.get("window_size_summaries", []):
        window_size = summary.get("window_size")
        top = summary.get("top_combined_candidates") or []

        for item in top:
            if not isinstance(item, dict):
                continue
            window = dict(item)
            window["window_size"] = window_size
            window["review_status"] = "review_qualified"
            window["review_notes"] = []
            windows.append(window)

    return windows


def summarize_counts(data: Dict[str, Any]) -> Dict[str, Any]:
    per_scale: List[Dict[str, Any]] = []
    total = 0
    qualifying_scales: List[int] = []

    for summary in data.get("window_size_summaries", []):
        window_size = summary.get("window_size")
        count = int(summary.get("combined_candidate_count") or 0)
        total += count

        if count > 0 and window_size is not None:
            qualifying_scales.append(int(window_size))

        per_scale.append(
            {
                "window_size": window_size,
                "combined_candidate_count": count,
                "windows_evaluated": summary.get("windows_evaluated"),
                "fit_windows": summary.get("fit_windows"),
                "has_best_candidate": summary.get("best_combined_candidate") is not None,
            }
        )

    return {
        "total_qualifying_window_count": total,
        "qualifying_window_scales": qualifying_scales,
        "qualifying_scale_count": len(qualifying_scales),
        "per_scale": per_scale,
    }


def select_strongest_review_scale(data: Dict[str, Any]) -> Optional[int]:
    """
    Selects the scale with the highest combined_candidate_count.
    Ties are resolved by choosing the larger window size, because this review
    layer is interested in persistent support over broader spans.
    """
    best_size: Optional[int] = None
    best_count = 0

    for summary in data.get("window_size_summaries", []):
        size = summary.get("window_size")
        count = int(summary.get("combined_candidate_count") or 0)

        if size is None:
            continue

        if count > best_count:
            best_count = count
            best_size = int(size)
        elif count == best_count and count > 0 and best_size is not None:
            best_size = max(best_size, int(size))

    return best_size


def characterize_support(total_count: int, qualifying_scale_count: int) -> str:
    if total_count <= 0:
        return "no_support"

    if total_count == 1:
        return "limited_window_support"

    if qualifying_scale_count <= 1:
        return "multi_window_support"

    if total_count >= STRONG_MULTI_SCALE_MIN_TOTAL_WINDOWS:
        return "strong_multi_scale_candidate_review"

    return "multi_scale_support"


def trace_review_status_from_characterization(characterization: str) -> str:
    if characterization == "no_support":
        return "withheld"
    return characterization


def build_withheld_reasons(
    characterization: str,
    data: Dict[str, Any],
    input_errors: List[str],
) -> List[str]:
    reasons: List[str] = []

    if input_errors:
        reasons.extend(["malformed_review_input", "missing_required_diagnostics"])
        return sorted(set(reasons))

    if characterization == "no_support":
        strongest = data.get("strongest_rotational_run")

        if not strongest:
            reasons.append("insufficient_rotational_persistence")
        else:
            reasons.append("insufficient_combined_support")

        reasons.append("diagnostic_only_boundary_required")
        reasons.append("emission_contract_absent")
        return sorted(set(reasons))

    if characterization == "limited_window_support":
        reasons.append("single_window_only")
        reasons.append("diagnostic_only_boundary_required")
        reasons.append("emission_contract_absent")

    elif characterization == "multi_window_support":
        reasons.append("single_scale_only")
        reasons.append("diagnostic_only_boundary_required")
        reasons.append("emission_contract_absent")

    elif characterization in {"multi_scale_support", "strong_multi_scale_candidate_review"}:
        reasons.append("diagnostic_only_boundary_required")
        reasons.append("emission_contract_absent")
        reasons.append("cadence_not_normalized")

    else:
        reasons.append("diagnostic_only_boundary_required")
        reasons.append("emission_contract_absent")

    return sorted(set(reasons))


def infer_optional_characterization(
    artifact_id: Optional[str],
    characterization: str,
) -> List[str]:
    """
    Adds descriptive context only. These are not core statuses.
    """
    notes: List[str] = []
    artifact_id = artifact_id or ""

    if "test_trace_orb_like" in artifact_id:
        notes.append("small_scale_reference_support")

    if artifact_id.startswith("tii_") and characterization in {
        "multi_scale_support",
        "strong_multi_scale_candidate_review",
    }:
        notes.append("engineered_scale_sensitive_support")

    if artifact_id.startswith("white_stork") and characterization == "limited_window_support":
        notes.append("biological_limited_window_support")

    if artifact_id.startswith("white_stork") and characterization == "multi_window_support":
        notes.append("biological_multi_window_support")

    return notes


def build_orb_candidacy_review(data: Dict[str, Any], source_path: Path) -> Dict[str, Any]:
    input_errors = require_review_input(data)

    meta = data.get("review_metadata", {}) if isinstance(data.get("review_metadata"), dict) else {}
    artifact_id = meta.get("artifact_id")
    point_count = meta.get("points")
    review_window_sizes = meta.get("window_sizes") or []
    review_step = meta.get("step")

    counts = summarize_counts(data) if not input_errors else {
        "total_qualifying_window_count": 0,
        "qualifying_window_scales": [],
        "qualifying_scale_count": 0,
        "per_scale": [],
    }

    total_count = counts["total_qualifying_window_count"]
    qualifying_scale_count = counts["qualifying_scale_count"]

    support_characterization = characterize_support(total_count, qualifying_scale_count)
    trace_review_status = trace_review_status_from_characterization(support_characterization)

    strongest_review_scale = select_strongest_review_scale(data) if not input_errors else None
    qualifying_windows = flatten_top_windows(data) if not input_errors else []

    withheld_reasons = build_withheld_reasons(
        support_characterization,
        data,
        input_errors,
    )

    optional_characterizations = infer_optional_characterization(
        artifact_id,
        support_characterization,
    )

    no_emission_boundary = {
        "review_only": True,
        "modifies_artifact": False,
        "emits_candidate_state": False,
        "emits_final_state": False,
        "changes_run_summary": False,
        "changes_pc_maw_admission": False,
        "changes_playback_behavior": False,
    }

    return {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "source_review": {
            "schema_name": data.get("schema_name"),
            "schema_version": data.get("schema_version"),
            "path": str(source_path),
        },
        "review_metadata": {
            "artifact_id": artifact_id,
            "artifact_path": meta.get("artifact_path"),
            "point_count": point_count,
            "review_window_sizes": review_window_sizes,
            "review_step": review_step,
            "cadence_status": "unknown",
            "cadence_notes": [
                "Draft v0 uses point-count review windows inherited from orb_support_window_scale_review.",
                "Duration-normalized or cadence-aware windows are not yet implemented.",
            ],
        },
        "no_emission_boundary": no_emission_boundary,
        "review_thresholds": data.get("review_thresholds", {}),
        "control_withholding_summary": {
            "controls_checked": [],
            "controls_preserved": None,
            "notes": [
                "This single-file helper does not verify control preservation by itself.",
                "Control preservation should be evaluated across the full anchor set.",
            ],
        },
        "trace_review_status": trace_review_status,
        "trace_review_summary": {
            "support_characterization": support_characterization,
            "optional_characterizations": optional_characterizations,
            "total_qualifying_window_count": total_count,
            "qualifying_window_scales": counts["qualifying_window_scales"],
            "qualifying_scale_count": qualifying_scale_count,
            "strongest_review_scale": strongest_review_scale,
            "strongest_rotational_run": data.get("strongest_rotational_run"),
            "scale_counts": counts["per_scale"],
            "scale_cadence_caveats": [
                "Review status is scale-sensitive.",
                "Absence of support at one point-count window size does not prove absence at another scale.",
                "Support at any review scale does not permit Orb emission.",
            ],
        },
        "qualifying_windows": qualifying_windows,
        "withheld_reasons": withheld_reasons,
        "input_errors": input_errors,
    }


def default_output_path(input_path: Path, output_dir: Optional[Path]) -> Path:
    name = input_path.name.replace(
        "_orb_support_window_scale_review.json",
        "_orb_candidacy_review.json",
    )

    if name == input_path.name:
        name = input_path.stem + "_orb_candidacy_review.json"

    if output_dir:
        return output_dir / name

    return input_path.with_name(name)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build review-only orb_candidacy_review JSON from an orb_support_window_scale_review JSON file."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to one *_orb_support_window_scale_review.json file.",
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
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir) if args.output_dir else None
    output_path = Path(args.output) if args.output else default_output_path(input_path, output_dir)

    data = load_json(input_path)
    review = build_orb_candidacy_review(data, input_path)
    write_json(output_path, review)

    print("Orb candidacy review")
    print(f"input : {input_path}")
    print(f"output: {output_path}")
    print(f"artifact_id: {review['review_metadata'].get('artifact_id')}")
    print(f"trace_review_status: {review.get('trace_review_status')}")
    print(
        "support_characterization:",
        review["trace_review_summary"].get("support_characterization"),
    )
    print(
        "total_qualifying_window_count:",
        review["trace_review_summary"].get("total_qualifying_window_count"),
    )
    print(
        "qualifying_window_scales:",
        review["trace_review_summary"].get("qualifying_window_scales"),
    )
    print("review_only:", review["no_emission_boundary"]["review_only"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())