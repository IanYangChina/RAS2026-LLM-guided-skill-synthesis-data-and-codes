from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _rows(relative: str):
    with (ROOT / relative).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def test_curated_cell_and_summary_counts():
    catalog = _rows("data/catalog.csv")
    assert len(catalog) == 1380
    assert sum(row["study"] == "primary" for row in catalog) == 900
    assert sum(row["study"] == "expert" for row in catalog) == 60
    assert sum(row["study"] == "semantic" for row in catalog) == 420
    assert len(_rows("data/paper_results/main/primary_task_summary.csv")) == 90
    assert len(_rows("data/paper_results/semantic/semantic_task_summary.csv")) == 42
    assert len(_rows("data/companions/generation_zero_catalog.csv")) == 10


def test_every_cell_has_complete_replay_identity():
    for row in _rows("data/catalog.csv"):
        assert row["render_addressable"] == "true"
        for field in ("skill_path", "parameters_path", "scene_bank_path", "cell_record_path", "run_log_path"):
            assert (ROOT / row[field]).is_file(), (row["record_id"], field)


def test_proposals_are_explicitly_non_replayable():
    skills = _rows("data/skill_catalog.csv")
    assert sum(row["role"] in {"selected_best", "executed_expert"} for row in skills) == 1380
    proposed = [row for row in skills if row["role"] == "proposed"]
    assert len(proposed) == 11700
    assert all(row["render_addressable"] == "false" for row in proposed)
    assert {row["evaluation_status"] for row in proposed} <= {"evaluated", "rejected", "skipped", "not_evaluated"}


def test_exact_reproduction_has_no_discrepancies(tmp_path):
    module = _load("reproduce_paper_results", ROOT / "scripts/reproduce_paper_results.py")
    report = module.reproduce(ROOT / "data", tmp_path)
    assert report["status"] == "ok"
    assert report["counts"]["total_cells"] == 1380
    assert report["counts"]["bootstrap_replicates"] == 20_000
    assert report["discrepancies"] == []
    trajectory_cells = list(csv.DictReader((tmp_path / "trajectory_cells.csv").open()))
    assert len(trajectory_cells) == 720
    assert all(row["source_run_log_path"].startswith("data/logs/run/") for row in trajectory_cells)
    persisted = json.loads((tmp_path / "verification_report.json").read_text())
    assert persisted["expert_comparison"]["expert_minus_create"] == 0.04196468749221507


def test_cma_source_aliases_resolve_uniquely():
    rows = _rows("data/catalog.csv")
    for source in ("llm_created", "expert_reference", "scaffold", "grammar_random"):
        selected = [row for row in rows if row["source"] == source]
        assert len(selected) == 60
        assert len({(row["task"], row["seed"]) for row in selected}) == 60


def test_strict_validator_ignores_a_completed_reanalysis_tree():
    import shutil

    reproduce = _load("reproduce_generated_output", ROOT / "scripts/reproduce_paper_results.py")
    validator = _load("validate_generated_output", ROOT / "scripts/validate_archive.py")
    output = ROOT / "reproduced_results" / "validator_regression"
    try:
        report = reproduce.reproduce(ROOT / "data", output)
        assert report["status"] == "ok"
        for row in _rows("data/paper_crosswalk.csv"):
            for relative in row["reproduced_outputs"].split(";"):
                assert (output / relative).is_file(), (row["paper_id"], relative)
        validator.main(["--root", str(ROOT), "--strict"])
    finally:
        shutil.rmtree(ROOT / "reproduced_results", ignore_errors=True)


def test_scientific_relation_validator_rejects_mutated_winner(tmp_path):
    validator = _load("validator_mutated_winner", ROOT / "scripts/validate_archive.py")
    (tmp_path / "data").mkdir()
    skill = tmp_path / "data/skill.yaml"
    skill.write_text("skill: mutated\n")
    params = tmp_path / "data/params.json"
    params.write_text("{}")
    bank = tmp_path / "data/bank.json"
    bank.write_text('{"configurations": [{"configuration_sha256": "scene"}]}')
    log = tmp_path / "data/log.json"
    log.write_text(json.dumps([{"iteration": 0, "canonical_task_score": 0.5, "composite_score": 0.4, "skill_yaml": "skill: expected\\n", "best_params": {}, "posthoc_diagnostics": {"randomised_config_results": [{"configuration_sha256": "scene"}]}}]))
    cell = tmp_path / "data/cell.json"
    row = {"record_id":"p-test","study":"primary","task":"peg_insert","arm":"test","skill_path":"data/skill.yaml","parameters_path":"data/params.json","scene_bank_path":"data/bank.json","run_log_path":"data/log.json","cell_record_path":"data/cell.json","task_score":"0.5"}
    cell.write_text(json.dumps({**row, "winner_entry_index": 0}))
    errors = []
    validator._validate_scientific_relations(tmp_path, [row], errors)
    assert any("exact declared winner YAML" in error for error in errors)


def test_scientific_relation_validator_rejects_mutated_params_scene_and_cell(tmp_path):
    validator = _load("validator_mutated_relations", ROOT / "scripts/validate_archive.py")
    (tmp_path / "data").mkdir()
    skill = tmp_path / "data/skill.yaml"; skill.write_text("skill: expected\n")
    params = tmp_path / "data/params.json"; params.write_text("{}")
    bank = tmp_path / "data/bank.json"; bank.write_text('{"configurations": [{"configuration_sha256": "scene"}]}')
    log = tmp_path / "data/log.json"; log.write_text(json.dumps([{"iteration":0,"canonical_task_score":0.5,"composite_score":0.4,"skill_yaml":"skill: expected\n","best_params":{},"posthoc_diagnostics":{"randomised_config_results":[{"configuration_sha256":"scene"}]}}]))
    row = {"record_id":"p-test","study":"primary","task":"peg_insert","arm":"test","skill_path":"data/skill.yaml","parameters_path":"data/params.json","scene_bank_path":"data/bank.json","run_log_path":"data/log.json","cell_record_path":"data/cell.json","task_score":"0.5"}
    cell = tmp_path / "data/cell.json"; cell.write_text(json.dumps({**row,"winner_entry_index":0}))
    for target, content, expected in ((params,'{"mutated": 1}',"parameters do not match"),(bank,'{"configurations": [{"configuration_sha256": "mutated"}]}',"scene bank does not match"),(cell,json.dumps({**row,"arm":"mutated","winner_entry_index":0}),"catalog/cell relation mismatch")):
        original = target.read_text(); target.write_text(content); errors=[]; validator._validate_scientific_relations(tmp_path,[row],errors); target.write_text(original)
        assert any(expected in error for error in errors), errors


def test_provenance_validator_rejects_mutated_output_hash(tmp_path):
    validator = _load("validator_mutated_provenance", ROOT / "scripts/validate_archive.py")
    provenance = tmp_path / "data/provenance"; provenance.mkdir(parents=True)
    output = tmp_path / "data/value.txt"; output.write_text("value")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    with (provenance / "normalized_file_provenance.csv").open("w", newline="") as handle:
        writer=csv.DictWriter(handle,["cell_id","public_path","role","attempt","original_sha256","public_sha256","normalization"]);writer.writeheader();writer.writerow({"cell_id":"p","public_path":"data/value.txt","role":"run_log","attempt":"","original_sha256":"0"*64,"public_sha256":digest,"normalization":"test"})
    for name, fields in (("winner_extractions.csv",["cell_id"]),("reconstructed_scene_banks.csv",["cell_id"]),("derived_records.csv",["cell_id","role"])):
        with (provenance/name).open("w",newline="") as handle: csv.DictWriter(handle,fields).writeheader()
    output.write_text("mutated")
    errors=[];validator._validate_provenance(tmp_path,[],errors)
    assert any("normalized provenance output hash mismatch" in error for error in errors)


def test_missing_trajectory_statistic_is_rejected():
    reproduce = _load("reproduce_missing_trajectory", ROOT / "scripts/reproduce_paper_results.py")
    try:
        reproduce._require_fields([{"arm": "x"}], {"arm", "retained_best"}, "trajectory cells")
    except ValueError as exc:
        assert "retained_best" in str(exc)
    else:
        raise AssertionError("missing trajectory statistic was accepted")
