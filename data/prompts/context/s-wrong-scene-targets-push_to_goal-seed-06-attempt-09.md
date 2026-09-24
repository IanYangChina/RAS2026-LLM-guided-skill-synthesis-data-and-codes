## Search State

- **Seed**: 6
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.1338 | 0.91 | ✅ accepted |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0006 | 0.72 | ✅ accepted |
| 7 | lift → approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2291 | 0.00 | ❌ rejected |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.1138 | 0.00 | ❌ rejected |
| 5 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0837 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is near-perfect (0.91). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.134) — your mutation base

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

- **Composite score**: 0.134
- **task_score** (E): 0.913
- **fitness_score**: 0.744  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1403 |
| descend_to_contact | 1.00 | 1.00 | 0.1485 |
| push_to_goal | 1.00 | 1.00 | 0.3187 |
| retract_high | 1.00 | 1.00 | 0.1005 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.069, 0.181) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.497, 0.069, 0.181)→(0.497, 0.147, 0.055) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 1.00 / step_budget | (0.497, 0.147, 0.055)→(0.500, -0.171, 0.047) | (0.500, 0.029, 0.025)→(0.514, -0.133, 0.029) | 0.180→0.024 | 1.00 / 2.667 | 0.746 | 139.194 |
| retract_high | retract | 1.00 / step_budget | (0.500, -0.171, 0.047)→(0.498, -0.170, 0.148) | (0.514, -0.133, 0.029)→(0.511, -0.140, 0.025) | 0.024→0.016 | 1.00 / 4.000 | 0.244 | 7.827 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.960
- lateral_force_integral: None
- approach_alignment: 0.880
- goal_progress: 0.957
- terminal_score: 0.957
- phase_score: 0.680
- phase_breakdown.push_to_goal_score: 0.943
- phase_breakdown.reach_object_score: 0.065

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.791
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.957
- **Median Q (composite search score)**: 0.174
- **K-run variance**: 0.0038
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.385


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36299,"average_solve_count":281.0,"average_success_count":281.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.15843,"approach_behind.approach_speed":0.05428,"approach_behind.approach_tolerance":0.02906,"approach_behind.behind_distance":-0.05683,"descend_to_contact.behind_distance":-0.12979,"descend_to_contact.descend_speed":0.0208,"descend_to_contact.descend_tolerance":0.02141,"descend_to_contact.descend_z_target":0.01672,"push_to_goal.push_distance":0.18102,"push_to_goal.push_speed":0.07368,"push_to_goal.push_tolerance":0.01009},"optimized_scores":{"best_composite_score":0.18059,"best_fitness_score":0.79059,"best_task_score":0.95657},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":497.0,"contact_point_centroid":[0.50947,-0.07531,0.05084],"force_p95":124.73499,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.42647,"mean_force":84.95631,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50258,-0.07376,0.05333]},{"body_a":"world","body_b":"push_box","contact_count":1951.0,"contact_point_centroid":[0.50633,-0.06116,-0.0002],"force_p95":69.31159,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.29938,"mean_force":22.00106,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50163,-0.02051,0.05265]},{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.49659,-0.16901,0.04817],"force_p95":15.66999,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.28003,"mean_force":4.59864,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.49477,-0.18082,0.04787]},{"body_a":"world","body_b":"push_box","contact_count":399.0,"contact_point_centroid":[0.50145,-0.14465,-4e-05],"force_p95":0.59505,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.4854,"mean_force":0.34036,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.49398,-0.18025,0.09825]},{"body_a":"world","body_b":"push_box","contact_count":872.0,"contact_point_centroid":[0.50458,-0.01881,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50093,0.01437,0.25232]},{"body_a":"world","body_b":"push_box","contact_count":1368.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50297,0.0637,0.13018]}],"total_contact_groups":6},"final_pose_error":0.04953,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50244,-0.14485,0.02499],"final_tcp_position":[0.495,-0.18007,0.14697],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":135.42647,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":218.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":872.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.50299,0.03049,0.20116],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.18295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":342.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.50486,0.09975,0.05739],"tcp_start":[0.50299,0.03049,0.20116],"tcp_to_object_dist_end":0.12291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,-0.14595,0.02663],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00743,"object_to_goal_dist_start":0.13127,"object_z_max":0.03518,"peak_contact_force":1.35075,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2448.0,"raw_peak_contact_force":135.42647,"subtask_id":"push_to_goal","tcp_end":[0.49621,-0.18046,0.04648],"tcp_start":[0.50486,0.09975,0.05739],"tcp_to_object_dist_end":0.041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":119.0,"n_steps_budget":930.0,"object_pos_end":[0.50244,-0.14485,0.02499],"object_pos_start":[0.50601,-0.14595,0.02663],"object_to_goal_dist_end":0.0057,"object_to_goal_dist_start":0.00743,"object_z_max":0.02663,"peak_contact_force":0.24525,"phase_name":"retract_high","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":405.0,"raw_peak_contact_force":20.28003,"tcp_end":[0.495,-0.18007,0.14697],"tcp_start":[0.49621,-0.18046,0.04648],"tcp_to_object_dist_end":0.12718,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16181,"average_solve_count":309.0,"average_success_count":309.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.16104,"approach_behind.approach_speed":0.07012,"approach_behind.approach_tolerance":0.04206,"approach_behind.behind_distance":-0.04648,"descend_to_contact.behind_distance":-0.14992,"descend_to_contact.descend_speed":0.03536,"descend_to_contact.descend_tolerance":0.0149,"descend_to_contact.descend_z_target":0.01504,"push_to_goal.push_distance":0.20302,"push_to_goal.push_speed":0.01287,"push_to_goal.push_tolerance":0.02573},"optimized_scores":{"best_composite_score":0.04668,"best_fitness_score":0.65668,"best_task_score":0.8469},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":648.0,"contact_point_centroid":[0.51573,-0.03345,0.04903],"force_p95":126.30316,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.10874,"mean_force":83.25858,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50908,-0.03084,0.05132]},{"body_a":"world","body_b":"push_box","contact_count":2346.0,"contact_point_centroid":[0.51822,-0.01077,-0.00021],"force_p95":78.18916,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.0661,"mean_force":23.38051,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51162,0.03737,0.04976]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.50419,-0.1249,0.04756],"force_p95":2.80077,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.94247,"mean_force":1.88562,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.49988,-0.13591,0.04945]},{"body_a":"world","body_b":"push_box","contact_count":300.0,"contact_point_centroid":[0.51886,-0.12036,-0.00035],"force_p95":1.0437,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.66161,"mean_force":0.43496,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.49908,-0.13502,0.10539]},{"body_a":"world","body_b":"push_box","contact_count":1112.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50588,0.03818,0.24979]},{"body_a":"world","body_b":"push_box","contact_count":1572.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51632,0.1294,0.12539]}],"total_contact_groups":6},"final_pose_error":0.04915,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51807,-0.12562,0.02486],"final_tcp_position":[0.49997,-0.13481,0.15003],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":134.10874,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":278.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1112.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.51335,0.07933,0.19832],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":393.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1572.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.52137,0.18266,0.05222],"tcp_start":[0.51335,0.07933,0.19832],"tcp_to_object_dist_end":0.13786,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":935.0,"n_steps_budget":1000.0,"object_pos_end":[0.52277,-0.10418,0.03495],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.05212,"object_to_goal_dist_start":0.19823,"object_z_max":0.03525,"peak_contact_force":0.62594,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2994.0,"raw_peak_contact_force":134.10874,"subtask_id":"push_to_goal","tcp_end":[0.5012,-0.13507,0.04916],"tcp_start":[0.52137,0.18266,0.05222],"tcp_to_object_dist_end":0.04027,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":120.0,"n_steps_budget":960.0,"object_pos_end":[0.51807,-0.12562,0.02486],"object_pos_start":[0.52277,-0.10418,0.03495],"object_to_goal_dist_end":0.03035,"object_to_goal_dist_start":0.05212,"object_z_max":0.03495,"peak_contact_force":0.24256,"phase_name":"retract_high","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":303.0,"raw_peak_contact_force":2.94247,"tcp_end":[0.49997,-0.13481,0.15003],"tcp_start":[0.5012,-0.13507,0.04916],"tcp_to_object_dist_end":0.1268,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12733,"average_solve_count":322.0,"average_success_count":322.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.10397,"approach_behind.approach_speed":0.0838,"approach_behind.approach_tolerance":0.0255,"approach_behind.behind_distance":-0.05252,"descend_to_contact.behind_distance":-0.11499,"descend_to_contact.descend_speed":0.01938,"descend_to_contact.descend_tolerance":0.03758,"descend_to_contact.descend_z_target":0.01809,"push_to_goal.push_distance":0.27522,"push_to_goal.push_speed":0.06063,"push_to_goal.push_tolerance":0.02962},"optimized_scores":{"best_composite_score":0.17403,"best_fitness_score":0.78403,"best_task_score":0.93694},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":635.0,"contact_point_centroid":[0.49598,-0.05455,0.04999],"force_p95":132.29028,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":148.04654,"mean_force":76.28153,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48961,-0.05204,0.05228]},{"body_a":"world","body_b":"push_box","contact_count":2197.0,"contact_point_centroid":[0.49675,-0.03729,-0.00022],"force_p95":68.80336,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.40392,"mean_force":22.44882,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48335,-0.00769,0.05185]},{"body_a":"world","body_b":"push_box","contact_count":476.0,"contact_point_centroid":[0.51314,-0.14858,-2e-05],"force_p95":0.24585,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.25965,"mean_force":0.24426,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.49921,-0.19663,0.09007]},{"body_a":"world","body_b":"push_box","contact_count":1500.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48685,0.04751,0.22255]},{"body_a":"world","body_b":"push_box","contact_count":992.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.46927,0.12592,0.10128]}],"total_contact_groups":5},"final_pose_error":0.04982,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51314,-0.14858,0.02499],"final_tcp_position":[0.50014,-0.19642,0.14554],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":148.04654,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1500.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47429,0.09767,0.14378],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12519,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":248.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":992.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.46569,0.1584,0.05643],"tcp_start":[0.47429,0.09767,0.14378],"tcp_to_object_dist_end":0.10562,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":994.0,"n_steps_budget":1000.0,"object_pos_end":[0.51314,-0.14886,0.0247],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.0132,"object_to_goal_dist_start":0.2095,"object_z_max":0.03512,"peak_contact_force":0.26161,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2832.0,"raw_peak_contact_force":148.04654,"subtask_id":"push_to_goal","tcp_end":[0.50138,-0.19689,0.04534],"tcp_start":[0.46569,0.1584,0.05643],"tcp_to_object_dist_end":0.05358,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":119.0,"n_steps_budget":930.0,"object_pos_end":[0.51314,-0.14858,0.02499],"object_pos_start":[0.51314,-0.14886,0.0247],"object_to_goal_dist_end":0.01321,"object_to_goal_dist_start":0.0132,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_high","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":476.0,"raw_peak_contact_force":0.25965,"tcp_end":[0.50014,-0.19642,0.14554],"tcp_start":[0.50138,-0.19689,0.04534],"tcp_to_object_dist_end":0.13034,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```