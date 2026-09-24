## Search State

- **Seed**: 0
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | 0.1308 | 0.80 | ❌ rejected |
| 3 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 10 | -0.3785 | 0.05 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2540 | 0.81 | ❌ rejected |
| 1 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2471 | 0.78 | ❌ rejected |
| 0 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.2439 | 0.83 | ✅ accepted |

**Proposal policy**: task_score is 0.80 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.131) — your mutation base

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

- **Composite score**: 0.131
- **task_score** (E): 0.804
- **fitness_score**: 0.721  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2539 |
| approach_1 | 1.00 | 1.00 | 0.0169 |
| contact_1 | 0.67 | 1.00 | 0.0243 |
| push_1 | 0.33 | 1.00 | 0.0613 |
| retract_1 | 0.33 | 1.00 | 0.1766 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.127, 0.058) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.333 | 72.154 | 73.149 |
| approach_1 | approach | 1.00 / step_budget | (0.496, 0.127, 0.058)→(0.496, 0.123, 0.042) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.538 | 177.249 |
| contact_1 | contact | 0.67 / step_budget | (0.496, 0.123, 0.042)→(0.496, 0.102, 0.030) | (0.500, 0.080, 0.034)→(0.502, 0.073, 0.035) | 0.161→0.153 | 1.00 / 2.000 | 2.047 | 4.901 |
| push_1 | push | 0.33 / guard_failure | (0.496, 0.007, 0.029)→(0.497, -0.054, 0.029) | (0.502, 0.073, 0.035)→(0.507, -0.082, 0.035) | 0.153→0.010 | 1.00 / 2.333 | 14.897 | 42.194 |
| retract_1 | retract | 0.33 / step_budget | (0.497, -0.054, 0.029)→(0.494, -0.008, 0.192) | (0.507, -0.082, 0.035)→(0.501, -0.077, 0.034) | 0.010→0.009 | 1.00 / 1.000 | 0.558 | 181.592 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.639
- phase_breakdown.approach_score: 0.904
- phase_breakdown.push_score: 0.497
- phase_breakdown.contact_score: 0.802

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.784
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.155
- **K-run variance**: 0.0040
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.307


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5027,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.alignment_speed":0.1999,"align_1.lateral_offset_x":-0.00215,"approach_1.approach_height":0.13378,"approach_1.approach_speed":0.04433,"contact_1.contact_force_threshold":9.91846,"contact_1.contact_speed":0.03361,"push_1.push_distance":0.19896,"push_1.push_speed":0.03271,"retract_1.retract_height":0.09148,"retract_1.retract_speed":0.12909},"optimized_scores":{"best_composite_score":0.15491,"best_fitness_score":0.74491,"best_task_score":0.8466},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":258.0,"contact_point_centroid":[0.50019,-0.07219,0.05863],"force_p95":99.11026,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.01791,"mean_force":66.97352,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49424,-0.06304,0.05443]},{"body_a":"peg","body_b":"channel_base_body","contact_count":278.0,"contact_point_centroid":[0.5081,-0.10192,0.06026],"force_p95":97.38294,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":101.70694,"mean_force":62.26685,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49429,-0.06371,0.05724]},{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.50649,-0.10119,0.03479],"force_p95":35.61225,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.60746,"mean_force":24.61065,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49902,-0.05592,0.02847]},{"body_a":"attachment","body_b":"peg","contact_count":651.0,"contact_point_centroid":[0.50288,-0.00454,0.04024],"force_p95":24.02847,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.82708,"mean_force":4.58981,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49772,0.00675,0.02734]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":242.0,"contact_point_centroid":[0.52524,-0.07973,0.04859],"force_p95":34.01909,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.26662,"mean_force":11.30242,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49463,-0.06577,0.09857]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":15.0,"contact_point_centroid":[0.53406,0.06156,0.06],"force_p95":34.00179,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.46206,"mean_force":25.39842,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49663,0.05711,0.02629]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47497,-0.07669,0.04585],"force_p95":18.96707,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.11165,"mean_force":14.64854,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49349,-0.0672,0.07924]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":545.0,"contact_point_centroid":[0.5251,-0.01748,0.02872],"force_p95":3.44022,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.27827,"mean_force":0.97637,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49754,0.01108,0.02717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":509.0,"contact_point_centroid":[0.50634,-0.03464,0.00992],"force_p95":7.98504,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.02838,"mean_force":3.44843,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49773,0.00861,0.02737]},{"body_a":"peg","body_b":"channel_base_body","contact_count":415.0,"contact_point_centroid":[0.50374,0.05174,0.00963],"force_p95":3.80732,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.07429,"mean_force":1.59435,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49923,0.09277,0.03387]},{"body_a":"attachment","body_b":"peg","contact_count":192.0,"contact_point_centroid":[0.50255,0.07551,0.04298],"force_p95":3.84373,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.79079,"mean_force":2.46889,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4993,0.08739,0.03142]},{"body_a":"peg","body_b":"channel_base_body","contact_count":686.0,"contact_point_centroid":[0.50515,-0.07247,0.00943],"force_p95":0.71564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.70648,"mean_force":0.58529,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49665,-0.0182,0.17774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":428.0,"contact_point_centroid":[0.50358,0.0616,0.00933],"force_p95":0.60173,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56544,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5021,0.1528,0.17288]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49997,0.19867,0.29693]},{"body_a":"peg","body_b":"channel_base_body","contact_count":53.0,"contact_point_centroid":[0.50347,0.06175,0.00938],"force_p95":0.60158,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60369,"mean_force":0.54612,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50299,0.10745,0.05016]}],"total_contact_groups":15},"final_pose_error":0.03313,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50684,-0.07387,0.03376],"final_tcp_position":[0.49743,0.06763,0.20661],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":102.01791,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":451.0,"n_steps_budget":870.0,"object_pos_end":[0.50378,0.06156,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14175,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.56088,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":447.0,"raw_peak_contact_force":2.17216,"tcp_end":[0.505,0.10932,0.05755],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":53.0,"n_steps_budget":600.0,"object_pos_end":[0.50374,0.0616,0.03377],"object_pos_start":[0.50378,0.06156,0.03378],"object_to_goal_dist_end":0.14179,"object_to_goal_dist_start":0.14175,"object_z_max":0.03378,"peak_contact_force":0.52868,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":53.0,"raw_peak_contact_force":0.60369,"subtask_id":"approach","tcp_end":[0.50172,0.10545,0.04262],"tcp_start":[0.505,0.10932,0.05755],"tcp_to_object_dist_end":0.04478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":424.0,"n_steps_budget":600.0,"object_pos_end":[0.50506,0.05384,0.0353],"object_pos_start":[0.50374,0.0616,0.03377],"object_to_goal_dist_end":0.13401,"object_to_goal_dist_start":0.14179,"object_z_max":0.03532,"peak_contact_force":1.623,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":607.0,"raw_peak_contact_force":6.07429,"subtask_id":"contact","tcp_end":[0.49963,0.08344,0.02994],"tcp_start":[0.50172,0.10545,0.04262],"tcp_to_object_dist_end":0.03057,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":900.0,"n_steps_budget":1000.0,"object_pos_end":[0.50681,-0.08652,0.03513],"object_pos_start":[0.50506,0.05384,0.0353],"object_to_goal_dist_end":0.01062,"object_to_goal_dist_start":0.13401,"object_z_max":0.03595,"peak_contact_force":29.57697,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1777.0,"raw_peak_contact_force":42.60746,"subtask_id":"push","tcp_end":[0.49907,-0.05837,0.02841],"tcp_start":[0.49908,-0.05833,0.02843],"tcp_to_object_dist_end":0.02997,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50684,-0.07387,0.03376],"object_pos_start":[0.50683,-0.08656,0.03514],"object_to_goal_dist_end":0.0111,"object_to_goal_dist_start":0.01064,"object_z_max":0.06594,"peak_contact_force":0.58244,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1480.0,"raw_peak_contact_force":102.01791,"tcp_end":[0.49743,0.06763,0.20661],"tcp_start":[0.49907,-0.05837,0.02841],"tcp_to_object_dist_end":0.22358,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.58192,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.alignment_speed":0.11422,"align_1.lateral_offset_x":0.00114,"approach_1.approach_height":0.18814,"approach_1.approach_speed":0.04941,"contact_1.contact_force_threshold":12.12263,"contact_1.contact_speed":0.02593,"push_1.push_distance":0.1864,"push_1.push_speed":0.07646,"retract_1.retract_height":0.11068,"retract_1.retract_speed":0.06606},"optimized_scores":{"best_composite_score":0.1936,"best_fitness_score":0.7836,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":362.0,"contact_point_centroid":[0.49836,-0.07051,0.05422],"force_p95":94.3622,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":96.01946,"mean_force":57.365,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49167,-0.06207,0.0518]},{"body_a":"peg","body_b":"channel_base_body","contact_count":366.0,"contact_point_centroid":[0.50744,-0.1013,0.05861],"force_p95":81.15512,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.88765,"mean_force":51.09254,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49137,-0.06435,0.05622]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":259.0,"contact_point_centroid":[0.52562,-0.0852,0.05984],"force_p95":58.86361,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.1221,"mean_force":36.30543,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4904,-0.06546,0.05887]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":22.0,"contact_point_centroid":[0.53114,0.11248,0.06],"force_p95":36.07826,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":37.68077,"mean_force":29.12335,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49376,0.10819,0.02633]},{"body_a":"attachment","body_b":"peg","contact_count":745.0,"contact_point_centroid":[0.50164,0.03655,0.04119],"force_p95":10.67377,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.45276,"mean_force":2.92676,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49541,0.04746,0.02773]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":688.0,"contact_point_centroid":[0.52512,0.01177,0.02893],"force_p95":5.71427,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.79813,"mean_force":1.55663,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49549,0.03953,0.02778]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":25.0,"contact_point_centroid":[0.47487,-0.07873,0.03216],"force_p95":15.87446,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.18591,"mean_force":11.26011,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4898,-0.07141,0.07553]},{"body_a":"peg","body_b":"channel_base_body","contact_count":518.0,"contact_point_centroid":[0.5054,-0.00226,0.00991],"force_p95":9.60106,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.11706,"mean_force":3.64713,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49562,0.04002,0.02792]},{"body_a":"peg","body_b":"channel_base_body","contact_count":665.0,"contact_point_centroid":[0.5012,-0.0818,0.00943],"force_p95":1.2324,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.88548,"mean_force":0.62828,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4942,-0.07419,0.12406]},{"body_a":"peg","body_b":"channel_base_body","contact_count":391.0,"contact_point_centroid":[0.50176,0.10351,0.00972],"force_p95":3.34093,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.36664,"mean_force":1.71888,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49564,0.1453,0.03394]},{"body_a":"attachment","body_b":"peg","contact_count":225.0,"contact_point_centroid":[0.49949,0.12958,0.04411],"force_p95":3.24746,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.0789,"mean_force":2.23951,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49593,0.14142,0.03178]},{"body_a":"peg","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52261,0.09847,0.0619],"force_p95":2.03749,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.19369,"mean_force":1.07038,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49352,0.11667,0.02619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":441.0,"contact_point_centroid":[0.50091,0.11604,0.00937],"force_p95":0.63181,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56154,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49888,0.17894,0.17657]},{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.50064,0.11577,0.00944],"force_p95":0.58672,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64323,"mean_force":0.54195,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49742,0.15807,0.05124]}],"total_contact_groups":14},"final_pose_error":0.15986,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50122,-0.08117,0.03379],"final_tcp_position":[0.49477,-0.05854,0.1801],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":96.01946,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":457.0,"n_steps_budget":1000.0,"object_pos_end":[0.50097,0.116,0.03393],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.1961,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54506,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":441.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49887,0.15915,0.05947],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05018,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":57.0,"n_steps_budget":600.0,"object_pos_end":[0.50093,0.11609,0.03388],"object_pos_start":[0.50097,0.116,0.03393],"object_to_goal_dist_end":0.19618,"object_to_goal_dist_start":0.1961,"object_z_max":0.03393,"peak_contact_force":0.53818,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":57.0,"raw_peak_contact_force":0.64323,"subtask_id":"approach","tcp_end":[0.49709,0.15711,0.04306],"tcp_start":[0.49887,0.15915,0.05947],"tcp_to_object_dist_end":0.04221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":401.0,"n_steps_budget":600.0,"object_pos_end":[0.50262,0.10771,0.03526],"object_pos_start":[0.50093,0.11609,0.03388],"object_to_goal_dist_end":0.18779,"object_to_goal_dist_start":0.19618,"object_z_max":0.03533,"peak_contact_force":2.37401,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":616.0,"raw_peak_contact_force":4.36664,"subtask_id":"contact","tcp_end":[0.49669,0.13719,0.02991],"tcp_start":[0.49709,0.15711,0.04306],"tcp_to_object_dist_end":0.03054,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50689,-0.07523,0.0351],"object_pos_start":[0.50262,0.10771,0.03526],"object_to_goal_dist_end":0.00971,"object_to_goal_dist_start":0.18779,"object_z_max":0.03646,"peak_contact_force":1.43977,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1976.0,"raw_peak_contact_force":37.68077,"subtask_id":"push","tcp_end":[0.49777,-0.04662,0.02977],"tcp_start":[0.49669,0.13719,0.02991],"tcp_to_object_dist_end":0.03051,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50122,-0.08117,0.03379],"object_pos_start":[0.50689,-0.07523,0.0351],"object_to_goal_dist_end":0.00643,"object_to_goal_dist_start":0.00971,"object_z_max":0.04772,"peak_contact_force":0.54819,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1677.0,"raw_peak_contact_force":96.01946,"tcp_end":[0.49477,-0.05854,0.1801],"tcp_start":[0.49777,-0.04662,0.02977],"tcp_to_object_dist_end":0.14819,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33511,"average_solve_count":188.0,"average_success_count":188.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.alignment_speed":0.14989,"align_1.lateral_offset_x":0.00428,"approach_1.approach_height":0.12204,"approach_1.approach_speed":0.1102,"contact_1.contact_force_threshold":10.23696,"contact_1.contact_speed":0.04368,"push_1.push_distance":0.12976,"push_1.push_speed":0.04322,"retract_1.retract_height":0.13949,"retract_1.retract_speed":0.07955},"optimized_scores":{"best_composite_score":0.04378,"best_fitness_score":0.63378,"best_task_score":0.564},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":147.0,"contact_point_centroid":[0.47497,0.10561,0.05981],"force_p95":431.28333,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":530.4993,"mean_force":392.89674,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48507,0.1107,0.05805]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":146.0,"contact_point_centroid":[0.47494,-0.0661,0.05388],"force_p95":315.71866,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":346.73926,"mean_force":230.5546,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48671,-0.06625,0.05195]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47497,0.1035,0.05978],"force_p95":215.35515,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":215.35515,"mean_force":215.35515,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48365,0.11163,0.05844]},{"body_a":"attachment","body_b":"peg","contact_count":365.0,"contact_point_centroid":[0.49615,-0.07236,0.05704],"force_p95":79.72297,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.40048,"mean_force":54.38467,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48735,-0.06496,0.04981]},{"body_a":"peg","body_b":"channel_base_body","contact_count":378.0,"contact_point_centroid":[0.50795,-0.10116,0.05878],"force_p95":67.78077,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.35481,"mean_force":42.31891,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48731,-0.0653,0.05095]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":340.0,"contact_point_centroid":[0.52549,-0.08439,0.05926],"force_p95":58.75224,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.6379,"mean_force":32.18935,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48688,-0.06627,0.05363]},{"body_a":"attachment","body_b":"peg","contact_count":834.0,"contact_point_centroid":[0.49839,0.00362,0.044],"force_p95":21.13251,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.29349,"mean_force":9.4951,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48981,0.01357,0.02819]},{"body_a":"peg","body_b":"channel_base_body","contact_count":39.0,"contact_point_centroid":[0.50731,-0.10038,0.06025],"force_p95":35.28607,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.54799,"mean_force":25.64351,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49291,-0.05639,0.03013]},{"body_a":"peg","body_b":"channel_base_body","contact_count":633.0,"contact_point_centroid":[0.50683,-0.01761,0.00991],"force_p95":14.72248,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.32239,"mean_force":7.45085,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48944,0.02319,0.02796]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":773.0,"contact_point_centroid":[0.5252,-0.01381,0.0424],"force_p95":14.8606,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.89241,"mean_force":6.56682,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48978,0.0116,0.02813]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":64.0,"contact_point_centroid":[0.47467,-0.07587,0.03935],"force_p95":15.24686,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.33711,"mean_force":7.6804,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48622,-0.07446,0.08279]},{"body_a":"peg","body_b":"link7","contact_count":277.0,"contact_point_centroid":[0.52154,0.03254,0.06228],"force_p95":9.1164,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.0408,"mean_force":6.86727,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48806,0.04734,0.02704]},{"body_a":"peg","body_b":"channel_base_body","contact_count":613.0,"contact_point_centroid":[0.49552,-0.07567,0.00937],"force_p95":0.89966,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.33652,"mean_force":0.61438,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48949,-0.06455,0.14177]},{"body_a":"peg","body_b":"channel_base_body","contact_count":419.0,"contact_point_centroid":[0.49633,0.05384,0.00964],"force_p95":3.11463,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.26317,"mean_force":1.43056,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48841,0.09432,0.03357]},{"body_a":"attachment","body_b":"peg","contact_count":197.0,"contact_point_centroid":[0.49354,0.07757,0.04508],"force_p95":2.92914,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.94716,"mean_force":2.07236,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48937,0.08937,0.03147]},{"body_a":"peg","body_b":"channel_base_body","contact_count":443.0,"contact_point_centroid":[0.49552,0.06402,0.00936],"force_p95":0.59691,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.5647,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49098,0.15372,0.17261]}],"total_contact_groups":18},"final_pose_error":0.13525,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49462,-0.07549,0.03397],"final_tcp_position":[0.49119,-0.03451,0.18898],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":530.4993,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":470.0,"n_steps_budget":1000.0,"object_pos_end":[0.4949,0.06388,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14409,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":215.35515,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":472.0,"raw_peak_contact_force":215.35515,"tcp_end":[0.48364,0.11148,0.05804],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":208.0,"n_steps_budget":600.0,"object_pos_end":[0.49487,0.06381,0.03396],"object_pos_start":[0.4949,0.06388,0.03394],"object_to_goal_dist_end":0.14403,"object_to_goal_dist_start":0.14409,"object_z_max":0.03396,"peak_contact_force":0.54597,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":355.0,"raw_peak_contact_force":530.4993,"subtask_id":"approach","tcp_end":[0.4888,0.10615,0.04138],"tcp_start":[0.48364,0.11148,0.05804],"tcp_to_object_dist_end":0.04341,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":431.0,"n_steps_budget":600.0,"object_pos_end":[0.49772,0.05607,0.03547],"object_pos_start":[0.49487,0.06381,0.03396],"object_to_goal_dist_end":0.13617,"object_to_goal_dist_start":0.14403,"object_z_max":0.0355,"peak_contact_force":2.14428,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":616.0,"raw_peak_contact_force":4.26317,"subtask_id":"contact","tcp_end":[0.49047,0.0854,0.03013],"tcp_start":[0.4888,0.10615,0.04138],"tcp_to_object_dist_end":0.03068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":992.0,"n_steps_budget":1000.0,"object_pos_end":[0.50738,-0.08315,0.03539],"object_pos_start":[0.49772,0.05607,0.03547],"object_to_goal_dist_end":0.00925,"object_to_goal_dist_start":0.13617,"object_z_max":0.037,"peak_contact_force":13.6752,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2556.0,"raw_peak_contact_force":46.29349,"subtask_id":"push","tcp_end":[0.49283,-0.05751,0.02995],"tcp_start":[0.49285,-0.05749,0.02998],"tcp_to_object_dist_end":0.02998,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49462,-0.07549,0.03397],"object_pos_start":[0.50739,-0.08318,0.03537],"object_to_goal_dist_end":0.00926,"object_to_goal_dist_start":0.00929,"object_z_max":0.04962,"peak_contact_force":0.54406,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1906.0,"raw_peak_contact_force":346.73926,"tcp_end":[0.49119,-0.03451,0.18898],"tcp_start":[0.49283,-0.05751,0.02995],"tcp_to_object_dist_end":0.16037,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```