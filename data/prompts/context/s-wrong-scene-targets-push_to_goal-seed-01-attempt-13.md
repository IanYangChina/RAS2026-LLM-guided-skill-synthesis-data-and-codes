## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0020 | 0.74 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4073 | 0.66 | ❌ rejected |
| 11 | approach → align → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1419 | 0.44 | ❌ rejected |
| 10 | approach → align → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0457 | 0.66 | ❌ rejected |
| 9 | approach → align → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3866 | 0.81 | ✅ accepted |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.806, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=-0.002) — your mutation base

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
  generator: arc_cartesian
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
    arc_height:
      type: scalar
      range:
      - 0.05
      - 0.15
      default: 0.1
      binds_to:
      - path: generator.arc_height
        mode: replace
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
    force_guard_threshold:
      type: scalar
      range:
      - 30.0
      - 50.0
      default: 40.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
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
      - 0.04
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: retry
  retries:
    max_attempts: 2
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
    - arc_height: status=consumed; consumers=generator.arc_height (replace)
    - behind_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_guard_threshold: status=consumed; consumers=guards.force_guard.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=40.0
  - retries: max_attempts=2, strategy=offset_target, offset=[-0.01, 0.0, 0.0]
- **retrieve** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=push_box, offset=[0.0, 0.0, 0.08], tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.002
- **task_score** (E): 0.738
- **fitness_score**: 0.338  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.340

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1921 |
| align_behind | 1.00 | 1.00 | 0.0565 |
| descend_behind | 1.00 | 1.00 | 0.0615 |
| push_to_goal | 0.00 | 1.00 | 0.0002 |
| retrieve | 1.00 | 1.00 | 0.1772 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.475, -0.000, 0.114) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_behind | align | 1.00 / step_budget | (0.475, -0.000, 0.114)→(0.463, 0.051, 0.104) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_behind | descend | 1.00 / step_budget | (0.463, 0.051, 0.104)→(0.459, 0.062, 0.044) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 0.00 / guard_failure | (0.462, 0.036, 0.031)→(0.462, 0.036, 0.031) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 3.000 | 1.528 | 37.346 |
| retrieve | retract | 1.00 / step_budget | (0.462, 0.036, 0.031)→(0.492, -0.126, 0.091) | (0.474, -0.001, 0.025)→(0.501, -0.109, 0.024) | 0.154→0.042 | 1.00 / 2.667 | 0.819 | 43.143 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.798
- lateral_force_integral: None
- approach_alignment: 0.729
- goal_progress: 0.797
- terminal_score: 0.797
- phase_score: 0.074
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.245

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.363
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.797
- **Median Q (composite search score)**: 0.014
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.281


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.6612,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.behind_distance":0.08899,"approach_object.approach_z_offset":0.0519,"descend_behind.descend_behind_distance":0.08228,"push_to_goal.push_distance":0.21063,"push_to_goal.push_speed":0.03345},"optimized_scores":{"best_composite_score":-0.04324,"best_fitness_score":0.29676,"best_task_score":0.65798},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":122.0,"contact_point_centroid":[0.49745,0.02313,0.04547],"force_p95":45.93169,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.03128,"mean_force":14.35684,"phase_index":4.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.49507,0.03464,0.04279]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49648,0.07878,0.02851],"force_p95":33.97372,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.59609,"mean_force":12.98947,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49644,0.09057,0.02842]},{"body_a":"world","body_b":"push_box","contact_count":686.0,"contact_point_centroid":[0.50774,-0.06073,-0.00023],"force_p95":19.83856,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.11585,"mean_force":2.99927,"phase_index":4.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.496,-0.05167,0.0694]},{"body_a":"world","body_b":"push_box","contact_count":446.0,"contact_point_centroid":[0.50142,0.05394,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.2674,"mean_force":0.32953,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.496,0.11314,0.03517]},{"body_a":"world","body_b":"push_box","contact_count":1636.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49861,0.0234,0.19896]},{"body_a":"world","body_b":"push_box","contact_count":804.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.4972,0.0857,0.09526]},{"body_a":"world","body_b":"push_box","contact_count":452.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.49785,0.12845,0.0725]}],"total_contact_groups":7},"final_pose_error":0.0295,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51049,-0.081,0.02497],"final_tcp_position":[0.4969,-0.12377,0.09185],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":56.03128,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":409.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1636.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.4984,0.04807,0.09566],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07099,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":201.0,"n_steps_budget":630.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":804.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.49827,0.12487,0.09837],"tcp_start":[0.4984,0.04807,0.09566],"tcp_to_object_dist_end":0.10202,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":113.0,"n_steps_budget":600.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":452.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.49792,0.13205,0.04372],"tcp_start":[0.49827,0.12487,0.09837],"tcp_to_object_dist_end":0.08029,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":113.0,"n_steps_budget":1000.0,"object_pos_end":[0.50144,0.05401,0.02502],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20402,"object_to_goal_dist_start":0.20406,"object_z_max":0.02502,"peak_contact_force":0.58316,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":449.0,"raw_peak_contact_force":37.59609,"subtask_id":"push_to_goal","tcp_end":[0.49641,0.09,0.02822],"tcp_start":[0.49642,0.09024,0.02832],"tcp_to_object_dist_end":0.03648,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.51049,-0.081,0.02497],"object_pos_start":[0.50145,0.05385,0.025],"object_to_goal_dist_end":0.06979,"object_to_goal_dist_start":0.20385,"object_z_max":0.03533,"peak_contact_force":0.2447,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":808.0,"raw_peak_contact_force":56.03128,"tcp_end":[0.4969,-0.12377,0.09185],"tcp_start":[0.49641,0.09,0.02822],"tcp_to_object_dist_end":0.08055,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56667,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.behind_distance":0.05829,"approach_object.approach_z_offset":0.06372,"descend_behind.descend_behind_distance":0.05999,"push_to_goal.push_distance":0.13444,"push_to_goal.push_speed":0.03275},"optimized_scores":{"best_composite_score":0.01414,"best_fitness_score":0.35414,"best_task_score":0.75714},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.45823,0.00061,0.03405],"force_p95":35.85811,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.64866,"mean_force":13.97397,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45821,0.01249,0.03404]},{"body_a":"attachment","body_b":"push_box","contact_count":90.0,"contact_point_centroid":[0.46895,-0.03432,0.04739],"force_p95":31.5718,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.27208,"mean_force":9.73843,"phase_index":4.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.46552,-0.02314,0.04673]},{"body_a":"world","body_b":"push_box","contact_count":374.0,"contact_point_centroid":[0.49425,-0.09133,-0.00016],"force_p95":15.87768,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.27125,"mean_force":2.94877,"phase_index":4.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.47708,-0.06948,0.06601]},{"body_a":"world","body_b":"push_box","contact_count":217.0,"contact_point_centroid":[0.47128,-0.0243,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.14853,"mean_force":0.4296,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45612,0.02191,0.03848]},{"body_a":"world","body_b":"push_box","contact_count":1492.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48578,-0.01038,0.20547]},{"body_a":"world","body_b":"push_box","contact_count":368.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.46582,-0.00573,0.10431]},{"body_a":"world","body_b":"push_box","contact_count":504.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.45818,0.02036,0.07412]}],"total_contact_groups":7},"final_pose_error":0.02956,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50531,-0.11914,0.02374],"final_tcp_position":[0.4914,-0.12606,0.08994],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":39.64866,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":373.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1492.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47191,-0.02138,0.10832],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":92.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":368.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.46064,0.013,0.10244],"tcp_start":[0.47191,-0.02138,0.10832],"tcp_to_object_dist_end":0.08658,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":126.0,"n_steps_budget":600.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":504.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.456,0.02809,0.04348],"tcp_start":[0.46064,0.013,0.10244],"tcp_to_object_dist_end":0.05754,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":56.0,"n_steps_budget":1000.0,"object_pos_end":[0.47142,-0.02423,0.02502],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12898,"object_to_goal_dist_start":0.12903,"object_z_max":0.02502,"peak_contact_force":2.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":220.0,"raw_peak_contact_force":39.64866,"subtask_id":"push_to_goal","tcp_end":[0.45819,0.01202,0.03384],"tcp_start":[0.45824,0.0122,0.03393],"tcp_to_object_dist_end":0.03958,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":277.0,"n_steps_budget":1000.0,"object_pos_end":[0.50531,-0.11914,0.02374],"object_pos_start":[0.47136,-0.02441,0.02501],"object_to_goal_dist_end":0.03134,"object_to_goal_dist_start":0.12881,"object_z_max":0.03534,"peak_contact_force":0.59189,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":464.0,"raw_peak_contact_force":33.27208,"tcp_end":[0.4914,-0.12606,0.08994],"tcp_start":[0.45819,0.01202,0.03384],"tcp_to_object_dist_end":0.068,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2659,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.behind_distance":0.0689,"approach_object.approach_z_offset":0.09541,"descend_behind.descend_behind_distance":0.06642,"push_to_goal.push_distance":0.15014,"push_to_goal.push_speed":0.0175},"optimized_scores":{"best_composite_score":0.02325,"best_fitness_score":0.36325,"best_task_score":0.79741},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":78.0,"contact_point_centroid":[0.44737,-0.03997,0.04809],"force_p95":32.74576,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.12612,"mean_force":9.21171,"phase_index":4.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.44386,-0.02848,0.04369]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.43246,-0.0068,0.03695],"force_p95":31.44792,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.79458,"mean_force":12.04085,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.43092,0.00506,0.03034]},{"body_a":"world","body_b":"push_box","contact_count":425.0,"contact_point_centroid":[0.47741,-0.09224,-9e-05],"force_p95":13.43748,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.89628,"mean_force":2.24394,"phase_index":4.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.46232,-0.0707,0.06306]},{"body_a":"world","body_b":"push_box","contact_count":333.0,"contact_point_centroid":[0.4502,-0.03166,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.77156,"mean_force":0.3497,"phase_index":3.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.42553,0.01739,0.03732]},{"body_a":"world","body_b":"push_box","contact_count":1292.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47733,-0.01326,0.22097]},{"body_a":"world","body_b":"push_box","contact_count":476.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.44215,-0.00785,0.12499]},{"body_a":"world","body_b":"push_box","contact_count":564.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"descend_behind","phase_type":"descend","tcp_position_centroid":[0.42647,0.02004,0.07878]}],"total_contact_groups":7},"final_pose_error":0.02965,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48823,-0.12684,0.02365],"final_tcp_position":[0.48762,-0.12782,0.08971],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":40.12612,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":323.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1292.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.45415,-0.02746,0.13915],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11431,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":119.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":476.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.43006,0.01463,0.11143],"tcp_start":[0.45415,-0.02746,0.13915],"tcp_to_object_dist_end":0.10009,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":141.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_behind","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":564.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.42346,0.02563,0.04418],"tcp_start":[0.43006,0.01463,0.11143],"tcp_to_object_dist_end":0.06603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":85.0,"n_steps_budget":1000.0,"object_pos_end":[0.4503,-0.03163,0.02502],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12838,"object_to_goal_dist_start":0.12843,"object_z_max":0.02502,"peak_contact_force":2.0,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":336.0,"raw_peak_contact_force":34.79458,"subtask_id":"push_to_goal","tcp_end":[0.4308,0.00468,0.03011],"tcp_start":[0.4309,0.00483,0.03021],"tcp_to_object_dist_end":0.04152,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":290.0,"n_steps_budget":1000.0,"object_pos_end":[0.48823,-0.12684,0.02365],"object_pos_start":[0.45028,-0.03177,0.02499],"object_to_goal_dist_end":0.02602,"object_to_goal_dist_start":0.12826,"object_z_max":0.03534,"peak_contact_force":1.61967,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":503.0,"raw_peak_contact_force":40.12612,"tcp_end":[0.48762,-0.12782,0.08971],"tcp_start":[0.4308,0.00468,0.03011],"tcp_to_object_dist_end":0.06608,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```