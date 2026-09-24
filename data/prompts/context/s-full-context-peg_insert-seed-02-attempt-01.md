## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2709 | 0.85 | ✅ accepted |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.0712 | 0.10 | ✅ accepted |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.850, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.271) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_pre_insert
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: insertion_progress
  weight: 0.7
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
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_z_offset:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_pre_insert
- id: align_at_entry
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
    - 0.0
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    align_tolerance:
      type: scalar
      range:
      - 0.001
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: reach_pre_insert
- id: insert_downward
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
      distance: 0.05
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    insert_distance:
      type: scalar
      range:
      - 0.03
      - 0.07
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insert_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insertion_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_socket** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **align_at_entry** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - align_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **insert_downward** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=replace_offset_projection, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - insert_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insert_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.271
- **task_score** (E): 0.850
- **fitness_score**: 0.601  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_socket | 1.00 | 0.00 | 0.0968 |
| align_at_entry | 0.33 | 0.00 | 0.0634 |
| insert_downward | 1.00 | 0.67 | 0.0929 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_socket | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.493, -0.010, 0.209) | (0.504, -0.000, 0.340)→(0.498, -0.010, 0.248) | 0.260→0.171 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_at_entry | align | 0.33 / step_budget | (0.493, -0.010, 0.209)→(0.492, -0.011, 0.145) | (0.498, -0.010, 0.248)→(0.492, -0.011, 0.185) | 0.171→0.111 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_downward | insert | 1.00 / step_budget | (0.492, -0.011, 0.145)→(0.498, -0.012, 0.053) | (0.492, -0.011, 0.185)→(0.498, -0.012, 0.093) | 0.111→0.031 | 0.67 / 0.667 | 298.176 | 343.417 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.871
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.871
- phase_score: 0.495
- phase_breakdown.reach_pre_insert_score: 0.511
- phase_breakdown.insertion_progress_score: 0.488

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.645
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.871
- **Median Q (composite search score)**: 0.250
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.448


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.69948,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_entry.align_speed":0.01253,"align_at_entry.align_tolerance":0.00283,"approach_above_socket.approach_speed":0.0286,"approach_above_socket.approach_z_offset":0.12039,"insert_downward.insert_distance":0.06782,"insert_downward.insert_speed":0.04113},"optimized_scores":{"best_composite_score":0.3152,"best_fitness_score":0.6452,"best_task_score":0.87102},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":421.0,"contact_point_centroid":[0.49731,-0.01752,0.04993],"force_p95":479.14609,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":520.62832,"mean_force":462.80841,"phase_index":2.0,"phase_name":"insert_downward","phase_type":"insert","tcp_position_centroid":[0.48247,-0.01571,0.05003]}],"total_contact_groups":1},"final_pose_error":0.03853,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.48825,-0.01584,0.05001],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":520.62832,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.48553,-0.01378,0.24977],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.17095,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_insert","tcp_end":[0.48097,-0.01378,0.21003],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47825,-0.01456,0.19939],"object_pos_start":[0.48553,-0.01378,0.24977],"object_to_goal_dist_end":0.12222,"object_to_goal_dist_start":0.17095,"object_z_max":0.24977,"peak_contact_force":0.0,"phase_name":"align_at_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_insert","tcp_end":[0.47782,-0.01455,0.15939],"tcp_start":[0.48097,-0.01378,0.21003],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":819.0,"n_steps_budget":1000.0,"object_pos_end":[0.48844,-0.0159,0.09],"object_pos_start":[0.47825,-0.01456,0.19939],"object_to_goal_dist_end":0.02205,"object_to_goal_dist_start":0.12222,"object_z_max":0.19939,"peak_contact_force":460.93836,"phase_name":"insert_downward","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":421.0,"raw_peak_contact_force":520.62832,"subtask_id":"insertion_progress","tcp_end":[0.48825,-0.01584,0.05001],"tcp_start":[0.47782,-0.01455,0.15939],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.6,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_entry.align_speed":0.02676,"align_at_entry.align_tolerance":0.0025,"approach_above_socket.approach_speed":0.03693,"approach_above_socket.approach_z_offset":0.14425,"insert_downward.insert_distance":0.06067,"insert_downward.insert_speed":0.02092},"optimized_scores":{"best_composite_score":0.2502,"best_fitness_score":0.5802,"best_task_score":0.81005},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":481.0,"contact_point_centroid":[0.46894,-0.02816,0.04992],"force_p95":487.94311,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":509.62308,"mean_force":455.78533,"phase_index":2.0,"phase_name":"insert_downward","phase_type":"insert","tcp_position_centroid":[0.46984,-0.02061,0.04991]}],"total_contact_groups":1},"final_pose_error":0.03172,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.47507,-0.02084,0.04996],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":509.62308,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.47462,-0.01742,0.27254],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.19499,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_insert","tcp_end":[0.47006,-0.01741,0.2328],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46642,-0.01855,0.21761],"object_pos_start":[0.47462,-0.01742,0.27254],"object_to_goal_dist_end":0.14286,"object_to_goal_dist_start":0.19499,"object_z_max":0.27254,"peak_contact_force":0.0,"phase_name":"align_at_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_insert","tcp_end":[0.466,-0.01854,0.17761],"tcp_start":[0.47006,-0.01741,0.2328],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.4749,-0.02089,0.08996],"object_pos_start":[0.46642,-0.01855,0.21761],"object_to_goal_dist_end":0.03414,"object_to_goal_dist_start":0.14286,"object_z_max":0.21761,"peak_contact_force":433.58924,"phase_name":"insert_downward","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":481.0,"raw_peak_contact_force":509.62308,"subtask_id":"insertion_progress","tcp_end":[0.47507,-0.02084,0.04996],"tcp_start":[0.466,-0.01854,0.17761],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.49231,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_at_entry.align_speed":0.02211,"align_at_entry.align_tolerance":0.01985,"approach_above_socket.approach_speed":0.08039,"approach_above_socket.approach_z_offset":0.09578,"insert_downward.insert_distance":0.03036,"insert_downward.insert_speed":0.01534},"optimized_scores":{"best_composite_score":0.2473,"best_fitness_score":0.5773,"best_task_score":0.86762},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[],"total_contact_groups":0},"final_pose_error":0.00984,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.53043,0.00081,0.05811],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":0.0,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.53351,0.00077,0.22283],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.14671,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_above_socket","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_insert","tcp_end":[0.52892,0.00077,0.18309],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":180.0,"n_steps_budget":1000.0,"object_pos_end":[0.53141,0.00083,0.13905],"object_pos_start":[0.53351,0.00077,0.22283],"object_to_goal_dist_end":0.06689,"object_to_goal_dist_start":0.14671,"object_z_max":0.22283,"peak_contact_force":0.0,"phase_name":"align_at_entry","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_pre_insert","tcp_end":[0.53082,0.00082,0.09906],"tcp_start":[0.52892,0.00077,0.18309],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":152.0,"n_steps_budget":1000.0,"object_pos_end":[0.53149,0.00082,0.09809],"object_pos_start":[0.53141,0.00083,0.13905],"object_to_goal_dist_end":0.03632,"object_to_goal_dist_start":0.06689,"object_z_max":0.13905,"peak_contact_force":0.0,"phase_name":"insert_downward","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion_progress","tcp_end":[0.53043,0.00081,0.05811],"tcp_start":[0.53082,0.00082,0.09906],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":false}]}
```