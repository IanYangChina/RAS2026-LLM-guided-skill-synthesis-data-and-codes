## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
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

## Current Skill (Q=0.221) — your mutation base

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
- id: descend
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
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: push
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
      distance: 0.3
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
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
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
- **descend** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.3, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.221
- **task_score** (E): 0.328
- **fitness_score**: 0.501  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1280 |
| descend | 1.00 | 1.00 | 0.1339 |
| push | 1.00 | 1.00 | 0.1545 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.020, 0.178) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend | descend | 1.00 / step_budget | (0.514, 0.020, 0.178)→(0.532, 0.022, 0.045) | (0.519, 0.022, 0.025)→(0.524, 0.022, 0.024) | 0.173→0.174 | 1.00 / 3.667 | 219.054 | 235.406 |
| push | push | 1.00 / time_limit | (0.532, 0.022, 0.045)→(0.504, -0.129, 0.033) | (0.524, 0.022, 0.024)→(0.515, -0.033, 0.025) | 0.174→0.119 | 1.00 / 4.000 | 0.245 | 133.122 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.433
- lateral_force_integral: None
- approach_alignment: 0.747
- goal_progress: 0.433
- terminal_score: 0.433
- phase_score: 0.757
- phase_breakdown.reach_contact_score: 0.600
- phase_breakdown.push_complete_score: 0.825

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.627
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.433
- **Median Q (composite search score)**: 0.172
- **K-run variance**: 0.0082
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.379


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.62667,"average_solve_count":225.0,"average_success_count":225.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.11073,"approach.speed":0.04625,"descend.descend_speed":0.01062,"push.push_depth":0.45094,"push.push_speed":0.09999},"optimized_scores":{"best_composite_score":0.17245,"best_fitness_score":0.45245,"best_task_score":0.27912},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":419.0,"contact_point_centroid":[0.55258,0.03669,0.04754],"force_p95":193.48875,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":208.31946,"mean_force":148.27706,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.54076,0.03666,0.04831]},{"body_a":"attachment","body_b":"push_box","contact_count":481.0,"contact_point_centroid":[0.54917,0.00836,0.04732],"force_p95":114.60911,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":119.61117,"mean_force":82.18964,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.54135,0.00133,0.04743]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.53744,0.03704,-0.00017],"force_p95":78.02223,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.61095,"mean_force":15.80049,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.53412,0.03553,0.07597]},{"body_a":"world","body_b":"push_box","contact_count":2949.0,"contact_point_centroid":[0.53352,-0.00397,-0.00016],"force_p95":77.25969,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.95168,"mean_force":13.74788,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52496,-0.05134,0.04016]},{"body_a":"world","body_b":"push_box","contact_count":2380.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.5141,0.01658,0.22146]}],"total_contact_groups":5},"final_pose_error":0.28833,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52954,-0.01589,0.02499],"final_tcp_position":[0.50621,-0.1218,0.03413],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":208.31946,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2380.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.5306,0.03387,0.14305],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11825,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54034,0.03729,0.02393],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19159,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":199.8884,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4419.0,"raw_peak_contact_force":208.31946,"subtask_id":"reach_contact","tcp_end":[0.54708,0.03725,0.04647],"tcp_start":[0.5306,0.03387,0.14305],"tcp_to_object_dist_end":0.02353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52954,-0.01589,0.02499],"object_pos_start":[0.54034,0.03729,0.02393],"object_to_goal_dist_end":0.13733,"object_to_goal_dist_start":0.19159,"object_z_max":0.03541,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3430.0,"raw_peak_contact_force":119.61117,"subtask_id":"push_complete","tcp_end":[0.50621,-0.1218,0.03413],"tcp_start":[0.54708,0.03725,0.04647],"tcp_to_object_dist_end":0.10883,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54745,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.17084,"approach.speed":0.04239,"descend.descend_speed":0.07715,"push.push_depth":0.47226,"push.push_speed":0.05607},"optimized_scores":{"best_composite_score":0.34745,"best_fitness_score":0.62745,"best_task_score":0.43265},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":190.0,"contact_point_centroid":[0.5207,-0.01863,0.04699],"force_p95":248.65424,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":248.90825,"mean_force":190.44043,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50885,-0.01874,0.04746]},{"body_a":"attachment","body_b":"push_box","contact_count":606.0,"contact_point_centroid":[0.52749,-0.0488,0.04626],"force_p95":119.75608,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.59167,"mean_force":91.97014,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52014,-0.05714,0.04611]},{"body_a":"world","body_b":"push_box","contact_count":3854.0,"contact_point_centroid":[0.50526,-0.01884,-9e-05],"force_p95":89.164,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":125.48181,"mean_force":9.67396,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50111,-0.01755,0.11216]},{"body_a":"world","body_b":"push_box","contact_count":2555.0,"contact_point_centroid":[0.50915,-0.05797,-0.00025],"force_p95":106.78941,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.66124,"mean_force":22.23107,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51238,-0.09485,0.0404]},{"body_a":"world","body_b":"push_box","contact_count":1340.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49987,-0.00777,0.25314]}],"total_contact_groups":5},"final_pose_error":0.33937,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5024,-0.07556,0.02499],"final_tcp_position":[0.50284,-0.15188,0.03402],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":248.90825,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1340.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.50133,-0.01629,0.20475],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.51083,-0.01906,0.02505],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13139,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":216.16484,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4044.0,"raw_peak_contact_force":248.90825,"subtask_id":"reach_contact","tcp_end":[0.52064,-0.01924,0.04482],"tcp_start":[0.50133,-0.01629,0.20475],"tcp_to_object_dist_end":0.02207,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5024,-0.07556,0.02499],"object_pos_start":[0.51083,-0.01906,0.02505],"object_to_goal_dist_end":0.07448,"object_to_goal_dist_start":0.13139,"object_z_max":0.03541,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3161.0,"raw_peak_contact_force":135.59167,"subtask_id":"push_complete","tcp_end":[0.50284,-0.15188,0.03402],"tcp_start":[0.52064,-0.01924,0.04482],"tcp_to_object_dist_end":0.07685,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90566,"average_solve_count":106.0,"average_success_count":106.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_height":0.15401,"approach.speed":0.08154,"descend.descend_speed":0.09481,"push.push_depth":0.40175,"push.push_speed":0.09956},"optimized_scores":{"best_composite_score":0.14287,"best_fitness_score":0.42287,"best_task_score":0.27175},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":160.0,"contact_point_centroid":[0.52989,0.04715,0.04711],"force_p95":247.24545,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":248.9914,"mean_force":189.99786,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.51805,0.04715,0.04768]},{"body_a":"attachment","body_b":"push_box","contact_count":487.0,"contact_point_centroid":[0.53389,0.01828,0.04653],"force_p95":128.74202,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":144.1628,"mean_force":94.58366,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52595,0.01133,0.04646]},{"body_a":"world","body_b":"push_box","contact_count":3316.0,"contact_point_centroid":[0.5155,0.04786,-8e-05],"force_p95":93.72475,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.90147,"mean_force":9.45751,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.51083,0.04482,0.10451]},{"body_a":"world","body_b":"push_box","contact_count":2908.0,"contact_point_centroid":[0.51544,0.00622,-0.00019],"force_p95":98.38601,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":110.99419,"mean_force":16.19973,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.51497,-0.04275,0.03881]},{"body_a":"world","body_b":"push_box","contact_count":1640.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50444,0.02062,0.24339]}],"total_contact_groups":5},"final_pose_error":0.23876,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51171,-0.00611,0.02499],"final_tcp_position":[0.5038,-0.11413,0.03233],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":248.9914,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1640.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.51064,0.04254,0.18639],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.51973,0.04815,0.0238],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19914,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":241.10857,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3476.0,"raw_peak_contact_force":248.9914,"subtask_id":"reach_contact","tcp_end":[0.52694,0.04818,0.04497],"tcp_start":[0.51064,0.04254,0.18639],"tcp_to_object_dist_end":0.02236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51171,-0.00611,0.02499],"object_pos_start":[0.51973,0.04815,0.0238],"object_to_goal_dist_end":0.14437,"object_to_goal_dist_start":0.19914,"object_z_max":0.03541,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3395.0,"raw_peak_contact_force":144.1628,"subtask_id":"push_complete","tcp_end":[0.5038,-0.11413,0.03233],"tcp_start":[0.52694,0.04818,0.04497],"tcp_to_object_dist_end":0.10855,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```