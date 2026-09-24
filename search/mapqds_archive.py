from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence
from dsl.serialiser import dump_skill
from evaluation.metrics import DesignMetrics
from search.mapqds_descriptors import Descriptor, compute_descriptor
MAPQDS_TOTAL_CELLS = 4 ** 5

@dataclass
class MAPQDSArchiveEntry:
    skill: Any
    metrics: DesignMetrics
    generation: int
    descriptor: Descriptor
    metadata: dict[str, Any] = field(default_factory=dict)

class MAPQDSArchive:

    def __init__(self, total_cell_count: int | None=MAPQDS_TOTAL_CELLS) -> None:
        if total_cell_count is not None and total_cell_count < 1:
            raise ValueError('total_cell_count must be positive or None')
        self.total_cell_count = total_cell_count
        self.cells: dict[Descriptor, MAPQDSArchiveEntry] = {}

    @staticmethod
    def _quality_key(entry: MAPQDSArchiveEntry) -> tuple[float, float, float, int]:
        return (float(entry.metrics.task_score), float(entry.metrics.composite_score), -float(entry.metrics.complexity_penalty), -int(entry.generation))

    @classmethod
    def is_better(cls, candidate: MAPQDSArchiveEntry, incumbent: MAPQDSArchiveEntry) -> bool:
        return cls._quality_key(candidate) > cls._quality_key(incumbent)

    def update(self, skill: Any, metrics: DesignMetrics, generation: int=0, descriptor: Sequence[str] | None=None, metadata: Mapping[str, Any] | None=None) -> bool:
        key = tuple(descriptor) if descriptor is not None else compute_descriptor(skill, metrics)
        if len(key) != 5:
            raise ValueError(f'descriptor must contain 5 labels, got {key!r}')
        entry = MAPQDSArchiveEntry(skill=skill, metrics=metrics, generation=int(generation), descriptor=key, metadata=dict(metadata or {}))
        incumbent = self.cells.get(entry.descriptor)
        if incumbent is None or self.is_better(entry, incumbent):
            self.cells[entry.descriptor] = entry
            return True
        return False

    def insert(self, skill: Any, metrics: DesignMetrics, generation: int=0, descriptor: Sequence[str] | None=None, metadata: Mapping[str, Any] | None=None) -> bool:
        return self.update(skill, metrics, generation, descriptor, metadata)

    def sample_parent(self, rng: Any) -> MAPQDSArchiveEntry:
        if not self.cells:
            raise RuntimeError('Cannot sample parent from an empty MAP-QD archive.')
        entries = list(self.cells.values())
        index = _rng_index(rng, len(entries))
        return entries[index]

    def best(self) -> MAPQDSArchiveEntry | None:
        if not self.cells:
            return None
        return max(self.cells.values(), key=self._quality_key)

    def size(self) -> int:
        return len(self.cells)

    def coverage(self) -> float | None:
        if self.total_cell_count is None:
            return None
        return len(self.cells) / self.total_cell_count

    def to_records(self) -> list[dict[str, Any]]:
        return [_entry_to_record(entry) for (_, entry) in sorted(self.cells.items())]

    def __len__(self) -> int:
        return len(self.cells)

def _rng_index(rng: Any, upper: int) -> int:
    if hasattr(rng, 'randrange'):
        return int(rng.randrange(upper))
    if hasattr(rng, 'integers'):
        return int(rng.integers(upper))
    if hasattr(rng, 'randint'):
        return int(rng.randint(upper))
    raise TypeError('rng must provide randrange(), integers(), or randint()')

def _entry_to_record(entry: MAPQDSArchiveEntry) -> dict[str, Any]:
    metrics = entry.metrics
    return {'descriptor': list(entry.descriptor), 'generation': entry.generation, 'skill_yaml': _skill_yaml(entry.skill), 'scores': {'task_score': float(metrics.task_score), 'fitness_score': float(metrics.fitness_score), 'termination_fidelity': _maybe_float(metrics.termination_fidelity), 'complexity_penalty': _maybe_float(metrics.complexity_penalty), 'force_compliance': _maybe_float(metrics.force_compliance), 'composite_score': float(metrics.composite_score)}, 'metadata': _json_safe(entry.metadata)}

def _skill_yaml(skill: Any) -> str:
    try:
        return dump_skill(skill)
    except Exception:
        return str(skill)

def _maybe_float(value: Any) -> float | None:
    return None if value is None else float(value)

def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for (k, v) in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if hasattr(value, 'item'):
        return value.item()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
__all__ = ['MAPQDSArchive', 'MAPQDSArchiveEntry', 'MAPQDS_TOTAL_CELLS']
