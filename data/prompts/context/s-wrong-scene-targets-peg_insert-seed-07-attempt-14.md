## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | descend → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | time_limit | pose_tolerance | force_exceeded | 7 | 0.6807 | 0.98 | ❌ rejected |
| 13 | descend → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | time_limit | time_limit | force_exceeded | 6 | 1.2313 | 0.98 | ✅ accepted |
| 12 | descend → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.5534 | 0.98 | ❌ rejected |
| 11 | descend → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.5534 | 0.98 | ✅ accepted |
| 10 | descend → align → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.2177 | 0.97 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.98). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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
- Frozen realised-scene SHA-256: `f2535c6a7dfc5a3ca3c25224b40d7fd8d1111b06ec904a3c56a54673c2686a85`
- Frozen object start: [0.5100076373283727, 0.031777104077566044, 0.08]
- Frozen task target: [0.5100076373283727, 0.031777104077566044, 0.025]
- Frozen socket pose: [0.5, 0.0, 0.3] (static fixture for this episode)
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5100076373283727, 0.031777104077566044, 0.08)
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
  frozen_task_target: [0.51, 0.0318, 0.08]
  frozen_socket_position: [0.51, 0.0318, 0.025]
  socket_state: static_frozen
  frozen_object_starts: {'peg': [0.5100076373283727, 0.031777104077566044, 0.08]}
  frozen_targets: {'socket_entry': [0.5100076373283727, 0.031777104077566044, 0.025]}
  frozen_fixtures: {'peg_socket': [0.5, 0.0, 0.3]}
  insertion_axis: [0, 0, -1]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  hole_depth_m: 0.05
  force_scale_n: 5
  realized_scene_sha256: f2535c6a7dfc5a3ca3c25224b40d7fd8d1111b06ec904a3c56a54673c2686a85

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.976, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5100076373283727, 0.031777104077566044, 0.08) | approach/contact targets near object start |
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

## Current Skill (Q=0.681) — your mutation base

```yaml
skill: peg_insert
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_insert_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - -0.05
  weight: 0.3
- id: insertion
  anchor: object
  offset:
  - 0.0
  - 0.0
  - -0.055
  weight: 0.7
phases:
- id: approach_to_entry
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - -0.05
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.07
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_insert_approach
- id: align_lateral
  type: align
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    entity: tcp
    offset:
    - 0.0
    - 0.0
    - -0.055
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
    lateral_offset_x:
      type: scalar
      range:
      - -0.015
      - 0.015
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    lateral_offset_y:
      type: scalar
      range:
      - -0.015
      - 0.015
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
  subtask_id: insertion
- id: insert_down
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - -1.0
      align_with: channel_axis
      tolerance: 0.05
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    insertion_force:
      type: scalar
      range:
      - 10.0
      - 40.0
      default: 25.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.003
    - 0.003
    - 0.0
  subtask_id: insertion

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_entry** (`descend`)
  - target: source=yaml, anchor=task_object, entity=tcp, offset=[0.0, 0.0, -0.05]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **align_lateral** (`align`)
  - target: source=yaml, anchor=task_object, entity=tcp, offset=[0.0, 0.0, -0.055]
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (add)
- **insert_down** (`insert`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=align_axis, axis=[0.0, 0.0, -1.0], align_with=channel_axis, tolerance=0.05
  - parameter_bindings:
    - insertion_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - insertion_force: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.003, 0.003, 0.0]

## Design Metrics

- **Composite score**: 0.681
- **task_score** (E): 0.975
- **fitness_score**: 0.561  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_entry | 1.00 | 0.00 | 0.0070 |
| align_lateral | 1.00 | 0.00 | 0.0155 |
| insert_down | 1.00 | 1.00 | 0.1980 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_entry | descend | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.500, -0.000, 0.294) | (0.504, -0.000, 0.340)→(0.505, -0.000, 0.333) | 0.260→0.253 | 0.00 / 0.000 | 0.000 | 0.000 |
| align_lateral | align | 1.00 / step_budget | (0.500, -0.000, 0.294)→(0.510, 0.001, 0.281) | (0.505, -0.000, 0.333)→(0.515, 0.001, 0.321) | 0.253→0.241 | 0.00 / 0.000 | 0.000 | 0.000 |
| insert_down | insert | 1.00 / force_exceeded | (0.510, 0.001, 0.281)→(0.499, -0.000, 0.084) | (0.515, 0.001, 0.321)→(0.533, 0.000, 0.104) | 0.241→0.041 | 1.00 / 1.667 | 1602.601 | 1602.861 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- distance_to_goal_ratio: 0.990
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.990
- phase_score: 0.283
- phase_breakdown.insertion_score: 0.016
- phase_breakdown.pre_insert_approach_score: 0.907

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.566
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.990
- **Median Q (composite search score)**: 0.679
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.298


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `0c4288e4b4f4eb50f7d141bdaea44f8ed4eecfe7429f8148c247811f0f5250bc`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2ae90e10c3e712e9da92b27bc0ded08b6d103e49e03139a26a0fa45d3ac81c97`; realized-scene SHA-256: `f2535c6a7dfc5a3ca3c25224b40d7fd8d1111b06ec904a3c56a54673c2686a85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.03178,0.08]},{"name":"task_object","value":[0.51001,0.03178,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.51001,0.03178,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.51001,0.03178,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.73333,"average_solve_count":45.0,"average_success_count":45.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.align_speed":0.03982,"align_lateral.align_tolerance":0.00866,"align_lateral.lateral_offset_x":0.01258,"align_lateral.lateral_offset_y":-0.00061,"approach_to_entry.approach_speed":0.11835,"insert_down.insertion_depth":0.2993,"insert_down.insertion_force":17.69385},"optimized_scores":{"best_composite_score":0.67763,"best_fitness_score":0.55763,"best_task_score":0.96606},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.51219,-0.00091,0.07858],"force_p95":1156.87306,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1156.87306,"mean_force":1156.87306,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.50384,-0.00097,0.08962]}],"total_contact_groups":1},"final_pose_error":0.10366,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.51001,0.03178,0.025],"final_tcp_position":[0.50127,-0.00097,0.08731],"realised_fixture_position":[0.51001,0.03178,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.51001,0.03178,0.08]},"peak_contact_force":1156.87306,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":46.0,"n_steps_budget":600.0,"object_pos_end":[0.50464,-1e-05,0.33327],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25332,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_insert_approach","tcp_end":[0.50026,-1e-05,0.29351],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":80.0,"n_steps_budget":600.0,"object_pos_end":[0.51341,-0.00038,0.32293],"object_pos_start":[0.50464,-1e-05,0.33327],"object_to_goal_dist_end":0.2433,"object_to_goal_dist_start":0.25332,"object_z_max":0.33327,"peak_contact_force":0.0,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.50866,-0.0004,0.28322],"tcp_start":[0.50026,-1e-05,0.29351],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":79.0,"n_steps_budget":1000.0,"object_pos_end":[0.53487,-0.0007,0.10901],"object_pos_start":[0.51341,-0.00038,0.32293],"object_to_goal_dist_end":0.04537,"object_to_goal_dist_start":0.2433,"object_z_max":0.32432,"peak_contact_force":1156.87306,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1.0,"raw_peak_contact_force":1156.87306,"subtask_id":"insertion","tcp_end":[0.50127,-0.00097,0.08731],"tcp_start":[0.50866,-0.0004,0.28322],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `02e4649f08bda5439eae760bf0bc4b5a6b47c91c93317c6956c2509043be6196`; realized-scene SHA-256: `586a2957baaedcadf28af0fbf7d32a1a4534953c544a60ba5a7051ee138050bc`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.03898,0.08]},{"name":"task_object","value":[0.48616,0.03898,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.48616,0.03898,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.48616,0.03898,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.62222,"average_solve_count":45.0,"average_success_count":45.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.align_speed":0.02923,"align_lateral.align_tolerance":0.00672,"align_lateral.lateral_offset_x":0.01047,"align_lateral.lateral_offset_y":0.00341,"approach_to_entry.approach_speed":0.05218,"insert_down.insertion_depth":0.23917,"insert_down.insertion_force":25.83935},"optimized_scores":{"best_composite_score":0.67863,"best_fitness_score":0.55863,"best_task_score":0.96895},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.5117,0.00246,0.07838],"force_p95":1157.90527,"geom_a":"peg_tip","geom_b":"socket_collar_y2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1157.94427,"mean_force":1157.55432,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.50344,0.00258,0.08928]},{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.51632,0.00258,0.07975],"force_p95":0.0,"geom_a":"peg_tip","geom_b":"socket_collar_x1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.50215,0.00258,0.0881]}],"total_contact_groups":2},"final_pose_error":0.04488,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.48616,0.03898,0.025],"final_tcp_position":[0.50014,0.00258,0.08634],"realised_fixture_position":[0.48616,0.03898,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.48616,0.03898,0.08]},"peak_contact_force":1157.94427,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":46.0,"n_steps_budget":600.0,"object_pos_end":[0.50464,-1e-05,0.33327],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25332,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_insert_approach","tcp_end":[0.50026,-1e-05,0.29351],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":123.0,"n_steps_budget":600.0,"object_pos_end":[0.51353,0.0024,0.32117],"object_pos_start":[0.50464,-1e-05,0.33327],"object_to_goal_dist_end":0.24156,"object_to_goal_dist_start":0.25332,"object_z_max":0.33327,"peak_contact_force":0.0,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.50872,0.00239,0.28146],"tcp_start":[0.50026,-1e-05,0.29351],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":80.0,"n_steps_budget":1000.0,"object_pos_end":[0.53404,0.0026,0.10757],"object_pos_start":[0.51353,0.0024,0.32117],"object_to_goal_dist_end":0.04388,"object_to_goal_dist_start":0.24156,"object_z_max":0.32318,"peak_contact_force":1157.16437,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":1157.94427,"subtask_id":"insertion","tcp_end":[0.50014,0.00258,0.08634],"tcp_start":[0.50872,0.00239,0.28146],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7363bc0b3fa7329ef53220378736f8cf8ba8a5eef8ffe48ac32070ac53331cd4`; realized-scene SHA-256: `b79f8c48d80d518422f0f353e5fb8a66ede3bec4fd1cbe80690c422c72d900f9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,-0.01705,0.08]},{"name":"task_object","value":[0.52962,-0.01705,0.08]},{"name":"fixture","value":[0.50397,-0.0,0.34031]},{"name":"target","value":[0.50397,-0.0,0.34031]},{"name":"socket","value":[0.50397,-0.0,0.34031]},{"name":"goal","value":[0.50397,-0.0,0.34031]}],"axes":[{"name":"insertion_axis","value":[0.0,0.0,-1.0]}],"fixture_states":[{"name":"peg_socket","state":"static_frozen"}],"fixtures":[{"name":"peg_socket","orientation":[1.0,0.0,0.0,0.0],"position":[0.50397,-0.0,0.34031]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"hole_depth_m","value":0.05},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","position":[0.52962,-0.01705,0.08]}],"obstacles":[],"targets":[{"name":"socket_entry","position":[0.52962,-0.01705,0.025]}],"task_name":"peg_insert"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.62222,"average_solve_count":45.0,"average_success_count":45.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_lateral.align_speed":0.02542,"align_lateral.align_tolerance":0.0032,"align_lateral.lateral_offset_x":0.01126,"align_lateral.lateral_offset_y":-0.00045,"approach_to_entry.approach_speed":0.11091,"insert_down.insertion_depth":0.18629,"insert_down.insertion_force":23.10944},"optimized_scores":{"best_composite_score":0.68574,"best_fitness_score":0.56574,"best_task_score":0.99},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg_socket","contact_count":1.0,"contact_point_centroid":[0.49856,0.01359,0.07939],"force_p95":2493.76585,"geom_a":"peg_tip","geom_b":"socket_collar_x2","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2493.76585,"mean_force":2493.76585,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.49732,-0.00139,0.07935]},{"body_a":"attachment","body_b":"peg_socket","contact_count":2.0,"contact_point_centroid":[0.5005,0.01331,0.07996],"force_p95":1700.80942,"geom_a":"peg_tip","geom_b":"socket_collar_y1","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1768.13961,"mean_force":1094.83774,"phase_index":2.0,"phase_name":"insert_down","phase_type":"insert","tcp_position_centroid":[0.4988,-0.00125,0.08062]}],"total_contact_groups":2},"final_pose_error":0.02309,"key_states":{"actual_goal_position":[0.5,0.0,0.08],"final_object_position":[0.52962,-0.01705,0.025],"final_tcp_position":[0.49479,-0.00164,0.07734],"realised_fixture_position":[0.52962,-0.01705,0.025],"realised_goal_position":[0.5,0.0,0.08],"realised_object_initial_position":[0.50397,-0.0,0.34031],"socket_entry_position":[0.52962,-0.01705,0.08]},"peak_contact_force":2493.76585,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":46.0,"n_steps_budget":600.0,"object_pos_end":[0.50464,-1e-05,0.33327],"object_pos_start":[0.50397,-0.0,0.34031],"object_to_goal_dist_end":0.25332,"object_to_goal_dist_start":0.26034,"object_z_max":0.34031,"peak_contact_force":0.0,"phase_name":"approach_to_entry","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_insert_approach","tcp_end":[0.50026,-1e-05,0.29351],"tcp_start":[0.49985,-0.0,0.30052],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.51658,-0.00042,0.31897],"object_pos_start":[0.50464,-1e-05,0.33327],"object_to_goal_dist_end":0.23955,"object_to_goal_dist_start":0.25332,"object_z_max":0.33327,"peak_contact_force":0.0,"phase_name":"align_lateral","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"insertion","tcp_end":[0.51174,-0.00044,0.27927],"tcp_start":[0.50026,-1e-05,0.29351],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":83.0,"n_steps_budget":1000.0,"object_pos_end":[0.52974,-0.00131,0.0968],"object_pos_start":[0.51658,-0.00042,0.31897],"object_to_goal_dist_end":0.03418,"object_to_goal_dist_start":0.23955,"object_z_max":0.32184,"peak_contact_force":2493.76585,"phase_name":"insert_down","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":2493.76585,"subtask_id":"insertion","tcp_end":[0.49479,-0.00164,0.07734],"tcp_start":[0.51174,-0.00044,0.27927],"tcp_to_object_dist_end":0.04,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```