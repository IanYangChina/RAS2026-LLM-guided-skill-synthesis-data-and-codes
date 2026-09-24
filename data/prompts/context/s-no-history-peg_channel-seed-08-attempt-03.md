## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

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

## Current Skill (Q=-0.790) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: push_to_goal
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_arc_height:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: generator.arc_height
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_peg
- id: descend_1
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
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    descend_z_offset:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_peg
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
      distance: 0.04
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance_1:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed_1:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard_1
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  - id: contact_guard_1
    when: during_phase
    predicate: force_below
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push_to_goal
- id: approach_2
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
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed_2:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_peg
- id: descend_2
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
    - 0.0
    - 0.02
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_speed_2:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    descend_z_offset_2:
      type: scalar
      range:
      - 0.01
      - 0.03
      default: 0.02
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_peg
- id: push_2
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
      distance: 0.04
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance_2:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed_2:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard_2
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  - id: contact_guard_2
    when: during_phase
    predicate: force_below
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push_to_goal
- id: approach_3
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
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed_3:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_peg
- id: push_3
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
      distance: 0.1
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance_3:
      type: scalar
      range:
      - 0.06
      - 0.14
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed_3:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard_3
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  - id: contact_guard_3
    when: during_phase
    predicate: force_below
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_arc_height: status=consumed; consumers=generator.arc_height (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_z_offset: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.04, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance_1: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed_1: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard_1, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
    - id=contact_guard_1, when=during_phase, predicate=force_below, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.01, 0.0]
- **approach_2** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed_2: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_2** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.02], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed_2: status=consumed; consumers=generator.speed (replace)
    - descend_z_offset_2: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_2** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.04, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance_2: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed_2: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard_2, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
    - id=contact_guard_2, when=during_phase, predicate=force_below, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.01, 0.0]
- **approach_3** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed_3: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_3** (`push`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.1, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance_3: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed_3: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard_3, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
    - id=contact_guard_3, when=during_phase, predicate=force_below, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.01, 0.0]

## Design Metrics

- **Composite score**: -0.790
- **task_score** (E): 0.000
- **fitness_score**: 0.090  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.880

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1189 |
| descend_1 | 1.00 | 1.00 | 0.1892 |
| push_1 | 0.00 | 1.00 | 0.0002 |
| approach_2 | 1.00 | 1.00 | 0.0996 |
| descend_2 | 1.00 | 1.00 | 0.0981 |
| push_2 | 0.00 | 1.00 | 0.0002 |
| approach_3 | 1.00 | 1.00 | 0.0989 |
| push_3 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.514, 0.094, 0.253) | (0.517, 0.080, 0.040)→(0.503, 0.080, 0.034) | 0.162→0.160 | 1.00 / 1.000 | 0.530 | 3.526 |
| descend_1 | descend | 1.00 / step_budget | (0.514, 0.094, 0.253)→(0.500, 0.080, 0.065) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.544 | 0.613 |
| push_1 | push | 0.00 / guard_failure | (0.500, 0.080, 0.065)→(0.500, 0.080, 0.065) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.518 | 0.560 |
| approach_2 | approach | 1.00 / step_budget | (0.500, 0.080, 0.065)→(0.500, 0.079, 0.164) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.511 | 0.607 |
| descend_2 | descend | 1.00 / step_budget | (0.500, 0.079, 0.164)→(0.499, 0.079, 0.066) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.535 | 0.606 |
| push_2 | push | 0.00 / guard_failure | (0.498, 0.079, 0.066)→(0.498, 0.079, 0.065) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.333 | 0.813 | 0.548 |
| approach_3 | approach | 1.00 / step_budget | (0.498, 0.079, 0.065)→(0.499, 0.079, 0.164) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.550 | 5.911 |
| push_3 | push | 0.00 / guard_failure | (0.500, 0.079, 0.165)→(0.500, 0.079, 0.165) | (0.503, 0.080, 0.034)→(0.503, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.564 | 0.564 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.955
- terminal_score: 0.000
- phase_score: 0.178
- phase_breakdown.approach_peg_score: 0.592
- phase_breakdown.push_to_goal_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.107
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.794
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07067,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.18407,"approach_1.approach_speed":0.10252,"approach_2.approach_speed_2":0.08763,"approach_3.approach_speed_3":0.08162,"descend_1.descend_speed":0.03222,"descend_1.descend_z_offset":0.02252,"descend_2.descend_speed_2":0.02931,"descend_2.descend_z_offset_2":0.02688,"push_1.push_distance_1":0.03695,"push_1.push_speed_1":0.00994,"push_2.push_distance_2":0.05189,"push_2.push_speed_2":0.01505,"push_3.push_distance_3":0.10524,"push_3.push_speed_3":0.01044},"optimized_scores":{"best_composite_score":-0.77343,"best_fitness_score":0.10657,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":147.0,"contact_point_centroid":[0.49667,0.11907,0.00934],"force_p95":0.80805,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.59531,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49198,0.16018,0.27863]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49881,0.1964,0.29868]},{"body_a":"peg","body_b":"channel_base_body","contact_count":303.0,"contact_point_centroid":[0.49593,0.11936,0.00943],"force_p95":0.60951,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66166,"mean_force":0.5426,"phase_index":6.0,"phase_name":"approach_3","phase_type":"approach","tcp_position_centroid":[0.49077,0.11793,0.11544]},{"body_a":"peg","body_b":"channel_base_body","contact_count":661.0,"contact_point_centroid":[0.49609,0.11905,0.00942],"force_p95":0.6188,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.653,"mean_force":0.54178,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48851,0.12562,0.1594]},{"body_a":"peg","body_b":"channel_base_body","contact_count":343.0,"contact_point_centroid":[0.49618,0.11921,0.00946],"force_p95":0.59475,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64599,"mean_force":0.5391,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.49151,0.11808,0.11774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":312.0,"contact_point_centroid":[0.49598,0.11901,0.00943],"force_p95":0.59958,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64293,"mean_force":0.54151,"phase_index":3.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49079,0.1184,0.11313]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50194,0.12,0.00941],"force_p95":0.58764,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59473,"mean_force":0.53843,"phase_index":7.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.49275,0.11857,0.16476]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.47837,0.12,0.00941],"force_p95":0.58527,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5891,"mean_force":0.55309,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49182,0.1191,0.0651]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.49963,0.11999,0.00956],"force_p95":0.53872,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54535,"mean_force":0.50399,"phase_index":5.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.4919,0.11805,0.06925]}],"total_contact_groups":9},"final_pose_error":0.16784,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.496,0.11902,0.03384],"final_tcp_position":[0.49285,0.1186,0.16495],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":2.24822,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":172.0,"n_steps_budget":630.0,"object_pos_end":[0.49603,0.11903,0.03387],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19917,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51761,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":171.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48704,0.13248,0.25443],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22115,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":661.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11919,0.03386],"object_pos_start":[0.49603,0.11903,0.03387],"object_to_goal_dist_end":0.19933,"object_to_goal_dist_start":0.19917,"object_z_max":0.03415,"peak_contact_force":0.5061,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":661.0,"raw_peak_contact_force":0.653,"subtask_id":"approach_peg","tcp_end":[0.49194,0.11914,0.06533],"tcp_start":[0.48704,0.13248,0.25443],"tcp_to_object_dist_end":0.03174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.496,0.11918,0.03386],"object_pos_start":[0.49601,0.11919,0.03386],"object_to_goal_dist_end":0.19932,"object_to_goal_dist_start":0.19933,"object_z_max":0.03386,"peak_contact_force":0.51941,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":0.5891,"subtask_id":"push_to_goal","tcp_end":[0.49158,0.11901,0.06473],"tcp_start":[0.4917,0.11905,0.0649],"tcp_to_object_dist_end":0.03119,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":312.0,"n_steps_budget":870.0,"object_pos_end":[0.49604,0.11899,0.03382],"object_pos_start":[0.49602,0.11915,0.03386],"object_to_goal_dist_end":0.19913,"object_to_goal_dist_start":0.19929,"object_z_max":0.03404,"peak_contact_force":0.49995,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":312.0,"raw_peak_contact_force":0.64293,"subtask_id":"approach_peg","tcp_end":[0.49273,0.11845,0.16424],"tcp_start":[0.49158,0.11901,0.06473],"tcp_to_object_dist_end":0.13046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11939,0.03414],"object_pos_start":[0.49604,0.11899,0.03382],"object_to_goal_dist_end":0.19952,"object_to_goal_dist_start":0.19913,"object_z_max":0.03416,"peak_contact_force":0.51252,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":343.0,"raw_peak_contact_force":0.64599,"subtask_id":"approach_peg","tcp_end":[0.49213,0.11811,0.06965],"tcp_start":[0.49273,0.11845,0.16424],"tcp_to_object_dist_end":0.03575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11942,0.03414],"object_pos_start":[0.49601,0.11939,0.03414],"object_to_goal_dist_end":0.19954,"object_to_goal_dist_start":0.19952,"object_z_max":0.03414,"peak_contact_force":0.49523,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":0.54535,"subtask_id":"push_to_goal","tcp_end":[0.49156,0.11796,0.06878],"tcp_start":[0.49166,0.11799,0.06891],"tcp_to_object_dist_end":0.03496,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":303.0,"n_steps_budget":900.0,"object_pos_end":[0.49608,0.1191,0.03384],"object_pos_start":[0.49603,0.11943,0.03414],"object_to_goal_dist_end":0.19923,"object_to_goal_dist_start":0.19955,"object_z_max":0.03414,"peak_contact_force":0.5563,"phase_name":"approach_3","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":303.0,"raw_peak_contact_force":0.66166,"subtask_id":"approach_peg","tcp_end":[0.49268,0.11855,0.16459],"tcp_start":[0.49156,0.11796,0.06878],"tcp_to_object_dist_end":0.13079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49606,0.11907,0.03384],"object_pos_start":[0.49608,0.1191,0.03384],"object_to_goal_dist_end":0.19921,"object_to_goal_dist_start":0.19923,"object_z_max":0.03384,"peak_contact_force":0.59473,"phase_name":"push_3","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":0.59473,"subtask_id":"push_to_goal","tcp_end":[0.49285,0.1186,0.16495],"tcp_start":[0.49282,0.11859,0.16489],"tcp_to_object_dist_end":0.13115,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.82778,"average_solve_count":360.0,"average_success_count":360.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.25038,"approach_1.approach_speed":0.08901,"approach_2.approach_speed_2":0.0619,"approach_3.approach_speed_3":0.05508,"descend_1.descend_speed":0.01633,"descend_1.descend_z_offset":0.01986,"descend_2.descend_speed_2":0.02106,"descend_2.descend_z_offset_2":0.01865,"push_1.push_distance_1":0.03666,"push_1.push_speed_1":0.01294,"push_2.push_distance_2":0.04611,"push_2.push_speed_2":0.01244,"push_3.push_distance_3":0.10763,"push_3.push_speed_3":0.00892},"optimized_scores":{"best_composite_score":-0.7941,"best_fitness_score":0.0859,"best_task_score":0.00035},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":348.0,"contact_point_centroid":[0.50489,0.06278,0.00942],"force_p95":0.65241,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.51531,"mean_force":0.74241,"phase_index":6.0,"phase_name":"approach_3","phase_type":"approach","tcp_position_centroid":[0.50083,0.06226,0.11141]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.51275,0.06228,0.05912],"force_p95":14.28288,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.93537,"mean_force":5.38902,"phase_index":6.0,"phase_name":"approach_3","phase_type":"approach","tcp_position_centroid":[0.50094,0.06233,0.061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":279.0,"contact_point_centroid":[0.50555,0.06308,0.00933],"force_p95":0.6375,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.59504,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5129,0.13246,0.28396]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50034,0.19471,0.29947]},{"body_a":"peg","body_b":"channel_base_body","contact_count":625.0,"contact_point_centroid":[0.50593,0.06291,0.00938],"force_p95":0.55203,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55641,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51336,0.07068,0.15712]},{"body_a":"peg","body_b":"channel_base_body","contact_count":334.0,"contact_point_centroid":[0.50611,0.06286,0.00938],"force_p95":0.55272,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54655,"phase_index":3.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50179,0.06289,0.1122]},{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.50586,0.06309,0.00938],"force_p95":0.55156,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55493,"mean_force":0.54655,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50142,0.06244,0.11375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50788,0.07822,0.00938],"force_p95":0.55085,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55119,"mean_force":0.54735,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50365,0.06355,0.06309]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.52319,0.06182,0.0094],"force_p95":0.54848,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5485,"mean_force":0.54777,"phase_index":7.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.5028,0.06249,0.16449]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.52248,0.06193,0.00939],"force_p95":0.54715,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54742,"mean_force":0.54533,"phase_index":5.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.50183,0.06244,0.06121]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.52505,0.06265,0.05897],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"approach_3","phase_type":"approach","tcp_position_centroid":[0.49986,0.06217,0.0701]}],"total_contact_groups":11},"final_pose_error":0.16907,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50607,0.06281,0.03394],"final_tcp_position":[0.50289,0.0625,0.16467],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":16.51531,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06295,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54627,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":313.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.52449,0.07797,0.25181],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.2193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":625.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.06303,0.03381],"object_pos_start":[0.50602,0.06295,0.03381],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14321,"object_z_max":0.03381,"peak_contact_force":0.54711,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":625.0,"raw_peak_contact_force":0.55641,"subtask_id":"approach_peg","tcp_end":[0.50379,0.06358,0.06333],"tcp_start":[0.52449,0.07797,0.25181],"tcp_to_object_dist_end":0.02961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.06304,0.0338],"object_pos_start":[0.50596,0.06303,0.03381],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":0.5478,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":0.55119,"subtask_id":"push_to_goal","tcp_end":[0.50338,0.06349,0.06269],"tcp_start":[0.50351,0.06351,0.06287],"tcp_to_object_dist_end":0.02901,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.06295,0.0338],"object_pos_start":[0.50603,0.063,0.03381],"object_to_goal_dist_end":0.14321,"object_to_goal_dist_start":0.14326,"object_z_max":0.03381,"peak_contact_force":0.54282,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":334.0,"raw_peak_contact_force":0.55532,"subtask_id":"approach_peg","tcp_end":[0.5029,0.06267,0.16434],"tcp_start":[0.50338,0.06349,0.06269],"tcp_to_object_dist_end":0.13057,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":381.0,"n_steps_budget":1000.0,"object_pos_end":[0.50605,0.06302,0.03383],"object_pos_start":[0.50594,0.06295,0.0338],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14321,"object_z_max":0.03383,"peak_contact_force":0.54469,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":381.0,"raw_peak_contact_force":0.55493,"subtask_id":"approach_peg","tcp_end":[0.50195,0.06245,0.06143],"tcp_start":[0.5029,0.06267,0.16434],"tcp_to_object_dist_end":0.02791,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50606,0.06298,0.03383],"object_pos_start":[0.50605,0.06302,0.03383],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14328,"object_z_max":0.03383,"peak_contact_force":1.39269,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":0.54742,"subtask_id":"push_to_goal","tcp_end":[0.50158,0.0624,0.06085],"tcp_start":[0.5017,0.06242,0.06101],"tcp_to_object_dist_end":0.0274,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.5061,0.06297,0.03393],"object_pos_start":[0.50602,0.06291,0.03383],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.14317,"object_z_max":0.03514,"peak_contact_force":0.54889,"phase_name":"approach_3","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":366.0,"raw_peak_contact_force":16.51531,"subtask_id":"approach_peg","tcp_end":[0.50273,0.06248,0.16434],"tcp_start":[0.50158,0.0624,0.06085],"tcp_to_object_dist_end":0.13045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.06291,0.03393],"object_pos_start":[0.5061,0.06297,0.03393],"object_to_goal_dist_end":0.14317,"object_to_goal_dist_start":0.14323,"object_z_max":0.03393,"peak_contact_force":0.5485,"phase_name":"push_3","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":0.5485,"subtask_id":"push_to_goal","tcp_end":[0.50289,0.0625,0.16467],"tcp_start":[0.50286,0.0625,0.16462],"tcp_to_object_dist_end":0.13078,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89097,"average_solve_count":321.0,"average_success_count":321.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_arc_height":0.2255,"approach_1.approach_speed":0.12972,"approach_2.approach_speed_2":0.0576,"approach_3.approach_speed_3":0.06243,"descend_1.descend_speed":0.02695,"descend_1.descend_z_offset":0.02369,"descend_2.descend_speed_2":0.02537,"descend_2.descend_z_offset_2":0.02453,"push_1.push_distance_1":0.04086,"push_1.push_speed_1":0.01368,"push_2.push_distance_2":0.03974,"push_2.push_speed_2":0.01053,"push_3.push_distance_3":0.09783,"push_3.push_speed_3":0.01166},"optimized_scores":{"best_composite_score":-0.80259,"best_fitness_score":0.07741,"best_task_score":0.00015},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":292.0,"contact_point_centroid":[0.50562,0.05667,0.00933],"force_p95":0.6025,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.60103,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51666,0.128,0.28709]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50076,0.19367,0.30002]},{"body_a":"peg","body_b":"channel_base_body","contact_count":610.0,"contact_point_centroid":[0.50613,0.05659,0.00937],"force_p95":0.62074,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62957,"mean_force":0.54645,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51702,0.0639,0.15937]},{"body_a":"peg","body_b":"channel_base_body","contact_count":325.0,"contact_point_centroid":[0.50587,0.05654,0.00936],"force_p95":0.62078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62361,"mean_force":0.54669,"phase_index":3.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50223,0.05658,0.11407]},{"body_a":"peg","body_b":"channel_base_body","contact_count":353.0,"contact_point_centroid":[0.50616,0.05672,0.00938],"force_p95":0.57717,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61816,"mean_force":0.54678,"phase_index":4.0,"phase_name":"descend_2","phase_type":"descend","tcp_position_centroid":[0.50167,0.05616,0.11661]},{"body_a":"peg","body_b":"channel_base_body","contact_count":322.0,"contact_point_centroid":[0.50602,0.05662,0.00939],"force_p95":0.55214,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55659,"mean_force":0.54642,"phase_index":6.0,"phase_name":"approach_3","phase_type":"approach","tcp_position_centroid":[0.50098,0.05598,0.11438]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.52184,0.06026,0.00938],"force_p95":0.55136,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55184,"mean_force":0.54863,"phase_index":5.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.50206,0.05616,0.06721]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.52231,0.05313,0.00939],"force_p95":0.54913,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5493,"mean_force":0.5474,"phase_index":7.0,"phase_name":"push_3","phase_type":"push","tcp_position_centroid":[0.5029,0.05617,0.1645]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.52403,0.05733,0.00937],"force_p95":0.53791,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54094,"mean_force":0.51248,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50428,0.05722,0.06686]}],"total_contact_groups":9},"final_pose_error":0.16313,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50616,0.05653,0.03384],"final_tcp_position":[0.503,0.05619,0.16467],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":4.44541,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":321.0,"n_steps_budget":780.0,"object_pos_end":[0.50613,0.05663,0.03377],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":0.52692,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":329.0,"raw_peak_contact_force":4.44541,"subtask_id":"approach_peg","tcp_end":[0.53104,0.07072,0.25251],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.22061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":610.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,0.05661,0.03376],"object_pos_start":[0.50613,0.05663,0.03377],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.13691,"object_z_max":0.03382,"peak_contact_force":0.57743,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":610.0,"raw_peak_contact_force":0.62957,"subtask_id":"approach_peg","tcp_end":[0.50441,0.05725,0.0671],"tcp_start":[0.53104,0.07072,0.25251],"tcp_to_object_dist_end":0.0334,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50618,0.05661,0.03376],"object_pos_start":[0.50619,0.05661,0.03376],"object_to_goal_dist_end":0.13689,"object_to_goal_dist_start":0.13689,"object_z_max":0.03376,"peak_contact_force":0.48589,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":0.54094,"subtask_id":"push_to_goal","tcp_end":[0.504,0.05717,0.06647],"tcp_start":[0.50413,0.05719,0.06664],"tcp_to_object_dist_end":0.03278,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05663,0.03376],"object_pos_start":[0.5061,0.05661,0.03376],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13689,"object_z_max":0.03377,"peak_contact_force":0.49022,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":325.0,"raw_peak_contact_force":0.62361,"subtask_id":"approach_peg","tcp_end":[0.5031,0.05634,0.16416],"tcp_start":[0.504,0.05717,0.06647],"tcp_to_object_dist_end":0.13044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.50618,0.05666,0.03382],"object_pos_start":[0.50615,0.05663,0.03376],"object_to_goal_dist_end":0.13694,"object_to_goal_dist_start":0.13691,"object_z_max":0.03382,"peak_contact_force":0.54702,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":353.0,"raw_peak_contact_force":0.61816,"subtask_id":"approach_peg","tcp_end":[0.50218,0.05618,0.06743],"tcp_start":[0.5031,0.05634,0.16416],"tcp_to_object_dist_end":0.03385,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5062,0.05663,0.03382],"object_pos_start":[0.50618,0.05666,0.03382],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13694,"object_z_max":0.03382,"peak_contact_force":0.55184,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":0.55184,"subtask_id":"push_to_goal","tcp_end":[0.50181,0.05613,0.06685],"tcp_start":[0.50193,0.05615,0.06701],"tcp_to_object_dist_end":0.03332,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":322.0,"n_steps_budget":1000.0,"object_pos_end":[0.50621,0.05664,0.03384],"object_pos_start":[0.50618,0.05656,0.03382],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.13684,"object_z_max":0.03384,"peak_contact_force":0.54491,"phase_name":"approach_3","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":322.0,"raw_peak_contact_force":0.55659,"subtask_id":"approach_peg","tcp_end":[0.50284,0.05616,0.16434],"tcp_start":[0.50181,0.05613,0.06685],"tcp_to_object_dist_end":0.13055,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50621,0.05659,0.03384],"object_pos_start":[0.50621,0.05664,0.03384],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.13691,"object_z_max":0.03384,"peak_contact_force":0.54759,"phase_name":"push_3","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":0.5493,"subtask_id":"push_to_goal","tcp_end":[0.503,0.05619,0.16467],"tcp_start":[0.50297,0.05618,0.16463],"tcp_to_object_dist_end":0.13088,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```