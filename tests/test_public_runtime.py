from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / name)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def catalog(path: Path, *, source: str = "llm_created", task: str = "peg_insert", seed: int = 0, digest: str | None = None) -> Path:
    target = ROOT / "tasks" / "seeds" / task / "seed_00.yaml"
    digest = digest or hashlib.sha256(target.read_bytes()).hexdigest()
    path.write_text("record_id,source,task,seed,path,sha256\nitem," + source + "," + task + "," + str(seed) + "," + target.relative_to(ROOT).as_posix() + "," + digest + "\n")
    return path


def manifest(path: Path, task: str = "peg_insert", seed: int = 0) -> Path:
    skill = (ROOT / "tasks" / "seeds" / task / "seed_00.yaml").read_text()
    scene, bank = "{}", "{}"
    row = {"task": task, "seed": seed, "initial_skill_yaml": skill, "initial_skill_yaml_sha256": hashlib.sha256(skill.encode()).hexdigest(), "realized_scene_state_json": scene, "realized_scene_state_sha256": hashlib.sha256(scene.encode()).hexdigest(), "randomized_config_bank_json": bank, "randomized_config_bank_sha256": hashlib.sha256(bank.encode()).hexdigest()}
    payload = {"semantic_policy_version": "semantic-context-policy-v1", "realized_scene_context_version": "skill-synthesis-realized-scene-context-v1", "cells": [row]}
    payload["manifest_sha256"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    path.write_text(json.dumps(payload))
    return path


def test_semantic_scene_removal_and_target_permutation() -> None:
    from search.semantic_context_policy import REALIZED_SCENE_BLOCK_MARKER, apply_policy

    original = {"task_specification": {"realized_geometry": {"a": [1], "b": [2]}}, "scene_entities": {"landmarks": {"a": [1], "b": [2]}}, "freest_anchor_resolution": {"anchors": {"a": [1], "b": [2]}}}
    assert not apply_policy("no_scene_description", original)["scene_entities"]["landmarks"]
    assert apply_policy("wrong_scene_targets", original)["scene_entities"]["landmarks"]["a"] == [2]
    assert REALIZED_SCENE_BLOCK_MARKER == "<!-- skill-synthesis:realized-scene:v1 -->"


def test_full_matrix_command_construction(tmp_path: Path) -> None:
    module = load_script("run_structural_search.py")
    created_catalog = catalog(tmp_path / "catalog.csv")
    for method in ("bandit", "map_qd", "llm"):
        for initialization in ("create", "scaffold", "random"):
            parser = module.build_parser()
            args = parser.parse_args(["--method", method, "--initialization", initialization, "--task", "peg_insert", "--catalog", str(created_catalog)])
            module._validate(args, parser)
            command = module._command(args, "peg_insert", 0, tmp_path / "stage")
            assert command and "--task" in command
            if initialization == "create" and method != "llm":
                assert "--initial-skill" in command


def test_primary_freest_has_no_manifest_or_initializer_replacement(tmp_path: Path) -> None:
    module = load_script("run_structural_search.py")
    for initialization in ("create", "scaffold", "random"):
        parser = module.build_parser()
        args = parser.parse_args(["--method", "llm", "--initialization", initialization, "--subtask-mode", "free", "--condition", "full", "--task", "peg_insert"])
        module._validate(args, parser)
        command = module._command(args, "peg_insert", 0, tmp_path / "stage")
        assert "--semantic-manifest-root" not in command
        assert "--initial-skill-yaml-sha256" not in command
        assert "--initial-skill" not in command
        assert "--system-prompt-file" not in command


def test_semantic_study_requires_manifest_and_pinned_prompt(tmp_path: Path) -> None:
    module = load_script("run_structural_search.py")
    source = manifest(tmp_path / "manifest.json")
    for condition in module.SEMANTIC_CONDITIONS:
        parser = module.build_parser()
        args = parser.parse_args(["--method", "llm", "--subtask-mode", "free", "--condition", condition, "--task", "peg_insert", "--semantic-study", "--semantic-manifest", str(source), "--dry-run"])
        module._validate(args, parser)
        command = module._command(args, "peg_insert", 0, tmp_path / "stage")
        assert "--semantic-manifest-root" in command
        assert "--randomized-config-bank-sha256" in command
        prompt = Path(command[command.index("--system-prompt-file") + 1])
        assert prompt.is_file() and hashlib.sha256(prompt.read_bytes()).hexdigest()


def test_parameter_resolution_never_falls_back_to_seed(tmp_path: Path) -> None:
    module = load_script("run_parameter_optimization.py")
    try:
        module.resolve_skill("expert_reference", "peg_insert", 0, None, tmp_path / "missing.csv", None)
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("missing catalog substituted a seed skill")
    assert module.resolve_skill("expert_reference", "peg_insert", 0, None, catalog(tmp_path / "catalog.csv", source="expert_reference"), None).is_file()


def test_parameter_optimization_lists_only_paper_tasks() -> None:
    module = load_script("run_parameter_optimization.py")
    assert module.PAPER_TASKS == ("door_push", "push_to_goal", "peg_insert", "peg_channel", "obstacle_reach", "grasp_place")
    parser = module.build_parser()
    assert parser.parse_args(["--task", "door_push"]).task == "door_push"
    try:
        parser.parse_args(["--task", "door_pull"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("parameter optimization accepted a non-paper task")


def test_catalog_resolution_requires_matching_sha256(tmp_path: Path) -> None:
    from search.public_catalog import resolve_record

    bad = catalog(tmp_path / "bad.csv", digest="0" * 64)
    try:
        resolve_record(bad, ROOT, source="llm_created", task="peg_insert", seed=0)
    except ValueError as exc:
        assert "hash mismatch" in str(exc)
    else:
        raise AssertionError("catalog accepted an incorrect skill digest")


def test_winner_order_atomic_outputs_and_replay_identity(tmp_path: Path) -> None:
    from search.winner import persist_winner

    first = (ROOT / "tasks" / "seeds" / "peg_insert" / "seed_00.yaml").read_text()
    bank = "a" * 64
    records = [{"iteration": 3, "skill_yaml": first, "task_score": 0.7, "composite_score": 0.1, "best_params": {"x": 1}, "configuration_bank_sha256": bank}, {"iteration": 1, "skill_yaml": first, "task_score": 0.7, "composite_score": 0.1, "best_params": {"x": 2}, "configuration_bank_sha256": bank}]
    (tmp_path / "run_log.json").write_text(json.dumps(records))
    winner = persist_winner(tmp_path, method="bandit", initialization="random", task="peg_insert", seed=0, subtask_mode="fixed", backend="mujoco")
    assert winner["winner_record_index"] == 0
    assert json.loads((tmp_path / "best_parameters.json").read_text())["x"] == 1
    assert json.loads((tmp_path / "scene_bank_identity.json").read_text())["scene_bank_sha256"] == bank


def test_scientific_winner_rejects_missing_replay_identity(tmp_path: Path) -> None:
    from search.winner import persist_winner

    skill = (ROOT / "tasks" / "seeds" / "peg_insert" / "seed_00.yaml").read_text()
    (tmp_path / "run_log.json").write_text(json.dumps([{"skill_yaml": skill, "task_score": 1.0, "composite_score": 1.0}]))
    try:
        persist_winner(tmp_path, method="bandit", initialization="random", task="peg_insert", seed=0, subtask_mode="fixed", backend="mujoco")
    except ValueError as exc:
        assert "optimized parameters" in str(exc)
    else:
        raise AssertionError("scientific winner lacked replay identity")


def test_no_implicit_mock_backend_in_structural_runners() -> None:
    for name in ("_bandit_search.py", "_mapqd_search.py"):
        text = (ROOT / "scripts" / name).read_text(encoding="utf-8")
        assert "MockSimulatorBackend" not in text
        assert "public --backend mock" in text


def test_validate_archive_rejects_personal_paths_and_duplicate_catalog(tmp_path: Path) -> None:
    module = load_script("validate_archive.py")
    (tmp_path / "README.md").write_text("ok")
    (tmp_path / "unsafe.txt").write_text("/home/" + "person/secret")
    try:
        module.main(["--root", str(tmp_path)])
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("validator accepted a personal path")


def test_validator_allows_blank_env_example_but_rejects_a_value(tmp_path: Path) -> None:
    module = load_script("validate_archive.py")
    (tmp_path / "README.md").write_text("ok")
    env = tmp_path / ".env.example"
    key_name = "DEEPSEEK_API_KEY"
    env.write_text(key_name + "=\n")
    module.main(["--root", str(tmp_path)])
    env.write_text(key_name + "=not-a-real-key\n")
    try:
        module.main(["--root", str(tmp_path)])
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("validator accepted a nonblank environment credential")


def test_validator_rejects_environment_files_except_the_example(tmp_path: Path) -> None:
    module = load_script("validate_archive.py")
    (tmp_path / "README.md").write_text("ok")
    key_name = "DEEPSEEK_API_KEY"
    (tmp_path / ".env.example").write_text(key_name + "=\n")
    module.main(["--root", str(tmp_path)])
    (tmp_path / ".env").write_text(key_name + "=\n")
    try:
        module.main(["--root", str(tmp_path)])
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("validator accepted a .env file")


def test_validator_scans_extensionless_text_without_reading_binary_assets(tmp_path: Path) -> None:
    module = load_script("validate_archive.py")
    (tmp_path / "README.md").write_text("ok")
    (tmp_path / "CONFIG").write_text("/" + "home/person/private")
    try:
        module.main(["--root", str(tmp_path)])
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("validator did not scan extensionless text")
    (tmp_path / "CONFIG").unlink()
    (tmp_path / "binary_asset").write_bytes(b"\0\xff\x00")
    module.main(["--root", str(tmp_path)])


def test_llm_credentials_are_environment_only(monkeypatch) -> None:
    module = load_script("_llm_search.py")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    try:
        module._load_deepseek_api_key()
    except EnvironmentError as exc:
        assert "DEEPSEEK_API_KEY" in str(exc)
    else:
        raise AssertionError("missing environment credential was accepted")


def test_semantic_ledger_provenance_and_first_policy_application(tmp_path: Path) -> None:
    module = load_script("_llm_search.py")
    manifest_path = manifest(tmp_path / "manifest.json")
    bound = {"manifest": json.loads(manifest_path.read_text())}
    prompt = ROOT / "search" / "prompts" / "public_semantic_pinned.txt"
    args = argparse.Namespace(condition="no_history", system_prompt_file=prompt)
    provenance = module._semantic_ledger_provenance(args, bound)
    before = "### Mutation History (most recent first)\n| Iter | Score | Task | Outcome |\n| --- | --- | --- | --- |\n| 0 | 0.1 | peg | failed |\n| 1 | 0.2 | peg | solved |\n\n## Next\ncontinue"
    after = module._apply_semantic_prompt_once("no_history", before)
    ledger = tmp_path / "manipulation_ledger.jsonl"
    module._append_semantic_ledger(ledger, iteration=0, attempt_kind="primary", condition="no_history", pre_prompt=before, post_prompt=after, provenance=provenance, total_iterations=1)
    row = json.loads(ledger.read_text().strip())
    assert row["applied"] is True and row["policy_hash"] == provenance["policy_hash"]
    assert row["pinned_system_prompt_sha256"] == hashlib.sha256(prompt.read_bytes()).hexdigest()


def test_standalone_semantic_preflight_subprocess(tmp_path: Path) -> None:
    source = manifest(tmp_path / "manifest.json")
    result = subprocess.run([sys.executable, "scripts/run_structural_search.py", "--method", "llm", "--subtask-mode", "free", "--condition", "full", "--task", "peg_insert", "--semantic-study", "--semantic-manifest", str(source), "--dry-run"], cwd=ROOT, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    assert "semantic-manifest-root" in result.stdout


def test_canned_llm_yaml_response_is_parseable() -> None:
    module = load_script("_llm_search.py")
    source = (ROOT / "tasks" / "seeds" / "peg_insert" / "seed_00.yaml").read_text()
    assert module._parse_full_skill_yaml("```yaml\n" + source + "\n```", "full") is not None


def test_validate_zip_membership(tmp_path: Path) -> None:
    import zipfile

    module = load_script("validate_archive.py")
    root = tmp_path / "archive"
    root.mkdir()
    (root / "README.md").write_text("ok")
    (root / "file.txt").write_text("ok")
    package = tmp_path / "archive.zip"
    with zipfile.ZipFile(package, "w") as handle:
        handle.write(root / "README.md", "archive/README.md")
        handle.write(root / "file.txt", "archive/file.txt")
    module.main(["--root", str(root), "--zip", str(package)])


def test_catalog_rejects_duplicate_and_traversal_records(tmp_path: Path) -> None:
    module = load_script("validate_archive.py")
    root = tmp_path / "archive"
    data = root / "data"
    data.mkdir(parents=True)
    (root / "README.md").write_text("ok")
    (data / "README.md").write_text("ok")
    (data / "catalog.csv").write_text("record_id,path\nduplicate,../outside.yaml\nduplicate,missing.yaml\n")
    errors: list[str] = []
    module._catalog(root, errors)
    assert any("traversal" in error for error in errors)
    assert any("duplicate" in error for error in errors)


def test_validator_ignores_generated_tree_outputs_but_rejects_packaged_outputs(tmp_path: Path) -> None:
    import zipfile

    module = load_script("validate_archive.py")
    root = tmp_path / "archive"
    cache = root / "module" / "__pycache__"
    cache.mkdir(parents=True)
    (root / "README.md").write_text("ok")
    (root / "module" / "README.md").write_text("ok")
    (cache / "module.cpython-310.pyc").write_bytes(b"cache")
    for relative in (".pytest_cache/state", "build/output", "dist/output", "package.egg-info/PKG-INFO", "orphan.pyc", "runs/result.json", "outputs/result.json", "renders/demo.gif", "reproduced_results/report.json"):
        output = root / relative
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("generated")
    module.main(["--root", str(root)])
    clean_package = tmp_path / "clean_archive.zip"
    with zipfile.ZipFile(clean_package, "w") as handle:
        handle.write(root / "README.md", "archive/README.md")
        handle.write(root / "module" / "README.md", "archive/module/README.md")
    module.main(["--root", str(root), "--zip", str(clean_package)])
    package = tmp_path / "archive.zip"
    with zipfile.ZipFile(package, "w") as handle:
        handle.write(root / "README.md", "archive/README.md")
        handle.write(root / "module" / "README.md", "archive/module/README.md")
        handle.write(cache / "module.cpython-310.pyc", "archive/module/__pycache__/module.cpython-310.pyc")
        handle.writestr("archive/package.egg-info/PKG-INFO", "generated")
        handle.writestr("archive/reproduced_results/report.json", "generated")
    try:
        module.main(["--root", str(root), "--zip", str(package)])
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("validator accepted packaged generated files")


def test_validator_rejects_packaged_environment_file(tmp_path: Path) -> None:
    import zipfile

    module = load_script("validate_archive.py")
    root = tmp_path / "archive"
    root.mkdir()
    (root / "README.md").write_text("ok")
    package = tmp_path / "archive.zip"
    with zipfile.ZipFile(package, "w") as handle:
        handle.write(root / "README.md", "archive/README.md")
        handle.writestr("archive/.env", "DEEPSEEK_API_KEY" + "=not-a-real-key\n")
    try:
        module.main(["--root", str(root), "--zip", str(package)])
    except SystemExit as exc:
        assert exc.code == 1
    else:
        raise AssertionError("validator accepted a packaged .env file")


def test_install_validator_render_context_is_optional_and_headless_mode_is_explicit(monkeypatch, capsys) -> None:
    validator = load_script("../environment/validate_install.py")
    monkeypatch.setattr(validator, "PACKAGES", {})
    monkeypatch.setattr(validator, "RUNTIME_MODULES", ())
    monkeypatch.setattr(validator, "PUBLIC_SCRIPTS", ())
    calls: list[object] = []
    monkeypatch.setattr(validator, "check_render_context", lambda: calls.append("checked"))
    validator.main([])
    assert calls == []
    assert "skipped" in capsys.readouterr().out
    monkeypatch.delenv("MUJOCO_GL", raising=False)
    validator.main(["--headless-render-context"])
    assert calls == ["checked"]
    assert os.environ["MUJOCO_GL"] == "osmesa"


def test_install_validator_reports_requested_render_context_failures(monkeypatch) -> None:
    validator = load_script("../environment/validate_install.py")
    monkeypatch.setattr(validator, "PACKAGES", {})
    monkeypatch.setattr(validator, "RUNTIME_MODULES", ())
    monkeypatch.setattr(validator, "PUBLIC_SCRIPTS", ())
    monkeypatch.setattr(validator, "check_render_context", lambda: (_ for _ in ()).throw(RuntimeError("no context")))
    try:
        validator.main(["--check-render-context"])
    except SystemExit as exc:
        assert "render-context check failed" in str(exc)
    else:
        raise AssertionError("requested render context failure did not fail validation")


def test_install_validator_releases_a_minimal_render_context() -> None:
    validator = load_script("../environment/validate_install.py")

    class Context:
        made_current = False
        freed = False

        def __init__(self, width: int, height: int) -> None:
            assert (width, height) == (1, 1)

        def make_current(self) -> None:
            type(self).made_current = True

        def free(self) -> None:
            type(self).freed = True

    class Model:
        @staticmethod
        def from_xml_string(xml: str) -> object:
            assert "<mujoco>" in xml
            return object()

    class Data:
        def __init__(self, model: object) -> None:
            self.model = model

    class Renderer:
        closed = False
        rendered = False

        def __init__(self, model: object, *, height: int, width: int) -> None:
            assert (height, width) == (1, 1)

        def update_scene(self, data: object) -> None:
            assert isinstance(data, Data)

        def render(self) -> None:
            type(self).rendered = True

        def close(self) -> None:
            type(self).closed = True

    FakeMujoco = type("FakeMujoco", (), {"GLContext": Context, "MjModel": Model, "MjData": Data, "Renderer": Renderer})

    validator.check_render_context(FakeMujoco)
    assert Context.made_current and Context.freed
    assert Renderer.rendered and Renderer.closed


def test_reproduce_cli_writes_a_reanalysis_report(tmp_path: Path) -> None:
    module = load_script("reproduce_paper_results.py")
    data = tmp_path / "data"
    data.mkdir()
    (data / "catalog.csv").write_text("record_id,task,arm,task_score\nrow,peg_insert,Random-Bandit,0.5\n")
    output = tmp_path / "results"
    module.main(["--data-root", str(data), "--out-dir", str(output)])
    report = json.loads((output / "paper_summary.json").read_text())
    assert report["status"] == "ok" and report["groups"][0]["mean_task_score"] == 0.5


def test_semantic_study_defaults_to_random_and_rejects_other_initializers(tmp_path: Path) -> None:
    module = load_script("run_structural_search.py")
    source = manifest(tmp_path / "manifest.json")
    parser = module.build_parser()
    default_args = parser.parse_args(["--method", "llm", "--subtask-mode", "free", "--condition", "full", "--task", "peg_insert", "--semantic-study", "--semantic-manifest", str(source)])
    module._validate(default_args, parser)
    assert default_args.initialization == "random"
    command = module._command(default_args, "peg_insert", 0, tmp_path / "stage")
    assert command[command.index("--init-mode") + 1] == "grammar_uniform_random"
    for initialization in ("create", "scaffold"):
        rejected = parser.parse_args(["--method", "llm", "--initialization", initialization, "--subtask-mode", "free", "--condition", "full", "--task", "peg_insert", "--semantic-study", "--semantic-manifest", str(source)])
        try:
            module._validate(rejected, parser)
        except SystemExit as exc:
            assert exc.code == 2
        else:
            raise AssertionError(f"semantic study accepted {initialization}")


def test_semantic_random_mock_winner_metadata(tmp_path: Path) -> None:
    module = load_script("run_structural_search.py")
    source = manifest(tmp_path / "manifest.json")
    parser = module.build_parser()
    args = parser.parse_args(["--method", "llm", "--subtask-mode", "free", "--condition", "full", "--task", "peg_insert", "--semantic-study", "--semantic-manifest", str(source), "--backend", "mock"])
    module._validate(args, parser)
    output = tmp_path / "semantic_random"
    module._mock_run(output, args, "peg_insert", 0)
    winner = json.loads((output / "winner.json").read_text())
    assert winner["initialization"] == "random" and winner["scientific"] is False


def test_all_task_assets_build_a_mujoco_model() -> None:
    from scripts.task_configs import SIM_CONFIGS
    from simulation.scene import SceneConfig, build_scene

    for task, config in SIM_CONFIGS.items():
        model = build_scene(SceneConfig(robot=config.get("robot", "panda"), gripper=config.get("gripper"), object_xml=config.get("object_xml"), target_markers=config.get("target_markers", ()), tcp_markers=config.get("tcp_markers", ())))
        assert model.nq > 0, task
