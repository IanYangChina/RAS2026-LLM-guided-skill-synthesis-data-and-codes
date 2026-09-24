## Search State

- **Seed**: 8
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.0630 | 0.43 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.1931 | 0.43 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.0281 | 0.46 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0915 | 0.47 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1052 | 0.52 | ❌ rejected |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
| `object` | offset from object initial position (0.48615778212844485, 0.11898214746703403, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48615778212844485, -0.04101785253296597, 0.04) | final destination targets |
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

## Current Skill (Q=0.063) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: pre_push
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.1
  weight: 0.3
- id: push_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.003
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: pre_push
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    lateral_offset:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.14
      - 0.18
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
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 50.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push_goal
- id: retract_tool
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
    - 0.05
    tolerance: 0.01
    orientation:
      mode: keep_current
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
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - lateral_offset: status=consumed; consumers=target.offset.x (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=50.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_tool** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.063
- **task_score** (E): 0.435
- **fitness_score**: 0.223  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1786 |
| descend_to_contact | 1.00 | 1.00 | 0.1110 |
| push_to_goal | 1.00 | 1.00 | 0.0181 |
| retract_tool | 1.00 | 1.00 | 0.1800 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.115, 0.147) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.197 | 4.952 |
| descend_to_contact | descend | 1.00 / step_budget | (0.513, 0.115, 0.147)→(0.500, 0.109, 0.038) | (0.503, 0.080, 0.034)→(0.503, 0.079, 0.034) | 0.160→0.159 | 1.00 / 2.000 | 1148.941 | 894.802 |
| push_to_goal | push | 1.00 / force_exceeded | (0.500, 0.109, 0.038)→(0.512, 0.099, 0.029) | (0.503, 0.079, 0.034)→(0.505, 0.068, 0.038) | 0.159→0.148 | 1.00 / 1.000 | 0.492 | 450.832 |
| retract_tool | retract | 1.00 / step_budget | (0.512, 0.099, 0.029)→(0.497, -0.072, 0.083) | (0.505, 0.068, 0.038)→(0.501, -0.045, 0.027) | 0.148→0.038 | 1.00 / 1.000 | 0.539 | 3.526 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.907
- phase_score: 0.109
- phase_breakdown.pre_push_score: 0.125
- phase_breakdown.push_goal_score: 0.102

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.428
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.907
- **Median Q (composite search score)**: -0.013
- **K-run variance**: 0.0215
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.275


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56849,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.10492,"descend_to_contact.descend_speed":0.03072,"descend_to_contact.descend_tolerance":0.00599,"push_to_goal.lateral_offset":0.00893,"push_to_goal.push_force_threshold":32.28492,"push_to_goal.push_speed":0.05058,"retract_tool.retract_speed":0.15404},"optimized_scores":{"best_composite_score":0.26818,"best_fitness_score":0.42818,"best_task_score":0.90741},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54137,0.11989,0.05959],"force_p95":1307.1691,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1308.58539,"mean_force":1294.42255,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51377,0.13268,0.02031]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":59.0,"contact_point_centroid":[0.54386,0.11989,0.05964],"force_p95":290.0175,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":575.15227,"mean_force":128.05715,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.51617,0.12999,0.01995]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":62.0,"contact_point_centroid":[0.52504,0.11965,0.05365],"force_p95":155.3802,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":164.13312,"mean_force":126.74018,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.51105,0.12123,0.0237]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.50419,0.10999,0.00971],"force_p95":32.88046,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.81306,"mean_force":7.16133,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50273,0.14043,0.02925]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49842,0.13327,0.0491],"force_p95":33.14703,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.66308,"mean_force":9.66917,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49713,0.14433,0.03303]},{"body_a":"attachment","body_b":"peg","contact_count":361.0,"contact_point_centroid":[0.50376,0.01556,0.05147],"force_p95":14.76559,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.6519,"mean_force":5.5063,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.50453,0.02722,0.04951]},{"body_a":"peg","body_b":"channel_base_body","contact_count":763.0,"contact_point_centroid":[0.49737,-0.00779,0.00945],"force_p95":10.64175,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.92558,"mean_force":2.60647,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.50477,0.02994,0.0497]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":215.0,"contact_point_centroid":[0.47494,-0.03374,0.03611],"force_p95":10.24115,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.54426,"mean_force":3.69751,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.50294,0.00427,0.05743]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52513,0.06783,0.03492],"force_p95":6.47548,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.99656,"mean_force":1.70125,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.51142,0.11271,0.02352]},{"body_a":"peg","body_b":"channel_base_body","contact_count":723.0,"contact_point_centroid":[0.49628,0.11759,0.00947],"force_p95":0.62761,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.21478,"mean_force":0.58284,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48677,0.15009,0.0903]},{"body_a":"attachment","body_b":"peg","contact_count":29.0,"contact_point_centroid":[0.49449,0.1367,0.05928],"force_p95":3.68842,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.75647,"mean_force":1.35343,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49096,0.14868,0.04248]},{"body_a":"peg","body_b":"channel_base_body","contact_count":450.0,"contact_point_centroid":[0.49625,0.11915,0.00942],"force_p95":0.61607,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5566,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49132,0.17526,0.2208]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49947,0.19897,0.29757]}],"total_contact_groups":13},"final_pose_error":0.01225,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4931,-0.05307,0.03414],"final_tcp_position":[0.49727,-0.07082,0.08237],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":1308.58539,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":475.0,"n_steps_budget":1000.0,"object_pos_end":[0.49603,0.1194,0.03414],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19953,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.02549,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":752.0,"raw_peak_contact_force":4.21478,"subtask_id":"pre_push","tcp_end":[0.48453,0.15251,0.14912],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":723.0,"n_steps_budget":1000.0,"object_pos_end":[0.49621,0.11862,0.0345],"object_pos_start":[0.49603,0.1194,0.03414],"object_to_goal_dist_end":0.19873,"object_to_goal_dist_start":0.19953,"object_z_max":0.0347,"peak_contact_force":1308.58539,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":20.0,"raw_peak_contact_force":1308.58539,"subtask_id":"pre_push","tcp_end":[0.49155,0.14851,0.03606],"tcp_start":[0.48453,0.15251,0.14912],"tcp_to_object_dist_end":0.03029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":17.0,"n_steps_budget":1000.0,"object_pos_end":[0.50099,0.09848,0.03793],"object_pos_start":[0.49621,0.11862,0.0345],"object_to_goal_dist_end":0.17849,"object_to_goal_dist_start":0.19873,"object_z_max":0.03785,"peak_contact_force":0.02288,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1476.0,"raw_peak_contact_force":575.15227,"subtask_id":"push_goal","tcp_end":[0.51549,0.13178,0.01859],"tcp_start":[0.49155,0.14851,0.03606],"tcp_to_object_dist_end":0.04115,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":872.0,"n_steps_budget":930.0,"object_pos_end":[0.4931,-0.05307,0.03414],"object_pos_start":[0.50099,0.09848,0.03793],"object_to_goal_dist_end":0.02841,"object_to_goal_dist_start":0.17849,"object_z_max":0.04081,"peak_contact_force":0.51701,"phase_name":"retract_tool","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":474.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.49727,-0.07082,0.08237],"tcp_start":[0.51549,0.13178,0.01859],"tcp_to_object_dist_end":0.05156,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17391,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.13978,"descend_to_contact.descend_speed":0.02703,"descend_to_contact.descend_tolerance":0.00561,"push_to_goal.lateral_offset":0.00101,"push_to_goal.push_force_threshold":36.07615,"push_to_goal.push_speed":0.04116,"retract_tool.retract_speed":0.08632},"optimized_scores":{"best_composite_score":-0.01302,"best_fitness_score":0.14698,"best_task_score":0.25453},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52571,0.08733,0.0599],"force_p95":1343.67689,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1343.67689,"mean_force":1343.67689,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51053,0.08642,0.03399]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52631,0.08505,0.0598],"force_p95":245.27694,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":416.52648,"mean_force":93.47741,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.51065,0.08277,0.02974]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50757,0.07825,0.04682],"force_p95":63.86225,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.31053,"mean_force":26.55293,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50694,0.08971,0.03589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50735,0.04609,0.0096],"force_p95":64.26544,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.82587,"mean_force":29.74801,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50461,0.09186,0.03727]},{"body_a":"peg","body_b":"channel_base_body","contact_count":962.0,"contact_point_centroid":[0.50378,-0.03046,0.00917],"force_p95":2.92691,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.69347,"mean_force":0.8492,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.50232,0.00441,0.05614]},{"body_a":"attachment","body_b":"peg","contact_count":139.0,"contact_point_centroid":[0.50447,-0.00086,0.05547],"force_p95":5.81113,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.06528,"mean_force":2.09226,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.50306,0.0109,0.05417]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50606,0.06232,0.00938],"force_p95":0.55285,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.31899,"mean_force":0.56556,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51303,0.09594,0.09112]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.50644,0.08088,0.05815],"force_p95":3.3699,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.97396,"mean_force":1.33281,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50416,0.09295,0.04098]},{"body_a":"peg","body_b":"channel_base_body","contact_count":559.0,"contact_point_centroid":[0.50577,0.06303,0.00936],"force_p95":0.56528,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57077,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51191,0.14766,0.21814]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52511,0.05909,0.06],"force_p95":3.39717,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.39717,"mean_force":3.39717,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51053,0.08642,0.03399]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5,0.19777,0.29639]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":67.0,"contact_point_centroid":[0.52537,-0.00594,0.05676],"force_p95":1.16397,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.82772,"mean_force":0.31347,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.50719,0.06262,0.03609]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47495,-0.00207,0.05833],"force_p95":1.1437,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.15577,"mean_force":1.03513,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.50698,0.07598,0.03092]}],"total_contact_groups":13},"final_pose_error":0.01201,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50358,-0.05365,0.02405],"final_tcp_position":[0.49706,-0.07119,0.08239],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":1343.67689,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":587.0,"n_steps_budget":870.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.02539,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":573.0,"raw_peak_contact_force":4.31899,"subtask_id":"pre_push","tcp_end":[0.52453,0.09953,0.14552],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11899,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,0.06279,0.03422],"object_pos_start":[0.50602,0.06295,0.03381],"object_to_goal_dist_end":0.14304,"object_to_goal_dist_start":0.14321,"object_z_max":0.03421,"peak_contact_force":1343.67689,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13.0,"raw_peak_contact_force":1343.67689,"subtask_id":"pre_push","tcp_end":[0.50365,0.09279,0.03806],"tcp_start":[0.52453,0.09953,0.14552],"tcp_to_object_dist_end":0.03035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.5073,0.05493,0.0388],"object_pos_start":[0.5061,0.06279,0.03422],"object_to_goal_dist_end":0.13513,"object_to_goal_dist_start":0.14304,"object_z_max":0.03824,"peak_contact_force":0.77007,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1190.0,"raw_peak_contact_force":416.52648,"subtask_id":"push_goal","tcp_end":[0.51188,0.0849,0.03324],"tcp_start":[0.50365,0.09279,0.03806],"tcp_to_object_dist_end":0.03082,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50358,-0.05365,0.02405],"object_pos_start":[0.5073,0.05493,0.0388],"object_to_goal_dist_end":0.03101,"object_to_goal_dist_start":0.13513,"object_z_max":0.04216,"peak_contact_force":0.55105,"phase_name":"retract_tool","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":593.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.49706,-0.07119,0.08239],"tcp_start":[0.51188,0.0849,0.03324],"tcp_to_object_dist_end":0.06127,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59155,"average_solve_count":142.0,"average_success_count":142.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.07998,"descend_to_contact.descend_speed":0.04507,"descend_to_contact.descend_tolerance":0.00528,"push_to_goal.lateral_offset":0.00288,"push_to_goal.push_force_threshold":32.87959,"push_to_goal.push_speed":0.04733,"retract_tool.retract_speed":0.10211},"optimized_scores":{"best_composite_score":-0.06623,"best_fitness_score":0.09377,"best_task_score":0.14258},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":14.0,"contact_point_centroid":[0.52568,0.07984,0.0599],"force_p95":256.50894,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":360.8181,"mean_force":66.02105,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.50997,0.07865,0.03178]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50569,0.07405,0.0419],"force_p95":31.74416,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.14319,"mean_force":28.1529,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50479,0.08601,0.0379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50893,0.04508,0.00959],"force_p95":28.7796,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.03534,"mean_force":13.23409,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50492,0.0859,0.03785]},{"body_a":"peg","body_b":"channel_base_body","contact_count":892.0,"contact_point_centroid":[0.50242,-0.01431,0.00878],"force_p95":5.7412,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.5105,"mean_force":1.44206,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.50094,-0.00138,0.05847]},{"body_a":"attachment","body_b":"peg","contact_count":222.0,"contact_point_centroid":[0.50338,0.02901,0.04451],"force_p95":6.4399,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.08637,"mean_force":3.59533,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.50336,0.04087,0.04419]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.50614,0.05617,0.00938],"force_p95":0.55048,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.32208,"mean_force":0.56795,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51676,0.08972,0.09112]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50682,0.07454,0.05704],"force_p95":5.52083,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.85876,"mean_force":2.57014,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50475,0.08661,0.04]},{"body_a":"peg","body_b":"channel_base_body","contact_count":622.0,"contact_point_centroid":[0.50592,0.0566,0.00936],"force_p95":0.60057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57211,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51514,0.14439,0.21773]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50005,0.19766,0.2963]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52513,0.05253,0.0109],"force_p95":0.7265,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.7265,"mean_force":0.7265,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50785,0.08287,0.03585]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":24.0,"contact_point_centroid":[0.52564,0.04107,0.03243],"force_p95":0.58328,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.71598,"mean_force":0.35259,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.50882,0.07793,0.03092]}],"total_contact_groups":11},"final_pose_error":0.01009,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50539,-0.02745,0.02413],"final_tcp_position":[0.49684,-0.07331,0.08314],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":794.56172,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":651.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,0.0566,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13688,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.53965,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":525.0,"raw_peak_contact_force":6.32208,"subtask_id":"pre_push","tcp_end":[0.53099,0.0933,0.1449],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":520.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.05643,0.03416],"object_pos_start":[0.50612,0.0566,0.03378],"object_to_goal_dist_end":0.13668,"object_to_goal_dist_start":0.13688,"object_z_max":0.03414,"peak_contact_force":794.56172,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":7.0,"raw_peak_contact_force":32.14319,"subtask_id":"pre_push","tcp_end":[0.50436,0.08652,0.03841],"tcp_start":[0.53099,0.0933,0.1449],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":6.0,"n_steps_budget":1000.0,"object_pos_end":[0.50744,0.05142,0.03626],"object_pos_start":[0.50603,0.05643,0.03416],"object_to_goal_dist_end":0.13168,"object_to_goal_dist_start":0.13668,"object_z_max":0.03583,"peak_contact_force":0.6834,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1152.0,"raw_peak_contact_force":360.8181,"subtask_id":"push_goal","tcp_end":[0.50928,0.0814,0.03505],"tcp_start":[0.50436,0.08652,0.03841],"tcp_to_object_dist_end":0.03007,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":950.0,"n_steps_budget":1000.0,"object_pos_end":[0.50539,-0.02745,0.02413],"object_pos_start":[0.50744,0.05142,0.03626],"object_to_goal_dist_end":0.05516,"object_to_goal_dist_start":0.13168,"object_z_max":0.04068,"peak_contact_force":0.55002,"phase_name":"retract_tool","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":659.0,"raw_peak_contact_force":4.44541,"tcp_end":[0.49684,-0.07331,0.08314],"tcp_start":[0.50928,0.0814,0.03505],"tcp_to_object_dist_end":0.07522,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```