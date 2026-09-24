## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `c110175cdc23a481ee4f5a8b0b433c8e6c91b615df874546135cb56aaa5a8af6`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.4668519333714893, -0.021055159472312023, 0.08]
- Frozen socket pose: [0.4668519333714893, -0.021055159472312023, 0.025] (static fixture for this episode)
- Goal object position: (0.4668519333714893, -0.021055159472312023, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.4669, -0.0211, 0.08]
  frozen_socket_position: [0.4669, -0.0211, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.4668519333714893, -0.021055159472312023, 0.08]}
  frozen_fixtures: {'peg_socket': [0.4668519333714893, -0.021055159472312023, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: c110175cdc23a481ee4f5a8b0b433c8e6c91b615df874546135cb56aaa5a8af6

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.956, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.4668519333714893, -0.021055159472312023, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.4668519333714893, -0.021055159472312023, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.386) — your mutation base

```yaml
skill: peg_insert
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: position_control
  termination: pose_tolerance
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2

```

## Design Metrics

- **Composite score**: 0.386
- **task_score** (E): 0.866
- **fitness_score**: 0.866  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_socket | 0.00 | 1.00 | 0.1444 |
| descend_into_hole | 0.00 | 1.00 | 0.0542 |
| retract_finish | 0.67 | 0.33 | 0.0434 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_socket | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.462, 0.013, 0.162) | (0.504, -0.000, 0.340)→(0.499, 0.011, 0.149) | 0.260→0.071 | 1.00 / 1.000 | 266.067 | 1053.157 |
| descend_into_hole | descend | 0.00 / step_budget | (0.462, 0.013, 0.162)→(0.470, 0.062, 0.174) | (0.499, 0.011, 0.149)→(0.503, 0.050, 0.157) | 0.071→0.095 | 1.00 / 1.333 | 290.858 | 360.362 |
| retract_finish | retract | 0.67 / step_budget | (0.470, 0.062, 0.174)→(0.467, 0.063, 0.217) | (0.503, 0.050, 0.157)→(0.501, 0.052, 0.200) | 0.095→0.132 | 0.33 / 0.333 | 28.062 | 209.182 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.925
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.925
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.925
- **Median Q (composite search score)**: 0.368
- **K-run variance**: 0.0018
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.287


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fc05e51a25fc23cdfa051e1c0c9cb8327fc4318047dd2c0794162fe696d964b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `78de15924f40c9df864f10a8c33fe438e6928bbf6063e6b2cf47f87609839b79`; realized-scene SHA-256: `c110175cdc23a481ee4f5a8b0b433c8e6c91b615df874546135cb56aaa5a8af6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.15152,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_height":0.06857,"approach_socket.arc_height":0.11604,"approach_socket.speed":0.04069,"approach_socket.tolerance":0.02016,"descend_into_hole.descend_speed":0.00746,"descend_into_hole.insertion_depth":0.07024,"descend_into_hole.tolerance":0.00909,"retract_finish.retract_height":0.06003,"retract_finish.speed":0.02289},"optimized_scores":{"best_composite_score":0.34557,"best_fitness_score":0.82557,"best_task_score":0.82557},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.44779,0.00926,0.07916],"force_p95":963.91013,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":985.81547,"mean_force":638.82455,"phase_index":0.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.44368,0.00397,0.09154]},{"body_a":"peg_socket","body_b":"link7","contact_count":905.0,"contact_point_centroid":[0.52673,0.00105,0.07992],"force_p95":310.04671,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":624.68276,"mean_force":293.93113,"phase_index":0.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.45341,0.0014,0.12934]},{"body_a":"peg_socket","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.52676,-0.00052,0.07998],"force_p95":370.59357,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":436.8395,"mean_force":356.23254,"phase_index":1.0,"phase_name":"descend_into_hole","phase_type":"descend","tcp_position_centroid":[0.4683,0.0069,0.14582]},{"body_a":"world","body_b":"link6","contact_count":664.0,"contact_point_centroid":[0.66946,0.00182,-2e-05],"force_p95":62.99173,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":383.07411,"mean_force":35.31379,"phase_index":1.0,"phase_name":"descend_into_hole","phase_type":"descend","tcp_position_centroid":[0.46904,0.00706,0.14658]},{"body_a":"peg_socket","body_b":"link7","contact_count":977.0,"contact_point_centroid":[0.52682,-9e-05,0.07999],"force_p95":124.8262,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":226.99956,"mean_force":97.68192,"phase_index":2.0,"phase_name":"retract_finish","phase_type":"retract","tcp_position_centroid":[0.46671,0.0104,0.14766]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.66964,0.00018,-1e-05],"force_p95":83.05859,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.87336,"mean_force":34.33487,"phase_index":2.0,"phase_name":"retract_finish","phase_type":"retract","tcp_position_centroid":[0.46915,0.0096,0.1463]}],"total_contact_groups":6},"final_pose_error":0.0508,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46498,0.01132,0.15573],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":985.81547,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49715,0.00406,0.12392],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0442,"object_to_goal_dist_start":0.26034,"object_z_max":0.34426,"peak_contact_force":309.78475,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":912.0,"raw_peak_contact_force":985.81547,"subtask_id":"approach_socket","tcp_end":[0.45914,0.0044,0.13638],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50464,0.00744,0.12798],"object_pos_start":[0.49715,0.00406,0.12392],"object_to_goal_dist_end":0.04877,"object_to_goal_dist_start":0.0442,"object_z_max":0.12846,"peak_contact_force":357.07336,"phase_name":"descend_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1664.0,"raw_peak_contact_force":436.8395,"subtask_id":"insertion_goal","tcp_end":[0.46915,0.0096,0.1463],"tcp_start":[0.45914,0.0044,0.13638],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50102,0.00911,0.13851],"object_pos_start":[0.50464,0.00744,0.12798],"object_to_goal_dist_end":0.05923,"object_to_goal_dist_start":0.04877,"object_z_max":0.13847,"peak_contact_force":84.18572,"phase_name":"retract_finish","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":982.0,"raw_peak_contact_force":226.99956,"tcp_end":[0.46498,0.01132,0.15573],"tcp_start":[0.46915,0.0096,0.1463],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `23bedb35dfb8044c9064b13b9f8101cd4e2be35581b8354b6b999b22e5fca070`; realized-scene SHA-256: `6aa6006ba5d7c7f83773c59f42ad1597db3f9073c3225635eb35deca1cb0f02a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.10063,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_height":0.10253,"approach_socket.arc_height":0.03737,"approach_socket.speed":0.02368,"approach_socket.tolerance":0.01226,"descend_into_hole.descend_speed":0.01298,"descend_into_hole.insertion_depth":0.06025,"descend_into_hole.tolerance":0.0049,"retract_finish.retract_height":0.05602,"retract_finish.speed":0.01989},"optimized_scores":{"best_composite_score":0.44466,"best_fitness_score":0.92466,"best_task_score":0.92466},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.48628,0.00068,0.07855],"force_p95":1025.64978,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1079.5286,"mean_force":171.75798,"phase_index":0.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.48211,0.00068,0.09149]},{"body_a":"peg_socket","body_b":"link7","contact_count":172.0,"contact_point_centroid":[0.591,0.00329,0.07932],"force_p95":459.48208,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":962.36014,"mean_force":259.64637,"phase_index":0.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.47445,0.00096,0.13535]},{"body_a":"peg_socket","body_b":"link6","contact_count":735.0,"contact_point_centroid":[0.59542,-0.00034,0.07992],"force_p95":263.25073,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":726.30495,"mean_force":242.68981,"phase_index":0.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.47121,0.00288,0.16375]},{"body_a":"peg_socket","body_b":"link6","contact_count":991.0,"contact_point_centroid":[0.59541,0.00668,0.07991],"force_p95":288.56528,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":325.14275,"mean_force":243.07306,"phase_index":1.0,"phase_name":"descend_into_hole","phase_type":"descend","tcp_position_centroid":[0.46322,0.04338,0.17186]},{"body_a":"peg_socket","body_b":"link6","contact_count":9.0,"contact_point_centroid":[0.59542,0.00334,0.07997],"force_p95":217.65457,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.09018,"mean_force":97.30802,"phase_index":2.0,"phase_name":"retract_finish","phase_type":"retract","tcp_position_centroid":[0.48941,0.09435,0.19403]}],"total_contact_groups":5},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.48784,0.0943,0.23997],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1079.5286,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50944,0.00606,0.15826],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07906,"object_to_goal_dist_start":0.26034,"object_z_max":0.3463,"peak_contact_force":242.83338,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":919.0,"raw_peak_contact_force":1079.5286,"subtask_id":"approach_socket","tcp_end":[0.4719,0.00786,0.17196],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51887,0.07378,0.17627],"object_pos_start":[0.50944,0.00606,0.15826],"object_to_goal_dist_end":0.12275,"object_to_goal_dist_start":0.07906,"object_z_max":0.17624,"peak_contact_force":276.19978,"phase_name":"descend_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":991.0,"raw_peak_contact_force":325.14275,"subtask_id":"insertion_goal","tcp_end":[0.48923,0.09412,0.19382],"tcp_start":[0.4719,0.00786,0.17196],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":615.0,"n_steps_budget":1000.0,"object_pos_end":[0.51786,0.07595,0.22094],"object_pos_start":[0.51887,0.07378,0.17627],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.12275,"object_z_max":0.22087,"peak_contact_force":0.0,"phase_name":"retract_finish","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":9.0,"raw_peak_contact_force":225.09018,"tcp_end":[0.48784,0.0943,0.23997],"tcp_start":[0.48923,0.09412,0.19382],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0b9f57c3f8a8fdb0f6fef54a4b5c0cfa6a2779a7721b018896a4efe993ac60cd`; realized-scene SHA-256: `68ad8ffad13ff17e4e79d7c12ed07a79b854360d1380b55b4d752be6df0d8737`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.98485,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_height":0.10816,"approach_socket.arc_height":0.07478,"approach_socket.speed":0.04054,"approach_socket.tolerance":0.00797,"descend_into_hole.descend_speed":0.01281,"descend_into_hole.insertion_depth":0.07998,"descend_into_hole.tolerance":0.01498,"retract_finish.retract_height":0.08331,"retract_finish.speed":0.03251},"optimized_scores":{"best_composite_score":0.36752,"best_fitness_score":0.84752,"best_task_score":0.84752},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.56154,0.01199,0.07836],"force_p95":360.48231,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1094.12563,"mean_force":214.25145,"phase_index":0.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.44976,0.01069,0.11114]},{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.46472,0.00985,0.07948],"force_p95":647.2569,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":924.65272,"mean_force":132.09325,"phase_index":0.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.45522,0.00984,0.0918]},{"body_a":"peg_socket","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.54749,-0.0057,0.07789],"force_p95":404.41316,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":548.07196,"mean_force":107.55367,"phase_index":0.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.45088,0.01017,0.10043]},{"body_a":"peg_socket","body_b":"link6","contact_count":718.0,"contact_point_centroid":[0.58438,0.01558,0.07989],"force_p95":260.79403,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":485.6407,"mean_force":243.5839,"phase_index":0.0,"phase_name":"approach_socket","phase_type":"approach","tcp_position_centroid":[0.44967,0.0184,0.16409]},{"body_a":"peg_socket","body_b":"link6","contact_count":997.0,"contact_point_centroid":[0.58438,0.02569,0.07993],"force_p95":260.94214,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":319.10297,"mean_force":233.31884,"phase_index":1.0,"phase_name":"descend_into_hole","phase_type":"descend","tcp_position_centroid":[0.44055,0.05406,0.17208]},{"body_a":"peg_socket","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.5844,0.02228,0.07999],"force_p95":155.59761,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":175.45533,"mean_force":89.42326,"phase_index":2.0,"phase_name":"retract_finish","phase_type":"retract","tcp_position_centroid":[0.45027,0.08223,0.18125]}],"total_contact_groups":6},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.44874,0.0824,0.25465],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1094.12563,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.49099,0.02432,0.16441],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0883,"object_to_goal_dist_start":0.26034,"object_z_max":0.34487,"peak_contact_force":245.58147,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":792.0,"raw_peak_contact_force":1094.12563,"subtask_id":"approach_socket","tcp_end":[0.45383,0.02556,0.17916],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48532,0.06923,0.16709],"object_pos_start":[0.49099,0.02432,0.16441],"object_to_goal_dist_end":0.11222,"object_to_goal_dist_start":0.0883,"object_z_max":0.16707,"peak_contact_force":239.30039,"phase_name":"descend_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":997.0,"raw_peak_contact_force":319.10297,"subtask_id":"insertion_goal","tcp_end":[0.45027,0.08236,0.18121],"tcp_start":[0.45383,0.02556,0.17916],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.48397,0.07155,0.23912],"object_pos_start":[0.48532,0.06923,0.16709],"object_to_goal_dist_end":0.1752,"object_to_goal_dist_start":0.11222,"object_z_max":0.23903,"peak_contact_force":0.0,"phase_name":"retract_finish","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":5.0,"raw_peak_contact_force":175.45533,"tcp_end":[0.44874,0.0824,0.25465],"tcp_start":[0.45027,0.08236,0.18121],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```