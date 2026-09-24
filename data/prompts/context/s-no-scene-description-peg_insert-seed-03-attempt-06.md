## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → retract → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.3242 | 0.82 | ❌ rejected |
| 5 | approach → retract → descend → push | arc_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 4 | 0.5934 | 0.85 | ❌ rejected |
| 4 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7614 | 0.97 | ❌ rejected |
| 3 | approach → align → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4406 | 0.85 | ❌ rejected |
| 2 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | 0.7616 | 0.97 | ✅ accepted |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.324) — your mutation base

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

- **Composite score**: 0.324
- **task_score** (E): 0.825
- **fitness_score**: 0.634  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.1640 |
| retract_1 | 1.00 | 0.00 | 0.0533 |
| descend_1 | 1.00 | 0.00 | 0.0790 |
| insert_1 | 0.00 | 1.00 | 0.0022 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.503, -0.000, 0.464) | (0.504, -0.000, 0.340)→(0.508, -0.000, 0.504) | 0.260→0.424 | 0.00 / 0.000 | 0.000 | 0.000 |
| retract_1 | retract | 1.00 / step_budget | (0.503, -0.000, 0.464)→(0.503, -0.000, 0.518) | (0.508, -0.000, 0.504)→(0.508, -0.000, 0.557) | 0.424→0.477 | 0.00 / 0.000 | 0.000 | 0.000 |
| descend_1 | descend | 1.00 / step_budget | (0.503, -0.000, 0.518)→(0.509, -0.000, 0.596) | (0.508, -0.000, 0.557)→(0.514, -0.000, 0.636) | 0.477→0.556 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 0.00 / guard_failure | (0.491, 0.003, 0.117)→(0.489, 0.003, 0.115) | (0.514, -0.000, 0.636)→(0.531, 0.004, 0.112) | 0.556→0.045 | 1.00 / 1.667 | 1263.989 | 2431.240 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.881
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.881
- phase_score: 0.592
- phase_breakdown.reach_goal_score: 0.590
- phase_breakdown.reach_pre_contact_score: 0.596

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.708
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.881
- **Median Q (composite search score)**: 0.294
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.321


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.27059,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"insert_1.insertion_force_threshold":37.817,"insert_1.lateral_x_offset":0.01169,"insert_1.lateral_y_offset":-0.03747,"insert_1.push_depth":0.0986,"retract_1.retract_height":0.0505},"optimized_scores":{"best_composite_score":0.39761,"best_fitness_score":0.70761,"best_task_score":0.88101},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.52623,0.00331,0.07747],"force_p95":2595.63242,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2631.58288,"mean_force":2294.91446,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48293,0.00288,0.10064]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.49684,0.00896,0.07997],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48114,0.00275,0.09803]}],"total_contact_groups":2},"final_pose_error":0.13051,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.47976,0.00265,0.09668],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":2631.58288,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50755,-3e-05,0.50419],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.42425,"object_to_goal_dist_start":0.26034,"object_z_max":0.50399,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_contact","tcp_end":[0.50297,-4e-05,0.46445],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":390.0,"n_steps_budget":600.0,"object_pos_end":[0.50794,-6e-05,0.54467],"object_pos_start":[0.50755,-3e-05,0.50419],"object_to_goal_dist_end":0.46474,"object_to_goal_dist_start":0.42425,"object_z_max":0.54459,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50291,-8e-05,0.50499],"tcp_start":[0.50297,-4e-05,0.46445],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.51392,-8e-05,0.6233],"object_pos_start":[0.50794,-6e-05,0.54467],"object_to_goal_dist_end":0.54347,"object_to_goal_dist_start":0.46474,"object_z_max":0.62318,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50846,-0.00012,0.58367],"tcp_start":[0.50291,-8e-05,0.50499],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.52171,0.0033,0.09093],"object_pos_start":[0.51392,-8e-05,0.6233],"object_to_goal_dist_end":0.02452,"object_to_goal_dist_start":0.54347,"object_z_max":0.66083,"peak_contact_force":0.95807,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":2631.58288,"subtask_id":"reach_goal","tcp_end":[0.47976,0.00265,0.09668],"tcp_start":[0.48114,0.00275,0.09803],"tcp_to_object_dist_end":0.04234,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `23bedb35dfb8044c9064b13b9f8101cd4e2be35581b8354b6b999b22e5fca070`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.49412,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"insert_1.insertion_force_threshold":26.3938,"insert_1.lateral_x_offset":0.0251,"insert_1.lateral_y_offset":0.00972,"insert_1.push_depth":0.12494,"retract_1.retract_height":0.08228},"optimized_scores":{"best_composite_score":0.28139,"best_fitness_score":0.59139,"best_task_score":0.79154},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.59447,0.0086,0.07462],"force_p95":2240.05665,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2257.67739,"mean_force":2038.03141,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49644,0.00414,0.13042]}],"total_contact_groups":1},"final_pose_error":0.18305,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.49367,0.0042,0.12533],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":2257.67739,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50755,-3e-05,0.50419],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.42425,"object_to_goal_dist_start":0.26034,"object_z_max":0.50399,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_contact","tcp_end":[0.50297,-4e-05,0.46445],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":510.0,"n_steps_budget":600.0,"object_pos_end":[0.50826,-6e-05,0.57562],"object_pos_start":[0.50755,-3e-05,0.50419],"object_to_goal_dist_end":0.49569,"object_to_goal_dist_start":0.42425,"object_z_max":0.57551,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50322,-9e-05,0.53594],"tcp_start":[0.50297,-4e-05,0.46445],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.51463,-9e-05,0.65443],"object_pos_start":[0.50826,-6e-05,0.57562],"object_to_goal_dist_end":0.57462,"object_to_goal_dist_start":0.49569,"object_z_max":0.65432,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50916,-0.00013,0.61481],"tcp_start":[0.50322,-9e-05,0.53594],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":140.0,"n_steps_budget":1000.0,"object_pos_end":[0.53574,0.00459,0.1233],"object_pos_start":[0.51463,-9e-05,0.65443],"object_to_goal_dist_end":0.05633,"object_to_goal_dist_start":0.57462,"object_z_max":0.6839,"peak_contact_force":1774.94682,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":2257.67739,"subtask_id":"reach_goal","tcp_end":[0.49367,0.0042,0.12533],"tcp_start":[0.49484,0.00416,0.12733],"tcp_to_object_dist_end":0.04212,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0b9f57c3f8a8fdb0f6fef54a4b5c0cfa6a2779a7721b018896a4efe993ac60cd`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.34118,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"insert_1.insertion_force_threshold":32.47581,"insert_1.lateral_x_offset":0.03694,"insert_1.lateral_y_offset":0.00657,"insert_1.push_depth":0.07702,"retract_1.retract_height":0.05771},"optimized_scores":{"best_composite_score":0.29358,"best_fitness_score":0.60358,"best_task_score":0.80208},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5803,0.00438,0.07791],"force_p95":2392.46413,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2404.45954,"mean_force":2235.00912,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49714,0.00322,0.12837]}],"total_contact_groups":1},"final_pose_error":0.14035,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.49444,0.00329,0.12316],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":2404.45954,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50755,-3e-05,0.50419],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.42425,"object_to_goal_dist_start":0.26034,"object_z_max":0.50399,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_contact","tcp_end":[0.50297,-4e-05,0.46445],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":439.0,"n_steps_budget":600.0,"object_pos_end":[0.50798,-6e-05,0.55192],"object_pos_start":[0.50755,-3e-05,0.50419],"object_to_goal_dist_end":0.47199,"object_to_goal_dist_start":0.42425,"object_z_max":0.55183,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50295,-8e-05,0.51224],"tcp_start":[0.50297,-4e-05,0.46445],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.51406,-9e-05,0.63063],"object_pos_start":[0.50798,-6e-05,0.55192],"object_to_goal_dist_end":0.55081,"object_to_goal_dist_start":0.47199,"object_z_max":0.63052,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50859,-0.00012,0.59101],"tcp_start":[0.50295,-8e-05,0.51224],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":140.0,"n_steps_budget":1000.0,"object_pos_end":[0.53646,0.00355,0.12148],"object_pos_start":[0.51406,-9e-05,0.63063],"object_to_goal_dist_end":0.05534,"object_to_goal_dist_start":0.55081,"object_z_max":0.66638,"peak_contact_force":2016.06243,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":2404.45954,"subtask_id":"reach_goal","tcp_end":[0.49444,0.00329,0.12316],"tcp_start":[0.49554,0.00325,0.12533],"tcp_to_object_dist_end":0.04206,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```