from __future__ import annotations
from dsl.nodes import Skill
from dsl.validator import validate, ValidationError

class NoValidMutantError(RuntimeError):
    """Mutation retry loop exhausted without producing an acceptable mutant."""

class MinPhasesNotSatisfiableError(NoValidMutantError):
    """All mutation attempts produced too few phases for the task constraint."""

def mutate_and_validate(skill: Skill, operator, rng=None, max_attempts: int=10, min_phases: int=1) -> Skill:
    last_errors: list[ValidationError] = []
    n_min_phases_rejections: int = 0
    for attempt in range(max_attempts):
        candidate: Skill = operator(skill, rng)
        errors: list[ValidationError] = validate(candidate)
        if not errors:
            if len(candidate.phases) < min_phases:
                n_min_phases_rejections += 1
                continue
            return candidate
        last_errors = errors
    op_name = getattr(operator, '__name__', repr(operator))
    if n_min_phases_rejections == max_attempts:
        raise MinPhasesNotSatisfiableError(f"mutate_and_validate: min_phases={min_phases} not satisfiable: all {max_attempts} mutation attempts produced fewer than {min_phases} phases (operator '{op_name}').")
    error_summary = '; '.join((e.message for e in last_errors))
    if n_min_phases_rejections:
        phase_note = f' ({n_min_phases_rejections} of {max_attempts} attempt(s) were rejected by min_phases={min_phases} constraint)'
    else:
        phase_note = ''
    raise NoValidMutantError(f"mutate_and_validate: no valid mutant produced after {max_attempts} attempt(s) using operator '{op_name}'.{phase_note} Last validation errors: {error_summary}")
