## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.3635 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.2912 | 0.42 | ✅ accepted |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.4917 | 0.40 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0143 | 0.00 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.4922 | 0.40 | ✅ accepted |

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

## Current Skill (Q=-0.363) — your mutation base

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
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: add
    approach_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object
- id: descend_1
  type: descend
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
    descend_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.02
      binds_to:
      - path: generator.speed
        mode: add
    force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 3.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
- id: push_1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.25
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: guards.contact_check.threshold
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: add
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.05
      default: 0.03
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: contact_check
    when: during_phase
    predicate: contact_detected
    threshold: 5.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (add)
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=0, strategy=repeat
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=replace_offset_projection, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=guards.contact_check.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (add)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=contact_check, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=5.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]

## Design Metrics

- **Composite score**: -0.363
- **task_score** (E): 0.000
- **fitness_score**: 0.047  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1664 |
| descend_1 | 1.00 | 0.0899 |
| push_1 | 0.00 | 0.0001 |
| push_2 | 0.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, -0.001, 0.142) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 |
| descend_1 | descend | 1.00 / force_exceeded | (0.520, -0.001, 0.142)→(0.520, -0.001, 0.052) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 |
| push_1 | push | 0.00 / guard_failure | (0.520, -0.001, 0.052)→(0.520, -0.001, 0.052) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 |
| push_2 | push | 0.00 / guard_failure | (0.520, -0.001, 0.052)→(0.520, -0.001, 0.052) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.001
- approach_alignment: 0.519
- goal_progress: 0.001
- terminal_score: 0.001
- phase_score: 0.078
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.260

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.047
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.363
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.280


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.78205,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04429,"approach_1.approach_tolerance":0.03415,"descend_1.descend_speed":0.02926,"descend_1.force_threshold":6.83694,"push_1.push1_distance":0.13331,"push_1.push1_force_threshold":2.01292,"push_1.push1_speed":0.06797,"push_1.push1_tolerance":0.05447,"push_2.push2_distance":0.20577,"push_2.push2_force_threshold":8.80346,"push_2.push2_speed":0.03512,"push_2.push2_tolerance":0.03853},"optimized_scores":{"best_composite_score":-0.36412,"best_fitness_score":0.04588,"best_task_score":3e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.48729,0.05609,0.0499],"force_p95":38.61509,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.93837,"mean_force":26.70549,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47555,0.05594,0.05229]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.4709,0.05847,-1e-05],"force_p95":22.35275,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.38744,"mean_force":9.1413,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47556,0.05594,0.0523]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.48719,0.0561,0.04985],"force_p95":17.16286,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.22691,"mean_force":16.58641,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.47545,0.05593,0.05213]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.4542,0.05847,-1e-05],"force_p95":10.16551,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.24824,"mean_force":8.64816,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.47545,0.05593,0.05213]},{"body_a":"world","body_b":"push_box","contact_count":1372.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48944,0.02434,0.22312]},{"body_a":"world","body_b":"push_box","contact_count":2248.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4761,0.05319,0.09611]}],"total_contact_groups":6},"final_pose_error":0.20544,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47909,0.05845,0.02504],"final_tcp_position":[0.47538,0.05592,0.05203],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"phases":[{"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.4793,0.05071,0.14292],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11819,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":562.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.47558,0.05594,0.05233],"tcp_start":[0.4793,0.05071,0.14292],"tcp_to_object_dist_end":0.0277,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.47919,0.05847,0.02501],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02501,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.47548,0.05593,0.05217],"tcp_start":[0.47553,0.05593,0.05224],"tcp_to_object_dist_end":0.02752,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.47912,0.05846,0.02504],"object_pos_start":[0.47915,0.05846,0.02503],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02504,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.47538,0.05592,0.05203],"tcp_start":[0.47543,0.05593,0.0521],"tcp_to_object_dist_end":0.02736,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12727,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08784,"approach_1.approach_tolerance":0.03198,"descend_1.descend_speed":0.02981,"descend_1.force_threshold":7.94903,"push_1.push1_distance":0.18414,"push_1.push1_force_threshold":5.62245,"push_1.push1_speed":0.09708,"push_1.push1_tolerance":0.04228,"push_2.push2_distance":0.1624,"push_2.push2_force_threshold":6.71473,"push_2.push2_speed":0.07034,"push_2.push2_tolerance":0.06613},"optimized_scores":{"best_composite_score":-0.36344,"best_fitness_score":0.04656,"best_task_score":0.00049},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.54965,-0.02463,0.04992],"force_p95":44.14204,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.39802,"mean_force":32.83822,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53792,-0.02457,0.05236]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.53609,-0.02558,-1e-05],"force_p95":23.24688,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.40407,"mean_force":11.20144,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53792,-0.02457,0.05238]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.54954,-0.02465,0.04985],"force_p95":21.88922,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.91916,"mean_force":21.61977,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.53781,-0.02457,0.05216]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.51939,-0.02558,-2e-05],"force_p95":11.54834,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.6023,"mean_force":11.16218,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.53781,-0.02457,0.05216]},{"body_a":"world","body_b":"push_box","contact_count":1312.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5169,-0.01073,0.22248]},{"body_a":"world","body_b":"push_box","contact_count":2168.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53547,-0.0234,0.09485]}],"total_contact_groups":6},"final_pose_error":0.16353,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54424,-0.02558,0.02507],"final_tcp_position":[0.53774,-0.02457,0.05204],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"phases":[{"n_steps":328.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.53589,-0.02223,0.14225],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11762,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":542.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.53794,-0.02457,0.05241],"tcp_start":[0.53589,-0.02223,0.14225],"tcp_to_object_dist_end":0.0282,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.54438,-0.02558,0.02502],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.1321,"object_to_goal_dist_start":0.13211,"object_z_max":0.02502,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.53784,-0.02457,0.05221],"tcp_start":[0.53789,-0.02457,0.0523],"tcp_to_object_dist_end":0.02798,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.54428,-0.02558,0.02506],"object_pos_start":[0.54433,-0.02558,0.02504],"object_to_goal_dist_end":0.13206,"object_to_goal_dist_start":0.13208,"object_z_max":0.02506,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.53774,-0.02457,0.05204],"tcp_start":[0.53779,-0.02457,0.05212],"tcp_to_object_dist_end":0.02778,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.41436,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04605,"approach_1.approach_tolerance":0.03631,"descend_1.descend_speed":0.01752,"descend_1.force_threshold":1.1728,"push_1.push1_distance":0.16697,"push_1.push1_force_threshold":6.13817,"push_1.push1_speed":0.05341,"push_1.push1_tolerance":0.0467,"push_2.push2_distance":0.14144,"push_2.push2_force_threshold":7.1269,"push_2.push2_speed":0.04168,"push_2.push2_tolerance":0.07389},"optimized_scores":{"best_composite_score":-0.36281,"best_fitness_score":0.04719,"best_task_score":0.00059},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.55953,-0.03377,0.0499],"force_p95":44.84714,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.10919,"mean_force":33.48865,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5478,-0.03367,0.05233]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.54638,-0.03508,-1e-05],"force_p95":23.73534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.03081,"mean_force":11.41469,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5478,-0.03367,0.05235]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.55943,-0.03379,0.04984],"force_p95":23.27746,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.37041,"mean_force":22.44088,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.5477,-0.03367,0.05215]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.52968,-0.03508,-2e-05],"force_p95":13.21998,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.50818,"mean_force":11.57149,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.5477,-0.03367,0.05215]},{"body_a":"world","body_b":"push_box","contact_count":1432.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52112,-0.01473,0.22225]},{"body_a":"world","body_b":"push_box","contact_count":2328.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54498,-0.03213,0.09413]}],"total_contact_groups":6},"final_pose_error":0.14247,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55455,-0.03508,0.02505],"final_tcp_position":[0.54764,-0.03367,0.05203],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"phases":[{"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object","tcp_end":[0.54508,-0.03061,0.14141],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11691,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.54781,-0.03367,0.05238],"tcp_start":[0.54508,-0.03061,0.14141],"tcp_to_object_dist_end":0.02828,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.55467,-0.03508,0.02501],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12726,"object_to_goal_dist_start":0.12728,"object_z_max":0.02501,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.54773,-0.03367,0.05219],"tcp_start":[0.54778,-0.03367,0.05228],"tcp_to_object_dist_end":0.02808,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.55458,-0.03508,0.02505],"object_pos_start":[0.55463,-0.03508,0.02504],"object_to_goal_dist_end":0.12722,"object_to_goal_dist_start":0.12724,"object_z_max":0.02505,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.54764,-0.03367,0.05203],"tcp_start":[0.54768,-0.03367,0.0521],"tcp_to_object_dist_end":0.02789,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```