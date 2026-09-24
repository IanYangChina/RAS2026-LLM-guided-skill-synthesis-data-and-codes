## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 7 | 0.3764 | 0.84 | ❌ rejected |
| 10 | approach → descend → pull | linear_cartesian | linear_cartesian | arc_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 3 | 0.6763 | 0.86 | ❌ rejected |
| 9 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7628 | 0.97 | ✅ accepted |
| 8 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7627 | 0.97 | ✅ accepted |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | 1.2189 | 0.88 | ❌ rejected |

**Proposal policy**: task_score is 0.84 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.376) — your mutation base

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

- **Composite score**: 0.376
- **task_score** (E): 0.842
- **fitness_score**: 0.536  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 0.00 | 0.67 | 0.1644 |
| align_lateral | 0.67 | 0.33 | 0.0311 |
| descend_contact | 0.00 | 0.00 | 0.0049 |
| insert_peg | 1.00 | 1.00 | 0.0292 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.469, 0.004, 0.142) | (0.504, -0.000, 0.340)→(0.506, 0.003, 0.143) | 0.260→0.069 | 0.67 / 0.667 | 159.729 | 782.338 |
| align_lateral | align | 0.67 / step_budget | (0.469, 0.004, 0.142)→(0.494, 0.001, 0.138) | (0.506, 0.003, 0.143)→(0.531, 0.001, 0.139) | 0.069→0.069 | 0.33 / 0.333 | 113.317 | 505.738 |
| descend_contact | descend | 0.00 / guard_failure | (0.494, 0.001, 0.138)→(0.496, -0.004, 0.137) | (0.531, 0.001, 0.139)→(0.533, -0.004, 0.138) | 0.069→0.068 | 0.00 / 0.000 | 0.000 | 144.813 |
| insert_peg | insert | 1.00 / force_exceeded | (0.496, -0.004, 0.137)→(0.474, -0.012, 0.122) | (0.533, -0.004, 0.138)→(0.512, -0.009, 0.116) | 0.068→0.044 | 1.00 / 1.667 | 922.044 | 1055.827 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.871
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.871
- phase_score: 0.413
- phase_breakdown.descend_to_contact_score: 0.531
- phase_breakdown.insert_fully_score: 0.544
- phase_breakdown.reach_above_score: 0.122

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.596
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.871
- **Median Q (composite search score)**: 0.405
- **K-run variance**: 0.0041
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.477


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.59091,"average_solve_count":44.0,"average_success_count":44.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_offset_x":0.01784,"align_lateral.lateral_offset_y":0.01997,"approach_above.approach_height":0.20932,"approach_above.speed":0.67296,"descend_contact.descend_depth":0.09998,"insert_peg.force_limit":35.07433,"insert_peg.insert_depth":0.08133},"optimized_scores":{"best_composite_score":0.40543,"best_fitness_score":0.56543,"best_task_score":0.80216},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":392.0,"contact_point_centroid":[0.52648,-0.01044,0.07965],"force_p95":271.67989,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1340.06625,"mean_force":274.32367,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.44346,-0.00595,0.12089]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52674,-0.0022,0.07956],"force_p95":951.3915,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":951.3915,"mean_force":951.3915,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.46438,9e-05,0.11007]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.43006,-0.00687,0.07858],"force_p95":808.17786,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":851.56779,"mean_force":135.35373,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.42676,-0.00527,0.09128]},{"body_a":"peg_socket","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.52683,-0.01128,0.07998],"force_p95":47.59402,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.11637,"mean_force":32.20204,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.44598,-0.00539,0.12273]}],"total_contact_groups":4},"final_pose_error":0.11284,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.4633,0.00014,0.10945],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":1340.06625,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.48512,-0.0068,0.12008],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.04329,"object_to_goal_dist_start":0.26034,"object_z_max":0.34395,"peak_contact_force":266.6538,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":404.0,"raw_peak_contact_force":1340.06625,"subtask_id":"reach_above","tcp_end":[0.44527,-0.00544,0.1233],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.51815,-0.00287,0.11998],"object_pos_start":[0.48512,-0.0068,0.12008],"object_to_goal_dist_end":0.044,"object_to_goal_dist_start":0.04329,"object_z_max":0.12008,"peak_contact_force":0.0,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":49.11637,"subtask_id":"descend_to_contact","tcp_end":[0.47835,-0.00151,0.12376],"tcp_start":[0.44527,-0.00544,0.1233],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":810.0,"object_pos_end":[0.51817,-0.00286,0.11991],"object_pos_start":[0.51815,-0.00287,0.11998],"object_to_goal_dist_end":0.04394,"object_to_goal_dist_start":0.044,"object_z_max":0.11998,"peak_contact_force":0.0,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"descend_to_contact","tcp_end":[0.47837,-0.00151,0.12368],"tcp_start":[0.47835,-0.00151,0.12376],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":27.0,"n_steps_budget":810.0,"object_pos_end":[0.50199,-0.0012,0.09935],"object_pos_start":[0.51817,-0.00286,0.11991],"object_to_goal_dist_end":0.01949,"object_to_goal_dist_start":0.04394,"object_z_max":0.11991,"peak_contact_force":951.3915,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":951.3915,"subtask_id":"insert_fully","tcp_end":[0.4633,0.00014,0.10945],"tcp_start":[0.47837,-0.00151,0.12368],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `23bedb35dfb8044c9064b13b9f8101cd4e2be35581b8354b6b999b22e5fca070`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.35556,"average_solve_count":45.0,"average_success_count":45.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_offset_x":-0.01887,"align_lateral.lateral_offset_y":-0.01996,"approach_above.approach_height":0.23783,"approach_above.speed":0.99893,"descend_contact.descend_depth":0.05145,"insert_peg.force_limit":12.12314,"insert_peg.insert_depth":0.12857},"optimized_scores":{"best_composite_score":0.43636,"best_fitness_score":0.59636,"best_task_score":0.87081},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.56592,-0.01628,0.07836],"force_p95":1121.23623,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1141.30363,"mean_force":940.62962,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.46626,-0.03733,0.09304]},{"body_a":"attachment","body_b":"peg_socket","contact_count":25.0,"contact_point_centroid":[0.47606,0.00023,0.07845],"force_p95":841.41309,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1042.63545,"mean_force":97.83861,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.46224,0.00027,0.08805]},{"body_a":"peg_socket","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.56617,-0.00193,0.0781],"force_p95":856.39534,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1014.14499,"mean_force":207.71579,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.4613,0.00024,0.08817]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.56492,-0.02931,0.07925],"force_p95":435.29719,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":458.20757,"mean_force":229.10378,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.46626,-0.03733,0.09304]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.47546,-0.03633,0.07996],"force_p95":337.07373,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":337.07373,"mean_force":337.07373,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.46525,-0.03778,0.09259]},{"body_a":"peg_socket","body_b":"link7","contact_count":19.0,"contact_point_centroid":[0.55947,-0.02929,0.07881],"force_p95":89.64753,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":90.78814,"mean_force":17.81543,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.46068,0.00025,0.08748]}],"total_contact_groups":6},"final_pose_error":0.16291,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.46375,-0.03882,0.09223],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":1141.30363,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":81.0,"n_steps_budget":600.0,"object_pos_end":[0.54159,0.00066,0.14627],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07824,"object_to_goal_dist_start":0.26034,"object_z_max":0.3457,"peak_contact_force":0.0,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_above","tcp_end":[0.50772,0.00067,0.12498],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.54623,-0.01733,0.14438],"object_pos_start":[0.54159,0.00066,0.14627],"object_to_goal_dist_end":0.08113,"object_to_goal_dist_start":0.07824,"object_z_max":0.14627,"peak_contact_force":0.0,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":70.0,"raw_peak_contact_force":1042.63545,"subtask_id":"descend_to_contact","tcp_end":[0.51206,-0.01732,0.12358],"tcp_start":[0.50772,0.00067,0.12498],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.54622,-0.01735,0.14435],"object_pos_start":[0.54623,-0.01733,0.14438],"object_to_goal_dist_end":0.08111,"object_to_goal_dist_start":0.08113,"object_z_max":0.14438,"peak_contact_force":0.0,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"descend_to_contact","tcp_end":[0.51206,-0.01734,0.12355],"tcp_start":[0.51206,-0.01732,0.12358],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":34.0,"n_steps_budget":1000.0,"object_pos_end":[0.50127,-0.02941,0.10241],"object_pos_start":[0.54622,-0.01735,0.14435],"object_to_goal_dist_end":0.037,"object_to_goal_dist_start":0.08111,"object_z_max":0.14435,"peak_contact_force":739.95562,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":1141.30363,"subtask_id":"insert_fully","tcp_end":[0.46375,-0.03882,0.09223],"tcp_start":[0.51206,-0.01734,0.12355],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0b9f57c3f8a8fdb0f6fef54a4b5c0cfa6a2779a7721b018896a4efe993ac60cd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":31.0,"average_failure_rate":0.44286,"average_mean_iterations":97.07143,"average_solve_count":70.0,"average_success_count":39.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.lateral_offset_x":0.00486,"align_lateral.lateral_offset_y":0.0033,"approach_above.approach_height":0.15943,"approach_above.speed":0.77054,"descend_contact.descend_depth":0.05906,"insert_peg.force_limit":16.8327,"insert_peg.insert_depth":0.10265},"optimized_scores":{"best_composite_score":0.28732,"best_fitness_score":0.44732,"best_task_score":0.85233},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58416,0.00162,0.07943],"force_p95":1074.78464,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1074.78464,"mean_force":1074.78464,"phase_index":3.0,"phase_name":"insert_peg","phase_type":"insert","tcp_position_centroid":[0.49555,0.00395,0.16321]},{"body_a":"peg_socket","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.5613,0.00604,0.07851],"force_p95":237.10269,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1006.94658,"mean_force":154.17388,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.44967,0.00525,0.11106]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.46495,0.00465,0.07935],"force_p95":916.00572,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":968.78486,"mean_force":223.34652,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.45463,0.00461,0.0912]},{"body_a":"peg_socket","body_b":"link7","contact_count":28.0,"contact_point_centroid":[0.54609,-0.00571,0.07784],"force_p95":635.08842,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":644.23295,"mean_force":214.64066,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.44993,0.00492,0.10237]},{"body_a":"peg_socket","body_b":"link6","contact_count":378.0,"contact_point_centroid":[0.58436,0.009,0.07983],"force_p95":277.68,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":445.89263,"mean_force":248.68175,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.45175,0.01059,0.16039]},{"body_a":"peg_socket","body_b":"link7","contact_count":50.0,"contact_point_centroid":[0.58436,0.03431,0.0799],"force_p95":389.52493,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":434.44021,"mean_force":289.2866,"phase_index":2.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.49401,0.02819,0.16518]},{"body_a":"peg_socket","body_b":"link7","contact_count":72.0,"contact_point_centroid":[0.58436,0.02347,0.07992],"force_p95":375.07797,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":425.46207,"mean_force":197.4068,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.48694,0.01988,0.1724]},{"body_a":"peg_socket","body_b":"link6","contact_count":180.0,"contact_point_centroid":[0.58438,0.01597,0.07995],"force_p95":177.35531,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":283.69238,"mean_force":136.86516,"phase_index":1.0,"phase_name":"align_lateral","phase_type":"align","tcp_position_centroid":[0.46643,0.01771,0.17796]}],"total_contact_groups":8},"final_pose_error":0.18904,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.49507,0.00359,0.1629],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":1074.78464,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.49053,0.01628,0.16361],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08571,"object_to_goal_dist_start":0.26034,"object_z_max":0.34459,"peak_contact_force":212.53234,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":456.0,"raw_peak_contact_force":1006.94658,"subtask_id":"reach_above","tcp_end":[0.45327,0.01621,0.17816],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":302.0,"n_steps_budget":600.0,"object_pos_end":[0.52943,0.0239,0.15144],"object_pos_start":[0.49053,0.01628,0.16361],"object_to_goal_dist_end":0.08088,"object_to_goal_dist_start":0.08571,"object_z_max":0.16366,"peak_contact_force":339.95041,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":252.0,"raw_peak_contact_force":425.46207,"subtask_id":"descend_to_contact","tcp_end":[0.49286,0.02096,0.16737],"tcp_start":[0.45327,0.01621,0.17816],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":92.0,"n_steps_budget":840.0,"object_pos_end":[0.53585,0.00883,0.14977],"object_pos_start":[0.52943,0.0239,0.15144],"object_to_goal_dist_end":0.07893,"object_to_goal_dist_start":0.08088,"object_z_max":0.15152,"peak_contact_force":0.0,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":50.0,"raw_peak_contact_force":434.44021,"subtask_id":"descend_to_contact","tcp_end":[0.4983,0.00794,0.16351],"tcp_start":[0.49286,0.02096,0.16737],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.53188,0.00318,0.14727],"object_pos_start":[0.53585,0.00883,0.14977],"object_to_goal_dist_end":0.07452,"object_to_goal_dist_start":0.07893,"object_z_max":0.15069,"peak_contact_force":1074.78464,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":1074.78464,"subtask_id":"insert_fully","tcp_end":[0.49507,0.00359,0.1629],"tcp_start":[0.4983,0.00794,0.16351],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```