## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.0697 | 0.63 | ✅ accepted |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.0676 | 0.62 | ✅ accepted |

**Proposal policy**: task_score is 0.63 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, 0.1046352631789195, 0.04]
- Frozen task target: [0.5244002338996304, -0.05536473682108051, 0.04]
- Goal object position: (0.5244002338996304, -0.05536473682108051, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, 0.1046352631789195, 0.04)
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, 0.1046352631789195, 0.04]}
  frozen_targets: {'channel_exit': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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

## Current Skill (Q=0.070) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
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
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: retract_1
  type: retract
  generator: linear_cartesian
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

- **Composite score**: 0.070
- **task_score** (E): 0.628
- **fitness_score**: 0.510  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2604 |
| approach_1 | 1.00 | 1.00 | 0.0072 |
| contact_1 | 1.00 | 1.00 | 0.0140 |
| push_1 | 1.00 | 1.00 | 0.1194 |
| retract_1 | 0.00 | 1.00 | 0.0959 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.137, 0.048) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.557 | 2.488 |
| approach_1 | approach | 1.00 / step_budget | (0.508, 0.137, 0.048)→(0.505, 0.136, 0.042) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.541 | 0.573 |
| contact_1 | contact | 1.00 / step_budget | (0.505, 0.136, 0.042)→(0.502, 0.125, 0.035) | (0.504, 0.095, 0.034)→(0.504, 0.094, 0.034) | 0.175→0.174 | 1.00 / 2.333 | 101.842 | 120.238 |
| push_1 | push | 1.00 / step_budget | (0.502, 0.125, 0.035)→(0.498, 0.006, 0.037) | (0.504, 0.094, 0.034)→(0.506, -0.024, 0.037) | 0.174→0.057 | 1.00 / 2.000 | 37.949 | 134.795 |
| retract_1 | retract | 0.00 / step_budget | (0.498, 0.006, 0.037)→(0.495, 0.003, 0.133) | (0.506, -0.024, 0.037)→(0.506, -0.024, 0.034) | 0.057→0.057 | 1.00 / 1.000 | 0.545 | 91.822 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.737
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.737
- phase_score: 0.518
- phase_breakdown.push_score: 0.312
- phase_breakdown.contact_score: 0.765
- phase_breakdown.approach_score: 0.891

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.606
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.750
- **Median Q (composite search score)**: 0.099
- **K-run variance**: 0.0086
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.319


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26316,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.18943,"approach_1.speed":0.03603,"contact_1.speed":0.03696,"push_1.push_depth":0.09876,"push_1.push_distance":0.15907,"retract_1.retract_height":0.15757,"retract_1.speed":0.03201},"optimized_scores":{"best_composite_score":-0.05573,"best_fitness_score":0.38427,"best_task_score":0.39641},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":497.0,"contact_point_centroid":[0.5464,0.08248,0.05999],"force_p95":147.41337,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":173.19636,"mean_force":87.60893,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50121,0.08498,0.03603]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":188.0,"contact_point_centroid":[0.52502,0.10732,0.05999],"force_p95":138.65945,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.51397,"mean_force":83.8755,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50164,0.10932,0.03569]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.54323,0.01203,0.05999],"force_p95":94.30898,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.46075,"mean_force":57.09537,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49828,0.01554,0.03706]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":242.0,"contact_point_centroid":[0.55418,0.12,0.05996],"force_p95":74.57379,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.03762,"mean_force":52.73076,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50603,0.13524,0.03395]},{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.49913,0.0422,0.00968],"force_p95":15.35373,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.68658,"mean_force":2.27888,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50116,0.08298,0.03607]},{"body_a":"attachment","body_b":"peg","contact_count":293.0,"contact_point_centroid":[0.50243,0.06653,0.0399],"force_p95":18.88325,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.59463,"mean_force":3.48744,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50097,0.07813,0.03613]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":80.0,"contact_point_centroid":[0.47472,0.05713,0.03462],"force_p95":2.416,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.72991,"mean_force":0.89407,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50092,0.08852,0.03628]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":128.0,"contact_point_centroid":[0.52509,0.0285,0.02219],"force_p95":1.3241,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.5022,"mean_force":0.52941,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50057,0.05795,0.03641]},{"body_a":"peg","body_b":"channel_base_body","contact_count":769.0,"contact_point_centroid":[0.50575,0.10463,0.00938],"force_p95":0.57576,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56104,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50896,0.17221,0.16946]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.50571,0.12221,0.03445],"force_p95":1.5068,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.56416,"mean_force":0.43078,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50553,0.13418,0.03406]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49979,0.19895,0.29625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":327.0,"contact_point_centroid":[0.50592,0.10359,0.00941],"force_p95":0.72453,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92473,"mean_force":0.57813,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50683,0.13667,0.03459]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":155.0,"contact_point_centroid":[0.52504,-0.01407,0.04926],"force_p95":1.49447,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71819,"mean_force":0.2682,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49554,0.01277,0.07812]},{"body_a":"attachment","body_b":"peg","contact_count":132.0,"contact_point_centroid":[0.50345,0.00294,0.05968],"force_p95":1.48319,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.67667,"mean_force":0.3843,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49509,0.01454,0.04815]},{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50663,-0.01744,0.00951],"force_p95":0.55601,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.93913,"mean_force":0.51879,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49506,0.0124,0.08447]},{"body_a":"peg","body_b":"channel_base_body","contact_count":34.0,"contact_point_centroid":[0.50415,0.10564,0.00939],"force_p95":0.57572,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57583,"mean_force":0.54683,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51648,0.14571,0.04478]}],"total_contact_groups":16},"final_pose_error":0.16821,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50687,-0.01404,0.03382],"final_tcp_position":[0.49554,0.00959,0.13212],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":173.19636,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":796.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55165,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":801.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51917,0.14645,0.04815],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":34.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":0.54964,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34.0,"raw_peak_contact_force":0.57583,"tcp_end":[0.51288,0.14511,0.04069],"tcp_start":[0.51917,0.14645,0.04815],"tcp_to_object_dist_end":0.04158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":327.0,"n_steps_budget":600.0,"object_pos_end":[0.50583,0.10365,0.03433],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.18383,"object_to_goal_dist_start":0.18488,"object_z_max":0.03438,"peak_contact_force":74.62586,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":611.0,"raw_peak_contact_force":75.03762,"tcp_end":[0.50534,0.13372,0.0341],"tcp_start":[0.51288,0.14511,0.04069],"tcp_to_object_dist_end":0.03007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.50647,-0.01345,0.036],"object_pos_start":[0.50583,0.10365,0.03433],"object_to_goal_dist_end":0.06698,"object_to_goal_dist_start":0.18383,"object_z_max":0.03937,"peak_contact_force":57.27204,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1728.0,"raw_peak_contact_force":173.19636,"tcp_end":[0.49829,0.01569,0.03705],"tcp_start":[0.50534,0.13372,0.0341],"tcp_to_object_dist_end":0.03028,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50687,-0.01404,0.03382],"object_pos_start":[0.50647,-0.01345,0.036],"object_to_goal_dist_end":0.06661,"object_to_goal_dist_start":0.06698,"object_z_max":0.036,"peak_contact_force":0.54603,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1288.0,"raw_peak_contact_force":102.46075,"tcp_end":[0.49554,0.00959,0.13212],"tcp_start":[0.49829,0.01569,0.03705],"tcp_to_object_dist_end":0.10174,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14205,"average_solve_count":176.0,"average_success_count":176.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.27457,"approach_1.speed":0.04941,"contact_1.speed":0.01811,"push_1.push_depth":0.1,"push_1.push_distance":0.06961,"retract_1.retract_height":0.17707,"retract_1.speed":0.05046},"optimized_scores":{"best_composite_score":0.1658,"best_fitness_score":0.6058,"best_task_score":0.73703},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":529.0,"contact_point_centroid":[0.54279,0.10373,0.05997],"force_p95":162.91112,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":170.42513,"mean_force":113.86992,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49811,0.10268,0.03629]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":500.0,"contact_point_centroid":[0.54432,0.04469,0.05999],"force_p95":101.20999,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":113.21131,"mean_force":82.7075,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49952,0.04655,0.03667]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54274,-0.02756,0.05999],"force_p95":72.40682,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.04278,"mean_force":54.07587,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49809,-0.02198,0.03692]},{"body_a":"attachment","body_b":"peg","contact_count":367.0,"contact_point_centroid":[0.50376,0.01975,0.04238],"force_p95":24.71091,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.60425,"mean_force":5.27072,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49926,0.0314,0.03679]},{"body_a":"peg","body_b":"channel_base_body","contact_count":536.0,"contact_point_centroid":[0.50424,0.00272,0.00971],"force_p95":20.93237,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":35.13639,"mean_force":3.97229,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49951,0.04548,0.03669]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":251.0,"contact_point_centroid":[0.52517,0.00761,0.02976],"force_p95":4.67719,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.80111,"mean_force":0.88069,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4994,0.03697,0.03679]},{"body_a":"peg","body_b":"channel_base_body","contact_count":805.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.5533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55733,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49866,0.1548,0.17095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50618,-0.05214,0.00945],"force_p95":0.5519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.06474,"mean_force":0.53654,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49491,-0.01754,0.08445]},{"body_a":"peg","body_b":"channel_base_body","contact_count":606.0,"contact_point_centroid":[0.50298,0.06744,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55077,"mean_force":0.54664,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49795,0.10318,0.03658]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50306,0.0668,0.00938],"force_p95":0.55034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55059,"mean_force":0.54668,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49835,0.11061,0.04566]},{"body_a":"attachment","body_b":"peg","contact_count":61.0,"contact_point_centroid":[0.50465,-0.03336,0.05797],"force_p95":0.34865,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48589,"mean_force":0.22339,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49565,-0.02143,0.04207]}],"total_contact_groups":11},"final_pose_error":0.16809,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50636,-0.05046,0.03394],"final_tcp_position":[0.49546,-0.01351,0.13252],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":170.42513,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5478,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":805.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.499,0.11132,0.04824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":28.0,"n_steps_budget":600.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54714,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28.0,"raw_peak_contact_force":0.55059,"tcp_end":[0.4983,0.10987,0.04224],"tcp_start":[0.499,0.11132,0.04824],"tcp_to_object_dist_end":0.04353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":606.0,"n_steps_budget":840.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":161.19811,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1135.0,"raw_peak_contact_force":170.42513,"tcp_end":[0.50084,0.10009,0.03609],"tcp_start":[0.4983,0.10987,0.04224],"tcp_to_object_dist_end":0.03274,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.50633,-0.05148,0.03602],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.02948,"object_to_goal_dist_start":0.14766,"object_z_max":0.03725,"peak_contact_force":1.44071,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1654.0,"raw_peak_contact_force":113.21131,"tcp_end":[0.4981,-0.02186,0.03692],"tcp_start":[0.50084,0.10009,0.03609],"tcp_to_object_dist_end":0.03076,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50636,-0.05046,0.03394],"object_pos_start":[0.50633,-0.05148,0.03602],"object_to_goal_dist_end":0.03082,"object_to_goal_dist_start":0.02948,"object_z_max":0.03602,"peak_contact_force":0.54698,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1064.0,"raw_peak_contact_force":75.04278,"tcp_end":[0.49546,-0.01351,0.13252],"tcp_start":[0.4981,-0.02186,0.03692],"tcp_to_object_dist_end":0.10584,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2378,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.0994,"approach_1.speed":0.07328,"contact_1.speed":0.02645,"push_1.push_depth":0.09877,"push_1.push_distance":0.12212,"retract_1.retract_height":0.17474,"retract_1.speed":0.05112},"optimized_scores":{"best_composite_score":0.0991,"best_fitness_score":0.5391,"best_task_score":0.74962},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":509.0,"contact_point_centroid":[0.54484,0.08564,0.05999],"force_p95":109.13912,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":117.97701,"mean_force":86.84203,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49927,0.089,0.03611]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":248.0,"contact_point_centroid":[0.55044,0.12,0.05998],"force_p95":113.1182,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.2511,"mean_force":73.57048,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50008,0.14156,0.03415]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54299,0.01995,0.05999],"force_p95":92.7783,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.96177,"mean_force":58.87716,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49802,0.02304,0.03708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":536.0,"contact_point_centroid":[0.50014,0.04918,0.00961],"force_p95":8.64764,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.72819,"mean_force":2.02967,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49928,0.08864,0.03613]},{"body_a":"attachment","body_b":"peg","contact_count":270.0,"contact_point_centroid":[0.5017,0.07451,0.04042],"force_p95":15.50728,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.59467,"mean_force":3.18693,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49919,0.08617,0.03609]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":163.0,"contact_point_centroid":[0.52532,0.03052,0.03445],"force_p95":4.27897,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.41431,"mean_force":0.82519,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49874,0.06001,0.03652]},{"body_a":"peg","body_b":"channel_base_body","contact_count":377.0,"contact_point_centroid":[0.5035,0.11005,0.00945],"force_p95":0.79772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.07069,"mean_force":0.59677,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50034,0.14326,0.03529]},{"body_a":"attachment","body_b":"peg","contact_count":77.0,"contact_point_centroid":[0.5035,0.1295,0.04143],"force_p95":1.81834,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.6809,"mean_force":0.38688,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50019,0.14146,0.03414]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":49.0,"contact_point_centroid":[0.47481,0.05527,0.0445],"force_p95":1.7113,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.60549,"mean_force":0.38123,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49943,0.0855,0.03645]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.50359,0.11169,0.00938],"force_p95":0.60779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55452,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50201,0.17585,0.17071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":992.0,"contact_point_centroid":[0.50527,-0.00821,0.00938],"force_p95":0.55887,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62262,"mean_force":0.55171,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49483,0.01826,0.08524]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.50512,0.11115,0.00939],"force_p95":0.58591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5936,"mean_force":0.54414,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50458,0.15277,0.04656]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49976,0.19944,0.29874]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52509,-0.00508,0.01346],"force_p95":0.31741,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31792,"mean_force":0.31279,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49802,0.02309,0.03708]},{"body_a":"attachment","body_b":"peg","contact_count":51.0,"contact_point_centroid":[0.50349,0.01015,0.05869],"force_p95":0.14633,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.17896,"mean_force":0.02941,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49517,0.02183,0.04461]}],"total_contact_groups":15},"final_pose_error":0.16759,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50535,-0.00816,0.03391],"final_tcp_position":[0.4954,0.0141,0.13307],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":117.97701,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11173,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57116,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":772.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50559,0.15326,0.04883],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":24.0,"n_steps_budget":600.0,"object_pos_end":[0.50368,0.11176,0.0338],"object_pos_start":[0.50367,0.11173,0.03382],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19187,"object_z_max":0.03382,"peak_contact_force":0.52478,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":0.5936,"tcp_end":[0.50369,0.1524,0.04354],"tcp_start":[0.50559,0.15326,0.04883],"tcp_to_object_dist_end":0.04179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":377.0,"n_steps_budget":600.0,"object_pos_end":[0.50366,0.11114,0.03407],"object_pos_start":[0.50368,0.11176,0.0338],"object_to_goal_dist_end":0.19127,"object_to_goal_dist_start":0.1919,"object_z_max":0.03433,"peak_contact_force":69.70274,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":702.0,"raw_peak_contact_force":115.2511,"tcp_end":[0.50059,0.14112,0.03413],"tcp_start":[0.50369,0.1524,0.04354],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.50607,-0.00644,0.03759],"object_pos_start":[0.50366,0.11114,0.03407],"object_to_goal_dist_end":0.07385,"object_to_goal_dist_start":0.19127,"object_z_max":0.0378,"peak_contact_force":55.13389,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1527.0,"raw_peak_contact_force":117.97701,"tcp_end":[0.49802,0.02314,0.03708],"tcp_start":[0.50059,0.14112,0.03413],"tcp_to_object_dist_end":0.03067,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50535,-0.00816,0.03391],"object_pos_start":[0.50607,-0.00644,0.03759],"object_to_goal_dist_end":0.07229,"object_to_goal_dist_start":0.07385,"object_z_max":0.03759,"peak_contact_force":0.54141,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1048.0,"raw_peak_contact_force":97.96177,"tcp_end":[0.4954,0.0141,0.13307],"tcp_start":[0.49802,0.02314,0.03708],"tcp_to_object_dist_end":0.10211,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```