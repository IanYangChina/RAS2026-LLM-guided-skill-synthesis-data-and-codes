## Search State

- **Seed**: 0
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | rotate → approach → insert | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.6205 | 0.88 | ❌ rejected |
| 13 | rotate → approach → insert | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.5104 | 0.88 | ✅ accepted |
| 12 | rotate → approach → insert | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.6210 | 0.88 | ✅ accepted |
| 11 | rotate → approach → insert | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.3768 | 0.88 | ❌ rejected |
| 10 | rotate → approach → insert | joint_interpolation | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.1093 | 0.67 | ❌ rejected |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `271e316106eeefadf1968368496c98b5aba16bca2ae9da2edeb84f157a6c113e`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5109569349857164, -0.018417062898890377, 0.08]
- Frozen socket pose: [0.5109569349857164, -0.018417062898890377, 0.025] (static fixture for this episode)
- Goal object position: (0.5109569349857164, -0.018417062898890377, 0.025)
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
  frozen_task_target: [0.511, -0.0184, 0.08]
  frozen_socket_position: [0.511, -0.0184, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5109569349857164, -0.018417062898890377, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5109569349857164, -0.018417062898890377, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 271e316106eeefadf1968368496c98b5aba16bca2ae9da2edeb84f157a6c113e

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.879, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.5109569349857164, -0.018417062898890377, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5109569349857164, -0.018417062898890377, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.621) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_preinsert
  anchor: fixture
  offset:
  - 0.0
  - 0.0
  - 0.04
  weight: 0.3
- id: insertion_complete
  target_entity: object
  weight: 0.7
phases:
- id: orient_downward
  type: rotate
  generator: joint_interpolation
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
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
      align_with: insertion_axis
      tolerance: 0.05
- id: approach_socket
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
    - 0.04
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_preinsert
- id: insert_into_socket
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
      distance: 0.05
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    insert_depth:
      type: scalar
      range:
      - 0.03
      - 0.065
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_force_threshold:
      type: scalar
      range:
      - 25.0
      - 40.0
      default: 35.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.008
    - 0.008
    - 0.0
  subtask_id: insertion_complete

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **orient_downward** (`rotate`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=insertion_axis, tolerance=0.05
  - parameter_bindings: none
- **approach_socket** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.04], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **insert_into_socket** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.008, 0.008, 0.0]

## Design Metrics

- **Composite score**: 0.621
- **task_score** (E): 0.878
- **fitness_score**: 0.617  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| orient_downward | 1.00 | 0.0223 |
| approach_socket | 1.00 | 0.1894 |
| insert_into_socket | 1.00 | 0.0571 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| orient_downward | rotate | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.022, 0.296) | (0.504, -0.000, 0.340)→(0.502, 0.022, 0.335) | 0.260→0.256 |
| approach_socket | approach | 1.00 / step_budget | (0.497, 0.022, 0.296)→(0.494, 0.002, 0.109) | (0.502, 0.022, 0.335)→(0.499, 0.002, 0.149) | 0.256→0.073 |
| insert_into_socket | insert | 1.00 / force_exceeded | (0.494, 0.002, 0.109)→(0.493, 0.001, 0.052) | (0.499, 0.002, 0.149)→(0.498, 0.001, 0.092) | 0.073→0.029 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.923
- alignment_error: None
- terminal_score: 0.923
- phase_score: 0.483
- phase_breakdown.insertion_complete_score: 0.512
- phase_breakdown.reach_preinsert_score: 0.416

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.659
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.923
- **Median Q (composite search score)**: 0.616
- **K-run variance**: 0.0011
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.435


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `193ea3a1ce1ed79056963f057d25ec25a24d300f4824e32f67c8dd96cb6cee27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a8b82e05e54fe244d72795229d8ab0587efc7638aafbc9b6be7ad9630911a897`; realized-scene SHA-256: `271e316106eeefadf1968368496c98b5aba16bca2ae9da2edeb84f157a6c113e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.51096,-0.01842,0.025]},{"name":"target","value":[0.51096,-0.01842,0.025]},{"name":"socket","value":[0.51096,-0.01842,0.025]},{"name":"goal","value":[0.51096,-0.01842,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,-0.01842,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51096,-0.01842,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62025,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_height":0.02014,"approach_socket.approach_speed":0.07497,"approach_socket.approach_tolerance":0.00602,"insert_into_socket.insert_depth":0.05093,"insert_into_socket.insert_force_threshold":38.92149,"insert_into_socket.insert_speed":0.05328},"optimized_scores":{"best_composite_score":0.66252,"best_fitness_score":0.65919,"best_task_score":0.92304},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.02358,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.50536,-0.01742,0.05195],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"phases":[{"n_steps":242.0,"n_steps_budget":600.0,"object_pos_end":[0.50175,0.02183,0.33531],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25625,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"orient_downward","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49719,0.02162,0.29558],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.51156,-0.01546,0.14824],"object_pos_start":[0.50175,0.02183,0.33531],"object_to_goal_dist_end":0.07092,"object_to_goal_dist_start":0.25625,"object_z_max":0.33531,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_preinsert","tcp_end":[0.50653,-0.01566,0.10856],"tcp_start":[0.49719,0.02162,0.29558],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":344.0,"n_steps_budget":930.0,"object_pos_end":[0.51086,-0.01722,0.09157],"object_pos_start":[0.51156,-0.01546,0.14824],"object_to_goal_dist_end":0.02342,"object_to_goal_dist_start":0.07092,"object_z_max":0.14824,"phase_name":"insert_into_socket","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insertion_complete","tcp_end":[0.50536,-0.01742,0.05195],"tcp_start":[0.50653,-0.01566,0.10856],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8b3071e2f56806ea19629fc8ca21c92088a0ed2e080a3c941a59355284793364`; realized-scene SHA-256: `8f814a9d9dd9825bee110b06b2d985dbb0aa82505ba300f6022b2e21e7c15f67`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50095,0.03604,0.025]},{"name":"target","value":[0.50095,0.03604,0.025]},{"name":"socket","value":[0.50095,0.03604,0.025]},{"name":"goal","value":[0.50095,0.03604,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.03604,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50095,0.03604,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43662,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_height":0.02002,"approach_socket.approach_speed":0.11096,"approach_socket.approach_tolerance":0.01056,"insert_into_socket.insert_depth":0.03287,"insert_into_socket.insert_force_threshold":35.91709,"insert_into_socket.insert_speed":0.03696},"optimized_scores":{"best_composite_score":0.58319,"best_fitness_score":0.57985,"best_task_score":0.83989},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00667,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.49639,0.0355,0.05196],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"phases":[{"n_steps":242.0,"n_steps_budget":600.0,"object_pos_end":[0.50175,0.02183,0.33531],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25625,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"orient_downward","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49719,0.02162,0.29558],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.50226,0.03499,0.14866],"object_pos_start":[0.50175,0.02183,0.33531],"object_to_goal_dist_end":0.0771,"object_to_goal_dist_start":0.25625,"object_z_max":0.33531,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_preinsert","tcp_end":[0.49723,0.03475,0.10898],"tcp_start":[0.49719,0.02162,0.29558],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":357.0,"n_steps_budget":1000.0,"object_pos_end":[0.50188,0.03578,0.09158],"object_pos_start":[0.50226,0.03499,0.14866],"object_to_goal_dist_end":0.03765,"object_to_goal_dist_start":0.0771,"object_z_max":0.14866,"phase_name":"insert_into_socket","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insertion_complete","tcp_end":[0.49639,0.0355,0.05196],"tcp_start":[0.49723,0.03475,0.10898],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `9052c43e0ec79f8dbaeeb446a29f2f8fb71a40595590f857e4c93b1d7e78cc51`; realized-scene SHA-256: `4c08395e36e43245f6092dd2e3719288cb8e1800970c3a851b5dc162486241ee`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48093,-0.01612,0.025]},{"name":"target","value":[0.48093,-0.01612,0.025]},{"name":"socket","value":[0.48093,-0.01612,0.025]},{"name":"goal","value":[0.48093,-0.01612,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.01612,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95146,"average_solve_count":103.0,"average_success_count":103.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_socket.approach_height":0.02027,"approach_socket.approach_speed":0.0584,"approach_socket.approach_tolerance":0.01484,"insert_into_socket.insert_depth":0.05325,"insert_into_socket.insert_force_threshold":34.81368,"insert_into_socket.insert_speed":0.03903},"optimized_scores":{"best_composite_score":0.6158,"best_fitness_score":0.61247,"best_task_score":0.87222},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.02572,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.47623,-0.01514,0.05202],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"phases":[{"n_steps":242.0,"n_steps_budget":600.0,"object_pos_end":[0.50175,0.02183,0.33531],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25625,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"phase_name":"orient_downward","phase_peak_obstacle_force":0.0,"phase_type":"rotate","tcp_end":[0.49719,0.02162,0.29558],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":641.0,"n_steps_budget":1000.0,"object_pos_end":[0.4836,-0.01325,0.14913],"object_pos_start":[0.50175,0.02183,0.33531],"object_to_goal_dist_end":0.07227,"object_to_goal_dist_start":0.25625,"object_z_max":0.33531,"phase_name":"approach_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_preinsert","tcp_end":[0.47857,-0.01346,0.10945],"tcp_start":[0.49719,0.02162,0.29558],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.4817,-0.01494,0.09164],"object_pos_start":[0.4836,-0.01325,0.14913],"object_to_goal_dist_end":0.02633,"object_to_goal_dist_start":0.07227,"object_z_max":0.14913,"phase_name":"insert_into_socket","phase_peak_obstacle_force":0.0,"phase_type":"insert","subtask_id":"insertion_complete","tcp_end":[0.47623,-0.01514,0.05202],"tcp_start":[0.47857,-0.01346,0.10945],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```