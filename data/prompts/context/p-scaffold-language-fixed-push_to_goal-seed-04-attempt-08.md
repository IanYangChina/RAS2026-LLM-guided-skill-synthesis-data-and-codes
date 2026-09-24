## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3482 | 0.75 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3227 | 0.73 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3482 | 0.75 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.3477 | 0.00 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3481 | 0.78 | ✅ accepted |

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

## Current Skill (Q=0.348) — your mutation base

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

- **Composite score**: 0.348
- **task_score** (E): 0.750
- **fitness_score**: 0.708  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2839 |
| contact_1 | 1.00 | 1.00 | 0.0480 |
| push_1 | 1.00 | 1.00 | 0.1268 |
| retract_1 | 0.00 | 1.00 | 0.1328 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.082, 0.032) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.526, 0.082, 0.032)→(0.527, 0.035, 0.020) | (0.531, 0.007, 0.025)→(0.533, -0.001, 0.025) | 0.161→0.153 | 1.00 / 2.667 | 1.003 | 12.884 |
| push_1 | push | 1.00 / step_budget | (0.527, 0.035, 0.020)→(0.504, -0.088, 0.026) | (0.533, -0.001, 0.025)→(0.523, -0.119, 0.029) | 0.153→0.042 | 1.00 / 4.333 | 84.564 | 106.903 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.088, 0.026)→(0.498, 0.031, 0.084) | (0.523, -0.119, 0.029)→(0.520, -0.115, 0.025) | 0.042→0.044 | 1.00 / 4.000 | 0.245 | 61.731 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.497
- goal_progress: 0.969
- terminal_score: 0.969
- phase_score: 0.834
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.824
- phase_breakdown.contact_score: 0.860

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.888
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.969
- **Median Q (composite search score)**: 0.302
- **K-run variance**: 0.0175
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.351


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48315,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09861,"contact_1.contact_force":4.02035,"push_1.push_depth":0.09887,"push_1.push_distance":0.12912,"push_1.push_speed":0.08546,"retract_1.speed":0.04152},"optimized_scores":{"best_composite_score":0.30203,"best_fitness_score":0.66203,"best_task_score":0.66225},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":924.0,"contact_point_centroid":[0.56073,-0.04735,0.05402],"force_p95":117.32834,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.91365,"mean_force":76.9368,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5265,-0.03129,0.02364]},{"body_a":"world","body_b":"push_box","contact_count":1806.0,"contact_point_centroid":[0.55479,-0.0808,-0.00035],"force_p95":82.18567,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.85488,"mean_force":49.92293,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52627,-0.03223,0.02379]},{"body_a":"attachment","body_b":"push_box","contact_count":922.0,"contact_point_centroid":[0.54589,-0.04001,0.05457],"force_p95":81.88749,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.71701,"mean_force":49.46477,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52649,-0.03137,0.02366]},{"body_a":"world","body_b":"push_box","contact_count":3641.0,"contact_point_centroid":[0.53482,-0.10819,-4e-05],"force_p95":0.3076,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.44796,"mean_force":0.60714,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50292,-0.0247,0.05768]},{"body_a":"push_box","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.54945,-0.09711,0.05704],"force_p95":71.08385,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.24398,"mean_force":30.86843,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50829,-0.08649,0.03059]},{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.53261,-0.08882,0.0614],"force_p95":50.86939,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.63815,"mean_force":17.96759,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50768,-0.08414,0.03108]},{"body_a":"attachment","body_b":"push_box","contact_count":86.0,"contact_point_centroid":[0.55285,0.02248,0.03539],"force_p95":6.30353,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.89837,"mean_force":2.07827,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54756,0.03446,0.02022]},{"body_a":"world","body_b":"push_box","contact_count":1890.0,"contact_point_centroid":[0.55343,-4e-05,-1e-05],"force_p95":0.80984,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.32683,"mean_force":0.34478,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5452,0.05588,0.02334]},{"body_a":"world","body_b":"push_box","contact_count":3812.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52234,0.03848,0.16432]}],"total_contact_groups":9},"final_pose_error":0.14069,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53425,-0.10802,0.02499],"final_tcp_position":[0.50103,0.02618,0.08321],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":135.91365,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3812.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54659,0.07722,0.03111],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55456,-0.00669,0.025],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15334,"object_to_goal_dist_start":0.16043,"object_z_max":0.02514,"peak_contact_force":1.11352,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1976.0,"raw_peak_contact_force":11.89837,"tcp_end":[0.54811,0.03028,0.01972],"tcp_start":[0.54659,0.07722,0.03111],"tcp_to_object_dist_end":0.03789,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":937.0,"n_steps_budget":1000.0,"object_pos_end":[0.53906,-0.11688,0.03112],"object_pos_start":[0.55456,-0.00669,0.025],"object_to_goal_dist_end":0.05157,"object_to_goal_dist_start":0.15334,"object_z_max":0.03113,"peak_contact_force":131.40632,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3652.0,"raw_peak_contact_force":135.91365,"tcp_end":[0.5094,-0.09061,0.02963],"tcp_start":[0.54811,0.03028,0.01972],"tcp_to_object_dist_end":0.03964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53425,-0.10802,0.02499],"object_pos_start":[0.53906,-0.11688,0.03112],"object_to_goal_dist_end":0.05418,"object_to_goal_dist_start":0.05157,"object_z_max":0.03475,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3775.0,"raw_peak_contact_force":84.44796,"tcp_end":[0.50103,0.02618,0.08321],"tcp_start":[0.5094,-0.09061,0.02963],"tcp_to_object_dist_end":0.15001,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80247,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09837,"contact_1.contact_force":6.79626,"push_1.push_depth":0.09961,"push_1.push_distance":0.18143,"push_1.push_speed":0.08126,"retract_1.speed":0.07123},"optimized_scores":{"best_composite_score":0.21445,"best_fitness_score":0.57445,"best_task_score":0.61877},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":951.0,"contact_point_centroid":[0.54872,-0.01305,0.05458],"force_p95":108.68725,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":122.16063,"mean_force":71.90392,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51742,0.00351,0.0234]},{"body_a":"attachment","body_b":"push_box","contact_count":957.0,"contact_point_centroid":[0.53667,-0.00513,0.05299],"force_p95":94.69086,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.79981,"mean_force":52.02091,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51752,0.00391,0.02338]},{"body_a":"push_box","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.54699,-0.06421,0.05579],"force_p95":78.94545,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.74165,"mean_force":38.67005,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50577,-0.05236,0.02976]},{"body_a":"world","body_b":"push_box","contact_count":1817.0,"contact_point_centroid":[0.54283,-0.04914,-0.00033],"force_p95":70.88191,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.45886,"mean_force":48.56428,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5171,0.00149,0.02364]},{"body_a":"attachment","body_b":"push_box","contact_count":68.0,"contact_point_centroid":[0.52846,-0.05624,0.05976],"force_p95":60.3152,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.13769,"mean_force":23.08389,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50513,-0.04979,0.03053]},{"body_a":"world","body_b":"push_box","contact_count":3674.0,"contact_point_centroid":[0.52546,-0.08201,-3e-05],"force_p95":0.28582,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.84355,"mean_force":0.523,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50068,0.01171,0.06367]},{"body_a":"attachment","body_b":"push_box","contact_count":95.0,"contact_point_centroid":[0.53745,0.05801,0.03663],"force_p95":9.36119,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.67262,"mean_force":3.37721,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53121,0.06994,0.02048]},{"body_a":"world","body_b":"push_box","contact_count":1880.0,"contact_point_centroid":[0.53682,0.03543,-1e-05],"force_p95":1.88894,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.03902,"mean_force":0.42047,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52928,0.08996,0.02328]},{"body_a":"world","body_b":"push_box","contact_count":3968.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51454,0.05561,0.16378]}],"total_contact_groups":9},"final_pose_error":0.10096,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52483,-0.08175,0.02499],"final_tcp_position":[0.4991,0.06517,0.09526],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":122.16063,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3968.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53089,0.11128,0.03074],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07477,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.53903,0.02885,0.02504],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18306,"object_to_goal_dist_start":0.1905,"object_z_max":0.02513,"peak_contact_force":1.1691,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1975.0,"raw_peak_contact_force":12.67262,"tcp_end":[0.53176,0.06566,0.02002],"tcp_start":[0.53089,0.11128,0.03074],"tcp_to_object_dist_end":0.03785,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":960.0,"n_steps_budget":1000.0,"object_pos_end":[0.53086,-0.08644,0.03111],"object_pos_start":[0.53903,0.02885,0.02504],"object_to_goal_dist_end":0.07092,"object_to_goal_dist_start":0.18306,"object_z_max":0.03111,"peak_contact_force":110.39426,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3725.0,"raw_peak_contact_force":122.16063,"tcp_end":[0.50673,-0.05589,0.02853],"tcp_start":[0.53176,0.06566,0.02002],"tcp_to_object_dist_end":0.03902,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52483,-0.08175,0.02499],"object_pos_start":[0.53086,-0.08644,0.03111],"object_to_goal_dist_end":0.07262,"object_to_goal_dist_start":0.07092,"object_z_max":0.03415,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3793.0,"raw_peak_contact_force":85.74165,"tcp_end":[0.4991,0.06517,0.09526],"tcp_start":[0.50673,-0.05589,0.02853],"tcp_to_object_dist_end":0.16488,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01277,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02516,"contact_1.contact_force":5.61849,"push_1.push_depth":0.09928,"push_1.push_distance":0.14059,"push_1.push_speed":0.06071,"retract_1.speed":0.05945},"optimized_scores":{"best_composite_score":0.52807,"best_fitness_score":0.88807,"best_task_score":0.96864},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1409.0,"contact_point_centroid":[0.51034,-0.10511,-0.00014],"force_p95":52.64974,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.63395,"mean_force":22.16672,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49806,-0.04981,0.02001]},{"body_a":"push_box","body_b":"link7","contact_count":673.0,"contact_point_centroid":[0.52516,-0.05263,0.05237],"force_p95":43.1764,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.44979,"mean_force":31.25286,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49867,-0.0319,0.02011]},{"body_a":"attachment","body_b":"push_box","contact_count":912.0,"contact_point_centroid":[0.51304,-0.06017,0.04598],"force_p95":39.7926,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.97171,"mean_force":21.34663,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49801,-0.04885,0.01994]},{"body_a":"push_box","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.5242,-0.13863,0.05027],"force_p95":11.11652,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.0035,"mean_force":5.56452,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49389,-0.11297,0.02003]},{"body_a":"attachment","body_b":"push_box","contact_count":86.0,"contact_point_centroid":[0.5063,0.00252,0.03492],"force_p95":11.17609,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.08006,"mean_force":3.90307,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49963,0.01438,0.02142]},{"body_a":"world","body_b":"push_box","contact_count":3866.0,"contact_point_centroid":[0.49966,-0.15365,-2e-05],"force_p95":0.24842,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.47614,"mean_force":0.30455,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49291,-0.05411,0.04602]},{"body_a":"world","body_b":"push_box","contact_count":1919.0,"contact_point_centroid":[0.50471,-0.01997,-1e-05],"force_p95":1.24381,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.39915,"mean_force":0.42366,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4982,0.03568,0.02523]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49587,-0.12999,0.01991],"force_p95":6.17001,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.12606,"mean_force":2.12715,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49577,-0.11807,0.01976]},{"body_a":"world","body_b":"push_box","contact_count":3812.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.02866,0.16595]}],"total_contact_groups":9},"final_pose_error":0.16707,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49961,-0.1541,0.02499],"final_tcp_position":[0.49383,0.00177,0.07319],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":62.63395,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3812.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.05779,0.03318],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":525.0,"n_steps_budget":600.0,"object_pos_end":[0.50662,-0.02614,0.02515],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12403,"object_to_goal_dist_start":0.13127,"object_z_max":0.02515,"peak_contact_force":0.72772,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2005.0,"raw_peak_contact_force":14.08006,"tcp_end":[0.50002,0.0105,0.02085],"tcp_start":[0.50029,0.05779,0.03318],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":965.0,"n_steps_budget":1000.0,"object_pos_end":[0.49991,-0.15478,0.02493],"object_pos_start":[0.50662,-0.02614,0.02515],"object_to_goal_dist_end":0.00478,"object_to_goal_dist_start":0.12403,"object_z_max":0.0278,"peak_contact_force":11.89043,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2994.0,"raw_peak_contact_force":62.63395,"tcp_end":[0.49583,-0.11799,0.01979],"tcp_start":[0.50002,0.0105,0.02085],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49961,-0.1541,0.02499],"object_pos_start":[0.49991,-0.15478,0.02493],"object_to_goal_dist_end":0.00412,"object_to_goal_dist_start":0.00478,"object_z_max":0.02675,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3904.0,"raw_peak_contact_force":15.0035,"tcp_end":[0.49383,0.00177,0.07319],"tcp_start":[0.49583,-0.11799,0.01979],"tcp_to_object_dist_end":0.16325,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```