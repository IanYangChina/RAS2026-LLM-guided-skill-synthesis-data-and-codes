## Search State

- **Seed**: 8
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 13 | -0.1899 | 0.37 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.1750 | 0.83 | ❌ rejected |
| 9 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 13 | 0.1458 | 0.90 | ✅ accepted |
| 8 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0803 | 0.45 | ✅ accepted |
| 7 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1433 | 0.07 | ❌ rejected |

**Proposal policy**: task_score is 0.37 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.4792366731926673, 0.05847322120055107, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.4792366731926673, 0.05847322120055107, 0.025]
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
  frozen_object_start: [0.4792, 0.0585, 0.025]
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [0.0208, -0.2085, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.899, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=-0.190) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: behind_approach
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: contact_establish
  anchor: object
  metric: contact
  weight: 0.2
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.6
phases:
- id: approach_high_behind
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
    - 0.15
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    behind_distance:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    behind_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: behind_approach
- id: descend_behind
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_distance:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: contact_object
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.08
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
    contact_stroke:
      type: scalar
      range:
      - 0.04
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: contact_establish
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - -0.005
    - 0.0
  subtask_id: push_to_goal
- id: retract_away
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    retract_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high_behind** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.15], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - behind_speed: status=consumed; consumers=generator.speed (replace)
- **descend_behind** (`descend`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=replace_offset_projection, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **contact_object** (`contact`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.08, mode=replace_offset_projection, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
    - contact_stroke: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=replace_offset_projection, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, -0.005, 0.0]
- **retract_away** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.190
- **task_score** (E): 0.370
- **fitness_score**: 0.417  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.740

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1848 |
| descend_to_push | 1.00 | 1.00 | 0.1692 |
| establish_contact | 0.67 | 1.00 | 0.0278 |
| push_to_goal | 1.00 | 1.00 | 0.2031 |
| retract_after_push | 1.00 | 1.00 | 0.0748 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.558, 0.116, 0.183) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_push | descend | 1.00 / step_budget | (0.558, 0.116, 0.183)→(0.528, 0.013, 0.058) | (0.526, -0.001, 0.025)→(0.526, -0.002, 0.025) | 0.156→0.156 | 1.00 / 4.667 | 116.445 | 116.445 |
| establish_contact | contact | 0.67 / force_exceeded | (0.528, 0.013, 0.058)→(0.530, -0.015, 0.056) | (0.526, -0.002, 0.025)→(0.526, -0.002, 0.025) | 0.156→0.156 | 1.00 / 4.667 | 53.328 | 53.328 |
| push_to_goal | push | 1.00 / step_budget | (0.530, -0.015, 0.056)→(0.478, -0.205, 0.052) | (0.526, -0.002, 0.025)→(0.509, -0.045, 0.025) | 0.156→0.108 | 1.00 / 4.000 | 0.245 | 82.783 |
| retract_after_push | retract | 1.00 / step_budget | (0.478, -0.205, 0.052)→(0.492, -0.163, 0.110) | (0.509, -0.045, 0.025)→(0.509, -0.045, 0.025) | 0.108→0.108 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.554
- lateral_force_integral: None
- approach_alignment: 0.804
- goal_progress: 0.553
- terminal_score: 0.553
- phase_score: 0.546
- phase_breakdown.contact_establish_score: 1.000
- phase_breakdown.behind_approach_score: 0.075
- phase_breakdown.push_to_goal_score: 0.552

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.549
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.556
- **Median Q (composite search score)**: 0.004
- **K-run variance**: 0.0770
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.298


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8267fcc1127ab3c529e380fe6aea430def9956719b146bd9818eb52355cb895d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33d626702a3717cebb1eda35e1cb80c1c9d108c246efccd193577b9105813420`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47924,0.05847,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44118,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.14559,"approach_behind.approach_speed":0.25593,"approach_behind.behind_distance":0.08076,"descend_to_push.descend_speed":0.17854,"descend_to_push.descend_z_clearance":0.03441,"establish_contact.contact_force_threshold":15.07178,"establish_contact.contact_speed":0.04958,"establish_contact.contact_stroke":0.13834,"push_to_goal.push_distance":0.21508,"push_to_goal.push_speed":0.06039,"retract_after_push.arc_height":0.15638,"retract_after_push.retract_height":0.10317,"retract_after_push.retract_speed":0.12467},"optimized_scores":{"best_composite_score":-0.58236,"best_fitness_score":0.15764,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":888.0,"contact_point_centroid":[0.47924,0.05847,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48754,0.05563,0.24469]},{"body_a":"world","body_b":"push_box","contact_count":920.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.47446,0.09209,0.13271]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.47635,0.02534,0.07244]},{"body_a":"world","body_b":"push_box","contact_count":1328.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48701,-0.10631,0.06819]},{"body_a":"world","body_b":"push_box","contact_count":732.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.49448,-0.1853,0.09073]}],"total_contact_groups":5},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47924,0.05847,0.02499],"final_tcp_position":[0.49589,-0.16319,0.11382],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":0.24534,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":222.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":888.0,"raw_peak_contact_force":0.24534,"subtask_id":"behind_approach","tcp_end":[0.47468,0.11476,0.18812],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":230.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":920.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47564,0.06746,0.07661],"tcp_start":[0.47468,0.11476,0.18812],"tcp_to_object_dist_end":0.05252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"establish_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_establish","tcp_end":[0.48028,-0.01543,0.07225],"tcp_start":[0.47564,0.06746,0.07661],"tcp_to_object_dist_end":0.08773,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":332.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1328.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.49599,-0.20048,0.06695],"tcp_start":[0.48028,-0.01543,0.07225],"tcp_to_object_dist_end":0.26287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":183.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":732.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49589,-0.16319,0.11382],"tcp_start":[0.49599,-0.20048,0.06695],"tcp_to_object_dist_end":0.23938,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.54443,-0.02558,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63441,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.13727,"approach_behind.approach_speed":0.20133,"approach_behind.behind_distance":0.20825,"descend_to_push.descend_speed":0.15336,"descend_to_push.descend_z_clearance":0.01247,"establish_contact.contact_force_threshold":9.07999,"establish_contact.contact_speed":0.03631,"establish_contact.contact_stroke":0.11195,"push_to_goal.push_distance":0.21991,"push_to_goal.push_speed":0.0413,"retract_after_push.arc_height":0.1321,"retract_after_push.retract_height":0.09612,"retract_after_push.retract_speed":0.09915},"optimized_scores":{"best_composite_score":0.00354,"best_fitness_score":0.54354,"best_task_score":0.5556},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":38.0,"contact_point_centroid":[0.56115,-0.00422,0.0483],"force_p95":170.07239,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":170.15776,"mean_force":148.1571,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.54938,-0.00415,0.04966]},{"body_a":"attachment","body_b":"push_box","contact_count":236.0,"contact_point_centroid":[0.54702,-0.04317,0.05135],"force_p95":123.22765,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.66328,"mean_force":96.29158,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53851,-0.04934,0.05228]},{"body_a":"world","body_b":"push_box","contact_count":914.0,"contact_point_centroid":[0.53229,-0.07141,-0.00035],"force_p95":84.42777,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.59157,"mean_force":25.31459,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51993,-0.09236,0.04885]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.56222,-0.00792,0.04743],"force_p95":83.54328,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.54328,"mean_force":83.54328,"phase_index":2.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.55042,-0.0078,0.04829]},{"body_a":"world","body_b":"push_box","contact_count":1596.0,"contact_point_centroid":[0.54443,-0.02566,-3e-05],"force_p95":15.99389,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.62944,"mean_force":3.78912,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.5711,0.06834,0.10577]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.54448,-0.02739,-0.00038],"force_p95":33.79181,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.25794,"mean_force":21.15009,"phase_index":2.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.55042,-0.0078,0.04829]},{"body_a":"world","body_b":"push_box","contact_count":1252.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.54817,0.07246,0.23724]},{"body_a":"world","body_b":"push_box","contact_count":872.0,"contact_point_centroid":[0.52156,-0.09539,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24523,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48291,-0.1779,0.07642]}],"total_contact_groups":8},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52156,-0.09539,0.02499],"final_tcp_position":[0.49139,-0.16017,0.10626],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":170.15776,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":313.0,"n_steps_budget":780.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.24534,"subtask_id":"behind_approach","tcp_end":[0.59883,0.14825,0.17414],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.23542,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":399.0,"n_steps_budget":930.0,"object_pos_end":[0.54499,-0.02737,0.02424],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13063,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":170.15776,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1634.0,"raw_peak_contact_force":170.15776,"tcp_end":[0.55042,-0.0078,0.04829],"tcp_start":[0.59883,0.14825,0.17414],"tcp_to_object_dist_end":0.03147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54499,-0.0274,0.02424],"object_pos_start":[0.54499,-0.02737,0.02424],"object_to_goal_dist_end":0.13059,"object_to_goal_dist_start":0.13063,"object_z_max":0.02424,"peak_contact_force":83.54328,"phase_name":"establish_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":83.54328,"subtask_id":"contact_establish","tcp_end":[0.55045,-0.0079,0.04827],"tcp_start":[0.55042,-0.0078,0.04829],"tcp_to_object_dist_end":0.03142,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":382.0,"n_steps_budget":1000.0,"object_pos_end":[0.52156,-0.09539,0.02498],"object_pos_start":[0.54499,-0.0274,0.02424],"object_to_goal_dist_end":0.05871,"object_to_goal_dist_start":0.13059,"object_z_max":0.03572,"peak_contact_force":0.24508,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1150.0,"raw_peak_contact_force":124.66328,"subtask_id":"push_to_goal","tcp_end":[0.48191,-0.1861,0.04461],"tcp_start":[0.55045,-0.0079,0.04827],"tcp_to_object_dist_end":0.10092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":218.0,"n_steps_budget":600.0,"object_pos_end":[0.52156,-0.09539,0.02499],"object_pos_start":[0.52156,-0.09539,0.02498],"object_to_goal_dist_end":0.05871,"object_to_goal_dist_start":0.05871,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":872.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49139,-0.16017,0.10626],"tcp_start":[0.48191,-0.1861,0.04461],"tcp_to_object_dist_end":0.10822,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.55472,-0.03508,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42632,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_height":0.14906,"approach_behind.approach_speed":0.13275,"approach_behind.behind_distance":0.15219,"descend_to_push.descend_speed":0.141,"descend_to_push.descend_z_clearance":0.01007,"establish_contact.contact_force_threshold":13.90216,"establish_contact.contact_speed":0.02462,"establish_contact.contact_stroke":0.06584,"push_to_goal.push_distance":0.26133,"push_to_goal.push_speed":0.05616,"retract_after_push.arc_height":0.13091,"retract_after_push.retract_height":0.09037,"retract_after_push.retract_speed":0.07558},"optimized_scores":{"best_composite_score":0.00907,"best_fitness_score":0.54907,"best_task_score":0.55342},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":20.0,"contact_point_centroid":[0.5693,-0.01915,0.04858],"force_p95":177.78215,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":178.93128,"mean_force":139.46713,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.55789,-0.01888,0.04996]},{"body_a":"attachment","body_b":"push_box","contact_count":222.0,"contact_point_centroid":[0.55197,-0.05295,0.05148],"force_p95":119.23816,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":123.43996,"mean_force":95.79119,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54328,-0.05923,0.05255]},{"body_a":"world","body_b":"push_box","contact_count":1119.0,"contact_point_centroid":[0.53449,-0.0844,-0.00029],"force_p95":93.63325,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":108.2103,"mean_force":19.43136,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50537,-0.12964,0.04773]},{"body_a":"world","body_b":"push_box","contact_count":1344.0,"contact_point_centroid":[0.55472,-0.03509,-1e-05],"force_p95":11.18501,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.31267,"mean_force":2.33397,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.57715,0.03284,0.11537]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.57032,-0.02064,0.04753],"force_p95":76.19518,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.19518,"mean_force":76.19518,"phase_index":2.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.55855,-0.02067,0.04838]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.55478,-0.03573,-0.00032],"force_p95":29.07169,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.40708,"mean_force":19.22397,"phase_index":2.0,"phase_name":"establish_contact","phase_type":"contact","tcp_position_centroid":[0.55855,-0.02067,0.04838]},{"body_a":"world","body_b":"push_box","contact_count":1048.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.54816,0.04149,0.2447]},{"body_a":"world","body_b":"push_box","contact_count":1236.0,"contact_point_centroid":[0.52588,-0.09939,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.46569,-0.20416,0.08339]}],"total_contact_groups":8},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52588,-0.09939,0.02499],"final_tcp_position":[0.48814,-0.16472,0.1093],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":178.93128,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":262.0,"n_steps_budget":960.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1048.0,"raw_peak_contact_force":0.24534,"subtask_id":"behind_approach","tcp_end":[0.59954,0.08569,0.18801],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.20777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":336.0,"n_steps_budget":900.0,"object_pos_end":[0.55516,-0.03572,0.02435],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.1269,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":178.93128,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1364.0,"raw_peak_contact_force":178.93128,"tcp_end":[0.55855,-0.02067,0.04838],"tcp_start":[0.59954,0.08569,0.18801],"tcp_to_object_dist_end":0.02856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.55516,-0.03576,0.02433],"object_pos_start":[0.55516,-0.03572,0.02435],"object_to_goal_dist_end":0.12687,"object_to_goal_dist_start":0.1269,"object_z_max":0.02435,"peak_contact_force":76.19518,"phase_name":"establish_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":5.0,"raw_peak_contact_force":76.19518,"subtask_id":"contact_establish","tcp_end":[0.55862,-0.02076,0.04834],"tcp_start":[0.55855,-0.02067,0.04838],"tcp_to_object_dist_end":0.02852,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":442.0,"n_steps_budget":1000.0,"object_pos_end":[0.52588,-0.09939,0.02499],"object_pos_start":[0.55516,-0.03576,0.02433],"object_to_goal_dist_end":0.05684,"object_to_goal_dist_start":0.12687,"object_z_max":0.03654,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1341.0,"raw_peak_contact_force":123.43996,"subtask_id":"push_to_goal","tcp_end":[0.45476,-0.22876,0.04473],"tcp_start":[0.55862,-0.02076,0.04834],"tcp_to_object_dist_end":0.14895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":309.0,"n_steps_budget":960.0,"object_pos_end":[0.52588,-0.09939,0.02499],"object_pos_start":[0.52588,-0.09939,0.02499],"object_to_goal_dist_end":0.05684,"object_to_goal_dist_start":0.05684,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1236.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48814,-0.16472,0.1093],"tcp_start":[0.45476,-0.22876,0.04473],"tcp_to_object_dist_end":0.11314,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```