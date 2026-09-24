## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 7 | 0.3498 | 0.89 | ❌ rejected |
| 13 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10 | 0.0284 | 0.69 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.3172 | 0.50 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0323 | 0.77 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2502 | 0.87 | ❌ rejected |

**Proposal policy**: task_score is 0.89 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5045797221766332, -0.01880749562239939, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5045797221766332, -0.01880749562239939, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.913, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.350) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: push_to_goal
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
      distance: -0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
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
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    behind_distance:
      type: scalar
      range:
      - -0.15
      - -0.02
      default: -0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: reach_object
- id: descend_to_contact
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
      distance: -0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
  parameters:
    behind_distance:
      type: scalar
      range:
      - -0.15
      - -0.02
      default: -0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    descend_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    descend_z_target:
      type: scalar
      range:
      - 0.015
      - 0.03
      default: 0.025
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.15
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
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: push_to_goal
- id: retract_high
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.05

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=task_goal_direction, distance=-0.05, mode=add_to_offset, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=-0.05, mode=add_to_offset, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - descend_z_target: status=consumed; consumers=target.offset.z (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **retract_high** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.05
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.350
- **task_score** (E): 0.891
- **fitness_score**: 0.730  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_contact | 1.00 | 1.00 | 0.2757 |
| push_to_goal | 1.00 | 1.00 | 0.2483 |
| retract_high | 1.00 | 1.00 | 0.1008 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_contact | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.132, 0.062) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 1.00 / time_limit | (0.497, 0.132, 0.062)→(0.502, -0.113, 0.029) | (0.500, 0.029, 0.025)→(0.525, -0.141, 0.031) | 0.180→0.027 | 1.00 / 4.000 | 87.041 | 124.944 |
| retract_high | retract | 1.00 / step_budget | (0.502, -0.113, 0.029)→(0.500, -0.113, 0.130) | (0.525, -0.141, 0.031)→(0.517, -0.141, 0.026) | 0.027→0.020 | 1.00 / 3.000 | 0.356 | 69.841 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.930
- lateral_force_integral: None
- approach_alignment: 0.767
- goal_progress: 0.912
- terminal_score: 0.912
- phase_score: 0.644
- phase_breakdown.push_to_goal_score: 0.870
- phase_breakdown.reach_object_score: 0.116

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.751
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.912
- **Median Q (composite search score)**: 0.360
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.423


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.50458,-0.01881,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14894,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.14131,"approach_contact.approach_tolerance":0.04999,"approach_contact.behind_distance":-0.09944,"approach_contact.contact_height":0.02552,"push_to_goal.push_distance":0.10733,"push_to_goal.push_max_time":23.22449,"push_to_goal.push_speed":0.17967},"optimized_scores":{"best_composite_score":0.37101,"best_fitness_score":0.75101,"best_task_score":0.91221},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1636.0,"contact_point_centroid":[0.50839,-0.05068,-7e-05],"force_p95":41.52753,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":116.73091,"mean_force":9.94038,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49995,0.00973,0.05039]},{"body_a":"attachment","body_b":"push_box","contact_count":336.0,"contact_point_centroid":[0.50818,-0.0552,0.0502],"force_p95":91.35064,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.01582,"mean_force":40.79077,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49959,-0.04399,0.03874]},{"body_a":"push_box","body_b":"link7","contact_count":68.0,"contact_point_centroid":[0.53554,-0.11792,0.05401],"force_p95":75.9011,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.24582,"mean_force":38.83616,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49899,-0.1012,0.02627]},{"body_a":"push_box","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.53623,-0.13049,0.05415],"force_p95":54.30624,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.7568,"mean_force":24.67312,"phase_index":2.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.50033,-0.11083,0.02586]},{"body_a":"attachment","body_b":"push_box","contact_count":17.0,"contact_point_centroid":[0.52,-0.12053,0.05818],"force_p95":34.39666,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.27972,"mean_force":9.5889,"phase_index":2.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.49951,-0.11076,0.02721]},{"body_a":"world","body_b":"push_box","contact_count":301.0,"contact_point_centroid":[0.50974,-0.14687,-0.00026],"force_p95":1.74869,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.96197,"mean_force":0.83416,"phase_index":2.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.49883,-0.11043,0.08412]},{"body_a":"world","body_b":"push_box","contact_count":1852.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.50137,0.03556,0.18522]}],"total_contact_groups":7},"final_pose_error":0.04909,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50708,-0.14091,0.02491],"final_tcp_position":[0.49941,-0.11039,0.12644],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":116.73091,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":463.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1852.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.50398,0.07273,0.06834],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10129,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":691.0,"n_steps_budget":720.0,"object_pos_end":[0.51575,-0.14444,0.02874],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.01712,"object_to_goal_dist_start":0.13127,"object_z_max":0.02906,"peak_contact_force":76.44875,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2040.0,"raw_peak_contact_force":116.73091,"subtask_id":"push_to_goal","tcp_end":[0.50069,-0.11061,0.02551],"tcp_start":[0.50398,0.07273,0.06834],"tcp_to_object_dist_end":0.03718,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":118.0,"n_steps_budget":930.0,"object_pos_end":[0.50708,-0.14091,0.02491],"object_pos_start":[0.51575,-0.14444,0.02874],"object_to_goal_dist_end":0.01152,"object_to_goal_dist_start":0.01712,"object_z_max":0.03065,"peak_contact_force":0.24552,"phase_name":"retract_high","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":327.0,"raw_peak_contact_force":57.7568,"tcp_end":[0.49941,-0.11039,0.12644],"tcp_start":[0.50069,-0.11061,0.02551],"tcp_to_object_dist_end":0.10629,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.51501,0.04767,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.19167,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.11385,"approach_contact.approach_tolerance":0.04467,"approach_contact.behind_distance":-0.12939,"approach_contact.contact_height":0.02016,"push_to_goal.push_distance":0.17785,"push_to_goal.push_max_time":15.1373,"push_to_goal.push_speed":0.18664},"optimized_scores":{"best_composite_score":0.31827,"best_fitness_score":0.69827,"best_task_score":0.85141},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":269.0,"contact_point_centroid":[0.54078,-0.08233,0.05799],"force_p95":106.48025,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":143.40829,"mean_force":60.89014,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50485,-0.0723,0.02947]},{"body_a":"attachment","body_b":"push_box","contact_count":516.0,"contact_point_centroid":[0.51932,-0.03426,0.04952],"force_p95":110.08101,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.96141,"mean_force":35.55815,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50608,-0.0251,0.03349]},{"body_a":"push_box","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.54954,-0.11965,0.05541],"force_p95":105.99501,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":109.08274,"mean_force":58.50309,"phase_index":2.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.50655,-0.11014,0.02947]},{"body_a":"world","body_b":"push_box","contact_count":2100.0,"contact_point_centroid":[0.52249,-0.00394,-7e-05],"force_p95":61.80702,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.48446,"mean_force":12.99271,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5105,0.06095,0.0425]},{"body_a":"attachment","body_b":"push_box","contact_count":23.0,"contact_point_centroid":[0.52589,-0.11447,0.05534],"force_p95":75.09903,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.59466,"mean_force":23.37827,"phase_index":2.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.50569,-0.11005,0.03244]},{"body_a":"world","body_b":"push_box","contact_count":191.0,"contact_point_centroid":[0.54244,-0.14756,-0.00011],"force_p95":9.82917,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.40803,"mean_force":1.93342,"phase_index":2.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.50541,-0.10973,0.07761]},{"body_a":"world","body_b":"push_box","contact_count":2360.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.50897,0.0803,0.17919]}],"total_contact_groups":7},"final_pose_error":0.04908,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52559,-0.13603,0.02919],"final_tcp_position":[0.50588,-0.10957,0.1295],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":143.40829,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":590.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2360.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.51954,0.16285,0.0581],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11994,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":961.0,"n_steps_budget":990.0,"object_pos_end":[0.53234,-0.13741,0.03153],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.03531,"object_to_goal_dist_start":0.19823,"object_z_max":0.03198,"peak_contact_force":116.38973,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2885.0,"raw_peak_contact_force":143.40829,"subtask_id":"push_to_goal","tcp_end":[0.50708,-0.10977,0.02856],"tcp_start":[0.51954,0.16285,0.0581],"tcp_to_object_dist_end":0.03756,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":117.0,"n_steps_budget":930.0,"object_pos_end":[0.52559,-0.13603,0.02919],"object_pos_start":[0.53234,-0.13741,0.03153],"object_to_goal_dist_end":0.02946,"object_to_goal_dist_start":0.03531,"object_z_max":0.03423,"peak_contact_force":0.57962,"phase_name":"retract_high","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":226.0,"raw_peak_contact_force":109.08274,"tcp_end":[0.50588,-0.10957,0.1295],"tcp_start":[0.50708,-0.10977,0.02856],"tcp_to_object_dist_end":0.1056,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47924,0.05847,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.20833,"average_solve_count":120.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.11878,"approach_contact.approach_tolerance":0.03856,"approach_contact.behind_distance":-0.11552,"approach_contact.contact_height":0.02055,"push_to_goal.push_distance":0.29064,"push_to_goal.push_max_time":15.02075,"push_to_goal.push_speed":0.18203},"optimized_scores":{"best_composite_score":0.36019,"best_fitness_score":0.74019,"best_task_score":0.90862},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":539.0,"contact_point_centroid":[0.49498,-0.03443,0.04881],"force_p95":63.68078,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.69138,"mean_force":19.62853,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48357,-0.02541,0.03922]},{"body_a":"push_box","body_b":"link7","contact_count":195.0,"contact_point_centroid":[0.53125,-0.0962,0.05993],"force_p95":73.1926,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.80289,"mean_force":37.32578,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49197,-0.09275,0.03389]},{"body_a":"world","body_b":"push_box","contact_count":1874.0,"contact_point_centroid":[0.49431,-0.00024,-6e-05],"force_p95":43.84101,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.28059,"mean_force":8.35929,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47439,0.05963,0.04685]},{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.53934,-0.12069,0.05803],"force_p95":41.89838,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.68207,"mean_force":18.66393,"phase_index":2.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.49659,-0.12025,0.03293]},{"body_a":"attachment","body_b":"push_box","contact_count":17.0,"contact_point_centroid":[0.5195,-0.12365,0.06171],"force_p95":32.97233,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.34107,"mean_force":7.42496,"phase_index":2.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.4956,-0.12029,0.03426]},{"body_a":"world","body_b":"push_box","contact_count":286.0,"contact_point_centroid":[0.52607,-0.14621,-0.00031],"force_p95":1.79535,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.00627,"mean_force":0.6455,"phase_index":2.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.49495,-0.11971,0.08925]},{"body_a":"world","body_b":"push_box","contact_count":2304.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.48298,0.07872,0.17991]}],"total_contact_groups":7},"final_pose_error":0.04956,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51852,-0.14515,0.0248],"final_tcp_position":[0.49574,-0.11954,0.13323],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":114.69138,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":576.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2304.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.46695,0.15959,0.05969],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5275,-0.14203,0.03236],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.02956,"object_to_goal_dist_start":0.2095,"object_z_max":0.0336,"peak_contact_force":68.28388,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2608.0,"raw_peak_contact_force":114.69138,"subtask_id":"push_to_goal","tcp_end":[0.497,-0.11974,0.03278],"tcp_start":[0.46695,0.15959,0.05969],"tcp_to_object_dist_end":0.03778,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":118.0,"n_steps_budget":930.0,"object_pos_end":[0.51852,-0.14515,0.0248],"object_pos_start":[0.5275,-0.14203,0.03236],"object_to_goal_dist_end":0.01914,"object_to_goal_dist_start":0.02956,"object_z_max":0.03248,"peak_contact_force":0.24272,"phase_name":"retract_high","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":311.0,"raw_peak_contact_force":42.68207,"tcp_end":[0.49574,-0.11954,0.13323],"tcp_start":[0.497,-0.11974,0.03278],"tcp_to_object_dist_end":0.11372,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```