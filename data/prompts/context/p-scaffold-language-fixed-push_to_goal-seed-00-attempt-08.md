## Search State

- **Seed**: 0
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7432 | 0.79 | ❌ rejected |
| 7 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.8088 | 0.91 | ✅ accepted |
| 6 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6468 | 0.90 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.7965 | 0.91 | ✅ accepted |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.5286 | 0.76 | ❌ rejected |

**Proposal policy**: task_score is 0.79 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.743) — your mutation base

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

- **Composite score**: 0.743
- **task_score** (E): 0.793
- **fitness_score**: 0.753  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.67 | 1.00 | 0.2684 |
| contact_1 | 1.00 | 1.00 | 0.0692 |
| push_1 | 0.00 | 1.00 | 0.1558 |
| retract_1 | 1.00 | 1.00 | 0.2303 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.67 / step_budget | (0.500, -0.000, 0.301)→(0.493, 0.095, 0.057) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.095, 0.057)→(0.492, 0.038, 0.024) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 36.051 | 0.245 |
| push_1 | push | 0.00 / step_budget | (0.492, 0.038, 0.024)→(0.495, -0.117, 0.021) | (0.496, 0.001, 0.025)→(0.525, -0.135, 0.028) | 0.152→0.038 | 1.00 / 3.667 | 24.862 | 41.791 |
| retract_1 | retract | 1.00 / step_budget | (0.495, -0.117, 0.021)→(0.493, -0.117, 0.251) | (0.525, -0.135, 0.028)→(0.521, -0.135, 0.025) | 0.038→0.035 | 1.00 / 4.000 | 0.245 | 28.441 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.944
- goal_progress: 0.924
- terminal_score: 0.924
- phase_score: 0.808
- phase_breakdown.approach_score: 0.772
- phase_breakdown.contact_score: 0.771
- phase_breakdown.push_score: 0.843

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.854
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.924
- **Median Q (composite search score)**: 0.801
- **K-run variance**: 0.0130
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.296


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68539,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.05451,"contact_1.contact_force":9.80682,"push_1.push_distance":0.11352,"push_1.push_speed":0.06294},"optimized_scores":{"best_composite_score":0.80129,"best_fitness_score":0.81129,"best_task_score":0.78018},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":843.0,"contact_point_centroid":[0.53472,-0.08776,0.05375],"force_p95":51.36621,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.2184,"mean_force":34.33112,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50124,-0.07689,0.01961]},{"body_a":"world","body_b":"push_box","contact_count":1676.0,"contact_point_centroid":[0.53885,-0.11587,-0.00018],"force_p95":39.88491,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.27713,"mean_force":24.39297,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50186,-0.07166,0.01964]},{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.53475,-0.13015,0.05454],"force_p95":41.82775,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.73483,"mean_force":16.10435,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49674,-0.12955,0.02135]},{"body_a":"attachment","body_b":"push_box","contact_count":956.0,"contact_point_centroid":[0.51703,-0.07594,0.05248],"force_p95":35.29999,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.21044,"mean_force":22.65426,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50202,-0.06823,0.01943]},{"body_a":"world","body_b":"push_box","contact_count":2618.0,"contact_point_centroid":[0.52795,-0.15554,-1e-05],"force_p95":0.34268,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.23829,"mean_force":0.28892,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49426,-0.12881,0.14306]},{"body_a":"attachment","body_b":"push_box","contact_count":34.0,"contact_point_centroid":[0.51225,-0.13181,0.05519],"force_p95":18.10633,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.22928,"mean_force":3.20392,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49516,-0.12919,0.03164]},{"body_a":"world","body_b":"push_box","contact_count":3904.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50444,0.05943,0.17483]},{"body_a":"world","body_b":"push_box","contact_count":1980.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51002,0.03331,0.02425]}],"total_contact_groups":8},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52664,-0.15521,0.02499],"final_tcp_position":[0.49502,-0.12895,0.25157],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":61.2184,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":976.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3904.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.51174,0.05798,0.03167],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":495.0,"n_steps_budget":600.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":37.04767,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1980.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.51165,0.00929,0.0209],"tcp_start":[0.51174,0.05798,0.03167],"tcp_to_object_dist_end":0.03745,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53053,-0.15463,0.02904],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.03115,"object_to_goal_dist_start":0.12347,"object_z_max":0.0294,"peak_contact_force":50.4299,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3475.0,"raw_peak_contact_force":61.2184,"subtask_id":"push","tcp_end":[0.49712,-0.12943,0.02118],"tcp_start":[0.51165,0.00929,0.0209],"tcp_to_object_dist_end":0.04259,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":702.0,"n_steps_budget":1000.0,"object_pos_end":[0.52664,-0.15521,0.02499],"object_pos_start":[0.53053,-0.15463,0.02904],"object_to_goal_dist_end":0.02714,"object_to_goal_dist_start":0.03115,"object_z_max":0.02938,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2660.0,"raw_peak_contact_force":48.73483,"tcp_end":[0.49502,-0.12895,0.25157],"tcp_start":[0.49712,-0.12943,0.02118],"tcp_to_object_dist_end":0.23028,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92814,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08768,"contact_1.contact_force":16.69334,"push_1.push_distance":0.13365,"push_1.push_speed":0.09988},"optimized_scores":{"best_composite_score":0.58403,"best_fitness_score":0.59403,"best_task_score":0.67356},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":795.0,"contact_point_centroid":[0.50584,-0.01215,0.04781],"force_p95":18.89502,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.94341,"mean_force":5.74474,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49416,-0.00377,0.02327]},{"body_a":"world","body_b":"push_box","contact_count":1399.0,"contact_point_centroid":[0.5334,-0.04768,-6e-05],"force_p95":18.13226,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.63076,"mean_force":6.28716,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49424,-0.01222,0.02323]},{"body_a":"push_box","body_b":"link7","contact_count":286.0,"contact_point_centroid":[0.53079,-0.04687,0.05602],"force_p95":21.23762,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.56597,"mean_force":13.01795,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49451,-0.05325,0.02289]},{"body_a":"push_box","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.5321,-0.08833,0.05473],"force_p95":11.30949,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.46049,"mean_force":4.47093,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49426,-0.09563,0.02204]},{"body_a":"world","body_b":"push_box","contact_count":2647.0,"contact_point_centroid":[0.53161,-0.09072,-1e-05],"force_p95":0.36016,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.47883,"mean_force":0.26067,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49147,-0.09508,0.14172]},{"body_a":"attachment","body_b":"push_box","contact_count":26.0,"contact_point_centroid":[0.50945,-0.09582,0.05373],"force_p95":1.23283,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.24593,"mean_force":0.85713,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49215,-0.09552,0.03204]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49875,0.10001,0.2298]},{"body_a":"world","body_b":"push_box","contact_count":2484.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49639,0.12585,0.06437]}],"total_contact_groups":8},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53029,-0.09067,0.02499],"final_tcp_position":[0.49221,-0.09516,0.25225],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":35.03923,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.49856,0.16158,0.10494],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13402,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":621.0,"n_steps_budget":720.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":35.03923,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2484.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49717,0.09104,0.02818],"tcp_start":[0.49856,0.16158,0.10494],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53511,-0.09073,0.02884],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.069,"object_to_goal_dist_start":0.20406,"object_z_max":0.02963,"peak_contact_force":4.8997,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2480.0,"raw_peak_contact_force":32.94341,"subtask_id":"push","tcp_end":[0.49432,-0.0955,0.02206],"tcp_start":[0.49717,0.09104,0.02818],"tcp_to_object_dist_end":0.04163,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.53029,-0.09067,0.02499],"object_pos_start":[0.53511,-0.09073,0.02884],"object_to_goal_dist_end":0.06661,"object_to_goal_dist_start":0.069,"object_z_max":0.02884,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2676.0,"raw_peak_contact_force":12.46049,"tcp_end":[0.49221,-0.09516,0.25225],"tcp_start":[0.49432,-0.0955,0.02206],"tcp_to_object_dist_end":0.23048,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55102,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29698,"contact_1.contact_force":8.33231,"push_1.push_distance":0.10599,"push_1.push_speed":0.03794},"optimized_scores":{"best_composite_score":0.84423,"best_fitness_score":0.85423,"best_task_score":0.92411},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":814.0,"contact_point_centroid":[0.48588,-0.06885,0.0421],"force_p95":16.33921,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.21177,"mean_force":5.55544,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47873,-0.05721,0.01876]},{"body_a":"world","body_b":"push_box","contact_count":1316.0,"contact_point_centroid":[0.4964,-0.1133,-6e-05],"force_p95":13.14671,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.99445,"mean_force":4.82651,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.479,-0.05813,0.01884]},{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.52601,-0.14122,0.05361],"force_p95":20.73811,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.12805,"mean_force":5.71109,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49344,-0.12607,0.01953]},{"body_a":"world","body_b":"push_box","contact_count":2540.0,"contact_point_centroid":[0.50605,-0.16027,-2e-05],"force_p95":0.38364,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.11258,"mean_force":0.28178,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4909,-0.12539,0.14313]},{"body_a":"push_box","body_b":"link7","contact_count":151.0,"contact_point_centroid":[0.52427,-0.12133,0.05256],"force_p95":16.42558,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.05398,"mean_force":8.59442,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48983,-0.10937,0.019]},{"body_a":"attachment","body_b":"push_box","contact_count":45.0,"contact_point_centroid":[0.50327,-0.13545,0.05416],"force_p95":1.19365,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.82365,"mean_force":1.06054,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49156,-0.12563,0.03374]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48524,0.06862,0.1795]},{"body_a":"world","body_b":"push_box","contact_count":1984.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46672,0.03819,0.02631]}],"total_contact_groups":8},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50489,-0.15848,0.02499],"final_tcp_position":[0.49162,-0.12553,0.24953],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":36.06733,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.46924,0.06465,0.03416],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08933,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":496.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":36.06733,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1984.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.46729,0.01275,0.02197],"tcp_start":[0.46924,0.06465,0.03416],"tcp_to_object_dist_end":0.03728,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50968,-0.16092,0.02724],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.01476,"object_to_goal_dist_start":0.12903,"object_z_max":0.02822,"peak_contact_force":19.25724,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2281.0,"raw_peak_contact_force":31.21177,"subtask_id":"push","tcp_end":[0.49374,-0.126,0.01932],"tcp_start":[0.46729,0.01275,0.02197],"tcp_to_object_dist_end":0.03919,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.50489,-0.15848,0.02499],"object_pos_start":[0.50968,-0.16092,0.02724],"object_to_goal_dist_end":0.00979,"object_to_goal_dist_start":0.01476,"object_z_max":0.02811,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2593.0,"raw_peak_contact_force":24.12805,"tcp_end":[0.49162,-0.12553,0.24953],"tcp_start":[0.49374,-0.126,0.01932],"tcp_to_object_dist_end":0.22733,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```