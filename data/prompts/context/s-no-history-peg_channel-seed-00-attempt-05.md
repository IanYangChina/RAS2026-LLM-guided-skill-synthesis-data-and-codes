## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.766, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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

## Current Skill (Q=0.164) — your mutation base

```yaml
skill: peg_channel
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: 0.164
- **task_score** (E): 0.766
- **fitness_score**: 0.534  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.370

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| insert_1 | 0.00 | 1.00 | 0.1730 |
| approach_1 | 1.00 | 1.00 | 0.1465 |
| push_1 | 1.00 | 1.00 | 0.1413 |
| retract_1 | 0.00 | 1.00 | 0.0999 |
| lift_1 | 0.00 | 1.00 | 0.1520 |
| insert_2 | 0.00 | 1.00 | 0.1651 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| insert_1 | insert | 0.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.575 | 2.179 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.497, 0.119, 0.043) | (0.500, 0.080, 0.034)→(0.500, 0.084, 0.033) | 0.161→0.165 | 1.00 / 1.667 | 34.686 | 43.877 |
| push_1 | push | 1.00 / step_budget | (0.497, 0.119, 0.043)→(0.497, -0.022, 0.037) | (0.500, 0.084, 0.033)→(0.506, -0.054, 0.037) | 0.165→0.030 | 1.00 / 2.333 | 34.193 | 114.621 |
| retract_1 | retract | 0.00 / step_budget | (0.497, -0.022, 0.037)→(0.495, 0.011, 0.131) | (0.506, -0.054, 0.037)→(0.503, -0.060, 0.031) | 0.030→0.027 | 1.00 / 1.000 | 0.545 | 54.895 |
| lift_1 | lift | 0.00 / step_budget | (0.495, 0.011, 0.131)→(0.412, -0.039, 0.248) | (0.503, -0.060, 0.031)→(0.505, -0.060, 0.031) | 0.027→0.027 | 1.00 / 1.000 | 0.575 | 3.062 |
| insert_2 | insert | 0.00 / step_budget | (0.412, -0.039, 0.248)→(0.471, -0.068, 0.097) | (0.505, -0.060, 0.031)→(0.503, -0.060, 0.031) | 0.027→0.027 | 1.00 / 1.000 | 0.589 | 3.164 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.885
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.885
- phase_score: 0.515
- phase_breakdown.push_score: 0.598
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.783

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.663
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.890
- **Median Q (composite search score)**: 0.163
- **K-run variance**: 0.0109
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.197


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7004,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.06277,"push_1.push_distance":0.13381,"push_1.push_speed":0.07129,"retract_1.retract_height":0.15158,"retract_1.speed":0.05939},"optimized_scores":{"best_composite_score":0.29304,"best_fitness_score":0.66304,"best_task_score":0.88483},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":361.0,"contact_point_centroid":[0.54166,-0.00827,0.06],"force_p95":63.6658,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.57986,"mean_force":48.32668,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49685,-0.00596,0.03699]},{"body_a":"attachment","body_b":"peg","contact_count":745.0,"contact_point_centroid":[0.50269,-0.00103,0.04293],"force_p95":22.27333,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.97355,"mean_force":7.23312,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49664,0.01043,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.50671,-0.10044,0.05969],"force_p95":55.59916,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.27862,"mean_force":26.42887,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49768,-0.05314,0.03669]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54255,-0.05072,0.05998],"force_p95":56.19149,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":56.49793,"mean_force":50.45651,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4979,-0.05463,0.03662]},{"body_a":"peg","body_b":"channel_base_body","contact_count":613.0,"contact_point_centroid":[0.50613,-0.02275,0.00983],"force_p95":14.93864,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.53493,"mean_force":6.34637,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49665,0.01997,0.03731]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":406.0,"contact_point_centroid":[0.52507,-0.00974,0.02412],"force_p95":6.91216,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.72939,"mean_force":2.00248,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49653,0.01699,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":33.0,"contact_point_centroid":[0.50557,-0.10058,0.0563],"force_p95":1.24568,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.02729,"mean_force":0.73844,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49699,-0.05337,0.03767]},{"body_a":"attachment","body_b":"peg","contact_count":40.0,"contact_point_centroid":[0.50538,-0.06457,0.05545],"force_p95":1.12474,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.02229,"mean_force":0.68624,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49669,-0.05269,0.03825]},{"body_a":"peg","body_b":"channel_base_body","contact_count":977.0,"contact_point_centroid":[0.50366,0.06159,0.00935],"force_p95":0.6416,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55484,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13519,0.23593]},{"body_a":"peg","body_b":"channel_base_body","contact_count":966.0,"contact_point_centroid":[0.50607,-0.08019,0.0094],"force_p95":0.55639,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84434,"mean_force":0.54825,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4947,-0.02637,0.08463]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.50368,0.06157,0.00936],"force_p95":0.64141,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64379,"mean_force":0.54631,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49703,0.08639,0.11069]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49956,0.19884,0.29897]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50623,-0.07999,0.00938],"force_p95":0.55316,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55685,"mean_force":0.5467,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45035,-0.0286,0.19164]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50623,-0.08,0.00938],"force_p95":0.55321,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55409,"mean_force":0.54675,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43657,-0.05974,0.17885]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52504,-0.08085,0.01218],"force_p95":0.17478,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.17544,"mean_force":0.09347,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4966,-0.05276,0.03811]}],"total_contact_groups":15},"final_pose_error":0.07166,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50619,-0.07999,0.03378],"final_tcp_position":[0.46777,-0.07016,0.10324],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":83.57986,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50384,0.06159,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.59321,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":996.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14707,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":454.0,"n_steps_budget":930.0,"object_pos_end":[0.5038,0.06158,0.03376],"object_pos_start":[0.50384,0.06159,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14178,"object_z_max":0.03377,"peak_contact_force":0.47825,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":454.0,"raw_peak_contact_force":0.64379,"tcp_end":[0.49926,0.09848,0.04185],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03805,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50592,-0.08349,0.03627],"object_pos_start":[0.5038,0.06158,0.03376],"object_to_goal_dist_end":0.00781,"object_to_goal_dist_start":0.14177,"object_z_max":0.03805,"peak_contact_force":56.43803,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2182.0,"raw_peak_contact_force":83.57986,"tcp_end":[0.49795,-0.05457,0.03666],"tcp_start":[0.49926,0.09848,0.04185],"tcp_to_object_dist_end":0.03,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50621,-0.08004,0.03378],"object_pos_start":[0.50592,-0.08349,0.03627],"object_to_goal_dist_end":0.00879,"object_to_goal_dist_start":0.00781,"object_z_max":0.03661,"peak_contact_force":0.55691,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1049.0,"raw_peak_contact_force":56.49793,"tcp_end":[0.49533,-0.00759,0.13203],"tcp_start":[0.49795,-0.05457,0.03666],"tcp_to_object_dist_end":0.12255,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,-0.08002,0.03378],"object_pos_start":[0.50621,-0.08004,0.03378],"object_to_goal_dist_end":0.00878,"object_to_goal_dist_start":0.00879,"object_z_max":0.03379,"peak_contact_force":0.54089,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55685,"tcp_end":[0.40809,-0.04973,0.25588],"tcp_start":[0.49533,-0.00759,0.13203],"tcp_to_object_dist_end":0.24468,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,-0.07999,0.03378],"object_pos_start":[0.50619,-0.08002,0.03378],"object_to_goal_dist_end":0.00877,"object_to_goal_dist_start":0.00878,"object_z_max":0.03378,"peak_contact_force":0.54511,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55409,"tcp_end":[0.46777,-0.07016,0.10324],"tcp_start":[0.40809,-0.04973,0.25588],"tcp_to_object_dist_end":0.07998,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.50373,"average_solve_count":268.0,"average_success_count":268.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.04365,"push_1.push_distance":0.16875,"push_1.push_speed":0.07699,"retract_1.retract_height":0.07299,"retract_1.speed":0.04031},"optimized_scores":{"best_composite_score":0.16305,"best_fitness_score":0.53305,"best_task_score":0.89041},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":816.0,"contact_point_centroid":[0.50047,0.06523,0.00837],"force_p95":185.85083,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":189.59103,"mean_force":74.20066,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50117,0.09602,0.04375]},{"body_a":"attachment","body_b":"peg","contact_count":739.0,"contact_point_centroid":[0.50438,0.09385,0.04523],"force_p95":185.59545,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.12218,"mean_force":87.33679,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50169,0.10345,0.0445]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":396.0,"contact_point_centroid":[0.47421,0.04772,0.03205],"force_p95":67.0412,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.1932,"mean_force":15.59339,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49997,0.07445,0.04104]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":116.0,"contact_point_centroid":[0.54174,0.0242,0.06],"force_p95":57.41322,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.31694,"mean_force":42.86843,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49674,0.02718,0.03712]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54201,0.00018,0.05999],"force_p95":48.96686,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.26621,"mean_force":44.17184,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49712,0.00442,0.03709]},{"body_a":"peg","body_b":"world","contact_count":130.0,"contact_point_centroid":[0.50196,0.12548,-0.00018],"force_p95":20.32441,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":14.12671,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50038,0.15446,0.04497]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50572,-0.02672,0.00941],"force_p95":0.57446,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99003,"mean_force":0.54776,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49412,0.01866,0.08281]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52537,-0.02907,0.05928],"force_p95":0.55134,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6894,"mean_force":0.15119,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4957,0.0056,0.03945]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50572,-0.02645,0.00938],"force_p95":0.55118,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55281,"mean_force":0.54662,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45372,-0.00135,0.18437]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50572,-0.02645,0.00938],"force_p95":0.55118,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55119,"mean_force":0.54662,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44267,-0.04735,0.16727]}],"total_contact_groups":14},"final_pose_error":0.06138,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50576,-0.02643,0.03381],"final_tcp_position":[0.47259,-0.06545,0.09296],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":189.59103,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50421,-0.02643,0.03556],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.05392,"object_to_goal_dist_start":0.20832,"object_z_max":0.03682,"peak_contact_force":0.47475,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2197.0,"raw_peak_contact_force":189.59103,"tcp_end":[0.49714,0.00462,0.03712],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.03189,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50577,-0.02643,0.03381],"object_pos_start":[0.50421,-0.02643,0.03556],"object_to_goal_dist_end":0.05423,"object_to_goal_dist_start":0.05392,"object_z_max":0.03556,"peak_contact_force":0.54587,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1022.0,"raw_peak_contact_force":49.26621,"tcp_end":[0.4948,0.02709,0.13002],"tcp_start":[0.49714,0.00462,0.03712],"tcp_to_object_dist_end":0.11064,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50577,-0.02643,0.03381],"object_pos_start":[0.50577,-0.02643,0.03381],"object_to_goal_dist_end":0.05424,"object_to_goal_dist_start":0.05423,"object_z_max":0.03381,"peak_contact_force":0.5468,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55281,"tcp_end":[0.41549,-0.02971,0.24321],"tcp_start":[0.4948,0.02709,0.13002],"tcp_to_object_dist_end":0.22806,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50576,-0.02643,0.03381],"object_pos_start":[0.50577,-0.02643,0.03381],"object_to_goal_dist_end":0.05424,"object_to_goal_dist_start":0.05424,"object_z_max":0.03381,"peak_contact_force":0.5468,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55119,"tcp_end":[0.47259,-0.06545,0.09296],"tcp_start":[0.41549,-0.02971,0.24321],"tcp_to_object_dist_end":0.07825,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39844,"average_solve_count":256.0,"average_success_count":256.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"lift_1.speed":0.05199,"push_1.push_distance":0.11819,"push_1.push_speed":0.06115,"retract_1.retract_height":0.12562,"retract_1.speed":0.04661},"optimized_scores":{"best_composite_score":0.0372,"best_fitness_score":0.4072,"best_task_score":0.52365},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":347.0,"contact_point_centroid":[0.53749,0.01716,0.06],"force_p95":56.07149,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.69206,"mean_force":43.65365,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4923,0.02049,0.03758]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54003,-0.02246,0.06],"force_p95":58.07499,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":58.91993,"mean_force":50.28319,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49521,-0.01703,0.03722]},{"body_a":"attachment","body_b":"peg","contact_count":893.0,"contact_point_centroid":[0.49888,0.0205,0.03591],"force_p95":44.40867,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.49857,"mean_force":28.59477,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49175,0.02927,0.03766]},{"body_a":"peg","body_b":"channel_base_body","contact_count":965.0,"contact_point_centroid":[0.50667,0.00075,0.00976],"force_p95":27.96901,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.79404,"mean_force":15.96922,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49156,0.03368,0.03779]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":842.0,"contact_point_centroid":[0.52536,0.00574,0.02517],"force_p95":29.66605,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.75378,"mean_force":20.30364,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49193,0.02604,0.03762]},{"body_a":"peg","body_b":"link7","contact_count":175.0,"contact_point_centroid":[0.51942,0.02007,0.06836],"force_p95":12.40831,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.28222,"mean_force":5.21021,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49047,0.04572,0.03774]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50129,-0.02639,0.03443],"force_p95":5.48387,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.57079,"mean_force":1.07383,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49498,-0.01703,0.03742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50174,-0.07272,0.00799],"force_p95":0.77009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.38563,"mean_force":0.62012,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.44134,-0.05188,0.16888]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52508,-0.04116,0.02207],"force_p95":7.47171,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.09205,"mean_force":1.39852,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49387,-0.01099,0.05044]},{"body_a":"peg","body_b":"channel_base_body","contact_count":981.0,"contact_point_centroid":[0.50213,-0.06889,0.00847],"force_p95":0.77941,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.0913,"mean_force":0.64108,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49256,0.00178,0.08338]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49876,-0.07269,0.00802],"force_p95":0.72553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.07701,"mean_force":0.61321,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.45211,-0.01148,0.18552]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":5.0,"contact_point_centroid":[0.525,-0.04953,0.02418],"force_p95":7.89351,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.00381,"mean_force":3.35334,"phase_index":5.0,"phase_name":"insert_2","phase_type":"insert","tcp_position_centroid":[0.43073,-0.04657,0.19417]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.475,-0.09581,0.02419],"force_p95":6.67019,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.77309,"mean_force":2.24127,"phase_index":4.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.47823,0.00573,0.14452]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":14.0,"contact_point_centroid":[0.47486,-0.09608,0.02656],"force_p95":4.05759,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.06945,"mean_force":1.63225,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49168,-0.00659,0.05592]},{"body_a":"peg","body_b":"channel_base_body","contact_count":76.0,"contact_point_centroid":[0.51388,-0.10012,0.02374],"force_p95":1.10328,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.30823,"mean_force":0.34822,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49183,-0.00441,0.06179]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49748,0.13493,0.23568]}],"total_contact_groups":18},"final_pose_error":0.06194,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49562,-0.07214,0.02405],"final_tcp_position":[0.47196,-0.06741,0.09377],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":70.69206,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50741,-0.05176,0.04057],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.0292,"object_to_goal_dist_start":0.14379,"object_z_max":0.04057,"peak_contact_force":45.66645,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3222.0,"raw_peak_contact_force":70.69206,"tcp_end":[0.4952,-0.01696,0.03722],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.03703,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49749,-0.07251,0.02413],"object_pos_start":[0.50741,-0.05176,0.04057],"object_to_goal_dist_end":0.01773,"object_to_goal_dist_start":0.0292,"object_z_max":0.0408,"peak_contact_force":0.53263,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1117.0,"raw_peak_contact_force":58.91993,"tcp_end":[0.4936,0.01388,0.13001],"tcp_start":[0.4952,-0.01696,0.03722],"tcp_to_object_dist_end":0.13671,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50261,-0.07306,0.0241],"object_pos_start":[0.49749,-0.07251,0.02413],"object_to_goal_dist_end":0.01754,"object_to_goal_dist_start":0.01773,"object_z_max":0.02433,"peak_contact_force":0.63683,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1004.0,"raw_peak_contact_force":8.07701,"tcp_end":[0.4135,-0.03681,0.24546],"tcp_start":[0.4936,0.01388,0.13001],"tcp_to_object_dist_end":0.24136,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49562,-0.07214,0.02405],"object_pos_start":[0.50261,-0.07306,0.0241],"object_to_goal_dist_end":0.01831,"object_to_goal_dist_start":0.01754,"object_z_max":0.02432,"peak_contact_force":0.67396,"phase_name":"insert_2","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1005.0,"raw_peak_contact_force":8.38563,"tcp_end":[0.47196,-0.06741,0.09377],"tcp_start":[0.4135,-0.03681,0.24546],"tcp_to_object_dist_end":0.07378,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```