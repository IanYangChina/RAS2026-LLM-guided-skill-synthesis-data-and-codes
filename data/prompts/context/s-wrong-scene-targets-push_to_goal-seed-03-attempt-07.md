## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.3234 | 0.57 | ❌ rejected |
| 6 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | 0.7347 | 0.94 | ✅ accepted |
| 5 | approach → descend → push → push → lift → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | 0.5258 | 0.91 | ✅ accepted |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | 0.8237 | 0.88 | ✅ accepted |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.7916 | 0.86 | ❌ rejected |

**Proposal policy**: task_score is 0.57 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.945, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.323) — your mutation base

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
      distance: -0.12
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_offset:
      type: scalar
      range:
      - -0.25
      - -0.05
      default: -0.12
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
    tolerance: 0.02
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
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=-0.12, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **push_2** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=-0.01, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_fine_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_fine_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.323
- **task_score** (E): 0.571
- **fitness_score**: 0.667  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 1.00 | 0.1286 |
| descend_1 | 0.67 | 1.00 | 0.1862 |
| push_1 | 1.00 | 1.00 | 0.0623 |
| push_2 | 1.00 | 1.00 | 0.1933 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.527, 0.093, 0.234) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 0.67 / force_exceeded | (0.527, 0.093, 0.234)→(0.512, 0.022, 0.065) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.667 | 50595.773 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.512, 0.022, 0.065)→(0.516, 0.070, 0.040) | (0.513, 0.002, 0.025)→(0.519, 0.015, 0.029) | 0.160→0.173 | 1.00 / 3.333 | 127.255 | 152.326 |
| push_2 | push | 1.00 / step_budget | (0.516, 0.070, 0.040)→(0.501, -0.112, 0.023) | (0.519, 0.015, 0.029)→(0.519, -0.078, 0.025) | 0.173→0.075 | 1.00 / 2.333 | 0.260 | 131.889 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.664
- goal_progress: 0.978
- terminal_score: 0.978
- phase_score: 0.985
- phase_breakdown.push_to_goal_score: 0.978
- phase_breakdown.contact_object_score: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.982
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.978
- **Median Q (composite search score)**: 0.296
- **K-run variance**: 0.0125
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.296


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.10791,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15519,"approach_1.approach_standoff":0.22133,"approach_1.approach_tolerance":0.15358,"descend_1.descend_force_threshold":7.28041,"descend_1.descend_lateral_offset":0.03522,"push_1.push_offset":-0.24682,"push_1.push_speed":0.26381,"push_2.push_fine_offset":-0.01979,"push_2.push_fine_speed":0.1543},"optimized_scores":{"best_composite_score":0.47216,"best_fitness_score":0.98216,"best_task_score":0.97824},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":180.0,"contact_point_centroid":[0.46437,-0.07135,0.0425],"force_p95":36.73278,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.25133,"mean_force":6.80896,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.459,-0.05948,0.02465]},{"body_a":"world","body_b":"push_box","contact_count":879.0,"contact_point_centroid":[0.45845,-0.05527,-3e-05],"force_p95":10.27656,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.74,"mean_force":1.78372,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.4317,0.00626,0.029]},{"body_a":"world","body_b":"push_box","contact_count":216.0,"contact_point_centroid":[0.45028,-0.03158,-0.0],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48363,0.02418,0.28276]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24526,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.44931,0.03967,0.16953]},{"body_a":"world","body_b":"push_box","contact_count":740.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.42948,0.02985,0.06242]}],"total_contact_groups":5},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50261,-0.14989,0.02598],"final_tcp_position":[0.48232,-0.11517,0.02123],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":64.25133,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24526,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":216.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.4538,0.07434,0.24885],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.24768,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24526,"subtask_id":"contact_object","tcp_end":[0.4481,0.00083,0.08981],"tcp_start":[0.4538,0.07434,0.24885],"tcp_to_object_dist_end":0.07251,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":185.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":740.0,"raw_peak_contact_force":0.24525,"subtask_id":"push_to_goal","tcp_end":[0.4106,0.06174,0.03479],"tcp_start":[0.4481,0.00083,0.08981],"tcp_to_object_dist_end":0.10188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":466.0,"n_steps_budget":870.0,"object_pos_end":[0.50261,-0.14989,0.02598],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.00279,"object_to_goal_dist_start":0.12843,"object_z_max":0.0265,"peak_contact_force":0.0,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1059.0,"raw_peak_contact_force":64.25133,"subtask_id":"push_to_goal","tcp_end":[0.48232,-0.11517,0.02123],"tcp_start":[0.4106,0.06174,0.03479],"tcp_to_object_dist_end":0.04049,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80745,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10359,"approach_1.approach_standoff":0.24707,"approach_1.approach_tolerance":0.16149,"descend_1.descend_force_threshold":5.99309,"descend_1.descend_lateral_offset":0.02463,"push_1.push_offset":-0.2241,"push_1.push_speed":0.3643,"push_2.push_fine_offset":-0.02492,"push_2.push_fine_speed":0.11643},"optimized_scores":{"best_composite_score":0.29634,"best_fitness_score":0.55634,"best_task_score":0.4263},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":150.0,"contact_point_centroid":[0.57275,0.02463,-0.00111],"force_p95":213.44653,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":228.52069,"mean_force":135.8992,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56581,0.03557,0.04717]},{"body_a":"attachment","body_b":"push_box","contact_count":114.0,"contact_point_centroid":[0.57186,0.02679,0.04747],"force_p95":214.06366,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":227.1222,"mean_force":177.68169,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56573,0.03514,0.04717]},{"body_a":"attachment","body_b":"push_box","contact_count":679.0,"contact_point_centroid":[0.57088,-0.01013,0.04642],"force_p95":165.0827,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":168.31047,"mean_force":145.95298,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.56223,-0.01316,0.04617]},{"body_a":"world","body_b":"push_box","contact_count":1741.0,"contact_point_centroid":[0.55511,-0.01325,-0.00058],"force_p95":146.36077,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.16054,"mean_force":57.57306,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.56092,-0.01481,0.04552]},{"body_a":"world","body_b":"push_box","contact_count":320.0,"contact_point_centroid":[0.55317,0.00136,-0.0],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53319,0.04487,0.26699]},{"body_a":"world","body_b":"push_box","contact_count":3788.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56953,0.07475,0.12893]}],"total_contact_groups":6},"final_pose_error":0.01959,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52475,-0.06136,0.02374],"final_tcp_position":[0.51505,-0.10814,0.02549],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":80.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":320.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.58682,0.12139,0.21194],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.2247,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":947.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3788.0,"raw_peak_contact_force":0.24525,"subtask_id":"contact_object","tcp_end":[0.55497,0.02242,0.05238],"tcp_start":[0.58682,0.12139,0.21194],"tcp_to_object_dist_end":0.0346,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":114.0,"n_steps_budget":600.0,"object_pos_end":[0.55952,0.02027,0.03117],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.18048,"object_to_goal_dist_start":0.16043,"object_z_max":0.03105,"peak_contact_force":181.35038,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":264.0,"raw_peak_contact_force":228.52069,"subtask_id":"push_to_goal","tcp_end":[0.57672,0.05243,0.0425],"tcp_start":[0.55497,0.02242,0.05238],"tcp_to_object_dist_end":0.03819,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":733.0,"n_steps_budget":1000.0,"object_pos_end":[0.52475,-0.06136,0.02374],"object_pos_start":[0.55952,0.02027,0.03117],"object_to_goal_dist_end":0.09204,"object_to_goal_dist_start":0.18048,"object_z_max":0.03524,"peak_contact_force":0.53403,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2420.0,"raw_peak_contact_force":168.31047,"subtask_id":"push_to_goal","tcp_end":[0.51505,-0.10814,0.02549],"tcp_start":[0.57672,0.05243,0.0425],"tcp_to_object_dist_end":0.04781,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85621,"average_solve_count":153.0,"average_success_count":153.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13477,"approach_1.approach_standoff":0.17023,"approach_1.approach_tolerance":0.09102,"descend_1.descend_force_threshold":3.98431,"descend_1.descend_lateral_offset":0.03786,"push_1.push_offset":-0.24951,"push_1.push_speed":0.18615,"push_2.push_fine_offset":-0.01795,"push_2.push_fine_speed":0.12629},"optimized_scores":{"best_composite_score":0.20181,"best_fitness_score":0.46181,"best_task_score":0.30893},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":269.0,"contact_point_centroid":[0.55865,0.06276,0.04584],"force_p95":223.57675,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":228.21078,"mean_force":200.30466,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54952,0.06913,0.04563]},{"body_a":"world","body_b":"push_box","contact_count":594.0,"contact_point_centroid":[0.54466,0.06187,-0.00083],"force_p95":215.25984,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":222.95069,"mean_force":91.51797,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54882,0.06789,0.04583]},{"body_a":"attachment","body_b":"push_box","contact_count":615.0,"contact_point_centroid":[0.5627,0.03363,0.04687],"force_p95":158.20327,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.1067,"mean_force":144.15367,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.554,0.03072,0.04651]},{"body_a":"world","body_b":"push_box","contact_count":2112.0,"contact_point_centroid":[0.54313,0.01523,-0.00048],"force_p95":124.15506,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":144.6978,"mean_force":42.49913,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.54525,0.00776,0.04187]},{"body_a":"world","body_b":"push_box","contact_count":236.0,"contact_point_centroid":[0.5366,0.03695,-0.0],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5138,0.0288,0.27938]},{"body_a":"world","body_b":"push_box","contact_count":3656.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24526,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53484,0.06505,0.14411]}],"total_contact_groups":6},"final_pose_error":0.01963,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5295,-0.0217,0.02498],"final_tcp_position":[0.50526,-0.11322,0.02203],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":59.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24526,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":236.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_object","tcp_end":[0.53978,0.08387,0.24075],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.22083,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":914.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3656.0,"raw_peak_contact_force":0.24526,"subtask_id":"contact_object","tcp_end":[0.53301,0.04363,0.05222],"tcp_start":[0.53978,0.08387,0.24075],"tcp_to_object_dist_end":0.02826,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":269.0,"n_steps_budget":600.0,"object_pos_end":[0.54773,0.0557,0.03003],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.21123,"object_to_goal_dist_start":0.1905,"object_z_max":0.02994,"peak_contact_force":200.1693,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":863.0,"raw_peak_contact_force":228.21078,"subtask_id":"push_to_goal","tcp_end":[0.55926,0.09474,0.04158],"tcp_start":[0.53301,0.04363,0.05222],"tcp_to_object_dist_end":0.04231,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":780.0,"n_steps_budget":1000.0,"object_pos_end":[0.5295,-0.0217,0.02498],"object_pos_start":[0.54773,0.0557,0.03003],"object_to_goal_dist_end":0.13165,"object_to_goal_dist_start":0.21123,"object_z_max":0.03571,"peak_contact_force":0.24515,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2727.0,"raw_peak_contact_force":163.1067,"subtask_id":"push_to_goal","tcp_end":[0.50526,-0.11322,0.02203],"tcp_start":[0.55926,0.09474,0.04158],"tcp_to_object_dist_end":0.09472,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```