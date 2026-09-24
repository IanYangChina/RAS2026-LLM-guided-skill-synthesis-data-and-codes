## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.2656 | 0.00 | ❌ rejected |
| 5 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.3173 | 0.10 | ❌ rejected |
| 4 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | 0.1308 | 0.80 | ❌ rejected |
| 3 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.3785 | 0.05 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2540 | 0.81 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.266) — your mutation base

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

- **Composite score**: -0.266
- **task_score** (E): 0.005
- **fitness_score**: 0.124  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1295 |
| approach_1 | 1.00 | 1.00 | 0.1050 |
| descend_1 | 1.00 | 1.00 | 0.0323 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 0.67 | 1.00 | 0.1193 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.127, 0.196) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.546 | 2.179 |
| approach_1 | approach | 1.00 / step_budget | (0.497, 0.127, 0.196)→(0.496, 0.108, 0.094) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.549 | 0.590 |
| descend_1 | contact | 1.00 / force_exceeded | (0.496, 0.108, 0.094)→(0.494, 0.096, 0.064) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 16.574 | 16.574 |
| push_1 | push | 0.00 / guard_failure | (0.494, 0.095, 0.063)→(0.494, 0.095, 0.063) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.000 | 23.969 | 37.277 |
| retract_1 | retract | 0.67 / step_budget | (0.494, 0.095, 0.063)→(0.491, 0.102, 0.182) | (0.500, 0.080, 0.034)→(0.499, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.539 | 27.640 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.006
- alignment_error: None
- force_efficiency: 0.286
- terminal_score: 0.004
- phase_score: 0.209
- phase_breakdown.approach_score: 0.326
- phase_breakdown.push_score: 0.041
- phase_breakdown.contact_score: 0.596

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.127
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.007
- **Median Q (composite search score)**: -0.265
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.274


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.625,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00409,"align_1.speed":0.18164,"approach_1.arc_height":0.05023,"approach_1.speed":0.05662,"descend_1.contact_force_threshold":5.64085,"descend_1.speed":0.02559,"push_1.push_distance":0.19783,"push_1.push_speed":0.03093,"retract_1.retract_height":0.17291,"retract_1.speed":0.09976},"optimized_scores":{"best_composite_score":-0.2645,"best_fitness_score":0.1255,"best_task_score":0.004},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":9.0,"contact_point_centroid":[0.48992,0.05525,0.00933],"force_p95":35.06736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.50351,"mean_force":25.57172,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49754,0.07671,0.06331]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50845,0.07688,0.05858],"force_p95":34.66959,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.10357,"mean_force":25.12631,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49754,0.07671,0.06331]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50266,0.06096,0.0094],"force_p95":0.55649,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.28033,"mean_force":0.64355,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49434,0.08748,0.14249]},{"body_a":"attachment","body_b":"peg","contact_count":19.0,"contact_point_centroid":[0.50764,0.07627,0.05897],"force_p95":24.67443,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.70854,"mean_force":5.19656,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49675,0.07643,0.06359]},{"body_a":"peg","body_b":"channel_base_body","contact_count":203.0,"contact_point_centroid":[0.50376,0.06167,0.00938],"force_p95":0.55002,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.67368,"mean_force":0.63113,"phase_index":2.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.49797,0.08296,0.07765]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50863,0.07715,0.05877],"force_p95":17.17881,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.17881,"mean_force":17.17881,"phase_index":2.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.49772,0.07704,0.06375]},{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.50353,0.06161,0.00933],"force_p95":0.59536,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56675,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50494,0.15286,0.24348]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49977,0.19855,0.29847]},{"body_a":"peg","body_b":"channel_base_body","contact_count":525.0,"contact_point_centroid":[0.50382,0.06155,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55261,"mean_force":0.54676,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.504,0.12373,0.13598]}],"total_contact_groups":9},"final_pose_error":0.01168,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5031,0.06085,0.03388],"final_tcp_position":[0.49486,0.07818,0.22466],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":35.50351,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":423.0,"n_steps_budget":600.0,"object_pos_end":[0.50377,0.06159,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54977,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":419.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.51102,0.10954,0.19439],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.06157,0.03378],"object_pos_start":[0.50377,0.06159,0.03378],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14178,"object_z_max":0.03378,"peak_contact_force":0.54875,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":525.0,"raw_peak_contact_force":0.55261,"tcp_end":[0.50007,0.08898,0.09321],"tcp_start":[0.51102,0.10954,0.19439],"tcp_to_object_dist_end":0.06556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":203.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06156,0.03378],"object_pos_start":[0.50374,0.06157,0.03378],"object_to_goal_dist_end":0.14175,"object_to_goal_dist_start":0.14176,"object_z_max":0.03378,"peak_contact_force":17.67368,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":204.0,"raw_peak_contact_force":17.67368,"tcp_end":[0.49772,0.07699,0.06364],"tcp_start":[0.50007,0.08898,0.09321],"tcp_to_object_dist_end":0.03415,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.50335,0.06124,0.03381],"object_pos_start":[0.50377,0.06156,0.03378],"object_to_goal_dist_end":0.14141,"object_to_goal_dist_start":0.14175,"object_z_max":0.03382,"peak_contact_force":22.75097,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":18.0,"raw_peak_contact_force":35.50351,"tcp_end":[0.49737,0.07625,0.063],"tcp_start":[0.49739,0.07632,0.06305],"tcp_to_object_dist_end":0.03336,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.5031,0.06085,0.03388],"object_pos_start":[0.5033,0.06115,0.03382],"object_to_goal_dist_end":0.14101,"object_to_goal_dist_start":0.14132,"object_z_max":0.03492,"peak_contact_force":0.54689,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1016.0,"raw_peak_contact_force":25.28033,"tcp_end":[0.49486,0.07818,0.22466],"tcp_start":[0.49737,0.07625,0.063],"tcp_to_object_dist_end":0.19175,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.9382,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00859,"align_1.speed":0.29975,"approach_1.arc_height":0.05465,"approach_1.speed":0.03232,"descend_1.contact_force_threshold":1.62141,"descend_1.speed":0.02525,"push_1.push_distance":0.04255,"push_1.push_speed":0.03133,"retract_1.retract_height":0.14095,"retract_1.speed":0.03809},"optimized_scores":{"best_composite_score":-0.26932,"best_fitness_score":0.12068,"best_task_score":0.00684},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.49306,0.10737,0.00943],"force_p95":37.35459,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.64639,"mean_force":27.86192,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49484,0.13077,0.06321]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50581,0.13105,0.05865],"force_p95":36.98436,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.30449,"mean_force":27.45631,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49484,0.13077,0.06321]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49989,0.11518,0.00943],"force_p95":0.62752,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.08907,"mean_force":0.6795,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49129,0.13985,0.10614]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.50462,0.13001,0.05898],"force_p95":22.87966,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.60322,"mean_force":4.47609,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49367,0.13036,0.06345]},{"body_a":"peg","body_b":"channel_base_body","contact_count":198.0,"contact_point_centroid":[0.50083,0.11613,0.00942],"force_p95":0.60776,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.66186,"mean_force":0.6084,"phase_index":2.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.49533,0.13748,0.07811]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50605,0.13157,0.05894],"force_p95":13.24881,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.24881,"mean_force":13.24881,"phase_index":2.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.49507,0.13125,0.06377]},{"body_a":"peg","body_b":"channel_base_body","contact_count":315.0,"contact_point_centroid":[0.50103,0.116,0.00932],"force_p95":0.67179,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.5718,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5022,0.17968,0.24679]},{"body_a":"peg","body_b":"channel_base_body","contact_count":549.0,"contact_point_centroid":[0.50088,0.11603,0.00941],"force_p95":0.61331,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66544,"mean_force":0.54342,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50032,0.17593,0.14033]}],"total_contact_groups":8},"final_pose_error":0.05346,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50036,0.11494,0.0339],"final_tcp_position":[0.49149,0.14168,0.15166],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":40.64639,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":331.0,"n_steps_budget":600.0,"object_pos_end":[0.50095,0.11608,0.03384],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.53839,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":315.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.50577,0.16043,0.19791],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":549.0,"n_steps_budget":1000.0,"object_pos_end":[0.50103,0.11604,0.03385],"object_pos_start":[0.50095,0.11608,0.03384],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19618,"object_z_max":0.03399,"peak_contact_force":0.55051,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":549.0,"raw_peak_contact_force":0.66544,"tcp_end":[0.49735,0.14385,0.09386],"tcp_start":[0.50577,0.16043,0.19791],"tcp_to_object_dist_end":0.06624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":198.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11594,0.03387],"object_pos_start":[0.50103,0.11604,0.03385],"object_to_goal_dist_end":0.19603,"object_to_goal_dist_start":0.19614,"object_z_max":0.03399,"peak_contact_force":13.66186,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":199.0,"raw_peak_contact_force":13.66186,"tcp_end":[0.49509,0.1312,0.06365],"tcp_start":[0.49735,0.14385,0.09386],"tcp_to_object_dist_end":0.03396,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.50061,0.11551,0.03392],"object_pos_start":[0.50092,0.11594,0.03387],"object_to_goal_dist_end":0.1956,"object_to_goal_dist_start":0.19603,"object_z_max":0.03393,"peak_contact_force":28.81253,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":24.0,"raw_peak_contact_force":40.64639,"tcp_end":[0.49461,0.13009,0.0628],"tcp_start":[0.49464,0.13016,0.06286],"tcp_to_object_dist_end":0.0329,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50036,0.11494,0.0339],"object_pos_start":[0.5006,0.11543,0.0339],"object_to_goal_dist_end":0.19504,"object_to_goal_dist_start":0.19553,"object_z_max":0.03534,"peak_contact_force":0.52116,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1031.0,"raw_peak_contact_force":35.08907,"tcp_end":[0.49149,0.14168,0.15166],"tcp_start":[0.49461,0.13009,0.0628],"tcp_to_object_dist_end":0.12108,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4812,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00799,"align_1.speed":0.13505,"approach_1.arc_height":0.05285,"approach_1.speed":0.05154,"descend_1.contact_force_threshold":5.14628,"descend_1.speed":0.03198,"push_1.push_distance":0.12537,"push_1.push_speed":0.02322,"retract_1.retract_height":0.1341,"retract_1.speed":0.06243},"optimized_scores":{"best_composite_score":-0.26294,"best_fitness_score":0.12706,"best_task_score":0.00412},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.49432,0.05867,0.00934],"force_p95":35.23829,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.68121,"mean_force":23.62245,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48893,0.0788,0.0635]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49975,0.07906,0.05857],"force_p95":34.7852,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.23947,"mean_force":23.18139,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48893,0.0788,0.0635]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49442,0.06322,0.0094],"force_p95":0.57734,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.552,"mean_force":0.62641,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48543,0.08736,0.11531]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.49871,0.07787,0.05879],"force_p95":20.12439,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.01201,"mean_force":3.56066,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48791,0.07805,0.06368]},{"body_a":"peg","body_b":"channel_base_body","contact_count":196.0,"contact_point_centroid":[0.49527,0.06378,0.0094],"force_p95":0.55081,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.38691,"mean_force":0.63626,"phase_index":2.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.48949,0.08554,0.07816]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50009,0.07979,0.05902],"force_p95":17.96009,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.96009,"mean_force":17.96009,"phase_index":2.0,"phase_name":"descend_1","phase_type":"contact","tcp_position_centroid":[0.48926,0.07948,0.06417]},{"body_a":"peg","body_b":"channel_base_body","contact_count":399.0,"contact_point_centroid":[0.49568,0.06391,0.00936],"force_p95":0.60961,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56679,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48514,0.15399,0.24381]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49895,0.19791,0.29741]},{"body_a":"peg","body_b":"channel_base_body","contact_count":583.0,"contact_point_centroid":[0.49491,0.06377,0.0094],"force_p95":0.55052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54548,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48225,0.12758,0.13737]}],"total_contact_groups":9},"final_pose_error":0.02882,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49461,0.06286,0.0339],"final_tcp_position":[0.4857,0.08494,0.16935],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":35.68121,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":426.0,"n_steps_budget":690.0,"object_pos_end":[0.49504,0.06406,0.03393],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14427,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54985,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":427.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.47282,0.11204,0.19544],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16995,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.49532,0.06371,0.03401],"object_pos_start":[0.49504,0.06406,0.03393],"object_to_goal_dist_end":0.14391,"object_to_goal_dist_start":0.14427,"object_z_max":0.03401,"peak_contact_force":0.54796,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":583.0,"raw_peak_contact_force":0.55289,"tcp_end":[0.49148,0.09171,0.09363],"tcp_start":[0.47282,0.11204,0.19544],"tcp_to_object_dist_end":0.06598,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":196.0,"n_steps_budget":1000.0,"object_pos_end":[0.49539,0.06383,0.03402],"object_pos_start":[0.49532,0.06371,0.03401],"object_to_goal_dist_end":0.14403,"object_to_goal_dist_start":0.14391,"object_z_max":0.03402,"peak_contact_force":18.38691,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":197.0,"raw_peak_contact_force":18.38691,"tcp_end":[0.48926,0.07942,0.06405],"tcp_start":[0.49148,0.09171,0.09363],"tcp_to_object_dist_end":0.03439,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":14.0,"n_steps_budget":1000.0,"object_pos_end":[0.49491,0.06335,0.03366],"object_pos_start":[0.49539,0.06383,0.03402],"object_to_goal_dist_end":0.14358,"object_to_goal_dist_start":0.14403,"object_z_max":0.03402,"peak_contact_force":20.34283,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":28.0,"raw_peak_contact_force":35.68121,"tcp_end":[0.48869,0.07785,0.06302],"tcp_start":[0.48872,0.07793,0.06308],"tcp_to_object_dist_end":0.03333,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49461,0.06286,0.0339],"object_pos_start":[0.49488,0.06327,0.03364],"object_to_goal_dist_end":0.14309,"object_to_goal_dist_start":0.1435,"object_z_max":0.03495,"peak_contact_force":0.54769,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1023.0,"raw_peak_contact_force":22.552,"tcp_end":[0.4857,0.08494,0.16935],"tcp_start":[0.48869,0.07785,0.06302],"tcp_to_object_dist_end":0.13753,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```