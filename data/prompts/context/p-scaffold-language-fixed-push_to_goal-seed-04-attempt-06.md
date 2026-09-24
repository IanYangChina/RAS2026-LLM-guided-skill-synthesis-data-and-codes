## Search State

- **Seed**: 4
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3482 | 0.75 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.3477 | 0.00 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3481 | 0.78 | ✅ accepted |
| 3 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.3267 | 0.19 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3474 | 0.75 | ✅ accepted |

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
| approach_1 | 1.00 | 1.00 | 0.2838 |
| contact_1 | 1.00 | 1.00 | 0.0480 |
| push_1 | 1.00 | 1.00 | 0.1267 |
| retract_1 | 0.00 | 1.00 | 0.1381 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.082, 0.032) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.526, 0.082, 0.032)→(0.527, 0.036, 0.020) | (0.531, 0.007, 0.025)→(0.533, -0.001, 0.025) | 0.161→0.154 | 1.00 / 2.667 | 4.794 | 12.904 |
| push_1 | push | 1.00 / step_budget | (0.527, 0.036, 0.020)→(0.504, -0.088, 0.026) | (0.533, -0.001, 0.025)→(0.523, -0.119, 0.029) | 0.154→0.042 | 1.00 / 3.667 | 81.684 | 107.738 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.088, 0.026)→(0.498, 0.036, 0.087) | (0.523, -0.119, 0.029)→(0.519, -0.114, 0.025) | 0.042→0.044 | 1.00 / 4.000 | 0.245 | 62.436 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.500
- goal_progress: 0.967
- terminal_score: 0.967
- phase_score: 0.838
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.832
- phase_breakdown.contact_score: 0.860

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.890
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.967
- **Median Q (composite search score)**: 0.302
- **K-run variance**: 0.0178
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.377


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54839,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07898,"contact_1.contact_force":12.30073,"push_1.push_depth":0.0997,"push_1.push_distance":0.1617,"push_1.push_speed":0.07997,"retract_1.speed":0.05514},"optimized_scores":{"best_composite_score":0.30179,"best_fitness_score":0.66179,"best_task_score":0.66344},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":982.0,"contact_point_centroid":[0.56029,-0.04766,0.05427],"force_p95":115.74388,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.8245,"mean_force":77.32164,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52641,-0.03181,0.02375]},{"body_a":"world","body_b":"push_box","contact_count":1955.0,"contact_point_centroid":[0.55381,-0.08103,-0.00036],"force_p95":79.15709,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.25501,"mean_force":49.23519,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52642,-0.03188,0.02379]},{"body_a":"world","body_b":"push_box","contact_count":3637.0,"contact_point_centroid":[0.53435,-0.10798,-3e-05],"force_p95":0.26899,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.3804,"mean_force":0.59414,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50296,-0.0239,0.05788]},{"body_a":"attachment","body_b":"push_box","contact_count":993.0,"contact_point_centroid":[0.54615,-0.0398,0.05496],"force_p95":78.89848,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.64884,"mean_force":49.75663,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52665,-0.03112,0.0237]},{"body_a":"push_box","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.54968,-0.09678,0.05688],"force_p95":70.49772,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.09074,"mean_force":30.41724,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50837,-0.08614,0.03051]},{"body_a":"attachment","body_b":"push_box","contact_count":74.0,"contact_point_centroid":[0.53254,-0.08858,0.06126],"force_p95":51.8834,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.56063,"mean_force":18.30239,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50776,-0.08374,0.03102]},{"body_a":"attachment","body_b":"push_box","contact_count":92.0,"contact_point_centroid":[0.5539,0.02251,0.038],"force_p95":10.36985,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.87216,"mean_force":3.36576,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5476,0.03445,0.02024]},{"body_a":"world","body_b":"push_box","contact_count":1882.0,"contact_point_centroid":[0.55322,-0.00045,-1e-05],"force_p95":1.04389,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.3661,"mean_force":0.41617,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5452,0.056,0.02332]},{"body_a":"world","body_b":"push_box","contact_count":3900.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52232,0.03848,0.16433]}],"total_contact_groups":9},"final_pose_error":0.13973,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53378,-0.10788,0.02499],"final_tcp_position":[0.50105,0.0271,0.08353],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":135.8245,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":975.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3900.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5466,0.07724,0.03104],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55444,-0.00622,0.02516],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15374,"object_to_goal_dist_start":0.16043,"object_z_max":0.02518,"peak_contact_force":7.37541,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1974.0,"raw_peak_contact_force":11.87216,"tcp_end":[0.54818,0.03046,0.01981],"tcp_start":[0.5466,0.07724,0.03104],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53872,-0.11688,0.03111],"object_pos_start":[0.55444,-0.00622,0.02516],"object_to_goal_dist_end":0.05131,"object_to_goal_dist_start":0.15374,"object_z_max":0.03111,"peak_contact_force":135.00094,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3930.0,"raw_peak_contact_force":135.8245,"tcp_end":[0.50949,-0.09031,0.0295],"tcp_start":[0.54818,0.03046,0.01981],"tcp_to_object_dist_end":0.03953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53378,-0.10788,0.02499],"object_pos_start":[0.53872,-0.11688,0.03111],"object_to_goal_dist_end":0.05399,"object_to_goal_dist_start":0.05131,"object_z_max":0.03479,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3770.0,"raw_peak_contact_force":86.3804,"tcp_end":[0.50105,0.0271,0.08353],"tcp_start":[0.50949,-0.09031,0.0295],"tcp_to_object_dist_end":0.15072,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7987,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09523,"contact_1.contact_force":9.64773,"push_1.push_depth":0.09986,"push_1.push_distance":0.11222,"push_1.push_speed":0.09125,"retract_1.speed":0.09278},"optimized_scores":{"best_composite_score":0.21295,"best_fitness_score":0.57295,"best_task_score":0.61805},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":846.0,"contact_point_centroid":[0.54754,-0.01198,0.05486],"force_p95":107.69654,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":118.65061,"mean_force":70.69602,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51741,0.00412,0.02318]},{"body_a":"attachment","body_b":"push_box","contact_count":849.0,"contact_point_centroid":[0.53613,-0.00481,0.05237],"force_p95":96.44117,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.9941,"mean_force":52.70921,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51746,0.00434,0.02317]},{"body_a":"push_box","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.54648,-0.06452,0.05581],"force_p95":78.35957,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.71056,"mean_force":39.33444,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50579,-0.05178,0.02955]},{"body_a":"world","body_b":"push_box","contact_count":1620.0,"contact_point_centroid":[0.54121,-0.04859,-0.0003],"force_p95":70.44514,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.40445,"mean_force":47.92345,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51715,0.0024,0.0234]},{"body_a":"attachment","body_b":"push_box","contact_count":64.0,"contact_point_centroid":[0.52787,-0.0558,0.05939],"force_p95":59.20243,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.01904,"mean_force":23.08927,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50509,-0.04898,0.03042]},{"body_a":"world","body_b":"push_box","contact_count":3689.0,"contact_point_centroid":[0.52422,-0.08147,-3e-05],"force_p95":0.26144,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.26503,"mean_force":0.49207,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50051,0.01895,0.06756]},{"body_a":"attachment","body_b":"push_box","contact_count":99.0,"contact_point_centroid":[0.53803,0.05797,0.03797],"force_p95":8.17158,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.75895,"mean_force":3.16046,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53121,0.06991,0.0205]},{"body_a":"world","body_b":"push_box","contact_count":1839.0,"contact_point_centroid":[0.5367,0.03491,-1e-05],"force_p95":1.1402,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.08861,"mean_force":0.42407,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52922,0.09041,0.02342]},{"body_a":"world","body_b":"push_box","contact_count":3988.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51452,0.05554,0.16393]}],"total_contact_groups":9},"final_pose_error":0.08424,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52363,-0.08118,0.02499],"final_tcp_position":[0.49873,0.07968,0.10363],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":118.65061,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3988.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53087,0.11123,0.03085],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.53833,0.02883,0.02512],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1829,"object_to_goal_dist_start":0.1905,"object_z_max":0.02518,"peak_contact_force":6.27958,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1938.0,"raw_peak_contact_force":12.75895,"tcp_end":[0.53174,0.06562,0.02002],"tcp_start":[0.53087,0.11123,0.03085],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":858.0,"n_steps_budget":960.0,"object_pos_end":[0.53006,-0.08623,0.03113],"object_pos_start":[0.53833,0.02883,0.02512],"object_to_goal_dist_end":0.07077,"object_to_goal_dist_start":0.1829,"object_z_max":0.03112,"peak_contact_force":110.05148,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3315.0,"raw_peak_contact_force":118.65061,"tcp_end":[0.50674,-0.05519,0.02831],"tcp_start":[0.53174,0.06562,0.02002],"tcp_to_object_dist_end":0.03892,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52363,-0.08118,0.02499],"object_pos_start":[0.53006,-0.08623,0.03113],"object_to_goal_dist_end":0.07276,"object_to_goal_dist_start":0.07077,"object_z_max":0.03384,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3800.0,"raw_peak_contact_force":87.71056,"tcp_end":[0.49873,0.07968,0.10363],"tcp_start":[0.50674,-0.05519,0.02831],"tcp_to_object_dist_end":0.18078,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11207,"average_solve_count":232.0,"average_success_count":232.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04447,"contact_1.contact_force":6.37037,"push_1.push_depth":0.09993,"push_1.push_distance":0.07874,"push_1.push_speed":0.08152,"retract_1.speed":0.02237},"optimized_scores":{"best_composite_score":0.5299,"best_fitness_score":0.8899,"best_task_score":0.96715},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1280.0,"contact_point_centroid":[0.51073,-0.10607,-0.00013],"force_p95":57.11105,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.7377,"mean_force":23.28276,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4981,-0.05231,0.02009]},{"body_a":"push_box","body_b":"link7","contact_count":618.0,"contact_point_centroid":[0.5253,-0.05326,0.05246],"force_p95":44.27935,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.48936,"mean_force":32.4645,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49877,-0.03276,0.02021]},{"body_a":"attachment","body_b":"push_box","contact_count":823.0,"contact_point_centroid":[0.51279,-0.06036,0.04541],"force_p95":43.38835,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.72174,"mean_force":22.74854,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49814,-0.04908,0.02005]},{"body_a":"attachment","body_b":"push_box","contact_count":86.0,"contact_point_centroid":[0.5063,0.00252,0.03492],"force_p95":11.17609,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.08006,"mean_force":3.90307,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49963,0.01438,0.02142]},{"body_a":"push_box","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.52429,-0.14035,0.05008],"force_p95":9.46523,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.21598,"mean_force":4.64197,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49406,-0.11445,0.01983]},{"body_a":"world","body_b":"push_box","contact_count":3922.0,"contact_point_centroid":[0.49964,-0.15413,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.11457,"mean_force":0.27128,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49295,-0.05601,0.04535]},{"body_a":"world","body_b":"push_box","contact_count":1919.0,"contact_point_centroid":[0.50471,-0.01997,-1e-05],"force_p95":1.24381,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.39915,"mean_force":0.42366,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4982,0.03568,0.02523]},{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.50646,-0.13039,0.04246],"force_p95":0.75822,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.86109,"mean_force":0.25627,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4957,-0.11863,0.01975]},{"body_a":"world","body_b":"push_box","contact_count":3812.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.02866,0.16595]}],"total_contact_groups":9},"final_pose_error":0.16871,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49968,-0.1543,0.02499],"final_tcp_position":[0.49387,0.00021,0.07261],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":68.7377,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3812.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.05779,0.03318],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":525.0,"n_steps_budget":600.0,"object_pos_end":[0.50662,-0.02614,0.02515],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12403,"object_to_goal_dist_start":0.13127,"object_z_max":0.02515,"peak_contact_force":0.72772,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2005.0,"raw_peak_contact_force":14.08006,"tcp_end":[0.50002,0.0105,0.02085],"tcp_start":[0.50029,0.05779,0.03318],"tcp_to_object_dist_end":0.03749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":877.0,"n_steps_budget":1000.0,"object_pos_end":[0.49993,-0.15506,0.02492],"object_pos_start":[0.50662,-0.02614,0.02515],"object_to_goal_dist_end":0.00506,"object_to_goal_dist_start":0.12403,"object_z_max":0.02786,"peak_contact_force":0.00104,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2721.0,"raw_peak_contact_force":68.7377,"tcp_end":[0.49591,-0.11858,0.01985],"tcp_start":[0.50002,0.0105,0.02085],"tcp_to_object_dist_end":0.03705,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49968,-0.1543,0.02499],"object_pos_start":[0.49993,-0.15506,0.02492],"object_to_goal_dist_end":0.00431,"object_to_goal_dist_start":0.00506,"object_z_max":0.02558,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3948.0,"raw_peak_contact_force":13.21598,"tcp_end":[0.49387,0.00021,0.07261],"tcp_start":[0.49591,-0.11858,0.01985],"tcp_to_object_dist_end":0.16179,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```