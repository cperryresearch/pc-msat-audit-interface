from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path
from typing import Any, Dict


TEST_DIR = Path(__file__).resolve().parent
STATE_CONSTRUCTOR_DIR = TEST_DIR.parent

BUILD_HELPER_PATH = STATE_CONSTRUCTOR_DIR / "tools" / "build_orb_candidacy_review.py"
ACCEPTANCE_HELPER_PATH = STATE_CONSTRUCTOR_DIR / "tools" / "validate_orb_candidacy_acceptance.py"

SUPPORT_REVIEW_FIXTURE_DIR = TEST_DIR / "fixtures" / "orb_support_window_scale_review"


def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load module {module_name} from {path}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


BUILD_HELPER = load_module("build_orb_candidacy_review", BUILD_HELPER_PATH)
ACCEPTANCE_HELPER = load_module("validate_orb_candidacy_acceptance", ACCEPTANCE_HELPER_PATH)


EXPECTED_ACCEPTANCE = {
    "test_trace_hover_001_orb_support_window_scale_review.json": {
        "artifact_id": "test_trace_hover_001_v0",
        "is_valid_candidate_support_evidence": False,
        "accepted_support_level": None,
        "source_trace_review_status": "withheld",
    },
    "test_trace_orb_like_001_orb_support_window_scale_review.json": {
        "artifact_id": "test_trace_orb_like_001_v0",
        "is_valid_candidate_support_evidence": True,
        "accepted_support_level": "limited_window_support",
        "source_trace_review_status": "limited_window_support",
    },
    "test_trace_turn_001_orb_support_window_scale_review.json": {
        "artifact_id": "test_trace_turn_001_v0",
        "is_valid_candidate_support_evidence": False,
        "accepted_support_level": None,
        "source_trace_review_status": "withheld",
    },
    "tii_flight_01a_ellipse_cam_ts_1460_1579_orb_support_window_scale_review.json": {
        "artifact_id": "tii_flight_01a_ellipse_cam_ts_1460_1579_v0",
        "is_valid_candidate_support_evidence": True,
        "accepted_support_level": "multi_scale_support",
        "source_trace_review_status": "multi_scale_support",
    },
    "tii_flight_01a_ellipse_cam_ts_950_1949_orb_support_window_scale_review.json": {
        "artifact_id": "tii_flight_01a_ellipse_cam_ts_950_1949_v0",
        "is_valid_candidate_support_evidence": True,
        "accepted_support_level": "strong_multi_scale_candidate_review",
        "source_trace_review_status": "strong_multi_scale_candidate_review",
    },
    "uci_pedestrians_in_traffic_oid_39406_orb_support_window_scale_review.json": {
        "artifact_id": "uci_pedestrians_in_traffic_oid_39406_v0",
        "is_valid_candidate_support_evidence": False,
        "accepted_support_level": None,
        "source_trace_review_status": "withheld",
    },
    "white_stork_nils_2014-08-07_113020_60pt_orb_support_window_scale_review.json": {
        "artifact_id": "white_stork_nils_2014-08-07_113020_60pt_v0",
        "is_valid_candidate_support_evidence": True,
        "accepted_support_level": "limited_window_support",
        "source_trace_review_status": "limited_window_support",
    },
    "white_stork_nils_2014-08-10_140015_60pt_orb_support_window_scale_review.json": {
        "artifact_id": "white_stork_nils_2014-08-10_140015_60pt_v0",
        "is_valid_candidate_support_evidence": True,
        "accepted_support_level": "multi_window_support",
        "source_trace_review_status": "multi_window_support",
    },
}


def build_candidacy_review_from_fixture(filename: str) -> Dict[str, Any]:
    fixture_path = SUPPORT_REVIEW_FIXTURE_DIR / filename
    support_review = BUILD_HELPER.load_json(fixture_path)
    return BUILD_HELPER.build_orb_candidacy_review(
        support_review,
        fixture_path,
    )


class OrbCandidacyAcceptanceValidationTests(unittest.TestCase):
    def test_expected_acceptance_results_are_preserved_with_provisional_controls(self) -> None:
        for filename, expected in EXPECTED_ACCEPTANCE.items():
            with self.subTest(filename=filename):
                candidacy_review = build_candidacy_review_from_fixture(filename)
                result = ACCEPTANCE_HELPER.validate_orb_candidacy_acceptance(
                    candidacy_review,
                    allow_provisional_controls=True,
                )

                self.assertEqual(result["schema_name"], "orb_candidacy_acceptance_result")
                self.assertEqual(result["schema_version"], "review_v0")
                self.assertEqual(result["artifact_id"], expected["artifact_id"])
                self.assertEqual(
                    result["source_trace_review_status"],
                    expected["source_trace_review_status"],
                )
                self.assertEqual(
                    result["is_valid_candidate_support_evidence"],
                    expected["is_valid_candidate_support_evidence"],
                )
                self.assertEqual(
                    result["accepted_support_level"],
                    expected["accepted_support_level"],
                )
                self.assertEqual(result["control_preservation_status"], "provisional")
                self.assertTrue(result["no_emission_boundary_verified"])
                self.assertFalse(result["emission_permitted"])

    def test_withheld_controls_are_rejected_as_candidate_support_evidence(self) -> None:
        withheld_fixtures = [
            "test_trace_hover_001_orb_support_window_scale_review.json",
            "test_trace_turn_001_orb_support_window_scale_review.json",
            "uci_pedestrians_in_traffic_oid_39406_orb_support_window_scale_review.json",
        ]

        for filename in withheld_fixtures:
            with self.subTest(filename=filename):
                candidacy_review = build_candidacy_review_from_fixture(filename)
                result = ACCEPTANCE_HELPER.validate_orb_candidacy_acceptance(
                    candidacy_review,
                    allow_provisional_controls=True,
                )

                self.assertFalse(result["is_valid_candidate_support_evidence"])
                self.assertIsNone(result["accepted_support_level"])
                self.assertIn("trace_review_status_withheld", result["blocking_failures"])
                self.assertFalse(result["emission_permitted"])

    def test_candidate_support_is_evidence_only_and_never_emission(self) -> None:
        candidate_fixtures = [
            "test_trace_orb_like_001_orb_support_window_scale_review.json",
            "tii_flight_01a_ellipse_cam_ts_1460_1579_orb_support_window_scale_review.json",
            "tii_flight_01a_ellipse_cam_ts_950_1949_orb_support_window_scale_review.json",
            "white_stork_nils_2014-08-07_113020_60pt_orb_support_window_scale_review.json",
            "white_stork_nils_2014-08-10_140015_60pt_orb_support_window_scale_review.json",
        ]

        for filename in candidate_fixtures:
            with self.subTest(filename=filename):
                candidacy_review = build_candidacy_review_from_fixture(filename)
                result = ACCEPTANCE_HELPER.validate_orb_candidacy_acceptance(
                    candidacy_review,
                    allow_provisional_controls=True,
                )

                self.assertTrue(result["is_valid_candidate_support_evidence"])
                self.assertIsNotNone(result["accepted_support_level"])
                self.assertTrue(result["no_emission_boundary_verified"])
                self.assertFalse(result["emission_permitted"])
                self.assertEqual(result["blocking_failures"], [])

    def test_acceptance_requires_no_emission_boundary(self) -> None:
        candidacy_review = build_candidacy_review_from_fixture(
            "tii_flight_01a_ellipse_cam_ts_950_1949_orb_support_window_scale_review.json"
        )

        candidacy_review["no_emission_boundary"]["emits_final_state"] = True

        result = ACCEPTANCE_HELPER.validate_orb_candidacy_acceptance(
            candidacy_review,
            allow_provisional_controls=True,
        )

        self.assertFalse(result["is_valid_candidate_support_evidence"])
        self.assertIsNone(result["accepted_support_level"])
        self.assertFalse(result["no_emission_boundary_verified"])
        self.assertIn("no_emission_boundary_violation", result["blocking_failures"])
        self.assertFalse(result["emission_permitted"])

    def test_acceptance_rejects_missing_review_thresholds(self) -> None:
        candidacy_review = build_candidacy_review_from_fixture(
            "tii_flight_01a_ellipse_cam_ts_950_1949_orb_support_window_scale_review.json"
        )

        candidacy_review["review_thresholds"] = {}

        result = ACCEPTANCE_HELPER.validate_orb_candidacy_acceptance(
            candidacy_review,
            allow_provisional_controls=True,
        )

        self.assertFalse(result["is_valid_candidate_support_evidence"])
        self.assertIsNone(result["accepted_support_level"])
        self.assertIn("missing_review_thresholds", result["blocking_failures"])
        self.assertFalse(result["emission_permitted"])

    def test_acceptance_rejects_non_empty_input_errors(self) -> None:
        candidacy_review = build_candidacy_review_from_fixture(
            "tii_flight_01a_ellipse_cam_ts_950_1949_orb_support_window_scale_review.json"
        )

        candidacy_review["input_errors"] = ["synthetic test error"]

        result = ACCEPTANCE_HELPER.validate_orb_candidacy_acceptance(
            candidacy_review,
            allow_provisional_controls=True,
        )

        self.assertFalse(result["is_valid_candidate_support_evidence"])
        self.assertIsNone(result["accepted_support_level"])
        self.assertIn("source_review_input_errors_present", result["blocking_failures"])
        self.assertFalse(result["emission_permitted"])

    def test_acceptance_rejects_wrong_schema(self) -> None:
        candidacy_review = build_candidacy_review_from_fixture(
            "tii_flight_01a_ellipse_cam_ts_950_1949_orb_support_window_scale_review.json"
        )

        candidacy_review["schema_name"] = "not_orb_candidacy_review"

        result = ACCEPTANCE_HELPER.validate_orb_candidacy_acceptance(
            candidacy_review,
            allow_provisional_controls=True,
        )

        self.assertFalse(result["is_valid_candidate_support_evidence"])
        self.assertIsNone(result["accepted_support_level"])
        self.assertIn("wrong_schema_name", result["blocking_failures"])
        self.assertFalse(result["emission_permitted"])

    def test_without_provisional_controls_acceptance_is_blocked_when_controls_not_embedded(self) -> None:
        candidacy_review = build_candidacy_review_from_fixture(
            "tii_flight_01a_ellipse_cam_ts_950_1949_orb_support_window_scale_review.json"
        )

        result = ACCEPTANCE_HELPER.validate_orb_candidacy_acceptance(
            candidacy_review,
            allow_provisional_controls=False,
        )

        self.assertFalse(result["is_valid_candidate_support_evidence"])
        self.assertIsNone(result["accepted_support_level"])
        self.assertEqual(result["control_preservation_status"], "not_checked")
        self.assertIn("control_preservation_not_checked", result["blocking_failures"])
        self.assertFalse(result["emission_permitted"])

    def test_verified_controls_allow_acceptance_without_provisional_flag(self) -> None:
        candidacy_review = build_candidacy_review_from_fixture(
            "tii_flight_01a_ellipse_cam_ts_950_1949_orb_support_window_scale_review.json"
        )

        candidacy_review = copy.deepcopy(candidacy_review)
        candidacy_review["control_withholding_summary"]["controls_preserved"] = True

        result = ACCEPTANCE_HELPER.validate_orb_candidacy_acceptance(
            candidacy_review,
            allow_provisional_controls=False,
        )

        self.assertTrue(result["is_valid_candidate_support_evidence"])
        self.assertEqual(
            result["accepted_support_level"],
            "strong_multi_scale_candidate_review",
        )
        self.assertEqual(result["control_preservation_status"], "verified")
        self.assertTrue(result["no_emission_boundary_verified"])
        self.assertFalse(result["emission_permitted"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
