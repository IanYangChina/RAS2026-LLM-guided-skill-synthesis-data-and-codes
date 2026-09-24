## Search State

- **Seed**: 4
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.2795 | 0.40 | ❌ rejected |
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2542 | 0.58 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3784 | 0.00 | ❌ rejected |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3973 | 0.60 | ✅ accepted |
| 0 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3739 | 0.56 | ✅ accepted |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.280) — your mutation base

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

- **Composite score**: 0.280
- **task_score** (E): 0.403
- **fitness_score**: 0.453  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.267
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1865 |
| descend_1 | 0.33 | 1.00 | 0.1047 |
| contact_1 | 1.00 | 1.00 | 0.0011 |
| push_1 | 0.00 | 1.00 | 0.0002 |
| retract_1 | 1.00 | 1.00 | 0.1801 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.124, 0.132) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.547 | 3.242 |
| descend_1 | descend | 0.33 / step_budget | (0.516, 0.124, 0.132)→(0.502, 0.114, 0.029) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.667 | 1.492 | 1.492 |
| contact_1 | contact | 1.00 / force_exceeded | (0.502, 0.114, 0.029)→(0.502, 0.114, 0.028) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 2.000 | 7.439 | 7.439 |
| push_1 | push | 0.00 / guard_failure | (0.503, 0.083, 0.026)→(0.503, 0.083, 0.026) | (0.505, 0.084, 0.034)→(0.506, 0.053, 0.036) | 0.164→0.134 | 1.00 / 2.667 | 31.323 | 139.379 |
| retract_1 | retract | 1.00 / step_budget | (0.503, 0.083, 0.026)→(0.497, -0.066, 0.126) | (0.506, 0.053, 0.036)→(0.506, -0.028, 0.024) | 0.133→0.054 | 1.00 / 1.000 | 0.636 | 108.974 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.912
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.470
- phase_score: 0.516
- phase_breakdown.reach_peg_score: 0.250
- phase_breakdown.reach_goal_score: 0.629

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.497
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.545
- **Median Q (composite search score)**: 0.256
- **K-run variance**: 0.0187
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.376


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.81696,"average_solve_count":224.0,"average_success_count":224.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0762,"contact_1.contact_force":4.45374,"contact_1.speed":0.02613,"descend_1.contact_force":1.00206,"descend_1.speed":0.01976,"push_1.lateral_offset_y":-0.00518,"push_1.push_speed":0.0354},"optimized_scores":{"best_composite_score":0.12492,"best_fitness_score":0.36492,"best_task_score":0.19496},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53955,0.08854,0.05999],"force_p95":150.40813,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.5653,"mean_force":108.6659,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50332,0.09249,0.02493]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.53961,0.08791,0.06],"force_p95":113.8294,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.07531,"mean_force":84.61623,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50338,0.09188,0.02494]},{"body_a":"attachment","body_b":"peg","contact_count":113.0,"contact_point_centroid":[0.50282,0.04442,0.04523],"force_p95":21.33326,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.95027,"mean_force":4.414,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49981,0.0558,0.04537]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":98.0,"contact_point_centroid":[0.52514,0.02629,0.03036],"force_p95":18.79098,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.89558,"mean_force":3.43574,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49962,0.05284,0.04713]},{"body_a":"peg","body_b":"channel_base_body","contact_count":421.0,"contact_point_centroid":[0.50616,-0.00471,0.00915],"force_p95":6.42728,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.21843,"mean_force":1.27338,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49856,0.00245,0.0805]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50148,0.06925,0.00972],"force_p95":10.0788,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.08266,"mean_force":2.73982,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50302,0.1044,0.02629]},{"body_a":"attachment","body_b":"peg","contact_count":37.0,"contact_point_centroid":[0.50659,0.0889,0.04843],"force_p95":9.24998,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.96367,"mean_force":2.33611,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50299,0.10058,0.02572]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52529,0.07086,0.02139],"force_p95":4.22388,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.07337,"mean_force":0.96345,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5029,0.10072,0.02564]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.49755,0.07661,0.00938],"force_p95":4.56026,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.97552,"mean_force":1.91104,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50381,0.11077,0.02803]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50542,0.09882,0.03692],"force_p95":4.1149,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.4247,"mean_force":1.93279,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50376,0.11075,0.02797]},{"body_a":"peg","body_b":"channel_base_body","contact_count":337.0,"contact_point_centroid":[0.50554,0.08094,0.00934],"force_p95":0.56935,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.59204,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51448,0.15796,0.21011]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50067,0.19725,0.29402]},{"body_a":"peg","body_b":"channel_base_body","contact_count":548.0,"contact_point_centroid":[0.50601,0.08082,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55014,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51524,0.11542,0.07925]}],"total_contact_groups":13},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50617,-0.0241,0.02416],"final_tcp_position":[0.49733,-0.06613,0.12619],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":154.5653,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54472,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":373.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52867,0.12056,0.13221],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10853,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":548.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":0.54819,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":548.0,"raw_peak_contact_force":0.55014,"subtask_id":"reach_peg","tcp_end":[0.50402,0.11083,0.02829],"tcp_start":[0.52867,0.12056,0.13221],"tcp_to_object_dist_end":0.03053,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,0.08074,0.03384],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16096,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":4.97552,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":9.0,"raw_peak_contact_force":4.97552,"subtask_id":"reach_peg","tcp_end":[0.50352,0.11064,0.0277],"tcp_start":[0.50402,0.11083,0.02829],"tcp_to_object_dist_end":0.03062,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.50673,0.06291,0.03546],"object_pos_start":[0.50592,0.08074,0.03384],"object_to_goal_dist_end":0.14314,"object_to_goal_dist_start":0.16096,"object_z_max":0.03556,"peak_contact_force":6.36494,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":100.0,"raw_peak_contact_force":154.5653,"subtask_id":"reach_goal","tcp_end":[0.50338,0.09203,0.02494],"tcp_start":[0.50335,0.09221,0.02494],"tcp_to_object_dist_end":0.03114,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":510.0,"n_steps_budget":1000.0,"object_pos_end":[0.50617,-0.0241,0.02416],"object_pos_start":[0.50669,0.06214,0.03548],"object_to_goal_dist_end":0.05843,"object_to_goal_dist_start":0.14237,"object_z_max":0.04079,"peak_contact_force":0.5693,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":634.0,"raw_peak_contact_force":117.07531,"subtask_id":"reach_goal","tcp_end":[0.49733,-0.06613,0.12619],"tcp_start":[0.50338,0.09203,0.02494],"tcp_to_object_dist_end":0.1107,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37158,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06044,"contact_1.contact_force":5.121,"contact_1.speed":0.02434,"descend_1.contact_force":2.21701,"descend_1.speed":0.03311,"push_1.lateral_offset_y":-0.00869,"push_1.push_speed":0.01454},"optimized_scores":{"best_composite_score":0.45729,"best_fitness_score":0.49729,"best_task_score":0.46971},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52502,0.06461,0.06],"force_p95":130.79413,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.64615,"mean_force":102.67361,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50764,0.06438,0.02713]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.06415,0.06],"force_p95":113.39222,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":113.39222,"mean_force":113.39222,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50759,0.06392,0.02707]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":52.0,"contact_point_centroid":[0.52521,0.06472,0.03559],"force_p95":2.72579,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.44044,"mean_force":1.20667,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50432,0.09487,0.02728]},{"body_a":"attachment","body_b":"peg","contact_count":146.0,"contact_point_centroid":[0.50603,0.08707,0.03969],"force_p95":3.64342,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.27745,"mean_force":1.23665,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50427,0.09873,0.02781]},{"body_a":"attachment","body_b":"peg","contact_count":77.0,"contact_point_centroid":[0.50463,0.02354,0.04598],"force_p95":8.79561,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.74212,"mean_force":2.34237,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50333,0.03523,0.04591]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.5251,0.01879,0.05989],"force_p95":9.61262,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.62766,"mean_force":1.8611,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50525,0.04778,0.03782]},{"body_a":"peg","body_b":"channel_base_body","contact_count":393.0,"contact_point_centroid":[0.50632,-0.01875,0.00938],"force_p95":3.24173,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.44251,"mean_force":0.93686,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50081,-0.00742,0.07876]},{"body_a":"peg","body_b":"channel_base_body","contact_count":105.0,"contact_point_centroid":[0.50391,0.06692,0.00975],"force_p95":3.92953,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.11303,"mean_force":1.84815,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50407,0.10172,0.02798]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.49999,0.10022,0.00934],"force_p95":4.62331,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.80643,"mean_force":1.27955,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50331,0.13426,0.03157]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50508,0.12228,0.04076],"force_p95":5.13296,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.49574,"mean_force":2.40521,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50334,0.13421,0.03161]},{"body_a":"peg","body_b":"channel_base_body","contact_count":429.0,"contact_point_centroid":[0.50588,0.10448,0.00939],"force_p95":0.57567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33431,"mean_force":0.55468,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51017,0.13756,0.07409]},{"body_a":"peg","body_b":"channel_base_body","contact_count":341.0,"contact_point_centroid":[0.50556,0.10457,0.00936],"force_p95":0.59954,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.5795,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50929,0.16905,0.20337]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50545,0.12266,0.04159],"force_p95":2.87906,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.11219,"mean_force":1.46583,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50399,0.13461,0.03346]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50032,0.1982,0.29465]}],"total_contact_groups":14},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50614,-0.04124,0.02415],"final_tcp_position":[0.49773,-0.06701,0.12529],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1435.48072,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":368.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.1046,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55391,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":373.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51889,0.14131,0.1181],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09284,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":429.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.1046,0.03373],"object_pos_start":[0.50584,0.1046,0.03383],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.1848,"object_z_max":0.03384,"peak_contact_force":3.33431,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":432.0,"raw_peak_contact_force":3.33431,"subtask_id":"reach_peg","tcp_end":[0.50381,0.13452,0.03218],"tcp_start":[0.51889,0.14131,0.1181],"tcp_to_object_dist_end":0.03003,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.50558,0.10397,0.03391],"object_pos_start":[0.50585,0.1046,0.03373],"object_to_goal_dist_end":0.18416,"object_to_goal_dist_start":0.1848,"object_z_max":0.03382,"peak_contact_force":5.80643,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":15.0,"raw_peak_contact_force":5.80643,"subtask_id":"reach_peg","tcp_end":[0.50282,0.13376,0.031],"tcp_start":[0.50381,0.13452,0.03218],"tcp_to_object_dist_end":0.03005,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":185.0,"n_steps_budget":1000.0,"object_pos_end":[0.50717,0.03467,0.0353],"object_pos_start":[0.50558,0.10397,0.03391],"object_to_goal_dist_end":0.11499,"object_to_goal_dist_start":0.18416,"object_z_max":0.03677,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":306.0,"raw_peak_contact_force":132.64615,"subtask_id":"reach_goal","tcp_end":[0.50759,0.06392,0.02707],"tcp_start":[0.50763,0.06411,0.02711],"tcp_to_object_dist_end":0.0304,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":450.0,"n_steps_budget":1000.0,"object_pos_end":[0.50614,-0.04124,0.02415],"object_pos_start":[0.50717,0.03388,0.0352],"object_to_goal_dist_end":0.04232,"object_to_goal_dist_start":0.1142,"object_z_max":0.04079,"peak_contact_force":0.67238,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":483.0,"raw_peak_contact_force":113.39222,"subtask_id":"reach_goal","tcp_end":[0.49773,-0.06701,0.12529],"tcp_start":[0.50759,0.06392,0.02707],"tcp_to_object_dist_end":0.10471,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40805,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08997,"contact_1.contact_force":8.45047,"contact_1.speed":0.0276,"descend_1.contact_force":2.88434,"descend_1.speed":0.03517,"push_1.lateral_offset_y":-0.01009,"push_1.push_speed":0.02556},"optimized_scores":{"best_composite_score":0.25636,"best_fitness_score":0.49636,"best_task_score":0.54477},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53389,0.08889,0.05996],"force_p95":126.59362,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.92582,"mean_force":96.90991,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4978,0.09284,0.02472]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.53395,0.08819,0.05995],"force_p95":91.60759,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":96.45558,"mean_force":67.76991,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49787,0.09216,0.02469]},{"body_a":"attachment","body_b":"peg","contact_count":91.0,"contact_point_centroid":[0.49966,0.04481,0.04473],"force_p95":19.2746,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.59473,"mean_force":5.79799,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49543,0.05575,0.04534]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":96.0,"contact_point_centroid":[0.52539,0.02499,0.02652],"force_p95":17.73438,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.75556,"mean_force":4.83982,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49511,0.04573,0.05149]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.50622,0.0501,0.00958],"force_p95":17.48243,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.7733,"mean_force":8.06751,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49802,0.09656,0.02554]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50258,0.08357,0.0511],"force_p95":17.20567,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.32875,"mean_force":7.8033,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49793,0.09541,0.02527]},{"body_a":"peg","body_b":"channel_base_body","contact_count":432.0,"contact_point_centroid":[0.50502,-0.00169,0.00892],"force_p95":5.43795,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.41008,"mean_force":1.22032,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49594,0.00429,0.07936]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49942,0.05534,0.00933],"force_p95":10.49065,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.5356,"mean_force":3.17854,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49865,0.09729,0.02631]},{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.50227,0.08536,0.04765],"force_p95":10.83752,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.16913,"mean_force":6.56907,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4986,0.09725,0.02626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":330.0,"contact_point_centroid":[0.50309,0.06739,0.00931],"force_p95":0.64579,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.5727,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49955,0.15358,0.21982]},{"body_a":"peg","body_b":"channel_base_body","contact_count":696.0,"contact_point_centroid":[0.503,0.06749,0.00938],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5929,"mean_force":0.54672,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4982,0.10294,0.08396]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.4749,0.04591,0.05903],"force_p95":0.37464,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38303,"mean_force":0.27502,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49592,0.07732,0.03183]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50275,0.08552,0.05205],"force_p95":0.19935,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19935,"mean_force":0.19935,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4989,0.09742,0.02676]}],"total_contact_groups":13},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50535,-0.0197,0.02414],"final_tcp_position":[0.4969,-0.06621,0.12625],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":130.92582,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":346.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06746,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14762,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54161,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":330.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_peg","tcp_end":[0.50019,0.10916,0.14552],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.50306,0.06749,0.03379],"object_pos_start":[0.50301,0.06746,0.0338],"object_to_goal_dist_end":0.14765,"object_to_goal_dist_start":0.14762,"object_z_max":0.0338,"peak_contact_force":0.5929,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":697.0,"raw_peak_contact_force":0.5929,"subtask_id":"reach_peg","tcp_end":[0.4989,0.0974,0.02661],"tcp_start":[0.50019,0.10916,0.14552],"tcp_to_object_dist_end":0.03104,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50318,0.06734,0.03377],"object_pos_start":[0.50306,0.06749,0.03379],"object_to_goal_dist_end":0.1475,"object_to_goal_dist_start":0.14765,"object_z_max":0.03379,"peak_contact_force":11.5356,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":10.0,"raw_peak_contact_force":11.5356,"subtask_id":"reach_peg","tcp_end":[0.49834,0.09707,0.02597],"tcp_start":[0.4989,0.0974,0.02661],"tcp_to_object_dist_end":0.03112,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.50333,0.0626,0.0363],"object_pos_start":[0.50318,0.06734,0.03377],"object_to_goal_dist_end":0.14269,"object_to_goal_dist_start":0.1475,"object_z_max":0.0363,"peak_contact_force":87.60379,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":27.0,"raw_peak_contact_force":130.92582,"subtask_id":"reach_goal","tcp_end":[0.49785,0.09239,0.02468],"tcp_start":[0.49783,0.09257,0.0247],"tcp_to_object_dist_end":0.03244,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":512.0,"n_steps_budget":1000.0,"object_pos_end":[0.50535,-0.0197,0.02414],"object_pos_start":[0.50328,0.06173,0.03624],"object_to_goal_dist_end":0.06258,"object_to_goal_dist_start":0.14182,"object_z_max":0.04078,"peak_contact_force":0.66717,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":629.0,"raw_peak_contact_force":96.45558,"subtask_id":"reach_goal","tcp_end":[0.4969,-0.06621,0.12625],"tcp_start":[0.49785,0.09239,0.02468],"tcp_to_object_dist_end":0.11252,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```