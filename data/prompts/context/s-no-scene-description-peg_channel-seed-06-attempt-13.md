## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.0987 | 0.62 | ❌ rejected |
| 12 | approach → align → contact → push → retract | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.1187 | 0.64 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1087 | 0.61 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3597 | 0.68 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3139 | 0.77 | ✅ accepted |

**Proposal policy**: task_score is 0.62 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: peg_channel
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.099) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_push
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
  weight: 0.3
- id: push_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_behind
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
  guards:
  - id: check_approach
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: pre_push
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: ensure_contact
    when: during_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
- id: push_channel
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  subtask_id: push_goal
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
  - guards:
    - id=check_approach, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=ensure_contact, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_channel** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.18, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.099
- **task_score** (E): 0.619
- **fitness_score**: 0.458  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.690

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1484 |
| descend_to_peg | 1.00 | 1.00 | 0.0639 |
| contact_peg | 0.67 | 1.00 | 0.0124 |
| push_channel | 0.33 | 1.00 | 0.0544 |
| retract | 1.00 | 1.00 | 0.0904 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.499, 0.097, 0.196) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.531 | 2.127 |
| descend_to_peg | descend | 1.00 / step_budget | (0.503, 0.114, 0.100)→(0.503, 0.121, 0.037) | (0.501, 0.099, 0.034)→(0.503, 0.114, 0.027) | 0.180→0.195 | 1.00 / 1.333 | 0.581 | 111.552 |
| contact_peg | contact | 0.67 / force_exceeded | (0.503, 0.121, 0.037)→(0.497, 0.113, 0.033) | (0.499, 0.110, 0.028)→(0.498, 0.101, 0.029) | 0.191→0.181 | 1.00 / 2.000 | 1311.650 | 2.636 |
| push_channel | push | 0.33 / guard_failure | (0.497, 0.063, 0.033)→(0.497, 0.009, 0.033) | (0.498, 0.101, 0.029)→(0.499, -0.003, 0.029) | 0.181→0.087 | 1.00 / 2.667 | 30.486 | 40.840 |
| retract | retract | 1.00 / step_budget | (0.497, 0.009, 0.033)→(0.494, 0.009, 0.123) | (0.499, -0.003, 0.029)→(0.512, 0.001, 0.027) | 0.087→0.086 | 1.00 / 1.000 | 0.586 | 33.830 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.858
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.858
- phase_score: 0.517
- phase_breakdown.pre_push_score: 0.201
- phase_breakdown.push_goal_score: 0.653

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.674
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: -0.016
- **K-run variance**: 0.0647
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.274


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.88983,"average_solve_count":354.0,"average_success_count":354.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.03463,"approach_above.arc_height":0.06218,"approach_above.lateral_offset_x":-0.0039,"approach_above.lateral_offset_y":-0.0091,"contact_peg.contact_force_threshold":11.68807,"contact_peg.contact_speed":0.01836,"descend_to_peg.descend_lateral_x":-0.00052,"descend_to_peg.descend_speed":0.01293,"push_channel.push_offset_x":0.00625,"push_channel.push_offset_y":0.00371,"push_channel.push_speed":0.03724,"retract.retract_speed":0.07403},"optimized_scores":{"best_composite_score":0.16346,"best_fitness_score":0.65346,"best_task_score":0.85802},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":114.0,"contact_point_centroid":[0.52503,0.09049,0.06],"force_p95":154.50136,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.58819,"mean_force":85.88716,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51199,0.09063,0.05047]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1513.0,"contact_point_centroid":[0.50791,0.07165,0.009],"force_p95":151.88968,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":159.66766,"mean_force":46.44932,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5009,0.07615,0.09666]},{"body_a":"attachment","body_b":"peg","contact_count":580.0,"contact_point_centroid":[0.51682,0.0806,0.05408],"force_p95":157.78353,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":159.28166,"mean_force":119.97784,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50817,0.08735,0.05279]},{"body_a":"attachment","body_b":"peg","contact_count":388.0,"contact_point_centroid":[0.49806,-0.06719,0.05809],"force_p95":35.36339,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.56974,"mean_force":24.28163,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50093,-0.056,0.05771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":56.0,"contact_point_centroid":[0.49311,-0.10129,0.03604],"force_p95":34.60627,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.86352,"mean_force":23.18512,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50388,-0.05708,0.03554]},{"body_a":"peg","body_b":"channel_base_body","contact_count":398.0,"contact_point_centroid":[0.4921,-0.10083,0.06096],"force_p95":37.27035,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.54991,"mean_force":24.44047,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50092,-0.05605,0.05833]},{"body_a":"attachment","body_b":"peg","contact_count":628.0,"contact_point_centroid":[0.49878,-0.00348,0.03475],"force_p95":22.59032,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.53502,"mean_force":3.24508,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50227,0.00787,0.03411]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":215.0,"contact_point_centroid":[0.47492,-0.08396,0.05656],"force_p95":21.52285,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.5481,"mean_force":5.40126,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50093,-0.05599,0.05132]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":252.0,"contact_point_centroid":[0.52511,0.07019,0.05692],"force_p95":4.956,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.87333,"mean_force":2.6353,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50887,0.08722,0.05309]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":533.0,"contact_point_centroid":[0.47492,-0.02095,0.03044],"force_p95":1.53799,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.54391,"mean_force":0.64452,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50217,0.00747,0.03399]},{"body_a":"peg","body_b":"channel_base_body","contact_count":612.0,"contact_point_centroid":[0.49541,-0.02106,0.00986],"force_p95":4.45106,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.36406,"mean_force":1.55303,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50213,0.01555,0.03398]},{"body_a":"peg","body_b":"channel_base_body","contact_count":342.0,"contact_point_centroid":[0.50297,-0.06973,0.00932],"force_p95":1.06262,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.30805,"mean_force":0.60488,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50061,-0.0591,0.10558]},{"body_a":"peg","body_b":"channel_base_body","contact_count":939.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55232,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55581,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49752,0.11681,0.28285]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47461,0.05792,0.0571],"force_p95":1.6278,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83726,"mean_force":0.52663,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5077,0.09081,0.044]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":29.0,"contact_point_centroid":[0.52516,-0.07344,0.04971],"force_p95":0.99656,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.10081,"mean_force":0.24438,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50062,-0.05767,0.08445]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50302,0.0795,0.03671],"force_p95":0.83762,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.86234,"mean_force":0.61509,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50403,0.09128,0.03666]}],"total_contact_groups":16},"final_pose_error":0.01011,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50307,-0.06982,0.03386],"final_tcp_position":[0.50078,-0.05919,0.12601],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":204.58819,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":955.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54558,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":939.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_push","tcp_end":[0.49655,0.05582,0.19916],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1518.0,"n_steps_budget":1000.0,"object_pos_end":[0.50569,0.06873,0.03263],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14902,"object_to_goal_dist_start":0.14759,"object_z_max":0.03718,"peak_contact_force":0.25703,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2473.0,"raw_peak_contact_force":204.58819,"tcp_end":[0.50408,0.09127,0.03673],"tcp_start":[0.50388,0.08382,0.05471],"tcp_to_object_dist_end":0.02296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50145,0.06159,0.03649],"object_pos_start":[0.50143,0.06178,0.03671],"object_to_goal_dist_end":0.14164,"object_to_goal_dist_start":0.14182,"object_z_max":0.03671,"peak_contact_force":12.70256,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":0.86234,"tcp_end":[0.50388,0.09129,0.03648],"tcp_start":[0.50408,0.09127,0.03673],"tcp_to_object_dist_end":0.0298,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":948.0,"n_steps_budget":1000.0,"object_pos_end":[0.49316,-0.08663,0.03517],"object_pos_start":[0.50145,0.06159,0.03649],"object_to_goal_dist_end":0.01068,"object_to_goal_dist_start":0.14164,"object_z_max":0.03649,"peak_contact_force":29.52526,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1829.0,"raw_peak_contact_force":42.86352,"subtask_id":"push_goal","tcp_end":[0.50408,-0.05953,0.03556],"tcp_start":[0.50411,-0.05952,0.0356],"tcp_to_object_dist_end":0.02922,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":766.0,"n_steps_budget":870.0,"object_pos_end":[0.50307,-0.06982,0.03386],"object_pos_start":[0.49306,-0.08673,0.03512],"object_to_goal_dist_end":0.01228,"object_to_goal_dist_start":0.01083,"object_z_max":0.0578,"peak_contact_force":0.54156,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1372.0,"raw_peak_contact_force":45.56974,"tcp_end":[0.50078,-0.05919,0.12601],"tcp_start":[0.50408,-0.05953,0.03556],"tcp_to_object_dist_end":0.09279,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.72823,"average_solve_count":379.0,"average_success_count":379.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.02809,"approach_above.arc_height":0.05696,"approach_above.lateral_offset_x":0.0018,"approach_above.lateral_offset_y":0.00362,"contact_peg.contact_force_threshold":17.35529,"contact_peg.contact_speed":0.0134,"descend_to_peg.descend_lateral_x":0.00621,"descend_to_peg.descend_speed":0.01136,"push_channel.push_offset_x":-0.00023,"push_channel.push_offset_y":0.00169,"push_channel.push_speed":0.0461,"retract.retract_speed":0.08407},"optimized_scores":{"best_composite_score":-0.01647,"best_fitness_score":0.67353,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1335.0,"contact_point_centroid":[0.50799,0.11383,0.00913],"force_p95":121.30865,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":127.09241,"mean_force":35.70895,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50994,0.12298,0.09827]},{"body_a":"attachment","body_b":"peg","contact_count":452.0,"contact_point_centroid":[0.51925,0.12269,0.05496],"force_p95":123.20381,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.63273,"mean_force":104.06466,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51493,0.13248,0.05354]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":177.0,"contact_point_centroid":[0.5251,0.11509,0.05727],"force_p95":10.14216,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.27284,"mean_force":2.88607,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51457,0.13145,0.05361]},{"body_a":"attachment","body_b":"peg","contact_count":823.0,"contact_point_centroid":[0.4993,0.01357,0.0401],"force_p95":9.92245,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.86689,"mean_force":3.11287,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49295,0.02463,0.02788]},{"body_a":"attachment","body_b":"peg","contact_count":89.0,"contact_point_centroid":[0.49952,-0.06436,0.05731],"force_p95":4.92376,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.19053,"mean_force":1.03462,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4922,-0.05302,0.03835]},{"body_a":"peg","body_b":"channel_base_body","contact_count":634.0,"contact_point_centroid":[0.50652,-0.08305,0.0095],"force_p95":0.55562,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.67074,"mean_force":0.54816,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49128,-0.05285,0.07599]},{"body_a":"peg","body_b":"channel_base_body","contact_count":537.0,"contact_point_centroid":[0.50511,-0.01478,0.00993],"force_p95":9.11962,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.24159,"mean_force":4.46498,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49291,0.02866,0.02781]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50693,-0.10009,0.0598],"force_p95":10.39801,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.55519,"mean_force":9.05884,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49473,-0.05277,0.03006]},{"body_a":"peg","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.52088,0.0584,0.06241],"force_p95":9.03732,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.15077,"mean_force":3.60286,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49161,0.07546,0.02617]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":604.0,"contact_point_centroid":[0.52511,-0.01347,0.02619],"force_p95":5.16584,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.08601,"mean_force":1.72667,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49307,0.01292,0.02806]},{"body_a":"peg","body_b":"channel_base_body","contact_count":27.0,"contact_point_centroid":[0.50676,-0.10019,0.06004],"force_p95":5.07366,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.67472,"mean_force":2.55077,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49376,-0.0533,0.0312]},{"body_a":"peg","body_b":"channel_base_body","contact_count":860.0,"contact_point_centroid":[0.4962,0.07776,0.0098],"force_p95":1.77209,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.32064,"mean_force":1.08797,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49933,0.11913,0.03085]},{"body_a":"attachment","body_b":"peg","contact_count":718.0,"contact_point_centroid":[0.49897,0.1058,0.03761],"force_p95":1.5229,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.85553,"mean_force":0.86031,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49857,0.11778,0.03058]},{"body_a":"peg","body_b":"channel_base_body","contact_count":732.0,"contact_point_centroid":[0.5036,0.11169,0.00939],"force_p95":0.60308,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55434,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50686,0.13589,0.27314]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52506,-0.08197,0.06],"force_p95":0.92731,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98412,"mean_force":0.47084,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49303,-0.05315,0.03259]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49962,0.19895,0.29998]}],"total_contact_groups":16},"final_pose_error":0.01066,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50528,-0.08022,0.03381],"final_tcp_position":[0.49147,-0.05285,0.11992],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":127.09241,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":754.0,"n_steps_budget":1000.0,"object_pos_end":[0.50372,0.11172,0.03392],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.49617,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":748.0,"raw_peak_contact_force":2.06328,"subtask_id":"pre_push","tcp_end":[0.5101,0.10812,0.19662],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16286,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1335.0,"n_steps_budget":1000.0,"object_pos_end":[0.50551,0.11327,0.03337],"object_pos_start":[0.50372,0.11172,0.03392],"object_to_goal_dist_end":0.19346,"object_to_goal_dist_start":0.19185,"object_z_max":0.0363,"peak_contact_force":0.92295,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1964.0,"raw_peak_contact_force":127.09241,"tcp_end":[0.51108,0.13576,0.03761],"tcp_start":[0.51411,0.13096,0.05313],"tcp_to_object_dist_end":0.02355,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":893.0,"n_steps_budget":1000.0,"object_pos_end":[0.49587,0.07999,0.03504],"object_pos_start":[0.49776,0.10946,0.03404],"object_to_goal_dist_end":0.16012,"object_to_goal_dist_start":0.18957,"object_z_max":0.03595,"peak_contact_force":1.23505,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1578.0,"raw_peak_contact_force":6.32064,"tcp_end":[0.49452,0.11,0.02951],"tcp_start":[0.51108,0.13576,0.03761],"tcp_to_object_dist_end":0.03055,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50689,-0.08088,0.03604],"object_pos_start":[0.49587,0.07999,0.03504],"object_to_goal_dist_end":0.00799,"object_to_goal_dist_start":0.16012,"object_z_max":0.03662,"peak_contact_force":12.75005,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1995.0,"raw_peak_contact_force":16.86689,"subtask_id":"push_goal","tcp_end":[0.49473,-0.05317,0.03006],"tcp_start":[0.49452,0.11,0.02951],"tcp_to_object_dist_end":0.03085,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":657.0,"n_steps_budget":750.0,"object_pos_end":[0.50528,-0.08022,0.03381],"object_pos_start":[0.50689,-0.08088,0.03604],"object_to_goal_dist_end":0.00814,"object_to_goal_dist_start":0.00799,"object_z_max":0.03643,"peak_contact_force":0.54751,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":756.0,"raw_peak_contact_force":16.19053,"tcp_end":[0.49147,-0.05285,0.11992],"tcp_start":[0.49473,-0.05317,0.03006],"tcp_to_object_dist_end":0.09141,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.81019,"average_solve_count":216.0,"average_success_count":216.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.07223,"approach_above.arc_height":0.06427,"approach_above.lateral_offset_x":0.00771,"approach_above.lateral_offset_y":0.0156,"contact_peg.contact_force_threshold":12.83188,"contact_peg.contact_speed":0.02367,"descend_to_peg.descend_lateral_x":0.0018,"descend_to_peg.descend_speed":0.0229,"push_channel.push_offset_x":0.00049,"push_channel.push_offset_y":-0.00359,"push_channel.push_speed":0.04977,"retract.retract_speed":0.04713},"optimized_scores":{"best_composite_score":-0.44316,"best_fitness_score":0.04684,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"world","contact_count":8.0,"contact_point_centroid":[0.49771,0.13493,-0.00192],"force_p95":58.02734,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.78906,"mean_force":38.39741,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49189,0.13876,0.03278]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50054,0.14651,0.03173],"force_p95":57.69121,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.37865,"mean_force":37.86537,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49189,0.13876,0.03278]},{"body_a":"peg","body_b":"world","contact_count":921.0,"contact_point_centroid":[0.51314,0.15606,-0.00187],"force_p95":0.7088,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.73037,"mean_force":0.93957,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4884,0.1377,0.07795]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.49957,0.14613,0.03312],"force_p95":31.66852,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.31348,"mean_force":8.70902,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49077,0.13843,0.0341]},{"body_a":"peg","body_b":"world","contact_count":197.0,"contact_point_centroid":[0.49642,0.15548,-0.00163],"force_p95":1.03879,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.97671,"mean_force":0.62892,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4931,0.13612,0.05188]},{"body_a":"peg","body_b":"channel_base_body","contact_count":659.0,"contact_point_centroid":[0.4962,0.11905,0.00942],"force_p95":0.61784,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5529,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49215,0.13587,0.26817]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49918,0.1979,0.30008]},{"body_a":"peg","body_b":"world","contact_count":34.0,"contact_point_centroid":[0.4977,0.15999,-0.00199],"force_p95":0.72589,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72592,"mean_force":0.60642,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49285,0.1378,0.03542]},{"body_a":"peg","body_b":"channel_base_body","contact_count":800.0,"contact_point_centroid":[0.49591,0.11926,0.00945],"force_p95":0.59794,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65043,"mean_force":0.53325,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49028,0.13012,0.12759]}],"total_contact_groups":9},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.52855,0.15397,0.01414],"final_tcp_position":[0.48851,0.13772,0.12321],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":3921.01344,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":684.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.11902,0.03382],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19916,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.55171,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":683.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_push","tcp_end":[0.49045,0.12581,0.19283],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49748,0.16001,0.01409],"object_pos_start":[0.49608,0.11902,0.03382],"object_to_goal_dist_end":0.24141,"object_to_goal_dist_start":0.19916,"object_z_max":0.03426,"peak_contact_force":0.56225,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":997.0,"raw_peak_contact_force":2.97671,"tcp_end":[0.49367,0.13726,0.03764],"tcp_start":[0.49045,0.12581,0.19283],"tcp_to_object_dist_end":0.03296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":34.0,"n_steps_budget":870.0,"object_pos_end":[0.49806,0.15993,0.01409],"object_pos_start":[0.49748,0.16001,0.01409],"object_to_goal_dist_end":0.24133,"object_to_goal_dist_start":0.24141,"object_z_max":0.01409,"peak_contact_force":3921.01344,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":34.0,"raw_peak_contact_force":0.72592,"tcp_end":[0.49212,0.13876,0.03302],"tcp_start":[0.49367,0.13726,0.03764],"tcp_to_object_dist_end":0.02901,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.49794,0.15985,0.01436],"object_pos_start":[0.49806,0.15993,0.01409],"object_to_goal_dist_end":0.24122,"object_to_goal_dist_start":0.24133,"object_z_max":0.01444,"peak_contact_force":49.18414,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":62.78906,"subtask_id":"push_goal","tcp_end":[0.4917,0.13859,0.03262],"tcp_start":[0.4917,0.13862,0.03264],"tcp_to_object_dist_end":0.02871,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":921.0,"n_steps_budget":1000.0,"object_pos_end":[0.52855,0.15397,0.01414],"object_pos_start":[0.49799,0.15978,0.01449],"object_to_goal_dist_end":0.23712,"object_to_goal_dist_start":0.24114,"object_z_max":0.01692,"peak_contact_force":0.66756,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":957.0,"raw_peak_contact_force":39.73037,"tcp_end":[0.48851,0.13772,0.12321],"tcp_start":[0.4917,0.13859,0.03262],"tcp_to_object_dist_end":0.11732,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```