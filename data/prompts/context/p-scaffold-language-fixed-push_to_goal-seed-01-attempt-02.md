## Search State

- **Seed**: 1
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6702 | 0.82 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5894 | 0.86 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6954 | 0.86 | ✅ accepted |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.670) — your mutation base

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

- **Composite score**: 0.670
- **task_score** (E): 0.820
- **fitness_score**: 0.764  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2822 |
| contact_1 | 0.67 | 1.00 | 0.0371 |
| push_1 | 0.67 | 1.00 | 0.1506 |
| retract_1 | 0.00 | 1.00 | 0.1220 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.472, 0.075, 0.033) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.472, 0.075, 0.033)→(0.469, 0.040, 0.023) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.667 | 8.140 | 0.245 |
| push_1 | push | 0.67 / step_budget | (0.469, 0.040, 0.023)→(0.494, -0.107, 0.020) | (0.474, -0.001, 0.025)→(0.485, -0.138, 0.025) | 0.154→0.027 | 1.00 / 4.333 | 11.733 | 51.141 |
| retract_1 | retract | 0.00 / step_budget | (0.494, -0.107, 0.020)→(0.493, -0.011, 0.095) | (0.485, -0.138, 0.025)→(0.484, -0.140, 0.025) | 0.027→0.027 | 1.00 / 4.000 | 0.245 | 4.302 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.845
- lateral_force_integral: None
- approach_alignment: 0.547
- goal_progress: 0.671
- terminal_score: 0.671
- phase_score: 0.799
- phase_breakdown.push_score: 0.806
- phase_breakdown.contact_score: 0.773
- phase_breakdown.approach_score: 0.822

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.836
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.930
- **Median Q (composite search score)**: 0.697
- **K-run variance**: 0.0047
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.279


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69006,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.16332,"contact_1.speed":0.0281,"push_1.push_distance":0.1979,"retract_1.speed":0.06909},"optimized_scores":{"best_composite_score":0.6969,"best_fitness_score":0.7069,"best_task_score":0.85863},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1434.0,"contact_point_centroid":[0.50238,-0.04716,-9e-05],"force_p95":53.39295,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.39589,"mean_force":14.80877,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49458,0.00197,0.01948]},{"body_a":"push_box","body_b":"link7","contact_count":475.0,"contact_point_centroid":[0.52148,0.02154,0.05236],"force_p95":41.72809,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.01044,"mean_force":25.05183,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4949,0.04349,0.02008]},{"body_a":"attachment","body_b":"push_box","contact_count":935.0,"contact_point_centroid":[0.50528,-0.0048,0.0379],"force_p95":48.43395,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.07772,"mean_force":16.17955,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49458,0.0065,0.01951]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49492,-0.09514,0.01922],"force_p95":2.87082,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.98628,"mean_force":2.13083,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4948,-0.08318,0.01923]},{"body_a":"world","body_b":"push_box","contact_count":3974.0,"contact_point_centroid":[0.49815,-0.12114,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.48048,"mean_force":0.24825,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49216,-0.03457,0.06211]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52319,-0.09783,0.05],"force_p95":0.39184,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.43538,"mean_force":0.14513,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49444,-0.08329,0.01924]},{"body_a":"world","body_b":"push_box","contact_count":3976.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49774,0.06374,0.16404]},{"body_a":"world","body_b":"push_box","contact_count":2876.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4949,0.10791,0.02412]}],"total_contact_groups":8},"final_pose_error":0.14068,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4982,-0.12121,0.02499],"final_tcp_position":[0.49349,0.01805,0.10165],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":71.39589,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":994.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3976.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49731,0.12754,0.03129],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":719.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":14.06028,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2876.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49604,0.09105,0.02164],"tcp_start":[0.49731,0.12754,0.03129],"tcp_to_object_dist_end":0.03753,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49853,-0.11995,0.02487],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.03009,"object_to_goal_dist_start":0.20406,"object_z_max":0.02805,"peak_contact_force":17.2213,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2844.0,"raw_peak_contact_force":71.39589,"tcp_end":[0.49484,-0.08306,0.01925],"tcp_start":[0.49604,0.09105,0.02164],"tcp_to_object_dist_end":0.03749,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4982,-0.12121,0.02499],"object_pos_start":[0.49853,-0.11995,0.02487],"object_to_goal_dist_end":0.02885,"object_to_goal_dist_start":0.03009,"object_z_max":0.02504,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3980.0,"raw_peak_contact_force":2.98628,"tcp_end":[0.49349,0.01805,0.10165],"tcp_start":[0.49484,-0.08306,0.01925],"tcp_to_object_dist_end":0.15903,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20765,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.21355,"contact_1.speed":0.01603,"push_1.push_distance":0.10317,"retract_1.speed":0.0322},"optimized_scores":{"best_composite_score":0.57573,"best_fitness_score":0.83573,"best_task_score":0.92986},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1386.0,"contact_point_centroid":[0.48354,-0.091,-5e-05],"force_p95":23.60176,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.02881,"mean_force":5.12411,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47839,-0.04601,0.02076]},{"body_a":"attachment","body_b":"push_box","contact_count":734.0,"contact_point_centroid":[0.48803,-0.06516,0.03474],"force_p95":23.34923,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.3593,"mean_force":7.79742,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47981,-0.05331,0.02047]},{"body_a":"push_box","body_b":"link7","contact_count":239.0,"contact_point_centroid":[0.50303,-0.05305,0.05125],"force_p95":11.79664,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.51412,"mean_force":6.65006,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47512,-0.03113,0.02074]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49413,-0.13183,0.02017],"force_p95":1.49792,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.5325,"mean_force":1.18667,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49442,-0.11986,0.02001]},{"body_a":"world","body_b":"push_box","contact_count":3987.0,"contact_point_centroid":[0.49519,-0.15769,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.43851,"mean_force":0.24671,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49157,-0.0743,0.05648]},{"body_a":"world","body_b":"push_box","contact_count":3424.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48366,0.02611,0.16637]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46571,0.03579,0.02689]}],"total_contact_groups":7},"final_pose_error":0.18596,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49516,-0.15765,0.02499],"final_tcp_position":[0.49266,-0.02641,0.09166],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":40.02881,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3424.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46886,0.05266,0.03395],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.46616,0.02255,0.0244],"tcp_start":[0.46886,0.05266,0.03395],"tcp_to_object_dist_end":0.04702,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":859.0,"n_steps_budget":960.0,"object_pos_end":[0.49541,-0.15677,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00818,"object_to_goal_dist_start":0.12903,"object_z_max":0.02843,"peak_contact_force":16.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2359.0,"raw_peak_contact_force":40.02881,"tcp_end":[0.49443,-0.11981,0.02002],"tcp_start":[0.46616,0.02255,0.0244],"tcp_to_object_dist_end":0.03731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49516,-0.15765,0.02499],"object_pos_start":[0.49541,-0.15677,0.02499],"object_to_goal_dist_end":0.00905,"object_to_goal_dist_start":0.00818,"object_z_max":0.02501,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3989.0,"raw_peak_contact_force":1.5325,"tcp_end":[0.49266,-0.02641,0.09166],"tcp_start":[0.49443,-0.11981,0.02002],"tcp_to_object_dist_end":0.14722,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4875,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08454,"contact_1.speed":0.04497,"push_1.push_distance":0.09351,"retract_1.speed":0.02375},"optimized_scores":{"best_composite_score":0.73811,"best_fitness_score":0.74811,"best_task_score":0.67121},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1329.0,"contact_point_centroid":[0.46029,-0.1062,-6e-05],"force_p95":29.76413,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.99974,"mean_force":5.858,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47242,-0.06631,0.02008]},{"body_a":"attachment","body_b":"push_box","contact_count":641.0,"contact_point_centroid":[0.47317,-0.06218,0.03339],"force_p95":25.61702,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.76635,"mean_force":8.93372,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46633,-0.05063,0.02024]},{"body_a":"push_box","body_b":"link7","contact_count":231.0,"contact_point_centroid":[0.48139,-0.04003,0.05092],"force_p95":18.03752,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.79987,"mean_force":11.98797,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45364,-0.01742,0.02069]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48717,-0.12811,0.02285],"force_p95":8.38646,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.38646,"mean_force":8.38646,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49332,-0.11824,0.01994]},{"body_a":"world","body_b":"push_box","contact_count":3981.0,"contact_point_centroid":[0.45904,-0.13969,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.5316,"mean_force":0.24804,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49066,-0.07263,0.05666]},{"body_a":"world","body_b":"push_box","contact_count":3404.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47375,0.02263,0.1666]},{"body_a":"world","body_b":"push_box","contact_count":2136.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44571,0.02485,0.02688]}],"total_contact_groups":7},"final_pose_error":0.18442,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45905,-0.13969,0.02499],"final_tcp_position":[0.49195,-0.02483,0.09186],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":41.99974,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":851.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3404.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44887,0.04566,0.03429],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":534.0,"n_steps_budget":750.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":10.11359,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44589,0.00539,0.02309],"tcp_start":[0.44887,0.04566,0.03429],"tcp_to_object_dist_end":0.03728,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":810.0,"n_steps_budget":900.0,"object_pos_end":[0.45965,-0.13865,0.02497],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.04192,"object_to_goal_dist_start":0.12843,"object_z_max":0.03203,"peak_contact_force":1.97769,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2201.0,"raw_peak_contact_force":41.99974,"tcp_end":[0.49332,-0.11824,0.01994],"tcp_start":[0.44589,0.00539,0.02309],"tcp_to_object_dist_end":0.03969,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45905,-0.13969,0.02499],"object_pos_start":[0.45965,-0.13865,0.02497],"object_to_goal_dist_end":0.04223,"object_to_goal_dist_start":0.04192,"object_z_max":0.02511,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3982.0,"raw_peak_contact_force":8.38646,"tcp_end":[0.49195,-0.02483,0.09186],"tcp_start":[0.49332,-0.11824,0.01994],"tcp_to_object_dist_end":0.13692,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```