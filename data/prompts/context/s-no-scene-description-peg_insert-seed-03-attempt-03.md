## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → align → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4406 | 0.85 | ❌ rejected |
| 2 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7616 | 0.97 | ✅ accepted |
| 1 | approach → align → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4537 | 0.91 | ❌ rejected |
| 0 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7464 | 0.96 | ✅ accepted |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.441) — your mutation base

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

- **Composite score**: 0.441
- **task_score** (E): 0.851
- **fitness_score**: 0.501  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.1395 |
| align_1 | 0.33 | 1.00 | 0.0367 |
| descend_1 | 1.00 | 1.00 | 0.0003 |
| insert_1 | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.472, 0.001, 0.165) | (0.504, -0.000, 0.340)→(0.508, 0.003, 0.149) | 0.260→0.072 | 1.00 / 1.000 | 650.135 | 1596.358 |
| align_1 | align | 0.33 / step_budget | (0.472, 0.001, 0.165)→(0.487, 0.029, 0.164) | (0.508, 0.003, 0.149)→(0.522, 0.025, 0.146) | 0.072→0.076 | 1.00 / 1.333 | 314.561 | 946.271 |
| descend_1 | descend | 1.00 / force_exceeded | (0.487, 0.029, 0.164)→(0.487, 0.029, 0.164) | (0.522, 0.025, 0.146)→(0.522, 0.025, 0.146) | 0.076→0.076 | 1.00 / 1.333 | 385.503 | 385.503 |
| insert_1 | push | 0.00 / guard_failure | (0.487, 0.029, 0.164)→(0.487, 0.029, 0.164) | (0.522, 0.025, 0.146)→(0.522, 0.025, 0.146) | 0.076→0.076 | 1.00 / 1.333 | 356.792 | 356.792 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.861
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.861
- phase_score: 0.304
- phase_breakdown.approach_goal_score: 0.768
- phase_breakdown.insert_goal_score: 0.105

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.527
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.861
- **Median Q (composite search score)**: 0.452
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.337


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.03448,"average_solve_count":58.0,"average_success_count":58.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_z":0.02274,"approach_1.approach_height":0.05114,"descend_1.descend_depth":0.09228,"descend_1.force_limit":39.17099,"insert_1.insert_depth":0.09336},"optimized_scores":{"best_composite_score":0.45154,"best_fitness_score":0.51154,"best_task_score":0.83608},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":7.0,"contact_point_centroid":[0.44964,0.00944,0.07921],"force_p95":925.26773,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":942.065,"mean_force":599.923,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44603,0.0013,0.08995]},{"body_a":"peg_socket","body_b":"link7","contact_count":905.0,"contact_point_centroid":[0.52671,-0.00573,0.07789],"force_p95":369.82016,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":707.5761,"mean_force":332.31548,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46095,-0.0039,0.13199]},{"body_a":"peg_socket","body_b":"link7","contact_count":455.0,"contact_point_centroid":[0.52676,-0.00897,0.07499],"force_p95":356.28782,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":385.59744,"mean_force":339.5917,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46639,-0.00096,0.13557]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52677,-0.0109,0.07428],"force_p95":352.6163,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":352.6163,"mean_force":352.6163,"phase_index":3.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46634,-0.00017,0.13441]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52677,-0.01094,0.07429],"force_p95":277.06393,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.06393,"mean_force":277.06393,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46635,-0.00021,0.13442]},{"body_a":"world","body_b":"link6","contact_count":276.0,"contact_point_centroid":[0.67425,-0.01024,-0.0],"force_p95":73.03558,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":160.4562,"mean_force":47.02059,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4664,-0.001,0.13564]},{"body_a":"world","body_b":"link6","contact_count":216.0,"contact_point_centroid":[0.67343,-0.00397,-2e-05],"force_p95":92.59186,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":158.11218,"mean_force":47.83091,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46667,-0.00252,0.1376]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67466,-0.01539,-0.0],"force_p95":108.64725,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.64725,"mean_force":108.64725,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46635,-0.00021,0.13442]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.67466,-0.01535,-0.0],"force_p95":38.69487,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":38.69487,"mean_force":38.69487,"phase_index":3.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.46634,-0.00017,0.13441]}],"total_contact_groups":9},"final_pose_error":0.14924,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46634,-9e-05,0.13439],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":942.065,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50294,-0.00398,0.12016],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04046,"object_to_goal_dist_start":0.26034,"object_z_max":0.34435,"peak_contact_force":367.50906,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1128.0,"raw_peak_contact_force":942.065,"subtask_id":"approach_goal","tcp_end":[0.46657,-0.00298,0.13678],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50278,-0.00331,0.1182],"object_pos_start":[0.50294,-0.00398,0.12016],"object_to_goal_dist_end":0.03844,"object_to_goal_dist_start":0.04046,"object_z_max":0.12016,"peak_contact_force":320.41383,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":731.0,"raw_peak_contact_force":385.59744,"tcp_end":[0.46635,-0.00021,0.13442],"tcp_start":[0.46657,-0.00298,0.13678],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50278,-0.00327,0.11819],"object_pos_start":[0.50278,-0.00331,0.1182],"object_to_goal_dist_end":0.03843,"object_to_goal_dist_start":0.03844,"object_z_max":0.1182,"peak_contact_force":277.06393,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":277.06393,"tcp_end":[0.46634,-0.00017,0.13441],"tcp_start":[0.46635,-0.00021,0.13442],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":930.0,"object_pos_end":[0.50277,-0.00318,0.11818],"object_pos_start":[0.50278,-0.00327,0.11819],"object_to_goal_dist_end":0.03841,"object_to_goal_dist_start":0.03843,"object_z_max":0.11819,"peak_contact_force":352.6163,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":352.6163,"subtask_id":"insert_goal","tcp_end":[0.46634,-9e-05,0.13439],"tcp_start":[0.46634,-0.00017,0.13441],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `23bedb35dfb8044c9064b13b9f8101cd4e2be35581b8354b6b999b22e5fca070`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":8.67308,"average_solve_count":52.0,"average_success_count":52.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_z":0.07729,"approach_1.approach_height":0.08334,"descend_1.descend_depth":0.02786,"descend_1.force_limit":11.14151,"insert_1.insert_depth":0.10487},"optimized_scores":{"best_composite_score":0.46694,"best_fitness_score":0.52694,"best_task_score":0.86119},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.58238,-0.02297,0.07936],"force_p95":407.89998,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1641.71162,"mean_force":311.37254,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49648,0.01443,0.18137]},{"body_a":"peg_socket","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.569,0.00692,0.07917],"force_p95":963.29645,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1331.42122,"mean_force":267.86494,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44921,0.00589,0.11039]},{"body_a":"peg_socket","body_b":"link6","contact_count":660.0,"contact_point_centroid":[0.59519,0.00737,0.07984],"force_p95":307.78702,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":864.87904,"mean_force":250.2069,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46391,0.0101,0.17255]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.47554,0.00605,0.07975],"force_p95":843.46929,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":846.26566,"mean_force":418.4722,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45906,0.00597,0.08959]},{"body_a":"peg_socket","body_b":"link6","contact_count":413.0,"contact_point_centroid":[0.59528,-0.00113,0.07972],"force_p95":389.70055,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":696.94461,"mean_force":287.02664,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.483,0.01407,0.19664]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.59542,0.03017,0.0799],"force_p95":413.03239,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":413.03239,"mean_force":413.03239,"phase_index":3.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.50158,0.055,0.178]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.59542,0.03014,0.07988],"force_p95":402.58938,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":402.58938,"mean_force":402.58938,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50151,0.05483,0.17804]},{"body_a":"peg_socket","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.54379,0.03109,0.07974],"force_p95":17.42252,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":17.66058,"mean_force":6.69034,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4478,0.00604,0.09487]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.54465,-0.02925,0.079],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.44747,0.00611,0.09769]}],"total_contact_groups":9},"final_pose_error":0.21277,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.50164,0.05522,0.17806],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1641.71162,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.52903,-0.00693,0.16372],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08889,"object_to_goal_dist_start":0.26034,"object_z_max":0.34474,"peak_contact_force":1331.42122,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":724.0,"raw_peak_contact_force":1331.42122,"subtask_id":"approach_goal","tcp_end":[0.49353,-0.01139,0.1816],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.53601,0.04503,0.16033],"object_pos_start":[0.52903,-0.00693,0.16372],"object_to_goal_dist_end":0.09888,"object_to_goal_dist_start":0.08889,"object_z_max":0.18658,"peak_contact_force":369.7738,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":441.0,"raw_peak_contact_force":1641.71162,"tcp_end":[0.50151,0.05483,0.17804],"tcp_start":[0.49353,-0.01139,0.1816],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":990.0,"object_pos_end":[0.53609,0.0452,0.16032],"object_pos_start":[0.53601,0.04503,0.16033],"object_to_goal_dist_end":0.09898,"object_to_goal_dist_start":0.09888,"object_z_max":0.16033,"peak_contact_force":402.58938,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":402.58938,"tcp_end":[0.50158,0.055,0.178],"tcp_start":[0.50151,0.05483,0.17804],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53615,0.04541,0.16038],"object_pos_start":[0.53609,0.0452,0.16032],"object_to_goal_dist_end":0.09915,"object_to_goal_dist_start":0.09898,"object_z_max":0.16032,"peak_contact_force":413.03239,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":413.03239,"subtask_id":"insert_goal","tcp_end":[0.50164,0.05522,0.17806],"tcp_start":[0.50158,0.055,0.178],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0b9f57c3f8a8fdb0f6fef54a4b5c0cfa6a2779a7721b018896a4efe993ac60cd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":9.45455,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_z":0.05897,"approach_1.approach_height":0.15412,"descend_1.descend_depth":0.06591,"descend_1.force_limit":14.6023,"insert_1.insert_depth":0.08585},"optimized_scores":{"best_composite_score":0.40341,"best_fitness_score":0.46341,"best_task_score":0.85431},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":380.0,"contact_point_centroid":[0.58434,0.01308,0.07977],"force_p95":281.2524,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2515.58714,"mean_force":259.64333,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45347,0.01429,0.1622]},{"body_a":"peg_socket","body_b":"link7","contact_count":53.0,"contact_point_centroid":[0.56682,0.01086,0.0787],"force_p95":781.76279,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2426.58442,"mean_force":269.55832,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45248,0.00864,0.11835]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.46563,0.00725,0.0793],"force_p95":1011.96086,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1053.11759,"mean_force":321.51973,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45792,0.00725,0.09192]},{"body_a":"peg_socket","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.55073,-0.00562,0.07839],"force_p95":935.79723,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1008.3763,"mean_force":173.29066,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45405,0.00775,0.10091]},{"body_a":"peg_socket","body_b":"link6","contact_count":442.0,"contact_point_centroid":[0.58433,0.02022,0.07986],"force_p95":306.74785,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":811.50302,"mean_force":257.61393,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.46259,0.02396,0.19101]},{"body_a":"peg_socket","body_b":"link7","contact_count":32.0,"contact_point_centroid":[0.58438,0.02707,0.07996],"force_p95":496.16238,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":515.68303,"mean_force":347.8481,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49353,0.03159,0.18051]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.58436,0.03342,0.07992],"force_p95":466.83441,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":476.85518,"mean_force":376.64755,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49318,0.03111,0.1793]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58429,0.03365,0.07979],"force_p95":304.72616,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.72616,"mean_force":304.72616,"phase_index":3.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.49296,0.03099,0.179]}],"total_contact_groups":8},"final_pose_error":0.18745,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.49292,0.03081,0.17884],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":2515.58714,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49305,0.01847,0.16302],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08534,"object_to_goal_dist_start":0.26034,"object_z_max":0.34474,"peak_contact_force":251.47469,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":466.0,"raw_peak_contact_force":2515.58714,"subtask_id":"approach_goal","tcp_end":[0.4558,0.01848,0.17762],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.52843,0.03214,0.16041],"object_pos_start":[0.49305,0.01847,0.16302],"object_to_goal_dist_end":0.09115,"object_to_goal_dist_start":0.08534,"object_z_max":0.1873,"peak_contact_force":253.49535,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":474.0,"raw_peak_contact_force":811.50302,"tcp_end":[0.49329,0.03103,0.1795],"tcp_start":[0.4558,0.01848,0.17762],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.5281,0.03268,0.15997],"object_pos_start":[0.52843,0.03214,0.16041],"object_to_goal_dist_end":0.09084,"object_to_goal_dist_start":0.09115,"object_z_max":0.16041,"peak_contact_force":476.85518,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2.0,"raw_peak_contact_force":476.85518,"tcp_end":[0.49296,0.03099,0.179],"tcp_start":[0.49329,0.03103,0.1795],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52808,0.03258,0.15984],"object_pos_start":[0.5281,0.03268,0.15997],"object_to_goal_dist_end":0.09069,"object_to_goal_dist_start":0.09084,"object_z_max":0.15997,"peak_contact_force":304.72616,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":304.72616,"subtask_id":"insert_goal","tcp_end":[0.49292,0.03081,0.17884],"tcp_start":[0.49296,0.03099,0.179],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```