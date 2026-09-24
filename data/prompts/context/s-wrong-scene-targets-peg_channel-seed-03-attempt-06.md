## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | 0.1064 | 0.00 | ❌ rejected |
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.0593 | 0.00 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 3 | 0.2422 | 0.00 | ❌ rejected |
| 3 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ❌ rejected |
| 2 | rotate → retract → descend → pull | impedance_motion | arc_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | admittance_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | 3 | -0.1168 | 0.09 | ❌ rejected |

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
- Frozen realised-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`
- Frozen object start: [0.46685193337148995, -0.10105515947231203, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.46685193337148995, -0.10105515947231203, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.46685193337148995, 0.058944840527687975, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.46685193337148995, 0.058944840527687975, 0.04]
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
  frozen_object_starts: {'peg': [0.46685193337148995, -0.10105515947231203, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.46685193337148995, -0.10105515947231203, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.2, 0.3) | final destination targets |
| `fixture` | offset from fixture pose (0.54, 0.0, 0.035) | approach/contact targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=0.106) — your mutation base

```yaml
skill: peg_channel
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: position_control
  termination: pose_tolerance
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  parameters:
    depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2

```

## Design Metrics

- **Composite score**: 0.106
- **task_score** (E): 0.000
- **fitness_score**: 0.264  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_channel | 1.00 | 1.00 | 0.2387 |
| contact_peg | 0.67 | 1.00 | 0.0414 |
| push_through_channel | 0.33 | 1.00 | 0.0070 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_channel | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.497, 0.077, 0.095) | (0.509, 0.081, 0.040)→(0.502, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.545 | 3.954 |
| contact_peg | descend | 0.67 / force_exceeded | (0.497, 0.077, 0.095)→(0.495, 0.079, 0.054) | (0.502, 0.082, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 2.000 | 13.100 | 14.653 |
| push_through_channel | push | 0.33 / guard_failure | (0.495, 0.079, 0.054)→(0.495, 0.072, 0.052) | (0.502, 0.082, 0.034)→(0.502, 0.082, 0.034) | 0.162→0.162 | 1.00 / 1.667 | 19.241 | 29.254 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.092
- terminal_score: 0.000
- phase_score: 0.417
- phase_breakdown.traverse_channel_score: 0.000
- phase_breakdown.reach_entrance_score: 0.729
- phase_breakdown.insert_peg_score: 0.661

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.292
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: 0.203
- **K-run variance**: 0.0189
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.260


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
{"anchors":[{"name":"object","value":[0.46685,-0.10106,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.10106,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.78723,"average_solve_count":47.0,"average_success_count":47.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_channel.approach_speed":0.21411,"approach_channel.approach_y_offset":0.14845,"contact_peg.contact_speed":0.08598,"contact_peg.force_threshold":4.28086,"push_through_channel.push_distance":0.1805,"push_through_channel.push_speed":0.06346,"push_through_channel.push_timeout":4.85607},"optimized_scores":{"best_composite_score":0.2036,"best_fitness_score":0.25027,"best_task_score":0.00016},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":8.0,"contact_point_centroid":[0.49393,0.05892,0.00937],"force_p95":40.97567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.38973,"mean_force":23.92047,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.495,0.07948,0.05977]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.50504,0.07309,0.05852],"force_p95":40.32893,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.76082,"mean_force":23.45974,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.495,0.07948,0.05977]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.4941,0.05922,0.00939],"force_p95":0.551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.7166,"mean_force":0.62619,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.49515,0.07936,0.07686]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50508,0.07293,0.0589],"force_p95":12.73896,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.25815,"mean_force":8.06619,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.4951,0.07941,0.06036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":385.0,"contact_point_centroid":[0.4944,0.05889,0.00934],"force_p95":0.59661,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.5842,"phase_index":0.0,"phase_name":"approach_channel","phase_type":"approach","tcp_position_centroid":[0.49806,0.13664,0.19071]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_channel","phase_type":"approach","tcp_position_centroid":[0.49963,0.19624,0.29339]}],"total_contact_groups":6},"final_pose_error":0.02893,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49399,0.05887,0.03375],"final_tcp_position":[0.49486,0.07961,0.05935],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":45.38973,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":414.0,"n_steps_budget":750.0,"object_pos_end":[0.4942,0.05889,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13915,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54253,"phase_name":"approach_channel","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":420.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_entrance","tcp_end":[0.49722,0.08001,0.09555],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06528,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":200.0,"n_steps_budget":600.0,"object_pos_end":[0.4941,0.05885,0.03384],"object_pos_start":[0.4942,0.05889,0.03385],"object_to_goal_dist_end":0.13911,"object_to_goal_dist_start":0.13915,"object_z_max":0.03388,"peak_contact_force":13.7166,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":202.0,"raw_peak_contact_force":13.7166,"subtask_id":"insert_peg","tcp_end":[0.49514,0.07942,0.06012],"tcp_start":[0.49722,0.08001,0.09555],"tcp_to_object_dist_end":0.0334,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":8.0,"n_steps_budget":600.0,"object_pos_end":[0.49409,0.05884,0.03379],"object_pos_start":[0.4941,0.05885,0.03384],"object_to_goal_dist_end":0.13911,"object_to_goal_dist_start":0.13911,"object_z_max":0.03384,"peak_contact_force":29.18261,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":45.38973,"subtask_id":"traverse_channel","tcp_end":[0.49486,0.07961,0.05935],"tcp_start":[0.49491,0.07959,0.05942],"tcp_to_object_dist_end":0.03294,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1ee374347cb6f80436633ebcb956aaa73ea8a10685d65b21d5c3814cf0c53498`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,-0.07909,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,-0.07909,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79592,"average_solve_count":49.0,"average_success_count":49.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_channel.approach_speed":0.1999,"approach_channel.approach_y_offset":0.1468,"contact_peg.contact_speed":0.05679,"contact_peg.force_threshold":4.59582,"push_through_channel.push_distance":0.15786,"push_through_channel.push_speed":0.06057,"push_through_channel.push_timeout":3.28463},"optimized_scores":{"best_composite_score":0.20333,"best_fitness_score":0.25,"best_task_score":0.00017},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49204,0.07455,0.00932],"force_p95":38.3706,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.64756,"mean_force":22.87904,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49498,0.07872,0.05995]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50684,0.07835,0.05847],"force_p95":37.94495,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.25902,"mean_force":22.36215,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49498,0.07872,0.05995]},{"body_a":"peg","body_b":"channel_base_body","contact_count":200.0,"contact_point_centroid":[0.50613,0.08088,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.13565,"mean_force":0.6647,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.49515,0.07824,0.07692]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50699,0.07824,0.0587],"force_p95":23.66377,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.66377,"mean_force":23.66377,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.49513,0.07873,0.06038]},{"body_a":"peg","body_b":"channel_base_body","contact_count":390.0,"contact_point_centroid":[0.50556,0.08091,0.00935],"force_p95":0.56158,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58589,"phase_index":0.0,"phase_name":"approach_channel","phase_type":"approach","tcp_position_centroid":[0.49806,0.13577,0.19058]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_channel","phase_type":"approach","tcp_position_centroid":[0.49964,0.19597,0.29297]}],"total_contact_groups":6},"final_pose_error":0.0203,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50576,0.08081,0.03371],"final_tcp_position":[0.49484,0.07869,0.05962],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":40.64756,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":419.0,"n_steps_budget":810.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55004,"phase_name":"approach_channel","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":426.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_entrance","tcp_end":[0.49723,0.07848,0.09548],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06237,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":200.0,"n_steps_budget":630.0,"object_pos_end":[0.50599,0.08086,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":24.13565,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":201.0,"raw_peak_contact_force":24.13565,"subtask_id":"insert_peg","tcp_end":[0.49513,0.07874,0.06023],"tcp_start":[0.49723,0.07848,0.09548],"tcp_to_object_dist_end":0.02867,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":600.0,"object_pos_end":[0.50579,0.08082,0.03371],"object_pos_start":[0.50599,0.08086,0.03378],"object_to_goal_dist_end":0.16105,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":28.00677,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":14.0,"raw_peak_contact_force":40.64756,"subtask_id":"traverse_channel","tcp_end":[0.49484,0.07869,0.05962],"tcp_start":[0.49488,0.0787,0.05968],"tcp_to_object_dist_end":0.02821,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e082b57d1be6744ae6d3993c25b90215f3fc56dc7131af62e0630c4f325e4b04`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,-0.05536,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,-0.05536,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59722,"average_solve_count":72.0,"average_success_count":72.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_channel.approach_speed":0.17264,"approach_channel.approach_y_offset":0.141,"contact_peg.contact_speed":0.10315,"contact_peg.force_threshold":7.03531,"push_through_channel.push_distance":0.1371,"push_through_channel.push_speed":0.05149,"push_through_channel.push_timeout":5.75223},"optimized_scores":{"best_composite_score":-0.08785,"best_fitness_score":0.29215,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":325.0,"contact_point_centroid":[0.50648,0.10948,0.00948],"force_p95":2.52768,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.10534,"mean_force":0.73795,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.49526,0.07543,0.06728]},{"body_a":"attachment","body_b":"peg","contact_count":28.0,"contact_point_centroid":[0.50045,0.08872,0.05851],"force_p95":5.05425,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.67892,"mean_force":2.63937,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"descend","tcp_position_centroid":[0.4955,0.07743,0.05093]},{"body_a":"peg","body_b":"channel_base_body","contact_count":410.0,"contact_point_centroid":[0.50546,0.1046,0.00937],"force_p95":0.57967,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57393,"phase_index":0.0,"phase_name":"approach_channel","phase_type":"approach","tcp_position_centroid":[0.49804,0.13358,0.19149]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_channel","phase_type":"approach","tcp_position_centroid":[0.49964,0.19667,0.29448]},{"body_a":"peg","body_b":"channel_base_body","contact_count":440.0,"contact_point_centroid":[0.50617,0.10598,0.00943],"force_p95":0.59358,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.7238,"mean_force":0.55539,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49443,0.06733,0.03699]},{"body_a":"attachment","body_b":"peg","contact_count":15.0,"contact_point_centroid":[0.50125,0.08902,0.0587],"force_p95":1.17465,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.29321,"mean_force":0.43779,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49511,0.07771,0.04111]}],"total_contact_groups":6},"final_pose_error":0.00638,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50635,0.10559,0.03387],"final_tcp_position":[0.49568,0.0587,0.03558],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":6.10534,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":437.0,"n_steps_budget":960.0,"object_pos_end":[0.50589,0.10472,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18492,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54285,"phase_name":"approach_channel","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":442.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_entrance","tcp_end":[0.49723,0.07306,0.09521],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0696,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":325.0,"n_steps_budget":600.0,"object_pos_end":[0.50638,0.10635,0.03526],"object_pos_start":[0.50589,0.10472,0.03383],"object_to_goal_dist_end":0.18652,"object_to_goal_dist_start":0.18492,"object_z_max":0.03532,"peak_contact_force":1.44792,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":353.0,"raw_peak_contact_force":6.10534,"subtask_id":"insert_peg","tcp_end":[0.49584,0.07847,0.04225],"tcp_start":[0.49723,0.07306,0.09521],"tcp_to_object_dist_end":0.03062,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":440.0,"n_steps_budget":600.0,"object_pos_end":[0.50635,0.10559,0.03387],"object_pos_start":[0.50638,0.10635,0.03526],"object_to_goal_dist_end":0.1858,"object_to_goal_dist_start":0.18652,"object_z_max":0.03526,"peak_contact_force":0.53432,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":455.0,"raw_peak_contact_force":1.7238,"subtask_id":"traverse_channel","tcp_end":[0.49568,0.0587,0.03558],"tcp_start":[0.49584,0.07847,0.04225],"tcp_to_object_dist_end":0.04811,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```