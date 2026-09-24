## Search State

- **Seed**: 2
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.1749 | 0.59 | ❌ rejected |
| 2 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6412 | 0.80 | ✅ accepted |
| 1 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6219 | 0.73 | ❌ rejected |
| 0 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.6133 | 0.74 | ✅ accepted |

**Proposal policy**: task_score is 0.59 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.801, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.175) — your mutation base

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

- **Composite score**: 0.175
- **task_score** (E): 0.590
- **fitness_score**: 0.315  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1693 |
| descend_behind | 1.00 | 1.00 | 0.0986 |
| contact_forward | 1.00 | 1.00 | 0.0129 |
| push_to_goal | 0.00 | 1.00 | 0.0001 |
| retract_up | 1.00 | 1.00 | 0.1804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.487, 0.025, 0.143) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_behind | descend | 1.00 / step_budget | (0.487, 0.025, 0.143)→(0.484, 0.028, 0.044) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_forward | contact | 1.00 / force_exceeded | (0.484, 0.028, 0.044)→(0.482, 0.019, 0.036) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 5.000 | 25310.025 | 0.245 |
| push_to_goal | push | 0.00 / guard_failure | (0.482, 0.019, 0.036)→(0.482, 0.019, 0.036) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 3.667 | 5.957 | 12.234 |
| retract_up | retract | 1.00 / step_budget | (0.482, 0.019, 0.036)→(0.495, -0.136, 0.113) | (0.492, -0.018, 0.025)→(0.498, -0.098, 0.025) | 0.139→0.057 | 1.00 / 4.000 | 0.248 | 22.711 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.606
- lateral_force_integral: None
- approach_alignment: 0.783
- goal_progress: 0.605
- terminal_score: 0.605
- phase_score: 0.132
- phase_breakdown.pre_contact_score: 0.440
- phase_breakdown.reach_goal_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.321
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.605
- **Median Q (composite search score)**: 0.175
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.259


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.74775,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.speed":0.1134,"contact_forward.contact_force":6.79313,"contact_forward.speed":0.03689,"push_to_goal.push_distance":0.14053,"push_to_goal.push_speed":0.06587},"optimized_scores":{"best_composite_score":0.18139,"best_fitness_score":0.32139,"best_task_score":0.60549},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":136.0,"contact_point_centroid":[0.46618,-0.03056,0.05107],"force_p95":21.21361,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.85119,"mean_force":7.20394,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.46335,-0.01904,0.05067]},{"body_a":"world","body_b":"push_box","contact_count":882.0,"contact_point_centroid":[0.48494,-0.07769,-0.00015],"force_p95":9.59893,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.48314,"mean_force":1.5924,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.47662,-0.07183,0.07843]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.45736,0.00079,0.03615],"force_p95":11.44606,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.04012,"mean_force":6.09957,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45736,0.01278,0.03614]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":7.16611,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.00134,"mean_force":3.20263,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45736,0.0128,0.03616]},{"body_a":"world","body_b":"push_box","contact_count":1228.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.48183,0.01021,0.22344]},{"body_a":"world","body_b":"push_box","contact_count":792.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.46005,0.02242,0.09485]},{"body_a":"world","body_b":"push_box","contact_count":684.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"contact_forward","phase_type":"contact","tcp_position_centroid":[0.45657,0.01798,0.03882]}],"total_contact_groups":7},"final_pose_error":0.0197,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49017,-0.10006,0.02442],"final_tcp_position":[0.49333,-0.13605,0.11279],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":23.85119,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1228.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.46328,0.0212,0.144],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12763,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":198.0,"n_steps_budget":750.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":792.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.458,0.02372,0.04441],"tcp_start":[0.46328,0.0212,0.144],"tcp_to_object_dist_end":0.0534,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":171.0,"n_steps_budget":900.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":22.48124,"phase_name":"contact_forward","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":684.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.45736,0.0128,0.03616],"tcp_start":[0.458,0.02372,0.04441],"tcp_to_object_dist_end":0.0411,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.47137,-0.02421,0.02501],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12901,"object_to_goal_dist_start":0.12903,"object_z_max":0.02501,"peak_contact_force":2.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":12.04012,"subtask_id":"reach_goal","tcp_end":[0.45732,0.01273,0.03607],"tcp_start":[0.45735,0.01277,0.03612],"tcp_to_object_dist_end":0.04105,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.49017,-0.10006,0.02442],"object_pos_start":[0.47134,-0.02425,0.025],"object_to_goal_dist_end":0.0509,"object_to_goal_dist_start":0.12898,"object_z_max":0.03534,"peak_contact_force":0.25351,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1018.0,"raw_peak_contact_force":23.85119,"tcp_end":[0.49333,-0.13605,0.11279],"tcp_start":[0.45732,0.01273,0.03607],"tcp_to_object_dist_end":0.09547,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90385,"average_solve_count":104.0,"average_success_count":104.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.speed":0.15263,"contact_forward.contact_force":4.40893,"contact_forward.speed":0.02573,"push_to_goal.push_distance":0.21031,"push_to_goal.push_speed":0.06676},"optimized_scores":{"best_composite_score":0.1683,"best_fitness_score":0.3083,"best_task_score":0.58398},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":109.0,"contact_point_centroid":[0.44285,-0.03384,0.05217],"force_p95":15.37494,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.15959,"mean_force":5.29108,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4401,-0.02219,0.05031]},{"body_a":"world","body_b":"push_box","contact_count":1062.0,"contact_point_centroid":[0.46966,-0.0865,-0.00013],"force_p95":4.39341,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.80591,"mean_force":0.96198,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.46601,-0.08082,0.08217]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.42993,-0.0066,0.0374],"force_p95":8.60827,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.94561,"mean_force":5.57222,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.42993,0.00539,0.03739]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.45028,-0.03992,-0.0],"force_p95":6.07694,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.21202,"mean_force":2.11366,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.42993,0.00539,0.0374]},{"body_a":"world","body_b":"push_box","contact_count":1220.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.46941,0.00608,0.22302]},{"body_a":"world","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.43306,0.01329,0.09461]},{"body_a":"world","body_b":"push_box","contact_count":744.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"contact_forward","phase_type":"contact","tcp_position_centroid":[0.42872,0.00933,0.03954]}],"total_contact_groups":7},"final_pose_error":0.01997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47314,-0.10381,0.02498],"final_tcp_position":[0.49119,-0.13671,0.11298],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":17.15959,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":305.0,"n_steps_budget":780.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1220.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.4376,0.0126,0.14342],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12704,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":200.0,"n_steps_budget":750.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":800.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.42952,0.01402,0.04451],"tcp_start":[0.4376,0.0126,0.14342],"tcp_to_object_dist_end":0.05377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":186.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":14.05645,"phase_name":"contact_forward","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":744.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.42993,0.0054,0.03741],"tcp_start":[0.42952,0.01402,0.04451],"tcp_to_object_dist_end":0.044,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.45027,-0.0316,0.025],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12842,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":2.67171,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":8.94561,"subtask_id":"reach_goal","tcp_end":[0.42989,0.00536,0.03734],"tcp_start":[0.42992,0.00538,0.03738],"tcp_to_object_dist_end":0.04397,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":496.0,"n_steps_budget":1000.0,"object_pos_end":[0.47314,-0.10381,0.02498],"object_pos_start":[0.45024,-0.03161,0.02501],"object_to_goal_dist_end":0.05343,"object_to_goal_dist_start":0.12842,"object_z_max":0.03534,"peak_contact_force":0.24513,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1171.0,"raw_peak_contact_force":17.15959,"tcp_end":[0.49119,-0.13671,0.11298],"tcp_start":[0.42989,0.00536,0.03734],"tcp_to_object_dist_end":0.09566,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73554,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.speed":0.1055,"contact_forward.contact_force":6.70469,"contact_forward.speed":0.02631,"push_to_goal.push_distance":0.28439,"push_to_goal.push_speed":0.05704},"optimized_scores":{"best_composite_score":0.17509,"best_fitness_score":0.31509,"best_task_score":0.57915},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":136.0,"contact_point_centroid":[0.54423,-0.00814,0.04729],"force_p95":20.06034,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.1231,"mean_force":5.64927,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.54403,0.00375,0.04729]},{"body_a":"world","body_b":"push_box","contact_count":1102.0,"contact_point_centroid":[0.53245,-0.07536,-0.00011],"force_p95":6.06297,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.45537,"mean_force":1.09834,"phase_index":4.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.52044,-0.07201,0.08275]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.55756,0.02633,0.03465],"force_p95":15.5893,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.71504,"mean_force":14.45768,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55757,0.03831,0.03462]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":5.77728,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.04594,"mean_force":3.7661,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55757,0.03831,0.03462]},{"body_a":"world","body_b":"push_box","contact_count":1424.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52805,0.02065,0.22092]},{"body_a":"world","body_b":"push_box","contact_count":728.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.56027,0.04457,0.09249]},{"body_a":"world","body_b":"push_box","contact_count":544.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"contact_forward","phase_type":"contact","tcp_position_centroid":[0.55926,0.04215,0.03719]}],"total_contact_groups":7},"final_pose_error":0.01977,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53099,-0.09002,0.02499],"final_tcp_position":[0.5014,-0.13453,0.11276],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1424.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.55864,0.04247,0.1402],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":182.0,"n_steps_budget":750.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":728.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.56375,0.04687,0.04373],"tcp_start":[0.55864,0.04247,0.1402],"tcp_to_object_dist_end":0.05034,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":136.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_forward","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":544.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.55758,0.03833,0.03464],"tcp_start":[0.56375,0.04687,0.04373],"tcp_to_object_dist_end":0.03846,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00135,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16042,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":13.20032,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":15.71504,"subtask_id":"reach_goal","tcp_end":[0.55752,0.03829,0.03454],"tcp_start":[0.55755,0.0383,0.0346],"tcp_to_object_dist_end":0.0384,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":518.0,"n_steps_budget":1000.0,"object_pos_end":[0.53099,-0.09002,0.02499],"object_pos_start":[0.55317,0.00134,0.02499],"object_to_goal_dist_end":0.06752,"object_to_goal_dist_start":0.1604,"object_z_max":0.03534,"peak_contact_force":0.24524,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1238.0,"raw_peak_contact_force":27.1231,"tcp_end":[0.5014,-0.13453,0.11276],"tcp_start":[0.55752,0.03829,0.03454],"tcp_to_object_dist_end":0.10277,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```