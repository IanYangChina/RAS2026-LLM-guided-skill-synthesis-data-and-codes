from __future__ import annotations

import json
import hashlib
import os
from pathlib import Path
from typing import Any


def select_winner(records: list[dict[str, Any]]) -> tuple[int, dict[str, Any]]:
    eligible = [(index, record) for index, record in enumerate(records) if isinstance(record.get("skill_yaml") or record.get("evaluated_skill_yaml"), str)]
    if not eligible:
        raise ValueError("cannot select a winner from an empty evaluated run log")
    def key(item: tuple[int, dict[str, Any]]) -> tuple[float, float, int]:
        index, record = item
        return (float(record.get("canonical_task_score", record.get("task_score", float("-inf")))), float(record.get("composite_score", float("-inf"))), -index)
    return max(eligible, key=key)

def _write_atomic(path: Path, content: str) -> None:
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, path)


def persist_winner(directory: Path, *, method: str, initialization: str, task: str, seed: int, subtask_mode: str, backend: str) -> dict[str, Any]:
    records = json.loads((directory / "run_log.json").read_text(encoding="utf-8"))
    index, winner = select_winner(records)
    skill_yaml = winner.get("skill_yaml") or winner.get("evaluated_skill_yaml")
    if not isinstance(skill_yaml, str): raise ValueError("winner does not contain an evaluated skill YAML")
    params = winner.get("best_params")
    def find_bank(value):
        if isinstance(value, dict):
            if isinstance(value.get("configuration_bank_sha256"), str): return value["configuration_bank_sha256"]
            for nested in value.values():
                found = find_bank(nested)
                if found: return found
        if isinstance(value, list):
            for nested in value:
                found = find_bank(nested)
                if found: return found
        return None
    identity = find_bank(winner)
    scientific = backend == "mujoco"
    if scientific and (not isinstance(params, dict) or not identity):
        raise ValueError("scientific winner requires optimized parameters and a frozen scene-bank hash")
    if not isinstance(params, dict): params = {}
    metadata = {"winner_record_index": index, "winner_iteration": winner.get("iteration"), "method": method, "initialization": initialization, "task": task, "seed": seed, "subtask_mode": subtask_mode, "backend": backend, "scientific": scientific, "canonical_task_score": winner.get("canonical_task_score", winner.get("task_score")), "composite_score": winner.get("composite_score"), "scene_bank_sha256": identity, "selection": "canonical_task_score, composite_score, earliest_record"}
    _write_atomic(directory / "best_skill.yaml", skill_yaml)
    _write_atomic(directory / "best_parameters.json", json.dumps(params, indent=2, sort_keys=True))
    if identity:
        _write_atomic(directory / "scene_bank_identity.json", json.dumps({"task": task, "seed": seed, "backend": backend, "scene_bank_sha256": identity}, indent=2, sort_keys=True))
    _write_atomic(directory / "winner.json", json.dumps(metadata, indent=2, sort_keys=True))
    return metadata
