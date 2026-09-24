## Search State

- **Seed**: 6
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1084 | 0.83 | ❌ rejected |
| 3 | approach → contact → insert → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.0820 | 0.83 | ✅ accepted |
| 2 | align → approach → contact → insert → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 5 | -0.2811 | 0.00 | ❌ rejected |
| 1 | align → approach → contact → insert → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 5 | -0.2811 | 0.00 | ❌ rejected |
| 0 | align → approach → contact → insert → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | admittance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 5 | -0.2811 | 0.00 | ✅ accepted |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.829, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=-0.108) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_sub
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.3
- id: insert_sub
  offset:
  - 0.0
  - 0.0
  - 0.005
  weight: 0.7
phases:
- id: approach_to_entry
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
    - 0.055
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
      - 0.02
      - 0.1
      default: 0.05
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
    - 0.055
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
    - 0.005
    orientation:
      mode: keep_current
  parameters:
    insert_force_limit:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 30.0
      binds_to:
      - path: guards.max_insert_force.threshold
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  guards:
  - id: max_insert_force
    when: during_phase
    predicate: force_below
    threshold: 30.0
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
- **approach_to_entry** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.055]
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - pos_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=1, strategy=repeat
- **contact_entry** (`contact`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.055]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=max_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.005]
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_force_limit: status=consumed; consumers=guards.max_insert_force.threshold (replace)
    - insertion_depth: status=consumed; consumers=target.offset.z (replace)
  - guards:
    - id=max_insert_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=30.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]
- **retract_after_insert** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=1, strategy=repeat

## Design Metrics

- **Composite score**: -0.108
- **task_score** (E): 0.829
- **fitness_score**: 0.432  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_standoff | 0.00 | 1.00 | 0.1404 |
| descend_to_entry | 1.00 | 0.67 | 0.0525 |
| contact_entry | 0.00 | 0.67 | 0.0004 |
| insert_into_hole | 0.00 | 0.00 | 0.0007 |
| retract_after_insert | 1.00 | 0.00 | 0.0884 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_standoff | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.441, 0.014, 0.175) | (0.504, -0.000, 0.340)→(0.478, 0.014, 0.160) | 0.260→0.086 | 1.00 / 1.000 | 265.338 | 1074.087 |
| descend_to_entry | descend | 1.00 / step_budget | (0.441, 0.014, 0.175)→(0.490, 0.018, 0.159) | (0.478, 0.014, 0.160)→(0.526, 0.019, 0.143) | 0.086→0.075 | 0.67 / 0.667 | 102.649 | 282.149 |
| contact_entry | contact | 0.00 / guard_failure | (0.490, 0.018, 0.159)→(0.490, 0.018, 0.159) | (0.526, 0.019, 0.143)→(0.526, 0.019, 0.143) | 0.075→0.075 | 0.67 / 0.667 | 236.852 | 236.852 |
| insert_into_hole | insert | 0.00 / step_budget | (0.496, 0.031, 0.143)→(0.496, 0.031, 0.142) | (0.535, 0.031, 0.132)→(0.535, 0.031, 0.132) | 0.070→0.070 | 0.00 / 0.000 | 0.000 | 0.000 |
| retract_after_insert | retract | 1.00 / step_budget | (0.496, 0.031, 0.142)→(0.494, 0.031, 0.230) | (0.535, 0.031, 0.132)→(0.533, 0.031, 0.219) | 0.070→0.147 | 0.00 / 0.000 | 0.000 | 425.305 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.834
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.834
- phase_score: 0.195
- phase_breakdown.approach_sub_score: 0.067
- phase_breakdown.insert_sub_score: 0.250

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.451
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.835
- **Median Q (composite search score)**: -0.093
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.365


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.09524,"average_mean_iterations":23.30159,"average_solve_count":63.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_standoff.approach_speed":0.05595,"approach_to_standoff.pos_tolerance":0.00848,"contact_entry.contact_force_threshold":3.8648,"contact_entry.contact_speed":0.01246,"descend_to_entry.descend_speed":0.02964,"descend_to_entry.descend_tolerance":0.00324,"insert_into_hole.insert_force_limit":24.45307,"insert_into_hole.insertion_depth":0.01778,"retract_after_insert.retract_speed":0.08265},"optimized_scores":{"best_composite_score":-0.09302,"best_fitness_score":0.44698,"best_task_score":0.83545},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.45221,-0.00429,0.07901],"force_p95":989.93814,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1041.38506,"mean_force":179.98875,"phase_index":0.0,"phase_name":"approach_to_standoff","phase_type":"approach","tcp_position_centroid":[0.44791,-0.00424,0.09238]},{"body_a":"peg_socket","body_b":"link7","contact_count":283.0,"contact_point_centroid":[0.56043,-0.00401,0.07966],"force_p95":346.4408,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":937.75801,"mean_force":274.52311,"phase_index":0.0,"phase_name":"approach_to_standoff","phase_type":"approach","tcp_position_centroid":[0.44886,-0.00629,0.15141]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56303,-0.01552,0.07999],"force_p95":335.53849,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":335.53849,"mean_force":335.53849,"phase_index":2.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.49357,-0.01162,0.1518]},{"body_a":"peg_socket","body_b":"link6","contact_count":41.0,"contact_point_centroid":[0.563,-0.01051,0.07984],"force_p95":293.67799,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":309.20715,"mean_force":267.58528,"phase_index":0.0,"phase_name":"approach_to_standoff","phase_type":"approach","tcp_position_centroid":[0.44872,-0.00849,0.16809]},{"body_a":"peg_socket","body_b":"link7","contact_count":849.0,"contact_point_centroid":[0.56302,-0.0098,0.07993],"force_p95":115.5435,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":283.70015,"mean_force":103.42358,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.47184,-0.01017,0.16195]},{"body_a":"peg_socket","body_b":"link6","contact_count":64.0,"contact_point_centroid":[0.56303,-0.01079,0.07993],"force_p95":146.49035,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":187.33258,"mean_force":105.79283,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.44978,-0.00884,0.16884]}],"total_contact_groups":6},"final_pose_error":0.01166,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49355,-0.01162,0.1517],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1041.38506,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.48575,-0.00894,0.15483],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0767,"object_to_goal_dist_start":0.26034,"object_z_max":0.34444,"peak_contact_force":259.07833,"phase_name":"approach_to_standoff","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":335.0,"raw_peak_contact_force":1041.38506,"subtask_id":"approach_sub","tcp_end":[0.44814,-0.00875,0.16847],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.5311,-0.01179,0.13799],"object_pos_start":[0.48575,-0.00894,0.15483],"object_to_goal_dist_end":0.06685,"object_to_goal_dist_start":0.0767,"object_z_max":0.15535,"peak_contact_force":87.20577,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":913.0,"raw_peak_contact_force":283.70015,"subtask_id":"approach_sub","tcp_end":[0.49357,-0.01162,0.1518],"tcp_start":[0.44814,-0.00875,0.16847],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53109,-0.01179,0.13789],"object_pos_start":[0.5311,-0.01179,0.13799],"object_to_goal_dist_end":0.06677,"object_to_goal_dist_start":0.06685,"object_z_max":0.13799,"peak_contact_force":335.53849,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":335.53849,"subtask_id":"insert_sub","tcp_end":[0.49355,-0.01162,0.1517],"tcp_start":[0.49357,-0.01162,0.1518],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":42.0,"average_failure_rate":0.26923,"average_mean_iterations":57.13462,"average_solve_count":156.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_standoff.approach_speed":0.10495,"approach_to_standoff.pos_tolerance":0.01,"contact_entry.contact_force_threshold":3.43722,"contact_entry.contact_speed":0.01013,"descend_to_entry.descend_speed":0.02586,"descend_to_entry.descend_tolerance":0.0063,"insert_into_hole.insert_force_limit":24.56431,"insert_into_hole.insertion_depth":0.00929,"retract_after_insert.retract_speed":0.08452},"optimized_scores":{"best_composite_score":-0.08903,"best_fitness_score":0.45097,"best_task_score":0.83436},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":152.0,"contact_point_centroid":[0.56285,0.01625,0.07933],"force_p95":447.1835,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1100.76216,"mean_force":280.86694,"phase_index":0.0,"phase_name":"approach_to_standoff","phase_type":"approach","tcp_position_centroid":[0.44977,0.01267,0.13719]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.45257,0.00877,0.07877],"force_p95":514.72284,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":935.85971,"mean_force":93.58597,"phase_index":0.0,"phase_name":"approach_to_standoff","phase_type":"approach","tcp_position_centroid":[0.44761,0.00875,0.09171]},{"body_a":"peg_socket","body_b":"link7","contact_count":25.0,"contact_point_centroid":[0.53912,0.00162,0.079],"force_p95":587.35331,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":626.26641,"mean_force":322.73793,"phase_index":0.0,"phase_name":"approach_to_standoff","phase_type":"approach","tcp_position_centroid":[0.44555,0.00918,0.10164]},{"body_a":"peg_socket","body_b":"link7","contact_count":35.0,"contact_point_centroid":[0.56971,0.02867,0.07988],"force_p95":159.99871,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":425.30483,"mean_force":94.6613,"phase_index":4.0,"phase_name":"retract_after_insert","phase_type":"retract","tcp_position_centroid":[0.49526,0.03068,0.14084]},{"body_a":"peg_socket","body_b":"link6","contact_count":197.0,"contact_point_centroid":[0.56997,0.02045,0.07985],"force_p95":282.95874,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":298.97329,"mean_force":254.27133,"phase_index":0.0,"phase_name":"approach_to_standoff","phase_type":"approach","tcp_position_centroid":[0.4433,0.02039,0.15909]},{"body_a":"peg_socket","body_b":"link7","contact_count":355.0,"contact_point_centroid":[0.57,0.0256,0.07996],"force_p95":123.21641,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":241.86382,"mean_force":88.23158,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.46961,0.02798,0.15245]},{"body_a":"peg_socket","body_b":"link6","contact_count":278.0,"contact_point_centroid":[0.57,0.02535,0.07996],"force_p95":141.39349,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":212.47376,"mean_force":117.32587,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.44296,0.02541,0.16102]}],"total_contact_groups":7},"final_pose_error":0.01175,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.49434,0.03053,0.23029],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1100.76216,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.4736,0.02504,0.14928],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07825,"object_to_goal_dist_start":0.26034,"object_z_max":0.34446,"peak_contact_force":257.15482,"phase_name":"approach_to_standoff","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":384.0,"raw_peak_contact_force":1100.76216,"subtask_id":"approach_sub","tcp_end":[0.43482,0.02454,0.15908],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":774.0,"n_steps_budget":1000.0,"object_pos_end":[0.5345,0.03098,0.13323],"object_pos_start":[0.4736,0.02504,0.14928],"object_to_goal_dist_end":0.07059,"object_to_goal_dist_start":0.07825,"object_z_max":0.15153,"peak_contact_force":0.0,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":633.0,"raw_peak_contact_force":241.86382,"subtask_id":"approach_sub","tcp_end":[0.49583,0.0305,0.14345],"tcp_start":[0.43482,0.02454,0.15908],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":11.0,"n_steps_budget":900.0,"object_pos_end":[0.53465,0.03111,0.13227],"object_pos_start":[0.5345,0.03098,0.13323],"object_to_goal_dist_end":0.07001,"object_to_goal_dist_start":0.07059,"object_z_max":0.13323,"peak_contact_force":0.0,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_sub","tcp_end":[0.496,0.03063,0.14257],"tcp_start":[0.49583,0.0305,0.14345],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":4.0,"n_steps_budget":600.0,"object_pos_end":[0.5346,0.03121,0.13157],"object_pos_start":[0.53465,0.03111,0.13227],"object_to_goal_dist_end":0.0695,"object_to_goal_dist_start":0.07001,"object_z_max":0.13227,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insert_sub","tcp_end":[0.49597,0.03071,0.14193],"tcp_start":[0.496,0.03063,0.14257],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":663.0,"n_steps_budget":750.0,"object_pos_end":[0.53282,0.03102,0.21938],"object_pos_start":[0.5346,0.03121,0.13157],"object_to_goal_dist_end":0.14652,"object_to_goal_dist_start":0.0695,"object_z_max":0.21928,"peak_contact_force":0.0,"phase_name":"retract_after_insert","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":35.0,"raw_peak_contact_force":425.30483,"tcp_end":[0.49434,0.03053,0.23029],"tcp_start":[0.49597,0.03071,0.14193],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.59016,"average_solve_count":61.0,"average_success_count":61.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_standoff.approach_speed":0.10354,"approach_to_standoff.pos_tolerance":0.00338,"contact_entry.contact_force_threshold":7.97667,"contact_entry.contact_speed":0.01027,"descend_to_entry.descend_speed":0.02999,"descend_to_entry.descend_tolerance":0.00736,"insert_into_hole.insert_force_limit":33.75066,"insert_into_hole.insertion_depth":0.01283,"retract_after_insert.retract_speed":0.05832},"optimized_scores":{"best_composite_score":-0.143,"best_fitness_score":0.397,"best_task_score":0.8165},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link7","contact_count":112.0,"contact_point_centroid":[0.54169,0.01212,0.07899],"force_p95":566.68368,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1080.1149,"mean_force":314.58691,"phase_index":0.0,"phase_name":"approach_to_standoff","phase_type":"approach","tcp_position_centroid":[0.43349,0.00903,0.14093]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54608,0.0383,0.0799],"force_p95":375.01661,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":375.01661,"mean_force":375.01661,"phase_index":2.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.48138,0.03598,0.18229]},{"body_a":"peg_socket","body_b":"link6","contact_count":316.0,"contact_point_centroid":[0.54608,0.02011,0.07985],"force_p95":308.36891,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":329.44998,"mean_force":281.56868,"phase_index":0.0,"phase_name":"approach_to_standoff","phase_type":"approach","tcp_position_centroid":[0.4378,0.01936,0.18592]},{"body_a":"peg_socket","body_b":"link7","contact_count":502.0,"contact_point_centroid":[0.54611,0.03745,0.07993],"force_p95":200.11053,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":320.8821,"mean_force":141.04527,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.47239,0.0328,0.19153]},{"body_a":"peg_socket","body_b":"link6","contact_count":444.0,"contact_point_centroid":[0.54613,0.02894,0.07996],"force_p95":136.30392,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":188.6113,"mean_force":123.68919,"phase_index":1.0,"phase_name":"descend_to_entry","phase_type":"descend","tcp_position_centroid":[0.45305,0.02788,0.19639]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.4416,0.0058,0.07901],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_standoff","phase_type":"approach","tcp_position_centroid":[0.43775,0.00575,0.09251]}],"total_contact_groups":6},"final_pose_error":0.03762,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48137,0.03599,0.18219],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1080.1149,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.47378,0.02611,0.17685],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10368,"object_to_goal_dist_start":0.26034,"object_z_max":0.34425,"peak_contact_force":279.78182,"phase_name":"approach_to_standoff","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":437.0,"raw_peak_contact_force":1080.1149,"subtask_id":"approach_sub","tcp_end":[0.43986,0.02506,0.19802],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51351,0.03695,0.15848],"object_pos_start":[0.47378,0.02611,0.17685],"object_to_goal_dist_end":0.08779,"object_to_goal_dist_start":0.10368,"object_z_max":0.17685,"peak_contact_force":220.74186,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":946.0,"raw_peak_contact_force":320.8821,"subtask_id":"approach_sub","tcp_end":[0.48138,0.03598,0.18229],"tcp_start":[0.43986,0.02506,0.19802],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51352,0.03696,0.15841],"object_pos_start":[0.51351,0.03695,0.15848],"object_to_goal_dist_end":0.08773,"object_to_goal_dist_start":0.08779,"object_z_max":0.15848,"peak_contact_force":375.01661,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":375.01661,"subtask_id":"insert_sub","tcp_end":[0.48137,0.03599,0.18219],"tcp_start":[0.48138,0.03598,0.18229],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```