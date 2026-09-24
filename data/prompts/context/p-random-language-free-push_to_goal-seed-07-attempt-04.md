## Search State

- **Seed**: 7
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.2807 | 0.72 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.6105 | 0.67 | ❌ rejected |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.5949 | 0.68 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.1381 | 0.00 | ✅ accepted |
| 0 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.3400 | 0.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
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
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.724, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.51501145599256, 0.047665656116349056, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.281) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  weight: 0.3
- id: push_goal
  target_entity: object
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_object
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
    - 0.0
    offset_along_axis:
      distance: 0.1
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    orientation:
      mode: keep_current
  parameters:
    approach_distance:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: contact_object
  type: contact
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
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 3.0
      - 15.0
      default: 8.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  guards:
  - id: contact_made
    when: after_phase
    predicate: contact_detected
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: reach_object
- id: push_stage1
  type: push
  generator: linear_cartesian
  control: admittance_control
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
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push1_distance:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push1_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: push_goal
- id: push_stage2
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
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
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push2_distance:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.08
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push2_speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: push_goal
- id: retract_after_push
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
    - 0.1
    orientation:
      mode: keep_current
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.1, mode=add_to_offset, sign=negative}
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **contact_object** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - guards:
    - id=contact_made, when=after_phase, predicate=contact_detected, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=reduce_speed
- **push_stage1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push1_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push1_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_stage2** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.08, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push2_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push2_speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_after_push** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.281
- **task_score** (E): 0.724
- **fitness_score**: 0.521  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.33 | 1.00 | 0.2702 |
| contact_object | 1.00 | 1.00 | 0.0615 |
| push_stage1 | 1.00 | 1.00 | 0.1267 |
| push_stage2 | 1.00 | 1.00 | 0.1012 |
| retract_after_push | 1.00 | 1.00 | 0.0894 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.33 / step_budget | (0.500, -0.000, 0.301)→(0.518, 0.117, 0.064) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_object | contact | 1.00 / force_exceeded | (0.518, 0.117, 0.064)→(0.511, 0.064, 0.036) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 38.346 | 0.245 |
| push_stage1 | push | 1.00 / step_budget | (0.511, 0.064, 0.036)→(0.487, -0.059, 0.032) | (0.513, 0.027, 0.025)→(0.517, -0.074, 0.028) | 0.180→0.087 | 1.00 / 1.667 | 1.402 | 27.222 |
| push_stage2 | push | 1.00 / step_budget | (0.487, -0.059, 0.032)→(0.446, -0.124, 0.021) | (0.517, -0.074, 0.028)→(0.514, -0.102, 0.027) | 0.087→0.054 | 1.00 / 2.667 | 0.443 | 26.031 |
| retract_after_push | retract | 1.00 / step_budget | (0.446, -0.124, 0.021)→(0.443, -0.123, 0.111) | (0.514, -0.102, 0.027)→(0.512, -0.103, 0.025) | 0.054→0.052 | 1.00 / 4.000 | 0.245 | 0.842 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.724
- lateral_force_integral: None
- approach_alignment: 0.759
- goal_progress: 0.717
- terminal_score: 0.717
- phase_score: 0.465
- phase_breakdown.push_goal_score: 0.474
- phase_breakdown.reach_object_score: 0.443

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.566
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.855
- **Median Q (composite search score)**: 0.308
- **K-run variance**: 0.0027
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.281


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56571,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_distance":0.13745,"approach_object.approach_speed":0.06974,"contact_object.contact_force_threshold":10.89435,"push_stage1.push1_distance":0.10423,"push_stage1.push1_speed":0.15646,"push_stage2.push2_distance":0.0975,"push_stage2.push2_speed":0.05786},"optimized_scores":{"best_composite_score":0.20848,"best_fitness_score":0.44848,"best_task_score":0.60186},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":346.0,"contact_point_centroid":[0.50947,0.02477,0.04543],"force_p95":22.48783,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.93537,"mean_force":6.65521,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.50459,0.03629,0.03395]},{"body_a":"attachment","body_b":"push_box","contact_count":378.0,"contact_point_centroid":[0.50268,-0.06105,0.05432],"force_p95":11.46618,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.26399,"mean_force":3.26048,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.48612,-0.05619,0.02836]},{"body_a":"world","body_b":"push_box","contact_count":621.0,"contact_point_centroid":[0.52288,-0.01133,-7e-05],"force_p95":12.69874,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.54249,"mean_force":4.20475,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.5049,0.03887,0.03409]},{"body_a":"world","body_b":"push_box","contact_count":767.0,"contact_point_centroid":[0.54382,-0.06497,-4e-05],"force_p95":8.16675,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.18519,"mean_force":2.14568,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.48644,-0.0551,0.02845]},{"body_a":"attachment","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.49135,-0.09506,0.05166],"force_p95":1.10488,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.2687,"mean_force":0.75781,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.47409,-0.09736,0.03036]},{"body_a":"world","body_b":"push_box","contact_count":2064.0,"contact_point_centroid":[0.51119,-0.07139,-1e-05],"force_p95":0.35391,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97398,"mean_force":0.25842,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.47258,-0.09677,0.07306]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50746,0.07401,0.18474]},{"body_a":"world","body_b":"push_box","contact_count":1764.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.51276,0.1165,0.05396]}],"total_contact_groups":8},"final_pose_error":0.01157,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51043,-0.07177,0.02499],"final_tcp_position":[0.4727,-0.09674,0.11593],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":32.97043,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.51683,0.1477,0.07337],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11113,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":441.0,"n_steps_budget":720.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":32.97043,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1764.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.51168,0.08454,0.03809],"tcp_start":[0.51683,0.1477,0.07337],"tcp_to_object_dist_end":0.03928,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":474.0,"n_steps_budget":600.0,"object_pos_end":[0.52667,-0.03828,0.02758],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.11489,"object_to_goal_dist_start":0.19823,"object_z_max":0.02753,"peak_contact_force":0.0,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":967.0,"raw_peak_contact_force":25.93537,"subtask_id":"push_goal","tcp_end":[0.50055,-0.01114,0.03352],"tcp_start":[0.51168,0.08454,0.03809],"tcp_to_object_dist_end":0.03813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.51284,-0.07056,0.02758],"object_pos_start":[0.52667,-0.03828,0.02758],"object_to_goal_dist_end":0.08051,"object_to_goal_dist_start":0.11489,"object_z_max":0.0297,"peak_contact_force":0.0,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1145.0,"raw_peak_contact_force":19.26399,"subtask_id":"push_goal","tcp_end":[0.47592,-0.09729,0.02703],"tcp_start":[0.50055,-0.01114,0.03352],"tcp_to_object_dist_end":0.04559,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.51043,-0.07177,0.02499],"object_pos_start":[0.51284,-0.07056,0.02758],"object_to_goal_dist_end":0.07893,"object_to_goal_dist_start":0.08051,"object_z_max":0.02758,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2085.0,"raw_peak_contact_force":1.2687,"tcp_end":[0.4727,-0.09674,0.11593],"tcp_start":[0.47592,-0.09729,0.02703],"tcp_to_object_dist_end":0.10158,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.375,"average_solve_count":192.0,"average_success_count":192.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_distance":0.1084,"approach_object.approach_speed":0.05235,"contact_object.contact_force_threshold":14.15878,"push_stage1.push1_distance":0.10476,"push_stage1.push1_speed":0.13646,"push_stage2.push2_distance":0.12293,"push_stage2.push2_speed":0.07821},"optimized_scores":{"best_composite_score":0.32554,"best_fitness_score":0.56554,"best_task_score":0.71668},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":331.0,"contact_point_centroid":[0.47777,0.03411,0.04602],"force_p95":21.24118,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.18766,"mean_force":6.5047,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.47302,0.04564,0.03679]},{"body_a":"attachment","body_b":"push_box","contact_count":483.0,"contact_point_centroid":[0.48958,-0.06639,0.04951],"force_p95":14.41805,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.06391,"mean_force":3.86908,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.47542,-0.06084,0.03134]},{"body_a":"world","body_b":"push_box","contact_count":546.0,"contact_point_centroid":[0.49251,-0.0078,-5e-05],"force_p95":11.94446,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.02772,"mean_force":4.50284,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.47295,0.04741,0.03691]},{"body_a":"world","body_b":"push_box","contact_count":931.0,"contact_point_centroid":[0.52904,-0.0764,-5e-05],"force_p95":9.40041,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.05555,"mean_force":2.57935,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.47553,-0.06338,0.03133]},{"body_a":"attachment","body_b":"push_box","contact_count":77.0,"contact_point_centroid":[0.4895,-0.1136,0.05457],"force_p95":0.89062,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.0114,"mean_force":0.61166,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.47403,-0.11561,0.04084]},{"body_a":"world","body_b":"push_box","contact_count":1867.0,"contact_point_centroid":[0.50958,-0.09014,-2e-05],"force_p95":0.51593,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.97592,"mean_force":0.28289,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.47335,-0.11534,0.07912]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48418,0.06874,0.18167]},{"body_a":"world","body_b":"push_box","contact_count":1240.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.46948,0.11674,0.05234]}],"total_contact_groups":8},"final_pose_error":0.01165,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50566,-0.09091,0.02499],"final_tcp_position":[0.47348,-0.11533,0.11884],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":34.85742,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47033,0.13751,0.06673],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08982,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":310.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":34.85742,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.47131,0.09532,0.04049],"tcp_start":[0.47033,0.13751,0.06673],"tcp_to_object_dist_end":0.04075,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":485.0,"n_steps_budget":600.0,"object_pos_end":[0.49668,-0.03242,0.02683],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.11764,"object_to_goal_dist_start":0.2095,"object_z_max":0.02696,"peak_contact_force":2.56227,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":877.0,"raw_peak_contact_force":27.18766,"subtask_id":"push_goal","tcp_end":[0.47728,-0.00099,0.03634],"tcp_start":[0.47131,0.09532,0.04049],"tcp_to_object_dist_end":0.03814,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":639.0,"n_steps_budget":990.0,"object_pos_end":[0.51137,-0.08937,0.02956],"object_pos_start":[0.49668,-0.03242,0.02683],"object_to_goal_dist_end":0.06185,"object_to_goal_dist_start":0.11764,"object_z_max":0.03005,"peak_contact_force":1.08414,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1414.0,"raw_peak_contact_force":26.06391,"subtask_id":"push_goal","tcp_end":[0.47668,-0.11599,0.03002],"tcp_start":[0.47728,-0.00099,0.03634],"tcp_to_object_dist_end":0.04372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.50566,-0.09091,0.02499],"object_pos_start":[0.51137,-0.08937,0.02956],"object_to_goal_dist_end":0.05936,"object_to_goal_dist_start":0.06185,"object_z_max":0.02956,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1944.0,"raw_peak_contact_force":1.0114,"tcp_end":[0.47348,-0.11533,0.11884],"tcp_start":[0.47668,-0.11599,0.03002],"tcp_to_object_dist_end":0.10217,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37186,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_distance":0.10868,"approach_object.approach_speed":0.04061,"contact_object.contact_force_threshold":8.11938,"push_stage1.push1_distance":0.1952,"push_stage1.push1_speed":0.12742,"push_stage2.push2_distance":0.10796,"push_stage2.push2_speed":0.16765},"optimized_scores":{"best_composite_score":0.30796,"best_fitness_score":0.54796,"best_task_score":0.85474},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.51436,-0.14972,-0.00019],"force_p95":15.85271,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.76385,"mean_force":1.78209,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.42993,-0.16055,0.01392]},{"body_a":"push_box","body_b":"link7","contact_count":71.0,"contact_point_centroid":[0.48523,-0.16537,0.04869],"force_p95":29.95979,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.80655,"mean_force":15.26821,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.44638,-0.16122,0.01646]},{"body_a":"attachment","body_b":"push_box","contact_count":709.0,"contact_point_centroid":[0.52239,-0.08465,0.04214],"force_p95":19.84968,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.54235,"mean_force":4.4887,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.51454,-0.07439,0.02552]},{"body_a":"world","body_b":"push_box","contact_count":1279.0,"contact_point_centroid":[0.54186,-0.11386,-5e-05],"force_p95":9.22461,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.04578,"mean_force":2.95606,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.51395,-0.07613,0.02556]},{"body_a":"attachment","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.49622,-0.16615,0.0541],"force_p95":8.6074,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.69529,"mean_force":2.0784,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.47727,-0.16324,0.02344]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.53251,0.03337,0.17481]},{"body_a":"world","body_b":"push_box","contact_count":1480.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.55664,0.03969,0.03912]},{"body_a":"world","body_b":"push_box","contact_count":2180.0,"contact_point_centroid":[0.5188,-0.14617,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24524,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.38306,-0.15759,0.05148]}],"total_contact_groups":8},"final_pose_error":0.01022,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5188,-0.14617,0.02499],"final_tcp_position":[0.38309,-0.15756,0.0968],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":47.2109,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.5671,0.06694,0.05227],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":370.0,"n_steps_budget":630.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":47.2109,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1480.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.54919,0.01139,0.03023],"tcp_start":[0.5671,0.06694,0.05227],"tcp_to_object_dist_end":0.03764,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":881.0,"n_steps_budget":960.0,"object_pos_end":[0.52661,-0.15113,0.02934],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.02698,"object_to_goal_dist_start":0.13211,"object_z_max":0.02948,"peak_contact_force":1.64249,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1988.0,"raw_peak_contact_force":28.54235,"subtask_id":"push_goal","tcp_end":[0.48245,-0.16341,0.02539],"tcp_start":[0.54919,0.01139,0.03023],"tcp_to_object_dist_end":0.046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":321.0,"n_steps_budget":600.0,"object_pos_end":[0.51881,-0.14617,0.02497],"object_pos_start":[0.52661,-0.15113,0.02934],"object_to_goal_dist_end":0.01919,"object_to_goal_dist_start":0.02698,"object_z_max":0.03321,"peak_contact_force":0.24486,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":880.0,"raw_peak_contact_force":32.76385,"subtask_id":"push_goal","tcp_end":[0.38584,-0.1585,0.0066],"tcp_start":[0.48245,-0.16341,0.02539],"tcp_to_object_dist_end":0.1348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.5188,-0.14617,0.02499],"object_pos_start":[0.51881,-0.14617,0.02497],"object_to_goal_dist_end":0.01919,"object_to_goal_dist_start":0.01919,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.38309,-0.15756,0.0968],"tcp_start":[0.38584,-0.1585,0.0066],"tcp_to_object_dist_end":0.15396,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```