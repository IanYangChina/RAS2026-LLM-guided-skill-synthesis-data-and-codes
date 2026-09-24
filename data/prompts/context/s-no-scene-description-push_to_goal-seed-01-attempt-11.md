## Search State

- **Seed**: 1
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 2 | 0.3645 | 0.42 | ❌ rejected |
| 10 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2110 | 0.55 | ❌ rejected |
| 9 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2069 | 0.55 | ✅ accepted |
| 8 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2061 | 0.55 | ✅ accepted |
| 7 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 2 | 0.0323 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.365) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: align_2
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

```

## Design Metrics

- **Composite score**: 0.365
- **task_score** (E): 0.421
- **fitness_score**: 0.525  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.160

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1543 |
| align_1 | 1.00 | 1.00 | 0.1050 |
| push_1 | 1.00 | 1.00 | 0.1606 |
| retract_1 | 1.00 | 1.00 | 0.0883 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.474, -0.000, 0.154) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_1 | align | 1.00 / step_budget | (0.474, -0.000, 0.154)→(0.481, -0.001, 0.050) | (0.474, -0.001, 0.025)→(0.476, -0.001, 0.025) | 0.154→0.154 | 1.00 / 3.667 | 103.168 | 103.168 |
| push_1 | push | 1.00 / step_budget | (0.481, -0.001, 0.050)→(0.499, -0.154, 0.022) | (0.476, -0.001, 0.025)→(0.506, -0.063, 0.025) | 0.154→0.092 | 1.00 / 4.000 | 0.245 | 146.575 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.154, 0.022)→(0.496, -0.153, 0.110) | (0.506, -0.063, 0.025)→(0.506, -0.063, 0.025) | 0.092→0.092 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.489
- lateral_force_integral: None
- approach_alignment: 0.795
- goal_progress: 0.483
- terminal_score: 0.483
- phase_score: 0.590
- phase_breakdown.push_to_goal_score: 0.779
- phase_breakdown.reach_pre_contact_score: 0.149

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.547
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.483
- **Median Q (composite search score)**: 0.378
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Parameters at lower bound**: push_1.push_distance
- **Final σ (mean)**: 0.436


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f21cc79f03d9e871b86947069440973ee7e2ef557ebaac0b26b4f6cbdabf5bb1`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec03d65db90cc6b4602194a1eefa4c3104517a971e566e099fb50a3df7102251`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90083,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset":0.01659,"push_1.push_distance":0.02776},"optimized_scores":{"best_composite_score":0.32822,"best_fitness_score":0.48822,"best_task_score":0.31635},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2792.0,"contact_point_centroid":[0.53315,-0.00562,-0.00015],"force_p95":100.81646,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.85462,"mean_force":12.3682,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.505,-0.06426,0.03361]},{"body_a":"attachment","body_b":"push_box","contact_count":409.0,"contact_point_centroid":[0.52581,0.0239,0.04759],"force_p95":110.83892,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.6923,"mean_force":81.97925,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51598,0.01805,0.04784]},{"body_a":"attachment","body_b":"push_box","contact_count":41.0,"contact_point_centroid":[0.52544,0.05327,0.04895],"force_p95":93.95772,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.10529,"mean_force":74.03265,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51367,0.05323,0.05086]},{"body_a":"world","body_b":"push_box","contact_count":2494.0,"contact_point_centroid":[0.50216,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.48595,"mean_force":1.46985,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50416,0.05112,0.09889]},{"body_a":"world","body_b":"push_box","contact_count":1988.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49836,0.02405,0.22666]},{"body_a":"world","body_b":"push_box","contact_count":2184.0,"contact_point_centroid":[0.53564,-0.01512,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49481,-0.13821,0.0671]}],"total_contact_groups":6},"final_pose_error":0.01215,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53564,-0.01512,0.02499],"final_tcp_position":[0.49487,-0.13816,0.11228],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":113.85462,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1988.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.49833,0.04925,0.15318],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":642.0,"n_steps_budget":720.0,"object_pos_end":[0.5035,0.0542,0.02592],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20423,"object_to_goal_dist_start":0.20406,"object_z_max":0.02589,"peak_contact_force":94.10529,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2535.0,"raw_peak_contact_force":94.10529,"subtask_id":"reach_pre_contact","tcp_end":[0.51611,0.05343,0.04981],"tcp_start":[0.49833,0.04925,0.15318],"tcp_to_object_dist_end":0.02702,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53564,-0.01512,0.02499],"object_pos_start":[0.5035,0.0542,0.02592],"object_to_goal_dist_end":0.13951,"object_to_goal_dist_start":0.20423,"object_z_max":0.03643,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3201.0,"raw_peak_contact_force":113.85462,"subtask_id":"push_to_goal","tcp_end":[0.49821,-0.13896,0.02393],"tcp_start":[0.51611,0.05343,0.04981],"tcp_to_object_dist_end":0.12937,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":630.0,"object_pos_end":[0.53564,-0.01512,0.02499],"object_pos_start":[0.53564,-0.01512,0.02499],"object_to_goal_dist_end":0.13951,"object_to_goal_dist_start":0.13951,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2184.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49487,-0.13816,0.11228],"tcp_start":[0.49821,-0.13896,0.02393],"tcp_to_object_dist_end":0.15627,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `060d405a872aae8d4597ed6284dedb60e9c99f80071c0520b1a8a2986f3c114d`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89091,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset":0.01364,"push_1.push_distance":0.02},"optimized_scores":{"best_composite_score":0.37809,"best_fitness_score":0.53809,"best_task_score":0.46345},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":470.0,"contact_point_centroid":[0.49868,-0.05343,0.04628],"force_p95":132.40952,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.8703,"mean_force":100.15678,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49338,-0.06282,0.04589]},{"body_a":"world","body_b":"push_box","contact_count":1745.0,"contact_point_centroid":[0.50757,-0.06408,-0.00029],"force_p95":124.77606,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":136.34327,"mean_force":27.50861,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49475,-0.10506,0.03434]},{"body_a":"attachment","body_b":"push_box","contact_count":35.0,"contact_point_centroid":[0.49304,-0.02392,0.04899],"force_p95":102.03927,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.51097,"mean_force":81.51591,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48127,-0.02393,0.05089]},{"body_a":"world","body_b":"push_box","contact_count":2458.0,"contact_point_centroid":[0.47199,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.5179,"mean_force":1.41234,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47446,-0.0229,0.09981]},{"body_a":"world","body_b":"push_box","contact_count":1840.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48515,-0.01065,0.22781]},{"body_a":"world","body_b":"push_box","contact_count":2180.0,"contact_point_centroid":[0.51431,-0.08226,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49575,-0.16103,0.06404]}],"total_contact_groups":6},"final_pose_error":0.01229,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51431,-0.08226,0.02499],"final_tcp_position":[0.49581,-0.16099,0.10915],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":136.8703,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":460.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1840.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.47108,-0.02193,0.15462],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12965,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":629.0,"n_steps_budget":720.0,"object_pos_end":[0.47295,-0.02425,0.02529],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12863,"object_to_goal_dist_start":0.12903,"object_z_max":0.02526,"peak_contact_force":102.51097,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2493.0,"raw_peak_contact_force":102.51097,"subtask_id":"reach_pre_contact","tcp_end":[0.48316,-0.02402,0.04982],"tcp_start":[0.47108,-0.02193,0.15462],"tcp_to_object_dist_end":0.02657,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":762.0,"n_steps_budget":930.0,"object_pos_end":[0.51431,-0.08226,0.02499],"object_pos_start":[0.47295,-0.02425,0.02529],"object_to_goal_dist_end":0.06923,"object_to_goal_dist_start":0.12863,"object_z_max":0.03535,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2215.0,"raw_peak_contact_force":136.8703,"subtask_id":"push_to_goal","tcp_end":[0.49917,-0.16193,0.02093],"tcp_start":[0.48316,-0.02402,0.04982],"tcp_to_object_dist_end":0.08119,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.51431,-0.08226,0.02499],"object_pos_start":[0.51431,-0.08226,0.02499],"object_to_goal_dist_end":0.06923,"object_to_goal_dist_start":0.06923,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49581,-0.16099,0.10915],"tcp_start":[0.49917,-0.16193,0.02093],"tcp_to_object_dist_end":0.11672,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c4af277909bfbef2010e50829d2192ea184fe34d7420833f45dd73455a81c9b6`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89189,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset":-0.00408,"push_1.push_distance":0.02037},"optimized_scores":{"best_composite_score":0.38721,"best_fitness_score":0.54721,"best_task_score":0.48284},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1945.0,"contact_point_centroid":[0.46657,-0.07354,-0.00034],"force_p95":157.02022,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":189.00131,"mean_force":31.61014,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47795,-0.10381,0.03536]},{"body_a":"attachment","body_b":"push_box","contact_count":472.0,"contact_point_centroid":[0.47379,-0.06188,0.04575],"force_p95":163.88136,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":188.47701,"mean_force":128.12562,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46586,-0.06829,0.04607]},{"body_a":"attachment","body_b":"push_box","contact_count":23.0,"contact_point_centroid":[0.45562,-0.03133,0.04911],"force_p95":111.35292,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.88822,"mean_force":86.53964,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44387,-0.03123,0.05095]},{"body_a":"world","body_b":"push_box","contact_count":2212.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.67501,"mean_force":1.14591,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.44628,-0.02996,0.10019]},{"body_a":"world","body_b":"push_box","contact_count":1912.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47569,-0.014,0.22746]},{"body_a":"world","body_b":"push_box","contact_count":2180.0,"contact_point_centroid":[0.46787,-0.09187,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4976,-0.16087,0.06408]}],"total_contact_groups":6},"final_pose_error":0.01233,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46787,-0.09187,0.02499],"final_tcp_position":[0.49765,-0.16084,0.10918],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":189.00131,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":478.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1912.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.45175,-0.02878,0.15419],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12924,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":553.0,"n_steps_budget":690.0,"object_pos_end":[0.45066,-0.03163,0.02445],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12824,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":112.88822,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2235.0,"raw_peak_contact_force":112.88822,"subtask_id":"reach_pre_contact","tcp_end":[0.44466,-0.03131,0.04999],"tcp_start":[0.45175,-0.02878,0.15419],"tcp_to_object_dist_end":0.02623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":775.0,"n_steps_budget":960.0,"object_pos_end":[0.46787,-0.09187,0.02499],"object_pos_start":[0.45066,-0.03163,0.02445],"object_to_goal_dist_end":0.06642,"object_to_goal_dist_start":0.12824,"object_z_max":0.03537,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2417.0,"raw_peak_contact_force":189.00131,"subtask_id":"push_to_goal","tcp_end":[0.50102,-0.16177,0.021],"tcp_start":[0.44466,-0.03131,0.04999],"tcp_to_object_dist_end":0.07747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.46787,-0.09187,0.02499],"object_pos_start":[0.46787,-0.09187,0.02499],"object_to_goal_dist_end":0.06642,"object_to_goal_dist_start":0.06642,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49765,-0.16084,0.10918],"tcp_start":[0.50102,-0.16177,0.021],"tcp_to_object_dist_end":0.11284,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```