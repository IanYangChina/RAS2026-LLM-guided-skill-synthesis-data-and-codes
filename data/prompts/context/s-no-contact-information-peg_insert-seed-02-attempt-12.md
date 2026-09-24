## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.5028 | 0.85 | ❌ rejected |
| 11 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.4054 | 0.85 | ✅ accepted |
| 10 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 9 | 0.4052 | 0.85 | ✅ accepted |
| 9 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 10 | 0.3768 | 0.85 | ❌ rejected |
| 8 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.0680 | 0.85 | ✅ accepted |

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

## Current Skill (Q=0.503) — your mutation base

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
    tolerance: 0.03
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
    tolerance: 0.03
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
  termination: force_exceeded
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
      - 0.06
      default: 0.055
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_force_threshold:
      type: scalar
      range:
      - 30.0
      - 39.0
      default: 35.0
      binds_to:
      - path: termination.force_threshold
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_offset_z: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_entry** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.055], tolerance=0.03
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - descend_offset_z: status=consumed; consumers=target.offset.z (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **insert_deep** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.055, mode=add_to_offset, sign=positive}, tolerance=0.04
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
    - retry_offset_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_offset_y: status=consumed; consumers=retry.offset.y (replace)
  - retries: max_attempts=3, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.503
- **task_score** (E): 0.851
- **fitness_score**: 0.611  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above_socket | 1.00 | 0.0761 |
| descend_to_entry | 1.00 | 0.1240 |
| insert_deep | 0.67 | 0.0533 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above_socket | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.495, -0.008, 0.228) | (0.504, -0.000, 0.340)→(0.503, -0.008, 0.267) | 0.260→0.188 |
| descend_to_entry | descend | 1.00 / step_budget | (0.495, -0.008, 0.228)→(0.492, -0.011, 0.104) | (0.503, -0.008, 0.267)→(0.492, -0.011, 0.144) | 0.188→0.072 |
| insert_deep | insert | 0.67 / force_exceeded | (0.492, -0.011, 0.104)→(0.490, -0.012, 0.051) | (0.492, -0.011, 0.144)→(0.490, -0.012, 0.091) | 0.072→0.035 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.873
- alignment_error: None
- terminal_score: 0.873
- phase_score: 0.460
- phase_breakdown.full_insertion_score: 0.433
- phase_breakdown.reach_socket_entry_score: 0.613
- phase_breakdown.reach_above_socket_score: 0.343

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.625
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.873
- **Median Q (composite search score)**: 0.628
- **K-run variance**: 0.0316
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.488


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.08333,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_socket.approach_offset_z":0.12023,"approach_above_socket.approach_speed":0.18925,"descend_to_entry.descend_speed":0.16797,"insert_deep.insert_depth":0.0469,"insert_deep.insert_force_threshold":38.27424,"insert_deep.insert_speed":0.06294},"optimized_scores":{"best_composite_score":0.6284,"best_fitness_score":0.62507,"best_task_score":0.87187},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.01753,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47668,-0.01578,0.0501],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"phases":[{"n_steps":106.0,"n_steps_budget":600.0,"object_pos_end":[0.49482,-0.01091,0.26772],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18811,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above_socket","tcp_end":[0.48576,-0.01085,0.22876],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":210.0,"n_steps_budget":600.0,"object_pos_end":[0.47967,-0.01516,0.14457],"object_pos_start":[0.49482,-0.01091,0.26772],"object_to_goal_dist_end":0.06937,"object_to_goal_dist_start":0.18811,"object_z_max":0.26772,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_socket_entry","tcp_end":[0.47907,-0.01515,0.10457],"tcp_start":[0.48576,-0.01085,0.22876],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":313.0,"n_steps_budget":720.0,"object_pos_end":[0.47712,-0.01578,0.09009],"object_pos_start":[0.47967,-0.01516,0.14457],"object_to_goal_dist_end":0.02957,"object_to_goal_dist_start":0.06937,"object_z_max":0.14457,"phase_name":"insert_deep","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"full_insertion","tcp_end":[0.47668,-0.01578,0.0501],"tcp_start":[0.47907,-0.01515,0.10457],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36782,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_socket.approach_offset_z":0.12111,"approach_above_socket.approach_speed":0.39285,"descend_to_entry.descend_speed":0.17913,"insert_deep.insert_depth":0.03014,"insert_deep.insert_force_threshold":38.58108,"insert_deep.insert_speed":0.02411},"optimized_scores":{"best_composite_score":0.25155,"best_fitness_score":0.58155,"best_task_score":0.80819},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00492,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.4631,-0.0208,0.05303],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"phases":[{"n_steps":110.0,"n_steps_budget":600.0,"object_pos_end":[0.48578,-0.01452,0.26711],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18821,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above_socket","tcp_end":[0.47594,-0.0144,0.22834],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":208.0,"n_steps_budget":600.0,"object_pos_end":[0.46638,-0.01983,0.14463],"object_pos_start":[0.48578,-0.01452,0.26711],"object_to_goal_dist_end":0.0755,"object_to_goal_dist_start":0.18821,"object_z_max":0.26711,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_socket_entry","tcp_end":[0.46576,-0.0198,0.10463],"tcp_start":[0.47594,-0.0144,0.22834],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":336.0,"n_steps_budget":1000.0,"object_pos_end":[0.46352,-0.02081,0.09303],"object_pos_start":[0.46638,-0.01983,0.14463],"object_to_goal_dist_end":0.04397,"object_to_goal_dist_start":0.0755,"object_z_max":0.14463,"phase_name":"insert_deep","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"full_insertion","tcp_end":[0.4631,-0.0208,0.05303],"tcp_start":[0.46576,-0.0198,0.10463],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85938,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_socket.approach_offset_z":0.12028,"approach_above_socket.approach_speed":0.12824,"descend_to_entry.descend_speed":0.28945,"insert_deep.insert_depth":0.05664,"insert_deep.insert_force_threshold":39.82378,"insert_deep.insert_speed":0.04993},"optimized_scores":{"best_composite_score":0.62847,"best_fitness_score":0.62514,"best_task_score":0.87296},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.02748,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.52941,0.00079,0.05017],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"phases":[{"n_steps":114.0,"n_steps_budget":600.0,"object_pos_end":[0.52931,0.0006,0.2666],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.18889,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_above_socket","tcp_end":[0.52315,0.00059,0.22708],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":214.0,"n_steps_budget":600.0,"object_pos_end":[0.53103,0.00081,0.14392],"object_pos_start":[0.52931,0.0006,0.2666],"object_to_goal_dist_end":0.07106,"object_to_goal_dist_start":0.18889,"object_z_max":0.2666,"phase_name":"descend_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_socket_entry","tcp_end":[0.53047,0.0008,0.10393],"tcp_start":[0.52315,0.00059,0.22708],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.52989,0.00079,0.09017],"object_pos_start":[0.53103,0.00081,0.14392],"object_to_goal_dist_end":0.03158,"object_to_goal_dist_start":0.07106,"object_z_max":0.14392,"phase_name":"insert_deep","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"full_insertion","tcp_end":[0.52941,0.00079,0.05017],"tcp_start":[0.53047,0.0008,0.10393],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```