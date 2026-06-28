#!/usr/bin/env python3
"""
Build orb_candidacy_emission_review JSON from an
orb_candidacy_acceptance_result JSON artifact.

This helper is a bounded emission-review layer.

It does not:
- modify the source artifact
- write candidate_state: Orb into points
- emit final state: Orb
- change run_summary
- change PC-MAW admission
- change Playback behavior
- permit public release
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional


SCHEMA_NAME = "orb_candidacy_emission_review"
SCHEMA_VERSION = "emission_v0"

EXPECTED_INPUT_SCHEMA_NAME = "orb_candidacy_acceptance_result"
EXPECTED_INPUT_SCHEMA_VERSION = "review_v0"

ALLOWED_EMISSION_MODES = {"internal_review", "private_review"}
SYNTHETIC_DIAGNOSTIC_ARTIFACT_IDS = {"test_trace_orb_like_001_v0"}

SUPPLIED_DURATION_CADENCE_REVIEW_SOURCE = "supplied_derived_contract"
ALLOWED_DURATION_CADENCE_CONTRACT_KEYS = {
    "review_source",
    "duration_effect",
    "notes",
}

DURATION_CADENCE_EFFECTS = {
    "no_point_count_support": {
        "emission_effect": "withhold_candidate_label",
        "passed": False,
        "failure_reason": "duration_cadence_no_point_count_support",
    },
    "point_count_weakened_by_duration": {
        "emission_effect": "withhold_candidate_label",
        "passed": False,
        "failure_reason": "duration_cadence_weakened_point_support",
    },
    "point_count_preserved_by_duration": {
        "emission_effect": "allow_gate_continuation",
        "passed": True,
        "failure_reason": None,
    },
    "cadence_missing_or_inconclusive": {
        "emission_effect": "withhold_candidate_label",
        "passed": False,
        "failure_reason": "duration_cadence_inconclusive",
    },
    "inspect_manually": {
        "emission_effect": "withhold_candidate_label",
        "passed": False,
        "failure_reason": "duration_cadence_inconclusive",
    },
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
        "_orb_candidacy_acceptance_result.json",
        "_orb_candidacy_emission_review.json",
    )

    if name == input_path.name:
        name = input_path.stem + "_orb_candidacy_emission_review.json"

    if output_dir:
        return output_dir / name

    return input_path.with_name(name)


def classify_artifact(artifact_id: Optional[str]) -> str:
    if not artifact_id:
        return "unknown"

    if artifact_id in SYNTHETIC_DIAGNOSTIC_ARTIFACT_IDS:
        return "synthetic_diagnostic_fixture"

    if artifact_id.startswith("test_trace_"):
        return "synthetic_control_or_baseline_fixture"

    if artifact_id.startswith("uci_pedestrians_in_traffic_oid_39406"):
        return "external_derived_public_sample"

    if artifact_id.startswith("white_stork") or artifact_id.startswith("barn_swallow"):
        return "real_world_biological_sample"

    if artifact_id.startswith("tii_"):
        return "engineered_aerial_review_anchor"

    return "unknown"


def build_source_acceptance_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema_name": data.get("schema_name"),
        "schema_version": data.get("schema_version"),
        "artifact_id": data.get("artifact_id"),
        "source_candidacy_review_path": data.get("source_candidacy_review_path"),
        "source_trace_review_status": data.get("source_trace_review_status"),
        "is_valid_candidate_support_evidence": data.get(
            "is_valid_candidate_support_evidence"
        ),
        "accepted_support_level": data.get("accepted_support_level"),
        "blocking_failures": data.get("blocking_failures", []),
        "warnings": data.get("warnings", []),
        "no_emission_boundary_verified": data.get("no_emission_boundary_verified"),
        "control_preservation_status": data.get("control_preservation_status"),
        "source_emission_permitted": data.get("emission_permitted"),
    }


def add_gate(
    *,
    gate_name: str,
    passed: bool,
    passed_gates: List[str],
    failed_gates: List[str],
    withheld_reasons: List[str],
    failure_reason: str,
) -> None:
    if passed:
        passed_gates.append(gate_name)
        return

    failed_gates.append(gate_name)
    withheld_reasons.append(failure_reason)


def unique_ordered(values: List[str]) -> List[str]:
    return list(dict.fromkeys(values))


def deferred_duration_cadence_gate() -> Dict[str, Any]:
    return {
        "gate_status": "deferred_pending_private_integration",
        "review_source": "not_supplied",
        "duration_effect": None,
        "emission_effect": "allow_existing_v0_behavior",
        "notes": [
            "No duration/cadence derived contract was supplied.",
            "Current v0 candidate-label behavior is preserved.",
        ],
    }


def invalid_duration_cadence_gate(
    *,
    review_source: Optional[Any],
    duration_effect: Optional[Any],
    notes: List[str],
) -> Dict[str, Any]:
    return {
        "gate_status": "invalid",
        "review_source": review_source if isinstance(review_source, str) else None,
        "duration_effect": duration_effect if isinstance(duration_effect, str) else None,
        "emission_effect": "withhold_candidate_label",
        "notes": notes,
    }


def evaluate_duration_cadence_contract(
    duration_cadence_contract: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    if duration_cadence_contract is None:
        return {
            "gate": deferred_duration_cadence_gate(),
            "gate_required": False,
            "passed": None,
            "failure_reason": None,
            "deferred": True,
        }

    if not isinstance(duration_cadence_contract, dict):
        return {
            "gate": invalid_duration_cadence_gate(
                review_source=None,
                duration_effect=None,
                notes=["Duration/cadence contract must be an object."],
            ),
            "gate_required": True,
            "passed": False,
            "failure_reason": "duration_cadence_contract_invalid",
            "deferred": False,
        }

    review_source = duration_cadence_contract.get(
        "review_source",
        SUPPLIED_DURATION_CADENCE_REVIEW_SOURCE,
    )
    duration_effect = duration_cadence_contract.get("duration_effect")
    contract_notes = duration_cadence_contract.get("notes", [])
    invalid_notes: List[str] = []

    unsupported_keys = sorted(
        set(duration_cadence_contract.keys()) - ALLOWED_DURATION_CADENCE_CONTRACT_KEYS
    )
    if unsupported_keys:
        invalid_notes.append(
            "Unsupported duration/cadence contract fields: "
            + ", ".join(unsupported_keys)
        )

    if review_source != SUPPLIED_DURATION_CADENCE_REVIEW_SOURCE:
        invalid_notes.append(
            "review_source must be 'supplied_derived_contract' for supplied contracts."
        )

    if duration_effect not in DURATION_CADENCE_EFFECTS:
        invalid_notes.append(
            "duration_effect must be one of: "
            + ", ".join(sorted(DURATION_CADENCE_EFFECTS.keys()))
        )

    if "notes" in duration_cadence_contract and not (
        isinstance(contract_notes, list)
        and all(isinstance(note, str) for note in contract_notes)
    ):
        invalid_notes.append("notes must be a list of strings when supplied.")

    if invalid_notes:
        return {
            "gate": invalid_duration_cadence_gate(
                review_source=review_source,
                duration_effect=duration_effect,
                notes=invalid_notes,
            ),
            "gate_required": True,
            "passed": False,
            "failure_reason": "duration_cadence_contract_invalid",
            "deferred": False,
        }

    effect_policy = DURATION_CADENCE_EFFECTS[duration_effect]

    return {
        "gate": {
            "gate_status": "reviewed",
            "review_source": review_source,
            "duration_effect": duration_effect,
            "emission_effect": effect_policy["emission_effect"],
            "notes": contract_notes,
        },
        "gate_required": True,
        "passed": effect_policy["passed"],
        "failure_reason": effect_policy["failure_reason"],
        "deferred": False,
    }


def build_orb_candidacy_emission_review(
    data: Dict[str, Any],
    source_path: Optional[Path] = None,
    *,
    emission_mode: str = "none",
    duration_cadence_contract: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    artifact_id = data.get("artifact_id") if isinstance(data.get("artifact_id"), str) else None
    artifact_class = classify_artifact(artifact_id)
    duration_cadence_result = evaluate_duration_cadence_contract(
        duration_cadence_contract
    )

    passed_gates: List[str] = []
    failed_gates: List[str] = []
    withheld_reasons: List[str] = []

    required_gates = [
        "source_schema_gate",
        "source_acceptance_gate",
        "source_no_emission_boundary_gate",
        "emission_mode_gate",
        "provenance_gate",
    ]

    add_gate(
        gate_name="source_schema_gate",
        passed=data.get("schema_name") == EXPECTED_INPUT_SCHEMA_NAME
        and data.get("schema_version") == EXPECTED_INPUT_SCHEMA_VERSION,
        passed_gates=passed_gates,
        failed_gates=failed_gates,
        withheld_reasons=withheld_reasons,
        failure_reason="source_acceptance_wrong_schema",
    )

    add_gate(
        gate_name="source_acceptance_gate",
        passed=data.get("is_valid_candidate_support_evidence") is True
        and data.get("accepted_support_level") is not None,
        passed_gates=passed_gates,
        failed_gates=failed_gates,
        withheld_reasons=withheld_reasons,
        failure_reason="source_acceptance_not_valid",
    )

    add_gate(
        gate_name="source_no_emission_boundary_gate",
        passed=data.get("no_emission_boundary_verified") is True
        and data.get("emission_permitted") is False,
        passed_gates=passed_gates,
        failed_gates=failed_gates,
        withheld_reasons=withheld_reasons,
        failure_reason="source_acceptance_boundary_violation",
    )

    add_gate(
        gate_name="emission_mode_gate",
        passed=emission_mode in ALLOWED_EMISSION_MODES,
        passed_gates=passed_gates,
        failed_gates=failed_gates,
        withheld_reasons=withheld_reasons,
        failure_reason=(
            "contract_not_enabled"
            if emission_mode == "none"
            else "unsupported_emission_mode"
        ),
    )

    add_gate(
        gate_name="provenance_gate",
        passed=artifact_class == "synthetic_diagnostic_fixture",
        passed_gates=passed_gates,
        failed_gates=failed_gates,
        withheld_reasons=withheld_reasons,
        failure_reason="provenance_not_emission_allowed",
    )

    if duration_cadence_result["gate_required"]:
        required_gates.append("duration_cadence_gate")
        add_gate(
            gate_name="duration_cadence_gate",
            passed=duration_cadence_result["passed"] is True,
            passed_gates=passed_gates,
            failed_gates=failed_gates,
            withheld_reasons=withheld_reasons,
            failure_reason=duration_cadence_result["failure_reason"],
        )

    add_gate(
        gate_name="public_release_gate",
        passed=True,
        passed_gates=passed_gates,
        failed_gates=failed_gates,
        withheld_reasons=withheld_reasons,
        failure_reason="public_release_not_allowed",
    )

    add_gate(
        gate_name="source_artifact_mutation_gate",
        passed=True,
        passed_gates=passed_gates,
        failed_gates=failed_gates,
        withheld_reasons=withheld_reasons,
        failure_reason="source_artifact_mutation_not_allowed",
    )

    add_gate(
        gate_name="final_state_emission_gate",
        passed=True,
        passed_gates=passed_gates,
        failed_gates=failed_gates,
        withheld_reasons=withheld_reasons,
        failure_reason="final_state_emission_not_allowed",
    )

    required_gates.extend(
        [
            "public_release_gate",
            "source_artifact_mutation_gate",
            "final_state_emission_gate",
        ]
    )

    deferred_gates = (
        [
            "duration_gate_deferred_pending_private_integration",
            "cadence_gate_deferred_pending_private_integration",
        ]
        if duration_cadence_result["deferred"]
        else []
    )

    duration_cadence_gate = duration_cadence_result["gate"]
    duration_cadence_policy_status = duration_cadence_gate["gate_status"]

    emission_permitted = not failed_gates
    candidate_label = "Orb" if emission_permitted else None

    return {
        "schema_name": SCHEMA_NAME,
        "schema_version": SCHEMA_VERSION,
        "contract_status": "internal_v0",
        "review_scope": "candidate_label_only",
        "public_release_allowed": False,
        "source_acceptance_review_path": str(source_path) if source_path else None,
        "source_acceptance_result": build_source_acceptance_summary(data),
        "artifact_policy": {
            "artifact_id": artifact_id,
            "artifact_class": artifact_class,
            "allowed_emission_classes": ["synthetic_diagnostic_fixture"],
        },
        "candidate_label_emission": {
            "emission_permitted": emission_permitted,
            "candidate_label": candidate_label,
            "emission_mode": emission_mode,
        },
        "source_artifact_mutation": {
            "modifies_artifact": False,
            "modifies_points_candidate_state": False,
            "modifies_points_state": False,
            "changes_run_summary": False,
        },
        "final_state_emission": {
            "emission_permitted": False,
            "final_state": None,
        },
        "frontend_playback_boundary": {
            "changes_pc_maw_admission": False,
            "changes_playback_behavior": False,
            "renders_orb_state_segments": False,
            "requires_frontend_change": False,
        },
        "duration_cadence_gate": duration_cadence_gate,
        "duration_cadence_policy": {
            "duration_gate_status": duration_cadence_policy_status,
            "cadence_gate_status": duration_cadence_policy_status,
            "tracked_v0_scope": "synthetic_diagnostic_fixture_only",
        },
        "required_gates": required_gates,
        "passed_gates": unique_ordered(passed_gates),
        "failed_gates": unique_ordered(failed_gates),
        "deferred_gates": deferred_gates,
        "withheld_reasons": unique_ordered(withheld_reasons),
        "support_basis": {
            "accepted_support_level": data.get("accepted_support_level"),
            "source_trace_review_status": data.get("source_trace_review_status"),
            "control_preservation_status": data.get("control_preservation_status"),
        },
        "non_claims": [
            "No physical-origin interpretation is made.",
            "No UAP confirmation is made.",
            "No object identity is asserted.",
            "No independent external validation is implied.",
            "No public-release approval is implied.",
            "No final-state Orb classification is emitted.",
            "The source state-segmented artifact is not modified.",
            "Synthetic orb-like fixtures are not real-world Orb evidence.",
        ],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build bounded orb_candidacy_emission_review JSON from an orb_candidacy_acceptance_result JSON file."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to one *_orb_candidacy_acceptance_result.json file.",
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
        "--emission-mode",
        default="none",
        choices=["none", "internal_review", "private_review"],
        help="Emission mode. Defaults to none so candidate-label emission is explicit.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output_dir) if args.output_dir else None
    output_path = Path(args.output) if args.output else default_output_path(input_path, output_dir)

    data = load_json(input_path)
    review = build_orb_candidacy_emission_review(
        data,
        source_path=input_path,
        emission_mode=args.emission_mode,
    )
    write_json(output_path, review)

    print("Orb candidacy emission review")
    print(f"input : {input_path}")
    print(f"output: {output_path}")
    print(f"artifact_id: {review['artifact_policy'].get('artifact_id')}")
    print(f"artifact_class: {review['artifact_policy'].get('artifact_class')}")
    print(
        "candidate_label_emission_permitted:",
        review["candidate_label_emission"].get("emission_permitted"),
    )
    print(
        "candidate_label:",
        review["candidate_label_emission"].get("candidate_label"),
    )
    print(
        "emission_mode:",
        review["candidate_label_emission"].get("emission_mode"),
    )

    reasons = review.get("withheld_reasons") or []
    if reasons:
        print("withheld_reasons:", reasons)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())