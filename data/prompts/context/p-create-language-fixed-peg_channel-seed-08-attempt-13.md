## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5148 | 0.93 | ❌ rejected |
| 12 | approach → approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1213 | 0.08 | ❌ rejected |
| 11 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.4770 | 0.69 | ❌ rejected |
| 10 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.2244 | 0.02 | ❌ rejected |
| 9 | approach → approach → contact → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1166 | 0.44 | ❌ rejected |

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

## Current Skill (Q=0.515) — your mutation base

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

- **Composite score**: 0.515
- **task_score** (E): 0.929
- **fitness_score**: 0.805  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
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
| push_along_channel | 1.00 | 1.00 | 0.1813 |
| retract_1 | 1.00 | 1.00 | 0.0805 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_high | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.135, 0.248) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.525 | 3.526 |
| descend_to_peg | approach | 1.00 / step_budget | (0.513, 0.135, 0.248)→(0.501, 0.121, 0.053) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.525 | 0.611 |
| contact_1 | contact | 1.00 / step_budget | (0.501, 0.121, 0.053)→(0.499, 0.101, 0.031) | (0.503, 0.080, 0.034)→(0.504, 0.071, 0.035) | 0.160→0.151 | 1.00 / 2.333 | 2.758 | 7.486 |
| push_along_channel | push | 1.00 / step_budget | (0.499, 0.101, 0.031)→(0.505, -0.080, 0.031) | (0.504, 0.071, 0.035)→(0.498, -0.110, 0.040) | 0.151→0.031 | 1.00 / 1.667 | 38.444 | 197.029 |
| retract_1 | retract | 1.00 / step_budget | (0.505, -0.080, 0.031)→(0.502, -0.079, 0.111) | (0.498, -0.110, 0.040)→(0.523, -0.166, 0.031) | 0.031→0.099 | 1.00 / 1.333 | 1.001 | 93.428 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.708
- phase_breakdown.approach_score: 0.567
- phase_breakdown.contact_score: 0.558
- phase_breakdown.push_score: 0.805

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.825
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.512
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.342


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37824,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":8.77754,"push_along_channel.push_depth":0.21646,"push_along_channel.push_lateral_x":0.01432,"push_along_channel.push_speed":0.05929},"optimized_scores":{"best_composite_score":0.49766,"best_fitness_score":0.78766,"best_task_score":0.80731},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52512,-0.07449,0.05998],"force_p95":220.43438,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":220.66959,"mean_force":161.90714,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50823,-0.0743,0.03073]},{"body_a":"attachment","body_b":"peg","contact_count":340.0,"contact_point_centroid":[0.50221,0.01972,0.04337],"force_p95":102.35286,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.11632,"mean_force":25.25231,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4976,0.0309,0.02849]},{"body_a":"peg","body_b":"channel_base_body","contact_count":70.0,"contact_point_centroid":[0.50237,-0.10582,0.03366],"force_p95":149.09926,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.67118,"mean_force":70.13571,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50605,-0.06506,0.02971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":215.0,"contact_point_centroid":[0.49279,-0.10375,0.05476],"force_p95":128.39224,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":136.29244,"mean_force":55.48425,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.507,-0.07092,0.06602]},{"body_a":"attachment","body_b":"peg","contact_count":170.0,"contact_point_centroid":[0.50098,-0.07888,0.06044],"force_p95":104.09656,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":132.45512,"mean_force":65.2848,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50737,-0.07007,0.05902]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":203.0,"contact_point_centroid":[0.47439,-0.0888,0.05672],"force_p95":73.45648,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.70231,"mean_force":25.53897,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50675,-0.07142,0.0683]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":187.0,"contact_point_centroid":[0.52537,0.01773,0.03978],"force_p95":53.17315,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.12961,"mean_force":16.90555,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49585,0.04572,0.02787]},{"body_a":"peg","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.52168,0.06706,0.06318],"force_p95":37.46076,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.8966,"mean_force":14.18557,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49239,0.08459,0.02726]},{"body_a":"peg","body_b":"channel_base_body","contact_count":118.0,"contact_point_centroid":[0.50556,0.00116,0.00987],"force_p95":34.25202,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.45844,"mean_force":10.30958,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49662,0.04324,0.02847]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47487,-0.10106,0.05998],"force_p95":14.86859,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.35103,"mean_force":10.01278,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50831,-0.07388,0.03079]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.49806,0.1052,0.00976],"force_p95":4.92014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.73604,"mean_force":2.49587,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4909,0.14759,0.03864]},{"body_a":"attachment","body_b":"peg","contact_count":191.0,"contact_point_centroid":[0.49484,0.13181,0.04792],"force_p95":4.73241,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.41841,"mean_force":3.45238,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49125,0.14373,0.03459]},{"body_a":"peg","body_b":"channel_base_body","contact_count":84.0,"contact_point_centroid":[0.49771,0.1192,0.00927],"force_p95":1.18561,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.63336,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49352,0.18346,0.2732]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.52503,-0.08094,0.05509],"force_p95":1.48232,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.74259,"mean_force":1.15919,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50507,-0.07483,0.10454]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.49907,0.19798,0.29708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":386.0,"contact_point_centroid":[0.49605,0.11899,0.00943],"force_p95":0.5981,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.626,"mean_force":0.5416,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.4901,0.1653,0.15471]}],"total_contact_groups":16},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49544,-0.07963,0.063],"final_tcp_position":[0.50491,-0.07543,0.11062],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":220.66959,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":109.0,"n_steps_budget":600.0,"object_pos_end":[0.49601,0.11901,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50659,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":108.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48922,0.17156,0.25482],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22724,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.119,0.03397],"object_pos_start":[0.49601,0.11901,0.03384],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19914,"object_z_max":0.03416,"peak_contact_force":0.50928,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":386.0,"raw_peak_contact_force":0.626,"subtask_id":"approach","tcp_end":[0.49224,0.15942,0.05347],"tcp_start":[0.48922,0.17156,0.25482],"tcp_to_object_dist_end":0.04504,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":600.0,"object_pos_end":[0.49763,0.11037,0.03525],"object_pos_start":[0.49602,0.119,0.03397],"object_to_goal_dist_end":0.19044,"object_to_goal_dist_start":0.19913,"object_z_max":0.03541,"peak_contact_force":2.89886,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":510.0,"raw_peak_contact_force":6.73604,"subtask_id":"contact","tcp_end":[0.49189,0.13994,0.03091],"tcp_start":[0.49224,0.15942,0.05347],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.49462,-0.10356,0.03953],"object_pos_start":[0.49763,0.11037,0.03525],"object_to_goal_dist_end":0.02417,"object_to_goal_dist_start":0.19044,"object_z_max":0.03932,"peak_contact_force":111.23566,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":745.0,"raw_peak_contact_force":220.66959,"subtask_id":"push","tcp_end":[0.50757,-0.07696,0.03015],"tcp_start":[0.49189,0.13994,0.03091],"tcp_to_object_dist_end":0.03104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":248.0,"n_steps_budget":660.0,"object_pos_end":[0.49544,-0.07963,0.063],"object_pos_start":[0.49462,-0.10356,0.03953],"object_to_goal_dist_end":0.02345,"object_to_goal_dist_start":0.02417,"object_z_max":0.07256,"peak_contact_force":0.22884,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":622.0,"raw_peak_contact_force":136.29244,"tcp_end":[0.50491,-0.07543,0.11062],"tcp_start":[0.50757,-0.07696,0.03015],"tcp_to_object_dist_end":0.04873,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77707,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":11.53732,"push_along_channel.push_depth":0.1646,"push_along_channel.push_lateral_x":0.00105,"push_along_channel.push_speed":0.0846},"optimized_scores":{"best_composite_score":0.53471,"best_fitness_score":0.82471,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":78.0,"contact_point_centroid":[0.50185,-0.10664,0.03216],"force_p95":153.43248,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.89391,"mean_force":75.15363,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50462,-0.06531,0.0301]},{"body_a":"attachment","body_b":"peg","contact_count":193.0,"contact_point_centroid":[0.50322,-0.01294,0.03629],"force_p95":145.87654,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":157.65203,"mean_force":32.09224,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50251,-0.00139,0.02918]},{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.49911,-0.11229,0.02975],"force_p95":6.05452,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.69734,"mean_force":4.79273,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50541,-0.08058,0.03675]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50485,-0.09237,0.03195],"force_p95":77.21232,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.99579,"mean_force":33.25851,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50674,-0.08071,0.03173]},{"body_a":"peg","body_b":"channel_base_body","contact_count":107.0,"contact_point_centroid":[0.50075,-0.03377,0.00964],"force_p95":14.84448,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.02105,"mean_force":4.55999,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50204,0.00221,0.02885]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":33.0,"contact_point_centroid":[0.47448,-0.05442,0.04761],"force_p95":15.168,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.21318,"mean_force":3.25424,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50284,-0.02344,0.02902]},{"body_a":"peg","body_b":"channel_base_body","contact_count":319.0,"contact_point_centroid":[0.50697,0.05008,0.0097],"force_p95":4.84682,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.26235,"mean_force":2.41142,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50195,0.09242,0.0386]},{"body_a":"attachment","body_b":"peg","contact_count":178.0,"contact_point_centroid":[0.50506,0.07614,0.04708],"force_p95":4.80396,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.935,"mean_force":3.59059,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50184,0.08811,0.03422]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.52518,0.02426,0.03587],"force_p95":6.92662,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.25908,"mean_force":1.58208,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5013,0.05394,0.02921]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47486,-0.11694,0.05997],"force_p95":4.52682,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.07554,"mean_force":1.30732,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50537,-0.08069,0.0356]},{"body_a":"peg","body_b":"world","contact_count":194.0,"contact_point_centroid":[0.52218,-0.18415,-0.00041],"force_p95":1.43393,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.93158,"mean_force":0.56875,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50377,-0.0798,0.07772]},{"body_a":"peg","body_b":"channel_base_body","contact_count":183.0,"contact_point_centroid":[0.50525,0.06282,0.0093],"force_p95":0.79803,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.62046,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51165,0.15603,0.26879]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.50082,0.19534,0.2964]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":27.0,"contact_point_centroid":[0.52503,0.05541,0.02687],"force_p95":1.45933,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.5136,"mean_force":0.91499,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50201,0.08496,0.03123]},{"body_a":"peg","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.50897,-0.04048,0.06812],"force_p95":0.61338,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.61838,"mean_force":0.4758,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50208,-0.01153,0.02853]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.50591,0.06309,0.00938],"force_p95":0.55253,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55664,"mean_force":0.54658,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.51309,0.11227,0.15038]}],"total_contact_groups":16},"final_pose_error":0.01994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.53175,-0.22185,0.01662],"final_tcp_position":[0.50379,-0.07971,0.11194],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":157.89391,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":211.0,"n_steps_budget":750.0,"object_pos_end":[0.50594,0.063,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54212,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":217.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.52217,0.12037,0.24581],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06303,0.0338],"object_pos_start":[0.50594,0.063,0.0338],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":0.55057,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":363.0,"raw_peak_contact_force":0.55664,"subtask_id":"approach","tcp_end":[0.50472,0.10434,0.05347],"tcp_start":[0.52217,0.12037,0.24581],"tcp_to_object_dist_end":0.04577,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":322.0,"n_steps_budget":600.0,"object_pos_end":[0.50699,0.05477,0.03528],"object_pos_start":[0.50602,0.06303,0.0338],"object_to_goal_dist_end":0.13503,"object_to_goal_dist_start":0.14329,"object_z_max":0.03537,"peak_contact_force":2.23578,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":524.0,"raw_peak_contact_force":9.26235,"subtask_id":"contact","tcp_end":[0.50202,0.08446,0.03077],"tcp_start":[0.50472,0.10434,0.05347],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.49955,-0.10961,0.04252],"object_pos_start":[0.50699,0.05477,0.03528],"object_to_goal_dist_end":0.02972,"object_to_goal_dist_start":0.13503,"object_z_max":0.04243,"peak_contact_force":2.0831,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":441.0,"raw_peak_contact_force":157.89391,"subtask_id":"push","tcp_end":[0.50693,-0.08013,0.03162],"tcp_start":[0.50202,0.08446,0.03077],"tcp_to_object_dist_end":0.03229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":246.0,"n_steps_budget":630.0,"object_pos_end":[0.53175,-0.22185,0.01662],"object_pos_start":[0.49955,-0.10961,0.04252],"object_to_goal_dist_end":0.14723,"object_to_goal_dist_start":0.02972,"object_z_max":0.04293,"peak_contact_force":2.17266,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":253.0,"raw_peak_contact_force":78.69734,"tcp_end":[0.50379,-0.07971,0.11194],"tcp_start":[0.50693,-0.08013,0.03162],"tcp_to_object_dist_end":0.17342,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35349,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"contact_1.contact_force":13.29051,"push_along_channel.push_depth":0.16107,"push_along_channel.push_lateral_x":-0.00349,"push_along_channel.push_speed":0.03719},"optimized_scores":{"best_composite_score":0.51205,"best_fitness_score":0.80205,"best_task_score":0.97979},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":114.0,"contact_point_centroid":[0.50273,-0.10593,0.0477],"force_p95":173.02848,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":212.52305,"mean_force":83.63963,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50015,-0.06756,0.02884]},{"body_a":"attachment","body_b":"peg","contact_count":329.0,"contact_point_centroid":[0.50419,-0.02124,0.0493],"force_p95":156.45882,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":212.45771,"mean_force":38.88307,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49963,-0.0099,0.02838]},{"body_a":"channel_base_body","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.54528,-0.1,0.06498],"force_p95":154.47692,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.75,"mean_force":110.2713,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50038,-0.0719,0.02878]},{"body_a":"channel_base_body","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53947,-0.1,0.065],"force_p95":65.26293,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":65.29566,"mean_force":64.96836,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50141,-0.08396,0.02991]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":160.0,"contact_point_centroid":[0.52533,-0.00653,0.0399],"force_p95":46.99321,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.59423,"mean_force":15.6996,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49914,0.02279,0.02784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":117.0,"contact_point_centroid":[0.50714,-0.05932,0.00988],"force_p95":32.69029,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.37376,"mean_force":12.66494,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49972,-0.01942,0.02858]},{"body_a":"attachment","body_b":"peg","contact_count":146.0,"contact_point_centroid":[0.50534,0.06945,0.04659],"force_p95":6.0052,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.46095,"mean_force":4.06073,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50212,0.08142,0.03385]},{"body_a":"peg","body_b":"channel_base_body","contact_count":292.0,"contact_point_centroid":[0.50664,0.04426,0.00969],"force_p95":5.2799,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.3841,"mean_force":2.25508,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50242,0.08629,0.03881]},{"body_a":"peg","body_b":"world","contact_count":208.0,"contact_point_centroid":[0.51805,-0.18481,-0.00178],"force_p95":1.43701,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.14181,"mean_force":0.68624,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4984,-0.08322,0.07499]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50547,0.05653,0.00931],"force_p95":0.75767,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.62609,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51493,0.15248,0.26826]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":127.0,"contact_point_centroid":[0.5251,0.05151,0.03147],"force_p95":2.53861,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.99659,"mean_force":1.40552,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50212,0.08108,0.03351]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.5012,0.19476,0.29613]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50383,-0.11505,0.02685],"force_p95":0.35695,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.27814,"mean_force":0.17109,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50045,-0.0844,0.03326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":360.0,"contact_point_centroid":[0.50603,0.05663,0.00938],"force_p95":0.60016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64921,"mean_force":0.54602,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"approach","tcp_position_centroid":[0.51665,0.10577,0.14992]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52506,-0.11999,0.01966],"force_p95":0.53564,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56104,"mean_force":0.35046,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5013,-0.08423,0.0301]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49146,-0.11418,0.00999],"force_p95":0.53545,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53545,"mean_force":0.53545,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50143,-0.08346,0.02987]}],"total_contact_groups":16},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.54189,-0.19691,0.01412],"final_tcp_position":[0.49831,-0.08302,0.11027],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":212.52305,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":229.0,"n_steps_budget":780.0,"object_pos_end":[0.50613,0.0566,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.52504,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":237.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.52825,0.11375,0.24485],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21979,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,0.05662,0.03377],"object_pos_start":[0.50613,0.0566,0.03377],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13688,"object_z_max":0.03383,"peak_contact_force":0.51533,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":360.0,"raw_peak_contact_force":0.64921,"subtask_id":"approach","tcp_end":[0.50559,0.09796,0.05344],"tcp_start":[0.52825,0.11375,0.24485],"tcp_to_object_dist_end":0.04579,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":302.0,"n_steps_budget":600.0,"object_pos_end":[0.50706,0.04848,0.03534],"object_pos_start":[0.50614,0.05662,0.03377],"object_to_goal_dist_end":0.12876,"object_to_goal_dist_start":0.1369,"object_z_max":0.03544,"peak_contact_force":3.13935,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":565.0,"raw_peak_contact_force":6.46095,"subtask_id":"contact","tcp_end":[0.50218,0.07816,0.03076],"tcp_start":[0.50559,0.09796,0.05344],"tcp_to_object_dist_end":0.03043,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.50127,-0.11814,0.03891],"object_pos_start":[0.50706,0.04848,0.03534],"object_to_goal_dist_end":0.03818,"object_to_goal_dist_start":0.12876,"object_z_max":0.03878,"peak_contact_force":2.01439,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":756.0,"raw_peak_contact_force":212.52305,"subtask_id":"push","tcp_end":[0.50143,-0.08346,0.02987],"tcp_start":[0.50218,0.07816,0.03076],"tcp_to_object_dist_end":0.03585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":245.0,"n_steps_budget":630.0,"object_pos_end":[0.54189,-0.19691,0.01412],"object_pos_start":[0.50127,-0.11814,0.03891],"object_to_goal_dist_end":0.12686,"object_to_goal_dist_start":0.03818,"object_z_max":0.03917,"peak_contact_force":0.60177,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":244.0,"raw_peak_contact_force":65.29566,"tcp_end":[0.49831,-0.08302,0.11027],"tcp_start":[0.50143,-0.08346,0.02987],"tcp_to_object_dist_end":0.1553,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```