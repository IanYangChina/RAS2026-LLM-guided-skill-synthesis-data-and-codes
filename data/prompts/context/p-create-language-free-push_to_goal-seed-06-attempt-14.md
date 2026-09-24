## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3343 | 0.90 | ❌ rejected |
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | time_limit | time_limit | time_limit | 7 | 0.3552 | 0.87 | ❌ rejected |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3356 | 0.90 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.4398 | 0.90 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3338 | 0.90 | ❌ rejected |

**Proposal policy**: task_score is 0.90 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`
- Frozen object start: [0.5045797221766332, -0.01880749562239939, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5045797221766332, -0.01880749562239939, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5046, -0.0188, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5045797221766332, -0.01880749562239939, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.900, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5045797221766332, -0.01880749562239939, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=0.334) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_standoff
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.2
- id: reach_contact
  anchor: object
  weight: 0.3
- id: push_complete
  target_entity: object
  weight: 0.5
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.3
      - 0.8
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.01
    - 0.01
    - 0.0
  subtask_id: reach_standoff
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.01
    offset_along_axis:
      distance: 0.04
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    behind_distance:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.01
    - 0.01
    - 0.0
  subtask_id: reach_contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.15
      - 0.5
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: push_complete

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.01, 0.01, 0.0]
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.01], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.01, 0.01, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.334
- **task_score** (E): 0.897
- **fitness_score**: 0.714  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1819 |
| descend_1 | 1.00 | 1.00 | 0.0938 |
| push_1 | 1.00 | 1.00 | 0.2027 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.026, 0.124) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.497, 0.026, 0.124)→(0.496, 0.071, 0.042) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.179 | 1.00 / 3.667 | 0.343 | 103.547 |
| push_1 | push | 1.00 / step_budget | (0.496, 0.071, 0.042)→(0.498, -0.130, 0.022) | (0.500, 0.029, 0.025)→(0.505, -0.167, 0.027) | 0.179→0.018 | 1.00 / 1.667 | 21.434 | 119.485 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.711
- goal_progress: 0.917
- terminal_score: 0.917
- phase_score: 0.590
- phase_breakdown.reach_contact_score: 0.398
- phase_breakdown.reach_standoff_score: 0.676
- phase_breakdown.push_complete_score: 0.671

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.721
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.917
- **Median Q (composite search score)**: 0.338
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.297


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.48333,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.52586,"approach_1.approach_tolerance":0.02143,"descend_1.behind_distance":0.04336,"descend_1.descend_speed":0.24931,"descend_1.descend_tolerance":0.01047,"push_1.push_speed":0.29089,"push_1.push_tolerance":0.02261},"optimized_scores":{"best_composite_score":0.3241,"best_fitness_score":0.7041,"best_task_score":0.86426},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":37.0,"contact_point_centroid":[0.50854,0.00669,0.04865],"force_p95":150.28162,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":174.12958,"mean_force":104.51308,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5025,0.01582,0.05078]},{"body_a":"world","body_b":"push_box","contact_count":1162.0,"contact_point_centroid":[0.50506,-0.01835,-3e-05],"force_p95":25.47618,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":149.39646,"mean_force":3.60065,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50028,0.0005,0.08318]},{"body_a":"attachment","body_b":"push_box","contact_count":152.0,"contact_point_centroid":[0.5076,-0.06502,0.04606],"force_p95":62.1483,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.70077,"mean_force":15.63861,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49912,-0.05347,0.03131]},{"body_a":"world","body_b":"push_box","contact_count":378.0,"contact_point_centroid":[0.51022,-0.10415,-0.00013],"force_p95":32.99939,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.56316,"mean_force":6.9444,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49921,-0.0536,0.03145]},{"body_a":"push_box","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.53266,-0.09901,0.05572],"force_p95":7.57691,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.84925,"mean_force":2.381,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49839,-0.0888,0.02709]},{"body_a":"world","body_b":"push_box","contact_count":1244.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50016,-0.00797,0.2136]}],"total_contact_groups":6},"final_pose_error":0.01986,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50584,-0.16683,0.02523],"final_tcp_position":[0.49683,-0.13062,0.02202],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":174.12958,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1244.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_standoff","tcp_end":[0.50116,-0.01645,0.12444],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":304.0,"n_steps_budget":600.0,"object_pos_end":[0.50485,-0.01978,0.0249],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13031,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.53856,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1199.0,"raw_peak_contact_force":174.12958,"subtask_id":"reach_contact","tcp_end":[0.50375,0.02001,0.04357],"tcp_start":[0.50116,-0.01645,0.12444],"tcp_to_object_dist_end":0.04397,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":343.0,"n_steps_budget":600.0,"object_pos_end":[0.50584,-0.16683,0.02523],"object_pos_start":[0.50485,-0.01978,0.0249],"object_to_goal_dist_end":0.01782,"object_to_goal_dist_start":0.13031,"object_z_max":0.02865,"peak_contact_force":0.30013,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":541.0,"raw_peak_contact_force":91.70077,"subtask_id":"push_complete","tcp_end":[0.49683,-0.13062,0.02202],"tcp_start":[0.50375,0.02001,0.04357],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.48333,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.49959,"approach_1.approach_tolerance":0.02478,"descend_1.behind_distance":0.05017,"descend_1.descend_speed":0.23684,"descend_1.descend_tolerance":0.01796,"push_1.push_speed":0.38096,"push_1.push_tolerance":0.01831},"optimized_scores":{"best_composite_score":0.33805,"best_fitness_score":0.71805,"best_task_score":0.90818},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":358.0,"contact_point_centroid":[0.51691,-0.03947,0.04551],"force_p95":80.68302,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.62635,"mean_force":25.96994,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50439,-0.02925,0.02866]},{"body_a":"world","body_b":"push_box","contact_count":548.0,"contact_point_centroid":[0.5233,-0.05931,-0.00015],"force_p95":68.7681,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":136.70778,"mean_force":20.19329,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50558,-0.0125,0.03011]},{"body_a":"push_box","body_b":"link7","contact_count":156.0,"contact_point_centroid":[0.53253,-0.08459,0.05738],"force_p95":60.02727,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.83531,"mean_force":22.51037,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50266,-0.06506,0.02667]},{"body_a":"attachment","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.51657,0.07268,0.04974],"force_p95":43.18312,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.52927,"mean_force":34.8395,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51314,0.08381,0.05101]},{"body_a":"world","body_b":"push_box","contact_count":1326.0,"contact_point_centroid":[0.51521,0.04783,-1e-05],"force_p95":0.2479,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.91648,"mean_force":0.61477,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51089,0.06568,0.08027]},{"body_a":"world","body_b":"push_box","contact_count":1292.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50464,0.02029,0.21269]}],"total_contact_groups":6},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50457,-0.16746,0.02736],"final_tcp_position":[0.49837,-0.13043,0.02185],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":139.62635,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1292.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_standoff","tcp_end":[0.51042,0.04175,0.12315],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09845,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":334.0,"n_steps_budget":600.0,"object_pos_end":[0.51512,0.04748,0.02498],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19805,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1340.0,"raw_peak_contact_force":43.52927,"subtask_id":"reach_contact","tcp_end":[0.51403,0.09074,0.04014],"tcp_start":[0.51042,0.04175,0.12315],"tcp_to_object_dist_end":0.04586,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":483.0,"n_steps_budget":600.0,"object_pos_end":[0.50457,-0.16746,0.02736],"object_pos_start":[0.51512,0.04748,0.02498],"object_to_goal_dist_end":0.0182,"object_to_goal_dist_start":0.19805,"object_z_max":0.03262,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1062.0,"raw_peak_contact_force":139.62635,"subtask_id":"push_complete","tcp_end":[0.49837,-0.13043,0.02185],"tcp_start":[0.51403,0.09074,0.04014],"tcp_to_object_dist_end":0.03795,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.50794,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.63078,"approach_1.approach_tolerance":0.03027,"descend_1.behind_distance":0.04974,"descend_1.descend_speed":0.16281,"descend_1.descend_tolerance":0.01516,"push_1.push_speed":0.23915,"push_1.push_tolerance":0.01855},"optimized_scores":{"best_composite_score":0.34073,"best_fitness_score":0.72073,"best_task_score":0.91726},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":573.0,"contact_point_centroid":[0.50264,-0.06588,-0.00011],"force_p95":64.27462,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":127.1273,"mean_force":19.89366,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48231,-0.01357,0.03037]},{"body_a":"push_box","body_b":"link7","contact_count":225.0,"contact_point_centroid":[0.52036,-0.08741,0.05594],"force_p95":61.45736,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":119.59566,"mean_force":22.57991,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48921,-0.07197,0.02627]},{"body_a":"attachment","body_b":"push_box","contact_count":373.0,"contact_point_centroid":[0.49638,-0.04447,0.04481],"force_p95":72.243,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.11273,"mean_force":20.45545,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48446,-0.03363,0.02872]},{"body_a":"attachment","body_b":"push_box","contact_count":19.0,"contact_point_centroid":[0.47652,0.08354,0.04956],"force_p95":68.77092,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.98335,"mean_force":50.93904,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47199,0.09409,0.05151]},{"body_a":"world","body_b":"push_box","contact_count":1305.0,"contact_point_centroid":[0.47926,0.05867,-2e-05],"force_p95":0.27393,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.66204,"mean_force":0.99071,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47386,0.0754,0.08112]},{"body_a":"world","body_b":"push_box","contact_count":1300.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48928,0.02495,0.21273]}],"total_contact_groups":6},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50592,-0.16575,0.02919],"final_tcp_position":[0.49778,-0.1302,0.0235],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":127.1273,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_standoff","tcp_end":[0.47885,0.05132,0.12325],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09852,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":329.0,"n_steps_budget":600.0,"object_pos_end":[0.47931,0.05838,0.02493],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2094,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24483,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1324.0,"raw_peak_contact_force":92.98335,"subtask_id":"reach_contact","tcp_end":[0.47143,0.10092,0.04121],"tcp_start":[0.47885,0.05132,0.12325],"tcp_to_object_dist_end":0.04623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":531.0,"n_steps_budget":690.0,"object_pos_end":[0.50592,-0.16575,0.02919],"object_pos_start":[0.47931,0.05838,0.02493],"object_to_goal_dist_end":0.01734,"object_to_goal_dist_start":0.2094,"object_z_max":0.03205,"peak_contact_force":64.00229,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1171.0,"raw_peak_contact_force":127.1273,"subtask_id":"push_complete","tcp_end":[0.49778,-0.1302,0.0235],"tcp_start":[0.47143,0.10092,0.04121],"tcp_to_object_dist_end":0.03691,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```