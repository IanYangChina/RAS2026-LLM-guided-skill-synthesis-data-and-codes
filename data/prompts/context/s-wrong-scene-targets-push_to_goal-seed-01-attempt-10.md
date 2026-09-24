## Search State

- **Seed**: 1
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → align → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0457 | 0.66 | ❌ rejected |
| 9 | approach → align → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.3866 | 0.81 | ✅ accepted |
| 8 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 4 | 0.2024 | 0.73 | ✅ accepted |
| 7 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.2042 | 0.54 | ❌ rejected |
| 6 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.2425 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.66 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.046) — your mutation base

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

- **Composite score**: 0.046
- **task_score** (E): 0.658
- **fitness_score**: 0.406  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.2200 |
| align_behind | 1.00 | 1.00 | 0.0848 |
| push_to_goal | 0.00 | 1.00 | 0.0002 |
| retrieve | 1.00 | 1.00 | 0.1746 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.474, -0.001, 0.086) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_behind | align | 1.00 / step_budget | (0.474, -0.001, 0.086)→(0.459, 0.069, 0.044) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 0.00 / guard_failure | (0.461, 0.035, 0.038)→(0.461, 0.035, 0.037) | (0.474, -0.001, 0.025)→(0.474, -0.001, 0.025) | 0.154→0.154 | 1.00 / 3.667 | 4.362 | 31.734 |
| retrieve | retract | 1.00 / step_budget | (0.461, 0.035, 0.037)→(0.492, -0.125, 0.091) | (0.474, -0.001, 0.025)→(0.495, -0.096, 0.025) | 0.154→0.055 | 1.00 / 4.000 | 0.408 | 33.740 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.700
- lateral_force_integral: None
- approach_alignment: 0.746
- goal_progress: 0.699
- terminal_score: 0.699
- phase_score: 0.246
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.820

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.428
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.722
- **Median Q (composite search score)**: 0.064
- **K-run variance**: 0.0008
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.333


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70667,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.arc_height":0.06255,"align_behind.behind_distance":0.0771,"approach_object.approach_z_offset":0.04001,"push_to_goal.force_guard_threshold":21.70307,"push_to_goal.push_distance":0.22897,"push_to_goal.push_speed":0.02453},"optimized_scores":{"best_composite_score":0.00592,"best_fitness_score":0.36592,"best_task_score":0.55286},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":100.0,"contact_point_centroid":[0.49638,0.03326,0.04674],"force_p95":35.89227,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.32817,"mean_force":12.65551,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.49431,0.04482,0.04713]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49553,0.07862,0.03758],"force_p95":30.245,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.56996,"mean_force":11.54581,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49548,0.09029,0.03753]},{"body_a":"world","body_b":"push_box","contact_count":789.0,"contact_point_centroid":[0.50609,-0.04699,-0.00017],"force_p95":14.97085,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.17639,"mean_force":2.00068,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.49559,-0.05125,0.07293]},{"body_a":"world","body_b":"push_box","contact_count":406.0,"contact_point_centroid":[0.50154,0.05405,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.30475,"mean_force":0.3558,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.49605,0.11083,0.03971]},{"body_a":"world","body_b":"push_box","contact_count":1724.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.49856,0.02357,0.19301]},{"body_a":"world","body_b":"push_box","contact_count":996.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.49751,0.09212,0.0791]}],"total_contact_groups":6},"final_pose_error":0.02971,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50741,-0.05906,0.02499],"final_tcp_position":[0.49679,-0.12317,0.09265],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":37.32817,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":431.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1724.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.49833,0.04835,0.08379],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05916,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":660.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":996.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49873,0.12894,0.0445],"tcp_start":[0.49833,0.04835,0.08379],"tcp_to_object_dist_end":0.07743,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":103.0,"n_steps_budget":1000.0,"object_pos_end":[0.50144,0.05401,0.02502],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20401,"object_to_goal_dist_start":0.20406,"object_z_max":0.02502,"peak_contact_force":11.40355,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":410.0,"raw_peak_contact_force":33.56996,"subtask_id":"push_to_goal","tcp_end":[0.49543,0.08969,0.03739],"tcp_start":[0.49546,0.08986,0.03745],"tcp_to_object_dist_end":0.03824,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.50741,-0.05906,0.02499],"object_pos_start":[0.50148,0.05376,0.02494],"object_to_goal_dist_end":0.09124,"object_to_goal_dist_start":0.20377,"object_z_max":0.03533,"peak_contact_force":0.24522,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":889.0,"raw_peak_contact_force":37.32817,"tcp_end":[0.49679,-0.12317,0.09265],"tcp_start":[0.49543,0.08969,0.03739],"tcp_to_object_dist_end":0.09382,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63514,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.arc_height":0.11621,"align_behind.behind_distance":0.09938,"approach_object.approach_z_offset":0.04008,"push_to_goal.force_guard_threshold":16.50154,"push_to_goal.push_distance":0.17174,"push_to_goal.push_speed":0.02583},"optimized_scores":{"best_composite_score":0.06751,"best_fitness_score":0.42751,"best_task_score":0.69937},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.45769,0.00038,0.03478],"force_p95":27.88103,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.65119,"mean_force":8.59766,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45766,0.01207,0.03477]},{"body_a":"attachment","body_b":"push_box","contact_count":95.0,"contact_point_centroid":[0.46779,-0.03367,0.04886],"force_p95":28.16226,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.07293,"mean_force":9.16406,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.46484,-0.02223,0.04691]},{"body_a":"world","body_b":"push_box","contact_count":456.0,"contact_point_centroid":[0.48965,-0.09449,-0.00024],"force_p95":13.09023,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.59968,"mean_force":2.41711,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.47812,-0.07484,0.06856]},{"body_a":"world","body_b":"push_box","contact_count":575.0,"contact_point_centroid":[0.47135,-0.02431,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.25586,"mean_force":0.30396,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45194,0.03897,0.03732]},{"body_a":"world","body_b":"push_box","contact_count":1672.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48546,-0.01055,0.19355]},{"body_a":"world","body_b":"push_box","contact_count":916.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.45841,0.02286,0.07296]}],"total_contact_groups":6},"final_pose_error":0.02951,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49349,-0.11176,0.02475],"final_tcp_position":[0.49131,-0.12609,0.09004],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":32.65119,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1672.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47143,-0.02167,0.08461],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.05967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":229.0,"n_steps_budget":720.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":916.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44879,0.06295,0.04201],"tcp_start":[0.47143,-0.02167,0.08461],"tcp_to_object_dist_end":0.09161,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":146.0,"n_steps_budget":1000.0,"object_pos_end":[0.47142,-0.02423,0.02503],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12897,"object_to_goal_dist_start":0.12903,"object_z_max":0.02503,"peak_contact_force":1.12507,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":579.0,"raw_peak_contact_force":32.65119,"subtask_id":"push_to_goal","tcp_end":[0.45766,0.01157,0.03467],"tcp_start":[0.4577,0.01171,0.03472],"tcp_to_object_dist_end":0.03955,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":276.0,"n_steps_budget":1000.0,"object_pos_end":[0.49349,-0.11176,0.02475],"object_pos_start":[0.47144,-0.02443,0.02501],"object_to_goal_dist_end":0.03879,"object_to_goal_dist_start":0.12878,"object_z_max":0.03534,"peak_contact_force":0.24144,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":551.0,"raw_peak_contact_force":31.07293,"tcp_end":[0.49131,-0.12609,0.09004],"tcp_start":[0.45766,0.01157,0.03467],"tcp_to_object_dist_end":0.06688,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71429,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.arc_height":0.09369,"align_behind.behind_distance":0.05747,"approach_object.approach_z_offset":0.04446,"push_to_goal.force_guard_threshold":24.66509,"push_to_goal.push_distance":0.20079,"push_to_goal.push_speed":0.02017},"optimized_scores":{"best_composite_score":0.0637,"best_fitness_score":0.4237,"best_task_score":0.72239},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":76.0,"contact_point_centroid":[0.44732,-0.04081,0.05256],"force_p95":29.09208,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.81947,"mean_force":10.58741,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.4443,-0.02938,0.05202]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.43139,-0.00698,0.04278],"force_p95":24.76342,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.98123,"mean_force":7.51427,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.43084,0.00479,0.04042]},{"body_a":"world","body_b":"push_box","contact_count":402.0,"contact_point_centroid":[0.47678,-0.09469,-0.00018],"force_p95":12.80751,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.44888,"mean_force":2.60004,"phase_index":3.0,"phase_name":"retrieve","phase_type":"retract","tcp_position_centroid":[0.46328,-0.07286,0.06906]},{"body_a":"world","body_b":"push_box","contact_count":160.0,"contact_point_centroid":[0.45028,-0.03221,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.13321,"mean_force":0.43032,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.42871,0.01132,0.04159]},{"body_a":"world","body_b":"push_box","contact_count":1664.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.47628,-0.01377,0.1956]},{"body_a":"world","body_b":"push_box","contact_count":580.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.43858,-0.00427,0.07094]}],"total_contact_groups":6},"final_pose_error":0.02964,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48458,-0.11787,0.02387],"final_tcp_position":[0.48736,-0.12721,0.09087],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":32.81947,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1664.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.45261,-0.02826,0.08897],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06411,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":145.0,"n_steps_budget":600.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":580.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.42846,0.01551,0.04408],"tcp_start":[0.45261,-0.02826,0.08897],"tcp_to_object_dist_end":0.0553,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":42.0,"n_steps_budget":1000.0,"object_pos_end":[0.45029,-0.03164,0.02503],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12837,"object_to_goal_dist_start":0.12843,"object_z_max":0.02504,"peak_contact_force":0.5587,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":164.0,"raw_peak_contact_force":28.98123,"subtask_id":"push_to_goal","tcp_end":[0.43073,0.00432,0.04026],"tcp_start":[0.4308,0.00445,0.04033],"tcp_to_object_dist_end":0.04368,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.48458,-0.11787,0.02387],"object_pos_start":[0.45026,-0.03183,0.02503],"object_to_goal_dist_end":0.03565,"object_to_goal_dist_start":0.12821,"object_z_max":0.03534,"peak_contact_force":0.7367,"phase_name":"retrieve","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":478.0,"raw_peak_contact_force":32.81947,"tcp_end":[0.48736,-0.12721,0.09087],"tcp_start":[0.43073,0.00432,0.04026],"tcp_to_object_dist_end":0.06771,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```