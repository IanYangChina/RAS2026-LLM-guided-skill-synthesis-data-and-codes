## Search State

- **Seed**: 8
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.4428 | 0.77 | ❌ rejected |
| 6 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5194 | 0.93 | ❌ rejected |
| 5 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5348 | 0.97 | ✅ accepted |
| 4 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5316 | 0.85 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 1 | 0.4142 | 0.29 | ❌ rejected |

**Proposal policy**: task_score is 0.77 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`
- Frozen object start: [0.48615778212844485, 0.11898214746703403, 0.04]
- Frozen task target: [0.48615778212844485, -0.04101785253296597, 0.04]
- Goal object position: (0.48615778212844485, -0.04101785253296597, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48615778212844485, 0.11898214746703403, 0.04)
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
  frozen_object_start: [0.4862, 0.119, 0.04]
  frozen_task_target: [0.4862, -0.041, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48615778212844485, 0.11898214746703403, 0.04]}
  frozen_targets: {'channel_exit': [0.48615778212844485, -0.04101785253296597, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e

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

## Current Skill (Q=0.443) — your mutation base

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
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  guards:
  - id: wall_contact_high
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - -0.02
    - 0.0
    - 0.0
- id: descend_to_peg
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
  guards:
  - id: wall_contact_descend
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - -0.02
    - 0.0
    - 0.0
  subtask_id: approach
- id: contact_1
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
  subtask_id: contact
- id: push_along_channel
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
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.12
      - 0.22
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_lateral_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
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
- id: retract_1
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=wall_contact_high, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[-0.02, 0.0, 0.0]
- **descend_to_peg** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.04, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
  - guards:
    - id=wall_contact_descend, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[-0.02, 0.0, 0.0]
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.02, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
- **push_along_channel** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_lateral_x: status=consumed; consumers=target.offset.x (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.443
- **task_score** (E): 0.772
- **fitness_score**: 0.711  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.022
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.0864 |
| descend_to_peg | 1.00 | 1.00 | 0.1963 |
| contact_1 | 1.00 | 1.00 | 0.0301 |
| push_along_channel | 0.67 | 1.00 | 0.1782 |
| retract_1 | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.135, 0.248) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.525 | 3.526 |
| descend_to_peg | approach | 1.00 / step_budget | (0.513, 0.135, 0.248)→(0.501, 0.121, 0.053) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.525 | 0.611 |
| contact_1 | contact | 1.00 / step_budget | (0.501, 0.121, 0.053)→(0.499, 0.101, 0.031) | (0.503, 0.080, 0.034)→(0.504, 0.071, 0.035) | 0.160→0.151 | 1.00 / 2.333 | 2.758 | 7.486 |
| push_along_channel | push | 0.67 / step_budget | (0.499, 0.101, 0.031)→(0.500, -0.077, 0.030) | (0.504, 0.071, 0.035)→(0.505, -0.150, 0.031) | 0.151→0.088 | 1.00 / 2.667 | 126.239 | 698.992 |
| retract_1 | retract | 1.00 / step_budget | (0.500, -0.077, 0.030)→(0.497, -0.077, 0.110) | (0.505, -0.150, 0.031)→(0.513, -0.233, 0.021) | 0.088→0.162 | 1.00 / 1.333 | 0.627 | 224.148 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.968
- phase_score: 0.648
- phase_breakdown.approach_score: 0.509
- phase_breakdown.contact_score: 0.492
- phase_breakdown.push_score: 0.746

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.776
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.968
- **Median Q (composite search score)**: 0.484
- **K-run variance**: 0.0121
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.277


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a8ce855c7f52ba2d198de8387bdd2f3b869655c206850d620daaec6ac6f298cd`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `79b30dd7102e96fb2fa0880d3932c959e04a6f943c7e87b878f77a0e54f87a94`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40299,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":8.61081,"push_along_channel.push_depth":0.19787,"push_along_channel.push_lateral_x":-0.00228,"push_along_channel.push_speed":0.04928},"optimized_scores":{"best_composite_score":0.48387,"best_fitness_score":0.77387,"best_task_score":0.93854},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.53546,0.11998,0.0594],"force_p95":773.53225,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":789.79332,"mean_force":600.25053,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48183,0.14504,0.02537]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":121.0,"contact_point_centroid":[0.47489,-0.05626,0.04198],"force_p95":529.59892,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":575.5468,"mean_force":405.63267,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48668,-0.05619,0.04042]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":128.0,"contact_point_centroid":[0.47497,0.05572,0.02985],"force_p95":203.49308,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":224.31204,"mean_force":118.83911,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48616,0.05766,0.02835]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":509.0,"contact_point_centroid":[0.52704,0.01041,0.05125],"force_p95":131.94757,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":179.53413,"mean_force":83.64348,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48711,0.0273,0.0288]},{"body_a":"attachment","body_b":"peg","contact_count":175.0,"contact_point_centroid":[0.49785,-0.0598,0.05425],"force_p95":157.6151,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":175.99961,"mean_force":71.15828,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48645,-0.05618,0.04587]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":238.0,"contact_point_centroid":[0.52773,-0.06768,0.05361],"force_p95":152.86179,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":172.72154,"mean_force":51.5508,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4862,-0.0563,0.05334]},{"body_a":"attachment","body_b":"peg","contact_count":538.0,"contact_point_centroid":[0.49783,0.02644,0.05022],"force_p95":144.76284,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":166.16407,"mean_force":87.33315,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48687,0.03305,0.02872]},{"body_a":"peg","body_b":"channel_base_body","contact_count":91.0,"contact_point_centroid":[0.51,-0.06021,0.00947],"force_p95":37.56353,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":123.22338,"mean_force":18.41284,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48627,-0.05796,0.05596]},{"body_a":"peg","body_b":"channel_base_body","contact_count":430.0,"contact_point_centroid":[0.51037,0.01592,0.00955],"force_p95":101.34288,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.0001,"mean_force":49.36653,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48626,0.04133,0.02839]},{"body_a":"peg","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.51794,-0.05472,0.06927],"force_p95":48.56877,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.59029,"mean_force":24.2344,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4867,-0.05927,0.03209]},{"body_a":"peg","body_b":"link7","contact_count":316.0,"contact_point_centroid":[0.51833,0.01101,0.06513],"force_p95":85.66034,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.93511,"mean_force":44.48771,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48657,0.01627,0.0285]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.49806,0.1052,0.00976],"force_p95":4.92014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.73604,"mean_force":2.49587,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4909,0.14759,0.03864]},{"body_a":"attachment","body_b":"peg","contact_count":191.0,"contact_point_centroid":[0.49484,0.13181,0.04792],"force_p95":4.73241,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.41841,"mean_force":3.45238,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49125,0.14373,0.03459]},{"body_a":"peg","body_b":"channel_base_body","contact_count":84.0,"contact_point_centroid":[0.49771,0.1192,0.00927],"force_p95":1.18561,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.63336,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49352,0.18346,0.2732]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":60.0,"contact_point_centroid":[0.47461,-0.06758,0.03577],"force_p95":1.72101,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.11869,"mean_force":0.87507,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48505,-0.05758,0.08445]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49907,0.19798,0.29708]}],"total_contact_groups":17},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49243,-0.07185,0.03355],"final_tcp_position":[0.48528,-0.05883,0.10977],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":789.79332,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":109.0,"n_steps_budget":600.0,"object_pos_end":[0.49601,0.11901,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50659,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":108.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48922,0.17156,0.25482],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.119,0.03397],"object_pos_start":[0.49601,0.11901,0.03384],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19914,"object_z_max":0.03416,"peak_contact_force":0.50928,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":386.0,"raw_peak_contact_force":0.626,"subtask_id":"approach","tcp_end":[0.49224,0.15942,0.05347],"tcp_start":[0.48922,0.17156,0.25482],"tcp_to_object_dist_end":0.04504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":600.0,"object_pos_end":[0.49763,0.11037,0.03525],"object_pos_start":[0.49602,0.119,0.03397],"object_to_goal_dist_end":0.19044,"object_to_goal_dist_start":0.19913,"object_z_max":0.03541,"peak_contact_force":2.89886,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":510.0,"raw_peak_contact_force":6.73604,"subtask_id":"contact","tcp_end":[0.49189,0.13994,0.03091],"tcp_start":[0.49224,0.15942,0.05347],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":612.0,"n_steps_budget":1000.0,"object_pos_end":[0.51421,-0.05631,0.03834],"object_pos_start":[0.49763,0.11037,0.03525],"object_to_goal_dist_end":0.02767,"object_to_goal_dist_start":0.19044,"object_z_max":0.03954,"peak_contact_force":119.36388,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1957.0,"raw_peak_contact_force":789.79332,"subtask_id":"push","tcp_end":[0.48746,-0.05926,0.02962],"tcp_start":[0.49189,0.13994,0.03091],"tcp_to_object_dist_end":0.02829,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":294.0,"n_steps_budget":630.0,"object_pos_end":[0.49243,-0.07185,0.03355],"object_pos_start":[0.51421,-0.05631,0.03834],"object_to_goal_dist_end":0.01286,"object_to_goal_dist_start":0.02767,"object_z_max":0.04903,"peak_contact_force":0.74073,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":723.0,"raw_peak_contact_force":575.5468,"tcp_end":[0.48528,-0.05883,0.10977],"tcp_start":[0.48746,-0.05926,0.02962],"tcp_to_object_dist_end":0.07766,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `0a7722137b05abd45e72adac5a0a8f18d70c24ddc36cf4c70c52ed7e5618005d`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67052,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":14.37101,"push_along_channel.push_depth":0.16889,"push_along_channel.push_lateral_x":0.00198,"push_along_channel.push_speed":0.06479},"optimized_scores":{"best_composite_score":0.29213,"best_fitness_score":0.58213,"best_task_score":0.40926},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":53.0,"contact_point_centroid":[0.53737,0.07527,0.05954],"force_p95":647.29381,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":658.43049,"mean_force":418.66572,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49535,0.08517,0.02563]},{"body_a":"attachment","body_b":"peg","contact_count":286.0,"contact_point_centroid":[0.50408,-0.01148,0.04475],"force_p95":118.90601,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":196.93199,"mean_force":39.4293,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50032,0.00014,0.02795]},{"body_a":"peg","body_b":"channel_base_body","contact_count":83.0,"contact_point_centroid":[0.50309,-0.10695,0.04151],"force_p95":169.72914,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.2066,"mean_force":64.28494,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50434,-0.06843,0.02964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":166.0,"contact_point_centroid":[0.50791,0.01153,0.00974],"force_p95":60.96142,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.91969,"mean_force":13.32375,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49778,0.04771,0.02684]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":181.0,"contact_point_centroid":[0.5254,0.00249,0.04936],"force_p95":65.77838,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.55371,"mean_force":28.6204,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4983,0.03265,0.02705]},{"body_a":"peg","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.52166,0.06168,0.06025],"force_p95":54.35093,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.09267,"mean_force":22.21422,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49547,0.08517,0.02511]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47487,-0.10673,0.05855],"force_p95":12.34751,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.39863,"mean_force":6.92148,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50512,-0.07799,0.03018]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.50697,0.05008,0.0097],"force_p95":4.84682,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.26235,"mean_force":2.41142,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50195,0.09242,0.0386]},{"body_a":"attachment","body_b":"peg","contact_count":178.0,"contact_point_centroid":[0.50506,0.07614,0.04708],"force_p95":4.80396,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.935,"mean_force":3.59059,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50184,0.08811,0.03422]},{"body_a":"peg","body_b":"channel_base_body","contact_count":183.0,"contact_point_centroid":[0.50525,0.06282,0.0093],"force_p95":0.79803,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.62046,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51165,0.15603,0.26879]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.48542,-0.11999,0.00992],"force_p95":3.58332,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.71303,"mean_force":2.50453,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50497,-0.0861,0.03447]},{"body_a":"peg","body_b":"world","contact_count":187.0,"contact_point_centroid":[0.50225,-0.18308,-0.00164],"force_p95":1.56757,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.45249,"mean_force":0.67277,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50385,-0.08481,0.07682]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50082,0.19534,0.2964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.5004,-0.11441,0.01316],"force_p95":1.91991,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.67556,"mean_force":0.43003,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50525,-0.08596,0.0336]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52503,0.05541,0.02687],"force_p95":1.45933,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5136,"mean_force":0.91499,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50201,0.08496,0.03123]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.50591,0.06309,0.00938],"force_p95":0.55253,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55664,"mean_force":0.54658,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.51309,0.11227,0.15038]}],"total_contact_groups":16},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50675,-0.18977,0.01405],"final_tcp_position":[0.50378,-0.08475,0.11144],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":658.43049,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":211.0,"n_steps_budget":750.0,"object_pos_end":[0.50594,0.063,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54212,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":217.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.52217,0.12037,0.24581],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06303,0.0338],"object_pos_start":[0.50594,0.063,0.0338],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":0.55057,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":363.0,"raw_peak_contact_force":0.55664,"subtask_id":"approach","tcp_end":[0.50472,0.10434,0.05347],"tcp_start":[0.52217,0.12037,0.24581],"tcp_to_object_dist_end":0.04577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":600.0,"object_pos_end":[0.50699,0.05477,0.03528],"object_pos_start":[0.50602,0.06303,0.0338],"object_to_goal_dist_end":0.13503,"object_to_goal_dist_start":0.14329,"object_z_max":0.03537,"peak_contact_force":2.23578,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":524.0,"raw_peak_contact_force":9.26235,"subtask_id":"contact","tcp_end":[0.50202,0.08446,0.03077],"tcp_start":[0.50472,0.10434,0.05347],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.49852,-0.11574,0.04004],"object_pos_start":[0.50699,0.05477,0.03528],"object_to_goal_dist_end":0.03577,"object_to_goal_dist_start":0.13503,"object_z_max":0.04042,"peak_contact_force":0.21001,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":798.0,"raw_peak_contact_force":658.43049,"subtask_id":"push","tcp_end":[0.50612,-0.08495,0.03098],"tcp_start":[0.50202,0.08446,0.03077],"tcp_to_object_dist_end":0.03298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":230.0,"n_steps_budget":630.0,"object_pos_end":[0.50675,-0.18977,0.01405],"object_pos_start":[0.49852,-0.11574,0.04004],"object_to_goal_dist_end":0.113,"object_to_goal_dist_start":0.03577,"object_z_max":0.04004,"peak_contact_force":0.67448,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":215.0,"raw_peak_contact_force":3.71303,"tcp_end":[0.50378,-0.08475,0.11144],"tcp_start":[0.50612,-0.08495,0.03098],"tcp_to_object_dist_end":0.14326,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `bf9c239495ea25cc1b534d0795871edaef0fee72244885088104a44eb548c1a2`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84146,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":7.22796,"push_along_channel.push_depth":0.21764,"push_along_channel.push_lateral_x":-0.00508,"push_along_channel.push_speed":0.09698},"optimized_scores":{"best_composite_score":0.55254,"best_fitness_score":0.77587,"best_task_score":0.96774},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":54.0,"contact_point_centroid":[0.5385,0.06747,0.05953],"force_p95":635.85513,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":648.75301,"mean_force":439.22452,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49531,0.07753,0.02563]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.51003,-0.10035,0.06499],"force_p95":281.51631,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":405.44695,"mean_force":249.85734,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50498,-0.0882,0.02951]},{"body_a":"channel_base_body","body_b":"link7","contact_count":85.0,"contact_point_centroid":[0.53864,-0.1,0.06496],"force_p95":213.50808,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":347.81563,"mean_force":166.58083,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50552,-0.08766,0.02928]},{"body_a":"peg","body_b":"channel_base_body","contact_count":344.0,"contact_point_centroid":[0.50356,-0.10541,0.05363],"force_p95":209.45262,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":221.82521,"mean_force":142.13343,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50104,-0.0689,0.02884]},{"body_a":"attachment","body_b":"peg","contact_count":500.0,"contact_point_centroid":[0.50354,-0.04715,0.05299],"force_p95":203.78133,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":218.08275,"mean_force":105.42842,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49954,-0.03696,0.02826]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":173.0,"contact_point_centroid":[0.52532,-0.02918,0.05012],"force_p95":70.57144,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":98.78434,"mean_force":20.12077,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49982,-0.00199,0.02777]},{"body_a":"channel_base_body","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53869,-0.1,0.06497],"force_p95":91.38113,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.18549,"mean_force":59.62694,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50555,-0.08753,0.02937]},{"body_a":"peg","body_b":"channel_base_body","contact_count":272.0,"contact_point_centroid":[0.50343,-0.04165,0.00973],"force_p95":49.85204,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.96117,"mean_force":13.28896,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49791,-0.00556,0.02757]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.51076,-0.10005,0.065],"force_p95":59.15154,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.67977,"mean_force":27.53519,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5055,-0.0875,0.02944]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.47429,-0.11899,0.02946],"force_p95":42.55217,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.53085,"mean_force":6.12542,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50427,-0.09095,0.02985]},{"body_a":"peg","body_b":"link7","contact_count":47.0,"contact_point_centroid":[0.51939,0.0208,0.06252],"force_p95":48.82887,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.758,"mean_force":12.94853,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49696,0.04586,0.02619]},{"body_a":"peg","body_b":"world","contact_count":172.0,"contact_point_centroid":[0.49074,-0.21648,-0.00174],"force_p95":1.58762,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.42566,"mean_force":0.71586,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50509,-0.08787,0.02945]},{"body_a":"attachment","body_b":"peg","contact_count":146.0,"contact_point_centroid":[0.50534,0.06945,0.04659],"force_p95":6.0052,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.46095,"mean_force":4.06073,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50212,0.08142,0.03385]},{"body_a":"peg","body_b":"channel_base_body","contact_count":292.0,"contact_point_centroid":[0.50664,0.04426,0.00969],"force_p95":5.2799,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.3841,"mean_force":2.25508,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50242,0.08629,0.03881]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50547,0.05653,0.00931],"force_p95":0.75767,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.62609,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51493,0.15248,0.26826]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":127.0,"contact_point_centroid":[0.5251,0.05151,0.03147],"force_p95":2.53861,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.99659,"mean_force":1.40552,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50212,0.08108,0.03351]}],"total_contact_groups":19},"final_pose_error":0.01969,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.54126,-0.43806,0.01404],"final_tcp_position":[0.50321,-0.08733,0.10982],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":648.75301,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":229.0,"n_steps_budget":780.0,"object_pos_end":[0.50613,0.0566,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.52504,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":237.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.52825,0.11375,0.24485],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.05662,0.03377],"object_pos_start":[0.50613,0.0566,0.03377],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03383,"peak_contact_force":0.51533,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":360.0,"raw_peak_contact_force":0.64921,"subtask_id":"approach","tcp_end":[0.50559,0.09796,0.05344],"tcp_start":[0.52825,0.11375,0.24485],"tcp_to_object_dist_end":0.04579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":302.0,"n_steps_budget":600.0,"object_pos_end":[0.50706,0.04848,0.03534],"object_pos_start":[0.50614,0.05662,0.03377],"object_to_goal_dist_end":0.12876,"object_to_goal_dist_start":0.1369,"object_z_max":0.03544,"peak_contact_force":3.13935,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":565.0,"raw_peak_contact_force":6.46095,"subtask_id":"contact","tcp_end":[0.50218,0.07816,0.03076],"tcp_start":[0.50559,0.09796,0.05344],"tcp_to_object_dist_end":0.03043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":790.0,"n_steps_budget":1000.0,"object_pos_end":[0.50316,-0.2794,0.01408],"object_pos_start":[0.50706,0.04848,0.03534],"object_to_goal_dist_end":0.20111,"object_to_goal_dist_start":0.12876,"object_z_max":0.0415,"peak_contact_force":259.14255,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1867.0,"raw_peak_contact_force":648.75301,"subtask_id":"push","tcp_end":[0.50556,-0.08755,0.02937],"tcp_start":[0.50218,0.07816,0.03076],"tcp_to_object_dist_end":0.19248,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":229.0,"n_steps_budget":630.0,"object_pos_end":[0.54126,-0.43806,0.01404],"object_pos_start":[0.50316,-0.2794,0.01408],"object_to_goal_dist_end":0.36136,"object_to_goal_dist_start":0.20111,"object_z_max":0.01409,"peak_contact_force":0.46579,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":237.0,"raw_peak_contact_force":93.18549,"tcp_end":[0.50321,-0.08733,0.10982],"tcp_start":[0.50556,-0.08755,0.02937],"tcp_to_object_dist_end":0.36556,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```