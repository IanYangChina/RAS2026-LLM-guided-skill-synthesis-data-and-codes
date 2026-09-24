## Search State

- **Seed**: 8
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.0915 | 0.47 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1052 | 0.52 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.1028 | 0.52 | ✅ accepted |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1579 | 0.37 | ✅ accepted |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0805 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.47 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.091) — your mutation base

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

- **Composite score**: 0.091
- **task_score** (E): 0.473
- **fitness_score**: 0.501  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1787 |
| descend_to_contact | 1.00 | 1.00 | 0.1111 |
| push_to_goal | 0.00 | 1.00 | 0.0002 |
| retract_tool | 1.00 | 1.00 | 0.0978 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.513, 0.115, 0.147) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.333 | 0.786 | 5.622 |
| descend_to_contact | descend | 1.00 / step_budget | (0.513, 0.115, 0.147)→(0.500, 0.109, 0.037) | (0.503, 0.080, 0.034)→(0.503, 0.079, 0.034) | 0.160→0.159 | 1.00 / 2.667 | 10.722 | 42.798 |
| push_to_goal | push | 0.00 / guard_failure | (0.493, 0.012, 0.034)→(0.493, 0.012, 0.034) | (0.503, 0.079, 0.034)→(0.502, -0.015, 0.039) | 0.159→0.066 | 1.00 / 2.000 | 0.441 | 77.889 |
| retract_tool | retract | 1.00 / step_budget | (0.493, 0.012, 0.034)→(0.496, -0.073, 0.082) | (0.502, -0.015, 0.039)→(0.501, -0.061, 0.032) | 0.065→0.022 | 1.00 / 1.000 | 0.531 | 3.526 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.904
- phase_score: 0.382
- phase_breakdown.pre_push_score: 0.124
- phase_breakdown.push_goal_score: 0.493

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.591
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.904
- **Median Q (composite search score)**: 0.066
- **K-run variance**: 0.0042
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.215


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18182,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.13162,"descend_to_contact.descend_speed":0.03528,"descend_to_contact.descend_tolerance":0.00421,"push_to_goal.lateral_offset":-0.0093,"push_to_goal.push_speed":0.05181,"push_to_goal.push_tolerance":0.02873,"retract_tool.retract_speed":0.11461},"optimized_scores":{"best_composite_score":0.18073,"best_fitness_score":0.59073,"best_task_score":0.90378},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":75.0,"contact_point_centroid":[0.47499,0.01544,0.03875],"force_p95":159.37379,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":182.02954,"mean_force":69.16272,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.48674,0.01535,0.0364]},{"body_a":"attachment","body_b":"peg","contact_count":175.0,"contact_point_centroid":[0.49337,0.08172,0.04862],"force_p95":32.34064,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.48796,"mean_force":5.74958,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48835,0.09232,0.03306]},{"body_a":"attachment","body_b":"peg","contact_count":211.0,"contact_point_centroid":[0.49637,0.0006,0.03849],"force_p95":31.40541,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.69986,"mean_force":17.55498,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.48688,0.00715,0.04005]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":230.0,"contact_point_centroid":[0.52553,-0.00948,0.02881],"force_p95":28.98236,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.60724,"mean_force":15.7004,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.48694,0.00561,0.04074]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":43.0,"contact_point_centroid":[0.52557,0.0063,0.03683],"force_p95":33.37583,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.03059,"mean_force":15.60759,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48743,0.03171,0.03338]},{"body_a":"peg","body_b":"channel_base_body","contact_count":159.0,"contact_point_centroid":[0.50126,0.04532,0.00929],"force_p95":11.03929,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.38984,"mean_force":2.63227,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48826,0.08487,0.03308]},{"body_a":"peg","body_b":"channel_base_body","contact_count":554.0,"contact_point_centroid":[0.50125,-0.03109,0.00887],"force_p95":15.87856,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.14065,"mean_force":4.22841,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49006,-0.02625,0.05679]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":43.0,"contact_point_centroid":[0.47483,0.0861,0.03824],"force_p95":13.24728,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.77031,"mean_force":2.62438,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48887,0.11627,0.03321]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":38.0,"contact_point_centroid":[0.47498,-0.05319,0.02478],"force_p95":8.80015,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.20679,"mean_force":4.04732,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49371,-0.05863,0.07372]},{"body_a":"peg","body_b":"channel_base_body","contact_count":720.0,"contact_point_centroid":[0.49614,0.11684,0.00947],"force_p95":0.65527,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.16315,"mean_force":0.60187,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48678,0.14997,0.09026]},{"body_a":"attachment","body_b":"peg","contact_count":36.0,"contact_point_centroid":[0.49421,0.13654,0.0592],"force_p95":3.52096,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.7324,"mean_force":1.53115,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49077,0.1485,0.04431]},{"body_a":"peg","body_b":"channel_base_body","contact_count":439.0,"contact_point_centroid":[0.49637,0.1191,0.00939],"force_p95":0.60654,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5597,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49139,0.17526,0.22074]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49949,0.19899,0.29761]}],"total_contact_groups":13},"final_pose_error":0.01164,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49318,-0.04311,0.02413],"final_tcp_position":[0.49563,-0.07313,0.08169],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":182.02954,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":464.0,"n_steps_budget":810.0,"object_pos_end":[0.49601,0.11912,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19925,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.45965,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":756.0,"raw_peak_contact_force":4.16315,"subtask_id":"pre_push","tcp_end":[0.48459,0.15253,0.14916],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":720.0,"n_steps_budget":1000.0,"object_pos_end":[0.49633,0.11836,0.03476],"object_pos_start":[0.49601,0.11912,0.03385],"object_to_goal_dist_end":0.19847,"object_to_goal_dist_start":0.19925,"object_z_max":0.03474,"peak_contact_force":16.36172,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":420.0,"raw_peak_contact_force":45.48796,"subtask_id":"pre_push","tcp_end":[0.49154,0.14826,0.03587],"tcp_start":[0.48459,0.15253,0.14916],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.50747,0.00042,0.03926],"object_pos_start":[0.49633,0.11836,0.03476],"object_to_goal_dist_end":0.08077,"object_to_goal_dist_start":0.19847,"object_z_max":0.04245,"peak_contact_force":0.53927,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1108.0,"raw_peak_contact_force":182.02954,"subtask_id":"push_goal","tcp_end":[0.48683,0.02299,0.0332],"tcp_start":[0.48689,0.02314,0.03326],"tcp_to_object_dist_end":0.03118,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":585.0,"n_steps_budget":660.0,"object_pos_end":[0.49318,-0.04311,0.02413],"object_pos_start":[0.5075,-0.0001,0.03905],"object_to_goal_dist_end":0.04073,"object_to_goal_dist_start":0.08026,"object_z_max":0.04081,"peak_contact_force":0.50592,"phase_name":"retract_tool","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":463.0,"raw_peak_contact_force":2.24822,"subtask_id":"push_goal","tcp_end":[0.49563,-0.07313,0.08169],"tcp_start":[0.48683,0.02299,0.0332],"tcp_to_object_dist_end":0.06496,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19075,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.13501,"descend_to_contact.descend_speed":0.03083,"descend_to_contact.descend_tolerance":0.00661,"push_to_goal.lateral_offset":-0.00549,"push_to_goal.push_speed":0.05025,"push_to_goal.push_tolerance":0.02242,"retract_tool.retract_speed":0.12664},"optimized_scores":{"best_composite_score":0.066,"best_fitness_score":0.476,"best_task_score":0.31366},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":141.0,"contact_point_centroid":[0.50153,0.04053,0.04669],"force_p95":16.04921,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.67147,"mean_force":3.59349,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4986,0.05201,0.03488]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":41.0,"contact_point_centroid":[0.52559,-0.00911,0.0354],"force_p95":31.73542,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.15471,"mean_force":6.85183,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49638,0.01961,0.03457]},{"body_a":"peg","body_b":"channel_base_body","contact_count":116.0,"contact_point_centroid":[0.50351,0.01357,0.00961],"force_p95":10.95225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.76033,"mean_force":3.00764,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49842,0.04913,0.03487]},{"body_a":"attachment","body_b":"peg","contact_count":226.0,"contact_point_centroid":[0.49921,-0.03056,0.04712],"force_p95":8.03939,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.75524,"mean_force":2.79494,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49321,-0.0202,0.04615]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":228.0,"contact_point_centroid":[0.52512,-0.04503,0.02985],"force_p95":7.45705,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.52355,"mean_force":2.58271,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49327,-0.02723,0.05043]},{"body_a":"peg","body_b":"channel_base_body","contact_count":453.0,"contact_point_centroid":[0.50663,-0.05547,0.00995],"force_p95":3.83951,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.63574,"mean_force":1.3969,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49407,-0.03814,0.05782]},{"body_a":"peg","body_b":"channel_base_body","contact_count":543.0,"contact_point_centroid":[0.50603,0.06233,0.00939],"force_p95":0.55296,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.77491,"mean_force":0.5731,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51302,0.09591,0.09104]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50642,0.08092,0.05854],"force_p95":5.19191,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.42306,"mean_force":1.9061,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.5042,0.093,0.04155]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":32.0,"contact_point_centroid":[0.47451,0.01726,0.03093],"force_p95":2.45087,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.27771,"mean_force":0.90078,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49798,0.04871,0.03427]},{"body_a":"peg","body_b":"channel_base_body","contact_count":562.0,"contact_point_centroid":[0.50578,0.06294,0.00936],"force_p95":0.56519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.57064,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51191,0.14761,0.21805]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5,0.19777,0.2964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":154.0,"contact_point_centroid":[0.50533,-0.10008,0.03881],"force_p95":1.77085,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.09503,"mean_force":0.43307,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49536,-0.06267,0.07391]}],"total_contact_groups":12},"final_pose_error":0.01131,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50526,-0.0692,0.03907],"final_tcp_position":[0.49611,-0.07381,0.08137],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":40.67147,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":590.0,"n_steps_budget":900.0,"object_pos_end":[0.50594,0.06297,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":1.40342,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":552.0,"raw_peak_contact_force":5.77491,"subtask_id":"pre_push","tcp_end":[0.52455,0.09944,0.14539],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":543.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.06281,0.03433],"object_pos_start":[0.50594,0.06297,0.03381],"object_to_goal_dist_end":0.14305,"object_to_goal_dist_start":0.14323,"object_z_max":0.03432,"peak_contact_force":7.93588,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":330.0,"raw_peak_contact_force":40.67147,"subtask_id":"pre_push","tcp_end":[0.5036,0.09282,0.03809],"tcp_start":[0.52455,0.09944,0.14539],"tcp_to_object_dist_end":0.03033,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":233.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,-0.02461,0.03671],"object_pos_start":[0.506,0.06281,0.03433],"object_to_goal_dist_end":0.0558,"object_to_goal_dist_start":0.14305,"object_z_max":0.04,"peak_contact_force":0.43554,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1061.0,"raw_peak_contact_force":11.75524,"subtask_id":"push_goal","tcp_end":[0.49502,0.00313,0.03423],"tcp_start":[0.49508,0.00327,0.03429],"tcp_to_object_dist_end":0.02987,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":519.0,"n_steps_budget":600.0,"object_pos_end":[0.50526,-0.0692,0.03907],"object_pos_start":[0.50563,-0.02505,0.03654],"object_to_goal_dist_end":0.01205,"object_to_goal_dist_start":0.05534,"object_z_max":0.04083,"peak_contact_force":0.54277,"phase_name":"retract_tool","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":596.0,"raw_peak_contact_force":3.88411,"subtask_id":"push_goal","tcp_end":[0.49611,-0.07381,0.08137],"tcp_start":[0.49502,0.00313,0.03423],"tcp_to_object_dist_end":0.04353,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34091,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.07206,"descend_to_contact.descend_speed":0.04032,"descend_to_contact.descend_tolerance":0.00674,"push_to_goal.lateral_offset":-0.00765,"push_to_goal.push_speed":0.05306,"push_to_goal.push_tolerance":0.01773,"retract_tool.retract_speed":0.12016},"optimized_scores":{"best_composite_score":0.0277,"best_fitness_score":0.4377,"best_task_score":0.20206},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_right_wall","contact_count":71.0,"contact_point_centroid":[0.47473,-0.0032,0.05282],"force_p95":38.98495,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.23579,"mean_force":17.10549,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49688,0.02527,0.03475]},{"body_a":"attachment","body_b":"peg","contact_count":116.0,"contact_point_centroid":[0.49918,0.0332,0.04935],"force_p95":38.14371,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.18926,"mean_force":12.3868,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49859,0.04439,0.03512]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":23.0,"contact_point_centroid":[0.47468,-0.01964,0.03797],"force_p95":30.59053,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.88336,"mean_force":9.82987,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49609,0.00861,0.03565]},{"body_a":"attachment","body_b":"peg","contact_count":151.0,"contact_point_centroid":[0.496,-0.01938,0.04464],"force_p95":10.53117,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.31071,"mean_force":3.16535,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49448,-0.00773,0.04289]},{"body_a":"peg","body_b":"channel_base_body","contact_count":84.0,"contact_point_centroid":[0.49987,0.0162,0.00935],"force_p95":16.41108,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.51883,"mean_force":3.59181,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49944,0.05517,0.03523]},{"body_a":"peg","body_b":"channel_base_body","contact_count":449.0,"contact_point_centroid":[0.49959,-0.051,0.00993],"force_p95":3.63519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.76609,"mean_force":1.02146,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49488,-0.036,0.05909]},{"body_a":"peg","body_b":"channel_base_body","contact_count":523.0,"contact_point_centroid":[0.50602,0.05617,0.00938],"force_p95":0.55018,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.9284,"mean_force":0.57199,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51675,0.08973,0.09108]},{"body_a":"attachment","body_b":"peg","contact_count":6.0,"contact_point_centroid":[0.50673,0.07454,0.05604],"force_p95":5.62553,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.55865,"mean_force":2.43646,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50477,0.08661,0.0401]},{"body_a":"peg","body_b":"channel_base_body","contact_count":628.0,"contact_point_centroid":[0.50593,0.05663,0.00936],"force_p95":0.60057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57191,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51513,0.14444,0.2178]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50005,0.1977,0.29637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":189.0,"contact_point_centroid":[0.49769,-0.10007,0.02365],"force_p95":0.58088,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62418,"mean_force":0.31735,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49555,-0.05717,0.07168]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":123.0,"contact_point_centroid":[0.52503,-0.09337,0.03711],"force_p95":0.31345,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55262,"mean_force":0.12197,"phase_index":3.0,"phase_name":"retract_tool","phase_type":"retract","tcp_position_centroid":[0.49571,-0.06115,0.07409]}],"total_contact_groups":12},"final_pose_error":0.01147,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50391,-0.07167,0.03212],"final_tcp_position":[0.49624,-0.07332,0.08146],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":42.23579,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":657.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.49352,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":529.0,"raw_peak_contact_force":6.9284,"subtask_id":"pre_push","tcp_end":[0.531,0.09334,0.14496],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1197,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,0.05641,0.03398],"object_pos_start":[0.50613,0.05659,0.03378],"object_to_goal_dist_end":0.13668,"object_to_goal_dist_start":0.13687,"object_z_max":0.03391,"peak_contact_force":7.86698,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":271.0,"raw_peak_contact_force":42.23579,"subtask_id":"pre_push","tcp_end":[0.50436,0.08651,0.03832],"tcp_start":[0.531,0.09334,0.14496],"tcp_to_object_dist_end":0.03047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":203.0,"n_steps_budget":1000.0,"object_pos_end":[0.49318,-0.01977,0.0408],"object_pos_start":[0.50619,0.05641,0.03398],"object_to_goal_dist_end":0.06062,"object_to_goal_dist_start":0.13668,"object_z_max":0.0413,"peak_contact_force":0.34804,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":935.0,"raw_peak_contact_force":39.88336,"subtask_id":"push_goal","tcp_end":[0.49664,0.01002,0.03548],"tcp_start":[0.49667,0.01017,0.03553],"tcp_to_object_dist_end":0.03046,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":522.0,"n_steps_budget":600.0,"object_pos_end":[0.50391,-0.07167,0.03212],"object_pos_start":[0.49296,-0.02017,0.04048],"object_to_goal_dist_end":0.01212,"object_to_goal_dist_start":0.06025,"object_z_max":0.04077,"peak_contact_force":0.54525,"phase_name":"retract_tool","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":665.0,"raw_peak_contact_force":4.44541,"subtask_id":"push_goal","tcp_end":[0.49624,-0.07332,0.08146],"tcp_start":[0.49664,0.01002,0.03548],"tcp_to_object_dist_end":0.04996,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```