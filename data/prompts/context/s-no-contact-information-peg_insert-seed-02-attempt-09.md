## Search State

- **Seed**: 2
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 10 | 0.3768 | 0.85 | ❌ rejected |
| 8 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0680 | 0.85 | ✅ accepted |
| 7 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0671 | 0.85 | ✅ accepted |
| 6 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0723 | 0.85 | ✅ accepted |
| 5 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.4288 | 0.85 | ❌ rejected |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.852, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.377) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_above_socket
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: reach_socket_entry
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.055
  weight: 0.3
- id: full_insertion
  weight: 0.4
phases:
- id: approach_above_socket
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_offset_z:
      type: scalar
      range:
      - 0.12
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_above_socket
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
    - 0.055
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    descend_offset_z:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.055
      binds_to:
      - path: target.offset.z
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_socket_entry
- id: insert_deep
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.055
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.04
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.055
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_force_threshold:
      type: scalar
      range:
      - 30.0
      - 39.0
      default: 38.0
      binds_to:
      - path: guards.force_limit.threshold
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    insert_tolerance:
      type: scalar
      range:
      - 0.02
      - 0.05
      default: 0.04
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    retry_offset_x:
      type: scalar
      range:
      - 0.002
      - 0.015
      default: 0.005
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_offset_y:
      type: scalar
      range:
      - 0.002
      - 0.015
      default: 0.005
      binds_to:
      - path: retry.offset.y
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 38.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: full_insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_socket** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_entry** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.055], tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_deep** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.055, mode=add_to_offset, sign=positive}, tolerance=0.04
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_force_threshold: status=consumed; consumers=guards.force_limit.threshold (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - insert_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=38.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.377
- **task_score** (E): 0.850
- **fitness_score**: 0.573  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above_socket | 1.00 | 0.0861 |
| descend_to_entry | 1.00 | 0.0845 |
| insert_deep | 1.00 | 0.0842 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above_socket | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, -0.009, 0.218) | (0.504, -0.000, 0.340)→(0.498, -0.009, 0.258) | 0.260→0.180 |
| descend_to_entry | descend | 1.00 / step_budget | (0.494, -0.009, 0.218)→(0.492, -0.011, 0.134) | (0.498, -0.009, 0.258)→(0.492, -0.011, 0.174) | 0.180→0.100 |
| insert_deep | insert | 1.00 / force_exceeded | (0.492, -0.011, 0.134)→(0.490, -0.012, 0.050) | (0.492, -0.011, 0.174)→(0.490, -0.012, 0.090) | 0.100→0.035 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.872
- alignment_error: None
- terminal_score: 0.872
- phase_score: 0.410
- phase_breakdown.full_insertion_score: 0.439
- phase_breakdown.reach_socket_entry_score: 0.368
- phase_breakdown.reach_above_socket_score: 0.413

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.595
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.872
- **Median Q (composite search score)**: 0.389
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.371


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74627,"average_solve_count":67.0,"average_success_count":67.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_socket.approach_offset_z":0.12009,"approach_above_socket.approach_speed":0.13706,"descend_to_entry.descend_offset_z":0.03044,"descend_to_entry.descend_speed":0.18117,"insert_deep.insert_depth":0.07223,"insert_deep.insert_force_threshold":33.66136,"insert_deep.insert_speed":0.06544,"insert_deep.retry_offset_x":0.01029,"insert_deep.retry_offset_y":0.00419,"insert_deep.seating_force":27.44686},"optimized_scores":{"best_composite_score":0.39791,"best_fitness_score":0.59458,"best_task_score":0.87156},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.04259,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47651,-0.01571,0.05012],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"phases":[{"n_steps":160.0,"n_steps_budget":600.0,"object_pos_end":[0.48806,-0.01233,0.25878],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1796,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above_socket","tcp_end":[0.48354,-0.01233,0.21903],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":167.0,"n_steps_budget":600.0,"object_pos_end":[0.47967,-0.01521,0.16992],"object_pos_start":[0.48806,-0.01233,0.25878],"object_to_goal_dist_end":0.09343,"object_to_goal_dist_start":0.1796,"object_z_max":0.25878,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_socket_entry","tcp_end":[0.4791,-0.0152,0.12992],"tcp_start":[0.48354,-0.01233,0.21903],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.47695,-0.01572,0.09012],"object_pos_start":[0.47967,-0.01521,0.16992],"object_to_goal_dist_end":0.02968,"object_to_goal_dist_start":0.09343,"object_z_max":0.16992,"phase_name":"insert_deep","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"full_insertion","tcp_end":[0.47651,-0.01571,0.05012],"tcp_start":[0.4791,-0.0152,0.12992],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0,"average_solve_count":113.0,"average_success_count":113.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_socket.approach_offset_z":0.12113,"approach_above_socket.approach_speed":0.12664,"descend_to_entry.descend_offset_z":0.03693,"descend_to_entry.descend_speed":0.12852,"insert_deep.insert_depth":0.06951,"insert_deep.insert_force_threshold":31.54271,"insert_deep.insert_speed":0.0254,"insert_deep.retry_offset_x":0.01194,"insert_deep.retry_offset_y":0.00782,"insert_deep.seating_force":26.82823},"optimized_scores":{"best_composite_score":0.34321,"best_fitness_score":0.53988,"best_task_score":0.80812},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.03982,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.46292,-0.02053,0.05011],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"phases":[{"n_steps":166.0,"n_steps_budget":600.0,"object_pos_end":[0.47707,-0.01628,0.25896],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18115,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above_socket","tcp_end":[0.47255,-0.01627,0.21921],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":156.0,"n_steps_budget":600.0,"object_pos_end":[0.4665,-0.01983,0.17647],"object_pos_start":[0.47707,-0.01628,0.25896],"object_to_goal_dist_end":0.10403,"object_to_goal_dist_start":0.18115,"object_z_max":0.25896,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_socket_entry","tcp_end":[0.4659,-0.01981,0.13648],"tcp_start":[0.47255,-0.01627,0.21921],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":565.0,"n_steps_budget":1000.0,"object_pos_end":[0.46334,-0.02055,0.09011],"object_pos_start":[0.4665,-0.01983,0.17647],"object_to_goal_dist_end":0.04323,"object_to_goal_dist_start":0.10403,"object_z_max":0.17647,"phase_name":"insert_deep","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"full_insertion","tcp_end":[0.46292,-0.02053,0.05011],"tcp_start":[0.4659,-0.01981,0.13648],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3913,"average_solve_count":92.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_socket.approach_offset_z":0.12016,"approach_above_socket.approach_speed":0.20476,"descend_to_entry.descend_offset_z":0.03732,"descend_to_entry.descend_speed":0.16238,"insert_deep.insert_depth":0.07926,"insert_deep.insert_force_threshold":32.04607,"insert_deep.insert_speed":0.03518,"insert_deep.retry_offset_x":0.00592,"insert_deep.retry_offset_y":0.00631,"insert_deep.seating_force":28.21316},"optimized_scores":{"best_composite_score":0.38935,"best_fitness_score":0.58602,"best_task_score":0.87121},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.04981,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.5293,0.00079,0.05017],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"phases":[{"n_steps":174.0,"n_steps_budget":600.0,"object_pos_end":[0.52998,0.00068,0.25697],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17949,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above_socket","tcp_end":[0.5254,0.00067,0.21723],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":150.0,"n_steps_budget":600.0,"object_pos_end":[0.53098,0.00082,0.17637],"object_pos_start":[0.52998,0.00068,0.25697],"object_to_goal_dist_end":0.10123,"object_to_goal_dist_start":0.17949,"object_z_max":0.25697,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_socket_entry","tcp_end":[0.53027,0.00081,0.13638],"tcp_start":[0.5254,0.00067,0.21723],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":500.0,"n_steps_budget":1000.0,"object_pos_end":[0.52978,0.00079,0.09017],"object_pos_start":[0.53098,0.00082,0.17637],"object_to_goal_dist_end":0.03148,"object_to_goal_dist_start":0.10123,"object_z_max":0.17637,"phase_name":"insert_deep","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"full_insertion","tcp_end":[0.5293,0.00079,0.05017],"tcp_start":[0.53027,0.00081,0.13638],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```