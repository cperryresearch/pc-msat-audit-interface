import json
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]

CONSTRUCTOR = REPO_ROOT / "state_constructor" / "src" / "construct_state_trace_v0.py"
CONFIG = REPO_ROOT / "state_constructor" / "config" / "constructor_v0_config.json"

ANCHORS = [
    {
        "name": "hover",
        "input": REPO_ROOT / "state_constructor" / "input" / "test_trace_hover_001.csv",
        "output": REPO_ROOT / "state_constructor" / "output" / "test_trace_hover_001_state_segmented_trace.json",
        "expected_support_status": "withheld",
        "expected_support_window_count": 0,
        "expected_first_candidate_state": "Hover",
        "expected_first_state": "Hover",
        "expected_candidate_runs": 1,
        "expected_state_runs": 1,
    },
    {
        "name": "ordinary_turn",
        "input": REPO_ROOT / "state_constructor" / "input" / "test_trace_turn_001.csv",
        "output": REPO_ROOT / "state_constructor" / "output" / "test_trace_turn_001_state_segmented_trace.json",
        "expected_support_status": "withheld",
        "expected_support_window_count": 0,
        "expected_first_candidate_state": "Turn",
        "expected_first_state": "Turn",
        "expected_candidate_runs": 1,
        "expected_state_runs": 1,
    },
    {
        "name": "orb_like_probe",
        "input": REPO_ROOT / "state_constructor" / "input" / "test_trace_orb_like_001.csv",
        "output": REPO_ROOT / "state_constructor" / "output" / "test_trace_orb_like_001_state_segmented_trace.json",
        "expected_support_status": "accepted",
        "expected_support_window_count": 8,
        "expected_first_candidate_state": "Turn",
        "expected_first_state": "Turn",
        "expected_candidate_runs": 1,
        "expected_state_runs": 1,
    },
    {
        "name": "uci_39406",
        "input": REPO_ROOT / "state_constructor" / "input" / "uci_pedestrians_in_traffic_oid_39406.csv",
        "output": REPO_ROOT / "state_constructor" / "output" / "uci_pedestrians_in_traffic_oid_39406_state_segmented_trace.json",
        "expected_support_status": "withheld",
        "expected_support_window_count": 0,
        "expected_first_candidate_state": "Straight",
        "expected_first_state": "Straight",
        "expected_candidate_runs": 57,
        "expected_state_runs": 27,
    },
]


def run_constructor(input_path: Path) -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(CONSTRUCTOR),
            "--input",
            str(input_path),
            "--config",
            str(CONFIG),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode == 0, (
        "Constructor run failed.\n"
        f"Input: {input_path}\n"
        f"STDOUT:\n{result.stdout}\n"
        f"STDERR:\n{result.stderr}"
    )


def load_output(output_path: Path) -> dict:
    assert output_path.exists(), f"Expected output file was not written: {output_path}"
    return json.loads(output_path.read_text())


def get_orb_candidate_support(artifact: dict) -> dict:
    support = (
        artifact.get("processing", {})
        .get("diagnostics", {})
        .get("orb_candidate_support")
    )

    assert isinstance(
        support, dict
    ), "processing.diagnostics.orb_candidate_support must be present as a dict"

    return support


def find_orb_emissions(artifact: dict) -> list[tuple[int, str | None, str | None]]:
    return [
        (index, point.get("candidate_state"), point.get("state"))
        for index, point in enumerate(artifact.get("points", []))
        if point.get("candidate_state") == "Orb" or point.get("state") == "Orb"
    ]


def test_orb_candidate_support_anchor_regression() -> None:
    for anchor in ANCHORS:
        run_constructor(anchor["input"])
        artifact = load_output(anchor["output"])

        support = get_orb_candidate_support(artifact)

        assert support.get("support_status") == anchor["expected_support_status"], (
            f"{anchor['name']} support_status changed"
        )
        assert support.get("support_window_count") == anchor["expected_support_window_count"], (
            f"{anchor['name']} support_window_count changed"
        )

        assert support.get("emits_candidate_state") is False, (
            f"{anchor['name']} must remain diagnostic-only for candidate_state"
        )
        assert support.get("emits_final_state") is False, (
            f"{anchor['name']} must remain diagnostic-only for final state"
        )

        assert find_orb_emissions(artifact) == [], (
            f"{anchor['name']} emitted Orb despite diagnostic-only boundary"
        )

        candidate_runs = artifact["run_summary"]["candidate_state_runs"]
        state_runs = artifact["run_summary"]["state_runs"]

        assert len(candidate_runs) == anchor["expected_candidate_runs"], (
            f"{anchor['name']} candidate run count changed"
        )
        assert len(state_runs) == anchor["expected_state_runs"], (
            f"{anchor['name']} state run count changed"
        )

        assert candidate_runs[0]["value"] == anchor["expected_first_candidate_state"], (
            f"{anchor['name']} first candidate run changed"
        )
        assert state_runs[0]["value"] == anchor["expected_first_state"], (
            f"{anchor['name']} first state run changed"
        )