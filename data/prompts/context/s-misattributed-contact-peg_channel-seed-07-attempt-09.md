## Search State

- **Seed**: 7
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1222 | 0.03 | ❌ rejected |
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1805 | 0.00 | ❌ rejected |
| 7 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ✅ accepted |
| 6 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.2034 | 0.00 | ❌ rejected |
| 5 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1315 | 0.26 | ❌ rejected |

**Proposal policy**: task_score is 0.03 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.122) — your mutation base

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

- **Composite score**: -0.122
- **task_score** (E): 0.034
- **fitness_score**: 0.158  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1751 |
| descend_1 | 1.00 | 1.00 | 0.1043 |
| push_1 | 0.00 | 1.00 | 0.0293 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.178, 0.129) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.062 | 20.167 |
| descend_1 | descend | 1.00 / step_budget | (0.505, 0.178, 0.129)→(0.499, 0.124, 0.040) | (0.502, 0.098, 0.034)→(0.502, 0.094, 0.036) | 0.178→0.174 | 1.00 / 2.333 | 859.251 | 1288.589 |
| push_1 | push | 0.00 / guard_failure | (0.499, 0.124, 0.040)→(0.491, 0.149, 0.027) | (0.502, 0.094, 0.036)→(0.502, 0.090, 0.034) | 0.174→0.170 | 1.00 / 1.000 | 0.557 | 2.732 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.046
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.034
- phase_score: 0.269
- phase_breakdown.insertion_score: 0.017
- phase_breakdown.pre_insertion_score: 0.856

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.175
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.051
- **Median Q (composite search score)**: -0.108
- **K-run variance**: 0.0005
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
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
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.49,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07759,"descend_1.speed":0.04952,"push_1.lateral_offset_x":-0.00617,"push_1.lateral_offset_y":-0.00322,"push_1.push_speed":0.0286},"optimized_scores":{"best_composite_score":-0.10756,"best_fitness_score":0.17244,"best_task_score":0.05065},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55495,0.09395,0.05919],"force_p95":1277.18858,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1277.18858,"mean_force":1277.18858,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49142,0.16146,0.02843]},{"body_a":"peg","body_b":"channel_base_body","contact_count":347.0,"contact_point_centroid":[0.5035,0.11066,0.00943],"force_p95":0.61741,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.78021,"mean_force":0.92604,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50216,0.16557,0.08503]},{"body_a":"attachment","body_b":"peg","contact_count":16.0,"contact_point_centroid":[0.5025,0.12779,0.05167],"force_p95":19.33989,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.49927,"mean_force":8.56577,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50044,0.13964,0.04302]},{"body_a":"peg","body_b":"channel_base_body","contact_count":512.0,"contact_point_centroid":[0.50355,0.11167,0.00937],"force_p95":0.63058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55902,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50238,0.19511,0.21147]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.50557,0.11585,0.00962],"force_p95":1.0675,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16578,"mean_force":0.59409,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49741,0.14922,0.03512]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49985,0.19959,0.29894]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50352,0.12656,0.06004],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50042,0.13836,0.04049]}],"total_contact_groups":7},"final_pose_error":0.24666,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50477,0.10358,0.03396],"final_tcp_position":[0.49059,0.1631,0.02752],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":1277.18858,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":534.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11184,0.034],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19197,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.09896,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":363.0,"raw_peak_contact_force":19.78021,"subtask_id":"pre_insertion","tcp_end":[0.50612,0.19125,0.12918],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":353.0,"n_steps_budget":1000.0,"object_pos_end":[0.50401,0.10791,0.03592],"object_pos_start":[0.50373,0.11184,0.034],"object_to_goal_dist_end":0.18799,"object_to_goal_dist_start":0.19197,"object_z_max":0.03599,"peak_contact_force":1277.18858,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":1277.18858,"subtask_id":"pre_insertion","tcp_end":[0.50038,0.13825,0.04064],"tcp_start":[0.50612,0.19125,0.12918],"tcp_to_object_dist_end":0.03093,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.50477,0.10358,0.03396],"object_pos_start":[0.50401,0.10791,0.03592],"object_to_goal_dist_end":0.18374,"object_to_goal_dist_start":0.18799,"object_z_max":0.03592,"peak_contact_force":0.54403,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":528.0,"raw_peak_contact_force":2.06328,"subtask_id":"insertion","tcp_end":[0.49059,0.1631,0.02752],"tcp_start":[0.50038,0.13825,0.04064],"tcp_to_object_dist_end":0.06153,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92771,"average_solve_count":83.0,"average_success_count":83.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07976,"descend_1.speed":0.07597,"push_1.lateral_offset_x":0.00507,"push_1.lateral_offset_y":0.01116,"push_1.push_speed":0.03009},"optimized_scores":{"best_composite_score":-0.10529,"best_fitness_score":0.17471,"best_task_score":0.03353},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54608,0.09822,0.05896],"force_p95":1288.01191,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1288.01191,"mean_force":1288.01191,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48153,0.16779,0.02796]},{"body_a":"peg","body_b":"channel_base_body","contact_count":345.0,"contact_point_centroid":[0.49619,0.11833,0.00943],"force_p95":0.60058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.15932,"mean_force":0.77624,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48647,0.17223,0.08511]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49408,0.13452,0.05368],"force_p95":18.66439,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.74751,"mean_force":6.03957,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49094,0.14625,0.04228]},{"body_a":"peg","body_b":"channel_base_body","contact_count":499.0,"contact_point_centroid":[0.49622,0.11903,0.00945],"force_p95":0.6145,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55309,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4913,0.19844,0.21119]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.50224,0.11194,0.00951],"force_p95":1.00498,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.02145,"mean_force":0.80797,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48791,0.15577,0.03462]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49953,0.19956,0.29771]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49522,0.13326,0.06003],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49122,0.14506,0.03995]}],"total_contact_groups":7},"final_pose_error":0.23986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4974,0.11165,0.03379],"final_tcp_position":[0.48066,0.16941,0.02705],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":1288.01191,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.49611,0.11917,0.03396],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1993,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.08568,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":359.0,"raw_peak_contact_force":19.15932,"subtask_id":"pre_insertion","tcp_end":[0.48443,0.19789,0.1297],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1245,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":353.0,"n_steps_budget":930.0,"object_pos_end":[0.49691,0.11508,0.0356],"object_pos_start":[0.49611,0.11917,0.03396],"object_to_goal_dist_end":0.19515,"object_to_goal_dist_start":0.1993,"object_z_max":0.036,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":1288.01191,"subtask_id":"pre_insertion","tcp_end":[0.49117,0.14495,0.0401],"tcp_start":[0.48443,0.19789,0.1297],"tcp_to_object_dist_end":0.03075,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.4974,0.11165,0.03379],"object_pos_start":[0.49691,0.11508,0.0356],"object_to_goal_dist_end":0.19177,"object_to_goal_dist_start":0.19515,"object_z_max":0.0356,"peak_contact_force":0.58134,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":523.0,"raw_peak_contact_force":2.24822,"subtask_id":"insertion","tcp_end":[0.48066,0.16941,0.02705],"tcp_start":[0.49117,0.14495,0.0401],"tcp_to_object_dist_end":0.06052,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28448,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04952,"descend_1.speed":0.07467,"push_1.lateral_offset_x":0.01206,"push_1.lateral_offset_y":-0.00675,"push_1.push_speed":0.04453},"optimized_scores":{"best_composite_score":-0.15368,"best_fitness_score":0.12632,"best_task_score":0.0183},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55497,0.06416,0.05941],"force_p95":1300.56547,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1300.56547,"mean_force":1300.56547,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50158,0.11315,0.0277]},{"body_a":"peg","body_b":"channel_base_body","contact_count":325.0,"contact_point_centroid":[0.50603,0.0625,0.00939],"force_p95":0.55321,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.56239,"mean_force":0.79122,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51369,0.11923,0.08415]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50593,0.07967,0.04998],"force_p95":20.17178,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.13469,"mean_force":9.14681,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50495,0.09165,0.04265]},{"body_a":"peg","body_b":"channel_base_body","contact_count":595.0,"contact_point_centroid":[0.50571,0.06297,0.00936],"force_p95":0.56339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.5693,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51158,0.17196,0.20965]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4999,0.19876,0.29662]},{"body_a":"peg","body_b":"channel_base_body","contact_count":15.0,"contact_point_centroid":[0.51601,0.05734,0.00975],"force_p95":0.87979,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.88392,"mean_force":0.57849,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50441,0.09972,0.03548]}],"total_contact_groups":6},"final_pose_error":0.20227,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50458,0.05497,0.0347],"final_tcp_position":[0.50115,0.11478,0.02669],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":1300.56547,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":623.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.06304,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":334.0,"raw_peak_contact_force":21.56239,"subtask_id":"pre_insertion","tcp_end":[0.5243,0.14613,0.12754],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12659,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":331.0,"n_steps_budget":960.0,"object_pos_end":[0.50563,0.05906,0.03567],"object_pos_start":[0.50598,0.06304,0.03381],"object_to_goal_dist_end":0.13924,"object_to_goal_dist_start":0.1433,"object_z_max":0.03569,"peak_contact_force":1300.56547,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":16.0,"raw_peak_contact_force":1300.56547,"subtask_id":"pre_insertion","tcp_end":[0.5045,0.09023,0.04045],"tcp_start":[0.5243,0.14613,0.12754],"tcp_to_object_dist_end":0.03155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":15.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,0.05497,0.0347],"object_pos_start":[0.50563,0.05906,0.03567],"object_to_goal_dist_end":0.13515,"object_to_goal_dist_start":0.13924,"object_z_max":0.03567,"peak_contact_force":0.54477,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":629.0,"raw_peak_contact_force":3.88411,"subtask_id":"insertion","tcp_end":[0.50115,0.11478,0.02669],"tcp_start":[0.5045,0.09023,0.04045],"tcp_to_object_dist_end":0.06044,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```