## Search State

- **Seed**: 3
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.2962 | 0.06 | ✅ accepted |
| 0 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.2210 | 0.05 | ✅ accepted |

**Proposal policy**: task_score is 0.06 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.296) — your mutation base

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
    - 0.06
    - 0.06
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend
  type: descend
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
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    descend_force:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_max_time:
      type: scalar
      range:
      - 2.0
      - 8.0
      default: 4.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.06, 0.06], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - descend_force: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.296
- **task_score** (E): 0.064
- **fitness_score**: 0.126  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1922 |
| descend | 1.00 | 1.00 | 0.0671 |
| push | 1.00 | 1.00 | 0.0378 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.506, 0.147, 0.118) | (0.509, 0.081, 0.040)→(0.502, 0.081, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.544 | 3.954 |
| descend | descend | 1.00 / force_exceeded | (0.506, 0.147, 0.118)→(0.498, 0.117, 0.060) | (0.502, 0.081, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 58.722 | 58.722 |
| push | push | 1.00 / time_limit | (0.498, 0.117, 0.060)→(0.503, 0.080, 0.057) | (0.502, 0.082, 0.034)→(0.502, 0.059, 0.034) | 0.162→0.139 | 1.00 / 3.333 | 133.569 | 277.362 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.288
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.148
- phase_score: 0.184
- phase_breakdown.approach_score: 0.194
- phase_breakdown.push_score: 0.041
- phase_breakdown.contact_score: 0.606

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.170
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.148
- **Median Q (composite search score)**: 0.288
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.349


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.61972,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.13412,"descend.descend_force":5.21354,"descend.descend_speed":0.01506,"push.push_depth":0.10732,"push.push_max_time":4.80545,"push.push_speed":0.02046},"optimized_scores":{"best_composite_score":0.26049,"best_fitness_score":0.09049,"best_task_score":0.00058},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":359.0,"contact_point_centroid":[0.4555,0.11995,0.06],"force_p95":217.46508,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":276.95428,"mean_force":170.46125,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48587,0.08028,0.06589]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":974.0,"contact_point_centroid":[0.47498,0.12,0.05997],"force_p95":119.20093,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":156.5455,"mean_force":99.4637,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48351,0.08763,0.06805]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.12,0.05996],"force_p95":49.71564,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.71564,"mean_force":49.71564,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47832,0.10135,0.07154]},{"body_a":"peg","body_b":"channel_base_body","contact_count":353.0,"contact_point_centroid":[0.49442,0.05902,0.00933],"force_p95":0.60895,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58765,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47816,0.1714,0.19728]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50231,0.22062,0.28697]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49401,0.05895,0.0094],"force_p95":0.55051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.54551,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48348,0.08773,0.06809]},{"body_a":"peg","body_b":"channel_base_body","contact_count":396.0,"contact_point_centroid":[0.49433,0.05896,0.00939],"force_p95":0.55041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54615,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.4724,0.11349,0.09307]}],"total_contact_groups":7},"final_pose_error":0.13274,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49406,0.05866,0.03403],"final_tcp_position":[0.48654,0.08054,0.06519],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":276.95428,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05886,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5463,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":388.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach","tcp_end":[0.4686,0.12689,0.11813],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11127,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.49404,0.05908,0.03389],"object_pos_start":[0.49409,0.05886,0.03385],"object_to_goal_dist_end":0.13934,"object_to_goal_dist_start":0.13912,"object_z_max":0.03389,"peak_contact_force":49.71564,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":397.0,"raw_peak_contact_force":49.71564,"subtask_id":"contact","tcp_end":[0.47835,0.1013,0.07145],"tcp_start":[0.4686,0.12689,0.11813],"tcp_to_object_dist_end":0.05864,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49406,0.05866,0.03403],"object_pos_start":[0.49404,0.05908,0.03389],"object_to_goal_dist_end":0.13892,"object_to_goal_dist_start":0.13934,"object_z_max":0.03403,"peak_contact_force":225.87199,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2333.0,"raw_peak_contact_force":276.95428,"tcp_end":[0.48654,0.08054,0.06519],"tcp_start":[0.47835,0.1013,0.07145],"tcp_to_object_dist_end":0.0388,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.65896,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.11678,"descend.descend_force":6.27593,"descend.descend_speed":0.01065,"push.push_depth":0.15166,"push.push_max_time":4.09383,"push.push_speed":0.03226},"optimized_scores":{"best_composite_score":0.28842,"best_fitness_score":0.11842,"best_task_score":0.04225},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":74.0,"contact_point_centroid":[0.525,0.11993,0.06],"force_p95":203.24927,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":207.19436,"mean_force":180.87706,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51147,0.07945,0.05238]},{"body_a":"world","body_b":"link7","contact_count":966.0,"contact_point_centroid":[0.51065,0.16011,-4e-05],"force_p95":187.80026,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":201.76662,"mean_force":135.89187,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5103,0.09693,0.05289]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51092,0.17522,-0.0],"force_p95":64.80225,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.80225,"mean_force":64.80225,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50979,0.11313,0.05423]},{"body_a":"attachment","body_b":"peg","contact_count":237.0,"contact_point_centroid":[0.50604,0.08933,0.05302],"force_p95":3.05051,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.47124,"mean_force":1.95397,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51067,0.0893,0.05264]},{"body_a":"peg","body_b":"channel_base_body","contact_count":946.0,"contact_point_centroid":[0.50467,0.06998,0.00956],"force_p95":2.47891,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.18948,"mean_force":0.93733,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51028,0.09747,0.05291]},{"body_a":"peg","body_b":"channel_base_body","contact_count":365.0,"contact_point_centroid":[0.50553,0.08086,0.00935],"force_p95":0.5656,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58857,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50688,0.18056,0.19854]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50333,0.22161,0.28663]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":165.0,"contact_point_centroid":[0.52512,0.06987,0.02574],"force_p95":2.38012,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.05693,"mean_force":0.64415,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51072,0.08851,0.05261]},{"body_a":"peg","body_b":"channel_base_body","contact_count":352.0,"contact_point_centroid":[0.50607,0.08088,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55014,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.51868,0.1298,0.08501]}],"total_contact_groups":9},"final_pose_error":0.15149,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50672,0.05877,0.03403],"final_tcp_position":[0.51165,0.07944,0.05238],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":207.19436,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54534,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":401.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52897,0.14639,0.1176],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10884,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":352.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":64.80225,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":353.0,"raw_peak_contact_force":64.80225,"subtask_id":"contact","tcp_end":[0.50975,0.11305,0.05408],"tcp_start":[0.52897,0.14639,0.1176],"tcp_to_object_dist_end":0.03824,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50672,0.05877,0.03403],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.13906,"object_to_goal_dist_start":0.1611,"object_z_max":0.0363,"peak_contact_force":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2388.0,"raw_peak_contact_force":207.19436,"tcp_end":[0.51165,0.07944,0.05238],"tcp_start":[0.50975,0.11305,0.05408],"tcp_to_object_dist_end":0.02807,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.60606,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.14047,"descend.descend_force":4.32699,"descend.descend_speed":0.01502,"push.push_depth":0.19916,"push.push_max_time":6.59293,"push.push_speed":0.04967},"optimized_scores":{"best_composite_score":0.33966,"best_fitness_score":0.16966,"best_task_score":0.14769},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":78.0,"contact_point_centroid":[0.525,0.11988,0.06],"force_p95":331.16925,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":347.93703,"mean_force":233.99256,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51015,0.07925,0.05219]},{"body_a":"world","body_b":"link7","contact_count":943.0,"contact_point_centroid":[0.50824,0.17072,-4e-05],"force_p95":213.66304,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.52562,"mean_force":149.88339,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50796,0.10746,0.0528]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50787,0.1978,-5e-05],"force_p95":61.64707,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":61.64707,"mean_force":61.64707,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50677,0.13573,0.05416]},{"body_a":"peg","body_b":"channel_base_body","contact_count":912.0,"contact_point_centroid":[0.50354,0.08209,0.00957],"force_p95":2.1212,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.04595,"mean_force":0.95232,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50789,0.10862,0.05282]},{"body_a":"attachment","body_b":"peg","contact_count":246.0,"contact_point_centroid":[0.50506,0.10012,0.05017],"force_p95":10.42623,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.22307,"mean_force":2.2444,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50834,0.09998,0.05261]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":222.0,"contact_point_centroid":[0.52517,0.08211,0.02542],"force_p95":5.22963,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.36575,"mean_force":0.91803,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50828,0.10041,0.05261]},{"body_a":"peg","body_b":"channel_base_body","contact_count":337.0,"contact_point_centroid":[0.5055,0.10474,0.00936],"force_p95":0.59969,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57991,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50195,0.19122,0.19825]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50416,0.21886,0.29009]},{"body_a":"peg","body_b":"channel_base_body","contact_count":353.0,"contact_point_centroid":[0.50597,0.10458,0.00939],"force_p95":0.57553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.5463,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.51209,0.15155,0.08543]}],"total_contact_groups":9},"final_pose_error":0.17491,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50607,0.05862,0.034],"final_tcp_position":[0.51043,0.07929,0.05224],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":347.93703,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":364.0,"n_steps_budget":930.0,"object_pos_end":[0.50599,0.1046,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53964,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":369.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach","tcp_end":[0.51913,0.16747,0.11858],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10633,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.50591,0.10456,0.03384],"object_pos_start":[0.50599,0.1046,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.1848,"object_z_max":0.03384,"peak_contact_force":61.64707,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":354.0,"raw_peak_contact_force":61.64707,"subtask_id":"contact","tcp_end":[0.50675,0.13565,0.05401],"tcp_start":[0.51913,0.16747,0.11858],"tcp_to_object_dist_end":0.03707,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50607,0.05862,0.034],"object_pos_start":[0.50591,0.10456,0.03384],"object_to_goal_dist_end":0.13888,"object_to_goal_dist_start":0.18476,"object_z_max":0.03674,"peak_contact_force":174.83544,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2401.0,"raw_peak_contact_force":347.93703,"tcp_end":[0.51043,0.07929,0.05224],"tcp_start":[0.50675,0.13565,0.05401],"tcp_to_object_dist_end":0.02791,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```