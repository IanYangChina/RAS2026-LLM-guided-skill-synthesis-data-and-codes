## Search State

- **Seed**: 1
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.1675 | 0.01 | ❌ rejected |
| 13 | approach → align → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0020 | 0.74 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.4073 | 0.66 | ❌ rejected |
| 11 | approach → align → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1419 | 0.44 | ❌ rejected |
| 10 | approach → align → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0457 | 0.66 | ❌ rejected |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.168) — your mutation base

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

- **Composite score**: -0.168
- **task_score** (E): 0.011
- **fitness_score**: 0.092  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.2036 |
| align_behind | 1.00 | 1.00 | 0.0610 |
| push_to_goal | 0.00 | 1.00 | 0.0001 |
| retrieve | 1.00 | 1.00 | 0.1201 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.474, -0.000, 0.102) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_behind | align | 1.00 / step_budget | (0.474, -0.000, 0.102)→(0.484, -0.016, 0.044) | (0.474, -0.001, 0.025)→(0.478, -0.002, 0.025) | 0.154→0.151 | 1.00 / 3.667 | 268.754 | 288.945 |
| push_to_goal | push | 0.00 / guard_failure | (0.485, -0.016, 0.045)→(0.485, -0.016, 0.045) | (0.478, -0.002, 0.025)→(0.478, -0.002, 0.025) | 0.151→0.151 | 1.00 / 3.667 | 144.726 | 144.726 |
| retrieve | retract | 1.00 / step_budget | (0.485, -0.016, 0.045)→(0.494, -0.126, 0.089) | (0.478, -0.002, 0.025)→(0.488, 0.003, 0.025) | 0.151→0.154 | 1.00 / 4.000 | 0.243 | 149.092 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.230
- lateral_force_integral: None
- approach_alignment: 0.730
- goal_progress: 0.034
- terminal_score: 0.034
- phase_score: 0.143
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.478

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.100
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.034
- **Median Q (composite search score)**: -0.170
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at lower bound**: align_behind.behind_distance
- **Final σ (mean)**: 0.503


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80702,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.behind_distance":0.02024,"approach_object.approach_z_offset":0.04887,"push_to_goal.push_distance":0.19493,"push_to_goal.push_speed":0.01945},"optimized_scores":{"best_composite_score":-0.17025,"best_fitness_score":0.08975,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":44.0,"contact_point_centroid":[0.51299,0.04052,0.04679],"force_p95":287.19274,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":287.41889,"mean_force":249.99292,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.50136,0.03869,0.04718]},{"body_a":"world","body_b":"push_box","contact_count":466.0,"contact_point_centroid":[0.50388,0.0518,-0.00016],"force_p95":183.58471,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":203.43727,"mean_force":24.02792,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.4985,0.04305,0.06556]},{"body_a":"attachment","body_b":"push_box","contact_count":54.0,"contact_point_centroid":[0.51477,0.03458,0.04973],"force_p95":106.73569,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":147.95514,"mean_force":59.32163,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.50744,0.02624,0.04973]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.51807,0.04093,0.04537],"force_p95":141.63709,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":143.01574,"mean_force":118.72808,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5067,0.03737,0.04492]},{"body_a":"world","body_b":"push_box","contact_count":652.0,"contact_point_centroid":[0.50346,0.0386,-0.00026],"force_p95":42.04687,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.64321,"mean_force":5.368,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.50206,-0.04858,0.06953]},{"body_a":"world","body_b":"push_box","contact_count":15.0,"contact_point_centroid":[0.51129,0.04567,-0.00084],"force_p95":95.95987,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.04094,"mean_force":40.03158,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5067,0.03737,0.04492]},{"body_a":"world","body_b":"push_box","contact_count":1660.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49859,0.02348,0.19731]}],"total_contact_groups":7},"final_pose_error":0.02987,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50305,0.05456,0.02484],"final_tcp_position":[0.49828,-0.12329,0.09172],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":287.41889,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":415.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1660.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.49837,0.04823,0.09227],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0676,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":127.0,"n_steps_budget":600.0,"object_pos_end":[0.50428,0.05287,0.02402],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20292,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":263.60713,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":510.0,"raw_peak_contact_force":287.41889,"subtask_id":"reach_object","tcp_end":[0.50643,0.0374,0.04484],"tcp_start":[0.49837,0.04823,0.09227],"tcp_to_object_dist_end":0.02603,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.50419,0.05286,0.02407],"object_pos_start":[0.50428,0.05287,0.02402],"object_to_goal_dist_end":0.20291,"object_to_goal_dist_start":0.20292,"object_z_max":0.02409,"peak_contact_force":143.01574,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":20.0,"raw_peak_contact_force":143.01574,"subtask_id":"push_to_goal","tcp_end":[0.507,0.03734,0.04512],"tcp_start":[0.50692,0.03734,0.04504],"tcp_to_object_dist_end":0.02631,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":289.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.05456,0.02484],"object_pos_start":[0.50413,0.05287,0.0241],"object_to_goal_dist_end":0.20458,"object_to_goal_dist_start":0.20292,"object_z_max":0.03523,"peak_contact_force":0.24223,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":706.0,"raw_peak_contact_force":147.95514,"tcp_end":[0.49828,-0.12329,0.09172],"tcp_start":[0.507,0.03734,0.04512],"tcp_to_object_dist_end":0.19007,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78723,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.behind_distance":0.02001,"approach_object.approach_z_offset":0.08257,"push_to_goal.push_distance":0.10088,"push_to_goal.push_speed":0.03973},"optimized_scores":{"best_composite_score":-0.17207,"best_fitness_score":0.08793,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":40.0,"contact_point_centroid":[0.48716,-0.03674,0.04679],"force_p95":288.91199,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":290.22064,"mean_force":251.03787,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.47556,-0.03868,0.04722]},{"body_a":"world","body_b":"push_box","contact_count":737.0,"contact_point_centroid":[0.47281,-0.02553,-8e-05],"force_p95":94.53644,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":222.08612,"mean_force":13.95721,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.47218,-0.03017,0.0832]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49152,-0.03627,0.04501],"force_p95":150.02647,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":151.93742,"mean_force":128.55943,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48041,-0.04065,0.04443]},{"body_a":"attachment","body_b":"push_box","contact_count":45.0,"contact_point_centroid":[0.49009,-0.04031,0.04948],"force_p95":114.83791,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":150.7395,"mean_force":49.03169,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.4825,-0.04861,0.04944]},{"body_a":"world","body_b":"push_box","contact_count":354.0,"contact_point_centroid":[0.4818,-0.03007,-0.00046],"force_p95":66.23527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":116.4313,"mean_force":6.76109,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.48803,-0.09106,0.06966]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.481,-0.03289,-0.00083],"force_p95":100.86565,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":107.50223,"mean_force":43.16464,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48041,-0.04065,0.04443]},{"body_a":"world","body_b":"push_box","contact_count":1348.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48608,-0.0102,0.21508]}],"total_contact_groups":7},"final_pose_error":0.02995,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48133,-0.01885,0.02471],"final_tcp_position":[0.49343,-0.12647,0.08768],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":290.22064,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1348.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47236,-0.02109,0.12729],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10236,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":194.0,"n_steps_budget":660.0,"object_pos_end":[0.47435,-0.02582,0.02421],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.1268,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":275.60447,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":777.0,"raw_peak_contact_force":290.22064,"subtask_id":"reach_object","tcp_end":[0.48019,-0.04059,0.04434],"tcp_start":[0.47236,-0.02109,0.12729],"tcp_to_object_dist_end":0.02564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.47431,-0.02586,0.02423],"object_pos_start":[0.47435,-0.02582,0.02421],"object_to_goal_dist_end":0.12677,"object_to_goal_dist_start":0.1268,"object_z_max":0.02424,"peak_contact_force":151.93742,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":151.93742,"subtask_id":"push_to_goal","tcp_end":[0.48069,-0.04072,0.04462],"tcp_start":[0.4806,-0.0407,0.04453],"tcp_to_object_dist_end":0.02602,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":178.0,"n_steps_budget":810.0,"object_pos_end":[0.48133,-0.01885,0.02471],"object_pos_start":[0.47424,-0.02586,0.02425],"object_to_goal_dist_end":0.13247,"object_to_goal_dist_start":0.12678,"object_z_max":0.03427,"peak_contact_force":0.24344,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":399.0,"raw_peak_contact_force":150.7395,"tcp_end":[0.49343,-0.12647,0.08768],"tcp_start":[0.48069,-0.04072,0.04462],"tcp_to_object_dist_end":0.12527,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80198,"average_solve_count":101.0,"average_success_count":101.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.behind_distance":0.02,"approach_object.approach_z_offset":0.04289,"push_to_goal.push_distance":0.29763,"push_to_goal.push_speed":0.03986},"optimized_scores":{"best_composite_score":-0.16022,"best_fitness_score":0.09978,"best_task_score":0.03422},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":50.0,"contact_point_centroid":[0.46952,-0.03949,0.04666],"force_p95":288.85065,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":289.19575,"mean_force":250.50786,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.45828,-0.04242,0.0469]},{"body_a":"world","body_b":"push_box","contact_count":437.0,"contact_point_centroid":[0.45495,-0.03276,-0.00019],"force_p95":190.31184,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":211.04576,"mean_force":29.00646,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.45377,-0.0357,0.06409]},{"body_a":"attachment","body_b":"push_box","contact_count":48.0,"contact_point_centroid":[0.4744,-0.04262,0.05037],"force_p95":112.43532,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":148.58271,"mean_force":53.54525,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.46956,-0.05324,0.0498]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.47334,-0.03589,0.04567],"force_p95":137.43555,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":139.22534,"mean_force":111.45001,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46577,-0.04529,0.04436]},{"body_a":"world","body_b":"push_box","contact_count":361.0,"contact_point_centroid":[0.47743,-0.03195,-0.00051],"force_p95":73.90485,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.42027,"mean_force":7.6399,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.48147,-0.09747,0.07181]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.47654,-0.03248,-0.00127],"force_p95":85.92316,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.10821,"mean_force":56.10424,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46577,-0.04529,0.04436]},{"body_a":"world","body_b":"push_box","contact_count":1676.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47626,-0.01378,0.19486]}],"total_contact_groups":7},"final_pose_error":0.02978,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47951,-0.02767,0.02491],"final_tcp_position":[0.49036,-0.12767,0.08781],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":289.19575,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":419.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1676.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.45259,-0.02827,0.08747],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":129.0,"n_steps_budget":600.0,"object_pos_end":[0.45517,-0.03396,0.02557],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.1244,"object_to_goal_dist_start":0.12843,"object_z_max":0.02548,"peak_contact_force":267.04975,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":487.0,"raw_peak_contact_force":289.19575,"subtask_id":"reach_object","tcp_end":[0.46549,-0.04523,0.04428],"tcp_start":[0.45259,-0.02827,0.08747],"tcp_to_object_dist_end":0.02416,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.45514,-0.03398,0.02557],"object_pos_start":[0.45517,-0.03396,0.02557],"object_to_goal_dist_end":0.12439,"object_to_goal_dist_start":0.1244,"object_z_max":0.02557,"peak_contact_force":139.22534,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":139.22534,"subtask_id":"push_to_goal","tcp_end":[0.46614,-0.04536,0.04453],"tcp_start":[0.46602,-0.04535,0.04445],"tcp_to_object_dist_end":0.0247,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":180.0,"n_steps_budget":810.0,"object_pos_end":[0.47951,-0.02767,0.02491],"object_pos_start":[0.45508,-0.03397,0.02558],"object_to_goal_dist_end":0.12404,"object_to_goal_dist_start":0.12442,"object_z_max":0.03559,"peak_contact_force":0.24371,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":409.0,"raw_peak_contact_force":148.58271,"tcp_end":[0.49036,-0.12767,0.08781],"tcp_start":[0.46614,-0.04536,0.04453],"tcp_to_object_dist_end":0.11864,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```