## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | 0.2262 | 0.43 | ❌ rejected |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.5405 | 0.57 | ✅ accepted |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Primary evaluation target: **object displacement ratio toward goal_object_position**

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
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=0.226) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: pull_1
  type: pull
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.226
- **task_score** (E): 0.434
- **fitness_score**: 0.426  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2356 |
| push_to_goal | 1.00 | 1.00 | 0.1828 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.479, 0.035, 0.077) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 1.00 / step_budget | (0.479, 0.035, 0.077)→(0.496, -0.131, 0.027) | (0.492, -0.018, 0.025)→(0.512, -0.075, 0.026) | 0.139→0.080 | 1.00 / 3.000 | 0.532 | 132.557 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.674
- lateral_force_integral: None
- approach_alignment: 0.697
- goal_progress: 0.546
- terminal_score: 0.546
- phase_score: 0.468
- phase_breakdown.approach_contact_score: 0.157
- phase_breakdown.push_goal_score: 0.546

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.499
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.546
- **Median Q (composite search score)**: 0.225
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.421


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `27920116be2b9a598fe307ae470bb0295293d051bb1ef513a0996a4d851f2459`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1a1e2536715050e6c37d8aed13e4ecd62004f6234f1413b07d7b475a233f55c9`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.18571,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_z":0.03536,"approach_behind.behind_dist":0.04309,"push_to_goal.push_speed":0.43145,"push_to_goal.push_tolerance":0.03411},"optimized_scores":{"best_composite_score":0.22543,"best_fitness_score":0.42543,"best_task_score":0.42379},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":962.0,"contact_point_centroid":[0.47333,-0.03492,-9e-05],"force_p95":26.73484,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":122.89254,"mean_force":3.15631,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47346,-0.04221,0.05734]},{"body_a":"attachment","body_b":"push_box","contact_count":76.0,"contact_point_centroid":[0.48568,-0.06291,0.04678],"force_p95":81.02568,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.83638,"mean_force":35.36412,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4806,-0.07315,0.0475]},{"body_a":"world","body_b":"push_box","contact_count":1708.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48124,0.00776,0.19131]}],"total_contact_groups":3},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47849,-0.07884,0.02397],"final_tcp_position":[0.49272,-0.13168,0.02628],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":122.89254,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":427.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1708.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_contact","tcp_end":[0.46283,0.01592,0.08023],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0688,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":342.0,"n_steps_budget":600.0,"object_pos_end":[0.47849,-0.07884,0.02397],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.07435,"object_to_goal_dist_start":0.12903,"object_z_max":0.03526,"peak_contact_force":0.57383,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1038.0,"raw_peak_contact_force":122.89254,"subtask_id":"push_goal","tcp_end":[0.49272,-0.13168,0.02628],"tcp_start":[0.46283,0.01592,0.08023],"tcp_to_object_dist_end":0.05478,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.21519,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_z":0.03218,"approach_behind.behind_dist":0.09982,"push_to_goal.push_speed":0.2056,"push_to_goal.push_tolerance":0.04319},"optimized_scores":{"best_composite_score":0.29897,"best_fitness_score":0.49897,"best_task_score":0.54559},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":277.0,"contact_point_centroid":[0.4773,-0.05832,0.04729],"force_p95":195.39038,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":238.07432,"mean_force":140.44345,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47219,-0.0671,0.04712]},{"body_a":"world","body_b":"push_box","contact_count":1160.0,"contact_point_centroid":[0.4617,-0.04034,-0.0003],"force_p95":180.04383,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":215.77342,"mean_force":33.98002,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.44411,-0.01155,0.05745]},{"body_a":"world","body_b":"push_box","contact_count":1884.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.45864,0.02682,0.18833]}],"total_contact_groups":3},"final_pose_error":0.0198,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51105,-0.09294,0.03035],"final_tcp_position":[0.49325,-0.13179,0.02888],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":238.07432,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":471.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1884.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_contact","tcp_end":[0.41694,0.05474,0.07533],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":494.0,"n_steps_budget":720.0,"object_pos_end":[0.51105,-0.09294,0.03035],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.05836,"object_to_goal_dist_start":0.12843,"object_z_max":0.03662,"peak_contact_force":0.77612,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1437.0,"raw_peak_contact_force":238.07432,"subtask_id":"push_goal","tcp_end":[0.49325,-0.13179,0.02888],"tcp_start":[0.41694,0.05474,0.07533],"tcp_to_object_dist_end":0.04276,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93478,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_z":0.03207,"approach_behind.behind_dist":0.04037,"push_to_goal.push_speed":0.10612,"push_to_goal.push_tolerance":0.02565},"optimized_scores":{"best_composite_score":0.15417,"best_fitness_score":0.35417,"best_task_score":0.33388},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1137.0,"contact_point_centroid":[0.54977,-0.01997,-0.00011],"force_p95":12.29777,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.70386,"mean_force":1.75257,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53071,-0.0399,0.04945]},{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.53888,-0.03401,0.04804],"force_p95":33.52094,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.6045,"mean_force":21.19777,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53083,-0.04198,0.0495]},{"body_a":"world","body_b":"push_box","contact_count":1876.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52729,0.01733,0.18814]}],"total_contact_groups":3},"final_pose_error":0.01965,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54577,-0.05343,0.02496],"final_tcp_position":[0.5021,-0.13046,0.02491],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":36.70386,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":469.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1876.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_contact","tcp_end":[0.55703,0.03549,0.07402],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":395.0,"n_steps_budget":1000.0,"object_pos_end":[0.54577,-0.05343,0.02496],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.10686,"object_to_goal_dist_start":0.16043,"object_z_max":0.03535,"peak_contact_force":0.24457,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1212.0,"raw_peak_contact_force":36.70386,"subtask_id":"push_goal","tcp_end":[0.5021,-0.13046,0.02491],"tcp_start":[0.55703,0.03549,0.07402],"tcp_to_object_dist_end":0.08854,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```