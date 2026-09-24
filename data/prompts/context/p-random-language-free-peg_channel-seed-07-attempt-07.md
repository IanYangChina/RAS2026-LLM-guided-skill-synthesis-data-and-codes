## Search State

- **Seed**: 7
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.0293 | 0.24 | ❌ rejected |
| 6 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.2759 | 0.00 | ❌ rejected |
| 5 | descend → approach → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.0821 | 0.24 | ❌ rejected |
| 4 | descend → insert → grasp → approach → align | linear_cartesian | impedance_motion | — | linear_cartesian | linear_cartesian | admittance_control | admittance_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | pose_tolerance | 5 | -0.1314 | 0.26 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0714 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.24 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.029) — your mutation base

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

- **Composite score**: -0.029
- **task_score** (E): 0.239
- **fitness_score**: 0.301  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| descend_to_peg | 1.00 | 1.00 | 0.1882 |
| approach_contact | 1.00 | 1.00 | 0.0748 |
| push_channel | 1.00 | 1.00 | 0.0962 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| descend_to_peg | descend | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.160, 0.119) | (0.509, 0.098, 0.040)→(0.502, 0.098, 0.034) | 0.179→0.178 | 1.00 / 1.000 | 0.548 | 2.732 |
| approach_contact | approach | 1.00 / step_budget | (0.505, 0.160, 0.119)→(0.499, 0.122, 0.056) | (0.502, 0.098, 0.034)→(0.503, 0.092, 0.035) | 0.178→0.172 | 1.00 / 1.000 | 0.522 | 62.578 |
| push_channel | push | 1.00 / step_budget | (0.499, 0.122, 0.056)→(0.495, 0.026, 0.051) | (0.503, 0.092, 0.035)→(0.500, 0.046, 0.024) | 0.172→0.127 | 1.00 / 1.333 | 0.687 | 30.740 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.340
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.305
- phase_score: 0.333
- phase_breakdown.pre_push_score: 0.537
- phase_breakdown.push_goal_score: 0.245

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.322
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.308
- **Median Q (composite search score)**: -0.016
- **K-run variance**: 0.0006
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.364


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96714,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.04087,"approach_contact.lateral_x":-0.00677,"descend_to_peg.descent_speed":0.04447,"push_channel.force_limit":34.50889,"push_channel.push_speed":0.03183,"push_channel.push_stroke":0.13515},"optimized_scores":{"best_composite_score":-0.01576,"best_fitness_score":0.31424,"best_task_score":0.30828},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.50414,0.11046,0.00938],"force_p95":17.58842,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.04884,"mean_force":2.47756,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.49878,0.15385,0.08564]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.50093,0.1286,0.05831],"force_p95":50.18164,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.51815,"mean_force":33.78079,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.4949,0.13826,0.0605]},{"body_a":"peg","body_b":"channel_base_body","contact_count":300.0,"contact_point_centroid":[0.50621,0.07577,0.00895],"force_p95":27.73976,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.52843,"mean_force":7.06117,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4914,0.07889,0.05202]},{"body_a":"attachment","body_b":"peg","contact_count":106.0,"contact_point_centroid":[0.49965,0.09769,0.04976],"force_p95":27.80381,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.09576,"mean_force":18.04157,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49184,0.10545,0.05262]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":12.0,"contact_point_centroid":[0.52501,0.03825,0.02557],"force_p95":7.35058,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.38574,"mean_force":4.22671,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49112,0.07513,0.05156]},{"body_a":"peg","body_b":"channel_base_body","contact_count":585.0,"contact_point_centroid":[0.50359,0.11171,0.00937],"force_p95":0.6116,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55848,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50219,0.18578,0.20644]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49973,0.19951,0.2991]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,0.10413,0.06],"force_p95":0.02798,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.02843,"mean_force":0.02389,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.49439,0.13573,0.05631]}],"total_contact_groups":8},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50562,0.06245,0.02406],"final_tcp_position":[0.49059,0.01922,0.05099],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":53.04884,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.50368,0.11175,0.0338],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19188,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57479,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":601.0,"raw_peak_contact_force":2.06328,"subtask_id":"pre_push","tcp_end":[0.50599,0.17279,0.11881],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10469,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":400.0,"n_steps_budget":1000.0,"object_pos_end":[0.50547,0.10713,0.03657],"object_pos_start":[0.50368,0.11175,0.0338],"object_to_goal_dist_end":0.18724,"object_to_goal_dist_start":0.19188,"object_z_max":0.03653,"peak_contact_force":0.40197,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":425.0,"raw_peak_contact_force":53.04884,"subtask_id":"pre_push","tcp_end":[0.49428,0.1354,0.05581],"tcp_start":[0.50599,0.17279,0.11881],"tcp_to_object_dist_end":0.03598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":302.0,"n_steps_budget":1000.0,"object_pos_end":[0.50562,0.06245,0.02406],"object_pos_start":[0.50547,0.10713,0.03657],"object_to_goal_dist_end":0.14345,"object_to_goal_dist_start":0.18724,"object_z_max":0.04028,"peak_contact_force":0.59293,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":418.0,"raw_peak_contact_force":28.52843,"subtask_id":"push_goal","tcp_end":[0.49059,0.01922,0.05099],"tcp_start":[0.49428,0.1354,0.05581],"tcp_to_object_dist_end":0.05311,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.98844,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.03723,"approach_contact.lateral_x":0.00308,"descend_to_peg.descent_speed":0.08475,"push_channel.force_limit":36.73547,"push_channel.push_speed":0.02739,"push_channel.push_stroke":0.10976},"optimized_scores":{"best_composite_score":-0.00828,"best_fitness_score":0.32172,"best_task_score":0.30504},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":699.0,"contact_point_centroid":[0.49698,0.11901,0.00938],"force_p95":50.94788,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.8805,"mean_force":7.00947,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.48849,0.15792,0.08135]},{"body_a":"attachment","body_b":"peg","contact_count":107.0,"contact_point_centroid":[0.50022,0.13511,0.05722],"force_p95":66.47395,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.327,"mean_force":42.31045,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.49435,0.14479,0.05904]},{"body_a":"peg","body_b":"channel_base_body","contact_count":242.0,"contact_point_centroid":[0.49677,0.08208,0.0091],"force_p95":28.76544,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.84626,"mean_force":10.60693,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49376,0.0999,0.05215]},{"body_a":"attachment","body_b":"peg","contact_count":121.0,"contact_point_centroid":[0.49804,0.10313,0.051],"force_p95":29.27485,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.58099,"mean_force":20.19454,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49403,0.11396,0.05253]},{"body_a":"peg","body_b":"channel_base_body","contact_count":527.0,"contact_point_centroid":[0.49625,0.11917,0.00944],"force_p95":0.62238,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55368,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49109,0.18908,0.20623]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49945,0.19938,0.29766]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47499,0.0893,0.02415],"force_p95":0.44236,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44236,"mean_force":0.44236,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49268,0.05239,0.05074]}],"total_contact_groups":7},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49333,0.06457,0.02409],"final_tcp_position":[0.49267,0.05201,0.05073],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":78.8805,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.49602,0.11912,0.03389],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.19925,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.51395,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":551.0,"raw_peak_contact_force":2.24822,"subtask_id":"pre_push","tcp_end":[0.48406,0.17947,0.11966],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10555,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":699.0,"n_steps_budget":1000.0,"object_pos_end":[0.49701,0.11274,0.03293],"object_pos_start":[0.49602,0.11912,0.03389],"object_to_goal_dist_end":0.19289,"object_to_goal_dist_start":0.19925,"object_z_max":0.03406,"peak_contact_force":0.7373,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":806.0,"raw_peak_contact_force":78.8805,"subtask_id":"pre_push","tcp_end":[0.49626,0.1428,0.0555],"tcp_start":[0.48406,0.17947,0.11966],"tcp_to_object_dist_end":0.0376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.49333,0.06457,0.02409],"object_pos_start":[0.49701,0.11274,0.03293],"object_to_goal_dist_end":0.1456,"object_to_goal_dist_start":0.19289,"object_z_max":0.04024,"peak_contact_force":0.82195,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":364.0,"raw_peak_contact_force":31.84626,"subtask_id":"push_goal","tcp_end":[0.49267,0.05201,0.05073],"tcp_start":[0.49626,0.1428,0.0555],"tcp_to_object_dist_end":0.02946,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.25658,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.0332,"approach_contact.lateral_x":0.00118,"descend_to_peg.descent_speed":0.08993,"push_channel.force_limit":36.48754,"push_channel.push_speed":0.03739,"push_channel.push_stroke":0.09979},"optimized_scores":{"best_composite_score":-0.06383,"best_fitness_score":0.26617,"best_task_score":0.10367},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":414.0,"contact_point_centroid":[0.50624,0.06217,0.00934],"force_p95":42.57966,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.80546,"mean_force":4.62449,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.51334,0.10674,0.08405]},{"body_a":"attachment","body_b":"peg","contact_count":44.0,"contact_point_centroid":[0.51017,0.0786,0.05776],"force_p95":50.23955,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.44728,"mean_force":38.44749,"phase_index":1.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.50643,0.08947,0.05884]},{"body_a":"peg","body_b":"channel_base_body","contact_count":214.0,"contact_point_centroid":[0.50485,0.02862,0.00924],"force_p95":29.81841,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.84651,"mean_force":11.82572,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50353,0.04905,0.05249]},{"body_a":"attachment","body_b":"peg","contact_count":115.0,"contact_point_centroid":[0.50674,0.0483,0.0517],"force_p95":30.17762,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.47049,"mean_force":21.07468,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50379,0.05955,0.05282]},{"body_a":"peg","body_b":"channel_base_body","contact_count":606.0,"contact_point_centroid":[0.50572,0.06299,0.00936],"force_p95":0.56254,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.5689,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.51162,0.16222,0.20414]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4999,0.19843,0.29629]}],"total_contact_groups":6},"final_pose_error":0.01979,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50132,0.00978,0.02397],"final_tcp_position":[0.50233,0.00643,0.05092],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":55.80546,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":634.0,"n_steps_budget":1000.0,"object_pos_end":[0.50601,0.06303,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.1433,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.55377,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":640.0,"raw_peak_contact_force":3.88411,"subtask_id":"pre_push","tcp_end":[0.52427,0.12719,0.11705],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10667,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":414.0,"n_steps_budget":1000.0,"object_pos_end":[0.50588,0.05634,0.035],"object_pos_start":[0.50601,0.06303,0.03381],"object_to_goal_dist_end":0.13655,"object_to_goal_dist_start":0.1433,"object_z_max":0.03476,"peak_contact_force":0.42587,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":458.0,"raw_peak_contact_force":55.80546,"subtask_id":"pre_push","tcp_end":[0.50589,0.08735,0.0557],"tcp_start":[0.52427,0.12719,0.11705],"tcp_to_object_dist_end":0.03728,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":216.0,"n_steps_budget":1000.0,"object_pos_end":[0.50132,0.00978,0.02397],"object_pos_start":[0.50588,0.05634,0.035],"object_to_goal_dist_end":0.09121,"object_to_goal_dist_start":0.13655,"object_z_max":0.04021,"peak_contact_force":0.64606,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":329.0,"raw_peak_contact_force":31.84651,"subtask_id":"push_goal","tcp_end":[0.50233,0.00643,0.05092],"tcp_start":[0.50589,0.08735,0.0557],"tcp_to_object_dist_end":0.02718,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```