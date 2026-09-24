## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2811 | 0.69 | ❌ rejected |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2685 | 0.70 | ✅ accepted |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0216 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2838 | 0.69 | ❌ rejected |
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2751 | 0.69 | ✅ accepted |

**Proposal policy**: task_score is 0.69 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.281) — your mutation base

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

- **Composite score**: 0.281
- **task_score** (E): 0.687
- **fitness_score**: 0.641  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2868 |
| contact_1 | 1.00 | 1.00 | 0.0538 |
| push_1 | 1.00 | 1.00 | 0.1255 |
| retract_1 | 0.00 | 1.00 | 0.1339 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.105, 0.038) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.105, 0.038)→(0.508, 0.055, 0.021) | (0.513, 0.027, 0.025)→(0.515, 0.018, 0.025) | 0.180→0.171 | 1.00 / 3.000 | 2.271 | 10.406 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.055, 0.021)→(0.501, -0.069, 0.024) | (0.515, 0.018, 0.025)→(0.508, -0.102, 0.028) | 0.171→0.059 | 1.00 / 4.000 | 49.546 | 85.423 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.069, 0.024)→(0.497, 0.048, 0.088) | (0.508, -0.102, 0.028)→(0.505, -0.099, 0.025) | 0.059→0.058 | 1.00 / 4.000 | 0.245 | 44.403 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.852
- lateral_force_integral: None
- approach_alignment: 0.484
- goal_progress: 0.759
- terminal_score: 0.759
- phase_score: 0.811
- phase_breakdown.push_score: 0.779
- phase_breakdown.approach_score: 0.822
- phase_breakdown.contact_score: 0.859

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.790
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.759
- **Median Q (composite search score)**: 0.212
- **K-run variance**: 0.0112
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.351


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48352,"average_solve_count":182.0,"average_success_count":182.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0899,"contact_1.speed":0.04421,"push_1.push_depth":0.09898,"push_1.push_distance":0.06661,"push_1.push_speed":0.07051,"retract_1.speed":0.05426},"optimized_scores":{"best_composite_score":0.2123,"best_fitness_score":0.5723,"best_task_score":0.6607},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1811.0,"contact_point_centroid":[0.52096,-0.0486,-0.00016],"force_p95":47.33467,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.16249,"mean_force":30.28068,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5042,0.00762,0.02171]},{"body_a":"push_box","body_b":"link7","contact_count":988.0,"contact_point_centroid":[0.53047,-0.00564,0.05434],"force_p95":48.67185,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.68428,"mean_force":41.09836,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50437,0.01122,0.02151]},{"body_a":"attachment","body_b":"push_box","contact_count":995.0,"contact_point_centroid":[0.52319,0.00118,0.05225],"force_p95":46.02848,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.91117,"mean_force":34.501,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50441,0.01167,0.02151]},{"body_a":"push_box","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.52671,-0.07182,0.0545],"force_p95":37.30448,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.36187,"mean_force":16.66262,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49925,-0.04764,0.02271]},{"body_a":"attachment","body_b":"push_box","contact_count":34.0,"contact_point_centroid":[0.51952,-0.0564,0.0555],"force_p95":28.74718,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.53283,"mean_force":7.23199,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49854,-0.04589,0.023]},{"body_a":"world","body_b":"push_box","contact_count":3876.0,"contact_point_centroid":[0.50463,-0.08341,-1e-05],"force_p95":0.24539,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.14669,"mean_force":0.27945,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49592,0.00626,0.05297]},{"body_a":"attachment","body_b":"push_box","contact_count":123.0,"contact_point_centroid":[0.5166,0.06834,0.03674],"force_p95":9.02107,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.4058,"mean_force":3.7519,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50996,0.08015,0.02218]},{"body_a":"world","body_b":"push_box","contact_count":2459.0,"contact_point_centroid":[0.51515,0.04613,-1e-05],"force_p95":1.91521,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.922,"mean_force":0.43848,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50821,0.10121,0.02863]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5035,0.07618,0.17968]}],"total_contact_groups":9},"final_pose_error":0.11695,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50444,-0.08289,0.02499],"final_tcp_position":[0.49613,0.05384,0.08355],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":65.16249,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50996,0.12512,0.04024],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":682.0,"n_steps_budget":780.0,"object_pos_end":[0.5172,0.03872,0.02505],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18951,"object_to_goal_dist_start":0.19823,"object_z_max":0.02511,"peak_contact_force":5.85394,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2582.0,"raw_peak_contact_force":12.4058,"tcp_end":[0.51043,0.07556,0.02086],"tcp_start":[0.50996,0.12512,0.04024],"tcp_to_object_dist_end":0.03769,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50617,-0.08576,0.0288],"object_pos_start":[0.5172,0.03872,0.02505],"object_to_goal_dist_end":0.06464,"object_to_goal_dist_start":0.18951,"object_z_max":0.02885,"peak_contact_force":40.58134,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3794.0,"raw_peak_contact_force":65.16249,"tcp_end":[0.49976,-0.04799,0.02273],"tcp_start":[0.51043,0.07556,0.02086],"tcp_to_object_dist_end":0.03879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50444,-0.08289,0.02499],"object_pos_start":[0.50617,-0.08576,0.0288],"object_to_goal_dist_end":0.06726,"object_to_goal_dist_start":0.06464,"object_z_max":0.0288,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3927.0,"raw_peak_contact_force":37.36187,"tcp_end":[0.49613,0.05384,0.08355],"tcp_start":[0.49976,-0.04799,0.02273],"tcp_to_object_dist_end":0.14897,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74556,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0984,"contact_1.speed":0.03734,"push_1.push_depth":0.09813,"push_1.push_distance":0.11296,"push_1.push_speed":0.07248,"retract_1.speed":0.0901},"optimized_scores":{"best_composite_score":0.20043,"best_fitness_score":0.56043,"best_task_score":0.64258},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1165.0,"contact_point_centroid":[0.48764,-0.03163,-9e-05],"force_p95":51.37777,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.70464,"mean_force":12.72367,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48485,0.01558,0.01955]},{"body_a":"attachment","body_b":"push_box","contact_count":741.0,"contact_point_centroid":[0.49206,0.01497,0.03516],"force_p95":36.50059,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.23854,"mean_force":13.52219,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48321,0.02627,0.0196]},{"body_a":"push_box","body_b":"link7","contact_count":325.0,"contact_point_centroid":[0.50622,0.03699,0.05142],"force_p95":36.49717,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.71781,"mean_force":24.56599,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47822,0.06038,0.02002]},{"body_a":"attachment","body_b":"push_box","contact_count":157.0,"contact_point_centroid":[0.47955,0.07903,0.03118],"force_p95":9.04166,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.97881,"mean_force":3.77092,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47462,0.09077,0.02276]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49156,-0.0538,0.02159],"force_p95":7.88176,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.43346,"mean_force":4.41102,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4946,-0.04232,0.02]},{"body_a":"world","body_b":"push_box","contact_count":2828.0,"contact_point_centroid":[0.4796,0.05687,-1e-05],"force_p95":2.48673,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.07661,"mean_force":0.45743,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47351,0.11067,0.02885]},{"body_a":"world","body_b":"push_box","contact_count":3983.0,"contact_point_centroid":[0.48143,-0.0775,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.30539,"mean_force":0.24926,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49267,0.02188,0.05893]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48499,0.08132,0.17979]}],"total_contact_groups":8},"final_pose_error":0.08351,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48148,-0.07745,0.02499],"final_tcp_position":[0.49456,0.08313,0.10026],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":59.70464,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4758,0.13519,0.04024],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":780.0,"n_steps_budget":900.0,"object_pos_end":[0.48094,0.04911,0.02492],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20002,"object_to_goal_dist_start":0.2095,"object_z_max":0.02508,"peak_contact_force":0.00061,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2985.0,"raw_peak_contact_force":9.97881,"tcp_end":[0.47495,0.08577,0.02128],"tcp_start":[0.4758,0.13519,0.04024],"tcp_to_object_dist_end":0.03733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":827.0,"n_steps_budget":1000.0,"object_pos_end":[0.48202,-0.07686,0.02483],"object_pos_start":[0.48094,0.04911,0.02492],"object_to_goal_dist_end":0.07532,"object_to_goal_dist_start":0.20002,"object_z_max":0.0294,"peak_contact_force":0.4165,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2231.0,"raw_peak_contact_force":59.70464,"tcp_end":[0.49462,-0.04224,0.02002],"tcp_start":[0.47495,0.08577,0.02128],"tcp_to_object_dist_end":0.03715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48148,-0.07745,0.02499],"object_pos_start":[0.48202,-0.07686,0.02483],"object_to_goal_dist_end":0.07488,"object_to_goal_dist_start":0.07532,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3986.0,"raw_peak_contact_force":8.43346,"tcp_end":[0.49456,0.08313,0.10026],"tcp_start":[0.49462,-0.04224,0.02002],"tcp_to_object_dist_end":0.17783,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48663,"average_solve_count":187.0,"average_success_count":187.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08715,"contact_1.speed":0.03591,"push_1.push_depth":0.09623,"push_1.push_distance":0.11767,"push_1.push_speed":0.08185,"retract_1.speed":0.05754},"optimized_scores":{"best_composite_score":0.43047,"best_fitness_score":0.79047,"best_task_score":0.75902},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":926.0,"contact_point_centroid":[0.55472,-0.07398,0.05436],"force_p95":110.71241,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.40142,"mean_force":75.64467,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52227,-0.05793,0.02333]},{"body_a":"attachment","body_b":"push_box","contact_count":927.0,"contact_point_centroid":[0.5409,-0.06663,0.05279],"force_p95":87.58768,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.27775,"mean_force":52.49869,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52229,-0.05786,0.02332]},{"body_a":"world","body_b":"push_box","contact_count":1837.0,"contact_point_centroid":[0.54754,-0.10836,-0.00033],"force_p95":74.69351,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.64397,"mean_force":48.65636,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52223,-0.05819,0.02338]},{"body_a":"push_box","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.54791,-0.12424,0.05621],"force_p95":79.82662,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.41459,"mean_force":31.8918,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50711,-0.1116,0.02951]},{"body_a":"world","body_b":"push_box","contact_count":3650.0,"contact_point_centroid":[0.52978,-0.1373,-3e-05],"force_p95":0.28611,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.24929,"mean_force":0.59253,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50217,-0.04673,0.05526]},{"body_a":"attachment","body_b":"push_box","contact_count":74.0,"contact_point_centroid":[0.53085,-0.11468,0.06025],"force_p95":60.35641,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.04625,"mean_force":21.53707,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50662,-0.10949,0.02989]},{"body_a":"attachment","body_b":"push_box","contact_count":167.0,"contact_point_centroid":[0.54522,-0.00496,0.03596],"force_p95":6.20854,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.8324,"mean_force":2.77843,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53915,0.00693,0.0204]},{"body_a":"world","body_b":"push_box","contact_count":3234.0,"contact_point_centroid":[0.54463,-0.02753,-1e-05],"force_p95":1.56159,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.29398,"mean_force":0.39454,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5367,0.03032,0.02373]},{"body_a":"world","body_b":"push_box","contact_count":3780.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51726,0.04384,0.17041]}],"total_contact_groups":9},"final_pose_error":0.15891,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52912,-0.13714,0.02499],"final_tcp_position":[0.50058,0.00733,0.08003],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":131.40142,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":945.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3780.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5381,0.05607,0.03233],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":905.0,"n_steps_budget":1000.0,"object_pos_end":[0.54692,-0.03456,0.0251],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12461,"object_to_goal_dist_start":0.13211,"object_z_max":0.02519,"peak_contact_force":0.95801,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3401.0,"raw_peak_contact_force":8.8324,"tcp_end":[0.53967,0.00218,0.01977],"tcp_start":[0.5381,0.05607,0.03233],"tcp_to_object_dist_end":0.03783,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":937.0,"n_steps_budget":1000.0,"object_pos_end":[0.53495,-0.14487,0.03112],"object_pos_start":[0.54692,-0.03456,0.0251],"object_to_goal_dist_end":0.03585,"object_to_goal_dist_start":0.12461,"object_z_max":0.03112,"peak_contact_force":107.64059,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3690.0,"raw_peak_contact_force":131.40142,"tcp_end":[0.50824,-0.11628,0.02853],"tcp_start":[0.53967,0.00218,0.01977],"tcp_to_object_dist_end":0.03921,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52912,-0.13714,0.02499],"object_pos_start":[0.53495,-0.14487,0.03112],"object_to_goal_dist_end":0.03184,"object_to_goal_dist_start":0.03585,"object_z_max":0.03491,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3787.0,"raw_peak_contact_force":87.41459,"tcp_end":[0.50058,0.00733,0.08003],"tcp_start":[0.50824,-0.11628,0.02853],"tcp_to_object_dist_end":0.15721,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```