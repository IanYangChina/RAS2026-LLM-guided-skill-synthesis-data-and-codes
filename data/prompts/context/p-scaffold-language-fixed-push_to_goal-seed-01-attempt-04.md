## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7663 | 0.86 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7644 | 0.83 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6702 | 0.82 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5894 | 0.86 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6954 | 0.86 | ✅ accepted |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`
- Frozen object start: [0.5014185949640309, 0.05405564355911223, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5014185949640309, 0.05405564355911223, 0.025)
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
  frozen_object_start: [0.5014, 0.0541, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5014185949640309, 0.05405564355911223, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0014, -0.2041, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0

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

## Current Skill (Q=0.766) — your mutation base

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
- id: contact_1
  type: contact
  generator: impedance_motion
  control: force_threshold_switch
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
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.766
- **task_score** (E): 0.861
- **fitness_score**: 0.776  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2798 |
| contact_1 | 1.00 | 1.00 | 0.0402 |
| push_1 | 1.00 | 1.00 | 0.1498 |
| retract_1 | 0.00 | 1.00 | 0.1000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.472, 0.074, 0.035) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.472, 0.074, 0.035)→(0.470, 0.036, 0.022) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 5.000 | 25309.780 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.470, 0.036, 0.022)→(0.492, -0.111, 0.021) | (0.474, -0.001, 0.025)→(0.513, -0.141, 0.027) | 0.154→0.025 | 1.00 / 2.333 | 11.722 | 40.856 |
| retract_1 | retract | 0.00 / step_budget | (0.492, -0.111, 0.021)→(0.488, -0.097, 0.120) | (0.513, -0.141, 0.027)→(0.511, -0.141, 0.025) | 0.025→0.025 | 1.00 / 4.000 | 0.245 | 12.361 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.735
- goal_progress: 0.966
- terminal_score: 0.966
- phase_score: 0.773
- phase_breakdown.push_score: 0.754
- phase_breakdown.contact_score: 0.771
- phase_breakdown.approach_score: 0.822

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.850
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.966
- **Median Q (composite search score)**: 0.812
- **K-run variance**: 0.0073
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.186


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f21cc79f03d9e871b86947069440973ee7e2ef557ebaac0b26b4f6cbdabf5bb1`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec03d65db90cc6b4602194a1eefa4c3104517a971e566e099fb50a3df7102251`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53368,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07413,"contact_1.speed":0.02933,"push_1.push_distance":0.17597,"retract_1.speed":0.05256},"optimized_scores":{"best_composite_score":0.64687,"best_fitness_score":0.65687,"best_task_score":0.73127},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":554.0,"contact_point_centroid":[0.53287,-0.04324,0.05427],"force_p95":40.76566,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.81773,"mean_force":25.68545,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49638,-0.03977,0.02092]},{"body_a":"world","body_b":"push_box","contact_count":1496.0,"contact_point_centroid":[0.53258,-0.05281,-9e-05],"force_p95":33.14915,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.44128,"mean_force":15.34527,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49569,-0.01094,0.02046]},{"body_a":"attachment","body_b":"push_box","contact_count":881.0,"contact_point_centroid":[0.50854,-0.01303,0.04946],"force_p95":29.21181,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.60245,"mean_force":13.05194,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49548,-0.00495,0.02029]},{"body_a":"push_box","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.53544,-0.08637,0.05487],"force_p95":25.54408,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.09965,"mean_force":7.53981,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49726,-0.08691,0.02195]},{"body_a":"world","body_b":"push_box","contact_count":3568.0,"contact_point_centroid":[0.53337,-0.10487,-1e-05],"force_p95":0.47297,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.91658,"mean_force":0.28778,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49418,-0.07418,0.0748]},{"body_a":"attachment","body_b":"push_box","contact_count":135.0,"contact_point_centroid":[0.51227,-0.08309,0.05425],"force_p95":3.73128,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.94089,"mean_force":0.97853,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49476,-0.08208,0.03094]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4978,0.06228,0.16716]},{"body_a":"world","body_b":"push_box","contact_count":2628.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49548,0.10622,0.02767]}],"total_contact_groups":8},"final_pose_error":0.05407,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53085,-0.10467,0.02499],"final_tcp_position":[0.49441,-0.07353,0.11953],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49757,0.12458,0.03769],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":657.0,"n_steps_budget":930.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2628.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49661,0.09105,0.02262],"tcp_start":[0.49757,0.12458,0.03769],"tcp_to_object_dist_end":0.03738,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53577,-0.10547,0.02939],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.05729,"object_to_goal_dist_start":0.20406,"object_z_max":0.02947,"peak_contact_force":33.10971,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2931.0,"raw_peak_contact_force":48.81773,"tcp_end":[0.49778,-0.08685,0.02183],"tcp_start":[0.49661,0.09105,0.02262],"tcp_to_object_dist_end":0.04298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53085,-0.10467,0.02499],"object_pos_start":[0.53577,-0.10547,0.02939],"object_to_goal_dist_end":0.05484,"object_to_goal_dist_start":0.05729,"object_z_max":0.02962,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3717.0,"raw_peak_contact_force":35.09965,"tcp_end":[0.49441,-0.07353,0.11953],"tcp_start":[0.49778,-0.08685,0.02183],"tcp_to_object_dist_end":0.106,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `060d405a872aae8d4597ed6284dedb60e9c99f80071c0520b1a8a2986f3c114d`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33514,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0671,"contact_1.speed":0.03859,"push_1.push_distance":0.10312,"retract_1.speed":0.04974},"optimized_scores":{"best_composite_score":0.83998,"best_fitness_score":0.84998,"best_task_score":0.96594},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":666.0,"contact_point_centroid":[0.48169,-0.06704,0.03526],"force_p95":19.04537,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.51604,"mean_force":4.45711,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4772,-0.0552,0.01962]},{"body_a":"world","body_b":"push_box","contact_count":990.0,"contact_point_centroid":[0.48643,-0.10538,-5e-05],"force_p95":10.38476,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.91976,"mean_force":3.40677,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47635,-0.05061,0.01961]},{"body_a":"world","body_b":"push_box","contact_count":3962.0,"contact_point_centroid":[0.50364,-0.15263,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99542,"mean_force":0.24757,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4857,-0.10505,0.06975]},{"body_a":"attachment","body_b":"push_box","contact_count":11.0,"contact_point_centroid":[0.49542,-0.12847,0.04159],"force_p95":0.91071,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.97271,"mean_force":0.31008,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48822,-0.11674,0.02091]},{"body_a":"world","body_b":"push_box","contact_count":3624.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48371,0.02618,0.16617]},{"body_a":"world","body_b":"push_box","contact_count":2412.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46655,0.03181,0.02621]}],"total_contact_groups":6},"final_pose_error":0.05264,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50362,-0.1525,0.02499],"final_tcp_position":[0.48591,-0.10388,0.11944],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":36.51604,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":906.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3624.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46911,0.05271,0.03402],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":603.0,"n_steps_budget":780.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":22.06407,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2412.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.46718,0.01277,0.02224],"tcp_start":[0.46911,0.05271,0.03402],"tcp_to_object_dist_end":0.0373,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":776.0,"n_steps_budget":900.0,"object_pos_end":[0.50366,-0.15216,0.02621],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00442,"object_to_goal_dist_start":0.12903,"object_z_max":0.02619,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1656.0,"raw_peak_contact_force":36.51604,"tcp_end":[0.48921,-0.11718,0.02027],"tcp_start":[0.46718,0.01277,0.02224],"tcp_to_object_dist_end":0.03831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50362,-0.1525,0.02499],"object_pos_start":[0.50366,-0.15216,0.02621],"object_to_goal_dist_end":0.00439,"object_to_goal_dist_start":0.00442,"object_z_max":0.02621,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3973.0,"raw_peak_contact_force":0.99542,"tcp_end":[0.48591,-0.10388,0.11944],"tcp_start":[0.48921,-0.11718,0.02027],"tcp_to_object_dist_end":0.10769,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c4af277909bfbef2010e50829d2192ea184fe34d7420833f45dd73455a81c9b6`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42222,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07789,"contact_1.speed":0.02502,"push_1.push_distance":0.11247,"retract_1.speed":0.05789},"optimized_scores":{"best_composite_score":0.81217,"best_fitness_score":0.82217,"best_task_score":0.88571},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":699.0,"contact_point_centroid":[0.47027,-0.07428,0.03653],"force_p95":18.84154,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.23373,"mean_force":4.27187,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46607,-0.06237,0.01993]},{"body_a":"world","body_b":"push_box","contact_count":1061.0,"contact_point_centroid":[0.47292,-0.11129,-4e-05],"force_p95":9.9383,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.72321,"mean_force":3.22356,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46433,-0.05706,0.01994]},{"body_a":"world","body_b":"push_box","contact_count":3987.0,"contact_point_centroid":[0.49955,-0.16475,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98814,"mean_force":0.24703,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4844,-0.11567,0.07007]},{"body_a":"world","body_b":"push_box","contact_count":3508.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47386,0.02271,0.16636]},{"body_a":"world","body_b":"push_box","contact_count":3588.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44615,0.02374,0.02642]}],"total_contact_groups":5},"final_pose_error":0.05141,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49956,-0.16467,0.02499],"final_tcp_position":[0.48459,-0.11464,0.12064],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":37.23373,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":877.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3508.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.44912,0.04573,0.0343],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07788,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":897.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":13.73835,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3588.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.4464,0.00538,0.02262],"tcp_start":[0.44912,0.04573,0.0343],"tcp_to_object_dist_end":0.03724,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":829.0,"n_steps_budget":930.0,"object_pos_end":[0.49918,-0.16445,0.0252],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.01447,"object_to_goal_dist_start":0.12843,"object_z_max":0.02569,"peak_contact_force":2.05525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1760.0,"raw_peak_contact_force":37.23373,"tcp_end":[0.48788,-0.12782,0.02022],"tcp_start":[0.4464,0.00538,0.02262],"tcp_to_object_dist_end":0.03866,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49956,-0.16467,0.02499],"object_pos_start":[0.49918,-0.16445,0.0252],"object_to_goal_dist_end":0.01468,"object_to_goal_dist_start":0.01447,"object_z_max":0.0252,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3987.0,"raw_peak_contact_force":0.98814,"tcp_end":[0.48459,-0.11464,0.12064],"tcp_start":[0.48788,-0.12782,0.02022],"tcp_to_object_dist_end":0.10898,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```