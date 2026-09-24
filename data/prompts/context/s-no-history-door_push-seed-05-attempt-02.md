## Search State

- **Seed**: 5
- **Iteration**: 3 / 15

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

- Task name: door_push
- Frozen realised-scene SHA-256: `f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618`
- Frozen initial hinge angle: 0.106 rad
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Robot initial TCP position: (0.1, 0.4, 0.35)
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.1, 0.4, 0.35]
objects:
  - name: door_panel
    role: fixture
    dynamics: hinged
    geometry: box
    dimensions_m: [0.4, 0.02, 0.7]
    hinge_axis: Z
    hinge_joint_name: door_hinge
  - name: door_handle
    role: grasp_site
    dynamics: hinged_with_panel
    geometry: site
    body_frame_offset_m: [-0.4, -0.02, 0.35]
  - name: door_frame
    role: fixture
    dynamics: static
    geometry: box
task_landmarks:
  frozen_fixture_position: [0.5, 0.2, 0]
  frozen_initial_hinge_angle_rad: 0.1065
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.524
  realized_scene_sha256: f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618

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
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose (0.5, 0.2, 0.0) | approach/contact targets near fixture |

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

## Current Skill (Q=-0.080) — your mutation base

```yaml
skill: door_push
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: release_2
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: release_3
  type: release
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  end_effector_action: open
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp

```

## Design Metrics

- **Composite score**: -0.080
- **task_score** (E): 0.170
- **fitness_score**: 0.170  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_handle | 1.00 | 1.00 | 0.1895 |
| push_door | 0.00 | 0.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.210, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.333 | 9.878 | 22.197 |
| push_door | push | 0.00 / guard_failure | (0.100, 0.209, 0.348)→(0.100, 0.209, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 20.628 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.249
- arc_quality: 0.500

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.249
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.249
- **Median Q (composite search score)**: -0.059
- **K-run variance**: 0.0056
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.305


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `e036e59174e9f4dc4d090dc26b64c24f51b2862ad33098baa3e34b1ab5217b2c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `121441f93055d9c3a0317d86ccf3c4d50a1368e9262fdd196bc29f47a537ab6f`; realized-scene SHA-256: `f3bd2e80ef0506fd6b5cd5a4fd1b44e0782b3c0a174abf2e2d5dfa29f59ee618`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.10647,"panel":{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99858,0.0,0.0,0.05321],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65714,"average_solve_count":35.0,"average_success_count":35.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.13498,"approach_handle.approach_tolerance":0.01166,"push_door.force_threshold":25.1908,"push_door.push_distance":0.26285,"push_door.push_speed":0.14735},"optimized_scores":{"best_composite_score":-0.18003,"best_fitness_score":0.06997,"best_task_score":0.06997},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.16508,0.15221,0.37238],"force_p95":19.71857,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.90953,"mean_force":7.30318,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09982,0.20963,0.34849]},{"body_a":"door_panel","body_b":"link6","contact_count":53.0,"contact_point_centroid":[0.10291,0.15279,0.4533],"force_p95":19.34429,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.69838,"mean_force":8.70229,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09983,0.22001,0.34842]},{"body_a":"door_panel","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.1651,0.15378,0.3724],"force_p95":18.19109,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.40129,"mean_force":13.59479,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09984,0.21116,0.3485]},{"body_a":"world","body_b":"door_panel","contact_count":800.0,"contact_point_centroid":[0.30218,0.16892,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09969,0.30479,0.34818]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30339,0.16199,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09984,0.20973,0.34851]}],"total_contact_groups":5},"final_pose_error":0.29228,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09978,0.20942,0.34836],"hinge_angle":0.14313,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":21.90953,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":710.0,"n_steps_budget":930.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":3.86036,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":865.0,"raw_peak_contact_force":20.69838,"subtask_id":"reach_handle","tcp_end":[0.09984,0.20973,0.34851],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":21.90953,"subtask_id":"open_door","tcp_end":[0.09978,0.20942,0.34836],"tcp_start":[0.09977,0.20947,0.3484],"tcp_to_object_dist_end":0.41853,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fbf559b1c4ad02fb5807d56e72eb3a3daf90ab4647e10f958130a5b70ea34720`; realized-scene SHA-256: `dc4259a01269d1a689f775747b3c927cb1b450b657cf3ca07d50da9e3593da80`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.01332,"panel":{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99998,0.0,0.0,0.00666],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67647,"average_solve_count":34.0,"average_success_count":34.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.13823,"approach_handle.approach_tolerance":0.00716,"push_door.force_threshold":24.50092,"push_door.push_distance":0.27167,"push_door.push_speed":0.11439},"optimized_scores":{"best_composite_score":-0.00111,"best_fitness_score":0.24889,"best_task_score":0.24889},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":193.0,"contact_point_centroid":[0.10137,0.17081,0.4547],"force_p95":19.16992,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.47213,"mean_force":8.74883,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09973,0.24235,0.34838]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.16506,0.15197,0.37236],"force_p95":17.7916,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.76844,"mean_force":6.58948,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.0998,0.20944,0.34846]},{"body_a":"door_panel","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.16511,0.15376,0.37244],"force_p95":17.93077,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.17157,"mean_force":13.35442,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09983,0.2112,0.34854]},{"body_a":"world","body_b":"door_panel","contact_count":712.0,"contact_point_centroid":[0.30062,0.18297,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09968,0.30084,0.34819]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30343,0.16177,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.0998,0.20956,0.3485]}],"total_contact_groups":5},"final_pose_error":0.30083,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09976,0.20916,0.34828],"hinge_angle":0.14374,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":23.47213,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":706.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.88622,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":917.0,"raw_peak_contact_force":23.47213,"subtask_id":"reach_handle","tcp_end":[0.09983,0.20977,0.34854],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":7.0,"raw_peak_contact_force":19.76844,"subtask_id":"open_door","tcp_end":[0.09976,0.20916,0.34828],"tcp_start":[0.09978,0.20921,0.34834],"tcp_to_object_dist_end":0.41833,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `99847c10f6e36b39751f22a6e7e446b09a6cc2d5cdc4857751225dedfedfe952`; realized-scene SHA-256: `82ce57ad272540c243cfe7c86f1faba3a732bddf0a834ea70613e69de7a6ff57`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.04367,"panel":{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.524},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99976,0.0,0.0,0.02183],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68571,"average_solve_count":35.0,"average_success_count":35.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_handle.approach_speed":0.13795,"approach_handle.approach_tolerance":0.00804,"push_door.force_threshold":23.15856,"push_door.push_distance":0.19923,"push_door.push_speed":0.08316},"optimized_scores":{"best_composite_score":-0.05894,"best_fitness_score":0.19106,"best_task_score":0.19106},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":145.0,"contact_point_centroid":[0.10178,0.1649,0.45425],"force_p95":19.2473,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.42063,"mean_force":8.89157,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09976,0.23499,0.3484]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.16507,0.15186,0.37234],"force_p95":18.73875,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.20677,"mean_force":7.65669,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.0998,0.20929,0.34843]},{"body_a":"door_panel","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.16511,0.15376,0.37244],"force_p95":17.93145,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.1724,"mean_force":13.35549,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09983,0.2112,0.34854]},{"body_a":"world","body_b":"door_panel","contact_count":672.0,"contact_point_centroid":[0.30086,0.17944,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_handle","phase_type":"approach","tcp_position_centroid":[0.09968,0.30366,0.34816]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30349,0.1615,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.09976,0.20903,0.34834]}],"total_contact_groups":5},"final_pose_error":0.22823,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09978,0.209,0.3483],"hinge_angle":0.14378,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":22.42063,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":705.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.88666,"phase_name":"approach_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":829.0,"raw_peak_contact_force":22.42063,"subtask_id":"reach_handle","tcp_end":[0.09983,0.20977,0.34854],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.41887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":20.20677,"subtask_id":"open_door","tcp_end":[0.09978,0.209,0.3483],"tcp_start":[0.09976,0.20903,0.34834],"tcp_to_object_dist_end":0.41827,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```