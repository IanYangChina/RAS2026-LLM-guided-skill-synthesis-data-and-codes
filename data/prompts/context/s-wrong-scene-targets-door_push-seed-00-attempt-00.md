## Search State

- **Seed**: 0
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | insert → insert → approach → push → retract → lift → insert → push | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | impedance_motion | impedance_control | impedance_control | force_threshold_switch | position_control | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 8 | -0.1509 | 0.43 | ✅ accepted |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: door_push
- Frozen realised-scene SHA-256: `62a65d94e3dd29d4ed838d1b497b403a6341a023abe76fe9c8f6f096e79b6b73`
- Frozen initial hinge angle: 0.524 rad
- target_hinge_angle: 0.048 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
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
  frozen_initial_hinge_angle_rad: 0.0478
  frozen_fixtures: {'door_panel': [0.5, 0.2, 0.0]}
  door_hinge_axis: [0, 0, 1]
  goal_tolerance_m: 0.05
  force_limit_n: 30
  force_scale_n: 5
  target_hinge_angle_rad: 0.048
  realized_scene_sha256: 62a65d94e3dd29d4ed838d1b497b403a6341a023abe76fe9c8f6f096e79b6b73

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

## Current Skill (Q=-0.151) — your mutation base

```yaml
skill: door_push
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: insert_2
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_3
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
- id: push_2
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit

```

## Design Metrics

- **Composite score**: -0.151
- **task_score** (E): 0.429
- **fitness_score**: 0.429  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.580

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 1.00 | 1.00 | 0.2094 |
| insert_2 | 1.00 | 0.33 | 0.0020 |
| approach_1 | 1.00 | 0.33 | 0.0016 |
| push_1 | 1.00 | 0.33 | 0.0013 |
| retract_1 | 1.00 | 0.67 | 0.0011 |
| lift_1 | 1.00 | 0.33 | 0.1399 |
| insert_3 | 1.00 | 0.67 | 0.1305 |
| push_2 | 1.00 | 0.67 | 0.0054 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.190, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.667 | 7.200 | 31.925 |
| insert_2 | insert | 1.00 / step_budget | (0.100, 0.190, 0.349)→(0.100, 0.188, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 15.934 |
| approach_1 | approach | 1.00 / step_budget | (0.100, 0.188, 0.348)→(0.100, 0.186, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 6.215 | 19.669 |
| push_1 | push | 1.00 / step_budget | (0.100, 0.186, 0.348)→(0.100, 0.185, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.667 | 2.078 | 13.519 |
| retract_1 | retract | 1.00 / step_budget | (0.100, 0.185, 0.348)→(0.100, 0.184, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 0.000 | 14.058 |
| lift_1 | lift | 1.00 / step_budget | (0.100, 0.184, 0.348)→(-0.040, 0.179, 0.349) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 8.357 |
| insert_3 | insert | 1.00 / step_budget | (-0.040, 0.179, 0.349)→(0.090, 0.179, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 3.000 | 2.441 | 24.657 |
| push_2 | push | 1.00 / time_limit | (0.090, 0.179, 0.348)→(0.096, 0.179, 0.348) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.667 | 0.000 | 17.218 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.568
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.568
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.568
- **Median Q (composite search score)**: -0.179
- **K-run variance**: 0.0108
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.266


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `275c70960dc683bb9d0f514db4e615bd3a6644bf8e38d8dd2bfa731bf179f097`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `35996939e2e1630dea7cedb55906290b2cb0393492844f540c2c9d9496e5416e`; realized-scene SHA-256: `62a65d94e3dd29d4ed838d1b497b403a6341a023abe76fe9c8f6f096e79b6b73`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.99971,0.0,0.0,0.0239],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.04781},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99971,0.0,0.0,0.0239],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.71366,"average_solve_count":227.0,"average_success_count":227.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13893,"approach_1.speed":0.04752,"insert_1.insertion_force":14.2319,"insert_2.insertion_depth":0.05605,"insert_3.insertion_depth":0.07135,"lift_1.lift_height":0.218,"lift_1.speed":0.05962,"push_1.push_speed":0.05456},"optimized_scores":{"best_composite_score":-0.26202,"best_fitness_score":0.31798,"best_task_score":0.31798},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":187.0,"contact_point_centroid":[0.14896,0.15865,0.39719],"force_p95":22.39842,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.45114,"mean_force":13.42055,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.0998,0.21627,0.34839]},{"body_a":"door_panel","body_b":"link7","contact_count":23.0,"contact_point_centroid":[0.13102,0.1246,0.40193],"force_p95":15.45735,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.65821,"mean_force":13.8163,"phase_index":6.0,"phase_name":"insert_3","phase_type":"insert","tcp_position_centroid":[0.08324,0.17897,0.34826]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.14595,0.12891,0.39956],"force_p95":19.50648,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.85907,"mean_force":17.50195,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09975,0.18681,0.34812]},{"body_a":"door_panel","body_b":"link7","contact_count":29.0,"contact_point_centroid":[0.13946,0.1224,0.40108],"force_p95":13.43252,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.21826,"mean_force":11.46813,"phase_index":7.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.09323,0.17865,0.34797]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.14567,0.12629,0.39908],"force_p95":16.63988,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.72114,"mean_force":16.27706,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09962,0.18409,0.34756]},{"body_a":"door_panel","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.14622,0.13107,0.3995],"force_p95":15.91194,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.95161,"mean_force":11.61775,"phase_index":1.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.09982,0.18899,0.34831]},{"body_a":"door_panel","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.14574,0.12754,0.39944],"force_p95":13.59574,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.61548,"mean_force":12.5761,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09968,0.18537,0.34784]},{"body_a":"world","body_b":"door_panel","contact_count":804.0,"contact_point_centroid":[0.30136,0.17605,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.09968,0.28387,0.34808]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30559,0.15201,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.09984,0.18931,0.34836]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30587,0.15087,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09975,0.18708,0.34807]},{"body_a":"world","body_b":"door_panel","contact_count":28.0,"contact_point_centroid":[0.30602,0.15027,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.0997,0.18582,0.34796]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30621,0.14956,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09962,0.18438,0.34757]},{"body_a":"world","body_b":"door_panel","contact_count":676.0,"contact_point_centroid":[0.30619,0.14961,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.02584,0.18098,0.34741]},{"body_a":"world","body_b":"door_panel","contact_count":524.0,"contact_point_centroid":[0.30594,0.1506,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"insert_3","phase_type":"insert","tcp_position_centroid":[0.02368,0.17879,0.34788]},{"body_a":"world","body_b":"door_panel","contact_count":68.0,"contact_point_centroid":[0.30654,0.14831,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":7.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.09236,0.17871,0.34801]}],"total_contact_groups":15},"final_pose_error":0.00498,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09564,0.17865,0.34803],"hinge_angle":0.21443,"initial_hinge_angle":0.04781,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04781,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":28.45114,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":818.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":12.67181,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":991.0,"raw_peak_contact_force":28.45114,"tcp_end":[0.09987,0.18989,0.34856],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":25.0,"raw_peak_contact_force":15.95161,"tcp_end":[0.0998,0.1879,0.34821],"tcp_start":[0.09987,0.18989,0.34856],"tcp_to_object_dist_end":0.40806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":19.85907,"tcp_end":[0.09974,0.18627,0.3482],"tcp_start":[0.0998,0.1879,0.34821],"tcp_to_object_dist_end":0.40729,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":35.0,"raw_peak_contact_force":13.61548,"tcp_end":[0.09967,0.18498,0.34785],"tcp_start":[0.09974,0.18627,0.3482],"tcp_to_object_dist_end":0.40639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":20.0,"raw_peak_contact_force":16.72114,"tcp_end":[0.09962,0.18388,0.34758],"tcp_start":[0.09967,0.18498,0.34785],"tcp_to_object_dist_end":0.40564,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":676.0,"raw_peak_contact_force":0.0,"tcp_end":[-0.04018,0.17933,0.34851],"tcp_start":[0.09962,0.18388,0.34758],"tcp_to_object_dist_end":0.39399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":569.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.32191,"phase_name":"insert_3","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":547.0,"raw_peak_contact_force":24.65821,"tcp_end":[0.09029,0.179,0.34832],"tcp_start":[-0.04018,0.17933,0.34851],"tcp_to_object_dist_end":0.4019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":74.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":97.0,"raw_peak_contact_force":19.21826,"tcp_end":[0.09564,0.17865,0.34803],"tcp_start":[0.09029,0.179,0.34832],"tcp_to_object_dist_end":0.40272,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7a748efd829eb09daaf6b07ec36a2131763f35cca8c1f058f1a757467a8ce067`; realized-scene SHA-256: `02510fe55caa23c78bf987721ef5c6c19c6d55c0df3e224216ba39f61ecd9c91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]},"target_hinge_angle":0.00413},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[1.0,0.0,0.0,0.00206],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.81166,"average_solve_count":223.0,"average_success_count":223.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.1777,"approach_1.speed":0.07058,"insert_1.insertion_force":12.91132,"insert_2.insertion_depth":0.10523,"insert_3.insertion_depth":0.0726,"lift_1.lift_height":0.22026,"lift_1.speed":0.06458,"push_1.push_speed":0.04329},"optimized_scores":{"best_composite_score":-0.17874,"best_fitness_score":0.40126,"best_task_score":0.40126},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":240.0,"contact_point_centroid":[0.14966,0.16616,0.39641],"force_p95":25.69669,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.12034,"mean_force":13.20899,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.09976,0.2237,0.34831]},{"body_a":"door_panel","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.1309,0.12464,0.40204],"force_p95":14.22919,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.64307,"mean_force":13.50533,"phase_index":6.0,"phase_name":"insert_3","phase_type":"insert","tcp_position_centroid":[0.08314,0.17898,0.34826]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.14592,0.12867,0.39966],"force_p95":20.33539,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.50262,"mean_force":17.59461,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09974,0.18655,0.34817]},{"body_a":"door_panel","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.13961,0.12237,0.40112],"force_p95":12.70195,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.23166,"mean_force":11.51765,"phase_index":7.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.09345,0.17867,0.34795]},{"body_a":"door_panel","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.14618,0.13076,0.39947],"force_p95":15.93628,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.96256,"mean_force":13.43258,"phase_index":1.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.09981,0.18868,0.34824]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.14574,0.12732,0.39951],"force_p95":13.50566,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.52046,"mean_force":12.89075,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09969,0.18514,0.34786]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.14556,0.12603,0.39938],"force_p95":12.13044,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.76888,"mean_force":6.38444,"phase_index":5.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.09964,0.18384,0.34759]},{"body_a":"door_panel","body_b":"link7","contact_count":12.0,"contact_point_centroid":[0.14571,0.12675,0.39929],"force_p95":12.43072,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.44627,"mean_force":7.73848,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09966,0.18455,0.34769]},{"body_a":"world","body_b":"door_panel","contact_count":912.0,"contact_point_centroid":[0.30071,0.18339,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.09965,0.29518,0.34803]},{"body_a":"world","body_b":"door_panel","contact_count":12.0,"contact_point_centroid":[0.30557,0.15206,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.09983,0.18934,0.34837]},{"body_a":"world","body_b":"door_panel","contact_count":36.0,"contact_point_centroid":[0.30586,0.15091,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09977,0.18729,0.3481]},{"body_a":"world","body_b":"door_panel","contact_count":20.0,"contact_point_centroid":[0.30606,0.15013,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09971,0.18574,0.34794]},{"body_a":"world","body_b":"door_panel","contact_count":24.0,"contact_point_centroid":[0.30618,0.14967,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09966,0.18446,0.34768]},{"body_a":"world","body_b":"door_panel","contact_count":668.0,"contact_point_centroid":[0.30616,0.14975,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.02932,0.18106,0.34734]},{"body_a":"world","body_b":"door_panel","contact_count":644.0,"contact_point_centroid":[0.3059,0.15076,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"insert_3","phase_type":"insert","tcp_position_centroid":[0.02351,0.1788,0.3479]},{"body_a":"world","body_b":"door_panel","contact_count":96.0,"contact_point_centroid":[0.30655,0.14827,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":7.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.09269,0.17873,0.348]}],"total_contact_groups":16},"final_pose_error":0.00496,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09565,0.17866,0.34802],"hinge_angle":0.21439,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":31.12034,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":819.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.47014,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1152.0,"raw_peak_contact_force":31.12034,"tcp_end":[0.09986,0.18989,0.34856],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":20.0,"raw_peak_contact_force":15.96256,"tcp_end":[0.09979,0.1879,0.34821],"tcp_start":[0.09986,0.18989,0.34856],"tcp_to_object_dist_end":0.40806,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40.0,"raw_peak_contact_force":20.50262,"tcp_end":[0.09976,0.18624,0.34822],"tcp_start":[0.09979,0.1879,0.34821],"tcp_to_object_dist_end":0.4073,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":6.23344,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":23.0,"raw_peak_contact_force":13.52046,"tcp_end":[0.09969,0.18493,0.34786],"tcp_start":[0.09976,0.18624,0.34822],"tcp_to_object_dist_end":0.40638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":36.0,"raw_peak_contact_force":12.44627,"tcp_end":[0.09963,0.18385,0.34759],"tcp_start":[0.09969,0.18493,0.34786],"tcp_to_object_dist_end":0.40565,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":671.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":670.0,"raw_peak_contact_force":12.76888,"tcp_end":[-0.04025,0.17935,0.34851],"tcp_start":[0.09963,0.18385,0.34759],"tcp_to_object_dist_end":0.39402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":569.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"insert_3","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":671.0,"raw_peak_contact_force":24.64307,"tcp_end":[0.09027,0.17902,0.34833],"tcp_start":[-0.04025,0.17935,0.34851],"tcp_to_object_dist_end":0.40191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":75.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":123.0,"raw_peak_contact_force":16.23166,"tcp_end":[0.09565,0.17866,0.34802],"tcp_start":[0.09027,0.17902,0.34833],"tcp_to_object_dist_end":0.40272,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `8f682501979e58f93da2583f25150788eff90e19c055477d4547c33e5c9d7ff1`; realized-scene SHA-256: `6dd40fac67fc7b4cb952edf7b79ea329c0b46aa4cb26369fc447c16f02a37d6d`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"fixture","value":[0.5,0.2,0.0]}],"axes":[{"name":"door_hinge_axis","value":[0.0,0.0,1.0]}],"door":{"hinge_axis":[0.0,0.0,1.0],"initial_hinge_angle":0.524,"panel":{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]},"target_hinge_angle":-0.08321},"fixture_states":[],"fixtures":[{"name":"door_panel","orientation":[0.99913,0.0,0.0,-0.04159],"position":[0.5,0.2,0.0]}],"limits":[{"name":"goal_tolerance_m","value":0.05},{"name":"force_limit_n","value":30.0},{"name":"force_scale_n","value":5.0},{"name":"target_hinge_angle_rad","value":0.524}],"object_starts":[],"obstacles":[],"targets":[],"task_name":"door_push"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.7087,"average_solve_count":230.0,"average_success_count":230.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15402,"approach_1.speed":0.05182,"insert_1.insertion_force":10.03783,"insert_2.insertion_depth":0.10214,"insert_3.insertion_depth":0.05363,"lift_1.lift_height":0.17428,"lift_1.speed":0.05594,"push_1.push_speed":0.04396},"optimized_scores":{"best_composite_score":-0.01199,"best_fitness_score":0.56801,"best_task_score":0.56801},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":64.0,"contact_point_centroid":[0.10097,0.22654,0.47115],"force_p95":25.95373,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.20413,"mean_force":12.22639,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.09949,0.28358,0.34785]},{"body_a":"door_panel","body_b":"link7","contact_count":317.0,"contact_point_centroid":[0.14986,0.17613,0.3951],"force_p95":25.62687,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.48672,"mean_force":13.11515,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.09966,0.23362,0.34818]},{"body_a":"door_panel","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.13093,0.12462,0.40199],"force_p95":14.22604,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.66925,"mean_force":13.50456,"phase_index":6.0,"phase_name":"insert_3","phase_type":"insert","tcp_position_centroid":[0.08315,0.17898,0.34826]},{"body_a":"door_panel","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.14588,0.1286,0.39966],"force_p95":18.62082,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.64387,"mean_force":18.0384,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09973,0.18643,0.34816]},{"body_a":"door_panel","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.13965,0.12236,0.40105],"force_p95":12.70702,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.20356,"mean_force":11.51578,"phase_index":7.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.09346,0.17867,0.34794]},{"body_a":"door_panel","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.14617,0.13066,0.39948],"force_p95":15.86619,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.88774,"mean_force":13.37672,"phase_index":1.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.09981,0.18859,0.34824]},{"body_a":"door_panel","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.1458,0.12765,0.39945],"force_p95":13.41211,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.42047,"mean_force":10.45166,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09969,0.18548,0.34791]},{"body_a":"door_panel","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.14565,0.12631,0.39914],"force_p95":13.00588,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.00696,"mean_force":11.74,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09962,0.18407,0.34756]},{"body_a":"door_panel","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.14565,0.12604,0.39913],"force_p95":11.68607,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.30112,"mean_force":6.15056,"phase_index":5.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.09963,0.18381,0.34756]},{"body_a":"world","body_b":"door_panel","contact_count":904.0,"contact_point_centroid":[0.30056,0.19458,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.0996,0.29673,0.34797]},{"body_a":"world","body_b":"door_panel","contact_count":40.0,"contact_point_centroid":[0.3056,0.15195,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.09983,0.18931,0.34833]},{"body_a":"world","body_b":"door_panel","contact_count":12.0,"contact_point_centroid":[0.30585,0.15097,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.09979,0.18752,0.34809]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30601,0.15031,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.09972,0.18602,0.34801]},{"body_a":"world","body_b":"door_panel","contact_count":16.0,"contact_point_centroid":[0.30622,0.14952,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.09963,0.18421,0.34757]},{"body_a":"world","body_b":"door_panel","contact_count":680.0,"contact_point_centroid":[0.30616,0.14973,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":5.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.02855,0.18101,0.34734]},{"body_a":"world","body_b":"door_panel","contact_count":604.0,"contact_point_centroid":[0.3059,0.15075,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":6.0,"phase_name":"insert_3","phase_type":"insert","tcp_position_centroid":[0.02367,0.17881,0.34792]}],"total_contact_groups":17},"final_pose_error":0.00496,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09565,0.17866,0.34802],"hinge_angle":0.21442,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":36.20413,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":4.45837,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1285.0,"raw_peak_contact_force":36.20413,"tcp_end":[0.09986,0.18979,0.34856],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.40925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":48.0,"raw_peak_contact_force":15.88774,"tcp_end":[0.09979,0.18782,0.34821],"tcp_start":[0.09986,0.18979,0.34856],"tcp_to_object_dist_end":0.40802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":18.64387,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15.0,"raw_peak_contact_force":18.64387,"tcp_end":[0.09974,0.18617,0.3482],"tcp_start":[0.09979,0.18782,0.34821],"tcp_to_object_dist_end":0.40725,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":13.0,"raw_peak_contact_force":13.42047,"tcp_end":[0.09968,0.18491,0.34785],"tcp_start":[0.09974,0.18617,0.3482],"tcp_to_object_dist_end":0.40635,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":21.0,"raw_peak_contact_force":13.00696,"tcp_end":[0.09962,0.18383,0.34757],"tcp_start":[0.09968,0.18491,0.34785],"tcp_to_object_dist_end":0.40561,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":682.0,"raw_peak_contact_force":12.30112,"tcp_end":[-0.04017,0.17933,0.34851],"tcp_start":[0.09962,0.18383,0.34757],"tcp_to_object_dist_end":0.39399,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":569.0,"n_steps_budget":900.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"insert_3","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":631.0,"raw_peak_contact_force":24.66925,"tcp_end":[0.09028,0.17902,0.34833],"tcp_start":[-0.04017,0.17933,0.34851],"tcp_to_object_dist_end":0.40191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":75.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":83.0,"raw_peak_contact_force":16.20356,"tcp_end":[0.09565,0.17866,0.34802],"tcp_start":[0.09028,0.17902,0.34833],"tcp_to_object_dist_end":0.40272,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```