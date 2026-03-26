from __future__ import annotations

import json
import sys
from pathlib import Path


# Allow imports from state_constructor/src when running tests from repo root.
TESTS_DIR = Path(__file__).resolve().parent
STATE_CONSTRUCTOR_DIR = TESTS_DIR.parent
SRC_DIR = STATE_CONSTRUCTOR_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from schema_utils import validate_artifact_consistency_v0  # noqa: E402


FIXTURES_DIR = TESTS_DIR / "fixtures"


def load_json_fixture(filename: str) -> dict:
    fixture_path = FIXTURES_DIR / filename
    with fixture_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def test_valid_artifact_returns_empty_error_list() -> None:
    artifact = load_json_fixture("valid_artifact_v0.json")

    errors = validate_artifact_consistency_v0(artifact)

    assert errors == []


def test_missing_top_level_block_reports_missing_top_level_block() -> None:
    artifact = load_json_fixture("valid_artifact_v0.json")
    artifact.pop("run_summary")

    errors = validate_artifact_consistency_v0(artifact)

    assert len(errors) >= 1
    assert any(error["category"] == "missing_top_level_block" for error in errors)


def test_missing_point_field_reports_missing_point_field() -> None:
    artifact = load_json_fixture("valid_artifact_v0.json")
    artifact["points"][0].pop("state")

    errors = validate_artifact_consistency_v0(artifact)

    assert len(errors) >= 1
    assert any(error["category"] == "missing_point_field" for error in errors)


def test_invalid_vocabulary_value_reports_invalid_vocabulary_value() -> None:
    artifact = load_json_fixture("valid_artifact_v0.json")
    artifact["points"][0]["state"] = "Diagonal"

    errors = validate_artifact_consistency_v0(artifact)

    assert len(errors) >= 1
    assert any(error["category"] == "invalid_vocabulary_value" for error in errors)


def test_candidate_run_mismatch_reports_candidate_run_mismatch() -> None:
    artifact = load_json_fixture("valid_artifact_v0.json")
    artifact["run_summary"]["candidate_state_runs"][0]["end_index"] = 0
    artifact["run_summary"]["candidate_state_runs"][0]["length"] = 1

    errors = validate_artifact_consistency_v0(artifact)

    assert len(errors) >= 1
    assert any(error["category"] == "candidate_run_mismatch" for error in errors)


def test_state_run_mismatch_reports_state_run_mismatch() -> None:
    artifact = load_json_fixture("valid_artifact_v0.json")
    artifact["run_summary"]["state_runs"][0]["end_index"] = 0
    artifact["run_summary"]["state_runs"][0]["length"] = 1

    errors = validate_artifact_consistency_v0(artifact)

    assert len(errors) >= 1
    assert any(error["category"] == "state_run_mismatch" for error in errors)
