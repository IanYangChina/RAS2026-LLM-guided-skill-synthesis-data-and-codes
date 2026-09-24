## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.3836 | 0.88 | ✅ accepted |
| 8 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3499 | 0.77 | ❌ rejected |
| 7 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | time_limit | force_exceeded | time_limit | time_limit | pose_tolerance | 10 | 0.2268 | 0.38 | ❌ rejected |
| 6 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3615 | 0.79 | ✅ accepted |
| 5 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | position_control | pose_tolerance | force_exceeded | time_limit | time_limit | pose_tolerance | 9 | 0.0456 | 0.39 | ❌ rejected |

**Proposal policy**: task_score is 0.88 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.885, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.384) — your mutation base

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
      distance: 0.2
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
      - 0.35
      default: 0.2
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
    push1_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
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
      distance: 0.12
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
      - 0.25
      default: 0.12
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
    push2_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.04
      default: 0.025
      binds_to:
      - path: termination.pose_tolerance
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
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push1_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push1_speed: status=consumed; consumers=generator.speed (replace)
    - push1_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_stage2** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.12, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push2_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push2_speed: status=consumed; consumers=generator.speed (replace)
    - push2_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **retract_after_push** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: 0.384
- **task_score** (E): 0.885
- **fitness_score**: 0.724  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.2781 |
| contact_object | 1.00 | 1.00 | 0.0314 |
| push_stage1 | 1.00 | 0.67 | 0.1142 |
| push_stage2 | 1.00 | 1.00 | 0.1526 |
| retract_after_push | 1.00 | 1.00 | 0.0892 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.517, 0.091, 0.043) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_object | contact | 1.00 / force_exceeded | (0.517, 0.091, 0.043)→(0.510, 0.064, 0.031) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 24.616 | 0.245 |
| push_stage1 | push | 1.00 / step_budget | (0.510, 0.064, 0.031)→(0.495, -0.047, 0.027) | (0.513, 0.027, 0.025)→(0.506, -0.083, 0.026) | 0.180→0.072 | 0.67 / 1.000 | 2.257 | 82.646 |
| push_stage2 | push | 1.00 / step_budget | (0.495, -0.047, 0.027)→(0.430, -0.154, 0.019) | (0.506, -0.083, 0.026)→(0.521, -0.143, 0.027) | 0.072→0.024 | 1.00 / 4.000 | 5.411 | 73.925 |
| retract_after_push | retract | 1.00 / step_budget | (0.430, -0.154, 0.019)→(0.427, -0.153, 0.108) | (0.521, -0.143, 0.027)→(0.519, -0.143, 0.025) | 0.024→0.022 | 1.00 / 4.000 | 0.245 | 0.736 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.839
- goal_progress: 0.958
- terminal_score: 0.958
- phase_score: 0.649
- phase_breakdown.push_goal_score: 0.724
- phase_breakdown.reach_object_score: 0.473

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.773
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.958
- **Median Q (composite search score)**: 0.405
- **K-run variance**: 0.0026
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4596,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_distance":0.07824,"approach_object.approach_speed":0.04531,"contact_object.contact_force_threshold":6.70995,"push_stage1.push1_distance":0.13727,"push_stage1.push1_speed":0.0852,"push_stage1.push1_tolerance":0.03471,"push_stage2.push2_distance":0.16909,"push_stage2.push2_speed":0.17352,"push_stage2.push2_tolerance":0.0239},"optimized_scores":{"best_composite_score":0.3132,"best_fitness_score":0.6532,"best_task_score":0.80245},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":70.0,"contact_point_centroid":[0.50571,-0.08347,0.05008],"force_p95":56.5444,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.43886,"mean_force":8.44292,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.49304,-0.07557,0.02677]},{"body_a":"attachment","body_b":"push_box","contact_count":97.0,"contact_point_centroid":[0.50828,0.02278,0.03804],"force_p95":15.39366,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.74818,"mean_force":4.61385,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.50496,0.0344,0.03282]},{"body_a":"world","body_b":"push_box","contact_count":530.0,"contact_point_centroid":[0.53245,-0.11832,-0.00023],"force_p95":5.83091,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.65692,"mean_force":1.56089,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.48959,-0.11158,0.02528]},{"body_a":"world","body_b":"push_box","contact_count":103.0,"contact_point_centroid":[0.51754,-0.01005,-5e-05],"force_p95":15.00855,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.52355,"mean_force":5.01307,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.50592,0.04373,0.03327]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.50638,0.05507,0.17436]},{"body_a":"world","body_b":"push_box","contact_count":912.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.51153,0.09752,0.04235]},{"body_a":"world","body_b":"push_box","contact_count":2180.0,"contact_point_centroid":[0.53498,-0.13239,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24521,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48155,-0.16249,0.06685]}],"total_contact_groups":7},"final_pose_error":0.01205,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53498,-0.13239,0.02499],"final_tcp_position":[0.48163,-0.16235,0.11196],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":67.43886,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.51472,0.11034,0.0517],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":228.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":19.0535,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":912.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.5108,0.08466,0.03604],"tcp_start":[0.51472,0.11034,0.0517],"tcp_to_object_dist_end":0.03884,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":151.0,"n_steps_budget":1000.0,"object_pos_end":[0.5079,-0.05388,0.02705],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.09646,"object_to_goal_dist_start":0.19823,"object_z_max":0.02694,"peak_contact_force":0.34194,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":200.0,"raw_peak_contact_force":66.74818,"subtask_id":"push_goal","tcp_end":[0.50029,-0.01809,0.03153],"tcp_start":[0.5108,0.08466,0.03604],"tcp_to_object_dist_end":0.03686,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":277.0,"n_steps_budget":630.0,"object_pos_end":[0.535,-0.1324,0.02493],"object_pos_start":[0.5079,-0.05388,0.02705],"object_to_goal_dist_end":0.03917,"object_to_goal_dist_start":0.09646,"object_z_max":0.02917,"peak_contact_force":0.24497,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":600.0,"raw_peak_contact_force":67.43886,"subtask_id":"push_goal","tcp_end":[0.48491,-0.16329,0.02351],"tcp_start":[0.50029,-0.01809,0.03153],"tcp_to_object_dist_end":0.05887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.53498,-0.13239,0.02499],"object_pos_start":[0.535,-0.1324,0.02493],"object_to_goal_dist_end":0.03916,"object_to_goal_dist_start":0.03917,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2180.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48163,-0.16235,0.11196],"tcp_start":[0.48491,-0.16329,0.02351],"tcp_to_object_dist_end":0.10633,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36058,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_distance":0.06955,"approach_object.approach_speed":0.04031,"contact_object.contact_force_threshold":9.2889,"push_stage1.push1_distance":0.14803,"push_stage1.push1_speed":0.07501,"push_stage1.push1_tolerance":0.03729,"push_stage2.push2_distance":0.12862,"push_stage2.push2_speed":0.12084,"push_stage2.push2_tolerance":0.0133},"optimized_scores":{"best_composite_score":0.40495,"best_fitness_score":0.74495,"best_task_score":0.89349},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":97.0,"contact_point_centroid":[0.47693,0.03439,0.03967],"force_p95":26.15199,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.98998,"mean_force":6.9349,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.47366,0.04601,0.03282]},{"body_a":"world","body_b":"push_box","contact_count":110.0,"contact_point_centroid":[0.48882,0.00517,-0.0001],"force_p95":38.65701,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.73511,"mean_force":6.74532,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.47296,0.05427,0.03306]},{"body_a":"attachment","body_b":"push_box","contact_count":282.0,"contact_point_centroid":[0.49361,-0.09123,0.04721],"force_p95":28.92311,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.85262,"mean_force":6.65135,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.48204,-0.08193,0.02615]},{"body_a":"world","body_b":"push_box","contact_count":553.0,"contact_point_centroid":[0.52052,-0.11405,-9e-05],"force_p95":16.72998,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.79799,"mean_force":4.1984,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.48168,-0.07543,0.02659]},{"body_a":"push_box","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.51762,-0.10559,0.05879],"force_p95":17.9652,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.62659,"mean_force":10.28693,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.4858,-0.12453,0.02493]},{"body_a":"world","body_b":"push_box","contact_count":1901.0,"contact_point_centroid":[0.52357,-0.14189,-1e-05],"force_p95":0.44573,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7183,"mean_force":0.27423,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48312,-0.13169,0.07329]},{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.5161,-0.11093,0.05919],"force_p95":1.34042,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.49066,"mean_force":0.49494,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48646,-0.13262,0.02478]},{"body_a":"attachment","body_b":"push_box","contact_count":70.0,"contact_point_centroid":[0.50032,-0.1358,0.05389],"force_p95":0.91581,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.07785,"mean_force":0.5893,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.48391,-0.13207,0.03441]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48475,0.05719,0.17204]},{"body_a":"world","body_b":"push_box","contact_count":744.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.4698,0.10508,0.04011]}],"total_contact_groups":10},"final_pose_error":0.01191,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52039,-0.14094,0.02499],"final_tcp_position":[0.48327,-0.13169,0.11337],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":87.98998,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47143,0.11463,0.04699],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06081,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":186.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":21.66655,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":744.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.47029,0.09544,0.03551],"tcp_start":[0.47143,0.11463,0.04699],"tcp_to_object_dist_end":0.03946,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":157.0,"n_steps_budget":1000.0,"object_pos_end":[0.49052,-0.05078,0.02664],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.09968,"object_to_goal_dist_start":0.2095,"object_z_max":0.02774,"peak_contact_force":6.42948,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":207.0,"raw_peak_contact_force":87.98998,"subtask_id":"push_goal","tcp_end":[0.47911,-0.01586,0.0314],"tcp_start":[0.47029,0.09544,0.03551],"tcp_to_object_dist_end":0.03704,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":445.0,"n_steps_budget":690.0,"object_pos_end":[0.52505,-0.14071,0.0296],"object_pos_start":[0.49052,-0.05078,0.02664],"object_to_goal_dist_end":0.02711,"object_to_goal_dist_start":0.09968,"object_z_max":0.02968,"peak_contact_force":15.74257,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":845.0,"raw_peak_contact_force":45.85262,"subtask_id":"push_goal","tcp_end":[0.48656,-0.13245,0.02479],"tcp_start":[0.47911,-0.01586,0.0314],"tcp_to_object_dist_end":0.03966,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":630.0,"object_pos_end":[0.52039,-0.14094,0.02499],"object_pos_start":[0.52505,-0.14071,0.0296],"object_to_goal_dist_end":0.02232,"object_to_goal_dist_start":0.02711,"object_z_max":0.0297,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1975.0,"raw_peak_contact_force":1.7183,"tcp_end":[0.48327,-0.13169,0.11337],"tcp_start":[0.48656,-0.13245,0.02479],"tcp_to_object_dist_end":0.09631,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.07182,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_distance":0.08232,"approach_object.approach_speed":0.07067,"contact_object.contact_force_threshold":10.42283,"push_stage1.push1_distance":0.15896,"push_stage1.push1_speed":0.09716,"push_stage1.push1_tolerance":0.03278,"push_stage2.push2_distance":0.2257,"push_stage2.push2_speed":0.15184,"push_stage2.push2_tolerance":0.03156},"optimized_scores":{"best_composite_score":0.43259,"best_fitness_score":0.77259,"best_task_score":0.95845},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":815.0,"contact_point_centroid":[0.50201,-0.15231,-0.00021],"force_p95":88.51649,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":108.48429,"mean_force":10.6942,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.39963,-0.13982,0.01174]},{"body_a":"push_box","body_b":"link7","contact_count":107.0,"contact_point_centroid":[0.50355,-0.1284,0.04968],"force_p95":107.30049,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":107.65056,"mean_force":78.71765,"phase_index":3.0,"phase_name":"push_stage2","phase_type":"push","tcp_position_centroid":[0.4657,-0.11976,0.01605]},{"body_a":"attachment","body_b":"push_box","contact_count":115.0,"contact_point_centroid":[0.53444,-0.05118,0.03789],"force_p95":56.14963,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.20058,"mean_force":9.69585,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.52952,-0.03952,0.01876]},{"body_a":"world","body_b":"push_box","contact_count":158.0,"contact_point_centroid":[0.53036,-0.09012,-0.0001],"force_p95":27.4578,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.17944,"mean_force":7.96583,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.5289,-0.04126,0.01869]},{"body_a":"push_box","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.53956,-0.1108,0.05179],"force_p95":20.26646,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.17422,"mean_force":3.28091,"phase_index":2.0,"phase_name":"push_stage1","phase_type":"push","tcp_position_centroid":[0.50858,-0.09615,0.01751]},{"body_a":"world","body_b":"push_box","contact_count":3920.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.53132,0.02452,0.16439]},{"body_a":"world","body_b":"push_box","contact_count":1192.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_object","phase_type":"contact","tcp_position_centroid":[0.55589,0.03073,0.02454]},{"body_a":"world","body_b":"push_box","contact_count":2020.0,"contact_point_centroid":[0.50239,-0.15494,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_after_push","phase_type":"retract","tcp_position_centroid":[0.31642,-0.16393,0.05201]}],"total_contact_groups":8},"final_pose_error":0.01,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50239,-0.15494,0.02499],"final_tcp_position":[0.31651,-0.16384,0.09764],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":108.48429,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":980.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3920.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.56471,0.04923,0.03104],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":298.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":33.1287,"phase_name":"contact_object","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1192.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.55007,0.01133,0.02226],"tcp_start":[0.56471,0.04923,0.03104],"tcp_to_object_dist_end":0.03744,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":191.0,"n_steps_budget":1000.0,"object_pos_end":[0.519,-0.14415,0.02573],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.01989,"object_to_goal_dist_start":0.13211,"object_z_max":0.02648,"peak_contact_force":0.0,"phase_name":"push_stage1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":289.0,"raw_peak_contact_force":93.20058,"subtask_id":"push_goal","tcp_end":[0.50451,-0.10755,0.01754],"tcp_start":[0.55007,0.01133,0.02226],"tcp_to_object_dist_end":0.0402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":930.0,"object_pos_end":[0.50239,-0.15494,0.02499],"object_pos_start":[0.519,-0.14415,0.02573],"object_to_goal_dist_end":0.00549,"object_to_goal_dist_start":0.01989,"object_z_max":0.02827,"peak_contact_force":0.24525,"phase_name":"push_stage2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":922.0,"raw_peak_contact_force":108.48429,"subtask_id":"push_goal","tcp_end":[0.31876,-0.16476,0.00734],"tcp_start":[0.50451,-0.10755,0.01754],"tcp_to_object_dist_end":0.18473,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":505.0,"n_steps_budget":630.0,"object_pos_end":[0.50239,-0.15494,0.02499],"object_pos_start":[0.50239,-0.15494,0.02499],"object_to_goal_dist_end":0.00549,"object_to_goal_dist_start":0.00549,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2020.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.31651,-0.16384,0.09764],"tcp_start":[0.31876,-0.16476,0.00734],"tcp_to_object_dist_end":0.19978,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```