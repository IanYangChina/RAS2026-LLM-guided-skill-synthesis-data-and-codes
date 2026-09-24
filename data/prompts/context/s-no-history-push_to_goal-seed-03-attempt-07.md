## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

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

## Current Skill (Q=0.012) — your mutation base

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
  - 0.06
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
    - 0.06
    offset_along_axis:
      distance: 0.05
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
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
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
    - 0.0
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.06], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=replace_offset_projection, sign=negative}, tolerance=0.02
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.12, mode=replace_offset_projection, sign=positive}, tolerance=0.03
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=guards.force_guard.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=24.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.012
- **task_score** (E): 0.004
- **fitness_score**: 0.122  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2074 |
| descend_1 | 1.00 | 1.00 | 0.0594 |
| contact_1 | 1.00 | 1.00 | 0.0001 |
| push_1 | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.027, 0.103) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.510, 0.027, 0.103)→(0.527, 0.028, 0.046) | (0.513, 0.002, 0.025)→(0.518, 0.003, 0.025) | 0.160→0.161 | 1.00 / 3.667 | 237.138 | 251.126 |
| contact_1 | contact | 1.00 / force_exceeded | (0.527, 0.028, 0.046)→(0.527, 0.028, 0.046) | (0.518, 0.003, 0.025)→(0.518, 0.003, 0.025) | 0.161→0.161 | 1.00 / 3.667 | 119.747 | 119.747 |
| push_1 | push | 0.00 / guard_failure | (0.527, 0.028, 0.046)→(0.527, 0.028, 0.046) | (0.518, 0.003, 0.025)→(0.518, 0.003, 0.025) | 0.161→0.161 | 1.00 / 3.667 | 139.928 | 139.928 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.032
- lateral_force_integral: None
- approach_alignment: 0.478
- goal_progress: 0.012
- terminal_score: 0.012
- phase_score: 0.212
- phase_breakdown.establish_contact_score: 0.505
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.approach_behind_score: 0.403

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.132
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.012
- **Median Q (composite search score)**: 0.008
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.288


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08257,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05282,"contact_1.contact_force_threshold":8.43389,"contact_1.contact_speed":0.04391,"descend_1.descend_speed":0.13706,"push_1.push_distance":0.11352,"push_1.push_speed":0.06617},"optimized_scores":{"best_composite_score":0.02202,"best_fitness_score":0.13202,"best_task_score":0.01191},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":151.0,"contact_point_centroid":[0.45631,-0.00725,0.04549],"force_p95":288.22945,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":296.95709,"mean_force":251.60031,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44614,-0.00616,0.04954]},{"body_a":"world","body_b":"push_box","contact_count":1115.0,"contact_point_centroid":[0.45379,-0.0291,-0.00031],"force_p95":189.83154,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":222.63014,"mean_force":34.48785,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4421,-0.00543,0.06722]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.46533,-0.00803,0.04416],"force_p95":169.59254,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":169.78939,"mean_force":167.82086,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45501,-0.00636,0.04751]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.46148,-0.02532,-0.00093],"force_p95":139.27358,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":140.42183,"mean_force":56.47282,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45501,-0.00636,0.04751]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.46524,-0.00803,0.04411],"force_p95":127.99882,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.99882,"mean_force":127.99882,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45492,-0.00636,0.04745]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.46147,-0.0253,-0.00095],"force_p95":68.18298,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.08614,"mean_force":43.0469,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45492,-0.00636,0.04745]},{"body_a":"world","body_b":"push_box","contact_count":1640.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47146,-0.00171,0.20383]}],"total_contact_groups":7},"final_pose_error":0.13899,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45426,-0.03163,0.02409],"final_tcp_position":[0.4551,-0.00637,0.0476],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":296.95709,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1640.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_behind","tcp_end":[0.44243,-0.00353,0.1044],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08459,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":311.0,"n_steps_budget":600.0,"object_pos_end":[0.45428,-0.03159,0.02404],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12693,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":270.41111,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1266.0,"raw_peak_contact_force":296.95709,"subtask_id":"approach_behind","tcp_end":[0.45492,-0.00636,0.04745],"tcp_start":[0.44243,-0.00353,0.1044],"tcp_to_object_dist_end":0.03443,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":720.0,"object_pos_end":[0.45427,-0.03161,0.02405],"object_pos_start":[0.45428,-0.03159,0.02404],"object_to_goal_dist_end":0.12692,"object_to_goal_dist_start":0.12693,"object_z_max":0.02404,"peak_contact_force":127.99882,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":127.99882,"subtask_id":"establish_contact","tcp_end":[0.45498,-0.00636,0.04748],"tcp_start":[0.45492,-0.00636,0.04745],"tcp_to_object_dist_end":0.03445,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.45427,-0.03162,0.02407],"object_pos_start":[0.45427,-0.03161,0.02405],"object_to_goal_dist_end":0.12691,"object_to_goal_dist_start":0.12692,"object_z_max":0.02407,"peak_contact_force":169.78939,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":169.78939,"subtask_id":"push_to_goal","tcp_end":[0.4551,-0.00637,0.0476],"tcp_start":[0.45504,-0.00637,0.04753],"tcp_to_object_dist_end":0.03452,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.24528,"average_solve_count":53.0,"average_success_count":53.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.15898,"contact_1.contact_force_threshold":6.36888,"contact_1.contact_speed":0.04403,"descend_1.descend_speed":0.13539,"push_1.push_distance":0.1378,"push_1.push_speed":0.06385},"optimized_scores":{"best_composite_score":0.0068,"best_fitness_score":0.1168,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":138.0,"contact_point_centroid":[0.5746,0.02373,0.04596],"force_p95":221.10464,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":222.47756,"mean_force":187.17128,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56341,0.02653,0.04758]},{"body_a":"world","body_b":"push_box","contact_count":937.0,"contact_point_centroid":[0.5593,0.00281,-0.00025],"force_p95":199.96566,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":205.52255,"mean_force":27.97146,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55625,0.02606,0.06668]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.58316,0.02193,0.04435],"force_p95":117.2161,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":117.48184,"mean_force":114.82438,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.57246,0.02702,0.04509]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.58034,-0.00034,-0.00112],"force_p95":115.14963,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":115.98406,"mean_force":58.23341,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.57246,0.02702,0.04509]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.58305,0.02187,0.04432],"force_p95":115.80292,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":115.80292,"mean_force":115.80292,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.57239,0.02703,0.04504]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.58035,-0.00033,-0.00114],"force_p95":102.83456,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.82274,"mean_force":57.94097,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.57239,0.02703,0.04504]},{"body_a":"world","body_b":"push_box","contact_count":1552.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52549,0.01279,0.20242]}],"total_contact_groups":7},"final_pose_error":0.16668,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55872,0.00268,0.0256],"final_tcp_position":[0.57256,0.027,0.04517],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":222.47756,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":388.0,"n_steps_budget":900.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1552.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_behind","tcp_end":[0.55335,0.02631,0.10209],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":287.0,"n_steps_budget":600.0,"object_pos_end":[0.55878,0.00275,0.02558],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16367,"object_to_goal_dist_start":0.16043,"object_z_max":0.02555,"peak_contact_force":213.9199,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1075.0,"raw_peak_contact_force":222.47756,"subtask_id":"approach_behind","tcp_end":[0.57239,0.02703,0.04504],"tcp_start":[0.55335,0.02631,0.10209],"tcp_to_object_dist_end":0.03396,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":750.0,"object_pos_end":[0.55875,0.00273,0.02557],"object_pos_start":[0.55878,0.00275,0.02558],"object_to_goal_dist_end":0.16364,"object_to_goal_dist_start":0.16367,"object_z_max":0.02558,"peak_contact_force":115.80292,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":115.80292,"subtask_id":"establish_contact","tcp_end":[0.57244,0.02702,0.04506],"tcp_start":[0.57239,0.02703,0.04504],"tcp_to_object_dist_end":0.03403,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.55872,0.0027,0.02558],"object_pos_start":[0.55875,0.00273,0.02557],"object_to_goal_dist_end":0.16361,"object_to_goal_dist_start":0.16364,"object_z_max":0.02558,"peak_contact_force":117.48184,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":117.48184,"subtask_id":"push_to_goal","tcp_end":[0.57256,0.027,0.04517],"tcp_start":[0.57249,0.02701,0.04511],"tcp_to_object_dist_end":0.03415,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58889,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07049,"contact_1.contact_force_threshold":5.60743,"contact_1.contact_speed":0.03794,"descend_1.descend_speed":0.15828,"push_1.push_distance":0.12542,"push_1.push_speed":0.08532},"optimized_scores":{"best_composite_score":0.00822,"best_fitness_score":0.11822,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":140.0,"contact_point_centroid":[0.55498,0.05987,0.04585],"force_p95":233.10063,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":233.94324,"mean_force":198.62151,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54383,0.06227,0.04786]},{"body_a":"world","body_b":"push_box","contact_count":1016.0,"contact_point_centroid":[0.54071,0.04021,-0.00025],"force_p95":207.83581,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":221.96134,"mean_force":27.80762,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53788,0.06066,0.06535]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.5479,0.04478,-0.00078],"force_p95":130.68247,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.51263,"mean_force":43.23371,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55251,0.06391,0.04519]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.56343,0.05992,0.044],"force_p95":130.9865,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.26799,"mean_force":128.45311,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55251,0.06391,0.04519]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.56332,0.05987,0.04396],"force_p95":115.43846,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":115.43846,"mean_force":115.43846,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.55242,0.06391,0.04514]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.54789,0.04479,-0.00079],"force_p95":77.31523,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.54626,"mean_force":39.06693,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.55242,0.06391,0.04514]},{"body_a":"world","body_b":"push_box","contact_count":1712.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51626,0.02864,0.20255]}],"total_contact_groups":7},"final_pose_error":0.15385,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54139,0.03872,0.02464],"final_tcp_position":[0.55261,0.06392,0.04528],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":233.94324,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1712.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_behind","tcp_end":[0.53483,0.0591,0.10199],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":289.0,"n_steps_budget":600.0,"object_pos_end":[0.54145,0.03877,0.02462],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19326,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":227.0835,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1156.0,"raw_peak_contact_force":233.94324,"subtask_id":"approach_behind","tcp_end":[0.55242,0.06391,0.04514],"tcp_start":[0.53483,0.0591,0.10199],"tcp_to_object_dist_end":0.03425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":870.0,"object_pos_end":[0.54143,0.03875,0.02462],"object_pos_start":[0.54145,0.03877,0.02462],"object_to_goal_dist_end":0.19325,"object_to_goal_dist_start":0.19326,"object_z_max":0.02462,"peak_contact_force":115.43846,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4.0,"raw_peak_contact_force":115.43846,"subtask_id":"establish_contact","tcp_end":[0.55248,0.06391,0.04516],"tcp_start":[0.55242,0.06391,0.04514],"tcp_to_object_dist_end":0.03431,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.54141,0.03874,0.02462],"object_pos_start":[0.54143,0.03875,0.02462],"object_to_goal_dist_end":0.19322,"object_to_goal_dist_start":0.19325,"object_z_max":0.02462,"peak_contact_force":132.51263,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":132.51263,"subtask_id":"push_to_goal","tcp_end":[0.55261,0.06392,0.04528],"tcp_start":[0.55254,0.06391,0.04521],"tcp_to_object_dist_end":0.03444,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```