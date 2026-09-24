## Search State

- **Seed**: 8
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → approach → approach → approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 11 | -0.0198 | 0.81 | ❌ rejected |
| 12 | approach → approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.2393 | 0.88 | ✅ accepted |
| 11 | approach → align → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1594 | 0.04 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.2328 | 0.02 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | 9 | 0.2939 | 0.81 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`
- Frozen object start: [0.4792366731926673, 0.05847322120055107, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.4792366731926673, 0.05847322120055107, 0.025)
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
  frozen_object_start: [0.4792, 0.0585, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.4792366731926673, 0.05847322120055107, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0208, -0.2085, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.881, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.4792366731926673, 0.05847322120055107, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=-0.020) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_1
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
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: reach_object
- id: descend_1
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
    - 0.005
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    descend_height:
      type: scalar
      range:
      - 0.0
      - 0.1
      default: 0.005
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: align_behind_1
  type: align
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
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    pre_push_offset:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: push_1
  type: push
  generator: impedance_motion
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
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
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
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.005
    - 0.0
    - 0.0
  subtask_id: push_to_goal
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
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
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **descend_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.005], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=0, strategy=repeat
- **align_behind_1** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=replace_offset_projection, sign=negative}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - pre_push_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=25.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.005, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.020
- **task_score** (E): 0.812
- **fitness_score**: 0.650  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.670

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1048 |
| descend_1 | 1.00 | 1.00 | 0.1176 |
| align_behind_1 | 1.00 | 1.00 | 0.0819 |
| descend_2 | 1.00 | 1.00 | 0.0632 |
| push_1 | 0.33 | 1.00 | 0.1181 |
| retract_1 | 0.33 | 1.00 | 0.0962 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, -0.002, 0.215) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | approach | 1.00 / step_budget | (0.521, -0.002, 0.215)→(0.522, -0.001, 0.097) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_behind_1 | approach | 1.00 / step_budget | (0.522, -0.001, 0.097)→(0.535, 0.066, 0.056) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_2 | approach | 1.00 / step_budget | (0.535, 0.066, 0.056)→(0.524, 0.008, 0.036) | (0.526, -0.001, 0.025)→(0.524, -0.028, 0.025) | 0.156→0.129 | 1.00 / 3.000 | 6.580 | 30.529 |
| push_1 | push | 0.33 / step_budget | (0.508, -0.019, 0.035)→(0.488, -0.132, 0.031) | (0.524, -0.028, 0.025)→(0.512, -0.127, 0.027) | 0.129→0.037 | 1.00 / 2.333 | 1.859 | 29.964 |
| retract_1 | retract | 0.33 / step_budget | (0.488, -0.132, 0.031)→(0.492, -0.135, 0.123) | (0.512, -0.127, 0.027)→(0.509, -0.128, 0.025) | 0.037→0.034 | 1.00 / 4.000 | 0.245 | 2.147 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.936
- lateral_force_integral: None
- approach_alignment: 0.791
- goal_progress: 0.914
- terminal_score: 0.914
- phase_score: 0.633
- phase_breakdown.push_to_goal_score: 0.878
- phase_breakdown.reach_object_score: 0.062

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.746
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.914
- **Median Q (composite search score)**: 0.029
- **K-run variance**: 0.0107
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.321


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
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41004,"average_solve_count":239.0,"average_success_count":239.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_1.align_height":0.02196,"align_behind_1.pre_push_lateral":0.10509,"approach_1.approach_height":0.2502,"descend_1.descend_height":0.05188,"descend_1.descend_tolerance":0.02346,"descend_2.low_height":0.00915,"push_1.push_distance":0.20395,"push_1.push_speed":0.07313,"push_1.push_tolerance":0.02318,"retract_1.retract_height":0.13121,"retract_1.speed":0.01014},"optimized_scores":{"best_composite_score":-0.16371,"best_fitness_score":0.50629,"best_task_score":0.6385},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":95.0,"contact_point_centroid":[0.47601,0.06991,0.04606],"force_p95":27.61268,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.56169,"mean_force":8.90281,"phase_index":3.0,"phase_name":"descend_2","phase_type":"approach","tcp_position_centroid":[0.4723,0.08167,0.03462]},{"body_a":"attachment","body_b":"push_box","contact_count":769.0,"contact_point_centroid":[0.49155,-0.03217,0.04934],"force_p95":16.79761,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.23914,"mean_force":4.0441,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47741,-0.02664,0.02719]},{"body_a":"world","body_b":"push_box","contact_count":1122.0,"contact_point_centroid":[0.48074,0.05368,-2e-05],"force_p95":7.27417,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.43923,"mean_force":1.03472,"phase_index":3.0,"phase_name":"descend_2","phase_type":"approach","tcp_position_centroid":[0.46832,0.11269,0.04128]},{"body_a":"world","body_b":"push_box","contact_count":1413.0,"contact_point_centroid":[0.52717,-0.04506,-5e-05],"force_p95":11.5483,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.1983,"mean_force":2.7581,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47775,-0.03178,0.02713]},{"body_a":"attachment","body_b":"push_box","contact_count":45.0,"contact_point_centroid":[0.4986,-0.10479,0.05198],"force_p95":0.97123,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.0829,"mean_force":0.70661,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48176,-0.11042,0.0286]},{"body_a":"world","body_b":"push_box","contact_count":3845.0,"contact_point_centroid":[0.50966,-0.07435,-1e-05],"force_p95":0.24538,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01459,"mean_force":0.25715,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48567,-0.11332,0.06913]},{"body_a":"world","body_b":"push_box","contact_count":928.0,"contact_point_centroid":[0.47924,0.05847,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48985,0.02362,0.28658]},{"body_a":"world","body_b":"push_box","contact_count":1392.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"approach","tcp_position_centroid":[0.47809,0.05274,0.18657]},{"body_a":"world","body_b":"push_box","contact_count":896.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"align_behind_1","phase_type":"approach","tcp_position_centroid":[0.47093,0.09915,0.07267]}],"total_contact_groups":9},"final_pose_error":0.05606,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50914,-0.07482,0.02499],"final_tcp_position":[0.4909,-0.12307,0.1079],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":28.56169,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":232.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":928.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.48051,0.04876,0.27472],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.24992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":348.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1392.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.47664,0.05694,0.09638],"tcp_start":[0.48051,0.04876,0.27472],"tcp_to_object_dist_end":0.07146,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":224.0,"n_steps_budget":750.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":896.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.467,0.14394,0.05099],"tcp_start":[0.47664,0.05694,0.09638],"tcp_to_object_dist_end":0.09017,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":371.0,"n_steps_budget":600.0,"object_pos_end":[0.48713,0.03132,0.02567],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.18177,"object_to_goal_dist_start":0.2095,"object_z_max":0.02564,"peak_contact_force":0.53022,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1217.0,"raw_peak_contact_force":28.56169,"subtask_id":"reach_object","tcp_end":[0.47442,0.06671,0.03166],"tcp_start":[0.467,0.14394,0.05099],"tcp_to_object_dist_end":0.03808,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50982,-0.07307,0.02731],"object_pos_start":[0.48713,0.03132,0.02567],"object_to_goal_dist_end":0.07759,"object_to_goal_dist_start":0.18177,"object_z_max":0.03026,"peak_contact_force":1.12597,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2182.0,"raw_peak_contact_force":24.23914,"subtask_id":"push_to_goal","tcp_end":[0.48309,-0.11079,0.02634],"tcp_start":[0.47442,0.06671,0.03166],"tcp_to_object_dist_end":0.04624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50914,-0.07482,0.02499],"object_pos_start":[0.50982,-0.07307,0.02731],"object_to_goal_dist_end":0.07574,"object_to_goal_dist_start":0.07759,"object_z_max":0.02731,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3890.0,"raw_peak_contact_force":2.0829,"tcp_end":[0.4909,-0.12307,0.1079],"tcp_start":[0.48309,-0.11079,0.02634],"tcp_to_object_dist_end":0.09764,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35122,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_1.align_height":0.03682,"align_behind_1.pre_push_lateral":0.08288,"approach_1.approach_height":0.11801,"descend_1.descend_height":0.04281,"descend_1.descend_tolerance":0.02427,"descend_2.low_height":0.01767,"push_1.push_distance":0.32955,"push_1.push_speed":0.05518,"push_1.push_tolerance":0.00819,"retract_1.retract_height":0.16028,"retract_1.speed":0.0512},"optimized_scores":{"best_composite_score":0.02875,"best_fitness_score":0.69875,"best_task_score":0.88332},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":90.0,"contact_point_centroid":[0.54668,-0.01284,0.04488],"force_p95":28.12815,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.21688,"mean_force":11.35174,"phase_index":3.0,"phase_name":"descend_2","phase_type":"approach","tcp_position_centroid":[0.54736,-0.00103,0.04471]},{"body_a":"attachment","body_b":"push_box","contact_count":749.0,"contact_point_centroid":[0.51331,-0.10904,0.04784],"force_p95":17.65629,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.99979,"mean_force":4.89497,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50563,-0.09918,0.03558]},{"body_a":"world","body_b":"push_box","contact_count":734.0,"contact_point_centroid":[0.54294,-0.03331,-4e-05],"force_p95":11.36426,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.97122,"mean_force":1.68075,"phase_index":3.0,"phase_name":"descend_2","phase_type":"approach","tcp_position_centroid":[0.55267,0.0151,0.05067]},{"body_a":"world","body_b":"push_box","contact_count":1568.0,"contact_point_centroid":[0.53396,-0.133,-7e-05],"force_p95":8.73264,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.06769,"mean_force":2.79975,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50689,-0.09626,0.03565]},{"body_a":"world","body_b":"push_box","contact_count":3443.0,"contact_point_centroid":[0.51166,-0.1637,-2e-05],"force_p95":0.55467,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.23111,"mean_force":0.2976,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47976,-0.15419,0.08502]},{"body_a":"attachment","body_b":"push_box","contact_count":162.0,"contact_point_centroid":[0.4878,-0.17186,0.05591],"force_p95":1.23326,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.71779,"mean_force":0.76189,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47302,-0.16939,0.04576]},{"body_a":"world","body_b":"push_box","contact_count":2092.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5177,-0.0115,0.22502]},{"body_a":"world","body_b":"push_box","contact_count":496.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"approach","tcp_position_centroid":[0.53817,-0.02418,0.11951]},{"body_a":"world","body_b":"push_box","contact_count":692.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"align_behind_1","phase_type":"approach","tcp_position_centroid":[0.54921,0.00436,0.07253]}],"total_contact_groups":9},"final_pose_error":0.06174,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50813,-0.1631,0.02499],"final_tcp_position":[0.48702,-0.14536,0.12509],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":33.21688,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2092.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.53773,-0.02348,0.15012],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12532,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":124.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":496.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.53946,-0.02492,0.08669],"tcp_start":[0.53773,-0.02348,0.15012],"tcp_to_object_dist_end":0.0619,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":173.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":692.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.56166,0.0356,0.06131],"tcp_start":[0.53946,-0.02492,0.08669],"tcp_to_object_dist_end":0.07321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":263.0,"n_steps_budget":600.0,"object_pos_end":[0.53894,-0.05278,0.0247],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.10473,"object_to_goal_dist_start":0.13211,"object_z_max":0.02549,"peak_contact_force":19.21003,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":824.0,"raw_peak_contact_force":33.21688,"subtask_id":"reach_object","tcp_end":[0.54301,-0.01611,0.04006],"tcp_start":[0.56166,0.0356,0.06131],"tcp_to_object_dist_end":0.03997,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51469,-0.16507,0.02984],"object_pos_start":[0.53894,-0.05278,0.0247],"object_to_goal_dist_end":0.0216,"object_to_goal_dist_start":0.10473,"object_z_max":0.02992,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2317.0,"raw_peak_contact_force":23.99979,"subtask_id":"push_to_goal","tcp_end":[0.47375,-0.17824,0.03575],"tcp_start":[0.54301,-0.01611,0.04006],"tcp_to_object_dist_end":0.04342,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50813,-0.1631,0.02499],"object_pos_start":[0.51469,-0.16507,0.02984],"object_to_goal_dist_end":0.01542,"object_to_goal_dist_start":0.0216,"object_z_max":0.02984,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3605.0,"raw_peak_contact_force":2.23111,"tcp_end":[0.48702,-0.14536,0.12509],"tcp_start":[0.47375,-0.17824,0.03575],"tcp_to_object_dist_end":0.10383,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56364,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind_1.align_height":0.02322,"align_behind_1.pre_push_lateral":0.07372,"approach_1.approach_height":0.19064,"descend_1.descend_height":0.0643,"descend_1.descend_tolerance":0.02189,"descend_2.low_height":0.01444,"push_1.push_distance":0.23814,"push_1.push_speed":0.06512,"push_1.push_tolerance":0.01385,"retract_1.retract_height":0.13419,"retract_1.speed":0.06687},"optimized_scores":{"best_composite_score":0.07553,"best_fitness_score":0.74553,"best_task_score":0.91367},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":335.0,"contact_point_centroid":[0.52623,-0.0814,0.03301],"force_p95":19.54674,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.65189,"mean_force":6.52008,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52752,-0.06958,0.03194]},{"body_a":"attachment","body_b":"push_box","contact_count":95.0,"contact_point_centroid":[0.55943,-0.02288,0.04225],"force_p95":28.71029,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.80759,"mean_force":10.66544,"phase_index":3.0,"phase_name":"descend_2","phase_type":"approach","tcp_position_centroid":[0.55996,-0.01106,0.04116]},{"body_a":"world","body_b":"push_box","contact_count":610.0,"contact_point_centroid":[0.55145,-0.04281,-6e-05],"force_p95":11.37566,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.56748,"mean_force":1.95291,"phase_index":3.0,"phase_name":"descend_2","phase_type":"approach","tcp_position_centroid":[0.5651,0.00034,0.04564]},{"body_a":"world","body_b":"push_box","contact_count":903.0,"contact_point_centroid":[0.52491,-0.10799,-9e-05],"force_p95":7.75324,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.46301,"mean_force":2.75421,"phase_index":4.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52866,-0.06756,0.03205]},{"body_a":"world","body_b":"push_box","contact_count":3973.0,"contact_point_centroid":[0.51004,-0.14558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.12601,"mean_force":0.24711,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50057,-0.11611,0.08618]},{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.51156,-0.11968,0.04778],"force_p95":1.80412,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.99491,"mean_force":0.60909,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50725,-0.10783,0.03175]},{"body_a":"world","body_b":"push_box","contact_count":1476.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52206,-0.01535,0.25885]},{"body_a":"world","body_b":"push_box","contact_count":840.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"approach","tcp_position_centroid":[0.54761,-0.0327,0.16499]},{"body_a":"world","body_b":"push_box","contact_count":692.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"align_behind_1","phase_type":"approach","tcp_position_centroid":[0.56116,-0.00968,0.08106]}],"total_contact_groups":9},"final_pose_error":0.02597,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51005,-0.14557,0.02499],"final_tcp_position":[0.49777,-0.13643,0.13716],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":41.65189,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":369.0,"n_steps_budget":690.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.54625,-0.03125,0.21907],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1943,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":210.0,"n_steps_budget":840.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":840.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.55008,-0.03424,0.10855],"tcp_start":[0.54625,-0.03125,0.21907],"tcp_to_object_dist_end":0.08369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":173.0,"n_steps_budget":630.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":692.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.5749,0.01698,0.05529],"tcp_start":[0.55008,-0.03424,0.10855],"tcp_to_object_dist_end":0.06353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":228.0,"n_steps_budget":600.0,"object_pos_end":[0.54533,-0.06153,0.02481],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.09941,"object_to_goal_dist_start":0.12728,"object_z_max":0.0256,"peak_contact_force":0.00114,"phase_name":"descend_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":705.0,"raw_peak_contact_force":29.80759,"subtask_id":"reach_object","tcp_end":[0.55416,-0.02552,0.03662],"tcp_start":[0.5749,0.01698,0.05529],"tcp_to_object_dist_end":0.03892,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.51049,-0.14396,0.02467],"object_pos_start":[0.54533,-0.06153,0.02481],"object_to_goal_dist_end":0.01211,"object_to_goal_dist_start":0.09941,"object_z_max":0.02558,"peak_contact_force":4.4522,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1238.0,"raw_peak_contact_force":41.65189,"subtask_id":"push_to_goal","tcp_end":[0.50759,-0.10776,0.03181],"tcp_start":[0.50764,-0.10769,0.03184],"tcp_to_object_dist_end":0.03701,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51005,-0.14557,0.02499],"object_pos_start":[0.51049,-0.14415,0.02486],"object_to_goal_dist_end":0.01099,"object_to_goal_dist_start":0.01202,"object_z_max":0.02516,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3981.0,"raw_peak_contact_force":2.12601,"tcp_end":[0.49777,-0.13643,0.13716],"tcp_start":[0.50759,-0.10776,0.03181],"tcp_to_object_dist_end":0.11321,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```