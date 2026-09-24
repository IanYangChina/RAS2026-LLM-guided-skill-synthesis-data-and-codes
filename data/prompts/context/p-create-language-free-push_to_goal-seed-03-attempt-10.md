## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push → lift → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 7 | 0.3345 | 0.81 | ✅ accepted |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.3836 | 0.81 | ✅ accepted |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3557 | 0.64 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.3690 | 0.48 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3618 | 0.63 | ❌ rejected |

**Proposal policy**: task_score is 0.81 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.814, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.45027790005723495, -0.03158273920846803, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.334) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_pre_contact
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
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.1
    offset_along_axis:
      distance: 0.02
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_z_offset:
      type: scalar
      range:
      - 0.08
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    behind_distance:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: reach_pre_contact
- id: descend_to_contact
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.02
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    behind_distance:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.02
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  subtask_id: reach_pre_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_duration:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_extension:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
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
  guards:
  - id: contact_guard
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_to_goal
- id: lift_off
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current
- id: retract_to_home
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: world
    offset:
    - 0.5
    - 0.0
    - 0.3
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=add_to_offset, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_to_contact** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.02, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_extension: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_guard, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **lift_off** (`lift`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_to_home** (`retract`)
  - target: source=yaml, anchor=world, offset=[0.5, 0.0, 0.3], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.334
- **task_score** (E): 0.814
- **fitness_score**: 0.691  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.083
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1607 |
| descend_to_contact | 0.33 | 1.00 | 0.1239 |
| push_to_goal | 1.00 | 0.33 | 0.1414 |
| lift_off | 1.00 | 1.00 | 0.2865 |
| retract_to_home | 1.00 | 1.00 | 0.1279 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.512, 0.036, 0.157) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 0.33 / step_budget | (0.512, 0.036, 0.157)→(0.510, 0.044, 0.035) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.333 | 15.214 | 0.245 |
| push_to_goal | push | 1.00 / time_limit | (0.510, 0.044, 0.035)→(0.499, -0.090, 0.026) | (0.513, 0.002, 0.025)→(0.510, -0.121, 0.027) | 0.160→0.032 | 0.33 / 1.000 | 4.315 | 38.347 |
| lift_off | lift | 1.00 / step_budget | (0.499, -0.090, 0.026)→(0.498, -0.147, 0.305) | (0.510, -0.121, 0.027)→(0.508, -0.121, 0.025) | 0.032→0.032 | 1.00 / 4.000 | 0.245 | 2.024 |
| retract_to_home | retract | 1.00 / step_budget | (0.498, -0.147, 0.305)→(0.498, -0.019, 0.296) | (0.508, -0.121, 0.025)→(0.508, -0.121, 0.025) | 0.032→0.032 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.654
- lateral_force_integral: None
- approach_alignment: 0.982
- goal_progress: 0.641
- terminal_score: 0.641
- phase_score: 0.508
- phase_breakdown.push_to_goal_score: 0.645
- phase_breakdown.reach_pre_contact_score: 0.190

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.785
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.934
- **Median Q (composite search score)**: 0.345
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.322


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92188,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_z_offset":0.11743,"approach_behind.behind_distance":0.03003,"descend_to_contact.behind_distance":0.04906,"descend_to_contact.contact_force_threshold":13.58466,"push_to_goal.push_duration":4.19712,"push_to_goal.push_extension":0.1421,"push_to_goal.push_speed":0.08173},"optimized_scores":{"best_composite_score":0.28669,"best_fitness_score":0.72669,"best_task_score":0.8684},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1506.0,"contact_point_centroid":[0.48256,-0.08777,-4e-05],"force_p95":10.41496,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.17942,"mean_force":3.72921,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.44812,-0.04012,0.02469]},{"body_a":"push_box","body_b":"link7","contact_count":68.0,"contact_point_centroid":[0.51039,-0.09895,0.0563],"force_p95":14.3334,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.10115,"mean_force":7.03876,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47473,-0.10257,0.02301]},{"body_a":"attachment","body_b":"push_box","contact_count":727.0,"contact_point_centroid":[0.46257,-0.06217,0.04928],"force_p95":15.52349,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.53913,"mean_force":6.11563,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45272,-0.05141,0.02417]},{"body_a":"world","body_b":"push_box","contact_count":3268.0,"contact_point_centroid":[0.50564,-0.13441,-2e-05],"force_p95":0.38463,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.52979,"mean_force":0.26312,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.48649,-0.12941,0.17334]},{"body_a":"attachment","body_b":"push_box","contact_count":42.0,"contact_point_centroid":[0.49123,-0.11685,0.05496],"force_p95":1.10115,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.21005,"mean_force":0.72224,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.47663,-0.11094,0.03772]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51491,-0.10797,0.05586],"force_p95":0.44017,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.44017,"mean_force":0.44017,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.47757,-0.10883,0.02296]},{"body_a":"world","body_b":"push_box","contact_count":1928.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.47057,-0.00175,0.22638]},{"body_a":"world","body_b":"push_box","contact_count":2648.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.43362,0.00443,0.08919]},{"body_a":"world","body_b":"push_box","contact_count":1216.0,"contact_point_centroid":[0.50413,-0.13361,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_to_home","phase_type":"retract","tcp_position_centroid":[0.49714,-0.08421,0.29901]}],"total_contact_groups":9},"final_pose_error":0.01964,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50413,-0.13361,0.02499],"final_tcp_position":[0.49801,-0.01907,0.29575],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":41.17942,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1928.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.44124,-0.00357,0.15208],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":662.0,"n_steps_budget":810.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2648.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.42835,0.01252,0.02875],"tcp_start":[0.44124,-0.00357,0.15208],"tcp_to_object_dist_end":0.04939,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5075,-0.13332,0.0292],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.01877,"object_to_goal_dist_start":0.12843,"object_z_max":0.02917,"peak_contact_force":12.94636,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2301.0,"raw_peak_contact_force":41.17942,"subtask_id":"push_to_goal","tcp_end":[0.47757,-0.10883,0.02296],"tcp_start":[0.42835,0.01252,0.02875],"tcp_to_object_dist_end":0.03917,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":879.0,"n_steps_budget":1000.0,"object_pos_end":[0.50413,-0.13361,0.02499],"object_pos_start":[0.5075,-0.13332,0.0292],"object_to_goal_dist_end":0.0169,"object_to_goal_dist_start":0.01877,"object_z_max":0.0292,"peak_contact_force":0.24525,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3311.0,"raw_peak_contact_force":1.52979,"tcp_end":[0.49729,-0.14762,0.30547],"tcp_start":[0.47757,-0.10883,0.02296],"tcp_to_object_dist_end":0.28091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":304.0,"n_steps_budget":930.0,"object_pos_end":[0.50413,-0.13361,0.02499],"object_pos_start":[0.50413,-0.13361,0.02499],"object_to_goal_dist_end":0.0169,"object_to_goal_dist_start":0.0169,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_to_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1216.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49801,-0.01907,0.29575],"tcp_start":[0.49729,-0.14762,0.30547],"tcp_to_object_dist_end":0.29405,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92228,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_z_offset":0.14233,"approach_behind.behind_distance":0.02921,"descend_to_contact.behind_distance":0.0473,"descend_to_contact.contact_force_threshold":6.8612,"push_to_goal.push_duration":3.91606,"push_to_goal.push_extension":0.19291,"push_to_goal.push_speed":0.09791},"optimized_scores":{"best_composite_score":0.34546,"best_fitness_score":0.78546,"best_task_score":0.93394},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":774.0,"contact_point_centroid":[0.53189,-0.04289,0.02063],"force_p95":14.55139,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.08547,"mean_force":3.82381,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53373,-0.03112,0.02019]},{"body_a":"world","body_b":"push_box","contact_count":1904.0,"contact_point_centroid":[0.52646,-0.06586,-4e-05],"force_p95":5.8053,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.03244,"mean_force":1.84316,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53591,-0.02543,0.02051]},{"body_a":"attachment","body_b":"push_box","contact_count":41.0,"contact_point_centroid":[0.50194,-0.12011,0.03853],"force_p95":2.05199,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.48658,"mean_force":0.95043,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50496,-0.10854,0.03783]},{"body_a":"world","body_b":"push_box","contact_count":3293.0,"contact_point_centroid":[0.49313,-0.14308,-2e-05],"force_p95":0.37538,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44854,"mean_force":0.26115,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50139,-0.12785,0.17118]},{"body_a":"world","body_b":"push_box","contact_count":2004.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5262,0.01298,0.23559]},{"body_a":"world","body_b":"push_box","contact_count":3188.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.55806,0.03572,0.09432]},{"body_a":"world","body_b":"push_box","contact_count":1212.0,"contact_point_centroid":[0.49346,-0.14166,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_to_home","phase_type":"retract","tcp_position_centroid":[0.49795,-0.08432,0.29889]}],"total_contact_groups":7},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49346,-0.14166,0.02499],"final_tcp_position":[0.4982,-0.01938,0.29572],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":20.08547,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":501.0,"n_steps_budget":960.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2004.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.55473,0.02638,0.17234],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14947,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":797.0,"n_steps_budget":930.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3188.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.5637,0.04467,0.02551],"tcp_start":[0.55473,0.02638,0.17234],"tcp_to_object_dist_end":0.04458,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49495,-0.14037,0.0251],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.01087,"object_to_goal_dist_start":0.16043,"object_z_max":0.02533,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2678.0,"raw_peak_contact_force":20.08547,"subtask_id":"push_to_goal","tcp_end":[0.50836,-0.10577,0.02029],"tcp_start":[0.5637,0.04467,0.02551],"tcp_to_object_dist_end":0.03742,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":885.0,"n_steps_budget":1000.0,"object_pos_end":[0.49346,-0.14166,0.02499],"object_pos_start":[0.49495,-0.14037,0.0251],"object_to_goal_dist_end":0.0106,"object_to_goal_dist_start":0.01087,"object_z_max":0.02689,"peak_contact_force":0.24525,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3334.0,"raw_peak_contact_force":2.48658,"tcp_end":[0.49873,-0.14747,0.30526],"tcp_start":[0.50836,-0.10577,0.02029],"tcp_to_object_dist_end":0.28038,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":930.0,"object_pos_end":[0.49346,-0.14166,0.02499],"object_pos_start":[0.49346,-0.14166,0.02499],"object_to_goal_dist_end":0.0106,"object_to_goal_dist_start":0.0106,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_to_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1212.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4982,-0.01938,0.29572],"tcp_start":[0.49873,-0.14747,0.30526],"tcp_to_object_dist_end":0.29711,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92147,"average_solve_count":191.0,"average_success_count":191.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_z_offset":0.11864,"approach_behind.behind_distance":0.05706,"descend_to_contact.behind_distance":0.03374,"descend_to_contact.contact_force_threshold":12.53911,"push_to_goal.push_duration":5.40514,"push_to_goal.push_extension":0.08977,"push_to_goal.push_speed":0.08051},"optimized_scores":{"best_composite_score":0.37128,"best_fitness_score":0.56128,"best_task_score":0.64089},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":744.0,"contact_point_centroid":[0.52537,-0.00229,0.04557],"force_p95":20.10712,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.77643,"mean_force":8.11612,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52337,0.00952,0.04054]},{"body_a":"world","body_b":"push_box","contact_count":1874.0,"contact_point_centroid":[0.52712,-0.03159,-0.00011],"force_p95":9.58737,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.68475,"mean_force":3.56898,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52421,0.01433,0.0409]},{"body_a":"world","body_b":"push_box","contact_count":3251.0,"contact_point_centroid":[0.52805,-0.08881,-2e-05],"force_p95":0.3946,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.05667,"mean_force":0.2632,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50299,-0.10331,0.17835]},{"body_a":"attachment","body_b":"push_box","contact_count":33.0,"contact_point_centroid":[0.51336,-0.07113,0.04954],"force_p95":1.26485,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.73845,"mean_force":0.80163,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50863,-0.05985,0.04631]},{"body_a":"world","body_b":"push_box","contact_count":2560.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51971,0.04295,0.22288]},{"body_a":"world","body_b":"push_box","contact_count":1844.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.53868,0.07999,0.09779]},{"body_a":"world","body_b":"push_box","contact_count":1192.0,"contact_point_centroid":[0.52759,-0.0874,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_to_home","phase_type":"retract","tcp_position_centroid":[0.49803,-0.08308,0.2992]}],"total_contact_groups":7},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52759,-0.0874,0.02499],"final_tcp_position":[0.49822,-0.0192,0.2958],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":53.77643,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2560.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.54134,0.08651,0.14799],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":461.0,"n_steps_budget":780.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":45.15018,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1844.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.53862,0.07362,0.05049],"tcp_start":[0.54134,0.08651,0.14799],"tcp_to_object_dist_end":0.04471,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52826,-0.08851,0.02671],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.0677,"object_to_goal_dist_start":0.1905,"object_z_max":0.02667,"peak_contact_force":0.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2618.0,"raw_peak_contact_force":53.77643,"subtask_id":"push_to_goal","tcp_end":[0.51158,-0.05534,0.03518],"tcp_start":[0.53862,0.07362,0.05049],"tcp_to_object_dist_end":0.03809,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":871.0,"n_steps_budget":1000.0,"object_pos_end":[0.52759,-0.0874,0.02499],"object_pos_start":[0.52826,-0.08851,0.02671],"object_to_goal_dist_end":0.06841,"object_to_goal_dist_start":0.0677,"object_z_max":0.02852,"peak_contact_force":0.24525,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3284.0,"raw_peak_contact_force":2.05667,"tcp_end":[0.49889,-0.14504,0.30576],"tcp_start":[0.51158,-0.05534,0.03518],"tcp_to_object_dist_end":0.28806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":930.0,"object_pos_end":[0.52759,-0.0874,0.02499],"object_pos_start":[0.52759,-0.0874,0.02499],"object_to_goal_dist_end":0.06841,"object_to_goal_dist_start":0.06841,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_to_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49822,-0.0192,0.2958],"tcp_start":[0.49889,-0.14504,0.30576],"tcp_to_object_dist_end":0.28081,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```