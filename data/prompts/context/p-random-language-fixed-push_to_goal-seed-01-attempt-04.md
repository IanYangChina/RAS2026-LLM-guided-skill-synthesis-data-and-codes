## Search State

- **Seed**: 1
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.2563 | 0.01 | ❌ rejected |
| 3 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2063 | 0.55 | ✅ accepted |
| 2 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2061 | 0.55 | ✅ accepted |
| 1 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2057 | 0.53 | ❌ rejected |
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2056 | 0.54 | ✅ accepted |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.256) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
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
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01

```

## Design Metrics

- **Composite score**: 0.256
- **task_score** (E): 0.006
- **fitness_score**: 0.253  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2822 |
| contact | 1.00 | 1.00 | 0.0406 |
| push | 0.00 | 1.00 | 0.0015 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.472, 0.075, 0.033) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / force_exceeded | (0.472, 0.075, 0.033)→(0.470, 0.036, 0.022) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 5.000 | 27.812 | 0.245 |
| push | push | 0.00 / guard_failure | (0.470, 0.036, 0.022)→(0.470, 0.035, 0.022) | (0.474, -0.001, 0.025)→(0.474, -0.002, 0.025) | 0.154→0.153 | 1.00 / 3.000 | 10.541 | 30.474 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.003
- lateral_force_integral: None
- approach_alignment: 0.456
- goal_progress: 0.002
- terminal_score: 0.002
- phase_score: 0.427
- phase_breakdown.approach_score: 0.823
- phase_breakdown.push_score: 0.060
- phase_breakdown.contact_score: 0.775

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.257
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.013
- **Median Q (composite search score)**: 0.259
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.357


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97143,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.14836,"approach.approach_tolerance":0.01162,"contact.contact_force_threshold":8.21579,"contact.contact_speed":0.11829,"push.push_speed":0.0651,"push.push_tolerance":0.02696},"optimized_scores":{"best_composite_score":0.24919,"best_fitness_score":0.24586,"best_task_score":0.01315},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.49734,0.07822,0.02518],"force_p95":28.21466,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.68433,"mean_force":9.36892,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49637,0.0901,0.02097]},{"body_a":"world","body_b":"push_box","contact_count":30.0,"contact_point_centroid":[0.50291,0.05343,-1e-05],"force_p95":11.89869,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.47135,"mean_force":4.40103,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49642,0.09023,0.02103]},{"body_a":"world","body_b":"push_box","contact_count":3724.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49794,0.06392,0.16388]},{"body_a":"world","body_b":"push_box","contact_count":1828.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49552,0.10863,0.0243]}],"total_contact_groups":4},"final_pose_error":0.20809,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50094,0.05137,0.02496],"final_tcp_position":[0.49591,0.088,0.02048],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":34.68433,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":931.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3724.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49752,0.12765,0.03129],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":457.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":30.20601,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1828.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49668,0.09103,0.02132],"tcp_start":[0.49752,0.12765,0.03129],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,0.05137,0.02496],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20138,"object_to_goal_dist_start":0.20406,"object_z_max":0.02509,"peak_contact_force":0.00073,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":44.0,"raw_peak_contact_force":34.68433,"subtask_id":"push","tcp_end":[0.49591,0.088,0.02048],"tcp_start":[0.49668,0.09103,0.02132],"tcp_to_object_dist_end":0.03724,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72093,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.09568,"approach.approach_tolerance":0.0149,"contact.contact_force_threshold":7.5852,"contact.contact_speed":0.11287,"push.push_speed":0.05472,"push.push_tolerance":0.01825},"optimized_scores":{"best_composite_score":0.25925,"best_fitness_score":0.25592,"best_task_score":0.00136},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.46717,0.0007,0.02216],"force_p95":29.42412,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.9509,"mean_force":17.37182,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46716,0.01264,0.02214]},{"body_a":"world","body_b":"push_box","contact_count":20.0,"contact_point_centroid":[0.47136,-0.02425,-2e-05],"force_p95":8.36794,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.52382,"mean_force":5.38365,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.46715,0.01262,0.02213]},{"body_a":"world","body_b":"push_box","contact_count":3460.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48378,0.02619,0.16619]},{"body_a":"world","body_b":"push_box","contact_count":1884.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.46664,0.03231,0.02637]}],"total_contact_groups":4},"final_pose_error":0.13644,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47137,-0.02437,0.02497],"final_tcp_position":[0.4671,0.01238,0.02196],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":30.9509,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":865.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3460.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46911,0.05271,0.03396],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07745,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":471.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":27.05483,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1884.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.46722,0.01279,0.02225],"tcp_start":[0.46911,0.05271,0.03396],"tcp_to_object_dist_end":0.0373,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.47137,-0.02437,0.02497],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12885,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":30.9509,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":26.0,"raw_peak_contact_force":30.9509,"subtask_id":"push","tcp_end":[0.4671,0.01238,0.02196],"tcp_start":[0.46722,0.01279,0.02225],"tcp_to_object_dist_end":0.03711,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02985,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.15408,"approach.approach_tolerance":0.0082,"contact.contact_force_threshold":6.40568,"contact.contact_speed":0.13507,"push.push_speed":0.02064,"push.push_tolerance":0.01002},"optimized_scores":{"best_composite_score":0.26058,"best_fitness_score":0.25724,"best_task_score":0.00238},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.44637,-0.00677,0.02243],"force_p95":24.67272,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.78538,"mean_force":15.65499,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.44634,0.00515,0.02242]},{"body_a":"world","body_b":"push_box","contact_count":36.0,"contact_point_centroid":[0.45023,-0.0317,-2e-05],"force_p95":6.88648,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.8526,"mean_force":4.52537,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.44633,0.00514,0.0224]},{"body_a":"world","body_b":"push_box","contact_count":3140.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47393,0.02273,0.16631]},{"body_a":"world","body_b":"push_box","contact_count":1896.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.44638,0.02515,0.02687]}],"total_contact_groups":4},"final_pose_error":0.13596,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45028,-0.03191,0.02501],"final_tcp_position":[0.44627,0.00486,0.02213],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":26.1764,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":785.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3140.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.44925,0.04574,0.03431],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07789,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":474.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":26.1764,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.44646,0.00535,0.02263],"tcp_start":[0.44925,0.04574,0.03431],"tcp_to_object_dist_end":0.0372,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03191,0.02501],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12813,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.67215,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":46.0,"raw_peak_contact_force":25.78538,"subtask_id":"push","tcp_end":[0.44627,0.00486,0.02213],"tcp_start":[0.44646,0.00535,0.02263],"tcp_to_object_dist_end":0.0371,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```