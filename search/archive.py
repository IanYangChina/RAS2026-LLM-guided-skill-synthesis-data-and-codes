from __future__ import annotations
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np

class _NumpyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)
from dsl.nodes import ControlMode, GeneratorType, Skill
from dsl.serialiser import dump_skill, load_skill
from evaluation.metrics import COMPOSITE_FORMULA_VERSION, METRICS_SCHEMA_VERSION, DesignMetrics, split_optimiser_posthoc_diagnostics
from search.map_elites import MAPElitesArchive

def _as_float(value, default: float=0.0) -> float:
    if value is None:
        return default
    return float(value)

def _as_dict(value) -> dict:
    return dict(value) if isinstance(value, dict) else {}

def _as_list(value) -> list:
    return list(value) if isinstance(value, list) else []

def _metrics_to_record(metrics: DesignMetrics) -> dict:
    if hasattr(metrics, 'to_dict'):
        return metrics.to_dict()
    return {'task_score': metrics.task_score, 'canonical_task_score': metrics.task_score, 'fitness_score': getattr(metrics, 'fitness_score', metrics.task_score), 'search_fitness_score': getattr(metrics, 'fitness_score', metrics.task_score), 'termination_fidelity': metrics.termination_fidelity, 'force_compliance': metrics.force_compliance, 'complexity_penalty': metrics.complexity_penalty, 'composite_score': metrics.composite_score, 'LAMBDA': metrics.LAMBDA, 'composite_formula_version': COMPOSITE_FORMULA_VERSION, 'metrics_version': METRICS_SCHEMA_VERSION}

def _metrics_from_record(m: dict) -> DesignMetrics:
    task_score = _as_float(m.get('canonical_task_score', m.get('task_score', m.get('expressivity', 0.0))))
    fitness_score = _as_float(m.get('search_fitness_score', m.get('fitness_score', task_score)), default=task_score)
    legacy_optimiser = _as_dict(m.get('skill_parameter_optimisation_scores', m.get('cma_diagnostics', {})))
    explicit_optimiser = _as_dict(m.get('optimiser_diagnostics', {}))
    (legacy_opt, legacy_posthoc) = split_optimiser_posthoc_diagnostics(legacy_optimiser)
    (explicit_opt, explicit_posthoc) = split_optimiser_posthoc_diagnostics(explicit_optimiser)
    optimiser_diagnostics = {**legacy_opt, **explicit_opt}
    posthoc_diagnostics = {**legacy_posthoc, **explicit_posthoc, **_as_dict(m.get('posthoc_diagnostics', {}))}
    return DesignMetrics(task_score=task_score, termination_fidelity=_as_float(m.get('termination_fidelity', m.get('smoothness', 0.0))), force_compliance=_as_float(m.get('force_compliance', 0.0)), complexity_penalty=_as_float(m.get('complexity_penalty', m.get('dimensional_penalty', 0.0))), composite_score=_as_float(m.get('composite_score', 0.0)), LAMBDA=_as_float(m.get('LAMBDA', 0.05), default=0.05), phase_completion_rate=None if m.get('phase_completion_rate') is None else _as_float(m.get('phase_completion_rate')), mean_phase_displacement=None if m.get('mean_phase_displacement') is None else _as_float(m.get('mean_phase_displacement')), fitness_score=fitness_score, task_subscores=_as_dict(m.get('task_subscores', m.get('skill_design_scores', m.get('sub_scores', {})))), task_score_components=_as_dict(m.get('task_score_components', {})), optimiser_fitness_components=_as_dict(m.get('optimiser_fitness_components', {})), safety_diagnostics=_as_dict(m.get('safety_diagnostics', {})), termination_diagnostics=_as_dict(m.get('termination_diagnostics', {})), randomised_task_state=_as_dict(m.get('randomised_task_state', {})), episode_task_state=_as_list(m.get('episode_task_state', [])), skill_parameter_optimisation_scores=optimiser_diagnostics, optimisation_signal_source=m.get('optimisation_signal_source', 'task_score_only'), optimiser_diagnostics=optimiser_diagnostics, posthoc_diagnostics=posthoc_diagnostics, composite_formula_version=m.get('composite_formula_version', COMPOSITE_FORMULA_VERSION), metrics_version=m.get('metrics_version', 'metrics-schema-v1'))

@dataclass
class ArchiveEntry:
    skill: Skill
    metrics: DesignMetrics
    generation: int = 0

class SkillArchive:

    def __init__(self, max_size: int=100, use_map_elites: bool=False) -> None:
        if max_size < 1:
            raise ValueError(f'max_size must be a positive integer, got {max_size!r}')
        self._max_size = max_size
        self._entries: list[ArchiveEntry] = []
        self._seen_hashes: set[str] = set()
        self._use_map_elites: bool = use_map_elites
        self._map_elites: MAPElitesArchive | None = MAPElitesArchive() if use_map_elites else None

    @property
    def map_elites_archive(self) -> MAPElitesArchive | None:
        return self._map_elites

    @staticmethod
    def _skill_hash(skill: Skill) -> str:
        return hashlib.md5(dump_skill(skill).encode()).hexdigest()[:12]

    def add(self, skill: Skill, metrics: DesignMetrics, generation: int=0) -> None:
        h = self._skill_hash(skill)
        if h in self._seen_hashes:
            return
        self._seen_hashes.add(h)
        if len(self._entries) >= self._max_size:
            worst_idx = min(range(len(self._entries)), key=lambda i: self._entries[i].metrics.composite_score)
            self._entries.pop(worst_idx)
        self._entries.append(ArchiveEntry(skill=skill, metrics=metrics, generation=generation))
        if self._map_elites is not None:
            self._map_elites.add(skill, metrics, generation=generation)

    def elite(self, n: int=5) -> list[ArchiveEntry]:
        sorted_entries = sorted(self._entries, key=lambda e: e.metrics.composite_score, reverse=True)
        return sorted_entries[:n]

    def best(self) -> ArchiveEntry | None:
        if not self._entries:
            return None
        return max(self._entries, key=lambda e: e.metrics.composite_score)

    def __len__(self) -> int:
        return len(self._entries)

    def save(self, path: Path | str) -> None:
        path = Path(path)
        with path.open('w', encoding='utf-8') as fh:
            for entry in self._entries:
                record = {'generation': entry.generation, 'composite_score': entry.metrics.composite_score, 'skill_yaml': dump_skill(entry.skill), 'metrics': _metrics_to_record(entry.metrics)}
                fh.write(json.dumps(record, cls=_NumpyEncoder) + '\n')

    def load(self, path: Path | str) -> None:
        path = Path(path)
        with path.open('r', encoding='utf-8') as fh:
            for (lineno, line) in enumerate(fh, start=1):
                line = line.strip()
                if not line:
                    continue
                record: dict = json.loads(line)
                metrics = _metrics_from_record(record['metrics'])
                skill: Skill = load_skill(record['skill_yaml'])
                generation: int = int(record.get('generation', 0))
                self.add(skill=skill, metrics=metrics, generation=generation)
_MAP_ROWS: int = 8
_MAP_COLS: int = 3
_COMPLEX_GENERATORS: frozenset[GeneratorType] = frozenset({GeneratorType.IMPEDANCE_MOTION, GeneratorType.BEZIER_CURVE})

def _compute_descriptors(skill: Skill) -> tuple[int, int]:
    phase_count = min(len(skill.phases), _MAP_ROWS)
    has_complex = any((ph.generator in _COMPLEX_GENERATORS for ph in skill.phases if ph.generator is not None))
    if has_complex:
        complexity = 2
    else:
        all_simple = all((ph.generator is None or ph.generator == GeneratorType.LINEAR_CARTESIAN for ph in skill.phases))
        complexity = 0 if all_simple else 1
    return (phase_count - 1, complexity)

class MapElitesArchive:

    def __init__(self, capacity: int=24) -> None:
        self._grid: list[list[ArchiveEntry | None]] = [[None, None, None] for _ in range(_MAP_ROWS)]

    def add(self, skill: Skill, metrics: DesignMetrics, generation: int=0) -> bool:
        (bd1, bd2) = _compute_descriptors(skill)
        incumbent = self._grid[bd1][bd2]
        if incumbent is None or metrics.composite_score > incumbent.metrics.composite_score:
            self._grid[bd1][bd2] = ArchiveEntry(skill=skill, metrics=metrics, generation=generation)
            return True
        return False

    def best(self) -> ArchiveEntry | None:
        best_entry: ArchiveEntry | None = None
        for row in self._grid:
            for cell in row:
                if cell is not None:
                    if best_entry is None or cell.metrics.composite_score > best_entry.metrics.composite_score:
                        best_entry = cell
        return best_entry

    def elite(self, n: int=5) -> list[ArchiveEntry]:
        all_entries = [cell for row in self._grid for cell in row if cell is not None]
        return sorted(all_entries, key=lambda e: e.metrics.composite_score, reverse=True)[:n]

    def __len__(self) -> int:
        return sum((1 for row in self._grid for cell in row if cell is not None))

    def heatmap(self) -> list[list[float | None]]:
        return [[cell.metrics.composite_score if cell is not None else None for cell in row] for row in self._grid]

    def save(self, path: Path | str) -> None:
        path = Path(path)
        with path.open('w', encoding='utf-8') as fh:
            for (i, row) in enumerate(self._grid):
                for (j, cell) in enumerate(row):
                    if cell is None:
                        continue
                    record = {'generation': cell.generation, 'composite_score': cell.metrics.composite_score, 'skill_yaml': dump_skill(cell.skill), 'bd1': i, 'bd2': j, 'metrics': _metrics_to_record(cell.metrics)}
                    fh.write(json.dumps(record, cls=_NumpyEncoder) + '\n')

    def load(self, path: Path | str) -> None:
        path = Path(path)
        with path.open('r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                record: dict = json.loads(line)
                metrics = _metrics_from_record(record['metrics'])
                skill: Skill = load_skill(record['skill_yaml'])
                bd1 = int(record['bd1'])
                bd2 = int(record['bd2'])
                generation: int = int(record.get('generation', 0))
                incumbent = self._grid[bd1][bd2]
                if incumbent is None or metrics.composite_score > incumbent.metrics.composite_score:
                    self._grid[bd1][bd2] = ArchiveEntry(skill=skill, metrics=metrics, generation=generation)
_MAP_V2_ROWS: int = 5
_MAP_V2_COLS: int = 3
_CONTACT_MODES: frozenset[ControlMode] = frozenset({ControlMode.IMPEDANCE_CONTROL, ControlMode.ADMITTANCE_CONTROL, ControlMode.FORCE_CONTROL})

def _compute_descriptors_v2(skill: Skill, metrics: DesignMetrics) -> tuple[int, int]:
    contact_count = sum((1 for p in skill.phases if p.control in _CONTACT_MODES))
    bd1 = min(contact_count, 4)
    disp = metrics.mean_phase_displacement
    if disp is None or disp < 0.1:
        bd2 = 0
    elif disp < 0.3:
        bd2 = 1
    else:
        bd2 = 2
    return (bd1, bd2)

class MapElitesArchiveV2:

    def __init__(self, capacity: int=15) -> None:
        self._grid: list[list[ArchiveEntry | None]] = [[None, None, None] for _ in range(_MAP_V2_ROWS)]

    def add(self, skill: Skill, metrics: DesignMetrics, generation: int=0) -> bool:
        (bd1, bd2) = _compute_descriptors_v2(skill, metrics)
        incumbent = self._grid[bd1][bd2]
        if incumbent is None or metrics.composite_score > incumbent.metrics.composite_score:
            self._grid[bd1][bd2] = ArchiveEntry(skill=skill, metrics=metrics, generation=generation)
            return True
        return False

    def best(self) -> ArchiveEntry | None:
        best_entry: ArchiveEntry | None = None
        for row in self._grid:
            for cell in row:
                if cell is not None:
                    if best_entry is None or cell.metrics.composite_score > best_entry.metrics.composite_score:
                        best_entry = cell
        return best_entry

    def elite(self, n: int=5) -> list[ArchiveEntry]:
        all_entries = [cell for row in self._grid for cell in row if cell is not None]
        return sorted(all_entries, key=lambda e: e.metrics.composite_score, reverse=True)[:n]

    def __len__(self) -> int:
        return sum((1 for row in self._grid for cell in row if cell is not None))

    def heatmap(self) -> list[list[float | None]]:
        return [[cell.metrics.composite_score if cell is not None else None for cell in row] for row in self._grid]

    def save(self, path: Path | str) -> None:
        path = Path(path)
        with path.open('w', encoding='utf-8') as fh:
            for (i, row) in enumerate(self._grid):
                for (j, cell) in enumerate(row):
                    if cell is None:
                        continue
                    record = {'generation': cell.generation, 'composite_score': cell.metrics.composite_score, 'skill_yaml': dump_skill(cell.skill), 'bd1': i, 'bd2': j, 'metrics': _metrics_to_record(cell.metrics)}
                    fh.write(json.dumps(record, cls=_NumpyEncoder) + '\n')

    def load(self, path: Path | str) -> None:
        path = Path(path)
        with path.open('r', encoding='utf-8') as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                record: dict = json.loads(line)
                metrics = _metrics_from_record(record['metrics'])
                skill: Skill = load_skill(record['skill_yaml'])
                bd1 = int(record['bd1'])
                bd2 = int(record['bd2'])
                generation: int = int(record.get('generation', 0))
                incumbent = self._grid[bd1][bd2]
                if incumbent is None or metrics.composite_score > incumbent.metrics.composite_score:
                    self._grid[bd1][bd2] = ArchiveEntry(skill=skill, metrics=metrics, generation=generation)

def seed_population(n_seeds: int=8, rng=None) -> list[Skill]:
    from dsl.nodes import ControlMode, GeneratorType, PhaseParameter, PhaseType, ParameterType, Phase, Skill, TerminationCond
    if n_seeds > 8:
        raise ValueError(f'seed_population() defines exactly 8 canonical seeds; requested {n_seeds}.')
    _phase_params = (('p0', PhaseParameter(type=ParameterType.SCALAR, range=(0.01, 0.3))), ('p1', PhaseParameter(type=ParameterType.SCALAR, range=(0.1, 0.5))))
    _PTYPE = {'approach': PhaseType.APPROACH, 'contact': PhaseType.CONTACT, 'push': PhaseType.PUSH, 'retract': PhaseType.RETRACT, 'align': PhaseType.ALIGN}
    LIN = GeneratorType.LINEAR_CARTESIAN
    ARC = GeneratorType.ARC_CARTESIAN
    IMP_GEN = GeneratorType.IMPEDANCE_MOTION
    POS = ControlMode.POSITION_CONTROL
    IMP = ControlMode.IMPEDANCE_CONTROL
    POSE_TOL = TerminationCond.POSE_TOLERANCE
    CONTACT = TerminationCond.CONTACT_DETECTED
    _used_ids: dict[str, int] = {}

    def _phase(name: str, gen, ctrl, term=POSE_TOL, first: bool=False) -> Phase:
        count = _used_ids.get(name, 0) + 1
        _used_ids[name] = count
        return Phase(phase_id=f'{name}_{count}', phase_type=_PTYPE[name], generator=gen, control=ctrl, termination=term, parameters=_phase_params if first else ())

    def _make_seed(skill_name: str, phase_specs: list) -> Skill:
        nonlocal _used_ids
        _used_ids = {}
        phases = tuple((_phase(n, g, c, t, first=i == 0) for (i, (n, g, c, t)) in enumerate(phase_specs)))
        return Skill(name=skill_name, phases=phases)
    seeds: list[Skill] = [_make_seed('seed_approach_linear', [('approach', LIN, POS, POSE_TOL)]), _make_seed('seed_contact_impedance', [('contact', LIN, IMP, CONTACT)]), _make_seed('seed_approach_contact', [('approach', LIN, POS, POSE_TOL), ('contact', LIN, IMP, CONTACT)]), _make_seed('seed_contact_push', [('contact', LIN, IMP, CONTACT), ('push', LIN, IMP, POSE_TOL)]), _make_seed('seed_approach_contact_retract', [('approach', LIN, POS, POSE_TOL), ('contact', LIN, IMP, CONTACT), ('retract', LIN, POS, POSE_TOL)]), _make_seed('seed_contact_push_retract', [('contact', LIN, IMP, CONTACT), ('push', LIN, IMP, POSE_TOL), ('retract', LIN, POS, POSE_TOL)]), _make_seed('seed_full_push', [('approach', LIN, POS, POSE_TOL), ('contact', LIN, IMP, CONTACT), ('push', LIN, IMP, POSE_TOL), ('retract', LIN, POS, POSE_TOL)]), _make_seed('seed_align_contact_arc', [('align', ARC, POS, POSE_TOL), ('contact', LIN, IMP, CONTACT)])]
    return seeds[:n_seeds]
