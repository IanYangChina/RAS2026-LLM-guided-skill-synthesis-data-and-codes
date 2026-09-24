from __future__ import annotations
from typing import Any
from evaluation.metrics import DesignMetrics
Descriptor = tuple[str, str, str, str, str]

def _score_bin(value: float, prefix: str) -> str:
    if value < 0.25:
        return f'{prefix}_low'
    if value < 0.5:
        return f'{prefix}_mid_low'
    if value < 0.75:
        return f'{prefix}_mid_high'
    return f'{prefix}_high'

def task_score_bin(task_score: float) -> str:
    return _score_bin(float(task_score), 'task')

def fitness_score_bin(fitness_score: float) -> str:
    return _score_bin(float(fitness_score), 'fitness')

def termination_fidelity_bin(termination_fidelity: float | None) -> str:
    if termination_fidelity is None:
        return 'termination_unknown'
    if termination_fidelity < 0.33:
        return 'termination_poor'
    if termination_fidelity < 0.67:
        return 'termination_mixed'
    return 'termination_reliable'

def complexity_penalty_bin(complexity_penalty: float | None) -> str:
    if complexity_penalty is None:
        return 'complexity_unknown'
    if complexity_penalty < 0.1:
        return 'complexity_low'
    if complexity_penalty < 0.25:
        return 'complexity_medium'
    return 'complexity_high'

def force_compliance_bin(force_compliance: float | None) -> str:
    if force_compliance is None:
        return 'force_unknown'
    if force_compliance < 0.33:
        return 'force_high'
    if force_compliance < 0.67:
        return 'force_medium'
    return 'force_low'

def compute_descriptor(skill: Any, metrics: DesignMetrics) -> Descriptor:
    del skill
    return (task_score_bin(metrics.task_score), fitness_score_bin(metrics.fitness_score), termination_fidelity_bin(metrics.termination_fidelity), complexity_penalty_bin(metrics.complexity_penalty), force_compliance_bin(metrics.force_compliance))
__all__ = ['Descriptor', 'compute_descriptor', 'task_score_bin', 'fitness_score_bin', 'termination_fidelity_bin', 'complexity_penalty_bin', 'force_compliance_bin']
