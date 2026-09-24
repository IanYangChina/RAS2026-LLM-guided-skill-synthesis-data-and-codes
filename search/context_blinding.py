from __future__ import annotations
import re
from pathlib import Path
from typing import Any
_PHASE_TYPE_MAP: dict[str, str] = {'approach': 'P01', 'align': 'P02', 'descend': 'P03', 'contact': 'P04', 'push': 'P05', 'pull': 'P06', 'insert': 'P07', 'lift': 'P08', 'retract': 'P09', 'rotate': 'P10', 'grasp': 'P11', 'release': 'P12'}
_GENERATOR_MAP: dict[str, str] = {'linear_cartesian': 'G01', 'arc_cartesian': 'G02', 'bezier_curve': 'G03', 'joint_interpolation': 'G04', 'impedance_motion': 'G05'}
_CONTROL_MAP: dict[str, str] = {'position_control': 'C01', 'impedance_control': 'C02', 'admittance_control': 'C03', 'force_threshold_switch': 'C04', 'force_control': 'C05'}
_TERMINATION_MAP: dict[str, str] = {'time_limit': 'T01', 'pose_tolerance': 'T02', 'force_exceeded': 'T03', 'contact_lost': 'T04', 'contact_detected': 'T05', 'grasp_success': 'T06'}
_END_EFFECTOR_MAP: dict[str, str] = {'force_grasp': 'E01', 'open': 'E02'}
_SKILL_TYPE_MAP: dict[str, str] = {'arm': 'ST1', 'arm_gripper': 'ST2', 'gripper': 'ST3'}
_ANONYMISE_MAP: dict[str, str] = {}
_ANONYMISE_MAP.update(_SKILL_TYPE_MAP)
_ANONYMISE_MAP.update(_END_EFFECTOR_MAP)
_ANONYMISE_MAP.update(_TERMINATION_MAP)
_ANONYMISE_MAP.update(_CONTROL_MAP)
_ANONYMISE_MAP.update(_GENERATOR_MAP)
_ANONYMISE_MAP.update(_PHASE_TYPE_MAP)
_ANONYMISE_KEYS_BY_LEN = sorted(_ANONYMISE_MAP, key=len, reverse=True)
_DEANONYMISE_MAP: dict[str, str] = {v: k for (k, v) in _ANONYMISE_MAP.items()}
_DEANONYMISE_KEYS_BY_LEN = sorted(_DEANONYMISE_MAP, key=len, reverse=True)

def anonymise_text(text: str) -> str:
    result = text
    for token in _ANONYMISE_KEYS_BY_LEN:
        opaque = _ANONYMISE_MAP[token]
        pattern = f'(?<!\\w){re.escape(token)}(?!\\w)|(?<!\\w){re.escape(token)}(?=_\\d)'
        result = re.sub(pattern, opaque, result)
    return result

def deanonymise_yaml(yaml_text: str) -> str:
    result = yaml_text
    for opaque in _DEANONYMISE_KEYS_BY_LEN:
        real = _DEANONYMISE_MAP[opaque]
        pattern = f'(?<!\\w){re.escape(opaque)}(?!\\w)|(?<!\\w){re.escape(opaque)}(?=_\\d)'
        result = re.sub(pattern, real, result)
    return result
_TASK_ENTITY_NEUTRAL: dict[str, dict[str, str]] = {'obstacle_reach': {'obstacle_reach': 'task_01', 'obstacle_block': 'entity_01', 'obstacle': 'entity_01', 'goal_marker': 'entity_02', 'goal': 'entity_02'}, 'grasp_place': {'grasp_place': 'task_02', 'grasp_target': 'entity_01', 'grasp': 'entity_01', 'placement_surface': 'entity_02', 'place': 'entity_02'}, 'peg_channel': {'peg_channel': 'task_03', 'peg': 'entity_01', 'channel_structure': 'entity_02', 'channel': 'entity_02'}}
_TASK_DESCRIPTION_MARKERS: tuple[str, ...] = ('reach target while avoiding', 'grasp and place', 'push the box', 'pull the door', 'peg must traverse', 'obstacle-clearing trajectory', 'collision-prone', 'object transfer', 'door opening', 'object must be placed', 'object must reach', 'task success criterion', 'avoid obstacle', 'clear the obstacle', 'collision penalty', 'grasp target', 'transport displacement', 'goal_beyond_obstacle')

def neutralise_scene_entities(entities: dict, task_name: str) -> dict:
    import copy
    ent = copy.deepcopy(entities)
    mapping = _TASK_ENTITY_NEUTRAL.get(task_name, {})
    for obj in ent.get('objects', []):
        if 'name' in obj and obj['name'] in mapping:
            obj['name'] = mapping[obj['name']]
        if 'role' in obj:
            obj['role'] = 'entity'
    new_landmarks: dict[str, Any] = {}
    _sorted_mapping = sorted(mapping.items(), key=lambda kv: len(kv[0]), reverse=True)
    for (key, val) in ent.get('task_landmarks', {}).items():
        neutral_key = key
        for (real, neutral) in _sorted_mapping:
            neutral_key = neutral_key.replace(real, neutral)
        new_landmarks[neutral_key] = val
    ent['task_landmarks'] = new_landmarks
    return ent

def redact_task_description_lines(lines: list[str]) -> list[str]:
    kept: list[str] = []
    for line in lines:
        lower = line.lower()
        if any((marker in lower for marker in _TASK_DESCRIPTION_MARKERS)):
            continue
        kept.append(line)
    return kept

def neutralise_task_name(task_name: str) -> str:
    return _TASK_ENTITY_NEUTRAL.get(task_name, {}).get(task_name, f'task_XX')
_WRONG_TASK_IMAGE_SOURCE: dict[str, str] = {'obstacle_reach': 'grasp_place', 'grasp_place': 'peg_channel', 'peg_channel': 'obstacle_reach'}

def wrong_image_task_for(task_name: str) -> str | None:
    return _WRONG_TASK_IMAGE_SOURCE.get(task_name)

def wrong_image_skill_path(task_name: str) -> Path | None:
    wrong = _WRONG_TASK_IMAGE_SOURCE.get(task_name)
    if wrong is None:
        return None
    return Path(__file__).resolve().parents[1] / 'tasks' / 'seeds' / wrong / 'seed_00.yaml'
_NUMERIC_OPERATOR_MAP: dict[str, str] = {'add_parameter': 'OP01', 'remove_parameter': 'OP02', 'insert_phase': 'OP03', 'remove_phase': 'OP04', 'swap_generator': 'OP05', 'change_control_mode': 'OP06', 'change_termination': 'OP07', 'adjust_parameter_range': 'OP08'}
_NUMERIC_OPERATOR_REVERSE: dict[str, str] = {v: k for (k, v) in _NUMERIC_OPERATOR_MAP.items()}

def numeric_only_context(*, iteration: int, total_iterations: int, task_score_history: list[float], fitness_score_history: list[float], composite_score_history: list[float], termination_fidelity: float, complexity_penalty: float, phase_count: int, parameter_count: int, current_composite: float, best_composite: float) -> str:
    lines: list[str] = ['# Iteration Context', '', f'Iteration {iteration + 1} of {total_iterations}.', '', '## Score History', '', '| Iteration | task_score | fitness_score | composite_score |', '|---|---|---|---|']
    for i in range(len(task_score_history)):
        ts = task_score_history[i]
        fs = fitness_score_history[i] if i < len(fitness_score_history) else 0.0
        cs = composite_score_history[i] if i < len(composite_score_history) else 0.0
        lines.append(f'| {i + 1} | {ts:.4f} | {fs:.4f} | {cs:.4f} |')
    lines.extend(['', '## Current State', '', f'- **Current composite score**: {current_composite:.4f}', f'- **Best composite score**: {best_composite:.4f}', f'- **Termination fidelity**: {termination_fidelity:.4f}', f'- **Complexity penalty**: {complexity_penalty:.4f}', f'- **Phase count**: {phase_count}', f'- **Parameter count**: {parameter_count}', '', '## Available Mutation Operators', '', 'Select ONE operator to apply:', '', '| Operator ID | Description |', '|---|---|', '| OP01 | Add a parameter to a randomly selected phase |', '| OP02 | Remove a parameter from a randomly selected phase |', '| OP03 | Insert a new phase with random type/generator/control/termination |', '| OP04 | Remove a randomly selected phase (keep at least 1) |', '| OP05 | Switch the generator of a randomly selected phase |', '| OP06 | Change the control mode of a randomly selected phase |', '| OP07 | Change the termination condition of a randomly selected phase |', '| OP08 | Adjust a parameter range bound |', '', '## Output Format', '', 'Return EXACTLY one operator ID.  You may optionally specify a 0-based', 'phase index to target:', '', '```yaml', 'operator: OP05', '```', '', 'or', '', '```yaml', 'operator: OP05', 'phase_index: 2', '```'])
    return '\n'.join(lines)

def parse_numeric_only_response(response_text: str) -> dict[str, Any] | None:
    import yaml as _yaml
    m = re.search('```(?:yaml|json)?\\s*\\n(.*?)\\n```', response_text, re.DOTALL)
    if m:
        try:
            parsed = _yaml.safe_load(m.group(1))
        except Exception:
            parsed = None
    else:
        try:
            parsed = _yaml.safe_load(response_text)
        except Exception:
            parsed = None
    if not isinstance(parsed, dict):
        return None
    op = parsed.get('operator')
    if op not in _NUMERIC_OPERATOR_REVERSE:
        return None
    result: dict[str, Any] = {'operator': _NUMERIC_OPERATOR_REVERSE[op]}
    if 'phase_index' in parsed and isinstance(parsed['phase_index'], int):
        result['phase_index'] = parsed['phase_index']
    return result
