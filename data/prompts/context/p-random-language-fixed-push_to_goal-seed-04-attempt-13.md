## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.9088 | 0.92 | ❌ rejected |
| 12 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.9092 | 0.92 | ❌ rejected |
| 11 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.9148 | 0.94 | ✅ accepted |
| 10 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4187 | 0.80 | ❌ rejected |
| 9 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4173 | 0.79 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.92). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.909) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
phases:
- id: approach_phase
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.08
    - 0.0
    tolerance: 0.01
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_phase
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.005
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_phase
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.015
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_phase** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.0], tolerance=0.01
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_phase** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.005
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_phase** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.03, 0.0], tolerance=0.015
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.909
- **task_score** (E): 0.921
- **fitness_score**: 0.805  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_phase | 1.00 | 1.00 | 0.2839 |
| contact_phase | 1.00 | 1.00 | 0.0401 |
| push_phase | 1.00 | 1.00 | 0.1526 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_phase | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.526, 0.082, 0.032) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_phase | contact | 1.00 / force_exceeded | (0.526, 0.082, 0.032)→(0.526, 0.044, 0.021) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 5.000 | 25311.325 | 0.245 |
| push_phase | push | 1.00 / step_budget | (0.526, 0.044, 0.021)→(0.500, -0.106, 0.022) | (0.531, 0.007, 0.025)→(0.509, -0.144, 0.028) | 0.161→0.013 | 1.00 / 2.667 | 21.862 | 73.902 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.976
- lateral_force_integral: None
- approach_alignment: 0.677
- goal_progress: 0.972
- terminal_score: 0.972
- phase_score: 0.730
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.674
- phase_breakdown.contact_score: 0.763

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.827
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.972
- **Median Q (composite search score)**: 0.927
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.365


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29231,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_phase.approach_speed":0.13239,"contact_phase.contact_force_threshold":3.3025,"contact_phase.contact_speed":0.03353,"push_phase.push_speed":0.05894},"optimized_scores":{"best_composite_score":0.86929,"best_fitness_score":0.76596,"best_task_score":0.8244},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":587.0,"contact_point_centroid":[0.54775,-0.06665,0.05399],"force_p95":64.23526,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.61456,"mean_force":40.40942,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.51931,-0.04935,0.02094]},{"body_a":"world","body_b":"push_box","contact_count":1211.0,"contact_point_centroid":[0.54039,-0.09517,-0.00016],"force_p95":51.58145,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.48358,"mean_force":27.31926,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.52055,-0.04503,0.02069]},{"body_a":"attachment","body_b":"push_box","contact_count":569.0,"contact_point_centroid":[0.53532,-0.06116,0.05214],"force_p95":53.03747,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.81166,"mean_force":34.06212,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.5188,-0.05128,0.02108]},{"body_a":"world","body_b":"push_box","contact_count":3692.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.52235,0.03847,0.16438]},{"body_a":"world","body_b":"push_box","contact_count":2668.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.54524,0.05672,0.02299]}],"total_contact_groups":5},"final_pose_error":0.01497,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52591,-0.14013,0.02998],"final_tcp_position":[0.50473,-0.1058,0.02495],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":923.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_phase","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3692.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.54659,0.07724,0.03106],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0764,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":667.0,"n_steps_budget":870.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_phase","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2668.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.54753,0.03839,0.02016],"tcp_start":[0.54659,0.07724,0.03106],"tcp_to_object_dist_end":0.03777,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":683.0,"n_steps_budget":1000.0,"object_pos_end":[0.52591,-0.14013,0.02998],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.02817,"object_to_goal_dist_start":0.16043,"object_z_max":0.03002,"peak_contact_force":62.35659,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2367.0,"raw_peak_contact_force":68.61456,"subtask_id":"push","tcp_end":[0.50473,-0.1058,0.02495],"tcp_start":[0.54753,0.03839,0.02016],"tcp_to_object_dist_end":0.04065,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03448,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_phase.approach_speed":0.15694,"contact_phase.contact_force_threshold":3.99097,"contact_phase.contact_speed":0.03628,"push_phase.push_speed":0.07853},"optimized_scores":{"best_composite_score":0.927,"best_fitness_score":0.82366,"best_task_score":0.96549},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":563.0,"contact_point_centroid":[0.52629,-0.03308,0.04477],"force_p95":51.35148,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.21219,"mean_force":20.39025,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.5128,-0.02208,0.01929]},{"body_a":"world","body_b":"push_box","contact_count":839.0,"contact_point_centroid":[0.52525,-0.05901,-0.0001],"force_p95":45.65317,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.88596,"mean_force":17.75487,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.51561,-0.00448,0.01882]},{"body_a":"push_box","body_b":"link7","contact_count":465.0,"contact_point_centroid":[0.53824,-0.03265,0.05324],"force_p95":36.61027,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.64374,"mean_force":14.33344,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.51474,-0.01069,0.01917]},{"body_a":"world","body_b":"push_box","contact_count":3604.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.51459,0.05554,0.16398]},{"body_a":"world","body_b":"push_box","contact_count":2364.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.52923,0.0916,0.02314]}],"total_contact_groups":5},"final_pose_error":0.0148,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50098,-0.1437,0.02661],"final_tcp_position":[0.49817,-0.10625,0.01984],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":56.21219,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":901.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_phase","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3604.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.53088,0.11127,0.03078],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":591.0,"n_steps_budget":780.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":18.83916,"phase_name":"contact_phase","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2364.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.53114,0.07399,0.02041],"tcp_start":[0.53088,0.11127,0.03078],"tcp_to_object_dist_end":0.03771,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":668.0,"n_steps_budget":1000.0,"object_pos_end":[0.50098,-0.1437,0.02661],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.00657,"object_to_goal_dist_start":0.1905,"object_z_max":0.02866,"peak_contact_force":1.17412,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1867.0,"raw_peak_contact_force":56.21219,"subtask_id":"push","tcp_end":[0.49817,-0.10625,0.01984],"tcp_start":[0.53114,0.07399,0.02041],"tcp_to_object_dist_end":0.03816,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73585,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_phase.approach_speed":0.15616,"contact_phase.contact_force_threshold":3.02727,"contact_phase.contact_speed":0.04599,"push_phase.push_speed":0.06081},"optimized_scores":{"best_composite_score":0.93004,"best_fitness_score":0.82671,"best_task_score":0.97168},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":767.0,"contact_point_centroid":[0.51909,-0.09318,-0.00017],"force_p95":83.56649,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.87939,"mean_force":41.46211,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49928,-0.0402,0.02154]},{"body_a":"attachment","body_b":"push_box","contact_count":566.0,"contact_point_centroid":[0.5161,-0.05106,0.0482],"force_p95":72.19275,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.19797,"mean_force":40.24923,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49919,-0.04067,0.02146]},{"body_a":"push_box","body_b":"link7","contact_count":545.0,"contact_point_centroid":[0.52596,-0.0633,0.05368],"force_p95":56.91958,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.15936,"mean_force":36.37666,"phase_index":2.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.49919,-0.04228,0.02149]},{"body_a":"world","body_b":"push_box","contact_count":3200.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.49931,0.02863,0.16614]},{"body_a":"world","body_b":"push_box","contact_count":2080.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_phase","phase_type":"contact","tcp_position_centroid":[0.49818,0.03747,0.02513]}],"total_contact_groups":5},"final_pose_error":0.01497,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49885,-0.14681,0.02653],"final_tcp_position":[0.49725,-0.1059,0.02079],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":96.87939,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":800.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_phase","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3200.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach","tcp_end":[0.50028,0.05779,0.03318],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":520.0,"n_steps_budget":660.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":21.59917,"phase_name":"contact_phase","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2080.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact","tcp_end":[0.49958,0.01819,0.02132],"tcp_start":[0.50028,0.05779,0.03318],"tcp_to_object_dist_end":0.03751,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":580.0,"n_steps_budget":1000.0,"object_pos_end":[0.49885,-0.14681,0.02653],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00372,"object_to_goal_dist_start":0.13127,"object_z_max":0.03118,"peak_contact_force":2.05481,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1878.0,"raw_peak_contact_force":96.87939,"subtask_id":"push","tcp_end":[0.49725,-0.1059,0.02079],"tcp_start":[0.49958,0.01819,0.02132],"tcp_to_object_dist_end":0.04134,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```