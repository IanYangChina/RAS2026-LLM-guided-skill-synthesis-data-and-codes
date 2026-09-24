## Search State

- **Seed**: 7
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.1048 | 0.01 | ❌ rejected |
| 5 | descend → approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7 | -0.2446 | 0.00 | ❌ rejected |
| 4 | descend → approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0575 | 0.03 | ❌ rejected |
| 3 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |
| 2 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ✅ accepted |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5100076373283734, -0.04822289592243395, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, -0.04822289592243395, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5100076373283734, 0.11177710407756605, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5100076373283734, 0.11177710407756605, 0.04]
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
  frozen_object_starts: {'peg': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
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
| `object` | offset from object initial position (0.5100076373283734, -0.04822289592243395, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
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

## Current Skill (Q=-0.105) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: insert_1
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: pose_tolerance
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01

```

## Design Metrics

- **Composite score**: -0.105
- **task_score** (E): 0.012
- **fitness_score**: 0.089  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1830 |
| descend_1 | 1.00 | 1.00 | 0.0972 |
| push_1 | 0.67 | 1.00 | 0.0197 |
| retract_1 | 0.00 | 1.00 | 0.1340 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.104, 0.146) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.551 | 2.732 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.104, 0.146)→(0.503, 0.099, 0.050) | (0.502, 0.098, 0.034)→(0.502, 0.111, 0.024) | 0.178→0.192 | 1.00 / 2.333 | 149.592 | 207.983 |
| push_1 | push | 0.67 / force_exceeded | (0.503, 0.099, 0.050)→(0.502, 0.080, 0.048) | (0.502, 0.111, 0.024)→(0.511, 0.111, 0.025) | 0.192→0.193 | 1.00 / 2.333 | 89.934 | 90.075 |
| retract_1 | retract | 0.00 / step_budget | (0.502, 0.080, 0.048)→(0.372, 0.057, 0.065) | (0.511, 0.111, 0.025)→(0.530, 0.109, 0.027) | 0.193→0.196 | 1.00 / 1.333 | 29.320 | 200.674 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.028
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.006
- phase_score: 0.150
- phase_breakdown.push_exit_score: 0.054
- phase_breakdown.reach_peg_score: 0.534

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.092
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.029
- **Median Q (composite search score)**: -0.021
- **K-run variance**: 0.0145
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.289


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
{"anchors":[{"name":"object","value":[0.51001,-0.04822,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,-0.04822,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24118,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0604,"descend_1.speed":0.034,"push_1.push_distance":0.16085,"push_1.push_force_threshold":15.75544,"push_1.speed":0.02543,"retract_1.speed":0.05829},"optimized_scores":{"best_composite_score":-0.02143,"best_fitness_score":0.08857,"best_task_score":0.02921},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":138.0,"contact_point_centroid":[0.52509,0.11366,0.05996],"force_p95":282.98622,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.55742,"mean_force":179.26856,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50835,0.11363,0.05108]},{"body_a":"peg","body_b":"channel_base_body","contact_count":529.0,"contact_point_centroid":[0.51007,0.11226,0.00834],"force_p95":199.29754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":203.81272,"mean_force":74.96164,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50442,0.11428,0.08114]},{"body_a":"attachment","body_b":"peg","contact_count":246.0,"contact_point_centroid":[0.51768,0.11345,0.05135],"force_p95":200.92549,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":203.3474,"mean_force":160.0815,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50664,0.1134,0.05311]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52286,0.11201,0.00685],"force_p95":162.88801,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":162.88801,"mean_force":162.88801,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50813,0.11373,0.051]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51913,0.1138,0.04996],"force_p95":162.26022,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":162.26022,"mean_force":162.26022,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50813,0.11373,0.051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49005,0.10383,0.00876],"force_p95":115.58283,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":151.06097,"mean_force":36.08406,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.45714,0.10032,0.06098]},{"body_a":"attachment","body_b":"peg","contact_count":595.0,"contact_point_centroid":[0.49017,0.10627,0.05548],"force_p95":123.23851,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":150.46994,"mean_force":59.55882,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47932,0.10594,0.05939]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":580.0,"contact_point_centroid":[0.46958,0.10758,0.05996],"force_p95":109.82214,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":147.46953,"mean_force":83.16488,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46336,0.10095,0.06269]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52504,0.1138,0.05998],"force_p95":89.12027,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":99.02252,"mean_force":33.00751,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50811,0.11376,0.05104]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":520.0,"contact_point_centroid":[0.47453,0.10428,0.04719],"force_p95":30.35788,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.65603,"mean_force":8.12271,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4686,0.10285,0.0614]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52505,0.11377,0.05998],"force_p95":39.17739,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":39.17739,"mean_force":39.17739,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50813,0.11373,0.051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":566.0,"contact_point_centroid":[0.50358,0.11161,0.00939],"force_p95":0.61226,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55721,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50227,0.15779,0.22027]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4997,0.19923,0.29911]}],"total_contact_groups":13},"final_pose_error":0.36914,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49303,0.10327,0.03379],"final_tcp_position":[0.35833,0.08017,0.06214],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":322.55742,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":588.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11176,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19189,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.59174,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":582.0,"raw_peak_contact_force":2.06328,"subtask_id":"reach_peg","tcp_end":[0.50614,0.11771,0.14695],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11333,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.50501,0.11004,0.02871],"object_pos_start":[0.50368,0.11176,0.0338],"object_to_goal_dist_end":0.19044,"object_to_goal_dist_start":0.19189,"object_z_max":0.03389,"peak_contact_force":198.76919,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":913.0,"raw_peak_contact_force":322.55742,"subtask_id":"reach_peg","tcp_end":[0.50813,0.11373,0.051],"tcp_start":[0.50614,0.11771,0.14695],"tcp_to_object_dist_end":0.02281,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.505,0.11005,0.02871],"object_pos_start":[0.50501,0.11004,0.02871],"object_to_goal_dist_end":0.19045,"object_to_goal_dist_start":0.19044,"object_z_max":0.02871,"peak_contact_force":162.88801,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":162.88801,"subtask_id":"push_exit","tcp_end":[0.50812,0.11374,0.05102],"tcp_start":[0.50813,0.11373,0.051],"tcp_to_object_dist_end":0.02283,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49303,0.10327,0.03379],"object_pos_start":[0.505,0.11005,0.02871],"object_to_goal_dist_end":0.18351,"object_to_goal_dist_start":0.19045,"object_z_max":0.03474,"peak_contact_force":0.54884,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2698.0,"raw_peak_contact_force":151.06097,"tcp_end":[0.35833,0.08017,0.06214],"tcp_start":[0.50812,0.11374,0.05102],"tcp_to_object_dist_end":0.13958,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,-0.04102,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,-0.04102,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13171,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04114,"descend_1.speed":0.05769,"push_1.push_distance":0.19868,"push_1.push_force_threshold":25.00329,"push_1.speed":0.01001,"retract_1.speed":0.02951},"optimized_scores":{"best_composite_score":-0.2752,"best_fitness_score":0.0848,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":920.0,"contact_point_centroid":[0.47324,0.05472,0.05276],"force_p95":216.12474,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":295.96351,"mean_force":134.89613,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47812,0.05633,0.05106]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.52982,0.06191,0.05993],"force_p95":147.16872,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.6376,"mean_force":95.16276,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48465,0.05979,0.03723]},{"body_a":"peg","body_b":"world","contact_count":74.0,"contact_point_centroid":[0.49495,0.14837,-0.00094],"force_p95":1.60977,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.88335,"mean_force":0.67681,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48964,0.11954,0.05396]},{"body_a":"peg","body_b":"channel_base_body","contact_count":547.0,"contact_point_centroid":[0.49627,0.11911,0.00945],"force_p95":0.60509,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55255,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49112,0.16113,0.2204]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.50438,0.16055,-0.00195],"force_p95":0.71222,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99308,"mean_force":0.60539,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4868,0.08809,0.03767]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49941,0.1989,0.29815]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.55888,0.16303,-0.00194],"force_p95":0.64396,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64397,"mean_force":0.60616,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47798,0.05629,0.05127]},{"body_a":"peg","body_b":"channel_base_body","contact_count":298.0,"contact_point_centroid":[0.49561,0.1196,0.00942],"force_p95":0.59779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62304,"mean_force":0.52406,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48532,0.12207,0.10565]}],"total_contact_groups":8},"final_pose_error":0.44946,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.60364,0.16485,0.01415],"final_tcp_position":[0.44489,0.05186,0.06251],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":295.96351,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":572.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11924,0.03384],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19937,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.50922,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":571.0,"raw_peak_contact_force":2.24822,"subtask_id":"reach_peg","tcp_end":[0.48421,0.12458,0.14777],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11466,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":375.0,"n_steps_budget":1000.0,"object_pos_end":[0.49441,0.16022,0.01346],"object_pos_start":[0.49601,0.11924,0.03384],"object_to_goal_dist_end":0.24175,"object_to_goal_dist_start":0.19937,"object_z_max":0.03385,"peak_contact_force":0.53136,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":372.0,"raw_peak_contact_force":2.88335,"subtask_id":"reach_peg","tcp_end":[0.49073,0.11897,0.04229],"tcp_start":[0.48421,0.12458,0.14777],"tcp_to_object_dist_end":0.05046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52305,0.16146,0.01415],"object_pos_start":[0.49441,0.16022,0.01346],"object_to_goal_dist_end":0.24394,"object_to_goal_dist_start":0.24175,"object_z_max":0.01445,"peak_contact_force":0.56852,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.99308,"subtask_id":"push_exit","tcp_end":[0.48661,0.06025,0.03754],"tcp_start":[0.49073,0.11897,0.04229],"tcp_to_object_dist_end":0.11008,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.60364,0.16485,0.01415],"object_pos_start":[0.52305,0.16146,0.01415],"object_to_goal_dist_end":0.26714,"object_to_goal_dist_start":0.24394,"object_z_max":0.01415,"peak_contact_force":86.85872,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1934.0,"raw_peak_contact_force":295.96351,"tcp_end":[0.44489,0.05186,0.06251],"tcp_start":[0.48661,0.06025,0.03754],"tcp_to_object_dist_end":0.20078,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,-0.09705,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,-0.09705,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90441,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07393,"descend_1.speed":0.09307,"push_1.push_distance":0.17744,"push_1.push_force_threshold":16.79332,"push_1.speed":0.03294,"retract_1.speed":0.04395},"optimized_scores":{"best_composite_score":-0.01764,"best_fitness_score":0.09236,"best_task_score":0.00582},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":83.0,"contact_point_centroid":[0.52516,0.06474,0.05993],"force_p95":269.93084,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":298.50773,"mean_force":220.28972,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51034,0.06474,0.05565]},{"body_a":"peg","body_b":"channel_base_body","contact_count":371.0,"contact_point_centroid":[0.51095,0.06345,0.00897],"force_p95":136.19828,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":174.51554,"mean_force":41.92078,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5138,0.06658,0.08796]},{"body_a":"attachment","body_b":"peg","contact_count":127.0,"contact_point_centroid":[0.52083,0.06465,0.05422],"force_p95":154.40568,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":173.72847,"mean_force":120.92188,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50984,0.06473,0.05688]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":340.0,"contact_point_centroid":[0.47136,0.06358,0.05995],"force_p95":125.92587,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.99801,"mean_force":85.90215,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.46356,0.05746,0.06407]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52262,0.05539,0.00782],"force_p95":106.34508,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.34508,"mean_force":106.34508,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50999,0.06477,0.05566]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.52091,0.06475,0.05316],"force_p95":105.78574,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.78574,"mean_force":105.78574,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50999,0.06477,0.05566]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49045,0.05882,0.00908],"force_p95":79.47225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":102.21432,"mean_force":21.6316,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.43107,0.05411,0.06343]},{"body_a":"attachment","body_b":"peg","contact_count":463.0,"contact_point_centroid":[0.48974,0.0603,0.05651],"force_p95":85.2473,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.72132,"mean_force":45.10431,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4791,0.06012,0.06118]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":494.0,"contact_point_centroid":[0.47463,0.05889,0.04882],"force_p95":28.51896,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.44641,"mean_force":7.22452,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4449,0.05566,0.06346]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52506,0.06477,0.05997],"force_p95":23.86335,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":23.86335,"mean_force":23.86335,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50999,0.06477,0.05566]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52503,0.06284,0.05227],"force_p95":5.76948,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.32909,"mean_force":1.42171,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51052,0.06468,0.05578]},{"body_a":"peg","body_b":"channel_base_body","contact_count":686.0,"contact_point_centroid":[0.50575,0.063,0.00936],"force_p95":0.55989,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51185,0.13275,0.21745]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4998,0.19769,0.29689]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52507,0.06479,0.05997],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51002,0.06478,0.0557]}],"total_contact_groups":14},"final_pose_error":0.31721,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49301,0.05843,0.03378],"final_tcp_position":[0.31328,0.03984,0.07008],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":298.50773,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":714.0,"n_steps_budget":1000.0,"object_pos_end":[0.50602,0.06302,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55136,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":720.0,"raw_peak_contact_force":3.88411,"subtask_id":"reach_peg","tcp_end":[0.52466,0.07042,0.14393],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":371.0,"n_steps_budget":780.0,"object_pos_end":[0.50623,0.06276,0.03065],"object_pos_start":[0.50602,0.06302,0.03381],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14328,"object_z_max":0.03381,"peak_contact_force":249.47607,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":593.0,"raw_peak_contact_force":298.50773,"subtask_id":"reach_peg","tcp_end":[0.50999,0.06477,0.05566],"tcp_start":[0.52466,0.07042,0.14393],"tcp_to_object_dist_end":0.02536,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50622,0.06276,0.03065],"object_pos_start":[0.50623,0.06276,0.03065],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.1432,"object_z_max":0.03065,"peak_contact_force":106.34508,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3.0,"raw_peak_contact_force":106.34508,"subtask_id":"push_exit","tcp_end":[0.51002,0.06478,0.05566],"tcp_start":[0.50999,0.06477,0.05566],"tcp_to_object_dist_end":0.02537,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49301,0.05843,0.03378],"object_pos_start":[0.50622,0.06276,0.03065],"object_to_goal_dist_end":0.13874,"object_to_goal_dist_start":0.1432,"object_z_max":0.03475,"peak_contact_force":0.55367,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2301.0,"raw_peak_contact_force":154.99801,"tcp_end":[0.31328,0.03984,0.07008],"tcp_start":[0.51002,0.06478,0.05566],"tcp_to_object_dist_end":0.1843,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```