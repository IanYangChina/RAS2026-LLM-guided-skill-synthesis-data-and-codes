## Search State

- **Seed**: 9
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3320 | 0.60 | ✅ accepted |
| 0 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3274 | 0.60 | ✅ accepted |

**Proposal policy**: task_score is 0.60 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`
- Frozen object start: [0.5444299044764102, -0.025581934909493356, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5444299044764102, -0.025581934909493356, 0.025)
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
  frozen_object_start: [0.5444, -0.0256, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5444299044764102, -0.025581934909493356, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0444, -0.1244, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b

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
| `object` | offset from object initial position (0.5444299044764102, -0.025581934909493356, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.332) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_contact
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.1
  weight: 0.3
- id: push_to_goal
  target_entity: object
  metric: goal_progress
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
    - 0.05
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_contact
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  subtask_id: reach_contact
- id: push_1
  type: push
  generator: impedance_motion
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
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_to_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.332
- **task_score** (E): 0.603
- **fitness_score**: 0.542  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1315 |
| descend_1 | 1.00 | 1.00 | 0.1462 |
| push_1 | 1.00 | 1.00 | 0.1665 |
| retract_1 | 1.00 | 1.00 | 0.0884 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.513, 0.027, 0.180) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.513, 0.027, 0.180)→(0.514, 0.029, 0.034) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.029, 0.034)→(0.498, -0.131, 0.021) | (0.518, -0.020, 0.025)→(0.536, -0.126, 0.025) | 0.139→0.052 | 1.00 / 3.667 | 9.256 | 51.803 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.131, 0.021)→(0.495, -0.130, 0.109) | (0.536, -0.126, 0.025)→(0.536, -0.127, 0.025) | 0.052→0.053 | 1.00 / 4.000 | 0.245 | 2.050 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.765
- goal_progress: 0.882
- terminal_score: 0.882
- phase_score: 0.717
- phase_breakdown.reach_contact_score: 0.162
- phase_breakdown.push_to_goal_score: 0.884

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.783
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.882
- **Median Q (composite search score)**: 0.239
- **K-run variance**: 0.0296
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.322


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `327b95871eb659cd41b4cf66bc0b4dfb3b240662e8501854b46ee2b8b86a04c5`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `5ffd2bb280d1d50ec9ffd23c1ed75abf73d645c1d10372a9b5bb6e9fac6e0bf8`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33918,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19426,"approach_1.speed":0.06118,"push_1.push_speed":0.04808},"optimized_scores":{"best_composite_score":0.23884,"best_fitness_score":0.44884,"best_task_score":0.49511},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":196.0,"contact_point_centroid":[0.53179,-0.05459,0.04756],"force_p95":30.71589,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.74295,"mean_force":6.62094,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52013,-0.04574,0.02549]},{"body_a":"world","body_b":"push_box","contact_count":730.0,"contact_point_centroid":[0.55459,-0.07952,-6e-05],"force_p95":14.69154,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.85188,"mean_force":2.29096,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5178,-0.05735,0.02537]},{"body_a":"push_box","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.54805,-0.06218,0.05701],"force_p95":15.79772,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.59938,"mean_force":8.99355,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51301,-0.07585,0.02372]},{"body_a":"world","body_b":"push_box","contact_count":1368.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51695,0.01033,0.26159]},{"body_a":"world","body_b":"push_box","contact_count":2332.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53701,0.02252,0.1283]},{"body_a":"world","body_b":"push_box","contact_count":2188.0,"contact_point_centroid":[0.55101,-0.10703,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24524,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49698,-0.12991,0.06398]}],"total_contact_groups":6},"final_pose_error":0.01216,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55101,-0.10703,0.02499],"final_tcp_position":[0.49706,-0.1298,0.10923],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":49.74295,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":342.0,"n_steps_budget":990.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1368.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.53633,0.02124,0.22392],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.20453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2332.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.53972,0.02392,0.03376],"tcp_start":[0.53633,0.02124,0.22392],"tcp_to_object_dist_end":0.0505,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":1000.0,"object_pos_end":[0.55101,-0.10702,0.02498],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.0667,"object_to_goal_dist_start":0.13211,"object_z_max":0.02885,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":932.0,"raw_peak_contact_force":49.74295,"subtask_id":"push_to_goal","tcp_end":[0.50044,-0.13054,0.02089],"tcp_start":[0.53972,0.02392,0.03376],"tcp_to_object_dist_end":0.05592,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":630.0,"object_pos_end":[0.55101,-0.10703,0.02499],"object_pos_start":[0.55101,-0.10702,0.02498],"object_to_goal_dist_end":0.0667,"object_to_goal_dist_start":0.0667,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2188.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49706,-0.1298,0.10923],"tcp_start":[0.50044,-0.13054,0.02089],"tcp_to_object_dist_end":0.1026,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `e094d2c5a71c8b89ef1fa30d7ce553b9c4ed64cd3fbca90620c3ede94e719cec`; realized-scene SHA-256: `d6f67641a3df0efca2ae6de2763dea57e4736e336d1ca3e6fe373ea0745d2d85`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55472,-0.03508,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05472,-0.11492,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55472,-0.03508,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57419,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11712,"approach_1.speed":0.06721,"push_1.push_speed":0.0635},"optimized_scores":{"best_composite_score":0.18379,"best_fitness_score":0.39379,"best_task_score":0.43132},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":140.0,"contact_point_centroid":[0.53881,-0.05686,0.05007],"force_p95":38.1561,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.82643,"mean_force":7.31982,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52725,-0.04754,0.02554]},{"body_a":"world","body_b":"push_box","contact_count":811.0,"contact_point_centroid":[0.56126,-0.08274,-9e-05],"force_p95":10.40058,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.27034,"mean_force":1.68323,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52204,-0.06552,0.02497]},{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.5551,-0.05938,0.05703],"force_p95":11.34154,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.38931,"mean_force":8.46959,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51947,-0.07233,0.02391]},{"body_a":"world","body_b":"push_box","contact_count":2292.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52238,0.00669,0.22407]},{"body_a":"world","body_b":"push_box","contact_count":1416.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54734,0.01405,0.09088]},{"body_a":"world","body_b":"push_box","contact_count":2188.0,"contact_point_centroid":[0.55598,-0.10412,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49826,-0.13017,0.06392]}],"total_contact_groups":6},"final_pose_error":0.01219,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55598,-0.10412,0.02499],"final_tcp_position":[0.49835,-0.13005,0.10918],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":54.82643,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.54732,0.01364,0.14866],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13312,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":354.0,"n_steps_budget":780.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1416.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.54969,0.01457,0.03359],"tcp_start":[0.54732,0.01364,0.14866],"tcp_to_object_dist_end":0.05064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.55598,-0.10412,0.02498],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.07238,"object_to_goal_dist_start":0.12728,"object_z_max":0.02863,"peak_contact_force":0.24521,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":955.0,"raw_peak_contact_force":54.82643,"subtask_id":"push_to_goal","tcp_end":[0.50174,-0.13079,0.02086],"tcp_start":[0.54969,0.01457,0.03359],"tcp_to_object_dist_end":0.06059,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":630.0,"object_pos_end":[0.55598,-0.10412,0.02499],"object_pos_start":[0.55598,-0.10412,0.02498],"object_to_goal_dist_end":0.07238,"object_to_goal_dist_start":0.07238,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2188.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49835,-0.13005,0.10918],"tcp_start":[0.50174,-0.13079,0.02086],"tcp_to_object_dist_end":0.10527,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0fd7d18e656259f06515eb57b82afa0c0febd9395a43c1a5f926ddaec3767c64`; realized-scene SHA-256: `5de0d8cc5a3c16249bcf1097af6edba15dfacc79d06e3eed726605dcb01257b0`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45543,-9e-05,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04457,-0.14991,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45543,-9e-05,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20707,"average_solve_count":198.0,"average_success_count":198.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1338,"approach_1.speed":0.04738,"push_1.push_speed":0.05297},"optimized_scores":{"best_composite_score":0.57322,"best_fitness_score":0.78322,"best_task_score":0.8819},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":379.0,"contact_point_centroid":[0.47614,-0.06065,0.03953],"force_p95":35.80747,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.8407,"mean_force":6.05112,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47266,-0.04886,0.02565]},{"body_a":"world","body_b":"push_box","contact_count":666.0,"contact_point_centroid":[0.47292,-0.07159,-6e-05],"force_p95":17.42939,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.34028,"mean_force":3.87943,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46733,-0.02508,0.02734]},{"body_a":"world","body_b":"push_box","contact_count":2109.0,"contact_point_centroid":[0.50102,-0.16926,-1e-05],"force_p95":0.24895,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.66058,"mean_force":0.25489,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48918,-0.13117,0.06587]},{"body_a":"attachment","body_b":"push_box","contact_count":22.0,"contact_point_centroid":[0.49733,-0.14394,0.04607],"force_p95":1.67019,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.63182,"mean_force":0.77953,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49088,-0.13205,0.02378]},{"body_a":"world","body_b":"push_box","contact_count":1992.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4781,0.02192,0.23397]},{"body_a":"world","body_b":"push_box","contact_count":1772.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.45338,0.04702,0.10065]}],"total_contact_groups":6},"final_pose_error":0.01202,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50099,-0.16844,0.02499],"final_tcp_position":[0.4893,-0.13112,0.1096],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":50.8407,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":498.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1992.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.45668,0.04518,0.16741],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14944,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":443.0,"n_steps_budget":900.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1772.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.45206,0.04908,0.03419],"tcp_start":[0.45668,0.04518,0.16741],"tcp_to_object_dist_end":0.05014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":516.0,"n_steps_budget":1000.0,"object_pos_end":[0.50091,-0.16813,0.02519],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.01815,"object_to_goal_dist_start":0.1564,"object_z_max":0.02607,"peak_contact_force":27.27875,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1045.0,"raw_peak_contact_force":50.8407,"subtask_id":"push_to_goal","tcp_end":[0.49264,-0.13188,0.02112],"tcp_start":[0.45206,0.04908,0.03419],"tcp_to_object_dist_end":0.0374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":546.0,"n_steps_budget":630.0,"object_pos_end":[0.50099,-0.16844,0.02499],"object_pos_start":[0.50091,-0.16813,0.02519],"object_to_goal_dist_end":0.01847,"object_to_goal_dist_start":0.01815,"object_z_max":0.0256,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2131.0,"raw_peak_contact_force":5.66058,"tcp_end":[0.4893,-0.13112,0.1096],"tcp_start":[0.49264,-0.13188,0.02112],"tcp_to_object_dist_end":0.09321,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```