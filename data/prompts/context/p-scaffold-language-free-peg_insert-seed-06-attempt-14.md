## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → descend → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.1070 | 0.84 | ❌ rejected |
| 13 | approach → align → descend → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0827 | 0.85 | ✅ accepted |
| 12 | approach → align → descend → contact → insert → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 13 | -0.1962 | 0.82 | ❌ rejected |
| 11 | approach → descend → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.0428 | 0.84 | ❌ rejected |
| 10 | approach → align → insert → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.1091 | 0.83 | ❌ rejected |

**Proposal policy**: task_score is 0.84 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.107) — your mutation base

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

- **Composite score**: -0.107
- **task_score** (E): 0.836
- **fitness_score**: 0.533  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.640

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_arc | 0.33 | 1.00 | 0.1049 |
| align_to_hole | 0.33 | 0.67 | 0.0849 |
| descend_to_entry | 0.00 | 0.67 | 0.0633 |
| insert_into_hole | 0.00 | 0.33 | 0.0315 |
| retract_after_insert | 1.00 | 0.00 | 0.0869 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_arc | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.462, 0.032, 0.209) | (0.504, -0.000, 0.340)→(0.493, 0.031, 0.185) | 0.260→0.110 | 1.00 / 1.000 | 284.079 | 1930.719 |
| align_to_hole | align | 0.33 / step_budget | (0.462, 0.032, 0.209)→(0.507, 0.032, 0.235) | (0.493, 0.031, 0.185)→(0.542, 0.032, 0.218) | 0.110→0.151 | 0.67 / 0.667 | 319.441 | 504.866 |
| descend_to_entry | descend | 0.00 / step_budget | (0.507, 0.032, 0.235)→(0.514, 0.025, 0.184) | (0.542, 0.032, 0.218)→(0.550, 0.025, 0.168) | 0.151→0.107 | 0.67 / 0.667 | 93.830 | 389.537 |
| insert_into_hole | insert | 0.00 / guard_failure | (0.514, 0.024, 0.184)→(0.510, 0.025, 0.153) | (0.550, 0.025, 0.168)→(0.546, 0.026, 0.137) | 0.107→0.080 | 0.33 / 0.333 | 39.481 | 104.619 |
| retract_after_insert | retract | 1.00 / step_budget | (0.510, 0.025, 0.153)→(0.510, 0.028, 0.240) | (0.546, 0.025, 0.137)→(0.546, 0.028, 0.223) | 0.080→0.154 | 0.00 / 0.000 | 0.000 | 151.065 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.866
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.866
- phase_score: 0.552
- phase_breakdown.approach_sub_score: 0.570
- phase_breakdown.insert_sub_score: 0.544

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.678
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.866
- **Median Q (composite search score)**: -0.153
- **K-run variance**: 0.0110
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.284


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":75.0,"average_failure_rate":0.28302,"average_mean_iterations":61.98113,"average_solve_count":265.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_hole.align_speed":0.0557,"align_to_hole.align_tolerance":0.00548,"approach_arc.approach_speed":0.05943,"approach_arc.arc_height":0.13902,"approach_arc.pos_tolerance":0.00585,"descend_to_entry.descend_speed":0.05347,"descend_to_entry.descend_tolerance":0.00331,"insert_into_hole.insert_force_limit":34.82328,"insert_into_hole.insert_speed":0.03806,"insert_into_hole.insertion_distance":0.09347,"retract_after_insert.retract_speed":0.07165},"optimized_scores":{"best_composite_score":0.03776,"best_fitness_score":0.67776,"best_task_score":0.86642},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":724.0,"contact_point_centroid":[0.56302,0.01415,0.07992],"force_p95":277.70932,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1049.52505,"mean_force":265.54327,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44721,0.01567,0.176]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.45122,0.00549,0.07911],"force_p95":985.22338,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1033.19832,"mean_force":195.97857,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44687,0.00553,0.09256]},{"body_a":"peg_socket","body_b":"link7","contact_count":185.0,"contact_point_centroid":[0.55873,0.01341,0.07948],"force_p95":487.38042,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":932.34104,"mean_force":279.52974,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44733,0.00931,0.1474]},{"body_a":"peg_socket","body_b":"link7","contact_count":353.0,"contact_point_centroid":[0.56301,0.007,0.07992],"force_p95":343.10871,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":397.66701,"mean_force":191.07637,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.48136,0.0049,0.1809]},{"body_a":"peg_socket","body_b":"link6","contact_count":227.0,"contact_point_centroid":[0.56303,0.01251,0.07995],"force_p95":145.75396,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":210.24874,"mean_force":133.08772,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.46091,0.01369,0.18708]}],"total_contact_groups":5},"final_pose_error":0.01089,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.50129,0.00693,0.19873],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1049.52505,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48747,0.01585,0.16954],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09179,"object_to_goal_dist_start":0.26034,"object_z_max":0.34435,"peak_contact_force":275.64716,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":919.0,"raw_peak_contact_force":1049.52505,"subtask_id":"approach_sub","tcp_end":[0.45207,0.01629,0.18815],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":753.0,"n_steps_budget":930.0,"object_pos_end":[0.57046,0.02347,0.32966],"object_pos_start":[0.48747,0.01585,0.16954],"object_to_goal_dist_end":0.26047,"object_to_goal_dist_start":0.09179,"object_z_max":0.32609,"peak_contact_force":0.0,"phase_name":"align_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":580.0,"raw_peak_contact_force":397.66701,"subtask_id":"approach_sub","tcp_end":[0.53062,0.0221,0.33302],"tcp_start":[0.45207,0.01629,0.18815],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55539,0.00682,0.19896],"object_pos_start":[0.57046,0.02347,0.32966],"object_to_goal_dist_end":0.1314,"object_to_goal_dist_start":0.26047,"object_z_max":0.35906,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_sub","tcp_end":[0.51559,0.00544,0.20274],"tcp_start":[0.53062,0.0221,0.33302],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":263.0,"n_steps_budget":1000.0,"object_pos_end":[0.54278,0.00886,0.1041],"object_pos_start":[0.55539,0.00682,0.19896],"object_to_goal_dist_end":0.0499,"object_to_goal_dist_start":0.1314,"object_z_max":0.19896,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_sub","tcp_end":[0.50319,0.00688,0.10946],"tcp_start":[0.51559,0.00544,0.20274],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.5408,0.00896,0.19286],"object_pos_start":[0.54278,0.00886,0.1041],"object_to_goal_dist_end":0.12034,"object_to_goal_dist_start":0.0499,"object_z_max":0.19276,"peak_contact_force":0.0,"phase_name":"retract_after_insert","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.50129,0.00693,0.19873],"tcp_start":[0.50319,0.00688,0.10946],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":13.0,"average_failure_rate":0.09091,"average_mean_iterations":23.55944,"average_solve_count":143.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_hole.align_speed":0.04622,"align_to_hole.align_tolerance":0.00631,"approach_arc.approach_speed":0.07334,"approach_arc.arc_height":0.13289,"approach_arc.pos_tolerance":0.00482,"descend_to_entry.descend_speed":0.08719,"descend_to_entry.descend_tolerance":0.00311,"insert_into_hole.insert_force_limit":33.36462,"insert_into_hole.insert_speed":0.02988,"insert_into_hole.insertion_distance":0.11144,"retract_after_insert.retract_speed":0.0511},"optimized_scores":{"best_composite_score":-0.20615,"best_fitness_score":0.43385,"best_task_score":0.82421},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":859.0,"contact_point_centroid":[0.56992,0.02915,0.07976],"force_p95":528.37812,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3655.90075,"mean_force":345.54094,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44733,0.02679,0.18172]},{"body_a":"peg_socket","body_b":"link7","contact_count":291.0,"contact_point_centroid":[0.56617,0.01957,0.07964],"force_p95":2666.54305,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3586.88663,"mean_force":493.9296,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44691,0.01335,0.14772]},{"body_a":"peg_socket","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53818,0.00153,0.07843],"force_p95":866.73826,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":935.54204,"mean_force":368.53337,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44223,0.01103,0.10116]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.4512,0.00994,0.0792],"force_p95":551.31024,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":918.8504,"mean_force":102.09449,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.44444,0.0099,0.09208]},{"body_a":"world","body_b":"link6","contact_count":110.0,"contact_point_centroid":[0.70057,0.01619,-0.0001],"force_p95":625.7456,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":806.48899,"mean_force":428.72462,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.51251,0.04,0.17708]},{"body_a":"world","body_b":"link6","contact_count":202.0,"contact_point_centroid":[0.70274,0.00632,-0.00011],"force_p95":442.58568,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":763.38846,"mean_force":273.76995,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.51768,0.03308,0.1763]},{"body_a":"peg_socket","body_b":"link7","contact_count":415.0,"contact_point_centroid":[0.56996,0.03528,0.07993],"force_p95":352.25193,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":516.02074,"mean_force":283.36322,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.49776,0.04452,0.17829]},{"body_a":"peg_socket","body_b":"link6","contact_count":394.0,"contact_point_centroid":[0.56997,0.03562,0.07994],"force_p95":291.40812,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":340.9461,"mean_force":207.89059,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.47752,0.03973,0.211]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.65027,-0.05088,-2e-05],"force_p95":248.14894,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.31835,"mean_force":143.64755,"phase_index":4.0,"phase_name":"retract_after_insert","phase_type":"retract","tcp_position_centroid":[0.53501,0.03654,0.18802]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.65598,-0.0436,-3e-05],"force_p95":87.0704,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.0704,"mean_force":87.0704,"phase_index":3.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.53374,0.03785,0.18597]}],"total_contact_groups":10},"final_pose_error":0.0206,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.53779,0.04639,0.26896],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":3655.90075,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4984,0.03953,0.19665],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.12318,"object_to_goal_dist_start":0.26034,"object_z_max":0.34434,"peak_contact_force":258.38588,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1182.0,"raw_peak_contact_force":3655.90075,"subtask_id":"approach_sub","tcp_end":[0.46782,0.04101,0.22239],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54784,0.03309,0.15515],"object_pos_start":[0.4984,0.03953,0.19665],"object_to_goal_dist_end":0.09503,"object_to_goal_dist_start":0.12318,"object_z_max":0.19668,"peak_contact_force":725.72795,"phase_name":"align_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":919.0,"raw_peak_contact_force":806.48899,"subtask_id":"approach_sub","tcp_end":[0.51532,0.03592,0.17827],"tcp_start":[0.46782,0.04101,0.22239],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":301.0,"n_steps_budget":720.0,"object_pos_end":[0.56727,0.03316,0.16468],"object_pos_start":[0.54784,0.03309,0.15515],"object_to_goal_dist_end":0.11312,"object_to_goal_dist_start":0.09503,"object_z_max":0.16449,"peak_contact_force":187.0609,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":202.0,"raw_peak_contact_force":763.38846,"subtask_id":"approach_sub","tcp_end":[0.53374,0.03785,0.18597],"tcp_start":[0.51532,0.03592,0.17827],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.56748,0.03295,0.16505],"object_pos_start":[0.56727,0.03316,0.16468],"object_to_goal_dist_end":0.11346,"object_to_goal_dist_start":0.11312,"object_z_max":0.16548,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":87.0704,"subtask_id":"insert_sub","tcp_end":[0.53436,0.03716,0.18705],"tcp_start":[0.53417,0.03738,0.18676],"tcp_to_object_dist_end":0.03998,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.57099,0.03949,0.24774],"object_pos_start":[0.5679,0.03247,0.16576],"object_to_goal_dist_end":0.18637,"object_to_goal_dist_start":0.1141,"object_z_max":0.24766,"peak_contact_force":0.0,"phase_name":"retract_after_insert","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3.0,"raw_peak_contact_force":256.31835,"tcp_end":[0.53779,0.04639,0.26896],"tcp_start":[0.53436,0.03716,0.18705],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.46528,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_to_hole.align_speed":0.01595,"align_to_hole.align_tolerance":0.00522,"approach_arc.approach_speed":0.055,"approach_arc.arc_height":0.11889,"approach_arc.pos_tolerance":0.00328,"descend_to_entry.descend_speed":0.0309,"descend_to_entry.descend_tolerance":0.00274,"insert_into_hole.insert_force_limit":34.84493,"insert_into_hole.insert_speed":0.03709,"insert_into_hole.insertion_distance":0.08245,"retract_after_insert.retract_speed":0.08194},"optimized_scores":{"best_composite_score":-0.15268,"best_fitness_score":0.48732,"best_task_score":0.81715},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":90.0,"contact_point_centroid":[0.541,0.01428,0.0788],"force_p95":589.08953,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1086.73186,"mean_force":325.79031,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.43406,0.01226,0.13651]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.44303,0.0085,0.07918],"force_p95":530.85269,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":884.75448,"mean_force":98.30605,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.43917,0.00845,0.09285]},{"body_a":"world","body_b":"link6","contact_count":22.0,"contact_point_centroid":[0.69083,0.06183,-7e-05],"force_p95":404.42636,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":405.22398,"mean_force":292.07767,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.49307,0.03024,0.16169]},{"body_a":"peg_socket","body_b":"link7","contact_count":948.0,"contact_point_centroid":[0.54611,0.04492,0.07994],"force_p95":307.14624,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":380.11624,"mean_force":247.34288,"phase_index":2.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.48346,0.03572,0.1773]},{"body_a":"peg_socket","body_b":"link6","contact_count":797.0,"contact_point_centroid":[0.54612,0.03502,0.07993],"force_p95":318.14457,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":327.82436,"mean_force":299.93131,"phase_index":0.0,"phase_name":"approach_arc","phase_type":"approach","tcp_position_centroid":[0.45235,0.02968,0.20207]},{"body_a":"peg_socket","body_b":"link7","contact_count":336.0,"contact_point_centroid":[0.54609,0.04522,0.07991],"force_p95":278.57151,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":310.44087,"mean_force":242.56683,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.47484,0.03762,0.19851]},{"body_a":"peg_socket","body_b":"link6","contact_count":636.0,"contact_point_centroid":[0.54611,0.04507,0.07994],"force_p95":228.8182,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":250.59664,"mean_force":172.85855,"phase_index":1.0,"phase_name":"align_to_hole","phase_type":"align","tcp_position_centroid":[0.47014,0.03792,0.20929]},{"body_a":"world","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.69089,0.06116,-0.00014],"force_p95":218.80089,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":226.7866,"mean_force":164.05334,"phase_index":3.0,"phase_name":"insert_into_hole","phase_type":"insert","tcp_position_centroid":[0.49352,0.03035,0.16218]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.6909,0.06088,-0.00013],"force_p95":196.36543,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":196.87578,"mean_force":130.15665,"phase_index":4.0,"phase_name":"retract_after_insert","phase_type":"retract","tcp_position_centroid":[0.49359,0.03019,0.16228]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54614,0.0411,0.07999],"force_p95":28.77718,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":29.70485,"mean_force":16.71099,"phase_index":4.0,"phase_name":"retract_after_insert","phase_type":"retract","tcp_position_centroid":[0.49337,0.02931,0.1646]}],"total_contact_groups":10},"final_pose_error":0.01128,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.49234,0.03002,0.25096],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1086.73186,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49458,0.03868,0.18974],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11649,"object_to_goal_dist_start":0.26034,"object_z_max":0.34426,"peak_contact_force":318.20483,"phase_name":"approach_arc","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":896.0,"raw_peak_contact_force":1086.73186,"subtask_id":"approach_sub","tcp_end":[0.46562,0.03783,0.21733],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50704,0.03876,0.16945],"object_pos_start":[0.49458,0.03868,0.18974],"object_to_goal_dist_end":0.09773,"object_to_goal_dist_start":0.11649,"object_z_max":0.18975,"peak_contact_force":232.59455,"phase_name":"align_to_hole","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":972.0,"raw_peak_contact_force":310.44087,"subtask_id":"approach_sub","tcp_end":[0.47634,0.03752,0.19505],"tcp_start":[0.46562,0.03783,0.21733],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52736,0.03487,0.14135],"object_pos_start":[0.50704,0.03876,0.16945],"object_to_goal_dist_end":0.07569,"object_to_goal_dist_start":0.09773,"object_z_max":0.16949,"peak_contact_force":94.43,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":970.0,"raw_peak_contact_force":405.22398,"subtask_id":"approach_sub","tcp_end":[0.4935,0.03039,0.16218],"tcp_start":[0.47634,0.03752,0.19505],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.52737,0.03483,0.14134],"object_pos_start":[0.52736,0.03487,0.14135],"object_to_goal_dist_end":0.07567,"object_to_goal_dist_start":0.07569,"object_z_max":0.14135,"peak_contact_force":118.44392,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":226.7866,"subtask_id":"insert_sub","tcp_end":[0.49355,0.03027,0.16218],"tcp_start":[0.49354,0.03031,0.16218],"tcp_to_object_dist_end":0.03999,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":679.0,"n_steps_budget":780.0,"object_pos_end":[0.52589,0.03446,0.22965],"object_pos_start":[0.52739,0.03475,0.14133],"object_to_goal_dist_end":0.15573,"object_to_goal_dist_start":0.07563,"object_z_max":0.22955,"peak_contact_force":0.0,"phase_name":"retract_after_insert","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":7.0,"raw_peak_contact_force":196.87578,"tcp_end":[0.49234,0.03002,0.25096],"tcp_start":[0.49355,0.03027,0.16218],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```