from __future__ import annotations
from dataclasses import dataclass, field
import numpy as np
from dsl.nodes import ControlMode, GeneratorType, Skill
from evaluation.metrics import DesignMetrics

@dataclass
class SkillEntry:
    skill: Skill
    metrics: DesignMetrics
    generation: int = 0

def compute_generator_complexity(skill: Skill) -> int:
    unique_generators = {ph.generator for ph in skill.phases if ph.generator is not None}
    return min(len(unique_generators), 4)

def compute_force_profile_type(skill: Skill) -> int:
    modes = {ph.control for ph in skill.phases}
    if ControlMode.FORCE_THRESHOLD_SWITCH in modes:
        return 3
    if ControlMode.ADMITTANCE_CONTROL in modes:
        return 2
    if ControlMode.IMPEDANCE_CONTROL in modes:
        return 1
    return 0

def compute_descriptors(skill: Skill) -> tuple[int, int]:
    return (compute_generator_complexity(skill), compute_force_profile_type(skill))
_DEFAULT_GRID_SIZE: tuple[int, int] = (5, 4)

@dataclass
class MAPElitesArchive:
    descriptor1_name: str = 'generator_complexity'
    descriptor2_name: str = 'force_profile_type'
    grid_size: tuple[int, int] = field(default_factory=lambda : (5, 4))
    cells: dict[tuple[int, int], SkillEntry] = field(default_factory=dict)

    def _is_better(self, candidate: SkillEntry, incumbent: SkillEntry) -> bool:
        c_expr = candidate.metrics.task_score
        i_expr = incumbent.metrics.task_score
        if c_expr > i_expr:
            return True
        if c_expr < i_expr:
            return False
        c_comp = candidate.metrics.composite_score
        i_comp = incumbent.metrics.composite_score
        if c_comp > i_comp:
            return True
        if c_comp < i_comp:
            return False
        return candidate.generation < incumbent.generation

    def add(self, skill_ast: Skill, metrics: DesignMetrics, generation: int=0) -> tuple[int, int]:
        (d1, d2) = compute_descriptors(skill_ast)
        candidate = SkillEntry(skill=skill_ast, metrics=metrics, generation=generation)
        key = (d1, d2)
        incumbent = self.cells.get(key)
        if incumbent is None or self._is_better(candidate, incumbent):
            self.cells[key] = candidate
        return key

    def best(self) -> SkillEntry | None:
        if not self.cells:
            return None
        return max(self.cells.values(), key=lambda e: (e.metrics.task_score, e.metrics.composite_score, -e.generation))

    def coverage(self) -> float:
        total = self.grid_size[0] * self.grid_size[1]
        if total == 0:
            return 0.0
        return len(self.cells) / total

    def to_grid(self) -> np.ndarray:
        (n_rows, n_cols) = self.grid_size
        grid = np.full((n_rows, n_cols), float('nan'), dtype=np.float64)
        for ((d1, d2), entry) in self.cells.items():
            if 0 <= d1 < n_rows and 0 <= d2 < n_cols:
                grid[d1, d2] = entry.metrics.task_score
        return grid

    def __len__(self) -> int:
        return len(self.cells)
