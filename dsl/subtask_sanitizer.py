from __future__ import annotations
import dataclasses
import difflib
from dsl.nodes import Phase, Skill

def sanitize_subtasks(skill: Skill, task_spec) -> tuple[Skill, int]:
    subtasks = getattr(task_spec, 'subtasks', None)
    if skill.skill_subtasks is not None and len(skill.skill_subtasks) > 0:
        valid_ids = [s['id'] for s in skill.skill_subtasks]
    elif subtasks is not None and len(subtasks) > 0:
        valid_ids = [s.id for s in subtasks]
    else:
        return (skill, 0)
    valid_id_set: frozenset[str] = frozenset(valid_ids)
    fallback_count = 0
    new_phases: list[Phase] = []
    changed = False
    for phase in skill.phases:
        if phase.subtask_id is None:
            new_phases.append(phase)
            continue
        if phase.subtask_id in valid_id_set:
            new_phases.append(phase)
            continue
        matches = difflib.get_close_matches(phase.subtask_id, valid_ids, n=1, cutoff=0.6)
        if matches:
            repaired_id = matches[0]
        else:
            repaired_id = None
        new_phase = dataclasses.replace(phase, subtask_id=repaired_id)
        new_phases.append(new_phase)
        fallback_count += 1
        changed = True
    if not changed:
        return (skill, 0)
    sanitized = dataclasses.replace(skill, phases=tuple(new_phases))
    return (sanitized, fallback_count)
