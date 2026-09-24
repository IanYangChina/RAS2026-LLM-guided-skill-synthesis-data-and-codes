## Search State

- **Seed**: 0
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → insert | linear_cartesian | impedance_motion | position_control | admittance_control | pose_tolerance | pose_tolerance | 5 | 0.5248 | 0.95 | ✅ accepted |
| 1 | approach → insert | linear_cartesian | impedance_motion | position_control | admittance_control | time_limit | time_limit | 5 | 0.5213 | 0.95 | ❌ rejected |
| 0 | approach → insert | linear_cartesian | impedance_motion | position_control | admittance_control | pose_tolerance | pose_tolerance | 5 | 0.5130 | 0.95 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (0.95). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.955, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.525) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
subtasks:
- id: reach_standoff
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: insert_goal
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
    - 0.1
    tolerance: 0.01
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
  subtask_id: reach_standoff
- id: insert_1
  type: insert
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
      distance: 0.05
      axis: channel_axis
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.07
      default: 0.05
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
  subtask_id: insert_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **insert_1** (`insert`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.05, mode=replace_offset_projection, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)

## Design Metrics

- **Composite score**: 0.525
- **task_score** (E): 0.955
- **fitness_score**: 0.775  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 0.00 | 0.1115 |
| insert_1 | 1.00 | 1.00 | 0.1386 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.500, -0.001, 0.189) | (0.504, -0.000, 0.340)→(0.505, -0.001, 0.229) | 0.260→0.149 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_1 | insert | 1.00 / step_budget | (0.500, -0.001, 0.189)→(0.497, 0.006, 0.052) | (0.505, -0.001, 0.229)→(0.503, 0.006, 0.091) | 0.149→0.018 | 1.00 / 1.333 | 359.201 | 536.514 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.984
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.984
- phase_score: 0.683
- phase_breakdown.insert_goal_score: 0.641
- phase_breakdown.reach_standoff_score: 0.780

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.803
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.984
- **Median Q (composite search score)**: 0.540
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.202


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89831,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.00209,"approach_1.lateral_offset_y":0.02049,"insert_1.insertion_depth":0.05019,"insert_1.lateral_offset_x":-0.01347,"insert_1.lateral_offset_y":0.01341},"optimized_scores":{"best_composite_score":0.55325,"best_fitness_score":0.80325,"best_task_score":0.98407},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":83.0,"contact_point_centroid":[0.5124,-0.00424,0.0498],"force_p95":424.03355,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":434.0963,"mean_force":376.38407,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49752,-0.00419,0.05144]},{"body_a":"attachment","body_b":"peg_socket","contact_count":10.0,"contact_point_centroid":[0.49914,0.01176,0.07994],"force_p95":189.26326,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":204.93623,"mean_force":114.51392,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.4979,-0.00291,0.07937]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.48095,-0.00414,0.0542],"force_p95":44.83986,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.28469,"mean_force":40.83632,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49583,-0.00414,0.05232]}],"total_contact_groups":3},"final_pose_error":0.022,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51096,-0.01842,0.025],"final_tcp_position":[0.49836,-0.00421,0.05178],"realised_fixture_position":[0.51096,-0.01842,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51096,-0.01842,0.08]},"peak_contact_force":434.0963,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":355.0,"n_steps_budget":780.0,"object_pos_end":[0.51322,0.0018,0.22847],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.14907,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.50863,0.00179,0.18873],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":510.0,"n_steps_budget":990.0,"object_pos_end":[0.50336,-0.00421,0.09147],"object_pos_start":[0.51322,0.0018,0.22847],"object_to_goal_dist_end":0.01267,"object_to_goal_dist_start":0.14907,"object_z_max":0.22847,"peak_contact_force":382.28066,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":95.0,"raw_peak_contact_force":434.0963,"subtask_id":"insert_goal","tcp_end":[0.49836,-0.00421,0.05178],"tcp_start":[0.50863,0.00179,0.18873],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90164,"average_solve_count":61.0,"average_success_count":61.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":-0.00119,"approach_1.lateral_offset_y":-0.03772,"insert_1.insertion_depth":0.05476,"insert_1.lateral_offset_x":0.00186,"insert_1.lateral_offset_y":-0.00689},"optimized_scores":{"best_composite_score":0.48094,"best_fitness_score":0.73094,"best_task_score":0.91908},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":31.0,"contact_point_centroid":[0.51628,0.02556,0.04931],"force_p95":578.50277,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":602.91265,"mean_force":419.72032,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50143,0.02534,0.05069]},{"body_a":"attachment","body_b":"peg_socket","contact_count":224.0,"contact_point_centroid":[0.50679,0.00601,0.07986],"force_p95":385.66067,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":435.6936,"mean_force":353.47373,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49926,0.01886,0.08075]}],"total_contact_groups":2},"final_pose_error":0.02645,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.50095,0.03604,0.025],"final_tcp_position":[0.50155,0.02542,0.05139],"realised_fixture_position":[0.50095,0.03604,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.50095,0.03604,0.08]},"peak_contact_force":602.91265,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":345.0,"n_steps_budget":780.0,"object_pos_end":[0.50149,-0.0015,0.22919],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.1492,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.4969,-0.00151,0.18945],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":651.0,"n_steps_budget":1000.0,"object_pos_end":[0.50718,0.02554,0.09099],"object_pos_start":[0.50149,-0.0015,0.22919],"object_to_goal_dist_end":0.02872,"object_to_goal_dist_start":0.1492,"object_z_max":0.22919,"peak_contact_force":366.23209,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":255.0,"raw_peak_contact_force":602.91265,"subtask_id":"insert_goal","tcp_end":[0.50155,0.02542,0.05139],"tcp_start":[0.4969,-0.00151,0.18945],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89831,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.lateral_offset_x":0.01751,"approach_1.lateral_offset_y":0.01233,"insert_1.insertion_depth":0.04691,"insert_1.lateral_offset_x":0.01547,"insert_1.lateral_offset_y":0.01145},"optimized_scores":{"best_composite_score":0.54028,"best_fitness_score":0.79028,"best_task_score":0.9615},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":60.0,"contact_point_centroid":[0.50698,-0.00458,0.04982],"force_p95":568.97525,"geom_a":"peg_tip","geom_b":"socket_base","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":572.53324,"mean_force":441.93787,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49211,-0.00458,0.05164]},{"body_a":"attachment","body_b":"peg_socket","contact_count":71.0,"contact_point_centroid":[0.51098,-0.00463,0.07999],"force_p95":404.84749,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":407.25214,"mean_force":324.85573,"phase_index":1.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49216,-0.00457,0.05189]}],"total_contact_groups":2},"final_pose_error":0.01936,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48093,-0.01612,0.025],"final_tcp_position":[0.49202,-0.00458,0.05194],"realised_fixture_position":[0.48093,-0.01612,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48093,-0.01612,0.08]},"peak_contact_force":572.53324,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":345.0,"n_steps_budget":780.0,"object_pos_end":[0.50033,-0.00335,0.2292],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.14924,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_standoff","tcp_end":[0.49574,-0.00335,0.18946],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":502.0,"n_steps_budget":990.0,"object_pos_end":[0.49763,-0.00459,0.09155],"object_pos_start":[0.50033,-0.00335,0.2292],"object_to_goal_dist_end":0.01265,"object_to_goal_dist_start":0.14924,"object_z_max":0.2292,"peak_contact_force":329.09032,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":131.0,"raw_peak_contact_force":572.53324,"subtask_id":"insert_goal","tcp_end":[0.49202,-0.00458,0.05194],"tcp_start":[0.49574,-0.00335,0.18946],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```