## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2573 | 0.42 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5784 | 0.71 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5817 | 0.73 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5886 | 0.74 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1308 | 0.00 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`
- Frozen object start: [0.47139345610991795, -0.0241810627903052, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.47139345610991795, -0.0241810627903052, 0.025)
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
  frozen_object_start: [0.4714, -0.0242, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.47139345610991795, -0.0241810627903052, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0286, -0.1258, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14

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

## Current Skill (Q=0.257) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: impedance_motion
  control: admittance_control
  termination: contact_detected
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.257
- **task_score** (E): 0.423
- **fitness_score**: 0.367  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1936 |
| contact_1 | 1.00 | 1.00 | 0.0943 |
| push_1 | 0.00 | 0.67 | 0.0321 |
| retract_1 | 0.00 | 1.00 | 0.1946 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, 0.057, 0.121) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.490, 0.057, 0.121)→(0.487, 0.019, 0.035) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 16.111 | 0.245 |
| push_1 | push | 0.00 / guard_failure | (0.488, 0.014, 0.034)→(0.503, -0.014, 0.031) | (0.492, -0.018, 0.025)→(0.499, -0.049, 0.026) | 0.139→0.107 | 0.67 / 1.333 | 4.012 | 48.681 |
| retract_1 | retract | 0.00 / step_budget | (0.503, -0.014, 0.031)→(0.498, 0.091, 0.192) | (0.499, -0.050, 0.026)→(0.507, -0.094, 0.025) | 0.107→0.084 | 1.00 / 4.000 | 0.245 | 6.418 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.364
- goal_progress: 0.680
- terminal_score: 0.680
- phase_score: 0.419
- phase_breakdown.approach_score: 0.109
- phase_breakdown.push_score: 0.376
- phase_breakdown.contact_score: 0.696

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.523
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.680
- **Median Q (composite search score)**: 0.264
- **K-run variance**: 0.0170
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.304


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `27920116be2b9a598fe307ae470bb0295293d051bb1ef513a0996a4d851f2459`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1a1e2536715050e6c37d8aed13e4ecd62004f6234f1413b07d7b475a233f55c9`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01695,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11097,"approach_1.speed":0.10675,"contact_1.contact_force_threshold":3.48682,"push_1.force_limit_threshold":25.05415,"push_1.push_distance":0.11509,"retract_1.retract_arc_height":0.12089},"optimized_scores":{"best_composite_score":0.26444,"best_fitness_score":0.37444,"best_task_score":0.54387},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":15.0,"contact_point_centroid":[0.46897,-0.00388,0.04146],"force_p95":35.81603,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.07976,"mean_force":12.3968,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46842,0.00801,0.03831]},{"body_a":"world","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.47518,-0.03433,-4e-05],"force_p95":31.79189,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.39983,"mean_force":8.24267,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46837,0.00847,0.03847]},{"body_a":"world","body_b":"push_box","contact_count":3742.0,"contact_point_centroid":[0.48934,-0.09271,-3e-05],"force_p95":0.2584,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.43231,"mean_force":0.26543,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47632,0.08758,0.10752]},{"body_a":"world","body_b":"push_box","contact_count":2076.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48484,0.02497,0.22239]},{"body_a":"world","body_b":"push_box","contact_count":2456.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46785,0.03186,0.09036]}],"total_contact_groups":5},"final_pose_error":0.14292,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48938,-0.09211,0.02499],"final_tcp_position":[0.48825,0.11059,0.21023],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":61.07976,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":519.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2076.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.47068,0.05114,0.14452],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14128,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":614.0,"n_steps_budget":810.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":11.73508,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2456.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.46761,0.01279,0.03965],"tcp_start":[0.47068,0.05114,0.14452],"tcp_to_object_dist_end":0.03995,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":22.0,"n_steps_budget":1000.0,"object_pos_end":[0.47329,-0.03775,0.02552],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.11539,"object_to_goal_dist_start":0.12903,"object_z_max":0.02552,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":36.0,"raw_peak_contact_force":61.07976,"subtask_id":"push","tcp_end":[0.47116,-0.00166,0.03704],"tcp_start":[0.47092,-0.00052,0.03713],"tcp_to_object_dist_end":0.03794,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48938,-0.09211,0.02499],"object_pos_start":[0.47365,-0.0394,0.02598],"object_to_goal_dist_end":0.05885,"object_to_goal_dist_start":0.1137,"object_z_max":0.02924,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3742.0,"raw_peak_contact_force":4.43231,"tcp_end":[0.48825,0.11059,0.21023],"tcp_start":[0.47116,-0.00166,0.03704],"tcp_to_object_dist_end":0.2746,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.925,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10172,"approach_1.speed":0.0824,"contact_1.contact_force_threshold":6.4022,"push_1.force_limit_threshold":25.21727,"push_1.push_distance":0.09765,"retract_1.retract_arc_height":0.07832},"optimized_scores":{"best_composite_score":0.41329,"best_fitness_score":0.52329,"best_task_score":0.68034},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":40.0,"contact_point_centroid":[0.45899,-0.03396,0.03498],"force_p95":14.59015,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.33583,"mean_force":3.94571,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46219,-0.02327,0.03427]},{"body_a":"world","body_b":"push_box","contact_count":41.0,"contact_point_centroid":[0.44808,-0.05207,-9e-05],"force_p95":10.63685,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.84357,"mean_force":3.2011,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45414,-0.00905,0.03578]},{"body_a":"world","body_b":"push_box","contact_count":3778.0,"contact_point_centroid":[0.47897,-0.18511,-2e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.52827,"mean_force":0.27253,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49119,-0.00439,0.0813]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.48587,-0.08737,0.03072],"force_p95":10.71137,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.97656,"mean_force":4.89592,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49558,-0.08147,0.02858]},{"body_a":"world","body_b":"push_box","contact_count":2236.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47528,0.02175,0.21806]},{"body_a":"world","body_b":"push_box","contact_count":2384.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44774,0.02489,0.08551]}],"total_contact_groups":6},"final_pose_error":0.14692,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47895,-0.18525,0.02499],"final_tcp_position":[0.49359,0.04086,0.15902],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":21.33583,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":559.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2236.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.45116,0.04451,0.13581],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":596.0,"n_steps_budget":780.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":8.10987,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2384.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.44685,0.00536,0.03816],"tcp_start":[0.45116,0.04451,0.13581],"tcp_to_object_dist_end":0.03937,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.47222,-0.10974,0.02609],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.04893,"object_to_goal_dist_start":0.12843,"object_z_max":0.02829,"peak_contact_force":0.09395,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":81.0,"raw_peak_contact_force":21.33583,"subtask_id":"push","tcp_end":[0.49304,-0.07673,0.02892],"tcp_start":[0.44685,0.00536,0.03816],"tcp_to_object_dist_end":0.03913,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47895,-0.18525,0.02499],"object_pos_start":[0.47222,-0.10974,0.02609],"object_to_goal_dist_end":0.04105,"object_to_goal_dist_start":0.04893,"object_z_max":0.02689,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3783.0,"raw_peak_contact_force":13.52827,"tcp_end":[0.49359,0.04086,0.15902],"tcp_start":[0.49304,-0.07673,0.02892],"tcp_to_object_dist_end":0.26326,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.94595,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05139,"approach_1.speed":0.11205,"contact_1.contact_force_threshold":6.0553,"push_1.force_limit_threshold":24.01922,"push_1.push_distance":0.09714,"retract_1.retract_arc_height":0.16894},"optimized_scores":{"best_composite_score":0.09416,"best_fitness_score":0.20416,"best_task_score":0.04613},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.54873,0.02545,0.03536],"force_p95":44.95207,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.62698,"mean_force":12.42278,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54698,0.03737,0.02798]},{"body_a":"world","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.55267,-0.00267,-4e-05],"force_p95":24.82278,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.9091,"mean_force":6.97785,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54692,0.03728,0.02797]},{"body_a":"world","body_b":"push_box","contact_count":3947.0,"contact_point_centroid":[0.55178,-0.00602,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.29373,"mean_force":0.24866,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52905,0.10494,0.10241]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.5511,0.02347,0.05015],"force_p95":0.47569,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52855,"mean_force":0.17618,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54579,0.03531,0.02738]},{"body_a":"world","body_b":"push_box","contact_count":3176.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52236,0.03809,0.19008]},{"body_a":"world","body_b":"push_box","contact_count":1864.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54571,0.05703,0.05272]}],"total_contact_groups":6},"final_pose_error":0.15437,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55167,-0.00596,0.02499],"final_tcp_position":[0.51233,0.12202,0.20625],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":63.62698,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":794.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3176.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54671,0.07667,0.08209],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":466.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":28.48659,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1864.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.5478,0.03832,0.02855],"tcp_start":[0.54671,0.07667,0.08209],"tcp_to_object_dist_end":0.03751,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.55205,-0.00064,0.02496],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15817,"object_to_goal_dist_start":0.16043,"object_z_max":0.0251,"peak_contact_force":11.94094,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":25.0,"raw_peak_contact_force":63.62698,"subtask_id":"push","tcp_end":[0.54588,0.03558,0.02747],"tcp_start":[0.54601,0.03597,0.02757],"tcp_to_object_dist_end":0.03683,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55167,-0.00596,0.02499],"object_pos_start":[0.55203,-0.00108,0.02511],"object_to_goal_dist_end":0.15303,"object_to_goal_dist_start":0.15775,"object_z_max":0.02543,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3950.0,"raw_peak_contact_force":1.29373,"tcp_end":[0.51233,0.12202,0.20625],"tcp_start":[0.54588,0.03558,0.02747],"tcp_to_object_dist_end":0.22535,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```