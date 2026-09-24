## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

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

## Current Skill (Q=-0.109) — your mutation base

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

- **Composite score**: -0.109
- **task_score** (E): 0.014
- **fitness_score**: 0.331  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1917 |
| descend_1 | 1.00 | 1.00 | 0.0891 |
| align_1 | 1.00 | 1.00 | 0.0133 |
| push_1 | 1.00 | 1.00 | 0.1588 |
| retract_1 | 1.00 | 1.00 | 0.0408 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.088, 0.146) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.550 | 2.179 |
| descend_1 | descend | 1.00 / step_budget | (0.495, 0.088, 0.146)→(0.497, 0.081, 0.058) | (0.500, 0.080, 0.034)→(0.501, 0.080, 0.033) | 0.161→0.161 | 1.00 / 2.000 | 51.663 | 69.770 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.081, 0.058)→(0.497, 0.071, 0.067) | (0.501, 0.080, 0.033)→(0.499, 0.078, 0.034) | 0.161→0.158 | 1.00 / 1.000 | 0.562 | 42.061 |
| push_1 | push | 1.00 / step_budget | (0.497, 0.071, 0.067)→(0.494, -0.088, 0.062) | (0.499, 0.078, 0.034)→(0.499, 0.078, 0.034) | 0.158→0.158 | 1.00 / 1.667 | 129.331 | 137.523 |
| retract_1 | retract | 1.00 / step_budget | (0.494, -0.088, 0.062)→(0.491, -0.087, 0.102) | (0.499, 0.078, 0.034)→(0.499, 0.078, 0.034) | 0.158→0.158 | 1.00 / 1.000 | 0.521 | 74.538 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.016
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.014
- phase_score: 0.553
- phase_breakdown.traverse_channel_score: 0.694
- phase_breakdown.reach_peg_top_score: 0.225

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.338
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.017
- **Median Q (composite search score)**: -0.109
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_1.push_distance
- **Final σ (mean)**: 0.309


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.38655,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.0856,"approach_1.speed":0.12638,"descend_1.speed":0.02483,"push_1.pose_tolerance":0.02929,"push_1.push_distance":0.15826,"push_1.speed":0.08475,"retract_1.speed":0.06147},"optimized_scores":{"best_composite_score":-0.10243,"best_fitness_score":0.33757,"best_task_score":0.01402},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":25.0,"contact_point_centroid":[0.49723,-0.10049,0.065],"force_p95":169.2184,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":169.26687,"mean_force":141.50153,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49672,-0.08895,0.06207]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":6.0,"contact_point_centroid":[0.49734,-0.10022,0.065],"force_p95":100.074,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":108.8033,"mean_force":69.36379,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49682,-0.08842,0.06205]},{"body_a":"peg","body_b":"channel_base_body","contact_count":486.0,"contact_point_centroid":[0.50426,0.0615,0.00937],"force_p95":0.60105,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.28595,"mean_force":2.84628,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50262,0.06593,0.10034]},{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.5127,0.06151,0.05804],"force_p95":66.29915,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.81961,"mean_force":53.31181,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50085,0.06212,0.05918]},{"body_a":"peg","body_b":"channel_base_body","contact_count":421.0,"contact_point_centroid":[0.5046,0.05325,0.00951],"force_p95":32.31542,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.68312,"mean_force":8.45972,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50002,0.05672,0.06209]},{"body_a":"attachment","body_b":"peg","contact_count":221.0,"contact_point_centroid":[0.51218,0.0586,0.05875],"force_p95":35.94217,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.20218,"mean_force":15.15116,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50033,0.05897,0.06012]},{"body_a":"peg","body_b":"channel_base_body","contact_count":525.0,"contact_point_centroid":[0.5036,0.06158,0.00934],"force_p95":0.60155,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56178,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50296,0.13342,0.21924]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49974,0.19857,0.29845]},{"body_a":"peg","body_b":"channel_base_body","contact_count":541.0,"contact_point_centroid":[0.50281,0.05904,0.00938],"force_p95":0.5519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55658,"mean_force":0.54662,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49687,-0.02036,0.06261]},{"body_a":"peg","body_b":"channel_base_body","contact_count":403.0,"contact_point_centroid":[0.5027,0.05888,0.00938],"force_p95":0.55169,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5517,"mean_force":0.54659,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49378,-0.08806,0.08232]}],"total_contact_groups":10},"final_pose_error":0.00999,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50279,0.05895,0.03379],"final_tcp_position":[0.49345,-0.08814,0.10267],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":169.26687,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":548.0,"n_steps_budget":600.0,"object_pos_end":[0.50378,0.06161,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.1418,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.56072,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":544.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_peg_top","tcp_end":[0.50727,0.07025,0.14567],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11229,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":486.0,"n_steps_budget":1000.0,"object_pos_end":[0.50413,0.06155,0.03328],"object_pos_start":[0.50378,0.06161,0.03376],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.1418,"object_z_max":0.03379,"peak_contact_force":66.54849,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":507.0,"raw_peak_contact_force":67.28595,"subtask_id":"reach_peg_top","tcp_end":[0.50138,0.06206,0.05806],"tcp_start":[0.50727,0.07025,0.14567],"tcp_to_object_dist_end":0.02494,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":421.0,"n_steps_budget":600.0,"object_pos_end":[0.50279,0.05896,0.03379],"object_pos_start":[0.50413,0.06155,0.03328],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.14177,"object_z_max":0.03511,"peak_contact_force":0.54366,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":642.0,"raw_peak_contact_force":40.68312,"subtask_id":"reach_peg_top","tcp_end":[0.50011,0.05235,0.06683],"tcp_start":[0.50138,0.06206,0.05806],"tcp_to_object_dist_end":0.03379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":541.0,"n_steps_budget":600.0,"object_pos_end":[0.50273,0.05896,0.03379],"object_pos_start":[0.50279,0.05896,0.03379],"object_to_goal_dist_end":0.13913,"object_to_goal_dist_start":0.13913,"object_z_max":0.03379,"peak_contact_force":168.76954,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":566.0,"raw_peak_contact_force":169.26687,"subtask_id":"traverse_channel","tcp_end":[0.49685,-0.08868,0.06205],"tcp_start":[0.50011,0.05235,0.06683],"tcp_to_object_dist_end":0.15044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":403.0,"n_steps_budget":600.0,"object_pos_end":[0.50279,0.05895,0.03379],"object_pos_start":[0.50273,0.05896,0.03379],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.13913,"object_z_max":0.03379,"peak_contact_force":0.53932,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":409.0,"raw_peak_contact_force":108.8033,"tcp_end":[0.49345,-0.08814,0.10267],"tcp_start":[0.49685,-0.08868,0.06205],"tcp_to_object_dist_end":0.1627,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56098,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.13216,"approach_1.speed":0.1128,"descend_1.speed":0.07129,"push_1.pose_tolerance":0.0137,"push_1.push_distance":0.2,"push_1.speed":0.0487,"retract_1.speed":0.0923},"optimized_scores":{"best_composite_score":-0.1088,"best_fitness_score":0.3312,"best_task_score":0.01681},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.5014,0.11603,0.00942],"force_p95":0.63195,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.26319,"mean_force":3.03086,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49634,0.11848,0.10078]},{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.50926,0.1155,0.05791],"force_p95":68.00557,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.73956,"mean_force":53.88544,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4974,0.11593,0.05898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":415.0,"contact_point_centroid":[0.50217,0.10733,0.00953],"force_p95":34.48827,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.98481,"mean_force":8.89805,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.497,0.11064,0.06197]},{"body_a":"attachment","body_b":"peg","contact_count":221.0,"contact_point_centroid":[0.50906,0.11265,0.05872],"force_p95":37.79315,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.54055,"mean_force":15.76306,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4972,0.11283,0.06007]},{"body_a":"peg","body_b":"channel_base_body","contact_count":453.0,"contact_point_centroid":[0.5009,0.11597,0.00936],"force_p95":0.62132,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56211,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49827,0.15994,0.22072]},{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.49998,0.11305,0.00943],"force_p95":0.5988,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65763,"mean_force":0.5417,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49049,-0.08524,0.0822]},{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50002,0.11329,0.00943],"force_p95":0.60323,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64552,"mean_force":0.54208,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49382,0.00727,0.06226]}],"total_contact_groups":7},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50004,0.11335,0.03393],"final_tcp_position":[0.49022,-0.08513,0.10262],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":69.26319,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":469.0,"n_steps_budget":600.0,"object_pos_end":[0.50096,0.11609,0.03391],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19619,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54858,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":453.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_peg_top","tcp_end":[0.49798,0.12181,0.14754],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":454.0,"n_steps_budget":600.0,"object_pos_end":[0.50132,0.11606,0.03318],"object_pos_start":[0.50096,0.11609,0.03391],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19619,"object_z_max":0.03401,"peak_contact_force":39.49362,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":475.0,"raw_peak_contact_force":69.26319,"subtask_id":"reach_peg_top","tcp_end":[0.49802,0.11598,0.05786],"tcp_start":[0.49798,0.12181,0.14754],"tcp_to_object_dist_end":0.0249,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":415.0,"n_steps_budget":600.0,"object_pos_end":[0.50002,0.11349,0.03384],"object_pos_start":[0.50132,0.11606,0.03318],"object_to_goal_dist_end":0.19359,"object_to_goal_dist_start":0.19618,"object_z_max":0.0351,"peak_contact_force":0.59411,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":636.0,"raw_peak_contact_force":42.98481,"subtask_id":"reach_peg_top","tcp_end":[0.49727,0.10643,0.06663],"tcp_start":[0.49802,0.11598,0.05786],"tcp_to_object_dist_end":0.03365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":978.0,"n_steps_budget":1000.0,"object_pos_end":[0.50003,0.11332,0.03394],"object_pos_start":[0.50002,0.11349,0.03384],"object_to_goal_dist_end":0.19341,"object_to_goal_dist_start":0.19359,"object_z_max":0.03413,"peak_contact_force":0.49583,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":978.0,"raw_peak_contact_force":0.64552,"subtask_id":"traverse_channel","tcp_end":[0.4936,-0.08566,0.06195],"tcp_start":[0.49727,0.10643,0.06663],"tcp_to_object_dist_end":0.20104,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":400.0,"n_steps_budget":600.0,"object_pos_end":[0.50004,0.11335,0.03393],"object_pos_start":[0.50003,0.11332,0.03394],"object_to_goal_dist_end":0.19344,"object_to_goal_dist_start":0.19341,"object_z_max":0.034,"peak_contact_force":0.48215,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":400.0,"raw_peak_contact_force":0.65763,"tcp_end":[0.49022,-0.08513,0.10262],"tcp_start":[0.4936,-0.08566,0.06195],"tcp_to_object_dist_end":0.21026,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59649,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.speed":0.09828,"approach_1.speed":0.09252,"descend_1.speed":0.09476,"push_1.pose_tolerance":0.01247,"push_1.push_distance":0.18822,"push_1.speed":0.06633,"retract_1.speed":0.08599},"optimized_scores":{"best_composite_score":-0.11539,"best_fitness_score":0.32461,"best_task_score":0.01243},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_base_body","contact_count":166.0,"contact_point_centroid":[0.49037,-0.10022,0.065],"force_p95":219.53178,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":242.65656,"mean_force":191.99901,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4898,-0.08839,0.06189]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49267,-0.1002,0.06499],"force_p95":104.58757,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.15282,"mean_force":75.53276,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49198,-0.0883,0.06133]},{"body_a":"peg","body_b":"channel_base_body","contact_count":528.0,"contact_point_centroid":[0.4959,0.06377,0.00939],"force_p95":37.06248,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":72.75997,"mean_force":3.87885,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48365,0.06764,0.09903]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.5025,0.06376,0.05789],"force_p95":71.89104,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":72.28984,"mean_force":58.73572,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49064,0.06424,0.05893]},{"body_a":"peg","body_b":"channel_base_body","contact_count":415.0,"contact_point_centroid":[0.49696,0.05531,0.00949],"force_p95":34.03622,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.5142,"mean_force":8.63107,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49139,0.05867,0.06208]},{"body_a":"attachment","body_b":"peg","contact_count":215.0,"contact_point_centroid":[0.50322,0.06061,0.05867],"force_p95":38.96616,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.89917,"mean_force":15.68063,"phase_index":2.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49137,0.061,0.05999]},{"body_a":"peg","body_b":"channel_base_body","contact_count":551.0,"contact_point_centroid":[0.49531,0.06385,0.00937],"force_p95":0.58227,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56098,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4885,0.13319,0.21788]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49922,0.19751,0.29687]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.49496,0.0609,0.0094],"force_p95":0.55052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55572,"mean_force":0.54518,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48891,-0.08794,0.08161]},{"body_a":"peg","body_b":"channel_base_body","contact_count":828.0,"contact_point_centroid":[0.4953,0.06107,0.0094],"force_p95":0.5505,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55315,"mean_force":0.54567,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48902,-0.03179,0.06258]}],"total_contact_groups":10},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49516,0.06072,0.03403],"final_tcp_position":[0.48856,-0.08804,0.10194],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":242.65656,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":578.0,"n_steps_budget":720.0,"object_pos_end":[0.4952,0.06369,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.1439,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54059,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":579.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg_top","tcp_end":[0.47925,0.07188,0.14552],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":528.0,"n_steps_budget":600.0,"object_pos_end":[0.49627,0.06358,0.03314],"object_pos_start":[0.4952,0.06369,0.03395],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.1439,"object_z_max":0.03402,"peak_contact_force":48.94544,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":558.0,"raw_peak_contact_force":72.75997,"subtask_id":"reach_peg_top","tcp_end":[0.49177,0.0642,0.05753],"tcp_start":[0.47925,0.07188,0.14552],"tcp_to_object_dist_end":0.02481,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":415.0,"n_steps_budget":600.0,"object_pos_end":[0.4952,0.06087,0.03389],"object_pos_start":[0.49627,0.06358,0.03314],"object_to_goal_dist_end":0.14108,"object_to_goal_dist_start":0.14379,"object_z_max":0.0352,"peak_contact_force":0.54705,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":630.0,"raw_peak_contact_force":42.5142,"subtask_id":"reach_peg_top","tcp_end":[0.49213,0.05431,0.06691],"tcp_start":[0.49177,0.0642,0.05753],"tcp_to_object_dist_end":0.0338,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":828.0,"n_steps_budget":900.0,"object_pos_end":[0.49495,0.0611,0.034],"object_pos_start":[0.4952,0.06087,0.03389],"object_to_goal_dist_end":0.14132,"object_to_goal_dist_start":0.14108,"object_z_max":0.03401,"peak_contact_force":218.72824,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":994.0,"raw_peak_contact_force":242.65656,"subtask_id":"traverse_channel","tcp_end":[0.49194,-0.0886,0.06128],"tcp_start":[0.49213,0.05431,0.06691],"tcp_to_object_dist_end":0.1522,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.49516,0.06072,0.03403],"object_pos_start":[0.49495,0.0611,0.034],"object_to_goal_dist_end":0.14093,"object_to_goal_dist_start":0.14132,"object_z_max":0.03403,"peak_contact_force":0.54254,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":404.0,"raw_peak_contact_force":114.15282,"tcp_end":[0.48856,-0.08804,0.10194],"tcp_start":[0.49194,-0.0886,0.06128],"tcp_to_object_dist_end":0.16366,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```