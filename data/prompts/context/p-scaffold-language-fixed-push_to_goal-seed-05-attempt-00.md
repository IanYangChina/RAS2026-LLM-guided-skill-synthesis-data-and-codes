## Search State

- **Seed**: 5
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4708 | 0.75 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`
- Frozen object start: [0.5366003508494456, 0.03695289476837925, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5366003508494456, 0.03695289476837925, 0.025)
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
  frozen_object_start: [0.5366, 0.037, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5366003508494456, 0.03695289476837925, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

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

## Current Skill (Q=0.471) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
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
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2

```

## Design Metrics

- **Composite score**: 0.471
- **task_score** (E): 0.751
- **fitness_score**: 0.681  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2855 |
| contact_1 | 1.00 | 1.00 | 0.0536 |
| push_1 | 1.00 | 1.00 | 0.1250 |
| retract_1 | 0.00 | 1.00 | 0.1654 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.101, 0.036) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.514, 0.101, 0.036)→(0.514, 0.050, 0.020) | (0.519, 0.022, 0.025)→(0.521, 0.013, 0.025) | 0.173→0.165 | 1.00 / 3.333 | 2.618 | 9.476 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.050, 0.020)→(0.500, -0.074, 0.023) | (0.521, 0.013, 0.025)→(0.511, -0.108, 0.027) | 0.165→0.048 | 1.00 / 2.667 | 44.018 | 87.233 |
| retract_1 | retract | 0.00 / step_budget | (0.500, -0.074, 0.023)→(0.496, 0.071, 0.102) | (0.511, -0.108, 0.027)→(0.508, -0.108, 0.025) | 0.048→0.047 | 1.00 / 4.000 | 0.245 | 30.689 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.425
- goal_progress: 0.953
- terminal_score: 0.953
- phase_score: 0.842
- phase_breakdown.contact_score: 0.871
- phase_breakdown.push_score: 0.834
- phase_breakdown.approach_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.887
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.953
- **Median Q (composite search score)**: 0.373
- **K-run variance**: 0.0212
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.416


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73125,"average_solve_count":160.0,"average_success_count":160.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03729,"push_1.push_depth":0.1,"retract_1.retract_height":0.13106},"optimized_scores":{"best_composite_score":0.36261,"best_fitness_score":0.57261,"best_task_score":0.62551},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":795.0,"contact_point_centroid":[0.54943,-0.01158,0.05488],"force_p95":114.18086,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.72256,"mean_force":76.03686,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51807,0.0039,0.02365]},{"body_a":"attachment","body_b":"push_box","contact_count":796.0,"contact_point_centroid":[0.53691,-0.00475,0.05236],"force_p95":100.17124,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.4453,"mean_force":56.42416,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5181,0.004,0.02365]},{"body_a":"world","body_b":"push_box","contact_count":1537.0,"contact_point_centroid":[0.54383,-0.04666,-0.00031],"force_p95":79.26887,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.91627,"mean_force":51.0753,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51789,0.00262,0.02382]},{"body_a":"world","body_b":"push_box","contact_count":3694.0,"contact_point_centroid":[0.52542,-0.08311,-3e-05],"force_p95":0.24655,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":90.2059,"mean_force":0.49439,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50096,0.02362,0.07095]},{"body_a":"push_box","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.54926,-0.06212,0.05575],"force_p95":80.40718,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.81533,"mean_force":38.84717,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50677,-0.05243,0.03022]},{"body_a":"attachment","body_b":"push_box","contact_count":60.0,"contact_point_centroid":[0.5292,-0.05554,0.06025],"force_p95":62.01736,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.10987,"mean_force":23.28307,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50612,-0.04971,0.03107]},{"body_a":"attachment","body_b":"push_box","contact_count":162.0,"contact_point_centroid":[0.53792,0.0574,0.03815],"force_p95":6.73281,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.60136,"mean_force":2.77549,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53127,0.06934,0.02116]},{"body_a":"world","body_b":"push_box","contact_count":2906.0,"contact_point_centroid":[0.53689,0.03479,-1e-05],"force_p95":1.78946,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.39139,"mean_force":0.40773,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52894,0.09108,0.02608]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51292,0.07216,0.17685]}],"total_contact_groups":9},"final_pose_error":0.07262,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52485,-0.08313,0.02499],"final_tcp_position":[0.49872,0.08955,0.10979],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":130.72256,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53035,0.11538,0.03637],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":823.0,"n_steps_budget":930.0,"object_pos_end":[0.53929,0.02761,0.02502],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1819,"object_to_goal_dist_start":0.1905,"object_z_max":0.02512,"peak_contact_force":1.02004,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3068.0,"raw_peak_contact_force":8.60136,"tcp_end":[0.53188,0.06442,0.02013],"tcp_start":[0.53035,0.11538,0.03637],"tcp_to_object_dist_end":0.03787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":805.0,"n_steps_budget":900.0,"object_pos_end":[0.53341,-0.08465,0.03125],"object_pos_start":[0.53929,0.02761,0.02502],"object_to_goal_dist_end":0.07366,"object_to_goal_dist_start":0.1819,"object_z_max":0.03134,"peak_contact_force":129.89494,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3128.0,"raw_peak_contact_force":130.72256,"tcp_end":[0.50768,-0.0557,0.02901],"tcp_start":[0.53188,0.06442,0.02013],"tcp_to_object_dist_end":0.0388,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52485,-0.08313,0.02499],"object_pos_start":[0.53341,-0.08465,0.03125],"object_to_goal_dist_end":0.07134,"object_to_goal_dist_start":0.07366,"object_z_max":0.0348,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3798.0,"raw_peak_contact_force":90.2059,"tcp_end":[0.49872,0.08955,0.10979],"tcp_start":[0.50768,-0.0557,0.02901],"tcp_to_object_dist_end":0.19414,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71795,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03768,"push_1.push_depth":0.0986,"retract_1.retract_height":0.17689},"optimized_scores":{"best_composite_score":0.67669,"best_fitness_score":0.88669,"best_task_score":0.95322},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1125.0,"contact_point_centroid":[0.50948,-0.10643,-0.00013],"force_p95":60.79171,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.81884,"mean_force":21.70781,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49796,-0.0546,0.01984]},{"body_a":"push_box","body_b":"link7","contact_count":515.0,"contact_point_centroid":[0.52497,-0.05349,0.05245],"force_p95":46.70039,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.75583,"mean_force":30.21386,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49885,-0.03221,0.02001]},{"body_a":"attachment","body_b":"push_box","contact_count":722.0,"contact_point_centroid":[0.51195,-0.0629,0.04407],"force_p95":48.23496,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.34707,"mean_force":21.78761,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49805,-0.05164,0.01983]},{"body_a":"attachment","body_b":"push_box","contact_count":155.0,"contact_point_centroid":[0.50737,0.00196,0.03669],"force_p95":7.25954,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.38855,"mean_force":3.1073,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49973,0.01382,0.02132]},{"body_a":"world","body_b":"push_box","contact_count":3047.0,"contact_point_centroid":[0.50492,-0.02076,-1e-05],"force_p95":1.76698,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.39551,"mean_force":0.40954,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49816,0.03694,0.02522]},{"body_a":"world","body_b":"push_box","contact_count":3986.0,"contact_point_centroid":[0.49978,-0.15614,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01765,"mean_force":0.24654,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49329,-0.0415,0.05253]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.50593,-0.13058,0.04132],"force_p95":0.63527,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.72616,"mean_force":0.18813,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49571,-0.11881,0.01977]},{"body_a":"world","body_b":"push_box","contact_count":3580.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.04658,0.17199]}],"total_contact_groups":8},"final_pose_error":0.13271,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49974,-0.15614,0.02499],"final_tcp_position":[0.49451,0.03257,0.08841],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":78.81884,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3580.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.06252,0.03384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":850.0,"n_steps_budget":960.0,"object_pos_end":[0.50686,-0.02771,0.02498],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12249,"object_to_goal_dist_start":0.13127,"object_z_max":0.02515,"peak_contact_force":0.00036,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3202.0,"raw_peak_contact_force":9.38855,"tcp_end":[0.50011,0.00908,0.02058],"tcp_start":[0.50029,0.06252,0.03384],"tcp_to_object_dist_end":0.03766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":778.0,"n_steps_budget":870.0,"object_pos_end":[0.49996,-0.15525,0.02502],"object_pos_start":[0.50686,-0.02771,0.02498],"object_to_goal_dist_end":0.00525,"object_to_goal_dist_start":0.12249,"object_z_max":0.0281,"peak_contact_force":1.71659,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2362.0,"raw_peak_contact_force":78.81884,"tcp_end":[0.49592,-0.11876,0.01984],"tcp_start":[0.50011,0.00908,0.02058],"tcp_to_object_dist_end":0.03707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49974,-0.15614,0.02499],"object_pos_start":[0.49996,-0.15525,0.02502],"object_to_goal_dist_end":0.00614,"object_to_goal_dist_start":0.00525,"object_z_max":0.02503,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3993.0,"raw_peak_contact_force":1.01765,"tcp_end":[0.49451,0.03257,0.08841],"tcp_start":[0.49592,-0.11876,0.01984],"tcp_to_object_dist_end":0.19915,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75817,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.04394,"push_1.push_depth":0.09463,"retract_1.retract_height":0.10888},"optimized_scores":{"best_composite_score":0.37311,"best_fitness_score":0.58311,"best_task_score":0.67454},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1068.0,"contact_point_centroid":[0.51379,-0.0343,-0.0001],"force_p95":40.28376,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.15857,"mean_force":18.15343,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50373,0.02156,0.01972]},{"body_a":"push_box","body_b":"link7","contact_count":504.0,"contact_point_centroid":[0.53003,0.00736,0.05284],"force_p95":39.5084,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.0213,"mean_force":22.7728,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50458,0.02841,0.01985]},{"body_a":"attachment","body_b":"push_box","contact_count":648.0,"contact_point_centroid":[0.5184,0.00428,0.04614],"force_p95":42.58312,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.82086,"mean_force":20.3884,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50316,0.01529,0.01983]},{"body_a":"attachment","body_b":"push_box","contact_count":130.0,"contact_point_centroid":[0.51587,0.06843,0.03446],"force_p95":8.7613,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.43736,"mean_force":3.88577,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50999,0.08026,0.02166]},{"body_a":"world","body_b":"push_box","contact_count":2463.0,"contact_point_centroid":[0.51509,0.04587,-1e-05],"force_p95":2.29834,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.688,"mean_force":0.45655,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50828,0.10153,0.02666]},{"body_a":"world","body_b":"push_box","contact_count":3987.0,"contact_point_centroid":[0.50048,-0.08549,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84222,"mean_force":0.24606,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.494,0.0228,0.06193]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49657,-0.05988,0.01992],"force_p95":0.3069,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32186,"mean_force":0.1647,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49641,-0.04796,0.01993]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50358,0.07681,0.17794]}],"total_contact_groups":8},"final_pose_error":0.07333,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50045,-0.08548,0.02499],"final_tcp_position":[0.49542,0.09102,0.10668],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":52.15857,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51015,0.12542,0.03668],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":685.0,"n_steps_budget":780.0,"object_pos_end":[0.51729,0.03889,0.02489],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18968,"object_to_goal_dist_start":0.19823,"object_z_max":0.02512,"peak_contact_force":6.83483,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2593.0,"raw_peak_contact_force":10.43736,"tcp_end":[0.51045,0.07562,0.02066],"tcp_start":[0.51015,0.12542,0.03668],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":715.0,"n_steps_budget":840.0,"object_pos_end":[0.50046,-0.08464,0.02509],"object_pos_start":[0.51729,0.03889,0.02489],"object_to_goal_dist_end":0.06536,"object_to_goal_dist_start":0.18968,"object_z_max":0.02828,"peak_contact_force":0.44203,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2220.0,"raw_peak_contact_force":52.15857,"tcp_end":[0.49644,-0.04788,0.01995],"tcp_start":[0.51045,0.07562,0.02066],"tcp_to_object_dist_end":0.03733,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50045,-0.08548,0.02499],"object_pos_start":[0.50046,-0.08464,0.02509],"object_to_goal_dist_end":0.06452,"object_to_goal_dist_start":0.06536,"object_z_max":0.02509,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3990.0,"raw_peak_contact_force":0.84222,"tcp_end":[0.49542,0.09102,0.10668],"tcp_start":[0.49644,-0.04788,0.01995],"tcp_to_object_dist_end":0.19455,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```