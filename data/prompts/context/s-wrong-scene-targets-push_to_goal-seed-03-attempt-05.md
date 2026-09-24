## Search State

- **Seed**: 3
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → push → push → lift → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.5258 | 0.91 | ✅ accepted |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.8237 | 0.88 | ✅ accepted |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.7916 | 0.86 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.9147 | 0.87 | ✅ accepted |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.7667 | 0.82 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.45027790005723495, -0.03158273920846803, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.45027790005723495, -0.03158273920846803, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.914, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.526) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: contact_object
  anchor: object
  metric: contact
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
    - 0.1
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
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
    approach_standoff:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  subtask_id: contact_object
- id: descend_1
  type: descend
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descend_force_threshold:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_lateral_offset:
      type: scalar
      range:
      - 0.0
      - 0.05
      default: 0.01
      binds_to:
      - path: retry.offset.x
        mode: replace
      - path: retry.offset.y
        mode: replace
  guards:
  - id: contact_made
    when: after_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.01
    - 0.01
    - 0.0
  subtask_id: contact_object
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: -0.05
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_offset:
      type: scalar
      range:
      - -0.15
      - -0.01
      default: -0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.25
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal
- id: push_2
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: -0.01
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    push_fine_offset:
      type: scalar
      range:
      - -0.03
      - -0.005
      default: -0.01
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_fine_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.01
    orientation:
      mode: keep_current
- id: retract_1
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
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: none

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_standoff: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_lateral_offset: status=consumed; consumers=retry.offset.x (replace), retry.offset.y (replace)
  - guards:
    - id=contact_made, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.01, 0.01, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=-0.05, mode=replace_offset_projection, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **push_2** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=-0.01, mode=replace_offset_projection, sign=positive}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_fine_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_fine_speed: status=consumed; consumers=generator.speed (replace)
- **lift_1** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=none
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.526
- **task_score** (E): 0.914
- **fitness_score**: 0.879  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.520

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2413 |
| descend_1 | 1.00 | 1.00 | 0.1205 |
| push_1 | 1.00 | 1.00 | 0.0763 |
| push_2 | 1.00 | 1.00 | 0.0987 |
| lift_1 | 1.00 | 1.00 | 0.1646 |
| retract_1 | 1.00 | 1.00 | 0.0907 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.131, 0.121) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / force_exceeded | (0.520, 0.131, 0.121)→(0.510, 0.039, 0.048) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 5.000 | 50610.529 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.510, 0.039, 0.048)→(0.495, -0.029, 0.025) | (0.513, 0.002, 0.025)→(0.495, -0.065, 0.025) | 0.160→0.090 | 1.00 / 2.333 | 0.365 | 73.516 |
| push_2 | push | 1.00 / step_budget | (0.495, -0.029, 0.025)→(0.495, -0.122, 0.020) | (0.495, -0.065, 0.025)→(0.502, -0.155, 0.026) | 0.090→0.015 | 1.00 / 3.000 | 5.969 | 28.164 |
| lift_1 | lift | 1.00 / step_budget | (0.495, -0.122, 0.020)→(0.492, -0.122, 0.185) | (0.502, -0.155, 0.026)→(0.500, -0.155, 0.025) | 0.015→0.014 | 1.00 / 4.000 | 0.245 | 12.581 |
| retract_1 | retract | 1.00 / step_budget | (0.492, -0.122, 0.185)→(0.522, -0.144, 0.179) | (0.500, -0.155, 0.025)→(0.500, -0.155, 0.025) | 0.014→0.014 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.859
- goal_progress: 0.969
- terminal_score: 0.969
- phase_score: 0.975
- phase_breakdown.push_to_goal_score: 0.964
- phase_breakdown.contact_object_score: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.972
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.969
- **Median Q (composite search score)**: 0.512
- **K-run variance**: 0.0050
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: push_1.push_offset
- **Final σ (mean)**: 0.397


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.45028,-0.03158,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77381,"average_solve_count":168.0,"average_success_count":168.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.07344,"approach_1.approach_standoff":0.11735,"descend_1.descend_force_threshold":2.05745,"descend_1.descend_lateral_offset":0.04241,"push_1.push_offset":-0.14999,"push_1.push_speed":0.16065,"push_2.push_fine_offset":-0.02747,"push_2.push_fine_speed":0.19967},"optimized_scores":{"best_composite_score":0.61905,"best_fitness_score":0.97238,"best_task_score":0.9691},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":61.0,"contact_point_centroid":[0.4363,-0.01116,0.04969],"force_p95":120.10433,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.52819,"mean_force":30.71998,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43346,0.00065,0.04163]},{"body_a":"world","body_b":"push_box","contact_count":288.0,"contact_point_centroid":[0.4513,-0.04113,-0.00011],"force_p95":30.29283,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.83097,"mean_force":6.80909,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.43355,0.00039,0.04106]},{"body_a":"attachment","body_b":"push_box","contact_count":339.0,"contact_point_centroid":[0.46238,-0.06722,0.04841],"force_p95":26.0079,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.16495,"mean_force":8.02964,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.4553,-0.05542,0.02448]},{"body_a":"world","body_b":"push_box","contact_count":737.0,"contact_point_centroid":[0.47708,-0.10952,-8e-05],"force_p95":14.29933,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.30214,"mean_force":4.22155,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.4563,-0.05751,0.02447]},{"body_a":"world","body_b":"push_box","contact_count":3944.0,"contact_point_centroid":[0.50399,-0.15001,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.77929,"mean_force":0.24898,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47812,-0.1147,0.10383]},{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.48771,-0.12689,0.04948],"force_p95":1.26491,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.26933,"mean_force":0.90827,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4798,-0.11525,0.02432]},{"body_a":"world","body_b":"push_box","contact_count":2844.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.45327,0.03557,0.20252]},{"body_a":"world","body_b":"push_box","contact_count":2212.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.41818,0.03889,0.07778]},{"body_a":"world","body_b":"push_box","contact_count":2168.0,"contact_point_centroid":[0.50396,-0.14976,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52368,-0.1114,0.18085]}],"total_contact_groups":9},"final_pose_error":0.01151,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50396,-0.14976,0.02499],"final_tcp_position":[0.56856,-0.1086,0.17946],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":711.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2844.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.40755,0.07181,0.10669],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13853,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":553.0,"n_steps_budget":870.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2212.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.43182,0.00501,0.05047],"tcp_start":[0.40755,0.07181,0.10669],"tcp_to_object_dist_end":0.04825,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":111.0,"n_steps_budget":600.0,"object_pos_end":[0.45169,-0.04163,0.02519],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.11865,"object_to_goal_dist_start":0.12843,"object_z_max":0.02521,"peak_contact_force":0.40733,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":349.0,"raw_peak_contact_force":138.52819,"subtask_id":"push_to_goal","tcp_end":[0.43614,-0.00558,0.03024],"tcp_start":[0.43182,0.00501,0.05047],"tcp_to_object_dist_end":0.03958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.50428,-0.14949,0.02488],"object_pos_start":[0.45169,-0.04163,0.02519],"object_to_goal_dist_end":0.00431,"object_to_goal_dist_start":0.11865,"object_z_max":0.026,"peak_contact_force":0.00178,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1076.0,"raw_peak_contact_force":37.16495,"subtask_id":"push_to_goal","tcp_end":[0.48135,-0.11533,0.02094],"tcp_start":[0.43614,-0.00558,0.03024],"tcp_to_object_dist_end":0.04133,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50396,-0.14976,0.02499],"object_pos_start":[0.50428,-0.14949,0.02488],"object_to_goal_dist_end":0.00397,"object_to_goal_dist_start":0.00431,"object_z_max":0.02582,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3965.0,"raw_peak_contact_force":5.77929,"tcp_end":[0.47849,-0.11474,0.18587],"tcp_start":[0.48135,-0.11533,0.02094],"tcp_to_object_dist_end":0.1666,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":630.0,"object_pos_end":[0.50396,-0.14976,0.02499],"object_pos_start":[0.50396,-0.14976,0.02499],"object_to_goal_dist_end":0.00397,"object_to_goal_dist_start":0.00397,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.56856,-0.1086,0.17946],"tcp_start":[0.47849,-0.11474,0.18587],"tcp_to_object_dist_end":0.17242,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.55317,0.00136,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90055,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.08009,"approach_1.approach_standoff":0.17975,"descend_1.descend_force_threshold":6.32743,"descend_1.descend_lateral_offset":0.01979,"push_1.push_offset":-0.08693,"push_1.push_speed":0.162,"push_2.push_fine_offset":-0.01766,"push_2.push_fine_speed":0.14106},"optimized_scores":{"best_composite_score":0.44677,"best_fitness_score":0.8001,"best_task_score":0.86665},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":247.0,"contact_point_centroid":[0.5426,-0.0156,0.03454],"force_p95":31.37566,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.94715,"mean_force":10.64271,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5436,-0.00388,0.03231]},{"body_a":"attachment","body_b":"push_box","contact_count":372.0,"contact_point_centroid":[0.50875,-0.10516,0.0192],"force_p95":11.99107,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.94589,"mean_force":3.47245,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.51246,-0.09381,0.01829]},{"body_a":"world","body_b":"push_box","contact_count":931.0,"contact_point_centroid":[0.5366,-0.04567,-0.00024],"force_p95":12.03183,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.129,"mean_force":3.17268,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54158,-0.01043,0.03093]},{"body_a":"world","body_b":"push_box","contact_count":1105.0,"contact_point_centroid":[0.49532,-0.12603,-6e-05],"force_p95":4.19835,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.36088,"mean_force":1.46075,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.51383,-0.09025,0.01845]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49791,-0.13795,0.02061],"force_p95":4.78253,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.78253,"mean_force":4.78253,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50222,-0.1268,0.01957]},{"body_a":"world","body_b":"push_box","contact_count":3985.0,"contact_point_centroid":[0.48061,-0.15907,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.02224,"mean_force":0.24713,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49891,-0.12603,0.10105]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54676,0.07451,0.20941]},{"body_a":"world","body_b":"push_box","contact_count":3320.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5749,0.09233,0.08226]},{"body_a":"world","body_b":"push_box","contact_count":1416.0,"contact_point_centroid":[0.48063,-0.15908,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.45731,-0.14408,0.18005]}],"total_contact_groups":9},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48063,-0.15908,0.02499],"final_tcp_position":[0.41611,-0.1631,0.17979],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":44.51346,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.59358,0.14636,0.12525],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.18086,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":830.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":44.51346,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3320.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.55928,0.03826,0.04482],"tcp_start":[0.59358,0.14636,0.12525],"tcp_to_object_dist_end":0.04233,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":467.0,"n_steps_budget":600.0,"object_pos_end":[0.51545,-0.09421,0.02446],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.05789,"object_to_goal_dist_start":0.16043,"object_z_max":0.02682,"peak_contact_force":0.68764,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1178.0,"raw_peak_contact_force":43.94715,"subtask_id":"push_to_goal","tcp_end":[0.5272,-0.05881,0.02142],"tcp_start":[0.55928,0.03826,0.04482],"tcp_to_object_dist_end":0.03742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.48152,-0.15816,0.025],"object_pos_start":[0.51545,-0.09421,0.02446],"object_to_goal_dist_end":0.0202,"object_to_goal_dist_start":0.05789,"object_z_max":0.02535,"peak_contact_force":0.70646,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1477.0,"raw_peak_contact_force":19.94589,"subtask_id":"push_to_goal","tcp_end":[0.50226,-0.12672,0.01959],"tcp_start":[0.5272,-0.05881,0.02142],"tcp_to_object_dist_end":0.03805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48063,-0.15908,0.02499],"object_pos_start":[0.48152,-0.15816,0.025],"object_to_goal_dist_end":0.02139,"object_to_goal_dist_start":0.0202,"object_z_max":0.02504,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3986.0,"raw_peak_contact_force":4.78253,"tcp_end":[0.49931,-0.12609,0.18389],"tcp_start":[0.50226,-0.12672,0.01959],"tcp_to_object_dist_end":0.16336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":354.0,"n_steps_budget":630.0,"object_pos_end":[0.48063,-0.15908,0.02499],"object_pos_start":[0.48063,-0.15908,0.02499],"object_to_goal_dist_end":0.02139,"object_to_goal_dist_start":0.02139,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1416.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.41611,-0.1631,0.17979],"tcp_start":[0.49931,-0.12609,0.18389],"tcp_to_object_dist_end":0.16776,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.5366,0.03695,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10558,"approach_1.approach_standoff":0.14879,"descend_1.descend_force_threshold":8.01795,"descend_1.descend_lateral_offset":0.01532,"push_1.push_offset":-0.12137,"push_1.push_speed":0.14257,"push_2.push_fine_offset":-0.01608,"push_2.push_fine_speed":0.17993},"optimized_scores":{"best_composite_score":0.51152,"best_fitness_score":0.86485,"best_task_score":0.90509},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":324.0,"contact_point_centroid":[0.52879,0.00959,0.03737],"force_p95":31.25996,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.07216,"mean_force":10.45713,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52749,0.02143,0.03215]},{"body_a":"world","body_b":"push_box","contact_count":725.0,"contact_point_centroid":[0.52485,-0.11563,-8e-05],"force_p95":18.53963,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.3798,"mean_force":4.90478,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.51033,-0.06607,0.01907]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.53429,-0.13714,0.05411],"force_p95":23.51396,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.18152,"mean_force":7.35183,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.50105,-0.12478,0.0206]},{"body_a":"push_box","body_b":"link7","contact_count":104.0,"contact_point_centroid":[0.53637,-0.12261,0.05329],"force_p95":24.90758,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.82929,"mean_force":13.11753,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.50303,-0.11125,0.01984]},{"body_a":"attachment","body_b":"push_box","contact_count":444.0,"contact_point_centroid":[0.51568,-0.08147,0.03593],"force_p95":15.57154,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.54242,"mean_force":4.49465,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.50948,-0.07001,0.01889]},{"body_a":"world","body_b":"push_box","contact_count":3674.0,"contact_point_centroid":[0.51802,-0.15873,-1e-05],"force_p95":0.38641,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.77652,"mean_force":0.27577,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49789,-0.12395,0.10805]},{"body_a":"world","body_b":"push_box","contact_count":899.0,"contact_point_centroid":[0.52523,-0.01476,-0.00012],"force_p95":15.14146,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.35616,"mean_force":4.09957,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52796,0.02475,0.03285]},{"body_a":"attachment","body_b":"push_box","contact_count":92.0,"contact_point_centroid":[0.51141,-0.13329,0.05299],"force_p95":0.88088,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.19694,"mean_force":0.83673,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.49841,-0.12416,0.03244]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52913,0.08857,0.21262]},{"body_a":"world","body_b":"push_box","contact_count":3156.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54746,0.12405,0.08719]},{"body_a":"world","body_b":"push_box","contact_count":2168.0,"contact_point_centroid":[0.51664,-0.15707,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":5.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53975,-0.14214,0.17973]}],"total_contact_groups":11},"final_pose_error":0.01186,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51664,-0.15707,0.02499],"final_tcp_position":[0.58112,-0.1598,0.17834],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.55921,0.17452,0.13109],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":789.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3156.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.53867,0.07383,0.04832],"tcp_start":[0.55921,0.17452,0.13109],"tcp_to_object_dist_end":0.04368,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.51913,-0.05858,0.02514],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.0934,"object_to_goal_dist_start":0.1905,"object_z_max":0.02565,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1223.0,"raw_peak_contact_force":38.07216,"subtask_id":"push_to_goal","tcp_end":[0.52066,-0.02175,0.02202],"tcp_start":[0.53867,0.07383,0.04832],"tcp_to_object_dist_end":0.03699,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":550.0,"n_steps_budget":600.0,"object_pos_end":[0.51953,-0.15875,0.02799],"object_pos_start":[0.51913,-0.05858,0.02514],"object_to_goal_dist_end":0.02161,"object_to_goal_dist_start":0.0934,"object_z_max":0.02796,"peak_contact_force":17.19974,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1273.0,"raw_peak_contact_force":27.3798,"subtask_id":"push_to_goal","tcp_end":[0.50125,-0.12464,0.02054],"tcp_start":[0.52066,-0.02175,0.02202],"tcp_to_object_dist_end":0.03941,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51664,-0.15707,0.02499],"object_pos_start":[0.51953,-0.15875,0.02799],"object_to_goal_dist_end":0.01808,"object_to_goal_dist_start":0.02161,"object_z_max":0.02806,"peak_contact_force":0.24525,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3772.0,"raw_peak_contact_force":27.18152,"tcp_end":[0.49832,-0.12402,0.18506],"tcp_start":[0.50125,-0.12464,0.02054],"tcp_to_object_dist_end":0.16447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":542.0,"n_steps_budget":630.0,"object_pos_end":[0.51664,-0.15707,0.02499],"object_pos_start":[0.51664,-0.15707,0.02499],"object_to_goal_dist_end":0.01808,"object_to_goal_dist_start":0.01808,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2168.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.58112,-0.1598,0.17834],"tcp_start":[0.49832,-0.12402,0.18506],"tcp_to_object_dist_end":0.16638,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```