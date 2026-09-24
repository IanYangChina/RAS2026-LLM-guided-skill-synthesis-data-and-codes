## Search State

- **Seed**: 2
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | rotate → approach → push | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | 9 | 0.2027 | 0.86 | ✅ accepted |
| 7 | rotate → approach → push → push | joint_interpolation | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.2466 | 0.86 | ✅ accepted |
| 6 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 7 | 0.3133 | 0.85 | ❌ rejected |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 7 | 0.3668 | 0.85 | ❌ rejected |
| 4 | approach → push → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3243 | 0.85 | ✅ accepted |

**Proposal policy**: task_score is 0.86 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.4809289707399447, -0.016120708526870135, 0.08]
- Frozen socket pose: [0.4809289707399447, -0.016120708526870135, 0.025] (static fixture for this episode)
- Goal object position: (0.4809289707399447, -0.016120708526870135, 0.025)
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
  frozen_task_target: [0.4809, -0.0161, 0.08]
  frozen_socket_position: [0.4809, -0.0161, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.4809289707399447, -0.016120708526870135, 0.08]}
  frozen_fixtures: {'peg_socket': [0.4809289707399447, -0.016120708526870135, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.861, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.4809289707399447, -0.016120708526870135, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.4809289707399447, -0.016120708526870135, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.203) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: approach_entry
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.3
- id: reach_goal
  target_entity: object
  weight: 0.7
phases:
- id: align_orientation
  type: rotate
  generator: joint_interpolation
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.05
  parameters:
    rotate_duration:
      type: scalar
      range:
      - 1.0
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
    rotate_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: approach_socket
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
    - 0.055
    tolerance: 0.01
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.08
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.04
      - 0.07
      default: 0.055
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_entry
- id: insert_peg
  type: push
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
    - 0.055
    offset_along_axis:
      distance: 0.055
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.015
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: insertion_axis
      tolerance: 0.08
  parameters:
    force_limit:
      type: scalar
      range:
      - 20.0
      - 60.0
      default: 40.0
      binds_to:
      - path: guards.force_limit.threshold
        mode: replace
    insert_depth:
      type: scalar
      range:
      - 0.04
      - 0.07
      default: 0.055
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.04
      default: 0.01
      binds_to:
      - path: generator.speed
        mode: replace
    insert_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.015
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_limit
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
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **align_orientation** (`rotate`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings:
    - rotate_duration: status=consumed; consumers=duration.max_time (replace)
    - rotate_speed: status=consumed; consumers=generator.speed (replace)
- **approach_socket** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], tolerance=0.01
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.08
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **insert_peg** (`push`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.055], offset_along_axis={axis=channel_axis, distance=0.055, mode=add_to_offset, sign=positive}, tolerance=0.015
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.08
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.force_limit.threshold (replace)
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insert_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]

## Design Metrics

- **Composite score**: 0.203
- **task_score** (E): 0.861
- **fitness_score**: 0.683  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_orientation | 1.00 | 0.00 | 0.0249 |
| approach_socket | 1.00 | 0.67 | 0.2204 |
| insert_peg | 0.33 | 0.00 | 0.0096 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_orientation | rotate | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.497, 0.024, 0.296) | (0.504, -0.000, 0.340)→(0.502, 0.024, 0.335) | 0.260→0.256 | 0.00 / 0.000 | 0.000 | 0.000 |
| approach_socket | approach | 1.00 / step_budget | (0.497, 0.024, 0.296)→(0.491, -0.010, 0.080) | (0.502, 0.024, 0.335)→(0.492, -0.010, 0.120) | 0.256→0.051 | 0.67 / 0.667 | 48.467 | 162.369 |
| insert_peg | push | 0.33 / guard_failure | (0.490, -0.011, 0.060)→(0.490, -0.011, 0.050) | (0.492, -0.010, 0.120)→(0.490, -0.011, 0.090) | 0.051→0.034 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.886
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.886
- phase_score: 0.588
- phase_breakdown.reach_goal_score: 0.441
- phase_breakdown.approach_entry_score: 0.933

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.707
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.886
- **Median Q (composite search score)**: 0.207
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.326


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6921a9025d4eafab3a26182307d104597a59aa3c28d9e7087cf253b6e9b1c7f`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `d09be956b809b9acd01354eeb5f0494d5058516cbca42b9f2b0bee8c1b6b25a7`; realized-scene SHA-256: `a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48093,-0.01612,0.025]},{"name":"target","value":[0.48093,-0.01612,0.025]},{"name":"socket","value":[0.48093,-0.01612,0.025]},{"name":"goal","value":[0.48093,-0.01612,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.01612,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21698,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.rotate_duration":3.84209,"align_orientation.rotate_speed":0.03713,"approach_socket.approach_height":0.04539,"approach_socket.approach_speed":0.06635,"approach_socket.approach_tolerance":0.01796,"insert_peg.force_limit":54.95278,"insert_peg.insert_depth":0.05419,"insert_peg.insert_speed":0.02865,"insert_peg.insert_tolerance":0.01293},"optimized_scores":{"best_composite_score":0.22745,"best_fitness_score":0.70745,"best_task_score":0.8862},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.49192,-0.01525,0.04985],"force_p95":249.28876,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":265.91334,"mean_force":144.36852,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"push","tcp_position_centroid":[0.47694,-0.01486,0.04987]}],"total_contact_groups":1},"final_pose_error":0.02407,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47699,-0.01489,0.04952],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":265.91334,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":464.0,"n_steps_budget":600.0,"object_pos_end":[0.50162,0.02442,0.33528],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25646,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49706,0.02419,0.29555],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":724.0,"n_steps_budget":1000.0,"object_pos_end":[0.47895,-0.01366,0.11975],"object_pos_start":[0.50162,0.02442,0.33528],"object_to_goal_dist_end":0.04701,"object_to_goal_dist_start":0.25646,"object_z_max":0.33528,"peak_contact_force":67.5247,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3.0,"raw_peak_contact_force":265.91334,"subtask_id":"approach_entry","tcp_end":[0.47851,-0.01365,0.07975],"tcp_start":[0.49706,0.02419,0.29555],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":88.0,"n_steps_budget":1000.0,"object_pos_end":[0.47736,-0.01486,0.08982],"object_pos_start":[0.47895,-0.01366,0.11975],"object_to_goal_dist_end":0.02881,"object_to_goal_dist_start":0.04701,"object_z_max":0.11975,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.47699,-0.01489,0.04952],"tcp_start":[0.47696,-0.01488,0.04963],"tcp_to_object_dist_end":0.0403,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`; realized-scene SHA-256: `c110175cdc23a481ee4f5a8b0b433c8e6c91b615df874546135cb56aaa5a8af6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.89157,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.rotate_duration":2.21337,"align_orientation.rotate_speed":0.13209,"approach_socket.approach_height":0.04553,"approach_socket.approach_speed":0.19314,"approach_socket.approach_tolerance":0.02593,"insert_peg.force_limit":29.87338,"insert_peg.insert_depth":0.04282,"insert_peg.insert_speed":0.01515,"insert_peg.insert_tolerance":0.01136},"optimized_scores":{"best_composite_score":0.17318,"best_fitness_score":0.65318,"best_task_score":0.8272},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01482,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46347,-0.01987,0.05155],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":464.0,"n_steps_budget":600.0,"object_pos_end":[0.50162,0.02442,0.33528],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25646,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49706,0.02419,0.29555],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":603.0,"n_steps_budget":750.0,"object_pos_end":[0.46579,-0.01829,0.11994],"object_pos_start":[0.50162,0.02442,0.33528],"object_to_goal_dist_end":0.05568,"object_to_goal_dist_start":0.25646,"object_z_max":0.33528,"peak_contact_force":0.0,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"approach_entry","tcp_end":[0.46535,-0.01827,0.07994],"tcp_start":[0.49706,0.02419,0.29555],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":90.0,"n_steps_budget":1000.0,"object_pos_end":[0.46389,-0.01988,0.09155],"object_pos_start":[0.46579,-0.01829,0.11994],"object_to_goal_dist_end":0.0428,"object_to_goal_dist_start":0.05568,"object_z_max":0.11994,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.46347,-0.01987,0.05155],"tcp_start":[0.46535,-0.01827,0.07994],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`; realized-scene SHA-256: `6aa6006ba5d7c7f83773c59f42ad1597db3f9073c3225635eb35deca1cb0f02a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.80612,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_orientation.rotate_duration":2.23821,"align_orientation.rotate_speed":0.02115,"approach_socket.approach_height":0.04699,"approach_socket.approach_speed":0.14812,"approach_socket.approach_tolerance":0.01685,"insert_peg.force_limit":43.58913,"insert_peg.insert_depth":0.05752,"insert_peg.insert_speed":0.01427,"insert_peg.insert_tolerance":0.00931},"optimized_scores":{"best_composite_score":0.20742,"best_fitness_score":0.68742,"best_task_score":0.86936},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.54408,0.0018,0.04978],"force_p95":211.05526,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":221.19443,"mean_force":139.62431,"phase_index":2.0,"phase_name":"insert_peg","phase_type":"push","tcp_position_centroid":[0.52909,0.00151,0.04974]}],"total_contact_groups":1},"final_pose_error":0.02766,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.5292,0.00149,0.04942],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":221.19443,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":464.0,"n_steps_budget":600.0,"object_pos_end":[0.50162,0.02442,0.33528],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25646,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"align_orientation","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.49706,0.02419,0.29555],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":667.0,"n_steps_budget":960.0,"object_pos_end":[0.53,0.00218,0.11991],"object_pos_start":[0.50162,0.02442,0.33528],"object_to_goal_dist_end":0.04997,"object_to_goal_dist_start":0.25646,"object_z_max":0.33528,"peak_contact_force":77.87571,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3.0,"raw_peak_contact_force":221.19443,"subtask_id":"approach_entry","tcp_end":[0.52952,0.00217,0.07991],"tcp_start":[0.49706,0.02419,0.29555],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":94.0,"n_steps_budget":1000.0,"object_pos_end":[0.52955,0.00153,0.08969],"object_pos_start":[0.53,0.00218,0.11991],"object_to_goal_dist_end":0.03114,"object_to_goal_dist_start":0.04997,"object_z_max":0.11991,"peak_contact_force":0.0,"phase_name":"insert_peg","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.5292,0.00149,0.04942],"tcp_start":[0.52915,0.00151,0.04951],"tcp_to_object_dist_end":0.04027,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```