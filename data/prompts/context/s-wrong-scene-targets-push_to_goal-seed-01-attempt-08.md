## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2024 | 0.73 | ✅ accepted |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2042 | 0.54 | ❌ rejected |
| 6 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.2425 | 0.00 | ❌ rejected |
| 5 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1999 | 0.52 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 4 | 0.5623 | 0.42 | ❌ rejected |

**Proposal policy**: task_score is 0.73 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5014185949640309, 0.05405564355911223, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5014185949640309, 0.05405564355911223, 0.025]
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
  frozen_object_start: [0.5014, 0.0541, 0.025]
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
  push_direction: [-0.0014, -0.2041, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.726, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.202) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.05
  weight: 0.3
- id: push_to_goal
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
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_z_offset:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: replace
  subtask_id: reach_object
- id: align_behind
  type: align
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
    - 0.0
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: add_to_offset
      sign: negative
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    behind_distance:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
- id: push_to_goal
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
      distance: 0.2
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
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - -0.01
    - 0.0
    - 0.0
  subtask_id: push_to_goal
- id: retrieve
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.08
    tolerance: 0.03
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_z_offset: status=consumed; consumers=target.offset.z (replace)
- **align_behind** (`align`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=add_to_offset, sign=negative}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=1, strategy=offset_target, offset=[-0.01, 0.0, 0.0]
- **retrieve** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=push_box, offset=[0.0, 0.0, 0.08], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.202
- **task_score** (E): 0.726
- **fitness_score**: 0.462  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.2121 |
| align_behind | 1.00 | 1.00 | 0.0902 |
| push_to_goal | 0.00 | 1.00 | 0.0003 |
| retrieve | 1.00 | 1.00 | 0.1635 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.474, -0.000, 0.094) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_behind | align | 1.00 / step_budget | (0.474, -0.000, 0.094)→(0.458, 0.064, 0.035) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 31.982 |
| push_to_goal | push | 0.00 / guard_failure | (0.466, 0.021, 0.029)→(0.466, 0.021, 0.029) | (0.474, -0.001, 0.025)→(0.480, -0.015, 0.025) | 0.154→0.139 | 1.00 / 3.000 | 8.687 | 31.446 |
| retrieve | retract | 1.00 / step_budget | (0.466, 0.021, 0.029)→(0.492, -0.126, 0.089) | (0.480, -0.015, 0.025)→(0.506, -0.105, 0.025) | 0.138→0.046 | 1.00 / 2.333 | 0.921 | 34.936 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.830
- lateral_force_integral: None
- approach_alignment: 0.729
- goal_progress: 0.822
- terminal_score: 0.822
- phase_score: 0.326
- phase_breakdown.push_to_goal_score: 0.207
- phase_breakdown.reach_object_score: 0.603

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.525
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.822
- **Median Q (composite search score)**: 0.231
- **K-run variance**: 0.0043
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.294


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `f21cc79f03d9e871b86947069440973ee7e2ef557ebaac0b26b4f6cbdabf5bb1`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec03d65db90cc6b4602194a1eefa4c3104517a971e566e099fb50a3df7102251`; realized-scene SHA-256: `258b33ff0697721ed1ba4810cf28d81707440dffd73b12c632f307c6591915c0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.50142,0.05406,0.025]}],"axes":[{"name":"push_direction","value":[-0.00142,-0.20406,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.50142,0.05406,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76027,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.behind_distance":0.07847,"approach_object.approach_z_offset":0.04156,"push_to_goal.push_distance":0.11537,"push_to_goal.push_speed":0.04613},"optimized_scores":{"best_composite_score":0.11156,"best_fitness_score":0.37156,"best_task_score":0.57689},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.50098,0.07941,0.04977],"force_p95":89.66346,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":95.45541,"mean_force":47.24464,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.49719,0.09047,0.05037]},{"body_a":"world","body_b":"push_box","contact_count":727.0,"contact_point_centroid":[0.5015,0.05478,-3e-05],"force_p95":0.32007,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.76214,"mean_force":0.77453,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.49725,0.08009,0.05848]},{"body_a":"attachment","body_b":"push_box","contact_count":136.0,"contact_point_centroid":[0.49633,0.02791,0.04043],"force_p95":40.94158,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.54754,"mean_force":12.87079,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.49411,0.03944,0.04084]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49522,0.07878,0.02771],"force_p95":32.23916,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.86407,"mean_force":17.61501,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.4952,0.09054,0.02765]},{"body_a":"world","body_b":"push_box","contact_count":799.0,"contact_point_centroid":[0.50883,-0.05287,-0.00019],"force_p95":18.89205,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.68163,"mean_force":2.57195,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.49556,-0.05392,0.06987]},{"body_a":"world","body_b":"push_box","contact_count":276.0,"contact_point_centroid":[0.50157,0.05405,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.28519,"mean_force":0.3657,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49581,0.10451,0.0295]},{"body_a":"world","body_b":"push_box","contact_count":1712.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49857,0.02354,0.19382]}],"total_contact_groups":7},"final_pose_error":0.02961,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51001,-0.06424,0.02499],"final_tcp_position":[0.49677,-0.12371,0.09177],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":95.45541,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":428.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1712.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.49835,0.0483,0.08543],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06079,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":187.0,"n_steps_budget":660.0,"object_pos_end":[0.50157,0.05404,0.02497],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20404,"object_to_goal_dist_start":0.20406,"object_z_max":0.02528,"peak_contact_force":0.24522,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":735.0,"raw_peak_contact_force":95.45541,"tcp_end":[0.49793,0.11481,0.0325],"tcp_start":[0.49835,0.0483,0.08543],"tcp_to_object_dist_end":0.06135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":70.0,"n_steps_budget":1000.0,"object_pos_end":[0.50159,0.054,0.02502],"object_pos_start":[0.50157,0.05404,0.02497],"object_to_goal_dist_end":0.20401,"object_to_goal_dist_start":0.20404,"object_z_max":0.02502,"peak_contact_force":2.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":278.0,"raw_peak_contact_force":33.86407,"subtask_id":"push_to_goal","tcp_end":[0.49516,0.09003,0.02758],"tcp_start":[0.4952,0.09034,0.02764],"tcp_to_object_dist_end":0.03669,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.51001,-0.06424,0.02499],"object_pos_start":[0.50162,0.0539,0.02501],"object_to_goal_dist_end":0.08634,"object_to_goal_dist_start":0.20391,"object_z_max":0.03529,"peak_contact_force":0.24523,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":935.0,"raw_peak_contact_force":49.54754,"tcp_end":[0.49677,-0.12371,0.09177],"tcp_start":[0.49516,0.09003,0.02758],"tcp_to_object_dist_end":0.0904,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `060d405a872aae8d4597ed6284dedb60e9c99f80071c0520b1a8a2986f3c114d`; realized-scene SHA-256: `8c36a5f9300ba3a57ccc09620ec8ba0a5276276ed83fb4303679e150911bfa14`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.47139,-0.02418,0.025]}],"axes":[{"name":"push_direction","value":[0.02861,-0.12582,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.47139,-0.02418,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65972,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.behind_distance":0.0995,"approach_object.approach_z_offset":0.05173,"push_to_goal.push_distance":0.15729,"push_to_goal.push_speed":0.04874},"optimized_scores":{"best_composite_score":0.23101,"best_fitness_score":0.49101,"best_task_score":0.77832},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.46302,-0.00705,0.04308],"force_p95":27.22462,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.39036,"mean_force":3.96184,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45925,0.00465,0.02819]},{"body_a":"attachment","body_b":"push_box","contact_count":78.0,"contact_point_centroid":[0.47274,-0.04671,0.04512],"force_p95":22.85621,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.88586,"mean_force":7.31999,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.46782,-0.03562,0.04065]},{"body_a":"world","body_b":"push_box","contact_count":539.0,"contact_point_centroid":[0.47209,-0.02655,-1e-05],"force_p95":1.57205,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.75996,"mean_force":0.55717,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45338,0.03264,0.03028]},{"body_a":"world","body_b":"push_box","contact_count":352.0,"contact_point_centroid":[0.49936,-0.09694,-5e-05],"force_p95":14.12488,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.92282,"mean_force":2.19386,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.4786,-0.07824,0.06252]},{"body_a":"world","body_b":"push_box","contact_count":1584.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48561,-0.01047,0.1994]},{"body_a":"world","body_b":"push_box","contact_count":852.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.4603,0.01554,0.06458]}],"total_contact_groups":6},"final_pose_error":0.0297,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51057,-0.12345,0.02374],"final_tcp_position":[0.49126,-0.12718,0.08812],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":30.39036,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47164,-0.02155,0.09619],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07125,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":213.0,"n_steps_budget":780.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":852.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.45024,0.05545,0.03394],"tcp_start":[0.47164,-0.02155,0.09619],"tcp_to_object_dist_end":0.08287,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":176.0,"n_steps_budget":1000.0,"object_pos_end":[0.47802,-0.04231,0.0252],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.10991,"object_to_goal_dist_start":0.12903,"object_z_max":0.02571,"peak_contact_force":8.06072,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":578.0,"raw_peak_contact_force":30.39036,"subtask_id":"push_to_goal","tcp_end":[0.46198,-0.00691,0.02763],"tcp_start":[0.46191,-0.00666,0.02764],"tcp_to_object_dist_end":0.03895,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":254.0,"n_steps_budget":1000.0,"object_pos_end":[0.51057,-0.12345,0.02374],"object_pos_start":[0.47813,-0.04256,0.02529],"object_to_goal_dist_end":0.0286,"object_to_goal_dist_start":0.10964,"object_z_max":0.03534,"peak_contact_force":1.90009,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":430.0,"raw_peak_contact_force":25.88586,"tcp_end":[0.49126,-0.12718,0.08812],"tcp_start":[0.46198,-0.00691,0.02763],"tcp_to_object_dist_end":0.06732,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `c4af277909bfbef2010e50829d2192ea184fe34d7420833f45dd73455a81c9b6`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.45028,-0.03158,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64234,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.behind_distance":0.07383,"approach_object.approach_z_offset":0.05588,"push_to_goal.push_distance":0.17773,"push_to_goal.push_speed":0.03287},"optimized_scores":{"best_composite_score":0.26452,"best_fitness_score":0.52452,"best_task_score":0.82243},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":50.0,"contact_point_centroid":[0.43927,-0.01871,0.04518],"force_p95":27.42086,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.08412,"mean_force":4.66089,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.43569,-0.00695,0.033]},{"body_a":"attachment","body_b":"push_box","contact_count":68.0,"contact_point_centroid":[0.45617,-0.05841,0.04754],"force_p95":26.53626,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.37362,"mean_force":8.94614,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.45157,-0.04724,0.04419]},{"body_a":"world","body_b":"push_box","contact_count":347.0,"contact_point_centroid":[0.48615,-0.10357,-3e-05],"force_p95":13.38268,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.50173,"mean_force":2.3188,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.46699,-0.08217,0.06291]},{"body_a":"world","body_b":"push_box","contact_count":327.0,"contact_point_centroid":[0.45344,-0.03699,-3e-05],"force_p95":5.51366,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.3371,"mean_force":1.03304,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.42993,0.00828,0.03475]},{"body_a":"world","body_b":"push_box","contact_count":1584.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47644,-0.0137,0.20113]},{"body_a":"world","body_b":"push_box","contact_count":684.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.43906,-0.00414,0.06895]}],"total_contact_groups":6},"final_pose_error":0.02992,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49647,-0.12764,0.02775],"final_tcp_position":[0.48776,-0.12844,0.08825],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":30.08412,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":396.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1584.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.45283,-0.02815,0.09994],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07507,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":171.0,"n_steps_budget":660.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":684.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.42575,0.02224,0.0379],"tcp_start":[0.45283,-0.02815,0.09994],"tcp_to_object_dist_end":0.06054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":137.0,"n_steps_budget":1000.0,"object_pos_end":[0.46121,-0.05586,0.02481],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.10182,"object_to_goal_dist_start":0.12843,"object_z_max":0.0259,"peak_contact_force":16.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":377.0,"raw_peak_contact_force":30.08412,"subtask_id":"push_to_goal","tcp_end":[0.4415,-0.02137,0.03179],"tcp_start":[0.44152,-0.02116,0.03182],"tcp_to_object_dist_end":0.04033,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":243.0,"n_steps_budget":990.0,"object_pos_end":[0.49647,-0.12764,0.02775],"object_pos_start":[0.4613,-0.05609,0.02491],"object_to_goal_dist_end":0.02281,"object_to_goal_dist_start":0.10157,"object_z_max":0.03533,"peak_contact_force":0.61718,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":415.0,"raw_peak_contact_force":29.37362,"tcp_end":[0.48776,-0.12844,0.08825],"tcp_start":[0.4415,-0.02137,0.03179],"tcp_to_object_dist_end":0.06113,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```