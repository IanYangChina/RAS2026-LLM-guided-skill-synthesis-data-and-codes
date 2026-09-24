## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → push | linear_cartesian | impedance_motion | position_control | admittance_control | pose_tolerance | pose_tolerance | 7 | 0.6438 | 0.99 | ✅ accepted |
| 11 | approach → push | linear_cartesian | impedance_motion | position_control | admittance_control | pose_tolerance | pose_tolerance | 7 | 0.6409 | 0.99 | ✅ accepted |
| 10 | approach → insert | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | force_exceeded | 8 | -0.0906 | 0.47 | ❌ rejected |
| 9 | approach → insert | linear_cartesian | impedance_motion | position_control | admittance_control | pose_tolerance | pose_tolerance | 7 | 0.2434 | 0.96 | ❌ rejected |
| 8 | approach → insert | linear_cartesian | impedance_motion | position_control | admittance_control | pose_tolerance | pose_tolerance | 7 | 0.2967 | 0.99 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.99). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.994, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.644) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_standoff
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.3
- id: insert_goal
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
    - 0.08
    tolerance: 0.04
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_standoff
- id: push_insert
  type: push
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.04
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.055
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lateral_offset_x:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.04
      - 0.04
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: insert_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.08], tolerance=0.04
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_insert** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.04, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.644
- **task_score** (E): 0.994
- **fitness_score**: 0.994  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.350

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.1093 |
| push_insert | 1.00 | 1.00 | 0.1227 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, -0.008, 0.197) | (0.504, -0.000, 0.340)→(0.502, -0.008, 0.237) | 0.260→0.161 | 0.00 / 0.000 | 0.000 | 0.000 |
| push_insert | push | 1.00 / step_budget | (0.497, -0.008, 0.197)→(0.504, 0.001, 0.080) | (0.502, -0.008, 0.237)→(0.505, 0.002, 0.120) | 0.161→0.041 | 1.00 / 1.000 | 396.480 | 515.393 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.997
- alignment_error: None
- force_efficiency: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.997
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.997
- **Median Q (composite search score)**: 0.643
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.472


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13514,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.02101,"approach_1.lateral_offset_y":0.02361,"approach_1.speed":0.06934,"push_insert.insertion_depth":0.04193,"push_insert.lateral_offset_x":-0.01688,"push_insert.lateral_offset_y":0.01625,"push_insert.speed":0.03145},"optimized_scores":{"best_composite_score":0.64683,"best_fitness_score":0.99683,"best_task_score":0.99683},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":421.0,"contact_point_centroid":[0.49604,0.01158,0.07986],"force_p95":414.36144,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":548.19466,"mean_force":403.91856,"phase_index":1.0,"phase_name":"push_insert","phase_type":"push","tcp_position_centroid":[0.50256,-0.00067,0.07982]}],"total_contact_groups":1},"final_pose_error":0.04368,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.50598,-0.00079,0.08007],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"peak_contact_force":548.19466,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":125.0,"n_steps_budget":1000.0,"object_pos_end":[0.52587,0.00357,0.23781],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15996,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.52132,0.00356,0.19807],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":652.0,"n_steps_budget":1000.0,"object_pos_end":[0.50488,-0.0008,0.12005],"object_pos_start":[0.52587,0.00357,0.23781],"object_to_goal_dist_end":0.04036,"object_to_goal_dist_start":0.15996,"object_z_max":0.23781,"peak_contact_force":405.11729,"phase_name":"push_insert","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":421.0,"raw_peak_contact_force":548.19466,"subtask_id":"insert_goal","tcp_end":[0.50598,-0.00079,0.08007],"tcp_start":[0.52132,0.00356,0.19807],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.73298,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.01355,"approach_1.lateral_offset_y":-0.01904,"approach_1.speed":0.02794,"push_insert.insertion_depth":0.04658,"push_insert.lateral_offset_x":-0.01085,"push_insert.lateral_offset_y":-0.03797,"push_insert.speed":0.03868},"optimized_scores":{"best_composite_score":0.64276,"best_fitness_score":0.99276,"best_task_score":0.99276},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":420.0,"contact_point_centroid":[0.49026,-0.0048,0.07986],"force_p95":432.374,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":576.06805,"mean_force":404.987,"phase_index":1.0,"phase_name":"push_insert","phase_type":"push","tcp_position_centroid":[0.49673,0.00182,0.07976]}],"total_contact_groups":1},"final_pose_error":0.04758,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.4997,0.00157,0.07989],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":576.06805,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":136.0,"n_steps_budget":1000.0,"object_pos_end":[0.51361,0.01167,0.23841],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.15942,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.50908,0.01164,0.19866],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":653.0,"n_steps_budget":1000.0,"object_pos_end":[0.4995,0.00153,0.11989],"object_pos_start":[0.51361,0.01167,0.23841],"object_to_goal_dist_end":0.03993,"object_to_goal_dist_start":0.15942,"object_z_max":0.23841,"peak_contact_force":391.75999,"phase_name":"push_insert","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":420.0,"raw_peak_contact_force":576.06805,"subtask_id":"insert_goal","tcp_end":[0.4997,0.00157,0.07989],"tcp_start":[0.50908,0.01164,0.19866],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99435,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":-0.03356,"approach_1.lateral_offset_y":-0.039,"approach_1.speed":0.04432,"push_insert.insertion_depth":0.03005,"push_insert.lateral_offset_x":0.03455,"push_insert.lateral_offset_y":0.03116,"push_insert.speed":0.03217},"optimized_scores":{"best_composite_score":0.64187,"best_fitness_score":0.99187,"best_task_score":0.99187},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":302.0,"contact_point_centroid":[0.51883,0.00368,0.07987],"force_p95":407.24433,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":421.9158,"mean_force":388.44506,"phase_index":1.0,"phase_name":"push_insert","phase_type":"push","tcp_position_centroid":[0.50387,0.00306,0.08052]},{"body_a":"attachment","body_b":"peg_socket","contact_count":50.0,"contact_point_centroid":[0.51065,0.0141,0.07963],"force_p95":222.26272,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":244.32466,"mean_force":102.12652,"phase_index":1.0,"phase_name":"push_insert","phase_type":"push","tcp_position_centroid":[0.50114,0.00258,0.07949]}],"total_contact_groups":2},"final_pose_error":0.03409,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.50675,0.00368,0.08089],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":421.9158,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":145.0,"n_steps_budget":1000.0,"object_pos_end":[0.46566,-0.04016,0.23362],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.16246,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.46114,-0.04012,0.19388],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":589.0,"n_steps_budget":1000.0,"object_pos_end":[0.5095,0.00384,0.1208],"object_pos_start":[0.46566,-0.04016,0.23362],"object_to_goal_dist_end":0.04206,"object_to_goal_dist_start":0.16246,"object_z_max":0.23362,"peak_contact_force":392.56153,"phase_name":"push_insert","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":352.0,"raw_peak_contact_force":421.9158,"subtask_id":"insert_goal","tcp_end":[0.50675,0.00368,0.08089],"tcp_start":[0.46114,-0.04012,0.19388],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```