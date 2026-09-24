## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7965 | 0.91 | ✅ accepted |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.5286 | 0.76 | ❌ rejected |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.0519 | 0.08 | ❌ rejected |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | 0.3752 | 0.72 | ❌ rejected |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1724 | 0.16 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.796) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
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
  control: admittance_control
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_1
  type: push
  generator: linear_cartesian
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
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.796
- **task_score** (E): 0.911
- **fitness_score**: 0.806  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2801 |
| contact_1 | 1.00 | 1.00 | 0.0452 |
| push_1 | 0.67 | 1.00 | 0.1458 |
| retract_1 | 0.00 | 1.00 | 0.1656 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.081, 0.035) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.081, 0.035)→(0.491, 0.038, 0.023) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 18.633 | 0.245 |
| push_1 | push | 0.67 / step_budget | (0.491, 0.038, 0.023)→(0.495, -0.107, 0.020) | (0.496, 0.001, 0.025)→(0.498, -0.144, 0.026) | 0.152→0.016 | 1.00 / 2.000 | 5.762 | 60.933 |
| retract_1 | retract | 0.00 / step_budget | (0.495, -0.107, 0.020)→(0.494, 0.042, 0.091) | (0.498, -0.144, 0.026)→(0.498, -0.144, 0.025) | 0.016→0.015 | 1.00 / 4.000 | 0.245 | 6.381 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.427
- goal_progress: 0.954
- terminal_score: 0.954
- phase_score: 0.820
- phase_breakdown.approach_score: 0.822
- phase_breakdown.contact_score: 0.763
- phase_breakdown.push_score: 0.854

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.874
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.954
- **Median Q (composite search score)**: 0.842
- **K-run variance**: 0.0065
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.273


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71154,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13941,"contact_1.contact_force":19.19364,"push_1.push_distance":0.10524,"push_1.push_speed":0.06659},"optimized_scores":{"best_composite_score":0.86384,"best_fitness_score":0.87384,"best_task_score":0.95432},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1634.0,"contact_point_centroid":[0.52005,-0.11079,-0.00014],"force_p95":50.52896,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.3509,"mean_force":27.00361,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50473,-0.05428,0.02108]},{"body_a":"push_box","body_b":"link7","contact_count":943.0,"contact_point_centroid":[0.52999,-0.07105,0.05403],"force_p95":45.468,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.53409,"mean_force":33.15899,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50473,-0.05309,0.02096]},{"body_a":"attachment","body_b":"push_box","contact_count":991.0,"contact_point_centroid":[0.52209,-0.06448,0.05034],"force_p95":42.54099,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.2607,"mean_force":28.69516,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50465,-0.05361,0.02095]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.52152,-0.14157,0.05341],"force_p95":2.15979,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.17652,"mean_force":2.00917,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49745,-0.1193,0.0202]},{"body_a":"world","body_b":"push_box","contact_count":3942.0,"contact_point_centroid":[0.49897,-0.15583,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.93505,"mean_force":0.24922,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49436,-0.04115,0.05307]},{"body_a":"attachment","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.51483,-0.12938,0.05277],"force_p95":1.40065,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.55086,"mean_force":0.55545,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49656,-0.11791,0.02018]},{"body_a":"world","body_b":"push_box","contact_count":3584.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50457,0.04257,0.17098]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5095,0.03174,0.0254]}],"total_contact_groups":8},"final_pose_error":0.13299,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49893,-0.15554,0.02499],"final_tcp_position":[0.49519,0.0322,0.08848],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":67.3509,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":896.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3584.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51151,0.05414,0.03326],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":450.0,"n_steps_budget":600.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":23.86761,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.511,0.0093,0.02161],"tcp_start":[0.51151,0.05414,0.03326],"tcp_to_object_dist_end":0.03748,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49935,-0.15712,0.02734],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.00752,"object_to_goal_dist_start":0.12347,"object_z_max":0.02858,"peak_contact_force":14.35081,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3568.0,"raw_peak_contact_force":67.3509,"tcp_end":[0.49747,-0.11924,0.02021],"tcp_start":[0.511,0.0093,0.02161],"tcp_to_object_dist_end":0.03859,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49893,-0.15554,0.02499],"object_pos_start":[0.49935,-0.15712,0.02734],"object_to_goal_dist_end":0.00564,"object_to_goal_dist_start":0.00752,"object_z_max":0.02734,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3960.0,"raw_peak_contact_force":2.17652,"tcp_end":[0.49519,0.0322,0.08848],"tcp_start":[0.49747,-0.11924,0.02021],"tcp_to_object_dist_end":0.19822,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81935,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15557,"contact_1.contact_force":8.20089,"push_1.push_distance":0.19174,"push_1.push_speed":0.09984},"optimized_scores":{"best_composite_score":0.68343,"best_fitness_score":0.69343,"best_task_score":0.84786},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1335.0,"contact_point_centroid":[0.50619,-0.04863,-0.0001],"force_p95":57.10202,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.19856,"mean_force":17.78124,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49488,0.0043,0.02068]},{"body_a":"attachment","body_b":"push_box","contact_count":938.0,"contact_point_centroid":[0.50819,-0.00521,0.0431],"force_p95":51.32126,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.74919,"mean_force":18.28858,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49486,0.00586,0.02069]},{"body_a":"push_box","body_b":"link7","contact_count":529.0,"contact_point_centroid":[0.52202,0.0133,0.0534],"force_p95":43.27246,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.71425,"mean_force":24.19211,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49511,0.03399,0.02128]},{"body_a":"push_box","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.52405,-0.10343,0.05039],"force_p95":6.43298,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.29785,"mean_force":4.90557,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49334,-0.0781,0.02048]},{"body_a":"world","body_b":"push_box","contact_count":3864.0,"contact_point_centroid":[0.49987,-0.11839,-2e-05],"force_p95":0.25237,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.17647,"mean_force":0.30337,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49285,-0.0063,0.05771]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49807,0.07938,0.1793]},{"body_a":"world","body_b":"push_box","contact_count":1704.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49517,0.11069,0.02883]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49521,-0.09426,0.0197],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.495,-0.08229,0.01975]}],"total_contact_groups":8},"final_pose_error":0.10259,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49995,-0.11895,0.02499],"final_tcp_position":[0.49451,0.0627,0.0964],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":74.19856,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49747,0.13125,0.03852],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07847,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":10.02121,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1704.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49618,0.09104,0.02329],"tcp_start":[0.49747,0.13125,0.03852],"tcp_to_object_dist_end":0.03739,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49969,-0.11908,0.02513],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.03092,"object_to_goal_dist_start":0.20406,"object_z_max":0.0295,"peak_contact_force":1.28913,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2802.0,"raw_peak_contact_force":74.19856,"tcp_end":[0.49501,-0.08222,0.01976],"tcp_start":[0.49618,0.09104,0.02329],"tcp_to_object_dist_end":0.03754,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49995,-0.11895,0.02499],"object_pos_start":[0.49969,-0.11908,0.02513],"object_to_goal_dist_end":0.03105,"object_to_goal_dist_start":0.03092,"object_z_max":0.02754,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3904.0,"raw_peak_contact_force":16.29785,"tcp_end":[0.49451,0.0627,0.0964],"tcp_start":[0.49501,-0.08222,0.01976],"tcp_to_object_dist_end":0.19526,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52326,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.20416,"contact_1.contact_force":11.03092,"push_1.push_distance":0.1107,"push_1.push_speed":0.05007},"optimized_scores":{"best_composite_score":0.84217,"best_fitness_score":0.85217,"best_task_score":0.92939},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1581.0,"contact_point_centroid":[0.4856,-0.10626,-7e-05],"force_p95":31.80793,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.24805,"mean_force":7.02354,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47994,-0.06074,0.01973]},{"body_a":"attachment","body_b":"push_box","contact_count":924.0,"contact_point_centroid":[0.48647,-0.06562,0.03291],"force_p95":25.27703,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.21835,"mean_force":8.81353,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47857,-0.05383,0.01978]},{"body_a":"push_box","body_b":"link7","contact_count":299.0,"contact_point_centroid":[0.49747,-0.03521,0.05117],"force_p95":22.74607,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.59702,"mean_force":14.82323,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47027,-0.01242,0.02012]},{"body_a":"world","body_b":"push_box","contact_count":3994.0,"contact_point_centroid":[0.49446,-0.15728,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66796,"mean_force":0.24587,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49098,-0.04227,0.05248]},{"body_a":"world","body_b":"push_box","contact_count":3528.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48423,0.04423,0.17157]},{"body_a":"world","body_b":"push_box","contact_count":1780.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46615,0.035,0.02673]}],"total_contact_groups":6},"final_pose_error":0.1331,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49449,-0.15725,0.02499],"final_tcp_position":[0.4931,0.0322,0.08842],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":41.24805,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":882.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3528.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.46891,0.05747,0.03438],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":445.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":22.00887,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1780.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4667,0.01281,0.02262],"tcp_start":[0.46891,0.05747,0.03438],"tcp_to_object_dist_end":0.03736,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4943,-0.15666,0.025],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00877,"object_to_goal_dist_start":0.12903,"object_z_max":0.03027,"peak_contact_force":1.64627,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2804.0,"raw_peak_contact_force":41.24805,"tcp_end":[0.49266,-0.11963,0.01982],"tcp_start":[0.4667,0.01281,0.02262],"tcp_to_object_dist_end":0.03743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49449,-0.15725,0.02499],"object_pos_start":[0.4943,-0.15666,0.025],"object_to_goal_dist_end":0.00911,"object_to_goal_dist_start":0.00877,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3994.0,"raw_peak_contact_force":0.66796,"tcp_end":[0.4931,0.0322,0.08842],"tcp_start":[0.49266,-0.11963,0.01982],"tcp_to_object_dist_end":0.19979,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```