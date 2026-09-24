## Search State

- **Seed**: 6
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | 0.0006 | 0.72 | ✅ accepted |
| 7 | lift → approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2291 | 0.00 | ❌ rejected |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 3 | -0.1138 | 0.00 | ❌ rejected |
| 5 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0837 | 0.00 | ❌ rejected |
| 4 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0827 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.723, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.001) — your mutation base

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

- **Composite score**: 0.001
- **task_score** (E): 0.723
- **fitness_score**: 0.611  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.2242 |
| descend_to_contact | 1.00 | 1.00 | 0.0722 |
| push_to_goal | 1.00 | 0.67 | 0.2507 |
| retract_high | 1.00 | 1.00 | 0.1008 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.498, 0.126, 0.118) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.498, 0.126, 0.118)→(0.495, 0.132, 0.056) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 1.00 / step_budget | (0.495, 0.132, 0.056)→(0.495, -0.118, 0.047) | (0.500, 0.029, 0.025)→(0.508, -0.097, 0.030) | 0.180→0.054 | 0.67 / 2.333 | 0.744 | 115.968 |
| retract_high | retract | 1.00 / step_budget | (0.495, -0.118, 0.047)→(0.494, -0.118, 0.148) | (0.508, -0.097, 0.030)→(0.507, -0.096, 0.028) | 0.054→0.056 | 1.00 / 3.333 | 0.334 | 11.835 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.990
- lateral_force_integral: None
- approach_alignment: 0.903
- goal_progress: 0.970
- terminal_score: 0.970
- phase_score: 0.702
- phase_breakdown.push_to_goal_score: 0.970
- phase_breakdown.reach_object_score: 0.075

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.809
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.970
- **Median Q (composite search score)**: -0.061
- **K-run variance**: 0.0206
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.376


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.99296,"average_solve_count":284.0,"average_success_count":284.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.11634,"approach_behind.approach_speed":0.05446,"approach_behind.approach_tolerance":0.02278,"approach_behind.behind_distance":-0.08956,"descend_to_contact.behind_distance":-0.11859,"descend_to_contact.descend_speed":0.01147,"descend_to_contact.descend_tolerance":0.03978,"descend_to_contact.descend_z_target":0.01501,"push_to_goal.push_distance":0.21223,"push_to_goal.push_speed":0.09846,"push_to_goal.push_tolerance":0.03565},"optimized_scores":{"best_composite_score":0.1989,"best_fitness_score":0.8089,"best_task_score":0.96989},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":520.0,"contact_point_centroid":[0.50835,-0.07169,0.0514],"force_p95":122.21503,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.99634,"mean_force":81.68327,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50189,-0.06922,0.05372]},{"body_a":"world","body_b":"push_box","contact_count":2140.0,"contact_point_centroid":[0.50517,-0.07461,-0.00019],"force_p95":70.8224,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":108.10114,"mean_force":20.19695,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50031,-0.04815,0.05221]},{"body_a":"world","body_b":"push_box","contact_count":480.0,"contact_point_centroid":[0.50376,-0.14878,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24542,"mean_force":0.24519,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.49179,-0.2115,0.08983]},{"body_a":"world","body_b":"push_box","contact_count":1300.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50131,0.0292,0.23037]},{"body_a":"world","body_b":"push_box","contact_count":928.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50322,0.07496,0.10986]}],"total_contact_groups":5},"final_pose_error":0.04948,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50376,-0.14878,0.02499],"final_tcp_position":[0.49285,-0.21131,0.14571],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":136.99634,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1300.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.50399,0.06078,0.15794],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15496,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":232.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":928.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.50437,0.09158,0.05772],"tcp_start":[0.50399,0.06078,0.15794],"tcp_to_object_dist_end":0.11514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":820.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,-0.14879,0.02497],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00395,"object_to_goal_dist_start":0.13127,"object_z_max":0.03514,"peak_contact_force":0.24543,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2660.0,"raw_peak_contact_force":136.99634,"subtask_id":"push_to_goal","tcp_end":[0.49408,-0.21182,0.04518],"tcp_start":[0.50437,0.09158,0.05772],"tcp_to_object_dist_end":0.06689,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":120.0,"n_steps_budget":930.0,"object_pos_end":[0.50376,-0.14878,0.02499],"object_pos_start":[0.50376,-0.14879,0.02497],"object_to_goal_dist_end":0.00395,"object_to_goal_dist_start":0.00395,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_high","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":480.0,"raw_peak_contact_force":0.24542,"tcp_end":[0.49285,-0.21131,0.14571],"tcp_start":[0.49408,-0.21182,0.04518],"tcp_to_object_dist_end":0.13639,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0756,"average_solve_count":291.0,"average_success_count":291.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.0537,"approach_behind.approach_speed":0.05408,"approach_behind.approach_tolerance":0.0315,"approach_behind.behind_distance":-0.14339,"descend_to_contact.behind_distance":-0.06816,"descend_to_contact.descend_speed":0.0525,"descend_to_contact.descend_tolerance":0.02576,"descend_to_contact.descend_z_target":0.02014,"push_to_goal.push_distance":0.16347,"push_to_goal.push_speed":0.01767,"push_to_goal.push_tolerance":0.0296},"optimized_scores":{"best_composite_score":-0.13572,"best_fitness_score":0.47428,"best_task_score":0.55439},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":563.0,"contact_point_centroid":[0.51749,-0.0085,0.05002],"force_p95":125.39845,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":129.7278,"mean_force":88.40126,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51049,-0.00644,0.05244]},{"body_a":"world","body_b":"push_box","contact_count":1735.0,"contact_point_centroid":[0.5171,-0.00367,-0.00026],"force_p95":64.00552,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.04304,"mean_force":29.07177,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51128,0.02766,0.05165]},{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.50906,-0.08544,0.04846],"force_p95":30.97794,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.86984,"mean_force":12.28133,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.50449,-0.09626,0.05042]},{"body_a":"world","body_b":"push_box","contact_count":199.0,"contact_point_centroid":[0.51302,-0.06942,-0.0001],"force_p95":1.54313,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.45303,"mean_force":1.07736,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.5029,-0.09577,0.10129]},{"body_a":"world","body_b":"push_box","contact_count":2416.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50945,0.08637,0.19482]},{"body_a":"world","body_b":"push_box","contact_count":488.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51793,0.15609,0.07169]}],"total_contact_groups":6},"final_pose_error":0.04917,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51906,-0.06427,0.03453],"final_tcp_position":[0.50381,-0.09546,0.1512],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":129.7278,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":604.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2416.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.52069,0.17527,0.08973],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":122.0,"n_steps_budget":900.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":488.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.51687,0.13302,0.05353],"tcp_start":[0.52069,0.17527,0.08973],"tcp_to_object_dist_end":0.09002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":702.0,"n_steps_budget":1000.0,"object_pos_end":[0.51726,-0.06408,0.03506],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.08821,"object_to_goal_dist_start":0.19823,"object_z_max":0.03514,"peak_contact_force":1.9859,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2298.0,"raw_peak_contact_force":129.7278,"subtask_id":"push_to_goal","tcp_end":[0.50501,-0.09557,0.05036],"tcp_start":[0.51687,0.13302,0.05353],"tcp_to_object_dist_end":0.03709,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":119.0,"n_steps_budget":930.0,"object_pos_end":[0.51906,-0.06427,0.03453],"object_pos_start":[0.51726,-0.06408,0.03506],"object_to_goal_dist_end":0.08834,"object_to_goal_dist_start":0.08821,"object_z_max":0.03608,"peak_contact_force":0.51087,"phase_name":"retract_high","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":207.0,"raw_peak_contact_force":32.86984,"tcp_end":[0.50381,-0.09546,0.1512],"tcp_start":[0.50501,-0.09557,0.05036],"tcp_to_object_dist_end":0.12173,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25941,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.06725,"approach_behind.approach_speed":0.06504,"approach_behind.approach_tolerance":0.02378,"approach_behind.behind_distance":-0.09716,"descend_to_contact.behind_distance":-0.12604,"descend_to_contact.descend_speed":0.0538,"descend_to_contact.descend_tolerance":0.03661,"descend_to_contact.descend_z_target":0.01912,"push_to_goal.push_distance":0.12588,"push_to_goal.push_speed":0.05017,"push_to_goal.push_tolerance":0.04044},"optimized_scores":{"best_composite_score":-0.06136,"best_fitness_score":0.54864,"best_task_score":0.64482},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":247.0,"contact_point_centroid":[0.48098,0.01769,0.04889],"force_p95":63.2308,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.1799,"mean_force":20.17476,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47755,0.02898,0.04918]},{"body_a":"world","body_b":"push_box","contact_count":1221.0,"contact_point_centroid":[0.48446,0.03107,-4e-05],"force_p95":26.91984,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.03652,"mean_force":4.4572,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46979,0.09675,0.05172]},{"body_a":"world","body_b":"push_box","contact_count":348.0,"contact_point_centroid":[0.50148,-0.07993,-0.00022],"force_p95":0.92166,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.38916,"mean_force":0.36675,"phase_index":3.0,"phase_name":"retract_high","phase_type":"retract","tcp_position_centroid":[0.48449,-0.04821,0.10125]},{"body_a":"world","body_b":"push_box","contact_count":2024.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48422,0.06903,0.2032]},{"body_a":"world","body_b":"push_box","contact_count":496.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4664,0.15437,0.08244]}],"total_contact_groups":5},"final_pose_error":0.04911,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49913,-0.07559,0.02495],"final_tcp_position":[0.48538,-0.04795,0.14725],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":81.1799,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":506.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2024.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.4693,0.14077,0.10579],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11575,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":124.0,"n_steps_budget":870.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":496.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.46448,0.16998,0.05816],"tcp_start":[0.4693,0.14077,0.10579],"tcp_to_object_dist_end":0.11726,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.50178,-0.07914,0.02983],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.07105,"object_to_goal_dist_start":0.2095,"object_z_max":0.03041,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1468.0,"raw_peak_contact_force":81.1799,"subtask_id":"push_to_goal","tcp_end":[0.48647,-0.04793,0.04635],"tcp_start":[0.46448,0.16998,0.05816],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":118.0,"n_steps_budget":930.0,"object_pos_end":[0.49913,-0.07559,0.02495],"object_pos_start":[0.50178,-0.07914,0.02983],"object_to_goal_dist_end":0.07441,"object_to_goal_dist_start":0.07105,"object_z_max":0.02983,"peak_contact_force":0.24493,"phase_name":"retract_high","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":348.0,"raw_peak_contact_force":2.38916,"tcp_end":[0.48538,-0.04795,0.14725],"tcp_start":[0.48647,-0.04793,0.04635],"tcp_to_object_dist_end":0.12613,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```