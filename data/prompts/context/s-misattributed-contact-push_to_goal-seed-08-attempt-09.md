## Search State

- **Seed**: 8
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.4032 | 0.38 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.0903 | 0.00 | ❌ rejected |
| 7 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 2 | 0.0336 | 0.00 | ❌ rejected |
| 6 | approach → push | linear_cartesian | linear_cartesian | impedance_control | impedance_control | time_limit | pose_tolerance | 4 | -0.1801 | 0.00 | ❌ rejected |
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | -0.0304 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.403) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: approach_obj
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.0
  weight: 0.3
- id: push_goal
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
    offset:
    - 0.0
    - 0.025
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: approach_obj
- id: push_to_goal
  type: push
  generator: linear_cartesian
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
      distance: 0.25
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_dist:
      type: scalar
      range:
      - 0.15
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_check
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: abort
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.005
    - 0.0
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.025, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
  - retries: max_attempts=0, strategy=repeat
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_dist: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_check, when=during_phase, predicate=contact_detected, on_failure=abort, threshold=1.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.005, 0.0]

## Design Metrics

- **Composite score**: 0.403
- **task_score** (E): 0.382
- **fitness_score**: 0.461  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1783 |
| descend_to_contact | 0.67 | 1.00 | 0.0797 |
| push_to_goal | 1.00 | 1.00 | 0.1692 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.022, 0.132) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.667 | 50595.773 | 0.245 |
| descend_to_contact | descend | 0.67 / force_exceeded | (0.521, 0.022, 0.132)→(0.522, 0.024, 0.053) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.295 | 92.257 |
| push_to_goal | push | 1.00 / step_budget | (0.522, 0.024, 0.053)→(0.475, -0.135, 0.048) | (0.526, -0.001, 0.025)→(0.498, -0.056, 0.025) | 0.156→0.098 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.576
- lateral_force_integral: None
- approach_alignment: 0.777
- goal_progress: 0.557
- terminal_score: 0.557
- phase_score: 0.636
- phase_breakdown.push_goal_score: 0.557
- phase_breakdown.approach_obj_score: 0.821

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.604
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.557
- **Median Q (composite search score)**: 0.413
- **K-run variance**: 0.0449
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.392


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76289,"average_solve_count":97.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.24778,"descend_to_contact.contact_force_threshold":6.31398,"descend_to_contact.descend_speed":0.05272,"push_to_goal.push_dist":0.15426,"push_to_goal.push_speed":0.07221},"optimized_scores":{"best_composite_score":0.13878,"best_fitness_score":0.41878,"best_task_score":0.33011},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":305.0,"contact_point_centroid":[0.48955,0.03863,0.05118],"force_p95":100.449,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.71454,"mean_force":68.06765,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48085,0.03276,0.05264]},{"body_a":"world","body_b":"push_box","contact_count":760.0,"contact_point_centroid":[0.48249,0.0222,-0.00025],"force_p95":88.395,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":93.73782,"mean_force":27.84535,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48117,0.0234,0.05201]},{"body_a":"world","body_b":"push_box","contact_count":2072.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.4882,0.03813,0.21576]},{"body_a":"world","body_b":"push_box","contact_count":1932.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47524,0.07962,0.09138]}],"total_contact_groups":4},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48138,-0.0109,0.02439],"final_tcp_position":[0.48575,-0.0523,0.04874],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":102.71454,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":518.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1932.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_obj","tcp_end":[0.4776,0.07735,0.13242],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":483.0,"n_steps_budget":990.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.39442,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1065.0,"raw_peak_contact_force":102.71454,"tcp_end":[0.47539,0.0823,0.05283],"tcp_start":[0.4776,0.07735,0.13242],"tcp_to_object_dist_end":0.03684,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":383.0,"n_steps_budget":1000.0,"object_pos_end":[0.48138,-0.0109,0.02439],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.14034,"object_to_goal_dist_start":0.2095,"object_z_max":0.03526,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2072.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_goal","tcp_end":[0.48575,-0.0523,0.04874],"tcp_start":[0.47539,0.0823,0.05283],"tcp_to_object_dist_end":0.04823,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27338,"average_solve_count":139.0,"average_success_count":139.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.17064,"descend_to_contact.contact_force_threshold":6.54842,"descend_to_contact.descend_speed":0.05206,"push_to_goal.push_dist":0.20207,"push_to_goal.push_speed":0.0493},"optimized_scores":{"best_composite_score":0.65756,"best_fitness_score":0.60422,"best_task_score":0.55663},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":341.0,"contact_point_centroid":[0.53291,-0.04064,0.05169],"force_p95":85.31213,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.19,"mean_force":66.22007,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52416,-0.04631,0.05316]},{"body_a":"world","body_b":"push_box","contact_count":1087.0,"contact_point_centroid":[0.53328,-0.07211,-0.00028],"force_p95":80.44799,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.12528,"mean_force":21.27355,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.50952,-0.08185,0.05084]},{"body_a":"world","body_b":"push_box","contact_count":2048.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51789,-0.0003,0.2162]},{"body_a":"world","body_b":"push_box","contact_count":1880.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.53744,-0.00067,0.09038]}],"total_contact_groups":4},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53154,-0.10064,0.02498],"final_tcp_position":[0.47485,-0.1718,0.04764],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":512.0,"n_steps_budget":690.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":75893.53664,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1880.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_obj","tcp_end":[0.53793,-0.00061,0.13241],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":470.0,"n_steps_budget":990.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.2453,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1428.0,"raw_peak_contact_force":86.19,"tcp_end":[0.53971,-0.00067,0.05238],"tcp_start":[0.53793,-0.00061,0.13241],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":531.0,"n_steps_budget":1000.0,"object_pos_end":[0.53154,-0.10064,0.02498],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.05858,"object_to_goal_dist_start":0.13211,"object_z_max":0.04132,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2048.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_goal","tcp_end":[0.47485,-0.1718,0.04764],"tcp_start":[0.53971,-0.00067,0.05238],"tcp_to_object_dist_end":0.09376,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18713,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.approach_speed":0.12045,"descend_to_contact.contact_force_threshold":6.76899,"descend_to_contact.descend_speed":0.06266,"push_to_goal.push_dist":0.20831,"push_to_goal.push_speed":0.03801},"optimized_scores":{"best_composite_score":0.41322,"best_fitness_score":0.35989,"best_task_score":0.25845},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1293.0,"contact_point_centroid":[0.51138,-0.05796,-0.00022],"force_p95":83.2911,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.86782,"mean_force":17.17393,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5065,-0.097,0.05028]},{"body_a":"attachment","body_b":"push_box","contact_count":336.0,"contact_point_centroid":[0.5377,-0.04787,0.05153],"force_p95":86.12119,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.90312,"mean_force":64.52355,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.52933,-0.05327,0.05293]},{"body_a":"world","body_b":"push_box","contact_count":2312.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.5226,-0.00462,0.21565]},{"body_a":"world","body_b":"push_box","contact_count":1800.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.54735,-0.00973,0.08988]}],"total_contact_groups":4},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48193,-0.05736,0.02499],"final_tcp_position":[0.46528,-0.17955,0.04779],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":578.0,"n_steps_budget":960.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":75893.53664,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1800.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_obj","tcp_end":[0.54757,-0.0094,0.13167],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10996,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":450.0,"n_steps_budget":840.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1629.0,"raw_peak_contact_force":87.86782,"tcp_end":[0.54985,-0.01004,0.05244],"tcp_start":[0.54757,-0.0094,0.13167],"tcp_to_object_dist_end":0.03747,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.48193,-0.05736,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.09439,"object_to_goal_dist_start":0.12728,"object_z_max":0.03689,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2312.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_goal","tcp_end":[0.46528,-0.17955,0.04779],"tcp_start":[0.54985,-0.01004,0.05244],"tcp_to_object_dist_end":0.12541,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```