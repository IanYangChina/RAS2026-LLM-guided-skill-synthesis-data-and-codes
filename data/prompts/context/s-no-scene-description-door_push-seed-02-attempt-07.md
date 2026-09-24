## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.3809 | 0.62 | ✅ accepted |
| 6 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.2367 | 0.53 | ❌ rejected |
| 5 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.2450 | 0.57 | ✅ accepted |
| 4 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1753 | 0.54 | ✅ accepted |
| 3 | approach → align → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.1958 | 0.52 | ❌ rejected |

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

- Task name: door_push
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

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
| `object` | offset from object initial position | approach/contact targets near object |
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

## Current Skill (Q=0.381) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_door
  offset:
  - 0.05
  - 0.0
  - 0.1
  weight: 0.3
- id: push_door
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.05
    - 0.0
    - 0.1
    tolerance: 0.02
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_door
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.02
    - 0.0
    - 0.0
    tolerance: 0.005
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: reach_door
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.06
      axis: world_x
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_push_dist:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: push_door
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: world_y
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: push_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.05, 0.0, 0.1], tolerance=0.02
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **align_1** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.02, 0.0, 0.0], tolerance=0.005
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_x, distance=0.06, mode=add_to_offset, sign=positive}, tolerance=0.01
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_push_dist: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.25, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.381
- **task_score** (E): 0.624
- **fitness_score**: 0.624  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2269 |
| align_1 | 1.00 | 1.00 | 0.0976 |
| contact_1 | 1.00 | 1.00 | 0.0381 |
| push_1 | 0.67 | 0.33 | 0.1300 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.146, 0.199, 0.446) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 12.920 | 27.495 |
| align_1 | align | 1.00 / step_budget | (0.146, 0.199, 0.446)→(0.125, 0.172, 0.355) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 4.333 | 2.431 | 20.746 |
| contact_1 | contact | 1.00 / force_exceeded | (0.125, 0.172, 0.355)→(0.163, 0.176, 0.350) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 16.085 | 19.369 |
| push_1 | push | 0.67 / step_budget | (0.154, 0.266, 0.348)→(0.106, 0.386, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.667 | 0.000 | 91.865 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.772
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.866
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.866
- **Median Q (composite search score)**: 0.456
- **K-run variance**: 0.0509
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.336


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7dec7b9d265217827596e50fcdf4f13e307fabe21fe4cab198e2a5d141ff1ba8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2703841599a88ffb6fe3c9276875d1c87ae4a75b7467b1c48183ebe23e97d755`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29358,"average_solve_count":218.0,"average_success_count":218.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00086,"align_1.lateral_offset_y":-0.00858,"approach_1.speed":0.04577,"contact_1.contact_force_threshold":24.79882,"contact_1.contact_push_dist":0.09116,"push_1.push_distance":0.19535,"push_1.push_speed":0.06574},"optimized_scores":{"best_composite_score":0.61189,"best_fitness_score":0.77189,"best_task_score":0.77189},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.21543,0.10341,0.39079],"force_p95":28.26542,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.26542,"mean_force":28.26542,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.18318,0.17825,0.34843]},{"body_a":"door_panel","body_b":"link7","contact_count":198.0,"contact_point_centroid":[0.18704,0.10328,0.39398],"force_p95":22.78229,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.71813,"mean_force":14.07705,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.15196,0.17471,0.35084]},{"body_a":"door_panel","body_b":"link7","contact_count":97.0,"contact_point_centroid":[0.1755,0.14724,0.4802],"force_p95":25.0959,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.45761,"mean_force":18.24619,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.14055,0.22136,0.44275]},{"body_a":"door_panel","body_b":"link6","contact_count":147.0,"contact_point_centroid":[0.10056,0.19748,0.54335],"force_p95":22.20303,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.49339,"mean_force":16.17918,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12721,0.2792,0.42636]},{"body_a":"door_panel","body_b":"link7","contact_count":143.0,"contact_point_centroid":[0.16819,0.113,0.43985],"force_p95":17.97165,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.79799,"mean_force":13.54414,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.1334,0.18489,0.39812]},{"body_a":"world","body_b":"door_panel","contact_count":600.0,"contact_point_centroid":[0.30088,0.19204,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12057,0.30847,0.4069]},{"body_a":"world","body_b":"door_panel","contact_count":612.0,"contact_point_centroid":[0.309,0.13988,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13429,0.1859,0.40161]},{"body_a":"world","body_b":"door_panel","contact_count":444.0,"contact_point_centroid":[0.31195,0.13123,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.15209,0.17474,0.35084]},{"body_a":"world","body_b":"door_panel","contact_count":464.0,"contact_point_centroid":[0.31366,0.12666,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.14439,0.26872,0.34725]}],"total_contact_groups":9},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10697,0.357,0.34743],"hinge_angle":0.32126,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":28.26542,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":8.00954,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":844.0,"raw_peak_contact_force":26.45761,"subtask_id":"reach_door","tcp_end":[0.14578,0.19896,0.4462],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":568.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":755.0,"raw_peak_contact_force":20.79799,"subtask_id":"reach_door","tcp_end":[0.12209,0.17221,0.35467],"tcp_start":[0.14578,0.19896,0.4462],"tcp_to_object_dist_end":0.41273,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":519.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":26.40681,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":642.0,"raw_peak_contact_force":26.71813,"subtask_id":"push_door","tcp_end":[0.18318,0.17825,0.34843],"tcp_start":[0.12209,0.17221,0.35467],"tcp_to_object_dist_end":0.43212,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":465.0,"raw_peak_contact_force":28.26542,"subtask_id":"push_door","tcp_end":[0.10697,0.357,0.34743],"tcp_start":[0.18318,0.17825,0.34843],"tcp_to_object_dist_end":0.50951,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0106e02cd8847cdbc8cb80732350ffe717d1fc22c509bf8221b103cb157c8e2d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05019,"average_solve_count":259.0,"average_success_count":259.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00269,"align_1.lateral_offset_y":-0.00745,"approach_1.speed":0.03746,"contact_1.contact_force_threshold":17.95976,"contact_1.contact_push_dist":0.07967,"push_1.push_distance":0.2004,"push_1.push_speed":0.0452},"optimized_scores":{"best_composite_score":0.45604,"best_fitness_score":0.86604,"best_task_score":0.86604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":162.0,"contact_point_centroid":[0.10065,0.20078,0.54188],"force_p95":22.33484,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.02931,"mean_force":16.36529,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12638,0.28273,0.42478]},{"body_a":"door_panel","body_b":"link7","contact_count":99.0,"contact_point_centroid":[0.1755,0.14714,0.48021],"force_p95":24.51096,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.18583,"mean_force":18.10264,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.14056,0.22126,0.44276]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.20788,0.10471,0.3916],"force_p95":24.13945,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.13945,"mean_force":24.13945,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.17419,0.17839,0.34834]},{"body_a":"door_panel","body_b":"link7","contact_count":216.0,"contact_point_centroid":[0.18367,0.10432,0.39388],"force_p95":16.87354,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.43427,"mean_force":12.90997,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.14814,0.17529,0.35086]},{"body_a":"door_panel","body_b":"link7","contact_count":142.0,"contact_point_centroid":[0.16898,0.11331,0.43946],"force_p95":16.51295,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.51248,"mean_force":13.48074,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13422,0.18526,0.39781]},{"body_a":"world","body_b":"door_panel","contact_count":556.0,"contact_point_centroid":[0.3009,0.19284,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12153,0.30415,0.40941]},{"body_a":"world","body_b":"door_panel","contact_count":596.0,"contact_point_centroid":[0.30901,0.13986,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13485,0.18599,0.40047]},{"body_a":"world","body_b":"door_panel","contact_count":596.0,"contact_point_centroid":[0.31154,0.13235,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.14868,0.17537,0.35082]},{"body_a":"world","body_b":"door_panel","contact_count":504.0,"contact_point_centroid":[0.31279,0.12891,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.14013,0.26953,0.34723]}],"total_contact_groups":9},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10611,0.36164,0.34741],"hinge_angle":0.30917,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":27.02931,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.22925,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":817.0,"raw_peak_contact_force":27.02931,"subtask_id":"reach_door","tcp_end":[0.14582,0.19879,0.44621],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":564.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.29447,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":738.0,"raw_peak_contact_force":20.51248,"subtask_id":"reach_door","tcp_end":[0.1238,0.17327,0.35473],"tcp_start":[0.14582,0.19879,0.44621],"tcp_to_object_dist_end":0.41374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":525.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.8921,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":812.0,"raw_peak_contact_force":23.43427,"subtask_id":"push_door","tcp_end":[0.17419,0.17839,0.34834],"tcp_start":[0.1238,0.17327,0.35473],"tcp_to_object_dist_end":0.42838,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":505.0,"raw_peak_contact_force":24.13945,"subtask_id":"push_door","tcp_end":[0.10611,0.36164,0.34741],"tcp_start":[0.17419,0.17839,0.34834],"tcp_to_object_dist_end":0.51258,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7bc2b9dece282a8a9fabbafdd09525b72694e2e86202e4d7347d50b4ed50bf95`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01778,"average_solve_count":225.0,"average_success_count":225.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00873,"align_1.lateral_offset_y":-0.00983,"approach_1.speed":0.05723,"contact_1.contact_force_threshold":6.78418,"contact_1.contact_push_dist":0.04668,"push_1.push_distance":0.31606,"push_1.push_speed":0.03735},"optimized_scores":{"best_composite_score":0.07492,"best_fitness_score":0.23492,"best_task_score":0.23492},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link4","contact_count":3.0,"contact_point_centroid":[0.11564,0.09035,0.64824],"force_p95":201.24171,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":223.18939,"mean_force":75.634,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.10449,0.43973,0.34789]},{"body_a":"door_panel","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.17601,0.13738,0.48195],"force_p95":27.39893,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.99875,"mean_force":18.43776,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.14278,0.21221,0.4446]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.16813,0.10246,0.39812],"force_p95":22.80945,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.80945,"mean_force":22.80945,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.13055,0.17137,0.35368]},{"body_a":"door_panel","body_b":"link7","contact_count":163.0,"contact_point_centroid":[0.17119,0.11162,0.4382],"force_p95":17.40103,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.92703,"mean_force":13.85061,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13692,0.18391,0.39669]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.16804,0.10244,0.39819],"force_p95":7.87976,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.95527,"mean_force":7.20015,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.13046,0.17134,0.35375]},{"body_a":"world","body_b":"door_panel","contact_count":600.0,"contact_point_centroid":[0.30406,0.15878,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.12002,0.31123,0.40453]},{"body_a":"world","body_b":"door_panel","contact_count":488.0,"contact_point_centroid":[0.30934,0.13884,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.13764,0.18514,0.40076]},{"body_a":"world","body_b":"door_panel","contact_count":32.0,"contact_point_centroid":[0.31093,0.13402,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.12974,0.17113,0.35431]},{"body_a":"world","body_b":"door_panel","contact_count":780.0,"contact_point_centroid":[0.31071,0.13465,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.11744,0.30598,0.3502]}],"total_contact_groups":9},"final_pose_error":0.05631,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10442,0.43997,0.34774],"hinge_angle":0.27775,"initial_hinge_angle":0.15466,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.15466,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":223.18939,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":578.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.52089,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":657.0,"raw_peak_contact_force":28.99875,"subtask_id":"reach_door","tcp_end":[0.14581,0.19907,0.44631],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50999,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":563.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":651.0,"raw_peak_contact_force":20.92703,"subtask_id":"reach_door","tcp_end":[0.1294,0.17111,0.35476],"tcp_start":[0.14581,0.19907,0.44631],"tcp_to_object_dist_end":0.41458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":21.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.95527,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":34.0,"raw_peak_contact_force":7.95527,"subtask_id":"push_door","tcp_end":[0.13055,0.17137,0.35368],"tcp_start":[0.1294,0.17111,0.35476],"tcp_to_object_dist_end":0.41413,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":721.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":784.0,"raw_peak_contact_force":223.18939,"subtask_id":"push_door","tcp_end":[0.10442,0.43997,0.34774],"tcp_start":[0.10445,0.43994,0.34783],"tcp_to_object_dist_end":0.57044,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```