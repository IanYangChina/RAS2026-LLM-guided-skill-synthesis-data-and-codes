## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2685 | 0.70 | ✅ accepted |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0216 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2838 | 0.69 | ❌ rejected |
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2751 | 0.69 | ✅ accepted |

**Proposal policy**: task_score is 0.70 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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

## Current Skill (Q=0.269) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
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
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.269
- **task_score** (E): 0.695
- **fitness_score**: 0.629  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2748 |
| contact_1 | 1.00 | 1.00 | 0.0588 |
| push_1 | 1.00 | 1.00 | 0.1263 |
| retract_1 | 0.00 | 1.00 | 0.1322 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.105, 0.050) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.507, 0.105, 0.050)→(0.508, 0.054, 0.021) | (0.513, 0.027, 0.025)→(0.515, 0.018, 0.025) | 0.180→0.171 | 1.00 / 3.333 | 3.330 | 11.709 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.054, 0.021)→(0.501, -0.070, 0.024) | (0.515, 0.018, 0.025)→(0.511, -0.104, 0.028) | 0.171→0.057 | 1.00 / 3.333 | 52.997 | 86.742 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.070, 0.024)→(0.497, 0.046, 0.087) | (0.511, -0.104, 0.028)→(0.508, -0.101, 0.025) | 0.057→0.056 | 1.00 / 4.000 | 0.245 | 42.952 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.853
- lateral_force_integral: None
- approach_alignment: 0.469
- goal_progress: 0.755
- terminal_score: 0.755
- phase_score: 0.796
- phase_breakdown.push_score: 0.782
- phase_breakdown.approach_score: 0.733
- phase_breakdown.contact_score: 0.862

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.780
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.755
- **Median Q (composite search score)**: 0.198
- **K-run variance**: 0.0115
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.412


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08621,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04159,"contact_1.speed":0.04862,"push_1.push_depth":0.09999,"push_1.push_distance":0.08017,"push_1.push_speed":0.09658,"retract_1.speed":0.03413},"optimized_scores":{"best_composite_score":0.1876,"best_fitness_score":0.5476,"best_task_score":0.66716},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1356.0,"contact_point_centroid":[0.5227,-0.0459,-0.00013],"force_p95":57.51918,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.08288,"mean_force":32.27189,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50437,0.00827,0.02236]},{"body_a":"attachment","body_b":"push_box","contact_count":783.0,"contact_point_centroid":[0.52185,0.00108,0.04977],"force_p95":56.11528,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.71149,"mean_force":36.95647,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50447,0.01135,0.0222]},{"body_a":"push_box","body_b":"link7","contact_count":758.0,"contact_point_centroid":[0.53111,-0.00849,0.05474],"force_p95":54.15198,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.68576,"mean_force":42.21347,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50432,0.00933,0.02223]},{"body_a":"push_box","body_b":"link7","contact_count":20.0,"contact_point_centroid":[0.52818,-0.07468,0.05455],"force_p95":42.05382,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.60213,"mean_force":22.79222,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4996,-0.04974,0.02328]},{"body_a":"attachment","body_b":"push_box","contact_count":43.0,"contact_point_centroid":[0.5198,-0.0577,0.05582],"force_p95":33.66592,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.37529,"mean_force":8.90728,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49876,-0.04744,0.02371]},{"body_a":"world","body_b":"push_box","contact_count":3848.0,"contact_point_centroid":[0.50618,-0.08483,-1e-05],"force_p95":0.24889,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.80952,"mean_force":0.30191,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4962,0.00413,0.05306]},{"body_a":"attachment","body_b":"push_box","contact_count":140.0,"contact_point_centroid":[0.5154,0.06835,0.0383],"force_p95":11.43992,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.79942,"mean_force":6.58097,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50984,0.0802,0.02618]},{"body_a":"world","body_b":"push_box","contact_count":2658.0,"contact_point_centroid":[0.51528,0.04628,-1e-05],"force_p95":3.34143,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.17428,"mean_force":0.59413,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50778,0.09856,0.0413]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50294,0.07203,0.19077]}],"total_contact_groups":9},"final_pose_error":0.11975,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50595,-0.08429,0.02499],"final_tcp_position":[0.49629,0.05101,0.08272],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":73.08288,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50875,0.12221,0.06447],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":720.0,"n_steps_budget":840.0,"object_pos_end":[0.51682,0.03859,0.02492],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18934,"object_to_goal_dist_start":0.19823,"object_z_max":0.02509,"peak_contact_force":7.41972,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2798.0,"raw_peak_contact_force":14.79942,"tcp_end":[0.51051,0.07549,0.02234],"tcp_start":[0.50875,0.12221,0.06447],"tcp_to_object_dist_end":0.03752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":796.0,"n_steps_budget":900.0,"object_pos_end":[0.50739,-0.08784,0.02894],"object_pos_start":[0.51682,0.03859,0.02492],"object_to_goal_dist_end":0.06272,"object_to_goal_dist_start":0.18934,"object_z_max":0.02945,"peak_contact_force":48.94184,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2897.0,"raw_peak_contact_force":73.08288,"tcp_end":[0.50014,-0.05032,0.02325],"tcp_start":[0.51051,0.07549,0.02234],"tcp_to_object_dist_end":0.03863,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50595,-0.08429,0.02499],"object_pos_start":[0.50739,-0.08784,0.02894],"object_to_goal_dist_end":0.06598,"object_to_goal_dist_start":0.06272,"object_z_max":0.02896,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3911.0,"raw_peak_contact_force":43.60213,"tcp_end":[0.49629,0.05101,0.08272],"tcp_start":[0.50014,-0.05032,0.02325],"tcp_to_object_dist_end":0.14742,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4574,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07757,"contact_1.speed":0.0309,"push_1.push_depth":0.098,"push_1.push_distance":0.03244,"push_1.push_speed":0.03992,"retract_1.speed":0.08184},"optimized_scores":{"best_composite_score":0.19795,"best_fitness_score":0.55795,"best_task_score":0.66256},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1328.0,"contact_point_centroid":[0.49267,-0.03321,-0.0001],"force_p95":50.71523,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.09963,"mean_force":13.79858,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48492,0.01514,0.01967]},{"body_a":"attachment","body_b":"push_box","contact_count":862.0,"contact_point_centroid":[0.49323,0.01257,0.03569],"force_p95":36.28018,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.18212,"mean_force":13.98706,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48362,0.0239,0.01976]},{"body_a":"push_box","body_b":"link7","contact_count":393.0,"contact_point_centroid":[0.50688,0.03588,0.05136],"force_p95":37.06537,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.98743,"mean_force":26.42102,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47841,0.05918,0.0202]},{"body_a":"attachment","body_b":"push_box","contact_count":219.0,"contact_point_centroid":[0.47772,0.07872,0.02882],"force_p95":8.62108,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.05388,"mean_force":4.55465,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47469,0.09056,0.02385]},{"body_a":"world","body_b":"push_box","contact_count":3568.0,"contact_point_centroid":[0.47941,0.05689,-1e-05],"force_p95":2.45195,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.87676,"mean_force":0.52375,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47371,0.10864,0.03218]},{"body_a":"world","body_b":"push_box","contact_count":3987.0,"contact_point_centroid":[0.48951,-0.08008,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93599,"mean_force":0.24615,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49253,0.01692,0.05575]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49303,-0.05443,0.02094],"force_p95":0.8785,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.89293,"mean_force":0.7486,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49466,-0.04261,0.02005]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48523,0.07982,0.18344]}],"total_contact_groups":8},"final_pose_error":0.0956,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48952,-0.08009,0.02499],"final_tcp_position":[0.49424,0.07307,0.09354],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":57.09963,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47602,0.13421,0.04774],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07915,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":967.0,"n_steps_budget":1000.0,"object_pos_end":[0.48189,0.04871,0.02504],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.19953,"object_to_goal_dist_start":0.2095,"object_z_max":0.02505,"peak_contact_force":1.62598,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3787.0,"raw_peak_contact_force":10.05388,"tcp_end":[0.47504,0.08531,0.0215],"tcp_start":[0.47602,0.13421,0.04774],"tcp_to_object_dist_end":0.0374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":942.0,"n_steps_budget":1000.0,"object_pos_end":[0.48989,-0.07918,0.02507],"object_pos_start":[0.48189,0.04871,0.02504],"object_to_goal_dist_end":0.07154,"object_to_goal_dist_start":0.19953,"object_z_max":0.02935,"peak_contact_force":0.81018,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2583.0,"raw_peak_contact_force":57.09963,"tcp_end":[0.49466,-0.04256,0.02006],"tcp_start":[0.47504,0.08531,0.0215],"tcp_to_object_dist_end":0.03727,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48952,-0.08009,0.02499],"object_pos_start":[0.48989,-0.07918,0.02507],"object_to_goal_dist_end":0.07069,"object_to_goal_dist_start":0.07154,"object_z_max":0.02507,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3989.0,"raw_peak_contact_force":0.93599,"tcp_end":[0.49424,0.07307,0.09354],"tcp_start":[0.49466,-0.04256,0.02006],"tcp_to_object_dist_end":0.16786,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20253,"average_solve_count":237.0,"average_success_count":237.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04337,"contact_1.speed":0.0356,"push_1.push_depth":0.09618,"push_1.push_distance":0.11151,"push_1.push_speed":0.08036,"retract_1.speed":0.06528},"optimized_scores":{"best_composite_score":0.42,"best_fitness_score":0.78,"best_task_score":0.75534},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":954.0,"contact_point_centroid":[0.55543,-0.07379,0.0543],"force_p95":110.4086,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.04417,"mean_force":76.13071,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5223,-0.05805,0.02354]},{"body_a":"attachment","body_b":"push_box","contact_count":959.0,"contact_point_centroid":[0.5411,-0.06646,0.05311],"force_p95":86.40954,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.4674,"mean_force":52.47449,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52239,-0.05773,0.02353]},{"body_a":"world","body_b":"push_box","contact_count":1912.0,"contact_point_centroid":[0.54881,-0.10656,-0.00033],"force_p95":74.72333,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.58559,"mean_force":48.56055,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5224,-0.05777,0.02355]},{"body_a":"push_box","body_b":"link7","contact_count":60.0,"contact_point_centroid":[0.54798,-0.12442,0.05656],"force_p95":75.17672,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.31705,"mean_force":29.66615,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50727,-0.11214,0.02981]},{"body_a":"world","body_b":"push_box","contact_count":3661.0,"contact_point_centroid":[0.53042,-0.13745,-3e-05],"force_p95":0.26894,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.47015,"mean_force":0.55558,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50222,-0.04347,0.05719]},{"body_a":"attachment","body_b":"push_box","contact_count":70.0,"contact_point_centroid":[0.53121,-0.11501,0.06058],"force_p95":56.52387,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.70604,"mean_force":19.71895,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50679,-0.11003,0.0302]},{"body_a":"attachment","body_b":"push_box","contact_count":168.0,"contact_point_centroid":[0.54543,-0.00501,0.03771],"force_p95":6.60659,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.27282,"mean_force":3.04486,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53907,0.00689,0.02117]},{"body_a":"world","body_b":"push_box","contact_count":3366.0,"contact_point_centroid":[0.5445,-0.02739,-1e-05],"force_p95":1.68292,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.76556,"mean_force":0.40335,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53624,0.03072,0.02705]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51674,0.04354,0.17358]}],"total_contact_groups":9},"final_pose_error":0.15135,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52974,-0.13735,0.02499],"final_tcp_position":[0.50051,0.01408,0.08342],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":130.04417,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5372,0.05709,0.03845],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08407,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.54694,-0.03468,0.02505],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12451,"object_to_goal_dist_start":0.13211,"object_z_max":0.02513,"peak_contact_force":0.94296,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3534.0,"raw_peak_contact_force":10.27282,"tcp_end":[0.53965,0.00217,0.02005],"tcp_start":[0.5372,0.05709,0.03845],"tcp_to_object_dist_end":0.0379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.53601,-0.14504,0.03112],"object_pos_start":[0.54694,-0.03468,0.02505],"object_to_goal_dist_end":0.03686,"object_to_goal_dist_start":0.12451,"object_z_max":0.03113,"peak_contact_force":109.23774,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3825.0,"raw_peak_contact_force":130.04417,"tcp_end":[0.50844,-0.11693,0.02883],"tcp_start":[0.53965,0.00217,0.02005],"tcp_to_object_dist_end":0.03944,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52974,-0.13735,0.02499],"object_pos_start":[0.53601,-0.14504,0.03112],"object_to_goal_dist_end":0.03232,"object_to_goal_dist_start":0.03686,"object_z_max":0.03494,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3791.0,"raw_peak_contact_force":84.31705,"tcp_end":[0.50051,0.01408,0.08342],"tcp_start":[0.50844,-0.11693,0.02883],"tcp_to_object_dist_end":0.16492,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```