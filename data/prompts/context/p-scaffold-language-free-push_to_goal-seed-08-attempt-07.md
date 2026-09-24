## Search State

- **Seed**: 8
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 11 | -0.1877 | 0.00 | ❌ rejected |
| 6 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 9 | -0.3638 | 0.00 | ❌ rejected |
| 5 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2261 | 0.81 | ❌ rejected |
| 4 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.3922 | 0.81 | ❌ rejected |
| 3 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4294 | 0.84 | ✅ accepted |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`
- Frozen object start: [0.4792366731926673, 0.05847322120055107, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.4792366731926673, 0.05847322120055107, 0.025)
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
  frozen_object_start: [0.4792, 0.0585, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.4792366731926673, 0.05847322120055107, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0208, -0.2085, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.838, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.4792366731926673, 0.05847322120055107, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=-0.188) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: push_to_goal
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
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.02
  subtask_id: reach_object
- id: pre_contact_1
  type: align
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
      distance: 0.05
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    pre_push_offset:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
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
    tolerance: 0.01
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
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.03
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_to_goal
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.02]
- **pre_contact_1** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=replace_offset_projection, sign=negative}, tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - pre_push_offset: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=abort, threshold=25.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - retries: max_attempts=0, strategy=repeat

## Design Metrics

- **Composite score**: -0.188
- **task_score** (E): 0.002
- **fitness_score**: 0.089  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_start_pos | 1.00 | 1.00 | 0.1422 |
| descend_to_contact | 1.00 | 1.00 | 0.1337 |
| push_1 | 0.00 | 1.00 | 0.0006 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_start_pos | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.535, 0.039, 0.179) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_to_contact | contact | 1.00 / force_exceeded | (0.535, 0.039, 0.179)→(0.529, 0.025, 0.046) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 5.000 | 40.981 | 0.245 |
| push_1 | push | 0.00 / guard_failure | (0.529, 0.025, 0.046)→(0.529, 0.025, 0.046) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 3.667 | 11.662 | 38.936 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.000
- lateral_force_integral: None
- approach_alignment: 0.349
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.153
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.511

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.092
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.007
- **Median Q (composite search score)**: -0.188
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.312


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8267fcc1127ab3c529e380fe6aea430def9956719b146bd9818eb52355cb895d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `33d626702a3717cebb1eda35e1cb80c1c9d108c246efccd193577b9105813420`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44681,"average_solve_count":94.0,"average_success_count":94.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_start_pos.approach_height":0.09397,"approach_to_start_pos.approach_speed":0.0815,"approach_to_start_pos.pre_push_offset":0.02002,"descend_to_contact.contact_force_threshold":3.45125,"descend_to_contact.descend_speed":0.03763,"descend_to_contact.pre_push_offset":0.0211,"push_1.push_distance":0.35543,"push_1.push_speed":0.04142,"push_1.push_tolerance":0.02919,"retract_1.retract_height":0.15862,"retract_1.retract_speed":0.06159},"optimized_scores":{"best_composite_score":-0.1846,"best_fitness_score":0.09207,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.48479,0.07689,0.04995],"force_p95":37.16346,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.16346,"mean_force":37.16346,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47305,0.07676,0.05241]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":21.73894,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.90703,"mean_force":9.5067,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47305,0.07676,0.05241]},{"body_a":"world","body_b":"push_box","contact_count":2480.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_to_start_pos","phase_type":"approach","tcp_position_centroid":[0.48723,0.03571,0.21318]},{"body_a":"world","body_b":"push_box","contact_count":1820.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"contact","tcp_position_centroid":[0.47314,0.07453,0.08846]}],"total_contact_groups":4},"final_pose_error":0.35543,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47919,0.05847,0.02502],"final_tcp_position":[0.473,0.07676,0.05232],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":45.66562,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":620.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_to_start_pos","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2480.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47576,0.07269,0.12677],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":455.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":45.66562,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1820.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.47305,0.07676,0.05241],"tcp_start":[0.47576,0.07269,0.12677],"tcp_to_object_dist_end":0.03353,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.47919,0.05847,0.02502],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20951,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":2.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":37.16346,"subtask_id":"push_to_goal","tcp_end":[0.473,0.07676,0.05232],"tcp_start":[0.47305,0.07676,0.05241],"tcp_to_object_dist_end":0.03344,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `021f3e69028f16fb65e79b302b37775f7324e143e034cbac30fdb04ffcd99d24`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95172,"average_solve_count":145.0,"average_success_count":145.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_start_pos.approach_height":0.18321,"approach_to_start_pos.approach_speed":0.0591,"approach_to_start_pos.pre_push_offset":0.04077,"descend_to_contact.contact_force_threshold":5.96512,"descend_to_contact.descend_speed":0.02967,"descend_to_contact.pre_push_offset":0.02101,"push_1.push_distance":0.26526,"push_1.push_speed":0.05084,"push_1.push_tolerance":0.01708,"retract_1.retract_height":0.10331,"retract_1.retract_speed":0.0448},"optimized_scores":{"best_composite_score":-0.18842,"best_fitness_score":0.08824,"best_task_score":5e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.5587,-0.00285,0.04991],"force_p95":48.65719,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.65719,"mean_force":48.65719,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54697,-0.00285,0.05236]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":30.96613,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.08542,"mean_force":12.31142,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54697,-0.00285,0.05236]},{"body_a":"world","body_b":"push_box","contact_count":1644.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_to_start_pos","phase_type":"approach","tcp_position_centroid":[0.52336,0.00555,0.25558]},{"body_a":"world","body_b":"push_box","contact_count":3428.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"contact","tcp_position_centroid":[0.5469,0.0042,0.12973]}],"total_contact_groups":4},"final_pose_error":0.26524,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54439,-0.02558,0.025],"final_tcp_position":[0.54693,-0.00286,0.05226],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":60.06732,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_to_start_pos","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1644.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.54929,0.01135,0.21233],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.19101,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":857.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":60.06732,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3428.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.54697,-0.00285,0.05236],"tcp_start":[0.54929,0.01135,0.21233],"tcp_to_object_dist_end":0.03567,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.54439,-0.02558,0.025],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":2.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":48.65719,"subtask_id":"push_to_goal","tcp_end":[0.54693,-0.00286,0.05226],"tcp_start":[0.54697,-0.00285,0.05236],"tcp_to_object_dist_end":0.03557,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `886824c4c8b8334954c1de9b3100fb0acfdd4a04855e7e82a07b72c52723cc86`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.97727,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_start_pos.approach_height":0.16988,"approach_to_start_pos.approach_speed":0.0429,"approach_to_start_pos.pre_push_offset":0.0779,"descend_to_contact.contact_force_threshold":8.69897,"descend_to_contact.descend_speed":0.03462,"descend_to_contact.pre_push_offset":0.03791,"push_1.push_distance":0.36833,"push_1.push_speed":0.06084,"push_1.push_tolerance":0.0229,"retract_1.retract_height":0.12721,"retract_1.retract_speed":0.03839},"optimized_scores":{"best_composite_score":-0.19,"best_fitness_score":0.08666,"best_task_score":0.00707},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.56675,-0.01036,0.03332],"force_p95":30.00311,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.98689,"mean_force":21.14907,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56677,0.00163,0.0333]},{"body_a":"world","body_b":"push_box","contact_count":13.0,"contact_point_centroid":[0.5563,-0.03737,-4e-05],"force_p95":10.15571,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.28344,"mean_force":3.49991,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56667,0.0016,0.03319]},{"body_a":"world","body_b":"push_box","contact_count":2380.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_to_start_pos","phase_type":"approach","tcp_position_centroid":[0.53837,0.01612,0.24686]},{"body_a":"world","body_b":"push_box","contact_count":3312.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"contact","tcp_position_centroid":[0.57171,0.01707,0.11246]}],"total_contact_groups":4},"final_pose_error":0.36715,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55404,-0.03575,0.02485],"final_tcp_position":[0.56604,0.00117,0.03278],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":30.98689,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":595.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_to_start_pos","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2380.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.57876,0.0324,0.19651],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.18588,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":828.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":17.20992,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3312.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.56727,0.0019,0.03373],"tcp_start":[0.57876,0.0324,0.19651],"tcp_to_object_dist_end":0.04001,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.55404,-0.03575,0.02485],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12638,"object_to_goal_dist_start":0.12728,"object_z_max":0.02512,"peak_contact_force":30.98689,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":30.98689,"subtask_id":"push_to_goal","tcp_end":[0.56604,0.00117,0.03278],"tcp_start":[0.56727,0.0019,0.03373],"tcp_to_object_dist_end":0.03963,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```