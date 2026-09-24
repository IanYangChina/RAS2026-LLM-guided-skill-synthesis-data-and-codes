## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

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

## Current Skill (Q=0.410) — your mutation base

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

- **Composite score**: 0.410
- **task_score** (E): 0.563
- **fitness_score**: 0.610  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_side | 1.00 | 1.00 | 0.2804 |
| push_south_to_goal | 0.00 | 1.00 | 0.1116 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_side | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.075, 0.033) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_south_to_goal | push | 0.00 / guard_failure | (0.496, 0.075, 0.033)→(0.494, -0.036, 0.025) | (0.500, 0.029, 0.025)→(0.505, -0.072, 0.027) | 0.180→0.080 | 1.00 / 3.333 | 24.904 | 27.942 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.650
- lateral_force_integral: None
- approach_alignment: 0.622
- goal_progress: 0.636
- terminal_score: 0.636
- phase_score: 0.691
- phase_breakdown.reach_object_score: 0.820
- phase_breakdown.push_to_goal_score: 0.636

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.669
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.636
- **Median Q (composite search score)**: 0.455
- **K-run variance**: 0.0055
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.494


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.725,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_side.speed":0.12309,"push_south_to_goal.push_distance":0.28802,"push_south_to_goal.push_duration":2.19363,"push_south_to_goal.push_speed":0.0673},"optimized_scores":{"best_composite_score":0.46895,"best_fitness_score":0.66895,"best_task_score":0.63579},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1503.0,"contact_point_centroid":[0.51323,-0.06276,-5e-05],"force_p95":11.12812,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.96578,"mean_force":3.58135,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.49717,-0.01017,0.02849]},{"body_a":"attachment","body_b":"push_box","contact_count":703.0,"contact_point_centroid":[0.50832,-0.03658,0.04605],"force_p95":14.9696,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.18657,"mean_force":5.50531,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.497,-0.02493,0.02767]},{"body_a":"push_box","body_b":"link7","contact_count":181.0,"contact_point_centroid":[0.53178,-0.06339,0.05516],"force_p95":13.02582,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.108,"mean_force":6.08882,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.49742,-0.05094,0.02703]},{"body_a":"world","body_b":"push_box","contact_count":3320.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.49927,0.01452,0.16658]}],"total_contact_groups":4},"final_pose_error":0.23806,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51152,-0.10376,0.02881],"final_tcp_position":[0.49794,-0.06887,0.02681],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":29.96578,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_to_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3320.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.50031,0.02935,0.03377],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":903.0,"n_steps_budget":1000.0,"object_pos_end":[0.51152,-0.10376,0.02881],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.04781,"object_to_goal_dist_start":0.13127,"object_z_max":0.0288,"peak_contact_force":29.96578,"phase_name":"push_south_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2387.0,"raw_peak_contact_force":29.96578,"subtask_id":"push_to_goal","tcp_end":[0.49794,-0.06887,0.02681],"tcp_start":[0.50031,0.02935,0.03377],"tcp_to_object_dist_end":0.03749,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.38333,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_side.speed":0.19749,"push_south_to_goal.push_distance":0.22315,"push_south_to_goal.push_duration":1.77945,"push_south_to_goal.push_speed":0.07702},"optimized_scores":{"best_composite_score":0.30514,"best_fitness_score":0.50514,"best_task_score":0.4356},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1217.0,"contact_point_centroid":[0.52305,-0.00233,-5e-05],"force_p95":10.58629,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.74746,"mean_force":4.01889,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.50736,0.05149,0.02659]},{"body_a":"attachment","body_b":"push_box","contact_count":631.0,"contact_point_centroid":[0.51774,0.02885,0.04462],"force_p95":15.77375,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.82047,"mean_force":5.67546,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.50714,0.04045,0.02581]},{"body_a":"push_box","body_b":"link7","contact_count":154.0,"contact_point_centroid":[0.54234,0.00029,0.05369],"force_p95":14.87374,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.18112,"mean_force":6.38468,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.50768,0.01361,0.02518]},{"body_a":"world","body_b":"push_box","contact_count":3248.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.5043,0.0462,0.1647]}],"total_contact_groups":4},"final_pose_error":0.17086,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52098,-0.04014,0.02805],"final_tcp_position":[0.50829,-0.00475,0.02499],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":28.74746,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":812.0,"n_steps_budget":930.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_to_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3248.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.51024,0.09264,0.03194],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":783.0,"n_steps_budget":1000.0,"object_pos_end":[0.52098,-0.04014,0.02805],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.11188,"object_to_goal_dist_start":0.19823,"object_z_max":0.02804,"peak_contact_force":28.74746,"phase_name":"push_south_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2002.0,"raw_peak_contact_force":28.74746,"subtask_id":"push_to_goal","tcp_end":[0.50829,-0.00475,0.02499],"tcp_start":[0.51024,0.09264,0.03194],"tcp_to_object_dist_end":0.03772,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.18182,"average_solve_count":77.0,"average_success_count":77.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_side.speed":0.15152,"push_south_to_goal.push_distance":0.12966,"push_south_to_goal.push_duration":4.2965,"push_south_to_goal.push_speed":0.08621},"optimized_scores":{"best_composite_score":0.45517,"best_fitness_score":0.65517,"best_task_score":0.61862},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":777.0,"contact_point_centroid":[0.48431,0.01973,0.04256],"force_p95":17.84117,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.11317,"mean_force":4.90483,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.47351,0.03138,0.0251]},{"body_a":"world","body_b":"push_box","contact_count":1426.0,"contact_point_centroid":[0.48372,-0.01099,-5e-05],"force_p95":10.17763,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.64038,"mean_force":3.32203,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.47364,0.04319,0.02597]},{"body_a":"push_box","body_b":"link7","contact_count":145.0,"contact_point_centroid":[0.50709,0.00259,0.05199],"force_p95":11.29283,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.51038,"mean_force":2.93398,"phase_index":1.0,"phase_name":"push_south_to_goal","phase_type":"push","tcp_position_centroid":[0.47375,0.01572,0.02439]},{"body_a":"world","body_b":"push_box","contact_count":3484.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.48728,0.05118,0.16525]}],"total_contact_groups":4},"final_pose_error":0.03617,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48194,-0.07217,0.02488],"final_tcp_position":[0.4746,-0.03543,0.02211],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":25.11317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":871.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_to_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3484.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47618,0.10289,0.03248],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":993.0,"n_steps_budget":1000.0,"object_pos_end":[0.48194,-0.07217,0.02488],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.0799,"object_to_goal_dist_start":0.2095,"object_z_max":0.02684,"peak_contact_force":16.0,"phase_name":"push_south_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2348.0,"raw_peak_contact_force":25.11317,"subtask_id":"push_to_goal","tcp_end":[0.4746,-0.03543,0.02211],"tcp_start":[0.47618,0.10289,0.03248],"tcp_to_object_dist_end":0.03756,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```