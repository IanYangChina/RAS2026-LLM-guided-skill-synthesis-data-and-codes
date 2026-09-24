## Search State

- **Seed**: 8
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.0999 | 0.20 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.4443 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`
- Frozen object start: [0.4792366731926673, 0.05847322120055107, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.4792366731926673, 0.05847322120055107, 0.025)
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
  frozen_object_start: [0.4792, 0.0585, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.4792366731926673, 0.05847322120055107, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0208, -0.2085, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be

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

## Current Skill (Q=-0.100) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
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
  control: impedance_control
  termination: contact_detected
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
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
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
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: -0.100
- **task_score** (E): 0.201
- **fitness_score**: 0.310  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2134 |
| contact | 1.00 | 1.00 | 0.0805 |
| push | 0.33 | 1.00 | 0.0493 |
| retract | 1.00 | 1.00 | 0.1429 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.071, 0.107) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / force_exceeded | (0.520, 0.071, 0.107)→(0.521, 0.036, 0.035) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 5.000 | 20.933 | 0.245 |
| push | push | 0.33 / guard_failure | (0.520, 0.028, 0.033)→(0.498, -0.016, 0.032) | (0.526, -0.001, 0.025)→(0.520, -0.028, 0.025) | 0.156→0.129 | 1.00 / 4.000 | 4.826 | 30.860 |
| retract | retract | 1.00 / step_budget | (0.498, -0.016, 0.032)→(0.495, -0.015, 0.175) | (0.520, -0.028, 0.025)→(0.519, -0.029, 0.025) | 0.129→0.128 | 1.00 / 4.000 | 0.245 | 5.754 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.481
- lateral_force_integral: None
- approach_alignment: 0.824
- goal_progress: 0.473
- terminal_score: 0.473
- phase_score: 0.616
- phase_breakdown.contact_score: 0.749
- phase_breakdown.approach_score: 0.230
- phase_breakdown.push_score: 0.691

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.559
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.473
- **Median Q (composite search score)**: -0.219
- **K-run variance**: 0.0310
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.339


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8267fcc1127ab3c529e380fe6aea430def9956719b146bd9818eb52355cb895d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33d626702a3717cebb1eda35e1cb80c1c9d108c246efccd193577b9105813420`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83103,"average_solve_count":290.0,"average_success_count":290.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.0909,"approach.pose_tol":0.03657,"approach.speed":0.06264,"contact.force_threshold":5.60565,"contact.speed":0.02109,"push.force_guard_threshold":24.19014,"push.push_distance":0.11519,"push.push_speed":0.06892,"push.push_tolerance":0.02832,"retract.pose_tol":0.02632,"retract.retract_height":0.17489,"retract.retract_speed":0.03233},"optimized_scores":{"best_composite_score":-0.22985,"best_fitness_score":0.18015,"best_task_score":0.11102},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.47528,0.0715,0.04388],"force_p95":21.87925,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.40001,"mean_force":8.27037,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47417,0.08343,0.04043]},{"body_a":"world","body_b":"push_box","contact_count":221.0,"contact_point_centroid":[0.48053,0.04128,-6e-05],"force_p95":10.4224,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.23189,"mean_force":3.15639,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.47416,0.08289,0.04036]},{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.47685,0.06074,0.04831],"force_p95":4.20673,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.49223,"mean_force":1.13352,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47426,0.07256,0.03931]},{"body_a":"world","body_b":"push_box","contact_count":1380.0,"contact_point_centroid":[0.47942,0.03504,-1e-05],"force_p95":0.24538,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.97272,"mean_force":0.25162,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47197,0.07225,0.11193]},{"body_a":"world","body_b":"push_box","contact_count":1784.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48881,0.0607,0.21504]},{"body_a":"world","body_b":"push_box","contact_count":2332.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.4756,0.10969,0.08496]}],"total_contact_groups":6},"final_pose_error":0.02611,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47938,0.0351,0.02499],"final_tcp_position":[0.47219,0.0723,0.18828],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":32.40001,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1784.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47858,0.12412,0.12951],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":16.78456,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2332.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.47536,0.09544,0.04318],"tcp_start":[0.47858,0.12412,0.12951],"tcp_to_object_dist_end":0.04138,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":119.0,"n_steps_budget":1000.0,"object_pos_end":[0.47927,0.03649,0.02483],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.18764,"object_to_goal_dist_start":0.2095,"object_z_max":0.02533,"peak_contact_force":0.00097,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":296.0,"raw_peak_contact_force":32.40001,"subtask_id":"push","tcp_end":[0.47438,0.07269,0.03941],"tcp_start":[0.47439,0.07277,0.03944],"tcp_to_object_dist_end":0.03933,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":350.0,"n_steps_budget":1000.0,"object_pos_end":[0.47938,0.0351,0.02499],"object_pos_start":[0.47936,0.03626,0.02496],"object_to_goal_dist_end":0.18625,"object_to_goal_dist_start":0.1874,"object_z_max":0.02511,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1386.0,"raw_peak_contact_force":5.49223,"tcp_end":[0.47219,0.0723,0.18828],"tcp_start":[0.47438,0.07269,0.03941],"tcp_to_object_dist_end":0.16763,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67273,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.05124,"approach.pose_tol":0.03029,"approach.speed":0.11144,"contact.force_threshold":4.99829,"contact.speed":0.06216,"push.force_guard_threshold":24.63564,"push.push_distance":0.23706,"push.push_speed":0.07693,"push.push_tolerance":0.02308,"retract.pose_tol":0.01967,"retract.retract_height":0.16664,"retract.retract_speed":0.10323},"optimized_scores":{"best_composite_score":-0.21876,"best_fitness_score":0.19124,"best_task_score":0.02012},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.53829,-0.00113,0.03009],"force_p95":31.70045,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.2651,"mean_force":18.61211,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.53824,0.01081,0.03009]},{"body_a":"world","body_b":"push_box","contact_count":28.0,"contact_point_centroid":[0.54397,-0.02608,-5e-05],"force_p95":10.09384,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.96919,"mean_force":4.23272,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.53819,0.01077,0.03003]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.53765,-0.00171,0.02953],"force_p95":10.71246,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.52475,"mean_force":5.32764,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.53755,0.01023,0.02953]},{"body_a":"world","body_b":"push_box","contact_count":1869.0,"contact_point_centroid":[0.54306,-0.02794,-2e-05],"force_p95":0.24598,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44605,"mean_force":0.25641,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5344,0.01012,0.10305]},{"body_a":"world","body_b":"push_box","contact_count":1692.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5174,0.02367,0.19788]},{"body_a":"world","body_b":"push_box","contact_count":2536.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.53631,0.02889,0.05829]}],"total_contact_groups":6},"final_pose_error":0.01963,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54296,-0.02788,0.02499],"final_tcp_position":[0.53479,0.01016,0.17684],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":33.2651,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":423.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1692.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53679,0.04855,0.09368],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":634.0,"n_steps_budget":840.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":23.84105,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2536.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53891,0.01138,0.03063],"tcp_start":[0.53679,0.04855,0.09368],"tcp_to_object_dist_end":0.03779,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.54379,-0.02629,0.02483],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13123,"object_to_goal_dist_start":0.13211,"object_z_max":0.0251,"peak_contact_force":14.23224,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":34.0,"raw_peak_contact_force":33.2651,"subtask_id":"push","tcp_end":[0.53765,0.01028,0.02962],"tcp_start":[0.53773,0.01035,0.02971],"tcp_to_object_dist_end":0.03739,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.54296,-0.02788,0.02499],"object_pos_start":[0.54377,-0.0265,0.02491],"object_to_goal_dist_end":0.12945,"object_to_goal_dist_start":0.13103,"object_z_max":0.0252,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1872.0,"raw_peak_contact_force":11.52475,"tcp_end":[0.53479,0.01016,0.17684],"tcp_start":[0.53765,0.01028,0.02962],"tcp_to_object_dist_end":0.15676,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48649,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.05575,"approach.pose_tol":0.03234,"approach.speed":0.09243,"contact.force_threshold":3.39797,"contact.speed":0.06906,"push.force_guard_threshold":28.73285,"push.push_distance":0.15521,"push.push_speed":0.0414,"push.push_tolerance":0.02925,"retract.pose_tol":0.01998,"retract.retract_height":0.15216,"retract.retract_speed":0.09687},"optimized_scores":{"best_composite_score":0.14893,"best_fitness_score":0.55893,"best_task_score":0.473},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":507.0,"contact_point_centroid":[0.53081,-0.06238,0.04981],"force_p95":16.05063,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.91397,"mean_force":3.74548,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51842,-0.0538,0.02603]},{"body_a":"world","body_b":"push_box","contact_count":1463.0,"contact_point_centroid":[0.55515,-0.08749,-4e-05],"force_p95":7.26926,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.82087,"mean_force":1.726,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50797,-0.07564,0.02607]},{"body_a":"world","body_b":"push_box","contact_count":1696.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52183,0.01947,0.20014]},{"body_a":"world","body_b":"push_box","contact_count":2412.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.54592,0.02028,0.0609]},{"body_a":"world","body_b":"push_box","contact_count":1612.0,"contact_point_centroid":[0.53589,-0.09333,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.47917,-0.12891,0.0913]}],"total_contact_groups":5},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53589,-0.09333,0.02499],"final_tcp_position":[0.47935,-0.12886,0.15859],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":26.91397,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":424.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1696.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54599,0.04002,0.09779],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":603.0,"n_steps_budget":780.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":22.17229,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54902,0.0019,0.03075],"tcp_start":[0.54599,0.04002,0.09779],"tcp_to_object_dist_end":0.03786,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":786.0,"n_steps_budget":1000.0,"object_pos_end":[0.53589,-0.09333,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.06708,"object_to_goal_dist_start":0.12728,"object_z_max":0.02922,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1970.0,"raw_peak_contact_force":26.91397,"subtask_id":"push","tcp_end":[0.48211,-0.1295,0.02604],"tcp_start":[0.54902,0.0019,0.03075],"tcp_to_object_dist_end":0.06481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":403.0,"n_steps_budget":990.0,"object_pos_end":[0.53589,-0.09333,0.02499],"object_pos_start":[0.53589,-0.09333,0.02499],"object_to_goal_dist_end":0.06708,"object_to_goal_dist_start":0.06708,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1612.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47935,-0.12886,0.15859],"tcp_start":[0.48211,-0.1295,0.02604],"tcp_to_object_dist_end":0.14936,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```