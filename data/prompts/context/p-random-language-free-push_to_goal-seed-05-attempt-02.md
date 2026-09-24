## Search State

- **Seed**: 5
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 6 | 0.6796 | 0.33 | ✅ accepted |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | 0.2209 | 0.33 | ✅ accepted |
| 0 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.3000 | 0.00 | ✅ accepted |

**Proposal policy**: task_score is 0.33 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.680) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  weight: 0.3
- id: push_complete
  target_entity: object
  weight: 0.7
phases:
- id: approach
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
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: push
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.45
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.45
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push_complete

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **contact** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.45, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.680
- **task_score** (E): 0.332
- **fitness_score**: 0.510  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1501 |
| contact | 1.00 | 1.00 | 0.1031 |
| push | 1.00 | 1.00 | 0.1531 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.020, 0.155) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact | contact | 1.00 / force_exceeded | (0.514, 0.020, 0.155)→(0.514, 0.021, 0.052) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 5.000 | 51.450 | 0.245 |
| push | push | 1.00 / time_limit | (0.514, 0.021, 0.052)→(0.496, -0.129, 0.031) | (0.519, 0.022, 0.025)→(0.513, -0.034, 0.025) | 0.173→0.118 | 1.00 / 4.000 | 0.245 | 110.565 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.412
- lateral_force_integral: None
- approach_alignment: 0.736
- goal_progress: 0.412
- terminal_score: 0.412
- phase_score: 0.797
- phase_breakdown.reach_contact_score: 0.574
- phase_breakdown.push_complete_score: 0.893

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.643
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.412
- **Median Q (composite search score)**: 0.634
- **K-run variance**: 0.0092
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at lower bound**: contact.contact_speed
- **Final σ (mean)**: 0.403


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78696,"average_solve_count":230.0,"average_success_count":230.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.11486,"approach.speed":0.03501,"contact.contact_force_threshold":4.67931,"contact.contact_speed":0.01,"push.push_depth":0.36393,"push.push_speed":0.09996},"optimized_scores":{"best_composite_score":0.63413,"best_fitness_score":0.46413,"best_task_score":0.30191},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":479.0,"contact_point_centroid":[0.53211,0.00637,0.04888],"force_p95":91.33803,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.69252,"mean_force":56.24196,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52479,-0.00125,0.04966]},{"body_a":"world","body_b":"push_box","contact_count":2881.0,"contact_point_centroid":[0.53033,-0.0079,-0.00011],"force_p95":46.67607,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.09518,"mean_force":9.68088,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51205,-0.05524,0.04223]},{"body_a":"world","body_b":"push_box","contact_count":2344.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51408,0.01654,0.2235]},{"body_a":"world","body_b":"push_box","contact_count":2360.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.52938,0.03471,0.09787]}],"total_contact_groups":4},"final_pose_error":0.19879,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52811,-0.02002,0.02499],"final_tcp_position":[0.49796,-0.12414,0.0351],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":94.69252,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2344.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.53061,0.03385,0.14697],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":590.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":52.32354,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2360.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.53094,0.03578,0.05247],"tcp_start":[0.53061,0.03385,0.14697],"tcp_to_object_dist_end":0.02809,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52811,-0.02002,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.13299,"object_to_goal_dist_start":0.1905,"object_z_max":0.03521,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3360.0,"raw_peak_contact_force":94.69252,"subtask_id":"push_complete","tcp_end":[0.49796,-0.12414,0.0351],"tcp_start":[0.53094,0.03578,0.05247],"tcp_to_object_dist_end":0.10888,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.04023,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.12845,"approach.speed":0.08047,"contact.contact_force_threshold":5.39135,"contact.contact_speed":0.01966,"push.push_depth":0.16275,"push.push_speed":0.07853},"optimized_scores":{"best_composite_score":0.81325,"best_fitness_score":0.64325,"best_task_score":0.41219},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":621.0,"contact_point_centroid":[0.50979,-0.04999,0.04647],"force_p95":124.09692,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.83675,"mean_force":79.46665,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50158,-0.05633,0.04716]},{"body_a":"world","body_b":"push_box","contact_count":2710.0,"contact_point_centroid":[0.50403,-0.05684,-0.0002],"force_p95":79.54061,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.62428,"mean_force":18.55886,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49843,-0.08867,0.03864]},{"body_a":"world","body_b":"push_box","contact_count":1784.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49983,-0.00824,0.23177]},{"body_a":"world","body_b":"push_box","contact_count":2740.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.49927,-0.01765,0.10579]}],"total_contact_groups":4},"final_pose_error":0.0344,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50145,-0.07285,0.02499],"final_tcp_position":[0.49508,-0.14728,0.02556],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":134.83675,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":446.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1784.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.50127,-0.01699,0.16251],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13758,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":685.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":49.70665,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2740.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.49996,-0.01834,0.0524],"tcp_start":[0.50127,-0.01699,0.16251],"tcp_to_object_dist_end":0.0278,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50145,-0.07285,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.07716,"object_to_goal_dist_start":0.13127,"object_z_max":0.03535,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3331.0,"raw_peak_contact_force":134.83675,"subtask_id":"push_complete","tcp_end":[0.49508,-0.14728,0.02556],"tcp_start":[0.49996,-0.01834,0.0524],"tcp_to_object_dist_end":0.0747,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.70213,"average_solve_count":235.0,"average_success_count":235.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.12404,"approach.speed":0.02212,"contact.contact_force_threshold":8.17081,"contact.contact_speed":0.02807,"push.push_depth":0.32287,"push.push_speed":0.09995},"optimized_scores":{"best_composite_score":0.59131,"best_fitness_score":0.42131,"best_task_score":0.28146},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":472.0,"contact_point_centroid":[0.51573,0.01716,0.04852],"force_p95":97.81879,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.165,"mean_force":59.87052,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50845,0.00951,0.04933]},{"body_a":"world","body_b":"push_box","contact_count":2875.0,"contact_point_centroid":[0.51207,0.00276,-0.00011],"force_p95":53.24548,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.44734,"mean_force":10.15114,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.50198,-0.04682,0.04127]},{"body_a":"world","body_b":"push_box","contact_count":2220.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50431,0.02109,0.22866]},{"body_a":"world","body_b":"push_box","contact_count":2572.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact","phase_type":"contact","tcp_position_centroid":[0.50903,0.04466,0.10286]}],"total_contact_groups":4},"final_pose_error":0.15906,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51062,-0.00796,0.02499],"final_tcp_position":[0.49621,-0.11555,0.0336],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":102.165,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2220.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.51071,0.04336,0.15686],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":643.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":52.32049,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2572.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.51003,0.0462,0.05238],"tcp_start":[0.51071,0.04336,0.15686],"tcp_to_object_dist_end":0.02787,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51062,-0.00796,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.14244,"object_to_goal_dist_start":0.19823,"object_z_max":0.03525,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3347.0,"raw_peak_contact_force":102.165,"subtask_id":"push_complete","tcp_end":[0.49621,-0.11555,0.0336],"tcp_start":[0.51003,0.0462,0.05238],"tcp_to_object_dist_end":0.1089,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```