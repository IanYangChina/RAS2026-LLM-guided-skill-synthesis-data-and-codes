## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → lift → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 6 | 0.3069 | 0.82 | ❌ rejected |
| 11 | approach → descend → push → lift → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 7 | 0.2652 | 0.85 | ✅ accepted |
| 10 | approach → descend → push → lift → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 7 | 0.3345 | 0.81 | ✅ accepted |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.3836 | 0.81 | ✅ accepted |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3557 | 0.64 | ❌ rejected |

**Proposal policy**: task_score is 0.82 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.846, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.307) — your mutation base

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

- **Composite score**: 0.307
- **task_score** (E): 0.822
- **fitness_score**: 0.697  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1641 |
| descend_to_contact | 1.00 | 1.00 | 0.1180 |
| push_to_goal | 1.00 | 1.00 | 0.1341 |
| lift_off | 1.00 | 1.00 | 0.2870 |
| retract_to_home | 1.00 | 1.00 | 0.1278 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, 0.035, 0.151) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 1.00 / step_budget | (0.510, 0.035, 0.151)→(0.512, 0.038, 0.034) | (0.513, 0.002, 0.025)→(0.513, -0.001, 0.025) | 0.160→0.157 | 1.00 / 2.667 | 0.480 | 159.545 |
| push_to_goal | push | 1.00 / time_limit | (0.512, 0.038, 0.034)→(0.501, -0.089, 0.026) | (0.513, -0.001, 0.025)→(0.505, -0.121, 0.025) | 0.157→0.031 | 1.00 / 2.333 | 0.968 | 23.432 |
| lift_off | lift | 1.00 / step_budget | (0.501, -0.089, 0.026)→(0.498, -0.147, 0.305) | (0.505, -0.121, 0.025)→(0.504, -0.122, 0.025) | 0.031→0.030 | 1.00 / 4.000 | 0.245 | 2.014 |
| retract_to_home | retract | 1.00 / step_budget | (0.498, -0.147, 0.305)→(0.498, -0.019, 0.296) | (0.504, -0.122, 0.025)→(0.504, -0.122, 0.025) | 0.030→0.030 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.956
- lateral_force_integral: None
- approach_alignment: 0.969
- goal_progress: 0.932
- terminal_score: 0.932
- phase_score: 0.693
- phase_breakdown.push_to_goal_score: 0.930
- phase_breakdown.reach_pre_contact_score: 0.141

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.789
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.932
- **Median Q (composite search score)**: 0.334
- **K-run variance**: 0.0078
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.335


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91667,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_z_offset":0.11817,"approach_behind.behind_distance":0.05012,"descend_to_contact.behind_distance":0.0361,"push_to_goal.push_duration":4.59342,"push_to_goal.push_extension":0.16733,"push_to_goal.push_speed":0.07581},"optimized_scores":{"best_composite_score":0.33382,"best_fitness_score":0.72382,"best_task_score":0.85394},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.43498,-0.00699,0.04939],"force_p95":95.43981,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":97.62927,"mean_force":58.70184,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.43282,0.00431,0.04953]},{"body_a":"world","body_b":"push_box","contact_count":1605.0,"contact_point_centroid":[0.45031,-0.032,-2e-05],"force_p95":0.3191,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.10454,"mean_force":0.68975,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4324,0.00826,0.09408]},{"body_a":"attachment","body_b":"push_box","contact_count":704.0,"contact_point_centroid":[0.46166,-0.06254,0.04987],"force_p95":14.29663,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.8748,"mean_force":6.39424,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45361,-0.05122,0.02887]},{"body_a":"world","body_b":"push_box","contact_count":1648.0,"contact_point_centroid":[0.48471,-0.10045,-5e-05],"force_p95":9.04897,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.28492,"mean_force":3.17407,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45568,-0.05579,0.02877]},{"body_a":"world","body_b":"push_box","contact_count":3467.0,"contact_point_centroid":[0.5122,-0.13573,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87469,"mean_force":0.24595,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.48649,-0.12842,0.16568]},{"body_a":"world","body_b":"push_box","contact_count":1972.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.467,0.00648,0.22649]},{"body_a":"world","body_b":"push_box","contact_count":1216.0,"contact_point_centroid":[0.5122,-0.13575,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_to_home","phase_type":"retract","tcp_position_centroid":[0.49716,-0.08422,0.29895]}],"total_contact_groups":7},"final_pose_error":0.01967,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5122,-0.13575,0.02499],"final_tcp_position":[0.49802,-0.0191,0.29573],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":97.62927,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":493.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1972.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.434,0.01333,0.15251],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13617,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":410.0,"n_steps_budget":810.0,"object_pos_end":[0.44943,-0.03449,0.02491],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12609,"object_to_goal_dist_start":0.12843,"object_z_max":0.02517,"peak_contact_force":0.24834,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1617.0,"raw_peak_contact_force":97.62927,"subtask_id":"reach_pre_contact","tcp_end":[0.43298,0.003,0.03421],"tcp_start":[0.434,0.01333,0.15251],"tcp_to_object_dist_end":0.04198,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51181,-0.13532,0.02493],"object_pos_start":[0.44943,-0.03449,0.02491],"object_to_goal_dist_end":0.01884,"object_to_goal_dist_start":0.12609,"object_z_max":0.02622,"peak_contact_force":0.9903,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2352.0,"raw_peak_contact_force":30.8748,"subtask_id":"push_to_goal","tcp_end":[0.47889,-0.10941,0.02639],"tcp_start":[0.43298,0.003,0.03421],"tcp_to_object_dist_end":0.04192,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":867.0,"n_steps_budget":1000.0,"object_pos_end":[0.5122,-0.13575,0.02499],"object_pos_start":[0.51181,-0.13532,0.02493],"object_to_goal_dist_end":0.01876,"object_to_goal_dist_start":0.01884,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3467.0,"raw_peak_contact_force":0.87469,"tcp_end":[0.49733,-0.14761,0.30535],"tcp_start":[0.47889,-0.10941,0.02639],"tcp_to_object_dist_end":0.28101,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":304.0,"n_steps_budget":930.0,"object_pos_end":[0.5122,-0.13575,0.02499],"object_pos_start":[0.5122,-0.13575,0.02499],"object_to_goal_dist_end":0.01876,"object_to_goal_dist_start":0.01876,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_to_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1216.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49802,-0.0191,0.29573],"tcp_start":[0.49733,-0.14761,0.30535],"tcp_to_object_dist_end":0.29515,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92188,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_z_offset":0.1196,"approach_behind.behind_distance":0.04574,"descend_to_contact.behind_distance":0.0362,"push_to_goal.push_duration":6.06162,"push_to_goal.push_extension":0.17661,"push_to_goal.push_speed":0.09104},"optimized_scores":{"best_composite_score":0.39878,"best_fitness_score":0.78878,"best_task_score":0.93246},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":19.0,"contact_point_centroid":[0.56366,0.02578,0.04711],"force_p95":103.42348,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.64299,"mean_force":62.71487,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.56054,0.03674,0.04739]},{"body_a":"world","body_b":"push_box","contact_count":1359.0,"contact_point_centroid":[0.5531,0.00115,-2e-05],"force_p95":0.53152,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":137.92464,"mean_force":1.13171,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.55932,0.03863,0.09259]},{"body_a":"attachment","body_b":"push_box","contact_count":747.0,"contact_point_centroid":[0.53251,-0.04189,0.0275],"force_p95":17.11872,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.21642,"mean_force":5.18768,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53424,-0.03009,0.0271]},{"body_a":"world","body_b":"push_box","contact_count":1918.0,"contact_point_centroid":[0.52413,-0.07441,-5e-05],"force_p95":6.49001,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.40837,"mean_force":2.32801,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53296,-0.03393,0.02705]},{"body_a":"attachment","body_b":"push_box","contact_count":35.0,"contact_point_centroid":[0.5033,-0.1184,0.03943],"force_p95":2.34913,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.55117,"mean_force":1.00431,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50575,-0.10669,0.03887]},{"body_a":"world","body_b":"push_box","contact_count":3259.0,"contact_point_centroid":[0.49451,-0.14182,-2e-05],"force_p95":0.36673,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.36257,"mean_force":0.26025,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50162,-0.12707,0.17301]},{"body_a":"world","body_b":"push_box","contact_count":2368.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52906,0.02033,0.22398]},{"body_a":"world","body_b":"push_box","contact_count":1212.0,"contact_point_centroid":[0.49479,-0.1405,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_to_home","phase_type":"retract","tcp_position_centroid":[0.49797,-0.08426,0.2989]}],"total_contact_groups":8},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49479,-0.1405,0.02499],"final_tcp_position":[0.4982,-0.01937,0.29573],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":163.64299,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":592.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2368.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.56037,0.04115,0.14948],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1309,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":352.0,"n_steps_budget":780.0,"object_pos_end":[0.5531,-0.00049,0.02496],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15866,"object_to_goal_dist_start":0.16043,"object_z_max":0.02509,"peak_contact_force":0.47801,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1378.0,"raw_peak_contact_force":163.64299,"subtask_id":"reach_pre_contact","tcp_end":[0.56101,0.03639,0.0338],"tcp_start":[0.56037,0.04115,0.14948],"tcp_to_object_dist_end":0.03874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49644,-0.13942,0.02502],"object_pos_start":[0.5531,-0.00049,0.02496],"object_to_goal_dist_end":0.01117,"object_to_goal_dist_start":0.15866,"object_z_max":0.0254,"peak_contact_force":0.94486,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2665.0,"raw_peak_contact_force":21.21642,"subtask_id":"push_to_goal","tcp_end":[0.50879,-0.10436,0.02532],"tcp_start":[0.56101,0.03639,0.0338],"tcp_to_object_dist_end":0.03717,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":870.0,"n_steps_budget":1000.0,"object_pos_end":[0.49479,-0.1405,0.02499],"object_pos_start":[0.49644,-0.13942,0.02502],"object_to_goal_dist_end":0.01083,"object_to_goal_dist_start":0.01117,"object_z_max":0.02669,"peak_contact_force":0.24525,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3294.0,"raw_peak_contact_force":2.55117,"tcp_end":[0.49876,-0.14737,0.30527],"tcp_start":[0.50879,-0.10436,0.02532],"tcp_to_object_dist_end":0.28039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":930.0,"object_pos_end":[0.49479,-0.1405,0.02499],"object_pos_start":[0.49479,-0.1405,0.02499],"object_to_goal_dist_end":0.01083,"object_to_goal_dist_start":0.01083,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_to_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1212.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4982,-0.01937,0.29573],"tcp_start":[0.49876,-0.14737,0.30527],"tcp_to_object_dist_end":0.29662,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91753,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_z_offset":0.12007,"approach_behind.behind_distance":0.01956,"descend_to_contact.behind_distance":0.03994,"push_to_goal.push_duration":7.27943,"push_to_goal.push_extension":0.12969,"push_to_goal.push_speed":0.07955},"optimized_scores":{"best_composite_score":0.18805,"best_fitness_score":0.57805,"best_task_score":0.68035},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1470.0,"contact_point_centroid":[0.53713,0.03763,-5e-05],"force_p95":18.41294,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":217.36261,"mean_force":5.31343,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.53572,0.06162,0.09423]},{"body_a":"attachment","body_b":"push_box","contact_count":56.0,"contact_point_centroid":[0.54887,0.06318,0.04768],"force_p95":185.84211,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":215.98779,"mean_force":131.58013,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54139,0.07173,0.04788]},{"body_a":"attachment","body_b":"push_box","contact_count":795.0,"contact_point_centroid":[0.52504,-0.00146,0.02797],"force_p95":13.60642,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.20566,"mean_force":4.35716,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5262,0.01041,0.02763]},{"body_a":"world","body_b":"push_box","contact_count":1985.0,"contact_point_centroid":[0.52083,-0.02799,-6e-05],"force_p95":5.52468,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.59207,"mean_force":2.0363,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52693,0.01352,0.02788]},{"body_a":"world","body_b":"push_box","contact_count":3262.0,"contact_point_centroid":[0.50405,-0.09122,-3e-05],"force_p95":0.41121,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.61503,"mean_force":0.26916,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50405,-0.10275,0.17672]},{"body_a":"attachment","body_b":"push_box","contact_count":49.0,"contact_point_centroid":[0.50881,-0.06996,0.04156],"force_p95":2.00435,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.57955,"mean_force":0.88446,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.51065,-0.05814,0.04115]},{"body_a":"world","body_b":"push_box","contact_count":2192.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.51603,0.02538,0.22526]},{"body_a":"world","body_b":"push_box","contact_count":1192.0,"contact_point_centroid":[0.50437,-0.08926,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_to_home","phase_type":"retract","tcp_position_centroid":[0.49809,-0.08309,0.29924]}],"total_contact_groups":8},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50437,-0.08926,0.02499],"final_tcp_position":[0.49823,-0.0192,0.29581],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":217.36261,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":548.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2192.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.53418,0.05162,0.15128],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12716,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":406.0,"n_steps_budget":810.0,"object_pos_end":[0.53595,0.03292,0.02575],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18642,"object_to_goal_dist_start":0.1905,"object_z_max":0.02676,"peak_contact_force":0.71467,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1526.0,"raw_peak_contact_force":217.36261,"subtask_id":"reach_pre_contact","tcp_end":[0.54257,0.07453,0.03444],"tcp_start":[0.53418,0.05162,0.15128],"tcp_to_object_dist_end":0.04302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50666,-0.08851,0.02498],"object_pos_start":[0.53595,0.03292,0.02575],"object_to_goal_dist_end":0.06185,"object_to_goal_dist_start":0.18642,"object_z_max":0.02575,"peak_contact_force":0.96858,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2780.0,"raw_peak_contact_force":18.20566,"subtask_id":"push_to_goal","tcp_end":[0.51406,-0.05224,0.0259],"tcp_start":[0.54257,0.07453,0.03444],"tcp_to_object_dist_end":0.03703,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":895.0,"n_steps_budget":1000.0,"object_pos_end":[0.50437,-0.08926,0.02499],"object_pos_start":[0.50666,-0.08851,0.02498],"object_to_goal_dist_end":0.06089,"object_to_goal_dist_start":0.06185,"object_z_max":0.02954,"peak_contact_force":0.24525,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3311.0,"raw_peak_contact_force":2.61503,"tcp_end":[0.49899,-0.14505,0.30583],"tcp_start":[0.51406,-0.05224,0.0259],"tcp_to_object_dist_end":0.28637,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":298.0,"n_steps_budget":930.0,"object_pos_end":[0.50437,-0.08926,0.02499],"object_pos_start":[0.50437,-0.08926,0.02499],"object_to_goal_dist_end":0.06089,"object_to_goal_dist_start":0.06089,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_to_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49823,-0.0192,0.29581],"tcp_start":[0.49899,-0.14505,0.30583],"tcp_to_object_dist_end":0.27981,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```