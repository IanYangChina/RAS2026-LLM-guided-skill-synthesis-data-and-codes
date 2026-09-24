## Search State

- **Seed**: 4
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
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

## Current Skill (Q=0.343) — your mutation base

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

- **Composite score**: 0.343
- **task_score** (E): 0.746
- **fitness_score**: 0.703  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2832 |
| contact_1 | 1.00 | 1.00 | 0.0479 |
| push_1 | 1.00 | 1.00 | 0.1257 |
| retract_1 | 0.00 | 1.00 | 0.1354 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.082, 0.032) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.526, 0.082, 0.032)→(0.527, 0.036, 0.020) | (0.531, 0.007, 0.025)→(0.533, -0.001, 0.025) | 0.161→0.153 | 1.00 / 2.667 | 2.962 | 11.690 |
| push_1 | push | 1.00 / step_budget | (0.527, 0.036, 0.020)→(0.504, -0.087, 0.026) | (0.533, -0.001, 0.025)→(0.523, -0.118, 0.029) | 0.153→0.044 | 1.00 / 3.667 | 82.324 | 110.858 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.087, 0.026)→(0.498, 0.034, 0.085) | (0.523, -0.118, 0.029)→(0.519, -0.115, 0.025) | 0.044→0.044 | 1.00 / 4.000 | 0.245 | 56.434 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.482
- goal_progress: 0.952
- terminal_score: 0.952
- phase_score: 0.838
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.830
- phase_breakdown.contact_score: 0.860

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.883
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.952
- **Median Q (composite search score)**: 0.303
- **K-run variance**: 0.0178
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_1.push_speed
- **Final σ (mean)**: 0.403


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49721,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09549,"contact_1.contact_force":9.4896,"push_1.push_depth":0.09643,"push_1.push_distance":0.06789,"push_1.push_speed":0.08024,"retract_1.speed":0.04756},"optimized_scores":{"best_composite_score":0.30267,"best_fitness_score":0.66267,"best_task_score":0.67771},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":968.0,"contact_point_centroid":[0.5593,-0.04661,0.05445],"force_p95":113.36492,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":133.14659,"mean_force":76.0939,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52616,-0.03068,0.02367]},{"body_a":"world","body_b":"push_box","contact_count":1908.0,"contact_point_centroid":[0.5527,-0.08096,-0.00035],"force_p95":77.95088,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.73211,"mean_force":48.9205,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52598,-0.03132,0.02375]},{"body_a":"world","body_b":"push_box","contact_count":3638.0,"contact_point_centroid":[0.53216,-0.10911,-3e-05],"force_p95":0.32213,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.20719,"mean_force":0.58143,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5026,-0.02284,0.05765]},{"body_a":"attachment","body_b":"push_box","contact_count":971.0,"contact_point_centroid":[0.54579,-0.03928,0.05528],"force_p95":78.24587,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.03509,"mean_force":49.67608,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52623,-0.03049,0.02365]},{"body_a":"push_box","body_b":"link7","contact_count":61.0,"contact_point_centroid":[0.54955,-0.09494,0.05652],"force_p95":74.06934,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.78419,"mean_force":29.67008,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50784,-0.08407,0.03043]},{"body_a":"attachment","body_b":"push_box","contact_count":75.0,"contact_point_centroid":[0.53194,-0.08668,0.06094],"force_p95":53.56284,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.74388,"mean_force":18.65426,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50724,-0.08171,0.03096]},{"body_a":"attachment","body_b":"push_box","contact_count":91.0,"contact_point_centroid":[0.55368,0.02254,0.03739],"force_p95":10.35357,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.87646,"mean_force":3.1062,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5476,0.03448,0.02024]},{"body_a":"world","body_b":"push_box","contact_count":1880.0,"contact_point_centroid":[0.55325,-0.00042,-1e-05],"force_p95":1.01861,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.3683,"mean_force":0.40171,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54519,0.05603,0.02333]},{"body_a":"world","body_b":"push_box","contact_count":3828.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52233,0.03847,0.16438]}],"total_contact_groups":9},"final_pose_error":0.13926,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53151,-0.10901,0.02499],"final_tcp_position":[0.5008,0.02775,0.08332],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":133.14659,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":957.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3828.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5466,0.07724,0.03105],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.55446,-0.00635,0.02516],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15363,"object_to_goal_dist_start":0.16043,"object_z_max":0.02518,"peak_contact_force":0.76443,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1971.0,"raw_peak_contact_force":11.87646,"tcp_end":[0.54816,0.03041,0.01978],"tcp_start":[0.5466,0.07724,0.03105],"tcp_to_object_dist_end":0.03767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":981.0,"n_steps_budget":1000.0,"object_pos_end":[0.53721,-0.11588,0.03108],"object_pos_start":[0.55446,-0.00635,0.02516],"object_to_goal_dist_end":0.05085,"object_to_goal_dist_start":0.15363,"object_z_max":0.03109,"peak_contact_force":131.35135,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3847.0,"raw_peak_contact_force":133.14659,"tcp_end":[0.50898,-0.08842,0.02939],"tcp_start":[0.54816,0.03041,0.01978],"tcp_to_object_dist_end":0.03942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53151,-0.10901,0.02499],"object_pos_start":[0.53721,-0.11588,0.03108],"object_to_goal_dist_end":0.0517,"object_to_goal_dist_start":0.05085,"object_z_max":0.03495,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3774.0,"raw_peak_contact_force":84.20719,"tcp_end":[0.5008,0.02775,0.08332],"tcp_start":[0.50898,-0.08842,0.02939],"tcp_to_object_dist_end":0.15181,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80723,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08469,"contact_1.contact_force":10.61035,"push_1.push_depth":0.09958,"push_1.push_distance":0.02337,"push_1.push_speed":0.1,"retract_1.speed":0.07138},"optimized_scores":{"best_composite_score":0.20424,"best_fitness_score":0.56424,"best_task_score":0.60757},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":793.0,"contact_point_centroid":[0.54975,-0.01056,0.05471],"force_p95":114.61836,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.06031,"mean_force":76.03844,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51794,0.00513,0.02369]},{"body_a":"attachment","body_b":"push_box","contact_count":798.0,"contact_point_centroid":[0.53694,-0.00324,0.05248],"force_p95":101.18426,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.46545,"mean_force":56.00985,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51803,0.00552,0.02367]},{"body_a":"world","body_b":"push_box","contact_count":1489.0,"contact_point_centroid":[0.5448,-0.04678,-0.00032],"force_p95":78.74929,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.96686,"mean_force":52.55505,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51751,0.00241,0.02402]},{"body_a":"push_box","body_b":"link7","contact_count":50.0,"contact_point_centroid":[0.54956,-0.06006,0.05588],"force_p95":77.46812,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.11867,"mean_force":35.80632,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50695,-0.0509,0.03045]},{"body_a":"world","body_b":"push_box","contact_count":3655.0,"contact_point_centroid":[0.526,-0.07992,-3e-05],"force_p95":0.31121,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.65105,"mean_force":0.52045,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50143,0.01374,0.0647]},{"body_a":"attachment","body_b":"push_box","contact_count":78.0,"contact_point_centroid":[0.52715,-0.05316,0.05875],"force_p95":57.02355,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.58639,"mean_force":18.47437,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50589,-0.04654,0.03184]},{"body_a":"attachment","body_b":"push_box","contact_count":100.0,"contact_point_centroid":[0.53822,0.05805,0.03899],"force_p95":9.23274,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.18436,"mean_force":3.86163,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53118,0.07,0.02088]},{"body_a":"world","body_b":"push_box","contact_count":1865.0,"contact_point_centroid":[0.53679,0.03521,-1e-05],"force_p95":2.24424,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.83164,"mean_force":0.45842,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52917,0.08954,0.02447]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51439,0.05515,0.16486]}],"total_contact_groups":9},"final_pose_error":0.0989,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52532,-0.07966,0.02499],"final_tcp_position":[0.49953,0.06699,0.09624],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":129.06031,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53071,0.11044,0.03278],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07413,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":522.0,"n_steps_budget":600.0,"object_pos_end":[0.5385,0.02882,0.02501],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18292,"object_to_goal_dist_start":0.1905,"object_z_max":0.02518,"peak_contact_force":1.23918,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1965.0,"raw_peak_contact_force":11.18436,"tcp_end":[0.53176,0.06563,0.02022],"tcp_start":[0.53071,0.11044,0.03278],"tcp_to_object_dist_end":0.03773,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":804.0,"n_steps_budget":900.0,"object_pos_end":[0.53394,-0.08303,0.03143],"object_pos_start":[0.5385,0.02882,0.02501],"object_to_goal_dist_end":0.07535,"object_to_goal_dist_start":0.18292,"object_z_max":0.03143,"peak_contact_force":114.41111,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3080.0,"raw_peak_contact_force":129.06031,"tcp_end":[0.5079,-0.05429,0.02923],"tcp_start":[0.53176,0.06563,0.02022],"tcp_to_object_dist_end":0.03884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52532,-0.07966,0.02499],"object_pos_start":[0.53394,-0.08303,0.03143],"object_to_goal_dist_end":0.07476,"object_to_goal_dist_start":0.07535,"object_z_max":0.03495,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3783.0,"raw_peak_contact_force":84.11867,"tcp_end":[0.49953,0.06699,0.09624],"tcp_start":[0.5079,-0.05429,0.02923],"tcp_to_object_dist_end":0.16507,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22857,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0524,"contact_1.contact_force":1.3352,"push_1.push_depth":0.09959,"push_1.push_distance":0.11059,"push_1.push_speed":0.08115,"retract_1.speed":0.06662},"optimized_scores":{"best_composite_score":0.52336,"best_fitness_score":0.88336,"best_task_score":0.95175},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1245.0,"contact_point_centroid":[0.51044,-0.10654,-0.00013],"force_p95":58.51834,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.36572,"mean_force":24.43457,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49824,-0.05092,0.02017]},{"body_a":"push_box","body_b":"link7","contact_count":643.0,"contact_point_centroid":[0.52472,-0.05533,0.0528],"force_p95":46.51216,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.49736,"mean_force":32.13109,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49878,-0.03492,0.02026]},{"body_a":"attachment","body_b":"push_box","contact_count":838.0,"contact_point_centroid":[0.5132,-0.06092,0.04587],"force_p95":44.93203,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.01106,"mean_force":23.02293,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49819,-0.04966,0.0201]},{"body_a":"attachment","body_b":"push_box","contact_count":87.0,"contact_point_centroid":[0.50624,0.00247,0.03473],"force_p95":10.99966,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.0099,"mean_force":4.2254,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49965,0.01431,0.02141]},{"body_a":"world","body_b":"push_box","contact_count":1917.0,"contact_point_centroid":[0.50486,-0.02,-1e-05],"force_p95":1.50472,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.14458,"mean_force":0.44078,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4982,0.03573,0.02519]},{"body_a":"world","body_b":"push_box","contact_count":3988.0,"contact_point_centroid":[0.49912,-0.15625,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97533,"mean_force":0.24618,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49299,-0.05286,0.04687]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.51,-0.1305,0.05001],"force_p95":0.55945,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.62161,"mean_force":0.2072,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49582,-0.11859,0.01978]},{"body_a":"world","body_b":"push_box","contact_count":3808.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.02862,0.16613]}],"total_contact_groups":8},"final_pose_error":0.15965,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49907,-0.15627,0.02499],"final_tcp_position":[0.49399,0.00837,0.07656],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":70.36572,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":952.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3808.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50028,0.0578,0.03309],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":525.0,"n_steps_budget":600.0,"object_pos_end":[0.50624,-0.0263,0.02503],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12385,"object_to_goal_dist_start":0.13127,"object_z_max":0.02514,"peak_contact_force":6.88382,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2004.0,"raw_peak_contact_force":12.0099,"tcp_end":[0.50003,0.01052,0.02084],"tcp_start":[0.50028,0.0578,0.03309],"tcp_to_object_dist_end":0.03758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.499,-0.15546,0.02507],"object_pos_start":[0.50624,-0.0263,0.02503],"object_to_goal_dist_end":0.00555,"object_to_goal_dist_start":0.12385,"object_z_max":0.02797,"peak_contact_force":1.20884,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2726.0,"raw_peak_contact_force":70.36572,"tcp_end":[0.49585,-0.11851,0.01981],"tcp_start":[0.50003,0.01052,0.02084],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49907,-0.15627,0.02499],"object_pos_start":[0.499,-0.15546,0.02507],"object_to_goal_dist_end":0.00633,"object_to_goal_dist_start":0.00555,"object_z_max":0.02509,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3991.0,"raw_peak_contact_force":0.97533,"tcp_end":[0.49399,0.00837,0.07656],"tcp_start":[0.49585,-0.11851,0.01981],"tcp_to_object_dist_end":0.1726,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```