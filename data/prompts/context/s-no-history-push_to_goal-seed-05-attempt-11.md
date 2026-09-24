## Search State

- **Seed**: 5
- **Iteration**: 12 / 15

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
- Frozen realised-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`
- Frozen object start: [0.5366003508494456, 0.03695289476837925, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5366003508494456, 0.03695289476837925, 0.025)
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
  frozen_object_start: [0.5366, 0.037, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5366003508494456, 0.03695289476837925, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

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
| `object` | offset from object initial position (0.5366003508494456, 0.03695289476837925, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=-0.167) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_behind
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: reach_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_behind
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
    - 0.1
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_behind_distance:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: reach_behind
- id: descend_behind
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
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_behind_distance:
      type: scalar
      range:
      - 0.03
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.01
    - 0.01
    - 0.0
  subtask_id: reach_behind
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.005
    - 0.0
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.0]
- **descend_behind** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.01, 0.01, 0.0]
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=25.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.005, 0.0]

## Design Metrics

- **Composite score**: -0.167
- **task_score** (E): 0.055
- **fitness_score**: 0.063  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1883 |
| descend_behind | 1.00 | 1.00 | 0.1180 |
| push_to_goal | 0.00 | 1.00 | 0.0002 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.522, 0.087, 0.147) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_behind | descend | 1.00 / step_budget | (0.522, 0.087, 0.147)→(0.518, 0.056, 0.033) | (0.519, 0.022, 0.025)→(0.519, 0.019, 0.025) | 0.173→0.171 | 1.00 / 3.667 | 1.323 | 82.427 |
| push_to_goal | push | 0.00 / guard_failure | (0.516, 0.050, 0.031)→(0.516, 0.049, 0.031) | (0.519, 0.019, 0.025)→(0.518, 0.013, 0.025) | 0.171→0.164 | 1.00 / 2.667 | 0.554 | 37.022 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.078
- lateral_force_integral: None
- approach_alignment: 0.384
- goal_progress: 0.078
- terminal_score: 0.078
- phase_score: 0.084
- phase_breakdown.reach_behind_score: 0.141
- phase_breakdown.reach_goal_score: 0.059

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.081
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.078
- **Median Q (composite search score)**: -0.174
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.339


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72289,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_behind_distance":0.07531,"approach_behind.approach_height":0.13452,"descend_behind.descend_behind_distance":0.03068,"push_to_goal.push_speed":0.06085},"optimized_scores":{"best_composite_score":-0.14869,"best_fitness_score":0.08131,"best_task_score":0.07782},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.53899,0.06073,0.04152],"force_p95":34.54229,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.3085,"mean_force":23.81507,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.53903,0.07271,0.04147]},{"body_a":"attachment","body_b":"push_box","contact_count":23.0,"contact_point_centroid":[0.53947,0.0547,0.04299],"force_p95":29.59599,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.83129,"mean_force":6.81827,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53664,0.06653,0.03128]},{"body_a":"world","body_b":"push_box","contact_count":47.0,"contact_point_centroid":[0.5417,0.01931,-7e-05],"force_p95":14.01902,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.87062,"mean_force":3.71242,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53708,0.06722,0.03165]},{"body_a":"world","body_b":"push_box","contact_count":1565.0,"contact_point_centroid":[0.53661,0.0365,-1e-05],"force_p95":0.46169,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.74848,"mean_force":0.56614,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.54081,0.08766,0.09909]},{"body_a":"world","body_b":"push_box","contact_count":2660.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52157,0.05168,0.22961]}],"total_contact_groups":5},"final_pose_error":0.21239,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5349,0.02218,0.02508],"final_tcp_position":[0.53458,0.0595,0.02979],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":36.3085,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":665.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2660.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_behind","tcp_end":[0.5449,0.10356,0.16228],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":404.0,"n_steps_budget":900.0,"object_pos_end":[0.53731,0.03364,0.02485],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1874,"object_to_goal_dist_start":0.1905,"object_z_max":0.02503,"peak_contact_force":0.45027,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1586.0,"raw_peak_contact_force":36.3085,"subtask_id":"reach_behind","tcp_end":[0.5389,0.07084,0.0333],"tcp_start":[0.5449,0.10356,0.16228],"tcp_to_object_dist_end":0.03818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":35.0,"n_steps_budget":1000.0,"object_pos_end":[0.53494,0.02287,0.02501],"object_pos_start":[0.53731,0.03364,0.02485],"object_to_goal_dist_end":0.17637,"object_to_goal_dist_start":0.1874,"object_z_max":0.0253,"peak_contact_force":1.66007,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":70.0,"raw_peak_contact_force":34.83129,"subtask_id":"reach_goal","tcp_end":[0.53458,0.0595,0.02979],"tcp_start":[0.53462,0.05973,0.02987],"tcp_to_object_dist_end":0.03694,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76712,"average_solve_count":73.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_behind_distance":0.04234,"approach_behind.approach_height":0.06318,"descend_behind.descend_behind_distance":0.03023,"push_to_goal.push_speed":0.07875},"optimized_scores":{"best_composite_score":-0.17387,"best_fitness_score":0.05613,"best_task_score":0.05431},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":43.0,"contact_point_centroid":[0.50614,0.00518,0.04651],"force_p95":172.05762,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":182.67384,"mean_force":86.47437,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.50242,0.01572,0.04629]},{"body_a":"world","body_b":"push_box","contact_count":823.0,"contact_point_centroid":[0.50469,-0.01989,-5e-05],"force_p95":28.71365,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.43906,"mean_force":4.7951,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.50122,0.01806,0.06653]},{"body_a":"attachment","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.50424,0.00051,0.04469],"force_p95":41.18127,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.16859,"mean_force":12.42598,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50163,0.01226,0.03261]},{"body_a":"world","body_b":"push_box","contact_count":32.0,"contact_point_centroid":[0.49799,-0.02707,-8e-05],"force_p95":18.87899,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.37438,"mean_force":4.11558,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50186,0.01279,0.0329]},{"body_a":"world","body_b":"push_box","contact_count":2576.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50026,0.01072,0.19847]}],"total_contact_groups":5},"final_pose_error":0.16065,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50418,-0.02593,0.02499],"final_tcp_position":[0.50122,0.01049,0.03203],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":182.67384,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":644.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2576.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_behind","tcp_end":[0.50229,0.0218,0.09713],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":224.0,"n_steps_budget":600.0,"object_pos_end":[0.50422,-0.02279,0.02477],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.13127,"object_z_max":0.02511,"peak_contact_force":1.52004,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":866.0,"raw_peak_contact_force":182.67384,"subtask_id":"reach_behind","tcp_end":[0.50263,0.01423,0.03395],"tcp_start":[0.50229,0.0218,0.09713],"tcp_to_object_dist_end":0.03818,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.50418,-0.02536,0.02495],"object_pos_start":[0.50422,-0.02279,0.02477],"object_to_goal_dist_end":0.12471,"object_to_goal_dist_start":0.12728,"object_z_max":0.02516,"peak_contact_force":0.0012,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":42.0,"raw_peak_contact_force":44.16859,"subtask_id":"reach_goal","tcp_end":[0.50122,0.01049,0.03203],"tcp_start":[0.50128,0.01069,0.03211],"tcp_to_object_dist_end":0.03666,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67778,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_behind_distance":0.09719,"approach_behind.approach_height":0.15498,"descend_behind.descend_behind_distance":0.03276,"push_to_goal.push_speed":0.02647},"optimized_scores":{"best_composite_score":-0.17871,"best_fitness_score":0.05129,"best_task_score":0.03399},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":23.0,"contact_point_centroid":[0.51522,0.07008,0.04358],"force_p95":28.633,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.06506,"mean_force":4.65038,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5124,0.08193,0.03167]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.5136,0.07257,0.03362],"force_p95":28.19132,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.29731,"mean_force":26.85437,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.51361,0.08449,0.03357]},{"body_a":"world","body_b":"push_box","contact_count":36.0,"contact_point_centroid":[0.51276,0.04211,-4e-05],"force_p95":16.63423,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.1951,"mean_force":3.25025,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51236,0.08181,0.03163]},{"body_a":"world","body_b":"push_box","contact_count":1948.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.73198,"mean_force":0.28597,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.51491,0.11039,0.10697]},{"body_a":"world","body_b":"push_box","contact_count":2792.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50824,0.06794,0.23892]}],"total_contact_groups":5},"final_pose_error":0.22834,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51361,0.04101,0.02488],"final_tcp_position":[0.5114,0.07798,0.03058],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":32.06506,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":698.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2792.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_behind","tcp_end":[0.51824,0.13563,0.18144],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":487.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.0476,0.025],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19817,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":2.0,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1951.0,"raw_peak_contact_force":28.29731,"subtask_id":"reach_behind","tcp_end":[0.51361,0.08435,0.03306],"tcp_start":[0.51824,0.13563,0.18144],"tcp_to_object_dist_end":0.03765,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":25.0,"n_steps_budget":1000.0,"object_pos_end":[0.51358,0.04163,0.02489],"object_pos_start":[0.51501,0.0476,0.025],"object_to_goal_dist_end":0.19211,"object_to_goal_dist_start":0.19817,"object_z_max":0.02517,"peak_contact_force":0.0009,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":59.0,"raw_peak_contact_force":32.06506,"subtask_id":"reach_goal","tcp_end":[0.5114,0.07798,0.03058],"tcp_start":[0.51144,0.0782,0.03066],"tcp_to_object_dist_end":0.03686,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```