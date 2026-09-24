## Search State

- **Seed**: 4
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2542 | 0.58 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3784 | 0.00 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3973 | 0.60 | ✅ accepted |
| 0 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3739 | 0.56 | ✅ accepted |

**Proposal policy**: task_score is 0.58 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, 0.08090620422514894, 0.04]
- Frozen task target: [0.5354444884457894, -0.07909379577485107, 0.04]
- Goal object position: (0.5354444884457894, -0.07909379577485107, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, 0.08090620422514894, 0.04)
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
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, 0.08090620422514894, 0.04]}
  frozen_targets: {'channel_exit': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5354444884457894, 0.08090620422514894, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5354444884457894, -0.07909379577485107, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.254) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: reach_goal
  offset:
  - 0.0
  - -0.03
  - 0.0
  weight: 0.7
phases:
- id: approach_1
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
    - 0.03
    - 0.05
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_peg
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - -0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 0.5
      - 5.0
      default: 2.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: push_1
  type: push
  generator: linear_cartesian
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
      distance: 0.19
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 35.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
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
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.05], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, -0.01]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.19, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=35.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.254
- **task_score** (E): 0.584
- **fitness_score**: 0.528  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2064 |
| descend_1 | 1.00 | 1.00 | 0.0591 |
| contact_1 | 0.33 | 1.00 | 0.0292 |
| push_1 | 0.00 | 1.00 | 0.0002 |
| retract_1 | 1.00 | 1.00 | 0.0922 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.123, 0.110) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.544 | 3.242 |
| descend_1 | descend | 1.00 / step_budget | (0.516, 0.123, 0.110)→(0.506, 0.117, 0.053) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.544 | 161.673 |
| contact_1 | contact | 0.33 / step_budget | (0.506, 0.117, 0.053)→(0.501, 0.092, 0.037) | (0.505, 0.084, 0.034)→(0.506, 0.063, 0.036) | 0.165→0.143 | 1.00 / 2.000 | 1307.538 | 8.814 |
| push_1 | push | 0.00 / guard_failure | (0.501, -0.053, 0.031)→(0.501, -0.054, 0.031) | (0.506, 0.063, 0.036)→(0.506, -0.083, 0.036) | 0.143→0.008 | 1.00 / 2.667 | 34.952 | 41.252 |
| retract_1 | retract | 1.00 / step_budget | (0.501, -0.054, 0.031)→(0.497, -0.076, 0.121) | (0.506, -0.083, 0.036)→(0.507, -0.073, 0.036) | 0.008→0.011 | 1.00 / 1.667 | 0.705 | 55.803 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.903
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.903
- phase_score: 0.509
- phase_breakdown.reach_peg_score: 0.347
- phase_breakdown.reach_goal_score: 0.578

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.666
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.903
- **Median Q (composite search score)**: 0.164
- **K-run variance**: 0.0384
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.359


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.72667,"average_solve_count":300.0,"average_success_count":300.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0456,"contact_1.contact_force":11.01151,"contact_1.contact_speed":0.00985,"descend_1.speed":0.01881,"push_1.push_speed":0.01626},"optimized_scores":{"best_composite_score":0.07215,"best_fitness_score":0.41215,"best_task_score":0.29969},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52533,0.11404,0.05995],"force_p95":472.59353,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":483.88831,"mean_force":361.08422,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51343,0.1141,0.06033]},{"body_a":"attachment","body_b":"peg","contact_count":226.0,"contact_point_centroid":[0.50074,-0.06762,0.06036],"force_p95":52.74398,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.0801,"mean_force":38.37168,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49623,-0.05716,0.0595]},{"body_a":"peg","body_b":"channel_base_body","contact_count":248.0,"contact_point_centroid":[0.50866,-0.10062,0.06424],"force_p95":50.15184,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.81873,"mean_force":34.16792,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49626,-0.05801,0.0625]},{"body_a":"attachment","body_b":"peg","contact_count":263.0,"contact_point_centroid":[0.50431,0.00322,0.04676],"force_p95":23.58164,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.79191,"mean_force":5.64667,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50098,0.0149,0.03311]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50665,-0.10044,0.05999],"force_p95":37.68927,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.82022,"mean_force":35.23309,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50048,-0.05302,0.03163]},{"body_a":"peg","body_b":"channel_base_body","contact_count":143.0,"contact_point_centroid":[0.50343,-0.01647,0.00967],"force_p95":22.5878,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.61715,"mean_force":7.22934,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50112,0.02644,0.03342]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":169.0,"contact_point_centroid":[0.52518,-0.03271,0.03219],"force_p95":19.08005,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.7641,"mean_force":3.67893,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50056,-0.00353,0.03236]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":94.0,"contact_point_centroid":[0.5251,-0.08095,0.05588],"force_p95":10.14839,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.32585,"mean_force":5.48179,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49575,-0.05945,0.06719]},{"body_a":"peg","body_b":"channel_base_body","contact_count":993.0,"contact_point_centroid":[0.50235,0.05377,0.00995],"force_p95":3.92838,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.57344,"mean_force":1.83647,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50532,0.0994,0.04184]},{"body_a":"attachment","body_b":"peg","contact_count":958.0,"contact_point_centroid":[0.505,0.08685,0.04148],"force_p95":3.73296,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.16245,"mean_force":1.55232,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50518,0.09881,0.0415]},{"body_a":"peg","body_b":"channel_base_body","contact_count":45.0,"contact_point_centroid":[0.49406,-0.07132,0.00897],"force_p95":4.10085,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.00884,"mean_force":1.24567,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49712,-0.07204,0.1067]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47447,-0.07675,0.04578],"force_p95":4.47147,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.43916,"mean_force":1.81463,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49612,-0.06659,0.0918]},{"body_a":"peg","body_b":"channel_base_body","contact_count":388.0,"contact_point_centroid":[0.50559,0.08084,0.00935],"force_p95":0.56158,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58609,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51452,0.1575,0.19489]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50058,0.19748,0.29384]},{"body_a":"peg","body_b":"channel_base_body","contact_count":120.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55008,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5501,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52018,0.11629,0.07923]}],"total_contact_groups":15},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50771,-0.06852,0.03538],"final_tcp_position":[0.49691,-0.0757,0.12075],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":483.88831,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":417.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54642,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":424.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52882,0.11931,0.10229],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":120.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54637,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":129.0,"raw_peak_contact_force":483.88831,"subtask_id":"reach_peg","tcp_end":[0.51054,0.11392,0.05263],"tcp_start":[0.52882,0.11931,0.10229],"tcp_to_object_dist_end":0.03831,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50403,0.06145,0.03553],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.14158,"object_to_goal_dist_start":0.16112,"object_z_max":0.03593,"peak_contact_force":1.58902,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1951.0,"raw_peak_contact_force":10.57344,"subtask_id":"reach_peg","tcp_end":[0.50428,0.09133,0.03816],"tcp_start":[0.51054,0.11392,0.05263],"tcp_to_object_dist_end":0.02999,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.50668,-0.08275,0.03535],"object_pos_start":[0.50403,0.06145,0.03553],"object_to_goal_dist_end":0.0086,"object_to_goal_dist_start":0.14158,"object_z_max":0.04071,"peak_contact_force":41.32974,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":579.0,"raw_peak_contact_force":42.79191,"subtask_id":"reach_goal","tcp_end":[0.50044,-0.05372,0.03157],"tcp_start":[0.50046,-0.05351,0.0316],"tcp_to_object_dist_end":0.02994,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":323.0,"n_steps_budget":720.0,"object_pos_end":[0.50771,-0.06852,0.03538],"object_pos_start":[0.50664,-0.08299,0.0353],"object_to_goal_dist_end":0.01459,"object_to_goal_dist_start":0.00867,"object_z_max":0.06687,"peak_contact_force":1.22443,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":637.0,"raw_peak_contact_force":54.0801,"tcp_end":[0.49691,-0.0757,0.12075],"tcp_start":[0.50044,-0.05372,0.03157],"tcp_to_object_dist_end":0.08635,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03774,"average_solve_count":265.0,"average_success_count":265.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.04846,"contact_1.contact_force":13.36912,"contact_1.contact_speed":0.0167,"descend_1.speed":0.03184,"push_1.push_speed":0.0278},"optimized_scores":{"best_composite_score":0.16401,"best_fitness_score":0.50401,"best_task_score":0.54874},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":234.0,"contact_point_centroid":[0.50059,-0.06751,0.0602],"force_p95":56.26693,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.18385,"mean_force":41.24897,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49756,-0.05661,0.05939]},{"body_a":"peg","body_b":"channel_base_body","contact_count":260.0,"contact_point_centroid":[0.50592,-0.10068,0.06447],"force_p95":56.0923,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.12971,"mean_force":37.12187,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49755,-0.05764,0.06297]},{"body_a":"attachment","body_b":"peg","contact_count":327.0,"contact_point_centroid":[0.50427,0.01618,0.04207],"force_p95":23.71687,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.12727,"mean_force":5.30793,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50069,0.02787,0.0304]},{"body_a":"peg","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.50503,-0.10028,0.02831],"force_p95":30.6225,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.2668,"mean_force":13.6383,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50208,-0.05229,0.03021]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":223.0,"contact_point_centroid":[0.52524,0.00516,0.03892],"force_p95":23.8351,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.99581,"mean_force":5.63315,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50056,0.03463,0.03042]},{"body_a":"peg","body_b":"channel_base_body","contact_count":161.0,"contact_point_centroid":[0.50589,-0.02044,0.00987],"force_p95":13.98868,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.70908,"mean_force":3.95029,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5008,0.02262,0.03041]},{"body_a":"peg","body_b":"channel_base_body","contact_count":974.0,"contact_point_centroid":[0.50469,0.07313,0.00995],"force_p95":4.24521,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.82668,"mean_force":2.41643,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50303,0.11781,0.04054]},{"body_a":"attachment","body_b":"peg","contact_count":954.0,"contact_point_centroid":[0.50438,0.10515,0.04112],"force_p95":3.92559,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.35143,"mean_force":2.12536,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50293,0.11704,0.0401]},{"body_a":"peg","body_b":"channel_base_body","contact_count":38.0,"contact_point_centroid":[0.50035,-0.06352,0.0084],"force_p95":4.10787,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.33116,"mean_force":1.14359,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49731,-0.07328,0.11243]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":43.0,"contact_point_centroid":[0.52543,-0.07543,0.02784],"force_p95":2.43565,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.1039,"mean_force":0.76315,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49731,-0.07295,0.11146]},{"body_a":"peg","body_b":"channel_base_body","contact_count":362.0,"contact_point_centroid":[0.50548,0.10474,0.00936],"force_p95":0.58323,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57761,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50928,0.16891,0.19746]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50029,0.19824,0.29461]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":44.0,"contact_point_centroid":[0.52501,0.08115,0.0311],"force_p95":0.8847,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.35588,"mean_force":0.59241,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5027,0.11078,0.03717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":111.0,"contact_point_centroid":[0.50592,0.10401,0.00939],"force_p95":0.57505,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.54625,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51318,0.13837,0.0816]}],"total_contact_groups":14},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5074,-0.0739,0.03544],"final_tcp_position":[0.49716,-0.07558,0.12072],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":59.18385,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":389.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10465,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18485,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.5405,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":394.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51894,0.14098,0.10647],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08224,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":111.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.10467,0.03384],"object_pos_start":[0.506,0.10465,0.03384],"object_to_goal_dist_end":0.18486,"object_to_goal_dist_start":0.18485,"object_z_max":0.03384,"peak_contact_force":0.54322,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":111.0,"raw_peak_contact_force":0.57865,"subtask_id":"reach_peg","tcp_end":[0.50742,0.13592,0.05359],"tcp_start":[0.51894,0.14098,0.10647],"tcp_to_object_dist_end":0.037,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50699,0.07509,0.03531],"object_pos_start":[0.50583,0.10467,0.03384],"object_to_goal_dist_end":0.15532,"object_to_goal_dist_start":0.18486,"object_z_max":0.03696,"peak_contact_force":1.76931,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1972.0,"raw_peak_contact_force":9.82668,"subtask_id":"reach_peg","tcp_end":[0.50233,0.10475,0.03415],"tcp_start":[0.50742,0.13592,0.05359],"tcp_to_object_dist_end":0.03004,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.50525,-0.08291,0.03645],"object_pos_start":[0.50699,0.07509,0.03531],"object_to_goal_dist_end":0.00698,"object_to_goal_dist_start":0.15532,"object_z_max":0.03671,"peak_contact_force":22.68959,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":717.0,"raw_peak_contact_force":40.12727,"subtask_id":"reach_goal","tcp_end":[0.50201,-0.05332,0.03014],"tcp_start":[0.50205,-0.0531,0.03018],"tcp_to_object_dist_end":0.03043,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":327.0,"n_steps_budget":720.0,"object_pos_end":[0.5074,-0.0739,0.03544],"object_pos_start":[0.50504,-0.08314,0.03643],"object_to_goal_dist_end":0.01062,"object_to_goal_dist_start":0.00693,"object_z_max":0.06975,"peak_contact_force":0.40344,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":575.0,"raw_peak_contact_force":59.18385,"tcp_end":[0.49716,-0.07558,0.12072],"tcp_start":[0.50201,-0.05332,0.03014],"tcp_to_object_dist_end":0.08591,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23077,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06608,"contact_1.contact_force":6.01063,"contact_1.contact_speed":0.02853,"descend_1.speed":0.03763,"push_1.push_speed":0.04442},"optimized_scores":{"best_composite_score":0.52634,"best_fitness_score":0.66634,"best_task_score":0.90281},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":221.0,"contact_point_centroid":[0.50021,-0.06765,0.06057],"force_p95":50.90316,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.14469,"mean_force":37.30611,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4957,-0.05721,0.05982]},{"body_a":"peg","body_b":"channel_base_body","contact_count":246.0,"contact_point_centroid":[0.50856,-0.10059,0.06432],"force_p95":50.7647,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.11043,"mean_force":33.00496,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49576,-0.0582,0.06327]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.5063,-0.10031,0.06035],"force_p95":40.66809,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.83707,"mean_force":33.87453,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4996,-0.05284,0.03248]},{"body_a":"attachment","body_b":"peg","contact_count":294.0,"contact_point_centroid":[0.50236,0.0023,0.04645],"force_p95":26.4621,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.58501,"mean_force":8.70143,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49699,0.01367,0.03462]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":328.0,"contact_point_centroid":[0.52526,-0.01368,0.03354],"force_p95":23.24789,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.58476,"mean_force":5.50285,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49695,0.01426,0.03463]},{"body_a":"peg","body_b":"channel_base_body","contact_count":115.0,"contact_point_centroid":[0.50675,-0.02263,0.00993],"force_p95":21.86954,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.05816,"mean_force":8.86559,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49682,0.02177,0.03505]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":100.0,"contact_point_centroid":[0.52525,-0.08032,0.04371],"force_p95":8.27141,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.1405,"mean_force":3.28325,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49577,-0.06374,0.08103]},{"body_a":"peg","body_b":"channel_base_body","contact_count":334.0,"contact_point_centroid":[0.50493,0.04516,0.00988],"force_p95":4.70817,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.04146,"mean_force":2.91984,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49675,0.08899,0.04421]},{"body_a":"attachment","body_b":"peg","contact_count":292.0,"contact_point_centroid":[0.50018,0.07608,0.04457],"force_p95":4.38576,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.72654,"mean_force":2.90306,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49666,0.08759,0.04335]},{"body_a":"peg","body_b":"channel_base_body","contact_count":41.0,"contact_point_centroid":[0.49352,-0.07389,0.00869],"force_p95":4.47107,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.23795,"mean_force":1.08747,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49665,-0.07381,0.11417]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47492,-0.07281,0.04665],"force_p95":1.86548,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.45323,"mean_force":0.80377,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4956,-0.06201,0.07789]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.503,0.06741,0.00932],"force_p95":0.61927,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.57001,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49947,0.15304,0.20819]},{"body_a":"peg","body_b":"channel_base_body","contact_count":147.0,"contact_point_centroid":[0.50317,0.06775,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55198,"mean_force":0.54667,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49901,0.10388,0.08918]}],"total_contact_groups":13},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5067,-0.07699,0.03572],"final_tcp_position":[0.4968,-0.0757,0.12084],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":3919.25596,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":384.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.0675,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54492,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":368.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.50007,0.10805,0.1225],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":147.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06745,0.0338],"object_pos_start":[0.50304,0.0675,0.0338],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14766,"object_z_max":0.0338,"peak_contact_force":0.54359,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":147.0,"raw_peak_contact_force":0.55198,"subtask_id":"reach_peg","tcp_end":[0.49921,0.09971,0.05315],"tcp_start":[0.50007,0.10805,0.1225],"tcp_to_object_dist_end":0.03781,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,0.05279,0.03593],"object_pos_start":[0.50309,0.06745,0.0338],"object_to_goal_dist_end":0.13304,"object_to_goal_dist_start":0.14762,"object_z_max":0.03604,"peak_contact_force":3919.25596,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":626.0,"raw_peak_contact_force":6.04146,"subtask_id":"reach_peg","tcp_end":[0.49711,0.08085,0.04008],"tcp_start":[0.49921,0.09971,0.05315],"tcp_to_object_dist_end":0.03004,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.50651,-0.0824,0.03593],"object_pos_start":[0.50701,0.05279,0.03593],"object_to_goal_dist_end":0.00804,"object_to_goal_dist_start":0.13304,"object_z_max":0.03717,"peak_contact_force":40.83707,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":742.0,"raw_peak_contact_force":40.83707,"subtask_id":"reach_goal","tcp_end":[0.49959,-0.05368,0.03239],"tcp_start":[0.49962,-0.05348,0.03244],"tcp_to_object_dist_end":0.02976,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":319.0,"n_steps_budget":720.0,"object_pos_end":[0.5067,-0.07699,0.03572],"object_pos_start":[0.50643,-0.08265,0.0359],"object_to_goal_dist_end":0.0085,"object_to_goal_dist_start":0.00807,"object_z_max":0.06711,"peak_contact_force":0.4864,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":631.0,"raw_peak_contact_force":54.14469,"tcp_end":[0.4968,-0.0757,0.12084],"tcp_start":[0.49959,-0.05368,0.03239],"tcp_to_object_dist_end":0.0857,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```