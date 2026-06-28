from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from typing import Any, Dict


TEST_DIR = Path(__file__).resolve().parent
STATE_CONSTRUCTOR_DIR = TEST_DIR.parent

BUILD_REVIEW_HELPER_PATH = STATE_CONSTRUCTOR_DIR / "tools" / "build_orb_candidacy_review.py"
ACCEPTANCE_HELPER_PATH = STATE_CONSTRUCTOR_DIR / "tools" / "validate_orb_candidacy_acceptance.py"
EMISSION_HELPER_PATH = STATE_CONSTRUCTOR_DIR / "tools" / "build_orb_candidacy_emission_review.py"

SUPPORT_REVIEW_FIXTURE_DIR = TEST_DIR / "fixtures" / "orb_support_window_scale_review"


def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module {module_name} from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD_REVIEW_HELPER = load_module("build_orb_candidacy_review", BUILD_REVIEW_HELPER_PATH)
ACCEPTANCE_HELPER = load_module("validate_orb_candidacy_acceptance", ACCEPTANCE_HELPER_PATH)
EMISSION_HELPER = load_module("build_orb_candidacy_emission_review", EMISSION_HELPER_PATH)


def acceptance_result_from_fixture(filename: str) -> Dict[str, Any]:
    fixture_path = SUPPORT_REVIEW_FIXTURE_DIR / filename
    support_review = BUILD_REVIEW_HELPER.load_json(fixture_path)
    candidacy_review = BUILD_REVIEW_HELPER.build_orb_candidacy_review(
        support_review,
        fixture_path,
    )
    return ACCEPTANCE_HELPER.validate_orb_candidacy_acceptance(
        candidacy_review,
        allow_provisional_controls=True,
    )


class OrbCandidacyEmissionReviewTests(unittest.TestCase):
    def test_synthetic_orb_like_can_emit_candidate_label_in_internal_review_mode(self) -> None:
        acceptance_result = acceptance_result_from_fixture(
            "test_trace_orb_like_001_orb_support_window_scale_review.json"
        )

        emission_review = EMISSION_HELPER.build_orb_candidacy_emission_review(
            acceptance_result,
            emission_mode="internal_review",
        )

        self.assertEqual(emission_review["schema_name"], "orb_candidacy_emission_review")
        self.assertEqual(emission_review["schema_version"], "emission_v0")
        self.assertFalse(emission_review["public_release_allowed"])
        self.assertEqual(
            emission_review["artifact_policy"]["artifact_class"],
            "synthetic_diagnostic_fixture",
        )
        self.assertEqual(emission_review["failed_gates"], [])
        self.assertEqual(emission_review["withheld_reasons"], [])
        self.assertTrue(
            emission_review["candidate_label_emission"]["emission_permitted"]
        )
        self.assertEqual(
            emission_review["candidate_label_emission"]["candidate_label"],
            "Orb",
        )
        self.assertFalse(
            emission_review["source_artifact_mutation"]["modifies_artifact"]
        )
        self.assertFalse(
            emission_review["source_artifact_mutation"]["modifies_points_candidate_state"]
        )
        self.assertFalse(
            emission_review["final_state_emission"]["emission_permitted"]
        )
        self.assertFalse(
            emission_review["frontend_playback_boundary"]["changes_playback_behavior"]
        )

    def test_valid_support_does_not_emit_when_contract_mode_is_not_enabled(self) -> None:
        acceptance_result = acceptance_result_from_fixture(
            "test_trace_orb_like_001_orb_support_window_scale_review.json"
        )

        emission_review = EMISSION_HELPER.build_orb_candidacy_emission_review(
            acceptance_result
        )

        self.assertFalse(
            emission_review["candidate_label_emission"]["emission_permitted"]
        )
        self.assertIsNone(
            emission_review["candidate_label_emission"]["candidate_label"]
        )
        self.assertIn("emission_mode_gate", emission_review["failed_gates"])
        self.assertIn("contract_not_enabled", emission_review["withheld_reasons"])

    def test_withheld_controls_and_external_anchor_do_not_emit(self) -> None:
        withheld_fixtures = [
            "test_trace_hover_001_orb_support_window_scale_review.json",
            "test_trace_turn_001_orb_support_window_scale_review.json",
            "uci_pedestrians_in_traffic_oid_39406_orb_support_window_scale_review.json",
        ]

        for filename in withheld_fixtures:
            with self.subTest(filename=filename):
                acceptance_result = acceptance_result_from_fixture(filename)
                emission_review = EMISSION_HELPER.build_orb_candidacy_emission_review(
                    acceptance_result,
                    emission_mode="internal_review",
                )

                self.assertFalse(
                    emission_review["candidate_label_emission"]["emission_permitted"]
                )
                self.assertIsNone(
                    emission_review["candidate_label_emission"]["candidate_label"]
                )
                self.assertIn("source_acceptance_gate", emission_review["failed_gates"])
                self.assertIn(
                    "source_acceptance_not_valid",
                    emission_review["withheld_reasons"],
                )
                self.assertFalse(
                    emission_review["final_state_emission"]["emission_permitted"]
                )

    def test_non_synthetic_candidate_support_is_provenance_withheld(self) -> None:
        non_synthetic_candidate_fixtures = [
            "tii_flight_01a_ellipse_cam_ts_1460_1579_orb_support_window_scale_review.json",
            "tii_flight_01a_ellipse_cam_ts_950_1949_orb_support_window_scale_review.json",
            "white_stork_nils_2014-08-07_113020_60pt_orb_support_window_scale_review.json",
            "white_stork_nils_2014-08-10_140015_60pt_orb_support_window_scale_review.json",
        ]

        for filename in non_synthetic_candidate_fixtures:
            with self.subTest(filename=filename):
                acceptance_result = acceptance_result_from_fixture(filename)
                emission_review = EMISSION_HELPER.build_orb_candidacy_emission_review(
                    acceptance_result,
                    emission_mode="private_review",
                )

                self.assertTrue(
                    emission_review["source_acceptance_result"][
                        "is_valid_candidate_support_evidence"
                    ]
                )
                self.assertFalse(
                    emission_review["candidate_label_emission"]["emission_permitted"]
                )
                self.assertIsNone(
                    emission_review["candidate_label_emission"]["candidate_label"]
                )
                self.assertIn("provenance_gate", emission_review["failed_gates"])
                self.assertIn(
                    "provenance_not_emission_allowed",
                    emission_review["withheld_reasons"],
                )

    def test_emission_review_keeps_duration_and_cadence_deferred_for_tracked_v0(self) -> None:
        acceptance_result = acceptance_result_from_fixture(
            "test_trace_orb_like_001_orb_support_window_scale_review.json"
        )

        emission_review = EMISSION_HELPER.build_orb_candidacy_emission_review(
            acceptance_result,
            emission_mode="internal_review",
        )

        self.assertEqual(
            emission_review["duration_cadence_policy"]["duration_gate_status"],
            "deferred_pending_private_integration",
        )
        self.assertEqual(
            emission_review["duration_cadence_gate"]["gate_status"],
            "deferred_pending_private_integration",
        )
        self.assertEqual(
            emission_review["duration_cadence_gate"]["review_source"],
            "not_supplied",
        )
        self.assertIsNone(
            emission_review["duration_cadence_gate"]["duration_effect"]
        )
        self.assertEqual(
            emission_review["duration_cadence_gate"]["emission_effect"],
            "allow_existing_v0_behavior",
        )
        self.assertEqual(
            emission_review["duration_cadence_policy"]["cadence_gate_status"],
            "deferred_pending_private_integration",
        )
        self.assertIn(
            "duration_gate_deferred_pending_private_integration",
            emission_review["deferred_gates"],
        )
        self.assertIn(
            "cadence_gate_deferred_pending_private_integration",
            emission_review["deferred_gates"],
        )

    def test_wrong_source_schema_is_blocked(self) -> None:
        acceptance_result = acceptance_result_from_fixture(
            "test_trace_orb_like_001_orb_support_window_scale_review.json"
        )
        acceptance_result["schema_name"] = "not_orb_candidacy_acceptance_result"

        emission_review = EMISSION_HELPER.build_orb_candidacy_emission_review(
            acceptance_result,
            emission_mode="internal_review",
        )

        self.assertFalse(
            emission_review["candidate_label_emission"]["emission_permitted"]
        )
        self.assertIn("source_schema_gate", emission_review["failed_gates"])
        self.assertIn(
            "source_acceptance_wrong_schema",
            emission_review["withheld_reasons"],
        )

    def test_weakened_duration_contract_withholds_candidate_label(self) -> None:
        acceptance_result = acceptance_result_from_fixture(
            "test_trace_orb_like_001_orb_support_window_scale_review.json"
        )

        emission_review = EMISSION_HELPER.build_orb_candidacy_emission_review(
            acceptance_result,
            emission_mode="internal_review",
            duration_cadence_contract={
                "review_source": "supplied_derived_contract",
                "duration_effect": "point_count_weakened_by_duration",
            },
        )

        self.assertFalse(
            emission_review["candidate_label_emission"]["emission_permitted"]
        )
        self.assertIsNone(
            emission_review["candidate_label_emission"]["candidate_label"]
        )
        self.assertEqual(
            emission_review["duration_cadence_gate"]["gate_status"],
            "reviewed",
        )
        self.assertEqual(
            emission_review["duration_cadence_gate"]["emission_effect"],
            "withhold_candidate_label",
        )
        self.assertIn("duration_cadence_gate", emission_review["failed_gates"])
        self.assertIn(
            "duration_cadence_weakened_point_support",
            emission_review["withheld_reasons"],
        )

    def test_preserved_duration_contract_allows_gate_continuation_only(self) -> None:
        acceptance_result = acceptance_result_from_fixture(
            "test_trace_orb_like_001_orb_support_window_scale_review.json"
        )

        emission_review = EMISSION_HELPER.build_orb_candidacy_emission_review(
            acceptance_result,
            emission_mode="internal_review",
            duration_cadence_contract={
                "review_source": "supplied_derived_contract",
                "duration_effect": "point_count_preserved_by_duration",
            },
        )

        self.assertTrue(
            emission_review["candidate_label_emission"]["emission_permitted"]
        )
        self.assertEqual(
            emission_review["candidate_label_emission"]["candidate_label"],
            "Orb",
        )
        self.assertEqual(
            emission_review["duration_cadence_gate"]["emission_effect"],
            "allow_gate_continuation",
        )
        self.assertIn("duration_cadence_gate", emission_review["passed_gates"])
        self.assertNotIn("duration_cadence_gate", emission_review["failed_gates"])

    def test_preserved_duration_contract_does_not_override_provenance_gate(self) -> None:
        acceptance_result = acceptance_result_from_fixture(
            "white_stork_nils_2014-08-10_140015_60pt_orb_support_window_scale_review.json"
        )

        emission_review = EMISSION_HELPER.build_orb_candidacy_emission_review(
            acceptance_result,
            emission_mode="private_review",
            duration_cadence_contract={
                "review_source": "supplied_derived_contract",
                "duration_effect": "point_count_preserved_by_duration",
            },
        )

        self.assertFalse(
            emission_review["candidate_label_emission"]["emission_permitted"]
        )
        self.assertIsNone(
            emission_review["candidate_label_emission"]["candidate_label"]
        )
        self.assertIn("duration_cadence_gate", emission_review["passed_gates"])
        self.assertIn("provenance_gate", emission_review["failed_gates"])
        self.assertIn(
            "provenance_not_emission_allowed",
            emission_review["withheld_reasons"],
        )

    def test_no_point_count_duration_contract_withholds_candidate_label(self) -> None:
        acceptance_result = acceptance_result_from_fixture(
            "test_trace_hover_001_orb_support_window_scale_review.json"
        )

        emission_review = EMISSION_HELPER.build_orb_candidacy_emission_review(
            acceptance_result,
            emission_mode="internal_review",
            duration_cadence_contract={
                "review_source": "supplied_derived_contract",
                "duration_effect": "no_point_count_support",
            },
        )

        self.assertFalse(
            emission_review["candidate_label_emission"]["emission_permitted"]
        )
        self.assertIn("duration_cadence_gate", emission_review["failed_gates"])
        self.assertIn(
            "duration_cadence_no_point_count_support",
            emission_review["withheld_reasons"],
        )

    def test_inconclusive_duration_contracts_withhold_candidate_label(self) -> None:
        acceptance_result = acceptance_result_from_fixture(
            "test_trace_orb_like_001_orb_support_window_scale_review.json"
        )

        for duration_effect in [
            "cadence_missing_or_inconclusive",
            "inspect_manually",
        ]:
            with self.subTest(duration_effect=duration_effect):
                emission_review = EMISSION_HELPER.build_orb_candidacy_emission_review(
                    acceptance_result,
                    emission_mode="internal_review",
                    duration_cadence_contract={
                        "review_source": "supplied_derived_contract",
                        "duration_effect": duration_effect,
                    },
                )

                self.assertFalse(
                    emission_review["candidate_label_emission"]["emission_permitted"]
                )
                self.assertIsNone(
                    emission_review["candidate_label_emission"]["candidate_label"]
                )
                self.assertIn("duration_cadence_gate", emission_review["failed_gates"])
                self.assertIn(
                    "duration_cadence_inconclusive",
                    emission_review["withheld_reasons"],
                )

    def test_invalid_duration_contract_is_withheld(self) -> None:
        acceptance_result = acceptance_result_from_fixture(
            "test_trace_orb_like_001_orb_support_window_scale_review.json"
        )

        emission_review = EMISSION_HELPER.build_orb_candidacy_emission_review(
            acceptance_result,
            emission_mode="internal_review",
            duration_cadence_contract={
                "review_source": "supplied_derived_contract",
                "duration_effect": "raw_private_threshold_payload",
            },
        )

        self.assertFalse(
            emission_review["candidate_label_emission"]["emission_permitted"]
        )
        self.assertEqual(
            emission_review["duration_cadence_gate"]["gate_status"],
            "invalid",
        )
        self.assertIn("duration_cadence_gate", emission_review["failed_gates"])
        self.assertIn(
            "duration_cadence_contract_invalid",
            emission_review["withheld_reasons"],
        )

    def test_duration_contract_rejects_private_or_raw_path_fields(self) -> None:
        acceptance_result = acceptance_result_from_fixture(
            "test_trace_orb_like_001_orb_support_window_scale_review.json"
        )

        emission_review = EMISSION_HELPER.build_orb_candidacy_emission_review(
            acceptance_result,
            emission_mode="internal_review",
            duration_cadence_contract={
                "review_source": "supplied_derived_contract",
                "duration_effect": "point_count_preserved_by_duration",
                "source_path": "private_output/cadence_aware_support_review/private.json",
            },
        )

        self.assertFalse(
            emission_review["candidate_label_emission"]["emission_permitted"]
        )
        self.assertEqual(
            emission_review["duration_cadence_gate"]["gate_status"],
            "invalid",
        )
        self.assertIn(
            "duration_cadence_contract_invalid",
            emission_review["withheld_reasons"],
        )

if __name__ == "__main__":
    unittest.main(verbosity=2)
