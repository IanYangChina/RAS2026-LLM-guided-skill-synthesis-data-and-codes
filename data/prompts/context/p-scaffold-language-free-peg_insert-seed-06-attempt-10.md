## Search State

- **Seed**: 6
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → align → insert → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.1091 | 0.83 | ❌ rejected |
| 9 | approach → descend → contact → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.1648 | 0.82 | ❌ rejected |
| 8 | approach → descend → contact → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.1965 | 0.84 | ❌ rejected |
| 7 | approach → contact → insert → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 9 | -0.0201 | 0.84 | ❌ rejected |
| 6 | approach → descend → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | 0.1110 | 0.84 | ✅ accepted |

**Proposal policy**: task_score is 0.83 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_insert
- Frozen realised-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5030531481177555, -0.012538330414932925, 0.08]
- Frozen socket pose: [0.5030531481177555, -0.012538330414932925, 0.025] (static fixture for this episode)
- Goal object position: (0.5030531481177555, -0.012538330414932925, 0.025)
- Object initial pose: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: peg_socket
    role: fixture
    dynamics: static
    geometry: box_with_hole
    base_dimensions_m: [0.12, 0.12, 0.05]
    hole_entry_height_m: 0.08
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    note: peg is a fixed end-effector attachment on the panda_peg arm
task_landmarks:
  frozen_object_start: [0.504, -0, 0.3403]
  frozen_task_target: [0.5031, -0.0125, 0.08]
  frozen_socket_position: [0.5031, -0.0125, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5030531481177555, -0.012538330414932925, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5030531481177555, -0.012538330414932925, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.844, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5030531481177555, -0.012538330414932925, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5030531481177555, -0.012538330414932925, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=-0.109) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_sub
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: insert_sub
  target_entity: object
  weight: 0.7
phases:
- id: approach_to_above
  type: approach
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
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: insertion_axis
      tolerance: 0.05
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    pos_tolerance:
      type: scalar
      range:
      - 0.001
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: approach_sub
- id: descend_to_entry
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    pos_tolerance:
      type: scalar
      range:
      - 0.001
      - 0.005
      default: 0.002
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat
  subtask_id: approach_sub
- id: contact_entry
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 20.0
      default: 5.0
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
  guards:
  - id: max_force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: approach_sub
- id: insert_into_hole
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    insert_force_limit:
      type: scalar
      range:
      - 30.0
      - 40.0
      default: 40.0
      binds_to:
      - path: guards.max_insert_force.threshold
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    insertion_distance:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: max_insert_force
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: insert_sub
- id: retract_after_insert
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
    orientation:
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 1
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_above** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - pos_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=repeat
- **descend_to_entry** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - pos_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=repeat
- **contact_entry** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=max_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_force_limit: status=consumed; consumers=guards.max_insert_force.threshold (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=max_insert_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]
- **retract_after_insert** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat

## Design Metrics

- **Composite score**: -0.109
- **task_score** (E): 0.835
- **fitness_score**: 0.501  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| arc_approach | 0.33 | 1.00 | 0.1340 |
| lateral_align | 1.00 | 0.67 | 0.0551 |
| insert_into_hole | 0.00 | 0.67 | 0.0146 |
| retract_after_insert | 0.00 | 0.00 | 0.0242 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| arc_approach | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.449, 0.019, 0.179) | (0.504, -0.000, 0.340)→(0.484, 0.019, 0.162) | 0.260→0.087 | 1.00 / 1.333 | 254.258 | 1184.283 |
| lateral_align | align | 1.00 / step_budget | (0.449, 0.019, 0.179)→(0.492, 0.015, 0.159) | (0.484, 0.019, 0.162)→(0.529, 0.017, 0.144) | 0.087→0.076 | 0.67 / 0.667 | 80.374 | 324.822 |
| insert_into_hole | insert | 0.00 / guard_failure | (0.492, 0.015, 0.159)→(0.492, 0.015, 0.144) | (0.529, 0.017, 0.144)→(0.529, 0.017, 0.130) | 0.076→0.064 | 0.67 / 0.667 | 134.558 | 134.558 |
| retract_after_insert | retract | 0.00 / step_budget | (0.492, 0.015, 0.144)→(0.490, 0.015, 0.168) | (0.529, 0.017, 0.130)→(0.526, 0.016, 0.153) | 0.064→0.082 | 0.00 / 0.000 | 0.000 | 301.683 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.851
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.851
- phase_score: 0.381
- phase_breakdown.approach_sub_score: 0.558
- phase_breakdown.insert_sub_score: 0.306

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.569
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.851
- **Median Q (composite search score)**: -0.142
- **K-run variance**: 0.0023
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at upper bound**: arc_approach.arc_height
- **Final σ (mean)**: 0.357


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2bcd5d362bce9ed2c176357e9c3237720ebba2a98dd8bfe48970c9fba5840ac0`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ac7031668c6a08077e83f2359534923b723fe0e5a20a177feb2fc3bf67104f66`; realized-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":79.0,"average_failure_rate":0.36406,"average_mean_iterations":75.39631,"average_solve_count":217.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach.approach_speed":0.0153,"arc_approach.arc_height":0.09958,"arc_approach.pos_tolerance":0.00525,"insert_into_hole.force_below_threshold":35.58256,"insert_into_hole.insert_speed":0.0302,"insert_into_hole.insertion_distance":0.08499,"insert_into_hole.pos_tolerance":0.00197,"lateral_align.align_speed":0.04942,"lateral_align.pos_tolerance":0.00265,"retract_after_insert.pos_tolerance":0.00735,"retract_after_insert.retract_speed":0.01008},"optimized_scores":{"best_composite_score":-0.0409,"best_fitness_score":0.5691,"best_task_score":0.85055},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":655.0,"contact_point_centroid":[0.56298,0.00182,0.07934],"force_p95":473.32172,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1438.33533,"mean_force":251.19428,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.4441,0.00349,0.15842]},{"body_a":"peg_socket","body_b":"link7","contact_count":900.0,"contact_point_centroid":[0.56128,0.0072,0.07984],"force_p95":410.11215,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1358.57437,"mean_force":212.92464,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.44417,0.00311,0.15558]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.44552,0.00178,0.0791],"force_p95":580.97692,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":893.81065,"mean_force":111.72633,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.44081,0.00183,0.09245]},{"body_a":"peg_socket","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.53214,0.01775,0.07909],"force_p95":680.93646,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":693.62643,"mean_force":436.39493,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.43808,0.00133,0.10144]},{"body_a":"attachment","body_b":"peg_socket","contact_count":25.0,"contact_point_centroid":[0.56305,-0.01244,0.07997],"force_p95":221.58514,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.68403,"mean_force":35.2378,"phase_index":3.0,"phase_name":"retract_after_insert","phase_type":"retract","tcp_position_centroid":[0.4948,-0.01201,0.11068]},{"body_a":"peg_socket","body_b":"link7","contact_count":175.0,"contact_point_centroid":[0.56296,0.00596,0.07996],"force_p95":124.24919,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":209.83973,"mean_force":77.01045,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.44352,0.0029,0.14905]},{"body_a":"peg_socket","body_b":"link6","contact_count":10.0,"contact_point_centroid":[0.56298,0.00212,0.07945],"force_p95":75.61168,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.073,"mean_force":34.83748,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.43805,0.0043,0.14878]},{"body_a":"peg_socket","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.53273,-0.0426,0.07963],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.4372,0.00161,0.09761]}],"total_contact_groups":8},"final_pose_error":0.07314,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49258,-0.01205,0.13749],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1438.33533,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47728,0.00408,0.14097],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06519,"object_to_goal_dist_start":0.26034,"object_z_max":0.34435,"peak_contact_force":190.11998,"phase_name":"arc_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1595.0,"raw_peak_contact_force":1438.33533,"subtask_id":"approach_sub","tcp_end":[0.438,0.00433,0.14854],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":812.0,"n_steps_budget":870.0,"object_pos_end":[0.53632,-0.01195,0.14528],"object_pos_start":[0.47728,0.00408,0.14097],"object_to_goal_dist_end":0.07566,"object_to_goal_dist_start":0.06519,"object_z_max":0.14528,"peak_contact_force":0.0,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":185.0,"raw_peak_contact_force":209.83973,"subtask_id":"approach_sub","tcp_end":[0.49715,-0.01171,0.15339],"tcp_start":[0.438,0.00433,0.14854],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":675.0,"n_steps_budget":1000.0,"object_pos_end":[0.53442,-0.01221,0.10193],"object_pos_start":[0.53632,-0.01195,0.14528],"object_to_goal_dist_end":0.0426,"object_to_goal_dist_start":0.07566,"object_z_max":0.14528,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_sub","tcp_end":[0.49537,-0.01197,0.11058],"tcp_start":[0.49715,-0.01171,0.15339],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5315,-0.01229,0.12828],"object_pos_start":[0.53442,-0.01221,0.10193],"object_to_goal_dist_end":0.05894,"object_to_goal_dist_start":0.0426,"object_z_max":0.12825,"peak_contact_force":0.0,"phase_name":"retract_after_insert","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":25.0,"raw_peak_contact_force":304.68403,"subtask_id":"insert_sub","tcp_end":[0.49258,-0.01205,0.13749],"tcp_start":[0.49537,-0.01197,0.11058],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4cf364ad7cdeb78864f76dd2c5686ed9e91b61eb5e5b2735897d619cb8f6dad4`; realized-scene SHA-256: `5286851552083a7c8a4164a2656d1a38f2da41529a3a0236ff73d4d9a02dc20c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51546,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach.approach_speed":0.08131,"arc_approach.arc_height":0.18146,"arc_approach.pos_tolerance":0.00869,"insert_into_hole.force_below_threshold":46.9523,"insert_into_hole.insert_speed":0.02966,"insert_into_hole.insertion_distance":0.07376,"insert_into_hole.pos_tolerance":0.00333,"lateral_align.align_speed":0.02723,"lateral_align.pos_tolerance":0.00328,"retract_after_insert.pos_tolerance":0.00209,"retract_after_insert.retract_speed":0.01643},"optimized_scores":{"best_composite_score":-0.14154,"best_fitness_score":0.46846,"best_task_score":0.83585},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.45416,0.00997,0.07877],"force_p95":997.78617,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1046.3629,"mean_force":181.41567,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.44983,0.00991,0.09189]},{"body_a":"peg_socket","body_b":"link7","contact_count":114.0,"contact_point_centroid":[0.56166,0.01383,0.07913],"force_p95":501.16211,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":943.38246,"mean_force":291.77263,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.45023,0.01369,0.13476]},{"body_a":"peg_socket","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.53949,0.00168,0.0794],"force_p95":374.53124,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":398.8454,"mean_force":218.36724,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.44734,0.01012,0.0987]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.57,0.03018,0.07998],"force_p95":311.4642,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":311.4642,"mean_force":311.4642,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.4889,0.03006,0.15924]},{"body_a":"peg_socket","body_b":"link6","contact_count":323.0,"contact_point_centroid":[0.56996,0.02295,0.07986],"force_p95":292.1325,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":310.47274,"mean_force":258.57662,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.44688,0.02304,0.16806]},{"body_a":"peg_socket","body_b":"link7","contact_count":216.0,"contact_point_centroid":[0.56999,0.03015,0.07997],"force_p95":72.76974,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.82041,"mean_force":44.74726,"phase_index":3.0,"phase_name":"retract_after_insert","phase_type":"retract","tcp_position_centroid":[0.48809,0.02986,0.15995]},{"body_a":"peg_socket","body_b":"link7","contact_count":484.0,"contact_point_centroid":[0.56998,0.03224,0.07997],"force_p95":96.18776,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":173.17656,"mean_force":52.82573,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.47211,0.02876,0.16563]},{"body_a":"peg_socket","body_b":"link6","contact_count":279.0,"contact_point_centroid":[0.57,0.02641,0.07997],"force_p95":114.4046,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":162.09452,"mean_force":90.3487,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.45228,0.02717,0.17297]}],"total_contact_groups":8},"final_pose_error":0.07822,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.48669,0.02982,0.18102],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1046.3629,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.48212,0.02677,0.16052],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08671,"object_to_goal_dist_start":0.26034,"object_z_max":0.3444,"peak_contact_force":257.72699,"phase_name":"arc_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":466.0,"raw_peak_contact_force":1046.3629,"subtask_id":"approach_sub","tcp_end":[0.44475,0.02654,0.17476],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5261,0.03027,0.14452],"object_pos_start":[0.48212,0.02677,0.16052],"object_to_goal_dist_end":0.07589,"object_to_goal_dist_start":0.08671,"object_z_max":0.16066,"peak_contact_force":14.52393,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":763.0,"raw_peak_contact_force":173.17656,"subtask_id":"approach_sub","tcp_end":[0.4889,0.03006,0.15924],"tcp_start":[0.44475,0.02654,0.17476],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52608,0.03024,0.1445],"object_pos_start":[0.5261,0.03027,0.14452],"object_to_goal_dist_end":0.07587,"object_to_goal_dist_start":0.07589,"object_z_max":0.14452,"peak_contact_force":311.4642,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":311.4642,"subtask_id":"insert_sub","tcp_end":[0.48889,0.03003,0.15921],"tcp_start":[0.4889,0.03006,0.15924],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52367,0.03,0.16578],"object_pos_start":[0.52608,0.03024,0.1445],"object_to_goal_dist_end":0.09391,"object_to_goal_dist_start":0.07587,"object_z_max":0.16575,"peak_contact_force":0.0,"phase_name":"retract_after_insert","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":216.0,"raw_peak_contact_force":251.82041,"subtask_id":"insert_sub","tcp_end":[0.48669,0.02982,0.18102],"tcp_start":[0.48889,0.03003,0.15921],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `989b6885a6cc20cf657766879d873fa27d37f906fbac12db49d02020abcc24a4`; realized-scene SHA-256: `b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.56757,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_approach.approach_speed":0.05327,"arc_approach.arc_height":0.2,"arc_approach.pos_tolerance":0.00103,"insert_into_hole.force_below_threshold":42.12189,"insert_into_hole.insert_speed":0.0307,"insert_into_hole.insertion_distance":0.07772,"insert_into_hole.pos_tolerance":0.0032,"lateral_align.align_speed":0.03371,"lateral_align.pos_tolerance":0.00269,"retract_after_insert.pos_tolerance":0.00405,"retract_after_insert.retract_speed":0.01612},"optimized_scores":{"best_composite_score":-0.14482,"best_fitness_score":0.46518,"best_task_score":0.81793},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":154.0,"contact_point_centroid":[0.54307,0.01112,0.07925],"force_p95":509.5627,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1068.15102,"mean_force":302.29614,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.43537,0.00765,0.1485]},{"body_a":"peg_socket","body_b":"link7","contact_count":615.0,"contact_point_centroid":[0.5461,0.03518,0.07994],"force_p95":332.36409,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":591.44871,"mean_force":270.68549,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.48128,0.03191,0.183]},{"body_a":"peg_socket","body_b":"link7","contact_count":380.0,"contact_point_centroid":[0.5461,0.04397,0.07999],"force_p95":149.54292,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":348.54526,"mean_force":114.85534,"phase_index":3.0,"phase_name":"retract_after_insert","phase_type":"retract","tcp_position_centroid":[0.49067,0.02623,0.16107]},{"body_a":"peg_socket","body_b":"link6","contact_count":664.0,"contact_point_centroid":[0.54611,0.01946,0.07991],"force_p95":313.56511,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":341.71022,"mean_force":294.35069,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.44962,0.0194,0.19763]},{"body_a":"peg_socket","body_b":"link6","contact_count":327.0,"contact_point_centroid":[0.54612,0.03538,0.07996],"force_p95":187.79615,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":251.53257,"mean_force":130.43724,"phase_index":1.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.46874,0.0267,0.20833]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54613,0.04308,0.07999],"force_p95":88.80217,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.20835,"mean_force":58.14657,"phase_index":2.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.49149,0.02769,0.16269]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.44231,0.00399,0.07916],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"arc_approach","phase_type":"approach","tcp_position_centroid":[0.43844,0.00396,0.09281]}],"total_contact_groups":7},"final_pose_error":0.07658,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48966,0.02694,0.18584],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1068.15102,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":931.0,"n_steps_budget":960.0,"object_pos_end":[0.49361,0.02586,0.18596],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10926,"object_to_goal_dist_start":0.26034,"object_z_max":0.34426,"peak_contact_force":314.92612,"phase_name":"arc_approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":827.0,"raw_peak_contact_force":1068.15102,"subtask_id":"approach_sub","tcp_end":[0.46391,0.02489,0.21273],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52558,0.03269,0.1427],"object_pos_start":[0.49361,0.02586,0.18596],"object_to_goal_dist_end":0.07519,"object_to_goal_dist_start":0.10926,"object_z_max":0.18596,"peak_contact_force":226.5986,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":942.0,"raw_peak_contact_force":591.44871,"subtask_id":"approach_sub","tcp_end":[0.49136,0.02807,0.16288],"tcp_start":[0.46391,0.02489,0.21273],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.52583,0.0319,0.1422],"object_pos_start":[0.52558,0.03269,0.1427],"object_to_goal_dist_end":0.07452,"object_to_goal_dist_start":0.07519,"object_z_max":0.14273,"peak_contact_force":92.20835,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":92.20835,"subtask_id":"insert_sub","tcp_end":[0.49162,0.02725,0.1624],"tcp_start":[0.49136,0.02807,0.16288],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52359,0.03156,0.16516],"object_pos_start":[0.52583,0.0319,0.1422],"object_to_goal_dist_end":0.09383,"object_to_goal_dist_start":0.07452,"object_z_max":0.16513,"peak_contact_force":0.0,"phase_name":"retract_after_insert","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":380.0,"raw_peak_contact_force":348.54526,"subtask_id":"insert_sub","tcp_end":[0.48966,0.02694,0.18584],"tcp_start":[0.49162,0.02725,0.1624],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```