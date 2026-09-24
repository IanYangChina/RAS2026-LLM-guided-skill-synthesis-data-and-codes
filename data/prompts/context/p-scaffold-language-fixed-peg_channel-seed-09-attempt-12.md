## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0523 | 0.17 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.2951 | 0.21 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.1229 | 0.17 | ❌ rejected |
| 9 | approach → align → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0795 | 0.23 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.1261 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.052) — your mutation base

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

- **Composite score**: 0.052
- **task_score** (E): 0.173
- **fitness_score**: 0.162  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1719 |
| contact_peg | 1.00 | 1.00 | 0.1007 |
| push_channel | 0.00 | 1.00 | 0.0324 |
| retract_up | 1.00 | 1.00 | 0.1302 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.518, 0.117, 0.155) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 1.000 | 0.545 | 4.034 |
| contact_peg | contact | 1.00 / force_exceeded | (0.518, 0.117, 0.155)→(0.502, 0.094, 0.060) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.000 | 27.166 | 27.166 |
| push_channel | push | 0.00 / step_budget | (0.502, 0.094, 0.060)→(0.519, 0.077, 0.080) | (0.502, 0.067, 0.034)→(0.500, -0.011, 0.024) | 0.147→0.072 | 1.00 / 2.333 | 298.975 | 1561.784 |
| retract_up | retract | 1.00 / step_budget | (0.519, 0.077, 0.080)→(0.518, 0.076, 0.210) | (0.500, -0.011, 0.024)→(0.500, -0.010, 0.024) | 0.072→0.072 | 1.00 / 1.000 | 0.643 | 142.167 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.842
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.343
- phase_score: 0.161
- phase_breakdown.approach_score: 0.096
- phase_breakdown.contact_score: 0.590
- phase_breakdown.push_score: 0.039

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.234
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.343
- **Median Q (composite search score)**: 0.022
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.252


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64634,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.lateral_x":0.02137,"approach_peg.speed":0.07975,"contact_peg.contact_force":10.83722,"push_channel.push_distance":0.05146,"push_channel.push_speed":0.03386,"retract_up.speed":0.08489},"optimized_scores":{"best_composite_score":0.02183,"best_fitness_score":0.13183,"best_task_score":0.0915},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":870.0,"contact_point_centroid":[0.52667,0.11996,0.05996],"force_p95":328.55195,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":985.84677,"mean_force":208.03368,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51593,0.07907,0.06908]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":798.0,"contact_point_centroid":[0.52506,0.07973,0.05993],"force_p95":283.88358,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":657.28902,"mean_force":230.76227,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51749,0.07875,0.06893]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":128.0,"contact_point_centroid":[0.47496,0.11994,0.05999],"force_p95":370.56074,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":402.27744,"mean_force":278.65882,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51627,0.07824,0.06788]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.47496,0.11994,0.05998],"force_p95":261.44528,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":267.09644,"mean_force":151.95866,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51618,0.07847,0.06774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":986.0,"contact_point_centroid":[0.49979,0.01694,0.00817],"force_p95":0.92766,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":187.51078,"mean_force":2.78883,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51574,0.07944,0.06863]},{"body_a":"attachment","body_b":"peg","contact_count":24.0,"contact_point_centroid":[0.51189,0.07836,0.05852],"force_p95":161.45466,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":187.1185,"mean_force":88.60575,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50967,0.08989,0.05819]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52506,0.07994,0.05995],"force_p95":82.73167,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.35012,"mean_force":32.83807,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51618,0.07853,0.06777]},{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.50599,0.06298,0.00938],"force_p95":0.55207,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.12618,"mean_force":0.63302,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.52604,0.10221,0.10589]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51452,0.07889,0.05867],"force_p95":34.72851,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.72851,"mean_force":34.72851,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51153,0.0904,0.05981]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":21.0,"contact_point_centroid":[0.52509,0.0432,0.03392],"force_p95":6.44188,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.64703,"mean_force":0.85004,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51405,0.08061,0.07009]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47499,-0.00745,0.02435],"force_p95":6.27687,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.28745,"mean_force":2.59238,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51843,0.07896,0.0698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":327.0,"contact_point_centroid":[0.50552,0.06305,0.00934],"force_p95":0.60522,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.58793,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.52147,0.15457,0.22147]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50089,0.19722,0.29506]},{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.50191,0.01367,0.00806],"force_p95":0.68461,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75999,"mean_force":0.60544,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51445,0.07795,0.1317]}],"total_contact_groups":14},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50047,0.01397,0.02413],"final_tcp_position":[0.51454,0.07809,0.19806],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":985.84677,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.50604,0.06301,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.5477,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":361.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.54211,0.11401,0.15362],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13512,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":400.0,"n_steps_budget":810.0,"object_pos_end":[0.50603,0.06301,0.0338],"object_pos_start":[0.50604,0.06301,0.0338],"object_to_goal_dist_end":0.14327,"object_to_goal_dist_start":0.14327,"object_z_max":0.03381,"peak_contact_force":35.12618,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":401.0,"raw_peak_contact_force":35.12618,"subtask_id":"contact","tcp_end":[0.51147,0.09034,0.05958],"tcp_start":[0.54211,0.11401,0.15362],"tcp_to_object_dist_end":0.03796,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50336,0.01349,0.02443],"object_pos_start":[0.50603,0.06301,0.0338],"object_to_goal_dist_end":0.09483,"object_to_goal_dist_start":0.14327,"object_z_max":0.04041,"peak_contact_force":355.75411,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2835.0,"raw_peak_contact_force":985.84677,"subtask_id":"push","tcp_end":[0.51618,0.07841,0.06772],"tcp_start":[0.51147,0.09034,0.05958],"tcp_to_object_dist_end":0.07908,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.50047,0.01397,0.02413],"object_pos_start":[0.50336,0.01349,0.02443],"object_to_goal_dist_end":0.09531,"object_to_goal_dist_start":0.09483,"object_z_max":0.02445,"peak_contact_force":0.60165,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":392.0,"raw_peak_contact_force":267.09644,"tcp_end":[0.51454,0.07809,0.19806],"tcp_start":[0.51618,0.07841,0.06772],"tcp_to_object_dist_end":0.1859,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.1991,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.lateral_x":0.01417,"approach_peg.speed":0.0418,"contact_peg.contact_force":8.42162,"push_channel.push_distance":0.09971,"push_channel.push_speed":0.02855,"retract_up.speed":0.06589},"optimized_scores":{"best_composite_score":0.01135,"best_fitness_score":0.12135,"best_task_score":0.08347},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":960.0,"contact_point_centroid":[0.52588,0.11993,0.0599],"force_p95":332.95216,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1071.06057,"mean_force":290.2263,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52458,0.07488,0.08751]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52517,0.08317,0.05993],"force_p95":586.7284,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":596.87454,"mean_force":446.48871,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51178,0.08307,0.05879]},{"body_a":"peg","body_b":"channel_base_body","contact_count":991.0,"contact_point_centroid":[0.49887,0.01358,0.00823],"force_p95":0.89204,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":168.44482,"mean_force":2.48282,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52393,0.07526,0.08647]},{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.51189,0.07223,0.0582],"force_p95":164.80789,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":167.51895,"mean_force":88.21867,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50955,0.08375,0.05816]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.525,0.11995,0.05996],"force_p95":62.3513,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.47296,"mean_force":53.68349,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.52862,0.07533,0.08906]},{"body_a":"peg","body_b":"channel_base_body","contact_count":401.0,"contact_point_centroid":[0.50616,0.05665,0.00938],"force_p95":0.55324,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.3727,"mean_force":0.61362,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.52593,0.09626,0.10571]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.5142,0.07262,0.05872],"force_p95":27.02432,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.02432,"mean_force":27.02432,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51155,0.08424,0.05977]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47496,-0.01421,0.0245],"force_p95":8.67143,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.83723,"mean_force":2.21107,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.52422,0.07368,0.09099]},{"body_a":"peg","body_b":"channel_base_body","contact_count":350.0,"contact_point_centroid":[0.50574,0.05655,0.00934],"force_p95":0.60206,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.59195,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.52115,0.15186,0.22177]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50067,0.19726,0.29532]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52516,0.01625,0.05795],"force_p95":0.79051,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84629,"mean_force":0.44668,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49958,0.07571,0.06593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.5056,0.00965,0.00807],"force_p95":0.67255,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.79175,"mean_force":0.60584,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.52687,0.07484,0.15285]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.03415,0.02415],"force_p95":0.39913,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40149,"mean_force":0.37791,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.5266,0.07464,0.127]}],"total_contact_groups":13},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50631,0.0096,0.02415],"final_tcp_position":[0.527,0.07506,0.21932],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":1071.06057,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":379.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.05663,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.54137,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":387.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach","tcp_end":[0.54189,0.10823,0.15326],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13498,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":401.0,"n_steps_budget":810.0,"object_pos_end":[0.50611,0.05658,0.03377],"object_pos_start":[0.50612,0.05663,0.03377],"object_to_goal_dist_end":0.13686,"object_to_goal_dist_start":0.13691,"object_z_max":0.03378,"peak_contact_force":27.3727,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":402.0,"raw_peak_contact_force":27.3727,"subtask_id":"contact","tcp_end":[0.51148,0.08418,0.05954],"tcp_start":[0.54189,0.10823,0.15326],"tcp_to_object_dist_end":0.03814,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50395,0.00975,0.02414],"object_pos_start":[0.50611,0.05658,0.03377],"object_to_goal_dist_end":0.09123,"object_to_goal_dist_start":0.13686,"object_z_max":0.04059,"peak_contact_force":262.3007,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1997.0,"raw_peak_contact_force":1071.06057,"subtask_id":"push","tcp_end":[0.52863,0.0753,0.08902],"tcp_start":[0.51148,0.08418,0.05954],"tcp_to_object_dist_end":0.09547,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.50631,0.0096,0.02415],"object_pos_start":[0.50395,0.00975,0.02414],"object_to_goal_dist_end":0.09121,"object_to_goal_dist_start":0.09123,"object_z_max":0.02428,"peak_contact_force":0.64359,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":407.0,"raw_peak_contact_force":62.47296,"tcp_end":[0.527,0.07506,0.21932],"tcp_start":[0.52863,0.0753,0.08902],"tcp_to_object_dist_end":0.20689,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10294,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.lateral_x":-0.00274,"approach_peg.speed":0.04869,"contact_peg.contact_force":7.27778,"push_channel.push_distance":0.12406,"push_channel.push_speed":0.05134,"retract_up.speed":0.05964},"optimized_scores":{"best_composite_score":0.12363,"best_fitness_score":0.23363,"best_task_score":0.3433},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":523.0,"contact_point_centroid":[0.52523,0.1199,0.05989],"force_p95":310.05262,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2628.44359,"mean_force":298.37665,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50248,0.07515,0.07926]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47431,0.10026,0.04335],"force_p95":1637.46871,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1657.13297,"mean_force":1274.52154,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48417,0.09892,0.03781]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":521.0,"contact_point_centroid":[0.47498,0.11994,0.05997],"force_p95":285.81645,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":314.51588,"mean_force":266.08529,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50967,0.07466,0.08305]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.49032,0.09588,0.05901],"force_p95":250.17925,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":259.0305,"mean_force":136.38393,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48503,0.10609,0.06097]},{"body_a":"peg","body_b":"channel_base_body","contact_count":952.0,"contact_point_centroid":[0.49652,-0.05021,0.00815],"force_p95":0.75359,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":258.80181,"mean_force":1.48216,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5062,0.07511,0.08141]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.47498,0.11995,0.05997],"force_p95":95.11261,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":96.93089,"mean_force":72.17425,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51262,0.07658,0.08201]},{"body_a":"peg","body_b":"channel_base_body","contact_count":570.0,"contact_point_centroid":[0.49382,0.08,0.00938],"force_p95":0.57973,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.99992,"mean_force":0.5787,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.47514,0.11811,0.10722]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.4901,0.09753,0.05877],"force_p95":18.54624,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.54624,"mean_force":18.54624,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48357,0.10715,0.06174]},{"body_a":"peg","body_b":"channel_base_body","contact_count":402.0,"contact_point_centroid":[0.4936,-0.0549,0.00806],"force_p95":0.68511,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.58772,"mean_force":0.64872,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.5109,0.07603,0.14583]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.475,-0.0301,0.02422],"force_p95":9.00122,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.1068,"mean_force":2.82324,"phase_index":3.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.51154,0.07641,0.10183]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47499,-0.0304,0.02412],"force_p95":7.74709,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.0386,"mean_force":2.54424,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.51044,0.07497,0.08271]},{"body_a":"peg","body_b":"channel_base_body","contact_count":298.0,"contact_point_centroid":[0.49441,0.0799,0.00935],"force_p95":0.61814,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.58938,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4834,0.16302,0.2234]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49859,0.19756,0.29507]}],"total_contact_groups":13},"final_pose_error":0.02,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49323,-0.05475,0.02413],"final_tcp_position":[0.511,0.0762,0.21203],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":2628.44359,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,0.07997,0.03379],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16021,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.54531,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":333.0,"raw_peak_contact_force":3.77147,"subtask_id":"approach","tcp_end":[0.46935,0.12987,0.15674],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":570.0,"n_steps_budget":810.0,"object_pos_end":[0.49379,0.07991,0.03376],"object_pos_start":[0.49382,0.07997,0.03379],"object_to_goal_dist_end":0.16015,"object_to_goal_dist_start":0.16021,"object_z_max":0.03383,"peak_contact_force":18.99992,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":571.0,"raw_peak_contact_force":18.99992,"subtask_id":"contact","tcp_end":[0.4836,0.10711,0.06158],"tcp_start":[0.46935,0.12987,0.15674],"tcp_to_object_dist_end":0.04022,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49344,-0.0551,0.02413],"object_pos_start":[0.49379,0.07991,0.03376],"object_to_goal_dist_end":0.03025,"object_to_goal_dist_start":0.16015,"object_z_max":0.04262,"peak_contact_force":278.87064,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2015.0,"raw_peak_contact_force":2628.44359,"subtask_id":"push","tcp_end":[0.51262,0.07655,0.08196],"tcp_start":[0.4836,0.10711,0.06158],"tcp_to_object_dist_end":0.14507,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":402.0,"n_steps_budget":1000.0,"object_pos_end":[0.49323,-0.05475,0.02413],"object_pos_start":[0.49344,-0.0551,0.02413],"object_to_goal_dist_end":0.03058,"object_to_goal_dist_start":0.03025,"object_z_max":0.02442,"peak_contact_force":0.68353,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":414.0,"raw_peak_contact_force":96.93089,"tcp_end":[0.511,0.0762,0.21203],"tcp_start":[0.51262,0.07655,0.08196],"tcp_to_object_dist_end":0.22972,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```