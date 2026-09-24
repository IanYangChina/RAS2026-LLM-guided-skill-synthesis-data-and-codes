## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

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

## Current Skill (Q=-0.087) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.0
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_to_side
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.0
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: push_south_to_goal
  type: push
  generator: impedance_motion
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
      distance: 0.2
      axis: world_y
      mode: add_to_offset
      sign: negative
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 1.5
      - 5.0
      default: 3.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: max_force
    when: during_phase
    predicate: force_below
    args:
      force_limit: 25.0
    threshold: 25.0
    on_failure: abort
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_side** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.0]
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_south_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.2, mode=add_to_offset, sign=negative}
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=max_force, when=during_phase, predicate=force_below, on_failure=abort, threshold=25.0, args={'force_limit': 25.0}

## Design Metrics

- **Composite score**: -0.087
- **task_score** (E): 0.000
- **fitness_score**: 0.113  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_side | 1.00 | 1.00 | 0.2616 |
| push_south_to_goal | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_side | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.052, 0.047) | (0.500, 0.029, 0.025)→(0.503, 0.031, 0.024) | 0.180→0.182 | 1.00 / 4.000 | 258.436 | 271.819 |
| push_south_to_goal | push | 0.00 / guard_failure | (0.507, 0.052, 0.047)→(0.507, 0.052, 0.047) | (0.503, 0.031, 0.024)→(0.503, 0.031, 0.024) | 0.182→0.182 | 1.00 / 4.000 | 110.376 | 110.376 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.029
- lateral_force_integral: None
- approach_alignment: 0.485
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.191
- phase_breakdown.reach_object_score: 0.636
- phase_breakdown.push_to_goal_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.115
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.086
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at lower bound**: push_south_to_goal.push_duration
- **Parameters at upper bound**: approach_to_side.speed
- **Final σ (mean)**: 0.316


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.73333,"average_solve_count":30.0,"average_success_count":30.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_side.speed":0.19931,"push_south_to_goal.push_distance":0.14803,"push_south_to_goal.push_duration":2.91773,"push_south_to_goal.push_speed":0.07788},"optimized_scores":{"best_composite_score":-0.08542,"best_fitness_score":0.11458,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":65.0,"contact_point_centroid":[0.51598,0.00518,0.04649],"force_p95":267.43061,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":269.84626,"mean_force":221.71149,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.50506,0.00642,0.04969]},{"body_a":"world","body_b":"push_box","contact_count":2890.0,"contact_point_centroid":[0.50518,-0.01829,-4e-05],"force_p95":17.31336,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":246.97315,"mean_force":5.28147,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.49965,0.00287,0.16865]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.52228,0.00513,0.0443],"force_p95":111.69154,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":111.69154,"mean_force":111.69154,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.51135,0.00743,0.04652]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.5148,-0.01114,-0.00088],"force_p95":76.57333,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.87285,"mean_force":37.58275,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.51135,0.00743,0.04652]}],"total_contact_groups":4},"final_pose_error":0.17435,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50802,-0.01743,0.02431],"final_tcp_position":[0.51148,0.00744,0.04653],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":269.84626,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":738.0,"n_steps_budget":870.0,"object_pos_end":[0.50805,-0.01743,0.0243],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13282,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":259.30587,"phase_name":"approach_to_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2955.0,"raw_peak_contact_force":269.84626,"subtask_id":"reach_object","tcp_end":[0.51135,0.00743,0.04652],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50802,-0.01743,0.02431],"object_pos_start":[0.50805,-0.01743,0.0243],"object_to_goal_dist_end":0.13281,"object_to_goal_dist_start":0.13282,"object_z_max":0.0243,"peak_contact_force":111.69154,"phase_name":"push_south_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":111.69154,"subtask_id":"push_to_goal","tcp_end":[0.51148,0.00744,0.04653],"tcp_start":[0.51135,0.00743,0.04652],"tcp_to_object_dist_end":0.03353,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.74194,"average_solve_count":31.0,"average_success_count":31.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_side.speed":0.2,"push_south_to_goal.push_distance":0.1885,"push_south_to_goal.push_duration":1.50015,"push_south_to_goal.push_speed":0.09085},"optimized_scores":{"best_composite_score":-0.08629,"best_fitness_score":0.11371,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":71.0,"contact_point_centroid":[0.52593,0.06518,0.04678],"force_p95":263.42035,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":271.83688,"mean_force":217.2785,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.51486,0.06628,0.04962]},{"body_a":"world","body_b":"push_box","contact_count":3064.0,"contact_point_centroid":[0.51564,0.04824,-4e-05],"force_p95":26.79311,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":244.64917,"mean_force":5.32555,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.50454,0.0337,0.16778]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53291,0.06732,0.04483],"force_p95":110.80242,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":110.80242,"mean_force":110.80242,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.52183,0.06967,0.04673]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.52555,0.0567,-0.00087],"force_p95":74.02155,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.20091,"mean_force":37.31303,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.52183,0.06967,0.04673]}],"total_contact_groups":4},"final_pose_error":0.20923,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51876,0.05022,0.02427],"final_tcp_position":[0.52197,0.06972,0.04674],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":271.83688,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":783.0,"n_steps_budget":900.0,"object_pos_end":[0.51879,0.05022,0.02427],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.2011,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":254.74977,"phase_name":"approach_to_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3135.0,"raw_peak_contact_force":271.83688,"subtask_id":"reach_object","tcp_end":[0.52183,0.06967,0.04673],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.51876,0.05022,0.02427],"object_pos_start":[0.51879,0.05022,0.02427],"object_to_goal_dist_end":0.2011,"object_to_goal_dist_start":0.2011,"object_z_max":0.02427,"peak_contact_force":110.80242,"phase_name":"push_south_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":110.80242,"subtask_id":"push_to_goal","tcp_end":[0.52197,0.06972,0.04674],"tcp_start":[0.52183,0.06967,0.04673],"tcp_to_object_dist_end":0.02992,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.74194,"average_solve_count":31.0,"average_success_count":31.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_side.speed":0.19999,"push_south_to_goal.push_distance":0.17785,"push_south_to_goal.push_duration":2.06915,"push_south_to_goal.push_speed":0.0689},"optimized_scores":{"best_composite_score":-0.08898,"best_fitness_score":0.11102,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":72.0,"contact_point_centroid":[0.49332,0.07536,0.04658],"force_p95":269.38448,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":273.77267,"mean_force":221.73103,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.48256,0.07597,0.05017]},{"body_a":"world","body_b":"push_box","contact_count":3047.0,"contact_point_centroid":[0.47985,0.05907,-5e-05],"force_p95":25.8027,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":247.15617,"mean_force":5.52172,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.48793,0.03868,0.16815]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49932,0.07822,0.04441],"force_p95":108.63501,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.63501,"mean_force":108.63501,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.48846,0.07989,0.04704]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.48903,0.06764,-0.00089],"force_p95":61.92866,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.03559,"mean_force":36.8132,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.48846,0.07989,0.04704]}],"total_contact_groups":4},"final_pose_error":0.19799,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48246,0.06121,0.02429],"final_tcp_position":[0.48857,0.07995,0.04705],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":273.77267,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":779.0,"n_steps_budget":900.0,"object_pos_end":[0.48248,0.06121,0.02429],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.21194,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":261.25176,"phase_name":"approach_to_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3119.0,"raw_peak_contact_force":273.77267,"subtask_id":"reach_object","tcp_end":[0.48846,0.07989,0.04704],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03004,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.48246,0.06121,0.02429],"object_pos_start":[0.48248,0.06121,0.02429],"object_to_goal_dist_end":0.21194,"object_to_goal_dist_start":0.21194,"object_z_max":0.02429,"peak_contact_force":108.63501,"phase_name":"push_south_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":108.63501,"subtask_id":"push_to_goal","tcp_end":[0.48857,0.07995,0.04705],"tcp_start":[0.48846,0.07989,0.04704],"tcp_to_object_dist_end":0.03011,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```