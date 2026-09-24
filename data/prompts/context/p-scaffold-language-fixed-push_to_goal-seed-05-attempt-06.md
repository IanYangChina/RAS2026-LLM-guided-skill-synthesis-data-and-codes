## Search State

- **Seed**: 5
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4737 | 0.75 | ❌ rejected |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | -0.2041 | 0.00 | ❌ rejected |
| 4 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4746 | 0.75 | ❌ rejected |
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.76 | ✅ accepted |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4735 | 0.75 | ✅ accepted |

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

## Current Skill (Q=0.474) — your mutation base

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

- **Composite score**: 0.474
- **task_score** (E): 0.751
- **fitness_score**: 0.684  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2855 |
| contact_1 | 1.00 | 1.00 | 0.0533 |
| push_1 | 1.00 | 1.00 | 0.1271 |
| retract_1 | 0.00 | 1.00 | 0.1654 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.101, 0.036) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.514, 0.101, 0.036)→(0.514, 0.050, 0.021) | (0.519, 0.022, 0.025)→(0.521, 0.013, 0.025) | 0.173→0.165 | 1.00 / 3.333 | 4.454 | 10.404 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.050, 0.021)→(0.500, -0.076, 0.023) | (0.521, 0.013, 0.025)→(0.509, -0.111, 0.027) | 0.165→0.047 | 1.00 / 3.000 | 40.367 | 83.494 |
| retract_1 | retract | 0.00 / step_budget | (0.500, -0.076, 0.023)→(0.496, 0.070, 0.101) | (0.509, -0.111, 0.027)→(0.507, -0.110, 0.025) | 0.047→0.047 | 1.00 / 4.000 | 0.245 | 32.688 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.426
- goal_progress: 0.935
- terminal_score: 0.935
- phase_score: 0.849
- phase_breakdown.contact_score: 0.870
- phase_breakdown.push_score: 0.847
- phase_breakdown.approach_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.883
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.935
- **Median Q (composite search score)**: 0.389
- **K-run variance**: 0.0201
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.315


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76623,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.04704,"push_1.push_depth":0.09973,"retract_1.retract_height":0.13626},"optimized_scores":{"best_composite_score":0.35849,"best_fitness_score":0.56849,"best_task_score":0.62014},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":792.0,"contact_point_centroid":[0.54832,-0.01179,0.05476],"force_p95":110.09103,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.43068,"mean_force":70.80104,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51758,0.00424,0.02333]},{"body_a":"attachment","body_b":"push_box","contact_count":801.0,"contact_point_centroid":[0.53608,-0.00413,0.05178],"force_p95":98.36114,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.75263,"mean_force":52.36029,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51774,0.00493,0.02329]},{"body_a":"world","body_b":"push_box","contact_count":1495.0,"contact_point_centroid":[0.54274,-0.04817,-0.0003],"force_p95":73.74175,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.1388,"mean_force":48.82969,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51722,0.00197,0.0236]},{"body_a":"push_box","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.54722,-0.06314,0.0558],"force_p95":81.95398,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":88.49499,"mean_force":40.55037,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50608,-0.05128,0.02969]},{"body_a":"attachment","body_b":"push_box","contact_count":60.0,"contact_point_centroid":[0.52896,-0.05524,0.05996],"force_p95":63.0189,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.54639,"mean_force":24.25994,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50552,-0.049,0.03038]},{"body_a":"world","body_b":"push_box","contact_count":3697.0,"contact_point_centroid":[0.52472,-0.08192,-3e-05],"force_p95":0.25758,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.42672,"mean_force":0.48515,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50055,0.02425,0.07058]},{"body_a":"attachment","body_b":"push_box","contact_count":120.0,"contact_point_centroid":[0.53837,0.05775,0.03942],"force_p95":9.89501,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.34177,"mean_force":4.0991,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53126,0.06967,0.02125]},{"body_a":"world","body_b":"push_box","contact_count":2393.0,"contact_point_centroid":[0.53666,0.0353,-1e-05],"force_p95":2.17298,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.67628,"mean_force":0.45667,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52895,0.09145,0.02622]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51292,0.07216,0.17685]}],"total_contact_groups":9},"final_pose_error":0.07244,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52407,-0.08176,0.02499],"final_tcp_position":[0.49853,0.08987,0.10963],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":126.43068,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53035,0.11538,0.03637],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.53851,0.02854,0.02505],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18265,"object_to_goal_dist_start":0.1905,"object_z_max":0.02516,"peak_contact_force":1.70506,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2513.0,"raw_peak_contact_force":11.34177,"tcp_end":[0.53189,0.06526,0.02038],"tcp_start":[0.53035,0.11538,0.03637],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":804.0,"n_steps_budget":900.0,"object_pos_end":[0.53096,-0.08501,0.03114],"object_pos_start":[0.53851,0.02854,0.02505],"object_to_goal_dist_end":0.07225,"object_to_goal_dist_start":0.18265,"object_z_max":0.03114,"peak_contact_force":110.2934,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3088.0,"raw_peak_contact_force":126.43068,"tcp_end":[0.50702,-0.05459,0.02845],"tcp_start":[0.53189,0.06526,0.02038],"tcp_to_object_dist_end":0.03881,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52407,-0.08176,0.02499],"object_pos_start":[0.53096,-0.08501,0.03114],"object_to_goal_dist_end":0.07236,"object_to_goal_dist_start":0.07225,"object_z_max":0.03415,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3802.0,"raw_peak_contact_force":88.49499,"tcp_end":[0.49853,0.08987,0.10963],"tcp_start":[0.50702,-0.05459,0.02845],"tcp_to_object_dist_end":0.19306,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72258,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.03813,"push_1.push_depth":0.09998,"retract_1.retract_height":0.16985},"optimized_scores":{"best_composite_score":0.67324,"best_fitness_score":0.88324,"best_task_score":0.93506},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1119.0,"contact_point_centroid":[0.50872,-0.10954,-0.00013],"force_p95":60.46284,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.38344,"mean_force":22.38783,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49807,-0.05572,0.01996]},{"body_a":"push_box","body_b":"link7","contact_count":468.0,"contact_point_centroid":[0.52569,-0.05024,0.05258],"force_p95":48.88038,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.9938,"mean_force":33.45337,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49923,-0.02826,0.02025]},{"body_a":"attachment","body_b":"push_box","contact_count":728.0,"contact_point_centroid":[0.51095,-0.06274,0.04181],"force_p95":50.8203,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.53492,"mean_force":23.3343,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49817,-0.05149,0.01993]},{"body_a":"attachment","body_b":"push_box","contact_count":147.0,"contact_point_centroid":[0.5067,0.00186,0.03528],"force_p95":7.44943,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.43239,"mean_force":3.28261,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49974,0.01373,0.02131]},{"body_a":"world","body_b":"push_box","contact_count":2965.0,"contact_point_centroid":[0.50465,-0.02057,-1e-05],"force_p95":1.67818,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.1286,"mean_force":0.41279,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49816,0.03696,0.02523]},{"body_a":"world","body_b":"push_box","contact_count":3992.0,"contact_point_centroid":[0.49622,-0.15762,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74068,"mean_force":0.24596,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49327,-0.04248,0.05246]},{"body_a":"world","body_b":"push_box","contact_count":3580.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.04658,0.17199]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49593,-0.132,0.0198],"force_p95":0.20128,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21018,"mean_force":0.11045,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49586,-0.12005,0.01979]}],"total_contact_groups":8},"final_pose_error":0.13318,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49619,-0.15763,0.02499],"final_tcp_position":[0.49451,0.03205,0.0884],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":76.38344,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3580.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.06252,0.03384],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08192,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":823.0,"n_steps_budget":930.0,"object_pos_end":[0.50643,-0.0276,0.02507],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12257,"object_to_goal_dist_start":0.13127,"object_z_max":0.02514,"peak_contact_force":4.82094,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3112.0,"raw_peak_contact_force":9.43239,"tcp_end":[0.50013,0.00923,0.02063],"tcp_start":[0.50029,0.06252,0.03384],"tcp_to_object_dist_end":0.03762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":780.0,"n_steps_budget":870.0,"object_pos_end":[0.49623,-0.1568,0.02509],"object_pos_start":[0.50643,-0.0276,0.02507],"object_to_goal_dist_end":0.00778,"object_to_goal_dist_start":0.12257,"object_z_max":0.0283,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2315.0,"raw_peak_contact_force":76.38344,"tcp_end":[0.4959,-0.11997,0.01982],"tcp_start":[0.50013,0.00923,0.02063],"tcp_to_object_dist_end":0.03721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49619,-0.15763,0.02499],"object_pos_start":[0.49623,-0.1568,0.02509],"object_to_goal_dist_end":0.00852,"object_to_goal_dist_start":0.00778,"object_z_max":0.02509,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3995.0,"raw_peak_contact_force":0.74068,"tcp_end":[0.49451,0.03205,0.0884],"tcp_start":[0.4959,-0.11997,0.01982],"tcp_to_object_dist_end":0.2,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75974,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.speed":0.04486,"push_1.push_depth":0.09967,"retract_1.retract_height":0.16111},"optimized_scores":{"best_composite_score":0.38925,"best_fitness_score":0.59925,"best_task_score":0.69795},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1118.0,"contact_point_centroid":[0.50633,-0.03264,-9e-05],"force_p95":24.16671,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.66875,"mean_force":6.04565,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50219,0.01389,0.01856]},{"body_a":"push_box","body_b":"link7","contact_count":207.0,"contact_point_centroid":[0.53183,0.02126,0.05087],"force_p95":33.8307,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.72183,"mean_force":12.66197,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50516,0.0429,0.01853]},{"body_a":"attachment","body_b":"push_box","contact_count":553.0,"contact_point_centroid":[0.51033,-0.00353,0.03519],"force_p95":26.2138,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.43709,"mean_force":8.26777,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50169,0.00811,0.01869]},{"body_a":"attachment","body_b":"push_box","contact_count":130.0,"contact_point_centroid":[0.51587,0.06843,0.03446],"force_p95":8.7613,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.43736,"mean_force":3.88577,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50999,0.08026,0.02166]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.51135,-0.06481,0.05001],"force_p95":8.04237,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.8271,"mean_force":3.58373,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49639,-0.05303,0.01993]},{"body_a":"world","body_b":"push_box","contact_count":2463.0,"contact_point_centroid":[0.51509,0.04587,-1e-05],"force_p95":2.29834,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.688,"mean_force":0.45655,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50828,0.10153,0.02666]},{"body_a":"world","body_b":"push_box","contact_count":3981.0,"contact_point_centroid":[0.50032,-0.09024,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.31827,"mean_force":0.24897,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49395,0.01834,0.06113]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50358,0.07681,0.17794]}],"total_contact_groups":8},"final_pose_error":0.07778,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50029,-0.09012,0.02499],"final_tcp_position":[0.49535,0.08678,0.10492],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":47.66875,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51015,0.12542,0.03668],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":685.0,"n_steps_budget":780.0,"object_pos_end":[0.51729,0.03889,0.02489],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18968,"object_to_goal_dist_start":0.19823,"object_z_max":0.02512,"peak_contact_force":6.83483,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2593.0,"raw_peak_contact_force":10.43736,"tcp_end":[0.51045,0.07562,0.02066],"tcp_start":[0.51015,0.12542,0.03668],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":699.0,"n_steps_budget":870.0,"object_pos_end":[0.50047,-0.08982,0.02495],"object_pos_start":[0.51729,0.03889,0.02489],"object_to_goal_dist_end":0.06018,"object_to_goal_dist_start":0.18968,"object_z_max":0.0267,"peak_contact_force":10.80675,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1878.0,"raw_peak_contact_force":47.66875,"tcp_end":[0.49642,-0.05294,0.01995],"tcp_start":[0.51045,0.07562,0.02066],"tcp_to_object_dist_end":0.03744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50029,-0.09012,0.02499],"object_pos_start":[0.50047,-0.08982,0.02495],"object_to_goal_dist_end":0.05988,"object_to_goal_dist_start":0.06018,"object_z_max":0.02508,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3984.0,"raw_peak_contact_force":8.8271,"tcp_end":[0.49535,0.08678,0.10492],"tcp_start":[0.49642,-0.05294,0.01995],"tcp_to_object_dist_end":0.19419,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```