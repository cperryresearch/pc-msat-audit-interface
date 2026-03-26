from __future__ import annotations

import sys
from pathlib import Path

import pytest


TESTS_DIR = Path(__file__).resolve().parent
STATE_CONSTRUCTOR_DIR = TESTS_DIR.parent
SRC_DIR = STATE_CONSTRUCTOR_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import construct_state_trace_v0 as constructor_module  # noqa: E402
from schema_utils import ArtifactValidationError  # noqa: E402


def test_constructor_raises_artifact_validation_error_on_invalid_artifact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_parse_args():
        class Args:
            input = "state_constructor/input/test_trace_001.csv"
            config = "state_constructor/config/constructor_v0_config.json"
            output = None

        return Args()

    def fake_validate_artifact_consistency_v0(_artifact):
        return [
            {
                "category": "state_run_mismatch",
                "message": "run_summary['state_runs'] does not match contiguous non-None state runs reconstructed from points",
            }
        ]

    monkeypatch.setattr(constructor_module, "parse_args", fake_parse_args)
    monkeypatch.setattr(
        constructor_module,
        "validate_artifact_consistency_v0",
        fake_validate_artifact_consistency_v0,
    )

    with pytest.raises(ArtifactValidationError) as exc_info:
        constructor_module.main()

    assert exc_info.value.errors != []


def test_artifact_validation_error_summary_string_is_exact(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_parse_args():
        class Args:
            input = "state_constructor/input/test_trace_001.csv"
            config = "state_constructor/config/constructor_v0_config.json"
            output = None

        return Args()

    def fake_validate_artifact_consistency_v0(_artifact):
        return [
            {
                "category": "missing_top_level_block",
                "message": "Missing required top-level block: run_summary",
            }
        ]

    monkeypatch.setattr(constructor_module, "parse_args", fake_parse_args)
    monkeypatch.setattr(
        constructor_module,
        "validate_artifact_consistency_v0",
        fake_validate_artifact_consistency_v0,
    )

    with pytest.raises(ArtifactValidationError) as exc_info:
        constructor_module.main()

    assert exc_info.value.summary == "Canonical v0 artifact validation failed."
