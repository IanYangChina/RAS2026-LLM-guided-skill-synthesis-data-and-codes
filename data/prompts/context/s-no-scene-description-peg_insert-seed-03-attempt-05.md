## Search State

- **Seed**: 3
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → retract → descend → push | arc_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 4 | 0.5934 | 0.85 | ❌ rejected |
| 4 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7614 | 0.97 | ❌ rejected |
| 3 | approach → align → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4406 | 0.85 | ❌ rejected |
| 2 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7616 | 0.97 | ✅ accepted |
| 1 | approach → align → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4537 | 0.91 | ❌ rejected |

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

## Current Skill (Q=0.593) — your mutation base

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

- **Composite score**: 0.593
- **task_score** (E): 0.853
- **fitness_score**: 0.853  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.1283 |
| retract_1 | 1.00 | 0.00 | 0.1313 |
| descend_1 | 1.00 | 0.00 | 0.0582 |
| insert_1 | 0.00 | 1.00 | 0.3911 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.503, 0.002, 0.429) | (0.504, -0.000, 0.340)→(0.507, 0.002, 0.468) | 0.260→0.389 | 0.00 / 0.000 | 0.000 | 0.000 |
| retract_1 | retract | 1.00 / step_budget | (0.503, 0.002, 0.429)→(0.503, 0.004, 0.560) | (0.507, 0.002, 0.468)→(0.508, 0.005, 0.600) | 0.389→0.520 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_1 | descend | 1.00 / step_budget | (0.503, 0.004, 0.560)→(0.504, 0.004, 0.502) | (0.508, 0.005, 0.600)→(0.509, 0.004, 0.541) | 0.520→0.461 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | push | 0.00 / guard_failure | (0.504, 0.004, 0.502)→(0.499, 0.004, 0.111) | (0.509, 0.004, 0.541)→(0.538, 0.004, 0.105) | 0.461→0.047 | 1.00 / 1.333 | 1491.996 | 2291.401 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.915
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.915
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.915
- **Median Q (composite search score)**: 0.582
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.219


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.2381,"average_solve_count":84.0,"average_success_count":84.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.05591,"insert_1.insert_distance":0.20772,"insert_1.insertion_force_threshold":70.35629,"retract_1.retract_height":0.1301},"optimized_scores":{"best_composite_score":0.65525,"best_fitness_score":0.91525,"best_task_score":0.91525},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.52655,0.00405,0.07828],"force_p95":2398.65807,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2398.65807,"mean_force":2398.65807,"phase_index":3.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.4913,0.00376,0.09781]}],"total_contact_groups":1},"final_pose_error":0.19967,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.48922,0.00371,0.09481],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":2398.65807,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":789.0,"n_steps_budget":870.0,"object_pos_end":[0.50747,0.00229,0.46849],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.38857,"object_to_goal_dist_start":0.26034,"object_z_max":0.46837,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_target","tcp_end":[0.5029,0.00228,0.42876],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.50833,0.00448,0.58736],"object_pos_start":[0.50747,0.00229,0.46849],"object_to_goal_dist_end":0.50745,"object_to_goal_dist_start":0.38857,"object_z_max":0.58724,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50331,0.00445,0.54767],"tcp_start":[0.5029,0.00228,0.42876],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":154.0,"n_steps_budget":600.0,"object_pos_end":[0.50884,0.00444,0.54132],"object_pos_start":[0.50833,0.00448,0.58736],"object_to_goal_dist_end":0.46143,"object_to_goal_dist_start":0.50745,"object_z_max":0.58741,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50337,0.0044,0.5017],"tcp_start":[0.50331,0.00445,0.54767],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":139.0,"n_steps_budget":1000.0,"object_pos_end":[0.52856,0.00402,0.08758],"object_pos_start":[0.50884,0.00444,0.54132],"object_to_goal_dist_end":0.02983,"object_to_goal_dist_start":0.46143,"object_z_max":0.58289,"peak_contact_force":0.44065,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":2398.65807,"tcp_end":[0.48922,0.00371,0.09481],"tcp_start":[0.50337,0.0044,0.5017],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `23bedb35dfb8044c9064b13b9f8101cd4e2be35581b8354b6b999b22e5fca070`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.43678,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.07271,"insert_1.insert_distance":0.12466,"insert_1.insertion_force_threshold":71.59899,"retract_1.retract_height":0.14694},"optimized_scores":{"best_composite_score":0.54299,"best_fitness_score":0.80299,"best_task_score":0.80299},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.59386,0.00108,0.079],"force_p95":2159.10026,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2159.10026,"mean_force":2159.10026,"phase_index":3.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.50796,0.00398,0.12616]}],"total_contact_groups":1},"final_pose_error":0.25406,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.50601,0.004,0.12284],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":2159.10026,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":789.0,"n_steps_budget":870.0,"object_pos_end":[0.50747,0.00229,0.46849],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.38857,"object_to_goal_dist_start":0.26034,"object_z_max":0.46837,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_target","tcp_end":[0.5029,0.00228,0.42876],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":843.0,"n_steps_budget":930.0,"object_pos_end":[0.50853,0.00454,0.60414],"object_pos_start":[0.50747,0.00229,0.46849],"object_to_goal_dist_end":0.52423,"object_to_goal_dist_start":0.38857,"object_z_max":0.60402,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50351,0.00451,0.56446],"tcp_start":[0.5029,0.00228,0.42876],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":199.0,"n_steps_budget":600.0,"object_pos_end":[0.50925,0.00451,0.54117],"object_pos_start":[0.50853,0.00454,0.60414],"object_to_goal_dist_end":0.46129,"object_to_goal_dist_start":0.52423,"object_z_max":0.6042,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50381,0.00446,0.50154],"tcp_start":[0.50351,0.00451,0.56446],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":132.0,"n_steps_budget":780.0,"object_pos_end":[0.54582,0.00432,0.11905],"object_pos_start":[0.50925,0.00451,0.54117],"object_to_goal_dist_end":0.06036,"object_to_goal_dist_start":0.46129,"object_z_max":0.58243,"peak_contact_force":2159.10026,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":2159.10026,"tcp_end":[0.50601,0.004,0.12284],"tcp_start":[0.50381,0.00446,0.50154],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0b9f57c3f8a8fdb0f6fef54a4b5c0cfa6a2779a7721b018896a4efe993ac60cd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.46591,"average_solve_count":88.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"descend_1.depth":0.07581,"insert_1.insert_distance":0.15709,"insert_1.insertion_force_threshold":65.90129,"retract_1.retract_height":0.15023},"optimized_scores":{"best_composite_score":0.58205,"best_fitness_score":0.84205,"best_task_score":0.84205},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.58237,0.00039,0.07879],"force_p95":2316.44594,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2316.44594,"mean_force":2316.44594,"phase_index":3.0,"phase_name":"insert_1","phase_type":"push","tcp_position_centroid":[0.50323,0.00401,0.11782]}],"total_contact_groups":1},"final_pose_error":0.23035,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.50126,0.00404,0.11457],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":2316.44594,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":789.0,"n_steps_budget":870.0,"object_pos_end":[0.50747,0.00229,0.46849],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.38857,"object_to_goal_dist_start":0.26034,"object_z_max":0.46837,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_target","tcp_end":[0.5029,0.00228,0.42876],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.50857,0.00452,0.60751],"object_pos_start":[0.50747,0.00229,0.46849],"object_to_goal_dist_end":0.5276,"object_to_goal_dist_start":0.38857,"object_z_max":0.60739,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50355,0.0045,0.56783],"tcp_start":[0.5029,0.00228,0.42876],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":207.0,"n_steps_budget":600.0,"object_pos_end":[0.50929,0.00449,0.54162],"object_pos_start":[0.50857,0.00452,0.60751],"object_to_goal_dist_end":0.46173,"object_to_goal_dist_start":0.5276,"object_z_max":0.60757,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50384,0.00445,0.50199],"tcp_start":[0.50355,0.0045,0.56783],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":134.0,"n_steps_budget":990.0,"object_pos_end":[0.54097,0.00436,0.10978],"object_pos_start":[0.50929,0.00449,0.54162],"object_to_goal_dist_end":0.05084,"object_to_goal_dist_start":0.46173,"object_z_max":0.58284,"peak_contact_force":2316.44594,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1.0,"raw_peak_contact_force":2316.44594,"tcp_end":[0.50126,0.00404,0.11457],"tcp_start":[0.50384,0.00445,0.50199],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```