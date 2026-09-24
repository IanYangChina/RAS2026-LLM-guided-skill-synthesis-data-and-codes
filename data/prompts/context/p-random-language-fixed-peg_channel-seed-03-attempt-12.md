## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0370 | 0.17 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.4306 | 0.08 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.5014 | 0.04 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | -0.0108 | 0.03 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.2722 | 0.11 | ❌ rejected |

**Proposal policy**: task_score is 0.17 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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

## Current Skill (Q=-0.037) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: approach
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: add
- id: contact
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_guard
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: contact
- id: push
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
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
    push_distance:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.05], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=reduce_speed
- **push** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.037
- **task_score** (E): 0.169
- **fitness_score**: 0.193  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2182 |
| contact | 1.00 | 1.00 | 0.0358 |
| push | 0.00 | 1.00 | 0.0465 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.125, 0.098) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.546 | 3.954 |
| contact | descend | 1.00 / step_budget | (0.500, 0.119, 0.079)→(0.503, 0.107, 0.048) | (0.502, 0.081, 0.034)→(0.502, 0.078, 0.035) | 0.162→0.158 | 1.00 / 1.333 | 119.919 | 243.780 |
| push | push | 0.00 / step_budget | (0.503, 0.107, 0.048)→(0.515, 0.078, 0.069) | (0.502, 0.077, 0.034)→(0.499, -0.005, 0.024) | 0.157→0.077 | 1.00 / 2.333 | 325.442 | 861.194 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.676
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.215
- phase_score: 0.219
- phase_breakdown.push_score: 0.043
- phase_breakdown.approach_score: 0.310
- phase_breakdown.contact_score: 0.656

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.218
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.215
- **Median Q (composite search score)**: -0.026
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.282


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47619,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.12802,"contact.contact_speed":0.06567,"push.push_distance":0.10669,"push.push_speed":0.05154},"optimized_scores":{"best_composite_score":-0.01228,"best_fitness_score":0.21772,"best_task_score":0.21548},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":899.0,"contact_point_centroid":[0.52602,0.11883,0.05993],"force_p95":307.35733,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":773.64474,"mean_force":266.08215,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51803,0.06553,0.09143]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":45.0,"contact_point_centroid":[0.47497,0.09756,0.05995],"force_p95":268.30792,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":340.60325,"mean_force":211.44369,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.48157,0.08898,0.0568]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50025,0.06702,0.05428],"force_p95":128.79167,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":132.88958,"mean_force":23.95609,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49172,0.07707,0.03786]},{"body_a":"peg","body_b":"channel_base_body","contact_count":859.0,"contact_point_centroid":[0.49984,-0.04676,0.00813],"force_p95":0.77224,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.03473,"mean_force":0.95983,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51888,0.06544,0.09335]},{"body_a":"peg","body_b":"channel_base_body","contact_count":276.0,"contact_point_centroid":[0.49388,0.05606,0.00942],"force_p95":0.76411,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.06785,"mean_force":0.89778,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.47547,0.09348,0.06859]},{"body_a":"attachment","body_b":"peg","contact_count":20.0,"contact_point_centroid":[0.49136,0.07325,0.04996],"force_p95":14.62395,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.68232,"mean_force":5.09295,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.48672,0.08474,0.04584]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":51.0,"contact_point_centroid":[0.52594,0.01115,0.03132],"force_p95":8.79939,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.43173,"mean_force":1.39169,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50235,0.06726,0.05735]},{"body_a":"peg","body_b":"channel_base_body","contact_count":640.0,"contact_point_centroid":[0.49432,0.05889,0.00936],"force_p95":0.56138,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56906,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48148,0.15043,0.19437]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4989,0.19807,0.29603]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47493,0.05709,0.05913],"force_p95":0.14435,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16272,"mean_force":0.06722,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.48615,0.08685,0.05165]}],"total_contact_groups":10},"final_pose_error":0.10986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49472,-0.0492,0.02405],"final_tcp_position":[0.52077,0.06562,0.09454],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":773.64474,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.49426,0.05894,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54863,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":675.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.4655,0.10433,0.09828],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08386,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":284.0,"n_steps_budget":720.0,"object_pos_end":[0.49677,0.05338,0.03516],"object_pos_start":[0.49426,0.05894,0.03388],"object_to_goal_dist_end":0.1335,"object_to_goal_dist_start":0.13919,"object_z_max":0.03653,"peak_contact_force":0.69547,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":347.0,"raw_peak_contact_force":340.60325,"subtask_id":"contact","tcp_end":[0.48761,0.0827,0.04033],"tcp_start":[0.4655,0.10433,0.09828],"tcp_to_object_dist_end":0.03116,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":921.0,"n_steps_budget":1000.0,"object_pos_end":[0.49472,-0.0492,0.02405],"object_pos_start":[0.49677,0.05338,0.03516],"object_to_goal_dist_end":0.03508,"object_to_goal_dist_start":0.1335,"object_z_max":0.04357,"peak_contact_force":262.2779,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1820.0,"raw_peak_contact_force":773.64474,"subtask_id":"push","tcp_end":[0.52077,0.06562,0.09454],"tcp_start":[0.48761,0.0827,0.04033],"tcp_to_object_dist_end":0.13724,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73109,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.08842,"contact.contact_speed":0.04732,"push.push_distance":0.12945,"push.push_speed":0.07921},"optimized_scores":{"best_composite_score":-0.07302,"best_fitness_score":0.15698,"best_task_score":0.10179},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":773.0,"contact_point_centroid":[0.52536,0.09501,0.05994],"force_p95":330.9004,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":759.59718,"mean_force":276.25275,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51845,0.09357,0.06777]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":205.0,"contact_point_centroid":[0.4749,0.11983,0.05998],"force_p95":492.24117,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":522.04663,"mean_force":421.61408,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51332,0.07989,0.06159]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":304.0,"contact_point_centroid":[0.52802,0.11232,0.05986],"force_p95":358.03602,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":363.56393,"mean_force":345.1895,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.51658,0.11275,0.06333]},{"body_a":"attachment","body_b":"peg","contact_count":155.0,"contact_point_centroid":[0.51216,0.09194,0.05901],"force_p95":43.2282,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.13855,"mean_force":21.11504,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51755,0.09224,0.06901]},{"body_a":"peg","body_b":"channel_base_body","contact_count":808.0,"contact_point_centroid":[0.50365,0.06792,0.00938],"force_p95":23.85429,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.03047,"mean_force":4.59646,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51862,0.09422,0.06784]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52502,0.00141,0.02479],"force_p95":8.54041,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.81947,"mean_force":2.45288,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51331,0.08008,0.06139]},{"body_a":"peg","body_b":"channel_base_body","contact_count":671.0,"contact_point_centroid":[0.50573,0.08087,0.00936],"force_p95":0.5553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.5695,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51442,0.16094,0.19377]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49996,0.19841,0.29595]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47476,0.04273,0.05933],"force_p95":0.66994,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68073,"mean_force":0.33482,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51334,0.07928,0.06194]},{"body_a":"peg","body_b":"channel_base_body","contact_count":420.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54677,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.51827,0.11457,0.06812]}],"total_contact_groups":10},"final_pose_error":0.09738,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50596,0.02552,0.02409],"final_tcp_position":[0.51325,0.08037,0.06123],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":759.59718,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":700.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":707.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52974,0.12477,0.09696],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":420.0,"n_steps_budget":960.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":358.37339,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":724.0,"raw_peak_contact_force":363.56393,"subtask_id":"contact","tcp_end":[0.51792,0.11257,0.06317],"tcp_start":[0.52974,0.12477,0.09696],"tcp_to_object_dist_end":0.04483,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":822.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.02552,0.02409],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.10688,"object_to_goal_dist_start":0.16113,"object_z_max":0.04073,"peak_contact_force":455.73789,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1961.0,"raw_peak_contact_force":759.59718,"subtask_id":"push","tcp_end":[0.51325,0.08037,0.06123],"tcp_start":[0.51792,0.11257,0.06317],"tcp_to_object_dist_end":0.06664,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18033,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.13869,"contact.contact_speed":0.065,"push.push_distance":0.17485,"push.push_speed":0.05455},"optimized_scores":{"best_composite_score":-0.02574,"best_fitness_score":0.20426,"best_task_score":0.18957},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52617,0.11959,0.05956],"force_p95":993.3716,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1050.34078,"mean_force":456.17734,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50642,0.12113,0.03736]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.54421,0.11983,0.05971],"force_p95":610.67245,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":616.77612,"mean_force":403.06262,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49152,0.12054,0.02924]},{"body_a":"world","body_b":"link7","contact_count":907.0,"contact_point_centroid":[0.49602,0.16395,-7e-05],"force_p95":330.96876,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":507.69175,"mean_force":273.38087,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5084,0.09939,0.04894]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.47495,0.1086,0.0229],"force_p95":134.45423,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.76846,"mean_force":120.72335,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48641,0.10559,0.02136]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50448,0.1128,0.03872],"force_p95":37.29432,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.51262,"mean_force":14.89248,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50527,0.12461,0.03831]},{"body_a":"peg","body_b":"channel_base_body","contact_count":963.0,"contact_point_centroid":[0.49662,0.01277,0.00834],"force_p95":0.71863,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.58675,"mean_force":0.69647,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50745,0.10036,0.04778]},{"body_a":"peg","body_b":"channel_base_body","contact_count":195.0,"contact_point_centroid":[0.5054,0.0989,0.00947],"force_p95":15.19068,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.17245,"mean_force":1.8994,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.51122,0.13755,0.06863]},{"body_a":"attachment","body_b":"peg","contact_count":24.0,"contact_point_centroid":[0.50545,0.11811,0.04666],"force_p95":20.5819,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.85495,"mean_force":11.23388,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50577,0.13003,0.04658]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47497,-0.01552,0.02431],"force_p95":8.20417,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.57649,"mean_force":3.20009,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50878,0.10513,0.05019]},{"body_a":"peg","body_b":"channel_base_body","contact_count":599.0,"contact_point_centroid":[0.50572,0.10466,0.00937],"force_p95":0.57627,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.5652,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50912,0.17252,0.19456]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49985,0.19882,0.29629]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.52518,0.04996,0.04073],"force_p95":1.51928,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01696,"mean_force":0.522,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49712,0.11458,0.03489]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52521,0.10048,0.05999],"force_p95":0.49495,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54601,"mean_force":0.22796,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50694,0.13156,0.05102]}],"total_contact_groups":13},"final_pose_error":0.13638,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49608,0.00729,0.02417],"final_tcp_position":[0.51014,0.08799,0.05044],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1050.34078,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":626.0,"n_steps_budget":990.0,"object_pos_end":[0.50591,0.10456,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54408,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":631.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51935,0.14718,0.09795],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07815,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":204.0,"n_steps_budget":690.0,"object_pos_end":[0.50399,0.09883,0.03625],"object_pos_start":[0.50591,0.10456,0.03384],"object_to_goal_dist_end":0.17891,"object_to_goal_dist_start":0.18476,"object_z_max":0.03684,"peak_contact_force":0.68831,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":228.0,"raw_peak_contact_force":27.17245,"subtask_id":"contact","tcp_end":[0.50341,0.12705,0.0397],"tcp_start":[0.50512,0.12882,0.0426],"tcp_to_object_dist_end":0.02844,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49608,0.00729,0.02417],"object_pos_start":[0.50276,0.09682,0.03411],"object_to_goal_dist_end":0.0888,"object_to_goal_dist_start":0.17694,"object_z_max":0.04085,"peak_contact_force":258.30874,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1966.0,"raw_peak_contact_force":1050.34078,"subtask_id":"push","tcp_end":[0.51014,0.08799,0.05044],"tcp_start":[0.50341,0.12705,0.0397],"tcp_to_object_dist_end":0.08603,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```