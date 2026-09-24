## Search State

- **Seed**: 9
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 7 | -0.0403 | 0.00 | ❌ rejected |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.0986 | 0.13 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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

## Current Skill (Q=-0.040) — your mutation base

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
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
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
  termination: time_limit
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
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: -0.040
- **task_score** (E): 0.002
- **fitness_score**: 0.150  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2618 |
| approach_1 | 1.00 | 1.00 | 0.0095 |
| contact_1 | 1.00 | 1.00 | 0.0000 |
| push_1 | 1.00 | 1.00 | 0.0169 |
| retract_1 | 0.00 | 1.00 | 0.0053 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.492, 0.112, 0.055) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 | 1.00 / 2.000 | 258.764 | 326.309 |
| approach_1 | approach | 1.00 / step_budget | (0.492, 0.112, 0.055)→(0.500, 0.110, 0.056) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.667 | 323.368 | 409.916 |
| contact_1 | contact | 1.00 / force_exceeded | (0.500, 0.110, 0.056)→(0.500, 0.110, 0.056) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 | 1.00 / 2.667 | 71.879 | 71.879 |
| push_1 | push | 1.00 / time_limit | (0.500, 0.110, 0.056)→(0.500, 0.095, 0.052) | (0.502, 0.067, 0.034)→(0.502, 0.066, 0.034) | 0.147→0.146 | 1.00 / 2.667 | 431.893 | 486.582 |
| retract_1 | retract | 0.00 / step_budget | (0.500, 0.095, 0.052)→(0.500, 0.097, 0.047) | (0.502, 0.066, 0.034)→(0.502, 0.066, 0.034) | 0.146→0.146 | 1.00 / 2.667 | 186.775 | 306.153 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.018
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.007
- phase_score: 0.258
- phase_breakdown.approach_score: 0.640
- phase_breakdown.contact_score: 0.529
- phase_breakdown.push_score: 0.040

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.157
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.007
- **Median Q (composite search score)**: -0.037
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.356


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19162,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.01579,"approach_1.speed":0.02188,"contact_1.contact_force":1.46564,"push_1.max_time":4.64637,"push_1.push_distance":0.09255,"push_1.push_speed":0.02423,"retract_1.speed":0.04982},"optimized_scores":{"best_composite_score":-0.03253,"best_fitness_score":0.15747,"best_task_score":0.00674},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":156.0,"contact_point_centroid":[0.47495,0.11992,0.05338],"force_p95":504.47228,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":557.96104,"mean_force":359.97395,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51311,0.07927,0.05096]},{"body_a":"world","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.51178,0.17008,-0.00047],"force_p95":317.40503,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":341.54439,"mean_force":263.53406,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50965,0.10861,0.05397]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.525,0.11995,0.06],"force_p95":213.68916,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":339.78021,"mean_force":166.97879,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5125,0.07931,0.05198]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.47497,0.11995,0.05967],"force_p95":287.93775,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":326.50657,"mean_force":223.10946,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5131,0.08123,0.04801]},{"body_a":"world","body_b":"link7","contact_count":700.0,"contact_point_centroid":[0.50929,0.16911,-7e-05],"force_p95":318.70289,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":326.20776,"mean_force":273.05241,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51113,0.10815,0.05523]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":197.0,"contact_point_centroid":[0.52503,0.08016,0.05106],"force_p95":266.25223,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":308.15952,"mean_force":154.43669,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5131,0.07924,0.05102]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":955.0,"contact_point_centroid":[0.52503,0.08234,0.04811],"force_p95":167.88987,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":181.31151,"mean_force":123.26114,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5131,0.08128,0.04792]},{"body_a":"world","body_b":"link7","contact_count":546.0,"contact_point_centroid":[0.50713,0.15421,-2e-05],"force_p95":123.2021,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":180.76006,"mean_force":92.46304,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51207,0.09133,0.05304]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50829,0.16745,-8e-05],"force_p95":45.47214,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":45.47214,"mean_force":45.47214,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51279,0.10581,0.05441]},{"body_a":"peg","body_b":"channel_base_body","contact_count":995.0,"contact_point_centroid":[0.5052,0.05946,0.00946],"force_p95":1.09406,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.60569,"mean_force":0.63769,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51229,0.08645,0.05252]},{"body_a":"attachment","body_b":"peg","contact_count":169.0,"contact_point_centroid":[0.50434,0.07865,0.05841],"force_p95":2.1163,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.55141,"mean_force":0.65326,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51268,0.07936,0.05171]},{"body_a":"peg","body_b":"channel_base_body","contact_count":853.0,"contact_point_centroid":[0.50583,0.06295,0.00937],"force_p95":0.55593,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56243,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50162,0.1567,0.16963]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50335,0.22034,0.28868]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50477,0.06008,0.00938],"force_p95":0.55627,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57042,"mean_force":0.5466,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5131,0.08123,0.04801]},{"body_a":"peg","body_b":"channel_base_body","contact_count":700.0,"contact_point_centroid":[0.50603,0.06299,0.00938],"force_p95":0.55239,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54656,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51113,0.10815,0.05523]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49104,0.05305,0.00939],"force_p95":0.54638,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54638,"mean_force":0.54638,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51279,0.10581,0.05441]}],"total_contact_groups":16},"final_pose_error":0.1935,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50473,0.06003,0.03379],"final_tcp_position":[0.51308,0.08233,0.0455],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":557.96104,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":881.0,"n_steps_budget":1000.0,"object_pos_end":[0.50593,0.06301,0.0338],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14326,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":262.08053,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":921.0,"raw_peak_contact_force":341.54439,"subtask_id":"approach","tcp_end":[0.5095,0.10938,0.05529],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05123,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":700.0,"n_steps_budget":990.0,"object_pos_end":[0.50592,0.06294,0.03383],"object_pos_start":[0.50593,0.06301,0.0338],"object_to_goal_dist_end":0.1432,"object_to_goal_dist_start":0.14326,"object_z_max":0.03383,"peak_contact_force":323.15212,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1400.0,"raw_peak_contact_force":326.20776,"subtask_id":"contact","tcp_end":[0.51279,0.10581,0.05441],"tcp_start":[0.5095,0.10938,0.05529],"tcp_to_object_dist_end":0.04804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50591,0.06298,0.03383],"object_pos_start":[0.50592,0.06294,0.03383],"object_to_goal_dist_end":0.14323,"object_to_goal_dist_start":0.1432,"object_z_max":0.03383,"peak_contact_force":45.47214,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":45.47214,"subtask_id":"contact","tcp_end":[0.51279,0.10581,0.0544],"tcp_start":[0.51279,0.10581,0.05441],"tcp_to_object_dist_end":0.04801,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50473,0.06007,0.03378],"object_pos_start":[0.50591,0.06298,0.03383],"object_to_goal_dist_end":0.14029,"object_to_goal_dist_start":0.14323,"object_z_max":0.03542,"peak_contact_force":474.91589,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2513.0,"raw_peak_contact_force":557.96104,"tcp_end":[0.51314,0.07962,0.05068],"tcp_start":[0.51279,0.10581,0.0544],"tcp_to_object_dist_end":0.02718,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50473,0.06003,0.03379],"object_pos_start":[0.50473,0.06007,0.03378],"object_to_goal_dist_end":0.14025,"object_to_goal_dist_start":0.14029,"object_z_max":0.03379,"peak_contact_force":207.36359,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2955.0,"raw_peak_contact_force":326.50657,"tcp_end":[0.51308,0.08233,0.0455],"tcp_start":[0.51314,0.07962,0.05068],"tcp_to_object_dist_end":0.02654,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.57051,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.01988,"approach_1.speed":0.03343,"contact_1.contact_force":11.07084,"push_1.max_time":6.1299,"push_1.push_distance":0.07294,"push_1.push_speed":0.07547,"retract_1.speed":0.05677},"optimized_scores":{"best_composite_score":-0.05118,"best_fitness_score":0.13882,"best_task_score":4e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":489.0,"contact_point_centroid":[0.47493,0.11989,0.05804],"force_p95":632.48091,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":675.62362,"mean_force":518.26096,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51317,0.08078,0.05085]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":558.0,"contact_point_centroid":[0.52505,0.08218,0.05113],"force_p95":398.36835,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":462.84498,"mean_force":260.35395,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51316,0.08102,0.05104]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":292.0,"contact_point_centroid":[0.525,0.11993,0.06],"force_p95":274.90207,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":458.69768,"mean_force":177.84849,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51261,0.07927,0.05238]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1000.0,"contact_point_centroid":[0.47498,0.11996,0.05999],"force_p95":281.22259,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":415.18488,"mean_force":198.62569,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51316,0.08543,0.04629]},{"body_a":"world","body_b":"link7","contact_count":38.0,"contact_point_centroid":[0.51444,0.1643,-0.00043],"force_p95":335.13772,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":378.55252,"mean_force":264.86357,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51229,0.10284,0.05404]},{"body_a":"world","body_b":"link7","contact_count":487.0,"contact_point_centroid":[0.51081,0.16379,-7e-05],"force_p95":268.46094,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.55313,"mean_force":240.53545,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51294,0.10282,0.05522]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":835.0,"contact_point_centroid":[0.52502,0.0874,0.04627],"force_p95":172.68737,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":288.26455,"mean_force":124.98468,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51317,0.08572,0.04578]},{"body_a":"world","body_b":"link7","contact_count":254.0,"contact_point_centroid":[0.5078,0.1543,-2e-05],"force_p95":158.61538,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":211.51063,"mean_force":103.23907,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51211,0.09182,0.05358]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":340.0,"contact_point_centroid":[0.52501,0.1026,0.05513],"force_p95":120.79676,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":122.72847,"mean_force":81.01858,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51302,0.10251,0.05513]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5087,0.16293,-7e-05],"force_p95":103.77975,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":103.77975,"mean_force":103.77975,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51302,0.10156,0.05476]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,0.10171,0.05475],"force_p95":62.49971,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.49971,"mean_force":62.49971,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51302,0.10156,0.05476]},{"body_a":"peg","body_b":"channel_base_body","contact_count":869.0,"contact_point_centroid":[0.50597,0.0566,0.00936],"force_p95":0.59968,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.56492,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50295,0.15355,0.16933]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5026,0.22245,0.28632]},{"body_a":"peg","body_b":"channel_base_body","contact_count":487.0,"contact_point_centroid":[0.5061,0.05663,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55027,"mean_force":0.54674,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51294,0.10282,0.05522]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50683,0.07451,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55015,"mean_force":0.55015,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.51302,0.10156,0.05476]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50615,0.05659,0.00938],"force_p95":0.55015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55015,"mean_force":0.54674,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51273,0.08359,0.05199]}],"total_contact_groups":17},"final_pose_error":0.19847,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50613,0.05659,0.03378],"final_tcp_position":[0.51315,0.08688,0.04337],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"peak_contact_force":675.62362,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":898.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"peak_contact_force":266.24375,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":944.0,"raw_peak_contact_force":378.55252,"subtask_id":"approach","tcp_end":[0.51214,0.10368,0.05547],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":487.0,"n_steps_budget":690.0,"object_pos_end":[0.50613,0.05663,0.03378],"object_pos_start":[0.50611,0.05662,0.03378],"object_to_goal_dist_end":0.13691,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":240.85643,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1314.0,"raw_peak_contact_force":288.55313,"subtask_id":"contact","tcp_end":[0.51302,0.10156,0.05476],"tcp_start":[0.51214,0.10368,0.05547],"tcp_to_object_dist_end":0.05006,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50615,0.05663,0.03378],"object_pos_start":[0.50613,0.05663,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.13691,"object_z_max":0.03378,"peak_contact_force":103.77975,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":103.77975,"subtask_id":"contact","tcp_end":[0.51301,0.10156,0.05475],"tcp_start":[0.51302,0.10156,0.05476],"tcp_to_object_dist_end":0.05007,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50611,0.05662,0.03378],"object_pos_start":[0.50615,0.05663,0.03378],"object_to_goal_dist_end":0.1369,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":616.95923,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2593.0,"raw_peak_contact_force":675.62362,"tcp_end":[0.5133,0.08314,0.04987],"tcp_start":[0.51301,0.10156,0.05475],"tcp_to_object_dist_end":0.03184,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50613,0.05659,0.03378],"object_pos_start":[0.50611,0.05662,0.03378],"object_to_goal_dist_end":0.13687,"object_to_goal_dist_start":0.1369,"object_z_max":0.03378,"peak_contact_force":177.93721,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2835.0,"raw_peak_contact_force":415.18488,"tcp_end":[0.51315,0.08688,0.04337],"tcp_start":[0.5133,0.08314,0.04987],"tcp_to_object_dist_end":0.03253,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":152.0,"average_success_count":152.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.01696,"approach_1.speed":0.0648,"contact_1.contact_force":11.72386,"push_1.max_time":3.80588,"push_1.push_distance":0.09016,"push_1.push_speed":0.05957,"retract_1.speed":0.06356},"optimized_scores":{"best_composite_score":-0.03714,"best_fitness_score":0.15286,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":190.0,"contact_point_centroid":[0.47974,0.30857,-3e-05],"force_p95":435.48039,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":614.98713,"mean_force":323.28461,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46945,0.12135,0.05953]},{"body_a":"world","body_b":"link7","contact_count":468.0,"contact_point_centroid":[0.46631,0.18056,-8e-05],"force_p95":382.42761,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":486.66623,"mean_force":265.22778,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46362,0.1227,0.05851]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":60.0,"contact_point_centroid":[0.46902,0.11998,0.04748],"force_p95":278.02078,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":285.32055,"mean_force":120.59711,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46699,0.12109,0.05924]},{"body_a":"world","body_b":"link7","contact_count":30.0,"contact_point_centroid":[0.45551,0.1855,-0.00044],"force_p95":258.74392,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.82921,"mean_force":253.36674,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4534,0.1239,0.05388]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":993.0,"contact_point_centroid":[0.46165,0.11993,0.05754],"force_p95":205.57585,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":226.16222,"mean_force":183.10634,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47224,0.12103,0.05597]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":999.0,"contact_point_centroid":[0.46273,0.11995,0.05921],"force_p95":176.41836,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":176.76859,"mean_force":165.2883,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47309,0.12265,0.0541]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.48492,0.30875,-2e-05],"force_p95":101.03747,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":101.03747,"mean_force":101.03747,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47367,0.12164,0.05971]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47684,0.17838,-1e-05],"force_p95":83.84351,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":83.84351,"mean_force":83.84351,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47367,0.12164,0.05971]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47682,0.17836,-2e-05],"force_p95":66.38571,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":66.38571,"mean_force":66.38571,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47366,0.12162,0.05971]},{"body_a":"world","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.48491,0.30874,-2e-05],"force_p95":19.68432,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":19.68432,"mean_force":19.68432,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47366,0.12162,0.05971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":819.0,"contact_point_centroid":[0.49401,0.07996,0.00937],"force_p95":0.58457,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.56213,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47369,0.16419,0.1686]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50288,0.22107,0.28779]},{"body_a":"peg","body_b":"channel_base_body","contact_count":484.0,"contact_point_centroid":[0.49374,0.07991,0.00938],"force_p95":0.58257,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64669,"mean_force":0.54626,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46362,0.12271,0.05851]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.4938,0.07998,0.00938],"force_p95":0.57742,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58598,"mean_force":0.54661,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47224,0.12103,0.05599]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51164,0.07789,0.00938],"force_p95":0.57468,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57468,"mean_force":0.57468,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47366,0.12162,0.05971]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49383,0.07994,0.00938],"force_p95":0.55278,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55316,"mean_force":0.54673,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47309,0.12265,0.0541]}],"total_contact_groups":16},"final_pose_error":0.22654,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49379,0.07997,0.03378],"final_tcp_position":[0.47438,0.12323,0.05325],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"peak_contact_force":614.98713,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,0.07993,0.03378],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16017,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"peak_contact_force":247.96627,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":884.0,"raw_peak_contact_force":258.82921,"subtask_id":"approach","tcp_end":[0.45318,0.12443,0.05486],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.49383,0.07995,0.03377],"object_pos_start":[0.49382,0.07993,0.03378],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16017,"object_z_max":0.03384,"peak_contact_force":406.09682,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1202.0,"raw_peak_contact_force":614.98713,"subtask_id":"contact","tcp_end":[0.47366,0.12162,0.05971],"tcp_start":[0.45318,0.12443,0.05486],"tcp_to_object_dist_end":0.05307,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49384,0.07996,0.03377],"object_pos_start":[0.49383,0.07995,0.03377],"object_to_goal_dist_end":0.1602,"object_to_goal_dist_start":0.16019,"object_z_max":0.03377,"peak_contact_force":66.38571,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3.0,"raw_peak_contact_force":66.38571,"subtask_id":"contact","tcp_end":[0.47367,0.12164,0.05971],"tcp_start":[0.47366,0.12162,0.05971],"tcp_to_object_dist_end":0.05307,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49382,0.07997,0.03378],"object_pos_start":[0.49384,0.07996,0.03377],"object_to_goal_dist_end":0.16021,"object_to_goal_dist_start":0.1602,"object_z_max":0.03378,"peak_contact_force":203.80359,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1995.0,"raw_peak_contact_force":226.16222,"tcp_end":[0.47248,0.12217,0.05472],"tcp_start":[0.47367,0.12164,0.05971],"tcp_to_object_dist_end":0.05172,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49379,0.07997,0.03378],"object_pos_start":[0.49382,0.07997,0.03378],"object_to_goal_dist_end":0.16021,"object_to_goal_dist_start":0.16021,"object_z_max":0.03378,"peak_contact_force":175.02501,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1999.0,"raw_peak_contact_force":176.76859,"tcp_end":[0.47438,0.12323,0.05325],"tcp_start":[0.47248,0.12217,0.05472],"tcp_to_object_dist_end":0.05125,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```