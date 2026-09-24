## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.4306 | 0.08 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.5014 | 0.04 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | -0.0108 | 0.03 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.2722 | 0.11 | ❌ rejected |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1376 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.08 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.431) — your mutation base

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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 15.0
      default: 5
      binds_to:
      - path: termination.force_threshold
        mode: add
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
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.02
      axis: channel_axis
      mode: add_to_offset
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
      - 0.0
      - 0.05
      default: 0.02
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
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (add)
  - guards:
    - id=contact_guard, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=reduce_speed
- **push** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.02, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.431
- **task_score** (E): 0.080
- **fitness_score**: 0.327  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1931 |
| contact | 1.00 | 1.00 | 0.0939 |
| push | 1.00 | 1.00 | 0.1452 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.506, 0.076, 0.155) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.542 | 3.954 |
| contact | descend | 1.00 / force_exceeded | (0.506, 0.076, 0.155)→(0.499, 0.065, 0.063) | (0.502, 0.082, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 41.799 | 41.799 |
| push | push | 1.00 / step_budget | (0.499, 0.065, 0.063)→(0.496, -0.080, 0.058) | (0.502, 0.081, 0.034)→(0.497, 0.038, 0.024) | 0.162→0.119 | 1.00 / 1.000 | 0.588 | 41.215 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.272
- alignment_error: None
- force_efficiency: 0.238
- terminal_score: 0.097
- phase_score: 0.517
- phase_breakdown.push_score: 0.706
- phase_breakdown.approach_score: 0.078
- phase_breakdown.contact_score: 0.387

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.349
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.097
- **Median Q (composite search score)**: 0.433
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.318


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.33348,"contact.contact_force_threshold":6.70589,"push.push_distance":0.1449,"push.push_speed":0.04743},"optimized_scores":{"best_composite_score":0.40677,"best_fitness_score":0.30343,"best_task_score":0.08983},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":522.0,"contact_point_centroid":[0.49399,0.05888,0.00939],"force_p95":0.5504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.5831,"mean_force":0.65553,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.47768,0.04894,0.10524]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49507,0.04402,0.0588],"force_p95":57.07953,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.07953,"mean_force":57.07953,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.4842,0.04342,0.06384]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.49379,0.0273,0.00884],"force_p95":39.76308,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.20714,"mean_force":6.44565,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48165,-0.01907,0.06017]},{"body_a":"attachment","body_b":"peg","contact_count":77.0,"contact_point_centroid":[0.49249,0.03653,0.05864],"force_p95":41.53495,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.73408,"mean_force":24.33163,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4835,0.03094,0.06244]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47499,0.03512,0.06],"force_p95":6.19527,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.20723,"mean_force":6.08762,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48288,0.01903,0.06154]},{"body_a":"peg","body_b":"channel_base_body","contact_count":150.0,"contact_point_centroid":[0.49526,0.05907,0.00927],"force_p95":0.92973,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.6435,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48546,0.1185,0.21534]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49799,0.18985,0.28919]}],"total_contact_groups":7},"final_pose_error":0.01984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49407,0.0153,0.02413],"final_tcp_position":[0.48073,-0.08255,0.05901],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":57.5831,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":179.0,"n_steps_budget":600.0,"object_pos_end":[0.49408,0.059,0.03381],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13927,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54633,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":185.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.47369,0.05541,0.15196],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":522.0,"n_steps_budget":780.0,"object_pos_end":[0.49428,0.05884,0.0339],"object_pos_start":[0.49408,0.059,0.03381],"object_to_goal_dist_end":0.13909,"object_to_goal_dist_start":0.13927,"object_z_max":0.03389,"peak_contact_force":57.5831,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":523.0,"raw_peak_contact_force":57.5831,"subtask_id":"contact","tcp_end":[0.4843,0.04341,0.06371],"tcp_start":[0.47369,0.05541,0.15196],"tcp_to_object_dist_end":0.03502,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":329.0,"n_steps_budget":1000.0,"object_pos_end":[0.49407,0.0153,0.02413],"object_pos_start":[0.49428,0.05884,0.0339],"object_to_goal_dist_end":0.09679,"object_to_goal_dist_start":0.13909,"object_z_max":0.04075,"peak_contact_force":0.63433,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":398.0,"raw_peak_contact_force":42.20714,"subtask_id":"push","tcp_end":[0.48073,-0.08255,0.05901],"tcp_start":[0.4843,0.04341,0.06371],"tcp_to_object_dist_end":0.10473,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96933,"average_solve_count":163.0,"average_success_count":163.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.25105,"contact.contact_force_threshold":8.85081,"push.push_distance":0.16285,"push.push_speed":0.02425},"optimized_scores":{"best_composite_score":0.43303,"best_fitness_score":0.3297,"best_task_score":0.05219},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":385.0,"contact_point_centroid":[0.50603,0.08087,0.00938],"force_p95":0.5501,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.18156,"mean_force":0.7045,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.51643,0.06926,0.10535]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.51887,0.06833,0.05866],"force_p95":44.21162,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.73968,"mean_force":30.45907,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50808,0.06435,0.062]},{"body_a":"peg","body_b":"channel_base_body","contact_count":380.0,"contact_point_centroid":[0.50194,0.04722,0.00867],"force_p95":38.61635,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.33759,"mean_force":6.08817,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50531,-0.00723,0.05782]},{"body_a":"attachment","body_b":"peg","contact_count":87.0,"contact_point_centroid":[0.51556,0.05869,0.0583],"force_p95":42.2686,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.77407,"mean_force":24.07555,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50738,0.05129,0.06037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":142.0,"contact_point_centroid":[0.50493,0.08078,0.00929],"force_p95":0.97355,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.65422,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51585,0.12946,0.21628]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5022,0.1906,0.28844]}],"total_contact_groups":6},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49741,0.03734,0.02413],"final_tcp_position":[0.5044,-0.07979,0.05668],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":46.18156,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":171.0,"n_steps_budget":630.0,"object_pos_end":[0.50596,0.08088,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54561,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":178.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52754,0.07527,0.15395],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":385.0,"n_steps_budget":780.0,"object_pos_end":[0.50599,0.08087,0.03372],"object_pos_start":[0.50596,0.08088,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":46.18156,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":387.0,"raw_peak_contact_force":46.18156,"subtask_id":"contact","tcp_end":[0.50807,0.06431,0.0617],"tcp_start":[0.52754,0.07527,0.15395],"tcp_to_object_dist_end":0.03258,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.49741,0.03734,0.02413],"object_pos_start":[0.50599,0.08087,0.03372],"object_to_goal_dist_end":0.11844,"object_to_goal_dist_start":0.1611,"object_z_max":0.04075,"peak_contact_force":0.55832,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":467.0,"raw_peak_contact_force":43.33759,"subtask_id":"push","tcp_end":[0.5044,-0.07979,0.05668],"tcp_start":[0.50807,0.06431,0.0617],"tcp_to_object_dist_end":0.12177,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33333,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.13841,"contact.contact_force_threshold":4.52218,"push.push_distance":0.18395,"push.push_speed":0.04252},"optimized_scores":{"best_composite_score":0.45211,"best_fitness_score":0.34877,"best_task_score":0.09679},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":420.0,"contact_point_centroid":[0.50163,0.06983,0.00865],"force_p95":34.19607,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.1014,"mean_force":4.63554,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50242,0.00421,0.05813]},{"body_a":"attachment","body_b":"peg","contact_count":77.0,"contact_point_centroid":[0.51307,0.0817,0.05851],"force_p95":37.09178,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.49196,"mean_force":22.11694,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5046,0.07475,0.06085]},{"body_a":"peg","body_b":"channel_base_body","contact_count":412.0,"contact_point_centroid":[0.50605,0.10461,0.00939],"force_p95":0.57505,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.63091,"mean_force":0.59751,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.51038,0.09137,0.10721]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51642,0.08996,0.05873],"force_p95":21.07857,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.07857,"mean_force":21.07857,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50533,0.08725,0.06234]},{"body_a":"peg","body_b":"channel_base_body","contact_count":137.0,"contact_point_centroid":[0.50456,0.10457,0.00932],"force_p95":0.93138,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.62888,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51029,0.14243,0.21978]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50102,0.19395,0.29127]}],"total_contact_groups":6},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49875,0.06114,0.02411],"final_tcp_position":[0.50168,-0.07794,0.05719],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":38.1014,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":164.0,"n_steps_budget":1000.0,"object_pos_end":[0.5059,0.10472,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53412,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":169.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51823,0.09659,0.15784],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12489,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":412.0,"n_steps_budget":810.0,"object_pos_end":[0.50585,0.10458,0.03384],"object_pos_start":[0.5059,0.10472,0.03383],"object_to_goal_dist_end":0.18477,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":21.63091,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":413.0,"raw_peak_contact_force":21.63091,"subtask_id":"contact","tcp_end":[0.50532,0.08724,0.06216],"tcp_start":[0.51823,0.09659,0.15784],"tcp_to_object_dist_end":0.03322,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":430.0,"n_steps_budget":1000.0,"object_pos_end":[0.49875,0.06114,0.02411],"object_pos_start":[0.50585,0.10458,0.03384],"object_to_goal_dist_end":0.14204,"object_to_goal_dist_start":0.18477,"object_z_max":0.04078,"peak_contact_force":0.5723,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":497.0,"raw_peak_contact_force":38.1014,"subtask_id":"push","tcp_end":[0.50168,-0.07794,0.05719],"tcp_start":[0.50532,0.08724,0.06216],"tcp_to_object_dist_end":0.14298,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```