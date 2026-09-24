## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5975 | 0.76 | ✅ accepted |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2573 | 0.42 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5784 | 0.71 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5817 | 0.73 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5886 | 0.74 | ❌ rejected |

**Proposal policy**: task_score is 0.76 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.597) — your mutation base

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

- **Composite score**: 0.597
- **task_score** (E): 0.760
- **fitness_score**: 0.807  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2776 |
| contact_1 | 1.00 | 1.00 | 0.0490 |
| push_1 | 1.00 | 1.00 | 0.1400 |
| retract_1 | 0.00 | 1.00 | 0.1679 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.059, 0.033) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.488, 0.059, 0.033)→(0.487, 0.011, 0.021) | (0.492, -0.018, 0.025)→(0.493, -0.026, 0.025) | 0.139→0.132 | 1.00 / 3.000 | 4.901 | 13.832 |
| push_1 | push | 1.00 / step_budget | (0.487, 0.011, 0.021)→(0.499, -0.123, 0.023) | (0.493, -0.026, 0.025)→(0.498, -0.147, 0.027) | 0.132→0.036 | 1.00 / 3.333 | 46.695 | 87.502 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.123, 0.023)→(0.496, 0.017, 0.116) | (0.498, -0.147, 0.027)→(0.493, -0.145, 0.025) | 0.036→0.033 | 1.00 / 4.000 | 0.245 | 26.782 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.456
- goal_progress: 0.879
- terminal_score: 0.879
- phase_score: 0.852
- phase_breakdown.approach_score: 0.823
- phase_breakdown.push_score: 0.853
- phase_breakdown.contact_score: 0.868

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.863
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.879
- **Median Q (composite search score)**: 0.585
- **K-run variance**: 0.0017
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.207


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28571,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07486,"approach_1.speed":0.05197,"push_1.push_distance":0.0986},"optimized_scores":{"best_composite_score":0.65258,"best_fitness_score":0.86258,"best_task_score":0.87886},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1091.0,"contact_point_centroid":[0.48806,-0.11049,-0.00012],"force_p95":58.0449,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.97508,"mean_force":17.69317,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4816,-0.06426,0.01985]},{"body_a":"attachment","body_b":"push_box","contact_count":698.0,"contact_point_centroid":[0.49116,-0.06721,0.03803],"force_p95":43.00869,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.7997,"mean_force":19.53471,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48003,-0.05568,0.02002]},{"body_a":"push_box","body_b":"link7","contact_count":388.0,"contact_point_centroid":[0.50167,-0.05018,0.05161],"force_p95":39.88914,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.92503,"mean_force":26.53915,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47437,-0.02645,0.02049]},{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.47026,-0.0027,0.02776],"force_p95":11.65746,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.26779,"mean_force":4.03605,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46687,0.00921,0.02209]},{"body_a":"world","body_b":"push_box","contact_count":1933.0,"contact_point_centroid":[0.47161,-0.02489,-1e-05],"force_p95":0.90386,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.67723,"mean_force":0.40394,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46618,0.03017,0.02606]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49272,-0.13478,0.02062],"force_p95":3.60025,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.67419,"mean_force":2.63947,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4943,-0.12296,0.01985]},{"body_a":"world","body_b":"push_box","contact_count":3979.0,"contact_point_centroid":[0.48846,-0.16056,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.53804,"mean_force":0.24796,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49207,-0.05582,0.07057]},{"body_a":"world","body_b":"push_box","contact_count":3728.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48362,0.02608,0.16649]}],"total_contact_groups":8},"final_pose_error":0.13939,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48844,-0.16053,0.02499],"final_tcp_position":[0.49373,0.0155,0.11395],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":70.97508,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":932.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3728.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46884,0.05267,0.03388],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.47306,-0.03185,0.02485],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12118,"object_to_goal_dist_start":0.12903,"object_z_max":0.02517,"peak_contact_force":0.56942,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2008.0,"raw_peak_contact_force":16.26779,"tcp_end":[0.46711,0.00512,0.02141],"tcp_start":[0.46884,0.05267,0.03388],"tcp_to_object_dist_end":0.03761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.4894,-0.15945,0.02489],"object_pos_start":[0.47306,-0.03185,0.02485],"object_to_goal_dist_end":0.0142,"object_to_goal_dist_start":0.12118,"object_z_max":0.03437,"peak_contact_force":8.78775,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2177.0,"raw_peak_contact_force":70.97508,"tcp_end":[0.49433,-0.12288,0.01987],"tcp_start":[0.46711,0.00512,0.02141],"tcp_to_object_dist_end":0.03724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48844,-0.16053,0.02499],"object_pos_start":[0.4894,-0.15945,0.02489],"object_to_goal_dist_end":0.01563,"object_to_goal_dist_start":0.0142,"object_z_max":0.02505,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3982.0,"raw_peak_contact_force":3.67419,"tcp_end":[0.49373,0.0155,0.11395],"tcp_start":[0.49433,-0.12288,0.01987],"tcp_to_object_dist_end":0.1973,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48045,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17144,"approach_1.speed":0.0622,"push_1.push_distance":0.09127},"optimized_scores":{"best_composite_score":0.55457,"best_fitness_score":0.76457,"best_task_score":0.64172},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1358.0,"contact_point_centroid":[0.45877,-0.10946,-8e-05],"force_p95":38.72028,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.87303,"mean_force":7.60211,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47232,-0.07155,0.01959]},{"body_a":"attachment","body_b":"push_box","contact_count":621.0,"contact_point_centroid":[0.47299,-0.06748,0.03306],"force_p95":29.11141,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.20268,"mean_force":11.68869,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46641,-0.05604,0.01969]},{"body_a":"push_box","body_b":"link7","contact_count":259.0,"contact_point_centroid":[0.48101,-0.04486,0.05065],"force_p95":25.38897,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.29453,"mean_force":17.62048,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45363,-0.02188,0.02018]},{"body_a":"attachment","body_b":"push_box","contact_count":83.0,"contact_point_centroid":[0.45263,-0.01024,0.0325],"force_p95":10.55347,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.35674,"mean_force":3.52397,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44607,0.00166,0.02247]},{"body_a":"world","body_b":"push_box","contact_count":1924.0,"contact_point_centroid":[0.4503,-0.0325,-1e-05],"force_p95":1.09424,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.80703,"mean_force":0.39939,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44583,0.02314,0.02673]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.48659,-0.13309,0.02291],"force_p95":3.7202,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.90135,"mean_force":2.08987,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49312,-0.12351,0.01984]},{"body_a":"world","body_b":"push_box","contact_count":3975.0,"contact_point_centroid":[0.45494,-0.14031,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.09161,"mean_force":0.24698,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49127,-0.05599,0.07075]},{"body_a":"world","body_b":"push_box","contact_count":3628.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47376,0.02258,0.16685]}],"total_contact_groups":8},"final_pose_error":0.13944,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45499,-0.14041,0.02499],"final_tcp_position":[0.4932,0.01544,0.11408],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":52.87303,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":907.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3628.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4489,0.04563,0.03449],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0778,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.45157,-0.03913,0.02503],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12099,"object_to_goal_dist_start":0.12843,"object_z_max":0.02507,"peak_contact_force":6.75824,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2007.0,"raw_peak_contact_force":13.35674,"tcp_end":[0.44619,-0.00225,0.02177],"tcp_start":[0.4489,0.04563,0.03449],"tcp_to_object_dist_end":0.03741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.45569,-0.13995,0.02501],"object_pos_start":[0.45157,-0.03913,0.02503],"object_to_goal_dist_end":0.04543,"object_to_goal_dist_start":0.12099,"object_z_max":0.03085,"peak_contact_force":0.49902,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2238.0,"raw_peak_contact_force":52.87303,"tcp_end":[0.49325,-0.1234,0.01986],"tcp_start":[0.44619,-0.00225,0.02177],"tcp_to_object_dist_end":0.04137,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45499,-0.14041,0.02499],"object_pos_start":[0.45569,-0.13995,0.02501],"object_to_goal_dist_end":0.04601,"object_to_goal_dist_start":0.04543,"object_z_max":0.02502,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3977.0,"raw_peak_contact_force":3.90135,"tcp_end":[0.4932,0.01544,0.11408],"tcp_start":[0.49325,-0.1234,0.01986],"tcp_to_object_dist_end":0.18354,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81176,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28323,"approach_1.speed":0.07864,"push_1.push_distance":0.13651},"optimized_scores":{"best_composite_score":0.58532,"best_fitness_score":0.79532,"best_task_score":0.76029},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":985.0,"contact_point_centroid":[0.56249,-0.05894,0.05464],"force_p95":132.05822,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.65732,"mean_force":87.22458,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52795,-0.04666,0.02415]},{"body_a":"world","body_b":"push_box","contact_count":1887.0,"contact_point_centroid":[0.55995,-0.09305,-0.00039],"force_p95":102.14389,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.30228,"mean_force":58.39845,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52742,-0.0492,0.02443]},{"body_a":"attachment","body_b":"push_box","contact_count":993.0,"contact_point_centroid":[0.5475,-0.05345,0.05382],"force_p95":90.77667,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.34046,"mean_force":58.08763,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52811,-0.04602,0.02412]},{"body_a":"push_box","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.55171,-0.12614,0.05711],"force_p95":50.52816,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.76965,"mean_force":20.66453,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50884,-0.12166,0.03095]},{"body_a":"world","body_b":"push_box","contact_count":3593.0,"contact_point_centroid":[0.53682,-0.13408,-2e-05],"force_p95":0.45638,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.29758,"mean_force":0.4465,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50367,-0.04846,0.08255]},{"body_a":"attachment","body_b":"push_box","contact_count":99.0,"contact_point_centroid":[0.5296,-0.11639,0.05962],"force_p95":30.08093,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.43447,"mean_force":6.66834,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50715,-0.11369,0.03628]},{"body_a":"attachment","body_b":"push_box","contact_count":92.0,"contact_point_centroid":[0.5539,0.02251,0.038],"force_p95":10.36985,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.87216,"mean_force":3.36576,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5476,0.03445,0.02024]},{"body_a":"world","body_b":"push_box","contact_count":1882.0,"contact_point_centroid":[0.55322,-0.00045,-1e-05],"force_p95":1.04389,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.3661,"mean_force":0.41617,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5452,0.056,0.02332]},{"body_a":"world","body_b":"push_box","contact_count":3900.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52232,0.03848,0.16433]}],"total_contact_groups":9},"final_pose_error":0.13494,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53483,-0.13369,0.02499],"final_tcp_position":[0.50139,0.01862,0.11923],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":138.65732,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":975.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3900.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5466,0.07724,0.03104],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55444,-0.00622,0.02516],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15374,"object_to_goal_dist_start":0.16043,"object_z_max":0.02518,"peak_contact_force":7.37541,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1974.0,"raw_peak_contact_force":11.87216,"tcp_end":[0.54818,0.03046,0.01981],"tcp_start":[0.5466,0.07724,0.03104],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54782,-0.1413,0.03091],"object_pos_start":[0.55444,-0.00622,0.02516],"object_to_goal_dist_end":0.04896,"object_to_goal_dist_start":0.15374,"object_z_max":0.03111,"peak_contact_force":130.7993,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3865.0,"raw_peak_contact_force":138.65732,"tcp_end":[0.51013,-0.12391,0.02949],"tcp_start":[0.54818,0.03046,0.01981],"tcp_to_object_dist_end":0.04153,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53483,-0.13369,0.02499],"object_pos_start":[0.54782,-0.1413,0.03091],"object_to_goal_dist_end":0.03846,"object_to_goal_dist_start":0.04896,"object_z_max":0.0332,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3734.0,"raw_peak_contact_force":72.76965,"tcp_end":[0.50139,0.01862,0.11923],"tcp_start":[0.51013,-0.12391,0.02949],"tcp_to_object_dist_end":0.18221,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```