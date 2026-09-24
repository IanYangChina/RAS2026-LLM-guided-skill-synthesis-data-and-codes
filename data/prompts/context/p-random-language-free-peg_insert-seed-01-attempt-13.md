## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → insert | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2964 | 0.89 | ❌ rejected |
| 12 | approach → align → push → align | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.2713 | 0.84 | ❌ rejected |
| 11 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |
| 10 | approach → align → insert | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.7475 | 0.96 | ✅ accepted |
| 9 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.7475 | 0.96 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `8f814a9d9dd9825bee110b06b2d985dbb0aa82505ba300f6022b2e21e7c15f67`
- Frozen object start: [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]
- Frozen task target: [0.5009457299760205, 0.03603709570607482, 0.08]
- Frozen socket pose: [0.5009457299760205, 0.03603709570607482, 0.025] (static fixture for this episode)
- Goal object position: (0.5009457299760205, 0.03603709570607482, 0.025)
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
  frozen_task_target: [0.5009, 0.036, 0.08]
  frozen_socket_position: [0.5009, 0.036, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5039660180420721, -2.3990369582946034e-19, 0.34030658323767055]}
  frozen_targets: {'socket_entry': [0.5009457299760205, 0.03603709570607482, 0.08]}
  frozen_fixtures: {'peg_socket': [0.5009457299760205, 0.03603709570607482, 0.025]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: 8f814a9d9dd9825bee110b06b2d985dbb0aa82505ba300f6022b2e21e7c15f67

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.957, which indicates the subtask decomposition is already effective.
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
| `goal` | offset from task goal position (0.5009457299760205, 0.03603709570607482, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (0.5009457299760205, 0.03603709570607482, 0.025) | approach/contact targets near fixture |

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

## Current Skill (Q=0.296) — your mutation base

```yaml
skill: peg_insert
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01

```

## Design Metrics

- **Composite score**: 0.296
- **task_score** (E): 0.890
- **fitness_score**: 0.626  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.1292 |
| align_1 | 1.00 | 0.00 | 0.0941 |
| insert_1 | 0.00 | 1.00 | 0.0327 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.481, -0.000, 0.176) | (0.504, -0.000, 0.340)→(0.482, -0.000, 0.216) | 0.260→0.140 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_1 | align | 1.00 / step_budget | (0.481, -0.000, 0.176)→(0.488, 0.003, 0.082) | (0.482, -0.000, 0.216)→(0.488, 0.003, 0.122) | 0.140→0.049 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 0.00 / guard_failure | (0.488, 0.003, 0.082)→(0.483, 0.002, 0.050) | (0.488, 0.003, 0.122)→(0.483, 0.002, 0.090) | 0.049→0.030 | 1.00 / 1.000 | 87.183 | 87.183 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.930
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.930
- phase_score: 0.523
- phase_breakdown.pre_insert_score: 0.604
- phase_breakdown.insertion_depth_score: 0.488

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.686
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.930
- **Median Q (composite search score)**: 0.287
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.546


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `4865da8c78c0d766958c01aea638a491e86f6ad380c20093f3e1db2b764e8196`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `66fcf22dcc3bcf7c938cd95aa7e21cfd304510ff9d22bdf68d85d724037825f3`; realized-scene SHA-256: `8f814a9d9dd9825bee110b06b2d985dbb0aa82505ba300f6022b2e21e7c15f67`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.50095,0.03604,0.025]},{"name":"target","value":[0.50095,0.03604,0.025]},{"name":"socket","value":[0.50095,0.03604,0.025]},{"name":"goal","value":[0.50095,0.03604,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.03604,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.50095,0.03604,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77273,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00761,"align_1.lateral_offset_y":-0.00926,"approach_1.approach_speed":0.04404,"approach_1.approach_z":0.14944,"insert_1.push_distance":0.08413,"insert_1.push_speed":0.00717},"optimized_scores":{"best_composite_score":0.2873,"best_fitness_score":0.6173,"best_task_score":0.87662},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.5143,0.0305,0.04993],"force_p95":75.58488,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.58488,"mean_force":75.58488,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49932,0.02961,0.05003]}],"total_contact_groups":1},"final_pose_error":0.05443,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.49933,0.02962,0.0499],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":75.58488,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.49829,0.03365,0.21745],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.14152,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_insert","tcp_end":[0.49784,0.03362,0.17745],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":584.0,"n_steps_budget":630.0,"object_pos_end":[0.50458,0.02703,0.12185],"object_pos_start":[0.49829,0.03365,0.21745],"object_to_goal_dist_end":0.05003,"object_to_goal_dist_start":0.14152,"object_z_max":0.21745,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_insert","tcp_end":[0.50412,0.027,0.08185],"tcp_start":[0.49784,0.03362,0.17745],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.49978,0.02965,0.0899],"object_pos_start":[0.50458,0.02703,0.12185],"object_to_goal_dist_end":0.03126,"object_to_goal_dist_start":0.05003,"object_z_max":0.12185,"peak_contact_force":75.58488,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":75.58488,"subtask_id":"insertion_depth","tcp_end":[0.49933,0.02962,0.0499],"tcp_start":[0.50412,0.027,0.08185],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `93acd10de345eed07b6dc6c2bbc440a51ca07353b2db3e19ce9d53254358a6c5`; realized-scene SHA-256: `4c08395e36e43245f6092dd2e3719288cb8e1800970c3a851b5dc162486241ee`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.48093,-0.01612,0.025]},{"name":"target","value":[0.48093,-0.01612,0.025]},{"name":"socket","value":[0.48093,-0.01612,0.025]},{"name":"goal","value":[0.48093,-0.01612,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.01612,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48093,-0.01612,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.55172,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00996,"align_1.lateral_offset_y":0.00964,"approach_1.approach_speed":0.02416,"approach_1.approach_z":0.1472,"insert_1.push_distance":0.09955,"insert_1.push_speed":0.01155},"optimized_scores":{"best_composite_score":0.35564,"best_fitness_score":0.68564,"best_task_score":0.93021},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.4962,-0.01006,0.04993],"force_p95":72.74383,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.74383,"mean_force":72.74383,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.48128,-0.00953,0.05003]}],"total_contact_groups":1},"final_pose_error":0.06976,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.48127,-0.00954,0.0499],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":72.74383,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.4797,-0.01494,0.21667],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.13897,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_insert","tcp_end":[0.47927,-0.01494,0.17667],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":585.0,"n_steps_budget":630.0,"object_pos_end":[0.48694,-0.00705,0.12213],"object_pos_start":[0.4797,-0.01494,0.21667],"object_to_goal_dist_end":0.04467,"object_to_goal_dist_start":0.13897,"object_z_max":0.21667,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_insert","tcp_end":[0.48649,-0.00705,0.08213],"tcp_start":[0.47927,-0.01494,0.17667],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.48171,-0.00955,0.0899],"object_pos_start":[0.48694,-0.00705,0.12213],"object_to_goal_dist_end":0.02288,"object_to_goal_dist_start":0.04467,"object_z_max":0.12213,"peak_contact_force":72.74383,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":72.74383,"subtask_id":"insertion_depth","tcp_end":[0.48127,-0.00954,0.0499],"tcp_start":[0.48649,-0.00705,0.08213],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e4487702be29fc714aef807905297ccb2e376a648cd6f3407ac6d1ceee44c37e`; realized-scene SHA-256: `71c7bcc0411146bb1295ec697eba8abcb9eaa89bf878970856d0e0a8305cc755`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50397,-0.0,0.34031]},{"name":"task_object","value":[0.50397,-0.0,0.34031]},{"name":"fixture","value":[0.46685,-0.02106,0.025]},{"name":"target","value":[0.46685,-0.02106,0.025]},{"name":"socket","value":[0.46685,-0.02106,0.025]},{"name":"goal","value":[0.46685,-0.02106,0.025]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.02106,0.025]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.50397,-0.0,0.34031]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.46685,-0.02106,0.08]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.47283,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00977,"align_1.lateral_offset_y":0.01,"approach_1.approach_speed":0.02157,"approach_1.approach_z":0.14326,"insert_1.push_distance":0.09955,"insert_1.push_speed":0.01532},"optimized_scores":{"best_composite_score":0.24631,"best_fitness_score":0.57631,"best_task_score":0.86343},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.48219,-0.01398,0.04997],"force_p95":113.22069,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":113.22069,"mean_force":113.22069,"phase_index":2.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.46721,-0.01421,0.05009]}],"total_contact_groups":1},"final_pose_error":0.06986,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.46685,-0.02106,0.025],"final_tcp_position":[0.4672,-0.01422,0.04997],"realised_fixture_position":[0.46685,-0.02106,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.46685,-0.02106,0.08]},"peak_contact_force":113.22069,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.46652,-0.01956,0.2129],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.13844,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_insert","tcp_end":[0.4661,-0.01955,0.1729],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":555.0,"n_steps_budget":600.0,"object_pos_end":[0.47277,-0.01163,0.12245],"object_pos_start":[0.46652,-0.01956,0.2129],"object_to_goal_dist_end":0.05176,"object_to_goal_dist_start":0.13844,"object_z_max":0.2129,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_insert","tcp_end":[0.47234,-0.01162,0.08246],"tcp_start":[0.4661,-0.01955,0.1729],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":212.0,"n_steps_budget":1000.0,"object_pos_end":[0.46762,-0.01423,0.08997],"object_pos_start":[0.47277,-0.01163,0.12245],"object_to_goal_dist_end":0.03674,"object_to_goal_dist_start":0.05176,"object_z_max":0.12245,"peak_contact_force":113.22069,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":113.22069,"subtask_id":"insertion_depth","tcp_end":[0.4672,-0.01422,0.04997],"tcp_start":[0.47234,-0.01162,0.08246],"tcp_to_object_dist_end":0.04,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```