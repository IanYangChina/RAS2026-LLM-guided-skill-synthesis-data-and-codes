## Search State

- **Seed**: 8
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.0230 | 0.29 | ✅ accepted |
| 5 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.1685 | 0.23 | ✅ accepted |
| 4 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0360 | 0.00 | ❌ rejected |
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.1885 | 0.19 | ✅ accepted |
| 2 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | -0.1928 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.023) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.0
- id: contact
  anchor: object
  offset:
  - 0.0
  - 0.02
  - 0.0
- id: push
  anchor: world
  offset:
  - 0.5
  - -0.08
  - 0.04
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.04
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_offset_x:
      type: scalar
      range:
      - -0.015
      - 0.015
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
  subtask_id: approach
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.02
    - 0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.005
    - 0.02
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 20.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: contact
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 1.0
      - 0.0
      align_with: channel_axis
      tolerance: 0.1
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
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: push
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_1** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.04, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.02, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.005, 0.02], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 1.0, 0.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=2, strategy=reduce_speed, offset=[0.0, 0.0, 0.005]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.023
- **task_score** (E): 0.291
- **fitness_score**: 0.367  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.150
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2479 |
| approach_1 | 1.00 | 1.00 | 0.0292 |
| contact_1 | 0.67 | 1.00 | 0.0073 |
| push_1 | 0.33 | 1.00 | 0.0872 |
| retract_1 | 1.00 | 1.00 | 0.1385 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.515, 0.123, 0.068) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.529 | 3.526 |
| approach_1 | approach | 1.00 / step_budget | (0.515, 0.123, 0.068)→(0.504, 0.104, 0.054) | (0.503, 0.080, 0.034)→(0.503, 0.076, 0.036) | 0.160→0.156 | 1.00 / 1.667 | 33.711 | 41.880 |
| contact_1 | contact | 0.67 / force_exceeded | (0.504, 0.104, 0.054)→(0.504, 0.097, 0.055) | (0.503, 0.076, 0.036)→(0.503, 0.070, 0.037) | 0.156→0.150 | 1.00 / 2.000 | 55.945 | 58.139 |
| push_1 | push | 0.33 / step_budget | (0.504, 0.097, 0.055)→(0.504, 0.010, 0.056) | (0.503, 0.070, 0.037)→(0.506, 0.012, 0.031) | 0.150→0.093 | 1.00 / 1.667 | 5.564 | 209.524 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.028, 0.053)→(0.495, -0.025, 0.191) | (0.506, -0.010, 0.030)→(0.499, -0.015, 0.024) | 0.071→0.067 | 1.00 / 1.000 | 0.588 | 25.742 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.752
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.659
- phase_score: 0.360
- phase_breakdown.approach_score: 0.648
- phase_breakdown.contact_score: 0.787
- phase_breakdown.push_score: 0.121

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.479
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.659
- **Median Q (composite search score)**: -0.063
- **K-run variance**: 0.0143
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.363


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40741,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.11211,"align_1.lateral_offset_x":0.00136,"approach_1.approach_speed":0.08397,"contact_1.contact_force_threshold":2.68102,"contact_1.contact_speed":0.01147,"push_1.push_distance":0.12738,"push_1.push_speed":0.03495,"push_1.push_tolerance":0.01931,"retract_1.retract_speed":0.14602},"optimized_scores":{"best_composite_score":0.1393,"best_fitness_score":0.4793,"best_task_score":0.65891},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50136,0.017,0.0507],"force_p95":38.10092,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.80123,"mean_force":8.46687,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49236,0.02464,0.05171]},{"body_a":"peg","body_b":"channel_base_body","contact_count":599.0,"contact_point_centroid":[0.49842,0.00056,0.00821],"force_p95":0.90457,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.88072,"mean_force":0.74079,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49023,0.03461,0.11832]},{"body_a":"attachment","body_b":"peg","contact_count":897.0,"contact_point_centroid":[0.49703,0.07307,0.04925],"force_p95":32.13223,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.19899,"mean_force":18.86014,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48918,0.08189,0.04838]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":869.0,"contact_point_centroid":[0.52545,0.05761,0.04838],"force_p95":21.68718,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.79804,"mean_force":15.69446,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48937,0.0801,0.04864]},{"body_a":"peg","body_b":"channel_base_body","contact_count":825.0,"contact_point_centroid":[0.50786,0.05539,0.00987],"force_p95":21.99024,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.34107,"mean_force":10.20904,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48873,0.08479,0.04767]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52514,0.02612,0.02856],"force_p95":4.46076,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.14116,"mean_force":2.37514,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49199,0.02489,0.05258]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47499,-0.02588,0.02428],"force_p95":8.86302,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.00152,"mean_force":2.77306,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49022,0.03695,0.15235]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50277,0.09836,0.00997],"force_p95":7.21673,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.21673,"mean_force":7.21673,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49133,0.14085,0.05067]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49406,0.1292,0.05022],"force_p95":6.90603,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.90603,"mean_force":6.90603,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49133,0.14085,0.05067]},{"body_a":"peg","body_b":"channel_base_body","contact_count":435.0,"contact_point_centroid":[0.49859,0.11036,0.00969],"force_p95":3.65112,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.66543,"mean_force":1.41291,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48728,0.14892,0.05721]},{"body_a":"attachment","body_b":"peg","contact_count":166.0,"contact_point_centroid":[0.49265,0.13248,0.05369],"force_p95":3.60955,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.31173,"mean_force":2.47987,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48953,0.14408,0.05314]},{"body_a":"peg","body_b":"channel_base_body","contact_count":673.0,"contact_point_centroid":[0.49616,0.11922,0.0094],"force_p95":0.63227,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55369,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49152,0.17926,0.18022]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49953,0.19924,0.29753]}],"total_contact_groups":13},"final_pose_error":0.01267,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49381,-0.00138,0.02415],"final_tcp_position":[0.49042,0.02772,0.18947],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":50.80123,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.11975,0.03393],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19989,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.53975,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":697.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48489,0.16029,0.06933],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":435.0,"n_steps_budget":600.0,"object_pos_end":[0.49759,0.11287,0.03662],"object_pos_start":[0.49603,0.11975,0.03393],"object_to_goal_dist_end":0.19291,"object_to_goal_dist_start":0.19989,"object_z_max":0.03662,"peak_contact_force":2.5298,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":601.0,"raw_peak_contact_force":4.66543,"subtask_id":"approach","tcp_end":[0.49133,0.14085,0.05067],"tcp_start":[0.48489,0.16029,0.06933],"tcp_to_object_dist_end":0.03193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49758,0.11283,0.03662],"object_pos_start":[0.49759,0.11287,0.03662],"object_to_goal_dist_end":0.19288,"object_to_goal_dist_start":0.19291,"object_z_max":0.03662,"peak_contact_force":7.21673,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":7.21673,"subtask_id":"contact","tcp_end":[0.49132,0.14083,0.05063],"tcp_start":[0.49133,0.14085,0.05067],"tcp_to_object_dist_end":0.03193,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50749,0.00872,0.03636],"object_pos_start":[0.49758,0.11283,0.03662],"object_to_goal_dist_end":0.08911,"object_to_goal_dist_start":0.19288,"object_z_max":0.04026,"peak_contact_force":16.00741,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2591.0,"raw_peak_contact_force":36.19899,"subtask_id":"push","tcp_end":[0.49248,0.02481,0.05163],"tcp_start":[0.49132,0.14083,0.05063],"tcp_to_object_dist_end":0.02678,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.49381,-0.00138,0.02415],"object_pos_start":[0.50749,0.00872,0.03636],"object_to_goal_dist_end":0.08044,"object_to_goal_dist_start":0.08911,"object_z_max":0.03636,"peak_contact_force":0.64356,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":630.0,"raw_peak_contact_force":50.80123,"tcp_end":[0.49042,0.02772,0.18947],"tcp_start":[0.49248,0.02481,0.05163],"tcp_to_object_dist_end":0.16789,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30994,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.13457,"align_1.lateral_offset_x":-0.01123,"approach_1.approach_speed":0.05615,"contact_1.contact_force_threshold":12.36111,"contact_1.contact_speed":0.04479,"push_1.push_distance":0.17423,"push_1.push_speed":0.04985,"push_1.push_tolerance":0.01813,"retract_1.retract_speed":0.11956},"optimized_scores":{"best_composite_score":-0.06264,"best_fitness_score":0.47736,"best_task_score":0.21296},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":399.0,"contact_point_centroid":[0.50307,0.02032,0.04857],"force_p95":26.76572,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.19669,"mean_force":15.27288,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49887,0.03128,0.04911]},{"body_a":"peg","body_b":"channel_base_body","contact_count":936.0,"contact_point_centroid":[0.50611,-0.0115,0.00894],"force_p95":21.83872,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.31072,"mean_force":5.83689,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49981,-0.00412,0.05059]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":413.0,"contact_point_centroid":[0.52523,0.01255,0.03596],"force_p95":12.85623,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.55984,"mean_force":7.41135,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49803,0.03804,0.04782]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.50519,0.03902,0.00996],"force_p95":5.90002,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.04863,"mean_force":2.55758,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50135,0.07489,0.05021]},{"body_a":"attachment","body_b":"peg","contact_count":449.0,"contact_point_centroid":[0.50346,0.06297,0.04981],"force_p95":5.5317,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.70954,"mean_force":2.16377,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50132,0.07473,0.05019]},{"body_a":"peg","body_b":"channel_base_body","contact_count":195.0,"contact_point_centroid":[0.50588,0.05707,0.00951],"force_p95":6.03108,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.64911,"mean_force":1.09443,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50765,0.09663,0.05804]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.50531,0.07804,0.0538],"force_p95":6.26822,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.35843,"mean_force":5.10877,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50474,0.08996,0.05341]},{"body_a":"peg","body_b":"channel_base_body","contact_count":732.0,"contact_point_centroid":[0.50582,0.06295,0.00936],"force_p95":0.55778,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56504,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50633,0.15195,0.17864]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49977,0.19835,0.2961]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.05914,0.06],"force_p95":1.61434,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.61434,"mean_force":1.61434,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50456,0.08948,0.05311]},{"body_a":"peg","body_b":"channel_base_body","contact_count":740.0,"contact_point_centroid":[0.50355,-0.0287,0.00804],"force_p95":0.68339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68339,"mean_force":0.60577,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49949,-0.06999,0.122]}],"total_contact_groups":11},"final_pose_error":0.01154,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50481,-0.02879,0.02413],"final_tcp_position":[0.49973,-0.07749,0.19323],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":29.19669,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":760.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06298,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54785,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":766.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.51383,0.10725,0.06754],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":195.0,"n_steps_budget":600.0,"object_pos_end":[0.50575,0.05845,0.03716],"object_pos_start":[0.50594,0.06298,0.03381],"object_to_goal_dist_end":0.1386,"object_to_goal_dist_start":0.14323,"object_z_max":0.03714,"peak_contact_force":0.45331,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":219.0,"raw_peak_contact_force":6.64911,"subtask_id":"approach","tcp_end":[0.50364,0.0868,0.05156],"tcp_start":[0.51383,0.10725,0.06754],"tcp_to_object_dist_end":0.03187,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50634,0.03916,0.04062],"object_pos_start":[0.50575,0.05845,0.03716],"object_to_goal_dist_end":0.11933,"object_to_goal_dist_start":0.1386,"object_z_max":0.04062,"peak_contact_force":1.46582,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":904.0,"raw_peak_contact_force":8.04863,"subtask_id":"contact","tcp_end":[0.5018,0.06515,0.05198],"tcp_start":[0.50364,0.0868,0.05156],"tcp_to_object_dist_end":0.02872,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,-0.02873,0.02413],"object_pos_start":[0.50634,0.03916,0.04062],"object_to_goal_dist_end":0.0538,"object_to_goal_dist_start":0.11933,"object_z_max":0.04092,"peak_contact_force":0.68339,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1748.0,"raw_peak_contact_force":29.19669,"subtask_id":"push","tcp_end":[0.50193,-0.08038,0.05418],"tcp_start":[0.5018,0.06515,0.05198],"tcp_to_object_dist_end":0.05979,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":740.0,"n_steps_budget":810.0,"object_pos_end":[0.50481,-0.02879,0.02413],"object_pos_start":[0.50376,-0.02873,0.02413],"object_to_goal_dist_end":0.05383,"object_to_goal_dist_start":0.0538,"object_z_max":0.02413,"peak_contact_force":0.53262,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":740.0,"raw_peak_contact_force":0.68339,"tcp_end":[0.49973,-0.07749,0.19323],"tcp_start":[0.50193,-0.08038,0.05418],"tcp_to_object_dist_end":0.17605,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.00813,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.05382,"align_1.lateral_offset_x":0.01479,"approach_1.approach_speed":0.06596,"contact_1.contact_force_threshold":6.39641,"contact_1.contact_speed":0.02225,"push_1.push_distance":0.10792,"push_1.push_speed":0.05101,"push_1.push_tolerance":0.01848,"retract_1.retract_speed":0.14365},"optimized_scores":{"best_composite_score":-0.14577,"best_fitness_score":0.14423,"best_task_score":9e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52944,0.08307,0.05997],"force_p95":563.17678,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":563.17678,"mean_force":563.17678,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51762,0.08479,0.06117]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52948,0.08307,0.05998],"force_p95":159.15285,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.15285,"mean_force":159.15285,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51767,0.08479,0.06117]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":395.0,"contact_point_centroid":[0.53864,0.08954,0.05995],"force_p95":101.28923,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.32397,"mean_force":76.87493,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52678,0.09054,0.0614]},{"body_a":"peg","body_b":"channel_base_body","contact_count":881.0,"contact_point_centroid":[0.50593,0.0566,0.00936],"force_p95":0.60267,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56448,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52218,0.14866,0.17786]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50003,0.19837,0.29627]},{"body_a":"peg","body_b":"channel_base_body","contact_count":459.0,"contact_point_centroid":[0.50617,0.05672,0.00938],"force_p95":0.56848,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60889,"mean_force":0.54672,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5282,0.09137,0.0616]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5228,0.04987,0.00938],"force_p95":0.5509,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5509,"mean_force":0.5509,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51762,0.08479,0.06117]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52343,0.06155,0.00938],"force_p95":0.5455,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5455,"mean_force":0.5455,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51767,0.08479,0.06117]}],"total_contact_groups":8},"final_pose_error":0.13686,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50617,0.05657,0.03381],"final_tcp_position":[0.51767,0.08485,0.06124],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":563.17678,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":910.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05664,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13692,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.49975,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":918.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach","tcp_end":[0.54495,0.10093,0.06613],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06719,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":459.0,"n_steps_budget":600.0,"object_pos_end":[0.50618,0.05663,0.03381],"object_pos_start":[0.50615,0.05664,0.03377],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13692,"object_z_max":0.03381,"peak_contact_force":98.15093,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":854.0,"raw_peak_contact_force":114.32397,"subtask_id":"approach","tcp_end":[0.51767,0.08479,0.06117],"tcp_start":[0.54495,0.10093,0.06613],"tcp_to_object_dist_end":0.04091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":780.0,"object_pos_end":[0.50618,0.05659,0.03381],"object_pos_start":[0.50618,0.05663,0.03381],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13691,"object_z_max":0.03381,"peak_contact_force":159.15285,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":159.15285,"subtask_id":"contact","tcp_end":[0.51762,0.08479,0.06117],"tcp_start":[0.51767,0.08479,0.06117],"tcp_to_object_dist_end":0.04091,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50617,0.05657,0.03381],"object_pos_start":[0.50618,0.05659,0.03381],"object_to_goal_dist_end":0.13684,"object_to_goal_dist_start":0.13687,"object_z_max":0.03381,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":563.17678,"subtask_id":"push","tcp_end":[0.51767,0.08485,0.06124],"tcp_start":[0.51762,0.08479,0.06117],"tcp_to_object_dist_end":0.04104,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```