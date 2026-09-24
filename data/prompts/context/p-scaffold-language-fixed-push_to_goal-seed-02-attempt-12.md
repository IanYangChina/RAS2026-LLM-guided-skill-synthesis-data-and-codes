## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5838 | 0.72 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.1150 | 0.00 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5971 | 0.76 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.5975 | 0.76 | ✅ accepted |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2573 | 0.42 | ❌ rejected |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.584) — your mutation base

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

- **Composite score**: 0.584
- **task_score** (E): 0.723
- **fitness_score**: 0.794  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
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
| contact_1 | contact | 1.00 / step_budget | (0.488, 0.059, 0.033)→(0.487, 0.011, 0.021) | (0.492, -0.018, 0.025)→(0.493, -0.026, 0.025) | 0.139→0.132 | 1.00 / 2.667 | 3.043 | 13.910 |
| push_1 | push | 1.00 / step_budget | (0.487, 0.011, 0.021)→(0.499, -0.123, 0.023) | (0.493, -0.026, 0.025)→(0.492, -0.145, 0.027) | 0.132→0.041 | 1.00 / 2.667 | 42.539 | 87.239 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.123, 0.023)→(0.496, 0.017, 0.116) | (0.492, -0.145, 0.027)→(0.488, -0.143, 0.025) | 0.041→0.038 | 1.00 / 4.000 | 0.245 | 25.524 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.458
- goal_progress: 0.767
- terminal_score: 0.767
- phase_score: 0.854
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.857
- phase_breakdown.contact_score: 0.868

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.819
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.767
- **Median Q (composite search score)**: 0.579
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.198


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30978,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.12311,"approach_1.speed":0.05914,"push_1.push_distance":0.10022},"optimized_scores":{"best_composite_score":0.60888,"best_fitness_score":0.81888,"best_task_score":0.76656},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1243.0,"contact_point_centroid":[0.47901,-0.11254,-0.0001],"force_p95":56.39077,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.28751,"mean_force":13.03733,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48186,-0.06809,0.01958]},{"body_a":"attachment","body_b":"push_box","contact_count":678.0,"contact_point_centroid":[0.48744,-0.06501,0.03539],"force_p95":40.6804,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.95967,"mean_force":16.47168,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47899,-0.05348,0.01975]},{"body_a":"push_box","body_b":"link7","contact_count":290.0,"contact_point_centroid":[0.50014,-0.0424,0.05116],"force_p95":38.23222,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.31052,"mean_force":28.50177,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4722,-0.0177,0.0204]},{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.47026,-0.0027,0.02776],"force_p95":11.66263,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.2738,"mean_force":4.03713,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46687,0.00921,0.02209]},{"body_a":"world","body_b":"push_box","contact_count":1933.0,"contact_point_centroid":[0.47161,-0.02489,-1e-05],"force_p95":0.90389,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.67929,"mean_force":0.40398,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46618,0.03017,0.02607]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.48979,-0.13575,0.02195],"force_p95":2.42318,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.45581,"mean_force":2.12947,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49431,-0.12485,0.01982]},{"body_a":"world","body_b":"push_box","contact_count":3988.0,"contact_point_centroid":[0.47032,-0.15508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.14899,"mean_force":0.24643,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49207,-0.05735,0.07055]},{"body_a":"world","body_b":"push_box","contact_count":3712.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48363,0.02607,0.16655]}],"total_contact_groups":8},"final_pose_error":0.14017,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47031,-0.15507,0.02499],"final_tcp_position":[0.49373,0.01465,0.11412],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":70.28751,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":928.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3712.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46884,0.05267,0.03389],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.47306,-0.03185,0.02485],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12118,"object_to_goal_dist_start":0.12903,"object_z_max":0.02517,"peak_contact_force":0.56944,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2008.0,"raw_peak_contact_force":16.2738,"tcp_end":[0.46711,0.00512,0.02141],"tcp_start":[0.46884,0.05267,0.03389],"tcp_to_object_dist_end":0.03761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":812.0,"n_steps_budget":900.0,"object_pos_end":[0.47096,-0.15421,0.02502],"object_pos_start":[0.47306,-0.03185,0.02485],"object_to_goal_dist_end":0.02935,"object_to_goal_dist_start":0.12118,"object_z_max":0.03107,"peak_contact_force":1.28591,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2211.0,"raw_peak_contact_force":70.28751,"tcp_end":[0.49432,-0.1248,0.01983],"tcp_start":[0.46711,0.00512,0.02141],"tcp_to_object_dist_end":0.03792,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47031,-0.15507,0.02499],"object_pos_start":[0.47096,-0.15421,0.02502],"object_to_goal_dist_end":0.03012,"object_to_goal_dist_start":0.02935,"object_z_max":0.02504,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3990.0,"raw_peak_contact_force":2.45581,"tcp_end":[0.49373,0.01465,0.11412],"tcp_start":[0.49432,-0.1248,0.01983],"tcp_to_object_dist_end":0.19313,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81065,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18184,"approach_1.speed":0.0709,"push_1.push_distance":0.09242},"optimized_scores":{"best_composite_score":0.56382,"best_fitness_score":0.77382,"best_task_score":0.66159},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1419.0,"contact_point_centroid":[0.46186,-0.11241,-8e-05],"force_p95":38.86645,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.12305,"mean_force":7.10144,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4728,-0.0735,0.01957]},{"body_a":"attachment","body_b":"push_box","contact_count":618.0,"contact_point_centroid":[0.47211,-0.0655,0.03271],"force_p95":29.20096,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.07453,"mean_force":11.34291,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46526,-0.0539,0.01963]},{"body_a":"push_box","body_b":"link7","contact_count":251.0,"contact_point_centroid":[0.48063,-0.04378,0.0506],"force_p95":25.46985,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.63112,"mean_force":18.23941,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45313,-0.02072,0.0202]},{"body_a":"attachment","body_b":"push_box","contact_count":83.0,"contact_point_centroid":[0.45263,-0.01024,0.0325],"force_p95":10.55196,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.35708,"mean_force":3.52386,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44607,0.00166,0.02247]},{"body_a":"world","body_b":"push_box","contact_count":1924.0,"contact_point_centroid":[0.4503,-0.0325,-1e-05],"force_p95":1.09417,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.80721,"mean_force":0.39938,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44583,0.02314,0.02673]},{"body_a":"world","body_b":"push_box","contact_count":3989.0,"contact_point_centroid":[0.45674,-0.14563,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81123,"mean_force":0.24577,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49136,-0.05726,0.07058]},{"body_a":"world","body_b":"push_box","contact_count":3512.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47379,0.02258,0.16688]}],"total_contact_groups":7},"final_pose_error":0.14011,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45676,-0.14564,0.02499],"final_tcp_position":[0.49327,0.01472,0.11414],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":53.12305,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":878.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3512.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44892,0.04563,0.03449],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.45157,-0.03913,0.02503],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12099,"object_to_goal_dist_start":0.12843,"object_z_max":0.02507,"peak_contact_force":6.75719,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2007.0,"raw_peak_contact_force":13.35708,"tcp_end":[0.44619,-0.00225,0.02177],"tcp_start":[0.44892,0.04563,0.03449],"tcp_to_object_dist_end":0.03741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":813.0,"n_steps_budget":900.0,"object_pos_end":[0.45699,-0.14531,0.02502],"object_pos_start":[0.45157,-0.03913,0.02503],"object_to_goal_dist_end":0.04326,"object_to_goal_dist_start":0.12099,"object_z_max":0.03078,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2288.0,"raw_peak_contact_force":53.12305,"tcp_end":[0.49337,-0.12466,0.01988],"tcp_start":[0.44619,-0.00225,0.02177],"tcp_to_object_dist_end":0.04215,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45676,-0.14564,0.02499],"object_pos_start":[0.45699,-0.14531,0.02502],"object_to_goal_dist_end":0.04346,"object_to_goal_dist_start":0.04326,"object_z_max":0.02503,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3989.0,"raw_peak_contact_force":0.81123,"tcp_end":[0.49327,0.01472,0.11414],"tcp_start":[0.49337,-0.12466,0.01988],"tcp_to_object_dist_end":0.18707,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80864,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15721,"approach_1.speed":0.08689,"push_1.push_distance":0.13004},"optimized_scores":{"best_composite_score":0.57866,"best_fitness_score":0.78866,"best_task_score":0.73979},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":969.0,"contact_point_centroid":[0.56313,-0.05581,0.05473],"force_p95":131.50282,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.30647,"mean_force":90.60598,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52783,-0.04473,0.02453]},{"body_a":"world","body_b":"push_box","contact_count":1940.0,"contact_point_centroid":[0.56029,-0.08721,-0.00039],"force_p95":101.73472,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.33895,"mean_force":57.94295,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52796,-0.04435,0.02452]},{"body_a":"attachment","body_b":"push_box","contact_count":976.0,"contact_point_centroid":[0.54776,-0.05136,0.05471],"force_p95":89.73652,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":95.09784,"mean_force":59.37691,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52798,-0.04418,0.0245]},{"body_a":"push_box","body_b":"link7","contact_count":42.0,"contact_point_centroid":[0.55059,-0.12236,0.05659],"force_p95":43.71103,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.30494,"mean_force":21.77624,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50752,-0.11809,0.03061]},{"body_a":"world","body_b":"push_box","contact_count":3597.0,"contact_point_centroid":[0.53749,-0.12836,-2e-05],"force_p95":0.44826,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.45629,"mean_force":0.46024,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50272,-0.04596,0.08209]},{"body_a":"attachment","body_b":"push_box","contact_count":96.0,"contact_point_centroid":[0.52893,-0.11316,0.05948],"force_p95":28.93769,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.22344,"mean_force":6.82447,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50596,-0.11083,0.0355]},{"body_a":"attachment","body_b":"push_box","contact_count":91.0,"contact_point_centroid":[0.55378,0.02256,0.0377],"force_p95":11.47403,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.1002,"mean_force":3.82842,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54762,0.0345,0.02027]},{"body_a":"world","body_b":"push_box","contact_count":1895.0,"contact_point_centroid":[0.55322,-0.00029,-1e-05],"force_p95":1.10761,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.59226,"mean_force":0.4343,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54521,0.05586,0.02333]},{"body_a":"world","body_b":"push_box","contact_count":3864.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52232,0.03846,0.16439]}],"total_contact_groups":9},"final_pose_error":0.1334,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53549,-0.12802,0.02499],"final_tcp_position":[0.50076,0.0203,0.1188],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":138.30647,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":966.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3864.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54659,0.07722,0.0311],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55458,-0.00637,0.02513],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15365,"object_to_goal_dist_start":0.16043,"object_z_max":0.02515,"peak_contact_force":1.80168,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1986.0,"raw_peak_contact_force":12.1002,"tcp_end":[0.54819,0.03048,0.01983],"tcp_start":[0.54659,0.07722,0.0311],"tcp_to_object_dist_end":0.03777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":987.0,"n_steps_budget":1000.0,"object_pos_end":[0.54856,-0.13603,0.03046],"object_pos_start":[0.55458,-0.00637,0.02513],"object_to_goal_dist_end":0.05082,"object_to_goal_dist_start":0.15365,"object_z_max":0.03109,"peak_contact_force":126.33173,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3885.0,"raw_peak_contact_force":138.30647,"tcp_end":[0.50882,-0.12033,0.02913],"tcp_start":[0.54819,0.03048,0.01983],"tcp_to_object_dist_end":0.04274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53549,-0.12802,0.02499],"object_pos_start":[0.54856,-0.13603,0.03046],"object_to_goal_dist_end":0.04174,"object_to_goal_dist_start":0.05082,"object_z_max":0.03238,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3735.0,"raw_peak_contact_force":73.30494,"tcp_end":[0.50076,0.0203,0.1188],"tcp_start":[0.50882,-0.12033,0.02913],"tcp_to_object_dist_end":0.1789,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```