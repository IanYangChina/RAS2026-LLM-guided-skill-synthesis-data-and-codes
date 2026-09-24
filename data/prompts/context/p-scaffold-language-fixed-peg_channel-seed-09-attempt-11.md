## Search State

- **Seed**: 9
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.2951 | 0.21 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.1229 | 0.17 | ❌ rejected |
| 9 | approach → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0795 | 0.23 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.1261 | 0.00 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.3181 | 0.26 | ✅ accepted |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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

## Current Skill (Q=0.295) — your mutation base

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
    tolerance: 0.01
  parameters:
    lateral_x:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
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
    offset:
    - 0.0
    - 0.02
    - 0.0
    tolerance: 0.005
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: contact
- id: push_channel
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - -0.08
    - 0.04
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push
- id: retract_up
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.0], tolerance=0.01
  - parameter_bindings:
    - lateral_x: status=consumed; consumers=target.offset.x (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact_peg** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.0], tolerance=0.005
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_channel** (`push`)
  - target: source=yaml, anchor=world, offset=[0.5, -0.08, 0.04], offset_along_axis={axis=channel_axis, distance=0.16, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_up** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.295
- **task_score** (E): 0.213
- **fitness_score**: 0.322  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2645 |
| contact_peg | 1.00 | 1.00 | 0.0090 |
| push_channel | 1.00 | 1.00 | 0.1201 |
| retract_up | 1.00 | 1.00 | 0.1304 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.502, 0.112, 0.051) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.333 | 107.989 | 126.192 |
| contact_peg | contact | 1.00 / force_exceeded | (0.502, 0.112, 0.051)→(0.500, 0.106, 0.045) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 38.557 | 38.557 |
| push_channel | push | 1.00 / time_limit | (0.500, 0.106, 0.045)→(0.498, -0.014, 0.042) | (0.502, 0.067, 0.034)→(0.506, -0.022, 0.032) | 0.147→0.059 | 1.00 / 3.000 | 71.193 | 114.487 |
| retract_up | retract | 1.00 / step_budget | (0.498, -0.014, 0.042)→(0.495, -0.014, 0.173) | (0.506, -0.022, 0.032)→(0.503, -0.026, 0.027) | 0.059→0.056 | 1.00 / 1.000 | 0.576 | 121.742 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.731
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.298
- phase_score: 0.428
- phase_breakdown.approach_score: 0.609
- phase_breakdown.contact_score: 0.531
- phase_breakdown.push_score: 0.334

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.376
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.298
- **Median Q (composite search score)**: 0.295
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.462


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82014,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.lateral_x":-0.01867,"approach_peg.speed":0.0943,"contact_peg.contact_force":19.41904,"push_channel.push_distance":0.18666,"push_channel.push_speed":0.07871,"retract_up.speed":0.09377},"optimized_scores":{"best_composite_score":0.34962,"best_fitness_score":0.37629,"best_task_score":0.29802},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54483,-0.03118,0.06],"force_p95":66.41182,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.9732,"mean_force":61.35939,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50033,-0.02535,0.03668]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":435.0,"contact_point_centroid":[0.54492,0.03086,0.06],"force_p95":55.02837,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.00895,"mean_force":42.21983,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50014,0.03352,0.03673]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.10043,0.06],"force_p95":36.90772,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.90772,"mean_force":36.90772,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50316,0.10032,0.04044]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.1003,0.06],"force_p95":24.60882,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":24.65584,"mean_force":24.18566,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50311,0.10019,0.04033]},{"body_a":"peg","body_b":"channel_base_body","contact_count":729.0,"contact_point_centroid":[0.50564,-0.0036,0.00985],"force_p95":12.64961,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.24858,"mean_force":4.83346,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50024,0.04107,0.03685]},{"body_a":"attachment","body_b":"peg","contact_count":716.0,"contact_point_centroid":[0.50466,0.02498,0.04282],"force_p95":12.3886,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.12306,"mean_force":4.54023,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50013,0.03676,0.03672]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":293.0,"contact_point_centroid":[0.52507,-0.00318,0.02277],"force_p95":2.43922,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.15045,"mean_force":0.66491,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50018,0.02546,0.03674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":809.0,"contact_point_centroid":[0.50584,0.06301,0.00937],"force_p95":0.55619,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56329,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50247,0.15191,0.16888]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49957,0.19844,0.29611]},{"body_a":"peg","body_b":"channel_base_body","contact_count":396.0,"contact_point_centroid":[0.5063,-0.0569,0.0095],"force_p95":0.58177,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.78405,"mean_force":0.53641,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49739,-0.02529,0.1012]},{"body_a":"attachment","body_b":"peg","contact_count":24.0,"contact_point_centroid":[0.50411,-0.03729,0.0553],"force_p95":0.64536,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.5386,"mean_force":0.42814,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49847,-0.02549,0.04736]},{"body_a":"peg","body_b":"channel_base_body","contact_count":66.0,"contact_point_centroid":[0.50529,0.06244,0.00938],"force_p95":0.55069,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55286,"mean_force":0.54651,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5044,0.10362,0.04369]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52505,-0.05491,0.04663],"force_p95":0.4648,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53327,"mean_force":0.20029,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.49859,-0.02546,0.04659]}],"total_contact_groups":13},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50668,-0.05399,0.03381],"final_tcp_position":[0.49754,-0.02522,0.16693],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":66.9732,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":837.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06294,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54796,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":843.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.50646,0.10699,0.04793],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04626,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":66.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.06304,0.03381],"object_pos_start":[0.50601,0.06294,0.0338],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":36.90772,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":67.0,"raw_peak_contact_force":36.90772,"subtask_id":"contact","tcp_end":[0.50313,0.10023,0.04037],"tcp_start":[0.50646,0.10699,0.04793],"tcp_to_object_dist_end":0.03787,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5068,-0.05465,0.03586],"object_pos_start":[0.50598,0.06304,0.03381],"object_to_goal_dist_end":0.02657,"object_to_goal_dist_start":0.1433,"object_z_max":0.03624,"peak_contact_force":45.34921,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2175.0,"raw_peak_contact_force":62.00895,"subtask_id":"push","tcp_end":[0.50033,-0.02529,0.03668],"tcp_start":[0.50313,0.10023,0.04037],"tcp_to_object_dist_end":0.03008,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":398.0,"n_steps_budget":990.0,"object_pos_end":[0.50668,-0.05399,0.03381],"object_pos_start":[0.5068,-0.05465,0.03586],"object_to_goal_dist_end":0.02756,"object_to_goal_dist_start":0.02657,"object_z_max":0.03608,"peak_contact_force":0.55058,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":433.0,"raw_peak_contact_force":66.9732,"tcp_end":[0.49754,-0.02522,0.16693],"tcp_start":[0.50033,-0.02529,0.03668],"tcp_to_object_dist_end":0.13651,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17521,"average_solve_count":234.0,"average_success_count":234.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.lateral_x":-0.01869,"approach_peg.speed":0.07421,"contact_peg.contact_force":8.84516,"push_channel.push_distance":0.18545,"push_channel.push_speed":0.07892,"retract_up.speed":0.02139},"optimized_scores":{"best_composite_score":0.24074,"best_fitness_score":0.2674,"best_task_score":0.08929},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":115.0,"contact_point_centroid":[0.52515,0.10527,0.05993],"force_p95":347.99573,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":370.92008,"mean_force":319.62502,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5115,0.10525,0.05832]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52508,0.10473,0.05996],"force_p95":94.51652,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.14561,"mean_force":77.15615,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5105,0.10468,0.05691]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52513,0.10485,0.05994],"force_p95":58.47546,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.47546,"mean_force":58.47546,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51069,0.1048,0.05705]},{"body_a":"peg","body_b":"channel_base_body","contact_count":461.0,"contact_point_centroid":[0.50527,0.00503,0.00807],"force_p95":0.68711,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.08249,"mean_force":0.65797,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50355,-0.02521,0.11496]},{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50378,0.02343,0.00894],"force_p95":7.34963,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.00458,"mean_force":2.36943,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50689,0.04029,0.05231]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.525,0.02946,0.02426],"force_p95":8.62498,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.66391,"mean_force":3.41696,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.50347,-0.02515,0.1466]},{"body_a":"attachment","body_b":"peg","contact_count":336.0,"contact_point_centroid":[0.50804,0.05052,0.05181],"force_p95":7.70697,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.6456,"mean_force":5.42393,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5069,0.06236,0.05226]},{"body_a":"peg","body_b":"channel_base_body","contact_count":914.0,"contact_point_centroid":[0.50596,0.0566,0.00937],"force_p95":0.59921,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56404,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50616,0.14549,0.16031]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49961,0.19832,0.29591]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5068,0.07451,0.00938],"force_p95":0.55013,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55013,"mean_force":0.55013,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51069,0.1048,0.05705]}],"total_contact_groups":10},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50597,0.00547,0.02412],"final_tcp_position":[0.50376,-0.02515,0.18241],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":370.92008,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":943.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05663,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":322.87168,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1066.0,"raw_peak_contact_force":370.92008,"subtask_id":"approach","tcp_end":[0.51069,0.1048,0.05705],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50615,0.05662,0.03378],"object_pos_start":[0.50613,0.05663,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13691,"object_z_max":0.03378,"peak_contact_force":58.47546,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":58.47546,"subtask_id":"contact","tcp_end":[0.51068,0.1048,0.05703],"tcp_start":[0.51069,0.1048,0.05705],"tcp_to_object_dist_end":0.05368,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50277,0.00512,0.02413],"object_pos_start":[0.50615,0.05662,0.03378],"object_to_goal_dist_end":0.08664,"object_to_goal_dist_start":0.1369,"object_z_max":0.04049,"peak_contact_force":0.68337,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1341.0,"raw_peak_contact_force":95.14561,"subtask_id":"push","tcp_end":[0.50656,-0.02522,0.05192],"tcp_start":[0.51068,0.1048,0.05703],"tcp_to_object_dist_end":0.04132,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":461.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.00547,0.02412],"object_pos_start":[0.50277,0.00512,0.02413],"object_to_goal_dist_end":0.08714,"object_to_goal_dist_start":0.08664,"object_z_max":0.02448,"peak_contact_force":0.53268,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":469.0,"raw_peak_contact_force":9.08249,"tcp_end":[0.50376,-0.02515,0.18241],"tcp_start":[0.50656,-0.02522,0.05192],"tcp_to_object_dist_end":0.16124,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16942,"average_solve_count":242.0,"average_success_count":242.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.lateral_x":0.02145,"approach_peg.speed":0.07144,"contact_peg.contact_force":8.47132,"push_channel.push_distance":0.15241,"push_channel.push_speed":0.07479,"retract_up.speed":0.02615},"optimized_scores":{"best_composite_score":0.29481,"best_fitness_score":0.32148,"best_task_score":0.25142},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":42.0,"contact_point_centroid":[0.47497,0.00697,0.05133],"force_p95":275.05557,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":289.16883,"mean_force":172.25318,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48562,0.00697,0.04587]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":803.0,"contact_point_centroid":[0.53212,0.06204,0.05999],"force_p95":159.27068,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":186.30711,"mean_force":111.32995,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48667,0.06282,0.03789]},{"body_a":"attachment","body_b":"peg","contact_count":781.0,"contact_point_centroid":[0.49537,0.04484,0.03828],"force_p95":85.03998,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.8899,"mean_force":39.06255,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48672,0.05213,0.03802]},{"body_a":"peg","body_b":"channel_base_body","contact_count":952.0,"contact_point_centroid":[0.50447,0.03134,0.00965],"force_p95":79.56571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.97349,"mean_force":22.30357,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4867,0.06068,0.03792]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":546.0,"contact_point_centroid":[0.52562,0.02565,0.02201],"force_p95":72.18167,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.97724,"mean_force":35.54768,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48677,0.03662,0.03816]},{"body_a":"attachment","body_b":"peg","contact_count":38.0,"contact_point_centroid":[0.49542,0.0045,0.0359],"force_p95":77.11793,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.96764,"mean_force":36.68146,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48577,0.00694,0.04034]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":71.0,"contact_point_centroid":[0.52615,-0.00424,0.03029],"force_p95":76.86098,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.88952,"mean_force":21.37459,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48573,0.00697,0.04462]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53178,0.00315,0.05997],"force_p95":73.12582,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.88525,"mean_force":64.62361,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48626,0.00708,0.03826]},{"body_a":"peg","body_b":"channel_base_body","contact_count":427.0,"contact_point_centroid":[0.49822,-0.02312,0.00849],"force_p95":7.29602,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.31513,"mean_force":1.54018,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48369,0.00711,0.10387]},{"body_a":"peg","body_b":"link7","contact_count":381.0,"contact_point_centroid":[0.51757,0.02218,0.06823],"force_p95":31.56839,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.08953,"mean_force":13.44598,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48693,0.04737,0.03809]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53197,0.11379,0.05999],"force_p95":20.28844,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":20.28844,"mean_force":20.28844,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48681,0.11195,0.03731]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47494,-0.0516,0.02426],"force_p95":7.90683,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.10648,"mean_force":2.92585,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48313,0.00712,0.09129]},{"body_a":"peg","body_b":"channel_base_body","contact_count":796.0,"contact_point_centroid":[0.494,0.07997,0.00937],"force_p95":0.61669,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.56248,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4932,0.16032,0.16966]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49933,0.19862,0.29608]},{"body_a":"peg","body_b":"channel_base_body","contact_count":159.0,"contact_point_centroid":[0.49397,0.07967,0.00938],"force_p95":0.56283,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59001,"mean_force":0.54684,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48672,0.11673,0.04141]}],"total_contact_groups":15},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4952,-0.02894,0.02415],"final_tcp_position":[0.48345,0.00717,0.1687],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":289.16883,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":824.0,"n_steps_budget":1000.0,"object_pos_end":[0.49385,0.07994,0.03377],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54704,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":831.0,"raw_peak_contact_force":3.77147,"subtask_id":"approach","tcp_end":[0.48834,0.1232,0.04873],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04611,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":159.0,"n_steps_budget":600.0,"object_pos_end":[0.4938,0.07996,0.03378],"object_pos_start":[0.49385,0.07994,0.03377],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16018,"object_z_max":0.03378,"peak_contact_force":20.28844,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":160.0,"raw_peak_contact_force":20.28844,"subtask_id":"contact","tcp_end":[0.48682,0.11191,0.03728],"tcp_start":[0.48834,0.1232,0.04873],"tcp_to_object_dist_end":0.03289,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50981,-0.01734,0.03601],"object_pos_start":[0.4938,0.07996,0.03378],"object_to_goal_dist_end":0.06355,"object_to_goal_dist_start":0.1602,"object_z_max":0.03984,"peak_contact_force":167.54613,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3463.0,"raw_peak_contact_force":186.30711,"subtask_id":"push","tcp_end":[0.48627,0.00726,0.03825],"tcp_start":[0.48682,0.11191,0.03728],"tcp_to_object_dist_end":0.03412,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":449.0,"n_steps_budget":1000.0,"object_pos_end":[0.4952,-0.02894,0.02415],"object_pos_start":[0.50981,-0.01734,0.03601],"object_to_goal_dist_end":0.05367,"object_to_goal_dist_start":0.06355,"object_z_max":0.03732,"peak_contact_force":0.6436,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":597.0,"raw_peak_contact_force":289.16883,"tcp_end":[0.48345,0.00717,0.1687],"tcp_start":[0.48627,0.00726,0.03825],"tcp_to_object_dist_end":0.14945,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```