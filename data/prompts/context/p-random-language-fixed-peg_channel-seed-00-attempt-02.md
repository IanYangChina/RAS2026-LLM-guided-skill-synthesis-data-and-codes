## Search State

- **Seed**: 0
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5607 | 0.71 | ❌ rejected |
| 1 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1787 | 0.00 | ❌ rejected |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2281 | 0.74 | ✅ accepted |

**Proposal policy**: task_score is 0.71 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.561) — your mutation base

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

- **Composite score**: 0.561
- **task_score** (E): 0.710
- **fitness_score**: 0.618  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2301 |
| contact | 0.67 | 1.00 | 0.0458 |
| push | 0.00 | 1.00 | 0.1664 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.494, 0.143, 0.079) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.567 | 2.179 |
| contact | descend | 0.67 / force_exceeded | (0.494, 0.143, 0.079)→(0.493, 0.114, 0.044) | (0.500, 0.080, 0.034)→(0.499, 0.078, 0.034) | 0.161→0.158 | 1.00 / 2.000 | 11.533 | 13.265 |
| push | push | 0.00 / step_budget | (0.493, 0.114, 0.044)→(0.493, -0.052, 0.035) | (0.499, 0.078, 0.034)→(0.501, -0.050, 0.035) | 0.158→0.038 | 1.00 / 2.667 | 57.394 | 117.566 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.935
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.935
- phase_score: 0.660
- phase_breakdown.push_score: 0.712
- phase_breakdown.approach_score: 0.406
- phase_breakdown.contact_score: 0.758

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.770
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.438
- **K-run variance**: 0.0346
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Parameters at upper bound**: push.push_speed
- **Final σ (mean)**: 0.469


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82407,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.11918,"contact.contact_force":10.48358,"contact.contact_speed":0.07941,"push.push_depth":0.09102,"push.push_speed":0.07903},"optimized_scores":{"best_composite_score":0.8236,"best_fitness_score":0.77027,"best_task_score":0.9353},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":767.0,"contact_point_centroid":[0.5018,-0.02176,0.04702],"force_p95":145.76889,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":172.23639,"mean_force":32.06498,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49639,-0.01075,0.03457]},{"body_a":"peg","body_b":"channel_base_body","contact_count":232.0,"contact_point_centroid":[0.50796,-0.1017,0.05848],"force_p95":143.84973,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":151.12626,"mean_force":89.05903,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49548,-0.05989,0.03357]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":617.0,"contact_point_centroid":[0.52526,-0.05028,0.0382],"force_p95":44.59946,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.97897,"mean_force":9.396,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49619,-0.0234,0.03438]},{"body_a":"peg","body_b":"channel_base_body","contact_count":579.0,"contact_point_centroid":[0.50791,-0.04311,0.00985],"force_p95":19.45644,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.52147,"mean_force":6.5833,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49644,-0.0011,0.03455]},{"body_a":"peg","body_b":"channel_base_body","contact_count":335.0,"contact_point_centroid":[0.50381,0.0612,0.00938],"force_p95":0.56387,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.85719,"mean_force":0.61934,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50241,0.1075,0.05663]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50323,0.07925,0.05445],"force_p95":10.31011,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.57496,"mean_force":6.33683,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.50065,0.09129,0.03957]},{"body_a":"peg","body_b":"channel_base_body","contact_count":687.0,"contact_point_centroid":[0.50364,0.0616,0.00936],"force_p95":0.58283,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55798,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50272,0.16146,0.18499]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49978,0.19919,0.29844]}],"total_contact_groups":8},"final_pose_error":0.10519,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50916,-0.08806,0.03433],"final_tcp_position":[0.49416,-0.06631,0.03188],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":172.23639,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":710.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.06157,0.03377],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.56223,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":706.0,"raw_peak_contact_force":2.17216,"subtask_id":"approach","tcp_end":[0.50687,0.12518,0.07814],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07761,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":335.0,"n_steps_budget":600.0,"object_pos_end":[0.50375,0.06112,0.03422],"object_pos_start":[0.50376,0.06157,0.03377],"object_to_goal_dist_end":0.14129,"object_to_goal_dist_start":0.14176,"object_z_max":0.03414,"peak_contact_force":10.85719,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":339.0,"raw_peak_contact_force":10.85719,"subtask_id":"contact","tcp_end":[0.50062,0.0908,0.03907],"tcp_start":[0.50687,0.12518,0.07814],"tcp_to_object_dist_end":0.03024,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50916,-0.08806,0.03433],"object_pos_start":[0.50375,0.06112,0.03422],"object_to_goal_dist_end":0.01346,"object_to_goal_dist_start":0.14129,"object_z_max":0.03757,"peak_contact_force":169.73445,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2195.0,"raw_peak_contact_force":172.23639,"subtask_id":"push","tcp_end":[0.49416,-0.06631,0.03188],"tcp_start":[0.50062,0.0908,0.03907],"tcp_to_object_dist_end":0.02653,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09813,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.02024,"contact.contact_force":11.06383,"contact.contact_speed":0.0364,"push.push_depth":0.17627,"push.push_speed":0.03564},"optimized_scores":{"best_composite_score":0.43812,"best_fitness_score":0.71812,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":725.0,"contact_point_centroid":[0.49487,0.00661,0.00988],"force_p95":2.55097,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.37355,"mean_force":1.22584,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49383,0.04456,0.03031]},{"body_a":"attachment","body_b":"peg","contact_count":752.0,"contact_point_centroid":[0.49434,0.03299,0.03454],"force_p95":1.99074,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.97005,"mean_force":0.82027,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49382,0.04489,0.03029]},{"body_a":"peg","body_b":"channel_base_body","contact_count":421.0,"contact_point_centroid":[0.50085,0.11236,0.00951],"force_p95":2.78377,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.9614,"mean_force":0.76759,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.49571,0.15703,0.05419]},{"body_a":"attachment","body_b":"peg","contact_count":50.0,"contact_point_centroid":[0.49894,0.13007,0.04619],"force_p95":5.06745,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.69641,"mean_force":2.11515,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.49646,0.14196,0.03675]},{"body_a":"peg","body_b":"channel_base_body","contact_count":719.0,"contact_point_centroid":[0.501,0.11603,0.00939],"force_p95":0.60727,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55458,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49789,0.18763,0.18722]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":119.0,"contact_point_centroid":[0.47495,0.01682,0.03573],"force_p95":0.70279,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.11534,"mean_force":0.33047,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49372,0.04679,0.03014]}],"total_contact_groups":6},"final_pose_error":0.21336,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49732,-0.07301,0.03489],"final_tcp_position":[0.49438,-0.04315,0.03167],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":9.37355,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":735.0,"n_steps_budget":1000.0,"object_pos_end":[0.50088,0.11608,0.03387],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58788,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":719.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach","tcp_end":[0.49751,0.17635,0.07934],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":435.0,"n_steps_budget":1000.0,"object_pos_end":[0.49852,0.10883,0.035],"object_pos_start":[0.50088,0.11608,0.03387],"object_to_goal_dist_end":0.1889,"object_to_goal_dist_start":0.19618,"object_z_max":0.03573,"peak_contact_force":1.76517,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":471.0,"raw_peak_contact_force":6.9614,"subtask_id":"contact","tcp_end":[0.4967,0.13866,0.03301],"tcp_start":[0.49751,0.17635,0.07934],"tcp_to_object_dist_end":0.02995,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49732,-0.07301,0.03489],"object_pos_start":[0.49852,0.10883,0.035],"object_to_goal_dist_end":0.00907,"object_to_goal_dist_start":0.1889,"object_z_max":0.03586,"peak_contact_force":1.40841,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1596.0,"raw_peak_contact_force":9.37355,"subtask_id":"push","tcp_end":[0.49438,-0.04315,0.03167],"tcp_start":[0.4967,0.13866,0.03301],"tcp_to_object_dist_end":0.03018,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.11223,"contact.contact_force":21.39273,"contact.contact_speed":0.01198,"push.push_depth":0.02167,"push.push_speed":0.08},"optimized_scores":{"best_composite_score":0.4204,"best_fitness_score":0.36707,"best_task_score":0.19357},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":532.0,"contact_point_centroid":[0.47499,0.07113,0.0574],"force_p95":151.14158,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":171.08804,"mean_force":94.41004,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48504,0.07534,0.05598]},{"body_a":"attachment","body_b":"peg","contact_count":388.0,"contact_point_centroid":[0.49612,0.02843,0.04964],"force_p95":43.79665,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.2553,"mean_force":23.25869,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48787,0.03141,0.05051]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.49975,0.03339,0.00933],"force_p95":39.78749,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.80807,"mean_force":8.30915,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48652,0.0442,0.05186]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":5.0,"contact_point_centroid":[0.475,0.10133,0.05999],"force_p95":21.59972,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":21.97628,"mean_force":17.77475,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.4806,0.11184,0.05921]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":170.0,"contact_point_centroid":[0.52503,0.02155,0.05234],"force_p95":18.83057,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.6141,"mean_force":11.7236,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48687,0.05374,0.05305]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47497,0.03627,0.02908],"force_p95":6.50467,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.56697,"mean_force":2.10614,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48827,-0.00999,0.04401]},{"body_a":"peg","body_b":"channel_base_body","contact_count":674.0,"contact_point_centroid":[0.49532,0.06397,0.00937],"force_p95":0.56638,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55819,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48834,0.16237,0.18463]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49936,0.19878,0.29698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":440.0,"contact_point_centroid":[0.49529,0.06382,0.0094],"force_p95":0.55077,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54528,"phase_index":1.0,"phase_name":"contact","phase_type":"descend","tcp_position_centroid":[0.47918,0.11679,0.06471]}],"total_contact_groups":9},"final_pose_error":0.05579,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49689,0.01029,0.03541],"final_tcp_position":[0.49152,-0.04654,0.04069],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":171.08804,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":701.0,"n_steps_budget":1000.0,"object_pos_end":[0.49489,0.06374,0.03397],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14396,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55032,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":702.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach","tcp_end":[0.47876,0.12745,0.07894],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07964,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":440.0,"n_steps_budget":1000.0,"object_pos_end":[0.49493,0.0641,0.03402],"object_pos_start":[0.49489,0.06374,0.03397],"object_to_goal_dist_end":0.14432,"object_to_goal_dist_start":0.14396,"object_z_max":0.03402,"peak_contact_force":21.97628,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":445.0,"raw_peak_contact_force":21.97628,"subtask_id":"contact","tcp_end":[0.48062,0.11182,0.05919],"tcp_start":[0.47876,0.12745,0.07894],"tcp_to_object_dist_end":0.05581,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49689,0.01029,0.03541],"object_pos_start":[0.49493,0.0641,0.03402],"object_to_goal_dist_end":0.09046,"object_to_goal_dist_start":0.14432,"object_z_max":0.04066,"peak_contact_force":1.03829,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2095.0,"raw_peak_contact_force":171.08804,"subtask_id":"push","tcp_end":[0.49152,-0.04654,0.04069],"tcp_start":[0.48062,0.11182,0.05919],"tcp_to_object_dist_end":0.05733,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```