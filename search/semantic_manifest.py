from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from search.semantic_context_policy import REALIZED_SCENE_CONTEXT_VERSION, SEMANTIC_CONTEXT_POLICY_VERSION, SUPPORTED_CONDITIONS

REQUIRED_CELL_FIELDS = ("task", "seed", "initial_skill_yaml", "initial_skill_yaml_sha256", "realized_scene_state_json", "realized_scene_state_sha256", "randomized_config_bank_json", "randomized_config_bank_sha256")


@dataclass(frozen=True)
class SemanticCell:
    task: str
    seed: int
    initial_skill_yaml_sha256: str
    realized_scene_state_sha256: str
    randomized_config_bank_sha256: str


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def load_cell(path: Path, *, task: str, seed: int, condition: str) -> tuple[SemanticCell, str]:
    if condition not in SUPPORTED_CONDITIONS: raise ValueError(f"unsupported semantic condition: {condition}")
    if not path.is_file(): raise FileNotFoundError(f"semantic manifest is required but missing: {path}")
    manifest: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    payload = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    digest = _digest(payload)
    if manifest.get("manifest_sha256") not in (None, digest): raise ValueError("semantic manifest hash mismatch")
    if manifest.get("semantic_policy_version", SEMANTIC_CONTEXT_POLICY_VERSION) != SEMANTIC_CONTEXT_POLICY_VERSION: raise ValueError("semantic policy capability mismatch")
    if manifest.get("realized_scene_context_version", REALIZED_SCENE_CONTEXT_VERSION) != REALIZED_SCENE_CONTEXT_VERSION: raise ValueError("realized-scene capability mismatch")
    matches = [row for row in manifest.get("cells", []) if row.get("task") == task and int(row.get("seed", -1)) == seed]
    if len(matches) != 1: raise LookupError(f"semantic manifest must contain exactly one cell for task={task}, seed={seed}")
    row = matches[0]
    if any(not isinstance(row.get(field), str) for field in REQUIRED_CELL_FIELDS[2:]): raise ValueError("semantic manifest cell omits required prompt or scene material")
    for content, field in ((row["initial_skill_yaml"], "initial_skill_yaml_sha256"), (row["realized_scene_state_json"], "realized_scene_state_sha256"), (row["randomized_config_bank_json"], "randomized_config_bank_sha256")):
        if len(row[field]) != 64 or hashlib.sha256(content.encode("utf-8")).hexdigest() != row[field]: raise ValueError(f"semantic manifest {field} mismatch")
    return SemanticCell(task, seed, row["initial_skill_yaml_sha256"], row["realized_scene_state_sha256"], row["randomized_config_bank_sha256"]), digest
