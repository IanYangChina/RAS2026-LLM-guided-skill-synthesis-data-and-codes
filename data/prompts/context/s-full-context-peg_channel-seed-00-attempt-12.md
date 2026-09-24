## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.0470 | 0.32 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.2491 | 0.65 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.3533 | 0.22 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.2268 | 0.17 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.3092 | 0.78 | ✅ accepted |

**Proposal policy**: task_score is 0.32 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: peg_channel
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5, 0.2, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0.2, 0.3]
objects:
  - name: peg
    role: manipulated_object
    dynamics: free
    geometry: cylinder
    radius_m: 0.018
    half_length_m: 0.025
  - name: channel_structure
    role: fixture
    dynamics: static
    geometry: two_parallel_walls
    inner_gap_m: 0.05
    wall_thickness_m: 0.03
    wall_height_m: 0.05
task_landmarks:
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

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
| `object` | offset from object initial position (0.5109569349857164, 0.061582937101109625, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5109569349857164, -0.09841706289889038, 0.04) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

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

## Current Skill (Q=-0.047) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.08
  - 0.1
  weight: 0.3
- id: push_channel
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
    - 0.08
    - 0.1
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
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
    - 0.08
    - 0.0
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: push_1
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
      distance: 0.16
      axis: channel_axis
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.2
      default: 0.16
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
  subtask_id: push_channel
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.08
    - 0.1
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    retract_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.0], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=channel_axis, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.08, 0.1], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: -0.047
- **task_score** (E): 0.319
- **fitness_score**: 0.313  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1478 |
| descend_1 | 1.00 | 1.00 | 0.1057 |
| push_1 | 1.00 | 1.00 | 0.1429 |
| retract_1 | 1.00 | 1.00 | 0.0947 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.165, 0.159) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.530 | 2.179 |
| descend_1 | descend | 1.00 / step_budget | (0.495, 0.165, 0.159)→(0.496, 0.160, 0.053) | (0.500, 0.080, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.535 | 0.592 |
| push_1 | push | 1.00 / step_budget | (0.496, 0.160, 0.053)→(0.490, 0.018, 0.049) | (0.500, 0.081, 0.034)→(0.506, 0.022, 0.024) | 0.161→0.103 | 1.00 / 1.000 | 0.559 | 43.896 |
| retract_1 | retract | 1.00 / step_budget | (0.490, 0.018, 0.049)→(0.500, 0.090, 0.109) | (0.506, 0.022, 0.024)→(0.501, 0.022, 0.024) | 0.103→0.103 | 1.00 / 1.000 | 0.543 | 3.678 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.348
- alignment_error: None
- force_efficiency: 0.215
- terminal_score: 0.329
- phase_score: 0.320
- phase_breakdown.push_channel_score: 0.382
- phase_breakdown.reach_object_score: 0.176

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.323
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.357
- **Median Q (composite search score)**: -0.039
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.344


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.17788,"average_solve_count":208.0,"average_success_count":208.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08844,"descend_1.speed":0.09474,"push_1.lateral_offset":-0.0073,"push_1.push_distance":0.17016,"push_1.push_speed":0.0278,"retract_1.retract_speed":0.18001},"optimized_scores":{"best_composite_score":-0.03661,"best_fitness_score":0.32339,"best_task_score":0.32852},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":399.0,"contact_point_centroid":[0.50513,0.038,0.00923],"force_p95":37.78277,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.25397,"mean_force":10.65003,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49487,0.06815,0.04953]},{"body_a":"attachment","body_b":"peg","contact_count":163.0,"contact_point_centroid":[0.50126,0.04889,0.04711],"force_p95":38.24185,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.83844,"mean_force":24.81587,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49455,0.05725,0.04977]},{"body_a":"peg","body_b":"channel_base_body","contact_count":269.0,"contact_point_centroid":[0.50339,0.06164,0.00931],"force_p95":0.68906,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.57652,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50299,0.1733,0.2246]},{"body_a":"peg","body_b":"channel_base_body","contact_count":293.0,"contact_point_centroid":[0.50598,0.00613,0.00805],"force_p95":0.6837,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.69381,"mean_force":0.60572,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49492,0.03222,0.07783]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49985,0.199,0.29784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":199.0,"contact_point_centroid":[0.50387,0.06143,0.00938],"force_p95":0.55727,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57488,"mean_force":0.54676,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50337,0.14553,0.10648]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.03086,0.02417],"force_p95":0.38601,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38601,"mean_force":0.38601,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49072,0.0019,0.05541]}],"total_contact_groups":7},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50479,0.00585,0.02413],"final_tcp_position":[0.5014,0.07339,0.10952],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":39.25397,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":292.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06158,0.03377],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.51941,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":288.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_object","tcp_end":[0.50681,0.14921,0.15794],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15201,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":199.0,"n_steps_budget":840.0,"object_pos_end":[0.50374,0.06159,0.03378],"object_pos_start":[0.50377,0.06158,0.03377],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14177,"object_z_max":0.03378,"peak_contact_force":0.54658,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":199.0,"raw_peak_contact_force":0.57488,"subtask_id":"reach_object","tcp_end":[0.50106,0.1422,0.05357],"tcp_start":[0.50681,0.14921,0.15794],"tcp_to_object_dist_end":0.08304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.50664,0.00593,0.02413],"object_pos_start":[0.50374,0.06159,0.03378],"object_to_goal_dist_end":0.08764,"object_to_goal_dist_start":0.14178,"object_z_max":0.04023,"peak_contact_force":0.53055,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":562.0,"raw_peak_contact_force":39.25397,"subtask_id":"push_channel","tcp_end":[0.49102,-0.00883,0.04894],"tcp_start":[0.50106,0.1422,0.05357],"tcp_to_object_dist_end":0.03282,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":293.0,"n_steps_budget":600.0,"object_pos_end":[0.50479,0.00585,0.02413],"object_pos_start":[0.50664,0.00593,0.02413],"object_to_goal_dist_end":0.08744,"object_to_goal_dist_start":0.08764,"object_z_max":0.02421,"peak_contact_force":0.53262,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":294.0,"raw_peak_contact_force":0.69381,"tcp_end":[0.5014,0.07339,0.10952],"tcp_start":[0.49102,-0.00883,0.04894],"tcp_to_object_dist_end":0.10892,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.40936,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.11085,"descend_1.speed":0.08445,"push_1.lateral_offset":-0.00608,"push_1.push_distance":0.1566,"push_1.push_speed":0.03602,"retract_1.retract_speed":0.11574},"optimized_scores":{"best_composite_score":-0.06551,"best_fitness_score":0.29449,"best_task_score":0.35652},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":353.0,"contact_point_centroid":[0.50248,0.0946,0.00932],"force_p95":38.76131,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.83033,"mean_force":12.45948,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49157,0.12711,0.04923]},{"body_a":"attachment","body_b":"peg","contact_count":157.0,"contact_point_centroid":[0.49801,0.10241,0.04692],"force_p95":38.9812,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.39993,"mean_force":26.82697,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49104,0.11049,0.04948]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52502,0.08349,0.02392],"force_p95":7.17635,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.40458,"mean_force":1.88663,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4886,0.05905,0.04888]},{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.5011,0.11595,0.00933],"force_p95":0.77475,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.57654,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49869,0.19743,0.22705]},{"body_a":"peg","body_b":"channel_base_body","contact_count":282.0,"contact_point_centroid":[0.50551,0.05882,0.00808],"force_p95":0.71781,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.98312,"mean_force":0.60073,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49348,0.09212,0.07762]},{"body_a":"peg","body_b":"channel_base_body","contact_count":204.0,"contact_point_centroid":[0.50055,0.11594,0.00943],"force_p95":0.61127,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64951,"mean_force":0.54235,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49704,0.19493,0.10703]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.0836,0.02441],"force_p95":0.39554,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39554,"mean_force":0.39554,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48819,0.06049,0.05154]}],"total_contact_groups":7},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50464,0.05899,0.02431],"final_tcp_position":[0.50089,0.12746,0.10909],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":39.83033,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":265.0,"n_steps_budget":900.0,"object_pos_end":[0.50089,0.11605,0.03388],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.52076,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":249.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_object","tcp_end":[0.49835,0.19563,0.15957],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":204.0,"n_steps_budget":930.0,"object_pos_end":[0.50092,0.11603,0.03388],"object_pos_start":[0.50089,0.11605,0.03388],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19615,"object_z_max":0.03395,"peak_contact_force":0.51096,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":204.0,"raw_peak_contact_force":0.64951,"subtask_id":"reach_object","tcp_end":[0.49714,0.19477,0.05323],"tcp_start":[0.49835,0.19563,0.15957],"tcp_to_object_dist_end":0.08117,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.50649,0.05895,0.02411],"object_pos_start":[0.50092,0.11603,0.03388],"object_to_goal_dist_end":0.14,"object_to_goal_dist_start":0.19613,"object_z_max":0.04022,"peak_contact_force":0.56539,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":516.0,"raw_peak_contact_force":39.83033,"subtask_id":"push_channel","tcp_end":[0.48849,0.05724,0.04883],"tcp_start":[0.49714,0.19477,0.05323],"tcp_to_object_dist_end":0.03062,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":282.0,"n_steps_budget":630.0,"object_pos_end":[0.50464,0.05899,0.02431],"object_pos_start":[0.50649,0.05895,0.02411],"object_to_goal_dist_end":0.13995,"object_to_goal_dist_start":0.14,"object_z_max":0.02443,"peak_contact_force":0.52752,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":283.0,"raw_peak_contact_force":0.98312,"tcp_end":[0.50089,0.12746,0.10909],"tcp_start":[0.48849,0.05724,0.04883],"tcp_to_object_dist_end":0.10903,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41139,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06765,"descend_1.speed":0.08936,"push_1.lateral_offset":0.00421,"push_1.push_distance":0.15823,"push_1.push_speed":0.05766,"retract_1.retract_speed":0.1729},"optimized_scores":{"best_composite_score":-0.03892,"best_fitness_score":0.32108,"best_task_score":0.27076},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":174.0,"contact_point_centroid":[0.49602,0.04542,0.04578],"force_p95":42.20551,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.60327,"mean_force":28.40675,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48852,0.05278,0.04881]},{"body_a":"peg","body_b":"channel_base_body","contact_count":349.0,"contact_point_centroid":[0.50009,0.04142,0.0094],"force_p95":40.79991,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.32515,"mean_force":14.02778,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48789,0.07455,0.04872]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":23.0,"contact_point_centroid":[0.52504,-0.01851,0.03388],"force_p95":23.34106,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.26094,"mean_force":12.8014,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48963,0.02512,0.04932]},{"body_a":"peg","body_b":"channel_base_body","contact_count":262.0,"contact_point_centroid":[0.49709,-0.00025,0.00811],"force_p95":0.65246,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.35644,"mean_force":0.72764,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49298,0.03687,0.077]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47499,0.02457,0.02445],"force_p95":8.69764,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.96224,"mean_force":3.03978,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49489,0.04907,0.0883]},{"body_a":"peg","body_b":"channel_base_body","contact_count":269.0,"contact_point_centroid":[0.49576,0.06411,0.00934],"force_p95":0.67498,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57692,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48956,0.17399,0.2239]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49915,0.19845,0.29603]},{"body_a":"peg","body_b":"channel_base_body","contact_count":210.0,"contact_point_centroid":[0.49535,0.06365,0.00939],"force_p95":0.55016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55295,"mean_force":0.54581,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48423,0.14755,0.10597]}],"total_contact_groups":8},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49357,0.0004,0.02414],"final_tcp_position":[0.49898,0.06908,0.10831],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":52.60327,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.49493,0.06384,0.03391],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14406,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54847,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":297.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_object","tcp_end":[0.48115,0.15109,0.15814],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15243,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":210.0,"n_steps_budget":900.0,"object_pos_end":[0.49504,0.06406,0.03394],"object_pos_start":[0.49493,0.06384,0.03391],"object_to_goal_dist_end":0.14427,"object_to_goal_dist_start":0.14406,"object_z_max":0.03394,"peak_contact_force":0.54681,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":210.0,"raw_peak_contact_force":0.55295,"subtask_id":"reach_object","tcp_end":[0.48904,0.14431,0.05258],"tcp_start":[0.48115,0.15109,0.15814],"tcp_to_object_dist_end":0.08261,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.50435,0.00016,0.02397],"object_pos_start":[0.49504,0.06406,0.03394],"object_to_goal_dist_end":0.08187,"object_to_goal_dist_start":0.14427,"object_z_max":0.04022,"peak_contact_force":0.58048,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":546.0,"raw_peak_contact_force":52.60327,"subtask_id":"push_channel","tcp_end":[0.48945,0.00506,0.0484],"tcp_start":[0.48904,0.14431,0.05258],"tcp_to_object_dist_end":0.02903,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":262.0,"n_steps_budget":600.0,"object_pos_end":[0.49357,0.0004,0.02414],"object_pos_start":[0.50435,0.00016,0.02397],"object_to_goal_dist_end":0.0822,"object_to_goal_dist_start":0.08187,"object_z_max":0.02477,"peak_contact_force":0.57016,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":274.0,"raw_peak_contact_force":9.35644,"tcp_end":[0.49898,0.06908,0.10831],"tcp_start":[0.48945,0.00506,0.0484],"tcp_to_object_dist_end":0.10877,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```