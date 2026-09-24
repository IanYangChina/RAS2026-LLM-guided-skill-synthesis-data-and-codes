## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | time_limit | time_limit | time_limit | 7 | 0.3552 | 0.87 | ❌ rejected |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3356 | 0.90 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.4398 | 0.90 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3338 | 0.90 | ❌ rejected |
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3362 | 0.90 | ✅ accepted |

**Proposal policy**: task_score is 0.87 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.355) — your mutation base

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

- **Composite score**: 0.355
- **task_score** (E): 0.874
- **fitness_score**: 0.735  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1926 |
| descend_1 | 1.00 | 1.00 | 0.0876 |
| push_1 | 1.00 | 1.00 | 0.2062 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.496, 0.027, 0.113) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / time_limit | (0.496, 0.027, 0.113)→(0.497, 0.072, 0.038) | (0.500, 0.029, 0.025)→(0.501, 0.028, 0.025) | 0.180→0.179 | 1.00 / 4.000 | 0.260 | 183.688 |
| push_1 | push | 1.00 / time_limit | (0.497, 0.072, 0.038)→(0.497, -0.133, 0.022) | (0.501, 0.028, 0.025)→(0.505, -0.170, 0.027) | 0.179→0.022 | 1.00 / 2.333 | 29.843 | 83.810 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.714
- goal_progress: 0.901
- terminal_score: 0.901
- phase_score: 0.638
- phase_breakdown.reach_contact_score: 0.402
- phase_breakdown.reach_standoff_score: 0.825
- phase_breakdown.push_complete_score: 0.704

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.743
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.901
- **Median Q (composite search score)**: 0.353
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.261


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.48333,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_max_time":3.57795,"approach_1.approach_speed":0.54363,"descend_1.behind_distance":0.04358,"descend_1.descend_max_time":3.1994,"descend_1.descend_speed":0.21774,"push_1.push_max_time":3.44917,"push_1.push_speed":0.38821},"optimized_scores":{"best_composite_score":0.34933,"best_fitness_score":0.72933,"best_task_score":0.83345},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":91.0,"contact_point_centroid":[0.51132,0.0076,0.0483],"force_p95":152.10844,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.73998,"mean_force":98.00575,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50328,0.01493,0.05127]},{"body_a":"world","body_b":"push_box","contact_count":1927.0,"contact_point_centroid":[0.50466,-0.01677,-7e-05],"force_p95":31.56786,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":171.81499,"mean_force":4.91227,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50014,0.00072,0.07547]},{"body_a":"world","body_b":"push_box","contact_count":751.0,"contact_point_centroid":[0.51328,-0.09498,-0.00011],"force_p95":39.28124,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.3876,"mean_force":12.00018,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49926,-0.04254,0.02927]},{"body_a":"attachment","body_b":"push_box","contact_count":412.0,"contact_point_centroid":[0.51009,-0.07094,0.04675],"force_p95":56.16309,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.22339,"mean_force":16.60591,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49856,-0.05938,0.02746]},{"body_a":"push_box","body_b":"link7","contact_count":157.0,"contact_point_centroid":[0.53053,-0.12586,0.05345],"force_p95":46.79699,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.99796,"mean_force":17.51469,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49805,-0.10711,0.02399]},{"body_a":"world","body_b":"push_box","contact_count":2264.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49956,-0.00832,0.20959]}],"total_contact_groups":6},"final_pose_error":0.01574,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50851,-0.16984,0.02844],"final_tcp_position":[0.49945,-0.13436,0.02325],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":189.73998,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":566.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2264.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_standoff","tcp_end":[0.50081,-0.01753,0.11308],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08818,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.50623,-0.01917,0.0249],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13098,"object_to_goal_dist_start":0.13127,"object_z_max":0.02517,"peak_contact_force":0.24707,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2018.0,"raw_peak_contact_force":189.73998,"subtask_id":"reach_contact","tcp_end":[0.50345,0.02178,0.0379],"tcp_start":[0.50081,-0.01753,0.11308],"tcp_to_object_dist_end":0.04305,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.50851,-0.16984,0.02844],"object_pos_start":[0.50623,-0.01917,0.0249],"object_to_goal_dist_end":0.02186,"object_to_goal_dist_start":0.13098,"object_z_max":0.02846,"peak_contact_force":53.0026,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1320.0,"raw_peak_contact_force":92.3876,"subtask_id":"push_complete","tcp_end":[0.49945,-0.13436,0.02325],"tcp_start":[0.50345,0.02178,0.0379],"tcp_to_object_dist_end":0.03698,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.48333,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_max_time":4.31377,"approach_1.approach_speed":0.73294,"descend_1.behind_distance":0.04823,"descend_1.descend_max_time":4.37719,"descend_1.descend_speed":0.14441,"push_1.push_max_time":3.67589,"push_1.push_speed":0.35718},"optimized_scores":{"best_composite_score":0.3531,"best_fitness_score":0.7331,"best_task_score":0.8869},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":78.0,"contact_point_centroid":[0.52176,0.07482,0.04856],"force_p95":117.09915,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":160.90477,"mean_force":80.61628,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51449,0.08327,0.05097]},{"body_a":"world","body_b":"push_box","contact_count":1989.0,"contact_point_centroid":[0.51525,0.04968,-6e-05],"force_p95":19.31348,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":158.93654,"mean_force":3.43524,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51096,0.06625,0.07487]},{"body_a":"world","body_b":"push_box","contact_count":674.0,"contact_point_centroid":[0.51917,-0.04174,-0.00011],"force_p95":37.25722,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.49337,"mean_force":8.71913,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50692,0.00983,0.02879]},{"body_a":"attachment","body_b":"push_box","contact_count":345.0,"contact_point_centroid":[0.51549,-0.02779,0.04533],"force_p95":53.97199,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.62185,"mean_force":12.76008,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50487,-0.01638,0.0269]},{"body_a":"push_box","body_b":"link7","contact_count":111.0,"contact_point_centroid":[0.53495,-0.09775,0.05254],"force_p95":51.74181,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.91065,"mean_force":11.83652,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50107,-0.07844,0.02378]},{"body_a":"world","body_b":"push_box","contact_count":2268.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50418,0.02092,0.20966]}],"total_contact_groups":6},"final_pose_error":0.01845,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5084,-0.17076,0.02607],"final_tcp_position":[0.49791,-0.13205,0.02126],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":160.90477,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":567.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2268.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_standoff","tcp_end":[0.51056,0.04417,0.11292],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08812,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":538.0,"n_steps_budget":600.0,"object_pos_end":[0.51627,0.04733,0.02494],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.198,"object_to_goal_dist_start":0.19823,"object_z_max":0.02613,"peak_contact_force":0.24632,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2067.0,"raw_peak_contact_force":160.90477,"subtask_id":"reach_contact","tcp_end":[0.51497,0.09186,0.03661],"tcp_start":[0.51056,0.04417,0.11292],"tcp_to_object_dist_end":0.04606,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.5084,-0.17076,0.02607],"object_pos_start":[0.51627,0.04733,0.02494],"object_to_goal_dist_end":0.02242,"object_to_goal_dist_start":0.198,"object_z_max":0.02881,"peak_contact_force":36.14272,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1130.0,"raw_peak_contact_force":93.49337,"subtask_id":"push_complete","tcp_end":[0.49791,-0.13205,0.02126],"tcp_start":[0.51497,0.09186,0.03661],"tcp_to_object_dist_end":0.04039,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.5,"average_solve_count":62.0,"average_success_count":62.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_max_time":2.85848,"approach_1.approach_speed":0.63638,"descend_1.behind_distance":0.04569,"descend_1.descend_max_time":3.57239,"descend_1.descend_speed":0.2369,"push_1.push_max_time":3.76235,"push_1.push_speed":0.24547},"optimized_scores":{"best_composite_score":0.36309,"best_fitness_score":0.74309,"best_task_score":0.90112},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":108.0,"contact_point_centroid":[0.48255,0.08684,0.04796],"force_p95":161.6934,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":200.41924,"mean_force":108.48052,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47434,0.09357,0.05124]},{"body_a":"world","body_b":"push_box","contact_count":1905.0,"contact_point_centroid":[0.47938,0.0612,-9e-05],"force_p95":56.43795,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":165.3827,"mean_force":6.43689,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4734,0.07489,0.07697]},{"body_a":"attachment","body_b":"push_box","contact_count":386.0,"contact_point_centroid":[0.49255,-0.02746,0.04357],"force_p95":56.06459,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.5486,"mean_force":11.7399,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48279,-0.01597,0.02841]},{"body_a":"push_box","body_b":"link7","contact_count":50.0,"contact_point_centroid":[0.5199,-0.06212,0.05442],"force_p95":33.67691,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.86118,"mean_force":5.92444,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48612,-0.04789,0.02641]},{"body_a":"world","body_b":"push_box","contact_count":706.0,"contact_point_centroid":[0.49288,-0.03754,-0.00013],"force_p95":30.41009,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.08618,"mean_force":7.33024,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48,0.01448,0.03078]},{"body_a":"world","body_b":"push_box","contact_count":2268.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48841,0.0257,0.20984]}],"total_contact_groups":6},"final_pose_error":0.01755,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49671,-0.17045,0.02522],"final_tcp_position":[0.49464,-0.13381,0.02085],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":200.41924,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":567.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2268.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_standoff","tcp_end":[0.47726,0.05422,0.11339],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08853,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":535.0,"n_steps_budget":600.0,"object_pos_end":[0.48047,0.05682,0.02443],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20774,"object_to_goal_dist_start":0.2095,"object_z_max":0.02719,"peak_contact_force":0.28712,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2013.0,"raw_peak_contact_force":200.41924,"subtask_id":"reach_contact","tcp_end":[0.47385,0.1013,0.03943],"tcp_start":[0.47726,0.05422,0.11339],"tcp_to_object_dist_end":0.04741,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":631.0,"n_steps_budget":660.0,"object_pos_end":[0.49671,-0.17045,0.02522],"object_pos_start":[0.48047,0.05682,0.02443],"object_to_goal_dist_end":0.02072,"object_to_goal_dist_start":0.20774,"object_z_max":0.02904,"peak_contact_force":0.38462,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1142.0,"raw_peak_contact_force":65.5486,"subtask_id":"push_complete","tcp_end":[0.49464,-0.13381,0.02085],"tcp_start":[0.47385,0.1013,0.03943],"tcp_to_object_dist_end":0.03696,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```