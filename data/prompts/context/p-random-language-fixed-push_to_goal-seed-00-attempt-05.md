## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.0617 | 0.03 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0191 | 0.03 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | 0.1042 | 0.07 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0570 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0670 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`
- Frozen object start: [0.5164354024785746, -0.027625594348335558, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5164354024785746, -0.027625594348335558, 0.025)
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
  frozen_object_start: [0.5164, -0.0276, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5164354024785746, -0.027625594348335558, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0164, -0.1224, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183

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

## Current Skill (Q=-0.062) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
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
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: -0.062
- **task_score** (E): 0.034
- **fitness_score**: 0.218  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2342 |
| contact_1 | 0.67 | 1.00 | 0.0739 |
| push_1 | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.076, 0.082) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / step_budget | (0.493, 0.076, 0.082)→(0.492, 0.033, 0.023) | (0.496, 0.001, 0.025)→(0.497, -0.004, 0.025) | 0.152→0.147 | 1.00 / 4.333 | 4.042 | 13.875 |
| push_1 | push | 0.00 / guard_failure | (0.492, 0.033, 0.023)→(0.492, 0.033, 0.022) | (0.497, -0.004, 0.025)→(0.497, -0.004, 0.025) | 0.147→0.147 | 1.00 / 4.667 | 16.848 | 14.323 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.039
- lateral_force_integral: None
- approach_alignment: 0.489
- goal_progress: 0.037
- terminal_score: 0.037
- phase_score: 0.351
- phase_breakdown.approach_score: 0.312
- phase_breakdown.contact_score: 0.837
- phase_breakdown.push_score: 0.074

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.225
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.037
- **Median Q (composite search score)**: -0.058
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.533


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1efc9b29f7d131941a1bd842274a029ca5b2a2ff6a8656033ab118e32e2fae7d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6150c547b3cd2920ed4582689733d59ef61d18dc295ccd2a0d2317d1cf4e7764`; realized-scene SHA-256: `79fe20ee7316d80bc617c84166fccacf882b4f96b2faf4b155be83e4f318b183`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51644,-0.02763,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01644,-0.12237,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51644,-0.02763,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51515,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08015,"contact_1.contact_force_threshold":22.45935,"contact_1.contact_speed":0.03981,"push_1.push_depth":0.1534,"push_1.push_speed":0.03858},"optimized_scores":{"best_composite_score":-0.05485,"best_fitness_score":0.22515,"best_task_score":0.03687},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":95.0,"contact_point_centroid":[0.51603,-0.00488,0.03493],"force_p95":12.19416,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.63799,"mean_force":6.49477,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51174,0.00704,0.02555]},{"body_a":"world","body_b":"push_box","contact_count":3724.0,"contact_point_centroid":[0.5165,-0.02814,-1e-05],"force_p95":1.60288,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.52166,"mean_force":0.41128,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51021,0.02487,0.04834]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.51212,-0.00736,0.02239],"force_p95":8.42364,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.42364,"mean_force":8.42364,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51204,0.00463,0.02239]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.5174,-0.03229,-4e-05],"force_p95":3.08392,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.16187,"mean_force":2.30156,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51204,0.00463,0.02239]},{"body_a":"world","body_b":"push_box","contact_count":2932.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50492,0.0241,0.19143]}],"total_contact_groups":5},"final_pose_error":0.27851,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51741,-0.03236,0.02494],"final_tcp_position":[0.51201,0.00461,0.02234],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":16.0,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":733.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2932.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51179,0.04897,0.08288],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.51742,-0.03232,0.02493],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.11896,"object_to_goal_dist_start":0.12347,"object_z_max":0.0251,"peak_contact_force":6.20036,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3819.0,"raw_peak_contact_force":14.63799,"subtask_id":"contact","tcp_end":[0.51204,0.00463,0.02239],"tcp_start":[0.51179,0.04897,0.08288],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51741,-0.03236,0.02494],"object_pos_start":[0.51742,-0.03232,0.02493],"object_to_goal_dist_end":0.11892,"object_to_goal_dist_start":0.11896,"object_z_max":0.02493,"peak_contact_force":16.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":8.42364,"subtask_id":"push","tcp_end":[0.51201,0.00461,0.02234],"tcp_start":[0.51204,0.00463,0.02239],"tcp_to_object_dist_end":0.03745,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50142,0.05406,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.88679,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.13907,"contact_1.contact_force_threshold":24.38336,"contact_1.contact_speed":0.02196,"push_1.push_depth":0.13148,"push_1.push_speed":0.05778},"optimized_scores":{"best_composite_score":-0.0721,"best_fitness_score":0.2079,"best_task_score":0.02822},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.50959,0.07347,0.04738],"force_p95":11.61875,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.61875,"mean_force":11.61875,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49715,0.08512,0.02183]},{"body_a":"attachment","body_b":"push_box","contact_count":269.0,"contact_point_centroid":[0.49794,0.07627,0.02783],"force_p95":7.31289,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.23332,"mean_force":4.91944,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49687,0.08822,0.02599]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.50248,0.04833,-3e-05],"force_p95":6.19933,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.33418,"mean_force":3.05581,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49715,0.08512,0.02183]},{"body_a":"world","body_b":"push_box","contact_count":3753.0,"contact_point_centroid":[0.50158,0.05276,-1e-05],"force_p95":2.22958,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.75134,"mean_force":0.58791,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49604,0.10045,0.04244]},{"body_a":"world","body_b":"push_box","contact_count":3300.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49799,0.06312,0.18914]}],"total_contact_groups":5},"final_pose_error":0.3366,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50248,0.04829,0.02494],"final_tcp_position":[0.49713,0.08511,0.02179],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":11.61875,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":825.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3300.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.4977,0.1268,0.08067],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09168,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":986.0,"n_steps_budget":1000.0,"object_pos_end":[0.50248,0.04831,0.02493],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.19833,"object_to_goal_dist_start":0.20406,"object_z_max":0.02502,"peak_contact_force":5.31195,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4022.0,"raw_peak_contact_force":9.23332,"subtask_id":"contact","tcp_end":[0.49715,0.08512,0.02183],"tcp_start":[0.4977,0.1268,0.08067],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50248,0.04829,0.02494],"object_pos_start":[0.50248,0.04831,0.02493],"object_to_goal_dist_end":0.1983,"object_to_goal_dist_start":0.19833,"object_z_max":0.02493,"peak_contact_force":11.61875,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":11.61875,"subtask_id":"push","tcp_end":[0.49713,0.08511,0.02179],"tcp_start":[0.49715,0.08512,0.02183],"tcp_to_object_dist_end":0.03734,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34884,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.17933,"contact_1.contact_force_threshold":23.45737,"contact_1.contact_speed":0.02882,"push_1.push_depth":0.15778,"push_1.push_speed":0.01986},"optimized_scores":{"best_composite_score":-0.05805,"best_fitness_score":0.22195,"best_task_score":0.03607},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48272,-0.00366,0.04995],"force_p95":22.92645,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.92645,"mean_force":22.92645,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46715,0.00817,0.02332]},{"body_a":"attachment","body_b":"push_box","contact_count":89.0,"contact_point_centroid":[0.47153,-0.00121,0.03401],"force_p95":13.3669,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.75253,"mean_force":7.23851,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4672,0.01071,0.02672]},{"body_a":"world","body_b":"push_box","contact_count":19.0,"contact_point_centroid":[0.47067,-0.02745,-4e-05],"force_p95":7.64792,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.42108,"mean_force":1.45339,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46724,0.00827,0.02345]},{"body_a":"world","body_b":"push_box","contact_count":2724.0,"contact_point_centroid":[0.47142,-0.0248,-1e-05],"force_p95":2.56767,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.20735,"mean_force":0.48172,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46678,0.02905,0.05068]},{"body_a":"world","body_b":"push_box","contact_count":2520.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48421,0.02569,0.19183]}],"total_contact_groups":5},"final_pose_error":0.29001,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47197,-0.02882,0.02494],"final_tcp_position":[0.46711,0.00809,0.02325],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":22.92645,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":630.0,"n_steps_budget":840.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2520.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46955,0.05214,0.08384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":712.0,"n_steps_budget":1000.0,"object_pos_end":[0.47195,-0.02867,0.02494],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12453,"object_to_goal_dist_start":0.12903,"object_z_max":0.02503,"peak_contact_force":0.61342,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2813.0,"raw_peak_contact_force":17.75253,"subtask_id":"contact","tcp_end":[0.46733,0.00836,0.02359],"tcp_start":[0.46955,0.05214,0.08384],"tcp_to_object_dist_end":0.03735,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.47197,-0.02882,0.02494],"object_pos_start":[0.47195,-0.02867,0.02494],"object_to_goal_dist_end":0.12438,"object_to_goal_dist_start":0.12453,"object_z_max":0.02494,"peak_contact_force":22.92645,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":20.0,"raw_peak_contact_force":22.92645,"subtask_id":"push","tcp_end":[0.46711,0.00809,0.02325],"tcp_start":[0.46733,0.00836,0.02359],"tcp_to_object_dist_end":0.03727,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```