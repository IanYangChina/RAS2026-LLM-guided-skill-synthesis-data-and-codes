## Search State

- **Seed**: 8
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5194 | 0.93 | ❌ rejected |
| 5 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5348 | 0.97 | ✅ accepted |
| 4 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5316 | 0.85 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 1 | 0.4142 | 0.29 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 1 | 0.4142 | 0.29 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.93). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.519) — your mutation base

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

- **Composite score**: 0.519
- **task_score** (E): 0.934
- **fitness_score**: 0.809  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_high | 1.00 | 1.00 | 0.0864 |
| descend_to_peg | 1.00 | 1.00 | 0.1963 |
| contact_1 | 1.00 | 1.00 | 0.0301 |
| push_along_channel | 1.00 | 1.00 | 0.1844 |
| retract_1 | 1.00 | 1.00 | 0.0802 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.135, 0.248) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.525 | 3.526 |
| descend_to_peg | approach | 1.00 / step_budget | (0.513, 0.135, 0.248)→(0.501, 0.121, 0.053) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.525 | 0.611 |
| contact_1 | contact | 1.00 / step_budget | (0.501, 0.121, 0.053)→(0.499, 0.101, 0.031) | (0.503, 0.080, 0.034)→(0.504, 0.071, 0.035) | 0.160→0.151 | 1.00 / 2.333 | 2.758 | 7.486 |
| push_along_channel | push | 1.00 / step_budget | (0.499, 0.101, 0.031)→(0.505, -0.083, 0.031) | (0.504, 0.071, 0.035)→(0.495, -0.127, 0.033) | 0.151→0.048 | 1.00 / 2.000 | 64.710 | 698.261 |
| retract_1 | retract | 1.00 / step_budget | (0.505, -0.083, 0.031)→(0.503, -0.083, 0.112) | (0.495, -0.127, 0.033)→(0.520, -0.178, 0.020) | 0.048→0.108 | 1.00 / 1.333 | 0.922 | 87.395 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.706
- phase_breakdown.approach_score: 0.509
- phase_breakdown.contact_score: 0.491
- phase_breakdown.push_score: 0.843

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.824
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.521
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.371


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36161,"average_solve_count":224.0,"average_success_count":224.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":8.34151,"push_along_channel.push_depth":0.21992,"push_along_channel.push_lateral_x":0.01155,"push_along_channel.push_speed":0.04349},"optimized_scores":{"best_composite_score":0.50339,"best_fitness_score":0.79339,"best_task_score":0.80135},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.53586,0.11998,0.0594],"force_p95":782.20418,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":800.60288,"mean_force":607.9704,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48213,0.14525,0.02536]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47494,0.11996,0.02857],"force_p95":196.3221,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":196.69688,"mean_force":168.13785,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48521,0.12561,0.02693]},{"body_a":"attachment","body_b":"peg","contact_count":768.0,"contact_point_centroid":[0.50262,0.00032,0.05436],"force_p95":172.7148,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":177.40324,"mean_force":112.82924,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49439,0.00867,0.02775]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.5065,-0.10343,0.05669],"force_p95":171.40823,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":172.8698,"mean_force":138.29181,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50358,-0.06421,0.02963]},{"body_a":"peg","body_b":"channel_base_body","contact_count":201.0,"contact_point_centroid":[0.49094,-0.10539,0.05717],"force_p95":164.60886,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":171.41963,"mean_force":67.91256,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50612,-0.07288,0.06386]},{"body_a":"attachment","body_b":"peg","contact_count":172.0,"contact_point_centroid":[0.5002,-0.08133,0.06308],"force_p95":127.60758,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.33934,"mean_force":71.08167,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50615,-0.07231,0.06183]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":708.0,"contact_point_centroid":[0.52684,-0.01389,0.05447],"force_p95":117.20463,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.06737,"mean_force":68.27804,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49414,0.00753,0.02762]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":152.0,"contact_point_centroid":[0.47446,-0.09505,0.05303],"force_p95":73.98503,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.0079,"mean_force":32.93144,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50599,-0.07349,0.05845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":466.0,"contact_point_centroid":[0.51084,0.02486,0.0097],"force_p95":61.22548,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.0122,"mean_force":42.47469,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48926,0.05671,0.02696]},{"body_a":"peg","body_b":"link7","contact_count":373.0,"contact_point_centroid":[0.52254,0.03776,0.06305],"force_p95":38.78592,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.55435,"mean_force":29.08691,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4897,0.04615,0.0269]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52504,-0.08151,0.03911],"force_p95":23.2211,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.35698,"mean_force":13.54651,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50658,-0.06739,0.07288]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":11.0,"contact_point_centroid":[0.47429,-0.10214,0.03858],"force_p95":16.26371,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.98076,"mean_force":8.71391,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50669,-0.07691,0.03075]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.50918,-0.08295,0.0088],"force_p95":11.81809,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.64136,"mean_force":3.86925,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50571,-0.07878,0.0835]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.49806,0.1052,0.00976],"force_p95":4.92014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.73604,"mean_force":2.49587,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4909,0.14759,0.03864]},{"body_a":"attachment","body_b":"peg","contact_count":191.0,"contact_point_centroid":[0.49484,0.13181,0.04792],"force_p95":4.73241,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.41841,"mean_force":3.45238,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49125,0.14373,0.03459]},{"body_a":"peg","body_b":"channel_base_body","contact_count":84.0,"contact_point_centroid":[0.49771,0.1192,0.00927],"force_p95":1.18561,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.63336,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49352,0.18346,0.2732]}],"total_contact_groups":18},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49559,-0.07289,0.0324],"final_tcp_position":[0.5051,-0.07814,0.11128],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":800.60288,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":109.0,"n_steps_budget":600.0,"object_pos_end":[0.49601,0.11901,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50659,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":108.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48922,0.17156,0.25482],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.119,0.03397],"object_pos_start":[0.49601,0.11901,0.03384],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19914,"object_z_max":0.03416,"peak_contact_force":0.50928,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":386.0,"raw_peak_contact_force":0.626,"subtask_id":"approach","tcp_end":[0.49224,0.15942,0.05347],"tcp_start":[0.48922,0.17156,0.25482],"tcp_to_object_dist_end":0.04504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":600.0,"object_pos_end":[0.49763,0.11037,0.03525],"object_pos_start":[0.49602,0.119,0.03397],"object_to_goal_dist_end":0.19044,"object_to_goal_dist_start":0.19913,"object_z_max":0.03541,"peak_contact_force":2.89886,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":510.0,"raw_peak_contact_force":6.73604,"subtask_id":"contact","tcp_end":[0.49189,0.13994,0.03091],"tcp_start":[0.49224,0.15942,0.05347],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":856.0,"n_steps_budget":1000.0,"object_pos_end":[0.49221,-0.10607,0.03592],"object_pos_start":[0.49763,0.11037,0.03525],"object_to_goal_dist_end":0.02752,"object_to_goal_dist_start":0.19044,"object_z_max":0.03814,"peak_contact_force":2.29497,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2622.0,"raw_peak_contact_force":800.60288,"subtask_id":"push","tcp_end":[0.50698,-0.08002,0.03105],"tcp_start":[0.49189,0.13994,0.03091],"tcp_to_object_dist_end":0.03034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":240.0,"n_steps_budget":630.0,"object_pos_end":[0.49559,-0.07289,0.0324],"object_pos_start":[0.49221,-0.10607,0.03592],"object_to_goal_dist_end":0.0113,"object_to_goal_dist_start":0.02752,"object_z_max":0.06602,"peak_contact_force":1.62539,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":554.0,"raw_peak_contact_force":171.41963,"tcp_end":[0.5051,-0.07814,0.11128],"tcp_start":[0.50698,-0.08002,0.03105],"tcp_to_object_dist_end":0.07962,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36797,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":16.93304,"push_along_channel.push_depth":0.17616,"push_along_channel.push_lateral_x":0.00016,"push_along_channel.push_speed":0.0149},"optimized_scores":{"best_composite_score":0.52142,"best_fitness_score":0.81142,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.53659,0.0765,0.0595],"force_p95":636.4056,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":652.95998,"mean_force":427.66987,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49538,0.08565,0.02556]},{"body_a":"peg","body_b":"channel_base_body","contact_count":221.0,"contact_point_centroid":[0.50193,-0.10805,0.05007],"force_p95":240.69743,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":256.58354,"mean_force":101.29394,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50402,-0.07426,0.02985]},{"body_a":"attachment","body_b":"peg","contact_count":399.0,"contact_point_centroid":[0.50477,-0.03001,0.05053],"force_p95":231.13773,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":250.9301,"mean_force":69.64098,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5008,-0.01947,0.02839]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":39.0,"contact_point_centroid":[0.51081,-0.10076,0.06499],"force_p95":211.66596,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":214.19064,"mean_force":189.328,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50641,-0.08903,0.03157]},{"body_a":"peg","body_b":"channel_base_body","contact_count":190.0,"contact_point_centroid":[0.50794,-0.00517,0.00974],"force_p95":68.24841,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.34596,"mean_force":13.98711,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49837,0.02996,0.02727]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.51062,-0.10014,0.065],"force_p95":76.5135,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.32497,"mean_force":40.89058,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50618,-0.08773,0.03172]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":220.0,"contact_point_centroid":[0.52533,-0.00585,0.04391],"force_p95":74.65942,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.37429,"mean_force":22.82374,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4984,0.02375,0.0273]},{"body_a":"peg","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.52199,0.05116,0.06105],"force_p95":47.93949,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.32618,"mean_force":19.09426,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49569,0.07438,0.02545]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":51.0,"contact_point_centroid":[0.47435,-0.10418,0.02422],"force_p95":26.02742,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.09959,"mean_force":8.11406,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50521,-0.08072,0.03049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.50697,0.05008,0.0097],"force_p95":4.84682,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.26235,"mean_force":2.41142,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50195,0.09242,0.0386]},{"body_a":"attachment","body_b":"peg","contact_count":178.0,"contact_point_centroid":[0.50506,0.07614,0.04708],"force_p95":4.80396,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.935,"mean_force":3.59059,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50184,0.08811,0.03422]},{"body_a":"peg","body_b":"channel_base_body","contact_count":183.0,"contact_point_centroid":[0.50525,0.06282,0.0093],"force_p95":0.79803,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.62046,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51165,0.15603,0.26879]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50082,0.19534,0.2964]},{"body_a":"peg","body_b":"world","contact_count":222.0,"contact_point_centroid":[0.50255,-0.22184,-0.0018],"force_p95":1.32613,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.84542,"mean_force":0.63487,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50427,-0.08745,0.07116]},{"body_a":"peg","body_b":"world","contact_count":9.0,"contact_point_centroid":[0.48709,-0.14402,-0.00138],"force_p95":2.15345,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.27223,"mean_force":1.26275,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50637,-0.0882,0.03157]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52503,0.05541,0.02687],"force_p95":1.45933,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5136,"mean_force":0.91499,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50201,0.08496,0.03123]}],"total_contact_groups":17},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.52594,-0.2646,0.01407],"final_tcp_position":[0.50412,-0.08772,0.11171],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":652.95998,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":211.0,"n_steps_budget":750.0,"object_pos_end":[0.50594,0.063,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54212,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":217.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.52217,0.12037,0.24581],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06303,0.0338],"object_pos_start":[0.50594,0.063,0.0338],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":0.55057,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":363.0,"raw_peak_contact_force":0.55664,"subtask_id":"approach","tcp_end":[0.50472,0.10434,0.05347],"tcp_start":[0.52217,0.12037,0.24581],"tcp_to_object_dist_end":0.04577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":600.0,"object_pos_end":[0.50699,0.05477,0.03528],"object_pos_start":[0.50602,0.06303,0.0338],"object_to_goal_dist_end":0.13503,"object_to_goal_dist_start":0.14329,"object_z_max":0.03537,"peak_contact_force":2.23578,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":524.0,"raw_peak_contact_force":9.26235,"subtask_id":"contact","tcp_end":[0.50202,0.08446,0.03077],"tcp_start":[0.50472,0.10434,0.05347],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.49354,-0.16123,0.02245],"object_pos_start":[0.50699,0.05477,0.03528],"object_to_goal_dist_end":0.08336,"object_to_goal_dist_start":0.13503,"object_z_max":0.04133,"peak_contact_force":191.09768,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1214.0,"raw_peak_contact_force":652.95998,"subtask_id":"push","tcp_end":[0.50635,-0.08797,0.03158],"tcp_start":[0.50202,0.08446,0.03077],"tcp_to_object_dist_end":0.07493,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":230.0,"n_steps_budget":660.0,"object_pos_end":[0.52594,-0.2646,0.01407],"object_pos_start":[0.49354,-0.16123,0.02245],"object_to_goal_dist_end":0.18821,"object_to_goal_dist_start":0.08336,"object_z_max":0.02935,"peak_contact_force":0.53719,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":229.0,"raw_peak_contact_force":87.32497,"tcp_end":[0.50412,-0.08772,0.11171],"tcp_start":[0.50635,-0.08797,0.03158],"tcp_to_object_dist_end":0.20322,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6686,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":7.42956,"push_along_channel.push_depth":0.15994,"push_along_channel.push_lateral_x":-0.0045,"push_along_channel.push_speed":0.06404},"optimized_scores":{"best_composite_score":0.5335,"best_fitness_score":0.8235,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":55.0,"contact_point_centroid":[0.53836,0.06792,0.05954],"force_p95":636.85885,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":641.22042,"mean_force":429.96679,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49533,0.07827,0.02565]},{"body_a":"attachment","body_b":"peg","contact_count":210.0,"contact_point_centroid":[0.50124,-0.01195,0.04266],"force_p95":122.75328,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":162.18686,"mean_force":33.87929,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49799,-0.00023,0.02834]},{"body_a":"peg","body_b":"channel_base_body","contact_count":67.0,"contact_point_centroid":[0.501,-0.10721,0.03191],"force_p95":151.77422,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":162.18044,"mean_force":58.30647,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50032,-0.06739,0.03071]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":83.0,"contact_point_centroid":[0.52536,0.03673,0.05104],"force_p95":70.20708,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.0714,"mean_force":31.0236,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4959,0.06807,0.02646]},{"body_a":"peg","body_b":"channel_base_body","contact_count":169.0,"contact_point_centroid":[0.50584,0.00173,0.00964],"force_p95":56.4329,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.38622,"mean_force":9.19092,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49712,0.03845,0.02715]},{"body_a":"peg","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.51853,0.01001,0.06341],"force_p95":38.48431,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.68888,"mean_force":12.59721,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49696,0.0357,0.02685]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47483,-0.09182,0.05922],"force_p95":7.80127,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.88007,"mean_force":3.20823,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50004,-0.06229,0.03032]},{"body_a":"attachment","body_b":"peg","contact_count":146.0,"contact_point_centroid":[0.50534,0.06945,0.04659],"force_p95":6.0052,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.46095,"mean_force":4.06073,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50212,0.08142,0.03385]},{"body_a":"peg","body_b":"channel_base_body","contact_count":292.0,"contact_point_centroid":[0.50664,0.04426,0.00969],"force_p95":5.2799,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.3841,"mean_force":2.25508,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50242,0.08629,0.03881]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50547,0.05653,0.00931],"force_p95":0.75767,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.62609,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51493,0.15248,0.26826]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":127.0,"contact_point_centroid":[0.5251,0.05151,0.03147],"force_p95":2.53861,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.99659,"mean_force":1.40552,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50212,0.08108,0.03351]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.5012,0.19476,0.29613]},{"body_a":"peg","body_b":"world","contact_count":182.0,"contact_point_centroid":[0.51507,-0.18685,-0.00183],"force_p95":1.55447,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.44009,"mean_force":0.68513,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49884,-0.08184,0.07827]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.48983,-0.11997,0.00988],"force_p95":2.9856,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.18408,"mean_force":1.4669,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49975,-0.08284,0.03767]},{"body_a":"peg","body_b":"channel_base_body","contact_count":30.0,"contact_point_centroid":[0.50026,-0.1139,0.02442],"force_p95":1.23553,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09635,"mean_force":0.30754,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5001,-0.08286,0.03541]},{"body_a":"peg","body_b":"channel_base_body","contact_count":360.0,"contact_point_centroid":[0.50603,0.05663,0.00938],"force_p95":0.60016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64921,"mean_force":0.54602,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.51665,0.10577,0.14992]}],"total_contact_groups":16},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.53746,-0.19597,0.01411],"final_tcp_position":[0.49877,-0.08183,0.11194],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":641.22042,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":229.0,"n_steps_budget":780.0,"object_pos_end":[0.50613,0.0566,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.52504,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":237.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.52825,0.11375,0.24485],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.05662,0.03377],"object_pos_start":[0.50613,0.0566,0.03377],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03383,"peak_contact_force":0.51533,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":360.0,"raw_peak_contact_force":0.64921,"subtask_id":"approach","tcp_end":[0.50559,0.09796,0.05344],"tcp_start":[0.52825,0.11375,0.24485],"tcp_to_object_dist_end":0.04579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":302.0,"n_steps_budget":600.0,"object_pos_end":[0.50706,0.04848,0.03534],"object_pos_start":[0.50614,0.05662,0.03377],"object_to_goal_dist_end":0.12876,"object_to_goal_dist_start":0.1369,"object_z_max":0.03544,"peak_contact_force":3.13935,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":565.0,"raw_peak_contact_force":6.46095,"subtask_id":"contact","tcp_end":[0.50218,0.07816,0.03076],"tcp_start":[0.50559,0.09796,0.05344],"tcp_to_object_dist_end":0.03043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.49836,-0.11261,0.04209],"object_pos_start":[0.50706,0.04848,0.03534],"object_to_goal_dist_end":0.03272,"object_to_goal_dist_start":0.12876,"object_z_max":0.0427,"peak_contact_force":0.73777,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":649.0,"raw_peak_contact_force":641.22042,"subtask_id":"push","tcp_end":[0.50109,-0.08202,0.03177],"tcp_start":[0.50218,0.07816,0.03076],"tcp_to_object_dist_end":0.0324,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":228.0,"n_steps_budget":630.0,"object_pos_end":[0.53746,-0.19597,0.01411],"object_pos_start":[0.49836,-0.11261,0.04209],"object_to_goal_dist_end":0.12459,"object_to_goal_dist_start":0.03272,"object_z_max":0.04209,"peak_contact_force":0.6024,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":218.0,"raw_peak_contact_force":3.44009,"tcp_end":[0.49877,-0.08183,0.11194],"tcp_start":[0.50109,-0.08202,0.03177],"tcp_to_object_dist_end":0.15523,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```