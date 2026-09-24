## Search State

- **Seed**: 3
- **Iteration**: 3 / 15

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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

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
| `object` | offset from object initial position (0.45027790005723495, -0.03158273920846803, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=-0.226) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_behind
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.08
  weight: 0.2
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.8
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.08
    offset_along_axis:
      distance: 0.04
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.02
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_behind
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.04
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_behind
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.12
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.03
  parameters:
    force_threshold:
      type: scalar
      range:
      - 15.0
      - 24.5
      default: 24.5
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.12
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 24.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.08], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=replace_offset_projection, sign=negative}, tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.12, mode=replace_offset_projection, sign=positive}, tolerance=0.03
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=guards.force_guard.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=24.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: -0.226
- **task_score** (E): 0.021
- **fitness_score**: 0.054  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1911 |
| descend_1 | 1.00 | 1.00 | 0.0640 |
| push_1 | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.511, 0.036, 0.122) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.511, 0.036, 0.122)→(0.510, 0.039, 0.058) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 0.00 / guard_failure | (0.505, 0.023, 0.054)→(0.505, 0.023, 0.054) | (0.513, 0.002, 0.025)→(0.513, -0.001, 0.025) | 0.160→0.156 | 1.00 / 5.000 | 40.843 | 40.843 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.030
- lateral_force_integral: None
- approach_alignment: 0.433
- goal_progress: 0.030
- terminal_score: 0.030
- phase_score: 0.084
- phase_breakdown.approach_behind_score: 0.301
- phase_breakdown.push_to_goal_score: 0.030

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.062
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.030
- **Median Q (composite search score)**: -0.224
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: descend_1.descend_speed
- **Final σ (mean)**: 0.432


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47887,"average_solve_count":71.0,"average_success_count":71.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.14236,"descend_1.descend_speed":0.05127,"push_1.force_threshold":24.2175,"push_1.push_distance":0.13991,"push_1.push_speed":0.0231},"optimized_scores":{"best_composite_score":-0.23571,"best_fitness_score":0.04429,"best_task_score":0.01029},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":68.0,"contact_point_centroid":[0.44091,-0.00729,0.04982],"force_p95":20.92961,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.08397,"mean_force":14.97893,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43201,-0.00197,0.05562]},{"body_a":"world","body_b":"push_box","contact_count":597.0,"contact_point_centroid":[0.45068,-0.03279,-2e-05],"force_p95":6.54337,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.52052,"mean_force":1.94428,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43156,0.00044,0.05643]},{"body_a":"world","body_b":"push_box","contact_count":1368.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4702,0.00223,0.21315]},{"body_a":"world","body_b":"push_box","contact_count":924.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43503,0.00481,0.09161]}],"total_contact_groups":4},"final_pose_error":0.17304,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45077,-0.03281,0.02489],"final_tcp_position":[0.43271,-0.00321,0.05556],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":33.08397,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":342.0,"n_steps_budget":900.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_behind","tcp_end":[0.43981,0.0046,0.12403],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10597,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":231.0,"n_steps_budget":900.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":924.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_behind","tcp_end":[0.43215,0.00507,0.05942],"tcp_start":[0.43981,0.0046,0.12403],"tcp_to_object_dist_end":0.05346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":156.0,"n_steps_budget":1000.0,"object_pos_end":[0.45078,-0.0328,0.0249],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12712,"object_to_goal_dist_start":0.12843,"object_z_max":0.02501,"peak_contact_force":33.08397,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":665.0,"raw_peak_contact_force":33.08397,"subtask_id":"push_to_goal","tcp_end":[0.43271,-0.00321,0.05556],"tcp_start":[0.4327,-0.00319,0.05557],"tcp_to_object_dist_end":0.04628,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.62821,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.10572,"descend_1.descend_speed":0.1,"push_1.force_threshold":24.39837,"push_1.push_distance":0.17911,"push_1.push_speed":0.02294},"optimized_scores":{"best_composite_score":-0.21791,"best_fitness_score":0.06209,"best_task_score":0.02958},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":279.0,"contact_point_centroid":[0.56405,0.02316,0.04972],"force_p95":22.30445,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.72089,"mean_force":18.91199,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55307,0.0255,0.05305]},{"body_a":"world","body_b":"push_box","contact_count":1344.0,"contact_point_centroid":[0.55249,-0.00086,-5e-05],"force_p95":7.17933,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.88913,"mean_force":4.14721,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55386,0.02723,0.05337]},{"body_a":"world","body_b":"push_box","contact_count":1528.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52663,0.01674,0.21173]},{"body_a":"world","body_b":"push_box","contact_count":804.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55694,0.03606,0.0889]}],"total_contact_groups":4},"final_pose_error":0.19405,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55167,-0.00315,0.02482],"final_tcp_position":[0.55081,0.01783,0.05312],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":44.72089,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1528.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_behind","tcp_end":[0.55589,0.03445,0.12124],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10182,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":201.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":804.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_behind","tcp_end":[0.56038,0.03787,0.05781],"tcp_start":[0.55589,0.03445,0.12124],"tcp_to_object_dist_end":0.04962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":341.0,"n_steps_budget":1000.0,"object_pos_end":[0.55167,-0.00314,0.02482],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15568,"object_to_goal_dist_start":0.16043,"object_z_max":0.02501,"peak_contact_force":44.72089,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1623.0,"raw_peak_contact_force":44.72089,"subtask_id":"push_to_goal","tcp_end":[0.55081,0.01783,0.05312],"tcp_start":[0.55082,0.01787,0.05314],"tcp_to_object_dist_end":0.03524,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17241,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0926,"descend_1.descend_speed":0.02858,"push_1.force_threshold":24.4776,"push_1.push_distance":0.16578,"push_1.push_speed":0.03629},"optimized_scores":{"best_composite_score":-0.22369,"best_fitness_score":0.05631,"best_task_score":0.02285},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":249.0,"contact_point_centroid":[0.54437,0.05923,0.0497],"force_p95":23.97244,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.72458,"mean_force":20.33928,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53362,0.06193,0.05342]},{"body_a":"world","body_b":"push_box","contact_count":1228.0,"contact_point_centroid":[0.53642,0.03489,-5e-05],"force_p95":8.17726,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.11599,"mean_force":4.35118,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53417,0.06377,0.05377]},{"body_a":"world","body_b":"push_box","contact_count":1572.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51717,0.03281,0.21147]},{"body_a":"world","body_b":"push_box","contact_count":888.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53639,0.07051,0.08903]}],"total_contact_groups":4},"final_pose_error":0.18287,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53591,0.03265,0.02481],"final_tcp_position":[0.53267,0.05495,0.0535],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":44.72458,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":393.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1572.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_behind","tcp_end":[0.53649,0.0675,0.12082],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":222.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":888.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_behind","tcp_end":[0.53883,0.07397,0.05795],"tcp_start":[0.53649,0.0675,0.12082],"tcp_to_object_dist_end":0.04962,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.53591,0.03266,0.02481],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18615,"object_to_goal_dist_start":0.1905,"object_z_max":0.02501,"peak_contact_force":44.72458,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1477.0,"raw_peak_contact_force":44.72458,"subtask_id":"push_to_goal","tcp_end":[0.53267,0.05495,0.0535],"tcp_start":[0.53268,0.05499,0.05351],"tcp_to_object_dist_end":0.03648,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```