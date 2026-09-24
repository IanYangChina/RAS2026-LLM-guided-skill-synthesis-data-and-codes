## Search State

- **Seed**: 3
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 8  | -0.0495 | 0.25 | ✅ accepted |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | -0.3779 | 0.00 | ❌ rejected |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | arc_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 7  | -0.4752 | 0.00 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 10  | -0.0545 | 0.25 | ✅ accepted |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 9  | 0.0091 | 0.28 | ✅ accepted |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.009) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: push_through_channel
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
    - 0.05
    - 0.08
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    approach_offset_y:
      type: scalar
      range:
      - 0.03
      - 0.08
      default: 0.05
      binds_to:
      - path: target.offset.y
        mode: add
    approach_offset_z:
      type: scalar
      range:
      - 0.05
      - 0.12
      default: 0.08
      binds_to:
      - path: target.offset.z
        mode: add
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 0.8
      default: 0.4
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
    offset:
    - 0.0
    - 0.03
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_offset_y:
      type: scalar
      range:
      - 0.02
      - 0.06
      default: 0.03
      binds_to:
      - path: target.offset.y
        mode: add
    descend_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_peg
- id: push_1
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
    push_speed:
      type: scalar
      range:
      - 0.04
      - 0.12
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_maintained
    when: during_phase
    predicate: contact_detected
    threshold: 0.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.01
    - 0.0
  subtask_id: push_through_channel
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: add
    retract_speed:
      type: scalar
      range:
      - 0.2
      - 0.8
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.05, 0.08], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - approach_offset_y: status=consumed; consumers=target.offset.y (add)
    - approach_offset_z: status=consumed; consumers=target.offset.z (add)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.03, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_offset_y: status=consumed; consumers=target.offset.y (add)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_maintained, when=during_phase, predicate=contact_detected, on_failure=retry, threshold=0.0
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.01, 0.0]
- **retract_1** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - retract_height: status=consumed; consumers=target.offset.z (add)
    - retract_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.009
- **task_score** (E): 0.278
- **fitness_score**: 0.469  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0751 |
| descend_1 | 1.00 | 1.00 | 0.1840 |
| push_1 | 1.00 | 1.00 | 0.2149 |
| retract_1 | 1.00 | 1.00 | 0.2731 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.195, 0.230) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.550 | 3.954 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.195, 0.230)→(0.499, 0.154, 0.052) | (0.502, 0.082, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.000 | 0.548 | 0.564 |
| push_1 | push | 1.00 / step_budget | (0.499, 0.154, 0.052)→(0.499, -0.060, 0.039) | (0.502, 0.082, 0.034)→(0.500, -0.032, 0.028) | 0.162→0.050 | 1.00 / 2.000 | 57.686 | 92.385 |
| retract_1 | retract | 1.00 / step_budget | (0.499, -0.060, 0.039)→(0.498, -0.054, 0.312) | (0.500, -0.032, 0.028)→(0.501, -0.040, 0.027) | 0.050→0.043 | 1.00 / 1.000 | 0.541 | 80.166 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.876
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.421
- phase_score: 0.551
- phase_breakdown.push_through_channel_score: 0.639
- phase_breakdown.reach_peg_score: 0.347

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.499
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.421
- **Median Q (composite search score)**: 0.015
- **K-run variance**: 0.0007
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.320


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.21739,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.06791,"approach_1.approach_offset_z":0.09194,"approach_1.approach_speed":0.57261,"descend_1.descend_offset_y":0.02016,"descend_1.descend_speed":0.11942,"push_1.push_speed":0.1073,"retract_1.retract_height":0.14136,"retract_1.retract_speed":0.34563},"optimized_scores":{"best_composite_score":0.01459,"best_fitness_score":0.47459,"best_task_score":0.21355},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":361.0,"contact_point_centroid":[0.50158,0.00706,0.04051],"force_p95":109.27256,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":121.03871,"mean_force":56.79817,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4927,0.01117,0.04244]},{"body_a":"peg","body_b":"channel_base_body","contact_count":448.0,"contact_point_centroid":[0.50366,0.00552,0.00825],"force_p95":95.3121,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.36652,"mean_force":42.78239,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49191,0.0242,0.04319]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.49529,-0.0461,0.008],"force_p95":0.74461,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.45908,"mean_force":0.93847,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49717,-0.04081,0.17008]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50889,-0.05477,0.03782],"force_p95":61.48517,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.1121,"mean_force":13.61555,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49864,-0.06033,0.04038]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":154.0,"contact_point_centroid":[0.52544,-0.01145,0.02754],"force_p95":61.71119,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.40887,"mean_force":37.75596,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49315,0.0066,0.04272]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":27.0,"contact_point_centroid":[0.47483,-0.02157,0.0248],"force_p95":10.02643,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.65718,"mean_force":2.67034,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49672,-0.04975,0.09722]},{"body_a":"peg","body_b":"channel_base_body","contact_count":117.0,"contact_point_centroid":[0.49557,0.05897,0.00923],"force_p95":1.17572,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.67089,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48459,0.18948,0.25897]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49746,0.19816,0.29382]},{"body_a":"peg","body_b":"channel_base_body","contact_count":365.0,"contact_point_centroid":[0.49417,0.05896,0.00939],"force_p95":0.55079,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55479,"mean_force":0.54634,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48016,0.14974,0.14059]}],"total_contact_groups":9},"final_pose_error":0.02377,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49418,-0.04542,0.0242],"final_tcp_position":[0.49822,-0.05402,0.30831],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":121.03871,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":146.0,"n_steps_budget":600.0,"object_pos_end":[0.49412,0.05901,0.0338],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13927,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54641,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":152.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_peg","tcp_end":[0.47348,0.18193,0.2296],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.2321,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.4941,0.05908,0.03387],"object_pos_start":[0.49412,0.05901,0.0338],"object_to_goal_dist_end":0.13934,"object_to_goal_dist_start":0.13927,"object_z_max":0.03386,"peak_contact_force":0.54473,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":365.0,"raw_peak_contact_force":0.55479,"subtask_id":"reach_peg","tcp_end":[0.48853,0.11667,0.05136],"tcp_start":[0.47348,0.18193,0.2296],"tcp_to_object_dist_end":0.06045,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":466.0,"n_steps_budget":1000.0,"object_pos_end":[0.50628,-0.04681,0.02105],"object_pos_start":[0.4941,0.05908,0.03387],"object_to_goal_dist_end":0.03873,"object_to_goal_dist_start":0.13934,"object_z_max":0.04028,"peak_contact_force":96.77432,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":963.0,"raw_peak_contact_force":121.03871,"subtask_id":"push_through_channel","tcp_end":[0.49939,-0.06024,0.03987],"tcp_start":[0.48853,0.11667,0.05136],"tcp_to_object_dist_end":0.02412,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.49418,-0.04542,0.0242],"object_pos_start":[0.50628,-0.04681,0.02105],"object_to_goal_dist_end":0.03846,"object_to_goal_dist_start":0.03873,"object_z_max":0.02588,"peak_contact_force":0.5339,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":578.0,"raw_peak_contact_force":78.45908,"tcp_end":[0.49822,-0.05402,0.30831],"tcp_start":[0.49939,-0.06024,0.03987],"tcp_to_object_dist_end":0.28427,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06452,"average_solve_count":155.0,"average_success_count":155.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.05608,"approach_1.approach_offset_z":0.10786,"approach_1.approach_speed":0.10064,"descend_1.descend_offset_y":0.05025,"descend_1.descend_speed":0.08203,"push_1.push_speed":0.08547,"retract_1.retract_height":0.12846,"retract_1.retract_speed":0.26261},"optimized_scores":{"best_composite_score":-0.02627,"best_fitness_score":0.43373,"best_task_score":0.20005},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":406.0,"contact_point_centroid":[0.50285,0.01456,0.04343],"force_p95":77.74138,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.98278,"mean_force":49.89825,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50073,0.02047,0.04313]},{"body_a":"peg","body_b":"channel_base_body","contact_count":566.0,"contact_point_centroid":[0.50322,0.02055,0.00903],"force_p95":74.93022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.79379,"mean_force":34.94865,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50088,0.04678,0.04417]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.49617,-0.05936,0.04325],"force_p95":57.86383,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.02982,"mean_force":13.30768,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50069,-0.06006,0.04154]},{"body_a":"peg","body_b":"channel_base_body","contact_count":622.0,"contact_point_centroid":[0.50276,-0.03817,0.00813],"force_p95":0.69711,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.51505,"mean_force":0.8177,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49912,-0.04124,0.16755]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47493,-0.06039,0.02632],"force_p95":40.75402,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.26271,"mean_force":7.75146,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50069,-0.06006,0.04154]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":39.0,"contact_point_centroid":[0.47484,-0.0499,0.0253],"force_p95":32.21737,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.50034,"mean_force":19.09591,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50059,-0.03908,0.04054]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":117.0,"contact_point_centroid":[0.52506,0.03849,0.03297],"force_p95":22.37972,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.7983,"mean_force":14.83331,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50072,0.06398,0.04496]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":10.0,"contact_point_centroid":[0.52501,-0.01552,0.02441],"force_p95":7.23443,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.41578,"mean_force":3.01778,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49856,-0.03704,0.11952]},{"body_a":"peg","body_b":"channel_base_body","contact_count":100.0,"contact_point_centroid":[0.5045,0.08075,0.00925],"force_p95":1.67955,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.69945,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51349,0.19405,0.26625]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50215,0.1989,0.29426]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.50602,0.0809,0.00938],"force_p95":0.55013,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55543,"mean_force":0.54674,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51394,0.1768,0.14881]}],"total_contact_groups":11},"final_pose_error":0.02084,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50419,-0.03803,0.02414],"final_tcp_position":[0.49998,-0.05461,0.29882],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":84.98278,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":129.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08088,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54821,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":136.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_peg","tcp_end":[0.52367,0.19001,0.24333],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.23693,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50596,0.08088,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16111,"object_z_max":0.03378,"peak_contact_force":0.54819,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":359.0,"raw_peak_contact_force":0.55543,"subtask_id":"reach_peg","tcp_end":[0.50472,0.16344,0.05311],"tcp_start":[0.52367,0.19001,0.24333],"tcp_to_object_dist_end":0.08482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.49566,-0.03709,0.02613],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.0453,"object_to_goal_dist_start":0.1611,"object_z_max":0.03994,"peak_contact_force":75.78571,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1128.0,"raw_peak_contact_force":84.98278,"subtask_id":"push_through_channel","tcp_end":[0.50142,-0.06008,0.0404],"tcp_start":[0.50472,0.16344,0.05311],"tcp_to_object_dist_end":0.02767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":622.0,"n_steps_budget":690.0,"object_pos_end":[0.50419,-0.03803,0.02414],"object_pos_start":[0.49566,-0.03709,0.02613],"object_to_goal_dist_end":0.04507,"object_to_goal_dist_start":0.0453,"object_z_max":0.02618,"peak_contact_force":0.54233,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":658.0,"raw_peak_contact_force":63.02982,"tcp_end":[0.49998,-0.05461,0.29882],"tcp_start":[0.50142,-0.06008,0.0404],"tcp_to_object_dist_end":0.27521,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1844,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_offset_y":0.06543,"approach_1.approach_offset_z":0.08027,"approach_1.approach_speed":0.369,"descend_1.descend_offset_y":0.04353,"descend_1.descend_speed":0.09372,"push_1.push_speed":0.09195,"retract_1.retract_height":0.16649,"retract_1.retract_speed":0.48706},"optimized_scores":{"best_composite_score":0.039,"best_fitness_score":0.499,"best_task_score":0.42067},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_right_wall","contact_count":26.0,"contact_point_centroid":[0.47456,-0.02621,0.05998],"force_p95":70.85288,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.00842,"mean_force":15.5896,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49456,-0.05557,0.0494]},{"body_a":"attachment","body_b":"peg","contact_count":26.0,"contact_point_centroid":[0.49469,-0.04281,0.05956],"force_p95":67.62252,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.80488,"mean_force":14.78663,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49462,-0.05436,0.05289]},{"body_a":"attachment","body_b":"peg","contact_count":334.0,"contact_point_centroid":[0.50167,0.04678,0.0445],"force_p95":63.4758,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.13219,"mean_force":41.53952,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50067,0.04663,0.04383]},{"body_a":"peg","body_b":"channel_base_body","contact_count":573.0,"contact_point_centroid":[0.50155,0.05039,0.0093],"force_p95":59.46846,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.22995,"mean_force":23.46374,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50041,0.06271,0.04408]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":92.0,"contact_point_centroid":[0.47495,0.00067,0.02629],"force_p95":20.77342,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.91198,"mean_force":13.03505,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50122,-0.00287,0.04249]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.52501,0.06436,0.04596],"force_p95":21.79495,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.95427,"mean_force":17.61055,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50072,0.09974,0.04604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":518.0,"contact_point_centroid":[0.50389,-0.0335,0.00944],"force_p95":0.78545,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.02934,"mean_force":0.59372,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49532,-0.03897,0.18429]},{"body_a":"peg","body_b":"channel_base_body","contact_count":141.0,"contact_point_centroid":[0.50483,0.10488,0.00933],"force_p95":0.90704,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.6267,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.509,0.20778,0.25345]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50099,0.20067,0.29454]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52528,-0.03072,0.05998],"force_p95":0.76473,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82973,"mean_force":0.39274,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49443,-0.04349,0.08574]},{"body_a":"peg","body_b":"channel_base_body","contact_count":311.0,"contact_point_centroid":[0.50584,0.10462,0.00939],"force_p95":0.57494,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58307,"mean_force":0.54631,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51007,0.1984,0.13585]}],"total_contact_groups":11},"final_pose_error":0.02533,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50473,-0.0355,0.03379],"final_tcp_position":[0.49646,-0.0539,0.32887],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":99.00842,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":168.0,"n_steps_budget":600.0,"object_pos_end":[0.50601,0.10462,0.03382],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18482,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55656,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":173.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_peg","tcp_end":[0.51682,0.21452,0.21793],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.21468,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.506,0.10468,0.03384],"object_pos_start":[0.50601,0.10462,0.03382],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18482,"object_z_max":0.03384,"peak_contact_force":0.55236,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":311.0,"raw_peak_contact_force":0.58307,"subtask_id":"reach_peg","tcp_end":[0.50417,0.18181,0.05297],"tcp_start":[0.51682,0.21452,0.21793],"tcp_to_object_dist_end":0.07949,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":598.0,"n_steps_budget":1000.0,"object_pos_end":[0.49893,-0.01326,0.03809],"object_pos_start":[0.506,0.10468,0.03384],"object_to_goal_dist_end":0.06678,"object_to_goal_dist_start":0.18488,"object_z_max":0.04125,"peak_contact_force":0.49833,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1039.0,"raw_peak_contact_force":71.13219,"subtask_id":"push_through_channel","tcp_end":[0.49734,-0.06062,0.03678],"tcp_start":[0.50417,0.18181,0.05297],"tcp_to_object_dist_end":0.04741,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.50473,-0.0355,0.03379],"object_pos_start":[0.49893,-0.01326,0.03809],"object_to_goal_dist_end":0.04518,"object_to_goal_dist_start":0.06678,"object_z_max":0.04053,"peak_contact_force":0.54681,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":579.0,"raw_peak_contact_force":99.00842,"tcp_end":[0.49646,-0.0539,0.32887],"tcp_start":[0.49734,-0.06062,0.03678],"tcp_to_object_dist_end":0.29577,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```