from __future__ import annotations
import json
import math
import pathlib
import random
import re
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
import numpy as np
from dsl.nodes import Skill
from dsl.serialiser import dump_skill
from dsl.grammar import ALLOWED_ANCHORS, ALLOWED_ENTITIES, ALLOWED_METRICS
from evaluation.metrics import DesignMetrics
from search.archive import SkillArchive
from search.contact_context import format_contact_telemetry_block
from simulation.realized_scene import RealizedSceneSnapshot, apply_realized_scene_to_entities, apply_realized_scene_to_task_spec, realized_scene_snapshot_from_evaluation, realized_scene_snapshot_hash
from simulation.scene_info import format_scene_entities_block
_PARAM_OPS: frozenset[int] = frozenset({0, 1})
_PHASE_OPS: frozenset[int] = frozenset({2, 3})
_STRUCT_OPS: frozenset[int] = frozenset({4, 5, 6})
_REWARD_CHANNEL_NAMES: dict[int, str] = {0: 'task_score+complexity_penalty', 1: 'task_score+complexity_penalty', 2: 'phase_completion+displacement', 3: 'phase_completion+displacement', 4: 'termination_fidelity+phase_completion', 5: 'termination_fidelity+phase_completion', 6: 'termination_fidelity+phase_completion', 7: 'task_score+complexity_penalty', 8: 'phase_completion+displacement', 9: 'termination_fidelity+phase_completion'}
ProposerCallable = Callable[[Skill, DesignMetrics, SkillArchive], Skill]

class BaseProposer(ABC):

    @abstractmethod
    def propose(self, skill: Skill, rng: np.random.Generator) -> Skill:
        ...

    @abstractmethod
    def stats(self) -> dict:
        ...

    @abstractmethod
    def last_action(self) -> dict:
        ...

def random_proposer(skill: Skill, metrics: DesignMetrics, archive: SkillArchive) -> Skill:
    from mutation.operators import random_mutation
    return random_mutation(skill)

class BanditProposer(BaseProposer):

    def __init__(self, operators: list | None=None, C: float=1.0, seed: int | None=None, rng: random.Random | None=None, reward_mode: str='aggregate', disable_mutations: bool=False) -> None:
        self._C = C
        if rng is None and seed is not None:
            rng = random.Random(seed)
        self._rng: random.Random = rng if rng is not None else random.Random()
        self._reward_mode = reward_mode
        self._disable_mutations = disable_mutations
        from mutation.operators import ALL_OPERATORS
        if operators is None:
            self._operators = ALL_OPERATORS[:7]
        else:
            self._operators = operators
        n_ops = len(self._operators)
        self._n: list[int] = [0] * n_ops
        self._total_reward: list[float] = [0.0] * n_ops
        self._t: int = 0
        self._warmup_queue: list[int] = list(range(n_ops))
        self._last_operator_idx: int | None = None
        self._last_score: float | None = None
        self._last_metrics: DesignMetrics | None = None

    def __call__(self, skill: Skill, metrics: DesignMetrics, archive: SkillArchive) -> Skill:
        if self._disable_mutations:
            import logging
            logging.getLogger(__name__).debug('disable_mutations=True: returning skill unchanged (param-only mode)')
            return skill
        if self._reward_mode == 'aggregate':
            if self._last_operator_idx is not None and self._last_score is not None:
                reward = max(0.0, metrics.composite_score - self._last_score)
                k = self._last_operator_idx
                self._n[k] += 1
                self._total_reward[k] += reward
        elif self._last_operator_idx is not None and self._last_metrics is not None:
            reward = self._compute_decomposed_reward(self._last_operator_idx, self._last_metrics, metrics)
            k = self._last_operator_idx
            self._n[k] += 1
            self._total_reward[k] += reward
        self._t += 1
        if self._warmup_queue:
            idx = self._warmup_queue.pop(0)
        else:
            ucb_values: list[float] = []
            log_t = math.log(max(self._t, 1))
            for k in range(len(self._operators)):
                if self._n[k] == 0:
                    ucb_values.append(float('inf'))
                else:
                    mean = self._total_reward[k] / self._n[k]
                    ucb = mean + self._C * math.sqrt(2.0 * log_t / self._n[k])
                    ucb_values.append(ucb)
            idx = ucb_values.index(max(ucb_values))
        operator = self._operators[idx]
        proposed_skill = operator(skill, self._rng)
        self._last_operator_idx = idx
        self._last_score = metrics.composite_score
        self._last_metrics = metrics
        return proposed_skill

    def _compute_decomposed_reward(self, op_idx: int, old_metrics: DesignMetrics, new_metrics: DesignMetrics) -> float:
        if old_metrics.phase_completion_rate is None or new_metrics.phase_completion_rate is None:
            return max(0.0, new_metrics.composite_score - old_metrics.composite_score)
        if op_idx in _PARAM_OPS:
            dp_delta = new_metrics.complexity_penalty - old_metrics.complexity_penalty
            expr_delta = new_metrics.task_score - old_metrics.task_score
            return max(0.0, -dp_delta + expr_delta)
        elif op_idx in _PHASE_OPS:
            pcr_delta = new_metrics.phase_completion_rate - old_metrics.phase_completion_rate
            mpd_delta = 0.0
            if old_metrics.mean_phase_displacement is not None and new_metrics.mean_phase_displacement is not None:
                mpd_delta = new_metrics.mean_phase_displacement - old_metrics.mean_phase_displacement
            return max(0.0, pcr_delta + 0.5 * mpd_delta)
        else:
            sm_delta = new_metrics.termination_fidelity - old_metrics.termination_fidelity
            pcr_delta = new_metrics.phase_completion_rate - old_metrics.phase_completion_rate
            return max(0.0, sm_delta + 0.5 * pcr_delta)

    def operator_stats(self) -> list[dict]:
        log_t = math.log(max(self._t, 1)) if self._t > 0 else 0.0
        stats: list[dict] = []
        for (k, op) in enumerate(self._operators):
            n = self._n[k]
            mean_reward = self._total_reward[k] / n if n > 0 else 0.0
            if n > 0:
                ucb_value = mean_reward + self._C * math.sqrt(2.0 * log_t / n)
            else:
                ucb_value = float('inf')
            entry: dict = {'name': op.__name__, 'n': n, 'mean_reward': mean_reward, 'ucb_value': ucb_value}
            if self._reward_mode == 'decomposed':
                entry['reward_channel'] = _REWARD_CHANNEL_NAMES.get(k, 'unknown')
            stats.append(entry)
        return stats

    def propose(self, skill: Skill, rng: np.random.Generator) -> Skill:
        raise NotImplementedError('BanditProposer.propose() requires DesignMetrics and SkillArchive. Use bandit(skill, metrics, archive) (__call__) instead.')

    def stats(self) -> dict:
        return {op.__name__: self._n[k] for (k, op) in enumerate(self._operators)}

    def last_action(self) -> dict:
        operator_name = None
        if self._last_operator_idx is not None:
            operator_name = self._operators[self._last_operator_idx].__name__
        return {'operator_idx': self._last_operator_idx, 'operator_name': operator_name, 'last_score': self._last_score}

class RandomProposer(BaseProposer):

    def __init__(self, operators: list | None=None, seed: int | None=None, rng: random.Random | None=None) -> None:
        if rng is None and seed is not None:
            rng = random.Random(seed)
        self._rng: random.Random = rng if rng is not None else random.Random()
        from mutation.operators import ALL_OPERATORS
        if operators is None:
            self._operators = ALL_OPERATORS[:7]
        else:
            self._operators = operators
        self._n: list[int] = [0] * len(self._operators)
        self._last_operator_idx: int | None = None

    def __call__(self, skill: Skill, metrics: DesignMetrics | None, archive: SkillArchive) -> Skill:
        idx = self._rng.randrange(len(self._operators))
        self._n[idx] += 1
        self._last_operator_idx = idx
        return self._operators[idx](skill, self._rng)

    def operator_stats(self) -> list[dict]:
        return [{'name': op.__name__, 'n': self._n[k], 'mean_reward': None, 'ucb_value': None} for (k, op) in enumerate(self._operators)]

    @property
    def last_operator_idx(self) -> int | None:
        return self._last_operator_idx

    def propose(self, skill: Skill, rng: np.random.Generator) -> Skill:
        idx = rng.integers(0, len(self._operators))
        self._n[idx] += 1
        self._last_operator_idx = idx
        return self._operators[idx](skill, self._rng)

    def stats(self) -> dict:
        return {op.__name__: self._n[k] for (k, op) in enumerate(self._operators)}

    def last_action(self) -> dict:
        operator_name = None
        if self._last_operator_idx is not None:
            operator_name = self._operators[self._last_operator_idx].__name__
        return {'operator_idx': self._last_operator_idx, 'operator_name': operator_name}

class RoundRobinProposer(BaseProposer):

    def __init__(self, operators: list | None=None, seed: int | None=None, rng: random.Random | None=None) -> None:
        if rng is None and seed is not None:
            rng = random.Random(seed)
        self._rng: random.Random = rng if rng is not None else random.Random()
        from mutation.operators import ALL_OPERATORS
        if operators is None:
            self._operators = ALL_OPERATORS[:7]
        else:
            self._operators = operators
        self._n: list[int] = [0] * len(self._operators)
        self._cursor: int = 0
        self._last_operator_idx: int | None = None

    def __call__(self, skill: Skill, metrics: DesignMetrics | None, archive: SkillArchive) -> Skill:
        idx = self._cursor
        self._cursor = (self._cursor + 1) % len(self._operators)
        self._n[idx] += 1
        self._last_operator_idx = idx
        return self._operators[idx](skill, self._rng)

    def operator_stats(self) -> list[dict]:
        return [{'name': op.__name__, 'n': self._n[k], 'mean_reward': None, 'ucb_value': None} for (k, op) in enumerate(self._operators)]

    @property
    def last_operator_idx(self) -> int | None:
        return self._last_operator_idx

    def propose(self, skill: Skill, rng: np.random.Generator) -> Skill:
        idx = self._cursor
        self._cursor = (self._cursor + 1) % len(self._operators)
        self._n[idx] += 1
        self._last_operator_idx = idx
        return self._operators[idx](skill, self._rng)

    def stats(self) -> dict:
        return {op.__name__: self._n[k] for (k, op) in enumerate(self._operators)}

    def last_action(self) -> dict:
        operator_name = None
        if self._last_operator_idx is not None:
            operator_name = self._operators[self._last_operator_idx].__name__
        return {'operator_idx': self._last_operator_idx, 'operator_name': operator_name}
_FULL_LIKE_CONDITIONS: frozenset[str] = frozenset({'full', 'text_only', 'text_reward', 'no_scene_entities', 'no_history', 'no_task_subscores', 'anonymised_dsl', 'no_task_language', 'wrong_image', 'semantics_ablation_contact_info'})
_PRIMARY_EVAL_TARGET: dict[str, str] = {'obstacle_reach': 'TCP distance to goal position (Gaussian proximity kernel)', 'push_to_goal': 'object displacement ratio toward goal_object_position', 'peg_insert': 'insertion depth ratio (axial progress into hole)', 'peg_channel': 'insertion depth × lateral alignment (axial progress penalised by wall deviation)', 'door_pull': 'hinge angle ratio (achieved_angle / target_hinge_angle)', 'door_push': 'hinge angle delta ratio (realised hinge motion / target_hinge_angle)', 'grasp_place': 'final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.'}

def _format_phase_target_map_guidance(task_spec: object) -> str | None:
    ptm = getattr(task_spec, 'phase_target_map', None)
    if not ptm:
        return None
    return '- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.'
_PHASE_LIBRARY_CATALOG: str = '### approach\nMoves the end-effector to a standoff pose above the manipulation target.\nCanonical parameters:\n  - approach_height (scalar): vertical standoff distance above target [0.05, 0.30] m\n  - speed (scalar): Cartesian translation speed [0.01, 0.10] m/s\n  - arc_height (scalar, optional): arc clearance height with arc_cartesian [0.10, 0.50] m\nCommon generators: linear_cartesian, arc_cartesian\nCommon control: position_control, force_threshold_switch\nCommon termination: pose_tolerance\n\n### align\nLateral fine-adjustment of end-effector position before contact or insertion.\nCanonical parameters:\n  - lateral_offset_x (scalar): signed x-axis correction [-0.01, 0.01] m\n  - lateral_offset_y (scalar): signed y-axis correction [-0.01, 0.01] m\nCommon generators: linear_cartesian\nCommon control: position_control\nCommon termination: pose_tolerance\n\n### descend\nControlled vertical descent toward a surface or object.\nCanonical parameters:\n  - depth (scalar): descent distance [0.01, 0.10] m\nCommon generators: linear_cartesian\nCommon control: position_control, admittance_control\nCommon termination: pose_tolerance, contact_detected\n\n### contact\nEstablishes and verifies physical contact with a surface using force-aware control.\nCanonical parameters:\n  - contact_force (scalar): force threshold for contact confirmation [1.0, 20.0] N\n  - speed (scalar): slow approach speed during probing [0.005, 0.05] m/s\nCommon generators: linear_cartesian, impedance_motion\nCommon control: force_threshold_switch for initial probing; impedance_control or admittance_control after contact is established\nCommon termination: force_exceeded; contact_detected only with non-impedance probing controls\n\n### push\nApplies a directed lateral or axial pushing displacement to an object.\nCanonical parameters:\n  - push_distance (scalar): total push stroke [0.02, 0.20] m\n  - push_speed (scalar): push velocity [0.01, 0.10] m/s\n  - push_depth (scalar): depth into contact surface [0.01, 0.10] m\nCommon generators: linear_cartesian, impedance_motion\nCommon control: impedance_control, position_control\nCommon termination: time_limit, pose_tolerance\n\n### pull\nPulls a constrained object through an arc or linear stroke.\nCanonical parameters:\n  - pull_angle (angle): arc rotation magnitude [0.10, 1.20] rad\n  - pull_distance (scalar): linear pull stroke distance [0.02, 0.20] m\nCommon generators: arc_cartesian, linear_cartesian\nCommon control: impedance_control\nCommon termination: time_limit, pose_tolerance\n\n### insert\nPrecision axial insertion of a peg, pin, or tool into a confined hole or channel.\nCanonical parameters:\n  - insertion_depth (scalar): axial insertion stroke [0.01, 0.15] m\n  - insertion_force (scalar): maximum permissible axial force [1.0, 20.0] N\nCommon generators: impedance_motion, linear_cartesian\nCommon control: admittance_control, impedance_control\nCommon termination: pose_tolerance, force_exceeded\n\n### lift\nRaises a grasped object vertically to a safe clearance height.\nCanonical parameters:\n  - lift_height (scalar): vertical lift stroke [0.05, 0.30] m\n  - speed (scalar): lift velocity [0.01, 0.10] m/s\nCommon generators: linear_cartesian\nCommon control: position_control\nCommon termination: pose_tolerance\n\n### retract\nReturns the end-effector to a safe standoff position after task completion.\nCanonical parameters:\n  - retract_height (scalar): standoff height during retraction [0.05, 0.20] m\n  - speed (scalar): retract velocity [0.01, 0.10] m/s\nCommon generators: linear_cartesian, arc_cartesian\nCommon control: position_control\nCommon termination: pose_tolerance\n\n### rotate\nRotates the end-effector or a grasped object about a specified axis.\nCanonical parameters:\n  - yaw_angle (angle): rotation magnitude [0.10, 1.57] rad\nCommon generators: arc_cartesian, impedance_motion\nCommon control: position_control, impedance_control\nCommon termination: pose_tolerance, time_limit\n\n### grasp\nCloses the gripper to grip an object.\nRequires end_effector_action: force_grasp and skill_type: arm_gripper.\nSet generator: null for a pure gripper action (no Cartesian motion).\nCanonical parameters:\n  - grip_force (scalar, optional): target gripper closure force [5.0, 30.0] N\nend_effector_action: force_grasp\nCommon control: position_control\nCommon termination: time_limit, grasp_success\n\n### release\nOpens the gripper to release a held object.\nRequires end_effector_action: open and skill_type: arm_gripper.\nNo default tunable parameters — release timing is typically fixed.\nGenerator: linear_cartesian (to move to release position) or null for in-place release.\nend_effector_action: open\nCommon control: position_control, admittance_control\nCommon termination: pose_tolerance, time_limit'

def _build_resolved_subtask_section(skill, subtask_mode: str, prompt_variant: int=0) -> list[str]:
    if prompt_variant < 1:
        return []
    if subtask_mode != 'free':
        return []
    if skill is None:
        return []
    subtasks = getattr(skill, 'skill_subtasks', None)
    if not subtasks:
        return []
    _DEFAULT_ANCHOR = 'goal'
    _DEFAULT_ENTITY = 'tcp'
    _DEFAULT_METRIC = 'distance'
    _DEFAULT_OFFSET = [0, 0, 0]
    _DEFAULT_WEIGHT = 1.0
    lines: list[str] = []
    lines.append('## Resolved Subtask Fields (all fields explicit)')
    lines.append('')
    lines.append('The following shows your current subtasks with ALL fields resolved. Specify any field explicitly in your proposal to keep or change its value:')
    lines.append('')
    lines.append('```yaml')
    lines.append('subtasks:')
    for st in subtasks:
        st_id = st.get('id', 'unknown')
        anchor = st.get('anchor', _DEFAULT_ANCHOR)
        target_entity = st.get('target_entity', _DEFAULT_ENTITY)
        metric = st.get('metric', _DEFAULT_METRIC)
        offset = st.get('offset', _DEFAULT_OFFSET)
        weight = st.get('weight', _DEFAULT_WEIGHT)
        _norm_offset = [float(v) for v in offset] if offset is not None else [0.0, 0.0, 0.0]
        anchor_str = str(anchor)
        entity_str = str(target_entity)
        metric_str = str(metric)
        offset_str = str(_norm_offset)
        weight_str = str(float(weight))
        lines.append(f'  - id: {st_id}')
        lines.append(f'    anchor: {anchor_str}')
        lines.append(f'    target_entity: {entity_str}')
        lines.append(f'    metric: {metric_str}')
        lines.append(f'    offset: {offset_str}')
        lines.append(f'    weight: {weight_str}')
    lines.append('```')
    lines.append('')
    return lines

def _build_subtask_layer_section(subtask_mode: str, task_spec, task_name: str='', prompt_variant: int=0) -> list[str]:
    lines: list[str] = []
    if subtask_mode == 'fixed':
        subtasks = getattr(task_spec, 'subtasks', None)
        if not subtasks:
            return []
        lines.append('## Subtask Layer')
        lines.append('')
        lines.append('**Mode**: fixed (subtask targets are defined by the task configuration)')
        lines.append('')
        lines.append('Available subtask IDs for phase binding:')
        lines.append('| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |')
        lines.append('|---|---|---|---|---|')
        for st in subtasks:
            param_key = getattr(st, 'param_offset_key', None) or '—'
            _off = getattr(st, 'offset', [0.0, 0.0, 0.0])
            _off_str = f"({', '.join((f'{float(v):.2f}' for v in _off))})" if _off is not None else '(0.00, 0.00, 0.00)'
            lines.append(f"| {st.id} | {getattr(st, 'anchor', 'goal')} | {_off_str} | {getattr(st, 'metric', 'distance')} | {param_key} |")
        lines.append('')
        lines.append('Annotate phases with `subtask_id: <id>` to bind them to a subtask target.')
        lines.append("- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.")
        lines.append('- Only the **last phase** bound to a given subtask is used for subtask scoring.')
        lines.append('- Phases without `subtask_id` are not scored against subtasks but still execute normally.')
    elif subtask_mode == 'free':
        anchors = ' | '.join(sorted(ALLOWED_ANCHORS))
        entities = ' | '.join(sorted(ALLOWED_ENTITIES))
        metrics_vals = ' | '.join(sorted(ALLOWED_METRICS))
        lines.append('## Subtask Layer')
        lines.append('')
        lines.append('**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)')
        lines.append('')
        lines.append('Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.')
        lines.append('')
        lines.append('**Required fields** — always include both, never omit:')
        lines.append(f'- `anchor` (**required**): {anchors}')
        lines.append(f'- `target_entity` (**required**): {entities}')
        lines.append('')
        lines.append('Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.')
        lines.append('')
        lines.append('Optional fields:')
        lines.append(f'- `metric`: {metrics_vals} (default: distance)')
        lines.append('- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])')
        lines.append('- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)')
        lines.append('- `weight`: scoring weight [0.1, 1.0] (default: 1.0)')
        lines.append('')
        lines.append('**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:')
        lines.append('| Anchor | Resolves to | Best used for |')
        lines.append('|--------|-------------|---------------|')
        lines.append('| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |')
        obj_pos = getattr(task_spec, 'object_initial_pose', None) if task_spec is not None else None
        if obj_pos is not None:
            lines.append(f'| `object` | offset from object initial position {tuple((float(v) for v in obj_pos[:3]))} | approach/contact targets near object start |')
        else:
            lines.append('| `object` | offset from object initial position | approach/contact targets near object |')
        _tn_lower_st = task_name.lower() if task_name else ''
        goal_pos = None
        if task_spec is not None:
            goal_pos = getattr(task_spec, 'goal_object_position', None)
            if goal_pos is None:
                if _tn_lower_st == 'grasp_place':
                    goal_pos = getattr(task_spec, 'place_goal_position', None)
                elif _tn_lower_st not in ('door_pull', 'door_push'):
                    goal_pos = getattr(task_spec, 'goal_tcp_position', None)
        if goal_pos is not None:
            lines.append(f'| `goal` | offset from task goal position {tuple((float(v) for v in goal_pos[:3]))} | final destination targets |')
        else:
            lines.append('| `goal` | offset from task goal position | final destination targets |')
        fixture_pos = getattr(task_spec, 'fixture_pose', None) if task_spec is not None else None
        if fixture_pos is not None:
            lines.append(f'| `fixture` | offset from fixture pose {tuple((float(v) for v in fixture_pos[:3]))} | approach/contact targets near fixture |')
        else:
            lines.append('| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |')
        lines.append('')
        lines.append('Annotate each phase with `subtask_id: <id>` to bind it to a subtask.')
        lines.append('Only the **last phase** bound to a given subtask contributes to subtask scoring.')
        lines.append('')
        lines.append('Example (two subtasks — one near object start, one at goal):')
        lines.append('```yaml')
        lines.append('subtasks:')
        lines.append('  - id: reach_pre_contact')
        lines.append('    anchor: object         # resolved to object initial position (see table above)')
        lines.append('    target_entity: tcp     # score TCP distance to this target')
        lines.append('    metric: distance')
        lines.append('    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position')
        lines.append('    weight: 0.3')
        lines.append('  - id: reach_goal')
        lines.append('    anchor: goal           # resolved to task goal position (see table above)')
        lines.append('    target_entity: tcp')
        lines.append('    metric: distance')
        lines.append('    offset: [0.0, 0.0, 0.0]')
        lines.append('    weight: 0.7')
        lines.append('phases:')
        lines.append('  - id: approach_1')
        lines.append('    type: approach')
        lines.append('    subtask_id: reach_pre_contact')
        lines.append('    ...')
        lines.append('  - id: push_1')
        lines.append('    type: push')
        lines.append('    subtask_id: reach_goal')
        lines.append('    ...')
        lines.append('```')
    return lines

def _format_v2_executable_phase_semantics(skill: Skill) -> list[str]:
    if getattr(skill, 'dsl_version', 1) != 2:
        return []
    from compiler.codegen import compile as compile_skill
    artifact = compile_skill(skill)
    lines = ['## Executable Phase Semantics', '', 'Visible executable target/binding metadata from the compiled controller:']
    for phase in artifact.phases:
        lines.append(f'- **{phase.phase_id}** (`{phase.phase_type}`)')
        if phase.target is not None:
            target_bits = [f'source={phase.target.source}', f'anchor={phase.target.anchor}']
            if phase.target.entity is not None:
                target_bits.append(f'entity={phase.target.entity}')
            target_bits.append(f'offset={list(phase.target.offset)}')
            if phase.target.offset_along_axis is not None:
                axis = phase.target.offset_along_axis
                target_bits.append(f'offset_along_axis={{axis={axis.axis}, distance={axis.distance}, mode={axis.mode}, sign={axis.sign}}}')
            if phase.target.tolerance is not None:
                target_bits.append(f'tolerance={phase.target.tolerance}')
            lines.append(f"  - target: {', '.join(target_bits)}")
            if phase.target.orientation is not None:
                orient = phase.target.orientation
                orient_bits = [f'mode={orient.mode}']
                if orient.axis is not None:
                    orient_bits.append(f'axis={list(orient.axis)}')
                if orient.align_with is not None:
                    orient_bits.append(f'align_with={orient.align_with}')
                if orient.quat is not None:
                    orient_bits.append(f'quat={list(orient.quat)}')
                if orient.tolerance is not None:
                    orient_bits.append(f'tolerance={orient.tolerance}')
                lines.append(f"  - orientation: {', '.join(orient_bits)}")
        else:
            lines.append('  - target: implicit target resolution (no explicit target block)')
        if phase.parameter_bindings:
            lines.append('  - parameter_bindings:')
            for (pname, entry) in phase.parameter_bindings.items():
                binding_bits = ', '.join((f'{binding.path} ({binding.mode})' for binding in entry.bindings)) or '<none>'
                suffix = f' justification={entry.justification}' if entry.justification else ''
                lines.append(f'    - {pname}: status={entry.status}; consumers={binding_bits}{suffix}')
        else:
            lines.append('  - parameter_bindings: none')
        if phase.guards:
            lines.append('  - guards:')
            for guard in phase.guards:
                guard_bits = [f'id={guard.guard_id}', f'when={guard.when}', f'predicate={guard.predicate}', f'on_failure={guard.on_failure}']
                if guard.threshold is not None:
                    guard_bits.append(f'threshold={guard.threshold}')
                if guard.args:
                    guard_bits.append(f'args={dict(guard.args)}')
                lines.append(f"    - {', '.join(guard_bits)}")
        if phase.retries is not None:
            retry_bits = [f'max_attempts={phase.retries.max_attempts}', f'strategy={phase.retries.strategy}']
            if phase.retries.offset is not None:
                retry_bits.append(f'offset={list(phase.retries.offset)}')
            if phase.retries.reduce_speed_factor != 0.5:
                retry_bits.append(f'reduce_speed_factor={phase.retries.reduce_speed_factor}')
            lines.append(f"  - retries: {', '.join(retry_bits)}")
    lines.append('')
    return lines

def _iter_phase_telemetry_rows(traces: list[dict] | None) -> list[dict]:
    rows: list[dict] = []
    for trace in traces or []:
        if not isinstance(trace, dict):
            continue
        phase_telemetry = trace.get('phase_telemetry')
        if not isinstance(phase_telemetry, list):
            continue
        for row in phase_telemetry:
            if isinstance(row, dict):
                rows.append(row)
    return rows

def _safe_xyz_displacement(start: object, end: object) -> float | None:
    if not isinstance(start, (list, tuple)) or not isinstance(end, (list, tuple)):
        return None
    if len(start) < 3 or len(end) < 3:
        return None
    coords: list[float] = []
    for value in (*start[:3], *end[:3]):
        if not isinstance(value, int | float) or not math.isfinite(float(value)):
            return None
        coords.append(float(value))
    return ((coords[3] - coords[0]) ** 2 + (coords[4] - coords[1]) ** 2 + (coords[5] - coords[2]) ** 2) ** 0.5

def _format_last_execution_state_section(traces: list[dict], max_phases: int=8) -> list[str]:

    def _is_num(value: object) -> bool:
        return isinstance(value, int | float) and math.isfinite(float(value))

    def _num(value: object) -> float | None:
        return float(value) if _is_num(value) else None

    def _mean(values: list[float]) -> float | None:
        return sum(values) / len(values) if values else None

    def _fmt_num(value: float | None) -> str:
        return f'{value:.3f}' if value is not None else '—'

    def _fmt_vec(values: list[list[float]]) -> str:
        if not values:
            return '—'
        means = [sum((v[i] for v in values)) / len(values) for i in range(3)]
        return '(' + ', '.join((f'{v:.3f}' for v in means)) + ')'

    def _vec(value: object) -> list[float] | None:
        if not isinstance(value, (list, tuple)) or len(value) < 3:
            return None
        out: list[float] = []
        for item in value[:3]:
            if not _is_num(item):
                return None
            out.append(float(item))
        return out

    def _dominant(values: list[str]) -> str:
        counts: dict[str, int] = {}
        for value in values:
            counts[value] = counts.get(value, 0) + 1
        return max(counts.items(), key=lambda item: item[1])[0] if counts else '—'

    def _contact_location(row: dict) -> str | None:
        for key in ('collision_location', 'contact_location'):
            value = row.get(key)
            if value:
                return str(value)
        body = row.get('phase_peak_obstacle_body') or row.get('peak_obstacle_body')
        geom = row.get('phase_peak_obstacle_geom') or row.get('peak_obstacle_geom')
        counterbody = row.get('phase_peak_obstacle_counterbody') or row.get('peak_obstacle_counterbody')
        countergeom = row.get('phase_peak_obstacle_countergeom') or row.get('peak_obstacle_countergeom')
        obstacle = '/'.join((str(x) for x in (body, geom) if x))
        counter = '/'.join((str(x) for x in (counterbody, countergeom) if x))
        if obstacle and counter:
            return f'{counter} ↔ {obstacle}'
        return obstacle or counter or None
    phase_stats: dict[str, dict] = {}
    phase_order: list[str] = []
    for row in _iter_phase_telemetry_rows(traces):
        phase_name = str(row.get('phase_name') or 'unknown')
        if phase_name not in phase_stats:
            phase_order.append(phase_name)
            phase_stats[phase_name] = {'phase_types': [], 'n_total': 0, 'n_normal': 0, 'termination_reasons': [], 'tcp_start': [], 'tcp_end': [], 'object_start': [], 'object_end': [], 'goal_start': [], 'goal_end': [], 'n_contact': 0, 'contact_events': [], 'peak_forces': [], 'raw_peak_forces': [], 'locations': []}
        stats = phase_stats[phase_name]
        stats['n_total'] += 1
        phase_type = row.get('phase_type')
        if phase_type:
            stats['phase_types'].append(str(phase_type))
        if row.get('terminated_normally'):
            stats['n_normal'] += 1
        reason = row.get('termination_reason')
        if reason:
            stats['termination_reasons'].append(str(reason))
        for (key, target) in (('tcp_start', 'tcp_start'), ('tcp_end', 'tcp_end'), ('object_pos_start', 'object_start'), ('object_pos_end', 'object_end')):
            vec = _vec(row.get(key))
            if vec is not None:
                stats[target].append(vec)
        for (key, target) in (('object_to_goal_dist_start', 'goal_start'), ('object_to_goal_dist_end', 'goal_end'), ('contact_event_count', 'contact_events'), ('peak_contact_force', 'peak_forces'), ('raw_peak_contact_force', 'raw_peak_forces')):
            value = _num(row.get(key))
            if value is not None:
                stats[target].append(value)
        if row.get('contact_detected'):
            stats['n_contact'] += 1
        location = _contact_location(row)
        if location:
            stats['locations'].append(location)
    if not phase_stats:
        return []
    selected = phase_order[:max_phases]
    has_object = any((phase_stats[name]['object_start'] or phase_stats[name]['object_end'] for name in selected))
    has_goal_dist = any((phase_stats[name]['goal_start'] or phase_stats[name]['goal_end'] for name in selected))
    has_force = any((phase_stats[name]['peak_forces'] for name in selected))
    has_raw_force = any((phase_stats[name]['raw_peak_forces'] for name in selected))
    has_location = any((phase_stats[name]['locations'] for name in selected))
    headers = ['Phase', 'Type', 'Normal / reason', 'TCP start→end']
    if has_object:
        headers.append('Object start→end')
    if has_goal_dist:
        headers.append('Obj→goal start→end')
    headers.append('Contact rate / events')
    if has_force:
        headers.append('Peak force')
    if has_raw_force:
        headers.append('Raw peak force')
    if has_location:
        headers.append('Obstacle/contact')
    lines = ['## Last Optimised Execution State', '']
    lines.append(f'Mean phase-boundary state across the latest CMA-ES optimised traces (up to {max_phases} phases; values rounded to 3 decimals).')
    lines.append('')
    lines.append('| ' + ' | '.join(headers) + ' |')
    lines.append('|' + '|'.join(('---' for _ in headers)) + '|')
    for phase_name in selected:
        stats = phase_stats[phase_name]
        n_total = stats['n_total']
        normal_rate = stats['n_normal'] / n_total if n_total else 0.0
        contact_rate = stats['n_contact'] / n_total if n_total else 0.0
        row = [phase_name, _dominant(stats['phase_types']), f"{normal_rate:.2f} / {_dominant(stats['termination_reasons'])}", f"{_fmt_vec(stats['tcp_start'])}→{_fmt_vec(stats['tcp_end'])}"]
        if has_object:
            row.append(f"{_fmt_vec(stats['object_start'])}→{_fmt_vec(stats['object_end'])}")
        if has_goal_dist:
            row.append(f"{_fmt_num(_mean(stats['goal_start']))}→{_fmt_num(_mean(stats['goal_end']))}")
        row.append(f"{contact_rate:.2f} / {_fmt_num(_mean(stats['contact_events']))}")
        if has_force:
            row.append(_fmt_num(_mean(stats['peak_forces'])))
        if has_raw_force:
            row.append(_fmt_num(_mean(stats['raw_peak_forces'])))
        if has_location:
            row.append(_dominant(stats['locations']))
        lines.append('| ' + ' | '.join(row) + ' |')
    if len(phase_order) > max_phases:
        lines.append(f'\n_Only first {max_phases} of {len(phase_order)} phases shown._')
    lines.append('')
    return lines

def format_proposal_context_v2(skill: Skill, metrics: DesignMetrics, traces: list[dict], cma_diagnostics: dict, task_spec, keyframes: dict | None=None, task_name: str='', condition: str='full', seed: int | None=None, iteration: int | None=None, total_iterations: int | None=None, proposal_history: list[tuple[str, float]] | None=None, creation_mode: bool=False, subtask_fallback_count: int=0, subtask_mode: str='fixed', best_skill: Skill | None=None, iteration_history: list[dict] | None=None, task_score: float | None=None, prompt_variant: int=0, best_task_score: float=0.0, scene_entities: dict | None=None, realized_scene_snapshot: RealizedSceneSnapshot | dict | None=None, randomised_task_state: dict | None=None, nominal_randomisation: dict | None=None) -> str:
    import warnings as _warnings
    _DEPRECATED_CONDITIONS: dict[str, str] = {'reduced': 'text_reward', 'context_free': 'text_only', 'vision': 'text_vision'}
    if condition in _DEPRECATED_CONDITIONS:
        new_cond = _DEPRECATED_CONDITIONS[condition]
        _warnings.warn(f"format_proposal_context_v2: condition='{condition}' is deprecated; use '{new_cond}' instead.", DeprecationWarning, stacklevel=2)
        condition = new_cond
    include_contact_telemetry = condition == 'semantics_ablation_contact_info'
    if include_contact_telemetry:
        condition = 'full'
    if creation_mode:
        creation_lines: list[str] = ['# Skill Creation Context', '']
        if task_name:
            creation_lines.append(f'## Task: {task_name}')
            creation_lines.append('')
        creation_lines.append('## Scene Facts')
        creation_lines.append('')
        _tn_lower = task_name.lower() if task_name else ''
        _show_tcp_goal = _tn_lower not in ('peg_channel', 'door_pull', 'door_push', 'grasp_place')
        if _show_tcp_goal and hasattr(task_spec, 'goal_tcp_position') and task_spec.goal_tcp_position:
            creation_lines.append(f'- Goal TCP position: {task_spec.goal_tcp_position}')
        if hasattr(task_spec, 'goal_object_position') and task_spec.goal_object_position:
            creation_lines.append(f'- Goal object position: {task_spec.goal_object_position}')
        if _tn_lower == 'grasp_place':
            _pgp = getattr(task_spec, 'place_goal_position', None)
            if _pgp is not None:
                creation_lines.append(f'- Place goal position (task success criterion — final object 3D position must be close to the realised airborne target here): {_pgp}')
            creation_lines.append('- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.')
        if _tn_lower == 'peg_channel':
            _ch_len = getattr(task_spec, 'channel_length', None)
            _ch_axis = getattr(task_spec, 'channel_axis', None)
            _ch_note = '- Task success criterion: peg must traverse the channel'
            if _ch_len is not None:
                _ch_note += f' ({_ch_len} m long)'
            if _ch_axis is not None:
                _ch_note += f' along axis {_ch_axis}'
            _ch_note += '; score = axial progress × lateral alignment — NOT a fixed TCP endpoint'
            creation_lines.append(_ch_note)
        if hasattr(task_spec, 'object_initial_pose') and task_spec.object_initial_pose:
            creation_lines.append(f'- Object initial pose: {task_spec.object_initial_pose}')
        if hasattr(task_spec, 'goal_tolerance'):
            creation_lines.append(f'- Goal tolerance: {task_spec.goal_tolerance} m')
        if hasattr(task_spec, 'force_limit'):
            creation_lines.append(f'- Force safety limit: {task_spec.force_limit} N')
        if hasattr(task_spec, 'obstacle_body_name') and task_spec.obstacle_body_name:
            creation_lines.append(f'- Obstacle: `{task_spec.obstacle_body_name}` (contacts impose collision penalty)')
        if hasattr(task_spec, 'peg_body_name') and task_spec.peg_body_name:
            creation_lines.append(f'- Peg body: `{task_spec.peg_body_name}`')
        if hasattr(task_spec, 'channel_axis') and task_spec.channel_axis:
            creation_lines.append(f'- Channel axis: `{task_spec.channel_axis}` — prefer `impedance_control` to absorb lateral wall forces')
        if hasattr(task_spec, 'hinge_body_name') and task_spec.hinge_body_name:
            creation_lines.append(f'- Hinge body: `{task_spec.hinge_body_name}`')
        if hasattr(task_spec, 'target_hinge_angle') and task_spec.target_hinge_angle is not None:
            creation_lines.append(f'- Target hinge angle (task success criterion): {task_spec.target_hinge_angle:.3f} rad')
        if hasattr(task_spec, 'arm_initial_tcp_position') and task_spec.arm_initial_tcp_position:
            creation_lines.append(f'- Robot initial TCP position: {task_spec.arm_initial_tcp_position}')
        has_gripper = bool(getattr(task_spec, 'grasp_target_body', None) or getattr(task_spec, 'gripper', None))
        if has_gripper:
            creation_lines.append('- Robot initial gripper state: **open** (gripper starts fully open; add an explicit `release` phase at the beginning if the arm first needs to grip something, or ensure a `grasp` / `force_grasp` phase closes it before lifting)')
        phase_target_map_guidance = _format_phase_target_map_guidance(task_spec)
        if phase_target_map_guidance:
            creation_lines.append(phase_target_map_guidance)
        if task_name and task_name.lower() in _PRIMARY_EVAL_TARGET:
            creation_lines.append(f'- Primary evaluation target: **{_PRIMARY_EVAL_TARGET[task_name.lower()]}**')
        creation_lines.append('')
        if nominal_randomisation is not None:
            ranges: dict[str, list[float]] = {}

            def _symmetric_range(delta: object) -> list[float]:
                value = abs(float(delta))
                return [0.0 if value == 0.0 else -value, value]
            for (config_key, axis_names) in (('object_xy_delta', ('object_x_offset_m', 'object_y_offset_m')), ('goal_xy_delta', ('goal_x_offset_m', 'goal_y_offset_m'))):
                deltas = nominal_randomisation.get(config_key)
                if isinstance(deltas, (list, tuple)) and len(deltas) == 2:
                    for (axis_name, delta) in zip(axis_names, deltas, strict=True):
                        ranges[axis_name] = _symmetric_range(delta)
            if 'hinge_delta_deg' in nominal_randomisation:
                ranges['initial_hinge_angle_offset_deg'] = _symmetric_range(nominal_randomisation['hinge_delta_deg'])
            if 'goal_z_delta' in nominal_randomisation:
                goal_z_delta = abs(float(nominal_randomisation['goal_z_delta']))
                ranges['goal_z_offset_m'] = [0.0, goal_z_delta]
            nominal_protocol = {'distribution': 'independent_uniform', 'ranges': ranges}
            creation_lines.append('## Nominal Task Randomization Distribution and Ranges')
            creation_lines.append('')
            creation_lines.append('Each listed offset is sampled independently from its uniform range.')
            creation_lines.append('')
            creation_lines.append(f"```json\n{json.dumps(nominal_protocol, sort_keys=True, separators=(',', ':'))}\n```")
            creation_lines.append('')
        if scene_entities:
            creation_lines.append('## Scene Entities')
            creation_lines.append('')
            creation_lines.append(format_scene_entities_block(scene_entities))
            creation_lines.append('')
        _subtask_layer_lines = _build_subtask_layer_section(subtask_mode=subtask_mode, task_spec=task_spec, task_name=task_name, prompt_variant=prompt_variant)
        if _subtask_layer_lines:
            creation_lines.extend(_subtask_layer_lines)
            creation_lines.append('')
        creation_lines.append('## Phase Library Catalog')
        creation_lines.append('')
        creation_lines.append(_PHASE_LIBRARY_CATALOG)
        creation_lines.append('')
        creation_lines.append('## Complexity Budget')
        creation_lines.append('')
        creation_lines.append('- Prefer **2–5 phases** for most manipulation tasks')
        creation_lines.append('- Keep parameter count **minimal** (0–3 per phase; total ≤ 8)')
        creation_lines.append('- Every parameter must have a clear physical interpretation')
        creation_lines.append('- Omit `parameters:` block entirely for phases with no tunable values')
        creation_lines.append('- Default skeleton: `approach` → [motion] → `retract`')
        creation_lines.append('- For initial contact probing, add a `contact` phase with `force_threshold_switch`; use `impedance_control` or `admittance_control` only for sustained contact after contact is established')
        creation_lines.append('')
        if keyframes is not None:
            creation_lines.append('## Start-State Visual Reference')
            creation_lines.append('')
            creation_lines.append('Initial scene frames for spatial reference:')
            creation_lines.append('')
            phase_frames = keyframes.get('phases', {}) if isinstance(keyframes, dict) else keyframes
            for (phase_name, cameras) in phase_frames.items():
                for (camera_name, path) in cameras.items():
                    creation_lines.append(f'- {camera_name}: {path}')
            creation_lines.append('')
        creation_lines.append('## Design Your Skill')
        creation_lines.append('')
        creation_lines.append('Design a new skill that achieves the task described above. Output exactly one YAML document only — no Markdown fence, prose, comments, tool calls, or justification field.')
        creation_lines.append('')
        return '\n'.join(creation_lines)
    _realized_snapshot = realized_scene_snapshot_from_evaluation(task_name, task_spec, realized_scene_snapshot=realized_scene_snapshot, randomised_task_state=randomised_task_state, metrics=metrics, traces=traces, cma_diagnostics=cma_diagnostics)
    if _realized_snapshot is not None:
        task_spec = apply_realized_scene_to_task_spec(task_spec, _realized_snapshot)
        scene_entities = apply_realized_scene_to_entities(scene_entities, _realized_snapshot)
    include_search_state = seed is not None or iteration is not None or proposal_history or iteration_history
    search_state_section = ''
    if include_search_state:
        search_state_lines = ['## Search State\n']
        if seed is not None:
            search_state_lines.append(f'- **Seed**: {seed}')
        if iteration is not None and total_iterations is not None:
            search_state_lines.append(f'- **Iteration**: {iteration + 1} / {total_iterations}')
        elif iteration is not None:
            search_state_lines.append(f'- **Iteration**: {iteration + 1}')
        if proposal_history and condition != 'no_history':
            _best_score_hist = max((s for (_, s) in proposal_history), default=float('-inf'))
            _best_hist_hash = SkillArchive._skill_hash(best_skill) if best_skill is not None else None
            search_state_lines.append('\n### Mutation History (most recent first)\n')
            if iteration_history is not None:
                search_state_lines.append('| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |')
                search_state_lines.append('|---|---|---|---|---|---|---|---|---|')
                recent = list(reversed(iteration_history[-5:]))
                for entry in recent:
                    phase_seq = ' → '.join((p['type'] for p in entry['phases']))
                    generators = ' | '.join((str(p.get('generator') or '—') for p in entry['phases']))
                    controls = ' | '.join((str(p.get('control') or '—') for p in entry['phases']))
                    terminations = ' | '.join((str(p.get('termination') or '—') for p in entry['phases']))
                    n_params = str(entry.get('n_total_params', '—'))
                    result = '✅ accepted' if entry['accepted'] else '❌ rejected'
                    search_state_lines.append(f"| {entry['iter']} | {phase_seq} | {generators} | {controls} | {terminations} | {n_params} | {entry['score']:.4f} | {entry['task_score']:.2f} | {result} |")
            else:
                search_state_lines.append('| # | Description | Q | ΔQ |')
                search_state_lines.append('|---|---|---|---|')
                recent = list(reversed(proposal_history[-5:]))
                for (i, (h, score)) in enumerate(recent, start=1):
                    delta = score - _best_score_hist
                    if _best_hist_hash is not None and h == _best_hist_hash:
                        desc = '**parent (best)** — no change'
                    else:
                        desc = f'evaluated structure #{len(proposal_history) - i + 1}'
                    search_state_lines.append(f'| {i} | {desc} | {score:.4f} | {delta:+.4f} |')
            _ts = task_score if task_score is not None else 0.0
            if _ts >= 0.9:
                _policy = f'\n**Proposal policy**: task_score is near-perfect ({_ts:.2f}). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.'
            else:
                _policy = f'\n**Proposal policy**: task_score is {_ts:.2f} — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.\n- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.\nA HOLD wastes an iteration when task_score is below 0.9.'
            search_state_lines.append(_policy)
        search_state_section = '\n'.join(search_state_lines) + '\n\n'
    _objective_section = '## Optimisation Objective\n\nYour goal is to **maximise task_score first, then composite score Q**:\n\n> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**\n\n> **Q = fitness_score + termination_fidelity − complexity_penalty**\n\n- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)\n- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)\n- `complexity_penalty`: cost for over-parameterised or over-phased designs\n\n**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.\n\n'
    lines: list[str] = []

    def _fmt(v: float | None) -> str:
        return f'{v:.3f}' if v is not None and (not math.isnan(float(v))) else 'N/A'
    lines.append('# Proposal Context')
    lines.append('')
    if condition not in ('text_reward',):
        lines.append('## Task Specification')
        lines.append('')
        if task_name:
            lines.append(f'- Task name: {task_name}')
        if _realized_snapshot is not None:
            lines.append(f'- Frozen realised-scene SHA-256: `{realized_scene_snapshot_hash(_realized_snapshot)}`')
            _object_start = _realized_snapshot.position('object_starts', 'manipulated_object') or _realized_snapshot.first_position('object_starts')
            _target = _realized_snapshot.position('targets', 'task_target') or _realized_snapshot.first_position('targets')
            _socket = _realized_snapshot.position('fixtures', 'peg_socket')
            if _object_start is not None:
                lines.append(f'- Frozen object start: {list(_object_start)}')
            if _target is not None:
                lines.append(f'- Frozen task target: {list(_target)}')
            if _socket is not None:
                lines.append(f'- Frozen socket pose: {list(_socket)} (static fixture for this episode)')
            if _realized_snapshot.door is not None:
                lines.append(f'- Frozen initial hinge angle: {_realized_snapshot.door.initial_hinge_angle:.3f} rad')
        _tn_lower = task_name.lower() if task_name else ''
        _show_tcp_goal = _tn_lower not in ('peg_channel', 'door_pull', 'door_push', 'grasp_place')
        if _realized_snapshot is None and _show_tcp_goal and hasattr(task_spec, 'goal_tcp_position') and task_spec.goal_tcp_position:
            lines.append(f'- Goal TCP position: {task_spec.goal_tcp_position}')
        if hasattr(task_spec, 'goal_object_position') and task_spec.goal_object_position:
            lines.append(f'- Goal object position: {task_spec.goal_object_position}')
        if _tn_lower in ('door_pull', 'door_push'):
            _tha = getattr(task_spec, 'target_hinge_angle', None)
            if _tha is not None:
                lines.append(f'- target_hinge_angle: {_tha:.3f} rad (task success = realised hinge-angle delta ratio; not TCP proximity)')
        if _tn_lower == 'grasp_place':
            _pgp = getattr(task_spec, 'place_goal_position', None)
            if _pgp is not None:
                lines.append(f'- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): {_pgp}')
            lines.append('- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.')
        if _tn_lower == 'peg_channel':
            _ch_len = getattr(task_spec, 'channel_length', None)
            _ch_axis = getattr(task_spec, 'channel_axis', None)
            _ch_note = '- Task success criterion: peg must traverse the channel'
            if _ch_len is not None:
                _ch_note += f' ({_ch_len} m long)'
            if _ch_axis is not None:
                _ch_note += f' along axis {_ch_axis}'
            _ch_note += '; score = axial progress × lateral alignment — NOT a fixed TCP endpoint'
            lines.append(_ch_note)
        if hasattr(task_spec, 'object_initial_pose') and task_spec.object_initial_pose:
            lines.append(f'- Object initial pose: {task_spec.object_initial_pose}')
        if hasattr(task_spec, 'goal_tolerance'):
            lines.append(f'- Goal tolerance: {task_spec.goal_tolerance} m')
        if hasattr(task_spec, 'expressivity_sigma'):
            lines.append(f'- Expressivity sigma: {task_spec.expressivity_sigma} m')
        if hasattr(task_spec, 'expressivity_threshold'):
            lines.append(f'- Expressivity threshold: {task_spec.expressivity_threshold}')
        if hasattr(task_spec, 'force_limit'):
            lines.append(f'- Force limit: {task_spec.force_limit} N')
        if hasattr(task_spec, 'obstacle_body_name') and task_spec.obstacle_body_name:
            lines.append(f'- Obstacle body: {task_spec.obstacle_body_name} (contact = collision penalty)')
        if hasattr(task_spec, 'peg_body_name') and task_spec.peg_body_name:
            lines.append(f'- Peg body: `{task_spec.peg_body_name}`')
        if hasattr(task_spec, 'channel_axis') and task_spec.channel_axis:
            lines.append(f'- Channel axis: `{task_spec.channel_axis}` — use `impedance_control` to absorb lateral wall forces')
        if hasattr(task_spec, 'arm_initial_tcp_position') and task_spec.arm_initial_tcp_position:
            lines.append(f'- Robot initial TCP position: {task_spec.arm_initial_tcp_position}')
        has_gripper = bool(getattr(task_spec, 'grasp_target_body', None) or getattr(task_spec, 'gripper', None))
        if has_gripper:
            lines.append('- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)')
        phase_target_map_guidance = _format_phase_target_map_guidance(task_spec)
        if phase_target_map_guidance:
            lines.append(phase_target_map_guidance)
        if task_name and task_name.lower() in _PRIMARY_EVAL_TARGET:
            lines.append(f'- Primary evaluation target: **{_PRIMARY_EVAL_TARGET[task_name.lower()]}**')
        lines.append('')
    elif task_name:
        lines.append('## Task')
        lines.append('')
        lines.append(f'- **Task name**: {task_name}')
        lines.append('')
    if scene_entities and condition != 'no_scene_entities':
        lines.append('## Scene Entities')
        lines.append('')
        lines.append(format_scene_entities_block(scene_entities))
        lines.append('')
    if condition in _FULL_LIKE_CONDITIONS:
        if subtask_mode == 'free' and (best_task_score >= 0.8 or (task_score is not None and task_score >= 0.7)):
            lines.append(f'> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is {best_task_score:.3f}, which indicates the subtask decomposition is already effective.')
            lines.append('> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.')
            lines.append('> Unnecessary subtask redesign when performance is already high often causes regression.')
            lines.append('')
        _subtask_layer_lines = _build_subtask_layer_section(subtask_mode=subtask_mode, task_spec=task_spec, task_name=task_name, prompt_variant=prompt_variant)
        if _subtask_layer_lines:
            lines.extend(_subtask_layer_lines)
            lines.append('')
    _best_skill_hash = SkillArchive._skill_hash(best_skill) if best_skill is not None else None
    _skill_hash = SkillArchive._skill_hash(skill)
    if best_skill is not None and _best_skill_hash != _skill_hash:
        _ph_best = max((s for (_, s) in proposal_history), default=None) if proposal_history else None
        _best_score = _ph_best if _ph_best is not None else metrics.composite_score
        lines.append(f'## Parent Skill (Best Known, Q={_best_score:.3f})')
        lines.append('')
        lines.append('```yaml')
        lines.append(dump_skill(best_skill))
        lines.append('```')
        lines.append('')
        lines.append(f'## Last Evaluated Skill (Q={metrics.composite_score:.3f})')
        lines.append('')
        lines.append('```yaml')
        lines.append(dump_skill(skill))
        lines.append('```')
        lines.append('')
    else:
        lines.append(f'## Current Skill (Q={metrics.composite_score:.3f}) — your mutation base')
        lines.append('')
        lines.append('```yaml')
        lines.append(dump_skill(skill))
        lines.append('```')
        lines.append('')
    _v2_semantics_lines = _format_v2_executable_phase_semantics(skill)
    if _v2_semantics_lines:
        lines.extend(_v2_semantics_lines)
    _resolved_subtask_lines = _build_resolved_subtask_section(skill=skill, subtask_mode=subtask_mode, prompt_variant=prompt_variant)
    if _resolved_subtask_lines:
        lines.extend(_resolved_subtask_lines)
    if condition in _FULL_LIKE_CONDITIONS:
        lines.append('## Design Metrics')
        lines.append('')
        lines.append(f'- **Composite score**: {_fmt(metrics.composite_score)}')
        lines.append(f'- **task_score** (E): {_fmt(metrics.task_score)}')
        lines.append(f'- **fitness_score**: {_fmt(metrics.fitness_score)}  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*')
        if metrics.fitness_score is not None and (not math.isnan(float(metrics.fitness_score))) and (metrics.fitness_score < 0.1):
            lines.append('  → CMA-ES cannot optimise this structure (shaped reward also near zero)')
        lines.append(f'- **Termination Fidelity** (C): {_fmt(metrics.termination_fidelity)}')
        if metrics.termination_fidelity is not None and (not math.isnan(float(metrics.termination_fidelity))) and (metrics.termination_fidelity < 0.5):
            lines.append('  → phases frequently time out instead of reaching designed conditions')
        lines.append(f'- **Force Compliance**: {_fmt(metrics.force_compliance)}')
        lines.append(f'- **Complexity Penalty**: {_fmt(metrics.complexity_penalty)}')
        if subtask_fallback_count > 0:
            lines.append(f'- **Subtask binding fallbacks**: {subtask_fallback_count} (phases with unknown subtask_id that were auto-corrected)')
        if cma_diagnostics.get('stagnated') and metrics.fitness_score < 0.2:
            lines.append('')
            lines.append('**⚠ Warning**: CMA-ES stagnated + low fitness_score → structure may be fundamentally incompatible with task')
        lines.append('')
    if condition in ('full', 'text_only') and traces and (len(traces) > 0):
        lines.append('## Per-Phase Performance')
        lines.append('')
        phase_stats: dict = {}
        for ph in _iter_phase_telemetry_rows(traces):
            phase_name = str(ph.get('phase_name') or 'unknown')
            if phase_name not in phase_stats:
                phase_stats[phase_name] = {'n_normal': 0, 'n_total': 0, 'displacements': [], 'n_contact': 0}
            phase_stats[phase_name]['n_total'] += 1
            if ph.get('terminated_normally'):
                phase_stats[phase_name]['n_normal'] += 1
            if ph.get('contact_detected'):
                phase_stats[phase_name]['n_contact'] += 1
            disp = _safe_xyz_displacement(ph.get('tcp_start'), ph.get('tcp_end'))
            if disp is not None:
                phase_stats[phase_name]['displacements'].append(disp)
        if phase_stats:
            lines.append('| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |')
            lines.append('|-------|-------------------|--------------|------------------------|')
            for (phase_name, pstats) in phase_stats.items():
                rate = pstats['n_normal'] / pstats['n_total'] if pstats['n_total'] > 0 else 0.0
                contact_rate = pstats['n_contact'] / pstats['n_total'] if pstats['n_total'] > 0 else 0.0
                mean_disp = sum(pstats['displacements']) / len(pstats['displacements']) if pstats['displacements'] else 0.0
                lines.append(f'| {phase_name} | {rate:.2f} | {contact_rate:.2f} | {mean_disp:.4f} |')
            lines.append('')
            _phase_ctrl_term: dict[str, tuple[str, str]] = {}
            for _ph in skill.phases:
                _ph_name = str(getattr(_ph, 'phase_id', '')).strip().lower()
                _ctrl_obj = getattr(_ph, 'control', None)
                _term_obj = getattr(_ph, 'termination', None)
                _ph_ctrl = getattr(_ctrl_obj, 'name', str(_ctrl_obj)).strip().lower()
                _ph_term = getattr(_term_obj, 'name', str(_term_obj)).strip().lower()
                if _ph_name:
                    _phase_ctrl_term[_ph_name] = (_ph_ctrl, _ph_term)
            warnings: list[str] = []
            for (phase_name, pstats) in phase_stats.items():
                rate = pstats['n_normal'] / pstats['n_total'] if pstats['n_total'] > 0 else 0.0
                contact_rate = pstats['n_contact'] / pstats['n_total'] if pstats['n_total'] > 0 else 0.0
                (_ctrl, _term) = _phase_ctrl_term.get(phase_name.strip().lower(), ('', ''))
                if rate == 0.0 and contact_rate == 0.0 and (_term == 'contact_detected'):
                    if _ctrl == 'impedance_control':
                        warnings.append(f'⚠ **{phase_name}**: `contact_detected` never triggered (normal term. rate = 0, contact rate = 0). This phase uses `impedance_control`, which is too compliant for initial contact probing — the robot backs away before contact force builds enough to trigger detection. **Switch to `force_threshold_switch`** to fix this.')
                    else:
                        warnings.append(f'⚠ **{phase_name}**: `contact_detected` never triggered (normal term. rate = 0, contact rate = 0). The phase is not reaching contact — check approach direction, target position, and speed.')
            if warnings:
                lines.append('**Phase Failure Diagnostics:**')
                lines.append('')
                for w in warnings:
                    lines.append(w)
                lines.append('')
    if condition in ('full', 'text_only', 'no_scene_entities', 'no_history', 'no_task_subscores', 'anonymised_dsl', 'no_task_language', 'wrong_image'):
        lines.extend(_format_last_execution_state_section(traces))
    if condition in _FULL_LIKE_CONDITIONS - {'no_task_subscores'} and hasattr(metrics, 'task_subscores') and metrics.task_subscores:
        lines.append('## Task Sub-Scores')
        lines.append('')
        lines.append('These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.')
        lines.append('')
        for (key, value) in metrics.task_subscores.items():
            if value is None:
                val_str = 'None'
            elif isinstance(value, str):
                val_str = value
            else:
                try:
                    val_str = f'{value:.3f}' if not math.isnan(float(value)) else 'N/A'
                except (TypeError, ValueError):
                    val_str = str(value)
            if key == 'collision_factor':
                lines.append(f'- {key}: {val_str}  (exp(−peak_force / force_scale))')
            elif key == 'peak_obstacle_force':
                lines.append(f'- {key}: {val_str} N')
            elif key == 'collision_location':
                lines.append(f'- {key}: {val_str}  (or None if no contact)')
            else:
                lines.append(f'- {key}: {val_str}')
        _ls = getattr(metrics, 'skill_parameter_optimisation_scores', {}).get('landscape_smoothness')
        if _ls is not None and math.isfinite(_ls):
            lines.append(f'- landscape_smoothness (param landscape): {_ls:.3f}')
        lines.append('')
    if condition in _FULL_LIKE_CONDITIONS:
        lines.append('## CMA-ES Diagnostics')
        lines.append('')
        best_fs = cma_diagnostics.get('best_fitness_score')
        if best_fs is not None:
            lines.append(f'- **Best shaped reward** (fitness_score): {_fmt(best_fs)}')
            lines.append(f'  *(shaped task+phase signal; this is the CMA-ES objective)*')
        best_ts = cma_diagnostics.get('best_task_score')
        if best_ts is not None:
            lines.append(f'- **Best task_score**: {_fmt(best_ts)}')
        lines.append(f"- **Median Q (composite search score)**: {_fmt(cma_diagnostics.get('median_score'))}")
        lines.append(f"- **K-run variance**: {cma_diagnostics.get('k_run_variance', 0.0):.4f}")
        stagnated = cma_diagnostics.get('stagnated', False)
        lines.append(f"- **Stagnated**: {('yes' if stagnated else 'no')}")
        if stagnated:
            lines.append('  → Parameter optimiser converged to local optimum; structural change likely needed')
        lines.append(f"- **Stop reason**: {cma_diagnostics.get('stop_reason', 'unknown')}")
        lines.append(f"- **Mean generations**: {cma_diagnostics.get('n_generations_mean', 0.0):.1f}")
        params_lo = cma_diagnostics.get('params_at_lower_bound', [])
        params_hi = cma_diagnostics.get('params_at_upper_bound', [])
        if params_lo:
            lines.append(f"- **Parameters at lower bound**: {', '.join(params_lo)}")
        if params_hi:
            lines.append(f"- **Parameters at upper bound**: {', '.join(params_hi)}")
        sigma_mean = cma_diagnostics.get('final_sigma_mean')
        if sigma_mean is not None:
            lines.append(f'- **Final σ (mean)**: {_fmt(sigma_mean)}')
        lines.append('')
    if condition in ('full', 'text_vision', 'no_scene_entities', 'no_history', 'no_task_subscores') and keyframes is not None:
        lines.append('## Visual Feedback')
        lines.append('')
        lines.append('Per-phase rendered frame paths (4 camera angles), for providers/runs that explicitly support visual context. Text-only callers should pass `keyframes=None` so these local paths are not sent.')
        lines.append('')
        phase_frames = keyframes.get('phases', {}) if isinstance(keyframes, dict) else keyframes
        for (phase_name, cameras) in phase_frames.items():
            lines.append(f'### Phase: {phase_name}')
            for (camera_name, path) in cameras.items():
                lines.append(f'- {camera_name}: {path}')
            lines.append('')
    if include_contact_telemetry:
        lines.append(format_contact_telemetry_block(traces))
    return search_state_section + _objective_section + '\n'.join(lines)
_VALID_OPERATOR_NAMES: frozenset[str] = frozenset({'add_parameter', 'remove_parameter', 'insert_phase', 'remove_phase', 'swap_generator', 'change_control_mode', 'change_termination'})

@dataclass(frozen=True)
class AgentProposerSchema:
    operator: str
    phase_index: int
    justification: str

def parse_agent_proposal(response_text: str) -> AgentProposerSchema | None:
    import yaml
    raw: str | None = None
    use_json: bool = False
    yaml_match = re.search('```yaml\\s*(.*?)```', response_text, re.DOTALL)
    json_match = re.search('```json\\s*(.*?)```', response_text, re.DOTALL)
    if yaml_match:
        raw = yaml_match.group(1).strip()
        use_json = False
    elif json_match:
        raw = json_match.group(1).strip()
        use_json = True
    else:
        raw = response_text.strip()
        use_json = False
    try:
        if use_json:
            data = json.loads(raw)
        else:
            data = yaml.safe_load(raw)
        if not isinstance(data, dict):
            return None
        operator = data.get('operator')
        phase_index = data.get('phase_index')
        justification = data.get('justification')
        if operator is None or phase_index is None or justification is None:
            return None
        if operator not in _VALID_OPERATOR_NAMES:
            return None
        return AgentProposerSchema(operator=str(operator), phase_index=int(phase_index), justification=str(justification))
    except Exception:
        return None

def apply_agent_proposal(schema: AgentProposerSchema, skill: Skill, rng: random.Random | None=None) -> Skill:
    import inspect
    try:
        from mutation.operators import ALL_OPERATORS
        op = next((o for o in ALL_OPERATORS if o.__name__ == schema.operator), None)
        if op is None:
            return skill
        kwargs: dict = {'rng': rng}
        if schema.phase_index is not None:
            sig_params = inspect.signature(op).parameters
            if 'target_phase_idx' in sig_params:
                kwargs['target_phase_idx'] = schema.phase_index
            elif 'phase_idx' in sig_params:
                kwargs['phase_idx'] = schema.phase_index
        return op(skill, **kwargs)
    except Exception:
        return skill

def load_agent_skill(yaml_path: str | pathlib.Path) -> Skill:
    from dsl.serialiser import load_skill
    from dsl.validator import validate
    yaml_path = pathlib.Path(yaml_path)
    yaml_text = yaml_path.read_text()
    skill = load_skill(yaml_text)
    errors = validate(skill)
    if errors:
        msg = '\n'.join((str(e) for e in errors))
        raise ValueError(f'Validation errors:\n{msg}')
    return skill

class AgentProposer(BaseProposer):

    def __init__(self, template_name: str='skill-proposer-full', max_retries: int=3):
        self.template_name = template_name
        self.max_retries = max_retries
        self._interaction_log: list[dict] = []
        self._last_action_record: dict = {}

    def propose(self, skill: Skill, rng: np.random.Generator) -> Skill:
        raise NotImplementedError('AgentProposer loop is managed by experiment-orchestrator agent. Use format_context() + parse_proposal() via CLI scripts instead.')

    def format_context(self, skill, metrics, traces, cma_diagnostics, task_spec, keyframes=None) -> str:
        return format_proposal_context_v2(skill=skill, metrics=metrics, traces=traces, cma_diagnostics=cma_diagnostics, task_spec=task_spec, keyframes=keyframes)

    def parse_proposal(self, response_text: str) -> tuple[Skill | None, str]:
        if not response_text.strip():
            return (None, 'empty_response')
        match = re.search('```(?:yaml)?\\s*\\n(.*?)```', response_text, re.DOTALL)
        if match:
            yaml_str = match.group(1)
        else:
            yaml_str = response_text
        try:
            import yaml
            data = yaml.safe_load(yaml_str)
            if data is None:
                return (None, 'yaml_parse_error')
        except Exception:
            return (None, 'yaml_parse_error')
        try:
            from dsl.serialiser import load_skill
            from dsl.validator import validate
            skill_yaml = yaml.dump(data, default_flow_style=False, sort_keys=False)
            skill = load_skill(skill_yaml)
            errors = validate(skill)
            if errors:
                msg = '; '.join((error.message for error in errors))
                return (None, f'dsl_validation_error: {msg}')
            return (skill, 'ok')
        except Exception as e:
            return (None, f'dsl_validation_error: {e}')

    def log_interaction(self, iteration: int, prompt: str, raw_response: str, parse_status: str, retry_count: int, accepted_yaml: str | None, metrics: dict | None=None):
        import hashlib
        record = {'iteration': iteration, 'template': self.template_name, 'prompt_hash': hashlib.sha256(prompt.encode()).hexdigest()[:16], 'prompt_length': len(prompt), 'raw_response_length': len(raw_response), 'parse_status': parse_status, 'retry_count': retry_count, 'accepted_yaml': accepted_yaml, 'metrics': metrics}
        self._interaction_log.append(record)
        self._last_action_record = record

    def stats(self) -> dict:
        total = len(self._interaction_log)
        ok = sum((1 for r in self._interaction_log if r['parse_status'] == 'ok'))
        return {'total_proposals': total, 'successful_parses': ok, 'parse_success_rate': ok / total if total > 0 else 0.0, 'mean_retries': sum((r['retry_count'] for r in self._interaction_log)) / total if total > 0 else 0.0}

    def last_action(self) -> dict:
        return self._last_action_record.copy()

    def get_interaction_log(self) -> list[dict]:
        return list(self._interaction_log)
