## Search State

- **Seed**: 5
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.0695 | 0.63 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 7 | 0.0561 | 0.61 | ❌ rejected |
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
- **task_score** (E): 0.626
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
| push_1 | 1.00 | 0.67 | 0.1201 |
| retract_1 | 0.00 | 1.00 | 0.0957 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.137, 0.048) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.557 | 2.488 |
| approach_1 | approach | 1.00 / step_budget | (0.508, 0.137, 0.048)→(0.505, 0.136, 0.042) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.541 | 0.573 |
| contact_1 | contact | 1.00 / step_budget | (0.505, 0.136, 0.042)→(0.502, 0.125, 0.035) | (0.504, 0.095, 0.034)→(0.504, 0.094, 0.034) | 0.175→0.174 | 1.00 / 2.333 | 93.971 | 124.167 |
| push_1 | push | 1.00 / step_budget | (0.502, 0.125, 0.035)→(0.498, 0.005, 0.037) | (0.504, 0.094, 0.034)→(0.506, -0.024, 0.037) | 0.174→0.056 | 0.67 / 0.667 | 1.022 | 138.362 |
| retract_1 | retract | 0.00 / step_budget | (0.498, 0.005, 0.037)→(0.495, 0.003, 0.132) | (0.506, -0.024, 0.037)→(0.506, -0.024, 0.034) | 0.056→0.057 | 1.00 / 1.000 | 0.553 | 67.378 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.739
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.739
- phase_score: 0.518
- phase_breakdown.push_score: 0.311
- phase_breakdown.contact_score: 0.765
- phase_breakdown.approach_score: 0.891

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.606
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.741
- **Median Q (composite search score)**: 0.096
- **K-run variance**: 0.0085
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.422


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26744,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.22351,"approach_1.speed":0.0423,"contact_1.speed":0.0454,"push_1.push_depth":0.09999,"push_1.push_distance":0.06273,"retract_1.retract_height":0.19013,"retract_1.speed":0.04352},"optimized_scores":{"best_composite_score":-0.05412,"best_fitness_score":0.38588,"best_task_score":0.39678},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":515.0,"contact_point_centroid":[0.54627,0.0803,0.05998],"force_p95":140.32129,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":179.38433,"mean_force":88.86083,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50111,0.08273,0.03607]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":194.0,"contact_point_centroid":[0.52501,0.10741,0.06],"force_p95":130.12045,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":156.69233,"mean_force":80.03556,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50156,0.10929,0.03568]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":242.0,"contact_point_centroid":[0.55418,0.12,0.05996],"force_p95":74.57379,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":75.03762,"mean_force":52.73076,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50603,0.13524,0.03395]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54324,0.01059,0.05999],"force_p95":49.66883,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":50.02883,"mean_force":43.50163,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4983,0.01417,0.03707]},{"body_a":"peg","body_b":"channel_base_body","contact_count":570.0,"contact_point_centroid":[0.50301,0.04077,0.00961],"force_p95":10.26071,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.40461,"mean_force":1.98724,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50112,0.08211,0.03608]},{"body_a":"attachment","body_b":"peg","contact_count":244.0,"contact_point_centroid":[0.5041,0.06972,0.03978],"force_p95":17.09899,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.90285,"mean_force":3.58404,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50106,0.0814,0.03607]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":255.0,"contact_point_centroid":[0.52521,0.05517,0.03608],"force_p95":3.04022,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.87312,"mean_force":0.65433,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50113,0.08607,0.03604]},{"body_a":"peg","body_b":"channel_base_body","contact_count":769.0,"contact_point_centroid":[0.50575,0.10463,0.00938],"force_p95":0.57576,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56104,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50896,0.17221,0.16946]},{"body_a":"attachment","body_b":"peg","contact_count":42.0,"contact_point_centroid":[0.50571,0.12221,0.03445],"force_p95":1.5068,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.56416,"mean_force":0.43078,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50553,0.13418,0.03406]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49979,0.19895,0.29625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":327.0,"contact_point_centroid":[0.50592,0.10359,0.00941],"force_p95":0.72453,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92473,"mean_force":0.57813,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50683,0.13667,0.03459]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":78.0,"contact_point_centroid":[0.52501,-0.0156,0.06],"force_p95":1.60358,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.77007,"mean_force":0.57997,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49479,0.01302,0.05308]},{"body_a":"attachment","body_b":"peg","contact_count":171.0,"contact_point_centroid":[0.50281,0.00168,0.05977],"force_p95":1.36813,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.68111,"mean_force":0.41836,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49501,0.01315,0.05065]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50683,-0.01887,0.00955],"force_p95":0.6014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87596,"mean_force":0.51157,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49509,0.01133,0.08425]},{"body_a":"peg","body_b":"channel_base_body","contact_count":34.0,"contact_point_centroid":[0.50415,0.10564,0.00939],"force_p95":0.57572,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57583,"mean_force":0.54683,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51648,0.14571,0.04478]}],"total_contact_groups":15},"final_pose_error":0.16825,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5069,-0.01399,0.03376],"final_tcp_position":[0.49556,0.00876,0.13204],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":179.38433,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":796.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55165,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":801.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51917,0.14645,0.04815],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":34.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":0.54964,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34.0,"raw_peak_contact_force":0.57583,"tcp_end":[0.51288,0.14511,0.04069],"tcp_start":[0.51917,0.14645,0.04815],"tcp_to_object_dist_end":0.04158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":327.0,"n_steps_budget":600.0,"object_pos_end":[0.50583,0.10365,0.03433],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.18383,"object_to_goal_dist_start":0.18488,"object_z_max":0.03438,"peak_contact_force":74.62586,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":611.0,"raw_peak_contact_force":75.03762,"tcp_end":[0.50534,0.13372,0.0341],"tcp_start":[0.51288,0.14511,0.04069],"tcp_to_object_dist_end":0.03007,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.50548,-0.01513,0.03667],"object_pos_start":[0.50583,0.10365,0.03433],"object_to_goal_dist_end":0.06518,"object_to_goal_dist_start":0.18383,"object_z_max":0.03881,"peak_contact_force":1.96836,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1778.0,"raw_peak_contact_force":179.38433,"tcp_end":[0.49833,0.01433,0.03709],"tcp_start":[0.50534,0.13372,0.0341],"tcp_to_object_dist_end":0.03032,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5069,-0.01399,0.03376],"object_pos_start":[0.50548,-0.01513,0.03667],"object_to_goal_dist_end":0.06667,"object_to_goal_dist_start":0.06518,"object_z_max":0.03667,"peak_contact_force":0.57419,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1252.0,"raw_peak_contact_force":50.02883,"tcp_end":[0.49556,0.00876,0.13204],"tcp_start":[0.49833,0.01433,0.03709],"tcp_to_object_dist_end":0.10151,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2622,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.19932,"approach_1.speed":0.02773,"contact_1.speed":0.04328,"push_1.push_depth":0.09982,"push_1.push_distance":0.09472,"retract_1.retract_height":0.12798,"retract_1.speed":0.05621},"optimized_scores":{"best_composite_score":0.16623,"best_fitness_score":0.60623,"best_task_score":0.73897},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":360.0,"contact_point_centroid":[0.54268,0.10365,0.05997],"force_p95":178.46015,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":182.21083,"mean_force":123.63096,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49798,0.10261,0.0363]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":511.0,"contact_point_centroid":[0.54426,0.04406,0.05999],"force_p95":103.02447,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.93155,"mean_force":83.71326,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49946,0.04595,0.03668]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54272,-0.02745,0.05999],"force_p95":54.36616,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":54.66008,"mean_force":48.45314,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49807,-0.02187,0.03691]},{"body_a":"attachment","body_b":"peg","contact_count":276.0,"contact_point_centroid":[0.50073,0.02292,0.0396],"force_p95":14.32536,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.35914,"mean_force":2.99664,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49926,0.03459,0.03676]},{"body_a":"peg","body_b":"channel_base_body","contact_count":577.0,"contact_point_centroid":[0.49894,0.00966,0.00968],"force_p95":10.98228,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.00751,"mean_force":1.86098,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49949,0.04694,0.03668]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":101.0,"contact_point_centroid":[0.47463,0.03426,0.04079],"force_p95":3.55491,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.09161,"mean_force":0.71812,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49973,0.0635,0.03663]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":157.0,"contact_point_centroid":[0.5252,-0.02733,0.02585],"force_p95":3.26018,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.24938,"mean_force":0.68265,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49874,0.00163,0.03696]},{"body_a":"peg","body_b":"channel_base_body","contact_count":805.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.5533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55733,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49866,0.1548,0.17095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":996.0,"contact_point_centroid":[0.50526,-0.05174,0.00941],"force_p95":0.55371,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.3948,"mean_force":0.54672,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49491,-0.01736,0.08496]},{"body_a":"attachment","body_b":"peg","contact_count":33.0,"contact_point_centroid":[0.50495,-0.03332,0.05814],"force_p95":0.46629,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.98708,"mean_force":0.22613,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49604,-0.02144,0.04049]},{"body_a":"peg","body_b":"channel_base_body","contact_count":433.0,"contact_point_centroid":[0.50303,0.06742,0.00938],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55077,"mean_force":0.54665,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49782,0.10326,0.03668]},{"body_a":"peg","body_b":"channel_base_body","contact_count":28.0,"contact_point_centroid":[0.50306,0.0668,0.00938],"force_p95":0.55034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55059,"mean_force":0.54668,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49835,0.11061,0.04566]}],"total_contact_groups":12},"final_pose_error":0.16731,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50538,-0.05077,0.03396],"final_tcp_position":[0.49547,-0.01334,0.13329],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":182.21083,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5478,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":805.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.499,0.11132,0.04824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":28.0,"n_steps_budget":600.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54714,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28.0,"raw_peak_contact_force":0.55059,"tcp_end":[0.4983,0.10987,0.04224],"tcp_start":[0.499,0.11132,0.04824],"tcp_to_object_dist_end":0.04353,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":433.0,"n_steps_budget":600.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":137.5851,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":793.0,"raw_peak_contact_force":182.21083,"tcp_end":[0.50065,0.10001,0.036],"tcp_start":[0.4983,0.10987,0.04224],"tcp_to_object_dist_end":0.03272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.50596,-0.05131,0.03707],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.02944,"object_to_goal_dist_start":0.14761,"object_z_max":0.03752,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1622.0,"raw_peak_contact_force":114.93155,"tcp_end":[0.49811,-0.0217,0.03694],"tcp_start":[0.50065,0.10001,0.036],"tcp_to_object_dist_end":0.03064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50538,-0.05077,0.03396],"object_pos_start":[0.50596,-0.05131,0.03707],"object_to_goal_dist_end":0.03033,"object_to_goal_dist_start":0.02944,"object_z_max":0.03707,"peak_contact_force":0.54215,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1032.0,"raw_peak_contact_force":54.66008,"tcp_end":[0.49547,-0.01334,0.13329],"tcp_start":[0.49811,-0.0217,0.03694],"tcp_to_object_dist_end":0.10661,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.22941,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11647,"approach_1.speed":0.09814,"contact_1.speed":0.04368,"push_1.push_depth":0.09976,"push_1.push_distance":0.06175,"retract_1.retract_height":0.13548,"retract_1.speed":0.028},"optimized_scores":{"best_composite_score":0.09644,"best_fitness_score":0.53644,"best_task_score":0.74092},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":501.0,"contact_point_centroid":[0.54486,0.08584,0.05999],"force_p95":108.21195,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.77061,"mean_force":87.34804,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49928,0.08924,0.0361]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":248.0,"contact_point_centroid":[0.55044,0.12,0.05998],"force_p95":113.1182,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.2511,"mean_force":73.57048,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50008,0.14156,0.03415]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54299,0.01898,0.06],"force_p95":91.48909,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":97.44516,"mean_force":56.37712,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49801,0.02212,0.03709]},{"body_a":"attachment","body_b":"peg","contact_count":351.0,"contact_point_centroid":[0.50383,0.06591,0.04231],"force_p95":19.98394,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.09045,"mean_force":4.33811,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49912,0.07756,0.03629]},{"body_a":"peg","body_b":"channel_base_body","contact_count":503.0,"contact_point_centroid":[0.50451,0.04504,0.00972],"force_p95":18.77883,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.7934,"mean_force":3.3618,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49927,0.08783,0.03612]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":293.0,"contact_point_centroid":[0.52515,0.05092,0.02821],"force_p95":2.96814,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.85627,"mean_force":0.70307,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49916,0.0802,0.03632]},{"body_a":"peg","body_b":"channel_base_body","contact_count":377.0,"contact_point_centroid":[0.5035,0.11005,0.00945],"force_p95":0.79772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.07069,"mean_force":0.59677,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50034,0.14326,0.03529]},{"body_a":"attachment","body_b":"peg","contact_count":77.0,"contact_point_centroid":[0.5035,0.1295,0.04143],"force_p95":1.81834,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.6809,"mean_force":0.38688,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50019,0.14146,0.03414]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.50359,0.11169,0.00938],"force_p95":0.60779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55452,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50201,0.17585,0.17071]},{"body_a":"peg","body_b":"channel_base_body","contact_count":995.0,"contact_point_centroid":[0.50652,-0.01176,0.00955],"force_p95":0.55438,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.30841,"mean_force":0.51755,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49484,0.01764,0.08438]},{"body_a":"attachment","body_b":"peg","contact_count":183.0,"contact_point_centroid":[0.50228,0.00899,0.05988],"force_p95":0.28509,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.68327,"mean_force":0.20962,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49473,0.02048,0.05059]},{"body_a":"peg","body_b":"channel_base_body","contact_count":24.0,"contact_point_centroid":[0.50512,0.11115,0.00939],"force_p95":0.58591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5936,"mean_force":0.54414,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50458,0.15277,0.04656]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49976,0.19944,0.29874]}],"total_contact_groups":13},"final_pose_error":0.16869,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50566,-0.00677,0.03399],"final_tcp_position":[0.49538,0.01365,0.13193],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":120.77061,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11173,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57116,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":772.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50559,0.15326,0.04883],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":24.0,"n_steps_budget":600.0,"object_pos_end":[0.50368,0.11176,0.0338],"object_pos_start":[0.50367,0.11173,0.03382],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19187,"object_z_max":0.03382,"peak_contact_force":0.52478,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":0.5936,"tcp_end":[0.50369,0.1524,0.04354],"tcp_start":[0.50559,0.15326,0.04883],"tcp_to_object_dist_end":0.04179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":377.0,"n_steps_budget":600.0,"object_pos_end":[0.50366,0.11114,0.03407],"object_pos_start":[0.50368,0.11176,0.0338],"object_to_goal_dist_end":0.19127,"object_to_goal_dist_start":0.1919,"object_z_max":0.03433,"peak_contact_force":69.70274,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":702.0,"raw_peak_contact_force":115.2511,"tcp_end":[0.50059,0.14112,0.03413],"tcp_start":[0.50369,0.1524,0.04354],"tcp_to_object_dist_end":0.03013,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":723.0,"n_steps_budget":810.0,"object_pos_end":[0.50654,-0.00689,0.0368],"object_pos_start":[0.50366,0.11114,0.03407],"object_to_goal_dist_end":0.07347,"object_to_goal_dist_start":0.19127,"object_z_max":0.03716,"peak_contact_force":1.09822,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1648.0,"raw_peak_contact_force":120.77061,"tcp_end":[0.49803,0.02225,0.03709],"tcp_start":[0.50059,0.14112,0.03413],"tcp_to_object_dist_end":0.03036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50566,-0.00677,0.03399],"object_pos_start":[0.50654,-0.00689,0.0368],"object_to_goal_dist_end":0.07369,"object_to_goal_dist_start":0.07347,"object_z_max":0.0368,"peak_contact_force":0.54354,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1181.0,"raw_peak_contact_force":97.44516,"tcp_end":[0.49538,0.01365,0.13193],"tcp_start":[0.49803,0.02225,0.03709],"tcp_to_object_dist_end":0.10058,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```