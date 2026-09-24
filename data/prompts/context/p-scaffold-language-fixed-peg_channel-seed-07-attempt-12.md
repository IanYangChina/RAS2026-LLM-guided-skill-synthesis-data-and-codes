## Search State

- **Seed**: 7
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.0636 | 0.12 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | 0.3569 | 0.52 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | -0.0909 | 0.00 | ❌ rejected |
| 9 | align → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 6 | 0.3410 | 0.62 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0625 | 0.27 | ❌ rejected |

**Proposal policy**: task_score is 0.12 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`
- Frozen object start: [0.5100076373283734, 0.11177710407756605, 0.04]
- Frozen task target: [0.5100076373283734, -0.04822289592243395, 0.04]
- Goal object position: (0.5100076373283734, -0.04822289592243395, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5100076373283734, 0.11177710407756605, 0.04)
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
  frozen_object_start: [0.51, 0.1118, 0.04]
  frozen_task_target: [0.51, -0.0482, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5100076373283734, 0.11177710407756605, 0.04]}
  frozen_targets: {'channel_exit': [0.5100076373283734, -0.04822289592243395, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415

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

## Current Skill (Q=0.064) — your mutation base

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
  control: admittance_control
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
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

- **Composite score**: 0.064
- **task_score** (E): 0.117
- **fitness_score**: 0.374  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2145 |
| contact_peg | 0.00 | 1.00 | 0.0591 |
| push_through_channel | 1.00 | 1.00 | 0.1892 |
| retract_from_channel | 1.00 | 1.00 | 0.1100 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.505, 0.178, 0.089) | (0.509, 0.098, 0.040)→(0.502, 0.106, 0.032) | 0.179→0.186 | 1.00 / 1.000 | 0.489 | 2.732 |
| contact_peg | contact | 0.00 / step_budget | (0.505, 0.178, 0.089)→(0.502, 0.128, 0.060) | (0.502, 0.106, 0.032)→(0.517, 0.111, 0.027) | 0.186→0.193 | 1.00 / 1.000 | 0.536 | 1.350 |
| push_through_channel | push | 1.00 / step_budget | (0.502, 0.128, 0.060)→(0.497, -0.061, 0.055) | (0.517, 0.111, 0.027)→(0.533, 0.081, 0.021) | 0.193→0.169 | 1.00 / 1.000 | 0.620 | 16.036 |
| retract_from_channel | retract | 1.00 / step_budget | (0.497, -0.061, 0.055)→(0.494, -0.061, 0.165) | (0.533, 0.081, 0.021)→(0.567, 0.080, 0.021) | 0.169→0.185 | 1.00 / 1.000 | 0.615 | 3.491 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.275
- alignment_error: None
- force_efficiency: 0.666
- terminal_score: 0.268
- phase_score: 0.527
- phase_breakdown.push_score: 0.606
- phase_breakdown.contact_score: 0.533
- phase_breakdown.approach_score: 0.284

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.423
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.268
- **Median Q (composite search score)**: 0.047
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.247


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `474e87cb3f7f98c9c8d99c8760356b7c026b70b97898f68d5a6c39ba94bca956`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a79e5fd8fc80d9ecadd30a274b12d8d7e7d0841df5ca68ae512c46dc86b114e6`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08397,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.08501,"contact_peg.contact_force_threshold":14.82083,"contact_peg.contact_speed":0.02487,"push_through_channel.push_speed":0.03572,"retract_from_channel.retract_speed":0.05065},"optimized_scores":{"best_composite_score":0.11341,"best_fitness_score":0.42341,"best_task_score":0.26772},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":519.0,"contact_point_centroid":[0.50299,0.08763,0.00903],"force_p95":12.20116,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.68392,"mean_force":1.60414,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49765,0.0429,0.05946]},{"body_a":"attachment","body_b":"peg","contact_count":60.0,"contact_point_centroid":[0.50537,0.09156,0.05968],"force_p95":15.83378,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.23516,"mean_force":8.99835,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49798,0.08342,0.06061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":632.0,"contact_point_centroid":[0.50361,0.11172,0.00936],"force_p95":0.60427,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55841,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50227,0.19499,0.19114]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50292,0.06769,0.00804],"force_p95":0.71723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73748,"mean_force":0.60573,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49347,-0.06067,0.10715]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50372,0.11176,0.00937],"force_p95":0.6015,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60315,"mean_force":0.5468,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.5019,0.16536,0.07444]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49983,0.19959,0.29889]}],"total_contact_groups":6},"final_pose_error":0.04709,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50446,0.06775,0.02412],"final_tcp_position":[0.49367,-0.06063,0.1589],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":16.68392,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":654.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11177,0.03376],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.55989,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":648.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50598,0.19104,0.0891],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0967,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.11178,0.03376],"object_pos_start":[0.50376,0.11177,0.03376],"object_to_goal_dist_end":0.19191,"object_to_goal_dist_start":0.19191,"object_z_max":0.03377,"peak_contact_force":0.55848,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.60315,"tcp_end":[0.5012,0.14597,0.06664],"tcp_start":[0.50598,0.19104,0.0891],"tcp_to_object_dist_end":0.0475,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":529.0,"n_steps_budget":1000.0,"object_pos_end":[0.50174,0.06776,0.02411],"object_pos_start":[0.50375,0.11178,0.03376],"object_to_goal_dist_end":0.14863,"object_to_goal_dist_start":0.19191,"object_z_max":0.04075,"peak_contact_force":0.65778,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":579.0,"raw_peak_contact_force":16.68392,"tcp_end":[0.49668,-0.06097,0.05589],"tcp_start":[0.5012,0.14597,0.06664],"tcp_to_object_dist_end":0.1327,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50446,0.06775,0.02412],"object_pos_start":[0.50174,0.06776,0.02411],"object_to_goal_dist_end":0.14867,"object_to_goal_dist_start":0.14863,"object_z_max":0.02413,"peak_contact_force":0.7104,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.73748,"tcp_end":[0.49367,-0.06063,0.1589],"tcp_start":[0.49668,-0.06097,0.05589],"tcp_to_object_dist_end":0.18645,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `3ca2e925d364d2c0fe81fb71ee31d40f947a20e349a0720e1c44a2dd2bc628da`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.21721,"average_solve_count":244.0,"average_success_count":244.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.07146,"contact_peg.contact_force_threshold":10.59906,"contact_peg.contact_speed":0.04267,"push_through_channel.push_speed":0.04802,"retract_from_channel.retract_speed":0.0445},"optimized_scores":{"best_composite_score":0.04726,"best_fitness_score":0.35726,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"world","contact_count":989.0,"contact_point_centroid":[0.51201,0.15933,-0.00196],"force_p95":0.72593,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.89251,"mean_force":0.61252,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.48674,0.16334,0.06441]},{"body_a":"peg","body_b":"channel_base_body","contact_count":612.0,"contact_point_centroid":[0.49626,0.11938,0.00943],"force_p95":0.6187,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.54406,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4912,0.19838,0.19369]},{"body_a":"peg","body_b":"world","contact_count":23.0,"contact_point_centroid":[0.49614,0.13354,-0.00021],"force_p95":0.94308,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.06703,"mean_force":0.54553,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.4841,0.19776,0.09339]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49957,0.19957,0.29772]},{"body_a":"peg","body_b":"world","contact_count":514.0,"contact_point_centroid":[0.56772,0.15837,-0.00199],"force_p95":0.72592,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72626,"mean_force":0.60631,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49257,0.03612,0.04839]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.64723,0.15628,-0.00199],"force_p95":0.72586,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72595,"mean_force":0.60602,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49269,-0.06134,0.10501]}],"total_contact_groups":6},"final_pose_error":0.04778,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.69767,0.15511,0.0141],"final_tcp_position":[0.49286,-0.0613,0.15653],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":2.89251,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":654.0,"n_steps_budget":1000.0,"object_pos_end":[0.49637,0.14246,0.0294],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.22274,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.36652,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":659.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48381,0.19773,0.08959],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08269,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":999.0,"n_steps_budget":1000.0,"object_pos_end":[0.54212,0.15896,0.01408],"object_pos_start":[0.49637,0.14246,0.0294],"object_to_goal_dist_end":0.24402,"object_to_goal_dist_start":0.22274,"object_z_max":0.0294,"peak_contact_force":0.49883,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":989.0,"raw_peak_contact_force":2.89251,"tcp_end":[0.49207,0.13413,0.04625],"tcp_start":[0.48381,0.19773,0.08959],"tcp_to_object_dist_end":0.06446,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":514.0,"n_steps_budget":1000.0,"object_pos_end":[0.59516,0.15762,0.0141],"object_pos_start":[0.54212,0.15896,0.01408],"object_to_goal_dist_end":0.25727,"object_to_goal_dist_start":0.24402,"object_z_max":0.0141,"peak_contact_force":0.63692,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":514.0,"raw_peak_contact_force":0.72626,"tcp_end":[0.4959,-0.06166,0.05421],"tcp_start":[0.49207,0.13413,0.04625],"tcp_to_object_dist_end":0.24401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.69767,0.15511,0.0141],"object_pos_start":[0.59516,0.15762,0.0141],"object_to_goal_dist_end":0.30826,"object_to_goal_dist_start":0.25727,"object_z_max":0.0141,"peak_contact_force":0.63707,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.72595,"tcp_end":[0.49286,-0.0613,0.15653],"tcp_start":[0.4959,-0.06166,0.05421],"tcp_to_object_dist_end":0.33026,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f85f1938a541e3d507519c8f918b8ca98f1f9baf6ab2f6f3ba2c32478e079e47`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.20392,"average_solve_count":255.0,"average_success_count":255.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.08616,"contact_peg.contact_force_threshold":10.27461,"contact_peg.contact_speed":0.0232,"push_through_channel.push_speed":0.01341,"retract_from_channel.retract_speed":0.07546},"optimized_scores":{"best_composite_score":0.03008,"best_fitness_score":0.34008,"best_task_score":0.08189},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":411.0,"contact_point_centroid":[0.5044,0.042,0.00909],"force_p95":28.622,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.6985,"mean_force":4.40623,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50413,0.02254,0.06021]},{"body_a":"attachment","body_b":"peg","contact_count":87.0,"contact_point_centroid":[0.5115,0.04451,0.06036],"force_p95":30.11434,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":30.23972,"mean_force":18.17001,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50537,0.03552,0.06094]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49707,0.01857,0.00805],"force_p95":0.72552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.01062,"mean_force":0.64383,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49463,-0.06048,0.11794]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47499,-0.0057,0.02447],"force_p95":8.46488,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.56618,"mean_force":3.36033,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.4944,-0.0604,0.10947]},{"body_a":"peg","body_b":"channel_base_body","contact_count":668.0,"contact_point_centroid":[0.50578,0.06303,0.00936],"force_p95":0.5601,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.56681,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51169,0.17154,0.18917]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49996,0.19881,0.29619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50599,0.06291,0.00938],"force_p95":0.55193,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54655,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.516,0.12055,0.07403]}],"total_contact_groups":7},"final_pose_error":0.02574,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49991,0.01787,0.02409],"final_tcp_position":[0.49491,-0.06045,0.1805],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"peak_contact_force":30.6985,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":696.0,"n_steps_budget":1000.0,"object_pos_end":[0.50603,0.06298,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"peak_contact_force":0.54173,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":702.0,"raw_peak_contact_force":3.88411,"tcp_end":[0.52432,0.14538,0.08784],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10023,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50589,0.063,0.03383],"object_pos_start":[0.50603,0.06298,0.03381],"object_to_goal_dist_end":0.14325,"object_to_goal_dist_start":0.14324,"object_z_max":0.03383,"peak_contact_force":0.54924,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55532,"tcp_end":[0.51219,0.10242,0.06724],"tcp_start":[0.52432,0.14538,0.08784],"tcp_to_object_dist_end":0.05206,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":420.0,"n_steps_budget":1000.0,"object_pos_end":[0.50066,0.01876,0.02416],"object_pos_start":[0.50589,0.063,0.03383],"object_to_goal_dist_end":0.10003,"object_to_goal_dist_start":0.14325,"object_z_max":0.04073,"peak_contact_force":0.56578,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":498.0,"raw_peak_contact_force":30.6985,"tcp_end":[0.49784,-0.06077,0.05607],"tcp_start":[0.51219,0.10242,0.06724],"tcp_to_object_dist_end":0.08574,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49991,0.01787,0.02409],"object_pos_start":[0.50066,0.01876,0.02416],"object_to_goal_dist_end":0.09916,"object_to_goal_dist_start":0.10003,"object_z_max":0.02472,"peak_contact_force":0.49884,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1013.0,"raw_peak_contact_force":9.01062,"tcp_end":[0.49491,-0.06045,0.1805],"tcp_start":[0.49784,-0.06077,0.05607],"tcp_to_object_dist_end":0.17499,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```