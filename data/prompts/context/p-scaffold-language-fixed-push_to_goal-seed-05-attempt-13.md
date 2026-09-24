## Search State

- **Seed**: 5
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4342 | 0.60 | ❌ rejected |
| 12 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.0309 | 0.44 | ❌ rejected |
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | -0.0569 | 0.03 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4729 | 0.75 | ❌ rejected |
| 9 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4690 | 0.74 | ❌ rejected |

**Proposal policy**: task_score is 0.60 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.434) — your mutation base

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

- **Composite score**: 0.434
- **task_score** (E): 0.600
- **fitness_score**: 0.594  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1961 |
| contact_1 | 1.00 | 1.00 | 0.1104 |
| push_1 | 0.00 | 1.00 | 0.1758 |
| retract_1 | 0.33 | 1.00 | 0.2051 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.515, 0.098, 0.134) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.515, 0.098, 0.134)→(0.514, 0.057, 0.032) | (0.519, 0.022, 0.025)→(0.519, 0.020, 0.025) | 0.173→0.171 | 1.00 / 5.000 | 33.499 | 13.836 |
| push_1 | push | 0.00 / step_budget | (0.514, 0.057, 0.032)→(0.494, -0.117, 0.024) | (0.519, 0.020, 0.025)→(0.536, -0.095, 0.025) | 0.171→0.072 | 1.00 / 2.667 | 0.541 | 24.202 |
| retract_1 | retract | 0.33 / step_budget | (0.494, -0.117, 0.024)→(0.492, -0.117, 0.229) | (0.536, -0.095, 0.025)→(0.536, -0.095, 0.025) | 0.072→0.072 | 1.00 / 4.000 | 0.245 | 0.680 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.941
- goal_progress: 0.712
- terminal_score: 0.712
- phase_score: 0.616
- phase_breakdown.contact_score: 0.823
- phase_breakdown.push_score: 0.693
- phase_breakdown.approach_score: 0.112

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.654
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.712
- **Median Q (composite search score)**: 0.415
- **K-run variance**: 0.0019
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.299


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08276,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.14377,"contact_1.speed":0.03901,"contact_1.threshold":13.04785,"push_1.push_depth":0.13369,"push_1.speed":0.02678,"retract_1.retract_height":0.12738,"retract_1.speed":0.07722},"optimized_scores":{"best_composite_score":0.41483,"best_fitness_score":0.57483,"best_task_score":0.51614},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":593.0,"contact_point_centroid":[0.52659,-0.00767,0.04716],"force_p95":17.11543,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.23019,"mean_force":4.59827,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51563,0.00157,0.02375]},{"body_a":"attachment","body_b":"push_box","contact_count":36.0,"contact_point_centroid":[0.53207,0.06073,0.03403],"force_p95":20.57868,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.65301,"mean_force":14.78358,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53201,0.07269,0.034]},{"body_a":"world","body_b":"push_box","contact_count":1940.0,"contact_point_centroid":[0.5504,-0.05484,-3e-05],"force_p95":9.52008,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.08421,"mean_force":1.98426,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50734,-0.04275,0.02325]},{"body_a":"push_box","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.54703,-0.01846,0.05615],"force_p95":12.4553,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.46124,"mean_force":8.49283,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51,-0.02775,0.0233]},{"body_a":"world","body_b":"push_box","contact_count":2414.0,"contact_point_centroid":[0.5364,0.03671,-1e-05],"force_p95":0.41778,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.76757,"mean_force":0.46636,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53068,0.0912,0.07919]},{"body_a":"world","body_b":"push_box","contact_count":2200.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51788,0.06376,0.22426]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5465,-0.07041,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49231,-0.1074,0.14404]}],"total_contact_groups":7},"final_pose_error":0.02797,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5465,-0.07041,0.02499],"final_tcp_position":[0.493,-0.10749,0.27196],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":40.66829,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2200.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53218,0.11237,0.13346],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":618.0,"n_steps_budget":960.0,"object_pos_end":[0.53643,0.03398,0.02482],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18755,"object_to_goal_dist_start":0.1905,"object_z_max":0.02502,"peak_contact_force":40.66829,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2450.0,"raw_peak_contact_force":20.65301,"subtask_id":"contact","tcp_end":[0.53225,0.07089,0.02903],"tcp_start":[0.53218,0.11237,0.13346],"tcp_to_object_dist_end":0.03739,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5465,-0.07041,0.02499],"object_pos_start":[0.53643,0.03398,0.02482],"object_to_goal_dist_end":0.09218,"object_to_goal_dist_start":0.18755,"object_z_max":0.02877,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2578.0,"raw_peak_contact_force":24.23019,"subtask_id":"push","tcp_end":[0.49516,-0.10789,0.02246],"tcp_start":[0.53225,0.07089,0.02903],"tcp_to_object_dist_end":0.06362,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5465,-0.07041,0.02499],"object_pos_start":[0.5465,-0.07041,0.02499],"object_to_goal_dist_end":0.09218,"object_to_goal_dist_start":0.09218,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.493,-0.10749,0.27196],"tcp_start":[0.49516,-0.10789,0.02246],"tcp_to_object_dist_end":0.25541,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36571,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.10551,"contact_1.speed":0.01995,"contact_1.threshold":13.31954,"push_1.push_depth":0.0976,"push_1.speed":0.0297,"retract_1.retract_height":0.12823,"retract_1.speed":0.0638},"optimized_scores":{"best_composite_score":0.49414,"best_fitness_score":0.65414,"best_task_score":0.71195},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":725.0,"contact_point_centroid":[0.5056,-0.06956,0.04662],"force_p95":18.15461,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.07137,"mean_force":5.20452,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49508,-0.05969,0.02252]},{"body_a":"attachment","body_b":"push_box","contact_count":48.0,"contact_point_centroid":[0.50105,0.00475,0.03541],"force_p95":20.08593,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.60941,"mean_force":11.32253,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50035,0.01671,0.03232]},{"body_a":"world","body_b":"push_box","contact_count":1512.0,"contact_point_centroid":[0.52997,-0.11237,-6e-05],"force_p95":10.40564,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.22087,"mean_force":3.21007,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49471,-0.07466,0.02237]},{"body_a":"push_box","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.53222,-0.08538,0.05478],"force_p95":12.75863,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.06708,"mean_force":7.7685,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49421,-0.08966,0.02208]},{"body_a":"world","body_b":"push_box","contact_count":3051.0,"contact_point_centroid":[0.50448,-0.019,-1e-05],"force_p95":0.38198,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.57197,"mean_force":0.42317,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49928,0.03715,0.07857]},{"body_a":"world","body_b":"push_box","contact_count":3993.0,"contact_point_centroid":[0.5377,-0.14711,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5247,"mean_force":0.24573,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48974,-0.14079,0.1202]},{"body_a":"world","body_b":"push_box","contact_count":2028.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49971,0.03887,0.2215]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.51064,-0.14607,0.05005],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49281,-0.14152,0.02138]}],"total_contact_groups":8},"final_pose_error":0.07466,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5377,-0.14712,0.02499],"final_tcp_position":[0.4903,-0.14089,0.225],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":38.70767,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":507.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2028.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5011,0.06059,0.13434],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13518,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.50493,-0.02222,0.02487],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12787,"object_to_goal_dist_start":0.13127,"object_z_max":0.02503,"peak_contact_force":38.70767,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3099.0,"raw_peak_contact_force":20.60941,"subtask_id":"contact","tcp_end":[0.50056,0.01472,0.02743],"tcp_start":[0.5011,0.06059,0.13434],"tcp_to_object_dist_end":0.03729,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53745,-0.14671,0.02506],"object_pos_start":[0.50493,-0.02222,0.02487],"object_to_goal_dist_end":0.03759,"object_to_goal_dist_start":0.12787,"object_z_max":0.02803,"peak_contact_force":0.1134,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2289.0,"raw_peak_contact_force":24.07137,"subtask_id":"push","tcp_end":[0.49281,-0.14152,0.02138],"tcp_start":[0.50056,0.01472,0.02743],"tcp_to_object_dist_end":0.04509,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5377,-0.14712,0.02499],"object_pos_start":[0.53745,-0.14671,0.02506],"object_to_goal_dist_end":0.03781,"object_to_goal_dist_start":0.03759,"object_z_max":0.02506,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3994.0,"raw_peak_contact_force":0.5247,"tcp_end":[0.4903,-0.14089,0.225],"tcp_start":[0.49281,-0.14152,0.02138],"tcp_to_object_dist_end":0.20565,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.04511,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.14665,"contact_1.speed":0.04782,"contact_1.threshold":11.03118,"push_1.push_depth":0.17779,"push_1.speed":0.02316,"retract_1.retract_height":0.06656,"retract_1.speed":0.04984},"optimized_scores":{"best_composite_score":0.39359,"best_fitness_score":0.55359,"best_task_score":0.57129},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":770.0,"contact_point_centroid":[0.512,-0.01811,0.04862],"force_p95":18.27953,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.30376,"mean_force":4.26332,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50043,-0.01137,0.03127]},{"body_a":"world","body_b":"push_box","contact_count":1431.0,"contact_point_centroid":[0.54354,-0.03601,-5e-05],"force_p95":9.72364,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.89227,"mean_force":2.82246,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50016,-0.01592,0.03117]},{"body_a":"world","body_b":"push_box","contact_count":3940.0,"contact_point_centroid":[0.52419,-0.06839,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.27131,"mean_force":0.24945,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49097,-0.10195,0.10963]},{"body_a":"attachment","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.51001,-0.09857,0.05102],"force_p95":1.17189,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.2417,"mean_force":0.73366,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49347,-0.10279,0.02888]},{"body_a":"world","body_b":"push_box","contact_count":2204.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50599,0.06898,0.22489]},{"body_a":"world","body_b":"push_box","contact_count":2136.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50951,0.10332,0.08415]}],"total_contact_groups":6},"final_pose_error":0.05455,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52432,-0.06857,0.02499],"final_tcp_position":[0.49136,-0.10198,0.19032],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":24.30376,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":551.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2204.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51135,0.12249,0.13381],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13211,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":534.0,"n_steps_budget":780.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":21.12047,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2136.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.51044,0.08466,0.03858],"tcp_start":[0.51135,0.12249,0.13381],"tcp_to_object_dist_end":0.03968,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52507,-0.06745,0.02624],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.08629,"object_to_goal_dist_start":0.19823,"object_z_max":0.02985,"peak_contact_force":1.2644,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2201.0,"raw_peak_contact_force":24.30376,"subtask_id":"push","tcp_end":[0.49424,-0.10249,0.02823],"tcp_start":[0.51044,0.08466,0.03858],"tcp_to_object_dist_end":0.04671,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52432,-0.06857,0.02499],"object_pos_start":[0.52507,-0.06745,0.02624],"object_to_goal_dist_end":0.08499,"object_to_goal_dist_start":0.08629,"object_z_max":0.02624,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3950.0,"raw_peak_contact_force":1.27131,"tcp_end":[0.49136,-0.10198,0.19032],"tcp_start":[0.49424,-0.10249,0.02823],"tcp_to_object_dist_end":0.17186,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```