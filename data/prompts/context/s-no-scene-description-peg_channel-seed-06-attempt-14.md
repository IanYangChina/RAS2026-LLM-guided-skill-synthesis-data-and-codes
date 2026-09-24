## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0570 | 0.31 | ❌ rejected |
| 13 | approach → descend → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.0987 | 0.62 | ❌ rejected |
| 12 | approach → align → contact → push → retract | linear_cartesian | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.1187 | 0.64 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1087 | 0.61 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3597 | 0.68 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.057) — your mutation base

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

- **Composite score**: -0.057
- **task_score** (E): 0.313
- **fitness_score**: 0.400  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1230 |
| descend_to_peg | 1.00 | 1.00 | 0.0148 |
| contact_peg | 0.67 | 1.00 | 0.0097 |
| push_channel | 0.33 | 1.00 | 0.0533 |
| retract | 1.00 | 1.00 | 0.0906 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.168, 0.253)→(0.499, 0.122, 0.140) | (0.500, 0.099, 0.040)→(0.501, 0.099, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.546 | 2.127 |
| descend_to_peg | descend | 1.00 / step_budget | (0.513, 0.106, 0.041)→(0.500, 0.105, 0.035) | (0.501, 0.099, 0.034)→(0.505, 0.096, 0.028) | 0.180→0.177 | 1.00 / 2.000 | 59.128 | 237.960 |
| contact_peg | contact | 0.67 / force_exceeded | (0.500, 0.105, 0.035)→(0.500, 0.096, 0.035) | (0.487, 0.100, 0.028)→(0.489, 0.090, 0.028) | 0.181→0.172 | 1.00 / 2.333 | 68.055 | 69.528 |
| push_channel | push | 0.33 / guard_failure | (0.500, 0.063, 0.034)→(0.504, 0.010, 0.036) | (0.489, 0.090, 0.028)→(0.489, 0.066, 0.024) | 0.172→0.151 | 1.00 / 2.667 | 63.773 | 87.444 |
| retract | retract | 1.00 / step_budget | (0.504, 0.010, 0.036)→(0.501, 0.010, 0.126) | (0.489, 0.066, 0.024)→(0.492, 0.066, 0.027) | 0.151→0.149 | 1.00 / 1.000 | 0.584 | 66.053 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.918
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.918
- phase_score: 0.629
- phase_breakdown.pre_push_score: 0.736
- phase_breakdown.push_goal_score: 0.583

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.744
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.918
- **Median Q (composite search score)**: -0.113
- **K-run variance**: 0.0240
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.338


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.49444,"average_solve_count":360.0,"average_success_count":360.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_x":-0.00058,"approach_above.approach_speed":0.04669,"contact_peg.contact_force_threshold":11.77349,"contact_peg.contact_speed":0.01588,"descend_to_peg.descend_lateral_x":-0.00735,"descend_to_peg.descend_speed":0.01959,"push_channel.push_offset_x":0.00625,"push_channel.push_offset_y":-0.00387,"push_channel.push_speed":0.05951,"retract.retract_speed":0.05234},"optimized_scores":{"best_composite_score":0.15432,"best_fitness_score":0.74432,"best_task_score":0.91759},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1951.0,"contact_point_centroid":[0.50942,0.06402,0.00761],"force_p95":245.17724,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":248.76174,"mean_force":125.78484,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50468,0.07284,0.05793]},{"body_a":"attachment","body_b":"peg","contact_count":1460.0,"contact_point_centroid":[0.5144,0.06545,0.04969],"force_p95":244.83544,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":247.42924,"mean_force":168.9302,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.507,0.07028,0.04718]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":681.0,"contact_point_centroid":[0.52504,0.06979,0.06],"force_p95":135.15245,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.20779,"mean_force":109.14675,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51181,0.06999,0.0458]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":408.0,"contact_point_centroid":[0.47403,0.05782,0.02334],"force_p95":81.27939,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":97.09681,"mean_force":22.93338,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50895,0.07064,0.04199]},{"body_a":"attachment","body_b":"peg","contact_count":517.0,"contact_point_centroid":[0.49657,-0.02241,0.03783],"force_p95":16.43976,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.33476,"mean_force":6.86332,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4887,-0.01261,0.02827]},{"body_a":"peg","body_b":"channel_base_body","contact_count":29.0,"contact_point_centroid":[0.50676,-0.10035,0.06037],"force_p95":36.21686,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.8793,"mean_force":26.23446,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49067,-0.0559,0.02984]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":151.0,"contact_point_centroid":[0.52532,0.06254,0.04976],"force_p95":23.05033,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.42918,"mean_force":11.2586,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50879,0.06916,0.0468]},{"body_a":"peg","body_b":"channel_base_body","contact_count":108.0,"contact_point_centroid":[0.50649,-0.10014,0.06059],"force_p95":17.24567,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.07597,"mean_force":4.80701,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4881,-0.05632,0.03585]},{"body_a":"attachment","body_b":"peg","contact_count":227.0,"contact_point_centroid":[0.49583,-0.06664,0.05919],"force_p95":10.25618,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.36637,"mean_force":2.07677,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.4875,-0.0564,0.04459]},{"body_a":"peg","body_b":"channel_base_body","contact_count":349.0,"contact_point_centroid":[0.50723,-0.04807,0.00992],"force_p95":9.24752,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.56255,"mean_force":4.34697,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48857,-0.00791,0.02817]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":484.0,"contact_point_centroid":[0.5252,-0.03823,0.03113],"force_p95":11.09589,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.11689,"mean_force":4.20334,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48858,-0.01462,0.02813]},{"body_a":"peg","body_b":"channel_base_body","contact_count":807.0,"contact_point_centroid":[0.50729,-0.08385,0.00959],"force_p95":1.16944,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.47589,"mean_force":0.64579,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48719,-0.05651,0.07727]},{"body_a":"peg","body_b":"channel_base_body","contact_count":913.0,"contact_point_centroid":[0.4945,0.00671,0.00996],"force_p95":2.31023,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.62607,"mean_force":1.4206,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48886,0.05323,0.02832]},{"body_a":"attachment","body_b":"peg","contact_count":947.0,"contact_point_centroid":[0.49199,0.04123,0.03715],"force_p95":1.94293,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.39732,"mean_force":1.07345,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48884,0.05308,0.02831]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":43.0,"contact_point_centroid":[0.52507,-0.08232,0.0599],"force_p95":3.64937,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.01011,"mean_force":1.76444,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48877,-0.0563,0.03238]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47492,0.03711,0.03511],"force_p95":1.76855,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.15633,"mean_force":0.50947,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48944,0.06707,0.02826]}],"total_contact_groups":17},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50345,-0.07935,0.03388],"final_tcp_position":[0.4874,-0.05655,0.12029],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":248.76174,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1231.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.55044,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1215.0,"raw_peak_contact_force":2.06903,"subtask_id":"pre_push","tcp_end":[0.50297,0.08927,0.13275],"tcp_start":[0.49906,0.10335,0.15871],"tcp_to_object_dist_end":0.10133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1964.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.06263,0.02528],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.14356,"object_to_goal_dist_start":0.14766,"object_z_max":0.03586,"peak_contact_force":0.51051,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4651.0,"raw_peak_contact_force":248.76174,"subtask_id":"pre_push","tcp_end":[0.49133,0.06927,0.03024],"tcp_start":[0.51169,0.07058,0.04352],"tcp_to_object_dist_end":0.01772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":987.0,"n_steps_budget":1000.0,"object_pos_end":[0.49842,0.01145,0.03569],"object_pos_start":[0.49362,0.03885,0.03466],"object_to_goal_dist_end":0.09156,"object_to_goal_dist_start":0.11914,"object_z_max":0.03571,"peak_contact_force":1.20584,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1888.0,"raw_peak_contact_force":5.62607,"tcp_end":[0.48967,0.04034,0.03],"tcp_start":[0.49133,0.06927,0.03024],"tcp_to_object_dist_end":0.03072,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":639.0,"n_steps_budget":1000.0,"object_pos_end":[0.50521,-0.08234,0.03614],"object_pos_start":[0.49842,0.01145,0.03569],"object_to_goal_dist_end":0.00689,"object_to_goal_dist_start":0.09156,"object_z_max":0.03739,"peak_contact_force":22.68828,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1379.0,"raw_peak_contact_force":40.33476,"subtask_id":"push_goal","tcp_end":[0.4906,-0.05691,0.0297],"tcp_start":[0.49062,-0.05691,0.02974],"tcp_to_object_dist_end":0.03003,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":863.0,"n_steps_budget":1000.0,"object_pos_end":[0.50345,-0.07935,0.03388],"object_pos_start":[0.50519,-0.08241,0.03612],"object_to_goal_dist_end":0.00706,"object_to_goal_dist_start":0.00692,"object_z_max":0.03717,"peak_contact_force":0.54341,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1185.0,"raw_peak_contact_force":18.07597,"tcp_end":[0.4874,-0.05655,0.12029],"tcp_start":[0.4906,-0.05691,0.0297],"tcp_to_object_dist_end":0.0908,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.42857,"average_solve_count":280.0,"average_success_count":280.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_x":0.00367,"approach_above.approach_speed":0.04614,"contact_peg.contact_force_threshold":18.0189,"contact_peg.contact_speed":0.01778,"descend_to_peg.descend_lateral_x":-0.00911,"descend_to_peg.descend_speed":0.01104,"push_channel.push_offset_x":-0.00251,"push_channel.push_offset_y":0.00235,"push_channel.push_speed":0.02843,"retract.retract_speed":0.0517},"optimized_scores":{"best_composite_score":-0.21224,"best_fitness_score":0.17776,"best_task_score":0.02063},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":2510.0,"contact_point_centroid":[0.51284,0.11031,0.00683],"force_p95":228.96874,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":251.8356,"mean_force":140.60956,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50741,0.1183,0.05662]},{"body_a":"attachment","body_b":"peg","contact_count":2050.0,"contact_point_centroid":[0.51564,0.11039,0.04916],"force_p95":231.73539,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":251.34942,"mean_force":172.49693,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5087,0.11664,0.04667]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":647.0,"contact_point_centroid":[0.52504,0.11717,0.06],"force_p95":147.19991,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":228.64401,"mean_force":64.96069,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51257,0.11757,0.04583]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50679,0.10035,0.00376],"force_p95":189.6089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":192.00672,"mean_force":157.04536,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51165,0.11686,0.0412]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50394,0.10769,0.04403],"force_p95":188.78371,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":191.15814,"mean_force":156.29583,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51165,0.11686,0.0412]},{"body_a":"peg","body_b":"channel_base_body","contact_count":825.0,"contact_point_centroid":[0.49784,0.10702,0.00914],"force_p95":56.96313,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":179.39823,"mean_force":7.15657,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50908,0.11633,0.09072]},{"body_a":"attachment","body_b":"peg","contact_count":105.0,"contact_point_centroid":[0.50462,0.10779,0.05304],"force_p95":130.33077,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":178.736,"mean_force":52.01358,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51223,0.117,0.05209]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51152,0.12,0.00371],"force_p95":173.47869,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":173.47869,"mean_force":173.47869,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51158,0.11688,0.04112]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50401,0.10761,0.04394],"force_p95":172.62375,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":172.62375,"mean_force":172.62375,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51158,0.11688,0.04112]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52501,0.11713,0.04876],"force_p95":80.35329,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.27391,"mean_force":35.61202,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51302,0.11714,0.04828]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":162.0,"contact_point_centroid":[0.52502,0.1083,0.05338],"force_p95":20.04855,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.68533,"mean_force":7.82949,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51047,0.11584,0.04814]},{"body_a":"peg","body_b":"world","contact_count":343.0,"contact_point_centroid":[0.50505,0.10642,-0.0008],"force_p95":15.48353,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.4633,"mean_force":7.10522,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51165,0.11705,0.04213]},{"body_a":"peg","body_b":"channel_base_body","contact_count":917.0,"contact_point_centroid":[0.50363,0.1117,0.00938],"force_p95":0.60142,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55299,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50412,0.16578,0.21709]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49972,0.1994,0.29936]},{"body_a":"peg","body_b":"world","contact_count":3.0,"contact_point_centroid":[0.50672,0.10099,-0.00124],"force_p95":0.079,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.08778,"mean_force":0.02926,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51165,0.11686,0.0412]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.50752,0.12309,-0.00129],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51158,0.11688,0.04112]}],"total_contact_groups":17},"final_pose_error":0.00996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4981,0.10711,0.03385],"final_tcp_position":[0.50872,0.11626,0.1319],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":251.8356,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":939.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11177,0.03384],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.54071,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":933.0,"raw_peak_contact_force":2.06328,"subtask_id":"pre_push","tcp_end":[0.50989,0.13408,0.14221],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":2510.0,"n_steps_budget":1000.0,"object_pos_end":[0.50464,0.108,0.02676],"object_pos_start":[0.50371,0.11177,0.03384],"object_to_goal_dist_end":0.18853,"object_to_goal_dist_start":0.19191,"object_z_max":0.03401,"peak_contact_force":159.27944,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5712.0,"raw_peak_contact_force":251.8356,"subtask_id":"pre_push","tcp_end":[0.51158,0.11688,0.04112],"tcp_start":[0.51267,0.11777,0.04359],"tcp_to_object_dist_end":0.01825,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":870.0,"object_pos_end":[0.49905,0.10725,0.02248],"object_pos_start":[0.49904,0.10726,0.02246],"object_to_goal_dist_end":0.18807,"object_to_goal_dist_start":0.18809,"object_z_max":0.02246,"peak_contact_force":173.47869,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":173.47869,"tcp_end":[0.5116,0.11687,0.04114],"tcp_start":[0.51158,0.11688,0.04112],"tcp_to_object_dist_end":0.02446,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49907,0.10723,0.02254],"object_pos_start":[0.49905,0.10725,0.02248],"object_to_goal_dist_end":0.18805,"object_to_goal_dist_start":0.18807,"object_z_max":0.02261,"peak_contact_force":168.02853,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":192.00672,"subtask_id":"push_goal","tcp_end":[0.51179,0.11693,0.04135],"tcp_start":[0.51172,0.11687,0.04126],"tcp_to_object_dist_end":0.02469,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.4981,0.10711,0.03385],"object_pos_start":[0.49918,0.10728,0.02269],"object_to_goal_dist_end":0.18723,"object_to_goal_dist_start":0.18808,"object_z_max":0.03466,"peak_contact_force":0.52502,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":949.0,"raw_peak_contact_force":179.39823,"tcp_end":[0.50872,0.11626,0.1319],"tcp_start":[0.51179,0.11693,0.04135],"tcp_to_object_dist_end":0.09904,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.58924,"average_solve_count":409.0,"average_success_count":409.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_offset_x":0.00071,"approach_above.approach_speed":0.02026,"contact_peg.contact_force_threshold":8.98081,"contact_peg.contact_speed":0.02312,"descend_to_peg.descend_lateral_x":0.00549,"descend_to_peg.descend_speed":0.01446,"push_channel.push_offset_x":-0.00545,"push_channel.push_offset_y":-0.00906,"push_channel.push_speed":0.03169,"retract.retract_speed":0.07271},"optimized_scores":{"best_composite_score":-0.1132,"best_fitness_score":0.2768,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":1324.0,"contact_point_centroid":[0.51154,0.1218,0.04971],"force_p95":194.84258,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":213.28279,"mean_force":123.94884,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50976,0.12632,0.04783]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1929.0,"contact_point_centroid":[0.50181,0.11916,0.00874],"force_p95":191.8986,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":212.41071,"mean_force":77.92908,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50266,0.12831,0.06485]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":571.0,"contact_point_centroid":[0.52502,0.11999,0.06],"force_p95":87.45057,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.53723,"mean_force":48.45147,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51418,0.12708,0.04715]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":520.0,"contact_point_centroid":[0.47405,0.11959,0.02301],"force_p95":95.54085,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.64549,"mean_force":42.51325,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51365,0.12899,0.04177]},{"body_a":"peg","body_b":"world","contact_count":994.0,"contact_point_centroid":[0.46832,0.16912,-0.00176],"force_p95":1.0614,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.99051,"mean_force":1.06594,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50199,0.04667,0.03239]},{"body_a":"attachment","body_b":"peg","contact_count":53.0,"contact_point_centroid":[0.48828,0.13371,0.03245],"force_p95":25.37591,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.62971,"mean_force":8.7719,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49674,0.1255,0.03125]},{"body_a":"peg","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.47885,0.14339,-0.00028],"force_p95":29.47908,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.47908,"mean_force":29.47908,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49747,0.12979,0.03244]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.48807,0.13692,0.03376],"force_p95":28.48186,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.48186,"mean_force":28.48186,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49747,0.12979,0.03244]},{"body_a":"peg","body_b":"world","contact_count":45.0,"contact_point_centroid":[0.47883,0.14259,-0.00018],"force_p95":16.64211,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.59506,"mean_force":6.65405,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50083,0.12999,0.03337]},{"body_a":"peg","body_b":"channel_base_body","contact_count":849.0,"contact_point_centroid":[0.49619,0.11907,0.00941],"force_p95":0.6123,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55071,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49118,0.16964,0.21825]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49946,0.19924,0.29867]},{"body_a":"peg","body_b":"world","contact_count":764.0,"contact_point_centroid":[0.4658,0.17243,-0.00196],"force_p95":0.68377,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68378,"mean_force":0.60615,"phase_index":4.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.506,-0.02925,0.08119]}],"total_contact_groups":12},"final_pose_error":0.01008,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.47475,0.17109,0.01413],"final_tcp_position":[0.50608,-0.02921,0.12661],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":213.28279,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.11906,0.0339],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19919,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.54547,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":873.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_push","tcp_end":[0.48452,0.1413,0.14361],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11253,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1977.0,"n_steps_budget":1000.0,"object_pos_end":[0.50212,0.11853,0.03092],"object_pos_start":[0.49608,0.11906,0.0339],"object_to_goal_dist_end":0.19875,"object_to_goal_dist_start":0.19919,"object_z_max":0.03517,"peak_contact_force":17.59506,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4389.0,"raw_peak_contact_force":213.28279,"subtask_id":"pre_push","tcp_end":[0.49747,0.12979,0.03244],"tcp_start":[0.51407,0.12847,0.03701],"tcp_to_object_dist_end":0.01228,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.46853,0.15269,0.02691],"object_pos_start":[0.4685,0.15261,0.02694],"object_to_goal_dist_end":0.23517,"object_to_goal_dist_start":0.2351,"object_z_max":0.02694,"peak_contact_force":29.47908,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":29.47908,"tcp_end":[0.49737,0.12979,0.0324],"tcp_start":[0.49747,0.12979,0.03244],"tcp_to_object_dist_end":0.03723,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46139,0.1731,0.01413],"object_pos_start":[0.46853,0.15269,0.02691],"object_to_goal_dist_end":0.25733,"object_to_goal_dist_start":0.23517,"object_z_max":0.02954,"peak_contact_force":0.60188,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1047.0,"raw_peak_contact_force":29.99051,"subtask_id":"push_goal","tcp_end":[0.50936,-0.0294,0.03614],"tcp_start":[0.49737,0.12979,0.0324],"tcp_to_object_dist_end":0.20927,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":764.0,"n_steps_budget":870.0,"object_pos_end":[0.47475,0.17109,0.01413],"object_pos_start":[0.46139,0.1731,0.01413],"object_to_goal_dist_end":0.25368,"object_to_goal_dist_start":0.25733,"object_z_max":0.01413,"peak_contact_force":0.68371,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":764.0,"raw_peak_contact_force":0.68378,"tcp_end":[0.50608,-0.02921,0.12661],"tcp_start":[0.50936,-0.0294,0.03614],"tcp_to_object_dist_end":0.23185,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```