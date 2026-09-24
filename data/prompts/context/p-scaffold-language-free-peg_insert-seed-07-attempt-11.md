## Search State

- **Seed**: 7
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1732 | 0.85 | ❌ rejected |
| 10 | approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.5442 | 0.85 | ✅ accepted |
| 9 | approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | 0.3626 | 0.85 | ❌ rejected |
| 8 | approach → approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.1988 | 0.84 | ❌ rejected |
| 7 | approach → contact → insert → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.5439 | 0.85 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `5286851552083a7c8a4164a2656d1a38f2da41529a3a0236ff73d4d9a02dc20c`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5100076373283734, 0.031777104077566044, 0.08]
- Frozen socket pose: [0.5100076373283734, 0.031777104077566044, 0.025] (static fixture for this episode)
- Goal object position: (0.5100076373283734, 0.031777104077566044, 0.025)
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
  frozen_task_target: [0.51, 0.0318, 0.08]
  frozen_socket_position: [0.51, 0.0318, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5100076373283734, 0.031777104077566044, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5100076373283734, 0.031777104077566044, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 5286851552083a7c8a4164a2656d1a38f2da41529a3a0236ff73d4d9a02dc20c

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.848, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.5100076373283734, 0.031777104077566044, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5100076373283734, 0.031777104077566044, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.173) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_entry
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.3
- id: reach_inserted
  anchor: fixture
  weight: 0.7
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
      align_with: channel_axis
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
  guards:
  - id: approach_pose_ok
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.01
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.002
    - 0.002
    - 0.0
  subtask_id: reach_entry
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.015
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 10.0
      default: 7.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_detected_guard
    when: after_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: reach_entry
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: fixture
    entity: peg_socket
    offset:
    - 0.0
    - 0.0
    - 0.08
    offset_along_axis:
      distance: 0.08
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.02
  parameters:
    insert_speed:
      type: scalar
      range:
      - 0.001
      - 0.01
      default: 0.003
      binds_to:
      - path: generator.speed
        mode: replace
    insertion_depth:
      type: scalar
      range:
      - 0.06
      - 0.1
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: reach_inserted
- id: retract_1
  type: retract
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
      mode: keep_current
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_pose_ok, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.01
  - retries: max_attempts=2, strategy=offset_target, offset=[0.002, 0.002, 0.0]
- **contact_1** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.015], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_detected_guard, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]
- **insert_1** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.08], offset_along_axis={axis=channel_axis, distance=0.08, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.02
  - parameter_bindings:
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.12], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.173
- **task_score** (E): 0.845
- **fitness_score**: 0.483  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.1506 |
| contact_1 | 0.00 | 0.00 | 0.0011 |
| insert_1 | 1.00 | 1.00 | 0.0007 |
| retract_1 | 1.00 | 0.00 | 0.0849 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.016, 0.154) | (0.504, -0.000, 0.340)→(0.505, 0.016, 0.194) | 0.260→0.118 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_1 | contact | 0.00 / step_budget | (0.507, 0.020, 0.076)→(0.507, 0.021, 0.074) | (0.505, 0.016, 0.194)→(0.505, 0.018, 0.123) | 0.118→0.055 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 1.00 / step_budget | (0.524, 0.020, 0.050)→(0.524, 0.020, 0.051) | (0.509, 0.021, 0.114)→(0.515, 0.019, 0.090) | 0.051→0.041 | 1.00 / 2.000 | 363.780 | 545.878 |
| retract_1 | retract | 1.00 / step_budget | (0.524, 0.020, 0.051)→(0.506, 0.018, 0.134) | (0.521, 0.020, 0.091)→(0.505, 0.018, 0.174) | 0.044→0.100 | 0.00 / 0.000 | 0.000 | 96.598 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.866
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.866
- phase_score: 0.241
- phase_breakdown.reach_entry_score: 0.537
- phase_breakdown.reach_inserted_score: 0.114

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.491
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.866
- **Median Q (composite search score)**: 0.178
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.326


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `67da8d8e2fdb6e51304324325b018cdd61d8458bea09169be4b0df58a766886a`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8885199a676d406ac1afd37384d9e8e130cfc792c4c5c21c0d1c4611010dfdf0`; realized-scene SHA-256: `5286851552083a7c8a4164a2656d1a38f2da41529a3a0236ff73d4d9a02dc20c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51001,0.03178,0.025]},{"name":"target","value":[0.51001,0.03178,0.025]},{"name":"socket","value":[0.51001,0.03178,0.025]},{"name":"goal","value":[0.51001,0.03178,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.03178,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.14423,"average_solve_count":416.0,"average_success_count":416.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05811,"contact_1.contact_force_threshold":7.8802,"contact_1.contact_speed":0.01099,"insert_1.insert_speed":0.00204,"retract_1.retract_speed":0.1224},"optimized_scores":{"best_composite_score":0.17751,"best_fitness_score":0.48751,"best_task_score":0.85611},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1220.0,"contact_point_centroid":[0.5215,0.0365,0.04994],"force_p95":424.77021,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":543.37732,"mean_force":390.43916,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51876,0.03365,0.05047]},{"body_a":"attachment","body_b":"peg_socket","contact_count":400.0,"contact_point_centroid":[0.54013,0.03426,0.05099],"force_p95":350.69458,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":356.26953,"mean_force":266.18718,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.52526,0.03427,0.05044]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.51021,0.0355,0.04993],"force_p95":95.43943,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.4876,"mean_force":74.30279,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52515,0.03445,0.05066]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.54006,0.03445,0.05148],"force_p95":56.61907,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.61067,"mean_force":16.65267,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52514,0.03445,0.05069]}],"total_contact_groups":4},"final_pose_error":0.01142,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50787,0.03173,0.13378],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":543.37732,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":515.0,"n_steps_budget":1000.0,"object_pos_end":[0.50643,0.02884,0.19364],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11742,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.50595,0.02881,0.15364],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1335.0,"n_steps_budget":1000.0,"object_pos_end":[0.50683,0.03127,0.12266],"object_pos_start":[0.50643,0.02884,0.19364],"object_to_goal_dist_end":0.05334,"object_to_goal_dist_start":0.11742,"object_z_max":0.19364,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.5084,0.03437,0.07445],"tcp_start":[0.50845,0.03411,0.0755],"tcp_to_object_dist_end":0.04834,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1312.0,"n_steps_budget":1000.0,"object_pos_end":[0.51655,0.03326,0.09049],"object_pos_start":[0.51026,0.03448,0.1144],"object_to_goal_dist_end":0.0386,"object_to_goal_dist_start":0.04978,"object_z_max":0.1144,"peak_contact_force":364.57208,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1620.0,"raw_peak_contact_force":543.37732,"subtask_id":"reach_inserted","tcp_end":[0.52516,0.03445,0.05064],"tcp_start":[0.52514,0.03407,0.0501],"tcp_to_object_dist_end":0.04078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.5062,0.03191,0.17374],"object_pos_start":[0.52304,0.0346,0.09059],"object_to_goal_dist_end":0.09922,"object_to_goal_dist_start":0.0429,"object_z_max":0.17362,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":7.0,"raw_peak_contact_force":98.4876,"subtask_id":"reach_inserted","tcp_end":[0.50787,0.03173,0.13378],"tcp_start":[0.52516,0.03445,0.05064],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e1b235def2e9a643097f1b13c71687d269bd084f74cc515d4edb33de063bcebb`; realized-scene SHA-256: `b9bf2317193e958308a6e071da8e3f166f4f6aad2cd63fb849fb719630631480`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48616,0.03898,0.025]},{"name":"target","value":[0.48616,0.03898,0.025]},{"name":"socket","value":[0.48616,0.03898,0.025]},{"name":"goal","value":[0.48616,0.03898,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.03898,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.13942,"average_solve_count":416.0,"average_success_count":416.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05909,"contact_1.contact_force_threshold":8.99872,"contact_1.contact_speed":0.00947,"insert_1.insert_speed":0.00413,"retract_1.retract_speed":0.10697},"optimized_scores":{"best_composite_score":0.16097,"best_fitness_score":0.47097,"best_task_score":0.81329},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1218.0,"contact_point_centroid":[0.49625,0.04353,0.04994],"force_p95":447.50763,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":565.79485,"mean_force":412.04732,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49528,0.04086,0.05049]},{"body_a":"attachment","body_b":"peg_socket","contact_count":394.0,"contact_point_centroid":[0.51629,0.04158,0.05162],"force_p95":379.42634,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":388.13093,"mean_force":289.47003,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50145,0.04158,0.05076]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.48643,0.0422,0.04994],"force_p95":106.01036,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":110.59463,"mean_force":76.37049,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50139,0.04181,0.051]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.51624,0.04181,0.05215],"force_p95":72.20456,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.94655,"mean_force":21.23664,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50137,0.04181,0.05103]}],"total_contact_groups":4},"final_pose_error":0.01094,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.48417,0.03891,0.13424],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":565.79485,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":510.0,"n_steps_budget":1000.0,"object_pos_end":[0.48487,0.03545,0.19391],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.12025,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.48446,0.03541,0.15391],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1239.0,"n_steps_budget":1000.0,"object_pos_end":[0.48328,0.03839,0.12312],"object_pos_start":[0.48487,0.03545,0.19391],"object_to_goal_dist_end":0.0601,"object_to_goal_dist_start":0.12025,"object_z_max":0.19391,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.48468,0.0415,0.07496],"tcp_start":[0.48459,0.04116,0.07607],"tcp_to_object_dist_end":0.04828,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1312.0,"n_steps_budget":1000.0,"object_pos_end":[0.49298,0.04044,0.09036],"object_pos_start":[0.48641,0.04163,0.11492],"object_to_goal_dist_end":0.04233,"object_to_goal_dist_start":0.05601,"object_z_max":0.11492,"peak_contact_force":374.08875,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1612.0,"raw_peak_contact_force":565.79485,"subtask_id":"reach_inserted","tcp_end":[0.50139,0.04181,0.05098],"tcp_start":[0.5013,0.0413,0.05037],"tcp_to_object_dist_end":0.04029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.48159,0.03903,0.17416],"object_pos_start":[0.49839,0.04189,0.09087],"object_to_goal_dist_end":0.10357,"object_to_goal_dist_start":0.04331,"object_z_max":0.17403,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":7.0,"raw_peak_contact_force":110.59463,"subtask_id":"reach_inserted","tcp_end":[0.48417,0.03891,0.13424],"tcp_start":[0.50139,0.04181,0.05098],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `df6f1ed20a97902d22fe59ab26d8224c17c9641018b24db1f81016e336a9d0ce`; realized-scene SHA-256: `d30c452da2a3cff083d30694df03632a9bb782339e47c14383f7124ad9a32464`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.52962,-0.01705,0.025]},{"name":"target","value":[0.52962,-0.01705,0.025]},{"name":"socket","value":[0.52962,-0.01705,0.025]},{"name":"goal","value":[0.52962,-0.01705,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.01705,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.1565,"average_solve_count":377.0,"average_success_count":377.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05963,"contact_1.contact_force_threshold":8.04407,"contact_1.contact_speed":0.01809,"insert_1.insert_speed":0.00321,"retract_1.retract_speed":0.12001},"optimized_scores":{"best_composite_score":0.18105,"best_fitness_score":0.49105,"best_task_score":0.86588},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1249.0,"contact_point_centroid":[0.54139,-0.0151,0.04994],"force_p95":409.93898,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":528.46245,"mean_force":375.21128,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53826,-0.01538,0.05047]},{"body_a":"attachment","body_b":"peg_socket","contact_count":419.0,"contact_point_centroid":[0.55974,-0.01532,0.05086],"force_p95":345.26895,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":353.93983,"mean_force":255.94149,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.54486,-0.0153,0.05038]},{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.5298,-0.01447,0.04993],"force_p95":79.66632,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.71069,"mean_force":69.60593,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54476,-0.0153,0.05061]},{"body_a":"attachment","body_b":"peg_socket","contact_count":4.0,"contact_point_centroid":[0.55967,-0.0153,0.05139],"force_p95":54.78869,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.45728,"mean_force":16.11432,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54475,-0.0153,0.05065]}],"total_contact_groups":4},"final_pose_error":0.01186,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.52736,-0.01688,0.13336],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":528.46245,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.52435,-0.01557,0.19299],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.11663,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.52386,-0.01556,0.153],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1338.0,"n_steps_budget":1000.0,"object_pos_end":[0.52617,-0.01687,0.12232],"object_pos_start":[0.52435,-0.01557,0.19299],"object_to_goal_dist_end":0.05254,"object_to_goal_dist_start":0.11663,"object_z_max":0.19299,"peak_contact_force":0.0,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_entry","tcp_end":[0.52789,-0.01408,0.07409],"tcp_start":[0.52768,-0.0144,0.07517],"tcp_to_object_dist_end":0.04834,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1341.0,"n_steps_budget":1000.0,"object_pos_end":[0.53644,-0.01566,0.09053],"object_pos_start":[0.52981,-0.01411,0.11404],"object_to_goal_dist_end":0.04104,"object_to_goal_dist_start":0.0474,"object_z_max":0.11404,"peak_contact_force":352.67894,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1668.0,"raw_peak_contact_force":528.46245,"subtask_id":"reach_inserted","tcp_end":[0.54476,-0.0153,0.0506],"tcp_start":[0.54474,-0.01529,0.05005],"tcp_to_object_dist_end":0.04078,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.52583,-0.01678,0.17333],"object_pos_start":[0.54277,-0.01519,0.09055],"object_to_goal_dist_end":0.09828,"object_to_goal_dist_start":0.0466,"object_z_max":0.1732,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":7.0,"raw_peak_contact_force":80.71069,"subtask_id":"reach_inserted","tcp_end":[0.52736,-0.01688,0.13336],"tcp_start":[0.54476,-0.0153,0.0506],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```