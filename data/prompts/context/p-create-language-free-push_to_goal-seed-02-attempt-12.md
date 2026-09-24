## Search State

- **Seed**: 2
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | 0.2782 | 0.91 | ❌ rejected |
| 11 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.6096 | 0.88 | ❌ rejected |
| 10 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.5503 | 0.92 | ❌ rejected |
| 9 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | 0.5687 | 0.95 | ✅ accepted |
| 8 | approach → descend → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.6300 | 0.78 | ❌ rejected |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.947, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.278) — your mutation base

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
    contact_x_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
    contact_y_offset:
      type: scalar
      range:
      - -0.03
      - 0.03
      default: 0.0
      binds_to:
      - path: target.offset.y
        mode: add
    retry_x:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.01
      binds_to:
      - path: retry.offset.x
        mode: replace
    retry_y:
      type: scalar
      range:
      - -0.02
      - 0.02
      default: 0.01
      binds_to:
      - path: retry.offset.y
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
  guards:
  - id: contact_check
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    - contact_x_offset: status=consumed; consumers=target.offset.x (add)
    - contact_y_offset: status=consumed; consumers=target.offset.y (add)
    - retry_x: status=consumed; consumers=retry.offset.x (replace)
    - retry_y: status=consumed; consumers=retry.offset.y (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_check, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.0]
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

- **Composite score**: 0.278
- **task_score** (E): 0.910
- **fitness_score**: 0.768  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.690

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1738 |
| descend_1 | 1.00 | 1.00 | 0.1036 |
| contact_1 | 1.00 | 1.00 | 0.0161 |
| push_1 | 1.00 | 1.00 | 0.1255 |
| retract_1 | 1.00 | 1.00 | 0.0960 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.487, 0.032, 0.142) | (0.492, -0.018, 0.025)→(0.492, -0.018, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.487, 0.032, 0.142)→(0.487, 0.030, 0.043) | (0.492, -0.018, 0.025)→(0.492, -0.020, 0.025) | 0.139→0.138 | 1.00 / 3.000 | 0.256 | 115.659 |
| contact_1 | contact | 1.00 / force_exceeded | (0.487, 0.030, 0.043)→(0.487, 0.017, 0.036) | (0.492, -0.020, 0.025)→(0.492, -0.022, 0.025) | 0.138→0.136 | 1.00 / 4.333 | 25323.825 | 0.892 |
| push_1 | push | 1.00 / step_budget | (0.487, 0.017, 0.036)→(0.495, -0.102, 0.022) | (0.492, -0.022, 0.025)→(0.503, -0.137, 0.026) | 0.136→0.015 | 1.00 / 2.667 | 3.832 | 61.332 |
| retract_1 | retract | 1.00 / step_budget | (0.495, -0.102, 0.022)→(0.496, -0.143, 0.107) | (0.503, -0.137, 0.026)→(0.503, -0.140, 0.025) | 0.015→0.013 | 1.00 / 4.000 | 0.245 | 2.853 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.771
- goal_progress: 0.973
- terminal_score: 0.973
- phase_score: 0.736
- phase_breakdown.pre_contact_score: 0.161
- phase_breakdown.reach_goal_score: 0.983

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.831
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.973
- **Median Q (composite search score)**: 0.276
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.315


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28649,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_behind":0.02423,"approach_1.speed":0.06678,"contact_1.contact_approach_depth":0.0262,"contact_1.contact_force":6.82295,"contact_1.contact_x_offset":0.02975,"contact_1.contact_y_offset":0.00104,"contact_1.retry_x":-0.0008,"contact_1.retry_y":0.00467,"contact_1.speed":0.01148,"descend_1.descend_behind":0.06792,"push_1.push_distance":0.02686,"push_1.push_speed":0.06462},"optimized_scores":{"best_composite_score":0.27608,"best_fitness_score":0.76608,"best_task_score":0.91149},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":196.0,"contact_point_centroid":[0.48017,-0.05568,0.04348],"force_p95":40.70762,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.5991,"mean_force":8.41754,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47448,-0.04404,0.02694]},{"body_a":"world","body_b":"push_box","contact_count":366.0,"contact_point_centroid":[0.48833,-0.08243,-0.00013],"force_p95":23.47409,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.81998,"mean_force":5.08296,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47296,-0.03645,0.02762]},{"body_a":"world","body_b":"push_box","contact_count":758.0,"contact_point_centroid":[0.5104,-0.15107,-0.00011],"force_p95":0.76534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.96351,"mean_force":0.38019,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49057,-0.12848,0.07165]},{"body_a":"attachment","body_b":"push_box","contact_count":66.0,"contact_point_centroid":[0.49234,-0.12621,0.04681],"force_p95":1.08528,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.2702,"mean_force":0.72154,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48685,-0.11489,0.04015]},{"body_a":"world","body_b":"push_box","contact_count":1252.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48417,-0.00025,0.22411]},{"body_a":"world","body_b":"push_box","contact_count":860.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.46137,0.01607,0.09427]},{"body_a":"world","body_b":"push_box","contact_count":3432.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.45885,0.02282,0.0367]}],"total_contact_groups":7},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50706,-0.14102,0.02499],"final_tcp_position":[0.49509,-0.14362,0.10683],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":74.5991,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":313.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1252.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.46819,-0.00051,0.14472],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":215.0,"n_steps_budget":810.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":860.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.45559,0.03404,0.04295],"tcp_start":[0.46819,-0.00051,0.14472],"tcp_to_object_dist_end":0.06295,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":858.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":13.71818,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3432.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.46488,0.01281,0.03429],"tcp_start":[0.45559,0.03404,0.04295],"tcp_to_object_dist_end":0.03869,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.50735,-0.13883,0.02645],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.01345,"object_to_goal_dist_start":0.12903,"object_z_max":0.027,"peak_contact_force":8.48463,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":562.0,"raw_peak_contact_force":74.5991,"subtask_id":"reach_goal","tcp_end":[0.48682,-0.1058,0.02155],"tcp_start":[0.46488,0.01281,0.03429],"tcp_to_object_dist_end":0.03919,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":294.0,"n_steps_budget":720.0,"object_pos_end":[0.50706,-0.14102,0.02499],"object_pos_start":[0.50735,-0.13883,0.02645],"object_to_goal_dist_end":0.01142,"object_to_goal_dist_start":0.01345,"object_z_max":0.03096,"peak_contact_force":0.2452,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":824.0,"raw_peak_contact_force":1.96351,"tcp_end":[0.49509,-0.14362,0.10683],"tcp_start":[0.48682,-0.1058,0.02155],"tcp_to_object_dist_end":0.08275,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.872,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_behind":0.08029,"approach_1.speed":0.16288,"contact_1.contact_approach_depth":0.01299,"contact_1.contact_force":8.06118,"contact_1.contact_x_offset":0.00424,"contact_1.contact_y_offset":-0.01368,"contact_1.retry_x":-0.00422,"contact_1.retry_y":0.00047,"contact_1.speed":0.04344,"descend_1.descend_behind":0.02448,"push_1.push_distance":0.02058,"push_1.push_speed":0.06682},"optimized_scores":{"best_composite_score":0.3407,"best_fitness_score":0.8307,"best_task_score":0.9727},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":32.0,"contact_point_centroid":[0.44223,-0.00778,0.04771],"force_p95":346.06295,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":346.48695,"mean_force":185.07808,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.43701,0.00165,0.04691]},{"body_a":"world","body_b":"push_box","contact_count":929.0,"contact_point_centroid":[0.45041,-0.03179,-4e-05],"force_p95":60.32408,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":189.81636,"mean_force":6.64729,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4308,0.01834,0.0915]},{"body_a":"attachment","body_b":"push_box","contact_count":182.0,"contact_point_centroid":[0.4653,-0.07421,0.04423],"force_p95":44.45176,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.13237,"mean_force":10.50491,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46091,-0.06245,0.02919]},{"body_a":"world","body_b":"push_box","contact_count":400.0,"contact_point_centroid":[0.4717,-0.10235,-0.00012],"force_p95":24.58434,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.33061,"mean_force":5.34196,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45657,-0.05108,0.03098]},{"body_a":"world","body_b":"push_box","contact_count":792.0,"contact_point_centroid":[0.50007,-0.16159,-0.0001],"force_p95":0.78857,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.63521,"mean_force":0.3612,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48822,-0.13268,0.0725]},{"body_a":"attachment","body_b":"push_box","contact_count":56.0,"contact_point_centroid":[0.4854,-0.13359,0.04442],"force_p95":1.70697,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.79154,"mean_force":0.86488,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48281,-0.12178,0.04127]},{"body_a":"world","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.44076,-0.02032,-9e-05],"force_p95":1.31531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.18484,"mean_force":0.52944,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.43821,0.00015,0.04042]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.44167,-0.01115,0.05052],"force_p95":0.57791,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.57791,"mean_force":0.57791,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.43916,0.00082,0.04187]},{"body_a":"world","body_b":"push_box","contact_count":1280.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46409,0.018,0.22226]}],"total_contact_groups":9},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4986,-0.15321,0.02499],"final_tcp_position":[0.4944,-0.1446,0.10667],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":346.48695,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":320.0,"n_steps_budget":780.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1280.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.42692,0.03715,0.14249],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":236.0,"n_steps_budget":810.0,"object_pos_end":[0.45053,-0.03599,0.02576],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12429,"object_to_goal_dist_start":0.12843,"object_z_max":0.02563,"peak_contact_force":0.27835,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":961.0,"raw_peak_contact_force":346.48695,"subtask_id":"pre_contact","tcp_end":[0.43916,0.00082,0.04187],"tcp_start":[0.42692,0.03715,0.14249],"tcp_to_object_dist_end":0.04176,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":13.0,"n_steps_budget":990.0,"object_pos_end":[0.45014,-0.04206,0.02486],"object_pos_start":[0.45053,-0.03599,0.02576],"object_to_goal_dist_end":0.1189,"object_to_goal_dist_start":0.12429,"object_z_max":0.02589,"peak_contact_force":64.21889,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":15.0,"raw_peak_contact_force":2.18484,"subtask_id":"pre_contact","tcp_end":[0.438,-0.00035,0.03994],"tcp_start":[0.43916,0.00082,0.04187],"tcp_to_object_dist_end":0.04599,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.49798,-0.14999,0.02544],"object_pos_start":[0.45014,-0.04206,0.02486],"object_to_goal_dist_end":0.00206,"object_to_goal_dist_start":0.1189,"object_z_max":0.02599,"peak_contact_force":1.08739,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":582.0,"raw_peak_contact_force":63.13237,"subtask_id":"reach_goal","tcp_end":[0.48159,-0.11443,0.02232],"tcp_start":[0.438,-0.00035,0.03994],"tcp_to_object_dist_end":0.03928,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":289.0,"n_steps_budget":720.0,"object_pos_end":[0.4986,-0.15321,0.02499],"object_pos_start":[0.49798,-0.14999,0.02544],"object_to_goal_dist_end":0.00351,"object_to_goal_dist_start":0.00206,"object_z_max":0.0291,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":848.0,"raw_peak_contact_force":3.63521,"tcp_end":[0.4944,-0.1446,0.10667],"tcp_start":[0.48159,-0.11443,0.02232],"tcp_to_object_dist_end":0.08225,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2963,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_behind":0.0706,"approach_1.speed":0.12411,"contact_1.contact_approach_depth":0.0294,"contact_1.contact_force":4.75039,"contact_1.contact_x_offset":-0.00449,"contact_1.contact_y_offset":-0.01771,"contact_1.retry_x":0.00247,"contact_1.retry_y":-0.00531,"contact_1.speed":0.01176,"descend_1.descend_behind":0.05604,"push_1.push_distance":0.04705,"push_1.push_speed":0.0561},"optimized_scores":{"best_composite_score":0.2178,"best_fitness_score":0.7078,"best_task_score":0.84676},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":224.0,"contact_point_centroid":[0.53623,-0.03213,0.03097],"force_p95":33.26122,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.2638,"mean_force":5.03321,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53702,-0.02055,0.02641]},{"body_a":"world","body_b":"push_box","contact_count":442.0,"contact_point_centroid":[0.53009,-0.05651,-0.00015],"force_p95":13.62733,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.45255,"mean_force":2.94839,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53716,-0.02041,0.02656]},{"body_a":"world","body_b":"push_box","contact_count":722.0,"contact_point_centroid":[0.49843,-0.13653,-0.00014],"force_p95":1.29619,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.9596,"mean_force":0.4578,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5051,-0.11886,0.07053]},{"body_a":"attachment","body_b":"push_box","contact_count":70.0,"contact_point_centroid":[0.50754,-0.11069,0.03988],"force_p95":2.34034,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.86486,"mean_force":1.01222,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51092,-0.09929,0.03901]},{"body_a":"world","body_b":"push_box","contact_count":1484.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53123,0.02917,0.22019]},{"body_a":"world","body_b":"push_box","contact_count":708.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.56502,0.05765,0.09226]},{"body_a":"world","body_b":"push_box","contact_count":1916.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.55988,0.04534,0.03671]}],"total_contact_groups":7},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50202,-0.1255,0.02497],"final_tcp_position":[0.49881,-0.14147,0.10718],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":371.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1484.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.56509,0.0599,0.13904],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":177.0,"n_steps_budget":720.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":708.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.56661,0.05505,0.04412],"tcp_start":[0.56509,0.0599,0.13904],"tcp_to_object_dist_end":0.05856,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":479.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1916.0,"raw_peak_contact_force":0.24525,"subtask_id":"pre_contact","tcp_end":[0.55765,0.03834,0.03505],"tcp_start":[0.56661,0.05505,0.04412],"tcp_to_object_dist_end":0.03858,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.50462,-0.12111,0.02511],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.02925,"object_to_goal_dist_start":0.16043,"object_z_max":0.02665,"peak_contact_force":1.92536,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":666.0,"raw_peak_contact_force":46.2638,"subtask_id":"reach_goal","tcp_end":[0.5172,-0.0863,0.02112],"tcp_start":[0.55765,0.03834,0.03505],"tcp_to_object_dist_end":0.03722,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":308.0,"n_steps_budget":780.0,"object_pos_end":[0.50202,-0.1255,0.02497],"object_pos_start":[0.50462,-0.12111,0.02511],"object_to_goal_dist_end":0.02458,"object_to_goal_dist_start":0.02925,"object_z_max":0.03336,"peak_contact_force":0.24504,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":792.0,"raw_peak_contact_force":2.9596,"tcp_end":[0.49881,-0.14147,0.10718],"tcp_start":[0.5172,-0.0863,0.02112],"tcp_to_object_dist_end":0.08381,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```