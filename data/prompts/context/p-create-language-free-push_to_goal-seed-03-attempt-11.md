## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → push → lift → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 7 | 0.2652 | 0.85 | ✅ accepted |
| 10 | approach → descend → push → lift → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 7 | 0.3345 | 0.81 | ✅ accepted |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.3836 | 0.81 | ✅ accepted |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.3557 | 0.64 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.3690 | 0.48 | ❌ rejected |

**Proposal policy**: task_score is 0.85 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.265) — your mutation base

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

- **Composite score**: 0.265
- **task_score** (E): 0.846
- **fitness_score**: 0.705  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1725 |
| descend_to_contact | 0.00 | 1.00 | 0.1187 |
| push_to_goal | 1.00 | 1.00 | 0.1590 |
| lift_off | 1.00 | 1.00 | 0.2886 |
| retract_to_home | 1.00 | 1.00 | 0.1283 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.512, 0.040, 0.144) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | descend | 0.00 / step_budget | (0.512, 0.040, 0.144)→(0.511, 0.051, 0.027) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 1.00 / time_limit | (0.511, 0.051, 0.027)→(0.501, -0.099, 0.022) | (0.513, 0.002, 0.025)→(0.518, -0.129, 0.028) | 0.160→0.030 | 1.00 / 3.000 | 10.506 | 34.882 |
| lift_off | lift | 1.00 / step_budget | (0.501, -0.099, 0.022)→(0.498, -0.147, 0.305) | (0.518, -0.129, 0.028)→(0.515, -0.129, 0.025) | 0.030→0.027 | 1.00 / 4.000 | 0.245 | 14.606 |
| retract_to_home | retract | 1.00 / step_budget | (0.498, -0.147, 0.305)→(0.498, -0.019, 0.296) | (0.515, -0.129, 0.025)→(0.515, -0.129, 0.025) | 0.027→0.027 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.929
- goal_progress: 0.926
- terminal_score: 0.926
- phase_score: 0.655
- phase_breakdown.push_to_goal_score: 0.890
- phase_breakdown.reach_pre_contact_score: 0.107

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.764
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.926
- **Median Q (composite search score)**: 0.316
- **K-run variance**: 0.0059
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.380


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92188,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_z_offset":0.12123,"approach_behind.behind_distance":0.039,"descend_to_contact.behind_distance":0.057,"descend_to_contact.contact_force_threshold":11.3302,"push_to_goal.push_duration":3.58979,"push_to_goal.push_extension":0.17019,"push_to_goal.push_speed":0.09555},"optimized_scores":{"best_composite_score":0.32356,"best_fitness_score":0.76356,"best_task_score":0.9262},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1600.0,"contact_point_centroid":[0.4779,-0.08195,-4e-05],"force_p95":12.09871,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.34905,"mean_force":3.27916,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.44611,-0.03539,0.02477]},{"body_a":"push_box","body_b":"link7","contact_count":77.0,"contact_point_centroid":[0.51649,-0.11313,0.05597],"force_p95":15.88131,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.99837,"mean_force":8.84491,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48016,-0.11528,0.02282]},{"body_a":"attachment","body_b":"push_box","contact_count":648.0,"contact_point_centroid":[0.46647,-0.07184,0.04771],"force_p95":17.68008,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.36726,"mean_force":6.00032,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45686,-0.0611,0.02394]},{"body_a":"world","body_b":"push_box","contact_count":3258.0,"contact_point_centroid":[0.51074,-0.14892,-2e-05],"force_p95":0.37742,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7083,"mean_force":0.26171,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.48931,-0.13607,0.17284]},{"body_a":"attachment","body_b":"push_box","contact_count":36.0,"contact_point_centroid":[0.4965,-0.12972,0.05436],"force_p95":1.15286,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.32222,"mean_force":0.8093,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.48205,-0.12401,0.03831]},{"body_a":"world","body_b":"push_box","contact_count":1908.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.46904,0.00192,0.2281]},{"body_a":"world","body_b":"push_box","contact_count":2740.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4305,0.01184,0.0909]},{"body_a":"world","body_b":"push_box","contact_count":1220.0,"contact_point_centroid":[0.50931,-0.14819,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_to_home","phase_type":"retract","tcp_position_centroid":[0.49729,-0.08466,0.29893]}],"total_contact_groups":8},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50931,-0.14819,0.02499],"final_tcp_position":[0.49804,-0.01939,0.29574],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":54.34905,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":477.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1908.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.43805,0.00397,0.1555],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":685.0,"n_steps_budget":840.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2740.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.42528,0.01983,0.02876],"tcp_start":[0.43805,0.00397,0.1555],"tcp_to_object_dist_end":0.05729,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51329,-0.14803,0.02928],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.0141,"object_to_goal_dist_start":0.12843,"object_z_max":0.02928,"peak_contact_force":4.99632,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2325.0,"raw_peak_contact_force":54.34905,"subtask_id":"push_to_goal","tcp_end":[0.48343,-0.12265,0.02277],"tcp_start":[0.42528,0.01983,0.02876],"tcp_to_object_dist_end":0.03972,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":872.0,"n_steps_budget":1000.0,"object_pos_end":[0.50931,-0.14819,0.02499],"object_pos_start":[0.51329,-0.14803,0.02928],"object_to_goal_dist_end":0.00948,"object_to_goal_dist_start":0.0141,"object_z_max":0.02928,"peak_contact_force":0.24525,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3294.0,"raw_peak_contact_force":1.7083,"tcp_end":[0.49756,-0.14826,0.30533],"tcp_start":[0.48343,-0.12265,0.02277],"tcp_to_object_dist_end":0.28059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":305.0,"n_steps_budget":930.0,"object_pos_end":[0.50931,-0.14819,0.02499],"object_pos_start":[0.50931,-0.14819,0.02499],"object_to_goal_dist_end":0.00948,"object_to_goal_dist_start":0.00948,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_to_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1220.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49804,-0.01939,0.29574],"tcp_start":[0.49756,-0.14826,0.30533],"tcp_to_object_dist_end":0.30004,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92228,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_z_offset":0.11108,"approach_behind.behind_distance":0.04665,"descend_to_contact.behind_distance":0.05954,"descend_to_contact.contact_force_threshold":9.85731,"push_to_goal.push_duration":5.72135,"push_to_goal.push_extension":0.08442,"push_to_goal.push_speed":0.09998},"optimized_scores":{"best_composite_score":0.31558,"best_fitness_score":0.75558,"best_task_score":0.90471},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":724.0,"contact_point_centroid":[0.53338,-0.04059,0.02026],"force_p95":14.12243,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.25849,"mean_force":3.90526,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53491,-0.02876,0.01989]},{"body_a":"world","body_b":"push_box","contact_count":2078.0,"contact_point_centroid":[0.5335,-0.05283,-4e-05],"force_p95":5.57543,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.70925,"mean_force":1.63339,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54121,-0.01096,0.02024]},{"body_a":"attachment","body_b":"push_box","contact_count":46.0,"contact_point_centroid":[0.5063,-0.11257,0.03815],"force_p95":2.27218,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.4997,"mean_force":0.98478,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.5083,-0.10079,0.03768]},{"body_a":"world","body_b":"push_box","contact_count":3288.0,"contact_point_centroid":[0.50272,-0.1366,-2e-05],"force_p95":0.38766,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.37302,"mean_force":0.26435,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50308,-0.12392,0.17182]},{"body_a":"world","body_b":"push_box","contact_count":2464.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5293,0.02083,0.21968]},{"body_a":"world","body_b":"push_box","contact_count":2592.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.56294,0.04916,0.0794]},{"body_a":"world","body_b":"push_box","contact_count":1212.0,"contact_point_centroid":[0.50288,-0.13499,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_to_home","phase_type":"retract","tcp_position_centroid":[0.49805,-0.08401,0.2989]}],"total_contact_groups":7},"final_pose_error":0.01963,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50288,-0.13499,0.02499],"final_tcp_position":[0.49822,-0.01908,0.29572],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":21.25849,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2464.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.56078,0.04207,0.14104],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12322,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":648.0,"n_steps_budget":750.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2592.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.56768,0.05615,0.02529],"tcp_start":[0.56078,0.04207,0.14104],"tcp_to_object_dist_end":0.05668,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50478,-0.1337,0.02507],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.01698,"object_to_goal_dist_start":0.16043,"object_z_max":0.02526,"peak_contact_force":0.00028,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2802.0,"raw_peak_contact_force":21.25849,"subtask_id":"push_to_goal","tcp_end":[0.51189,-0.09741,0.02006],"tcp_start":[0.56768,0.05615,0.02529],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":890.0,"n_steps_budget":1000.0,"object_pos_end":[0.50288,-0.13499,0.02499],"object_pos_start":[0.50478,-0.1337,0.02507],"object_to_goal_dist_end":0.01529,"object_to_goal_dist_start":0.01698,"object_z_max":0.02739,"peak_contact_force":0.24525,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3334.0,"raw_peak_contact_force":2.4997,"tcp_end":[0.4989,-0.14709,0.30528],"tcp_start":[0.51189,-0.09741,0.02006],"tcp_to_object_dist_end":0.28058,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":303.0,"n_steps_budget":930.0,"object_pos_end":[0.50288,-0.13499,0.02499],"object_pos_start":[0.50288,-0.13499,0.02499],"object_to_goal_dist_end":0.01529,"object_to_goal_dist_start":0.01529,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_to_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1212.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49822,-0.01908,0.29572],"tcp_start":[0.4989,-0.14709,0.30528],"tcp_to_object_dist_end":0.29454,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92308,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_z_offset":0.10647,"approach_behind.behind_distance":0.04294,"descend_to_contact.behind_distance":0.04309,"descend_to_contact.contact_force_threshold":15.98455,"push_to_goal.push_duration":4.45993,"push_to_goal.push_extension":0.15611,"push_to_goal.push_speed":0.09894},"optimized_scores":{"best_composite_score":0.15646,"best_fitness_score":0.59646,"best_task_score":0.7057},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.54646,-0.08164,0.05489],"force_p95":30.93947,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.60968,"mean_force":7.72068,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50806,-0.07847,0.02215]},{"body_a":"world","body_b":"push_box","contact_count":3306.0,"contact_point_centroid":[0.53332,-0.10501,-2e-05],"force_p95":0.38848,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.0746,"mean_force":0.28245,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50137,-0.11465,0.17288]},{"body_a":"push_box","body_b":"link7","contact_count":154.0,"contact_point_centroid":[0.54794,-0.06993,0.0544],"force_p95":25.51379,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.03837,"mean_force":18.14178,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51021,-0.06541,0.02152]},{"body_a":"world","body_b":"push_box","contact_count":1540.0,"contact_point_centroid":[0.53785,-0.04241,-5e-05],"force_p95":17.14402,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.32162,"mean_force":4.79213,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52321,0.00608,0.02144]},{"body_a":"attachment","body_b":"push_box","contact_count":849.0,"contact_point_centroid":[0.52778,-0.01211,0.03728],"force_p95":16.21747,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.54994,"mean_force":4.98187,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52167,-0.00084,0.02111]},{"body_a":"attachment","body_b":"push_box","contact_count":46.0,"contact_point_centroid":[0.51951,-0.08958,0.05556],"force_p95":1.2797,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.76897,"mean_force":1.16575,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50555,-0.0822,0.03668]},{"body_a":"world","body_b":"push_box","contact_count":2536.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.5183,0.03633,0.21772]},{"body_a":"world","body_b":"push_box","contact_count":2296.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.53807,0.07571,0.07866]},{"body_a":"world","body_b":"push_box","contact_count":1200.0,"contact_point_centroid":[0.53185,-0.10386,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_to_home","phase_type":"retract","tcp_position_centroid":[0.49795,-0.08373,0.29915]}],"total_contact_groups":9},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53185,-0.10386,0.02499],"final_tcp_position":[0.4982,-0.01939,0.29579],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":39.60968,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":634.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2536.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.53865,0.07348,0.13692],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11776,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":574.0,"n_steps_budget":720.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2296.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.54014,0.07821,0.0261],"tcp_start":[0.53865,0.07348,0.13692],"tcp_to_object_dist_end":0.04143,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53568,-0.10497,0.02864],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.05756,"object_to_goal_dist_start":0.1905,"object_z_max":0.02866,"peak_contact_force":26.52068,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2543.0,"raw_peak_contact_force":29.03837,"subtask_id":"push_to_goal","tcp_end":[0.50837,-0.07821,0.02206],"tcp_start":[0.54014,0.07821,0.0261],"tcp_to_object_dist_end":0.0388,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":892.0,"n_steps_budget":1000.0,"object_pos_end":[0.53185,-0.10386,0.02499],"object_pos_start":[0.53568,-0.10497,0.02864],"object_to_goal_dist_end":0.05606,"object_to_goal_dist_start":0.05756,"object_z_max":0.02865,"peak_contact_force":0.24525,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":3359.0,"raw_peak_contact_force":39.60968,"tcp_end":[0.49873,-0.14626,0.30568],"tcp_start":[0.50837,-0.07821,0.02206],"tcp_to_object_dist_end":0.2858,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":300.0,"n_steps_budget":930.0,"object_pos_end":[0.53185,-0.10386,0.02499],"object_pos_start":[0.53185,-0.10386,0.02499],"object_to_goal_dist_end":0.05606,"object_to_goal_dist_start":0.05606,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_to_home","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1200.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4982,-0.01939,0.29579],"tcp_start":[0.49873,-0.14626,0.30568],"tcp_to_object_dist_end":0.28566,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```