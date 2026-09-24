## Search State

- **Seed**: 4
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → insert → retract | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 1 | 0.6111 | 0.89 | ✅ accepted |

**Proposal policy**: task_score is 0.89 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5354444884457894, 0.000906204225148928, 0.08]
- Frozen socket pose: [0.5354444884457894, 0.000906204225148928, 0.025] (static fixture for this episode)
- Goal object position: (0.5354444884457894, 0.000906204225148928, 0.025)
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
  frozen_task_target: [0.5354, 0.0009, 0.08]
  frozen_socket_position: [0.5354, 0.0009, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5354444884457894, 0.000906204225148928, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5354444884457894, 0.000906204225148928, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.894, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.5354444884457894, 0.000906204225148928, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5354444884457894, 0.000906204225148928, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.611) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_standoff
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: reach_insertion
  offset:
  - 0.0
  - 0.0
  - -0.05
  weight: 0.7
phases:
- id: approach_1
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
    - 0.05
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  subtask_id: reach_standoff
- id: insert_1
  type: insert
  generator: impedance_motion
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
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.1
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: reach_insertion
- id: retract_1
  type: retract
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

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.05]
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings: none
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.1
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.611
- **task_score** (E): 0.894
- **fitness_score**: 0.691  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.080

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.1640 |
| insert_1 | 1.00 | 1.00 | 0.0892 |
| retract_1 | 1.00 | 0.00 | 0.1193 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.516, 0.004, 0.138) | (0.504, -0.000, 0.340)→(0.517, 0.004, 0.178) | 0.260→0.102 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 1.00 / step_budget | (0.516, 0.004, 0.138)→(0.517, 0.004, 0.049) | (0.517, 0.004, 0.178)→(0.517, 0.004, 0.089) | 0.102→0.027 | 1.00 / 1.000 | 292.309 | 292.309 |
| retract_1 | retract | 1.00 / step_budget | (0.517, 0.004, 0.049)→(0.518, 0.004, 0.169) | (0.517, 0.004, 0.089)→(0.519, 0.004, 0.208) | 0.027→0.131 | 0.00 / 0.000 | 0.000 | 73.835 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.945
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.945
- phase_score: 0.669
- phase_breakdown.reach_standoff_score: 0.744
- phase_breakdown.reach_insertion_score: 0.637

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.779
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.945
- **Median Q (composite search score)**: 0.569
- **K-run variance**: 0.0039
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 17.0
- **Final σ (mean)**: 0.033


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9dafd9212fa57d4ed6b507cf5ac09991f034abfc2fa41dbd37d7c702246c6284`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ab22a59b7a3c9c0e28c9743e3882e986d7ba7a97654ba206ec4bffa38a24163`; realized-scene SHA-256: `03ab66c73c39e70252b7764557f10cd17ad49cc08b28e1c3cb573bd8dcea88ba`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.53544,0.00091,0.025]},{"name":"target","value":[0.53544,0.00091,0.025]},{"name":"socket","value":[0.53544,0.00091,0.025]},{"name":"goal","value":[0.53544,0.00091,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.00091,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.53544,0.00091,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95294,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"insert_1.insertion_depth":0.03919},"optimized_scores":{"best_composite_score":0.5693,"best_fitness_score":0.6493,"best_task_score":0.87202},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.54574,0.00073,0.0498],"force_p95":174.20002,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":176.38924,"mean_force":154.49703,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.53075,0.00081,0.04977]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.54575,0.00088,0.04974],"force_p95":77.09139,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":85.06352,"mean_force":29.97794,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53076,0.0008,0.04965]}],"total_contact_groups":2},"final_pose_error":0.01222,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.53544,0.00091,0.025],"final_tcp_position":[0.53205,0.00085,0.16826],"realised_fixture_position":[0.53544,0.00091,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.53544,0.00091,0.08]},"peak_contact_force":176.38924,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.52994,0.00079,0.17784],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.10232,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.52946,0.00079,0.13784],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":280.0,"n_steps_budget":630.0,"object_pos_end":[0.53126,0.00082,0.08944],"object_pos_start":[0.52994,0.00079,0.17784],"object_to_goal_dist_end":0.03267,"object_to_goal_dist_start":0.10232,"object_z_max":0.17784,"peak_contact_force":176.38924,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":2.0,"raw_peak_contact_force":176.38924,"subtask_id":"reach_insertion","tcp_end":[0.5308,0.00081,0.04944],"tcp_start":[0.52946,0.00079,0.13784],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.53299,0.00086,0.20825],"object_pos_start":[0.53126,0.00082,0.08944],"object_to_goal_dist_end":0.13242,"object_to_goal_dist_start":0.03267,"object_z_max":0.20812,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":9.0,"raw_peak_contact_force":85.06352,"tcp_end":[0.53205,0.00085,0.16826],"tcp_start":[0.5308,0.00081,0.04944],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1cd3bcde9ecee8889beeec63bba6949652ce08dd1277aacff8bc717cc59ca677`; realized-scene SHA-256: `3a693f0216d44408acf55cd4ed5e7511210ea06892083b191557e74fdeb42bf8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.5244,0.02464,0.025]},{"name":"target","value":[0.5244,0.02464,0.025]},{"name":"socket","value":[0.5244,0.02464,0.025]},{"name":"goal","value":[0.5244,0.02464,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.02464,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.5244,0.02464,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95294,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"insert_1.insertion_depth":0.03967},"optimized_scores":{"best_composite_score":0.56466,"best_fitness_score":0.64466,"best_task_score":0.86532},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":3.0,"contact_point_centroid":[0.53488,0.02496,0.04974],"force_p95":220.95681,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":225.24725,"mean_force":181.30705,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51992,0.02411,0.04966]},{"body_a":"attachment","body_b":"peg_socket","contact_count":8.0,"contact_point_centroid":[0.53498,0.02498,0.04966],"force_p95":73.34484,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.99795,"mean_force":33.94641,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52001,0.02411,0.04949]}],"total_contact_groups":2},"final_pose_error":0.01203,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.5244,0.02464,0.025],"final_tcp_position":[0.52106,0.02443,0.16845],"realised_fixture_position":[0.5244,0.02464,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.5244,0.02464,0.08]},"peak_contact_force":225.24725,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.51975,0.02259,0.17811],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1026,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.51928,0.02256,0.13811],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":284.0,"n_steps_budget":630.0,"object_pos_end":[0.52045,0.02414,0.08926],"object_pos_start":[0.51975,0.02259,0.17811],"object_to_goal_dist_end":0.03297,"object_to_goal_dist_start":0.1026,"object_z_max":0.17811,"peak_contact_force":225.24725,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":225.24725,"subtask_id":"reach_insertion","tcp_end":[0.52,0.02412,0.04927],"tcp_start":[0.51928,0.02256,0.13811],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.52198,0.02448,0.20844],"object_pos_start":[0.52045,0.02414,0.08926],"object_to_goal_dist_end":0.13258,"object_to_goal_dist_start":0.03297,"object_z_max":0.20831,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":8.0,"raw_peak_contact_force":79.99795,"tcp_end":[0.52106,0.02443,0.16845],"tcp_start":[0.52,0.02412,0.04927],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `3a12d7f15d1e6c6a0af002631f15bc7a534f5434829fc9db32b3974b909f1f84`; realized-scene SHA-256: `72d0fc56eb607f902ea78d3570decababa6da9acffffae87b8c65460ac3ff15e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50305,-0.01254,0.025]},{"name":"target","value":[0.50305,-0.01254,0.025]},{"name":"socket","value":[0.50305,-0.01254,0.025]},{"name":"goal","value":[0.50305,-0.01254,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.01254,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50305,-0.01254,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.95294,"average_solve_count":85.0,"average_success_count":85.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"insert_1.insertion_depth":0.04047},"optimized_scores":{"best_composite_score":0.69939,"best_fitness_score":0.77939,"best_task_score":0.94477},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.51415,-0.01273,0.04958],"force_p95":463.48743,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":475.28922,"mean_force":324.92354,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49916,-0.01236,0.04931]},{"body_a":"attachment","body_b":"peg_socket","contact_count":9.0,"contact_point_centroid":[0.51465,-0.01276,0.04958],"force_p95":56.25836,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.44258,"mean_force":25.76889,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49967,-0.01237,0.0493]}],"total_contact_groups":2},"final_pose_error":0.01164,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50305,-0.01254,0.025],"final_tcp_position":[0.49983,-0.01249,0.16882],"realised_fixture_position":[0.50305,-0.01254,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50305,-0.01254,0.08]},"peak_contact_force":475.28922,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":503.0,"n_steps_budget":1000.0,"object_pos_end":[0.50009,-0.01148,0.17927],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.09993,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.49963,-0.01147,0.13927],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":297.0,"n_steps_budget":630.0,"object_pos_end":[0.49995,-0.01236,0.08887],"object_pos_start":[0.50009,-0.01148,0.17927],"object_to_goal_dist_end":0.01522,"object_to_goal_dist_start":0.09993,"object_z_max":0.17927,"peak_contact_force":475.28922,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":10.0,"raw_peak_contact_force":475.28922,"subtask_id":"reach_insertion","tcp_end":[0.4996,-0.01236,0.04887],"tcp_start":[0.49963,-0.01147,0.13927],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.50063,-0.0125,0.20881],"object_pos_start":[0.49995,-0.01236,0.08887],"object_to_goal_dist_end":0.12941,"object_to_goal_dist_start":0.01522,"object_z_max":0.20868,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":9.0,"raw_peak_contact_force":56.44258,"tcp_end":[0.49983,-0.01249,0.16882],"tcp_start":[0.4996,-0.01236,0.04887],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```