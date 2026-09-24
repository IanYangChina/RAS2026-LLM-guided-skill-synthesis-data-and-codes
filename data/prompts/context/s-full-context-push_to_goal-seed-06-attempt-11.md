## Search State

- **Seed**: 6
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | -0.0757 | 0.03 | ✅ accepted |
| 10 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | -0.1085 | 0.01 | ✅ accepted |
| 9 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | -0.1100 | 0.01 | ✅ accepted |
| 8 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.1413 | 0.00 | ✅ accepted |
| 7 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | -0.2057 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.076) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.04
  - 0.08
  weight: 0.3
- id: push_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_tcp_to_precontact
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
    - 0.04
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
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
  guards:
  - id: contact_during_approach
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: reach_contact
- id: push_object_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.025
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: contact_during_push
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_tcp_to_precontact** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.04, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=contact_during_approach, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.01, 0.0]
- **push_object_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=contact_during_push, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.01, 0.0]

## Design Metrics

- **Composite score**: -0.076
- **task_score** (E): 0.032
- **fitness_score**: 0.174  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_tcp_to_precontact | 1.00 | 1.00 | 0.2016 |
| push_object_to_goal | 1.00 | 1.00 | 0.1813 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_tcp_to_precontact | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.064, 0.113) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_object_to_goal | push | 1.00 / step_budget | (0.496, 0.064, 0.113)→(0.499, -0.096, 0.033) | (0.500, 0.029, 0.025)→(0.501, 0.025, 0.027) | 0.180→0.175 | 1.00 / 3.667 | 63.684 | 82.501 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.115
- lateral_force_integral: None
- approach_alignment: 0.629
- goal_progress: 0.097
- terminal_score: 0.097
- phase_score: 0.314
- phase_breakdown.push_goal_score: 0.097
- phase_breakdown.reach_contact_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.227
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.097
- **Median Q (composite search score)**: -0.102
- **K-run variance**: 0.0014
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.272


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91139,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_tcp_to_precontact.approach_speed":0.09507,"approach_tcp_to_precontact.approach_tolerance":0.01857,"push_object_to_goal.push_distance":0.05898,"push_object_to_goal.push_speed":0.07615,"push_object_to_goal.push_tolerance":0.01236},"optimized_scores":{"best_composite_score":-0.02303,"best_fitness_score":0.22697,"best_task_score":0.09682},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":71.0,"contact_point_centroid":[0.51068,-0.04778,0.0469],"force_p95":235.7349,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":247.0137,"mean_force":191.18176,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.50327,-0.05542,0.04689]},{"body_a":"world","body_b":"push_box","contact_count":904.0,"contact_point_centroid":[0.50475,-0.02262,-0.00011],"force_p95":138.64195,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":204.12967,"mean_force":15.34816,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.49977,-0.01734,0.07741]},{"body_a":"world","body_b":"push_box","contact_count":2372.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_tcp_to_precontact","phase_type":"approach","tcp_position_centroid":[0.49964,0.00956,0.20727]}],"total_contact_groups":3},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50763,-0.03189,0.03194],"final_tcp_position":[0.50775,-0.06928,0.04232],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":247.0137,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":593.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_tcp_to_precontact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2372.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.50102,0.01952,0.11412],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.50763,-0.03189,0.03194],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.11856,"object_to_goal_dist_start":0.13127,"object_z_max":0.03183,"peak_contact_force":190.56204,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":975.0,"raw_peak_contact_force":247.0137,"subtask_id":"push_goal","tcp_end":[0.50775,-0.06928,0.04232],"tcp_start":[0.50102,0.01952,0.11412],"tcp_to_object_dist_end":0.03881,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.3,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_tcp_to_precontact.approach_speed":0.15391,"approach_tcp_to_precontact.approach_tolerance":0.0141,"push_object_to_goal.push_distance":0.19022,"push_object_to_goal.push_speed":0.12043,"push_object_to_goal.push_tolerance":0.01497},"optimized_scores":{"best_composite_score":-0.10198,"best_fitness_score":0.14802,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2496.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_tcp_to_precontact","phase_type":"approach","tcp_position_centroid":[0.50456,0.04048,0.20526]},{"body_a":"world","body_b":"push_box","contact_count":1944.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.50314,-0.01984,0.06783]}],"total_contact_groups":2},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51501,0.04767,0.02499],"final_tcp_position":[0.49784,-0.12261,0.02732],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":0.24534,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":624.0,"n_steps_budget":870.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_tcp_to_precontact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2496.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.51082,0.08189,0.11169],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1944.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_goal","tcp_end":[0.49784,-0.12261,0.02732],"tcp_start":[0.51082,0.08189,0.11169],"tcp_to_object_dist_end":0.17115,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64348,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_tcp_to_precontact.approach_speed":0.10075,"approach_tcp_to_precontact.approach_tolerance":0.01412,"push_object_to_goal.push_distance":0.17575,"push_object_to_goal.push_speed":0.06609,"push_object_to_goal.push_tolerance":0.01453},"optimized_scores":{"best_composite_score":-0.10196,"best_fitness_score":0.14804,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2744.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_tcp_to_precontact","phase_type":"approach","tcp_position_centroid":[0.48789,0.04553,0.20536]},{"body_a":"world","body_b":"push_box","contact_count":1964.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"push_object_to_goal","phase_type":"push","tcp_position_centroid":[0.4831,-0.00209,0.06869]}],"total_contact_groups":2},"final_pose_error":0.01982,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47924,0.05847,0.02499],"final_tcp_position":[0.49141,-0.09753,0.02798],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":0.24534,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_tcp_to_precontact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2744.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.47731,0.09206,0.11212],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0934,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":491.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_object_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1964.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_goal","tcp_end":[0.49141,-0.09753,0.02798],"tcp_start":[0.47731,0.09206,0.11212],"tcp_to_object_dist_end":0.15651,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```