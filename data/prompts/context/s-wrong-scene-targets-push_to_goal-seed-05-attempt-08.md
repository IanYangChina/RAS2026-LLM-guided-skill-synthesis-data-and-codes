## Search State

- **Seed**: 5
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.5133 | 0.78 | ❌ rejected |
| 7 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.5284 | 0.81 | ❌ rejected |
| 6 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.5419 | 0.82 | ✅ accepted |
| 5 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.3000 | 0.00 | ❌ rejected |
| 4 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.3000 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.78 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5366003508494456, 0.03695289476837925, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5366003508494456, 0.03695289476837925, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.816, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5, -0.15, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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

## Current Skill (Q=0.513) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.025
  weight: 0.3
- id: push_toward_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: arc_behind
  type: approach
  generator: arc_cartesian
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
      distance: 0.04
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    arc_height:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.arc_height
        mode: replace
  subtask_id: approach_pre_contact
- id: push_forward
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_toward_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **arc_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.04, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
- **push_forward** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.513
- **task_score** (E): 0.781
- **fitness_score**: 0.713  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| arc_behind | 1.00 | 1.00 | 0.2780 |
| push_forward | 1.00 | 1.00 | 0.1575 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| arc_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.064, 0.032) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_forward | push | 1.00 / time_limit | (0.518, 0.064, 0.032)→(0.503, -0.093, 0.030) | (0.519, 0.022, 0.025)→(0.526, -0.123, 0.031) | 0.173→0.040 | 1.00 / 4.000 | 67.364 | 79.542 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.695
- goal_progress: 0.883
- terminal_score: 0.883
- phase_score: 0.727
- phase_breakdown.push_toward_goal_score: 0.883
- phase_breakdown.approach_pre_contact_score: 0.364

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.790
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.883
- **Median Q (composite search score)**: 0.480
- **K-run variance**: 0.0029
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.527


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.5366,0.03695,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.38571,"average_solve_count":70.0,"average_success_count":70.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_behind.approach_speed":0.17708,"arc_behind.arc_height":0.03088,"push_forward.push_distance":0.39855,"push_forward.push_speed":0.01296},"optimized_scores":{"best_composite_score":0.47027,"best_fitness_score":0.67027,"best_task_score":0.72583},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":482.0,"contact_point_centroid":[0.54934,-0.05645,0.05738],"force_p95":77.1636,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.87584,"mean_force":44.69358,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.51317,-0.0472,0.02882]},{"body_a":"attachment","body_b":"push_box","contact_count":875.0,"contact_point_centroid":[0.53123,-0.02024,0.04489],"force_p95":63.92215,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.28885,"mean_force":20.53614,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.51897,-0.01045,0.02805]},{"body_a":"world","body_b":"push_box","contact_count":1589.0,"contact_point_centroid":[0.54291,-0.06025,-0.00012],"force_p95":56.39587,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.52207,"mean_force":19.87947,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.51904,-0.01167,0.02839]},{"body_a":"world","body_b":"push_box","contact_count":3400.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.51701,0.05527,0.17231]}],"total_contact_groups":4},"final_pose_error":0.46242,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53648,-0.11323,0.03174],"final_tcp_position":[0.50866,-0.08667,0.03091],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":87.87584,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":850.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"arc_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3400.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_pre_contact","tcp_end":[0.53793,0.07702,0.03257],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0408,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53648,-0.11323,0.03174],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.05223,"object_to_goal_dist_start":0.1905,"object_z_max":0.03174,"peak_contact_force":71.13461,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2946.0,"raw_peak_contact_force":87.87584,"subtask_id":"push_toward_goal","tcp_end":[0.50866,-0.08667,0.03091],"tcp_start":[0.53793,0.07702,0.03257],"tcp_to_object_dist_end":0.03847,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.50458,-0.01881,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93333,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_behind.approach_speed":0.10537,"arc_behind.arc_height":0.05183,"push_forward.push_distance":0.35881,"push_forward.push_speed":0.07287},"optimized_scores":{"best_composite_score":0.5897,"best_fitness_score":0.7897,"best_task_score":0.88304},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":403.0,"contact_point_centroid":[0.52841,-0.10064,0.05614],"force_p95":51.30216,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.8814,"mean_force":29.88333,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.49654,-0.086,0.02642]},{"body_a":"attachment","body_b":"push_box","contact_count":835.0,"contact_point_centroid":[0.50952,-0.06278,0.04636],"force_p95":51.71333,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.36199,"mean_force":16.50019,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.49644,-0.05181,0.02601]},{"body_a":"world","body_b":"push_box","contact_count":1659.0,"contact_point_centroid":[0.51394,-0.09408,-8e-05],"force_p95":36.31021,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.77258,"mean_force":12.52136,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.49695,-0.04154,0.02643]},{"body_a":"world","body_b":"push_box","contact_count":3744.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.49985,0.04381,0.16934]}],"total_contact_groups":4},"final_pose_error":0.39295,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51428,-0.15044,0.03063],"final_tcp_position":[0.49775,-0.11578,0.02749],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":66.8814,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":936.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"arc_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3744.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_pre_contact","tcp_end":[0.50157,0.02775,0.03076],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.04701,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51428,-0.15044,0.03063],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.01535,"object_to_goal_dist_start":0.13127,"object_z_max":0.03064,"peak_contact_force":59.66007,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2897.0,"raw_peak_contact_force":66.8814,"subtask_id":"push_toward_goal","tcp_end":[0.49775,-0.11578,0.02749],"tcp_start":[0.50157,0.02775,0.03076],"tcp_to_object_dist_end":0.03853,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.51501,0.04767,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.37681,"average_solve_count":69.0,"average_success_count":69.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"arc_behind.approach_speed":0.18388,"arc_behind.arc_height":0.02201,"push_forward.push_distance":0.37616,"push_forward.push_speed":0.0821},"optimized_scores":{"best_composite_score":0.48,"best_fitness_score":0.68,"best_task_score":0.73458},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":428.0,"contact_point_centroid":[0.53784,-0.0514,0.05771],"force_p95":69.48495,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.86796,"mean_force":40.82834,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.50267,-0.04121,0.02929]},{"body_a":"attachment","body_b":"push_box","contact_count":878.0,"contact_point_centroid":[0.51675,-0.00989,0.04559],"force_p95":62.15748,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.88105,"mean_force":18.3138,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.50439,0.0003,0.0288]},{"body_a":"world","body_b":"push_box","contact_count":1530.0,"contact_point_centroid":[0.52712,-0.05095,-0.00011],"force_p95":44.25366,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.83031,"mean_force":17.61322,"phase_index":1.0,"phase_name":"push_forward","phase_type":"push","tcp_position_centroid":[0.50457,-0.0011,0.02908]},{"body_a":"world","body_b":"push_box","contact_count":3292.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"arc_behind","phase_type":"approach","tcp_position_centroid":[0.50533,0.05466,0.17166]}],"total_contact_groups":4},"final_pose_error":0.45024,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52706,-0.10536,0.03159],"final_tcp_position":[0.50251,-0.07595,0.03064],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":83.86796,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":823.0,"n_steps_budget":990.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"arc_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3292.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_pre_contact","tcp_end":[0.51305,0.08631,0.03357],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03963,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52706,-0.10536,0.03159],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.05262,"object_to_goal_dist_start":0.19823,"object_z_max":0.03158,"peak_contact_force":71.29778,"phase_name":"push_forward","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2836.0,"raw_peak_contact_force":83.86796,"subtask_id":"push_toward_goal","tcp_end":[0.50251,-0.07595,0.03064],"tcp_start":[0.51305,0.08631,0.03357],"tcp_to_object_dist_end":0.03832,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```