## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → descend → contact → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 13 | -0.1962 | 0.82 | ❌ rejected |
| 11 | approach → descend → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0428 | 0.84 | ❌ rejected |
| 10 | approach → align → insert → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.1091 | 0.83 | ❌ rejected |
| 9 | approach → descend → contact → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.1648 | 0.82 | ❌ rejected |
| 8 | approach → descend → contact → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.1965 | 0.84 | ❌ rejected |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.196) — your mutation base

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

- **Composite score**: -0.196
- **task_score** (E): 0.820
- **fitness_score**: 0.574  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.770

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_above | 0.00 | 1.00 | 0.1501 |
| align_to_hole | 0.67 | 0.00 | 0.0575 |
| descend_to_entry | 0.67 | 1.00 | 0.0688 |
| contact_entry | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_above | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.440, 0.010, 0.164) | (0.504, -0.000, 0.340)→(0.478, 0.011, 0.152) | 0.260→0.077 | 1.00 / 1.667 | 222.005 | 1161.821 |
| align_to_hole | align | 0.67 / step_budget | (0.440, 0.010, 0.164)→(0.479, 0.018, 0.204) | (0.478, 0.011, 0.152)→(0.516, 0.020, 0.191) | 0.077→0.116 | 0.00 / 0.000 | 0.000 | 133.754 |
| descend_to_entry | descend | 0.67 / step_budget | (0.479, 0.018, 0.204)→(0.492, 0.018, 0.138) | (0.516, 0.020, 0.191)→(0.530, 0.019, 0.125) | 0.116→0.062 | 1.00 / 1.000 | 170.105 | 276.123 |
| contact_entry | contact | 0.00 / guard_failure | (0.492, 0.018, 0.138)→(0.492, 0.018, 0.138) | (0.530, 0.019, 0.125)→(0.530, 0.019, 0.125) | 0.062→0.062 | 1.00 / 1.000 | 327.995 | 327.995 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.828
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.828
- phase_score: 0.419
- phase_breakdown.approach_sub_score: 0.733
- phase_breakdown.insert_sub_score: 0.285

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.583
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.828
- **Median Q (composite search score)**: -0.196
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.293


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":17.0,"average_failure_rate":0.17347,"average_mean_iterations":38.18367,"average_solve_count":98.0,"average_success_count":81.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_hole.align_speed":0.03621,"align_to_hole.align_tolerance":0.00362,"approach_to_above.approach_speed":0.0621,"approach_to_above.arc_height":0.06256,"approach_to_above.pos_tolerance":0.00325,"contact_entry.contact_force_threshold":16.08538,"contact_entry.contact_speed":0.01724,"descend_to_entry.descend_speed":0.05941,"descend_to_entry.descend_tolerance":0.00406,"insert_into_hole.insert_force_limit":37.58939,"insert_into_hole.insert_speed":0.02522,"insert_into_hole.insertion_distance":0.14074,"retract_after_insert.retract_speed":0.05036},"optimized_scores":{"best_composite_score":-0.20585,"best_fitness_score":0.56415,"best_task_score":0.82283},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":414.0,"contact_point_centroid":[0.55998,-0.00267,0.07971],"force_p95":311.34298,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1084.36999,"mean_force":189.43528,"phase_index":0.0,"phase_name":"approach_to_above","phase_type":"approach","tcp_position_centroid":[0.4455,-0.00601,0.15585]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.44593,-0.0037,0.07928],"force_p95":574.42704,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":883.7339,"mean_force":110.46674,"phase_index":0.0,"phase_name":"approach_to_above","phase_type":"approach","tcp_position_centroid":[0.44151,-0.00365,0.09289]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.53259,0.01768,0.07956],"force_p95":456.07475,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":482.74046,"mean_force":309.59036,"phase_index":0.0,"phase_name":"approach_to_above","phase_type":"approach","tcp_position_centroid":[0.43796,-0.00386,0.0998]},{"body_a":"peg_socket","body_b":"link6","contact_count":353.0,"contact_point_centroid":[0.563,-0.00794,0.07931],"force_p95":325.63107,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":411.09176,"mean_force":221.5103,"phase_index":0.0,"phase_name":"approach_to_above","phase_type":"approach","tcp_position_centroid":[0.4466,-0.00627,0.16203]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56303,-0.01546,0.07999],"force_p95":325.38172,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":325.38172,"mean_force":325.38172,"phase_index":3.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.49344,-0.01171,0.14313]},{"body_a":"peg_socket","body_b":"link7","contact_count":78.0,"contact_point_centroid":[0.56301,-0.01506,0.07993],"force_p95":139.08774,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":259.19347,"mean_force":96.05699,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.49164,-0.01164,0.14807]},{"body_a":"peg_socket","body_b":"link7","contact_count":70.0,"contact_point_centroid":[0.56247,-0.00239,0.07998],"force_p95":140.35089,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":142.16162,"mean_force":60.77587,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.44721,-0.00696,0.16273]},{"body_a":"peg_socket","body_b":"link6","contact_count":30.0,"contact_point_centroid":[0.56298,-0.00813,0.07936],"force_p95":106.75037,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":107.62575,"mean_force":49.02018,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.4467,-0.00691,0.16239]},{"body_a":"peg_socket","body_b":"link7","contact_count":13.0,"contact_point_centroid":[0.5327,-0.0426,0.07961],"force_p95":0.0,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_above","phase_type":"approach","tcp_position_centroid":[0.43781,-0.00384,0.09871]}],"total_contact_groups":9},"final_pose_error":0.0638,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49344,-0.01172,0.14307],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1084.36999,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.48467,-0.0069,0.15006],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07205,"object_to_goal_dist_start":0.26034,"object_z_max":0.34437,"peak_contact_force":210.51185,"phase_name":"approach_to_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":803.0,"raw_peak_contact_force":1084.36999,"subtask_id":"approach_sub","tcp_end":[0.44648,-0.00687,0.16196],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52141,-0.01087,0.19052],"object_pos_start":[0.48467,-0.0069,0.15006],"object_to_goal_dist_end":0.1131,"object_to_goal_dist_start":0.07205,"object_z_max":0.19047,"peak_contact_force":0.0,"phase_name":"align_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":100.0,"raw_peak_contact_force":142.16162,"subtask_id":"approach_sub","tcp_end":[0.4834,-0.01085,0.20297],"tcp_start":[0.44648,-0.00687,0.16196],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.53141,-0.01172,0.13054],"object_pos_start":[0.52141,-0.01087,0.19052],"object_to_goal_dist_end":0.06065,"object_to_goal_dist_start":0.1131,"object_z_max":0.19052,"peak_contact_force":94.84896,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":78.0,"raw_peak_contact_force":259.19347,"subtask_id":"approach_sub","tcp_end":[0.49344,-0.01171,0.14313],"tcp_start":[0.4834,-0.01085,0.20297],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53141,-0.01173,0.13049],"object_pos_start":[0.53141,-0.01172,0.13054],"object_to_goal_dist_end":0.06061,"object_to_goal_dist_start":0.06065,"object_z_max":0.13054,"peak_contact_force":325.38172,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":325.38172,"subtask_id":"insert_sub","tcp_end":[0.49344,-0.01172,0.14307],"tcp_start":[0.49344,-0.01171,0.14313],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":15.0,"average_failure_rate":0.14286,"average_mean_iterations":32.57143,"average_solve_count":105.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_hole.align_speed":0.03299,"align_to_hole.align_tolerance":0.00194,"approach_to_above.approach_speed":0.09052,"approach_to_above.arc_height":0.14813,"approach_to_above.pos_tolerance":0.00812,"contact_entry.contact_force_threshold":12.42897,"contact_entry.contact_speed":0.02347,"descend_to_entry.descend_speed":0.0454,"descend_to_entry.descend_tolerance":0.00396,"insert_into_hole.insert_force_limit":33.38593,"insert_into_hole.insert_speed":0.03282,"insert_into_hole.insertion_distance":0.08093,"retract_after_insert.retract_speed":0.05725},"optimized_scores":{"best_composite_score":-0.18716,"best_fitness_score":0.58284,"best_task_score":0.82797},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.45249,0.00965,0.07939],"force_p95":976.48149,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1015.1781,"mean_force":239.97431,"phase_index":0.0,"phase_name":"approach_to_above","phase_type":"approach","tcp_position_centroid":[0.44725,0.0096,0.09287]},{"body_a":"peg_socket","body_b":"link7","contact_count":157.0,"contact_point_centroid":[0.56298,0.01608,0.07943],"force_p95":459.40033,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":933.73437,"mean_force":277.82013,"phase_index":0.0,"phase_name":"approach_to_above","phase_type":"approach","tcp_position_centroid":[0.44894,0.01424,0.1367]},{"body_a":"peg_socket","body_b":"link7","contact_count":26.0,"contact_point_centroid":[0.53912,0.00162,0.079],"force_p95":656.00017,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":717.25303,"mean_force":382.71639,"phase_index":0.0,"phase_name":"approach_to_above","phase_type":"approach","tcp_position_centroid":[0.44453,0.01045,0.10329]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56995,0.02982,0.07997],"force_p95":299.88879,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":299.88879,"mean_force":299.88879,"phase_index":3.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.4975,0.03154,0.13425]},{"body_a":"peg_socket","body_b":"link6","contact_count":190.0,"contact_point_centroid":[0.56997,0.02193,0.07984],"force_p95":279.26829,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":296.6811,"mean_force":250.79777,"phase_index":0.0,"phase_name":"approach_to_above","phase_type":"approach","tcp_position_centroid":[0.44177,0.02169,0.15579]},{"body_a":"peg_socket","body_b":"link7","contact_count":373.0,"contact_point_centroid":[0.56998,0.02824,0.07993],"force_p95":189.66785,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":252.59755,"mean_force":125.38483,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.48929,0.02991,0.14681]},{"body_a":"peg_socket","body_b":"link6","contact_count":114.0,"contact_point_centroid":[0.56999,0.02524,0.07994],"force_p95":108.29146,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.68483,"mean_force":63.98162,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.43489,0.02554,0.15666]}],"total_contact_groups":7},"final_pose_error":0.05556,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.49752,0.03159,0.13414],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1015.1781,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.47314,0.02584,0.14664],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07635,"object_to_goal_dist_start":0.26034,"object_z_max":0.3444,"peak_contact_force":238.30475,"phase_name":"approach_to_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":381.0,"raw_peak_contact_force":1015.1781,"subtask_id":"approach_sub","tcp_end":[0.43412,0.02533,0.15541],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50893,0.02886,0.17819],"object_pos_start":[0.47314,0.02584,0.14664],"object_to_goal_dist_end":0.10273,"object_to_goal_dist_start":0.07635,"object_z_max":0.17815,"peak_contact_force":0.0,"phase_name":"align_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":114.0,"raw_peak_contact_force":136.68483,"subtask_id":"approach_sub","tcp_end":[0.47004,0.02836,0.18752],"tcp_start":[0.43412,0.02533,0.15541],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.53627,0.03233,0.12442],"object_pos_start":[0.50893,0.02886,0.17819],"object_to_goal_dist_end":0.06584,"object_to_goal_dist_start":0.10273,"object_z_max":0.17819,"peak_contact_force":170.718,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":373.0,"raw_peak_contact_force":252.59755,"subtask_id":"approach_sub","tcp_end":[0.4975,0.03154,0.13425],"tcp_start":[0.47004,0.02836,0.18752],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.53629,0.03237,0.12432],"object_pos_start":[0.53627,0.03233,0.12442],"object_to_goal_dist_end":0.0658,"object_to_goal_dist_start":0.06584,"object_z_max":0.12442,"peak_contact_force":299.88879,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":299.88879,"subtask_id":"insert_sub","tcp_end":[0.49752,0.03159,0.13414],"tcp_start":[0.4975,0.03154,0.13425],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.73984,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_hole.align_speed":0.0499,"align_to_hole.align_tolerance":0.00231,"approach_to_above.approach_speed":0.07108,"approach_to_above.arc_height":0.07355,"approach_to_above.pos_tolerance":0.00382,"contact_entry.contact_force_threshold":12.42892,"contact_entry.contact_speed":0.02771,"descend_to_entry.descend_speed":0.02675,"descend_to_entry.descend_tolerance":0.00269,"insert_into_hole.insert_force_limit":35.9084,"insert_into_hole.insert_speed":0.03991,"insert_into_hole.insertion_distance":0.05156,"retract_after_insert.retract_speed":0.08109},"optimized_scores":{"best_composite_score":-0.19553,"best_fitness_score":0.57447,"best_task_score":0.80827},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":366.0,"contact_point_centroid":[0.54608,0.01583,0.07951],"force_p95":904.32133,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1385.91634,"mean_force":275.81239,"phase_index":0.0,"phase_name":"approach_to_above","phase_type":"approach","tcp_position_centroid":[0.43492,0.01297,0.16895]},{"body_a":"peg_socket","body_b":"link7","contact_count":437.0,"contact_point_centroid":[0.54389,0.01893,0.0797],"force_p95":770.5899,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1317.10174,"mean_force":262.74011,"phase_index":0.0,"phase_name":"approach_to_above","phase_type":"approach","tcp_position_centroid":[0.43416,0.01234,0.16225]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.43944,0.00681,0.0795],"force_p95":560.35128,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":862.07888,"mean_force":107.75986,"phase_index":0.0,"phase_name":"approach_to_above","phase_type":"approach","tcp_position_centroid":[0.43558,0.00676,0.09349]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54613,0.04282,0.07565],"force_p95":358.71332,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":358.71332,"mean_force":358.71332,"phase_index":3.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.48563,0.03454,0.13602]},{"body_a":"peg_socket","body_b":"link7","contact_count":519.0,"contact_point_centroid":[0.54613,0.0486,0.07977],"force_p95":195.18669,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":316.57925,"mean_force":104.75821,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.48454,0.03801,0.14806]},{"body_a":"peg_socket","body_b":"link6","contact_count":34.0,"contact_point_centroid":[0.54614,0.01718,0.07997],"force_p95":62.58954,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.41424,"mean_force":21.42599,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.4395,0.01105,0.17456]},{"body_a":"peg_socket","body_b":"link7","contact_count":74.0,"contact_point_centroid":[0.54502,0.02127,0.07998],"force_p95":55.94604,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.99807,"mean_force":38.05247,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.43994,0.01131,0.1749]}],"total_contact_groups":7},"final_pose_error":0.05623,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48567,0.03445,0.13605],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1385.91634,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.47576,0.01409,0.15843],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08329,"object_to_goal_dist_start":0.26034,"object_z_max":0.34409,"peak_contact_force":217.19761,"phase_name":"approach_to_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":811.0,"raw_peak_contact_force":1385.91634,"subtask_id":"approach_sub","tcp_end":[0.43924,0.01092,0.17445],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":942.0,"n_steps_budget":990.0,"object_pos_end":[0.51848,0.04053,0.20498],"object_pos_start":[0.47576,0.01409,0.15843],"object_to_goal_dist_end":0.13268,"object_to_goal_dist_start":0.08329,"object_z_max":0.20494,"peak_contact_force":0.0,"phase_name":"align_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":108.0,"raw_peak_contact_force":122.41424,"subtask_id":"approach_sub","tcp_end":[0.48219,0.03739,0.22151],"tcp_start":[0.43924,0.01092,0.17445],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52207,0.03745,0.11977],"object_pos_start":[0.51848,0.04053,0.20498],"object_to_goal_dist_end":0.05892,"object_to_goal_dist_start":0.13268,"object_z_max":0.20498,"peak_contact_force":244.74684,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":519.0,"raw_peak_contact_force":316.57925,"subtask_id":"approach_sub","tcp_end":[0.48563,0.03454,0.13602],"tcp_start":[0.48219,0.03739,0.22151],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.52211,0.03737,0.1198],"object_pos_start":[0.52207,0.03745,0.11977],"object_to_goal_dist_end":0.0589,"object_to_goal_dist_start":0.05892,"object_z_max":0.11977,"peak_contact_force":358.71332,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":358.71332,"subtask_id":"insert_sub","tcp_end":[0.48567,0.03445,0.13605],"tcp_start":[0.48563,0.03454,0.13602],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```