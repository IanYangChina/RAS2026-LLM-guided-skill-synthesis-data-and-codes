## Search State

- **Seed**: 6
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
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

## Current Skill (Q=-0.082) — your mutation base

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

- **Composite score**: -0.082
- **task_score** (E): 0.829
- **fitness_score**: 0.378  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_entry | 0.00 | 1.00 | 0.1455 |
| contact_entry | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_entry | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.450, 0.015, 0.166) | (0.504, -0.000, 0.340)→(0.486, 0.015, 0.152) | 0.260→0.077 | 1.00 / 1.667 | 290.656 | 2160.498 |
| contact_entry | contact | 0.00 / guard_failure | (0.450, 0.015, 0.166)→(0.450, 0.015, 0.166) | (0.486, 0.015, 0.152)→(0.486, 0.015, 0.152) | 0.077→0.077 | 1.00 / 1.667 | 130.160 | 130.160 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.828
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.828
- phase_score: 0.091
- phase_breakdown.approach_sub_score: 0.305
- phase_breakdown.insert_sub_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.386
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.831
- **Median Q (composite search score)**: -0.078
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.363


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.87179,"average_solve_count":39.0,"average_success_count":39.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_entry.approach_speed":0.02515,"approach_to_entry.arc_height":0.02051,"approach_to_entry.pos_tolerance":0.00498,"contact_entry.contact_force_threshold":14.28921,"contact_entry.contact_speed":0.03459,"insert_into_hole.insert_force_limit":34.39212,"insert_into_hole.insertion_depth":0.027,"retract_after_insert.retract_speed":0.09079},"optimized_scores":{"best_composite_score":-0.07832,"best_fitness_score":0.38168,"best_task_score":0.82916},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":700.0,"contact_point_centroid":[0.56297,0.0037,0.07933],"force_p95":436.97519,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1393.13896,"mean_force":269.39732,"phase_index":0.0,"phase_name":"approach_to_entry","phase_type":"approach","tcp_position_centroid":[0.4454,0.00552,0.16021]},{"body_a":"peg_socket","body_b":"link7","contact_count":900.0,"contact_point_centroid":[0.56133,0.00912,0.07984],"force_p95":393.76079,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1306.38459,"mean_force":216.49914,"phase_index":0.0,"phase_name":"approach_to_entry","phase_type":"approach","tcp_position_centroid":[0.44535,0.00505,0.15721]},{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.44729,0.00226,0.07882],"force_p95":463.32873,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":926.65746,"mean_force":84.24159,"phase_index":0.0,"phase_name":"approach_to_entry","phase_type":"approach","tcp_position_centroid":[0.44327,0.00231,0.09208]},{"body_a":"peg_socket","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.53264,0.0176,0.07958],"force_p95":428.60636,"geom_a":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":442.94982,"mean_force":260.72797,"phase_index":0.0,"phase_name":"approach_to_entry","phase_type":"approach","tcp_position_centroid":[0.44083,0.00227,0.09774]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56203,0.01055,0.07993],"force_p95":196.20466,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":196.20466,"mean_force":196.20466,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.43791,0.00757,0.14873]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.5629,0.00475,0.0794],"force_p95":131.67885,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.67885,"mean_force":131.67885,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.43791,0.00757,0.14873]}],"total_contact_groups":6},"final_pose_error":0.06954,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.43792,0.00758,0.14872],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1393.13896,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47718,0.00715,0.14109],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0656,"object_to_goal_dist_start":0.26034,"object_z_max":0.34436,"peak_contact_force":320.83284,"phase_name":"approach_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1626.0,"raw_peak_contact_force":1393.13896,"subtask_id":"approach_sub","tcp_end":[0.43791,0.00757,0.14873],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47718,0.00715,0.14108],"object_pos_start":[0.47718,0.00715,0.14109],"object_to_goal_dist_end":0.06559,"object_to_goal_dist_start":0.0656,"object_z_max":0.14109,"peak_contact_force":196.20466,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":196.20466,"subtask_id":"approach_sub","tcp_end":[0.43792,0.00758,0.14872],"tcp_start":[0.43791,0.00757,0.14873],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.87179,"average_solve_count":39.0,"average_success_count":39.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_entry.approach_speed":0.01902,"approach_to_entry.arc_height":0.02004,"approach_to_entry.pos_tolerance":0.00608,"contact_entry.contact_force_threshold":13.65538,"contact_entry.contact_speed":0.00801,"insert_into_hole.insert_force_limit":25.56697,"insert_into_hole.insertion_depth":0.04075,"retract_after_insert.retract_speed":0.06559},"optimized_scores":{"best_composite_score":-0.07403,"best_fitness_score":0.38597,"best_task_score":0.82777},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg_socket","body_b":"link6","contact_count":868.0,"contact_point_centroid":[0.56992,0.00627,0.07948],"force_p95":559.78518,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2999.42335,"mean_force":294.47734,"phase_index":0.0,"phase_name":"approach_to_entry","phase_type":"approach","tcp_position_centroid":[0.44169,0.00684,0.14186]},{"body_a":"peg_socket","body_b":"link7","contact_count":902.0,"contact_point_centroid":[0.56817,0.01157,0.07985],"force_p95":537.28784,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2980.58417,"mean_force":273.86727,"phase_index":0.0,"phase_name":"approach_to_entry","phase_type":"approach","tcp_position_centroid":[0.44169,0.00675,0.14059]},{"body_a":"peg_socket","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.53822,0.00134,0.07861],"force_p95":1010.17818,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1146.86278,"mean_force":345.71241,"phase_index":0.0,"phase_name":"approach_to_entry","phase_type":"approach","tcp_position_centroid":[0.44049,0.00439,0.10968]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.45118,0.00378,0.07916],"force_p95":598.88369,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":921.35952,"mean_force":115.16994,"phase_index":0.0,"phase_name":"approach_to_entry","phase_type":"approach","tcp_position_centroid":[0.44433,0.00377,0.09195]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.56894,0.01264,0.07995],"force_p95":137.78731,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.78731,"mean_force":137.78731,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.44131,0.00647,0.14178]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.56996,0.0094,0.07999],"force_p95":93.17457,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":93.17457,"mean_force":93.17457,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.44131,0.00647,0.14178]}],"total_contact_groups":6},"final_pose_error":0.07351,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.44133,0.00646,0.14176],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":2999.42335,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48092,0.00765,0.13638],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.06001,"object_to_goal_dist_start":0.26034,"object_z_max":0.34436,"peak_contact_force":202.80133,"phase_name":"approach_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1812.0,"raw_peak_contact_force":2999.42335,"subtask_id":"approach_sub","tcp_end":[0.44131,0.00647,0.14178],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.48095,0.00764,0.13636],"object_pos_start":[0.48092,0.00765,0.13638],"object_to_goal_dist_end":0.05998,"object_to_goal_dist_start":0.06001,"object_z_max":0.13638,"peak_contact_force":137.78731,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":137.78731,"subtask_id":"approach_sub","tcp_end":[0.44133,0.00646,0.14176],"tcp_start":[0.44131,0.00647,0.14178],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.86486,"average_solve_count":37.0,"average_success_count":37.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_entry.approach_speed":0.0819,"approach_to_entry.arc_height":0.02073,"approach_to_entry.pos_tolerance":0.00635,"contact_entry.contact_force_threshold":10.68508,"contact_entry.contact_speed":0.02278,"insert_into_hole.insert_force_limit":31.83337,"insert_into_hole.insertion_depth":0.02343,"retract_after_insert.retract_speed":0.03174},"optimized_scores":{"best_composite_score":-0.09362,"best_fitness_score":0.36638,"best_task_score":0.83058},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.44929,0.00799,0.07874],"force_p95":1481.81865,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2088.93295,"mean_force":269.42157,"phase_index":0.0,"phase_name":"approach_to_entry","phase_type":"approach","tcp_position_centroid":[0.44524,0.0073,0.09173]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.45667,0.00724,0.0793],"force_p95":1391.01961,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1688.3401,"mean_force":292.59766,"phase_index":0.0,"phase_name":"approach_to_entry","phase_type":"approach","tcp_position_centroid":[0.44693,0.00725,0.09134]},{"body_a":"peg_socket","body_b":"link6","contact_count":689.0,"contact_point_centroid":[0.54609,0.03072,0.07969],"force_p95":459.51452,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1108.57262,"mean_force":340.37615,"phase_index":0.0,"phase_name":"approach_to_entry","phase_type":"approach","tcp_position_centroid":[0.46516,0.02498,0.19864]},{"body_a":"peg_socket","body_b":"link7","contact_count":523.0,"contact_point_centroid":[0.54512,0.02346,0.07974],"force_p95":563.74351,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":948.5071,"mean_force":253.80965,"phase_index":0.0,"phase_name":"approach_to_entry","phase_type":"approach","tcp_position_centroid":[0.45303,0.01874,0.1792]},{"body_a":"peg_socket","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.54612,0.03826,0.07996],"force_p95":56.48884,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.48884,"mean_force":56.48884,"phase_index":1.0,"phase_name":"contact_entry","phase_type":"contact","tcp_position_centroid":[0.47034,0.03031,0.20649]}],"total_contact_groups":5},"final_pose_error":0.07373,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.47035,0.03029,0.20649],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":2088.93295,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50012,0.03057,0.17978],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10436,"object_to_goal_dist_start":0.26034,"object_z_max":0.34435,"peak_contact_force":348.33301,"phase_name":"approach_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1232.0,"raw_peak_contact_force":2088.93295,"subtask_id":"approach_sub","tcp_end":[0.47034,0.03031,0.20649],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50012,0.03054,0.17978],"object_pos_start":[0.50012,0.03057,0.17978],"object_to_goal_dist_end":0.10435,"object_to_goal_dist_start":0.10436,"object_z_max":0.17978,"peak_contact_force":56.48884,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1.0,"raw_peak_contact_force":56.48884,"subtask_id":"approach_sub","tcp_end":[0.47035,0.03029,0.20649],"tcp_start":[0.47034,0.03031,0.20649],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```