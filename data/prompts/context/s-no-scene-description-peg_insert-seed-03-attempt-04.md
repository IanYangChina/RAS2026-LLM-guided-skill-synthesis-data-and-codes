## Search State

- **Seed**: 3
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7614 | 0.97 | ❌ rejected |
| 3 | approach → align → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4406 | 0.85 | ❌ rejected |
| 2 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7616 | 0.97 | ✅ accepted |
| 1 | approach → align → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4537 | 0.91 | ❌ rejected |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7464 | 0.96 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.97). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

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

## Current Skill (Q=0.761) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: none
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.1
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **rotate_1** (`rotate`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=none
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.05, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **pull_1** (`pull`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.1
  - parameter_bindings:
    - pull_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)

## Design Metrics

- **Composite score**: 0.761
- **task_score** (E): 0.971
- **fitness_score**: 0.971  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 0.00 | 0.0017 |
| retract_1 | 1.00 | 0.00 | 0.0416 |
| descend_1 | 1.00 | 0.00 | 0.0721 |
| pull_1 | 1.00 | 0.67 | 0.1069 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.499, -0.000, 0.299) | (0.504, -0.000, 0.340)→(0.503, -0.000, 0.339) | 0.260→0.259 | 0.00 / 0.000 | 0.000 | 0.000 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.000, 0.299)→(0.497, 0.001, 0.341) | (0.503, -0.000, 0.339)→(0.502, 0.001, 0.380) | 0.259→0.300 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.001, 0.341)→(0.495, 0.001, 0.268) | (0.502, 0.001, 0.380)→(0.500, 0.001, 0.308) | 0.300→0.228 | 0.00 / 0.000 | 0.000 | 0.000 |
| pull_1 | pull | 1.00 / time_limit | (0.495, 0.001, 0.268)→(0.547, 0.038, 0.217) | (0.500, 0.001, 0.308)→(0.568, 0.037, 0.187) | 0.228→0.135 | 0.67 / 0.667 | 160.727 | 3992.126 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.976
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.976
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.976
- **Median Q (composite search score)**: 0.762
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.543


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fc05e51a25fc23cdfa051e1c0c9cb8327fc4318047dd2c0794162fe696d964b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `78de15924f40c9df864f10a8c33fe438e6928bbf6063e6b2cf47f87609839b79`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.63542,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.08286,"pull_1.pull_distance":0.14705,"retract_1.retract_height":0.05006},"optimized_scores":{"best_composite_score":0.76573,"best_fitness_score":0.97573,"best_task_score":0.97573},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":697.0,"contact_point_centroid":[0.52659,0.01535,0.06425],"force_p95":355.00529,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9516.92012,"mean_force":486.39904,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.4582,0.00853,0.11524]},{"body_a":"attachment","body_b":"peg_socket","contact_count":471.0,"contact_point_centroid":[0.52525,0.01017,0.07969],"force_p95":1200.88724,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":7903.28809,"mean_force":395.85961,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.46308,0.0083,0.11567]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.49682,0.00897,0.07967],"force_p95":1845.64408,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1857.04675,"mean_force":1329.53008,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.44128,0.00709,0.10045]},{"body_a":"world","body_b":"link6","contact_count":466.0,"contact_point_centroid":[0.67797,0.01603,-8e-05],"force_p95":260.1295,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":913.31241,"mean_force":119.48775,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.46383,0.01279,0.12511]},{"body_a":"peg_socket","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.5259,0.01089,0.04946],"force_p95":106.10689,"geom_a":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.31145,"mean_force":58.03743,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.44155,0.0076,0.10196]}],"total_contact_groups":5},"final_pose_error":0.22402,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.47493,0.02788,0.1514],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":9516.92012,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50343,-0.0,0.33877],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25879,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49918,-1e-05,0.299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":405.0,"n_steps_budget":600.0,"object_pos_end":[0.50213,0.00148,0.37908],"object_pos_start":[0.50343,-0.0,0.33877],"object_to_goal_dist_end":0.29909,"object_to_goal_dist_start":0.25879,"object_z_max":0.379,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49743,0.00147,0.33936],"tcp_start":[0.49918,-1e-05,0.299],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":229.0,"n_steps_budget":600.0,"object_pos_end":[0.5004,0.00146,0.30583],"object_pos_start":[0.50213,0.00148,0.37908],"object_to_goal_dist_end":0.22583,"object_to_goal_dist_start":0.29909,"object_z_max":0.37912,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49525,0.00144,0.26616],"tcp_start":[0.49743,0.00147,0.33936],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50998,0.02702,0.13215],"object_pos_start":[0.5004,0.00146,0.30583],"object_to_goal_dist_end":0.05958,"object_to_goal_dist_start":0.22583,"object_z_max":0.30583,"peak_contact_force":211.96661,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":1658.0,"raw_peak_contact_force":9516.92012,"tcp_end":[0.47493,0.02788,0.1514],"tcp_start":[0.49525,0.00144,0.26616],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `23bedb35dfb8044c9064b13b9f8101cd4e2be35581b8354b6b999b22e5fca070`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.51546,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.07906,"pull_1.pull_distance":0.08827,"retract_1.retract_height":0.05021},"optimized_scores":{"best_composite_score":0.76199,"best_fitness_score":0.97199,"best_task_score":0.97199},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":780.0,"contact_point_centroid":[0.59528,0.01718,0.07983],"force_p95":375.16679,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1421.64079,"mean_force":264.987,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.50666,0.01124,0.10652]},{"body_a":"attachment","body_b":"peg_socket","contact_count":37.0,"contact_point_centroid":[0.50225,0.02052,0.07825],"force_p95":1037.47645,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1152.46746,"mean_force":407.76067,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49778,0.00601,0.07945]},{"body_a":"peg_socket","body_b":"link6","contact_count":23.0,"contact_point_centroid":[0.5951,0.06017,0.07968],"force_p95":362.34859,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":624.14717,"mean_force":261.78425,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.56036,-0.01753,0.19824]},{"body_a":"world","body_b":"link6","contact_count":15.0,"contact_point_centroid":[0.64095,0.12516,-0.00085],"force_p95":454.45245,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":464.72942,"mean_force":184.39039,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.57753,0.00678,0.22049]},{"body_a":"world","body_b":"link5","contact_count":37.0,"contact_point_centroid":[0.52602,0.13901,-0.00014],"force_p95":396.89281,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":412.70955,"mean_force":324.28089,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.57709,0.03546,0.24258]}],"total_contact_groups":5},"final_pose_error":0.27077,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.57238,0.05187,0.25508],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1421.64079,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50343,-0.0,0.33877],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25879,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49918,-1e-05,0.299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":405.0,"n_steps_budget":600.0,"object_pos_end":[0.50213,0.00149,0.37922],"object_pos_start":[0.50343,-0.0,0.33877],"object_to_goal_dist_end":0.29923,"object_to_goal_dist_start":0.25879,"object_z_max":0.37913,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49743,0.00147,0.33949],"tcp_start":[0.49918,-1e-05,0.299],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":219.0,"n_steps_budget":600.0,"object_pos_end":[0.50045,0.00147,0.30964],"object_pos_start":[0.50213,0.00149,0.37922],"object_to_goal_dist_end":0.22964,"object_to_goal_dist_start":0.29923,"object_z_max":0.37926,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.4953,0.00144,0.26997],"tcp_start":[0.49743,0.00147,0.33949],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5841,0.06478,0.21908],"object_pos_start":[0.50045,0.00147,0.30964],"object_to_goal_dist_end":0.17497,"object_to_goal_dist_start":0.22964,"object_z_max":0.30964,"peak_contact_force":0.0,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":892.0,"raw_peak_contact_force":1421.64079,"tcp_end":[0.57238,0.05187,0.25508],"tcp_start":[0.4953,0.00144,0.26997],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0b9f57c3f8a8fdb0f6fef54a4b5c0cfa6a2779a7721b018896a4efe993ac60cd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.54167,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.08326,"pull_1.pull_distance":0.1012,"retract_1.retract_height":0.05347},"optimized_scores":{"best_composite_score":0.75656,"best_fitness_score":0.96656,"best_task_score":0.96656},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":25.0,"contact_point_centroid":[0.49185,0.01082,0.07864],"force_p95":917.63524,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1037.81799,"mean_force":370.95804,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49024,0.01254,0.07569]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.50019,-0.00608,0.0793],"force_p95":906.59211,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":946.09421,"mean_force":644.0707,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49837,0.0076,0.08138]},{"body_a":"peg_socket","body_b":"link6","contact_count":32.0,"contact_point_centroid":[0.58349,-0.03469,0.07954],"force_p95":829.03755,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":863.68153,"mean_force":417.32881,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.59191,0.05373,0.23247]},{"body_a":"peg_socket","body_b":"link7","contact_count":814.0,"contact_point_centroid":[0.58421,0.01929,0.07983],"force_p95":378.51461,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":793.17634,"mean_force":267.0263,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.49766,0.01661,0.11104]},{"body_a":"world","body_b":"link6","contact_count":30.0,"contact_point_centroid":[0.6705,-0.04912,-0.0009],"force_p95":481.99921,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":497.6361,"mean_force":313.50721,"phase_index":3.0,"phase_name":"pull_1","phase_type":"pull","tcp_position_centroid":[0.57443,0.07059,0.20452]}],"total_contact_groups":5},"final_pose_error":0.27457,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.59495,0.03433,0.24397],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1037.81799,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50343,-0.0,0.33877],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25879,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49918,-1e-05,0.299],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":440.0,"n_steps_budget":600.0,"object_pos_end":[0.50213,0.00149,0.38253],"object_pos_start":[0.50343,-0.0,0.33877],"object_to_goal_dist_end":0.30254,"object_to_goal_dist_start":0.25879,"object_z_max":0.38244,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49743,0.00148,0.3428],"tcp_start":[0.49918,-1e-05,0.299],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":230.0,"n_steps_budget":600.0,"object_pos_end":[0.50043,0.00147,0.30892],"object_pos_start":[0.50213,0.00149,0.38253],"object_to_goal_dist_end":0.22893,"object_to_goal_dist_start":0.30254,"object_z_max":0.38257,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49527,0.00145,0.26926],"tcp_start":[0.49743,0.00148,0.3428],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60888,0.01972,0.20944],"object_pos_start":[0.50043,0.00147,0.30892],"object_to_goal_dist_end":0.17029,"object_to_goal_dist_start":0.22893,"object_z_max":0.30892,"peak_contact_force":270.21576,"phase_name":"pull_1","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":905.0,"raw_peak_contact_force":1037.81799,"tcp_end":[0.59495,0.03433,0.24397],"tcp_start":[0.49527,0.00145,0.26926],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```