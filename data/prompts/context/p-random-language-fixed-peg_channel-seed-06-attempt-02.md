## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0795 | 0.00 | ✅ accepted |
| 1 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0828 | 0.00 | ❌ rejected |
| 0 | align → lift → push → approach → approach → descend → grasp | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | arc_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | force_threshold_switch | position_control | admittance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 5 | -0.0805 | 0.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`
- Frozen object start: [0.5030531481177555, 0.06746166958506708, 0.04]
- Frozen task target: [0.5030531481177555, -0.09253833041493292, 0.04]
- Goal object position: (0.5030531481177555, -0.09253833041493292, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5030531481177555, 0.06746166958506708, 0.04)
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
  frozen_object_start: [0.5031, 0.0675, 0.04]
  frozen_task_target: [0.5031, -0.0925, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5030531481177555, 0.06746166958506708, 0.04]}
  frozen_targets: {'channel_exit': [0.5030531481177555, -0.09253833041493292, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de

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

## Current Skill (Q=-0.080) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
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
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
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
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: approach_2
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp

```

## Design Metrics

- **Composite score**: -0.080
- **task_score** (E): 0.000
- **fitness_score**: 0.320  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.400

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2592 |
| lift_1 | 0.00 | 1.00 | 0.1708 |
| push_1 | 1.00 | 1.00 | 0.1869 |
| approach_1 | 0.33 | 1.00 | 0.1656 |
| approach_2 | 0.67 | 1.00 | 0.0481 |
| descend_1 | 0.67 | 0.67 | 0.0853 |
| grasp_1 | 1.00 | 1.00 | 0.0062 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.142, 0.049) | (0.500, 0.099, 0.040)→(0.501, 0.100, 0.034) | 0.180→0.180 | 1.00 / 1.000 | 0.547 | 2.127 |
| lift_1 | lift | 0.00 / step_budget | (0.496, 0.142, 0.049)→(0.430, 0.046, 0.174) | (0.501, 0.100, 0.034)→(0.503, 0.113, 0.027) | 0.180→0.194 | 1.00 / 1.000 | 0.598 | 1.939 |
| push_1 | push | 1.00 / step_budget | (0.430, 0.046, 0.174)→(0.494, -0.068, 0.042) | (0.503, 0.113, 0.027)→(0.517, 0.114, 0.027) | 0.194→0.196 | 1.00 / 1.333 | 48.600 | 116.556 |
| approach_1 | approach | 0.33 / step_budget | (0.494, -0.068, 0.042)→(0.499, 0.098, 0.042) | (0.517, 0.114, 0.027)→(0.551, 0.137, 0.028) | 0.196→0.230 | 1.00 / 2.000 | 156.394 | 216.240 |
| approach_2 | approach | 0.67 / step_budget | (0.499, 0.098, 0.042)→(0.503, 0.145, 0.038) | (0.551, 0.137, 0.028)→(0.594, 0.162, 0.013) | 0.230→0.279 | 1.00 / 1.667 | 24.459 | 131.074 |
| descend_1 | descend | 0.67 / step_budget | (0.503, 0.145, 0.038)→(0.568, 0.187, 0.021) | (0.594, 0.162, 0.013)→(0.701, 0.173, -2.190) | 0.279→2.397 | 0.67 / 1.333 | 129.952 | 199.597 |
| grasp_1 | grasp | 1.00 / step_budget | (0.568, 0.187, 0.021)→(0.566, 0.187, 0.016) | (0.701, 0.173, -2.190)→(0.773, 0.163, -6.932) | 2.397→7.129 | 1.00 / 1.667 | 38.926 | 49.958 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.681
- phase_breakdown.push_score: 0.869
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.797

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.408
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.046
- **K-run variance**: 0.0079
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.344


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `080f370e6b427cbdf66706e7036a0e474f3967ccfc94f129756881a980a10a27`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `1f3f20d8b9dd2cb87de5d9f0723b4addbc88cdcf096cd2177633d23c0fa32881`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.70916,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00404,"approach_2.speed":0.03603,"lift_1.lift_height":0.26519,"push_1.push_distance":0.17304,"push_1.push_speed":0.07623},"optimized_scores":{"best_composite_score":-0.04612,"best_fitness_score":0.35388,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":2,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":263.0,"contact_point_centroid":[0.55499,0.11999,0.05995],"force_p95":248.57505,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":292.82558,"mean_force":162.71729,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51573,0.17883,0.02605]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.54389,0.08918,0.05993],"force_p95":279.22615,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":281.14545,"mean_force":130.34969,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49912,0.08883,0.03634]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":125.0,"contact_point_centroid":[0.50167,-0.10007,0.065],"force_p95":179.71362,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":212.04599,"mean_force":132.9589,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49307,-0.0879,0.04698]},{"body_a":"peg","body_b":"world","contact_count":343.0,"contact_point_centroid":[0.53203,0.17035,-0.00492],"force_p95":70.47396,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.98857,"mean_force":26.36477,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51494,0.17722,0.02657]},{"body_a":"attachment","body_b":"peg","contact_count":240.0,"contact_point_centroid":[0.52342,0.1702,0.02381],"force_p95":72.09683,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.83976,"mean_force":37.02335,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51269,0.17293,0.02795]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.54419,0.09369,0.05999],"force_p95":59.34864,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.0825,"mean_force":45.02734,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49948,0.09314,0.03637]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.555,0.12,0.05998],"force_p95":71.23254,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.74855,"mean_force":62.49012,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52622,0.19649,0.02015]},{"body_a":"attachment","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.5092,-0.10006,0.065],"force_p95":65.63776,"geom_a":"pusher_tip","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":68.26387,"mean_force":48.03707,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49832,-0.08786,0.04155]},{"body_a":"peg","body_b":"world","contact_count":386.0,"contact_point_centroid":[0.50959,0.14957,-0.00216],"force_p95":24.02865,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.44805,"mean_force":2.63038,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49901,0.12471,0.0367]},{"body_a":"attachment","body_b":"peg","contact_count":46.0,"contact_point_centroid":[0.51178,0.1457,0.03016],"force_p95":33.15155,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.93172,"mean_force":16.97498,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50079,0.14636,0.03488]},{"body_a":"peg","body_b":"channel_base_body","contact_count":969.0,"contact_point_centroid":[0.50389,0.07675,0.00952],"force_p95":18.60297,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.13322,"mean_force":3.85245,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49675,-0.00082,0.04745]},{"body_a":"attachment","body_b":"peg","contact_count":254.0,"contact_point_centroid":[0.50182,0.07366,0.04299],"force_p95":23.10916,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.03528,"mean_force":12.78048,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.06244,0.04427]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":30.0,"contact_point_centroid":[0.52507,0.11176,0.03556],"force_p95":1.64309,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.09731,"mean_force":0.52598,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49892,0.08336,0.03817]},{"body_a":"peg","body_b":"channel_base_body","contact_count":805.0,"contact_point_centroid":[0.50309,0.06747,0.00935],"force_p95":0.5533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55733,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49866,0.1548,0.17095]},{"body_a":"peg","body_b":"channel_base_body","contact_count":65.0,"contact_point_centroid":[0.50651,0.11982,0.0097],"force_p95":0.65107,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77344,"mean_force":0.45148,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49942,0.09352,0.03638]},{"body_a":"peg","body_b":"world","contact_count":450.0,"contact_point_centroid":[0.57329,0.17179,-0.00202],"force_p95":0.76991,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77192,"mean_force":0.60496,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.52622,0.19649,0.02015]}],"total_contact_groups":18},"final_pose_error":0.01247,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.59036,0.16088,0.01406],"final_tcp_position":[0.52546,0.19616,0.02031],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":292.82558,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.5478,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":805.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.499,0.11132,0.04824],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0464,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"peak_contact_force":0.54731,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55077,"tcp_end":[0.43006,0.02624,0.17825],"tcp_start":[0.499,0.11132,0.04824],"tcp_to_object_dist_end":0.16699,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":921.0,"n_steps_budget":1000.0,"object_pos_end":[0.50303,0.0675,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":144.71631,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1046.0,"raw_peak_contact_force":212.04599,"tcp_end":[0.49833,-0.08789,0.0416],"tcp_start":[0.43006,0.02624,0.17825],"tcp_to_object_dist_end":0.15566,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50579,0.12127,0.0355],"object_pos_start":[0.50303,0.0675,0.0338],"object_to_goal_dist_end":0.2014,"object_to_goal_dist_start":0.14766,"object_z_max":0.03978,"peak_contact_force":104.28148,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1274.0,"raw_peak_contact_force":281.14545,"tcp_end":[0.49981,0.09005,0.03631],"tcp_start":[0.49833,-0.08789,0.0416],"tcp_to_object_dist_end":0.03179,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":458.0,"n_steps_budget":1000.0,"object_pos_end":[0.51961,0.16247,0.01129],"object_pos_start":[0.50579,0.12127,0.0355],"object_to_goal_dist_end":0.24495,"object_to_goal_dist_start":0.2014,"object_z_max":0.0355,"peak_contact_force":33.73718,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":531.0,"raw_peak_contact_force":78.0825,"tcp_end":[0.50165,0.15234,0.0338],"tcp_start":[0.49981,0.09005,0.03631],"tcp_to_object_dist_end":0.03053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":343.0,"n_steps_budget":600.0,"object_pos_end":[0.55657,0.18247,0.01415],"object_pos_start":[0.51961,0.16247,0.01129],"object_to_goal_dist_end":0.26974,"object_to_goal_dist_start":0.24495,"object_z_max":0.01418,"peak_contact_force":213.23291,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":846.0,"raw_peak_contact_force":292.82558,"tcp_end":[0.52546,0.19616,0.02031],"tcp_start":[0.50165,0.15234,0.0338],"tcp_to_object_dist_end":0.03454,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.59036,0.16088,0.01406],"object_pos_start":[0.55657,0.18247,0.01415],"object_to_goal_dist_end":0.25858,"object_to_goal_dist_start":0.26974,"object_z_max":0.01415,"peak_contact_force":57.18762,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":71.74855,"tcp_end":[0.52644,0.19656,0.02006],"tcp_start":[0.52546,0.19616,0.02031],"tcp_to_object_dist_end":0.07346,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `625c03a21403c0f6267b643060335ee3d751a26340ace08db5429afcee4c5ccf`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,0.11178,0.04]},{"name":"goal","value":[0.51001,-0.04822,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51001,-0.04822,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.72398,"average_solve_count":221.0,"average_success_count":221.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00357,"approach_2.speed":0.05788,"lift_1.lift_height":0.24571,"push_1.push_distance":0.19954,"push_1.push_speed":0.09182},"optimized_scores":{"best_composite_score":0.00837,"best_fitness_score":0.40837,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":348.0,"contact_point_centroid":[0.55498,0.11999,0.05993],"force_p95":275.60058,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":305.08677,"mean_force":191.62286,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51027,0.1722,0.02851]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":450.0,"contact_point_centroid":[0.55499,0.12,0.05998],"force_p95":72.37513,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.72552,"mean_force":62.79207,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51773,0.18486,0.02416]},{"body_a":"peg","body_b":"world","contact_count":402.0,"contact_point_centroid":[0.50333,0.15522,-0.00252],"force_p95":47.65593,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.29162,"mean_force":20.00417,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50977,0.17122,0.02883]},{"body_a":"attachment","body_b":"peg","contact_count":299.0,"contact_point_centroid":[0.51022,0.15856,0.02914],"force_p95":49.7601,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":71.25522,"mean_force":26.33012,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50787,0.16755,0.03004]},{"body_a":"peg","body_b":"world","contact_count":333.0,"contact_point_centroid":[0.5051,0.15045,-0.00199],"force_p95":27.75871,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.05791,"mean_force":3.10579,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49684,0.12825,0.04185]},{"body_a":"attachment","body_b":"peg","contact_count":34.0,"contact_point_centroid":[0.51032,0.15023,0.03117],"force_p95":38.96336,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.54943,"mean_force":24.34011,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.49927,0.15042,0.03574]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50378,0.11222,0.0094],"force_p95":0.6031,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.14727,"mean_force":0.56149,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49326,0.00584,0.05095]},{"body_a":"attachment","body_b":"peg","contact_count":13.0,"contact_point_centroid":[0.50097,0.09782,0.05306],"force_p95":2.96002,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.98128,"mean_force":1.57108,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4968,0.08611,0.0496]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50352,0.11122,0.00941],"force_p95":0.60591,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.43975,"mean_force":0.54793,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46978,0.10378,0.10742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":756.0,"contact_point_centroid":[0.50359,0.11169,0.00938],"force_p95":0.60779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55452,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50201,0.17585,0.17071]},{"body_a":"attachment","body_b":"peg","contact_count":17.0,"contact_point_centroid":[0.49753,0.12798,0.05958],"force_p95":1.1545,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.97536,"mean_force":0.44372,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4931,0.13894,0.06131]},{"body_a":"peg","body_b":"world","contact_count":450.0,"contact_point_centroid":[0.48988,0.17006,-0.00193],"force_p95":0.64422,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64445,"mean_force":0.60645,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.51773,0.18486,0.02416]},{"body_a":"peg","body_b":"channel_base_body","contact_count":840.0,"contact_point_centroid":[0.50369,0.11158,0.00941],"force_p95":0.59221,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.61894,"mean_force":0.54391,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46466,-0.01375,0.10327]},{"body_a":"peg","body_b":"channel_base_body","contact_count":47.0,"contact_point_centroid":[0.50501,0.11984,0.00976],"force_p95":0.52669,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5783,"mean_force":0.4242,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.4962,0.09875,0.04644]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49976,0.19944,0.29874]}],"total_contact_groups":15},"final_pose_error":0.01664,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.48699,0.16878,0.01415],"final_tcp_position":[0.51717,0.1844,0.0244],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":305.08677,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":778.0,"n_steps_budget":1000.0,"object_pos_end":[0.50367,0.11173,0.03382],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.19187,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57116,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":772.0,"raw_peak_contact_force":2.06328,"tcp_end":[0.50559,0.15326,0.04883],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0442,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.11176,0.0338],"object_pos_start":[0.50367,0.11173,0.03382],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19187,"object_z_max":0.03525,"peak_contact_force":0.61004,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":1017.0,"raw_peak_contact_force":2.43975,"tcp_end":[0.43774,0.05553,0.1705],"tcp_start":[0.50559,0.15326,0.04883],"tcp_to_object_dist_end":0.1619,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":840.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.11166,0.03387],"object_pos_start":[0.50377,0.11176,0.0338],"object_to_goal_dist_end":0.19179,"object_to_goal_dist_start":0.1919,"object_z_max":0.03396,"peak_contact_force":0.52037,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":840.0,"raw_peak_contact_force":0.61894,"tcp_end":[0.49309,-0.08081,0.04106],"tcp_start":[0.43774,0.05553,0.1705],"tcp_to_object_dist_end":0.1929,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50399,0.12204,0.03534],"object_pos_start":[0.50373,0.11166,0.03387],"object_to_goal_dist_end":0.20213,"object_to_goal_dist_start":0.19179,"object_z_max":0.0354,"peak_contact_force":0.47274,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1013.0,"raw_peak_contact_force":3.14727,"tcp_end":[0.49717,0.09518,0.04762],"tcp_start":[0.49309,-0.08081,0.04106],"tcp_to_object_dist_end":0.03031,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":386.0,"n_steps_budget":750.0,"object_pos_end":[0.50741,0.15162,0.01302],"object_pos_start":[0.50399,0.12204,0.03534],"object_to_goal_dist_end":0.2333,"object_to_goal_dist_start":0.20213,"object_z_max":0.03534,"peak_contact_force":39.07818,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":414.0,"raw_peak_contact_force":40.05791,"tcp_end":[0.50001,0.1529,0.03478],"tcp_start":[0.49717,0.09518,0.04762],"tcp_to_object_dist_end":0.02303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":402.0,"n_steps_budget":600.0,"object_pos_end":[0.49303,0.17147,0.01416],"object_pos_start":[0.50741,0.15162,0.01302],"object_to_goal_dist_end":0.25289,"object_to_goal_dist_start":0.2333,"object_z_max":0.01417,"peak_contact_force":176.62415,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1049.0,"raw_peak_contact_force":305.08677,"tcp_end":[0.51717,0.1844,0.0244],"tcp_start":[0.50001,0.1529,0.03478],"tcp_to_object_dist_end":0.02923,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.48699,0.16878,0.01415],"object_pos_start":[0.49303,0.17147,0.01416],"object_to_goal_dist_end":0.25045,"object_to_goal_dist_start":0.25289,"object_z_max":0.01416,"peak_contact_force":56.75517,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":900.0,"raw_peak_contact_force":73.72552,"tcp_end":[0.51795,0.18495,0.02408],"tcp_start":[0.51717,0.1844,0.0244],"tcp_to_object_dist_end":0.03631,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `abe38b4b57ac37a91047e57d04e408cb1fd05583a47670bcb186dc9505a3f021`; realized-scene SHA-256: `c5fb87552d009c7e1ef813cadc54d289d6d9c896c1dd51a37fa468bf6305165e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48616,0.11898,0.04]},{"name":"goal","value":[0.48616,-0.04102,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48616,0.11898,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48616,-0.04102,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.53957,"average_solve_count":278.0,"average_success_count":278.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_y":0.00276,"approach_2.speed":0.03987,"lift_1.lift_height":0.09079,"push_1.push_distance":0.19982,"push_1.push_speed":0.05075},"optimized_scores":{"best_composite_score":-0.20083,"best_fitness_score":0.19917,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":79.0,"contact_point_centroid":[0.54653,0.10906,0.05992],"force_p95":346.21381,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":364.42775,"mean_force":234.30525,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5001,0.10711,0.03988]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":413.0,"contact_point_centroid":[0.52506,0.0807,0.05997],"force_p95":232.49142,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":300.67398,"mean_force":156.97324,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50378,0.08039,0.04425]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":872.0,"contact_point_centroid":[0.55057,0.11566,0.05997],"force_p95":227.71387,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":275.08146,"mean_force":147.96784,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50009,0.11356,0.04569]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":896.0,"contact_point_centroid":[0.52504,0.11376,0.05997],"force_p95":172.50655,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.72855,"mean_force":113.95872,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50003,0.11293,0.04539]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47497,-0.02792,0.05992],"force_p95":133.84706,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":137.00209,"mean_force":81.50695,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48529,-0.02548,0.05462]},{"body_a":"attachment","body_b":"world","contact_count":243.0,"contact_point_centroid":[0.66534,0.17501,-0.0],"force_p95":4.32353,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.3989,"mean_force":3.32907,"phase_index":6.0,"phase_name":"grasp_1","phase_type":"grasp","tcp_position_centroid":[0.65418,0.17839,0.00282]},{"body_a":"peg","body_b":"world","contact_count":601.0,"contact_point_centroid":[0.49712,0.15864,-0.00186],"force_p95":0.72597,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.8278,"mean_force":0.61334,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.4405,0.08822,0.1344]},{"body_a":"peg","body_b":"channel_base_body","contact_count":739.0,"contact_point_centroid":[0.49619,0.11915,0.0094],"force_p95":0.61089,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.24822,"mean_force":0.55292,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49061,0.17919,0.17037]},{"body_a":"peg","body_b":"world","contact_count":432.0,"contact_point_centroid":[0.7807,0.17209,-0.00186],"force_p95":0.72585,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.87928,"mean_force":0.58272,"phase_index":5.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53997,0.14048,0.03638]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":24.0,"contact_point_centroid":[0.47288,0.11898,0.03087],"force_p95":0.72905,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.86893,"mean_force":0.3628,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49948,0.19927,0.29748]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.58947,0.16434,-0.00199],"force_p95":0.72595,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72611,"mean_force":0.60602,"phase_index":3.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50078,0.0439,0.04517]},{"body_a":"peg","body_b":"world","contact_count":817.0,"contact_point_centroid":[0.52078,0.16133,-0.00199],"force_p95":0.72591,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72593,"mean_force":0.60597,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.45679,0.01101,0.10617]},{"body_a":"peg","body_b":"world","contact_count":1000.0,"contact_point_centroid":[0.69949,0.16867,-0.00199],"force_p95":0.72587,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72587,"mean_force":0.60602,"phase_index":4.0,"phase_name":"approach_2","phase_type":"approach","tcp_position_centroid":[0.50012,0.11351,0.04562]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.49585,0.11953,0.00942],"force_p95":0.60298,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62344,"mean_force":0.52859,"phase_index":1.0,"phase_name":"lift_1","phase_type":"lift","tcp_position_centroid":[0.46838,0.13841,0.07114]}],"total_contact_groups":14},"final_pose_error":0.09834,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[1.24261,0.15809,-20.82378],"final_tcp_position":[0.66252,0.18054,0.01695],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48616,0.11898,0.04]},"peak_contact_force":364.42775,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":764.0,"n_steps_budget":1000.0,"object_pos_end":[0.49601,0.11947,0.03385],"object_pos_start":[0.48616,0.11898,0.04],"object_to_goal_dist_end":0.1996,"object_to_goal_dist_start":0.19946,"object_z_max":0.04,"peak_contact_force":0.52313,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":763.0,"raw_peak_contact_force":2.24822,"tcp_end":[0.48315,0.16005,0.04931],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0453,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50294,0.16045,0.01409],"object_pos_start":[0.49601,0.11947,0.03385],"object_to_goal_dist_end":0.24186,"object_to_goal_dist_start":0.1996,"object_z_max":0.03393,"peak_contact_force":0.63703,"phase_name":"lift_1","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":998.0,"raw_peak_contact_force":2.8278,"tcp_end":[0.4234,0.05711,0.17396],"tcp_start":[0.48315,0.16005,0.04931],"tcp_to_object_dist_end":0.2063,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":817.0,"n_steps_budget":1000.0,"object_pos_end":[0.54454,0.16244,0.01409],"object_pos_start":[0.50294,0.16045,0.01409],"object_to_goal_dist_end":0.24786,"object_to_goal_dist_start":0.24186,"object_z_max":0.01409,"peak_contact_force":0.56212,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":824.0,"raw_peak_contact_force":137.00209,"tcp_end":[0.49201,-0.03411,0.04243],"tcp_start":[0.4234,0.05711,0.17396],"tcp_to_object_dist_end":0.20541,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.64273,0.16645,0.0141],"object_pos_start":[0.54454,0.16244,0.01409],"object_to_goal_dist_end":0.28597,"object_to_goal_dist_start":0.24786,"object_z_max":0.0141,"peak_contact_force":364.42775,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1492.0,"raw_peak_contact_force":364.42775,"tcp_end":[0.50001,0.10817,0.04078],"tcp_start":[0.49201,-0.03411,0.04243],"tcp_to_object_dist_end":0.15645,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.75603,0.17083,0.01409],"object_pos_start":[0.64273,0.16645,0.0141],"object_to_goal_dist_end":0.35936,"object_to_goal_dist_start":0.28597,"object_z_max":0.0141,"peak_contact_force":0.56218,"phase_name":"approach_2","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2768.0,"raw_peak_contact_force":275.08146,"tcp_end":[0.50656,0.12921,0.04689],"tcp_start":[0.50001,0.10817,0.04078],"tcp_to_object_dist_end":0.25504,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[1.0537,0.16443,-6.59965],"object_pos_start":[0.75603,0.17083,0.01409],"object_to_goal_dist_end":6.66718,"object_to_goal_dist_start":0.35936,"object_z_max":0.01504,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":432.0,"raw_peak_contact_force":0.87928,"tcp_end":[0.66252,0.18054,0.01695],"tcp_start":[0.50656,0.12921,0.04689],"tcp_to_object_dist_end":6.62817,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[1.24261,0.15809,-20.82378],"object_pos_start":[1.0537,0.16443,-6.59965],"object_to_goal_dist_end":20.87835,"object_to_goal_dist_start":6.66718,"object_z_max":-6.59965,"peak_contact_force":2.8344,"phase_name":"grasp_1","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":243.0,"raw_peak_contact_force":4.3989,"tcp_end":[0.65419,0.1784,0.00282],"tcp_start":[0.66252,0.18054,0.01695],"tcp_to_object_dist_end":20.83492,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```