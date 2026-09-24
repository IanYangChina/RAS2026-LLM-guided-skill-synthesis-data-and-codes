## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.3380 | 0.54 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | 0.3790 | 0.45 | ❌ rejected |
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.1530 | 0.04 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.4551 | 0.63 | ❌ rejected |
| 4 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.6774 | 0.82 | ✅ accepted |

**Proposal policy**: task_score is 0.54 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`
- Frozen object start: [0.5444299044764102, -0.025581934909493356, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5444299044764102, -0.025581934909493356, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5444, -0.0256, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5444299044764102, -0.025581934909493356, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0444, -0.1244, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.08, 0.00) | distance | — |
| contact | object | (0.00, 0.03, 0.00) | distance | — |
| push | goal | (0.00, 0.03, 0.00) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.338) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.338
- **task_score** (E): 0.542
- **fitness_score**: 0.598  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2014 |
| contact_1 | 1.00 | 1.00 | 0.0530 |
| push_1 | 1.00 | 1.00 | 0.1441 |
| retract_1 | 1.00 | 1.00 | 0.1210 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, -0.002, 0.105) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.514, -0.002, 0.105)→(0.512, 0.005, 0.052) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 25328.595 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.512, 0.005, 0.052)→(0.497, -0.129, 0.026) | (0.518, -0.020, 0.025)→(0.527, -0.090, 0.027) | 0.139→0.068 | 1.00 / 2.000 | 0.392 | 179.039 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.129, 0.026)→(0.494, -0.128, 0.147) | (0.527, -0.090, 0.027)→(0.525, -0.093, 0.025) | 0.068→0.064 | 1.00 / 4.000 | 0.245 | 2.660 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.539
- lateral_force_integral: None
- approach_alignment: 0.835
- goal_progress: 0.531
- terminal_score: 0.531
- phase_score: 0.659
- phase_breakdown.approach_score: 0.116
- phase_breakdown.push_score: 0.929
- phase_breakdown.contact_score: 0.571

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.608
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.595
- **Median Q (composite search score)**: 0.337
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.437


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `327b95871eb659cd41b4cf66bc0b4dfb3b240662e8501854b46ee2b8b86a04c5`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ffd2bb280d1d50ec9ffd23c1ed75abf73d645c1d10372a9b5bb6e9fac6e0bf8`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82034,"average_solve_count":295.0,"average_success_count":295.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.13527,"approach_1.approach_height":0.08609,"approach_1.approach_speed":0.08165,"contact_1.contact_force_threshold":18.58706,"contact_1.contact_speed":0.02019,"push_1.push_depth":0.02283,"push_1.push_speed":0.04861,"retract_1.retract_height":0.16876,"retract_1.retract_speed":0.02946},"optimized_scores":{"best_composite_score":0.34766,"best_fitness_score":0.60766,"best_task_score":0.53074},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":550.0,"contact_point_centroid":[0.53756,-0.04618,0.04712],"force_p95":178.5386,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":180.55058,"mean_force":134.06435,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52755,-0.04997,0.04793]},{"body_a":"world","body_b":"push_box","contact_count":1564.0,"contact_point_centroid":[0.53979,-0.04552,-0.00045],"force_p95":126.4562,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":139.19048,"mean_force":47.58768,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52876,-0.04277,0.04823]},{"body_a":"world","body_b":"push_box","contact_count":2020.0,"contact_point_centroid":[0.52846,-0.0947,-3e-05],"force_p95":0.31845,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.17211,"mean_force":0.26193,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49543,-0.12247,0.10258]},{"body_a":"attachment","body_b":"push_box","contact_count":33.0,"contact_point_centroid":[0.50438,-0.11308,0.04835],"force_p95":1.85371,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.29944,"mean_force":0.75975,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4963,-0.12354,0.0307]},{"body_a":"world","body_b":"push_box","contact_count":1924.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5192,0.03383,0.20502]},{"body_a":"world","body_b":"push_box","contact_count":1584.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53745,-0.0035,0.08152]}],"total_contact_groups":6},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52846,-0.09492,0.02499],"final_tcp_position":[0.49581,-0.12242,0.17691],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":180.55058,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1924.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53926,-0.00669,0.11345],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0906,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":46.76241,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53841,0.0002,0.05239],"tcp_start":[0.53926,-0.00669,0.11345],"tcp_to_object_dist_end":0.0381,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":581.0,"n_steps_budget":1000.0,"object_pos_end":[0.53027,-0.09146,0.02738],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.06594,"object_to_goal_dist_start":0.13211,"object_z_max":0.03495,"peak_contact_force":0.2233,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2114.0,"raw_peak_contact_force":180.55058,"subtask_id":"push","tcp_end":[0.4985,-0.12299,0.02769],"tcp_start":[0.53841,0.0002,0.05239],"tcp_to_object_dist_end":0.04476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.52846,-0.09492,0.02499],"object_pos_start":[0.53027,-0.09146,0.02738],"object_to_goal_dist_end":0.062,"object_to_goal_dist_start":0.06594,"object_z_max":0.02738,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2053.0,"raw_peak_contact_force":4.17211,"tcp_end":[0.49581,-0.12242,0.17691],"tcp_start":[0.4985,-0.12299,0.02769],"tcp_to_object_dist_end":0.1578,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77622,"average_solve_count":286.0,"average_success_count":286.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.29963,"approach_1.approach_height":0.05666,"approach_1.approach_speed":0.09809,"contact_1.contact_force_threshold":8.7179,"contact_1.contact_speed":0.00623,"push_1.push_depth":0.03498,"push_1.push_speed":0.07012,"retract_1.retract_height":0.14138,"retract_1.retract_speed":0.01437},"optimized_scores":{"best_composite_score":0.33704,"best_fitness_score":0.59704,"best_task_score":0.59478},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":526.0,"contact_point_centroid":[0.54035,-0.05775,0.04712],"force_p95":170.26314,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":171.7245,"mean_force":132.28697,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53013,-0.06159,0.048]},{"body_a":"world","body_b":"push_box","contact_count":1282.0,"contact_point_centroid":[0.54594,-0.05997,-0.00053],"force_p95":155.80401,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":167.1135,"mean_force":55.24588,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53227,-0.05427,0.04842]},{"body_a":"push_box","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.53176,-0.11318,0.06449],"force_p95":38.2158,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.92935,"mean_force":18.17033,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49737,-0.1276,0.03047]},{"body_a":"world","body_b":"push_box","contact_count":1626.0,"contact_point_centroid":[0.53305,-0.11056,-5e-05],"force_p95":0.26813,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.51129,"mean_force":0.26493,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48995,-0.13299,0.08882]},{"body_a":"world","body_b":"push_box","contact_count":1832.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52331,0.01275,0.19414]},{"body_a":"world","body_b":"push_box","contact_count":1120.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54576,-0.01632,0.07048]}],"total_contact_groups":6},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53335,-0.11066,0.02499],"final_tcp_position":[0.49021,-0.1329,0.14934],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1832.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54739,-0.01983,0.092],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06912,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1120.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54693,-0.01238,0.05247],"tcp_start":[0.54739,-0.01983,0.092],"tcp_to_object_dist_end":0.03649,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.53841,-0.10515,0.03092],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.05935,"object_to_goal_dist_start":0.12728,"object_z_max":0.03685,"peak_contact_force":0.64442,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1838.0,"raw_peak_contact_force":171.7245,"subtask_id":"push","tcp_end":[0.49308,-0.13357,0.02768],"tcp_start":[0.54693,-0.01238,0.05247],"tcp_to_object_dist_end":0.0536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.53335,-0.11066,0.02499],"object_pos_start":[0.53841,-0.10515,0.03092],"object_to_goal_dist_end":0.05158,"object_to_goal_dist_start":0.05935,"object_z_max":0.03092,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1626.0,"raw_peak_contact_force":3.51129,"tcp_end":[0.49021,-0.1329,0.14934],"tcp_start":[0.49308,-0.13357,0.02768],"tcp_to_object_dist_end":0.13349,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`; realized-scene SHA-256: `5de0d8cc5a3c16249bcf1097af6edba15dfacc79d06e3eed726605dcb01257b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45543,-9e-05,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04457,-0.14991,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45543,-9e-05,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55233,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.10849,"approach_1.approach_height":0.08079,"approach_1.approach_speed":0.22392,"contact_1.contact_force_threshold":8.6292,"contact_1.contact_speed":0.03171,"push_1.push_depth":0.02936,"push_1.push_speed":0.07413,"retract_1.retract_height":0.11152,"retract_1.retract_speed":0.03727},"optimized_scores":{"best_composite_score":0.32929,"best_fitness_score":0.58929,"best_task_score":0.50118},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":455.0,"contact_point_centroid":[0.4828,-0.02112,0.04706],"force_p95":174.87651,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":184.8433,"mean_force":142.33513,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47632,-0.02853,0.04712]},{"body_a":"world","body_b":"push_box","contact_count":962.0,"contact_point_centroid":[0.48986,-0.02959,-0.00072],"force_p95":169.36019,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":179.89267,"mean_force":68.09276,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47816,-0.03962,0.04404]},{"body_a":"world","body_b":"push_box","contact_count":1264.0,"contact_point_centroid":[0.51169,-0.07287,-3e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29579,"mean_force":0.24446,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49708,-0.12958,0.06826]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47832,0.05736,0.20953]},{"body_a":"world","body_b":"push_box","contact_count":1468.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45187,0.02219,0.08018]}],"total_contact_groups":5},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51169,-0.07287,0.02499],"final_tcp_position":[0.49699,-0.12938,0.11589],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":184.8433,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":450.0,"n_steps_budget":600.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.45453,0.01925,0.1092],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0864,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":367.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":45.48539,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1468.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.45158,0.02572,0.05244],"tcp_start":[0.45453,0.01925,0.1092],"tcp_to_object_dist_end":0.03788,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.51168,-0.07277,0.02415],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.07811,"object_to_goal_dist_start":0.1564,"object_z_max":0.03526,"peak_contact_force":0.30953,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1417.0,"raw_peak_contact_force":184.8433,"subtask_id":"push","tcp_end":[0.50013,-0.13007,0.02386],"tcp_start":[0.45158,0.02572,0.05244],"tcp_to_object_dist_end":0.05845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.51169,-0.07287,0.02499],"object_pos_start":[0.51168,-0.07277,0.02415],"object_to_goal_dist_end":0.07801,"object_to_goal_dist_start":0.07811,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1264.0,"raw_peak_contact_force":0.29579,"tcp_end":[0.49699,-0.12938,0.11589],"tcp_start":[0.50013,-0.13007,0.02386],"tcp_to_object_dist_end":0.10804,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```