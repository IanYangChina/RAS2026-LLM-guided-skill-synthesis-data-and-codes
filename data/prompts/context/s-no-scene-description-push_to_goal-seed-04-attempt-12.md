## Search State

- **Seed**: 4
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4262 | 0.82 | ✅ accepted |
| 11 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4171 | 0.80 | ✅ accepted |
| 10 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4187 | 0.80 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | -0.2283 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | -0.3614 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.426) — your mutation base

```yaml
skill: push_to_goal
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: 0.426
- **task_score** (E): 0.816
- **fitness_score**: 0.453  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1960 |
| align_1 | 1.00 | 1.00 | 0.1617 |
| release_1 | 0.33 | 1.00 | 0.1694 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.496, -0.051, 0.114) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_1 | align | 1.00 / step_budget | (0.496, -0.051, 0.114)→(0.527, 0.079, 0.027) | (0.531, 0.007, 0.025)→(0.534, 0.017, 0.028) | 0.161→0.171 | 1.00 / 3.667 | 24.999 | 62.839 |
| release_1 | release | 0.33 / step_budget | (0.527, 0.079, 0.027)→(0.504, -0.088, 0.020) | (0.534, 0.017, 0.028)→(0.519, -0.131, 0.025) | 0.171→0.032 | 1.00 / 4.333 | 18.065 | 94.135 |
| insert_1 | insert | 1.00 / force_exceeded | (0.504, -0.088, 0.020)→(0.504, -0.088, 0.020) | (0.519, -0.131, 0.025)→(0.519, -0.131, 0.025) | 0.032→0.032 | 1.00 / 4.333 | 35.597 | 35.597 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.696
- goal_progress: 0.933
- terminal_score: 0.933
- phase_score: 0.218
- phase_breakdown.approach_score: 0.821
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.108

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.504
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.933
- **Median Q (composite search score)**: 0.432
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.369


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8d5a7e825d9524a0954b44a69bda19e1d764760f64bb1262d03aec3c389fadbb`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c4094dd933e0897d422d7ea261a82b80810f7dec183b19c1da5b940157e7d0c4`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89516,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.0014,"align_1.lateral_offset_y":0.00723,"insert_1.insertion_depth":0.09851,"insert_1.insertion_force":7.39647,"push_1.push_distance":0.02637,"push_1.push_speed":0.07714},"optimized_scores":{"best_composite_score":0.43222,"best_fitness_score":0.45889,"best_task_score":0.84521},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2246.0,"contact_point_centroid":[0.54917,-0.06098,-0.00013],"force_p95":40.49867,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.63922,"mean_force":16.73603,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52546,-0.01105,0.0207]},{"body_a":"push_box","body_b":"link7","contact_count":1051.0,"contact_point_centroid":[0.5581,-0.05059,0.05022],"force_p95":48.68141,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.85478,"mean_force":30.03041,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52185,-0.02893,0.02085]},{"body_a":"attachment","body_b":"push_box","contact_count":804.0,"contact_point_centroid":[0.52595,-0.05757,0.03598],"force_p95":34.72965,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.01932,"mean_force":13.04075,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5185,-0.04621,0.02116]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53939,-0.11813,0.04965],"force_p95":30.75433,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.75433,"mean_force":30.75433,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50746,-0.09337,0.01947]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.5296,-0.15689,-0.00013],"force_p95":24.53612,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.50321,"mean_force":15.83232,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50746,-0.09337,0.01947]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.52684,-0.10384,0.05011],"force_p95":14.03885,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.03885,"mean_force":14.03885,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50746,-0.09337,0.01947]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49717,-0.00894,0.19744]},{"body_a":"world","body_b":"push_box","contact_count":2548.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52027,0.03011,0.05756]}],"total_contact_groups":8},"final_pose_error":0.0574,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51932,-0.1344,0.02498],"final_tcp_position":[0.50744,-0.09336,0.01944],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":62.63922,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4963,-0.01791,0.09808],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09459,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":637.0,"n_steps_budget":870.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2548.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.54556,0.07523,0.02325],"tcp_start":[0.4963,-0.01791,0.09808],"tcp_to_object_dist_end":0.07428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51933,-0.13439,0.02501],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.02484,"object_to_goal_dist_start":0.16043,"object_z_max":0.02828,"peak_contact_force":18.04736,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4101.0,"raw_peak_contact_force":62.63922,"tcp_end":[0.50746,-0.09337,0.01947],"tcp_start":[0.54556,0.07523,0.02325],"tcp_to_object_dist_end":0.04306,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.51932,-0.1344,0.02498],"object_pos_start":[0.51933,-0.13439,0.02501],"object_to_goal_dist_end":0.02483,"object_to_goal_dist_start":0.02484,"object_z_max":0.02501,"peak_contact_force":30.75433,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":30.75433,"tcp_end":[0.50744,-0.09336,0.01944],"tcp_start":[0.50746,-0.09337,0.01947],"tcp_to_object_dist_end":0.04308,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90476,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00359,"align_1.lateral_offset_y":-0.00074,"insert_1.insertion_depth":0.12026,"insert_1.insertion_force":8.8788,"push_1.push_distance":0.17524,"push_1.push_speed":0.09684},"optimized_scores":{"best_composite_score":0.36892,"best_fitness_score":0.39558,"best_task_score":0.66935},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":242.0,"contact_point_centroid":[0.5362,0.06978,0.04629],"force_p95":154.95152,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":188.02508,"mean_force":104.26798,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52877,0.07697,0.04832]},{"body_a":"attachment","body_b":"push_box","contact_count":909.0,"contact_point_centroid":[0.53387,0.03079,0.03486],"force_p95":156.6346,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.77927,"mean_force":116.69571,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52965,0.04095,0.03564]},{"body_a":"world","body_b":"push_box","contact_count":3264.0,"contact_point_centroid":[0.53715,0.04078,-8e-05],"force_p95":63.34172,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":150.45314,"mean_force":8.67893,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51044,0.00135,0.08391]},{"body_a":"world","body_b":"push_box","contact_count":2421.0,"contact_point_centroid":[0.53836,-0.02278,-0.00042],"force_p95":105.89391,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":118.4873,"mean_force":59.73338,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52599,0.0239,0.03315]},{"body_a":"push_box","body_b":"link7","contact_count":1049.0,"contact_point_centroid":[0.56203,-0.00031,0.0672],"force_p95":73.02486,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.36546,"mean_force":47.4602,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52813,0.03488,0.03445]},{"body_a":"push_box","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.56773,0.07387,0.06715],"force_p95":77.82002,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.8866,"mean_force":64.77718,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5341,0.10643,0.03439]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55331,-0.0724,0.04973],"force_p95":32.16947,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.16947,"mean_force":32.16947,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50988,-0.04949,0.02248]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.54478,-0.09019,-5e-05],"force_p95":20.5129,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.12247,"mean_force":11.10078,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50988,-0.04949,0.02248]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49727,-0.04126,0.21342]}],"total_contact_groups":9},"final_pose_error":0.10103,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53745,-0.09935,0.02493],"final_tcp_position":[0.50988,-0.04949,0.02246],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":188.02508,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49661,-0.08147,0.13251],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16488,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":947.0,"n_steps_budget":1000.0,"object_pos_end":[0.54289,0.06713,0.0328],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.22147,"object_to_goal_dist_start":0.1905,"object_z_max":0.03485,"peak_contact_force":74.50709,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3539.0,"raw_peak_contact_force":188.02508,"tcp_end":[0.53522,0.1102,0.03215],"tcp_start":[0.49661,-0.08147,0.13251],"tcp_to_object_dist_end":0.04374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53745,-0.09935,0.02493],"object_pos_start":[0.54289,0.06713,0.0328],"object_to_goal_dist_end":0.06299,"object_to_goal_dist_start":0.22147,"object_z_max":0.03448,"peak_contact_force":6.59495,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4379.0,"raw_peak_contact_force":164.77927,"tcp_end":[0.50988,-0.04949,0.02248],"tcp_start":[0.53522,0.1102,0.03215],"tcp_to_object_dist_end":0.05702,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.53745,-0.09935,0.02493],"object_pos_start":[0.53745,-0.09935,0.02493],"object_to_goal_dist_end":0.06299,"object_to_goal_dist_start":0.06299,"object_z_max":0.02493,"peak_contact_force":32.16947,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":32.16947,"tcp_end":[0.50988,-0.04949,0.02246],"tcp_start":[0.50988,-0.04949,0.02248],"tcp_to_object_dist_end":0.05703,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89916,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00381,"align_1.lateral_offset_y":-0.00261,"insert_1.insertion_depth":0.11736,"insert_1.insertion_force":6.17189,"push_1.push_distance":0.06218,"push_1.push_speed":0.08386},"optimized_scores":{"best_composite_score":0.47751,"best_fitness_score":0.50418,"best_task_score":0.9331},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2289.0,"contact_point_centroid":[0.50583,-0.09108,-8e-05],"force_p95":30.34601,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.98502,"mean_force":8.98999,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49627,-0.04066,0.02108]},{"body_a":"attachment","body_b":"push_box","contact_count":741.0,"contact_point_centroid":[0.51115,-0.06156,0.04526],"force_p95":38.72264,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.16889,"mean_force":15.75507,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49677,-0.05024,0.0216]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52374,-0.14687,0.04926],"force_p95":43.86736,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.86736,"mean_force":43.86736,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49476,-0.1205,0.01811]},{"body_a":"push_box","body_b":"link7","contact_count":680.0,"contact_point_centroid":[0.52371,-0.07176,0.05294],"force_p95":33.11127,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.97591,"mean_force":17.53152,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49657,-0.05054,0.02126]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49866,-0.15881,-0.00013],"force_p95":24.82127,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.48746,"mean_force":11.22213,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49476,-0.1205,0.01811]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4972,-0.02719,0.20315]},{"body_a":"world","body_b":"push_box","contact_count":2164.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49672,-0.00051,0.06624]}],"total_contact_groups":7},"final_pose_error":0.03075,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49874,-0.15869,0.02473],"final_tcp_position":[0.49476,-0.1205,0.0181],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":54.98502,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49642,-0.05414,0.11063],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.093,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":541.0,"n_steps_budget":900.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2164.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49979,0.05262,0.02606],"tcp_start":[0.49642,-0.05414,0.11063],"tcp_to_object_dist_end":0.0716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49875,-0.15869,0.02473],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00878,"object_to_goal_dist_start":0.13127,"object_z_max":0.02866,"peak_contact_force":29.55256,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3710.0,"raw_peak_contact_force":54.98502,"tcp_end":[0.49476,-0.1205,0.01811],"tcp_start":[0.49979,0.05262,0.02606],"tcp_to_object_dist_end":0.03896,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49874,-0.15869,0.02473],"object_pos_start":[0.49875,-0.15869,0.02473],"object_to_goal_dist_end":0.00878,"object_to_goal_dist_start":0.00878,"object_z_max":0.02473,"peak_contact_force":43.86736,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":43.86736,"tcp_end":[0.49476,-0.1205,0.0181],"tcp_start":[0.49476,-0.1205,0.01811],"tcp_to_object_dist_end":0.03897,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```