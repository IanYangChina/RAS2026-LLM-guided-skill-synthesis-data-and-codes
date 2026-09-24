## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1659 | 0.40 | ❌ rejected |
| 5 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1208 | 0.32 | ❌ rejected |
| 4 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1680 | 0.40 | ❌ rejected |
| 3 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1494 | 0.30 | ❌ rejected |
| 2 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1153 | 0.34 | ❌ rejected |

**Proposal policy**: task_score is 0.40 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.166) — your mutation base

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

- **Composite score**: 0.166
- **task_score** (E): 0.400
- **fitness_score**: 0.376  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| rotate_1 | 1.00 | 1.00 | 0.1730 |
| align_1 | 1.00 | 1.00 | 0.1462 |
| push_1 | 0.33 | 0.67 | 0.1268 |
| align_2 | 1.00 | 1.00 | 0.0067 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| rotate_1 | rotate | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.075, 0.180) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.560 | 2.857 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.075, 0.180)→(0.494, 0.118, 0.043) | (0.497, 0.080, 0.034)→(0.497, 0.084, 0.033) | 0.160→0.164 | 1.00 / 1.667 | 34.709 | 43.847 |
| push_1 | push | 0.33 / step_budget | (0.494, 0.118, 0.043)→(0.497, -0.009, 0.040) | (0.497, 0.084, 0.033)→(0.505, -0.023, 0.025) | 0.164→0.070 | 0.67 / 3.000 | 63.885 | 198.978 |
| align_2 | align | 1.00 / step_budget | (0.497, -0.009, 0.040)→(0.500, -0.005, 0.039) | (0.505, -0.023, 0.025)→(0.496, -0.023, 0.029) | 0.070→0.064 | 1.00 / 4.000 | 168.314 | 230.917 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.836
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.612
- phase_score: 0.472
- phase_breakdown.push_score: 0.775
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.035

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.528
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.612
- **Median Q (composite search score)**: 0.213
- **K-run variance**: 0.0216
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Final σ (mean)**: 0.431


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28571,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00234,"align_2.lateral_offset_x":-0.0031,"push_1.push_distance":0.02088},"optimized_scores":{"best_composite_score":-0.03313,"best_fitness_score":0.17687,"best_task_score":0.29052},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.50789,0.11577,0.00736],"force_p95":194.50816,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":195.76218,"mean_force":133.60802,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50323,0.14282,0.047]},{"body_a":"attachment","body_b":"peg","contact_count":436.0,"contact_point_centroid":[0.5098,0.13565,0.04675],"force_p95":194.04876,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":195.39268,"mean_force":143.61819,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50314,0.14387,0.04703]},{"body_a":"attachment","body_b":"peg","contact_count":109.0,"contact_point_centroid":[0.50657,0.13982,0.05102],"force_p95":119.53343,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":130.43451,"mean_force":83.80714,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49846,0.14657,0.05326]},{"body_a":"peg","body_b":"channel_base_body","contact_count":563.0,"contact_point_centroid":[0.50214,0.1166,0.00925],"force_p95":94.17839,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.99062,"mean_force":15.43742,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49609,0.11288,0.10781]},{"body_a":"peg","body_b":"world","contact_count":175.0,"contact_point_centroid":[0.50197,0.12508,-0.00016],"force_p95":19.66497,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.74864,"mean_force":14.05169,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5004,0.1546,0.04468]},{"body_a":"peg","body_b":"world","contact_count":28.0,"contact_point_centroid":[0.50222,0.12719,-0.0003],"force_p95":37.33342,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.90411,"mean_force":28.00895,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49992,0.15488,0.04587]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47426,0.08616,0.05677],"force_p95":3.15298,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.422,"mean_force":1.5304,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50619,0.11982,0.04752]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50098,0.11602,0.0094],"force_p95":0.60736,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55146,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49749,0.13563,0.23636]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":8.0,"contact_point_centroid":[0.52522,0.0541,0.05121],"force_p95":1.59075,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.69502,"mean_force":0.93538,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50121,0.11555,0.04146]},{"body_a":"peg","body_b":"channel_base_body","contact_count":15.0,"contact_point_centroid":[0.50004,0.08095,0.00996],"force_p95":0.77561,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.78991,"mean_force":0.61185,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50159,0.11555,0.04188]}],"total_contact_groups":10},"final_pose_error":0.00454,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50257,0.06955,0.03855],"final_tcp_position":[0.50074,0.1157,0.04103],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":195.76218,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11601,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.58045,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":984.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.15182,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":563.0,"n_steps_budget":1000.0,"object_pos_end":[0.50228,0.12805,0.02979],"object_pos_start":[0.50092,0.11601,0.03383],"object_to_goal_dist_end":0.20832,"object_to_goal_dist_start":0.19611,"object_z_max":0.0342,"peak_contact_force":103.03901,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":700.0,"raw_peak_contact_force":130.43451,"tcp_end":[0.50029,0.1577,0.04359],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03276,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":460.0,"n_steps_budget":600.0,"object_pos_end":[0.49887,0.07983,0.04109],"object_pos_start":[0.50228,0.12805,0.02979],"object_to_goal_dist_end":0.15984,"object_to_goal_dist_start":0.20832,"object_z_max":0.04112,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1075.0,"raw_peak_contact_force":195.76218,"tcp_end":[0.50268,0.11609,0.04321],"tcp_start":[0.50029,0.1577,0.04359],"tcp_to_object_dist_end":0.03653,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.50257,0.06955,0.03855],"object_pos_start":[0.49887,0.07983,0.04109],"object_to_goal_dist_end":0.14958,"object_to_goal_dist_start":0.15984,"object_z_max":0.04109,"peak_contact_force":0.58091,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":23.0,"raw_peak_contact_force":1.69502,"tcp_end":[0.50074,0.1157,0.04103],"tcp_start":[0.50268,0.11609,0.04321],"tcp_to_object_dist_end":0.04624,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00227,"align_2.lateral_offset_x":-0.00294,"push_1.push_distance":0.19995},"optimized_scores":{"best_composite_score":0.31793,"best_fitness_score":0.52793,"best_task_score":0.61156},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":343.0,"contact_point_centroid":[0.52507,-0.06389,0.05997],"force_p95":269.00934,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":349.16792,"mean_force":213.2256,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50055,-0.06367,0.03733]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":341.0,"contact_point_centroid":[0.54547,-0.0604,0.05994],"force_p95":295.35512,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":317.50078,"mean_force":222.7403,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50039,-0.0638,0.03734]},{"body_a":"channel_base_body","body_b":"link7","contact_count":82.0,"contact_point_centroid":[0.53991,-0.10001,0.06496],"force_p95":229.59164,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.23277,"mean_force":161.52376,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49732,-0.06722,0.03707]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":307.0,"contact_point_centroid":[0.53464,-0.01066,0.05999],"force_p95":164.04551,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":208.75757,"mean_force":100.22369,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48931,-0.00589,0.03816]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.49618,-0.06542,0.00663],"force_p95":127.90705,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":139.19912,"mean_force":63.0242,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49976,-0.06454,0.03727]},{"body_a":"attachment","body_b":"peg","contact_count":450.0,"contact_point_centroid":[0.5024,-0.06805,0.037],"force_p95":127.5254,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.77351,"mean_force":68.81842,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49978,-0.06451,0.03728]},{"body_a":"attachment","body_b":"peg","contact_count":920.0,"contact_point_centroid":[0.49783,0.00617,0.03582],"force_p95":119.65438,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.64851,"mean_force":68.32898,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48943,0.0116,0.03806]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.5084,-0.00715,0.00909],"force_p95":95.07777,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.74332,"mean_force":42.8869,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48942,0.01567,0.03817]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":838.0,"contact_point_centroid":[0.52616,-0.0064,0.02674],"force_p95":96.8267,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.8525,"mean_force":57.46145,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48953,0.00494,0.03805]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":35.0,"contact_point_centroid":[0.5251,-0.05839,0.01654],"force_p95":39.10437,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.31145,"mean_force":30.73332,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49496,-0.06891,0.03769]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":296.0,"contact_point_centroid":[0.47461,-0.08113,0.02347],"force_p95":31.98925,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.08575,"mean_force":25.68582,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50046,-0.0636,0.03746]},{"body_a":"peg","body_b":"link7","contact_count":362.0,"contact_point_centroid":[0.52006,0.00974,0.06777],"force_p95":24.76105,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.17384,"mean_force":12.32344,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48934,0.03458,0.03791]},{"body_a":"peg","body_b":"world","contact_count":68.0,"contact_point_centroid":[0.50914,-0.06785,-0.00085],"force_p95":17.76393,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.97072,"mean_force":1.89019,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49194,-0.06113,0.03789]},{"body_a":"peg","body_b":"world","contact_count":104.0,"contact_point_centroid":[0.5052,-0.06599,-0.00119],"force_p95":10.32647,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.99789,"mean_force":1.63877,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.4971,-0.06736,0.03715]},{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.51688,-0.10001,0.01586],"force_p95":4.22272,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.27891,"mean_force":3.71701,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49892,-0.06621,0.03669]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49527,0.06395,0.00938],"force_p95":0.55699,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55424,"phase_index":0.0,"phase_name":"rotate_1","phase_type":"rotate","tcp_position_centroid":[0.49748,0.13493,0.23568]}],"total_contact_groups":18},"final_pose_error":0.03872,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49218,-0.06984,0.02425],"final_tcp_position":[0.50018,-0.06314,0.03852],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":349.16792,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06382,0.03401],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14404,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55002,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1001.0,"raw_peak_contact_force":2.44546,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14649,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":447.0,"n_steps_budget":930.0,"object_pos_end":[0.49519,0.06359,0.03403],"object_pos_start":[0.49482,0.06382,0.03401],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14404,"object_z_max":0.03403,"peak_contact_force":0.54085,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":447.0,"raw_peak_contact_force":0.55403,"tcp_end":[0.4911,0.10042,0.04259],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50742,-0.07192,0.01679],"object_pos_start":[0.49519,0.06359,0.03403],"object_to_goal_dist_end":0.02567,"object_to_goal_dist_start":0.14379,"object_z_max":0.03988,"peak_contact_force":89.0535,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3466.0,"raw_peak_contact_force":208.75757,"tcp_end":[0.49386,-0.06903,0.03806],"tcp_start":[0.4911,0.10042,0.04259],"tcp_to_object_dist_end":0.02539,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49218,-0.06984,0.02425],"object_pos_start":[0.50742,-0.07192,0.01679],"object_to_goal_dist_end":0.02031,"object_to_goal_dist_start":0.02567,"object_z_max":0.02422,"peak_contact_force":255.25592,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2108.0,"raw_peak_contact_force":349.16792,"tcp_end":[0.50018,-0.06314,0.03852],"tcp_start":[0.49386,-0.06903,0.03806],"tcp_to_object_dist_end":0.01768,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75397,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00526,"align_2.lateral_offset_x":0.00012,"push_1.push_distance":0.18222},"optimized_scores":{"best_composite_score":0.21287,"best_fitness_score":0.42287,"best_task_score":0.29728},"replay_outcomes":[{"contacts":{"omitted_contact_groups":3,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":331.0,"contact_point_centroid":[0.52506,-0.06776,0.05997],"force_p95":321.52141,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":341.88681,"mean_force":217.63966,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50071,-0.06757,0.03768]},{"body_a":"channel_base_body","body_b":"link7","contact_count":441.0,"contact_point_centroid":[0.54295,-0.10001,0.06495],"force_p95":283.67779,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":325.94247,"mean_force":227.26488,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50005,-0.06833,0.03766]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":345.0,"contact_point_centroid":[0.53466,-0.01159,0.05999],"force_p95":167.55748,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":192.41514,"mean_force":99.09056,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48934,-0.0071,0.03815]},{"body_a":"attachment","body_b":"peg","contact_count":441.0,"contact_point_centroid":[0.50157,-0.07634,0.03743],"force_p95":91.15898,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":147.11857,"mean_force":52.99098,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49996,-0.0684,0.03768]},{"body_a":"peg","body_b":"channel_base_body","contact_count":966.0,"contact_point_centroid":[0.50768,-0.01047,0.00911],"force_p95":98.95987,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":140.54732,"mean_force":42.74299,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48936,0.01119,0.0382]},{"body_a":"attachment","body_b":"peg","contact_count":880.0,"contact_point_centroid":[0.49777,-0.00072,0.03522],"force_p95":121.26632,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.49953,"mean_force":73.59061,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48946,0.00434,0.0381]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.49533,-0.07747,0.00661],"force_p95":86.39682,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.13889,"mean_force":50.14625,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49995,-0.06844,0.03767]},{"body_a":"channel_base_body","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.53552,-0.1,0.065],"force_p95":118.05111,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":123.52339,"mean_force":89.32997,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49252,-0.06765,0.03796]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":851.0,"contact_point_centroid":[0.52616,-0.00927,0.02439],"force_p95":97.36314,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":109.56374,"mean_force":58.4116,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48951,0.00176,0.03808]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":39.0,"contact_point_centroid":[0.52536,-0.07128,0.01749],"force_p95":76.1907,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.51458,"mean_force":41.02317,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49545,-0.07278,0.03827]},{"body_a":"peg","body_b":"channel_base_body","contact_count":33.0,"contact_point_centroid":[0.51467,-0.10025,0.01707],"force_p95":50.78231,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.64149,"mean_force":31.28216,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49327,-0.06969,0.03818]},{"body_a":"peg","body_b":"channel_base_body","contact_count":27.0,"contact_point_centroid":[0.51403,-0.1002,0.01734],"force_p95":27.58865,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.63802,"mean_force":14.34165,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49664,-0.07188,0.03799]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":333.0,"contact_point_centroid":[0.4744,-0.07438,0.02296],"force_p95":37.52059,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.64989,"mean_force":27.79006,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.50071,-0.06757,0.03768]},{"body_a":"peg","body_b":"world","contact_count":57.0,"contact_point_centroid":[0.50984,-0.06569,-0.00058],"force_p95":2.24426,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.61761,"mean_force":0.93692,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49238,-0.06647,0.03809]},{"body_a":"peg","body_b":"link7","contact_count":157.0,"contact_point_centroid":[0.51674,0.00812,0.0693],"force_p95":10.22019,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.86701,"mean_force":6.24755,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48914,0.03524,0.03794]},{"body_a":"peg","body_b":"world","contact_count":104.0,"contact_point_centroid":[0.50549,-0.07049,-0.00076],"force_p95":4.92617,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.49439,"mean_force":0.83846,"phase_index":3.0,"phase_name":"align_2","phase_type":"align","tcp_position_centroid":[0.49746,-0.07109,0.03775]}],"total_contact_groups":19},"final_pose_error":0.03854,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49178,-0.06986,0.02337],"final_tcp_position":[0.50027,-0.0669,0.03876],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":341.88681,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49409,0.05914,0.03393],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.1394,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54973,"phase_name":"rotate_1","phase_peak_obstacle_force":0.0,"phase_type":"rotate","raw_contact_event_count":1006.0,"raw_peak_contact_force":4.20518,"tcp_end":[0.49696,0.07528,0.18003],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.14702,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":443.0,"n_steps_budget":930.0,"object_pos_end":[0.49439,0.05889,0.034],"object_pos_start":[0.49409,0.05914,0.03393],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.1394,"object_z_max":0.034,"peak_contact_force":0.54579,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":443.0,"raw_peak_contact_force":0.55295,"tcp_end":[0.49044,0.0962,0.04256],"tcp_start":[0.49696,0.07528,0.18003],"tcp_to_object_dist_end":0.03848,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50859,-0.07565,0.01778],"object_pos_start":[0.49439,0.05889,0.034],"object_to_goal_dist_end":0.02421,"object_to_goal_dist_start":0.13914,"object_z_max":0.04022,"peak_contact_force":102.60132,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3296.0,"raw_peak_contact_force":192.41514,"tcp_end":[0.49434,-0.073,0.03846],"tcp_start":[0.49044,0.0962,0.04256],"tcp_to_object_dist_end":0.02525,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.49178,-0.06986,0.02337],"object_pos_start":[0.50859,-0.07565,0.01778],"object_to_goal_dist_end":0.02114,"object_to_goal_dist_start":0.02421,"object_z_max":0.02387,"peak_contact_force":249.10582,"phase_name":"align_2","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2171.0,"raw_peak_contact_force":341.88681,"tcp_end":[0.50027,-0.0669,0.03876],"tcp_start":[0.49434,-0.073,0.03846],"tcp_to_object_dist_end":0.01782,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```