from __future__ import annotations

import hashlib
import inspect
import json
from pathlib import Path
from typing import Any

from search import semantic_context_policy as policy


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def validate_manifest_capability(manifest: dict[str, Any]) -> dict[str, Any]:
    """Validate a public semantic manifest against the shipped policy contract."""
    if manifest.get("semantic_policy_version") != policy.SEMANTIC_CONTEXT_POLICY_VERSION:
        raise ValueError("semantic policy capability mismatch")
    if manifest.get("realized_scene_context_version") != policy.REALIZED_SCENE_CONTEXT_VERSION:
        raise ValueError("realized-scene context capability mismatch")
    cells = manifest.get("cells")
    if not isinstance(cells, list) or not cells:
        raise ValueError("semantic manifest requires at least one cell")
    policy_hashes = {condition: policy.condition_policy_implementation_hash(condition) for condition in sorted(policy.SUPPORTED_CONDITIONS)}
    source_hashes = {
        "policy": hashlib.sha256(Path(policy.__file__).read_bytes()).hexdigest(),
        "capability": hashlib.sha256(inspect.getsource(validate_manifest_capability).encode("utf-8")).hexdigest(),
    }
    payload = {key: value for (key, value) in manifest.items() if key != "manifest_sha256"}
    return {
        "policy_hashes": policy_hashes,
        "source_hashes": source_hashes,
        "truth_table_report_sha256": _sha256({"conditions": sorted(policy.SUPPORTED_CONDITIONS), "policy_hashes": policy_hashes}),
        "capability_integration_digest": _sha256({"manifest": _sha256(payload), "source_hashes": source_hashes, "policy_hashes": policy_hashes}),
    }
