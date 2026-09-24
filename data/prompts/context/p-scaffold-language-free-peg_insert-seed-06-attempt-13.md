## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → descend → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0827 | 0.85 | ✅ accepted |
| 12 | approach → align → descend → contact → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 13 | -0.1962 | 0.82 | ❌ rejected |
| 11 | approach → descend → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0428 | 0.84 | ❌ rejected |
| 10 | approach → align → insert → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.1091 | 0.83 | ❌ rejected |
| 9 | approach → descend → contact → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | 0.1648 | 0.82 | ❌ rejected |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.846, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=-0.083) — your mutation base

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
- id: approach_arc
  type: approach
  generator: arc_cartesian
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
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
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
- id: align_to_hole
  type: align
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
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
    align_tolerance:
      type: scalar
      range:
      - 0.001
      - 0.008
      default: 0.003
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
    descend_tolerance:
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
    on_failure: retry
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
- **approach_arc** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - pos_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=repeat
- **align_to_hole** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - align_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=repeat
- **descend_to_entry** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=repeat
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.1, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_force_limit: status=consumed; consumers=guards.max_insert_force.threshold (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=max_insert_force, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]
- **retract_after_insert** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat

## Design Metrics

- **Composite score**: -0.083
- **task_score** (E): 0.846
- **fitness_score**: 0.557  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_arc | 0.33 | 1.00 | 0.1057 |
| align_to_hole | 0.67 | 0.67 | 0.0997 |
| descend_to_entry | 0.00 | 0.67 | 0.0659 |
| insert_into_hole | 0.00 | 0.33 | 0.0003 |
| retract_after_insert | 1.00 | 0.00 | 0.0854 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_arc | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.460, 0.032, 0.209) | (0.504, -0.000, 0.340)→(0.492, 0.032, 0.185) | 0.260→0.111 | 1.00 / 1.000 | 304.130 | 1121.906 |
| align_to_hole | align | 0.67 / step_budget | (0.460, 0.032, 0.209)→(0.517, 0.034, 0.230) | (0.492, 0.032, 0.185)→(0.553, 0.033, 0.214) | 0.111→0.151 | 0.67 / 0.667 | 287.899 | 692.624 |
| descend_to_entry | descend | 0.00 / step_budget | (0.517, 0.034, 0.230)→(0.518, 0.023, 0.179) | (0.553, 0.033, 0.214)→(0.554, 0.021, 0.164) | 0.151→0.104 | 0.67 / 0.667 | 189.657 | 279.146 |
| insert_into_hole | insert | 0.00 / guard_failure | (0.515, 0.024, 0.151)→(0.515, 0.024, 0.151) | (0.554, 0.021, 0.164)→(0.551, 0.022, 0.136) | 0.104→0.081 | 0.33 / 0.333 | 62.823 | 230.637 |
| retract_after_insert | retract | 1.00 / step_budget | (0.515, 0.024, 0.151)→(0.516, 0.028, 0.237) | (0.551, 0.022, 0.136)→(0.551, 0.025, 0.221) | 0.081→0.153 | 0.00 / 0.000 | 0.000 | 243.338 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.897
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.897
- phase_score: 0.665
- phase_breakdown.approach_sub_score: 0.737
- phase_breakdown.insert_sub_score: 0.634

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.758
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.897
- **Median Q (composite search score)**: -0.157
- **K-run variance**: 0.0206
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.303


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.02703,"average_mean_iterations":12.36216,"average_solve_count":185.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_hole.align_speed":0.05295,"align_to_hole.align_tolerance":0.00313,"approach_arc.approach_speed":0.05794,"approach_arc.arc_height":0.13073,"approach_arc.pos_tolerance":0.00395,"descend_to_entry.descend_speed":0.07777,"descend_to_entry.descend_tolerance":0.00254,"insert_into_hole.insert_force_limit":35.82466,"insert_into_hole.insert_speed":0.02572,"insert_into_hole.insertion_distance":0.11159,"retract_after_insert.retract_speed":0.07659},"optimized_scores":{"best_composite_score":0.118,"best_fitness_score":0.758,"best_task_score":0.89706},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.45106,0.00575,0.07915],"force_p95":983.6126,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1031.8233,"mean_force":195.65117,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44671,0.00578,0.09264]},{"body_a":"peg_socket","body_b":"link7","contact_count":162.0,"contact_point_centroid":[0.55819,0.01343,0.07942],"force_p95":441.95263,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":930.52614,"mean_force":277.1277,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44644,0.00949,0.14448]},{"body_a":"peg_socket","body_b":"link7","contact_count":371.0,"contact_point_centroid":[0.56301,0.00786,0.07993],"force_p95":328.54248,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":404.22069,"mean_force":193.9623,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.48212,0.00545,0.18131]},{"body_a":"peg_socket","body_b":"link6","contact_count":737.0,"contact_point_centroid":[0.56302,0.01564,0.07991],"force_p95":281.20395,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":373.71648,"mean_force":262.60759,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44656,0.01715,0.17686]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.56303,0.00707,0.07982],"force_p95":245.05926,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":260.08785,"mean_force":131.09395,"phase_index":4.0,"phase_name":"retract_after_insert","phase_type":"retract","tcp_position_centroid":[0.50265,0.00423,0.10239]},{"body_a":"peg_socket","body_b":"link6","contact_count":290.0,"contact_point_centroid":[0.56303,0.01414,0.07996],"force_p95":148.15287,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":216.82964,"mean_force":131.31564,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.46024,0.01545,0.18778]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.56304,0.0072,0.07988],"force_p95":180.52651,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":188.46985,"mean_force":114.56125,"phase_index":3.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.50292,0.00436,0.10233]}],"total_contact_groups":7},"final_pose_error":0.01111,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.50078,0.00434,0.19124],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1031.8233,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48669,0.01782,0.17041],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09311,"object_to_goal_dist_start":0.26034,"object_z_max":0.34435,"peak_contact_force":272.85057,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":909.0,"raw_peak_contact_force":1031.8233,"subtask_id":"approach_sub","tcp_end":[0.45136,0.01829,0.18917],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":842.0,"n_steps_budget":990.0,"object_pos_end":[0.57102,0.02151,0.33643],"object_pos_start":[0.48669,0.01782,0.17041],"object_to_goal_dist_end":0.26695,"object_to_goal_dist_start":0.09311,"object_z_max":0.33299,"peak_contact_force":0.0,"phase_name":"align_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":661.0,"raw_peak_contact_force":404.22069,"subtask_id":"approach_sub","tcp_end":[0.53116,0.02032,0.33952],"tcp_start":[0.45136,0.01829,0.18917],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55343,0.00329,0.18301],"object_pos_start":[0.57102,0.02151,0.33643],"object_to_goal_dist_end":0.11609,"object_to_goal_dist_start":0.26695,"object_z_max":0.36401,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_sub","tcp_end":[0.51361,0.0021,0.18653],"tcp_start":[0.53116,0.02032,0.33952],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":257.0,"n_steps_budget":1000.0,"object_pos_end":[0.54259,0.00615,0.0974],"object_pos_start":[0.55343,0.00329,0.18301],"object_to_goal_dist_end":0.04642,"object_to_goal_dist_start":0.11609,"object_z_max":0.18301,"peak_contact_force":188.46985,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":188.46985,"subtask_id":"insert_sub","tcp_end":[0.5028,0.00432,0.10216],"tcp_start":[0.50286,0.00433,0.10221],"tcp_to_object_dist_end":0.04012,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":734.0,"n_steps_budget":840.0,"object_pos_end":[0.54036,0.00617,0.18577],"object_pos_start":[0.54245,0.00611,0.09722],"object_to_goal_dist_end":0.11338,"object_to_goal_dist_start":0.04622,"object_z_max":0.18568,"peak_contact_force":0.0,"phase_name":"retract_after_insert","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":9.0,"raw_peak_contact_force":260.08785,"tcp_end":[0.50078,0.00434,0.19124],"tcp_start":[0.5028,0.00432,0.10216],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":13.0,"average_failure_rate":0.0963,"average_mean_iterations":24.65926,"average_solve_count":135.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_hole.align_speed":0.0533,"align_to_hole.align_tolerance":0.00564,"approach_arc.approach_speed":0.06696,"approach_arc.arc_height":0.11235,"approach_arc.pos_tolerance":0.0043,"descend_to_entry.descend_speed":0.09435,"descend_to_entry.descend_tolerance":0.00253,"insert_into_hole.insert_force_limit":35.40474,"insert_into_hole.insert_speed":0.03134,"insert_into_hole.insertion_distance":0.07289,"retract_after_insert.retract_speed":0.05672},"optimized_scores":{"best_composite_score":-0.20917,"best_fitness_score":0.43083,"best_task_score":0.81893},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.53352,0.00137,0.07736],"force_p95":980.55019,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1239.7599,"mean_force":258.67841,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.43784,0.01101,0.10328]},{"body_a":"peg_socket","body_b":"link7","contact_count":41.0,"contact_point_centroid":[0.54687,0.00954,0.078],"force_p95":830.5775,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1073.69874,"mean_force":209.0532,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.43749,0.01177,0.11212]},{"body_a":"peg_socket","body_b":"link7","contact_count":393.0,"contact_point_centroid":[0.56995,0.03809,0.07992],"force_p95":357.0209,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":906.93519,"mean_force":286.15331,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.49743,0.04333,0.17708]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.45047,0.01023,0.07952],"force_p95":668.1712,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":890.89493,"mean_force":148.48249,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44227,0.01018,0.09233]},{"body_a":"world","body_b":"link6","contact_count":113.0,"contact_point_centroid":[0.70396,0.01682,-8e-05],"force_p95":675.7814,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":845.206,"mean_force":436.87807,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.51313,0.03808,0.17555]},{"body_a":"peg_socket","body_b":"link6","contact_count":857.0,"contact_point_centroid":[0.56995,0.03429,0.07987],"force_p95":294.32208,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":482.203,"mean_force":266.1772,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44193,0.03212,0.19084]},{"body_a":"world","body_b":"link6","contact_count":147.0,"contact_point_centroid":[0.6976,0.00161,-7e-05],"force_p95":346.50943,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":390.65906,"mean_force":226.46192,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.51979,0.03264,0.17729]},{"body_a":"peg_socket","body_b":"link6","contact_count":416.0,"contact_point_centroid":[0.56997,0.03549,0.07995],"force_p95":295.41143,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":368.6788,"mean_force":201.18535,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.475,0.04088,0.21277]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.65032,-0.05067,-5e-05],"force_p95":240.65228,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":249.56095,"mean_force":160.47421,"phase_index":3.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.53581,0.03367,0.18981]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.66647,-0.06089,-3e-05],"force_p95":223.85593,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.22558,"mean_force":116.62604,"phase_index":4.0,"phase_name":"retract_after_insert","phase_type":"retract","tcp_position_centroid":[0.53739,0.03122,0.19204]}],"total_contact_groups":10},"final_pose_error":0.0189,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.54073,0.04275,0.27552],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1239.7599,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49405,0.0414,0.19834],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.12551,"object_to_goal_dist_start":0.26034,"object_z_max":0.34432,"peak_contact_force":310.59065,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":931.0,"raw_peak_contact_force":1239.7599,"subtask_id":"approach_sub","tcp_end":[0.4631,0.04269,0.22365],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54896,0.03068,0.15379],"object_pos_start":[0.49405,0.0414,0.19834],"object_to_goal_dist_end":0.09372,"object_to_goal_dist_start":0.12551,"object_z_max":0.1984,"peak_contact_force":470.63668,"phase_name":"align_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":922.0,"raw_peak_contact_force":906.93519,"subtask_id":"approach_sub","tcp_end":[0.51614,0.0329,0.17654],"tcp_start":[0.4631,0.04269,0.22365],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":241.0,"n_steps_budget":660.0,"object_pos_end":[0.5692,0.02927,0.16823],"object_pos_start":[0.54896,0.03068,0.15379],"object_to_goal_dist_end":0.11589,"object_to_goal_dist_start":0.09372,"object_z_max":0.16798,"peak_contact_force":318.41579,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":147.0,"raw_peak_contact_force":390.65906,"subtask_id":"approach_sub","tcp_end":[0.5357,0.03388,0.18961],"tcp_start":[0.51614,0.0329,0.17654],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.56942,0.02884,0.16865],"object_pos_start":[0.5692,0.02927,0.16823],"object_to_goal_dist_end":0.11623,"object_to_goal_dist_start":0.11589,"object_z_max":0.1691,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":249.56095,"subtask_id":"insert_sub","tcp_end":[0.53642,0.03257,0.19085],"tcp_start":[0.5362,0.03299,0.19047],"tcp_to_object_dist_end":0.03994,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":945.0,"n_steps_budget":1000.0,"object_pos_end":[0.57379,0.03568,0.25415],"object_pos_start":[0.56992,0.02791,0.16949],"object_to_goal_dist_end":0.19247,"object_to_goal_dist_start":0.11694,"object_z_max":0.25407,"peak_contact_force":0.0,"phase_name":"retract_after_insert","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3.0,"raw_peak_contact_force":241.22558,"tcp_end":[0.54073,0.04275,0.27552],"tcp_start":[0.53642,0.03257,0.19085],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.9542,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_hole.align_speed":0.05342,"align_to_hole.align_tolerance":0.00767,"approach_arc.approach_speed":0.08212,"approach_arc.arc_height":0.14695,"approach_arc.pos_tolerance":0.00559,"descend_to_entry.descend_speed":0.02877,"descend_to_entry.descend_tolerance":0.00332,"insert_into_hole.insert_force_limit":37.24969,"insert_into_hole.insert_speed":0.03859,"insert_into_hole.insertion_distance":0.14275,"retract_after_insert.retract_speed":0.08893},"optimized_scores":{"best_composite_score":-0.15695,"best_fitness_score":0.48305,"best_task_score":0.82169},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":114.0,"contact_point_centroid":[0.54339,0.01499,0.0791],"force_p95":544.01771,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1094.13629,"mean_force":320.60698,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.43785,0.01689,0.14377]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.44636,0.01088,0.07882],"force_p95":461.94283,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":923.88567,"mean_force":83.98961,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44237,0.01084,0.09209]},{"body_a":"world","body_b":"link6","contact_count":166.0,"contact_point_centroid":[0.69155,0.02937,-0.00016],"force_p95":623.66547,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":766.7157,"mean_force":414.79978,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.49851,0.04993,0.16726]},{"body_a":"peg_socket","body_b":"link7","contact_count":523.0,"contact_point_centroid":[0.54609,0.04047,0.07993],"force_p95":342.70065,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":747.81907,"mean_force":284.83302,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.48199,0.03942,0.18045]},{"body_a":"world","body_b":"link6","contact_count":977.0,"contact_point_centroid":[0.70164,0.02431,-0.00011],"force_p95":379.01442,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":446.77808,"mean_force":300.80986,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.50543,0.04252,0.16695]},{"body_a":"peg_socket","body_b":"link6","contact_count":706.0,"contact_point_centroid":[0.54611,0.03481,0.07993],"force_p95":326.15691,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":345.70834,"mean_force":312.46372,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.45929,0.03351,0.2047]},{"body_a":"peg_socket","body_b":"link6","contact_count":156.0,"contact_point_centroid":[0.54613,0.03509,0.07997],"force_p95":257.93502,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":285.30711,"mean_force":199.64114,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.47044,0.03666,0.20837]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.71082,0.01732,-4e-05],"force_p95":248.17655,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.88055,"mean_force":196.84053,"phase_index":3.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.50608,0.03369,0.16104]},{"body_a":"world","body_b":"link6","contact_count":8.0,"contact_point_centroid":[0.71061,0.01688,-9e-05],"force_p95":185.66208,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":228.69909,"mean_force":51.34161,"phase_index":4.0,"phase_name":"retract_after_insert","phase_type":"retract","tcp_position_centroid":[0.50616,0.03404,0.16121]},{"body_a":"attachment","body_b":"peg_socket","contact_count":6.0,"contact_point_centroid":[0.45624,0.00895,0.07973],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44453,0.01072,0.09147]}],"total_contact_groups":10},"final_pose_error":0.01851,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.50503,0.03642,0.24292],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1094.13629,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":932.0,"n_steps_budget":990.0,"object_pos_end":[0.49605,0.0366,0.18717],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11331,"object_to_goal_dist_start":0.26034,"object_z_max":0.34427,"peak_contact_force":328.9487,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":837.0,"raw_peak_contact_force":1094.13629,"subtask_id":"approach_sub","tcp_end":[0.46687,0.03637,0.21453],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":907.0,"n_steps_budget":1000.0,"object_pos_end":[0.53778,0.04545,0.15079],"object_pos_start":[0.49605,0.0366,0.18717],"object_to_goal_dist_end":0.09222,"object_to_goal_dist_start":0.11331,"object_z_max":0.18717,"peak_contact_force":393.06143,"phase_name":"align_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":845.0,"raw_peak_contact_force":766.7157,"subtask_id":"approach_sub","tcp_end":[0.50484,0.04808,0.17333],"tcp_start":[0.46687,0.03637,0.21453],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54058,0.03158,0.14089],"object_pos_start":[0.53778,0.04545,0.15079],"object_to_goal_dist_end":0.0797,"object_to_goal_dist_start":0.09222,"object_z_max":0.1511,"peak_contact_force":250.55527,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":977.0,"raw_peak_contact_force":446.77808,"subtask_id":"approach_sub","tcp_end":[0.50607,0.03372,0.16101],"tcp_start":[0.50484,0.04808,0.17333],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5406,0.03152,0.14096],"object_pos_start":[0.54058,0.03158,0.14089],"object_to_goal_dist_end":0.07974,"object_to_goal_dist_start":0.0797,"object_z_max":0.14109,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":253.88055,"subtask_id":"insert_sub","tcp_end":[0.50615,0.03362,0.16117],"tcp_start":[0.50616,0.03369,0.16119],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.53984,0.03356,0.22342],"object_pos_start":[0.54067,0.03147,0.14108],"object_to_goal_dist_end":0.15258,"object_to_goal_dist_start":0.07984,"object_z_max":0.2233,"peak_contact_force":0.0,"phase_name":"retract_after_insert","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":8.0,"raw_peak_contact_force":228.69909,"tcp_end":[0.50503,0.03642,0.24292],"tcp_start":[0.50615,0.03362,0.16117],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```