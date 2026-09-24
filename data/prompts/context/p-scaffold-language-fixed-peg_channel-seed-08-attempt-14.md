## Search State

- **Seed**: 8
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.0453 | 0.24 | ❌ rejected |
| 13 | align → push → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | impedance_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.4227 | 0.00 | ❌ rejected |
| 12 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | -0.1435 | 0.00 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.0528 | 0.09 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.1845 | 0.11 | ❌ rejected |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.045) — your mutation base

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

- **Composite score**: -0.045
- **task_score** (E): 0.235
- **fitness_score**: 0.345  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.150
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2479 |
| approach_1 | 1.00 | 1.00 | 0.0295 |
| contact_1 | 0.67 | 1.00 | 0.0072 |
| push_1 | 0.33 | 1.00 | 0.0899 |
| retract_1 | 1.00 | 1.00 | 0.1379 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.123, 0.068) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.569 | 3.526 |
| approach_1 | approach | 1.00 / step_budget | (0.516, 0.123, 0.068)→(0.504, 0.104, 0.054) | (0.503, 0.080, 0.034)→(0.503, 0.076, 0.036) | 0.160→0.156 | 1.00 / 2.000 | 35.790 | 42.700 |
| contact_1 | contact | 0.67 / force_exceeded | (0.504, 0.104, 0.054)→(0.504, 0.097, 0.054) | (0.503, 0.076, 0.036)→(0.503, 0.069, 0.037) | 0.156→0.150 | 1.00 / 2.000 | 56.293 | 59.390 |
| push_1 | push | 0.33 / step_budget | (0.504, 0.097, 0.054)→(0.504, 0.007, 0.056) | (0.503, 0.069, 0.037)→(0.502, 0.019, 0.028) | 0.150→0.101 | 1.00 / 1.333 | 2.573 | 209.838 |
| retract_1 | retract | 1.00 / step_budget | (0.497, -0.032, 0.053)→(0.495, -0.029, 0.191) | (0.500, 0.001, 0.025)→(0.500, 0.001, 0.024) | 0.083→0.083 | 1.00 / 1.000 | 0.612 | 10.820 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.541
- alignment_error: None
- force_efficiency: 0.221
- terminal_score: 0.477
- phase_score: 0.370
- phase_breakdown.approach_score: 0.639
- phase_breakdown.contact_score: 0.788
- phase_breakdown.push_score: 0.142

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.477
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.477
- **Median Q (composite search score)**: -0.063
- **K-run variance**: 0.0081
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.321


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.11072,"align_1.lateral_offset_x":0.00272,"approach_1.approach_speed":0.04129,"contact_1.contact_force_threshold":6.3729,"contact_1.contact_speed":0.02529,"push_1.push_distance":0.15989,"push_1.push_speed":0.02776,"push_1.push_tolerance":0.02648,"retract_1.retract_speed":0.14107},"optimized_scores":{"best_composite_score":0.07301,"best_fitness_score":0.41301,"best_task_score":0.47692},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":713.0,"contact_point_centroid":[0.49705,0.0857,0.04892],"force_p95":35.14981,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.92679,"mean_force":21.22676,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48847,0.09381,0.04756]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":673.0,"contact_point_centroid":[0.52563,0.06964,0.04544],"force_p95":27.15325,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.65774,"mean_force":18.2742,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48877,0.09079,0.04801]},{"body_a":"peg","body_b":"channel_base_body","contact_count":905.0,"contact_point_centroid":[0.50622,0.06412,0.00954],"force_p95":24.18816,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.66573,"mean_force":9.20332,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48875,0.08423,0.04752]},{"body_a":"peg","body_b":"channel_base_body","contact_count":632.0,"contact_point_centroid":[0.49333,0.03225,0.00832],"force_p95":7.84872,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.77284,"mean_force":2.24708,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49018,0.02657,0.1175]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":187.0,"contact_point_centroid":[0.47489,0.0322,0.02581],"force_p95":10.25287,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.44104,"mean_force":5.82092,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49033,0.02279,0.06791]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":27.0,"contact_point_centroid":[0.47495,0.03506,0.02483],"force_p95":9.68108,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.02365,"mean_force":4.47133,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49234,0.02032,0.05079]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50249,0.09785,0.00997],"force_p95":7.51424,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.51424,"mean_force":7.51424,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49162,0.14003,0.05061]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49429,0.12836,0.05018],"force_p95":7.1982,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.1982,"mean_force":7.1982,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49162,0.14003,0.05061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":430.0,"contact_point_centroid":[0.49847,0.10957,0.00966],"force_p95":3.98608,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.77641,"mean_force":1.54433,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.488,0.14847,0.05725]},{"body_a":"attachment","body_b":"peg","contact_count":168.0,"contact_point_centroid":[0.49292,0.13185,0.05342],"force_p95":3.92372,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.41693,"mean_force":2.75671,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48997,0.14347,0.05317]},{"body_a":"peg","body_b":"channel_base_body","contact_count":675.0,"contact_point_centroid":[0.4962,0.11905,0.00942],"force_p95":0.60845,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55234,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49217,0.1793,0.18046]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49955,0.19925,0.29757]}],"total_contact_groups":12},"final_pose_error":0.0122,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49369,0.03236,0.02409],"final_tcp_position":[0.49037,0.01955,0.18922],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":38.92679,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":700.0,"n_steps_budget":1000.0,"object_pos_end":[0.49612,0.11899,0.03397],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19912,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.57289,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":699.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach","tcp_end":[0.48618,0.16033,0.06952],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":430.0,"n_steps_budget":600.0,"object_pos_end":[0.49766,0.11212,0.03681],"object_pos_start":[0.49612,0.11899,0.03397],"object_to_goal_dist_end":0.19216,"object_to_goal_dist_start":0.19912,"object_z_max":0.0368,"peak_contact_force":2.93764,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":598.0,"raw_peak_contact_force":4.77641,"subtask_id":"approach","tcp_end":[0.49162,0.14003,0.05061],"tcp_start":[0.48618,0.16033,0.06952],"tcp_to_object_dist_end":0.03172,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":630.0,"object_pos_end":[0.49764,0.11208,0.0368],"object_pos_start":[0.49766,0.11212,0.03681],"object_to_goal_dist_end":0.19212,"object_to_goal_dist_start":0.19216,"object_z_max":0.03681,"peak_contact_force":7.51424,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":7.51424,"subtask_id":"contact","tcp_end":[0.49161,0.14,0.05057],"tcp_start":[0.49162,0.14003,0.05061],"tcp_to_object_dist_end":0.03171,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49297,0.03236,0.0255],"object_pos_start":[0.49764,0.11208,0.0368],"object_to_goal_dist_end":0.11351,"object_to_goal_dist_start":0.19212,"object_z_max":0.04032,"peak_contact_force":7.1008,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2318.0,"raw_peak_contact_force":38.92679,"subtask_id":"push","tcp_end":[0.49246,0.01675,0.05091],"tcp_start":[0.49161,0.14,0.05057],"tcp_to_object_dist_end":0.02983,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":632.0,"n_steps_budget":690.0,"object_pos_end":[0.49369,0.03236,0.02409],"object_pos_start":[0.49297,0.03236,0.0255],"object_to_goal_dist_end":0.11366,"object_to_goal_dist_start":0.11351,"object_z_max":0.02611,"peak_contact_force":0.49887,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":819.0,"raw_peak_contact_force":11.77284,"tcp_end":[0.49037,0.01955,0.18922],"tcp_start":[0.49246,0.01675,0.05091],"tcp_to_object_dist_end":0.16566,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47458,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.09192,"align_1.lateral_offset_x":-0.00916,"approach_1.approach_speed":0.06896,"contact_1.contact_force_threshold":11.74757,"contact_1.contact_speed":0.03513,"push_1.push_distance":0.13719,"push_1.push_speed":0.05459,"push_1.push_tolerance":0.01986,"retract_1.retract_speed":0.15492},"optimized_scores":{"best_composite_score":-0.06296,"best_fitness_score":0.47704,"best_task_score":0.22902},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":403.0,"contact_point_centroid":[0.50294,0.01985,0.04873],"force_p95":25.32855,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.40604,"mean_force":14.542,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49874,0.03082,0.04917]},{"body_a":"peg","body_b":"channel_base_body","contact_count":929.0,"contact_point_centroid":[0.50663,-0.01309,0.00895],"force_p95":20.29427,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.68031,"mean_force":5.60345,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49985,-0.00489,0.05118]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":422.0,"contact_point_centroid":[0.52527,0.0115,0.03595],"force_p95":13.34631,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.31058,"mean_force":7.43794,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49802,0.03694,0.04801]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.50432,0.03907,0.00996],"force_p95":5.28187,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.86183,"mean_force":2.5247,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5015,0.07525,0.0501]},{"body_a":"attachment","body_b":"peg","contact_count":448.0,"contact_point_centroid":[0.50333,0.06326,0.04974],"force_p95":4.90472,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.63105,"mean_force":2.13601,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50146,0.07507,0.05009]},{"body_a":"peg","body_b":"channel_base_body","contact_count":572.0,"contact_point_centroid":[0.50649,-0.03057,0.00807],"force_p95":0.72556,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.86682,"mean_force":0.73958,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49977,-0.07047,0.12163]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52501,-0.03056,0.02454],"force_p95":9.13146,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.36293,"mean_force":4.58194,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49959,-0.06596,0.1215]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.50571,0.07776,0.05337],"force_p95":7.57862,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.64338,"mean_force":5.66167,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50525,0.08968,0.05318]},{"body_a":"peg","body_b":"channel_base_body","contact_count":186.0,"contact_point_centroid":[0.50604,0.05738,0.00949],"force_p95":6.30174,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.10684,"mean_force":1.23804,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50893,0.0969,0.05815]},{"body_a":"peg","body_b":"channel_base_body","contact_count":766.0,"contact_point_centroid":[0.50577,0.06299,0.00936],"force_p95":0.55659,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56423,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50727,0.15195,0.17863]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49977,0.19839,0.29622]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52509,0.05836,0.06],"force_p95":2.26291,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.26443,"mean_force":1.52705,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50495,0.08898,0.05277]}],"total_contact_groups":12},"final_pose_error":0.01329,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50583,-0.03083,0.02409],"final_tcp_position":[0.49998,-0.07736,0.1929],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":27.40604,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":794.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06303,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55034,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":800.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach","tcp_end":[0.51574,0.10723,0.06744],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":186.0,"n_steps_budget":600.0,"object_pos_end":[0.50556,0.0589,0.03686],"object_pos_start":[0.50601,0.06303,0.03381],"object_to_goal_dist_end":0.13905,"object_to_goal_dist_start":0.14329,"object_z_max":0.03683,"peak_contact_force":5.90001,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":222.0,"raw_peak_contact_force":7.64338,"subtask_id":"approach","tcp_end":[0.50412,0.0871,0.05166],"tcp_start":[0.51574,0.10723,0.06744],"tcp_to_object_dist_end":0.03188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.5057,0.03939,0.04058],"object_pos_start":[0.50556,0.0589,0.03686],"object_to_goal_dist_end":0.11953,"object_to_goal_dist_start":0.13905,"object_z_max":0.04058,"peak_contact_force":1.57115,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":903.0,"raw_peak_contact_force":10.86183,"subtask_id":"contact","tcp_end":[0.50168,0.06559,0.05172],"tcp_start":[0.50412,0.0871,0.05166],"tcp_to_object_dist_end":0.02875,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50623,-0.03057,0.02414],"object_pos_start":[0.5057,0.03939,0.04058],"object_to_goal_dist_end":0.05229,"object_to_goal_dist_start":0.11953,"object_z_max":0.04088,"peak_contact_force":0.61748,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1754.0,"raw_peak_contact_force":27.40604,"subtask_id":"push","tcp_end":[0.50212,-0.08068,0.05559],"tcp_start":[0.50168,0.06559,0.05172],"tcp_to_object_dist_end":0.0593,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.50583,-0.03083,0.02409],"object_pos_start":[0.50623,-0.03057,0.02414],"object_to_goal_dist_end":0.05201,"object_to_goal_dist_start":0.05229,"object_z_max":0.02513,"peak_contact_force":0.72551,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":590.0,"raw_peak_contact_force":9.86682,"tcp_end":[0.49998,-0.07736,0.1929],"tcp_start":[0.50212,-0.08068,0.05559],"tcp_to_object_dist_end":0.1752,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71053,"average_solve_count":76.0,"average_success_count":76.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.align_speed":0.10139,"align_1.lateral_offset_x":0.01499,"approach_1.approach_speed":0.05474,"contact_1.contact_force_threshold":11.97284,"contact_1.contact_speed":0.02575,"push_1.push_distance":0.14391,"push_1.push_speed":0.02815,"push_1.push_tolerance":0.01488,"retract_1.retract_speed":0.14478},"optimized_scores":{"best_composite_score":-0.14581,"best_fitness_score":0.14419,"best_task_score":3e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52942,0.08313,0.05997],"force_p95":563.1817,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":563.1817,"mean_force":563.1817,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5176,0.08484,0.06116]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52946,0.08313,0.05997],"force_p95":159.79424,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":159.79424,"mean_force":159.79424,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51765,0.08484,0.06116]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":396.0,"contact_point_centroid":[0.53872,0.08961,0.05995],"force_p95":102.01571,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.68121,"mean_force":77.0664,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52686,0.09061,0.0614]},{"body_a":"peg","body_b":"channel_base_body","contact_count":805.0,"contact_point_centroid":[0.50595,0.05661,0.00936],"force_p95":0.60055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56632,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52241,0.14855,0.17758]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50021,0.19814,0.29569]},{"body_a":"peg","body_b":"channel_base_body","contact_count":460.0,"contact_point_centroid":[0.50612,0.05665,0.00938],"force_p95":0.55885,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58277,"mean_force":0.54671,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52828,0.09143,0.0616]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52227,0.0487,0.00938],"force_p95":0.54512,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54512,"mean_force":0.54512,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5176,0.08484,0.06116]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52116,0.06651,0.00938],"force_p95":0.54506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54506,"mean_force":0.54506,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51765,0.08484,0.06116]}],"total_contact_groups":8},"final_pose_error":0.17275,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50613,0.0566,0.03378],"final_tcp_position":[0.51765,0.0849,0.06123],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":563.1817,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":834.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05663,0.03376],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.58241,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":842.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach","tcp_end":[0.54514,0.10092,0.06613],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0673,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":460.0,"n_steps_budget":600.0,"object_pos_end":[0.50615,0.05663,0.03378],"object_pos_start":[0.50615,0.05663,0.03376],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13691,"object_z_max":0.03378,"peak_contact_force":98.53117,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":856.0,"raw_peak_contact_force":115.68121,"subtask_id":"approach","tcp_end":[0.51765,0.08484,0.06116],"tcp_start":[0.54514,0.10092,0.06613],"tcp_to_object_dist_end":0.04097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.50615,0.05661,0.03378],"object_pos_start":[0.50615,0.05663,0.03378],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.13691,"object_z_max":0.03378,"peak_contact_force":159.79424,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":159.79424,"subtask_id":"contact","tcp_end":[0.5176,0.08484,0.06116],"tcp_start":[0.51765,0.08484,0.06116],"tcp_to_object_dist_end":0.04096,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.0566,0.03378],"object_pos_start":[0.50615,0.05661,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13689,"object_z_max":0.03378,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":563.1817,"subtask_id":"push","tcp_end":[0.51765,0.0849,0.06123],"tcp_start":[0.5176,0.08484,0.06116],"tcp_to_object_dist_end":0.04108,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```