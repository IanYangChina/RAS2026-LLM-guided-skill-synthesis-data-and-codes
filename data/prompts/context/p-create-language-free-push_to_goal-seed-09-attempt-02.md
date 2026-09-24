## Search State

- **Seed**: 9
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3449 | 0.62 | ✅ accepted |
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3320 | 0.60 | ✅ accepted |
| 0 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.3274 | 0.60 | ✅ accepted |

**Proposal policy**: task_score is 0.62 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.345) — your mutation base

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

- **Composite score**: 0.345
- **task_score** (E): 0.619
- **fitness_score**: 0.555  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1515 |
| descend_1 | 1.00 | 1.00 | 0.1254 |
| push_1 | 1.00 | 1.00 | 0.1665 |
| retract_1 | 1.00 | 1.00 | 0.0884 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.514, 0.027, 0.159) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.514, 0.027, 0.159)→(0.514, 0.029, 0.034) | (0.518, -0.020, 0.025)→(0.518, -0.020, 0.025) | 0.139→0.139 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.514, 0.029, 0.034)→(0.498, -0.131, 0.021) | (0.518, -0.020, 0.025)→(0.538, -0.129, 0.025) | 0.139→0.051 | 1.00 / 3.333 | 0.313 | 41.136 |
| retract_1 | retract | 1.00 / step_budget | (0.498, -0.131, 0.021)→(0.495, -0.130, 0.109) | (0.538, -0.129, 0.025)→(0.538, -0.130, 0.025) | 0.051→0.050 | 1.00 / 4.000 | 0.245 | 1.603 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.765
- goal_progress: 0.877
- terminal_score: 0.877
- phase_score: 0.713
- phase_breakdown.reach_contact_score: 0.162
- phase_breakdown.push_to_goal_score: 0.878

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.778
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.877
- **Median Q (composite search score)**: 0.280
- **K-run variance**: 0.0265
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.264


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.9037,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11746,"approach_1.speed":0.08827,"push_1.push_speed":0.07584},"optimized_scores":{"best_composite_score":0.28046,"best_fitness_score":0.49046,"best_task_score":0.5435},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":182.0,"contact_point_centroid":[0.53054,-0.05686,0.04555],"force_p95":18.34251,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.49896,"mean_force":4.22284,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51958,-0.04779,0.02518]},{"body_a":"world","body_b":"push_box","contact_count":647.0,"contact_point_centroid":[0.55389,-0.08201,-7e-05],"force_p95":10.05354,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.02453,"mean_force":1.79567,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51812,-0.05592,0.02535]},{"body_a":"push_box","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.54959,-0.065,0.05668],"force_p95":24.74902,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.16654,"mean_force":12.78007,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51346,-0.07372,0.02368]},{"body_a":"world","body_b":"push_box","contact_count":2188.0,"contact_point_centroid":[0.54944,-0.11546,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24555,"mean_force":0.24522,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49701,-0.12984,0.06396]},{"body_a":"world","body_b":"push_box","contact_count":2128.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51772,0.01092,0.22465]},{"body_a":"world","body_b":"push_box","contact_count":1436.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53751,0.02304,0.09118]}],"total_contact_groups":6},"final_pose_error":0.01216,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54944,-0.11546,0.02499],"final_tcp_position":[0.49709,-0.12972,0.1092],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":34.49896,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":532.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2128.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.53774,0.02231,0.14945],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":780.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1436.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.53955,0.02392,0.03346],"tcp_start":[0.53774,0.02231,0.14945],"tcp_to_object_dist_end":0.05045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.54941,-0.11545,0.02495],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.06029,"object_to_goal_dist_start":0.13211,"object_z_max":0.02889,"peak_contact_force":0.24558,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":837.0,"raw_peak_contact_force":34.49896,"subtask_id":"push_to_goal","tcp_end":[0.50048,-0.13046,0.02086],"tcp_start":[0.53955,0.02392,0.03346],"tcp_to_object_dist_end":0.05134,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":630.0,"object_pos_end":[0.54944,-0.11546,0.02499],"object_pos_start":[0.54941,-0.11545,0.02495],"object_to_goal_dist_end":0.06031,"object_to_goal_dist_start":0.06029,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2188.0,"raw_peak_contact_force":0.24555,"tcp_end":[0.49709,-0.12972,0.1092],"tcp_start":[0.50048,-0.13046,0.02086],"tcp_to_object_dist_end":0.10018,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.37952,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1089,"approach_1.speed":0.06411,"push_1.push_speed":0.05485},"optimized_scores":{"best_composite_score":0.18566,"best_fitness_score":0.39566,"best_task_score":0.43637},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":173.0,"contact_point_centroid":[0.5363,-0.06488,0.04948],"force_p95":31.66064,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.84048,"mean_force":6.78424,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52474,-0.05555,0.02497]},{"body_a":"world","body_b":"push_box","contact_count":691.0,"contact_point_centroid":[0.56202,-0.08313,-7e-05],"force_p95":12.87133,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.96478,"mean_force":2.19136,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52481,-0.05657,0.02547]},{"body_a":"push_box","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.5575,-0.06162,0.05668],"force_p95":21.79337,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.41781,"mean_force":16.17348,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52011,-0.07018,0.02397]},{"body_a":"world","body_b":"push_box","contact_count":2173.0,"contact_point_centroid":[0.55661,-0.10584,-2e-05],"force_p95":0.24555,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65548,"mean_force":0.24747,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49826,-0.13008,0.06423]},{"body_a":"world","body_b":"push_box","contact_count":2396.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52246,0.00672,0.21997]},{"body_a":"world","body_b":"push_box","contact_count":1324.0,"contact_point_centroid":[0.55472,-0.03508,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54738,0.01407,0.08681]}],"total_contact_groups":6},"final_pose_error":0.01219,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55671,-0.10606,0.02499],"final_tcp_position":[0.49836,-0.12997,0.10919],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55472,-0.03508,0.025]},"peak_contact_force":38.84048,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.025],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2396.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.54744,0.01369,0.14048],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":331.0,"n_steps_budget":750.0,"object_pos_end":[0.55472,-0.03508,0.02499],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1324.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.54965,0.01457,0.03342],"tcp_start":[0.54744,0.01369,0.14048],"tcp_to_object_dist_end":0.05061,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":385.0,"n_steps_budget":1000.0,"object_pos_end":[0.55697,-0.10533,0.0242],"object_pos_start":[0.55472,-0.03508,0.02499],"object_to_goal_dist_end":0.0724,"object_to_goal_dist_start":0.12728,"object_z_max":0.02834,"peak_contact_force":0.69465,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":866.0,"raw_peak_contact_force":38.84048,"subtask_id":"push_to_goal","tcp_end":[0.50175,-0.13071,0.02088],"tcp_start":[0.54965,0.01457,0.03342],"tcp_to_object_dist_end":0.06087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":630.0,"object_pos_end":[0.55671,-0.10606,0.02499],"object_pos_start":[0.55697,-0.10533,0.0242],"object_to_goal_dist_end":0.07174,"object_to_goal_dist_start":0.0724,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2173.0,"raw_peak_contact_force":0.65548,"tcp_end":[0.49836,-0.12997,0.10919],"tcp_start":[0.50175,-0.13071,0.02088],"tcp_to_object_dist_end":0.1052,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24862,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15399,"approach_1.speed":0.05262,"push_1.push_speed":0.05831},"optimized_scores":{"best_composite_score":0.56846,"best_fitness_score":0.77846,"best_task_score":0.87652},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":352.0,"contact_point_centroid":[0.4752,-0.05673,0.03722],"force_p95":33.18283,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.06806,"mean_force":4.83359,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4717,-0.04502,0.02583]},{"body_a":"world","body_b":"push_box","contact_count":644.0,"contact_point_centroid":[0.47398,-0.06706,-8e-05],"force_p95":15.63385,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.99642,"mean_force":3.09705,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46606,-0.01983,0.02762]},{"body_a":"world","body_b":"push_box","contact_count":2145.0,"contact_point_centroid":[0.5071,-0.16846,-1e-05],"force_p95":0.24683,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.90727,"mean_force":0.2503,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48894,-0.1315,0.06503]},{"body_a":"attachment","body_b":"push_box","contact_count":19.0,"contact_point_centroid":[0.49844,-0.14392,0.04943],"force_p95":1.40651,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.65855,"mean_force":0.74434,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49034,-0.13233,0.02418]},{"body_a":"world","body_b":"push_box","contact_count":1748.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4785,0.02157,0.2438]},{"body_a":"world","body_b":"push_box","contact_count":2028.0,"contact_point_centroid":[0.45543,-9e-05,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4537,0.04676,0.1104]}],"total_contact_groups":6},"final_pose_error":0.01201,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50702,-0.16799,0.02499],"final_tcp_position":[0.48905,-0.13145,0.10944],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45543,-9e-05,0.025]},"peak_contact_force":50.06806,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":437.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.025],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1748.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_contact","tcp_end":[0.45725,0.04465,0.18705],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16813,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":507.0,"n_steps_budget":1000.0,"object_pos_end":[0.45543,-9e-05,0.02499],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.1564,"object_to_goal_dist_start":0.1564,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2028.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.45209,0.04909,0.03419],"tcp_start":[0.45725,0.04465,0.18705],"tcp_to_object_dist_end":0.05014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":514.0,"n_steps_budget":1000.0,"object_pos_end":[0.50702,-0.16768,0.02559],"object_pos_start":[0.45543,-9e-05,0.02499],"object_to_goal_dist_end":0.01903,"object_to_goal_dist_start":0.1564,"object_z_max":0.02658,"peak_contact_force":4e-05,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":996.0,"raw_peak_contact_force":50.06806,"subtask_id":"push_to_goal","tcp_end":[0.49239,-0.13221,0.02096],"tcp_start":[0.45209,0.04909,0.03419],"tcp_to_object_dist_end":0.03865,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":547.0,"n_steps_budget":630.0,"object_pos_end":[0.50702,-0.16799,0.02499],"object_pos_start":[0.50702,-0.16768,0.02559],"object_to_goal_dist_end":0.01931,"object_to_goal_dist_start":0.01903,"object_z_max":0.02581,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2164.0,"raw_peak_contact_force":3.90727,"tcp_end":[0.48905,-0.13145,0.10944],"tcp_start":[0.49239,-0.13221,0.02096],"tcp_to_object_dist_end":0.09376,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```