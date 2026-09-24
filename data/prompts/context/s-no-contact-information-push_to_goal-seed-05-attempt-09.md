## Search State

- **Seed**: 5
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.2725 | 0.38 | ✅ accepted |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0820 | 0.00 | ✅ accepted |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0808 | 0.00 | ✅ accepted |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 2 | -0.0093 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0610 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`
- Frozen object start: [0.5366003508494456, 0.03695289476837925, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5366003508494456, 0.03695289476837925, 0.025)
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
  frozen_object_start: [0.5366, 0.037, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5366003508494456, 0.03695289476837925, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0366, -0.187, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266

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
| `object` | offset from object initial position (0.5366003508494456, 0.03695289476837925, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.272) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_contact
  anchor: object
  offset:
  - 0.025
  - 0.025
  - 0.0
  weight: 0.4
- id: push_goal
  target_entity: object
  metric: goal_progress
  weight: 0.6
phases:
- id: approach_high
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.025
    - 0.025
    - 0.08
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_high_speed:
      type: scalar
      range:
      - 0.05
      - 0.5
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_contact
- id: descend_to_contact
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.025
    - 0.025
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 10.0
      - 30.0
      default: 20.0
      binds_to:
      - path: termination.force_threshold
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
  guards:
  - id: contact_established
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: approach_contact
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
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_goal
- id: lift_after_push
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
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_high** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.025, 0.025, 0.08], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_high_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_contact** (`contact`)
  - target: source=yaml, anchor=task_object, offset=[0.025, 0.025, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_established, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=replace_offset_projection, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **lift_after_push** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.272
- **task_score** (E): 0.382
- **fitness_score**: 0.332  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_high | 1.00 | 0.1994 |
| descend_to_contact | 1.00 | 0.0608 |
| push_to_goal | 1.00 | 0.1563 |
| lift_after_push | 1.00 | 0.0884 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_high | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.538, 0.044, 0.112) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 |
| descend_to_contact | contact | 1.00 / force_exceeded | (0.538, 0.044, 0.112)→(0.537, 0.045, 0.051) | (0.519, 0.022, 0.025)→(0.519, 0.022, 0.025) | 0.173→0.173 |
| push_to_goal | push | 1.00 / step_budget | (0.537, 0.045, 0.051)→(0.505, -0.106, 0.028) | (0.519, 0.022, 0.025)→(0.516, -0.031, 0.034) | 0.173→0.122 |
| lift_after_push | retract | 1.00 / step_budget | (0.505, -0.106, 0.028)→(0.502, -0.105, 0.116) | (0.516, -0.031, 0.034)→(0.512, -0.045, 0.025) | 0.122→0.108 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.468
- approach_alignment: 0.758
- goal_progress: 0.418
- terminal_score: 0.418
- phase_score: 0.349
- phase_breakdown.push_goal_score: 0.191

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.376
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.418
- **Median Q (composite search score)**: 0.262
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.244


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `7ff7a4e3a1b03e3d7ba3d0b298d1ee8847b5344eb55f2aa0aaf582e7a98ab8ac`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `028a6956ebe09ab7c7952341570355f52da12e46fb22d3462091c70c024324ff`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.03704,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_high_speed":0.13077,"descend_to_contact.contact_force_threshold":19.68135,"descend_to_contact.descend_speed":0.06184,"push_to_goal.push_distance":0.21449,"push_to_goal.push_speed":0.15713},"optimized_scores":{"best_composite_score":0.23928,"best_fitness_score":0.29928,"best_task_score":0.40075},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":378.0,"contact_point_centroid":[0.54855,0.01333,0.04853],"force_p95":140.31657,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":144.16132,"mean_force":101.85963,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54438,0.00556,0.0486]},{"body_a":"world","body_b":"push_box","contact_count":1666.0,"contact_point_centroid":[0.52143,-0.01199,-0.00025],"force_p95":106.87771,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.7763,"mean_force":23.53392,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52924,-0.04215,0.03967]},{"body_a":"world","body_b":"push_box","contact_count":2744.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.52621,0.02871,0.20449]},{"body_a":"world","body_b":"push_box","contact_count":1324.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"contact","tcp_position_centroid":[0.55331,0.05882,0.07906]},{"body_a":"world","body_b":"push_box","contact_count":2192.0,"contact_point_centroid":[0.51311,-0.0366,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"lift_after_push","phase_type":"retract","tcp_position_centroid":[0.49311,-0.15305,0.06506]}],"total_contact_groups":5},"final_pose_error":0.01221,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51311,-0.0366,0.02499],"final_tcp_position":[0.49321,-0.15293,0.11039],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"phases":[{"n_steps":686.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_contact","tcp_end":[0.55448,0.05797,0.11046],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08982,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":331.0,"n_steps_budget":870.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_contact","tcp_end":[0.55473,0.05993,0.05136],"tcp_start":[0.55448,0.05797,0.11046],"tcp_to_object_dist_end":0.03939,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":598.0,"n_steps_budget":960.0,"object_pos_end":[0.51311,-0.0366,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.11416,"object_to_goal_dist_start":0.1905,"object_z_max":0.03546,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_goal","tcp_end":[0.49655,-0.15382,0.02209],"tcp_start":[0.55473,0.05993,0.05136],"tcp_to_object_dist_end":0.11842,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":548.0,"n_steps_budget":630.0,"object_pos_end":[0.51311,-0.0366,0.02499],"object_pos_start":[0.51311,-0.0366,0.02499],"object_to_goal_dist_end":0.11416,"object_to_goal_dist_start":0.11416,"object_z_max":0.02499,"phase_name":"lift_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"push_goal","tcp_end":[0.49321,-0.15293,0.11039],"tcp_start":[0.49655,-0.15382,0.02209],"tcp_to_object_dist_end":0.14568,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1c6409cc6d884b90ecc3937d36e5ea87cc4ef513b6f301a9da66b4e84390f805`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81111,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_high_speed":0.27688,"descend_to_contact.contact_force_threshold":17.62209,"descend_to_contact.descend_speed":0.05538,"push_to_goal.push_distance":0.10768,"push_to_goal.push_speed":0.12058},"optimized_scores":{"best_composite_score":0.31629,"best_fitness_score":0.37629,"best_task_score":0.41798},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1236.0,"contact_point_centroid":[0.50739,-0.04062,-0.0005],"force_p95":173.29834,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":191.0948,"mean_force":54.45608,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52194,-0.03803,0.04685]},{"body_a":"attachment","body_b":"push_box","contact_count":463.0,"contact_point_centroid":[0.52556,-0.03443,0.04692],"force_p95":183.08347,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.96854,"mean_force":143.5839,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52172,-0.04457,0.04645]},{"body_a":"attachment","body_b":"push_box","contact_count":80.0,"contact_point_centroid":[0.49912,-0.09852,0.04578],"force_p95":1.84915,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.90396,"mean_force":0.87642,"phase_index":3.0,"phase_name":"lift_after_push","phase_type":"retract","tcp_position_centroid":[0.50454,-0.10906,0.04463]},{"body_a":"world","body_b":"push_box","contact_count":1698.0,"contact_point_centroid":[0.483,-0.07133,-5e-05],"force_p95":0.87883,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.31199,"mean_force":0.32103,"phase_index":3.0,"phase_name":"lift_after_push","phase_type":"retract","tcp_position_centroid":[0.50437,-0.10874,0.08319]},{"body_a":"world","body_b":"push_box","contact_count":2096.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51117,0.00279,0.20652]},{"body_a":"world","body_b":"push_box","contact_count":1444.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"contact","tcp_position_centroid":[0.52259,0.00573,0.08072]}],"total_contact_groups":6},"final_pose_error":0.01217,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48177,-0.0758,0.02499],"final_tcp_position":[0.50458,-0.1087,0.12032],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":524.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_contact","tcp_end":[0.52416,0.00566,0.11329],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0937,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":361.0,"n_steps_budget":990.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_contact","tcp_end":[0.52367,0.00588,0.05115],"tcp_start":[0.52416,0.00566,0.11329],"tcp_to_object_dist_end":0.04072,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":478.0,"n_steps_budget":720.0,"object_pos_end":[0.49528,-0.0562,0.03477],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.09442,"object_to_goal_dist_start":0.13127,"object_z_max":0.03475,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_goal","tcp_end":[0.5079,-0.1093,0.03202],"tcp_start":[0.52367,0.00588,0.05115],"tcp_to_object_dist_end":0.05464,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":557.0,"n_steps_budget":630.0,"object_pos_end":[0.48177,-0.0758,0.02499],"object_pos_start":[0.49528,-0.0562,0.03477],"object_to_goal_dist_end":0.0764,"object_to_goal_dist_start":0.09442,"object_z_max":0.03477,"phase_name":"lift_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"push_goal","tcp_end":[0.50458,-0.1087,0.12032],"tcp_start":[0.5079,-0.1093,0.03202],"tcp_to_object_dist_end":0.1034,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f52ec1899e2888770a8b6b3ae605718303ef4b10e72cfd7d20ce53303721b2b0`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89655,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_high.approach_high_speed":0.37639,"descend_to_contact.contact_force_threshold":19.58972,"descend_to_contact.descend_speed":0.05552,"push_to_goal.push_distance":0.12005,"push_to_goal.push_speed":0.14333},"optimized_scores":{"best_composite_score":0.2619,"best_fitness_score":0.3219,"best_task_score":0.32633},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1031.0,"contact_point_centroid":[0.51789,0.02393,-0.00047],"force_p95":160.49698,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":175.96567,"mean_force":53.73729,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5302,0.02805,0.04753]},{"body_a":"attachment","body_b":"push_box","contact_count":427.0,"contact_point_centroid":[0.53557,0.02804,0.04681],"force_p95":168.08586,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":174.88659,"mean_force":128.22128,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52974,0.01831,0.04688]},{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54128,-0.00342,0.08119],"force_p95":6.76477,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.79306,"mean_force":5.65731,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51561,-0.04646,0.03286]},{"body_a":"world","body_b":"push_box","contact_count":1805.0,"contact_point_centroid":[0.54183,-0.02168,-0.0001],"force_p95":0.76161,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.85391,"mean_force":0.31217,"phase_index":3.0,"phase_name":"lift_after_push","phase_type":"retract","tcp_position_centroid":[0.508,-0.0533,0.07933]},{"body_a":"world","body_b":"push_box","contact_count":2192.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_high","phase_type":"approach","tcp_position_centroid":[0.51585,0.03289,0.20687]},{"body_a":"world","body_b":"push_box","contact_count":1428.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"contact","tcp_position_centroid":[0.53247,0.0686,0.08012]}],"total_contact_groups":6},"final_pose_error":0.01209,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54091,-0.02288,0.02499],"final_tcp_position":[0.50824,-0.05327,0.11741],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"phases":[{"n_steps":548.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"phase_name":"approach_high","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_contact","tcp_end":[0.53386,0.06736,0.11241],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09158,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":357.0,"n_steps_budget":990.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"approach_contact","tcp_end":[0.53369,0.07015,0.05129],"tcp_start":[0.53386,0.06736,0.11241],"tcp_to_object_dist_end":0.03932,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":449.0,"n_steps_budget":660.0,"object_pos_end":[0.53916,0.00013,0.04186],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.15606,"object_to_goal_dist_start":0.19823,"object_z_max":0.04291,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_goal","tcp_end":[0.51162,-0.05353,0.02902],"tcp_start":[0.53369,0.07015,0.05129],"tcp_to_object_dist_end":0.06166,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":554.0,"n_steps_budget":630.0,"object_pos_end":[0.54091,-0.02288,0.02499],"object_pos_start":[0.53916,0.00013,0.04186],"object_to_goal_dist_end":0.13354,"object_to_goal_dist_start":0.15606,"object_z_max":0.04186,"phase_name":"lift_after_push","phase_peak_obstacle_force":0.0,"phase_type":"retract","subtask_id":"push_goal","tcp_end":[0.50824,-0.05327,0.11741],"tcp_start":[0.51162,-0.05353,0.02902],"tcp_to_object_dist_end":0.10263,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```