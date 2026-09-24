## Search State

- **Seed**: 6
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → align → descend | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | -0.0535 | 0.84 | ❌ rejected |
| 11 | approach → align → descend | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 9 | -0.1188 | 0.83 | ❌ rejected |
| 10 | approach → descend | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 5 | 1.0944 | 0.84 | ❌ rejected |
| 9 | approach → descend | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 5 | 0.5790 | 0.83 | ❌ rejected |
| 8 | approach → descend | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 5 | 0.5848 | 0.83 | ❌ rejected |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.853, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=-0.054) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.12
  weight: 0.2
- id: insertion
  anchor: fixture
  metric: goal_progress
  weight: 0.8
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.12
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.08
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: channel_axis
      mode: add_to_offset
      sign: negative
  parameters:
    descent_distance:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descent_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    force_threshold:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 30.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.1, mode=add_to_offset, sign=negative}
  - parameter_bindings:
    - descent_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descent_speed: status=consumed; consumers=generator.speed (replace)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: -0.054
- **task_score** (E): 0.842
- **fitness_score**: 0.376  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.430

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_socket | 0.33 | 1.00 | 0.1480 |
| align_socket_entry | 0.00 | 1.00 | 0.0212 |
| descend_insert | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_socket | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.461, 0.003, 0.158) | (0.504, -0.000, 0.340)→(0.499, 0.003, 0.146) | 0.260→0.067 | 1.00 / 1.667 | 382.445 | 1871.576 |
| align_socket_entry | align | 0.00 / step_budget | (0.461, 0.003, 0.158)→(0.463, 0.002, 0.161) | (0.499, 0.003, 0.146)→(0.500, 0.004, 0.147) | 0.067→0.070 | 1.00 / 1.333 | 258.067 | 558.953 |
| descend_insert | descend | 0.00 / guard_failure | (0.463, 0.002, 0.161)→(0.463, 0.002, 0.161) | (0.500, 0.004, 0.147)→(0.500, 0.004, 0.147) | 0.070→0.070 | 1.00 / 1.333 | 148.600 | 187.358 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.837
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.837
- phase_score: 0.089
- phase_breakdown.approach_score: 0.444
- phase_breakdown.insertion_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.388
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.845
- **Median Q (composite search score)**: -0.059
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.311


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.76543,"average_solve_count":81.0,"average_success_count":81.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_socket_entry.align_speed":0.0151,"align_socket_entry.align_x_offset":-0.00947,"align_socket_entry.align_y_offset":-0.01542,"approach_to_socket.approach_height":0.11767,"approach_to_socket.approach_speed":0.07533,"descend_insert.descent_distance":0.09233,"descend_insert.descent_speed":0.02525,"descend_insert.force_threshold":23.64685},"optimized_scores":{"best_composite_score":-0.05894,"best_fitness_score":0.37106,"best_task_score":0.84548},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.45596,-0.0013,0.07866],"force_p95":1020.25899,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1068.99913,"mean_force":246.01052,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45148,-0.00125,0.09162]},{"body_a":"peg_socket","body_b":"link6","contact_count":366.0,"contact_point_centroid":[0.56287,-0.00522,0.07923],"force_p95":700.72739,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1037.10402,"mean_force":380.97142,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.45402,-0.00455,0.17171]},{"body_a":"peg_socket","body_b":"link7","contact_count":898.0,"contact_point_centroid":[0.56196,0.00086,0.07987],"force_p95":346.76695,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":946.92426,"mean_force":260.2117,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.4535,-0.00328,0.16418]},{"body_a":"peg_socket","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.56299,-0.00711,0.0797],"force_p95":352.5174,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":751.77263,"mean_force":256.14386,"phase_index":1.0,"phase_name":"align_socket_entry","phase_type":"align","tcp_position_centroid":[0.45047,-0.01291,0.16673]},{"body_a":"peg_socket","body_b":"link7","contact_count":881.0,"contact_point_centroid":[0.56225,-0.00924,0.07997],"force_p95":236.85014,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":612.32196,"mean_force":127.94774,"phase_index":1.0,"phase_name":"align_socket_entry","phase_type":"align","tcp_position_centroid":[0.45055,-0.01181,0.16679]},{"body_a":"peg_socket","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.56304,-0.01144,0.07999],"force_p95":122.2993,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.94296,"mean_force":91.399,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.45103,-0.02279,0.16761]},{"body_a":"peg_socket","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.56229,-0.01384,0.07999],"force_p95":65.81764,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.59663,"mean_force":49.80677,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.45103,-0.02278,0.16759]}],"total_contact_groups":7},"final_pose_error":0.09239,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.45106,-0.02272,0.16757],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":1068.99913,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49733,-0.0056,0.16219],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.08243,"object_to_goal_dist_start":0.26034,"object_z_max":0.34444,"peak_contact_force":525.10571,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1276.0,"raw_peak_contact_force":1068.99913,"subtask_id":"approach","tcp_end":[0.46174,-0.00602,0.18045],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4884,-0.01912,0.1539],"object_pos_start":[0.49733,-0.0056,0.16219],"object_to_goal_dist_end":0.07721,"object_to_goal_dist_start":0.08243,"object_z_max":0.16317,"peak_contact_force":263.20818,"phase_name":"align_socket_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1881.0,"raw_peak_contact_force":751.77263,"subtask_id":"approach","tcp_end":[0.45101,-0.02283,0.16763],"tcp_start":[0.46174,-0.00602,0.18045],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.48842,-0.01908,0.15388],"object_pos_start":[0.4884,-0.01912,0.1539],"object_to_goal_dist_end":0.07718,"object_to_goal_dist_start":0.07721,"object_z_max":0.1539,"peak_contact_force":80.50632,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":126.94296,"subtask_id":"insertion","tcp_end":[0.45106,-0.02272,0.16757],"tcp_start":[0.45104,-0.02276,0.16758],"tcp_to_object_dist_end":0.03996,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.76829,"average_solve_count":82.0,"average_success_count":82.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_socket_entry.align_speed":0.01558,"align_socket_entry.align_x_offset":-0.00124,"align_socket_entry.align_y_offset":0.00142,"approach_to_socket.approach_height":0.10163,"approach_to_socket.approach_speed":0.05573,"descend_insert.descent_distance":0.05935,"descend_insert.descent_speed":0.02429,"descend_insert.force_threshold":25.11982},"optimized_scores":{"best_composite_score":-0.05978,"best_fitness_score":0.37022,"best_task_score":0.84236},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":11.0,"contact_point_centroid":[0.45371,0.00207,0.07853],"force_p95":1010.49683,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1057.27067,"mean_force":183.7267,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.44923,0.00205,0.09137]},{"body_a":"peg_socket","body_b":"link7","contact_count":900.0,"contact_point_centroid":[0.5682,0.00981,0.07983],"force_p95":506.47814,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":956.71237,"mean_force":255.68195,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.44908,0.00603,0.15028]},{"body_a":"peg_socket","body_b":"link6","contact_count":598.0,"contact_point_centroid":[0.56986,0.00524,0.07936],"force_p95":574.61236,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":750.35731,"mean_force":331.41422,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.44724,0.00723,0.1525]},{"body_a":"peg_socket","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.53927,-0.00126,0.07916],"force_p95":537.06778,"geom_a":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":588.83457,"mean_force":324.03413,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.44697,0.00211,0.10088]},{"body_a":"peg_socket","body_b":"link6","contact_count":1000.0,"contact_point_centroid":[0.56993,0.01044,0.07959],"force_p95":424.77757,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":574.89549,"mean_force":260.88157,"phase_index":1.0,"phase_name":"align_socket_entry","phase_type":"align","tcp_position_centroid":[0.45186,0.01629,0.15952]},{"body_a":"peg_socket","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.56923,0.01494,0.07995],"force_p95":344.54316,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":507.2405,"mean_force":174.13111,"phase_index":1.0,"phase_name":"align_socket_entry","phase_type":"align","tcp_position_centroid":[0.45186,0.01629,0.15952]},{"body_a":"peg_socket","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.56938,0.01759,0.07998],"force_p95":150.62309,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":155.84163,"mean_force":115.16721,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.45832,0.02644,0.16796]},{"body_a":"peg_socket","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.56999,0.01416,0.07999],"force_p95":111.23472,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":111.70971,"mean_force":106.95981,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.45831,0.02646,0.16797]}],"total_contact_groups":8},"final_pose_error":0.05938,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.45836,0.02636,0.16795],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1057.27067,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49255,0.00911,0.15128],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.07225,"object_to_goal_dist_start":0.26034,"object_z_max":0.34444,"peak_contact_force":336.5985,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1532.0,"raw_peak_contact_force":1057.27067,"subtask_id":"approach","tcp_end":[0.45456,0.00947,0.16378],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49568,0.02307,0.15416],"object_pos_start":[0.49255,0.00911,0.15128],"object_to_goal_dist_end":0.07778,"object_to_goal_dist_start":0.07225,"object_z_max":0.15413,"peak_contact_force":191.67972,"phase_name":"align_socket_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2000.0,"raw_peak_contact_force":574.89549,"subtask_id":"approach","tcp_end":[0.4583,0.02647,0.16798],"tcp_start":[0.45456,0.00947,0.16378],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.4957,0.02303,0.15414],"object_pos_start":[0.49568,0.02307,0.15416],"object_to_goal_dist_end":0.07775,"object_to_goal_dist_start":0.07778,"object_z_max":0.15416,"peak_contact_force":86.00378,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":5.0,"raw_peak_contact_force":155.84163,"subtask_id":"insertion","tcp_end":[0.45836,0.02636,0.16795],"tcp_start":[0.45834,0.0264,0.16795],"tcp_to_object_dist_end":0.03995,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.72308,"average_solve_count":65.0,"average_success_count":65.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_socket_entry.align_speed":0.03686,"align_socket_entry.align_x_offset":-0.00684,"align_socket_entry.align_y_offset":-0.00463,"approach_to_socket.approach_height":0.07756,"approach_to_socket.approach_speed":0.05169,"descend_insert.descent_distance":0.09703,"descend_insert.descent_speed":0.0238,"descend_insert.force_threshold":28.85301},"optimized_scores":{"best_composite_score":-0.04185,"best_fitness_score":0.38815,"best_task_score":0.83681},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":13.0,"contact_point_centroid":[0.45034,0.00339,0.0785],"force_p95":2010.98456,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3488.45818,"mean_force":347.26618,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.44635,0.00206,0.09101]},{"body_a":"attachment","body_b":"peg_socket","contact_count":12.0,"contact_point_centroid":[0.45677,0.00205,0.07892],"force_p95":1825.76484,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2771.52606,"mean_force":398.65442,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.4472,0.00206,0.09067]},{"body_a":"peg_socket","body_b":"link7","contact_count":909.0,"contact_point_centroid":[0.546,0.00228,0.07987],"force_p95":290.00489,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1141.77188,"mean_force":284.0574,"phase_index":0.0,"phase_name":"approach_to_socket","phase_type":"approach","tcp_position_centroid":[0.4659,0.00356,0.12964]},{"body_a":"peg_socket","body_b":"link7","contact_count":633.0,"contact_point_centroid":[0.54601,0.01471,0.07994],"force_p95":333.8522,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":350.19068,"mean_force":301.40462,"phase_index":1.0,"phase_name":"align_socket_entry","phase_type":"align","tcp_position_centroid":[0.47299,0.00431,0.13965]},{"body_a":"peg_socket","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54613,0.01919,0.07999],"force_p95":279.28913,"geom_a":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":279.28913,"mean_force":279.28913,"phase_index":2.0,"phase_name":"descend_insert","phase_type":"descend","tcp_position_centroid":[0.48002,0.00286,0.14741]}],"total_contact_groups":5},"final_pose_error":0.09713,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48005,0.00297,0.14731],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":3488.45818,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.00602,0.1246],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.0454,"object_to_goal_dist_start":0.26034,"object_z_max":0.34439,"peak_contact_force":285.63049,"phase_name":"approach_to_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":934.0,"raw_peak_contact_force":3488.45818,"subtask_id":"approach","tcp_end":[0.46642,0.00523,0.13047],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":633.0,"n_steps_budget":720.0,"object_pos_end":[0.5171,0.00776,0.13323],"object_pos_start":[0.50598,0.00602,0.1246],"object_to_goal_dist_end":0.05644,"object_to_goal_dist_start":0.0454,"object_z_max":0.13322,"peak_contact_force":319.31197,"phase_name":"align_socket_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":633.0,"raw_peak_contact_force":350.19068,"subtask_id":"approach","tcp_end":[0.48002,0.00286,0.14741],"tcp_start":[0.46642,0.00523,0.13047],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51714,0.0078,0.13319],"object_pos_start":[0.5171,0.00776,0.13323],"object_to_goal_dist_end":0.05643,"object_to_goal_dist_start":0.05644,"object_z_max":0.13323,"peak_contact_force":279.28913,"phase_name":"descend_insert","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1.0,"raw_peak_contact_force":279.28913,"subtask_id":"insertion","tcp_end":[0.48005,0.00297,0.14731],"tcp_start":[0.48006,0.00294,0.14735],"tcp_to_object_dist_end":0.03998,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```