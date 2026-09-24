from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from pathlib import Path

from PIL import Image
import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from simulation.public_renderer import (  # noqa: E402
    RenderInputError,
    RenderSpec,
    _validated_reconstructed_configuration,
    _validated_public_normalized_configuration,
)
TASKS = (
    "door_push",
    "push_to_goal",
    "peg_insert",
    "peg_channel",
    "grasp_place",
    "obstacle_reach",
)


def _catalog() -> list[dict[str, str]]:
    with (ROOT / "data/catalog.csv").open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _winner(rows: list[dict[str, str]], task: str) -> dict[str, str]:
    candidates = [row for row in rows if row["study"] == "primary" and row["task"] == task]
    return sorted(
        candidates,
        key=lambda row: (-float(row["task_score"]), -float(row["composite_score"]), row["record_id"]),
    )[0]


def _manifest() -> dict:
    return json.loads((ROOT / "media/demos/manifest.json").read_text(encoding="utf-8"))


def test_manifest_uses_deterministic_primary_winners() -> None:
    rows = _catalog()
    entries = {entry["task"]: entry for entry in _manifest()["demos"]}
    assert set(entries) == set(TASKS)
    for task in TASKS:
        winner = _winner(rows, task)
        entry = entries[task]
        assert entry["record_id"] == winner["record_id"]
        assert entry["seed"] == int(winner["seed"])
        assert entry["scene_index"] == 0
        assert entry["canonical_task_score"] == float(winner["task_score"])
        assert entry["composite_score"] == float(winner["composite_score"])
        assert entry["selection_rule"].startswith("study=primary")


def test_featured_gifs_decode_and_obey_release_limits() -> None:
    manifest = _manifest()
    render_spec = manifest["render_spec"]
    for entry in manifest["demos"]:
        path = ROOT / entry["gif"]["path"]
        assert path.is_file()
        assert path.stat().st_size == entry["gif"]["size_bytes"]
        assert path.stat().st_size <= render_spec["max_size_bytes"]
        with Image.open(path) as image:
            assert image.format == "GIF"
            assert image.size == (render_spec["width"], render_spec["height"])
            assert image.n_frames == entry["gif"]["frame_count"]
            assert image.info.get("loop") == render_spec["loop"]
            durations = []
            for index in range(image.n_frames):
                image.seek(index)
                durations.append(int(image.info.get("duration", 0)))
            assert all(duration > 0 for duration in durations)
            effective_fps = image.n_frames / (sum(durations) / 1000.0)
            assert abs(effective_fps - render_spec["fps"]) <= 0.1
            assert all(duration % 10 == 0 for duration in durations)
            assert abs(sum(durations) / 1000.0 - entry["gif"]["duration_seconds"]) <= 0.001


def test_manifest_hashes_bind_every_replay_input_and_gif() -> None:
    for entry in _manifest()["demos"]:
        for key, relative in (
            ("skill_sha256", entry["skill_path"]),
            ("parameters_sha256", entry["parameters_path"]),
            ("scene_bank_sha256", entry["scene_bank_path"]),
            ("gif_sha256", entry["gif"]["path"]),
        ):
            path = ROOT / relative
            assert path.is_file()
            assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["hashes"][key]


def test_root_readme_links_every_featured_gif() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for entry in _manifest()["demos"]:
        relative = entry["gif"]["path"]
        assert f"]({relative})" in readme
        assert (ROOT / relative).is_file()
        assert f"]({entry['cell_record_path']})" in readme
        assert (ROOT / entry["cell_record_path"]).is_file()
        assert entry["record_id"] in readme


def test_demo_readmes_use_archive_relative_paths() -> None:
    demos_readme = (ROOT / "media/demos/README.md").read_text(encoding="utf-8")
    assert "manifest.json" in demos_readme
    assert "scene index `0`" in demos_readme
    assert not re.search(r"(?:v\d+\.\d+|paper_" + "campaign|artifact_v1_" + "archive)", demos_readme)


def test_manifest_commands_are_exact_catalog_replays() -> None:
    for entry in _manifest()["demos"]:
        command = entry["reproduction_command"]
        assert f"--record-id {entry['record_id']}" in command
        assert f"--output {entry['gif']['path']}" in command
        assert "--fps 15 --width 640 --height 480" in command


def _normalized_fixture(tmp_path: Path) -> tuple[RenderSpec, dict, object, Path, Path]:
    data = tmp_path / "data"
    (data / "scenes").mkdir(parents=True)
    (data / "records" / "primary").mkdir(parents=True)
    (data / "logs" / "run").mkdir(parents=True)
    (data / "provenance").mkdir(parents=True)
    (data / "skills").mkdir()
    (data / "parameters").mkdir()
    (data / "skills/demo.yaml").write_text("skill: demo\n", encoding="utf-8")
    (data / "parameters/demo.json").write_text("{}", encoding="utf-8")
    scene_path = data / "scenes/demo.json"
    configuration_hash = "a" * 64
    bank = {
        "schema_version": "paper-release",
        "task_name": "demo",
        "outer_seed": 0,
        "k_runs": 1,
        "configurations": [
            {
                "schema_version": "paper-release",
                "config_index": 0,
                "seed": 0,
                "configuration_sha256": configuration_hash,
                "realized_scene_sha256": "b" * 64,
                "realized_scene": {"schema_version": "paper-release", "task_name": "demo"},
                "backend_state": {
                    "body_deltas": {"1": [0.0, 0.0, 0.0]},
                    "qpos_delta": [0.0, 0.0],
                    "scene_frozen": True,
                },
            }
        ],
        "configuration_bank_sha256": "c" * 64,
    }
    scene_path.write_text(json.dumps(bank), encoding="utf-8")
    run_log = [
        {
            "posthoc_diagnostics": {
                "randomised_config_results": [{"configuration_sha256": configuration_hash}]
            }
        }
    ]
    run_path = data / "logs/run/demo.json"
    run_path.write_text(json.dumps(run_log), encoding="utf-8")
    cell_path = data / "records/primary/demo.json"
    cell_path.write_text(json.dumps({"winner_entry_index": 0}), encoding="utf-8")
    public_hash = hashlib.sha256(scene_path.read_bytes()).hexdigest()
    provenance = data / "provenance/normalized_file_provenance.csv"
    provenance.write_text(
        "cell_id,public_path,role,original_sha256,public_sha256\n"
        f"p-demo,data/scenes/demo.json,scene_bank,{'d' * 64},{public_hash}\n",
        encoding="utf-8",
    )
    (data / "provenance/normalization.json").write_text(
        json.dumps({"declaration": "test normalization"}), encoding="utf-8"
    )
    metadata = {
        "record_id": "p-demo",
        "study": "primary",
        "task": "demo",
        "seed": "0",
        "cell_record_path": "data/records/primary/demo.json",
        "run_log_path": "data/logs/run/demo.json",
    }
    spec = RenderSpec(
        record_id="p-demo",
        task="demo",
        skill_path=data / "skills/demo.yaml",
        parameters={},
        scene_bank_path=scene_path,
        scene_index=0,
        scene={},
        metadata=metadata,
    )
    model = type("Model", (), {"nq": 2, "nbody": 3})()
    return spec, bank, model, scene_path, provenance


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        ("task", "task does not match"),
        ("public_hash", "public hash mismatch"),
        ("evidence", "configuration evidence mismatch"),
        ("dimensions", "qpos dimensions are invalid"),
    ),
)
def test_normalized_scene_fallback_rejects_tampering(
    tmp_path: Path, mutation: str, message: str
) -> None:
    spec, bank, model, scene_path, provenance = _normalized_fixture(tmp_path)
    if mutation == "task":
        bank["task_name"] = "other"
        scene_path.write_text(json.dumps(bank), encoding="utf-8")
    elif mutation == "public_hash":
        fields = provenance.read_text(encoding="utf-8").strip().splitlines()
        columns = fields[1].split(",")
        columns[4] = "0" * 64
        fields[1] = ",".join(columns)
        provenance.write_text("\n".join(fields) + "\n", encoding="utf-8")
    elif mutation == "evidence":
        bank["configurations"][0]["configuration_sha256"] = "f" * 64
        scene_path.write_text(json.dumps(bank), encoding="utf-8")
        public_hash = hashlib.sha256(scene_path.read_bytes()).hexdigest()
        fields = provenance.read_text(encoding="utf-8").strip().splitlines()
        columns = fields[1].split(",")
        columns[4] = public_hash
        fields[1] = ",".join(columns)
        provenance.write_text("\n".join(fields) + "\n", encoding="utf-8")
    else:
        bank["configurations"][0]["backend_state"]["qpos_delta"] = [0.0]
        scene_path.write_text(json.dumps(bank), encoding="utf-8")
        public_hash = hashlib.sha256(scene_path.read_bytes()).hexdigest()
        fields = provenance.read_text(encoding="utf-8").strip().splitlines()
        columns = fields[1].split(",")
        columns[4] = public_hash
        fields[1] = ",".join(columns)
        provenance.write_text("\n".join(fields) + "\n", encoding="utf-8")
    with pytest.raises(RenderInputError, match=message):
        _validated_public_normalized_configuration(tmp_path, spec, bank, model)


def _reconstructed_fixture(tmp_path: Path) -> tuple[RenderSpec, dict, object, Path, Path, Path]:
    data = tmp_path / "data"
    for relative in (
        "scenes",
        "records/primary",
        "logs/run",
        "provenance",
        "skills",
        "parameters",
    ):
        (data / relative).mkdir(parents=True, exist_ok=True)
    (data / "skills/demo.yaml").write_text("skill: demo\n", encoding="utf-8")
    (data / "parameters/demo.json").write_text("{}", encoding="utf-8")
    source_path = data / "logs/run/demo.json"
    source_results = [
        {
            "configuration_index": 0,
            "configuration_seed": 101,
            "randomisation_debug": {
                "frozen_body_deltas": {"1": [0.1, 0.0, 0.0]},
                "frozen_qpos_delta": [0.0, 0.0],
                "scene_frozen": True,
            },
        },
        {
            "configuration_index": 1,
            "configuration_seed": 102,
            "randomisation_debug": {
                "frozen_body_deltas": {},
                "frozen_qpos_delta": [0.0, 0.2],
                "scene_frozen": True,
            },
        },
    ]
    source_path.write_text(
        json.dumps([{"iteration": 0, "posthoc_diagnostics": {"randomised_config_results": source_results}}]),
        encoding="utf-8",
    )
    cell_path = data / "records/primary/demo.json"
    cell_path.write_text(json.dumps({"record_id": "p-demo", "winner_entry_index": 0}), encoding="utf-8")
    configurations = []
    for source in source_results:
        debug = source["randomisation_debug"]
        configurations.append(
            {
                "schema_version": "paper-release",
                "config_index": source["configuration_index"],
                "seed": source["configuration_seed"],
                "configuration_sha256": None,
                "realized_scene_sha256": None,
                "realized_scene": None,
                "backend_state": {
                    "body_deltas": debug["frozen_body_deltas"],
                    "qpos_delta": debug["frozen_qpos_delta"],
                    "scene_frozen": True,
                },
            }
        )
    scene_path = data / "scenes/demo.json"
    bank = {
        "schema_version": "paper-release",
        "task_name": "demo",
        "outer_seed": 0,
        "k_runs": 2,
        "configurations": configurations,
    }
    scene_path.write_text(json.dumps(bank), encoding="utf-8")
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    public_hash = hashlib.sha256(scene_path.read_bytes()).hexdigest()
    provenance_path = data / "provenance/reconstructed_scene_banks.csv"
    provenance_path.write_text(
        "cell_id,source_container_path,source_container_original_sha256,entry_index,entry_iteration,evidence_field,configuration_count,configuration_sha256s,public_path,public_sha256,derivation\n"
        f"p-demo,data/logs/run/demo.json,{source_hash},0,0,posthoc_diagnostics.randomised_config_results[*].randomisation_debug,2,None|None,data/scenes/demo.json,{public_hash},lossless reconstruction\n",
        encoding="utf-8",
    )
    (data / "provenance/normalized_file_provenance.csv").write_text(
        "cell_id,public_path,role,attempt,original_sha256,public_sha256,normalization\n"
        f"p-demo,data/logs/run/demo.json,run_log,,{source_hash},{source_hash},test\n",
        encoding="utf-8",
    )
    metadata = {
        "record_id": "p-demo",
        "study": "primary",
        "task": "demo",
        "seed": "0",
        "cell_record_path": "data/records/primary/demo.json",
        "run_log_path": "data/logs/run/demo.json",
    }
    spec = RenderSpec(
        record_id="p-demo",
        task="demo",
        skill_path=data / "skills/demo.yaml",
        parameters={},
        scene_bank_path=scene_path,
        scene_index=0,
        scene={},
        metadata=metadata,
    )
    model = type("Model", (), {"nq": 2, "nbody": 3})()
    return spec, bank, model, scene_path, provenance_path, source_path


def test_reconstructed_scene_branch_accepts_provenance_bound_bank(tmp_path: Path) -> None:
    spec, bank, model, _scene_path, _provenance_path, _source_path = _reconstructed_fixture(tmp_path)
    configuration = _validated_reconstructed_configuration(tmp_path, spec, bank, model)
    assert configuration["config_index"] == 0
    assert configuration["configuration_sha256"] is None
    assert configuration["realized_scene"] is None


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        ("public_hash", "public hash mismatch"),
        ("source_hash", "source container hash mismatch"),
        ("seed", "scene-bank seed does not match"),
        ("index", "configuration index mismatch"),
        ("task", "task does not match"),
        ("dimensions", "qpos dimensions are invalid"),
        ("evidence", "backend evidence mismatch"),
    ),
)
def test_reconstructed_scene_branch_rejects_tampering(
    tmp_path: Path, mutation: str, message: str
) -> None:
    spec, bank, model, scene_path, provenance_path, source_path = _reconstructed_fixture(tmp_path)
    if mutation == "public_hash":
        fields = provenance_path.read_text(encoding="utf-8").strip().splitlines()
        columns = fields[1].split(",")
        columns[9] = "0" * 64
        fields[1] = ",".join(columns)
        provenance_path.write_text("\n".join(fields) + "\n", encoding="utf-8")
    elif mutation == "source_hash":
        source_path.write_text(source_path.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    elif mutation == "seed":
        bank["outer_seed"] = 5
    elif mutation == "index":
        bank["configurations"][0]["config_index"] = 1
    elif mutation == "task":
        bank["task_name"] = "other"
    elif mutation == "dimensions":
        bank["configurations"][0]["backend_state"]["qpos_delta"] = [0.0]
        source_document = json.loads(source_path.read_text(encoding="utf-8"))
        source_document[0]["posthoc_diagnostics"]["randomised_config_results"][0]["randomisation_debug"]["frozen_qpos_delta"] = [0.0]
        source_path.write_text(json.dumps(source_document), encoding="utf-8")
        fields = provenance_path.read_text(encoding="utf-8").strip().splitlines()
        columns = fields[1].split(",")
        columns[2] = hashlib.sha256(source_path.read_bytes()).hexdigest()
        fields[1] = ",".join(columns)
        provenance_path.write_text("\n".join(fields) + "\n", encoding="utf-8")
        normalized_path = source_path.parents[2] / "provenance/normalized_file_provenance.csv"
        normalized_fields = normalized_path.read_text(encoding="utf-8").strip().splitlines()
        normalized_columns = normalized_fields[1].split(",")
        normalized_columns[4] = columns[2]
        normalized_columns[5] = columns[2]
        normalized_fields[1] = ",".join(normalized_columns)
        normalized_path.write_text("\n".join(normalized_fields) + "\n", encoding="utf-8")
    else:
        bank["configurations"][0]["backend_state"]["qpos_delta"] = [0.0, 0.9]
    scene_path.write_text(json.dumps(bank), encoding="utf-8")
    if mutation not in {"public_hash", "source_hash"}:
        fields = provenance_path.read_text(encoding="utf-8").strip().splitlines()
        columns = fields[1].split(",")
        columns[9] = hashlib.sha256(scene_path.read_bytes()).hexdigest()
        fields[1] = ",".join(columns)
        provenance_path.write_text("\n".join(fields) + "\n", encoding="utf-8")
    with pytest.raises(RenderInputError, match=message):
        _validated_reconstructed_configuration(tmp_path, spec, bank, model)
