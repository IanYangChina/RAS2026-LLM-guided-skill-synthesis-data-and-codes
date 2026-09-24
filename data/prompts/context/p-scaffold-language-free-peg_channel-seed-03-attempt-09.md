## Search State

- **Seed**: 3
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | time_limit | time_limit | force_exceeded | pose_tolerance | 9 | 0.1497 | 0.06 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1753 | 0.33 | ✅ accepted |
| 7 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 8 | -0.2081 | 0.10 | ❌ rejected |
| 6 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 9 | -0.1448 | 0.00 | ❌ rejected |
| 5 | approach → descend → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8 | -0.2433 | 0.10 | ❌ rejected |

**Proposal policy**: task_score is 0.06 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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
| `object` | offset from object initial position (0.46685193337148995, 0.058944840527687975, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.46685193337148995, -0.10105515947231203, 0.04) | final destination targets |
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

## Current Skill (Q=0.150) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.05
  - 0.05
  weight: 0.3
- id: push_progress
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
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.1
    tolerance: 0.02
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
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.05
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_peg
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  subtask_id: reach_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: channel_exit
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.16
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.12
      - 0.18
      default: 0.16
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    speed:
      type: scalar
      range:
      - 0.01
      - 0.06
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_safe
    when: during_phase
    predicate: force_below
    threshold: 40.0
    on_failure: abort
  retries:
    max_attempts: 1
    strategy: reduce_speed
    offset:
    - 0.0
    - 0.0
    - 0.0
  subtask_id: push_progress
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
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.05, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_peg, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=channel_exit, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.16, mode=add_to_offset, sign=positive}, tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_safe, when=during_phase, predicate=force_below, on_failure=abort, threshold=40.0
  - retries: max_attempts=1, strategy=reduce_speed, offset=[0.0, 0.0, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.150
- **task_score** (E): 0.058
- **fitness_score**: 0.160  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.500
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1458 |
| descend_1 | 1.00 | 1.00 | 0.1325 |
| push_1 | 1.00 | 1.00 | 0.0415 |
| retract_1 | 1.00 | 1.00 | 0.0805 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.506, 0.134, 0.176) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.547 | 3.954 |
| descend_1 | descend | 1.00 / time_limit | (0.506, 0.134, 0.176)→(0.497, 0.113, 0.047) | (0.502, 0.082, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.547 | 0.560 |
| push_1 | push | 1.00 / force_exceeded | (0.497, 0.113, 0.047)→(0.495, 0.073, 0.043) | (0.502, 0.082, 0.034)→(0.504, 0.055, 0.035) | 0.162→0.135 | 1.00 / 2.000 | 2625.005 | 18.580 |
| retract_1 | retract | 1.00 / step_budget | (0.495, 0.073, 0.043)→(0.492, 0.072, 0.123) | (0.504, 0.055, 0.035)→(0.503, 0.055, 0.034) | 0.135→0.136 | 1.00 / 1.000 | 0.544 | 16.976 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.177
- alignment_error: None
- force_efficiency: 0.081
- terminal_score: 0.050
- phase_score: 0.301
- phase_breakdown.reach_peg_score: 0.511
- phase_breakdown.push_progress_score: 0.212

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.201
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.070
- **Median Q (composite search score)**: 0.137
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.267


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95833,"average_solve_count":240.0,"average_success_count":240.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.17375,"approach_1.approach_time":0.54012,"approach_1.speed":0.03691,"descend_1.descend_time":0.55511,"descend_1.speed":0.02851,"push_1.force_threshold":36.3545,"push_1.push_distance":0.15474,"push_1.speed":0.04666,"retract_1.speed":0.05409},"optimized_scores":{"best_composite_score":0.19097,"best_fitness_score":0.20097,"best_task_score":0.05043},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":261.0,"contact_point_centroid":[0.4961,0.02985,0.00945],"force_p95":0.57044,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.96175,"mean_force":0.90493,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48545,0.02411,0.09897]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.49938,0.0253,0.05897],"force_p95":36.95542,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.53724,"mean_force":7.89942,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48759,0.02412,0.06025]},{"body_a":"peg","body_b":"channel_base_body","contact_count":762.0,"contact_point_centroid":[0.49812,0.03612,0.0096],"force_p95":33.89106,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.98259,"mean_force":16.42075,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48454,0.05845,0.06089]},{"body_a":"attachment","body_b":"peg","contact_count":606.0,"contact_point_centroid":[0.49686,0.05129,0.059],"force_p95":33.73009,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.49301,"mean_force":20.06144,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48502,0.05146,0.06044]},{"body_a":"peg","body_b":"channel_base_body","contact_count":716.0,"contact_point_centroid":[0.49435,0.05902,0.00936],"force_p95":0.55965,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56661,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48182,0.15539,0.254]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49891,0.19836,0.29794]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49415,0.05896,0.0094],"force_p95":0.55051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.54554,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.47449,0.10326,0.13781]}],"total_contact_groups":7},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49697,0.03062,0.0342],"final_tcp_position":[0.4852,0.02413,0.14041],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":45.96175,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":745.0,"n_steps_budget":1000.0,"object_pos_end":[0.49399,0.059,0.03389],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13927,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54477,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":751.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.4663,0.11383,0.21454],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1908,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4939,0.05915,0.03403],"object_pos_start":[0.49399,0.059,0.03389],"object_to_goal_dist_end":0.13941,"object_to_goal_dist_start":0.13927,"object_z_max":0.03403,"peak_contact_force":0.54458,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55392,"subtask_id":"reach_peg","tcp_end":[0.48476,0.09339,0.06621],"tcp_start":[0.4663,0.11383,0.21454],"tcp_to_object_dist_end":0.04787,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":762.0,"n_steps_budget":1000.0,"object_pos_end":[0.4971,0.02974,0.03457],"object_pos_start":[0.4939,0.05915,0.03403],"object_to_goal_dist_end":0.10991,"object_to_goal_dist_start":0.13941,"object_z_max":0.03461,"peak_contact_force":36.98259,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1368.0,"raw_peak_contact_force":36.98259,"subtask_id":"push_progress","tcp_end":[0.48799,0.0243,0.05992],"tcp_start":[0.48476,0.09339,0.06621],"tcp_to_object_dist_end":0.02748,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":261.0,"n_steps_budget":1000.0,"object_pos_end":[0.49697,0.03062,0.0342],"object_pos_start":[0.4971,0.02974,0.03457],"object_to_goal_dist_end":0.11081,"object_to_goal_dist_start":0.10991,"object_z_max":0.03459,"peak_contact_force":0.53461,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":273.0,"raw_peak_contact_force":45.96175,"tcp_end":[0.4852,0.02413,0.14041],"tcp_start":[0.48799,0.0243,0.05992],"tcp_to_object_dist_end":0.10706,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.95,"average_solve_count":180.0,"average_success_count":180.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11567,"approach_1.approach_time":0.64465,"approach_1.speed":0.05924,"descend_1.descend_time":0.40596,"descend_1.speed":0.03625,"push_1.force_threshold":35.20963,"push_1.push_distance":0.13876,"push_1.speed":0.03042,"retract_1.speed":0.05445},"optimized_scores":{"best_composite_score":0.13694,"best_fitness_score":0.14694,"best_task_score":0.05463},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":249.0,"contact_point_centroid":[0.50459,0.05186,0.00986],"force_p95":5.70754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.10291,"mean_force":2.97065,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50031,0.0967,0.03452]},{"body_a":"attachment","body_b":"peg","contact_count":235.0,"contact_point_centroid":[0.50308,0.08312,0.04328],"force_p95":5.48178,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.67651,"mean_force":2.74712,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50006,0.09495,0.0343]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50581,0.08087,0.00937],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56248,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51526,0.16432,0.22232]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49977,0.1988,0.29752]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":58.0,"contact_point_centroid":[0.52512,0.05546,0.02942],"force_p95":1.55901,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71289,"mean_force":0.83538,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4994,0.08432,0.03412]},{"body_a":"peg","body_b":"channel_base_body","contact_count":265.0,"contact_point_centroid":[0.50753,0.04774,0.00957],"force_p95":0.57332,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73109,"mean_force":0.51895,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49652,0.08081,0.07352]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.0532,0.01081],"force_p95":0.64276,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64276,"mean_force":0.64276,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49928,0.08133,0.03417]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.50267,0.06918,0.05924],"force_p95":0.4456,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.55553,"mean_force":0.33074,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49733,0.08083,0.04429]},{"body_a":"peg","body_b":"channel_base_body","contact_count":582.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5165,0.12228,0.09647]}],"total_contact_groups":9},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50678,0.05237,0.03383],"final_tcp_position":[0.49626,0.08083,0.1147],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":3918.40906,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1007.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.53085,0.1329,0.15599],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13513,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":582.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08089,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54527,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":582.0,"raw_peak_contact_force":0.55006,"subtask_id":"reach_peg","tcp_end":[0.50401,0.11172,0.03819],"tcp_start":[0.53085,0.1329,0.15599],"tcp_to_object_dist_end":0.03121,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":319.0,"n_steps_budget":1000.0,"object_pos_end":[0.50691,0.05225,0.03572],"object_pos_start":[0.50597,0.08089,0.03378],"object_to_goal_dist_end":0.1325,"object_to_goal_dist_start":0.16113,"object_z_max":0.0358,"peak_contact_force":3918.40906,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":542.0,"raw_peak_contact_force":8.10291,"subtask_id":"push_progress","tcp_end":[0.49928,0.08133,0.03417],"tcp_start":[0.50401,0.11172,0.03819],"tcp_to_object_dist_end":0.0301,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":267.0,"n_steps_budget":1000.0,"object_pos_end":[0.50678,0.05237,0.03383],"object_pos_start":[0.50691,0.05225,0.03572],"object_to_goal_dist_end":0.13269,"object_to_goal_dist_start":0.1325,"object_z_max":0.03572,"peak_contact_force":0.54523,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":297.0,"raw_peak_contact_force":0.73109,"tcp_end":[0.49626,0.08083,0.1147],"tcp_start":[0.49928,0.08133,0.03417],"tcp_to_object_dist_end":0.08637,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25466,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11676,"approach_1.approach_time":0.37649,"approach_1.speed":0.06517,"descend_1.descend_time":0.73039,"descend_1.speed":0.03547,"push_1.force_threshold":32.37254,"push_1.push_distance":0.13573,"push_1.speed":0.02643,"retract_1.speed":0.07159},"optimized_scores":{"best_composite_score":0.12109,"best_fitness_score":0.13109,"best_task_score":0.07002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":178.0,"contact_point_centroid":[0.50362,0.07834,0.00988],"force_p95":6.26752,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.65506,"mean_force":3.4228,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49986,0.12377,0.03421]},{"body_a":"attachment","body_b":"peg","contact_count":182.0,"contact_point_centroid":[0.50277,0.11052,0.04238],"force_p95":5.97852,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.49469,"mean_force":2.99083,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49957,0.12232,0.03392]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52501,0.08217,0.05508],"force_p95":4.07976,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.23548,"mean_force":0.9345,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49779,0.11165,0.03748]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.50203,0.09988,0.05908],"force_p95":2.31023,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.01181,"mean_force":0.60103,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49668,0.11143,0.04578]},{"body_a":"peg","body_b":"channel_base_body","contact_count":764.0,"contact_point_centroid":[0.50568,0.10468,0.00938],"force_p95":0.57577,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56116,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50942,0.17687,0.22509]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49971,0.19906,0.2977]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52503,0.08476,0.0221],"force_p95":1.9009,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90835,"mean_force":1.23033,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49887,0.1131,0.03349]},{"body_a":"peg","body_b":"channel_base_body","contact_count":252.0,"contact_point_centroid":[0.50706,0.0777,0.0096],"force_p95":0.59089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78408,"mean_force":0.51678,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49605,0.11138,0.07281]},{"body_a":"peg","body_b":"channel_base_body","contact_count":616.0,"contact_point_centroid":[0.50599,0.10458,0.00939],"force_p95":0.5757,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57583,"mean_force":0.5463,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51049,0.14546,0.09735]}],"total_contact_groups":9},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50654,0.08332,0.03381],"final_tcp_position":[0.49572,0.11137,0.11384],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":3919.62434,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":791.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54967,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":796.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.52006,0.15605,0.15875],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1358,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,0.10456,0.03384],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18488,"object_z_max":0.03384,"peak_contact_force":0.55164,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":616.0,"raw_peak_contact_force":0.57583,"subtask_id":"reach_peg","tcp_end":[0.50313,0.13518,0.03775],"tcp_start":[0.52006,0.15605,0.15875],"tcp_to_object_dist_end":0.03099,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":230.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,0.08321,0.03577],"object_pos_start":[0.50586,0.10456,0.03384],"object_to_goal_dist_end":0.16342,"object_to_goal_dist_start":0.18476,"object_z_max":0.03576,"peak_contact_force":3919.62434,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":377.0,"raw_peak_contact_force":10.65506,"subtask_id":"push_progress","tcp_end":[0.49882,0.11207,0.03351],"tcp_start":[0.50313,0.13518,0.03775],"tcp_to_object_dist_end":0.03008,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":254.0,"n_steps_budget":870.0,"object_pos_end":[0.50654,0.08332,0.03381],"object_pos_start":[0.50698,0.08321,0.03577],"object_to_goal_dist_end":0.16357,"object_to_goal_dist_start":0.16342,"object_z_max":0.03577,"peak_contact_force":0.5512,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":293.0,"raw_peak_contact_force":4.23548,"tcp_end":[0.49572,0.11137,0.11384],"tcp_start":[0.49882,0.11207,0.03351],"tcp_to_object_dist_end":0.08549,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```