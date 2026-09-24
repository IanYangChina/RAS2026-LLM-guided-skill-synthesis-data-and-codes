## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.3406 | 0.14 | ❌ rejected |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.0370 | 0.17 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.4306 | 0.08 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 5 | 0.5014 | 0.04 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | -0.0108 | 0.03 | ❌ rejected |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.341) — your mutation base

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

- **Composite score**: 0.341
- **task_score** (E): 0.136
- **fitness_score**: 0.171  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1907 |
| descend | 1.00 | 1.00 | 0.0724 |
| push | 1.00 | 1.00 | 0.0629 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.126, 0.127) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.541 | 3.954 |
| descend | descend | 1.00 / force_exceeded | (0.505, 0.126, 0.127)→(0.500, 0.109, 0.059) | (0.502, 0.082, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.161 | 1.00 / 2.000 | 31.856 | 31.856 |
| push | push | 1.00 / time_limit | (0.500, 0.109, 0.059)→(0.499, 0.052, 0.034) | (0.502, 0.081, 0.034)→(0.506, 0.018, 0.029) | 0.161→0.099 | 1.00 / 2.667 | 88.712 | 123.181 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.445
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.229
- phase_score: 0.178
- phase_breakdown.push_score: 0.049
- phase_breakdown.approach_score: 0.171
- phase_breakdown.contact_score: 0.570

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.198
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.229
- **Median Q (composite search score)**: 0.327
- **K-run variance**: 0.0004
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.359


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42529,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.14694,"descend.contact_force_threshold":5.13129,"descend.contact_speed":0.05893,"push.push_duration":3.78473,"push.push_offset_distance":0.03997,"push.push_speed":0.05236},"optimized_scores":{"best_composite_score":0.32719,"best_fitness_score":0.15719,"best_task_score":0.06103},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":234.0,"contact_point_centroid":[0.53462,0.04111,0.05998],"force_p95":211.72483,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":224.60817,"mean_force":134.6566,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48931,0.03793,0.03772]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":367.0,"contact_point_centroid":[0.47499,0.07459,0.05534],"force_p95":111.86719,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.17028,"mean_force":64.65008,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48508,0.07213,0.05048]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,0.09547,0.06],"force_p95":52.18765,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":52.18765,"mean_force":52.18765,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48185,0.08611,0.05697]},{"body_a":"attachment","body_b":"peg","contact_count":607.0,"contact_point_centroid":[0.49349,0.04548,0.0444],"force_p95":15.66724,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.3777,"mean_force":6.57331,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48675,0.05568,0.0439]},{"body_a":"peg","body_b":"channel_base_body","contact_count":702.0,"contact_point_centroid":[0.50069,0.02304,0.0099],"force_p95":15.47611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.86073,"mean_force":5.4929,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48625,0.05984,0.04566]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":186.0,"contact_point_centroid":[0.5253,0.01188,0.03996],"force_p95":6.72928,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.26785,"mean_force":3.86535,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48972,0.0374,0.03769]},{"body_a":"peg","body_b":"channel_base_body","contact_count":669.0,"contact_point_centroid":[0.49418,0.05867,0.00939],"force_p95":0.55062,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.59863,"mean_force":0.58236,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.47303,0.09468,0.08842]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.48732,0.07558,0.0589],"force_p95":10.5069,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.31876,"mean_force":2.54471,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.4815,0.08638,0.05807]},{"body_a":"peg","body_b":"channel_base_body","contact_count":546.0,"contact_point_centroid":[0.49446,0.05897,0.00935],"force_p95":0.56873,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57301,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48166,0.15057,0.20902]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49879,0.19776,0.2959]}],"total_contact_groups":10},"final_pose_error":0.01518,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50566,0.006,0.03646],"final_tcp_position":[0.49301,0.03301,0.0374],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":224.60817,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":575.0,"n_steps_budget":900.0,"object_pos_end":[0.4941,0.05908,0.03387],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13934,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54753,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":581.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.46595,0.105,0.12758],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.49417,0.05812,0.03447],"object_pos_start":[0.4941,0.05908,0.03387],"object_to_goal_dist_end":0.13836,"object_to_goal_dist_start":0.13934,"object_z_max":0.03437,"peak_contact_force":52.18765,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":680.0,"raw_peak_contact_force":52.18765,"subtask_id":"contact","tcp_end":[0.4819,0.08609,0.05688],"tcp_start":[0.46595,0.105,0.12758],"tcp_to_object_dist_end":0.03788,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":785.0,"n_steps_budget":870.0,"object_pos_end":[0.50566,0.006,0.03646],"object_pos_start":[0.49417,0.05812,0.03447],"object_to_goal_dist_end":0.08626,"object_to_goal_dist_start":0.13836,"object_z_max":0.03996,"peak_contact_force":196.55633,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2096.0,"raw_peak_contact_force":224.60817,"subtask_id":"push","tcp_end":[0.49301,0.03301,0.0374],"tcp_start":[0.4819,0.08609,0.05688],"tcp_to_object_dist_end":0.02984,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80556,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.1796,"descend.contact_force_threshold":6.73045,"descend.contact_speed":0.05687,"push.push_duration":4.37331,"push.push_offset_distance":0.03459,"push.push_speed":0.099},"optimized_scores":{"best_composite_score":0.32629,"best_fitness_score":0.15629,"best_task_score":0.11859},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.54426,0.05376,0.05994],"force_p95":69.67968,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":69.69157,"mean_force":59.30915,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50242,0.05204,0.03154]},{"body_a":"peg","body_b":"channel_base_body","contact_count":524.0,"contact_point_centroid":[0.50548,0.04249,0.00902],"force_p95":49.87028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.82878,"mean_force":6.46842,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50486,0.07934,0.04357]},{"body_a":"attachment","body_b":"peg","contact_count":156.0,"contact_point_centroid":[0.50877,0.06787,0.04941],"force_p95":60.2259,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.42137,"mean_force":20.09223,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50556,0.07951,0.04443]},{"body_a":"peg","body_b":"channel_base_body","contact_count":322.0,"contact_point_centroid":[0.50593,0.08079,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.89621,"mean_force":0.61307,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.51917,0.11698,0.09284]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51384,0.09703,0.05869],"force_p95":21.47798,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.47798,"mean_force":21.47798,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.51015,0.10835,0.05986]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52501,0.00224,0.02571],"force_p95":5.6897,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.63902,"mean_force":2.2903,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50305,0.06368,0.0363]},{"body_a":"peg","body_b":"channel_base_body","contact_count":517.0,"contact_point_centroid":[0.50569,0.08092,0.00936],"force_p95":0.55885,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57628,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51467,0.16093,0.20812]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50022,0.19794,0.29518]}],"total_contact_groups":8},"final_pose_error":0.00677,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5054,0.01454,0.02581],"final_tcp_position":[0.5026,0.05176,0.03158],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":69.69157,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":546.0,"n_steps_budget":720.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54459,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":553.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.52972,0.12546,0.12667],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10574,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.0809,0.03377],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":21.89621,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":323.0,"raw_peak_contact_force":21.89621,"subtask_id":"contact","tcp_end":[0.5101,0.1083,0.05968],"tcp_start":[0.52972,0.12546,0.12667],"tcp_to_object_dist_end":0.03793,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":534.0,"n_steps_budget":600.0,"object_pos_end":[0.5054,0.01454,0.02581],"object_pos_start":[0.50596,0.0809,0.03377],"object_to_goal_dist_end":0.09575,"object_to_goal_dist_start":0.16113,"object_z_max":0.04077,"peak_contact_force":69.58018,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":707.0,"raw_peak_contact_force":69.69157,"subtask_id":"push","tcp_end":[0.5026,0.05176,0.03158],"tcp_start":[0.5101,0.1083,0.05968],"tcp_to_object_dist_end":0.03777,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.74809,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.13735,"descend.contact_force_threshold":8.56466,"descend.contact_speed":0.02104,"push.push_duration":2.31478,"push.push_offset_distance":0.03997,"push.push_speed":0.05211},"optimized_scores":{"best_composite_score":0.36826,"best_fitness_score":0.19826,"best_task_score":0.22911},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":52.0,"contact_point_centroid":[0.5443,0.07448,0.05998],"force_p95":75.04755,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.24369,"mean_force":54.05166,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50225,0.07131,0.03205]},{"body_a":"peg","body_b":"channel_base_body","contact_count":772.0,"contact_point_centroid":[0.5049,0.05841,0.00867],"force_p95":49.81522,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.93042,"mean_force":6.90381,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50288,0.09903,0.04351]},{"body_a":"attachment","body_b":"peg","contact_count":260.0,"contact_point_centroid":[0.50739,0.08724,0.04886],"force_p95":59.742,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.38354,"mean_force":18.84832,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50355,0.09865,0.04408]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.07053,0.06],"force_p95":34.62541,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.30651,"mean_force":26.61204,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50264,0.07057,0.03198]},{"body_a":"peg","body_b":"channel_base_body","contact_count":357.0,"contact_point_centroid":[0.50612,0.10468,0.00939],"force_p95":0.57568,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.48414,"mean_force":0.60501,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.512,0.13973,0.09383]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51241,0.12132,0.05885],"force_p95":21.01935,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.01935,"mean_force":21.01935,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50665,0.13165,0.06079]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52501,0.01979,0.0259],"force_p95":6.58909,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.34296,"mean_force":3.08056,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.502,0.08123,0.03576]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.50553,0.10464,0.00937],"force_p95":0.57737,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56826,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50916,0.17277,0.20964]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.4999,0.1987,0.2963]}],"total_contact_groups":9},"final_pose_error":0.00704,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50613,0.03348,0.02503],"final_tcp_position":[0.50266,0.07054,0.03197],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":75.24369,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":870.0,"object_pos_end":[0.50593,0.10472,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.53011,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":547.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51936,0.14784,0.12798],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10441,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.10455,0.03384],"object_pos_start":[0.50593,0.10472,0.03383],"object_to_goal_dist_end":0.18475,"object_to_goal_dist_start":0.18492,"object_z_max":0.03384,"peak_contact_force":21.48414,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":358.0,"raw_peak_contact_force":21.48414,"subtask_id":"contact","tcp_end":[0.50662,0.13162,0.06062],"tcp_start":[0.51936,0.14784,0.12798],"tcp_to_object_dist_end":0.03809,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50613,0.03348,0.02503],"object_pos_start":[0.50593,0.10455,0.03384],"object_to_goal_dist_end":0.11462,"object_to_goal_dist_start":0.18475,"object_z_max":0.04076,"peak_contact_force":0.0,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1107.0,"raw_peak_contact_force":75.24369,"subtask_id":"push","tcp_end":[0.50266,0.07054,0.03197],"tcp_start":[0.50662,0.13162,0.06062],"tcp_to_object_dist_end":0.03787,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```