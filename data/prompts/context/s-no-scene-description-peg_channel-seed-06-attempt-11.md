## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1087 | 0.61 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3597 | 0.68 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3139 | 0.77 | ✅ accepted |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3307 | 0.46 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3411 | 0.65 | ❌ rejected |

**Proposal policy**: task_score is 0.61 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.109) — your mutation base

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

- **Composite score**: 0.109
- **task_score** (E): 0.608
- **fitness_score**: 0.435  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 0.00 | 1.00 | 0.0840 |
| contact_peg | 0.33 | 1.00 | 0.0388 |
| push_channel | 0.00 | 1.00 | 0.0015 |
| retract | 1.00 | 1.00 | 0.0903 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 0.00 / step_budget | (0.496, 0.144, 0.116)→(0.501, 0.121, 0.035) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.590 | 42.679 |
| contact_peg | contact | 0.33 / step_budget | (0.501, 0.121, 0.035)→(0.494, 0.083, 0.032) | (0.500, 0.108, 0.027)→(0.498, 0.070, 0.028) | 0.188→0.151 | 1.00 / 1.667 | 16.383 | 3.094 |
| push_channel | push | 0.00 / guard_failure | (0.501, 0.073, 0.028)→(0.502, 0.072, 0.027) | (0.498, 0.070, 0.028)→(0.500, 0.062, 0.029) | 0.151→0.142 | 1.00 / 2.333 | 52.728 | 1702.000 |
| retract | retract | 1.00 / step_budget | (0.502, 0.072, 0.027)→(0.499, 0.072, 0.118) | (0.501, 0.059, 0.029)→(0.495, 0.015, 0.021) | 0.139→0.101 | 1.00 / 1.000 | 0.609 | 698.414 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.950
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.950
- phase_score: 0.319
- phase_breakdown.pre_push_score: 0.928
- phase_breakdown.push_goal_score: 0.058

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.571
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.950
- **Median Q (composite search score)**: 0.157
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.362


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15306,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.04938,"approach_behind.lateral_offset_x":0.00246,"contact_peg.contact_force_threshold":10.50763,"contact_peg.contact_speed":0.03162,"push_channel.max_push_force":29.29378,"push_channel.push_speed":0.03363,"retract.retract_speed":0.04433},"optimized_scores":{"best_composite_score":0.15733,"best_fitness_score":0.56733,"best_task_score":0.87441},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53906,0.0326,0.05963],"force_p95":1458.88941,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1478.77379,"mean_force":1274.6329,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50455,0.01983,0.02506]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.53896,0.03615,0.05938],"force_p95":460.0064,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":472.31304,"mean_force":239.93104,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50784,0.01416,0.02559]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52532,0.01857,0.05995],"force_p95":433.04192,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":467.91345,"mean_force":174.56245,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50789,0.01401,0.02606]},{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.49584,0.00491,0.00985],"force_p95":13.10612,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.30988,"mean_force":5.52541,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49938,0.02809,0.02822]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1532.0,"contact_point_centroid":[0.50282,0.06627,0.00938],"force_p95":0.59595,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.20361,"mean_force":0.68288,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50014,0.14262,0.16331]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.49915,0.01548,0.03081],"force_p95":13.42698,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.08567,"mean_force":6.11102,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49995,0.0273,0.02792]},{"body_a":"attachment","body_b":"peg","contact_count":50.0,"contact_point_centroid":[0.50362,0.08122,0.04394],"force_p95":11.8361,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.96158,"mean_force":4.26893,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50515,0.09303,0.04377]},{"body_a":"peg","body_b":"channel_base_body","contact_count":869.0,"contact_point_centroid":[0.49957,-0.06866,0.00839],"force_p95":0.78549,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.85954,"mean_force":0.63052,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50292,0.01636,0.07206]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":18.0,"contact_point_centroid":[0.47494,-0.09106,0.03298],"force_p95":2.16866,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.68207,"mean_force":1.08268,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50272,0.01634,0.04819]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":24.0,"contact_point_centroid":[0.5253,-0.03831,0.03099],"force_p95":1.87193,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.22071,"mean_force":0.8168,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50587,0.01507,0.04824]},{"body_a":"peg","body_b":"channel_base_body","contact_count":983.0,"contact_point_centroid":[0.49624,0.02121,0.00992],"force_p95":1.26866,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.45266,"mean_force":0.77649,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49882,0.06005,0.03042]},{"body_a":"attachment","body_b":"peg","contact_count":881.0,"contact_point_centroid":[0.49822,0.04752,0.03125],"force_p95":0.94178,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.87032,"mean_force":0.49833,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4987,0.05948,0.03036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":87.0,"contact_point_centroid":[0.51295,-0.1001,0.02428],"force_p95":0.92522,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.60971,"mean_force":0.30185,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50274,0.01645,0.07456]}],"total_contact_groups":13},"final_pose_error":0.00993,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5,-0.07244,0.02406],"final_tcp_position":[0.50296,0.01652,0.11513],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":1478.77379,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1559.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.57043,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1582.0,"raw_peak_contact_force":15.20361,"subtask_id":"pre_push","tcp_end":[0.50598,0.08922,0.03469],"tcp_start":[0.50029,0.1265,0.1275],"tcp_to_object_dist_end":0.022,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49509,0.00395,0.03501],"object_pos_start":[0.49871,0.05988,0.03374],"object_to_goal_dist_end":0.08425,"object_to_goal_dist_start":0.14002,"object_z_max":0.03503,"peak_contact_force":0.68108,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1864.0,"raw_peak_contact_force":3.45266,"tcp_end":[0.49555,0.0339,0.03047],"tcp_start":[0.50598,0.08922,0.03469],"tcp_to_object_dist_end":0.03029,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.49974,-0.00889,0.0357],"object_pos_start":[0.49509,0.00395,0.03501],"object_to_goal_dist_end":0.07124,"object_to_goal_dist_start":0.08425,"object_z_max":0.03576,"peak_contact_force":1.0165,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":22.0,"raw_peak_contact_force":1478.77379,"subtask_id":"push_goal","tcp_end":[0.50632,0.01678,0.02448],"tcp_start":[0.50552,0.01817,0.02461],"tcp_to_object_dist_end":0.02878,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.5,-0.07244,0.02406],"object_pos_start":[0.50085,-0.01229,0.03583],"object_to_goal_dist_end":0.01764,"object_to_goal_dist_start":0.06784,"object_z_max":0.04075,"peak_contact_force":0.52459,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1027.0,"raw_peak_contact_force":472.31304,"tcp_end":[0.50296,0.01652,0.11513],"tcp_start":[0.50632,0.01678,0.02448],"tcp_to_object_dist_end":0.12735,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15306,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.03423,"approach_behind.lateral_offset_x":0.00519,"contact_peg.contact_force_threshold":12.89489,"contact_peg.contact_speed":0.03928,"push_channel.max_push_force":33.45495,"push_channel.push_speed":0.03401,"retract.retract_speed":0.04497},"optimized_scores":{"best_composite_score":0.16123,"best_fitness_score":0.57123,"best_task_score":0.94995},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52608,0.06666,0.05983],"force_p95":3270.71842,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3472.0559,"mean_force":1993.57363,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50965,0.06452,0.02559]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54654,0.07221,0.05971],"force_p95":3387.1927,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3387.1927,"mean_force":3387.1927,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5107,0.0628,0.025]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.54383,0.07976,0.05948],"force_p95":1484.97772,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1553.92389,"mean_force":996.48306,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51231,0.05908,0.02532]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":43.0,"contact_point_centroid":[0.52638,0.06307,0.05977],"force_p95":1287.15135,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1502.17786,"mean_force":371.42205,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51017,0.05946,0.02702]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1414.0,"contact_point_centroid":[0.50429,0.11107,0.00939],"force_p95":13.34818,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.81644,"mean_force":3.79451,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50417,0.16491,0.16416]},{"body_a":"attachment","body_b":"peg","contact_count":93.0,"contact_point_centroid":[0.51192,0.12615,0.05299],"force_p95":104.03627,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.00198,"mean_force":49.44519,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50991,0.13726,0.05256]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50232,0.06149,0.03313],"force_p95":18.14261,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.60839,"mean_force":13.96631,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50237,0.07321,0.02914]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.4986,0.04196,0.00988],"force_p95":17.07304,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.21014,"mean_force":7.29703,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50433,0.07086,0.02819]},{"body_a":"peg","body_b":"channel_base_body","contact_count":929.0,"contact_point_centroid":[0.50362,-0.04071,0.00808],"force_p95":0.72212,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.17818,"mean_force":0.69194,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50771,0.06075,0.0714]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":41.0,"contact_point_centroid":[0.52548,-0.0022,0.02704],"force_p95":8.28325,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.76295,"mean_force":2.14447,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50983,0.05993,0.04837]},{"body_a":"peg","body_b":"channel_base_body","contact_count":830.0,"contact_point_centroid":[0.50103,0.06529,0.00993],"force_p95":1.55782,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.11186,"mean_force":0.85238,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50321,0.10323,0.03112]},{"body_a":"attachment","body_b":"peg","contact_count":726.0,"contact_point_centroid":[0.50264,0.09044,0.03197],"force_p95":1.23854,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.23227,"mean_force":0.58402,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50307,0.1024,0.03104]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47491,-0.06099,0.03228],"force_p95":2.43625,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.48687,"mean_force":2.00707,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.50713,0.06019,0.02933]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52527,0.03074,0.01411],"force_p95":1.92932,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92932,"mean_force":1.92932,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5107,0.0628,0.025]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":21.0,"contact_point_centroid":[0.52577,0.10925,0.03619],"force_p95":0.49606,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.29022,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50232,0.18443,0.23953]}],"total_contact_groups":15},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5053,-0.04021,0.02413],"final_tcp_position":[0.50804,0.06085,0.1153],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":3472.0559,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1445.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11176,0.03381],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.56534,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1528.0,"raw_peak_contact_force":109.81644,"subtask_id":"pre_push","tcp_end":[0.50998,0.13315,0.03652],"tcp_start":[0.50711,0.15199,0.11607],"tcp_to_object_dist_end":0.02247,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":849.0,"n_steps_budget":960.0,"object_pos_end":[0.50052,0.04572,0.03496],"object_pos_start":[0.50453,0.10332,0.03391],"object_to_goal_dist_end":0.12582,"object_to_goal_dist_start":0.18348,"object_z_max":0.03513,"peak_contact_force":0.02552,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1556.0,"raw_peak_contact_force":5.11186,"tcp_end":[0.50014,0.07574,0.03024],"tcp_start":[0.50998,0.13315,0.03652],"tcp_to_object_dist_end":0.03039,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.50432,0.0336,0.03639],"object_pos_start":[0.50052,0.04572,0.03496],"object_to_goal_dist_end":0.11374,"object_to_goal_dist_start":0.12582,"object_z_max":0.03692,"peak_contact_force":2.0,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":21.0,"raw_peak_contact_force":3472.0559,"subtask_id":"push_goal","tcp_end":[0.51141,0.06137,0.02469],"tcp_start":[0.5107,0.0628,0.025],"tcp_to_object_dist_end":0.03096,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":970.0,"n_steps_budget":1000.0,"object_pos_end":[0.5053,-0.04021,0.02413],"object_pos_start":[0.50528,0.02938,0.03742],"object_to_goal_dist_end":0.04316,"object_to_goal_dist_start":0.10954,"object_z_max":0.04139,"peak_contact_force":0.53255,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1028.0,"raw_peak_contact_force":1553.92389,"tcp_end":[0.50804,0.06085,0.1153],"tcp_start":[0.51141,0.06137,0.02469],"tcp_to_object_dist_end":0.13614,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31915,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.04998,"approach_behind.lateral_offset_x":-0.00998,"contact_peg.contact_force_threshold":8.95894,"contact_peg.contact_speed":0.01426,"push_channel.max_push_force":30.42498,"push_channel.push_speed":0.02286,"retract.retract_speed":0.09074},"optimized_scores":{"best_composite_score":0.00766,"best_fitness_score":0.16766,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"world","contact_count":3.0,"contact_point_centroid":[0.49835,0.13522,-0.00192],"force_p95":152.70508,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":155.16893,"mean_force":134.10024,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48622,0.13965,0.03365]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49806,0.14017,0.03205],"force_p95":151.29088,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":153.77111,"mean_force":132.56677,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48622,0.13965,0.03365]},{"body_a":"peg","body_b":"world","contact_count":633.0,"contact_point_centroid":[0.4881,0.15778,-0.00191],"force_p95":1.04804,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.00633,"mean_force":1.09875,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48464,0.13784,0.07694]},{"body_a":"attachment","body_b":"peg","contact_count":39.0,"contact_point_centroid":[0.49892,0.14135,0.03343],"force_p95":20.92535,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.71363,"mean_force":8.23181,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48746,0.13834,0.03461]},{"body_a":"peg","body_b":"world","contact_count":291.0,"contact_point_centroid":[0.49577,0.15705,-0.00177],"force_p95":0.94342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.01598,"mean_force":0.62312,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48278,0.14459,0.05681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1103.0,"contact_point_centroid":[0.49606,0.1193,0.00943],"force_p95":0.5985,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54315,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48725,0.17309,0.18516]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49944,0.1993,0.29848]},{"body_a":"peg","body_b":"world","contact_count":10.0,"contact_point_centroid":[0.49724,0.1602,-0.00191],"force_p95":0.68707,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71664,"mean_force":0.60316,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48598,0.14013,0.03453]}],"total_contact_groups":8},"final_pose_error":0.01101,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.48095,0.15906,0.01404],"final_tcp_position":[0.48462,0.13788,0.12264],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":155.16893,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1423.0,"n_steps_budget":1000.0,"object_pos_end":[0.49605,0.1202,0.03386],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.20033,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.63475,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1418.0,"raw_peak_contact_force":3.01598,"subtask_id":"pre_push","tcp_end":[0.48624,0.14028,0.03503],"tcp_start":[0.47912,0.15383,0.10328],"tcp_to_object_dist_end":0.02238,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.49736,0.16018,0.0142],"object_pos_start":[0.49721,0.16012,0.01422],"object_to_goal_dist_end":0.24158,"object_to_goal_dist_start":0.24152,"object_z_max":0.01422,"peak_contact_force":48.44346,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10.0,"raw_peak_contact_force":0.71664,"tcp_end":[0.48579,0.13993,0.03386],"tcp_start":[0.48624,0.14028,0.03503],"tcp_to_object_dist_end":0.0305,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49744,0.1601,0.01431],"object_pos_start":[0.49736,0.16018,0.0142],"object_to_goal_dist_end":0.24148,"object_to_goal_dist_start":0.24158,"object_z_max":0.01452,"peak_contact_force":155.16893,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":155.16893,"subtask_id":"push_goal","tcp_end":[0.48777,0.13874,0.03315],"tcp_start":[0.48676,0.13931,0.03342],"tcp_to_object_dist_end":0.03007,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.48095,0.15906,0.01404],"object_pos_start":[0.49779,0.15967,0.01482],"object_to_goal_dist_end":0.24122,"object_to_goal_dist_start":0.241,"object_z_max":0.01763,"peak_contact_force":0.77041,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":672.0,"raw_peak_contact_force":69.00633,"tcp_end":[0.48462,0.13788,0.12264],"tcp_start":[0.48777,0.13874,0.03315],"tcp_to_object_dist_end":0.1107,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```