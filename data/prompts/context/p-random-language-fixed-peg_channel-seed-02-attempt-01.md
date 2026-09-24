## Search State

- **Seed**: 2
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 1 | 0.0778 | 0.02 | ❌ rejected |
| 0 | align → align → pull | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.1029 | 0.13 | ✅ accepted |

**Proposal policy**: task_score is 0.02 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.078) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
- id: pull_1
  type: pull
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.078
- **task_score** (E): 0.015
- **fitness_score**: 0.158  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.080

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.2533 |
| contact | 1.00 | 1.00 | 0.0158 |
| push | 0.00 | 1.00 | 0.0166 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.115, 0.063) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.667 | 132.981 | 172.392 |
| contact | align | 1.00 / step_budget | (0.495, 0.115, 0.063)→(0.500, 0.104, 0.057) | (0.498, 0.068, 0.034)→(0.499, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.667 | 275.171 | 313.654 |
| push | pull | 0.00 / step_budget | (0.500, 0.104, 0.057)→(0.507, 0.099, 0.049) | (0.499, 0.068, 0.034)→(0.499, 0.064, 0.034) | 0.148→0.144 | 1.00 / 2.667 | 261.274 | 538.253 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.079
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.046
- phase_score: 0.264
- phase_breakdown.push_score: 0.032
- phase_breakdown.contact_score: 0.551
- phase_breakdown.approach_score: 0.672

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.177
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.046
- **Median Q (composite search score)**: 0.078
- **K-run variance**: 0.0002
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.778


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86441,"average_solve_count":118.0,"average_success_count":118.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push.push_depth":0.03933},"optimized_scores":{"best_composite_score":0.0966,"best_fitness_score":0.1766,"best_task_score":0.04564},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":916.0,"contact_point_centroid":[0.46019,0.1199,0.05753],"force_p95":288.19703,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":477.94416,"mean_force":240.76917,"phase_index":2.0,"phase_name":"push","phase_type":"pull","tcp_position_centroid":[0.49628,0.08554,0.05276]},{"body_a":"world","body_b":"link7","contact_count":248.0,"contact_point_centroid":[0.48539,0.1657,-0.00014],"force_p95":365.48,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":377.93156,"mean_force":338.22749,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.48821,0.10571,0.05611]},{"body_a":"world","body_b":"link7","contact_count":386.0,"contact_point_centroid":[0.4816,0.15001,-6e-05],"force_p95":300.36028,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":373.25579,"mean_force":222.46743,"phase_index":2.0,"phase_name":"push","phase_type":"pull","tcp_position_centroid":[0.49942,0.08958,0.0528]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":50.0,"contact_point_centroid":[0.47479,0.12,0.05969],"force_p95":214.76172,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":233.19896,"mean_force":167.80377,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48408,0.11206,0.06605]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47499,0.12,0.05771],"force_p95":169.66848,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":174.18849,"mean_force":101.05894,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.48717,0.10766,0.05804]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49476,0.08119,0.04496],"force_p95":25.77089,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.42697,"mean_force":6.14671,"phase_index":2.0,"phase_name":"push","phase_type":"pull","tcp_position_centroid":[0.49042,0.08097,0.05439]},{"body_a":"peg","body_b":"channel_base_body","contact_count":986.0,"contact_point_centroid":[0.49679,0.05276,0.00946],"force_p95":0.61907,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.34669,"mean_force":0.59834,"phase_index":2.0,"phase_name":"push","phase_type":"pull","tcp_position_centroid":[0.4958,0.08631,0.05299]},{"body_a":"peg","body_b":"channel_base_body","contact_count":530.0,"contact_point_centroid":[0.49532,0.06386,0.00937],"force_p95":0.5849,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56158,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48558,0.15856,0.16567]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50409,0.21532,0.29281]},{"body_a":"peg","body_b":"channel_base_body","contact_count":264.0,"contact_point_centroid":[0.49514,0.06374,0.0094],"force_p95":0.55066,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54551,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.48816,0.10579,0.05617]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":12.0,"contact_point_centroid":[0.47476,0.0527,0.05867],"force_p95":0.2426,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28516,"mean_force":0.07085,"phase_index":2.0,"phase_name":"push","phase_type":"pull","tcp_position_centroid":[0.49148,0.08107,0.05313]}],"total_contact_groups":11},"final_pose_error":0.2112,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49684,0.05128,0.0344],"final_tcp_position":[0.50468,0.09143,0.05276],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":477.94416,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":557.0,"n_steps_budget":1000.0,"object_pos_end":[0.49518,0.06369,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.1439,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":119.40282,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":608.0,"raw_peak_contact_force":233.19896,"subtask_id":"approach","tcp_end":[0.48713,0.10788,0.05846],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05118,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":264.0,"n_steps_budget":600.0,"object_pos_end":[0.49531,0.06373,0.03399],"object_pos_start":[0.49518,0.06369,0.03394],"object_to_goal_dist_end":0.14393,"object_to_goal_dist_start":0.1439,"object_z_max":0.03399,"peak_contact_force":351.29776,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":515.0,"raw_peak_contact_force":377.93156,"subtask_id":"contact","tcp_end":[0.48916,0.10636,0.0577],"tcp_start":[0.48713,0.10788,0.05846],"tcp_to_object_dist_end":0.04917,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49684,0.05128,0.0344],"object_pos_start":[0.49531,0.06373,0.03399],"object_to_goal_dist_end":0.13144,"object_to_goal_dist_start":0.14393,"object_z_max":0.03653,"peak_contact_force":289.58978,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":2309.0,"raw_peak_contact_force":477.94416,"subtask_id":"push","tcp_end":[0.50468,0.09143,0.05276],"tcp_start":[0.48916,0.10636,0.0577],"tcp_to_object_dist_end":0.04484,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89655,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push.push_depth":0.0141},"optimized_scores":{"best_composite_score":0.05842,"best_fitness_score":0.13842,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":956.0,"contact_point_centroid":[0.45953,0.11991,0.05829],"force_p95":454.42401,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":789.79133,"mean_force":283.98189,"phase_index":2.0,"phase_name":"push","phase_type":"pull","tcp_position_centroid":[0.49214,0.08481,0.04785]},{"body_a":"world","body_b":"link7","contact_count":418.0,"contact_point_centroid":[0.48449,0.1526,-5e-05],"force_p95":531.33913,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":751.74675,"mean_force":236.03403,"phase_index":2.0,"phase_name":"push","phase_type":"pull","tcp_position_centroid":[0.49508,0.08766,0.04264]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":261.0,"contact_point_centroid":[0.47497,0.12,0.05345],"force_p95":358.04601,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":446.80516,"mean_force":121.27382,"phase_index":2.0,"phase_name":"push","phase_type":"pull","tcp_position_centroid":[0.4905,0.08351,0.04994]},{"body_a":"world","body_b":"link7","contact_count":96.0,"contact_point_centroid":[0.48469,0.14341,-0.00028],"force_p95":308.68607,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.72737,"mean_force":265.11316,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.48716,0.08574,0.0583]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":90.0,"contact_point_centroid":[0.46864,0.11999,0.05966],"force_p95":279.52789,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":279.65064,"mean_force":257.55675,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.46864,0.11106,0.07178]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":288.0,"contact_point_centroid":[0.47329,0.11942,0.05993],"force_p95":227.98272,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":262.9022,"mean_force":198.46535,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.47517,0.10093,0.07286]},{"body_a":"world","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.49791,0.27366,-6e-05],"force_p95":108.73303,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":111.19702,"mean_force":80.60424,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.48724,0.0865,0.05958]},{"body_a":"world","body_b":"link6","contact_count":2.0,"contact_point_centroid":[0.49799,0.27368,-5e-05],"force_p95":83.85362,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":86.89514,"mean_force":56.47991,"phase_index":2.0,"phase_name":"push","phase_type":"pull","tcp_position_centroid":[0.48734,0.08651,0.0596]},{"body_a":"peg","body_b":"channel_base_body","contact_count":557.0,"contact_point_centroid":[0.49434,0.05888,0.00935],"force_p95":0.56733,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57247,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.47817,0.15424,0.16162]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50251,0.22069,0.28708]},{"body_a":"peg","body_b":"channel_base_body","contact_count":975.0,"contact_point_centroid":[0.49419,0.05892,0.0094],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.54532,"phase_index":2.0,"phase_name":"push","phase_type":"pull","tcp_position_centroid":[0.49207,0.08481,0.04802]},{"body_a":"peg","body_b":"channel_base_body","contact_count":426.0,"contact_point_centroid":[0.49406,0.05897,0.00939],"force_p95":0.55014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54597,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.47827,0.09698,0.06927]}],"total_contact_groups":12},"final_pose_error":0.18393,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4944,0.0591,0.03404],"final_tcp_position":[0.49898,0.08983,0.03992],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":789.79133,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.49425,0.05894,0.03387],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":278.994,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":682.0,"raw_peak_contact_force":279.65064,"subtask_id":"approach","tcp_end":[0.46868,0.11118,0.07269],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06993,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":426.0,"n_steps_budget":600.0,"object_pos_end":[0.49427,0.05884,0.03393],"object_pos_start":[0.49425,0.05894,0.03387],"object_to_goal_dist_end":0.13909,"object_to_goal_dist_start":0.13919,"object_z_max":0.03393,"peak_contact_force":251.81018,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":821.0,"raw_peak_contact_force":334.72737,"subtask_id":"contact","tcp_end":[0.48736,0.08656,0.05957],"tcp_start":[0.46868,0.11118,0.07269],"tcp_to_object_dist_end":0.03838,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":975.0,"n_steps_budget":1000.0,"object_pos_end":[0.4944,0.0591,0.03404],"object_pos_start":[0.49427,0.05884,0.03393],"object_to_goal_dist_end":0.13934,"object_to_goal_dist_start":0.13909,"object_z_max":0.03404,"peak_contact_force":279.49066,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":2612.0,"raw_peak_contact_force":789.79133,"subtask_id":"push","tcp_end":[0.49898,0.08983,0.03992],"tcp_start":[0.48736,0.08656,0.05957],"tcp_to_object_dist_end":0.03162,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.85217,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push.push_depth":0.07137},"optimized_scores":{"best_composite_score":0.07834,"best_fitness_score":0.15834,"best_task_score":7e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":351.0,"contact_point_centroid":[0.49684,0.17551,-2e-05],"force_p95":136.0315,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":347.02306,"mean_force":105.42512,"phase_index":2.0,"phase_name":"push","phase_type":"pull","tcp_position_centroid":[0.51926,0.11782,0.05431]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":997.0,"contact_point_centroid":[0.52502,0.1199,0.05057],"force_p95":206.76527,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":236.98362,"mean_force":190.30429,"phase_index":2.0,"phase_name":"push","phase_type":"pull","tcp_position_centroid":[0.51984,0.11854,0.05387]},{"body_a":"world","body_b":"link7","contact_count":281.0,"contact_point_centroid":[0.52056,0.1839,-0.00012],"force_p95":225.56511,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":228.30395,"mean_force":191.68258,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.52321,0.1209,0.05278]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":102.0,"contact_point_centroid":[0.525,0.11995,0.06],"force_p95":143.34238,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":158.88998,"mean_force":116.9093,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.52221,0.11997,0.05254]},{"body_a":"peg","body_b":"channel_base_body","contact_count":494.0,"contact_point_centroid":[0.50571,0.0809,0.00936],"force_p95":0.56027,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57765,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50873,0.16953,0.17385]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50315,0.22162,0.2867]},{"body_a":"peg","body_b":"channel_base_body","contact_count":295.0,"contact_point_centroid":[0.50598,0.08081,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55008,"mean_force":0.54677,"phase_index":1.0,"phase_name":"contact","phase_type":"align","tcp_position_centroid":[0.52343,0.1211,0.05293]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50596,0.0809,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":2.0,"phase_name":"push","phase_type":"pull","tcp_position_centroid":[0.51985,0.11854,0.05387]}],"total_contact_groups":8},"final_pose_error":0.26956,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50598,0.08087,0.03378],"final_tcp_position":[0.51881,0.11716,0.05422],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":347.02306,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.5461,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":530.0,"raw_peak_contact_force":4.32595,"subtask_id":"approach","tcp_end":[0.52944,0.12651,0.05798],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05674,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":295.0,"n_steps_budget":600.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":222.40584,"phase_name":"contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":678.0,"raw_peak_contact_force":228.30395,"subtask_id":"contact","tcp_end":[0.52204,0.11992,0.05257],"tcp_start":[0.52944,0.12651,0.05798],"tcp_to_object_dist_end":0.04623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.08087,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"peak_contact_force":214.74229,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"pull","raw_contact_event_count":2348.0,"raw_peak_contact_force":347.02306,"subtask_id":"push","tcp_end":[0.51881,0.11716,0.05422],"tcp_start":[0.52204,0.11992,0.05257],"tcp_to_object_dist_end":0.04359,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```