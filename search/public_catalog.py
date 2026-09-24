from __future__ import annotations

import csv
import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class CatalogRecord:
    record_id: str
    source: str
    task: str
    seed: int
    path: Path
    sha256: str | None = None


def load_catalog(catalog: Path, root: Path) -> list[CatalogRecord]:
    if not catalog.is_file():
        raise FileNotFoundError(f"catalog is required but missing: {catalog}")
    records: list[CatalogRecord] = []
    with catalog.open(encoding="utf-8", newline="") as handle:
        for index, row in enumerate(csv.DictReader(handle), start=2):
            record_id = row.get("record_id", "")
            relative = row.get("path", "")
            if not record_id or not relative:
                raise ValueError(f"catalog row {index} requires record_id and path")
            candidate = (root / relative).resolve()
            if root.resolve() not in candidate.parents and candidate != root.resolve():
                raise ValueError(f"catalog row {index} escapes archive root")
            records.append(CatalogRecord(record_id, row.get("source", ""), row.get("task", ""), int(row.get("seed", "0")), candidate, row.get("sha256") or None))
    return records


def resolve_record(catalog: Path, root: Path, *, source: str, task: str, seed: int, record_id: str | None = None) -> CatalogRecord:
    records = load_catalog(catalog, root)
    candidates = [record for record in records if (record.record_id == record_id if record_id else record.source == source and record.task == task and record.seed == seed)]
    if len(candidates) != 1:
        description = f"record_id={record_id}" if record_id else f"source={source}, task={task}, seed={seed}"
        raise LookupError(f"catalog must contain exactly one skill record for {description}; found {len(candidates)}")
    record = candidates[0]
    if not record.path.is_file():
        raise FileNotFoundError(f"catalog record points to missing skill: {record.path}")
    if not record.sha256:
        raise ValueError("scientific catalog records require sha256")
    if hashlib.sha256(record.path.read_bytes()).hexdigest() != record.sha256:
        raise ValueError(f"catalog hash mismatch: {record.record_id}")
    return record
