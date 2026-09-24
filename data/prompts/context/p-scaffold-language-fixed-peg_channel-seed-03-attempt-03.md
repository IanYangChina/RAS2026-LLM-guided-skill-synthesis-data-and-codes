## Search State

- **Seed**: 3
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1016 | 0.21 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.1392 | 0.28 | ✅ accepted |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1455 | 0.00 | ❌ rejected |
| 0 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0963 | 0.18 | ✅ accepted |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, 0.058944840527687975, 0.04]
- Frozen task target: [0.46685193337148995, -0.10105515947231203, 0.04]
- Goal object position: (0.46685193337148995, -0.10105515947231203, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, 0.058944840527687975, 0.04)
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
  frozen_object_start: [0.4669, 0.0589, 0.04]
  frozen_task_target: [0.4669, -0.1011, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.46685193337148995, 0.058944840527687975, 0.04]}
  frozen_targets: {'channel_exit': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

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

## Current Skill (Q=0.102) — your mutation base

```yaml
skill: peg_channel
phases:
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
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
  generator: impedance_motion
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
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
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

- **Composite score**: 0.102
- **task_score** (E): 0.210
- **fitness_score**: 0.292  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2555 |
| approach_1 | 1.00 | 1.00 | 0.0121 |
| contact_1 | 1.00 | 1.00 | 0.0052 |
| push_1 | 0.67 | 1.00 | 0.0901 |
| retract_1 | 0.00 | 1.00 | 0.1008 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.508, 0.127, 0.057) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.667 | 214.537 | 260.773 |
| approach_1 | approach | 1.00 / step_budget | (0.508, 0.127, 0.057)→(0.510, 0.126, 0.047) | (0.502, 0.082, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 1.333 | 72.809 | 185.216 |
| contact_1 | contact | 1.00 / force_exceeded | (0.510, 0.126, 0.047)→(0.507, 0.123, 0.044) | (0.502, 0.081, 0.034)→(0.502, 0.081, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 40.073 | 40.073 |
| push_1 | push | 0.67 / step_budget | (0.507, 0.123, 0.044)→(0.505, 0.033, 0.046) | (0.502, 0.081, 0.034)→(0.506, 0.004, 0.037) | 0.162→0.084 | 1.00 / 2.333 | 106.636 | 195.619 |
| retract_1 | retract | 0.00 / step_budget | (0.505, 0.033, 0.046)→(0.499, 0.018, 0.143) | (0.506, 0.004, 0.037)→(0.503, -0.002, 0.032) | 0.084→0.080 | 1.00 / 1.667 | 0.478 | 81.823 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.748
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.392
- phase_score: 0.375
- phase_breakdown.approach_score: 0.794
- phase_breakdown.contact_score: 0.641
- phase_breakdown.push_score: 0.148

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.382
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.392
- **Median Q (composite search score)**: 0.165
- **K-run variance**: 0.0119
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.454


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `cc7283febf3c95cef1fde4c5a16cbcb134186cb6faf3a169717a9aa53375931d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `178d67757a065da6e29d31070e25f6065dc7e42bdbf58dfbff0deec513214033`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43827,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00023,"approach_1.approach_height":0.20285,"approach_1.speed":0.05359,"contact_1.contact_force":9.26067,"push_1.push_depth":0.09606,"retract_1.speed":0.04447},"optimized_scores":{"best_composite_score":0.16469,"best_fitness_score":0.35469,"best_task_score":0.23883},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":106.0,"contact_point_centroid":[0.47492,0.11854,0.05985],"force_p95":346.92903,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.37637,"mean_force":313.68239,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47019,0.10819,0.06243]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":122.0,"contact_point_centroid":[0.47498,0.11482,0.05979],"force_p95":302.50296,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":333.35946,"mean_force":243.23909,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48151,0.10684,0.05662]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":479.0,"contact_point_centroid":[0.53601,0.0487,0.05999],"force_p95":108.55542,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":124.81966,"mean_force":91.26264,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49061,0.05021,0.03784]},{"body_a":"attachment","body_b":"peg","contact_count":563.0,"contact_point_centroid":[0.49987,0.01726,0.03684],"force_p95":86.28451,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.325,"mean_force":49.15426,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49274,0.02582,0.03779]},{"body_a":"peg","body_b":"channel_base_body","contact_count":743.0,"contact_point_centroid":[0.50508,0.00702,0.00968],"force_p95":58.47548,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.38422,"mean_force":23.21752,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49147,0.0403,0.03782]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":566.0,"contact_point_centroid":[0.52554,0.00498,0.025],"force_p95":51.21737,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.59351,"mean_force":31.66401,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49281,0.02513,0.0378]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54164,-0.02724,0.05999],"force_p95":47.88313,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":48.25788,"mean_force":44.51031,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49678,-0.02163,0.03732]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53144,0.10131,0.05999],"force_p95":35.96293,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":35.96293,"mean_force":35.96293,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48599,0.10003,0.03786]},{"body_a":"peg","body_b":"channel_base_body","contact_count":974.0,"contact_point_centroid":[0.50208,-0.05152,0.00998],"force_p95":0.5818,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.08926,"mean_force":0.47778,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49385,-0.01724,0.08475]},{"body_a":"attachment","body_b":"peg","contact_count":29.0,"contact_point_centroid":[0.50198,-0.03078,0.03564],"force_p95":8.86099,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.8373,"mean_force":1.61846,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49594,-0.02163,0.03826]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":9.0,"contact_point_centroid":[0.52524,-0.03967,0.02137],"force_p95":5.21933,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.62924,"mean_force":1.90798,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49665,-0.02171,0.03741]},{"body_a":"peg","body_b":"channel_base_body","contact_count":854.0,"contact_point_centroid":[0.49433,0.05892,0.00937],"force_p95":0.55492,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56328,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48064,0.14718,0.16216]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49899,0.19829,0.29587]},{"body_a":"peg","body_b":"channel_base_body","contact_count":861.0,"contact_point_centroid":[0.50494,-0.10002,0.02588],"force_p95":0.35189,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38688,"mean_force":0.25897,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49376,-0.01698,0.08763]},{"body_a":"peg","body_b":"channel_base_body","contact_count":20.0,"contact_point_centroid":[0.49418,0.05911,0.0094],"force_p95":0.55094,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5514,"mean_force":0.54597,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4864,0.10097,0.03884]},{"body_a":"peg","body_b":"channel_base_body","contact_count":186.0,"contact_point_centroid":[0.4936,0.05918,0.00939],"force_p95":0.54984,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55091,"mean_force":0.54582,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4826,0.10607,0.05403]}],"total_contact_groups":17},"final_pose_error":0.1683,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49656,-0.07251,0.02895],"final_tcp_position":[0.49461,-0.01332,0.13231],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":355.37637,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.0591,0.03391],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13935,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":328.62809,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":995.0,"raw_peak_contact_force":355.37637,"tcp_end":[0.4745,0.10691,0.06026],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":186.0,"n_steps_budget":600.0,"object_pos_end":[0.49413,0.05876,0.03394],"object_pos_start":[0.49422,0.0591,0.03391],"object_to_goal_dist_end":0.13902,"object_to_goal_dist_start":0.13935,"object_z_max":0.03394,"peak_contact_force":0.54072,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":308.0,"raw_peak_contact_force":333.35946,"tcp_end":[0.48701,0.1018,0.04003],"tcp_start":[0.4745,0.10691,0.06026],"tcp_to_object_dist_end":0.04405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":20.0,"n_steps_budget":600.0,"object_pos_end":[0.49412,0.05876,0.03394],"object_pos_start":[0.49413,0.05876,0.03394],"object_to_goal_dist_end":0.13901,"object_to_goal_dist_start":0.13902,"object_z_max":0.03394,"peak_contact_force":35.96293,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":21.0,"raw_peak_contact_force":35.96293,"tcp_end":[0.48597,0.09994,0.03778],"tcp_start":[0.48701,0.1018,0.04003],"tcp_to_object_dist_end":0.04216,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":783.0,"n_steps_budget":870.0,"object_pos_end":[0.50774,-0.05571,0.04001],"object_pos_start":[0.49412,0.05876,0.03394],"object_to_goal_dist_end":0.02549,"object_to_goal_dist_start":0.13901,"object_z_max":0.04039,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2351.0,"raw_peak_contact_force":124.81966,"tcp_end":[0.49679,-0.0215,0.03734],"tcp_start":[0.48597,0.09994,0.03778],"tcp_to_object_dist_end":0.03602,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49656,-0.07251,0.02895],"object_pos_start":[0.50774,-0.05571,0.04001],"object_to_goal_dist_end":0.01378,"object_to_goal_dist_start":0.02549,"object_z_max":0.04076,"peak_contact_force":0.33836,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2190.0,"raw_peak_contact_force":48.25788,"tcp_end":[0.49461,-0.01332,0.13231],"tcp_start":[0.49679,-0.0215,0.03734],"tcp_to_object_dist_end":0.11912,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64189,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00388,"approach_1.approach_height":0.10688,"approach_1.speed":0.08481,"contact_1.contact_force":4.396,"push_1.push_depth":0.09979,"retract_1.speed":0.0648},"optimized_scores":{"best_composite_score":-0.05192,"best_fitness_score":0.13808,"best_task_score":4e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":95.0,"contact_point_centroid":[0.53608,0.11993,0.0598],"force_p95":364.62154,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.61103,"mean_force":316.10752,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5286,0.12877,0.06252]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":859.0,"contact_point_centroid":[0.53263,0.11166,0.05993],"force_p95":261.81662,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":270.95287,"mean_force":223.68214,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52227,0.11396,0.06412]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":455.0,"contact_point_centroid":[0.53556,0.11997,0.05996],"force_p95":220.3564,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":221.71329,"mean_force":197.86905,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52958,0.13002,0.06235]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.53052,0.10475,0.05996],"force_p95":89.78576,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":94.23431,"mean_force":64.51879,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51946,0.10618,0.06437]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53369,0.11997,0.05996],"force_p95":64.53005,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.53005,"mean_force":64.53005,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52924,0.13093,0.06172]},{"body_a":"peg","body_b":"channel_base_body","contact_count":845.0,"contact_point_centroid":[0.50578,0.08087,0.00937],"force_p95":0.55112,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56482,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5151,0.15903,0.16341]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49991,0.19854,0.29567]},{"body_a":"peg","body_b":"channel_base_body","contact_count":455.0,"contact_point_centroid":[0.50601,0.08085,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52958,0.13002,0.06235]},{"body_a":"peg","body_b":"channel_base_body","contact_count":873.0,"contact_point_centroid":[0.50601,0.08089,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52232,0.11408,0.06411]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50594,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51167,0.08128,0.11361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49001,0.08914,0.00938],"force_p95":0.54527,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54527,"mean_force":0.54527,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52924,0.13093,0.06172]}],"total_contact_groups":11},"final_pose_error":0.14836,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50597,0.08088,0.03378],"final_tcp_position":[0.50773,0.05866,0.16395],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":423.61103,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":314.43154,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":976.0,"raw_peak_contact_force":423.61103,"tcp_end":[0.5292,0.12912,0.06281],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0609,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":455.0,"n_steps_budget":600.0,"object_pos_end":[0.50595,0.08088,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":217.33618,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":910.0,"raw_peak_contact_force":221.71329,"tcp_end":[0.52924,0.13093,0.06172],"tcp_start":[0.5292,0.12912,0.06281],"tcp_to_object_dist_end":0.06186,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50597,0.08089,0.03378],"object_pos_start":[0.50595,0.08088,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16111,"object_z_max":0.03378,"peak_contact_force":64.53005,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2.0,"raw_peak_contact_force":64.53005,"tcp_end":[0.52924,0.13093,0.06172],"tcp_start":[0.52924,0.13093,0.06172],"tcp_to_object_dist_end":0.06185,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":873.0,"n_steps_budget":960.0,"object_pos_end":[0.50596,0.08085,0.03378],"object_pos_start":[0.50597,0.08089,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":262.08136,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1732.0,"raw_peak_contact_force":270.95287,"tcp_end":[0.51947,0.10617,0.06435],"tcp_start":[0.52924,0.13093,0.06172],"tcp_to_object_dist_end":0.04192,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08088,0.03378],"object_pos_start":[0.50596,0.08085,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":0.55006,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":94.23431,"tcp_end":[0.50773,0.05866,0.16395],"tcp_start":[0.51947,0.10617,0.06435],"tcp_to_object_dist_end":0.13207,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.31847,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":-0.00606,"approach_1.approach_height":0.16014,"approach_1.speed":0.038,"contact_1.contact_force":4.81208,"push_1.push_depth":0.09983,"retract_1.speed":0.05229},"optimized_scores":{"best_composite_score":0.1919,"best_fitness_score":0.3819,"best_task_score":0.39156},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":514.0,"contact_point_centroid":[0.54701,0.08361,0.05999],"force_p95":159.52838,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":191.08539,"mean_force":89.69013,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50164,0.08696,0.03592]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":253.0,"contact_point_centroid":[0.52503,0.10561,0.05999],"force_p95":158.9398,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":176.60862,"mean_force":99.80752,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5019,0.10801,0.03568]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54333,0.01191,0.05999],"force_p95":97.09625,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":102.9776,"mean_force":59.66064,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49839,0.01547,0.03708]},{"body_a":"attachment","body_b":"peg","contact_count":298.0,"contact_point_centroid":[0.49959,0.06887,0.03716],"force_p95":9.89809,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.40205,"mean_force":2.33621,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50121,0.08044,0.03616]},{"body_a":"peg","body_b":"channel_base_body","contact_count":590.0,"contact_point_centroid":[0.49785,0.04679,0.00966],"force_p95":6.58,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.8449,"mean_force":1.53393,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50163,0.08554,0.03594]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.555,0.12,0.05997],"force_p95":19.72551,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":19.72551,"mean_force":19.72551,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50687,0.13688,0.03376]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":238.0,"contact_point_centroid":[0.47484,0.04266,0.03],"force_p95":2.73686,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.46783,"mean_force":0.94954,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50068,0.0718,0.03649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":769.0,"contact_point_centroid":[0.50575,0.10463,0.00938],"force_p95":0.57576,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.56104,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50896,0.17221,0.16946]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52516,-0.0139,0.05923],"force_p95":2.93445,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.97488,"mean_force":2.3201,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49849,0.0167,0.03707]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49979,0.19895,0.29625]},{"body_a":"peg","body_b":"channel_base_body","contact_count":989.0,"contact_point_centroid":[0.50585,-0.01552,0.00941],"force_p95":0.59302,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.22385,"mean_force":0.54887,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49513,0.01226,0.08528]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.5253,-0.01502,0.02169],"force_p95":0.75644,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.83087,"mean_force":0.35512,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49684,0.01488,0.0395]},{"body_a":"peg","body_b":"channel_base_body","contact_count":34.0,"contact_point_centroid":[0.50415,0.10564,0.00939],"force_p95":0.57572,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57583,"mean_force":0.54683,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51648,0.14571,0.04478]},{"body_a":"peg","body_b":"channel_base_body","contact_count":80.0,"contact_point_centroid":[0.50632,0.10475,0.00939],"force_p95":0.57569,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57579,"mean_force":0.54613,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50931,0.1411,0.03655]},{"body_a":"attachment","body_b":"peg","contact_count":22.0,"contact_point_centroid":[0.50425,0.00298,0.05714],"force_p95":0.37651,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.52913,"mean_force":0.12136,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49582,0.01477,0.04296]}],"total_contact_groups":15},"final_pose_error":0.16728,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50645,-0.01508,0.03381],"final_tcp_position":[0.49562,0.00948,0.13305],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":191.08539,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":796.0,"n_steps_budget":1000.0,"object_pos_end":[0.50587,0.10457,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.55165,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":801.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.51917,0.14645,0.04815],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04622,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":34.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.10468,0.03384],"object_pos_start":[0.50587,0.10457,0.03384],"object_to_goal_dist_end":0.18488,"object_to_goal_dist_start":0.18476,"object_z_max":0.03384,"peak_contact_force":0.54964,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":34.0,"raw_peak_contact_force":0.57583,"tcp_end":[0.51288,0.14511,0.04069],"tcp_start":[0.51917,0.14645,0.04815],"tcp_to_object_dist_end":0.04158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":80.0,"n_steps_budget":600.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.50599,0.10468,0.03384],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18488,"object_z_max":0.03384,"peak_contact_force":19.72551,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":81.0,"raw_peak_contact_force":19.72551,"tcp_end":[0.50684,0.1368,0.03372],"tcp_start":[0.51288,0.14511,0.04069],"tcp_to_object_dist_end":0.03221,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":753.0,"n_steps_budget":840.0,"object_pos_end":[0.5054,-0.01348,0.0367],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.06682,"object_to_goal_dist_start":0.1848,"object_z_max":0.03744,"peak_contact_force":57.82589,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1900.0,"raw_peak_contact_force":191.08539,"tcp_end":[0.4984,0.01559,0.03709],"tcp_start":[0.50684,0.1368,0.03372],"tcp_to_object_dist_end":0.02991,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50645,-0.01508,0.03381],"object_pos_start":[0.5054,-0.01348,0.0367],"object_to_goal_dist_end":0.06553,"object_to_goal_dist_start":0.06682,"object_z_max":0.03671,"peak_contact_force":0.54422,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1051.0,"raw_peak_contact_force":102.9776,"tcp_end":[0.49562,0.00948,0.13305],"tcp_start":[0.4984,0.01559,0.03709],"tcp_to_object_dist_end":0.1028,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```