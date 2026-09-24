## Search State

- **Seed**: 4
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | -0.0424 | 0.33 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.1451 | 0.22 | ❌ rejected |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1114 | 0.22 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.2299 | 0.37 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | -0.0426 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, 0.08090620422514894, 0.04]
- Frozen task target: [0.5354444884457894, -0.07909379577485107, 0.04]
- Goal object position: (0.5354444884457894, -0.07909379577485107, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, 0.08090620422514894, 0.04)
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
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, 0.08090620422514894, 0.04]}
  frozen_targets: {'channel_exit': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

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

## Current Skill (Q=-0.042) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach_peg
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.0
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
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
    offset:
    - 0.0
    - -0.01
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.008
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
- id: retract_lift
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, -0.01, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_lift** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.042
- **task_score** (E): 0.328
- **fitness_score**: 0.231  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1600 |
| descend_to_peg | 1.00 | 1.00 | 0.1044 |
| contact_peg | 0.33 | 1.00 | 0.0336 |
| push_channel | 0.00 | 1.00 | 0.0009 |
| retract_lift | 1.00 | 1.00 | 0.1823 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.134, 0.156) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.544 | 3.242 |
| descend_to_peg | descend | 1.00 / step_budget | (0.516, 0.134, 0.156)→(0.504, 0.125, 0.053) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.545 | 0.562 |
| contact_peg | contact | 0.33 / step_budget | (0.504, 0.125, 0.053)→(0.500, 0.095, 0.039) | (0.505, 0.084, 0.034)→(0.506, 0.066, 0.036) | 0.165→0.146 | 1.00 / 2.000 | 96.575 | 3.510 |
| push_channel | push | 0.00 / guard_failure | (0.501, 0.094, 0.039)→(0.502, 0.094, 0.038) | (0.506, 0.066, 0.036)→(0.507, 0.066, 0.037) | 0.146→0.146 | 1.00 / 2.000 | 207.113 | 243.350 |
| retract_lift | retract | 1.00 / step_budget | (0.502, 0.094, 0.038)→(0.497, -0.066, 0.127) | (0.507, 0.064, 0.037)→(0.504, -0.001, 0.024) | 0.144→0.080 | 1.00 / 1.000 | 0.548 | 88.619 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.568
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.568
- phase_score: 0.204
- phase_breakdown.contact_score: 0.784
- phase_breakdown.push_score: 0.046
- phase_breakdown.approach_score: 0.097

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.349
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.568
- **Median Q (composite search score)**: 0.007
- **K-run variance**: 0.0051
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.235


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26316,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.09591,"contact_peg.contact_force":7.02044,"contact_peg.contact_speed":0.01994,"descend_to_peg.descend_speed":0.03605,"push_channel.push_speed":0.07742},"optimized_scores":{"best_composite_score":0.00692,"best_fitness_score":0.14692,"best_task_score":0.15789},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.5251,0.08999,0.05996],"force_p95":625.01166,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":625.78615,"mean_force":618.04126,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50272,0.08984,0.03832]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50454,0.07815,0.03816],"force_p95":52.73851,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.41686,"mean_force":20.46852,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50261,0.08996,0.03836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50512,0.04466,0.00994],"force_p95":54.00856,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.00856,"mean_force":54.00856,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50239,0.09021,0.03844]},{"body_a":"attachment","body_b":"peg","contact_count":71.0,"contact_point_centroid":[0.50282,0.05139,0.05149],"force_p95":22.9851,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.3872,"mean_force":8.07122,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49893,0.06276,0.05077]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":70.0,"contact_point_centroid":[0.52538,0.04224,0.04551],"force_p95":17.75218,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.15952,"mean_force":4.99265,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49941,0.07023,0.04719]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.50669,0.00785,0.00884],"force_p95":9.32654,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.49554,"mean_force":1.47836,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49812,0.00798,0.08278]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52515,0.08997,0.05993],"force_p95":8.36973,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":8.86654,"mean_force":5.30619,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50268,0.08963,0.03828]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52533,0.0602,0.04376],"force_p95":6.37823,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.90255,"mean_force":3.38561,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50261,0.08996,0.03836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":886.0,"contact_point_centroid":[0.50571,0.06168,0.0098],"force_p95":2.97658,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.49243,"mean_force":1.91414,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50283,0.10456,0.04324]},{"body_a":"peg","body_b":"channel_base_body","contact_count":291.0,"contact_point_centroid":[0.50552,0.08086,0.00934],"force_p95":0.59178,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.5992,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.5143,0.16297,0.22193]},{"body_a":"attachment","body_b":"peg","contact_count":655.0,"contact_point_centroid":[0.50428,0.08867,0.04201],"force_p95":2.69077,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.05188,"mean_force":2.057,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50261,0.10054,0.04178]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50068,0.19722,0.29409]},{"body_a":"peg","body_b":"channel_base_body","contact_count":206.0,"contact_point_centroid":[0.50583,0.08087,0.00938],"force_p95":0.55009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55023,"mean_force":0.54676,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51751,0.12617,0.10605]}],"total_contact_groups":13},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50552,-0.00694,0.02413],"final_tcp_position":[0.49713,-0.06555,0.1265],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":625.78615,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54801,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":327.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52816,0.13052,0.15543],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":206.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54525,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":206.0,"raw_peak_contact_force":0.55023,"tcp_end":[0.50708,0.12202,0.05358],"tcp_start":[0.52816,0.13052,0.15543],"tcp_to_object_dist_end":0.04566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":899.0,"n_steps_budget":1000.0,"object_pos_end":[0.50682,0.06069,0.03613],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.14091,"object_to_goal_dist_start":0.16113,"object_z_max":0.03647,"peak_contact_force":287.6537,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1541.0,"raw_peak_contact_force":4.49243,"subtask_id":"contact","tcp_end":[0.50239,0.09021,0.03844],"tcp_start":[0.50708,0.12202,0.05358],"tcp_to_object_dist_end":0.02994,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50709,0.06046,0.0363],"object_pos_start":[0.50682,0.06069,0.03613],"object_to_goal_dist_end":0.14069,"object_to_goal_dist_start":0.14091,"object_z_max":0.03644,"peak_contact_force":610.29636,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":9.0,"raw_peak_contact_force":625.78615,"subtask_id":"push","tcp_end":[0.50291,0.0895,0.03828],"tcp_start":[0.5028,0.08972,0.03829],"tcp_to_object_dist_end":0.0294,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.50552,-0.00694,0.02413],"object_pos_start":[0.5074,0.05986,0.03656],"object_to_goal_dist_end":0.07496,"object_to_goal_dist_start":0.1401,"object_z_max":0.04081,"peak_contact_force":0.6016,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":594.0,"raw_peak_contact_force":28.3872,"tcp_end":[0.49713,-0.06555,0.1265],"tcp_start":[0.50291,0.0895,0.03828],"tcp_to_object_dist_end":0.11825,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23858,"average_solve_count":197.0,"average_success_count":197.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.14325,"contact_peg.contact_force":10.7904,"contact_peg.contact_speed":0.01385,"descend_to_peg.descend_speed":0.03183,"push_channel.push_speed":0.08392},"optimized_scores":{"best_composite_score":-0.14339,"best_fitness_score":0.19661,"best_task_score":0.2597},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50607,0.07325,0.00993],"force_p95":45.29063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.29063,"mean_force":45.29063,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50131,0.1185,0.03989]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50442,0.10639,0.0413],"force_p95":41.08126,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.69176,"mean_force":20.2664,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50165,0.11819,0.03975]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52519,0.11677,0.05992],"force_p95":25.71416,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":29.50705,"mean_force":7.30709,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.5032,0.11634,0.03851]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.50314,0.07868,0.04764],"force_p95":18.89998,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.42055,"mean_force":7.99364,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49949,0.08968,0.04904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":518.0,"contact_point_centroid":[0.50662,0.03544,0.00858],"force_p95":8.51852,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.29405,"mean_force":1.5034,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49832,0.02293,0.08267]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":64.0,"contact_point_centroid":[0.52535,0.07378,0.0368],"force_p95":8.64964,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.56679,"mean_force":2.40885,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50058,0.10214,0.04352]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52523,0.08997,0.01174],"force_p95":5.64087,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.68757,"mean_force":5.2206,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50182,0.11803,0.03968]},{"body_a":"peg","body_b":"channel_base_body","contact_count":254.0,"contact_point_centroid":[0.50519,0.10457,0.00935],"force_p95":0.62531,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.59084,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50921,0.17422,0.22317]},{"body_a":"peg","body_b":"channel_base_body","contact_count":993.0,"contact_point_centroid":[0.50643,0.08694,0.00981],"force_p95":2.17002,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.08315,"mean_force":1.46233,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50128,0.12967,0.04361]},{"body_a":"attachment","body_b":"peg","contact_count":733.0,"contact_point_centroid":[0.50385,0.11467,0.04423],"force_p95":1.86586,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.69967,"mean_force":1.44126,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5012,0.12649,0.04245]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50041,0.19799,0.2942]},{"body_a":"peg","body_b":"channel_base_body","contact_count":211.0,"contact_point_centroid":[0.50595,0.10486,0.00939],"force_p95":0.57504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57941,"mean_force":0.54643,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5113,0.14831,0.10711]}],"total_contact_groups":12},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50662,0.02592,0.02414],"final_tcp_position":[0.49711,-0.06488,0.12743],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":3901.6815,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":281.0,"n_steps_budget":750.0,"object_pos_end":[0.5059,0.10472,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54277,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":286.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51838,0.15178,0.15762],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.5059,0.10472,0.03384],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18491,"object_z_max":0.03384,"peak_contact_force":0.54648,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":211.0,"raw_peak_contact_force":0.57941,"tcp_end":[0.50498,0.14517,0.05332],"tcp_start":[0.51838,0.15178,0.15762],"tcp_to_object_dist_end":0.04495,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50684,0.08925,0.03617],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.16944,"object_to_goal_dist_start":0.18488,"object_z_max":0.03628,"peak_contact_force":1.87997,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1726.0,"raw_peak_contact_force":3.08315,"subtask_id":"contact","tcp_end":[0.50131,0.1185,0.03989],"tcp_start":[0.50498,0.14517,0.05332],"tcp_to_object_dist_end":0.03,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50716,0.08898,0.03651],"object_pos_start":[0.50684,0.08925,0.03617],"object_to_goal_dist_end":0.16917,"object_to_goal_dist_start":0.16944,"object_z_max":0.03666,"peak_contact_force":1.03026,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":45.29063,"subtask_id":"push","tcp_end":[0.50285,0.11705,0.03927],"tcp_start":[0.50208,0.11779,0.03958],"tcp_to_object_dist_end":0.02853,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.50662,0.02592,0.02414],"object_pos_start":[0.50768,0.08747,0.03666],"object_to_goal_dist_end":0.10731,"object_to_goal_dist_start":0.16768,"object_z_max":0.04077,"peak_contact_force":0.54232,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":648.0,"raw_peak_contact_force":29.50705,"tcp_end":[0.49711,-0.06488,0.12743],"tcp_start":[0.50285,0.11705,0.03927],"tcp_to_object_dist_end":0.13786,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24581,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.10054,"contact_peg.contact_force":7.81987,"contact_peg.contact_speed":0.01806,"descend_to_peg.descend_speed":0.04458,"push_channel.push_speed":0.0383},"optimized_scores":{"best_composite_score":0.00916,"best_fitness_score":0.34916,"best_task_score":0.56757},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.54522,0.0746,0.0599],"force_p95":191.91095,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.96402,"mean_force":95.78067,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.50051,0.07252,0.03624]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50487,0.03274,0.00997],"force_p95":58.97362,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.97362,"mean_force":58.97362,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49723,0.07671,0.03817]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50216,0.06477,0.04151],"force_p95":50.21463,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.30926,"mean_force":18.90638,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49759,0.07632,0.03803]},{"body_a":"attachment","body_b":"peg","contact_count":43.0,"contact_point_centroid":[0.50094,0.02924,0.05404],"force_p95":14.69004,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.44828,"mean_force":4.60971,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49647,0.03995,0.05557]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":105.0,"contact_point_centroid":[0.52555,0.02054,0.03603],"force_p95":12.75182,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.31322,"mean_force":1.84064,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49773,0.05352,0.04735]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52522,0.048,0.01292],"force_p95":7.29313,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.29313,"mean_force":7.29313,"phase_index":3.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49841,0.07538,0.0377]},{"body_a":"peg","body_b":"channel_base_body","contact_count":423.0,"contact_point_centroid":[0.50361,-0.00612,0.00912],"force_p95":2.67414,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.83403,"mean_force":0.77766,"phase_index":4.0,"phase_name":"retract_lift","phase_type":"retract","tcp_position_centroid":[0.49666,0.00057,0.08172]},{"body_a":"peg","body_b":"channel_base_body","contact_count":988.0,"contact_point_centroid":[0.50413,0.04957,0.0098],"force_p95":2.66246,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95386,"mean_force":1.66888,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.4962,0.09138,0.04291]},{"body_a":"attachment","body_b":"peg","contact_count":703.0,"contact_point_centroid":[0.50055,0.0753,0.0445],"force_p95":2.35706,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.57756,"mean_force":1.76996,"phase_index":2.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49637,0.08695,0.04139]},{"body_a":"peg","body_b":"channel_base_body","contact_count":303.0,"contact_point_centroid":[0.50305,0.06737,0.0093],"force_p95":0.68423,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57503,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49946,0.15847,0.22513]},{"body_a":"peg","body_b":"channel_base_body","contact_count":212.0,"contact_point_centroid":[0.50304,0.06771,0.00938],"force_p95":0.5513,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5555,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4988,0.11389,0.10573]}],"total_contact_groups":11},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50007,-0.02335,0.02423],"final_tcp_position":[0.49681,-0.06614,0.12596],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":207.96402,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06747,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14763,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54064,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":303.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.50005,0.11891,0.15597],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50301,0.06747,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14763,"object_z_max":0.0338,"peak_contact_force":0.54359,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":212.0,"raw_peak_contact_force":0.5555,"tcp_end":[0.49904,0.10901,0.05302],"tcp_start":[0.50005,0.11891,0.15597],"tcp_to_object_dist_end":0.04596,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50547,0.0483,0.03679],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.12845,"object_to_goal_dist_start":0.14762,"object_z_max":0.03678,"peak_contact_force":0.1927,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1691.0,"raw_peak_contact_force":2.95386,"subtask_id":"contact","tcp_end":[0.497,0.07702,0.03828],"tcp_start":[0.49904,0.10901,0.05302],"tcp_to_object_dist_end":0.02998,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,0.04739,0.03708],"object_pos_start":[0.50547,0.0483,0.03679],"object_to_goal_dist_end":0.12757,"object_to_goal_dist_start":0.12845,"object_z_max":0.03734,"peak_contact_force":10.01176,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":58.97362,"subtask_id":"push","tcp_end":[0.49935,0.07431,0.03734],"tcp_start":[0.49841,0.07538,0.0377],"tcp_to_object_dist_end":0.02775,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.50007,-0.02335,0.02423],"object_pos_start":[0.50723,0.04526,0.03741],"object_to_goal_dist_end":0.0588,"object_to_goal_dist_start":0.12549,"object_z_max":0.0408,"peak_contact_force":0.50143,"phase_name":"retract_lift","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":577.0,"raw_peak_contact_force":207.96402,"tcp_end":[0.49681,-0.06614,0.12596],"tcp_start":[0.49935,0.07431,0.03734],"tcp_to_object_dist_end":0.11041,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```