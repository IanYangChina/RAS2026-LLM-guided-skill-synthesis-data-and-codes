## Search State

- **Seed**: 8
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | contact_detected | pose_tolerance | 4 | -0.1264 | 0.00 | ✅ accepted |
| 2 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | contact_detected | pose_tolerance | 6 | 0.0679 | 0.00 | ✅ accepted |
| 1 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | -0.3100 | 0.00 | ❌ rejected |
| 0 | pull → insert → descend → contact | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | impedance_control | impedance_control | position_control | impedance_control | time_limit | pose_tolerance | contact_detected | force_exceeded | 5 | -0.3100 | 0.00 | ✅ accepted |

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

## Current Skill (Q=-0.126) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: contact_box
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
- id: approach_and_contact
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.05
    offset_along_axis:
      distance: 0.05
      axis: task_goal_direction
      mode: replace_offset_projection
      sign: negative
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
    contact_z_offset:
      type: scalar
      range:
      - 0.03
      - 0.07
      default: 0.05
      binds_to:
      - path: target.offset.z
        mode: replace
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.01
  subtask_id: contact_box
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_force_limit:
      type: scalar
      range:
      - 5.0
      - 25.0
      default: 15.0
      binds_to:
      - path: guards.force_guard.threshold
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
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 25.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push_to_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_and_contact** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.05], offset_along_axis={axis=task_goal_direction, distance=0.05, mode=replace_offset_projection, sign=negative}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - contact_z_offset: status=consumed; consumers=target.offset.z (replace)
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.01]
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_force_limit: status=consumed; consumers=guards.force_guard.threshold (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=25.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.01, 0.0]

## Design Metrics

- **Composite score**: -0.126
- **task_score** (E): 0.001
- **fitness_score**: 0.074  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_and_contact | 1.00 | 1.00 | 0.2408 |
| push_to_goal | 0.00 | 1.00 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_and_contact | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.531, 0.043, 0.073) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_to_goal | push | 0.00 / guard_failure | (0.516, -0.019, 0.052)→(0.516, -0.019, 0.052) | (0.526, -0.001, 0.025)→(0.526, -0.001, 0.025) | 0.156→0.156 | 1.00 / 3.000 | 41.981 | 41.981 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.002
- lateral_force_integral: None
- approach_alignment: 0.436
- goal_progress: 0.001
- terminal_score: 0.001
- phase_score: 0.128
- phase_breakdown.contact_box_score: 0.424
- phase_breakdown.push_to_goal_score: 0.001

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.077
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.128
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.408


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.22222,"average_solve_count":45.0,"average_success_count":45.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_and_contact.approach_speed":0.29952,"approach_and_contact.contact_z_offset":0.03197,"push_to_goal.push_force_limit":17.56204,"push_to_goal.push_speed":0.08354},"optimized_scores":{"best_composite_score":-0.12271,"best_fitness_score":0.07729,"best_task_score":0.00145},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.4885,0.0333,0.04992],"force_p95":30.35349,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.68937,"mean_force":19.85205,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47701,0.03085,0.0523]},{"body_a":"world","body_b":"push_box","contact_count":690.0,"contact_point_centroid":[0.47924,0.05826,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.72138,"mean_force":0.36493,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.47378,0.06676,0.05941]},{"body_a":"world","body_b":"push_box","contact_count":2284.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_and_contact","phase_type":"approach","tcp_position_centroid":[0.48636,0.0473,0.18918]}],"total_contact_groups":3},"final_pose_error":0.1834,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47925,0.05817,0.02526],"final_tcp_position":[0.47711,0.02993,0.05215],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":31.68937,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_box","tcp_end":[0.47267,0.10039,0.06857],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":174.0,"n_steps_budget":1000.0,"object_pos_end":[0.47926,0.05827,0.02517],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2093,"object_to_goal_dist_start":0.2095,"object_z_max":0.02517,"peak_contact_force":31.68937,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":694.0,"raw_peak_contact_force":31.68937,"subtask_id":"push_to_goal","tcp_end":[0.47711,0.02993,0.05215],"tcp_start":[0.47709,0.03024,0.05221],"tcp_to_object_dist_end":0.03919,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.23256,"average_solve_count":43.0,"average_success_count":43.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_and_contact.approach_speed":0.29555,"approach_and_contact.contact_z_offset":0.03978,"push_to_goal.push_force_limit":13.34885,"push_to_goal.push_speed":0.08511},"optimized_scores":{"best_composite_score":-0.12841,"best_fitness_score":0.07159,"best_task_score":0.00068},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.54338,-0.03843,0.04994],"force_p95":40.18366,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.40468,"mean_force":38.19445,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.53165,-0.03855,0.05241]},{"body_a":"world","body_b":"push_box","contact_count":586.0,"contact_point_centroid":[0.54443,-0.02567,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.57973,"mean_force":0.37729,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54219,-0.00788,0.06256]},{"body_a":"world","body_b":"push_box","contact_count":2284.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_and_contact","phase_type":"approach","tcp_position_centroid":[0.52444,0.00935,0.19215]}],"total_contact_groups":3},"final_pose_error":0.11847,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54443,-0.02568,0.02505],"final_tcp_position":[0.53146,-0.03908,0.05225],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":40.40468,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_box","tcp_end":[0.55366,0.01986,0.07479],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":147.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02562,0.02502],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13208,"object_to_goal_dist_start":0.13211,"object_z_max":0.02502,"peak_contact_force":40.40468,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":588.0,"raw_peak_contact_force":40.40468,"subtask_id":"push_to_goal","tcp_end":[0.53146,-0.03908,0.05225],"tcp_start":[0.53159,-0.03876,0.05235],"tcp_to_object_dist_end":0.03303,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53333,"average_solve_count":60.0,"average_success_count":60.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_and_contact.approach_speed":0.27648,"approach_and_contact.contact_z_offset":0.04122,"push_to_goal.push_force_limit":15.0259,"push_to_goal.push_speed":0.0461},"optimized_scores":{"best_composite_score":-0.12817,"best_fitness_score":0.07183,"best_task_score":0.00059},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.55181,-0.04689,0.04996],"force_p95":52.82955,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.84885,"mean_force":43.65579,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54008,-0.04693,0.05245]},{"body_a":"world","body_b":"push_box","contact_count":614.0,"contact_point_centroid":[0.55472,-0.03516,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.62853,"mean_force":0.38859,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55353,-0.01705,0.06312]},{"body_a":"world","body_b":"push_box","contact_count":2284.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_and_contact","phase_type":"approach","tcp_position_centroid":[0.53106,0.00435,0.19275]}],"total_contact_groups":3},"final_pose_error":0.11338,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55473,-0.03517,0.02504],"final_tcp_position":[0.53986,-0.04742,0.05228],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":53.84885,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":571.0,"n_steps_budget":600.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_and_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2284.0,"raw_peak_contact_force":0.24534,"subtask_id":"contact_box","tcp_end":[0.56765,0.00924,0.07592],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":154.0,"n_steps_budget":1000.0,"object_pos_end":[0.55471,-0.03511,0.02501],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12725,"object_to_goal_dist_start":0.12728,"object_z_max":0.02501,"peak_contact_force":53.84885,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":616.0,"raw_peak_contact_force":53.84885,"subtask_id":"push_to_goal","tcp_end":[0.53986,-0.04742,0.05228],"tcp_start":[0.54,-0.04712,0.05239],"tcp_to_object_dist_end":0.0334,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```