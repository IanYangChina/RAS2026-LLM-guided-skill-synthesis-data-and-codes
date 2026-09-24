## Search State

- **Seed**: 2
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5938 | 0.75 | ❌ rejected |
| 13 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5829 | 0.74 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5838 | 0.72 | ✅ accepted |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.1150 | 0.00 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5971 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.75 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.594) — your mutation base

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

- **Composite score**: 0.594
- **task_score** (E): 0.751
- **fitness_score**: 0.804  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2777 |
| contact_1 | 1.00 | 1.00 | 0.0490 |
| push_1 | 1.00 | 1.00 | 0.1390 |
| retract_1 | 0.00 | 1.00 | 0.1673 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.488, 0.059, 0.033) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.488, 0.059, 0.033)→(0.487, 0.011, 0.021) | (0.492, -0.018, 0.025)→(0.493, -0.026, 0.025) | 0.139→0.132 | 1.00 / 3.333 | 3.169 | 14.001 |
| push_1 | push | 1.00 / step_budget | (0.487, 0.011, 0.021)→(0.499, -0.122, 0.023) | (0.493, -0.026, 0.025)→(0.497, -0.146, 0.027) | 0.132→0.037 | 1.00 / 2.333 | 43.366 | 87.338 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.122, 0.023)→(0.496, 0.017, 0.116) | (0.497, -0.146, 0.027)→(0.492, -0.144, 0.025) | 0.037→0.035 | 1.00 / 4.000 | 0.245 | 27.440 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.456
- goal_progress: 0.847
- terminal_score: 0.847
- phase_score: 0.851
- phase_breakdown.contact_score: 0.868
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.852

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.849
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.847
- **Median Q (composite search score)**: 0.581
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.253


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30601,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21893,"approach_1.speed":0.05919,"push_1.push_distance":0.09828},"optimized_scores":{"best_composite_score":0.63937,"best_fitness_score":0.84937,"best_task_score":0.84694},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1216.0,"contact_point_centroid":[0.48404,-0.11018,-0.0001],"force_p95":52.53615,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.79144,"mean_force":11.62106,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48147,-0.06574,0.01951]},{"body_a":"attachment","body_b":"push_box","contact_count":685.0,"contact_point_centroid":[0.48689,-0.06657,0.03301],"force_p95":37.37537,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.96122,"mean_force":14.58377,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47929,-0.05488,0.01962]},{"body_a":"push_box","body_b":"link7","contact_count":260.0,"contact_point_centroid":[0.49965,-0.04092,0.05097],"force_p95":35.83766,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.19502,"mean_force":26.37887,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47165,-0.01585,0.02027]},{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.47026,-0.0027,0.02776],"force_p95":11.66263,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.2738,"mean_force":4.03713,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46687,0.00921,0.02209]},{"body_a":"world","body_b":"push_box","contact_count":1933.0,"contact_point_centroid":[0.47161,-0.02489,-1e-05],"force_p95":0.90389,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.67929,"mean_force":0.40398,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46618,0.03017,0.02607]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49144,-0.13414,0.02125],"force_p95":0.67753,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.67753,"mean_force":0.67753,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49433,-0.12259,0.01987]},{"body_a":"world","body_b":"push_box","contact_count":3990.0,"contact_point_centroid":[0.48205,-0.15823,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.67455,"mean_force":0.24603,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49208,-0.0558,0.07041]},{"body_a":"world","body_b":"push_box","contact_count":3712.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48363,0.02607,0.16655]}],"total_contact_groups":8},"final_pose_error":0.13927,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48205,-0.15825,0.02499],"final_tcp_position":[0.49373,0.01563,0.11392],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":67.79144,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":928.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3712.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46884,0.05267,0.03389],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.47306,-0.03185,0.02485],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12118,"object_to_goal_dist_start":0.12903,"object_z_max":0.02517,"peak_contact_force":0.56944,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2008.0,"raw_peak_contact_force":16.2738,"tcp_end":[0.46711,0.00512,0.02141],"tcp_start":[0.46884,0.05267,0.03389],"tcp_to_object_dist_end":0.03761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.4825,-0.15752,0.02512],"object_pos_start":[0.47306,-0.03185,0.02485],"object_to_goal_dist_end":0.01905,"object_to_goal_dist_start":0.12118,"object_z_max":0.02975,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2161.0,"raw_peak_contact_force":67.79144,"tcp_end":[0.49433,-0.12259,0.01987],"tcp_start":[0.46711,0.00512,0.02141],"tcp_to_object_dist_end":0.03725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48205,-0.15825,0.02499],"object_pos_start":[0.4825,-0.15752,0.02512],"object_to_goal_dist_end":0.01975,"object_to_goal_dist_start":0.01905,"object_z_max":0.02512,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3991.0,"raw_peak_contact_force":0.67753,"tcp_end":[0.49373,0.01563,0.11392],"tcp_start":[0.49433,-0.12259,0.01987],"tcp_to_object_dist_end":0.19565,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7987,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11814,"approach_1.speed":0.08554,"push_1.push_distance":0.0889},"optimized_scores":{"best_composite_score":0.56138,"best_fitness_score":0.77138,"best_task_score":0.66631},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1326.0,"contact_point_centroid":[0.45939,-0.11015,-8e-05],"force_p95":40.31295,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.91008,"mean_force":7.98009,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47266,-0.07103,0.01959]},{"body_a":"attachment","body_b":"push_box","contact_count":613.0,"contact_point_centroid":[0.47432,-0.06717,0.03428],"force_p95":29.66351,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.3815,"mean_force":11.84878,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46675,-0.05567,0.01974]},{"body_a":"push_box","body_b":"link7","contact_count":260.0,"contact_point_centroid":[0.48133,-0.0454,0.05075],"force_p95":25.8631,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.79896,"mean_force":19.09342,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45392,-0.0218,0.02025]},{"body_a":"attachment","body_b":"push_box","contact_count":81.0,"contact_point_centroid":[0.4514,-0.01027,0.03057],"force_p95":10.59521,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.83227,"mean_force":3.96331,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44606,0.00162,0.02243]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48689,-0.13105,0.0228],"force_p95":8.34507,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.34507,"mean_force":8.34507,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49318,-0.12129,0.01983]},{"body_a":"world","body_b":"push_box","contact_count":1934.0,"contact_point_centroid":[0.45026,-0.03237,-1e-05],"force_p95":1.74588,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.85065,"mean_force":0.41245,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4458,0.02303,0.02658]},{"body_a":"world","body_b":"push_box","contact_count":3975.0,"contact_point_centroid":[0.45792,-0.1419,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.3191,"mean_force":0.24809,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49126,-0.05439,0.0706]},{"body_a":"world","body_b":"push_box","contact_count":3460.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47377,0.0226,0.16676]}],"total_contact_groups":8},"final_pose_error":0.13855,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45792,-0.14186,0.02499],"final_tcp_position":[0.4932,0.01642,0.11386],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":54.91008,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":865.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3460.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44887,0.04567,0.03427],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.45153,-0.03914,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12099,"object_to_goal_dist_start":0.12843,"object_z_max":0.02505,"peak_contact_force":7.82832,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2015.0,"raw_peak_contact_force":13.83227,"tcp_end":[0.4462,-0.00219,0.02177],"tcp_start":[0.44887,0.04567,0.03427],"tcp_to_object_dist_end":0.03747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.45929,-0.14112,0.02499],"object_pos_start":[0.45153,-0.03914,0.02499],"object_to_goal_dist_end":0.04167,"object_to_goal_dist_start":0.12099,"object_z_max":0.03181,"peak_contact_force":0.21366,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2199.0,"raw_peak_contact_force":54.91008,"tcp_end":[0.49325,-0.12117,0.01987],"tcp_start":[0.4462,-0.00219,0.02177],"tcp_to_object_dist_end":0.03972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45792,-0.14186,0.02499],"object_pos_start":[0.45929,-0.14112,0.02499],"object_to_goal_dist_end":0.04286,"object_to_goal_dist_start":0.04167,"object_z_max":0.02515,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3976.0,"raw_peak_contact_force":8.34507,"tcp_end":[0.4932,0.01642,0.11386],"tcp_start":[0.49325,-0.12117,0.01987],"tcp_to_object_dist_end":0.18492,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81395,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.28604,"approach_1.speed":0.07628,"push_1.push_distance":0.135},"optimized_scores":{"best_composite_score":0.58067,"best_fitness_score":0.79067,"best_task_score":0.73896},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":989.0,"contact_point_centroid":[0.56404,-0.05679,0.05447],"force_p95":131.22933,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.31324,"mean_force":89.48621,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52836,-0.04535,0.0244]},{"body_a":"world","body_b":"push_box","contact_count":1936.0,"contact_point_centroid":[0.56174,-0.08941,-0.00039],"force_p95":100.70577,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.09184,"mean_force":58.55996,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52811,-0.04658,0.02454]},{"body_a":"attachment","body_b":"push_box","contact_count":993.0,"contact_point_centroid":[0.54836,-0.05216,0.05476],"force_p95":90.9665,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.90364,"mean_force":58.5214,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52845,-0.04503,0.02438]},{"body_a":"push_box","body_b":"link7","contact_count":43.0,"contact_point_centroid":[0.55098,-0.12528,0.05641],"force_p95":52.25544,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.29873,"mean_force":22.63724,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50798,-0.12073,0.03035]},{"body_a":"world","body_b":"push_box","contact_count":3600.0,"contact_point_centroid":[0.53901,-0.13079,-2e-05],"force_p95":0.459,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.6179,"mean_force":0.47002,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50308,-0.04804,0.08189]},{"body_a":"attachment","body_b":"push_box","contact_count":97.0,"contact_point_centroid":[0.52955,-0.11581,0.05924],"force_p95":34.33018,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.24097,"mean_force":7.12903,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50646,-0.11372,0.03496]},{"body_a":"attachment","body_b":"push_box","contact_count":89.0,"contact_point_centroid":[0.55317,0.02256,0.03616],"force_p95":8.44004,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.89793,"mean_force":2.70357,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54757,0.03452,0.02024]},{"body_a":"world","body_b":"push_box","contact_count":1884.0,"contact_point_centroid":[0.55337,-0.00026,-1e-05],"force_p95":1.02315,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.32695,"mean_force":0.37928,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5452,0.05595,0.02335]},{"body_a":"world","body_b":"push_box","contact_count":3908.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52229,0.03842,0.16451]}],"total_contact_groups":9},"final_pose_error":0.13481,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53708,-0.13054,0.02499],"final_tcp_position":[0.50101,0.01886,0.1188],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":139.31324,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":977.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3908.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54659,0.07722,0.03112],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55531,-0.00655,0.02509],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15375,"object_to_goal_dist_start":0.16043,"object_z_max":0.02513,"peak_contact_force":1.10845,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1973.0,"raw_peak_contact_force":11.89793,"tcp_end":[0.54815,0.03037,0.01977],"tcp_start":[0.54659,0.07722,0.03112],"tcp_to_object_dist_end":0.03798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54956,-0.13805,0.0303],"object_pos_start":[0.55531,-0.00655,0.02509],"object_to_goal_dist_end":0.05125,"object_to_goal_dist_start":0.15375,"object_z_max":0.03108,"peak_contact_force":129.88387,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3918.0,"raw_peak_contact_force":139.31324,"tcp_end":[0.50931,-0.12286,0.02887],"tcp_start":[0.54815,0.03037,0.01977],"tcp_to_object_dist_end":0.04304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53708,-0.13054,0.02499],"object_pos_start":[0.54956,-0.13805,0.0303],"object_to_goal_dist_end":0.04188,"object_to_goal_dist_start":0.05125,"object_z_max":0.03213,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3740.0,"raw_peak_contact_force":73.29873,"tcp_end":[0.50101,0.01886,0.1188],"tcp_start":[0.50931,-0.12286,0.02887],"tcp_to_object_dist_end":0.18006,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```