## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1527 | 0.31 | ❌ rejected |
| 11 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1517 | 0.30 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.2234 | 0.02 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 2 | 0.1954 | 0.00 | ❌ rejected |
| 8 | approach → contact → push → align | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2037 | 0.12 | ❌ rejected |

**Proposal policy**: task_score is 0.31 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`
- Frozen object start: [0.5009457299760205, 0.11603709570607482, 0.04]
- Frozen task target: [0.5009457299760205, -0.04396290429392519, 0.04]
- Goal object position: (0.5009457299760205, -0.04396290429392519, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, 0.11603709570607482, 0.04)
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
  frozen_object_start: [0.5009, 0.116, 0.04]
  frozen_task_target: [0.5009, -0.044, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5009457299760205, 0.11603709570607482, 0.04]}
  frozen_targets: {'channel_exit': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a

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

## Current Skill (Q=0.153) — your mutation base

```yaml
skill: peg_channel
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
- id: align_2
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

```

## Design Metrics

- **Composite score**: 0.153
- **task_score** (E): 0.306
- **fitness_score**: 0.363  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1730 |
| align_1 | 1.00 | 1.00 | 0.1462 |
| push_1 | 0.00 | 1.00 | 0.1697 |
| align_2 | 1.00 | 1.00 | 0.0394 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.560 | 2.857 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.494, 0.118, 0.043) | (0.497, 0.080, 0.034)→(0.497, 0.084, 0.033) | 0.160→0.164 | 1.00 / 1.667 | 34.709 | 43.847 |
| push_1 | push | 0.00 / step_budget | (0.494, 0.118, 0.043)→(0.495, -0.051, 0.038) | (0.497, 0.084, 0.033)→(0.503, -0.024, 0.023) | 0.164→0.068 | 1.00 / 3.000 | 75.869 | 200.931 |
| align_2 | align | 1.00 / step_budget | (0.495, -0.051, 0.038)→(0.500, -0.014, 0.038) | (0.503, -0.024, 0.023)→(0.496, -0.006, 0.027) | 0.068→0.081 | 1.00 / 4.000 | 217.781 | 320.954 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.847
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.618
- phase_score: 0.467
- phase_breakdown.push_score: 0.767
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.034

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.528
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.618
- **Median Q (composite search score)**: 0.229
- **K-run variance**: 0.0304
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.520


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.91111,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00012,"align_2.lateral_offset_x":0.00531,"push_1.push_distance":0.19992},"optimized_scores":{"best_composite_score":-0.08864,"best_fitness_score":0.12136,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":610.0,"contact_point_centroid":[0.5431,0.03245,0.05997],"force_p95":184.28492,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":220.25149,"mean_force":142.93852,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49825,0.03509,0.0368]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49871,0.08719,0.00784],"force_p95":185.85794,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":193.54958,"mean_force":88.5593,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50309,0.08088,0.04549]},{"body_a":"attachment","body_b":"peg","contact_count":705.0,"contact_point_centroid":[0.50838,0.10403,0.04972],"force_p95":188.79529,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":193.11787,"mean_force":134.68905,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50524,0.10791,0.04846]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":155.0,"contact_point_centroid":[0.52501,0.07329,0.06],"force_p95":141.98564,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":190.72617,"mean_force":75.91143,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50708,0.07327,0.04895]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":530.0,"contact_point_centroid":[0.47372,0.07713,0.02858],"force_p95":76.86196,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":116.50474,"mean_force":35.97492,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50414,0.05887,0.04557]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":68.0,"contact_point_centroid":[0.54174,-0.00035,0.06],"force_p95":56.87929,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.83886,"mean_force":44.24977,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49684,0.00391,0.03713]},{"body_a":"peg","body_b":"world","contact_count":123.0,"contact_point_centroid":[0.50192,0.12554,-0.00019],"force_p95":20.00454,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":14.0888,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5003,0.15484,0.04487]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"attachment","body_b":"peg","contact_count":92.0,"contact_point_centroid":[0.49839,0.07375,0.03756],"force_p95":8.18388,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.53833,"mean_force":1.71747,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49882,0.06203,0.03666]},{"body_a":"peg","body_b":"channel_base_body","contact_count":671.0,"contact_point_centroid":[0.49523,0.08445,0.00944],"force_p95":1.11096,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.43104,"mean_force":0.7535,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49822,0.03281,0.03682]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":206.0,"contact_point_centroid":[0.4749,0.07573,0.05218],"force_p95":0.41179,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.85357,"mean_force":0.11863,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49805,0.0239,0.03691]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52518,0.11568,0.05866],"force_p95":0.47283,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.53841,"mean_force":0.14175,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.4991,0.07908,0.03646]}],"total_contact_groups":15},"final_pose_error":0.0231,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5044,0.12107,0.03358],"final_tcp_position":[0.4992,0.09102,0.03622],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":220.25149,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49304,0.07315,0.03378],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.15344,"object_to_goal_dist_start":0.20832,"object_z_max":0.03454,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2581.0,"raw_peak_contact_force":193.54958,"tcp_end":[0.49702,-0.01011,0.03707],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.08342,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.5044,0.12107,0.03358],"object_pos_start":[0.49304,0.07315,0.03378],"object_to_goal_dist_end":0.20122,"object_to_goal_dist_start":0.15344,"object_z_max":0.03739,"peak_contact_force":148.54513,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1590.0,"raw_peak_contact_force":220.25149,"tcp_end":[0.4992,0.09102,0.03622],"tcp_start":[0.49702,-0.01011,0.03707],"tcp_to_object_dist_end":0.03061,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00162,"align_2.lateral_offset_x":0.01,"push_1.push_distance":0.19666},"optimized_scores":{"best_composite_score":0.31758,"best_fitness_score":0.52758,"best_task_score":0.61837},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":314.0,"contact_point_centroid":[0.52506,-0.06496,0.05997],"force_p95":341.44717,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":438.42142,"mean_force":208.43804,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.5005,-0.06474,0.03754]},{"body_a":"channel_base_body","body_b":"link7","contact_count":338.0,"contact_point_centroid":[0.54219,-0.1,0.06498],"force_p95":319.10334,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":386.75929,"mean_force":124.92871,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49933,-0.06575,0.03733]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":320.0,"contact_point_centroid":[0.54566,-0.06144,0.05995],"force_p95":291.66492,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":313.82796,"mean_force":205.16726,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50049,-0.06477,0.03752]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":321.0,"contact_point_centroid":[0.53465,-0.01277,0.05999],"force_p95":165.18578,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":202.91556,"mean_force":102.46143,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48931,-0.00828,0.03819]},{"body_a":"attachment","body_b":"peg","contact_count":431.0,"contact_point_centroid":[0.50132,-0.07412,0.03739],"force_p95":111.59317,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":185.61145,"mean_force":58.75929,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49948,-0.06554,0.03748]},{"body_a":"peg","body_b":"channel_base_body","contact_count":968.0,"contact_point_centroid":[0.50842,-0.0071,0.00917],"force_p95":91.81335,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":150.1572,"mean_force":43.20947,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48937,0.01516,0.03819]},{"body_a":"attachment","body_b":"peg","contact_count":920.0,"contact_point_centroid":[0.4977,0.00568,0.03578],"force_p95":121.36437,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":136.61763,"mean_force":71.14491,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48937,0.01108,0.03808]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.4955,-0.07152,0.00668],"force_p95":114.20924,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":134.1821,"mean_force":49.53667,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49944,-0.06561,0.03745]},{"body_a":"channel_base_body","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.53505,-0.1,0.065],"force_p95":102.23532,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":113.38355,"mean_force":52.52815,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49204,-0.06663,0.03783]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":835.0,"contact_point_centroid":[0.52622,-0.00893,0.02682],"force_p95":97.66543,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":111.85511,"mean_force":59.15588,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48946,0.00435,0.03807]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":57.0,"contact_point_centroid":[0.52561,-0.06906,0.01694],"force_p95":67.32322,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.85586,"mean_force":45.88505,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49471,-0.0687,0.03773]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":335.0,"contact_point_centroid":[0.47458,-0.07693,0.0233],"force_p95":34.01382,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.66366,"mean_force":26.36242,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50046,-0.06482,0.03749]},{"body_a":"peg","body_b":"link7","contact_count":356.0,"contact_point_centroid":[0.52007,0.0102,0.06778],"force_p95":24.70296,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.15179,"mean_force":12.19008,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48938,0.03503,0.03791]},{"body_a":"peg","body_b":"world","contact_count":41.0,"contact_point_centroid":[0.50978,-0.06619,-0.00056],"force_p95":1.58782,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.58982,"mean_force":0.94542,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49157,-0.06402,0.03786]},{"body_a":"peg","body_b":"world","contact_count":113.0,"contact_point_centroid":[0.50516,-0.06834,-0.00094],"force_p95":12.79348,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.21564,"mean_force":1.82916,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49641,-0.06787,0.03739]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49748,0.13493,0.23568]}],"total_contact_groups":18},"final_pose_error":0.03884,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49221,-0.07159,0.02427],"final_tcp_position":[0.50012,-0.06431,0.03878],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":438.42142,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50912,-0.07288,0.01781],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.02502,"object_to_goal_dist_start":0.14379,"object_z_max":0.03984,"peak_contact_force":103.14511,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3448.0,"raw_peak_contact_force":202.91556,"tcp_end":[0.49289,-0.06898,0.03804],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.02623,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49221,-0.07159,0.02427],"object_pos_start":[0.50912,-0.07288,0.01781],"object_to_goal_dist_end":0.01946,"object_to_goal_dist_start":0.02502,"object_z_max":0.02437,"peak_contact_force":256.51165,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2363.0,"raw_peak_contact_force":438.42142,"tcp_end":[0.50012,-0.06431,0.03878],"tcp_start":[0.49289,-0.06898,0.03804],"tcp_to_object_dist_end":0.01806,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00157,"align_2.lateral_offset_x":-0.00269,"push_1.push_distance":0.18659},"optimized_scores":{"best_composite_score":0.22929,"best_fitness_score":0.43929,"best_task_score":0.29984},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":438.0,"contact_point_centroid":[0.54328,-0.10001,0.06494],"force_p95":292.06487,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":304.19003,"mean_force":242.5276,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50056,-0.06967,0.03752]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":350.0,"contact_point_centroid":[0.52505,-0.06934,0.05998],"force_p95":230.78042,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":248.33762,"mean_force":201.56506,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50088,-0.06919,0.03753]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":312.0,"contact_point_centroid":[0.53446,-0.0073,0.05999],"force_p95":161.35262,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":206.32798,"mean_force":98.21461,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4891,-0.00275,0.03816]},{"body_a":"peg","body_b":"channel_base_body","contact_count":970.0,"contact_point_centroid":[0.50771,-0.0103,0.00883],"force_p95":92.13746,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":138.18696,"mean_force":42.99386,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48944,0.01048,0.0382]},{"body_a":"attachment","body_b":"peg","contact_count":885.0,"contact_point_centroid":[0.49799,-0.00107,0.03501],"force_p95":120.77785,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.94784,"mean_force":71.53882,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48954,0.00365,0.0381]},{"body_a":"channel_base_body","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.53825,-0.1,0.06499],"force_p95":122.09227,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.46231,"mean_force":67.4315,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49548,-0.07481,0.03845]},{"body_a":"attachment","body_b":"peg","contact_count":396.0,"contact_point_centroid":[0.50102,-0.07477,0.0376],"force_p95":79.91914,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":111.97088,"mean_force":37.53021,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50036,-0.06991,0.03757]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":824.0,"contact_point_centroid":[0.52612,-0.00922,0.02403],"force_p95":96.90993,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":110.33939,"mean_force":56.74226,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48952,0.00118,0.03808]},{"body_a":"peg","body_b":"channel_base_body","contact_count":457.0,"contact_point_centroid":[0.49423,-0.07286,0.00654],"force_p95":75.83238,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.26157,"mean_force":36.38612,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50043,-0.06984,0.03754]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":20.0,"contact_point_centroid":[0.52502,-0.04785,0.01622],"force_p95":43.75351,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.5986,"mean_force":28.82367,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.4968,-0.07445,0.03826]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":356.0,"contact_point_centroid":[0.47412,-0.07518,0.0226],"force_p95":41.17704,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":44.1184,"mean_force":25.48442,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50088,-0.0692,0.03752]},{"body_a":"peg","body_b":"world","contact_count":107.0,"contact_point_centroid":[0.50839,-0.06868,-0.0007],"force_p95":0.70362,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.79279,"mean_force":0.77846,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49318,-0.06485,0.03805]},{"body_a":"peg","body_b":"link7","contact_count":242.0,"contact_point_centroid":[0.51781,0.00958,0.06875],"force_p95":18.69635,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.71085,"mean_force":8.81251,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.489,0.0357,0.03795]},{"body_a":"peg","body_b":"world","contact_count":90.0,"contact_point_centroid":[0.50563,-0.07252,-0.001],"force_p95":6.01241,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.68551,"mean_force":0.73389,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49855,-0.0724,0.03771]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.49432,0.05896,0.00937],"force_p95":0.55417,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56118,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49747,0.13481,0.23556]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49933,0.1979,0.29752]}],"total_contact_groups":17},"final_pose_error":0.04221,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49137,-0.06836,0.02319],"final_tcp_position":[0.50048,-0.06854,0.03851],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":304.19003,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05914,0.03393],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54973,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1006.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14702,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":443.0,"n_steps_budget":930.0,"object_pos_end":[0.49439,0.05889,0.034],"object_pos_start":[0.49409,0.05914,0.03393],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.1394,"object_z_max":0.034,"peak_contact_force":0.54579,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":443.0,"raw_peak_contact_force":0.55295,"tcp_end":[0.49044,0.0962,0.04256],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50698,-0.07305,0.01661],"object_pos_start":[0.49439,0.05889,0.034],"object_to_goal_dist_end":0.02538,"object_to_goal_dist_start":0.13914,"object_z_max":0.04008,"peak_contact_force":124.46231,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3345.0,"raw_peak_contact_force":206.32798,"tcp_end":[0.49565,-0.07524,0.03855],"tcp_start":[0.49044,0.0962,0.04256],"tcp_to_object_dist_end":0.02478,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":457.0,"n_steps_budget":600.0,"object_pos_end":[0.49137,-0.06836,0.02319],"object_pos_start":[0.50698,-0.07305,0.01661],"object_to_goal_dist_end":0.02219,"object_to_goal_dist_start":0.02538,"object_z_max":0.02412,"peak_contact_force":248.28613,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2107.0,"raw_peak_contact_force":304.19003,"tcp_end":[0.50048,-0.06854,0.03851],"tcp_start":[0.49565,-0.07524,0.03855],"tcp_to_object_dist_end":0.01782,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```