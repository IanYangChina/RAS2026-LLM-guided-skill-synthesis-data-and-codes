## Search State

- **Seed**: 7
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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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
| `object` | offset from object initial position (0.51501145599256, 0.047665656116349056, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.501) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: reach_goal
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
    - 0.03
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
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
      distance: 0.02
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
      - 0.0
      - 0.05
      default: 0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_side** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.501
- **task_score** (E): 0.381
- **fitness_score**: 0.651  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.150

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_side | 1.00 | 1.00 | 0.2661 |
| push_to_goal | 1.00 | 1.00 | 0.2097 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_side | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.055, 0.045) | (0.513, 0.027, 0.025)→(0.517, 0.029, 0.024) | 0.180→0.182 | 1.00 / 4.000 | 213.486 | 225.755 |
| push_to_goal | push | 1.00 / step_budget | (0.521, 0.055, 0.045)→(0.497, -0.149, 0.022) | (0.517, 0.029, 0.024)→(0.507, -0.039, 0.025) | 0.182→0.114 | 1.00 / 4.000 | 0.244 | 171.760 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.487
- lateral_force_integral: None
- approach_alignment: 0.724
- goal_progress: 0.478
- terminal_score: 0.478
- phase_score: 0.837
- phase_breakdown.reach_contact_score: 0.658
- phase_breakdown.reach_goal_score: 0.914

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.694
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.478
- **Median Q (composite search score)**: 0.480
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.254


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37624,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_side.approach_speed":0.07157,"push_to_goal.push_distance":0.01946,"push_to_goal.push_speed":0.03524},"optimized_scores":{"best_composite_score":0.47989,"best_fitness_score":0.62989,"best_task_score":0.33249},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":139.0,"contact_point_centroid":[0.5288,0.06847,0.04636],"force_p95":241.29916,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":241.83383,"mean_force":197.75818,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.518,0.07285,0.04653]},{"body_a":"world","body_b":"push_box","contact_count":3863.0,"contact_point_centroid":[0.51606,0.0486,-7e-05],"force_p95":30.53206,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":212.8233,"mean_force":7.41346,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.50531,0.03799,0.16144]},{"body_a":"attachment","body_b":"push_box","contact_count":577.0,"contact_point_centroid":[0.53674,0.0306,0.04667],"force_p95":168.97684,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":171.31697,"mean_force":143.71375,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52675,0.02698,0.04654]},{"body_a":"world","body_b":"push_box","contact_count":2462.0,"contact_point_centroid":[0.51773,0.00953,-0.0004],"force_p95":137.71294,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":153.9127,"mean_force":34.193,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51749,-0.02136,0.03858]}],"total_contact_groups":4},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5087,-0.01796,0.02499],"final_tcp_position":[0.49653,-0.14984,0.02148],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":241.83383,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51951,0.05043,0.02434],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.20137,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":240.75432,"phase_name":"approach_to_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4002.0,"raw_peak_contact_force":241.83383,"subtask_id":"reach_contact","tcp_end":[0.52612,0.07683,0.04374],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03342,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":860.0,"n_steps_budget":1000.0,"object_pos_end":[0.5087,-0.01796,0.02499],"object_pos_start":[0.51951,0.05043,0.02434],"object_to_goal_dist_end":0.13232,"object_to_goal_dist_start":0.20137,"object_z_max":0.03528,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3039.0,"raw_peak_contact_force":171.31697,"subtask_id":"reach_goal","tcp_end":[0.49653,-0.14984,0.02148],"tcp_start":[0.52612,0.07683,0.04374],"tcp_to_object_dist_end":0.13248,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98305,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_side.approach_speed":0.03816,"push_to_goal.push_distance":0.0183,"push_to_goal.push_speed":0.02751},"optimized_scores":{"best_composite_score":0.47976,"best_fitness_score":0.62976,"best_task_score":0.33161},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":89.0,"contact_point_centroid":[0.49342,0.07815,0.04714],"force_p95":200.25685,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":215.63299,"mean_force":165.96252,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.48206,0.08111,0.04786]},{"body_a":"world","body_b":"push_box","contact_count":3913.0,"contact_point_centroid":[0.47984,0.05905,-4e-05],"force_p95":14.44146,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":192.03609,"mean_force":4.04423,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.4877,0.04153,0.16646]},{"body_a":"world","body_b":"push_box","contact_count":1939.0,"contact_point_centroid":[0.49051,0.01185,-0.00042],"force_p95":156.19993,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":170.3296,"mean_force":37.17054,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49459,-0.03567,0.03583]},{"body_a":"attachment","body_b":"push_box","contact_count":498.0,"contact_point_centroid":[0.50515,0.03802,0.0466],"force_p95":166.8893,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":169.22936,"mean_force":142.70449,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49554,0.03332,0.04665]}],"total_contact_groups":4},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48048,-0.01134,0.02499],"final_tcp_position":[0.49681,-0.14947,0.02151],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":215.63299,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48179,0.06059,0.02438],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.21138,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":200.26167,"phase_name":"approach_to_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4002.0,"raw_peak_contact_force":215.63299,"subtask_id":"reach_contact","tcp_end":[0.4863,0.08386,0.04566],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":801.0,"n_steps_budget":1000.0,"object_pos_end":[0.48048,-0.01134,0.02499],"object_pos_start":[0.48179,0.06059,0.02438],"object_to_goal_dist_end":0.14003,"object_to_goal_dist_start":0.21138,"object_z_max":0.03724,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2437.0,"raw_peak_contact_force":170.3296,"subtask_id":"reach_goal","tcp_end":[0.49681,-0.14947,0.02151],"tcp_start":[0.4863,0.08386,0.04566],"tcp_to_object_dist_end":0.13914,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9789,"average_solve_count":237.0,"average_success_count":237.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_side.approach_speed":0.02296,"push_to_goal.push_distance":0.01955,"push_to_goal.push_speed":0.01095},"optimized_scores":{"best_composite_score":0.5436,"best_fitness_score":0.6936,"best_task_score":0.47803},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":110.0,"contact_point_centroid":[0.55355,0.00047,0.04687],"force_p95":200.39353,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":219.79834,"mean_force":169.18256,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.54263,0.00501,0.04741]},{"body_a":"world","body_b":"push_box","contact_count":3846.0,"contact_point_centroid":[0.54493,-0.02462,-5e-05],"force_p95":30.19175,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":201.68017,"mean_force":5.12602,"phase_index":0.0,"phase_name":"approach_to_side","phase_type":"approach","tcp_position_centroid":[0.5184,0.0021,0.16612]},{"body_a":"attachment","body_b":"push_box","contact_count":695.0,"contact_point_centroid":[0.55062,-0.04189,0.04703],"force_p95":172.76051,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.63433,"mean_force":148.69382,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54027,-0.04497,0.04705]},{"body_a":"world","body_b":"push_box","contact_count":2437.0,"contact_point_centroid":[0.54432,-0.04646,-0.00049],"force_p95":96.28697,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.07015,"mean_force":42.84408,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53745,-0.04876,0.04507]}],"total_contact_groups":4},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5315,-0.08866,0.02485],"final_tcp_position":[0.49619,-0.14864,0.02306],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":219.79834,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54832,-0.02494,0.02453],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13407,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":199.44101,"phase_name":"approach_to_side","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3956.0,"raw_peak_contact_force":219.79834,"subtask_id":"reach_contact","tcp_end":[0.54932,0.00556,0.04531],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03692,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":809.0,"n_steps_budget":1000.0,"object_pos_end":[0.5315,-0.08866,0.02485],"object_pos_start":[0.54832,-0.02494,0.02453],"object_to_goal_dist_end":0.06896,"object_to_goal_dist_start":0.13407,"object_z_max":0.03549,"peak_contact_force":0.2419,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3132.0,"raw_peak_contact_force":173.63433,"subtask_id":"reach_goal","tcp_end":[0.49619,-0.14864,0.02306],"tcp_start":[0.54932,0.00556,0.04531],"tcp_to_object_dist_end":0.06963,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```