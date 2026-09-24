## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | 0.0474 | 0.29 | ✅ accepted |
| 13 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 4 | -0.0590 | 0.26 | ✅ accepted |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.0054 | 0.21 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0306 | 0.00 | ❌ rejected |
| 10 | approach → descend → insert | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.1299 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.29 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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
| `object` | offset from object initial position (0.5100076373283734, 0.11177710407756605, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5100076373283734, -0.04822289592243395, 0.04) | final destination targets |
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

## Current Skill (Q=0.047) — your mutation base

```yaml
skill: peg_channel
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: approach_peg
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.2
  weight: 0.2
- id: align_to_peg
  anchor: object
  offset:
  - 0.0
  - 0.03
  - 0.0
  weight: 0.3
- id: push_through_channel
  offset:
  - 0.0
  - -0.04
  - 0.0
  weight: 0.5
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
    - 0.0
    - 0.2
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_peg
- id: move_behind_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
    - 0.2
    orientation:
      mode: keep_current
  parameters:
    align_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: align_to_peg
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: peg
    offset:
    - 0.0
    - 0.03
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
        mode: replace
  subtask_id: align_to_peg
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: time_limit
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - -0.04
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    push_max_time:
      type: scalar
      range:
      - 2.0
      - 10.0
      default: 6.0
      binds_to:
      - path: duration.max_time
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.005
      - 0.05
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: push_through_channel

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.0, 0.2]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **move_behind_1** (`align`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.2]
  - orientation: mode=keep_current
  - parameter_bindings:
    - align_speed: status=consumed; consumers=generator.speed (replace)
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=peg, offset=[0.0, 0.03, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, -0.04, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_max_time: status=consumed; consumers=duration.max_time (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)

## Design Metrics

- **Composite score**: 0.047
- **task_score** (E): 0.290
- **fitness_score**: 0.357  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1118 |
| move_behind_1 | 1.00 | 1.00 | 0.0172 |
| descend_1 | 1.00 | 1.00 | 0.1905 |
| push_1 | 1.00 | 1.00 | 0.0789 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.506, 0.107, 0.241) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.540 | 2.732 |
| move_behind_1 | align | 1.00 / step_budget | (0.506, 0.107, 0.241)→(0.501, 0.119, 0.232) | (0.502, 0.098, 0.034)→(0.502, 0.098, 0.034) | 0.178→0.178 | 1.00 / 1.000 | 0.530 | 0.586 |
| descend_1 | descend | 1.00 / step_budget | (0.501, 0.119, 0.232)→(0.500, 0.130, 0.042) | (0.502, 0.098, 0.034)→(0.503, 0.098, 0.033) | 0.178→0.178 | 1.00 / 2.000 | 45.154 | 116.282 |
| push_1 | push | 1.00 / time_limit | (0.500, 0.130, 0.042)→(0.501, 0.052, 0.041) | (0.503, 0.098, 0.033)→(0.502, 0.035, 0.034) | 0.178→0.115 | 1.00 / 3.000 | 53.598 | 65.434 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.457
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.457
- phase_score: 0.427
- phase_breakdown.align_to_peg_score: 0.836
- phase_breakdown.approach_peg_score: 0.821
- phase_breakdown.push_through_channel_score: 0.024

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.439
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.457
- **Median Q (composite search score)**: 0.009
- **K-run variance**: 0.0033
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: push_1.push_speed
- **Final σ (mean)**: 0.278


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.90594,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05413,"descend_1.descend_speed":0.03887,"move_behind_1.align_speed":0.07434,"push_1.push_max_time":5.86039,"push_1.push_speed":0.03215},"optimized_scores":{"best_composite_score":0.12907,"best_fitness_score":0.43907,"best_task_score":0.45711},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":669.0,"contact_point_centroid":[0.50422,0.11181,0.00932],"force_p95":73.78446,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":123.82607,"mean_force":6.35741,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50077,0.13594,0.13593]},{"body_a":"attachment","body_b":"peg","contact_count":52.0,"contact_point_centroid":[0.50748,0.13125,0.05569],"force_p95":121.61666,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":123.15932,"mean_force":74.82918,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5016,0.14109,0.05503]},{"body_a":"peg","body_b":"channel_base_body","contact_count":747.0,"contact_point_centroid":[0.5063,0.05964,0.00993],"force_p95":4.93221,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.72383,"mean_force":2.90545,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49781,0.10431,0.0384]},{"body_a":"attachment","body_b":"peg","contact_count":863.0,"contact_point_centroid":[0.50167,0.09023,0.04079],"force_p95":5.37479,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.16039,"mean_force":2.41708,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49767,0.10164,0.03822]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":573.0,"contact_point_centroid":[0.52502,0.07119,0.0207],"force_p95":2.05449,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.79679,"mean_force":1.04993,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49761,0.09872,0.03815]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.50356,0.11166,0.00935],"force_p95":0.62733,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.56575,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50259,0.15866,0.26777]},{"body_a":"peg","body_b":"channel_base_body","contact_count":71.0,"contact_point_centroid":[0.50383,0.11156,0.00942],"force_p95":0.5714,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58042,"mean_force":0.54381,"phase_index":1.0,"phase_name":"move_behind_1","phase_type":"align","tcp_position_centroid":[0.50481,0.12533,0.23713]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49969,0.19896,0.29934]}],"total_contact_groups":8},"final_pose_error":0.18689,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50702,0.03864,0.03597],"final_tcp_position":[0.49736,0.06686,0.03778],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":123.82607,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11176,0.0339],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.55362,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":384.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_peg","tcp_end":[0.50656,0.12088,0.24147],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20779,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":71.0,"n_steps_budget":600.0,"object_pos_end":[0.50371,0.11176,0.03379],"object_pos_start":[0.50371,0.11176,0.0339],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19189,"object_z_max":0.0339,"peak_contact_force":0.5211,"phase_name":"move_behind_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":71.0,"raw_peak_contact_force":0.58042,"subtask_id":"align_to_peg","tcp_end":[0.50314,0.13183,0.23325],"tcp_start":[0.50656,0.12088,0.24147],"tcp_to_object_dist_end":0.20047,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.50422,0.10609,0.035],"object_pos_start":[0.50371,0.11176,0.03379],"object_to_goal_dist_end":0.1862,"object_to_goal_dist_start":0.1919,"object_z_max":0.03485,"peak_contact_force":0.38123,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":721.0,"raw_peak_contact_force":123.82607,"subtask_id":"align_to_peg","tcp_end":[0.50172,0.14194,0.04334],"tcp_start":[0.50314,0.13183,0.23325],"tcp_to_object_dist_end":0.0369,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50702,0.03864,0.03597],"object_pos_start":[0.50422,0.10609,0.035],"object_to_goal_dist_end":0.11892,"object_to_goal_dist_start":0.1862,"object_z_max":0.03606,"peak_contact_force":4.57803,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2183.0,"raw_peak_contact_force":9.72383,"subtask_id":"push_through_channel","tcp_end":[0.49736,0.06686,0.03778],"tcp_start":[0.50172,0.14194,0.04334],"tcp_to_object_dist_end":0.02988,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96209,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06241,"descend_1.descend_speed":0.02959,"move_behind_1.align_speed":0.05747,"push_1.push_max_time":4.804,"push_1.push_speed":0.0275},"optimized_scores":{"best_composite_score":0.0095,"best_fitness_score":0.3195,"best_task_score":0.19682},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50547,0.10425,0.0073],"force_p95":173.52161,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.79915,"mean_force":142.48223,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50293,0.12304,0.04728]},{"body_a":"attachment","body_b":"peg","contact_count":1000.0,"contact_point_centroid":[0.50745,0.11427,0.04934],"force_p95":172.99446,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":177.28736,"mean_force":143.3667,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50293,0.12304,0.04728]},{"body_a":"attachment","body_b":"peg","contact_count":137.0,"contact_point_centroid":[0.49924,0.14206,0.04915],"force_p95":129.50946,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":133.38746,"mean_force":96.27266,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49459,0.15227,0.04843]},{"body_a":"peg","body_b":"channel_base_body","contact_count":743.0,"contact_point_centroid":[0.49679,0.11913,0.00917],"force_p95":104.10503,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":124.94563,"mean_force":16.9728,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49082,0.14516,0.12828]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":332.0,"contact_point_centroid":[0.47458,0.08988,0.01192],"force_p95":27.33848,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.21666,"mean_force":16.61329,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50595,0.0946,0.04893]},{"body_a":"peg","body_b":"world","contact_count":52.0,"contact_point_centroid":[0.49733,0.12654,-0.00019],"force_p95":27.91686,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.20733,"mean_force":20.03507,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49616,0.15574,0.04286]},{"body_a":"peg","body_b":"world","contact_count":17.0,"contact_point_centroid":[0.49724,0.12484,-0.00012],"force_p95":14.4824,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.81898,"mean_force":8.15159,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49664,0.15808,0.04105]},{"body_a":"peg","body_b":"channel_base_body","contact_count":312.0,"contact_point_centroid":[0.49634,0.11915,0.0094],"force_p95":0.64147,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.5647,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49177,0.16239,0.26828]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49924,0.19824,0.29845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":93.0,"contact_point_centroid":[0.49603,0.11907,0.00948],"force_p95":0.60072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62274,"mean_force":0.54014,"phase_index":1.0,"phase_name":"move_behind_1","phase_type":"align","tcp_position_centroid":[0.48753,0.13401,0.23737]}],"total_contact_groups":10},"final_pose_error":0.20191,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49188,0.08634,0.02984],"final_tcp_position":[0.50655,0.0816,0.04911],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":177.79915,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":337.0,"n_steps_budget":1000.0,"object_pos_end":[0.49604,0.11902,0.03407],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19915,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51489,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":336.0,"raw_peak_contact_force":2.24822,"subtask_id":"approach_peg","tcp_end":[0.48563,0.12848,0.24268],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20909,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":93.0,"n_steps_budget":600.0,"object_pos_end":[0.49602,0.11898,0.03383],"object_pos_start":[0.49604,0.11902,0.03407],"object_to_goal_dist_end":0.19911,"object_to_goal_dist_start":0.19915,"object_z_max":0.03411,"peak_contact_force":0.52325,"phase_name":"move_behind_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":93.0,"raw_peak_contact_force":0.62274,"subtask_id":"align_to_peg","tcp_end":[0.49029,0.141,0.23295],"tcp_start":[0.48563,0.12848,0.24268],"tcp_to_object_dist_end":0.20041,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":743.0,"n_steps_budget":1000.0,"object_pos_end":[0.49741,0.12506,0.03026],"object_pos_start":[0.49602,0.11898,0.03383],"object_to_goal_dist_end":0.2053,"object_to_goal_dist_start":0.19911,"object_z_max":0.03403,"peak_contact_force":127.77758,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":932.0,"raw_peak_contact_force":133.38746,"subtask_id":"align_to_peg","tcp_end":[0.4967,0.1576,0.04094],"tcp_start":[0.49029,0.141,0.23295],"tcp_to_object_dist_end":0.03425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49188,0.08634,0.02984],"object_pos_start":[0.49741,0.12506,0.03026],"object_to_goal_dist_end":0.16685,"object_to_goal_dist_start":0.2053,"object_z_max":0.03117,"peak_contact_force":150.92782,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2349.0,"raw_peak_contact_force":177.79915,"subtask_id":"push_through_channel","tcp_end":[0.50655,0.0816,0.04911],"tcp_start":[0.4967,0.1576,0.04094],"tcp_to_object_dist_end":0.02468,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.77055,"average_solve_count":292.0,"average_success_count":292.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.02691,"descend_1.descend_speed":0.03,"move_behind_1.align_speed":0.0482,"push_1.push_max_time":7.37275,"push_1.push_speed":0.05},"optimized_scores":{"best_composite_score":0.00352,"best_fitness_score":0.31352,"best_task_score":0.21665},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":647.0,"contact_point_centroid":[0.50588,0.06194,0.00939],"force_p95":0.55393,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.63314,"mean_force":1.6924,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50581,0.0881,0.13667]},{"body_a":"attachment","body_b":"peg","contact_count":18.0,"contact_point_centroid":[0.50737,0.08053,0.05759],"force_p95":90.61784,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.19976,"mean_force":41.5624,"phase_index":2.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5034,0.09132,0.05635]},{"body_a":"peg","body_b":"channel_base_body","contact_count":717.0,"contact_point_centroid":[0.5064,0.00414,0.00996],"force_p95":5.67246,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.77918,"mean_force":3.42898,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49867,0.04953,0.03801]},{"body_a":"attachment","body_b":"peg","contact_count":892.0,"contact_point_centroid":[0.50236,0.03745,0.04151],"force_p95":5.54114,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.37565,"mean_force":2.6358,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49863,0.04901,0.03796]},{"body_a":"peg","body_b":"channel_base_body","contact_count":656.0,"contact_point_centroid":[0.50574,0.063,0.00936],"force_p95":0.5603,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56719,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51221,0.13275,0.26592]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49975,0.19762,0.29819]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":504.0,"contact_point_centroid":[0.52502,0.0162,0.01916],"force_p95":2.09483,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.73854,"mean_force":1.01205,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49847,0.04399,0.0378]},{"body_a":"peg","body_b":"channel_base_body","contact_count":93.0,"contact_point_centroid":[0.5065,0.06314,0.00938],"force_p95":0.55123,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55422,"mean_force":0.54652,"phase_index":1.0,"phase_name":"move_behind_1","phase_type":"align","tcp_position_centroid":[0.51825,0.07732,0.23434]}],"total_contact_groups":8},"final_pose_error":0.12799,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50705,-0.02051,0.03598],"final_tcp_position":[0.4979,0.00795,0.03725],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":91.63314,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":684.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06303,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14329,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.5502,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":690.0,"raw_peak_contact_force":3.88411,"subtask_id":"approach_peg","tcp_end":[0.5252,0.07166,0.23866],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.20594,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":93.0,"n_steps_budget":600.0,"object_pos_end":[0.50601,0.06294,0.0338],"object_pos_start":[0.50601,0.06303,0.0338],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14329,"object_z_max":0.03381,"peak_contact_force":0.54696,"phase_name":"move_behind_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":93.0,"raw_peak_contact_force":0.55422,"subtask_id":"align_to_peg","tcp_end":[0.51084,0.08485,0.23114],"tcp_start":[0.5252,0.07166,0.23866],"tcp_to_object_dist_end":0.1986,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":647.0,"n_steps_budget":1000.0,"object_pos_end":[0.50645,0.06268,0.03501],"object_pos_start":[0.50601,0.06294,0.0338],"object_to_goal_dist_end":0.14291,"object_to_goal_dist_start":0.1432,"object_z_max":0.03648,"peak_contact_force":7.30437,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":665.0,"raw_peak_contact_force":91.63314,"subtask_id":"align_to_peg","tcp_end":[0.50293,0.09184,0.04298],"tcp_start":[0.51084,0.08485,0.23114],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50705,-0.02051,0.03598],"object_pos_start":[0.50645,0.06268,0.03501],"object_to_goal_dist_end":0.06004,"object_to_goal_dist_start":0.14291,"object_z_max":0.03604,"peak_contact_force":5.2885,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2113.0,"raw_peak_contact_force":8.77918,"subtask_id":"push_through_channel","tcp_end":[0.4979,0.00795,0.03725],"tcp_start":[0.50293,0.09184,0.04298],"tcp_to_object_dist_end":0.02992,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
```