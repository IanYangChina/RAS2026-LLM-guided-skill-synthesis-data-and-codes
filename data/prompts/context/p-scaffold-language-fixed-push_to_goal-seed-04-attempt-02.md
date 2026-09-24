## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3474 | 0.75 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.4720 | 0.58 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3434 | 0.75 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`
- Frozen object start: [0.5531667326686841, 0.0013593063377233885, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5531667326686841, 0.0013593063377233885, 0.025)
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
  frozen_object_start: [0.5532, 0.0014, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5531667326686841, 0.0013593063377233885, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0532, -0.1514, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702

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

## Current Skill (Q=0.347) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
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
  control: impedance_control
  termination: contact_detected
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

- **Composite score**: 0.347
- **task_score** (E): 0.750
- **fitness_score**: 0.707  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2839 |
| contact_1 | 1.00 | 1.00 | 0.0480 |
| push_1 | 1.00 | 1.00 | 0.1262 |
| retract_1 | 0.00 | 1.00 | 0.1331 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.082, 0.032) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.526, 0.082, 0.032)→(0.527, 0.036, 0.020) | (0.531, 0.007, 0.025)→(0.533, -0.001, 0.025) | 0.161→0.153 | 1.00 / 2.000 | 0.604 | 12.276 |
| push_1 | push | 1.00 / step_budget | (0.527, 0.036, 0.020)→(0.504, -0.088, 0.026) | (0.533, -0.001, 0.025)→(0.523, -0.119, 0.029) | 0.153→0.043 | 1.00 / 3.000 | 82.371 | 107.498 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.088, 0.026)→(0.498, 0.032, 0.084) | (0.523, -0.119, 0.029)→(0.519, -0.115, 0.025) | 0.043→0.044 | 1.00 / 4.000 | 0.245 | 62.615 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.481
- goal_progress: 0.966
- terminal_score: 0.966
- phase_score: 0.832
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.819
- phase_breakdown.contact_score: 0.860

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.885
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.966
- **Median Q (composite search score)**: 0.311
- **K-run variance**: 0.0177
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.388


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8d5a7e825d9524a0954b44a69bda19e1d764760f64bb1262d03aec3c389fadbb`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c4094dd933e0897d422d7ea261a82b80810f7dec183b19c1da5b940157e7d0c4`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52551,"average_solve_count":196.0,"average_success_count":196.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07503,"contact_1.contact_force":16.62579,"push_1.push_depth":0.09952,"push_1.push_distance":0.09834,"push_1.push_speed":0.08743,"retract_1.speed":0.03435},"optimized_scores":{"best_composite_score":0.31096,"best_fitness_score":0.67096,"best_task_score":0.68207},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":911.0,"contact_point_centroid":[0.55892,-0.04765,0.05453],"force_p95":114.22211,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.06208,"mean_force":76.74364,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5261,-0.03222,0.0236]},{"body_a":"world","body_b":"push_box","contact_count":1839.0,"contact_point_centroid":[0.55174,-0.08118,-0.00033],"force_p95":80.72999,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.18044,"mean_force":48.37831,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52637,-0.0315,0.02356]},{"body_a":"world","body_b":"push_box","contact_count":3642.0,"contact_point_centroid":[0.53268,-0.11043,-4e-05],"force_p95":0.29785,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.93716,"mean_force":0.59697,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50275,-0.02487,0.05747]},{"body_a":"attachment","body_b":"push_box","contact_count":923.0,"contact_point_centroid":[0.54546,-0.04025,0.05451],"force_p95":81.36594,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.70644,"mean_force":50.23414,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52637,-0.03143,0.02354]},{"body_a":"push_box","body_b":"link7","contact_count":61.0,"contact_point_centroid":[0.54956,-0.09753,0.05661],"force_p95":75.19513,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.84277,"mean_force":30.90229,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50805,-0.08651,0.03038]},{"body_a":"attachment","body_b":"push_box","contact_count":74.0,"contact_point_centroid":[0.53236,-0.08932,0.06124],"force_p95":54.81535,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.96245,"mean_force":19.68858,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50752,-0.08444,0.03082]},{"body_a":"attachment","body_b":"push_box","contact_count":91.0,"contact_point_centroid":[0.55354,0.02251,0.03706],"force_p95":9.41036,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.12796,"mean_force":3.16502,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5476,0.03447,0.02024]},{"body_a":"world","body_b":"push_box","contact_count":1878.0,"contact_point_centroid":[0.55317,-0.00049,-1e-05],"force_p95":0.92821,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.54208,"mean_force":0.40531,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5452,0.05605,0.02331]},{"body_a":"world","body_b":"push_box","contact_count":3916.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5223,0.03844,0.16445]}],"total_contact_groups":9},"final_pose_error":0.14094,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53202,-0.1103,0.02499],"final_tcp_position":[0.50091,0.02599,0.08303],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":136.06208,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":979.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3916.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54661,0.07725,0.03101],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07641,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55365,-0.00643,0.02512],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15327,"object_to_goal_dist_start":0.16043,"object_z_max":0.02513,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1969.0,"raw_peak_contact_force":12.12796,"tcp_end":[0.54817,0.03041,0.01978],"tcp_start":[0.54661,0.07725,0.03101],"tcp_to_object_dist_end":0.03762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.53741,-0.11807,0.0311],"object_pos_start":[0.55365,-0.00643,0.02512],"object_to_goal_dist_end":0.04956,"object_to_goal_dist_start":0.15327,"object_z_max":0.0311,"peak_contact_force":132.77738,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3673.0,"raw_peak_contact_force":136.06208,"tcp_end":[0.50917,-0.0908,0.02935],"tcp_start":[0.54817,0.03041,0.01978],"tcp_to_object_dist_end":0.0393,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53202,-0.1103,0.02499],"object_pos_start":[0.53741,-0.11807,0.0311],"object_to_goal_dist_end":0.051,"object_to_goal_dist_start":0.04956,"object_z_max":0.03492,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3777.0,"raw_peak_contact_force":83.93716,"tcp_end":[0.50091,0.02599,0.08303],"tcp_start":[0.50917,-0.0908,0.02935],"tcp_to_object_dist_end":0.15137,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67081,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09579,"contact_1.contact_force":2.83142,"push_1.push_depth":0.0988,"push_1.push_distance":0.19802,"push_1.push_speed":0.08943,"retract_1.speed":0.06627},"optimized_scores":{"best_composite_score":0.20565,"best_fitness_score":0.56565,"best_task_score":0.60276},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":881.0,"contact_point_centroid":[0.54975,-0.0108,0.05458],"force_p95":113.76774,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.07327,"mean_force":75.52221,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51789,0.00521,0.02359]},{"body_a":"attachment","body_b":"push_box","contact_count":884.0,"contact_point_centroid":[0.53691,-0.00344,0.05258],"force_p95":98.82841,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.37055,"mean_force":54.22202,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51794,0.00542,0.02358]},{"body_a":"push_box","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.54895,-0.06053,0.05579],"force_p95":84.34505,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.51725,"mean_force":37.8421,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50648,-0.05084,0.0303]},{"body_a":"world","body_b":"push_box","contact_count":1673.0,"contact_point_centroid":[0.54441,-0.04739,-0.00033],"force_p95":74.88372,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":90.25215,"mean_force":51.13751,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51745,0.00267,0.02386]},{"body_a":"world","body_b":"push_box","contact_count":3640.0,"contact_point_centroid":[0.52616,-0.07906,-3e-05],"force_p95":0.32928,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.87389,"mean_force":0.53365,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50117,0.01077,0.06282]},{"body_a":"attachment","body_b":"push_box","contact_count":81.0,"contact_point_centroid":[0.52784,-0.05317,0.05971],"force_p95":63.29106,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.37855,"mean_force":19.37797,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50543,-0.04671,0.03158]},{"body_a":"attachment","body_b":"push_box","contact_count":95.0,"contact_point_centroid":[0.53725,0.058,0.03608],"force_p95":9.36248,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.68006,"mean_force":3.1468,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53121,0.06994,0.02048]},{"body_a":"world","body_b":"push_box","contact_count":1875.0,"contact_point_centroid":[0.5368,0.03546,-1e-05],"force_p95":1.74268,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.04324,"mean_force":0.40967,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52926,0.09002,0.02329]},{"body_a":"world","body_b":"push_box","contact_count":3980.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51452,0.05554,0.16393]}],"total_contact_groups":9},"final_pose_error":0.10598,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52551,-0.07875,0.02499],"final_tcp_position":[0.49951,0.06093,0.09257],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":129.07327,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3980.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53088,0.11128,0.03074],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.53895,0.02869,0.02506],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18289,"object_to_goal_dist_start":0.1905,"object_z_max":0.02513,"peak_contact_force":1.09212,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1970.0,"raw_peak_contact_force":12.68006,"tcp_end":[0.53174,0.06562,0.02],"tcp_start":[0.53088,0.11128,0.03074],"tcp_to_object_dist_end":0.03796,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":888.0,"n_steps_budget":990.0,"object_pos_end":[0.53309,-0.08348,0.03132],"object_pos_start":[0.53895,0.02869,0.02506],"object_to_goal_dist_end":0.07456,"object_to_goal_dist_start":0.18289,"object_z_max":0.03131,"peak_contact_force":113.85711,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3438.0,"raw_peak_contact_force":129.07327,"tcp_end":[0.50739,-0.05437,0.029],"tcp_start":[0.53174,0.06562,0.02],"tcp_to_object_dist_end":0.0389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52551,-0.07875,0.02499],"object_pos_start":[0.53309,-0.08348,0.03132],"object_to_goal_dist_end":0.07568,"object_to_goal_dist_start":0.07456,"object_z_max":0.03494,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3772.0,"raw_peak_contact_force":91.51725,"tcp_end":[0.49951,0.06093,0.09257],"tcp_start":[0.50739,-0.05437,0.029],"tcp_to_object_dist_end":0.15733,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24686,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06274,"contact_1.contact_force":11.33128,"push_1.push_depth":0.09997,"push_1.push_distance":0.14721,"push_1.push_speed":0.03499,"retract_1.speed":0.0642},"optimized_scores":{"best_composite_score":0.52547,"best_fitness_score":0.88547,"best_task_score":0.96605},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1461.0,"contact_point_centroid":[0.509,-0.10607,-0.00013],"force_p95":47.67341,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.35945,"mean_force":20.45401,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49791,-0.05028,0.01986]},{"body_a":"push_box","body_b":"link7","contact_count":662.0,"contact_point_centroid":[0.52512,-0.05128,0.05219],"force_p95":41.16285,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.45894,"mean_force":30.35308,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4986,-0.02979,0.01996]},{"body_a":"attachment","body_b":"push_box","contact_count":958.0,"contact_point_centroid":[0.51208,-0.06081,0.04452],"force_p95":37.88777,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.56887,"mean_force":19.2761,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49783,-0.04942,0.01977]},{"body_a":"world","body_b":"push_box","contact_count":3892.0,"contact_point_centroid":[0.4999,-0.15401,-2e-05],"force_p95":0.25012,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.39156,"mean_force":0.28117,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49301,-0.05064,0.04754]},{"body_a":"push_box","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.52439,-0.13733,0.05018],"force_p95":10.21153,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.29082,"mean_force":3.84006,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4937,-0.11156,0.02018]},{"body_a":"attachment","body_b":"push_box","contact_count":84.0,"contact_point_centroid":[0.50372,0.00247,0.02967],"force_p95":10.0801,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.01895,"mean_force":3.4752,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49961,0.01437,0.0214]},{"body_a":"world","body_b":"push_box","contact_count":1936.0,"contact_point_centroid":[0.50484,-0.0197,-1e-05],"force_p95":1.17475,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.90147,"mean_force":0.39684,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49822,0.03547,0.02516]},{"body_a":"world","body_b":"push_box","contact_count":3700.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49922,0.02864,0.16605]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.50785,-0.1295,0.04529],"force_p95":0.11903,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12106,"mean_force":0.10074,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49586,-0.11757,0.01977]}],"total_contact_groups":9},"final_pose_error":0.15918,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49993,-0.15446,0.02499],"final_tcp_position":[0.49401,0.00891,0.07655],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":57.35945,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3700.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5003,0.0578,0.03312],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":525.0,"n_steps_budget":600.0,"object_pos_end":[0.50621,-0.02635,0.02505],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.1238,"object_to_goal_dist_start":0.13127,"object_z_max":0.02505,"peak_contact_force":0.72008,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2020.0,"raw_peak_contact_force":12.01895,"tcp_end":[0.5,0.01047,0.02082],"tcp_start":[0.5003,0.0578,0.03312],"tcp_to_object_dist_end":0.03759,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49975,-0.15443,0.02512],"object_pos_start":[0.50621,-0.02635,0.02505],"object_to_goal_dist_end":0.00444,"object_to_goal_dist_start":0.1238,"object_z_max":0.02771,"peak_contact_force":0.4774,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3081.0,"raw_peak_contact_force":57.35945,"tcp_end":[0.49587,-0.11752,0.01978],"tcp_start":[0.5,0.01047,0.02082],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49993,-0.15446,0.02499],"object_pos_start":[0.49975,-0.15443,0.02512],"object_to_goal_dist_end":0.00446,"object_to_goal_dist_start":0.00444,"object_z_max":0.02666,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3923.0,"raw_peak_contact_force":12.39156,"tcp_end":[0.49401,0.00891,0.07655],"tcp_start":[0.49587,-0.11752,0.01978],"tcp_to_object_dist_end":0.17141,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```