#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
import sys
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

if str(Path(__file__).resolve().parent) not in sys.path:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
from release_safety import _is_generated_path, _is_text_file, _scan_raw_bytes, _scan_relative_name, _scan_text


def _is_disallowed_env_path(path: Path | PurePosixPath) -> bool:
    """Only the intentionally blank .env.example template may be distributed."""
    return path.name.startswith(".env") and path.name != ".env.example"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Check catalog links, release safety, and package membership.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--zip", type=Path)
    parser.add_argument("--expected-primary", type=int)
    parser.add_argument("--expected-expert", type=int)
    parser.add_argument("--expected-semantic", type=int)
    parser.add_argument("--expected-total", type=int)
    parser.add_argument("--strict", action="store_true")
    return parser


def _catalog(root: Path, errors: list[str]) -> list[dict[str, str]]:
    try:
        catalog = _safe_reference(root, "data/catalog.csv")
    except ValueError as exc:
        errors.append(f"unsafe catalog path: {exc}")
        return []
    if not catalog.is_file():
        return []
    rows = list(csv.DictReader(catalog.open(encoding="utf-8", newline="")))
    seen: set[str] = set()
    for index, row in enumerate(rows, start=2):
        record_id, target = row.get("record_id", ""), row.get("path", "")
        if not record_id or record_id in seen:
            errors.append(f"catalog row {index} has duplicate or empty record_id")
        seen.add(record_id)
        try:
            candidate = _safe_reference(root, target)
        except ValueError as exc:
            errors.append(f"catalog row {index} has unsafe traversal path: {exc}")
            continue
        if not candidate.is_file():
            errors.append(f"catalog row {index} points to missing file: {target}")
            continue
        digest = row.get("sha256")
        if digest and hashlib.sha256(candidate.read_bytes()).hexdigest() != digest:
            errors.append(f"catalog row {index} hash mismatch: {target}")
    return rows


def _safe_reference(root: Path, relative: str, *, base: Path | None = None) -> Path:
    """Resolve an archive reference without permitting absolute or escaping paths."""
    if not relative or not isinstance(relative, str) or "\\" in relative or relative.startswith("/") or re.match(r"^[A-Za-z]:", relative):
        raise ValueError(f"invalid relative path: {relative!r}")
    if any(part in {"", ".", ".."} for part in relative.split("/")):
        raise ValueError(f"non-canonical relative path: {relative!r}")
    root_real = root.resolve()
    candidate = ((base or root) / relative).resolve()
    if not candidate.is_relative_to(root_real) or candidate == root_real:
        raise ValueError(f"path escapes release root: {relative!r}")
    return candidate


def _validate_reference_paths(root: Path, rows: list[dict[str, str]], errors: list[str]) -> None:
    """Check every CSV/manifest path before any strict science-file dereference."""
    def check(value: str, label: str, *, base: Path | None = None) -> None:
        try:
            _safe_reference(root, value, base=base)
        except ValueError as exc:
            errors.append(f"unsafe {label}: {exc}")

    for row in rows:
        for field in ("path", "skill_path", "parameters_path", "scene_bank_path", "cell_record_path", "run_log_path"):
            check(row.get(field, ""), f"catalog {row.get('record_id', '')} {field}")
    tables = {
        "data/skill_catalog.csv": ("path", "scene_bank_path"),
        "data/companions/generation_zero_catalog.csv": ("path",),
        "data/provenance/normalized_file_provenance.csv": ("public_path",),
        "data/provenance/winner_extractions.csv": ("public_path", "source_container_path"),
        "data/provenance/reconstructed_scene_banks.csv": ("public_path", "source_container_path"),
        "data/provenance/derived_records.csv": ("public_path", "source_container_path"),
    }
    for table, fields in tables.items():
        try:
            path = _safe_reference(root, table)
        except ValueError as exc:
            errors.append(f"unsafe table path: {exc}")
            continue
        if not path.is_file():
            continue
        with path.open(encoding="utf-8", newline="") as handle:
            for index, row in enumerate(csv.DictReader(handle), start=2):
                for field in fields:
                    check(row.get(field, ""), f"{table} row {index} {field}")
                if table == "data/skill_catalog.csv" and row.get("parameters_path"):
                    check(row["parameters_path"], f"{table} row {index} parameters_path")
    try:
        crosswalk = _safe_reference(root, "data/paper_crosswalk.csv")
        data = _safe_reference(root, "data")
        manifest = _safe_reference(root, "data/provenance/checksums.sha256")
    except ValueError as exc:
        errors.append(f"unsafe data table path: {exc}")
        return
    if crosswalk.is_file():
        with crosswalk.open(encoding="utf-8", newline="") as handle:
            for index, row in enumerate(csv.DictReader(handle), start=2):
                for field in ("public_sources", "reproduced_outputs"):
                    for reference in row.get(field, "").split(";"):
                        check(reference, f"crosswalk row {index} {field}")
    if manifest.is_file():
        seen: set[str] = set()
        for index, line in enumerate(manifest.read_text(encoding="utf-8").splitlines(), start=1):
            parts = line.split("  ", 1)
            if len(parts) != 2 or not re.fullmatch(r"[0-9a-f]{64}", parts[0]):
                errors.append(f"invalid checksum manifest line {index}")
                continue
            if parts[1] in seen:
                errors.append(f"duplicate checksum manifest path at line {index}")
            seen.add(parts[1])
            check(parts[1], f"checksum manifest line {index}", base=data)


def _zip_membership(archive: Path, root: Path, errors: list[str]) -> None:
    if not archive.is_file():
        errors.append(f"zip does not exist: {archive}")
        return
    expected = {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and not _is_generated_path(path.relative_to(root))
    }
    with zipfile.ZipFile(archive) as handle:
        names = [name for name in handle.namelist() if not name.endswith("/")]
    generated_members = [name for name in names if _is_generated_path(PurePosixPath(name))]
    if generated_members:
        errors.append("zip must not contain generated cache or build files")
    if any(_is_disallowed_env_path(PurePosixPath(name)) for name in names):
        errors.append("zip must not contain .env files")
    prefixes = {name.split("/", 1)[0] for name in names if "/" in name}
    if len(prefixes) != 1:
        errors.append("zip must contain exactly one top-level directory")
        return
    actual = {name.split("/", 1)[1] for name in names if "/" in name}
    if actual != expected:
        errors.append("zip membership does not exactly match archive directory")



def _validate_public_data(root: Path, rows: list[dict[str, str]], errors: list[str]) -> None:
    """Validate the immutable cell, skill, crosswalk, summary, and checksum contracts."""
    data = root / "data"
    required_catalog = {"record_id", "study", "task", "arm", "seed", "task_score", "skill_path", "parameters_path", "scene_bank_path", "cell_record_path", "run_log_path", "sha256", "render_addressable"}
    if rows and not required_catalog.issubset(rows[0]):
        errors.append(f"catalog missing fields: {sorted(required_catalog - set(rows[0]))}")
    for row in rows:
        for field in ("skill_path", "parameters_path", "scene_bank_path", "cell_record_path", "run_log_path"):
            value = row.get(field, "")
            if not value or not (root / value).is_file(): errors.append(f"catalog {row.get('record_id')} missing {field}: {value}")
        if row.get("render_addressable") != "true": errors.append(f"selected cell is not render-addressable: {row.get('record_id')}")
    studies = {kind: sum(row.get("study") == kind for row in rows) for kind in ("primary", "expert", "semantic")}
    if studies != {"primary": 900, "expert": 60, "semantic": 420}: errors.append(f"cell study counts are not 900/60/420: {studies}")
    for source in ("llm_created", "expert_reference", "scaffold", "grammar_random"):
        aliases = [row for row in rows if row.get("source") == source]
        identities = {(row.get("task"), row.get("seed")) for row in aliases}
        if len(aliases) != 60 or len(identities) != 60: errors.append(f"CMA source alias is not uniquely resolvable for 60 task/seed cells: {source}")
    def csv_rows(path: Path) -> list[dict[str, str]]:
        if not path.is_file(): errors.append(f"missing data table: {path.relative_to(root)}"); return []
        with path.open(encoding="utf-8", newline="") as handle: return list(csv.DictReader(handle))
    primary = csv_rows(data / "paper_results/main/primary_task_summary.csv")
    semantic = csv_rows(data / "paper_results/semantic/semantic_task_summary.csv")
    companions = csv_rows(data / "companions/generation_zero_catalog.csv")
    crosswalk = csv_rows(data / "paper_crosswalk.csv")
    skills = csv_rows(data / "skill_catalog.csv")
    winner_provenance = csv_rows(data / "provenance/winner_extractions.csv")
    scene_provenance = csv_rows(data / "provenance/reconstructed_scene_banks.csv")
    derived_provenance = csv_rows(data / "provenance/derived_records.csv")
    if len(primary) != 90: errors.append(f"expected 90 primary task-summary rows; found {len(primary)}")
    if len(semantic) != 42: errors.append(f"expected 42 semantic task-summary rows; found {len(semantic)}")
    if len(companions) != 10: errors.append(f"expected 10 generation-zero companions; found {len(companions)}")
    if len(winner_provenance) != 552: errors.append(f"expected 552 winner-extraction provenance rows; found {len(winner_provenance)}")
    if len(scene_provenance) != 540: errors.append(f"expected 540 reconstructed-scene provenance rows; found {len(scene_provenance)}")
    if len(derived_provenance) != 2760: errors.append(f"expected 2760 derived-record provenance rows; found {len(derived_provenance)}")
    selected = [row for row in skills if row.get("role") in {"selected_best", "executed_expert"}]
    if len(selected) != 1380: errors.append(f"expected 1380 selected/executed skill rows; found {len(selected)}")
    permitted_status = {"evaluated", "evaluated_generation_zero", "rejected", "skipped", "not_evaluated"}
    seen_skills: set[str] = set()
    for index, row in enumerate(skills, start=2):
        skill_id, relative = row.get("skill_id", ""), row.get("path", "")
        if not skill_id or skill_id in seen_skills: errors.append(f"skill catalog row {index} has duplicate or empty skill_id")
        seen_skills.add(skill_id)
        path = root / relative
        if not relative or not path.is_file(): errors.append(f"skill catalog row {index} has missing path: {relative}")
        elif row.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest(): errors.append(f"skill catalog row {index} hash mismatch: {relative}")
        if row.get("evaluation_status") not in permitted_status: errors.append(f"skill catalog row {index} has invalid evaluation status")
        if row.get("role") == "proposed" and row.get("render_addressable") != "false": errors.append(f"unevaluated proposal marked render-addressable: {skill_id}")
    catalog_by_id = {row.get("record_id", ""): row for row in rows}
    for row in companions:
        path = root / row.get("path", "")
        if not path.is_file() or row.get("sha256") != hashlib.sha256(path.read_bytes()).hexdigest(): errors.append(f"invalid generation-zero companion: {row.get('companion_id')}")
        primary = catalog_by_id.get(row.get("primary_record_id", ""))
        if primary is None:
            errors.append(f"generation-zero companion has no primary cell: {row.get('companion_id')}")
            continue
        if any(str(row.get(key, "")) != str(primary.get(key, "")) for key in ("task", "arm", "seed")):
            errors.append(f"generation-zero companion identity mismatch: {row.get('companion_id')}")
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
            score = float(document["optimization_metrics"]["canonical_task_score"])
            if abs(score - float(row["canonical_task_score"])) > 1e-12 or abs(score - float(primary["generation_zero_task_score"])) > 1e-12:
                errors.append(f"generation-zero companion score mismatch: {row.get('companion_id')}")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
            errors.append(f"invalid generation-zero companion content {row.get('companion_id')}: {exc}")
    for row in crosswalk:
        if not row.get("reproduced_outputs"): errors.append(f"crosswalk has no reproduced output coverage: {row.get('paper_id')}")
        sources = row.get("public_sources", "").split(";")
        hashes = row.get("source_sha256", "").split(";")
        if len(sources) != len(hashes): errors.append(f"crosswalk hash arity mismatch: {row.get('paper_id')}"); continue
        for relative, digest in zip(sources, hashes):
            path = root / relative
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest: errors.append(f"invalid crosswalk source: {row.get('paper_id')} -> {relative}")
    manifest = data / "provenance/checksums.sha256"
    if not manifest.is_file(): errors.append("missing data checksum manifest")
    else:
        listed = {}
        for line in manifest.read_text(encoding="utf-8").splitlines():
            digest, relative = line.split("  ", 1); listed[relative] = digest
        actual = {path.relative_to(data).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in data.rglob("*") if path.is_file() and path != manifest}
        if listed != actual: errors.append("data checksum manifest does not exactly match the curated data tree")


def _winner_record(log: list[dict[str, Any]]) -> tuple[int, dict[str, Any]]:
    candidates = []
    for index, record in enumerate(log):
        score = record.get("canonical_task_score", record.get("task_score"))
        if score is not None:
            composite = record.get("composite_score")
            candidates.append((float(score), float(composite) if composite is not None else -math.inf, -index, index, record))
    if not candidates: raise ValueError("run log has no scored record")
    _, _, _, index, record = max(candidates)
    return index, record

def _record_parameters(record: dict[str, Any]) -> dict[str, Any]:
    if isinstance(record.get("best_params"), dict): return record["best_params"]
    results = record.get("posthoc_diagnostics", {}).get("randomised_config_results", [])
    return results[0].get("best_params", {}) if results else {}

def _validate_scientific_relations(root: Path, rows: list[dict[str, str]], errors: list[str]) -> None:
    """Independently bind catalog rows to cell, declared winner, parameters, and scenes."""
    for row in rows:
        rid = row.get("record_id", "")
        try:
            cell = json.loads((root / row["cell_record_path"]).read_text(encoding="utf-8"))
            if any(str(cell.get(key, "")) != str(row.get(key, "")) for key in ("record_id", "study", "task", "arm", "skill_path", "parameters_path", "scene_bank_path", "run_log_path")):
                errors.append(f"catalog/cell relation mismatch: {rid}")
            container = json.loads((root / row["run_log_path"]).read_text(encoding="utf-8"))
            if row.get("study") == "expert":
                expected_yaml = container.get("expert_yaml", "")
                expected_params = container.get("optimization", {}).get("optimized_params", {})
                expected_score = container.get("optimization", {}).get("canonical_task_score")
                expected_hashes = container.get("configuration_sha256", [])
            else:
                index, winner = _winner_record(container)
                expected_yaml = winner.get("evaluated_skill_yaml") or winner.get("skill_yaml") or ""
                expected_params = _record_parameters(winner)
                expected_score = winner.get("canonical_task_score", winner.get("task_score"))
                expected_hashes = [item.get("configuration_sha256", "") for item in winner.get("posthoc_diagnostics", {}).get("randomised_config_results", [])]
                if int(cell.get("winner_entry_index", -1)) != index: errors.append(f"cell winner entry mismatch: {rid}")
            if expected_score is None or abs(float(expected_score) - float(row["task_score"])) > 1e-12: errors.append(f"catalog/winner score mismatch: {rid}")
            skill_bytes = (root / row["skill_path"]).read_bytes()
            if skill_bytes != expected_yaml.encode("utf-8"): errors.append(f"catalog skill is not exact declared winner YAML: {rid}")
            if json.loads((root / row["parameters_path"]).read_text(encoding="utf-8")) != expected_params: errors.append(f"catalog parameters do not match declared winner: {rid}")
            bank = json.loads((root / row["scene_bank_path"]).read_text(encoding="utf-8"))
            actual_hashes = [item.get("configuration_sha256", "") for item in bank.get("configurations", [])]
            if expected_hashes and actual_hashes != expected_hashes: errors.append(f"catalog scene bank does not match winner evidence: {rid}")
        except (KeyError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
            errors.append(f"scientific relation validation failed for {rid}: {exc}")


def _validate_provenance(root: Path, rows: list[dict[str, str]], errors: list[str]) -> None:
    """Validate normalized and derived provenance against distributed evidence."""
    provenance = root / "data/provenance"
    def read(name: str) -> list[dict[str, str]]:
        with (provenance / name).open(encoding="utf-8", newline="") as handle:
            return list(csv.DictReader(handle))
    normalized = read("normalized_file_provenance.csv")
    winner_rows = read("winner_extractions.csv")
    scene_rows = read("reconstructed_scene_banks.csv")
    derived_rows = read("derived_records.csv")
    permitted_roles = {"api_metadata", "realized_prompt", "response_skill", "proposal_metadata", "run_log", "scene_bank", "selected_skill", "winner_skill_extraction"}
    normalized_by_path: dict[str, dict[str, str]] = {}
    for row in normalized:
        path = root / row["public_path"]
        if row["role"] not in permitted_roles: errors.append(f"invalid normalized provenance role: {row['role']}")
        if row["public_path"] in normalized_by_path: errors.append(f"duplicate normalized provenance output: {row['public_path']}")
        normalized_by_path[row["public_path"]] = row
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != row["public_sha256"]: errors.append(f"normalized provenance output hash mismatch: {row['public_path']}")
        if not re.fullmatch(r"[0-9a-f]{64}", row["original_sha256"]): errors.append(f"invalid normalized provenance source hash: {row['public_path']}")

    catalog_by_id = {row["record_id"]: row for row in rows}
    for row in winner_rows:
        rid = row["cell_id"]
        try:
            catalog = catalog_by_id[rid]
            if row["source_container_path"] != catalog["run_log_path"] or row["public_path"] != catalog["skill_path"]: raise ValueError("catalog paths")
            normalized_source = normalized_by_path[row["source_container_path"]]
            if normalized_source["original_sha256"] != row["source_container_original_sha256"]: raise ValueError("source hash")
            log = json.loads((root / row["source_container_path"]).read_text(encoding="utf-8")); index = int(row["entry_index"]); entry = log[index]
            if str(entry.get("iteration", "")) != row["entry_iteration"]: raise ValueError("entry iteration")
            if row["embedded_field"] not in {"skill_yaml", "evaluated_skill_yaml"} or row["embedded_field"] not in entry: raise ValueError("embedded field")
            embedded = entry[row["embedded_field"]].encode("utf-8"); embedded_hash = hashlib.sha256(embedded).hexdigest()
            public = (root / row["public_path"]).read_bytes(); public_hash = hashlib.sha256(public).hexdigest()
            if embedded_hash != row["selected_embedded_sha256"] or public_hash != row["public_sha256"] or public != embedded: raise ValueError("selected/public bytes")
            normalized_skill = normalized_by_path[row["public_path"]]
            cell = json.loads((root / catalog["cell_record_path"]).read_text(encoding="utf-8"))
            if not re.fullmatch(r"[0-9a-f]{64}", normalized_skill["original_sha256"]) or row["superseded_top_level_sha256"] not in cell.get("source_hashes", {}).values(): raise ValueError("superseded hash")
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
            errors.append(f"winner provenance mismatch {rid}: {exc}")

    for row in scene_rows:
        rid = row["cell_id"]
        try:
            catalog = catalog_by_id[rid]
            if row["source_container_path"] != catalog["run_log_path"] or row["public_path"] != catalog["scene_bank_path"]: raise ValueError("catalog paths")
            if normalized_by_path[row["source_container_path"]]["original_sha256"] != row["source_container_original_sha256"]: raise ValueError("source hash")
            log = json.loads((root / row["source_container_path"]).read_text(encoding="utf-8")); entry = log[int(row["entry_index"])]
            if str(entry.get("iteration", "")) != row["entry_iteration"] or row["evidence_field"] != "posthoc_diagnostics.randomised_config_results[*].randomisation_debug": raise ValueError("entry/field")
            evidence = entry["posthoc_diagnostics"]["randomised_config_results"]
            bank = json.loads((root / row["public_path"]).read_text(encoding="utf-8")); configurations = bank["configurations"]
            if len(evidence) != int(row["configuration_count"]) or len(configurations) != len(evidence): raise ValueError("configuration count")
            expected_hashes = "|".join(str(item["configuration_sha256"]) if "configuration_sha256" in item else "" for item in evidence)
            if expected_hashes != row["configuration_sha256s"]: raise ValueError("configuration hash list")
            for config_index, (source, output) in enumerate(zip(evidence, configurations)):
                debug = source["randomisation_debug"]
                if output.get("seed") != source.get("configuration_seed", source.get("seed")): raise ValueError("seed")
                if output.get("config_index") != source.get("configuration_index", config_index): raise ValueError("configuration index")
                if output.get("configuration_sha256") != source.get("configuration_sha256", ""): raise ValueError("configuration hash")
                state = output.get("backend_state", {})
                if state.get("body_deltas") != debug.get("frozen_body_deltas") or state.get("qpos_delta") != debug.get("frozen_qpos_delta") or state.get("scene_frozen") != debug.get("scene_frozen"): raise ValueError("frozen body/qpos evidence")
            if hashlib.sha256((root / row["public_path"]).read_bytes()).hexdigest() != row["public_sha256"]: raise ValueError("output hash")
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
            errors.append(f"reconstructed scene provenance mismatch {rid}: {exc}")

    role_counts = {role: sum(row["role"] == role for row in derived_rows) for role in ("cell_record", "parameter_map")}
    if role_counts != {"cell_record": 1380, "parameter_map": 1380}: errors.append(f"derived provenance role counts mismatch: {role_counts}")
    for row in derived_rows:
        rid = row["cell_id"]
        try:
            catalog = catalog_by_id[rid]; expected_path = catalog["cell_record_path" if row["role"] == "cell_record" else "parameters_path"]
            if row["public_path"] != expected_path or hashlib.sha256((root / expected_path).read_bytes()).hexdigest() != row["public_sha256"]: raise ValueError("output path/hash")
            if row["source_container_path"] != catalog["run_log_path"] or normalized_by_path[row["source_container_path"]]["original_sha256"] != row["source_container_original_sha256"]: raise ValueError("source path/hash")
            if row["role"] == "parameter_map" and row["evidence_field"] != "best_params or configuration-zero posthoc best_params": raise ValueError("parameter evidence field")
            if row["role"] == "cell_record" and row["evidence_field"] != "winner scores, identities, and source hashes": raise ValueError("cell evidence field")
            if row["entry_index"] != "canonical":
                log = json.loads((root / row["source_container_path"]).read_text(encoding="utf-8")); index = int(row["entry_index"])
                if index < 0 or index >= len(log): raise ValueError("entry index")
        except (KeyError, IndexError, TypeError, ValueError, json.JSONDecodeError, OSError) as exc:
            errors.append(f"derived provenance mismatch {rid}/{row.get('role')}: {exc}")

def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    root, errors = args.root.resolve(), []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if _is_generated_path(relative):
            continue
        _scan_relative_name(relative, errors)
        if path.is_symlink():
            errors.append(f"symlink is not permitted: {path.relative_to(root)}")
            continue
        if path.is_file() and _is_disallowed_env_path(relative): errors.append(f"environment file is not permitted: {relative}")
        if path.is_file() and path.stat().st_size > 100 * 1024 * 1024: errors.append(f"file exceeds 100 MiB: {path.relative_to(root)}")
        if path.is_file() and _is_text_file(path): _scan_text(path, root, errors)
        if path.is_file(): _scan_raw_bytes(path, root, errors)
    for directory in (path for path in root.rglob("*") if path.is_dir() and not _is_generated_path(path.relative_to(root))):
        if not (directory / "README.md").is_file(): errors.append(f"directory missing README: {directory.relative_to(root)}")
    rows = _catalog(root, errors)
    if args.strict and not rows: errors.append("missing data/catalog.csv")
    by_kind = {"primary": args.expected_primary, "expert": args.expected_expert, "semantic": args.expected_semantic}
    if args.strict:
        by_kind = {"primary": 900 if args.expected_primary is None else args.expected_primary, "expert": 60 if args.expected_expert is None else args.expected_expert, "semantic": 420 if args.expected_semantic is None else args.expected_semantic}
        if args.expected_total is None: args.expected_total = 1380
    for kind, expected in by_kind.items():
        if expected is not None and sum(row.get("study") == kind for row in rows) != expected: errors.append(f"expected {expected} {kind} catalog records")
    if args.expected_total is not None and len(rows) != args.expected_total: errors.append(f"expected {args.expected_total} catalog records")
    if args.strict:
        _validate_reference_paths(root, rows, errors)
        if not errors:
            _validate_public_data(root, rows, errors)
            _validate_scientific_relations(root, rows, errors)
            _validate_provenance(root, rows, errors)
    if args.zip: _zip_membership(args.zip, root, errors)
    report: dict[str, Any] = {"ok": not errors, "errors": errors, "catalog_records": len(rows)}
    print(json.dumps(report, indent=2, sort_keys=True))
    if errors: raise SystemExit(1)


if __name__ == "__main__": main()
