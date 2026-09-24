## Search State

- **Seed**: 2
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 10 | -0.4125 | 0.00 | ❌ rejected |
| 4 | approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 10 | 0.4021 | 0.87 | ❌ rejected |
| 3 | approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.5048 | 0.87 | ✅ accepted |
| 2 | approach → contact → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.5046 | 0.87 | ✅ accepted |
| 1 | approach → insert | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 4 | -0.1914 | 0.01 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.4809289707399447, -0.016120708526870135, 0.08]
- Frozen task target: [0.4809289707399447, -0.016120708526870135, 0.025]
- Frozen socket pose: [0.5, 0.0, 0.3] (static fixture for this episode)
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.4809289707399447, -0.016120708526870135, 0.08)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 40.0 N
- Channel axis: `(0.0, 0.0, -1.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth ratio (axial progress into hole)**

## Scene Entities

robot:
  model: panda_peg
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
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
  frozen_object_starts: {'peg': [0.4809289707399447, -0.016120708526870135, 0.08]}
  frozen_targets: {'socket_entry': [0.4809289707399447, -0.016120708526870135, 0.025]}
  frozen_fixtures: {'peg_socket': [0.5, 0.0, 0.3]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: a6823a6b5ef7fcb4f9033e8129e1dc742f22f8d88729a895d8be5b1aeb9126b0

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.872, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.4809289707399447, -0.016120708526870135, 0.08) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.0, 0.3) | approach/contact targets near fixture |

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

## Current Skill (Q=-0.413) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_pre_contact
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.02
  weight: 0.3
- id: insertion_goal
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - -0.05
  weight: 0.7
phases:
- id: approach_above_socket
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
    - 0.02
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
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: add
  subtask_id: reach_pre_contact
- id: contact_socket
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
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 40.0
      default: 20.0
      binds_to:
      - path: termination.force_threshold
        mode: add
    lateral_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: reach_pre_contact
- id: insert_into_hole
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
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    insert_distance:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: add
    lateral_offset_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 3
    strategy: offset_target
    offset:
    - 0.008
    - 0.008
    - 0.0
  subtask_id: insertion_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_socket** (`approach`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.02]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
- **contact_socket** (`contact`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (add)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **insert_into_hole** (`insert`)
  - target: source=yaml, anchor=fixture, entity=peg_socket, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=replace_offset_projection, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - insert_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (add)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=3, strategy=offset_target, offset=[0.008, 0.008, 0.0]

## Design Metrics

- **Composite score**: -0.413
- **task_score** (E): 0.001
- **fitness_score**: 0.117  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_entry | 1.00 | 0.00 | 0.0501 |
| contact_entry | 0.00 | 0.00 | 0.0318 |
| insert_into_hole | 1.00 | 0.00 | 0.0096 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_entry | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.502, -0.000, 0.351) | (0.504, -0.000, 0.340)→(0.502, -0.000, 0.391) | 0.260→0.311 | 0.00 / 0.000 | 0.000 | 0.000 |
| contact_entry | contact | 0.00 / step_budget | (0.502, -0.000, 0.351)→(0.504, 0.000, 0.382) | (0.502, -0.000, 0.391)→(0.504, 0.000, 0.422) | 0.311→0.342 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_into_hole | insert | 1.00 / step_budget | (0.504, 0.000, 0.382)→(0.504, -0.001, 0.373) | (0.504, 0.000, 0.422)→(0.504, -0.001, 0.413) | 0.342→0.333 | 0.00 / 0.000 | 0.000 | 0.000 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.001
- alignment_error: None
- force_efficiency: 1.000
- terminal_score: 0.001
- phase_score: 0.195
- phase_breakdown.insertion_goal_score: 0.003
- phase_breakdown.reach_pre_contact_score: 0.643

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.118
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.412
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.197


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
{"anchors":[{"name":"object","value":[0.48093,-0.01612,0.08]},{"name":"task_object","value":[0.48093,-0.01612,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.48093,-0.01612,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.93333,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_entry.approach_speed":0.26897,"contact_entry.contact_force_threshold":19.41973,"contact_entry.lateral_offset_x":0.00317,"contact_entry.lateral_offset_y":0.00134,"insert_into_hole.insert_distance":0.06037,"insert_into_hole.insert_speed":0.03333,"insert_into_hole.lateral_offset_x":-0.0054,"insert_into_hole.lateral_offset_y":0.00096,"insert_into_hole.retry_offset_x":1e-05,"insert_into_hole.retry_offset_y":0.00334},"optimized_scores":{"best_composite_score":-0.41249,"best_fitness_score":0.11751,"best_task_score":0.00116},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00986,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.50116,0.00156,0.37152],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":465.0,"n_steps_budget":600.0,"object_pos_end":[0.50236,-1e-05,0.3906],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.31061,"object_to_goal_dist_start":0.26034,"object_z_max":0.39051,"peak_contact_force":0.0,"phase_name":"approach_above_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_contact","tcp_end":[0.5019,-2e-05,0.3506],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50428,0.00121,0.42232],"object_pos_start":[0.50236,-1e-05,0.3906],"object_to_goal_dist_end":0.34235,"object_to_goal_dist_start":0.31061,"object_z_max":0.42227,"peak_contact_force":0.0,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_contact","tcp_end":[0.50384,0.0012,0.38232],"tcp_start":[0.5019,-2e-05,0.3506],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":44.0,"n_steps_budget":600.0,"object_pos_end":[0.50157,0.00158,0.41152],"object_pos_start":[0.50428,0.00121,0.42232],"object_to_goal_dist_end":0.33153,"object_to_goal_dist_start":0.34235,"object_z_max":0.42234,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_goal","tcp_end":[0.50116,0.00156,0.37152],"tcp_start":[0.50384,0.0012,0.38232],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7c892e828ea48eee928c80191ad243a972830b09953cba6358be1d4656816d00`; realized-scene SHA-256: `c110175cdc23a481ee4f5a8b0b433c8e6c91b615df874546135cb56aaa5a8af6`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,-0.02106,0.08]},{"name":"task_object","value":[0.46685,-0.02106,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.46685,-0.02106,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98333,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_entry.approach_speed":0.31152,"contact_entry.contact_force_threshold":31.04604,"contact_entry.lateral_offset_x":0.00336,"contact_entry.lateral_offset_y":-0.00136,"insert_into_hole.insert_distance":0.06244,"insert_into_hole.insert_speed":0.02686,"insert_into_hole.lateral_offset_x":0.00428,"insert_into_hole.lateral_offset_y":-0.00957,"insert_into_hole.retry_offset_x":-0.01804,"insert_into_hole.retry_offset_y":0.01413},"optimized_scores":{"best_composite_score":-0.41239,"best_fitness_score":0.11761,"best_task_score":0.00116},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00973,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.50546,-0.006,0.36767],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":465.0,"n_steps_budget":600.0,"object_pos_end":[0.50236,-1e-05,0.3906],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.31061,"object_to_goal_dist_start":0.26034,"object_z_max":0.39051,"peak_contact_force":0.0,"phase_name":"approach_above_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_contact","tcp_end":[0.5019,-2e-05,0.3506],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50446,-0.00126,0.42232],"object_pos_start":[0.50236,-1e-05,0.3906],"object_to_goal_dist_end":0.34235,"object_to_goal_dist_start":0.31061,"object_z_max":0.42226,"peak_contact_force":0.0,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_contact","tcp_end":[0.50401,-0.00127,0.38232],"tcp_start":[0.5019,-2e-05,0.3506],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":61.0,"n_steps_budget":600.0,"object_pos_end":[0.50589,-0.00599,0.40767],"object_pos_start":[0.50446,-0.00126,0.42232],"object_to_goal_dist_end":0.32777,"object_to_goal_dist_start":0.34235,"object_z_max":0.42234,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_goal","tcp_end":[0.50546,-0.006,0.36767],"tcp_start":[0.50401,-0.00127,0.38232],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `65c1f23a0338c26bf257d85b07ab64c0180da795e8d67e7d51a2ed2fb2a4d0db`; realized-scene SHA-256: `6aa6006ba5d7c7f83773c59f42ad1597db3f9073c3225635eb35deca1cb0f02a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.00091,0.08]},{"name":"task_object","value":[0.53544,0.00091,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.53544,0.00091,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.7,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_entry.approach_speed":0.31826,"contact_entry.contact_force_threshold":24.13887,"contact_entry.lateral_offset_x":0.00301,"contact_entry.lateral_offset_y":0.00127,"insert_into_hole.insert_distance":0.04555,"insert_into_hole.insert_speed":0.01923,"insert_into_hole.lateral_offset_x":0.00411,"insert_into_hole.lateral_offset_y":0.00215,"insert_into_hole.retry_offset_x":-0.00325,"insert_into_hole.retry_offset_y":0.01188},"optimized_scores":{"best_composite_score":-0.41269,"best_fitness_score":0.11731,"best_task_score":0.00116},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00585,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.50399,0.00139,0.38031],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":465.0,"n_steps_budget":600.0,"object_pos_end":[0.50236,-1e-05,0.3906],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.31061,"object_to_goal_dist_start":0.26034,"object_z_max":0.39051,"peak_contact_force":0.0,"phase_name":"approach_above_entry","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_contact","tcp_end":[0.5019,-2e-05,0.3506],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":513.0,"n_steps_budget":600.0,"object_pos_end":[0.50414,0.00115,0.42232],"object_pos_start":[0.50236,-1e-05,0.3906],"object_to_goal_dist_end":0.34235,"object_to_goal_dist_start":0.31061,"object_z_max":0.42227,"peak_contact_force":0.0,"phase_name":"contact_entry","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_contact","tcp_end":[0.5037,0.00114,0.38232],"tcp_start":[0.5019,-2e-05,0.3506],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50441,0.00141,0.4203],"object_pos_start":[0.50414,0.00115,0.42232],"object_to_goal_dist_end":0.34034,"object_to_goal_dist_start":0.34235,"object_z_max":0.42234,"peak_contact_force":0.0,"phase_name":"insert_into_hole","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_goal","tcp_end":[0.50399,0.00139,0.38031],"tcp_start":[0.5037,0.00114,0.38232],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```