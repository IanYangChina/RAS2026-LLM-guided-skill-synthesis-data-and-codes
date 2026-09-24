## Search State

- **Seed**: 2
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2813 | 0.23 | ✅ accepted |

**Proposal policy**: task_score is 0.23 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
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
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

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

## Current Skill (Q=0.281) — your mutation base

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
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.281
- **task_score** (E): 0.229
- **fitness_score**: 0.321  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.240

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2560 |
| approach_1 | 1.00 | 1.00 | 0.0147 |
| contact_1 | 1.00 | 1.00 | 0.0029 |
| push_1 | 0.67 | 1.00 | 0.0911 |
| retract_1 | 0.00 | 1.00 | 0.1659 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.116, 0.060) | (0.494, 0.068, 0.040)→(0.499, 0.068, 0.034) | 0.151→0.148 | 1.00 / 2.000 | 325.920 | 378.205 |
| approach_1 | approach | 1.00 / step_budget | (0.495, 0.116, 0.060)→(0.501, 0.112, 0.048) | (0.499, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.333 | 72.687 | 282.385 |
| contact_1 | contact | 1.00 / force_exceeded | (0.501, 0.112, 0.048)→(0.500, 0.111, 0.046) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 48.368 | 48.368 |
| push_1 | push | 0.67 / step_budget | (0.500, 0.111, 0.046)→(0.504, 0.020, 0.046) | (0.498, 0.068, 0.034)→(0.503, -0.008, 0.037) | 0.148→0.072 | 1.00 / 2.333 | 89.864 | 173.610 |
| retract_1 | retract | 0.00 / step_budget | (0.504, 0.020, 0.046)→(0.499, 0.030, 0.207) | (0.503, -0.008, 0.037)→(0.499, -0.012, 0.034) | 0.072→0.069 | 1.00 / 1.333 | 0.509 | 72.540 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.698
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.460
- phase_score: 0.477
- phase_breakdown.approach_score: 0.853
- phase_breakdown.push_score: 0.291
- phase_breakdown.contact_score: 0.660

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.470
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.460
- **Median Q (composite search score)**: 0.316
- **K-run variance**: 0.0190
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.376


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69128,"average_solve_count":149.0,"average_success_count":149.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00985,"align_1.lateral_offset_y":-0.00723,"push_1.push_depth":0.09448},"optimized_scores":{"best_composite_score":0.43016,"best_fitness_score":0.47016,"best_task_score":0.45974},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":60.0,"contact_point_centroid":[0.4749,0.12,0.0598],"force_p95":341.5277,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.62701,"mean_force":311.80708,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47984,0.111,0.05723]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.47497,0.11792,0.05994],"force_p95":283.70214,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.29523,"mean_force":209.67753,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48303,0.11067,0.05591]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":533.0,"contact_point_centroid":[0.53809,0.04632,0.05999],"force_p95":110.23856,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.01693,"mean_force":91.58843,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49253,0.04796,0.03817]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54322,-0.02385,0.06],"force_p95":63.7236,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.15621,"mean_force":59.83012,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49814,-0.01847,0.03772]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53298,0.10511,0.05998],"force_p95":36.59731,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":36.59731,"mean_force":36.59731,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48737,0.10365,0.03818]},{"body_a":"attachment","body_b":"peg","contact_count":218.0,"contact_point_centroid":[0.49819,0.0288,0.0437],"force_p95":23.08013,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.64416,"mean_force":4.74411,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49327,0.04033,0.03819]},{"body_a":"peg","body_b":"channel_base_body","contact_count":557.0,"contact_point_centroid":[0.49969,0.00854,0.00954],"force_p95":15.82815,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.37332,"mean_force":2.37322,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49247,0.04866,0.03817]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":101.0,"contact_point_centroid":[0.52521,-0.00963,0.02821],"force_p95":1.2645,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.95014,"mean_force":0.61764,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49522,0.01888,0.03812]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":51.0,"contact_point_centroid":[0.47465,0.02527,0.04172],"force_p95":1.55568,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.14801,"mean_force":0.67646,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49184,0.05571,0.03822]},{"body_a":"peg","body_b":"channel_base_body","contact_count":820.0,"contact_point_centroid":[0.49531,0.0638,0.00938],"force_p95":0.56258,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55591,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48773,0.15105,0.1656]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49933,0.19869,0.29695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":994.0,"contact_point_centroid":[0.49515,-0.04812,0.00946],"force_p95":0.55776,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.95984,"mean_force":0.5437,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49548,0.00677,0.11644]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49778,-0.03034,0.03791],"force_p95":0.56929,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.59925,"mean_force":0.29963,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49816,-0.01839,0.03773]},{"body_a":"peg","body_b":"channel_base_body","contact_count":95.0,"contact_point_centroid":[0.49536,0.06392,0.0094],"force_p95":0.55022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54534,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48551,0.10908,0.05114]},{"body_a":"peg","body_b":"channel_base_body","contact_count":26.0,"contact_point_centroid":[0.49629,0.06493,0.0094],"force_p95":0.55077,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55176,"mean_force":0.54506,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48783,0.10485,0.03944]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47494,-0.04909,0.05928],"force_p95":0.31651,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.33768,"mean_force":0.16783,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49673,-0.01677,0.04036]}],"total_contact_groups":16},"final_pose_error":0.1022,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49427,-0.04773,0.03454],"final_tcp_position":[0.49652,0.01726,0.19933],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":355.62701,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.49535,0.06392,0.03399],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":334.70153,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":908.0,"raw_peak_contact_force":355.62701,"tcp_end":[0.481,0.11081,0.05671],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":95.0,"n_steps_budget":600.0,"object_pos_end":[0.49532,0.06402,0.034],"object_pos_start":[0.49535,0.06392,0.03399],"object_to_goal_dist_end":0.14422,"object_to_goal_dist_start":0.14412,"object_z_max":0.034,"peak_contact_force":0.55289,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":125.0,"raw_peak_contact_force":307.29523,"tcp_end":[0.48856,0.10593,0.04095],"tcp_start":[0.481,0.11081,0.05671],"tcp_to_object_dist_end":0.04301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":26.0,"n_steps_budget":600.0,"object_pos_end":[0.4952,0.06412,0.03401],"object_pos_start":[0.49532,0.06402,0.034],"object_to_goal_dist_end":0.14433,"object_to_goal_dist_start":0.14422,"object_z_max":0.03401,"peak_contact_force":36.59731,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":27.0,"raw_peak_contact_force":36.59731,"tcp_end":[0.48735,0.10356,0.03811],"tcp_start":[0.48856,0.10593,0.04095],"tcp_to_object_dist_end":0.04042,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.49641,-0.04813,0.03658],"object_pos_start":[0.4952,0.06412,0.03401],"object_to_goal_dist_end":0.03225,"object_to_goal_dist_start":0.14433,"object_z_max":0.03921,"peak_contact_force":7.64784,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1460.0,"raw_peak_contact_force":118.01693,"tcp_end":[0.49817,-0.01834,0.03774],"tcp_start":[0.48735,0.10356,0.03811],"tcp_to_object_dist_end":0.02987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49427,-0.04773,0.03454],"object_pos_start":[0.49641,-0.04813,0.03658],"object_to_goal_dist_end":0.03323,"object_to_goal_dist_start":0.03225,"object_z_max":0.03688,"peak_contact_force":0.54223,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":64.15621,"tcp_end":[0.49652,0.01726,0.19933],"tcp_start":[0.49817,-0.01834,0.03774],"tcp_to_object_dist_end":0.17715,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70199,"average_solve_count":151.0,"average_success_count":151.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00578,"align_1.lateral_offset_y":-0.00571,"push_1.push_depth":0.09938},"optimized_scores":{"best_composite_score":0.31615,"best_fitness_score":0.35615,"best_task_score":0.22634},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":106.0,"contact_point_centroid":[0.47492,0.11854,0.05985],"force_p95":346.92903,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.37637,"mean_force":313.68239,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47019,0.10819,0.06243]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":69.0,"contact_point_centroid":[0.47497,0.11524,0.05995],"force_p95":296.63938,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":322.46444,"mean_force":213.26593,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48035,0.10608,0.0574]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":471.0,"contact_point_centroid":[0.53597,0.04719,0.05999],"force_p95":109.37769,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":132.20273,"mean_force":91.58529,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49061,0.04879,0.03778]},{"body_a":"attachment","body_b":"peg","contact_count":579.0,"contact_point_centroid":[0.49959,0.01708,0.03589],"force_p95":94.40135,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.37983,"mean_force":55.98531,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49256,0.02521,0.03773]},{"body_a":"peg","body_b":"channel_base_body","contact_count":750.0,"contact_point_centroid":[0.50537,0.00661,0.00965],"force_p95":64.49486,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.11556,"mean_force":26.94888,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49145,0.03857,0.03775]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":559.0,"contact_point_centroid":[0.5256,0.00388,0.02577],"force_p95":56.04085,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.98535,"mean_force":37.26712,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49276,0.02286,0.03773]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5414,-0.02995,0.06],"force_p95":59.32009,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.32009,"mean_force":59.32009,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4966,-0.0242,0.03725]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53162,0.09941,0.05997],"force_p95":32.10104,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":32.10104,"mean_force":32.10104,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4862,0.09824,0.03774]},{"body_a":"peg","body_b":"channel_base_body","contact_count":990.0,"contact_point_centroid":[0.50101,-0.05348,0.00999],"force_p95":0.49266,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.92374,"mean_force":0.4632,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49446,0.00294,0.11572]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.50207,-0.03261,0.03563],"force_p95":4.0823,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":20.93541,"mean_force":1.32783,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49597,-0.0236,0.03824]},{"body_a":"peg","body_b":"channel_base_body","contact_count":854.0,"contact_point_centroid":[0.49433,0.05892,0.00937],"force_p95":0.55492,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56328,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48064,0.14718,0.16216]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49899,0.19829,0.29587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":860.0,"contact_point_centroid":[0.50034,-0.10001,0.02974],"force_p95":0.24133,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.62077,"mean_force":0.22162,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49446,0.00573,0.12451]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.5252,-0.042,0.02161],"force_p95":1.89511,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.01398,"mean_force":0.7949,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49616,-0.02389,0.03787]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":561.0,"contact_point_centroid":[0.47499,-0.08981,0.0433],"force_p95":0.21287,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.90268,"mean_force":0.09855,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49436,0.00456,0.11923]},{"body_a":"peg","body_b":"channel_base_body","contact_count":139.0,"contact_point_centroid":[0.49413,0.05949,0.00939],"force_p95":0.5498,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55091,"mean_force":0.54582,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48263,0.10497,0.05384]}],"total_contact_groups":17},"final_pose_error":0.10275,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49727,-0.07016,0.03499],"final_tcp_position":[0.49596,0.01527,0.19847],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":355.37637,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.0591,0.03391],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13935,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":328.62809,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":995.0,"raw_peak_contact_force":355.37637,"tcp_end":[0.4745,0.10691,0.06026],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":139.0,"n_steps_budget":600.0,"object_pos_end":[0.49397,0.05907,0.03393],"object_pos_start":[0.49422,0.0591,0.03391],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.13935,"object_z_max":0.03393,"peak_contact_force":0.54501,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":208.0,"raw_peak_contact_force":322.46444,"tcp_end":[0.48761,0.10116,0.04108],"tcp_start":[0.4745,0.10691,0.06026],"tcp_to_object_dist_end":0.04317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":33.0,"n_steps_budget":600.0,"object_pos_end":[0.49431,0.05903,0.03393],"object_pos_start":[0.49397,0.05907,0.03393],"object_to_goal_dist_end":0.13928,"object_to_goal_dist_start":0.13933,"object_z_max":0.03393,"peak_contact_force":32.10104,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":34.0,"raw_peak_contact_force":32.10104,"tcp_end":[0.48619,0.09816,0.03767],"tcp_start":[0.48761,0.10116,0.04108],"tcp_to_object_dist_end":0.04014,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50785,-0.058,0.03997],"object_pos_start":[0.49431,0.05903,0.03393],"object_to_goal_dist_end":0.02336,"object_to_goal_dist_start":0.13928,"object_z_max":0.04048,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2359.0,"raw_peak_contact_force":132.20273,"tcp_end":[0.49665,-0.02405,0.03727],"tcp_start":[0.48619,0.09816,0.03767],"tcp_to_object_dist_end":0.03585,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49727,-0.07016,0.03499],"object_pos_start":[0.50785,-0.058,0.03997],"object_to_goal_dist_end":0.01138,"object_to_goal_dist_start":0.02336,"object_z_max":0.04074,"peak_contact_force":0.4408,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2452.0,"raw_peak_contact_force":59.32009,"tcp_end":[0.49596,0.01527,0.19847],"tcp_start":[0.49665,-0.02405,0.03727],"tcp_to_object_dist_end":0.18446,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76712,"average_solve_count":146.0,"average_success_count":146.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00553,"align_1.lateral_offset_y":0.00899,"push_1.push_depth":0.1},"optimized_scores":{"best_composite_score":0.09758,"best_fitness_score":0.13758,"best_task_score":8e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":95.0,"contact_point_centroid":[0.53608,0.11993,0.0598],"force_p95":364.62154,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.61103,"mean_force":316.10752,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5286,0.12877,0.06252]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":859.0,"contact_point_centroid":[0.53169,0.10985,0.05993],"force_p95":261.72238,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":270.61143,"mean_force":224.42059,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52119,0.11183,0.06427]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":437.0,"contact_point_centroid":[0.5348,0.11998,0.05995],"force_p95":216.87959,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":217.39575,"mean_force":180.83381,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52816,0.12956,0.0626]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52953,0.10237,0.05996],"force_p95":91.8041,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":94.14498,"mean_force":73.82215,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5185,0.10366,0.06448]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53338,0.11997,0.05995],"force_p95":76.40648,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.40648,"mean_force":76.40648,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52764,0.13021,0.06223]},{"body_a":"peg","body_b":"channel_base_body","contact_count":845.0,"contact_point_centroid":[0.50578,0.08087,0.00937],"force_p95":0.55112,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56482,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5151,0.15903,0.16341]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49991,0.19854,0.29567]},{"body_a":"peg","body_b":"channel_base_body","contact_count":438.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52816,0.12956,0.0626]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.507,0.09875,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.55006,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52764,0.13021,0.06223]},{"body_a":"peg","body_b":"channel_base_body","contact_count":873.0,"contact_point_centroid":[0.50601,0.08085,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52123,0.11196,0.06427]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50595,0.0809,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50883,0.08652,0.14466]}],"total_contact_groups":11},"final_pose_error":0.09556,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50597,0.08086,0.03378],"final_tcp_position":[0.50304,0.05663,0.22308],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":423.61103,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":314.43154,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":976.0,"raw_peak_contact_force":423.61103,"tcp_end":[0.5292,0.12912,0.06281],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":438.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.08089,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":216.96175,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":875.0,"raw_peak_contact_force":217.39575,"tcp_end":[0.52764,0.13021,0.06223],"tcp_start":[0.5292,0.12912,0.06281],"tcp_to_object_dist_end":0.06092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.50597,0.08089,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":76.40648,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":76.40648,"tcp_end":[0.52764,0.13022,0.06223],"tcp_start":[0.52764,0.13021,0.06223],"tcp_to_object_dist_end":0.06093,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.50595,0.08086,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":261.94419,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1732.0,"raw_peak_contact_force":270.61143,"tcp_end":[0.51851,0.10365,0.06447],"tcp_start":[0.52764,0.13022,0.06223],"tcp_to_object_dist_end":0.04024,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50595,0.08086,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":0.54458,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1003.0,"raw_peak_contact_force":94.14498,"tcp_end":[0.50304,0.05663,0.22308],"tcp_start":[0.51851,0.10365,0.06447],"tcp_to_object_dist_end":0.19087,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```