## Search State

- **Seed**: 9
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | align → approach → approach → descend → contact → push | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | 0.0611 | 0.34 | ✅ accepted |
| 7 | align → approach → descend → contact → push | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 5 | 0.1917 | 0.22 | ✅ accepted |
| 6 | align → approach → contact → push | joint_interpolation | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 4 | 0.1554 | 0.13 | ✅ accepted |
| 5 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.0859 | 0.04 | ✅ accepted |
| 4 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0746 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.34 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.061) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
phases:
- id: align
  type: align
  generator: joint_interpolation
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.05
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
- id: approach_entry
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.16
    - -0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    entry_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_peg
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.018
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
- id: contact
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
    - 0.018
    - 0.0
    tolerance: 0.02
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
  subtask_id: contact
- id: push
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.018
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
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
    push_duration:
      type: scalar
      range:
      - 1.0
      - 3.0
      default: 2.0
      binds_to:
      - path: duration.max_time
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
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align** (`align`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.05
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings: none
- **approach_entry** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.16, -0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - entry_speed: status=consumed; consumers=generator.speed (replace)
- **approach_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.018, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **contact** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.018, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.018, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=50.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]

## Design Metrics

- **Composite score**: 0.061
- **task_score** (E): 0.344
- **fitness_score**: 0.464  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.470

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align | 1.00 | 1.00 | 0.0041 |
| approach_entry | 1.00 | 1.00 | 0.2747 |
| approach_peg | 1.00 | 1.00 | 0.0106 |
| descend | 1.00 | 1.00 | 0.0039 |
| contact | 0.67 | 1.00 | 0.0136 |
| push | 1.00 | 1.00 | 0.1408 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.498, 0.203, 0.299) | (0.512, 0.067, 0.040)→(0.507, 0.067, 0.038) | 0.150→0.148 | 1.00 / 1.000 | 0.133 | 3.257 |
| approach_entry | approach | 1.00 / step_budget | (0.498, 0.203, 0.299)→(0.498, 0.090, 0.048) | (0.507, 0.067, 0.038)→(0.503, 0.065, 0.034) | 0.148→0.145 | 1.00 / 1.333 | 63.338 | 70.570 |
| approach_peg | approach | 1.00 / step_budget | (0.498, 0.090, 0.048)→(0.500, 0.097, 0.044) | (0.503, 0.065, 0.034)→(0.503, 0.066, 0.035) | 0.145→0.147 | 1.00 / 1.333 | 0.461 | 66.006 |
| descend | descend | 1.00 / step_budget | (0.500, 0.097, 0.044)→(0.499, 0.096, 0.041) | (0.503, 0.066, 0.035)→(0.502, 0.063, 0.035) | 0.147→0.144 | 1.00 / 1.333 | 0.563 | 7.916 |
| contact | contact | 0.67 / step_budget | (0.499, 0.096, 0.041)→(0.500, 0.086, 0.033) | (0.502, 0.063, 0.035)→(0.504, 0.057, 0.036) | 0.144→0.137 | 1.00 / 2.333 | 4.406 | 6.273 |
| push | push | 1.00 / time_limit | (0.500, 0.086, 0.033)→(0.500, -0.054, 0.031) | (0.504, 0.057, 0.036)→(0.502, -0.083, 0.035) | 0.137→0.009 | 1.00 / 2.667 | 31.711 | 37.351 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.397
- phase_score: 0.536
- phase_breakdown.approach_score: 0.457
- phase_breakdown.push_score: 0.552
- phase_breakdown.contact_score: 0.570

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.488
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.397
- **Median Q (composite search score)**: 0.018
- **K-run variance**: 0.0118
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.319


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16364,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.entry_speed":0.90176,"approach_peg.approach_speed":0.70925,"contact.contact_force":7.98682,"descend.descend_speed":0.19517,"push.push_depth":0.13323,"push.push_duration":1.45114,"push.push_speed":0.09999},"optimized_scores":{"best_composite_score":0.01755,"best_fitness_score":0.48755,"best_task_score":0.37595},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":655.0,"contact_point_centroid":[0.50467,-0.00035,0.04355],"force_p95":12.87592,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.88488,"mean_force":5.21692,"phase_index":5.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50064,0.01148,0.02915]},{"body_a":"peg","body_b":"channel_base_body","contact_count":38.0,"contact_point_centroid":[0.50675,-0.10067,0.05591],"force_p95":44.15485,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.56365,"mean_force":28.82869,"phase_index":5.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.503,-0.0539,0.03033]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50162,0.07835,0.05649],"force_p95":18.41229,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.34785,"mean_force":9.66542,"phase_index":3.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49599,0.08969,0.04087]},{"body_a":"peg","body_b":"channel_base_body","contact_count":19.0,"contact_point_centroid":[0.50944,0.04549,0.0099],"force_p95":12.62234,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.59538,"mean_force":3.77188,"phase_index":3.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49603,0.08994,0.04149]},{"body_a":"peg","body_b":"channel_base_body","contact_count":431.0,"contact_point_centroid":[0.5058,0.06256,0.00935],"force_p95":0.59723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.01456,"mean_force":0.62426,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49689,0.14589,0.17039]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50117,0.0801,0.05887],"force_p95":15.95898,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.57441,"mean_force":10.42012,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49688,0.09162,0.05171]},{"body_a":"peg","body_b":"channel_base_body","contact_count":496.0,"contact_point_centroid":[0.50636,-0.03677,0.00993],"force_p95":10.13284,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.98754,"mean_force":5.1682,"phase_index":5.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50075,0.00944,0.02923]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52513,0.06009,0.06],"force_p95":9.99534,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.12029,"mean_force":4.96032,"phase_index":3.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49622,0.08928,0.0404]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":439.0,"contact_point_centroid":[0.52506,-0.01247,0.02787],"force_p95":3.78655,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.9142,"mean_force":0.98474,"phase_index":5.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50042,0.01678,0.02902]},{"body_a":"attachment","body_b":"peg","contact_count":330.0,"contact_point_centroid":[0.50342,0.07114,0.04671],"force_p95":4.96559,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.25342,"mean_force":2.82113,"phase_index":4.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49865,0.08283,0.03346]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":370.0,"contact_point_centroid":[0.52517,0.05434,0.03901],"force_p95":3.3604,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.14061,"mean_force":1.73544,"phase_index":4.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49845,0.08323,0.03387]},{"body_a":"peg","body_b":"channel_base_body","contact_count":337.0,"contact_point_centroid":[0.50718,0.03757,0.00998],"force_p95":3.84298,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.75952,"mean_force":2.17132,"phase_index":4.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49846,0.08318,0.03381]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.53373,0.06295,0.0362],"force_p95":1.36479,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.64647,"phase_index":0.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49923,0.20034,0.29957]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52714,0.06295,0.02495],"force_p95":0.76857,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85654,"mean_force":0.24853,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49748,0.20268,0.29604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50881,0.04526,0.00965],"force_p95":0.42236,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43082,"mean_force":0.40952,"phase_index":2.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.496,0.08908,0.04468]}],"total_contact_groups":15},"final_pose_error":0.01181,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5067,-0.08439,0.03504],"final_tcp_position":[0.50303,-0.05549,0.03017],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":48.88488,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.5166,0.06295,0.03827],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.18909,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":2.98455,"tcp_end":[0.49787,0.20278,0.29862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.29613,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":439.0,"n_steps_budget":600.0,"object_pos_end":[0.50634,0.06089,0.03526],"object_pos_start":[0.5166,0.06295,0.03827],"object_to_goal_dist_end":0.14111,"object_to_goal_dist_start":0.14392,"object_z_max":0.03827,"peak_contact_force":0.4426,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":447.0,"raw_peak_contact_force":17.01456,"tcp_end":[0.49671,0.0894,0.04699],"tcp_start":[0.49787,0.20278,0.29862],"tcp_to_object_dist_end":0.03229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50631,0.06035,0.0364],"object_pos_start":[0.50634,0.06089,0.03526],"object_to_goal_dist_end":0.14054,"object_to_goal_dist_start":0.14111,"object_z_max":0.03646,"peak_contact_force":0.41074,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20.0,"raw_peak_contact_force":0.43082,"subtask_id":"approach","tcp_end":[0.49651,0.09001,0.04267],"tcp_start":[0.49671,0.0894,0.04699],"tcp_to_object_dist_end":0.03186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50691,0.06084,0.03622],"object_pos_start":[0.50631,0.06035,0.0364],"object_to_goal_dist_end":0.14106,"object_to_goal_dist_start":0.14054,"object_z_max":0.0364,"peak_contact_force":0.14326,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":30.0,"raw_peak_contact_force":21.34785,"tcp_end":[0.49646,0.0889,0.04003],"tcp_start":[0.49651,0.09001,0.04267],"tcp_to_object_dist_end":0.03019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":372.0,"n_steps_budget":600.0,"object_pos_end":[0.50726,0.05,0.03536],"object_pos_start":[0.50691,0.06084,0.03622],"object_to_goal_dist_end":0.13029,"object_to_goal_dist_start":0.14106,"object_z_max":0.03628,"peak_contact_force":2.04681,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1037.0,"raw_peak_contact_force":6.25342,"subtask_id":"contact","tcp_end":[0.50165,0.0796,0.03186],"tcp_start":[0.49646,0.0889,0.04003],"tcp_to_object_dist_end":0.03032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":842.0,"n_steps_budget":900.0,"object_pos_end":[0.5067,-0.08439,0.03504],"object_pos_start":[0.50726,0.05,0.03536],"object_to_goal_dist_end":0.00942,"object_to_goal_dist_start":0.13029,"object_z_max":0.03596,"peak_contact_force":45.02516,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1628.0,"raw_peak_contact_force":48.88488,"subtask_id":"push","tcp_end":[0.50303,-0.05549,0.03017],"tcp_start":[0.50165,0.0796,0.03186],"tcp_to_object_dist_end":0.02953,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18182,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.entry_speed":0.70344,"approach_peg.approach_speed":0.9982,"contact.contact_force":19.87392,"descend.descend_speed":0.23806,"push.push_depth":0.12981,"push.push_duration":1.19706,"push.push_speed":0.09892},"optimized_scores":{"best_composite_score":-0.04481,"best_fitness_score":0.42519,"best_task_score":0.25802},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":647.0,"contact_point_centroid":[0.50456,-0.00315,0.04291],"force_p95":17.29779,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.60254,"mean_force":5.22504,"phase_index":5.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50037,0.00868,0.02807]},{"body_a":"peg","body_b":"channel_base_body","contact_count":43.0,"contact_point_centroid":[0.50695,-0.10067,0.05751],"force_p95":46.30374,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.30801,"mean_force":30.62248,"phase_index":5.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50298,-0.05396,0.03012]},{"body_a":"peg","body_b":"channel_base_body","contact_count":483.0,"contact_point_centroid":[0.50572,-0.03821,0.00992],"force_p95":9.27486,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.11576,"mean_force":4.68186,"phase_index":5.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5004,0.00826,0.0281]},{"body_a":"attachment","body_b":"peg","contact_count":338.0,"contact_point_centroid":[0.50355,0.06825,0.0506],"force_p95":5.71672,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.44412,"mean_force":3.55952,"phase_index":4.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49808,0.07997,0.03173]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":434.0,"contact_point_centroid":[0.52507,-0.01366,0.02469],"force_p95":3.19876,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.41679,"mean_force":0.85305,"phase_index":5.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.5,0.01547,0.02775]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":324.0,"contact_point_centroid":[0.5251,0.05041,0.04729],"force_p95":3.59512,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.27421,"mean_force":2.16205,"phase_index":4.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49825,0.07965,0.03148]},{"body_a":"peg","body_b":"channel_base_body","contact_count":380.0,"contact_point_centroid":[0.50877,0.03619,0.0099],"force_p95":3.91342,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.64437,"mean_force":2.44356,"phase_index":4.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49772,0.08079,0.03244]},{"body_a":"peg","body_b":"channel_base_body","contact_count":430.0,"contact_point_centroid":[0.50582,0.05666,0.00935],"force_p95":0.60146,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58331,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49689,0.14576,0.1701]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.5365,0.05661,0.03623],"force_p95":1.44525,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.75988,"phase_index":0.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49923,0.20034,0.29957]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52781,0.05661,0.01411],"force_p95":0.88065,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04601,"mean_force":0.25192,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49744,0.2024,0.29522]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50563,0.05597,0.00939],"force_p95":0.56371,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56805,"mean_force":0.54709,"phase_index":2.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49597,0.0889,0.04462]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.5057,0.05662,0.00939],"force_p95":0.56325,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56564,"mean_force":0.54595,"phase_index":3.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49598,0.08905,0.04108]}],"total_contact_groups":12},"final_pose_error":0.01216,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50693,-0.08426,0.03497],"final_tcp_position":[0.50305,-0.05558,0.03],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":49.60254,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.52027,0.05661,0.03869],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13812,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.14277,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":3.83578,"tcp_end":[0.49787,0.20278,0.29862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.29905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":439.0,"n_steps_budget":600.0,"object_pos_end":[0.50612,0.0566,0.03379],"object_pos_start":[0.52027,0.05661,0.03869],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.13812,"object_z_max":0.03869,"peak_contact_force":0.52395,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":447.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.4967,0.08936,0.04697],"tcp_start":[0.49787,0.20278,0.29862],"tcp_to_object_dist_end":0.03654,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50612,0.05662,0.03378],"object_pos_start":[0.50612,0.0566,0.03379],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03379,"peak_contact_force":0.56348,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20.0,"raw_peak_contact_force":0.56805,"subtask_id":"approach","tcp_end":[0.49644,0.08944,0.04249],"tcp_start":[0.4967,0.08936,0.04697],"tcp_to_object_dist_end":0.03531,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50613,0.05661,0.03379],"object_pos_start":[0.50612,0.05662,0.03378],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.1369,"object_z_max":0.03379,"peak_contact_force":0.55603,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20.0,"raw_peak_contact_force":0.56564,"tcp_end":[0.49643,0.08766,0.03941],"tcp_start":[0.49644,0.08944,0.04249],"tcp_to_object_dist_end":0.03301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.50739,0.04623,0.03539],"object_pos_start":[0.50613,0.05661,0.03379],"object_to_goal_dist_end":0.12653,"object_to_goal_dist_start":0.13689,"object_z_max":0.0357,"peak_contact_force":1.42047,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1042.0,"raw_peak_contact_force":7.44412,"subtask_id":"contact","tcp_end":[0.50096,0.07578,0.02968],"tcp_start":[0.49643,0.08766,0.03941],"tcp_to_object_dist_end":0.03078,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":842.0,"n_steps_budget":900.0,"object_pos_end":[0.50693,-0.08426,0.03497],"object_pos_start":[0.50739,0.04623,0.03539],"object_to_goal_dist_end":0.00957,"object_to_goal_dist_start":0.12653,"object_z_max":0.03599,"peak_contact_force":48.69459,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1607.0,"raw_peak_contact_force":49.60254,"subtask_id":"push","tcp_end":[0.50305,-0.05558,0.03],"tcp_start":[0.50096,0.07578,0.02968],"tcp_to_object_dist_end":0.02937,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5566,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.entry_speed":0.58207,"approach_peg.approach_speed":0.54396,"contact.contact_force":5.27338,"descend.descend_speed":0.14789,"push.push_depth":0.15151,"push.push_duration":2.48378,"push.push_speed":0.09883},"optimized_scores":{"best_composite_score":0.21071,"best_fitness_score":0.48071,"best_task_score":0.39709},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":99.0,"contact_point_centroid":[0.50657,0.09119,0.0077],"force_p95":193.75534,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":197.01805,"mean_force":165.82323,"phase_index":2.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50598,0.10098,0.04901]},{"body_a":"attachment","body_b":"peg","contact_count":99.0,"contact_point_centroid":[0.50792,0.09049,0.05243],"force_p95":193.25762,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":196.47948,"mean_force":165.3808,"phase_index":2.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50598,0.10098,0.04901]},{"body_a":"peg","body_b":"channel_base_body","contact_count":436.0,"contact_point_centroid":[0.49533,0.08006,0.00932],"force_p95":160.87451,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":190.24889,"mean_force":11.71748,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49703,0.14531,0.16913]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.51026,0.08851,0.0553],"force_p95":189.58677,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.66614,"mean_force":173.5621,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49908,0.09286,0.05459]},{"body_a":"peg","body_b":"channel_base_body","contact_count":577.0,"contact_point_centroid":[0.49498,-0.01667,0.00989],"force_p95":7.38319,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.56576,"mean_force":2.61654,"phase_index":5.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49379,0.02791,0.03305]},{"body_a":"attachment","body_b":"peg","contact_count":709.0,"contact_point_centroid":[0.49454,0.0137,0.04295],"force_p95":8.00222,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.1037,"mean_force":2.28706,"phase_index":5.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49377,0.02574,0.03307]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":194.0,"contact_point_centroid":[0.47488,-0.03875,0.0377],"force_p95":8.18186,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.9336,"mean_force":2.17018,"phase_index":5.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.4934,-0.00881,0.03319]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47498,0.08081,0.01255],"force_p95":11.63409,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.23487,"mean_force":7.76745,"phase_index":2.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50948,0.11147,0.04773]},{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.49451,-0.10022,0.05985],"force_p95":10.93816,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.02625,"mean_force":9.57114,"phase_index":5.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49301,-0.05136,0.03341]},{"body_a":"peg","body_b":"channel_base_body","contact_count":60.0,"contact_point_centroid":[0.49673,0.06257,0.00964],"force_p95":0.72549,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.12189,"mean_force":0.57901,"phase_index":4.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50151,0.10787,0.03938]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49765,0.09282,0.03697],"force_p95":4.3322,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.02047,"mean_force":1.34687,"phase_index":4.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49832,0.10439,0.03701]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.46621,0.07994,0.03877],"force_p95":1.38176,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.64457,"phase_index":0.0,"phase_name":"align","phase_type":"align","tcp_position_centroid":[0.49923,0.20034,0.29957]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47468,0.07251,0.03848],"force_p95":1.73803,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.83361,"mean_force":1.17507,"phase_index":3.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50573,0.11172,0.04333]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50149,0.07057,0.00843],"force_p95":1.51983,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62127,"mean_force":0.96942,"phase_index":3.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50668,0.11223,0.04436]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":15.0,"contact_point_centroid":[0.47289,0.07995,0.02378],"force_p95":0.64934,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.74814,"mean_force":0.21246,"phase_index":1.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49747,0.20259,0.29576]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47452,0.06482,0.05996],"force_p95":0.62319,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.70618,"mean_force":0.1928,"phase_index":4.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50431,0.1105,0.04172]}],"total_contact_groups":17},"final_pose_error":0.00928,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49376,-0.08164,0.0358],"final_tcp_position":[0.49299,-0.05187,0.03339],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":197.01805,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.4833,0.07995,0.03833],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16082,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":0.06788,"phase_name":"align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":20.0,"raw_peak_contact_force":2.95027,"tcp_end":[0.49787,0.20278,0.29862],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.28819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":444.0,"n_steps_budget":600.0,"object_pos_end":[0.49568,0.078,0.03201],"object_pos_start":[0.4833,0.07995,0.03833],"object_to_goal_dist_end":0.15826,"object_to_goal_dist_start":0.16082,"object_z_max":0.03833,"peak_contact_force":189.04657,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":479.0,"raw_peak_contact_force":190.24889,"tcp_end":[0.50202,0.09074,0.05069],"tcp_start":[0.49787,0.20278,0.29862],"tcp_to_object_dist_end":0.02349,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":99.0,"n_steps_budget":600.0,"object_pos_end":[0.49626,0.08247,0.03416],"object_pos_start":[0.49568,0.078,0.03201],"object_to_goal_dist_end":0.16262,"object_to_goal_dist_start":0.15826,"object_z_max":0.03425,"peak_contact_force":0.40834,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":201.0,"raw_peak_contact_force":197.01805,"subtask_id":"approach","tcp_end":[0.50825,0.11247,0.04605],"tcp_start":[0.50202,0.09074,0.05069],"tcp_to_object_dist_end":0.03442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49226,0.07263,0.03621],"object_pos_start":[0.49626,0.08247,0.03416],"object_to_goal_dist_end":0.15287,"object_to_goal_dist_start":0.16262,"object_z_max":0.03599,"peak_contact_force":0.99073,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":28.0,"raw_peak_contact_force":1.83361,"tcp_end":[0.50485,0.11099,0.04239],"tcp_start":[0.50825,0.11247,0.04605],"tcp_to_object_dist_end":0.04084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":67.0,"n_steps_budget":600.0,"object_pos_end":[0.4967,0.07447,0.03795],"object_pos_start":[0.49226,0.07263,0.03621],"object_to_goal_dist_end":0.15452,"object_to_goal_dist_start":0.15287,"object_z_max":0.03934,"peak_contact_force":9.75073,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":79.0,"raw_peak_contact_force":5.12189,"subtask_id":"contact","tcp_end":[0.4979,0.10386,0.03674],"tcp_start":[0.50485,0.11099,0.04239],"tcp_to_object_dist_end":0.02944,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":962.0,"n_steps_budget":1000.0,"object_pos_end":[0.49376,-0.08164,0.0358],"object_pos_start":[0.4967,0.07447,0.03795],"object_to_goal_dist_end":0.0077,"object_to_goal_dist_start":0.15452,"object_z_max":0.03795,"peak_contact_force":1.41298,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1488.0,"raw_peak_contact_force":13.56576,"subtask_id":"push","tcp_end":[0.49299,-0.05187,0.03339],"tcp_start":[0.4979,0.10386,0.03674],"tcp_to_object_dist_end":0.02988,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```