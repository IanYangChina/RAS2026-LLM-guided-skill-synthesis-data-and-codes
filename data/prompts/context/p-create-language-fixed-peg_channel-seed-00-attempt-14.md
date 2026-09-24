## Search State

- **Seed**: 0
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.4684 | 0.85 | ❌ rejected |
| 13 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.4842 | 0.85 | ✅ accepted |
| 12 | approach → descend → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | 0.1221 | 0.71 | ❌ rejected |
| 11 | approach → approach → contact → push | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2293 | 0.09 | ❌ rejected |
| 10 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 11 | -0.1634 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.468) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_high
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.08
    orientation:
      mode: none
  parameters:
    clearance_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_final
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.04
    - 0.0
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_peg
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_through
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.18
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.16
      - 0.25
      default: 0.18
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.08]
  - orientation: mode=none
  - parameter_bindings:
    - clearance_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **approach_final** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0]
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_through** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.18, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.468
- **task_score** (E): 0.849
- **fitness_score**: 0.678  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.1737 |
| approach_final | 1.00 | 1.00 | 0.1050 |
| contact_peg | 1.00 | 1.00 | 0.0091 |
| push_through | 0.00 | 1.00 | 0.1425 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.126, 0.147) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.541 | 2.179 |
| approach_final | approach | 1.00 / step_budget | (0.495, 0.126, 0.147)→(0.495, 0.120, 0.043) | (0.500, 0.080, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.581 | 0.614 |
| contact_peg | contact | 1.00 / force_exceeded | (0.495, 0.120, 0.043)→(0.493, 0.114, 0.036) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 18.309 | 18.309 |
| push_through | push | 0.00 / step_budget | (0.493, 0.114, 0.036)→(0.502, -0.028, 0.040) | (0.500, 0.080, 0.034)→(0.500, -0.068, 0.031) | 0.161→0.023 | 1.00 / 4.333 | 316.154 | 388.762 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.963
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.819
- phase_score: 0.754
- phase_breakdown.push_score: 0.743
- phase_breakdown.contact_score: 0.704
- phase_breakdown.approach_score: 0.838

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.780
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.520
- **K-run variance**: 0.0122
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.324


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.94071,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_final.speed":0.0348,"approach_high.clearance_height":0.14222,"approach_high.speed":0.0524,"contact_peg.contact_force":9.20332,"contact_peg.speed":0.0271,"push_through.push_distance":0.17791,"push_through.push_speed":0.03394,"push_through.push_tolerance":0.03888},"optimized_scores":{"best_composite_score":0.31465,"best_fitness_score":0.52465,"best_task_score":0.72803},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":930.0,"contact_point_centroid":[0.54655,0.01909,0.05996],"force_p95":238.7412,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":311.58021,"mean_force":158.52362,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50065,0.01966,0.03659]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":861.0,"contact_point_centroid":[0.52503,0.01533,0.05999],"force_p95":200.92009,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":257.22216,"mean_force":161.3424,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50077,0.01552,0.03661]},{"body_a":"peg","body_b":"channel_base_body","contact_count":938.0,"contact_point_centroid":[0.5047,-0.0438,0.00837],"force_p95":0.89992,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.65074,"mean_force":0.97562,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50062,0.02044,0.03659]},{"body_a":"attachment","body_b":"peg","contact_count":32.0,"contact_point_centroid":[0.50406,0.05845,0.04459],"force_p95":52.24938,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.23409,"mean_force":11.68336,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49933,0.06978,0.03637]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54252,0.09664,0.05998],"force_p95":19.61674,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":19.61674,"mean_force":19.61674,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49776,0.0957,0.03644]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":48.0,"contact_point_centroid":[0.52538,0.00148,0.04606],"force_p95":7.7923,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.41512,"mean_force":1.42683,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50049,0.04606,0.03634]},{"body_a":"peg","body_b":"channel_base_body","contact_count":499.0,"contact_point_centroid":[0.50365,0.06159,0.00934],"force_p95":0.64161,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56269,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50285,0.15323,0.24026]},{"body_a":"peg","body_b":"channel_base_body","contact_count":72.0,"contact_point_centroid":[0.50375,0.0616,0.00936],"force_p95":0.64131,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64347,"mean_force":0.5466,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49848,0.09852,0.03898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":489.0,"contact_point_centroid":[0.50365,0.0616,0.00936],"force_p95":0.64157,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64281,"mean_force":0.54654,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.50269,0.10524,0.11511]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49967,0.19893,0.29886]}],"total_contact_groups":10},"final_pose_error":0.12911,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50649,-0.0549,0.02417],"final_tcp_position":[0.50056,0.01267,0.03739],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":311.58021,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":522.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,0.06159,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.52238,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":518.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.50722,0.1093,0.18706],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.50383,0.06158,0.03376],"object_pos_start":[0.50382,0.06159,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14177,"object_z_max":0.03377,"peak_contact_force":0.63918,"phase_name":"approach_final","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":489.0,"raw_peak_contact_force":0.64281,"subtask_id":"approach","tcp_end":[0.50019,0.10152,0.04287],"tcp_start":[0.50722,0.1093,0.18706],"tcp_to_object_dist_end":0.04113,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":72.0,"n_steps_budget":600.0,"object_pos_end":[0.50383,0.06157,0.03376],"object_pos_start":[0.50383,0.06158,0.03376],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14177,"object_z_max":0.03377,"peak_contact_force":19.61674,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":73.0,"raw_peak_contact_force":19.61674,"subtask_id":"contact","tcp_end":[0.49776,0.09565,0.0364],"tcp_start":[0.50019,0.10152,0.04287],"tcp_to_object_dist_end":0.03473,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50649,-0.0549,0.02417],"object_pos_start":[0.50383,0.06157,0.03376],"object_to_goal_dist_end":0.03038,"object_to_goal_dist_start":0.14176,"object_z_max":0.04358,"peak_contact_force":246.00958,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2809.0,"raw_peak_contact_force":311.58021,"tcp_end":[0.50056,0.01267,0.03739],"tcp_start":[0.49776,0.09565,0.0364],"tcp_to_object_dist_end":0.06911,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26108,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_final.speed":0.06772,"approach_high.clearance_height":0.05507,"approach_high.speed":0.07172,"contact_peg.contact_force":12.13196,"contact_peg.speed":0.04985,"push_through.push_distance":0.22629,"push_through.push_speed":0.04189,"push_through.push_tolerance":0.02842},"optimized_scores":{"best_composite_score":0.52024,"best_fitness_score":0.73024,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":437.0,"contact_point_centroid":[0.56851,-0.10006,0.06494],"force_p95":350.15482,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":374.90114,"mean_force":316.21323,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50135,-0.02854,0.03659]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":406.0,"contact_point_centroid":[0.5434,0.05067,0.05998],"force_p95":206.46863,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":271.63936,"mean_force":146.38155,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49851,0.04921,0.03543]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":419.0,"contact_point_centroid":[0.52502,-0.02657,0.05999],"force_p95":167.03448,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":260.67318,"mean_force":94.19723,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50134,-0.02688,0.03651]},{"body_a":"peg","body_b":"channel_base_body","contact_count":790.0,"contact_point_centroid":[0.50177,-0.03008,0.00944],"force_p95":3.99966,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.29637,"mean_force":1.47821,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50006,0.00688,0.03607]},{"body_a":"attachment","body_b":"peg","contact_count":342.0,"contact_point_centroid":[0.50214,0.0001,0.03968],"force_p95":11.80734,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.17825,"mean_force":2.46281,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49989,0.0118,0.03603]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5472,0.12,0.06],"force_p95":13.97884,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13.97884,"mean_force":13.97884,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49436,0.14688,0.0345]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":130.0,"contact_point_centroid":[0.5252,-0.01022,0.03632],"force_p95":6.29963,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.39369,"mean_force":1.16474,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49992,0.021,0.03551]},{"body_a":"peg","body_b":"channel_base_body","contact_count":608.0,"contact_point_centroid":[0.50093,0.11605,0.00938],"force_p95":0.60701,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55697,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49793,0.1785,0.19979]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":50.0,"contact_point_centroid":[0.47456,0.06623,0.03551],"force_p95":0.99556,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69603,"mean_force":0.42499,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49628,0.10181,0.03553]},{"body_a":"peg","body_b":"channel_base_body","contact_count":202.0,"contact_point_centroid":[0.50106,0.11591,0.00941],"force_p95":0.64043,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64675,"mean_force":0.54346,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.49605,0.15639,0.07335]},{"body_a":"peg","body_b":"channel_base_body","contact_count":116.0,"contact_point_centroid":[0.50063,0.11599,0.00936],"force_p95":0.64139,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64297,"mean_force":0.54598,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49468,0.15058,0.03742]}],"total_contact_groups":11},"final_pose_error":0.08069,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50288,-0.05959,0.03414],"final_tcp_position":[0.50116,-0.02964,0.03706],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":374.90114,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":624.0,"n_steps_budget":1000.0,"object_pos_end":[0.50097,0.11602,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.557,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":608.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49751,0.15801,0.10398],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":202.0,"n_steps_budget":660.0,"object_pos_end":[0.50102,0.11603,0.03376],"object_pos_start":[0.50097,0.11602,0.03386],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19612,"object_z_max":0.03395,"peak_contact_force":0.55386,"phase_name":"approach_final","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":202.0,"raw_peak_contact_force":0.64675,"subtask_id":"approach","tcp_end":[0.49645,0.15529,0.04267],"tcp_start":[0.49751,0.15801,0.10398],"tcp_to_object_dist_end":0.04052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":116.0,"n_steps_budget":600.0,"object_pos_end":[0.50092,0.11603,0.03376],"object_pos_start":[0.50102,0.11603,0.03376],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19613,"object_z_max":0.03377,"peak_contact_force":13.97884,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":117.0,"raw_peak_contact_force":13.97884,"subtask_id":"contact","tcp_end":[0.49437,0.14684,0.03448],"tcp_start":[0.49645,0.15529,0.04267],"tcp_to_object_dist_end":0.03152,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50288,-0.05959,0.03414],"object_pos_start":[0.50092,0.11603,0.03376],"object_to_goal_dist_end":0.02143,"object_to_goal_dist_start":0.19613,"object_z_max":0.04167,"peak_contact_force":326.01561,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2574.0,"raw_peak_contact_force":374.90114,"tcp_end":[0.50116,-0.02964,0.03706],"tcp_start":[0.49437,0.14684,0.03448],"tcp_to_object_dist_end":0.03014,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96897,"average_solve_count":290.0,"average_success_count":290.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_final.speed":0.03543,"approach_high.clearance_height":0.10348,"approach_high.speed":0.03104,"contact_peg.contact_force":10.59514,"contact_peg.speed":0.00555,"push_through.push_distance":0.2207,"push_through.push_speed":0.06791,"push_through.push_tolerance":0.0408},"optimized_scores":{"best_composite_score":0.57025,"best_fitness_score":0.78025,"best_task_score":0.81905},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":568.0,"contact_point_centroid":[0.56063,-0.10556,0.06493],"force_p95":434.20591,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":479.80591,"mean_force":351.9051,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50208,-0.06271,0.04152]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":123.0,"contact_point_centroid":[0.53659,0.03776,0.05998],"force_p95":233.62327,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.13774,"mean_force":185.11031,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49148,0.03584,0.0372]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":441.0,"contact_point_centroid":[0.52503,-0.06502,0.05998],"force_p95":212.95829,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":239.24613,"mean_force":165.83629,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50274,-0.06497,0.04216]},{"body_a":"peg","body_b":"channel_base_body","contact_count":561.0,"contact_point_centroid":[0.49491,-0.10453,0.04481],"force_p95":125.67756,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.1122,"mean_force":74.64138,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50221,-0.06352,0.0416]},{"body_a":"attachment","body_b":"peg","contact_count":602.0,"contact_point_centroid":[0.4993,-0.065,0.0428],"force_p95":109.89503,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":128.77635,"mean_force":68.00327,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50124,-0.0542,0.04124]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":371.0,"contact_point_centroid":[0.47419,-0.0824,0.03976],"force_p95":70.4947,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.17844,"mean_force":32.35675,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50186,-0.05578,0.04244]},{"body_a":"peg","body_b":"channel_base_body","contact_count":412.0,"contact_point_centroid":[0.4932,-0.06353,0.0097],"force_p95":21.15148,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.62555,"mean_force":8.43984,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49863,-0.02893,0.04076]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52538,-0.06319,0.03934],"force_p95":9.9815,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.04638,"mean_force":3.09394,"phase_index":3.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49614,-0.02916,0.03761]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53254,0.10148,0.05999],"force_p95":21.33041,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":21.33041,"mean_force":21.33041,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48731,0.1001,0.03742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":571.0,"contact_point_centroid":[0.4953,0.06387,0.00937],"force_p95":0.57998,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56045,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.48862,0.15384,0.22165]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49926,0.19863,0.2978]},{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.49533,0.06404,0.0094],"force_p95":0.55065,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54539,"phase_index":1.0,"phase_name":"approach_final","phase_type":"approach","tcp_position_centroid":[0.4831,0.10686,0.09626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.49331,0.06252,0.0094],"force_p95":0.55122,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55238,"mean_force":0.54522,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48797,0.10205,0.03943]}],"total_contact_groups":13},"final_pose_error":0.09145,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.48917,-0.09021,0.03499],"final_tcp_position":[0.50357,-0.06678,0.04568],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":479.80591,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":598.0,"n_steps_budget":1000.0,"object_pos_end":[0.49515,0.06367,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14388,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54383,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":599.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.47937,0.11048,0.15065],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12672,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.49483,0.06396,0.03401],"object_pos_start":[0.49515,0.06367,0.03395],"object_to_goal_dist_end":0.14418,"object_to_goal_dist_start":0.14388,"object_z_max":0.03401,"peak_contact_force":0.54864,"phase_name":"approach_final","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":400.0,"raw_peak_contact_force":0.55289,"subtask_id":"approach","tcp_end":[0.48948,0.10364,0.04219],"tcp_start":[0.47937,0.11048,0.15065],"tcp_to_object_dist_end":0.04086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":57.0,"n_steps_budget":1000.0,"object_pos_end":[0.49519,0.0636,0.03402],"object_pos_start":[0.49483,0.06396,0.03401],"object_to_goal_dist_end":0.14381,"object_to_goal_dist_start":0.14418,"object_z_max":0.03402,"peak_contact_force":21.33041,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":58.0,"raw_peak_contact_force":21.33041,"subtask_id":"contact","tcp_end":[0.4873,0.10005,0.03738],"tcp_start":[0.48948,0.10364,0.04219],"tcp_to_object_dist_end":0.03744,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":814.0,"n_steps_budget":1000.0,"object_pos_end":[0.48917,-0.09021,0.03499],"object_pos_start":[0.49519,0.0636,0.03402],"object_to_goal_dist_end":0.0157,"object_to_goal_dist_start":0.14381,"object_z_max":0.04185,"peak_contact_force":376.43658,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3110.0,"raw_peak_contact_force":479.80591,"tcp_end":[0.50357,-0.06678,0.04568],"tcp_start":[0.4873,0.10005,0.03738],"tcp_to_object_dist_end":0.02951,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```