from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from typing import Any, Dict


TEST_DIR = Path(__file__).resolve().parent
STATE_CONSTRUCTOR_DIR = TEST_DIR.parent
HELPER_PATH = STATE_CONSTRUCTOR_DIR / "tools" / "build_orb_candidacy_review.py"
FIXTURE_DIR = TEST_DIR / "fixtures" / "orb_support_window_scale_review"


def load_helper_module():
    spec = importlib.util.spec_from_file_location(
        "build_orb_candidacy_review",
        HELPER_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load helper module from {HELPER_PATH}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


HELPER = load_helper_module()


EXPECTED_REVIEWS: Dict[str, Dict[str, Any]] = {
    "test_trace_hover_001_orb_support_window_scale_review.json": {
        "artifact_id": "test_trace_hover_001_v0",
        "trace_review_status": "withheld",
        "support_characterization": "no_support",
        "total_qualifying_window_count": 0,
        "qualifying_window_scales": [],
    },
    "test_trace_orb_like_001_orb_support_window_scale_review.json": {
        "artifact_id": "test_trace_orb_like_001_v0",
        "trace_review_status": "limited_window_support",
        "support_characterization": "limited_window_support",
        "total_qualifying_window_count": 1,
        "qualifying_window_scales": [5],
    },
    "test_trace_turn_001_orb_support_window_scale_review.json": {
        "artifact_id": "test_trace_turn_001_v0",
        "trace_review_status": "withheld",
        "support_characterization": "no_support",
        "total_qualifying_window_count": 0,
        "qualifying_window_scales": [],
    },
    "tii_flight_01a_ellipse_cam_ts_1460_1579_orb_support_window_scale_review.json": {
        "artifact_id": "tii_flight_01a_ellipse_cam_ts_1460_1579_v0",
        "trace_review_status": "multi_scale_support",
        "support_characterization": "multi_scale_support",
        "total_qualifying_window_count": 11,
        "qualifying_window_scales": [25, 50, 100],
    },
    "tii_flight_01a_ellipse_cam_ts_950_1949_orb_support_window_scale_review.json": {
        "artifact_id": "tii_flight_01a_ellipse_cam_ts_950_1949_v0",
        "trace_review_status": "strong_multi_scale_candidate_review",
        "support_characterization": "strong_multi_scale_candidate_review",
        "total_qualifying_window_count": 204,
        "qualifying_window_scales": [25, 50, 100, 250, 500],
    },
    "uci_pedestrians_in_traffic_oid_39406_orb_support_window_scale_review.json": {
        "artifact_id": "uci_pedestrians_in_traffic_oid_39406_v0",
        "trace_review_status": "withheld",
        "support_characterization": "no_support",
        "total_qualifying_window_count": 0,
        "qualifying_window_scales": [],
    },
    "white_stork_nils_2014-08-07_113020_60pt_orb_support_window_scale_review.json": {
        "artifact_id": "white_stork_nils_2014-08-07_113020_60pt_v0",
        "trace_review_status": "limited_window_support",
        "support_characterization": "limited_window_support",
        "total_qualifying_window_count": 1,
        "qualifying_window_scales": [25],
    },
    "white_stork_nils_2014-08-10_140015_60pt_orb_support_window_scale_review.json": {
        "artifact_id": "white_stork_nils_2014-08-10_140015_60pt_v0",
        "trace_review_status": "multi_window_support",
        "support_characterization": "multi_window_support",
        "total_qualifying_window_count": 4,
        "qualifying_window_scales": [25],
    },
}


class OrbCandidacyReviewRegressionTests(unittest.TestCase):
    def test_expected_fixture_set_is_present(self) -> None:
        actual_names = {path.name for path in FIXTURE_DIR.glob("*.json")}
        expected_names = set(EXPECTED_REVIEWS)

        self.assertEqual(
            actual_names,
            expected_names,
            "Fixture set should remain intentionally small and curated.",
        )

    def test_expected_trace_review_statuses_are_preserved(self) -> None:
        for filename, expected in EXPECTED_REVIEWS.items():
            with self.subTest(filename=filename):
                fixture_path = FIXTURE_DIR / filename
                source_review = HELPER.load_json(fixture_path)
                candidacy_review = HELPER.build_orb_candidacy_review(
                    source_review,
                    fixture_path,
                )

                self.assertEqual(candidacy_review["schema_name"], "orb_candidacy_review")
                self.assertEqual(candidacy_review["schema_version"], "review_v0")
                self.assertEqual(candidacy_review["input_errors"], [])

                self.assertEqual(
                    candidacy_review["review_metadata"]["artifact_id"],
                    expected["artifact_id"],
                )
                self.assertEqual(
                    candidacy_review["trace_review_status"],
                    expected["trace_review_status"],
                )
                self.assertEqual(
                    candidacy_review["trace_review_summary"]["support_characterization"],
                    expected["support_characterization"],
                )
                self.assertEqual(
                    candidacy_review["trace_review_summary"]["total_qualifying_window_count"],
                    expected["total_qualifying_window_count"],
                )
                self.assertEqual(
                    candidacy_review["trace_review_summary"]["qualifying_window_scales"],
                    expected["qualifying_window_scales"],
                )

    def test_no_emission_boundary_is_preserved_for_all_reviews(self) -> None:
        for filename in EXPECTED_REVIEWS:
            with self.subTest(filename=filename):
                fixture_path = FIXTURE_DIR / filename
                source_review = HELPER.load_json(fixture_path)
                candidacy_review = HELPER.build_orb_candidacy_review(
                    source_review,
                    fixture_path,
                )

                boundary = candidacy_review["no_emission_boundary"]

                self.assertIs(boundary["review_only"], True)
                self.assertIs(boundary["modifies_artifact"], False)
                self.assertIs(boundary["emits_candidate_state"], False)
                self.assertIs(boundary["emits_final_state"], False)
                self.assertIs(boundary["changes_run_summary"], False)
                self.assertIs(boundary["changes_pc_maw_admission"], False)
                self.assertIs(boundary["changes_playback_behavior"], False)

    def test_withheld_reviews_do_not_report_candidate_support(self) -> None:
        for filename, expected in EXPECTED_REVIEWS.items():
            with self.subTest(filename=filename):
                fixture_path = FIXTURE_DIR / filename
                source_review = HELPER.load_json(fixture_path)
                candidacy_review = HELPER.build_orb_candidacy_review(
                    source_review,
                    fixture_path,
                )

                summary = candidacy_review["trace_review_summary"]

                if expected["trace_review_status"] == "withheld":
                    self.assertEqual(summary["support_characterization"], "no_support")
                    self.assertEqual(summary["total_qualifying_window_count"], 0)
                    self.assertEqual(summary["qualifying_window_scales"], [])
                    self.assertIn(
                        "emission_contract_absent",
                        candidacy_review["withheld_reasons"],
                    )

    def test_candidate_support_reviews_remain_review_only(self) -> None:
        candidate_statuses = {
            "limited_window_support",
            "multi_window_support",
            "multi_scale_support",
            "strong_multi_scale_candidate_review",
        }

        for filename, expected in EXPECTED_REVIEWS.items():
            with self.subTest(filename=filename):
                fixture_path = FIXTURE_DIR / filename
                source_review = HELPER.load_json(fixture_path)
                candidacy_review = HELPER.build_orb_candidacy_review(
                    source_review,
                    fixture_path,
                )

                if expected["trace_review_status"] in candidate_statuses:
                    self.assertGreater(
                        candidacy_review["trace_review_summary"]["total_qualifying_window_count"],
                        0,
                    )
                    self.assertGreater(
                        len(candidacy_review["trace_review_summary"]["qualifying_window_scales"]),
                        0,
                    )
                    self.assertIn(
                        "emission_contract_absent",
                        candidacy_review["withheld_reasons"],
                    )
                    self.assertIs(
                        candidacy_review["no_emission_boundary"]["emits_candidate_state"],
                        False,
                    )
                    self.assertIs(
                        candidacy_review["no_emission_boundary"]["emits_final_state"],
                        False,
                    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
