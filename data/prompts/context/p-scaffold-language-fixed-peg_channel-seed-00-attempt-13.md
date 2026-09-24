## Search State

- **Seed**: 0
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2504 | 0.81 | ❌ rejected |
| 12 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2190 | 0.78 | ❌ rejected |
| 11 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2603 | 0.83 | ❌ rejected |
| 10 | approach → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 12 | -0.2603 | 0.08 | ❌ rejected |
| 9 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1451 | 0.10 | ❌ rejected |

**Proposal policy**: task_score is 0.81 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.04, 0.00) | distance | — |
| contact | object | (0.00, 0.02, 0.00) | distance | — |
| push | world | (0.50, -0.08, 0.04) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.250) — your mutation base

```yaml
skill: peg_channel
phases:
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
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
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

```

## Design Metrics

- **Composite score**: 0.250
- **task_score** (E): 0.811
- **fitness_score**: 0.690  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2615 |
| approach_1 | 1.00 | 1.00 | 0.0099 |
| contact_1 | 1.00 | 1.00 | 0.0114 |
| push_1 | 0.67 | 1.00 | 0.1553 |
| retract_1 | 0.00 | 1.00 | 0.1022 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.125, 0.051) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.333 | 111.931 | 119.907 |
| approach_1 | approach | 1.00 / step_budget | (0.495, 0.125, 0.051)→(0.496, 0.122, 0.042) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.333 | 39.219 | 141.478 |
| contact_1 | contact | 1.00 / step_budget | (0.496, 0.122, 0.042)→(0.497, 0.114, 0.036) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.333 | 141.578 | 159.378 |
| push_1 | push | 0.67 / step_budget | (0.497, 0.114, 0.036)→(0.498, -0.042, 0.037) | (0.500, 0.080, 0.034)→(0.502, -0.070, 0.036) | 0.160→0.017 | 1.00 / 2.333 | 23.082 | 123.862 |
| retract_1 | retract | 0.00 / step_budget | (0.498, -0.042, 0.037)→(0.496, -0.000, 0.130) | (0.502, -0.070, 0.036)→(0.502, -0.069, 0.034) | 0.017→0.017 | 1.00 / 1.000 | 0.546 | 65.415 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.890
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.865
- phase_score: 0.657
- phase_breakdown.approach_score: 0.856
- phase_breakdown.push_score: 0.579
- phase_breakdown.contact_score: 0.691

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.740
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.991
- **Median Q (composite search score)**: 0.262
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.351


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29714,"average_solve_count":175.0,"average_success_count":175.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00676,"approach_1.approach_height":0.19616,"contact_1.contact_force":13.32903,"push_1.push_distance":0.14325,"push_1.push_speed":0.09362,"retract_1.retract_height":0.1026,"retract_1.speed":0.05527},"optimized_scores":{"best_composite_score":0.29997,"best_fitness_score":0.73997,"best_task_score":0.86481},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.10482,0.06],"force_p95":116.55472,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.55472,"mean_force":116.55472,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50457,0.10474,0.04324]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":700.0,"contact_point_centroid":[0.54468,0.02727,0.05999],"force_p95":105.60033,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.42459,"mean_force":86.01627,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49994,0.02922,0.03667]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":327.0,"contact_point_centroid":[0.54556,0.0976,0.05997],"force_p95":113.6143,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.42509,"mean_force":77.26061,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50097,0.09694,0.03612]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":246.0,"contact_point_centroid":[0.52502,0.09709,0.05999],"force_p95":112.31273,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":112.94108,"mean_force":79.56813,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50103,0.09694,0.03618]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52502,0.09679,0.05999],"force_p95":65.18499,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.59131,"mean_force":22.83479,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50101,0.09665,0.03613]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54328,-0.04891,0.05999],"force_p95":61.818,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.42183,"mean_force":55.9359,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49863,-0.05297,0.03668]},{"body_a":"attachment","body_b":"peg","contact_count":447.0,"contact_point_centroid":[0.50194,-0.00708,0.041],"force_p95":20.64542,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.53732,"mean_force":5.06024,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49962,0.00458,0.03674]},{"body_a":"peg","body_b":"channel_base_body","contact_count":19.0,"contact_point_centroid":[0.50662,-0.10031,0.05987],"force_p95":40.94273,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.03327,"mean_force":15.24861,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49861,-0.05198,0.03669]},{"body_a":"peg","body_b":"channel_base_body","contact_count":776.0,"contact_point_centroid":[0.50127,-0.01143,0.00969],"force_p95":18.25055,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.44163,"mean_force":2.92422,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49993,0.02849,0.03668]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.50499,-0.06396,0.05015],"force_p95":7.24252,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.0463,"mean_force":1.50604,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49786,-0.05218,0.03737]},{"body_a":"peg","body_b":"channel_base_body","contact_count":22.0,"contact_point_centroid":[0.50634,-0.1003,0.06026],"force_p95":7.31326,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.02045,"mean_force":1.40103,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.498,-0.05246,0.03715]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":276.0,"contact_point_centroid":[0.47485,0.0171,0.03062],"force_p95":1.54272,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.79817,"mean_force":0.53566,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50022,0.04739,0.03672]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":98.0,"contact_point_centroid":[0.52507,-0.04994,0.02833],"force_p95":4.83833,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.90624,"mean_force":1.10978,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49933,-0.02088,0.03681]},{"body_a":"peg","body_b":"channel_base_body","contact_count":812.0,"contact_point_centroid":[0.50369,0.06161,0.00935],"force_p95":0.64051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55646,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50246,0.15146,0.16945]},{"body_a":"peg","body_b":"channel_base_body","contact_count":979.0,"contact_point_centroid":[0.50535,-0.08095,0.0094],"force_p95":0.55366,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.76799,"mean_force":0.54836,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49522,-0.02644,0.08159]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49971,0.19912,0.29835]}],"total_contact_groups":18},"final_pose_error":0.17312,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50538,-0.0808,0.03388],"final_tcp_position":[0.49567,-0.00807,0.12712],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":116.55472,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":835.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06154,0.03379],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14173,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.5445,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":831.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.50647,0.10562,0.04772],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":23.0,"n_steps_budget":600.0,"object_pos_end":[0.50379,0.06161,0.03379],"object_pos_start":[0.50377,0.06154,0.03379],"object_to_goal_dist_end":0.14179,"object_to_goal_dist_start":0.14173,"object_z_max":0.03379,"peak_contact_force":116.55472,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":116.55472,"tcp_end":[0.50449,0.10469,0.043],"tcp_start":[0.50647,0.10562,0.04772],"tcp_to_object_dist_end":0.04406,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":406.0,"n_steps_budget":600.0,"object_pos_end":[0.50379,0.06157,0.0338],"object_pos_start":[0.50379,0.06161,0.03379],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14179,"object_z_max":0.0338,"peak_contact_force":114.42509,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":979.0,"raw_peak_contact_force":114.42509,"tcp_end":[0.50101,0.09668,0.03611],"tcp_start":[0.50449,0.10469,0.043],"tcp_to_object_dist_end":0.03529,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50681,-0.08134,0.03628],"object_pos_start":[0.50379,0.06157,0.0338],"object_to_goal_dist_end":0.00787,"object_to_goal_dist_start":0.14176,"object_z_max":0.03767,"peak_contact_force":68.13822,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2323.0,"raw_peak_contact_force":115.42459,"tcp_end":[0.49863,-0.05291,0.03668],"tcp_start":[0.50101,0.09668,0.03611],"tcp_to_object_dist_end":0.02958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50538,-0.0808,0.03388],"object_pos_start":[0.50681,-0.08134,0.03628],"object_to_goal_dist_end":0.00819,"object_to_goal_dist_start":0.00787,"object_z_max":0.03628,"peak_contact_force":0.54644,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1026.0,"raw_peak_contact_force":62.42183,"tcp_end":[0.49567,-0.00807,0.12712],"tcp_start":[0.49863,-0.05291,0.03668],"tcp_to_object_dist_end":0.11865,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27374,"average_solve_count":179.0,"average_success_count":179.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00786,"approach_1.approach_height":0.2052,"contact_1.contact_force":1.79023,"push_1.push_distance":0.17844,"push_1.push_speed":0.09996,"retract_1.retract_height":0.16043,"retract_1.speed":0.03921},"optimized_scores":{"best_composite_score":0.26209,"best_fitness_score":0.70209,"best_task_score":0.99126},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":283.0,"contact_point_centroid":[0.54773,0.12,0.05998],"force_p95":128.3165,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":131.33072,"mean_force":80.04581,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49551,0.14659,0.0343]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":739.0,"contact_point_centroid":[0.54353,0.067,0.05998],"force_p95":119.76011,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":130.95809,"mean_force":99.83278,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49787,0.07116,0.03635]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54318,-0.02274,0.06],"force_p95":68.35216,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.52081,"mean_force":54.08434,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4985,-0.01745,0.03691]},{"body_a":"attachment","body_b":"peg","contact_count":412.0,"contact_point_centroid":[0.50197,0.05793,0.04169],"force_p95":23.95489,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.98511,"mean_force":4.55991,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49788,0.06953,0.03637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":732.0,"contact_point_centroid":[0.50231,0.02961,0.00975],"force_p95":18.3958,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.34644,"mean_force":2.82529,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49788,0.07079,0.03634]},{"body_a":"peg","body_b":"channel_base_body","contact_count":418.0,"contact_point_centroid":[0.50076,0.11464,0.00945],"force_p95":0.65217,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.27037,"mean_force":0.63327,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49521,0.1481,0.0352]},{"body_a":"attachment","body_b":"peg","contact_count":46.0,"contact_point_centroid":[0.50067,0.13372,0.04272],"force_p95":2.79028,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.98287,"mean_force":1.04541,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49668,0.14564,0.03421]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":392.0,"contact_point_centroid":[0.52528,0.03899,0.03462],"force_p95":5.30265,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.46362,"mean_force":1.18221,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49782,0.06831,0.03642]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":68.0,"contact_point_centroid":[0.47488,0.02858,0.02153],"force_p95":1.51526,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.14373,"mean_force":0.76823,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49837,0.0594,0.03682]},{"body_a":"peg","body_b":"channel_base_body","contact_count":755.0,"contact_point_centroid":[0.50092,0.11599,0.00939],"force_p95":0.61661,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55392,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4977,0.17803,0.1717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50603,-0.0468,0.0094],"force_p95":0.56314,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.0613,"mean_force":0.54827,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49518,0.00115,0.08187]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50075,0.11655,0.00946],"force_p95":0.5787,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58479,"mean_force":0.54094,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49639,0.15694,0.04619]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50606,-0.02754,0.05884],"force_p95":0.14526,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.201,"mean_force":0.03083,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49666,-0.01581,0.03911]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.525,-0.04932,0.06],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49833,-0.01776,0.03703]}],"total_contact_groups":14},"final_pose_error":0.17205,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50612,-0.04654,0.03383],"final_tcp_position":[0.49564,0.01349,0.12853],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":131.33072,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11605,0.03394],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54801,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":755.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49706,0.15726,0.04892],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":28.0,"n_steps_budget":600.0,"object_pos_end":[0.50092,0.11601,0.03391],"object_pos_start":[0.50095,0.11605,0.03394],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19615,"object_z_max":0.03394,"peak_contact_force":0.54838,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28.0,"raw_peak_contact_force":0.58479,"tcp_end":[0.49634,0.15677,0.04264],"tcp_start":[0.49706,0.15726,0.04892],"tcp_to_object_dist_end":0.04193,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":418.0,"n_steps_budget":600.0,"object_pos_end":[0.50145,0.11511,0.03456],"object_pos_start":[0.50092,0.11601,0.03391],"object_to_goal_dist_end":0.1952,"object_to_goal_dist_start":0.19611,"object_z_max":0.03456,"peak_contact_force":103.05412,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":747.0,"raw_peak_contact_force":131.33072,"tcp_end":[0.49714,0.14524,0.03415],"tcp_start":[0.49634,0.15677,0.04264],"tcp_to_object_dist_end":0.03044,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50671,-0.04642,0.03648],"object_pos_start":[0.50145,0.11511,0.03456],"object_to_goal_dist_end":0.03442,"object_to_goal_dist_start":0.1952,"object_z_max":0.03896,"peak_contact_force":1.10433,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2343.0,"raw_peak_contact_force":130.95809,"tcp_end":[0.4985,-0.0173,0.03691],"tcp_start":[0.49714,0.14524,0.03415],"tcp_to_object_dist_end":0.03026,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50612,-0.04654,0.03383],"object_pos_start":[0.50671,-0.04642,0.03648],"object_to_goal_dist_end":0.03457,"object_to_goal_dist_start":0.03442,"object_z_max":0.03648,"peak_contact_force":0.5448,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1013.0,"raw_peak_contact_force":70.52081,"tcp_end":[0.49564,0.01349,0.12853],"tcp_start":[0.4985,-0.0173,0.03691],"tcp_to_object_dist_end":0.11261,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51445,"average_solve_count":173.0,"average_success_count":173.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00548,"approach_1.approach_height":0.24263,"contact_1.contact_force":9.92633,"push_1.push_distance":0.17782,"push_1.push_speed":0.0948,"retract_1.retract_height":0.09943,"retract_1.speed":0.06261},"optimized_scores":{"best_composite_score":0.18921,"best_fitness_score":0.62921,"best_task_score":0.5778},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":60.0,"contact_point_centroid":[0.4749,0.12,0.0598],"force_p95":341.5277,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.62701,"mean_force":311.80708,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47984,0.111,0.05723]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.47497,0.11792,0.05994],"force_p95":283.70214,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.29523,"mean_force":209.67753,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48303,0.11067,0.05591]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":409.0,"contact_point_centroid":[0.535,0.10349,0.05995],"force_p95":214.24986,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":232.3783,"mean_force":173.94326,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48947,0.10213,0.03793]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":738.0,"contact_point_centroid":[0.54082,0.02617,0.05999],"force_p95":116.11804,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":125.20325,"mean_force":96.5736,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49547,0.02798,0.03787]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54297,-0.05044,0.05999],"force_p95":62.87625,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":63.30255,"mean_force":58.12178,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49792,-0.0545,0.03747]},{"body_a":"attachment","body_b":"peg","contact_count":296.0,"contact_point_centroid":[0.49724,0.00975,0.03971],"force_p95":19.43275,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.90149,"mean_force":4.00128,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49568,0.02139,0.03787]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.49346,-0.10017,0.04974],"force_p95":39.98422,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.07061,"mean_force":14.05504,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49782,-0.05278,0.0375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":784.0,"contact_point_centroid":[0.49814,-0.01035,0.00957],"force_p95":7.79549,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.1689,"mean_force":1.6353,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49547,0.02828,0.03788]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.49592,-0.06495,0.03921],"force_p95":8.11853,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.35181,"mean_force":2.87158,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49694,-0.05324,0.03865]},{"body_a":"peg","body_b":"channel_base_body","contact_count":34.0,"contact_point_centroid":[0.49306,-0.10059,0.05746],"force_p95":8.73533,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.34616,"mean_force":4.61527,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49693,-0.05325,0.03861]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":69.0,"contact_point_centroid":[0.52522,-0.02938,0.03968],"force_p95":8.2014,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.77454,"mean_force":1.62375,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49652,-0.00086,0.03789]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":156.0,"contact_point_centroid":[0.47477,-0.04161,0.03223],"force_p95":2.88466,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.93432,"mean_force":0.80088,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49667,-0.01062,0.03776]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":22.0,"contact_point_centroid":[0.47487,-0.08302,0.05999],"force_p95":5.68127,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.69671,"mean_force":4.20115,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49659,-0.05273,0.03902]},{"body_a":"peg","body_b":"channel_base_body","contact_count":820.0,"contact_point_centroid":[0.49531,0.0638,0.00938],"force_p95":0.56258,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55591,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48773,0.15105,0.1656]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49933,0.19869,0.29695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.49477,-0.08065,0.0094],"force_p95":0.55638,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.96352,"mean_force":0.54738,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4947,-0.02576,0.08668]}],"total_contact_groups":18},"final_pose_error":0.16479,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49488,-0.08078,0.03389],"final_tcp_position":[0.49539,-0.00675,0.13542],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":355.62701,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.49535,0.06392,0.03399],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":334.70153,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":908.0,"raw_peak_contact_force":355.62701,"tcp_end":[0.481,0.11081,0.05671],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":95.0,"n_steps_budget":600.0,"object_pos_end":[0.49532,0.06402,0.034],"object_pos_start":[0.49535,0.06392,0.03399],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14412,"object_z_max":0.034,"peak_contact_force":0.55289,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":125.0,"raw_peak_contact_force":307.29523,"tcp_end":[0.48856,0.10593,0.04095],"tcp_start":[0.481,0.11081,0.05671],"tcp_to_object_dist_end":0.04301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":439.0,"n_steps_budget":600.0,"object_pos_end":[0.49527,0.06412,0.03403],"object_pos_start":[0.49532,0.06402,0.034],"object_to_goal_dist_end":0.14432,"object_to_goal_dist_start":0.14422,"object_z_max":0.03403,"peak_contact_force":207.25489,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":848.0,"raw_peak_contact_force":232.3783,"tcp_end":[0.49312,0.0992,0.03757],"tcp_start":[0.48856,0.10593,0.04095],"tcp_to_object_dist_end":0.03533,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49362,-0.08328,0.03553],"object_pos_start":[0.49527,0.06412,0.03403],"object_to_goal_dist_end":0.00845,"object_to_goal_dist_start":0.14432,"object_z_max":0.03992,"peak_contact_force":0.00402,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2063.0,"raw_peak_contact_force":125.20325,"tcp_end":[0.49792,-0.0544,0.03748],"tcp_start":[0.49312,0.0992,0.03757],"tcp_to_object_dist_end":0.02926,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49488,-0.08078,0.03389],"object_pos_start":[0.49362,-0.08328,0.03553],"object_to_goal_dist_end":0.00801,"object_to_goal_dist_start":0.00845,"object_z_max":0.03611,"peak_contact_force":0.54581,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1059.0,"raw_peak_contact_force":63.30255,"tcp_end":[0.49539,-0.00675,0.13542],"tcp_start":[0.49792,-0.0544,0.03748],"tcp_to_object_dist_end":0.12565,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```