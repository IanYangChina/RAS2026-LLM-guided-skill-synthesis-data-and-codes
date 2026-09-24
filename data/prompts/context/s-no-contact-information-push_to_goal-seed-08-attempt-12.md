## Search State

- **Seed**: 8
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → align → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | admittance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 11 | 0.2768 | 0.54 | ✅ accepted |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.5156 | 0.43 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.5163 | 0.43 | ✅ accepted |
| 9 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.3635 | 0.00 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 8 | 0.2912 | 0.42 | ✅ accepted |

**Proposal policy**: task_score is 0.54 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.277) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object_side
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.025
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
    - 0.03
    - 0.08
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
    lateral_offset_y:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.y
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object_side
- id: descend_to_side
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.03
    - 0.025
    tolerance: 0.01
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
    descend_tolerance:
      type: scalar
      range:
      - 0.002
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    lateral_offset_y:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.y
        mode: replace
  retries:
    max_attempts: 0
    strategy: repeat
  subtask_id: reach_object_side
- id: align_side_contact
  type: align
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.025
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.015
      binds_to:
      - path: generator.speed
        mode: add
    side_contact_force:
      type: scalar
      range:
      - 1.0
      - 10.0
      default: 5.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - -0.005
    - 0.0
  subtask_id: reach_object_side
- id: push_1
  type: push
  generator: linear_cartesian
  control: admittance_control
  termination: time_limit
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
    tolerance: 0.05
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.35
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_duration:
      type: scalar
      range:
      - 500.0
      - 3000.0
      default: 1500
      binds_to:
      - path: duration.max_time
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
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.08], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (add)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (replace)
  - retries: max_attempts=0, strategy=repeat
- **descend_to_side** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.025], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (add)
    - descend_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
    - lateral_offset_y: status=consumed; consumers=target.offset.y (replace)
  - retries: max_attempts=0, strategy=repeat
- **align_side_contact** (`align`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.025]
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (add)
    - side_contact_force: status=consumed; consumers=termination.force_threshold (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, -0.005, 0.0]
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.25, mode=replace_offset_projection, sign=positive}, tolerance=0.05
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_duration: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (add)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.005, 0.0]

## Design Metrics

- **Composite score**: 0.277
- **task_score** (E): 0.542
- **fitness_score**: 0.553  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.610

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1881 |
| descend_to_side | 1.00 | 0.0652 |
| align_side_contact | 1.00 | 0.0093 |
| push_1 | 1.00 | 0.2141 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.520, 0.028, 0.122) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 |
| descend_to_side | descend | 1.00 / step_budget | (0.520, 0.028, 0.122)→(0.521, 0.031, 0.058) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 |
| align_side_contact | align | 1.00 / force_exceeded | (0.521, 0.031, 0.058)→(0.519, 0.025, 0.052) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 |
| push_1 | push | 1.00 / time_limit | (0.519, 0.025, 0.052)→(0.465, -0.178, 0.029) | (0.526, -0.001, 0.025)→(0.508, -0.076, 0.025) | 0.156→0.078 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.685
- approach_alignment: 0.782
- goal_progress: 0.681
- terminal_score: 0.681
- phase_score: 0.627
- phase_breakdown.push_to_goal_score: 0.681
- phase_breakdown.reach_object_side_score: 0.500

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.648
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.681
- **Median Q (composite search score)**: 0.351
- **K-run variance**: 0.0144
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.351


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31967,"average_solve_count":122.0,"average_success_count":122.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_side_contact.align_speed":0.04101,"align_side_contact.side_contact_force":4.96594,"approach_1.approach_speed":0.19769,"approach_1.approach_tolerance":0.02755,"approach_1.lateral_offset_y":0.03288,"descend_to_side.descend_speed":0.032,"descend_to_side.descend_tolerance":0.01593,"descend_to_side.lateral_offset_y":0.01002,"push_1.push_distance":0.31624,"push_1.push_duration":1456.34328,"push_1.push_speed":0.06501},"optimized_scores":{"best_composite_score":0.1076,"best_fitness_score":0.38427,"best_task_score":0.28604},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":810.0,"contact_point_centroid":[0.48844,0.02858,0.0477],"force_p95":98.6272,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.57851,"mean_force":65.22946,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47963,0.02295,0.04887]},{"body_a":"world","body_b":"push_box","contact_count":2332.0,"contact_point_centroid":[0.48193,0.02844,-0.00026],"force_p95":74.66508,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.69314,"mean_force":23.06678,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47953,0.01552,0.04733]},{"body_a":"world","body_b":"push_box","contact_count":1408.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48923,0.03953,0.21151]},{"body_a":"world","body_b":"push_box","contact_count":904.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_side","phase_type":"descend","tcp_position_centroid":[0.47631,0.07586,0.09045]},{"body_a":"world","body_b":"push_box","contact_count":252.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"align_side_contact","phase_type":"align","tcp_position_centroid":[0.47451,0.06811,0.05548]}],"total_contact_groups":5},"final_pose_error":0.21367,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47994,-0.00177,0.02497],"final_tcp_position":[0.4828,-0.04479,0.03864],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"phases":[{"n_steps":352.0,"n_steps_budget":690.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object_side","tcp_end":[0.47892,0.08094,0.12181],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0994,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":226.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"phase_name":"descend_to_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object_side","tcp_end":[0.4757,0.07031,0.05911],"tcp_start":[0.47892,0.08094,0.12181],"tcp_to_object_dist_end":0.03629,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":63.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"phase_name":"align_side_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"reach_object_side","tcp_end":[0.47414,0.0657,0.05257],"tcp_start":[0.4757,0.07031,0.05911],"tcp_to_object_dist_end":0.02896,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47994,-0.00177,0.02497],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.14958,"object_to_goal_dist_start":0.2095,"object_z_max":0.03532,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.4828,-0.04479,0.03864],"tcp_start":[0.47414,0.0657,0.05257],"tcp_to_object_dist_end":0.04523,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2069,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_side_contact.align_speed":0.00925,"align_side_contact.side_contact_force":2.11536,"approach_1.approach_speed":0.08387,"approach_1.approach_tolerance":0.02582,"approach_1.lateral_offset_y":0.04358,"descend_to_side.descend_speed":0.02299,"descend_to_side.descend_tolerance":0.01465,"descend_to_side.lateral_offset_y":0.0461,"push_1.push_distance":0.33386,"push_1.push_duration":1527.54865,"push_1.push_speed":0.19842},"optimized_scores":{"best_composite_score":0.35103,"best_fitness_score":0.62769,"best_task_score":0.66055},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":469.0,"contact_point_centroid":[0.53068,-0.04539,0.04919],"force_p95":156.15138,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":172.46447,"mean_force":105.51117,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52183,-0.04724,0.04978]},{"body_a":"world","body_b":"push_box","contact_count":3088.0,"contact_point_centroid":[0.52793,-0.08985,-0.00016],"force_p95":99.74104,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":149.34247,"mean_force":16.35416,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4875,-0.14759,0.0371]},{"body_a":"world","body_b":"push_box","contact_count":1452.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51706,0.00761,0.21279]},{"body_a":"world","body_b":"push_box","contact_count":932.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_side","phase_type":"descend","tcp_position_centroid":[0.53631,0.01743,0.09018]},{"body_a":"world","body_b":"push_box","contact_count":1456.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"align_side_contact","phase_type":"align","tcp_position_centroid":[0.53605,0.01357,0.05232]}],"total_contact_groups":5},"final_pose_error":0.04978,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52276,-0.11136,0.02499],"final_tcp_position":[0.44257,-0.29135,0.02326],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"phases":[{"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object_side","tcp_end":[0.53624,0.01572,0.12282],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10651,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":233.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"phase_name":"descend_to_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object_side","tcp_end":[0.53902,0.0194,0.05814],"tcp_start":[0.53624,0.01572,0.12282],"tcp_to_object_dist_end":0.05615,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":364.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"phase_name":"align_side_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"reach_object_side","tcp_end":[0.53595,0.01032,0.05109],"tcp_start":[0.53902,0.0194,0.05814],"tcp_to_object_dist_end":0.04519,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52276,-0.11136,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.04485,"object_to_goal_dist_start":0.13211,"object_z_max":0.03931,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.44257,-0.29135,0.02326],"tcp_start":[0.53595,0.01032,0.05109],"tcp_to_object_dist_end":0.19706,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.35294,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_side_contact.align_speed":0.04088,"align_side_contact.side_contact_force":2.86426,"approach_1.approach_speed":0.10161,"approach_1.approach_tolerance":0.01444,"approach_1.lateral_offset_y":0.02046,"descend_to_side.descend_speed":0.02929,"descend_to_side.descend_tolerance":0.01133,"descend_to_side.lateral_offset_y":0.04244,"push_1.push_distance":0.22319,"push_1.push_duration":1088.18149,"push_1.push_speed":0.13501},"optimized_scores":{"best_composite_score":0.37164,"best_fitness_score":0.6483,"best_task_score":0.68079},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":621.0,"contact_point_centroid":[0.5402,-0.05101,0.04794],"force_p95":150.64603,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":154.3057,"mean_force":107.13181,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53025,-0.05319,0.04919]},{"body_a":"world","body_b":"push_box","contact_count":2685.0,"contact_point_centroid":[0.53847,-0.077,-0.0003],"force_p95":123.51188,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":152.28992,"mean_force":25.64754,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51349,-0.08912,0.04144]},{"body_a":"push_box","body_b":"link7","contact_count":90.0,"contact_point_centroid":[0.54537,-0.10744,0.07672],"force_p95":22.95049,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.91419,"mean_force":13.823,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4979,-0.13052,0.03581]},{"body_a":"world","body_b":"push_box","contact_count":1464.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52159,-0.00627,0.21223]},{"body_a":"world","body_b":"push_box","contact_count":960.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_to_side","phase_type":"descend","tcp_position_centroid":[0.54593,-0.0051,0.08911]},{"body_a":"world","body_b":"push_box","contact_count":284.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"align_side_contact","phase_type":"align","tcp_position_centroid":[0.54733,0.00126,0.05389]}],"total_contact_groups":6},"final_pose_error":0.03927,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52234,-0.11607,0.02499],"final_tcp_position":[0.46864,-0.19859,0.02431],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"phases":[{"n_steps":366.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_object_side","tcp_end":[0.54542,-0.01293,0.12213],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10006,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"phase_name":"descend_to_side","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_object_side","tcp_end":[0.54909,0.00361,0.05728],"tcp_start":[0.54542,-0.01293,0.12213],"tcp_to_object_dist_end":0.0507,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":71.0,"n_steps_budget":630.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"phase_name":"align_side_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","subtask_id":"reach_object_side","tcp_end":[0.5465,-0.00149,0.0518],"tcp_start":[0.54909,0.00361,0.05728],"tcp_to_object_dist_end":0.04376,"terminated_normally":true,"termination_reason":"force_exceeded"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52234,-0.11607,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.04063,"object_to_goal_dist_start":0.12728,"object_z_max":0.04045,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.46864,-0.19859,0.02431],"tcp_start":[0.5465,-0.00149,0.0518],"tcp_to_object_dist_end":0.09846,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```