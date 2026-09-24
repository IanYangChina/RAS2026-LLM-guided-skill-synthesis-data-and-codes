## Search State

- **Seed**: 9
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | time_limit | 7 | 0.0100 | 0.27 | ❌ rejected |
| 11 | align → approach → approach → contact → push | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 6 | 0.0368 | 0.24 | ❌ rejected |
| 10 | align → approach → descend → contact → push | joint_interpolation | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | 0.2295 | 0.09 | ❌ rejected |
| 9 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 5 | 0.1992 | 0.00 | ❌ rejected |
| 8 | align → approach → approach → descend → contact → push | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 7 | 0.0611 | 0.34 | ✅ accepted |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.010) — your mutation base

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

- **Composite score**: 0.010
- **task_score** (E): 0.274
- **fitness_score**: 0.420  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_entry | 1.00 | 1.00 | 0.2750 |
| approach_peg | 1.00 | 1.00 | 0.0079 |
| contact_engage | 1.00 | 1.00 | 0.0253 |
| push | 0.33 | 1.00 | 0.0435 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_entry | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.499, 0.090, 0.048) | (0.512, 0.067, 0.040)→(0.503, 0.065, 0.034) | 0.150→0.145 | 1.00 / 1.667 | 62.255 | 69.402 |
| approach_peg | approach | 1.00 / step_budget | (0.499, 0.090, 0.048)→(0.500, 0.092, 0.043) | (0.503, 0.065, 0.034)→(0.501, 0.064, 0.034) | 0.145→0.145 | 1.00 / 1.667 | 18.445 | 64.001 |
| contact_engage | contact | 1.00 / time_limit | (0.500, 0.092, 0.043)→(0.498, 0.072, 0.031) | (0.501, 0.064, 0.034)→(0.502, 0.043, 0.035) | 0.145→0.123 | 1.00 / 3.000 | 2.505 | 22.901 |
| push | push | 0.33 / guard_failure | (0.498, -0.008, 0.030)→(0.497, -0.051, 0.029) | (0.502, 0.043, 0.035)→(0.507, -0.078, 0.036) | 0.123→0.011 | 1.00 / 3.000 | 22.720 | 42.526 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.916
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.382
- phase_score: 0.547
- phase_breakdown.approach_score: 0.482
- phase_breakdown.push_score: 0.582
- phase_breakdown.contact_score: 0.507

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.481
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.382
- **Median Q (composite search score)**: 0.010
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.395


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4898,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.entry_speed":0.49734,"approach_peg.approach_speed":0.08678,"contact_engage.contact_duration":0.80087,"contact_engage.contact_speed":0.03654,"push.push_depth":0.15166,"push.push_duration":3.38112,"push.push_speed":0.07666},"optimized_scores":{"best_composite_score":0.07079,"best_fitness_score":0.48079,"best_task_score":0.38184},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":838.0,"contact_point_centroid":[0.50398,-0.00687,0.04391],"force_p95":23.45439,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.25494,"mean_force":5.33398,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49958,0.00494,0.02951]},{"body_a":"peg","body_b":"channel_base_body","contact_count":54.0,"contact_point_centroid":[0.50715,-0.1005,0.06047],"force_p95":44.8021,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":52.51108,"mean_force":33.49837,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50152,-0.05383,0.02988]},{"body_a":"peg","body_b":"channel_base_body","contact_count":411.0,"contact_point_centroid":[0.50584,0.06255,0.00935],"force_p95":0.59723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.97051,"mean_force":0.64255,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49792,0.1415,0.16541]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50129,0.08001,0.05897],"force_p95":15.55535,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.77762,"mean_force":13.5549,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.4971,0.09157,0.05244]},{"body_a":"peg","body_b":"channel_base_body","contact_count":591.0,"contact_point_centroid":[0.50633,-0.03867,0.00994],"force_p95":8.30871,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.32448,"mean_force":4.65256,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49953,0.00766,0.02954]},{"body_a":"peg","body_b":"channel_base_body","contact_count":371.0,"contact_point_centroid":[0.50729,0.03099,0.00998],"force_p95":5.66934,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.94834,"mean_force":3.32923,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.49754,0.07584,0.03575]},{"body_a":"attachment","body_b":"peg","contact_count":408.0,"contact_point_centroid":[0.50236,0.06397,0.04424],"force_p95":7.14534,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.51497,"mean_force":3.46861,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.49761,0.07545,0.03556]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":497.0,"contact_point_centroid":[0.52504,-0.02808,0.02575],"force_p95":3.56096,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.45747,"mean_force":1.12739,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49971,0.00075,0.02953]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":430.0,"contact_point_centroid":[0.52523,0.047,0.03384],"force_p95":4.26521,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.23904,"mean_force":2.02859,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.49764,0.07524,0.03545]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":35.0,"contact_point_centroid":[0.53085,0.0628,0.03238],"force_p95":1.12518,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.47622,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.4995,0.19362,0.28532]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50739,0.04513,0.00971],"force_p95":0.42516,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.42576,"mean_force":0.40643,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49606,0.08836,0.04482]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.05721,0.06],"force_p95":0.1935,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19656,"mean_force":0.16588,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4968,0.08907,0.04691]}],"total_contact_groups":12},"final_pose_error":0.05554,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50712,-0.08364,0.03547],"final_tcp_position":[0.50159,-0.05498,0.02969],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":55.25494,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":439.0,"n_steps_budget":600.0,"object_pos_end":[0.50652,0.06011,0.03589],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14033,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.31279,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":448.0,"raw_peak_contact_force":15.97051,"tcp_end":[0.49688,0.08916,0.04713],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0326,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50587,0.05914,0.03711],"object_pos_start":[0.50652,0.06011,0.03589],"object_to_goal_dist_end":0.13929,"object_to_goal_dist_start":0.14033,"object_z_max":0.03713,"peak_contact_force":0.42576,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":22.0,"raw_peak_contact_force":0.42576,"subtask_id":"approach","tcp_end":[0.49648,0.08789,0.04287],"tcp_start":[0.49688,0.08916,0.04713],"tcp_to_object_dist_end":0.0308,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":462.0,"n_steps_budget":600.0,"object_pos_end":[0.50744,0.03675,0.0355],"object_pos_start":[0.50587,0.05914,0.03711],"object_to_goal_dist_end":0.11707,"object_to_goal_dist_start":0.13929,"object_z_max":0.03711,"peak_contact_force":3.06352,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1209.0,"raw_peak_contact_force":8.94834,"subtask_id":"contact","tcp_end":[0.50102,0.06613,0.03297],"tcp_start":[0.49648,0.08789,0.04287],"tcp_to_object_dist_end":0.03018,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":996.0,"n_steps_budget":1000.0,"object_pos_end":[0.50713,-0.08355,0.03552],"object_pos_start":[0.50744,0.03675,0.0355],"object_to_goal_dist_end":0.00914,"object_to_goal_dist_start":0.11707,"object_z_max":0.03594,"peak_contact_force":26.15154,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1980.0,"raw_peak_contact_force":55.25494,"subtask_id":"push","tcp_end":[0.50159,-0.05498,0.02969],"tcp_start":[0.50163,-0.05499,0.02974],"tcp_to_object_dist_end":0.02968,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58163,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.entry_speed":0.79074,"approach_peg.approach_speed":0.29126,"contact_engage.contact_duration":1.29625,"contact_engage.contact_speed":0.06976,"push.push_depth":0.1296,"push.push_duration":2.38268,"push.push_speed":0.07636},"optimized_scores":{"best_composite_score":0.01002,"best_fitness_score":0.42002,"best_task_score":0.25794},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":841.0,"contact_point_centroid":[0.50438,-0.01004,0.04349],"force_p95":27.1193,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.81378,"mean_force":5.18362,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50001,0.00184,0.02768]},{"body_a":"peg","body_b":"channel_base_body","contact_count":59.0,"contact_point_centroid":[0.50703,-0.10053,0.0603],"force_p95":46.49716,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.73185,"mean_force":34.54311,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50197,-0.05388,0.02931]},{"body_a":"attachment","body_b":"peg","contact_count":401.0,"contact_point_centroid":[0.50287,0.0614,0.04522],"force_p95":6.16772,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.53115,"mean_force":3.59589,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.498,0.07301,0.03328]},{"body_a":"peg","body_b":"channel_base_body","contact_count":576.0,"contact_point_centroid":[0.50635,-0.03982,0.00996],"force_p95":7.20867,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.46256,"mean_force":4.16181,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49987,0.00673,0.02757]},{"body_a":"peg","body_b":"channel_base_body","contact_count":395.0,"contact_point_centroid":[0.50776,0.03006,0.00991],"force_p95":5.26263,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.40282,"mean_force":3.22688,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.49766,0.07458,0.03412]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":538.0,"contact_point_centroid":[0.52503,-0.02823,0.02615],"force_p95":2.61613,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.52778,"mean_force":0.89142,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50008,0.0008,0.02774]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":395.0,"contact_point_centroid":[0.5252,0.04399,0.0349],"force_p95":4.35948,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.77639,"mean_force":2.14254,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.49812,0.07256,0.03307]},{"body_a":"peg","body_b":"channel_base_body","contact_count":410.0,"contact_point_centroid":[0.50581,0.05666,0.00934],"force_p95":0.60207,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.58537,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49792,0.14137,0.16512]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49955,0.19632,0.29142]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.50486,0.05624,0.00938],"force_p95":0.55394,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5546,"mean_force":0.54669,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49609,0.08821,0.04474]}],"total_contact_groups":10},"final_pose_error":0.03646,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50701,-0.08369,0.0353],"final_tcp_position":[0.5021,-0.05511,0.02921],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":55.81378,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":439.0,"n_steps_budget":600.0,"object_pos_end":[0.50614,0.05659,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.55896,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":447.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.49686,0.08911,0.0471],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03634,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50616,0.05663,0.03378],"object_pos_start":[0.50614,0.05659,0.03378],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13687,"object_z_max":0.03378,"peak_contact_force":0.55122,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":20.0,"raw_peak_contact_force":0.5546,"subtask_id":"approach","tcp_end":[0.4965,0.08745,0.04261],"tcp_start":[0.49686,0.08911,0.0471],"tcp_to_object_dist_end":0.03348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":466.0,"n_steps_budget":600.0,"object_pos_end":[0.50722,0.03393,0.03542],"object_pos_start":[0.50616,0.05663,0.03378],"object_to_goal_dist_end":0.11425,"object_to_goal_dist_start":0.13691,"object_z_max":0.03628,"peak_contact_force":2.86538,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1191.0,"raw_peak_contact_force":10.53115,"subtask_id":"contact","tcp_end":[0.50138,0.06352,0.02981],"tcp_start":[0.4965,0.08745,0.04261],"tcp_to_object_dist_end":0.03068,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":996.0,"n_steps_budget":1000.0,"object_pos_end":[0.50703,-0.08361,0.03535],"object_pos_start":[0.50722,0.03393,0.03542],"object_to_goal_dist_end":0.00917,"object_to_goal_dist_start":0.11425,"object_z_max":0.03581,"peak_contact_force":27.1193,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2014.0,"raw_peak_contact_force":55.81378,"subtask_id":"push","tcp_end":[0.5021,-0.05511,0.02921],"tcp_start":[0.50213,-0.05512,0.02925],"tcp_to_object_dist_end":0.02957,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67708,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_entry.entry_speed":0.86251,"approach_peg.approach_speed":0.17367,"contact_engage.contact_duration":0.94128,"contact_engage.contact_speed":0.07566,"push.push_depth":0.15027,"push.push_duration":3.28844,"push.push_speed":0.07994},"optimized_scores":{"best_composite_score":-0.05089,"best_fitness_score":0.35911,"best_task_score":0.18103},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":159.0,"contact_point_centroid":[0.50716,0.08499,0.00767],"force_p95":187.46894,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":191.02243,"mean_force":158.93833,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50673,0.09699,0.04854]},{"body_a":"attachment","body_b":"peg","contact_count":159.0,"contact_point_centroid":[0.50921,0.08642,0.05141],"force_p95":186.99233,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":190.50248,"mean_force":158.35193,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50673,0.09699,0.04854]},{"body_a":"peg","body_b":"channel_base_body","contact_count":416.0,"contact_point_centroid":[0.4954,0.08005,0.00932],"force_p95":162.69781,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":187.78873,"mean_force":11.98094,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49806,0.14094,0.16415]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.51047,0.08826,0.05534],"force_p95":187.11544,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":187.2052,"mean_force":169.48629,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49926,0.09251,0.0547]},{"body_a":"attachment","body_b":"peg","contact_count":106.0,"contact_point_centroid":[0.49627,0.08403,0.04433],"force_p95":40.94611,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.22238,"mean_force":10.97348,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.49837,0.09545,0.03652]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47306,0.07716,0.05514],"force_p95":46.53152,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.05468,"mean_force":39.27261,"phase_index":1.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50706,0.10169,0.04454]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":140.0,"contact_point_centroid":[0.47435,0.06796,0.03758],"force_p95":31.07298,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.92224,"mean_force":6.51163,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.49929,0.09653,0.0372]},{"body_a":"peg","body_b":"channel_base_body","contact_count":121.0,"contact_point_centroid":[0.49194,0.05653,0.00968],"force_p95":35.5134,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.92892,"mean_force":7.29382,"phase_index":2.0,"phase_name":"contact_engage","phase_type":"contact","tcp_position_centroid":[0.49891,0.09606,0.03693]},{"body_a":"attachment","body_b":"peg","contact_count":821.0,"contact_point_centroid":[0.49524,0.01,0.03783],"force_p95":11.6757,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.51046,"mean_force":4.71744,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48798,0.02,0.02837]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":665.0,"contact_point_centroid":[0.52524,-0.02131,0.0304],"force_p95":9.74842,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.56065,"mean_force":3.83806,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48795,0.00164,0.02862]},{"body_a":"peg","body_b":"channel_base_body","contact_count":605.0,"contact_point_centroid":[0.50426,-0.01428,0.00995],"force_p95":8.14593,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.36953,"mean_force":3.85088,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.488,0.02697,0.02828]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":32.0,"contact_point_centroid":[0.47491,0.05442,0.03205],"force_p95":2.76091,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.11991,"mean_force":1.05701,"phase_index":3.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48973,0.08437,0.02946]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_entry","phase_type":"approach","tcp_position_centroid":[0.49957,0.19656,0.29202]}],"total_contact_groups":13},"final_pose_error":0.04548,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50773,-0.06673,0.03728],"final_tcp_position":[0.48816,-0.04306,0.02955],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":191.02243,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":444.0,"n_steps_budget":600.0,"object_pos_end":[0.49565,0.07802,0.03213],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.15828,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":185.89195,"phase_name":"approach_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":479.0,"raw_peak_contact_force":187.78873,"tcp_end":[0.5022,0.09046,0.05077],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.02334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":159.0,"n_steps_budget":600.0,"object_pos_end":[0.49059,0.07768,0.03245],"object_pos_start":[0.49565,0.07802,0.03213],"object_to_goal_dist_end":0.15814,"object_to_goal_dist_start":0.15828,"object_z_max":0.03264,"peak_contact_force":54.35791,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":332.0,"raw_peak_contact_force":191.02243,"subtask_id":"approach","tcp_end":[0.50582,0.10204,0.043],"tcp_start":[0.5022,0.09046,0.05077],"tcp_to_object_dist_end":0.03061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":160.0,"n_steps_budget":600.0,"object_pos_end":[0.49274,0.05732,0.03527],"object_pos_start":[0.49059,0.07768,0.03245],"object_to_goal_dist_end":0.13759,"object_to_goal_dist_start":0.15814,"object_z_max":0.03556,"peak_contact_force":1.58488,"phase_name":"contact_engage","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":367.0,"raw_peak_contact_force":49.22238,"subtask_id":"contact","tcp_end":[0.49107,0.08738,0.03095],"tcp_start":[0.50582,0.10204,0.043],"tcp_to_object_dist_end":0.03041,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50773,-0.06673,0.03728],"object_pos_start":[0.49274,0.05732,0.03527],"object_to_goal_dist_end":0.01559,"object_to_goal_dist_start":0.13759,"object_z_max":0.03731,"peak_contact_force":14.88855,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2123.0,"raw_peak_contact_force":16.51046,"subtask_id":"push","tcp_end":[0.48816,-0.04306,0.02955],"tcp_start":[0.49107,0.08738,0.03095],"tcp_to_object_dist_end":0.03167,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```