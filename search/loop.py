from __future__ import annotations
import random
from dsl.nodes import Skill
from dsl.validator import validate
from compiler.codegen import compile
from evaluation.runner import run_evaluation
from evaluation.metrics import compute_metrics, DesignMetrics
from evaluation.task_spec import TaskSpec
from simulation.backend import SimulatorBackend
from mutation.validator import mutate_and_validate
from mutation.operators import random_mutation
from search.archive import SkillArchive
from search.proposer import ProposerCallable
from search.parameter_optimiser import optimise_parameters

def run_search(initial_skill: Skill, backend: SimulatorBackend, n_iterations: int=10, n_eval_samples: int=20, seed: int=42, lambda_penalty: float=0.05, proposer: ProposerCallable | None=None, task_spec: TaskSpec | None=None, seed_skills: list[Skill] | None=None, inner_loop_optimiser: str | None=None, task_name: str | None=None, min_phases: int=1, cma_budget: int=200) -> SkillArchive:
    rng = random.Random(seed)
    archive = SkillArchive()
    if proposer is not None and hasattr(proposer, '_rng'):
        proposer._rng = random.Random(rng.randint(0, 2 ** 31 - 1))

    def _evaluate(art, skill_for_metrics, current_iteration: int=0) -> DesignMetrics:
        if inner_loop_optimiser == 'cma-es':
            cma_seed = rng.randint(0, 2 ** 31 - 1)
            (best_metrics, _best_params, _cma_diagnostics) = optimise_parameters(art, backend, task_spec, budget=cma_budget, seed=cma_seed, lambda_penalty=lambda_penalty)
            return best_metrics
        else:
            traces = run_evaluation(art, backend, n_samples=n_eval_samples, seed=seed, task_spec=task_spec)
            return compute_metrics(traces, skill_for_metrics, lambda_penalty=lambda_penalty, task_spec=task_spec, current_iteration=current_iteration, total_iterations=n_iterations, task_name=task_name)
    if seed_skills:
        for s in seed_skills:
            art = compile(s)
            m = _evaluate(art, s)
            archive.add(s, m, generation=-1)
    artifact = compile(initial_skill)
    metrics = _evaluate(artifact, initial_skill)
    archive.add(initial_skill, metrics, generation=0)
    for i in range(1, n_iterations + 1):
        best_entry = archive.best()
        parent: Skill = best_entry.skill
        if proposer is None:
            candidate: Skill = mutate_and_validate(parent, operator=random_mutation, rng=rng, min_phases=min_phases)
        else:
            parent_metrics: DesignMetrics = best_entry.metrics
            proposed: Skill = proposer(parent, parent_metrics, archive)
            if validate(proposed):
                candidate = mutate_and_validate(parent, operator=random_mutation, rng=rng, min_phases=min_phases)
            else:
                candidate = proposed
        artifact = compile(candidate)
        metrics = _evaluate(artifact, candidate, current_iteration=i)
        archive.add(candidate, metrics, generation=i)
    return archive
