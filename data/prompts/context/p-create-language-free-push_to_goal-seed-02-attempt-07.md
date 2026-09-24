## Search State

- **Seed**: 2
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6548 | 0.82 | ✅ accepted |
| 6 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3478 | 0.48 | ❌ rejected |
| 5 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.5642 | 0.70 | ❌ rejected |
| 4 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6401 | 0.80 | ❌ rejected |
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1749 | 0.59 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`
- Frozen object start: [0.47139345610991795, -0.0241810627903052, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.47139345610991795, -0.0241810627903052, 0.025)
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
  frozen_object_start: [0.4714, -0.0242, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.47139345610991795, -0.0241810627903052, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0286, -0.1258, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.818, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.47139345610991795, -0.0241810627903052, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.655) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.0
  weight: 0.3
- id: reach_goal
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
    entity: push_box
    offset:
    - 0.0
    - 0.05
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: pre_contact
- id: contact_1
  type: contact
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
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_contact
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.08
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_goal
- id: retract_1
  type: retract
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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.05, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.05, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **contact_1** (`contact`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.655
- **task_score** (E): 0.818
- **fitness_score**: 0.795  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1650 |
| descend_1 | 1.00 | 1.00 | 0.0991 |
| contact_1 | 1.00 | 1.00 | 0.0153 |
| push_1 | 1.00 | 1.00 | 0.1221 |
| retract_1 | 1.00 | 1.00 | 0.0978 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.490, 0.028, 0.143) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.490, 0.028, 0.143)→(0.488, 0.031, 0.044) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.488, 0.031, 0.044)→(0.485, 0.019, 0.035) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 25313.404 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.485, 0.019, 0.035)→(0.498, -0.099, 0.022) | (0.492, -0.018, 0.025)→(0.518, -0.129, 0.027) | 0.139→0.029 | 1.00 / 2.333 | 17.885 | 49.874 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.099, 0.022)→(0.496, -0.143, 0.107) | (0.518, -0.129, 0.027)→(0.518, -0.133, 0.025) | 0.029→0.029 | 1.00 / 4.000 | 0.245 | 8.448 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.789
- goal_progress: 0.965
- terminal_score: 0.965
- phase_score: 0.904
- phase_breakdown.pre_contact_score: 0.699
- phase_breakdown.reach_goal_score: 0.992

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.928
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.981
- **Median Q (composite search score)**: 0.786
- **K-run variance**: 0.0351
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.532


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `27920116be2b9a598fe307ae470bb0295293d051bb1ef513a0996a4d851f2459`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1a1e2536715050e6c37d8aed13e4ecd62004f6234f1413b07d7b475a233f55c9`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47139,-0.02418,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73288,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08063,"contact_1.contact_force":5.11431,"contact_1.speed":0.02232,"push_1.push_distance":0.11073,"push_1.push_speed":0.08277},"optimized_scores":{"best_composite_score":0.78843,"best_fitness_score":0.92843,"best_task_score":0.96524},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":217.0,"contact_point_centroid":[0.47923,-0.05852,0.04199],"force_p95":40.04877,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.81833,"mean_force":7.8112,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47549,-0.04673,0.02783]},{"body_a":"world","body_b":"push_box","contact_count":395.0,"contact_point_centroid":[0.48623,-0.09304,-9e-05],"force_p95":19.43351,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.33869,"mean_force":4.80617,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47527,-0.04555,0.02797]},{"body_a":"attachment","body_b":"push_box","contact_count":55.0,"contact_point_centroid":[0.49282,-0.13318,0.04729],"force_p95":0.92807,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.50741,"mean_force":0.69615,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4887,-0.12146,0.04107]},{"body_a":"world","body_b":"push_box","contact_count":811.0,"contact_point_centroid":[0.49944,-0.16102,-0.00011],"force_p95":0.62418,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.46063,"mean_force":0.3373,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49152,-0.1318,0.07038]},{"body_a":"world","body_b":"push_box","contact_count":1240.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48644,0.01066,0.22383]},{"body_a":"world","body_b":"push_box","contact_count":788.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47018,0.02349,0.09519]},{"body_a":"world","body_b":"push_box","contact_count":988.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.46584,0.01795,0.03838]}],"total_contact_groups":7},"final_pose_error":0.01995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49791,-0.15397,0.02499],"final_tcp_position":[0.49533,-0.14448,0.10641],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":48.81833,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":310.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1240.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.47286,0.02218,0.14442],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":197.0,"n_steps_budget":750.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":788.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.46875,0.02489,0.04476],"tcp_start":[0.47286,0.02218,0.14442],"tcp_to_object_dist_end":0.05298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":247.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":18.92243,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":988.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.46562,0.0128,0.03587],"tcp_start":[0.46875,0.02489,0.04476],"tcp_to_object_dist_end":0.03898,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.49915,-0.14975,0.0256],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.00106,"object_to_goal_dist_start":0.12903,"object_z_max":0.02613,"peak_contact_force":32.94029,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":612.0,"raw_peak_contact_force":48.81833,"subtask_id":"reach_goal","tcp_end":[0.48908,-0.11387,0.02177],"tcp_start":[0.46562,0.0128,0.03587],"tcp_to_object_dist_end":0.03747,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":284.0,"n_steps_budget":690.0,"object_pos_end":[0.49791,-0.15397,0.02499],"object_pos_start":[0.49915,-0.14975,0.0256],"object_to_goal_dist_end":0.00448,"object_to_goal_dist_start":0.00106,"object_z_max":0.02902,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":866.0,"raw_peak_contact_force":2.50741,"tcp_end":[0.49533,-0.14448,0.10641],"tcp_start":[0.48908,-0.11387,0.02177],"tcp_to_object_dist_end":0.08201,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e864853e179d3df1b19d9aaa17e18a5fe8c66fe7533fc0dd3a88a693de7416e7`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.97273,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.18775,"contact_1.contact_force":9.40833,"contact_1.speed":0.04893,"push_1.push_distance":0.10549,"push_1.push_speed":0.09585},"optimized_scores":{"best_composite_score":0.78601,"best_fitness_score":0.92601,"best_task_score":0.98101},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":239.0,"contact_point_centroid":[0.46591,-0.06553,0.03856],"force_p95":37.57215,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.07716,"mean_force":6.1773,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46302,-0.0537,0.02765]},{"body_a":"world","body_b":"push_box","contact_count":348.0,"contact_point_centroid":[0.47241,-0.09946,-8e-05],"force_p95":19.50507,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.46672,"mean_force":4.7392,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46277,-0.05273,0.02782]},{"body_a":"world","body_b":"push_box","contact_count":871.0,"contact_point_centroid":[0.49893,-0.15859,-9e-05],"force_p95":0.66363,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72808,"mean_force":0.33069,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48798,-0.13004,0.06891]},{"body_a":"attachment","body_b":"push_box","contact_count":49.0,"contact_point_centroid":[0.48599,-0.13234,0.04667],"force_p95":1.06268,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.50373,"mean_force":0.75703,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48365,-0.12044,0.04342]},{"body_a":"world","body_b":"push_box","contact_count":1148.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4776,0.00768,0.22324]},{"body_a":"world","body_b":"push_box","contact_count":796.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45089,0.01679,0.09493]},{"body_a":"world","body_b":"push_box","contact_count":604.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4457,0.01138,0.03891]}],"total_contact_groups":7},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49826,-0.15171,0.02499],"final_tcp_position":[0.4945,-0.14428,0.10675],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":52.07716,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":287.0,"n_steps_budget":630.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1148.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.45463,0.01588,0.14411],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":199.0,"n_steps_budget":750.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":796.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.4483,0.01777,0.04449],"tcp_start":[0.45463,0.01588,0.14411],"tcp_to_object_dist_end":0.0531,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":151.0,"n_steps_budget":690.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":27.75213,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":604.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.44526,0.00536,0.03597],"tcp_start":[0.4483,0.01777,0.04449],"tcp_to_object_dist_end":0.03887,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":324.0,"n_steps_budget":930.0,"object_pos_end":[0.49709,-0.1476,0.0257],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.00384,"object_to_goal_dist_start":0.12843,"object_z_max":0.02651,"peak_contact_force":0.16349,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":587.0,"raw_peak_contact_force":52.07716,"subtask_id":"reach_goal","tcp_end":[0.48227,-0.11145,0.02189],"tcp_start":[0.44526,0.00536,0.03597],"tcp_to_object_dist_end":0.03925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":291.0,"n_steps_budget":720.0,"object_pos_end":[0.49826,-0.15171,0.02499],"object_pos_start":[0.49709,-0.1476,0.0257],"object_to_goal_dist_end":0.00244,"object_to_goal_dist_start":0.00384,"object_z_max":0.02927,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":920.0,"raw_peak_contact_force":1.72808,"tcp_end":[0.4945,-0.14428,0.10675],"tcp_start":[0.48227,-0.11145,0.02189],"tcp_to_object_dist_end":0.08218,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c820cf29ab3e34ea9695cb40d5aba5de55f3ad951ee91f0df578ae7146ee7727`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6014,"average_solve_count":143.0,"average_success_count":143.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.15664,"contact_1.contact_force":5.92386,"contact_1.speed":0.02853,"push_1.push_distance":0.09841,"push_1.push_speed":0.05097},"optimized_scores":{"best_composite_score":0.38986,"best_fitness_score":0.52986,"best_task_score":0.50718},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":194.0,"contact_point_centroid":[0.54237,-0.03126,0.04842],"force_p95":35.18579,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.72772,"mean_force":9.99024,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53024,-0.0225,0.02569]},{"body_a":"push_box","body_b":"link7","contact_count":89.0,"contact_point_centroid":[0.56219,-0.0507,0.05548],"force_p95":37.96394,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.33588,"mean_force":25.58112,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52413,-0.05404,0.02313]},{"body_a":"world","body_b":"push_box","contact_count":395.0,"contact_point_centroid":[0.56879,-0.0545,-9e-05],"force_p95":34.27327,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.43988,"mean_force":10.94995,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53148,-0.01676,0.02633]},{"body_a":"attachment","body_b":"push_box","contact_count":20.0,"contact_point_centroid":[0.53675,-0.07889,0.0525],"force_p95":2.69772,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.10825,"mean_force":1.98435,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51837,-0.07672,0.02651]},{"body_a":"world","body_b":"push_box","contact_count":1174.0,"contact_point_centroid":[0.55707,-0.09539,-2e-05],"force_p95":0.48329,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.51875,"mean_force":0.29589,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50767,-0.10946,0.06766]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.55932,-0.06547,0.05455],"force_p95":0.41984,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42201,"mean_force":0.40028,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52107,-0.07237,0.02232]},{"body_a":"world","body_b":"push_box","contact_count":1296.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52092,0.02168,0.22168]},{"body_a":"world","body_b":"push_box","contact_count":744.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5449,0.04703,0.09316]},{"body_a":"world","body_b":"push_box","contact_count":852.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54462,0.04349,0.03672]}],"total_contact_groups":9},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55653,-0.09473,0.02499],"final_tcp_position":[0.49931,-0.14006,0.10776],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":324.0,"n_steps_budget":780.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1296.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.54388,0.04469,0.14139],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":186.0,"n_steps_budget":750.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":744.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.54766,0.04958,0.04383],"tcp_start":[0.54388,0.04469,0.14139],"tcp_to_object_dist_end":0.05206,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":213.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":852.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.54458,0.03833,0.03398],"tcp_start":[0.54766,0.04958,0.04383],"tcp_to_object_dist_end":0.03901,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":300.0,"n_steps_budget":1000.0,"object_pos_end":[0.55878,-0.0908,0.02842],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.08349,"object_to_goal_dist_start":0.16043,"object_z_max":0.02924,"peak_contact_force":20.55271,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":678.0,"raw_peak_contact_force":48.72772,"subtask_id":"reach_goal","tcp_end":[0.5212,-0.072,0.02239],"tcp_start":[0.54458,0.03833,0.03398],"tcp_to_object_dist_end":0.04245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":325.0,"n_steps_budget":840.0,"object_pos_end":[0.55653,-0.09473,0.02499],"object_pos_start":[0.55878,-0.0908,0.02842],"object_to_goal_dist_end":0.07906,"object_to_goal_dist_start":0.08349,"object_z_max":0.02845,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1196.0,"raw_peak_contact_force":21.10825,"tcp_end":[0.49931,-0.14006,0.10776],"tcp_start":[0.5212,-0.072,0.02239],"tcp_to_object_dist_end":0.11037,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```