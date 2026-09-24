## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3043 | 0.61 | ❌ rejected |
| 13 | approach → align → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10 | -0.3516 | 0.07 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 9 | -0.3886 | 0.00 | ❌ rejected |
| 11 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3041 | 0.61 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 7 | 0.1616 | 0.06 | ❌ rejected |

**Proposal policy**: task_score is 0.61 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`
- Frozen object start: [0.5354444884457894, 0.08090620422514894, 0.04]
- Frozen task target: [0.5354444884457894, -0.07909379577485107, 0.04]
- Goal object position: (0.5354444884457894, -0.07909379577485107, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5354444884457894, 0.08090620422514894, 0.04)
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
  frozen_object_start: [0.5354, 0.0809, 0.04]
  frozen_task_target: [0.5354, -0.0791, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5354444884457894, 0.08090620422514894, 0.04]}
  frozen_targets: {'channel_exit': [0.5354444884457894, -0.07909379577485107, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c

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
| `object` | offset from object initial position (0.5354444884457894, 0.08090620422514894, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5354444884457894, -0.07909379577485107, 0.04) | final destination targets |
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

## Current Skill (Q=0.304) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
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
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: 0.304
- **task_score** (E): 0.605
- **fitness_score**: 0.331  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1920 |
| align_1 | 1.00 | 1.00 | 0.1095 |
| release_1 | 1.00 | 1.00 | 0.1723 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.087, 0.145) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.507 | 57.839 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.087, 0.145)→(0.501, 0.120, 0.042) | (0.505, 0.084, 0.034)→(0.505, 0.082, 0.035) | 0.165→0.162 | 1.00 / 3.667 | 85.279 | 102.286 |
| release_1 | release | 1.00 / step_budget | (0.501, 0.120, 0.042)→(0.498, -0.052, 0.037) | (0.505, 0.082, 0.035)→(0.506, -0.081, 0.036) | 0.162→0.010 | 1.00 / 3.667 | 91.180 | 91.180 |
| insert_1 | insert | 1.00 / force_exceeded | (0.498, -0.052, 0.037)→(0.498, -0.052, 0.037) | (0.506, -0.081, 0.036)→(0.506, -0.081, 0.036) | 0.010→0.010 | 1.00 / 1.000 | 0.544 | 3.242 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.971
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.971
- phase_score: 0.189
- phase_breakdown.push_score: 0.020
- phase_breakdown.approach_score: 0.888
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.502
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.971
- **Median Q (composite search score)**: 0.273
- **K-run variance**: 0.0166
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_1.push_speed
- **Final σ (mean)**: 0.369


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `424e8a040c59c1e1e42822c1022320b6050001458f7b9b4937cb9238911ce80b`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `72d2436204c0f1ee3bbdbdfe3e5489661153a48f95d8f0dc3b73e6ce1e1e081b`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88889,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00049,"align_1.lateral_offset_y":0.00286,"insert_1.insertion_depth":0.13301,"insert_1.insertion_force":13.92339,"push_1.push_distance":0.0562,"push_1.push_speed":0.08979},"optimized_scores":{"best_composite_score":0.1641,"best_fitness_score":0.19077,"best_task_score":0.31005},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":524.0,"contact_point_centroid":[0.5425,-0.00592,0.05999],"force_p95":76.58674,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.52594,"mean_force":57.57406,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49772,-0.0054,0.03685]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54271,-0.04905,0.05998],"force_p95":81.10486,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":81.10486,"mean_force":81.10486,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49807,-0.05306,0.03664]},{"body_a":"attachment","body_b":"peg","contact_count":857.0,"contact_point_centroid":[0.50356,-0.00106,0.04404],"force_p95":18.19148,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.03341,"mean_force":7.26929,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49767,0.01053,0.03688]},{"body_a":"peg","body_b":"channel_base_body","contact_count":170.0,"contact_point_centroid":[0.50708,-0.10034,0.05827],"force_p95":19.42494,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.07777,"mean_force":12.82462,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49798,-0.05293,0.03666]},{"body_a":"peg","body_b":"channel_base_body","contact_count":661.0,"contact_point_centroid":[0.50576,-0.01784,0.00984],"force_p95":15.90677,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.61236,"mean_force":6.56012,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49772,0.02569,0.03707]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50712,-0.0649,0.05584],"force_p95":10.12639,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.12639,"mean_force":10.12639,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49807,-0.05306,0.03664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50698,-0.10032,0.06079],"force_p95":10.01265,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.01265,"mean_force":10.01265,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49807,-0.05306,0.03664]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":482.0,"contact_point_centroid":[0.52506,-0.03211,0.03211],"force_p95":5.75097,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.52063,"mean_force":1.39448,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49775,-0.00409,0.03686]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50581,0.08087,0.00937],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56248,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49733,0.14364,0.21303]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49934,0.1983,0.2972]},{"body_a":"peg","body_b":"channel_base_body","contact_count":330.0,"contact_point_centroid":[0.50598,0.08087,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49765,0.10379,0.08835]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52504,-0.08254,0.01086],"force_p95":0.03143,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.03143,"mean_force":0.03143,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49807,-0.05306,0.03664]}],"total_contact_groups":12},"final_pose_error":0.02722,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50702,-0.08259,0.03581],"final_tcp_position":[0.49807,-0.05306,0.03664],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":84.52594,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":330.0,"raw_peak_contact_force":0.55006,"tcp_end":[0.49666,0.09224,0.13643],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1037,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":330.0,"n_steps_budget":690.0,"object_pos_end":[0.50597,0.08089,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":72.28632,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2694.0,"raw_peak_contact_force":84.52594,"tcp_end":[0.50091,0.11657,0.04105],"tcp_start":[0.49666,0.09224,0.13643],"tcp_to_object_dist_end":0.03676,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50703,-0.08259,0.03582],"object_pos_start":[0.50597,0.08089,0.03378],"object_to_goal_dist_end":0.00858,"object_to_goal_dist_start":0.16113,"object_z_max":0.0385,"peak_contact_force":81.10486,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4.0,"raw_peak_contact_force":81.10486,"tcp_end":[0.49807,-0.05306,0.03664],"tcp_start":[0.50091,0.11657,0.04105],"tcp_to_object_dist_end":0.03087,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50702,-0.08259,0.03581],"object_pos_start":[0.50703,-0.08259,0.03582],"object_to_goal_dist_end":0.00858,"object_to_goal_dist_start":0.00858,"object_z_max":0.03582,"peak_contact_force":0.54527,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1007.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.49807,-0.05306,0.03664],"tcp_start":[0.49807,-0.05306,0.03664],"tcp_to_object_dist_end":0.03087,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `54762c1e743ba455eff3c9979c2b42f5642abe1893e28eae37dc231d7efcd4e4`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,0.10464,0.04]},{"name":"goal","value":[0.5244,-0.05536,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.5244,-0.05536,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89189,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00527,"align_1.lateral_offset_y":-0.00994,"insert_1.insertion_depth":0.08524,"insert_1.insertion_force":10.59726,"push_1.push_distance":0.1252,"push_1.push_speed":0.1},"optimized_scores":{"best_composite_score":0.27342,"best_fitness_score":0.30009,"best_task_score":0.53454},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":87.0,"contact_point_centroid":[0.5119,0.12662,0.05531],"force_p95":143.85675,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":172.41615,"mean_force":104.3076,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50334,0.13283,0.05698]},{"body_a":"peg","body_b":"channel_base_body","contact_count":470.0,"contact_point_centroid":[0.50676,0.10684,0.00924],"force_p95":139.62812,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":160.16417,"mean_force":19.75337,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49871,0.11046,0.09608]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54268,-0.03886,0.05998],"force_p95":78.82234,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.82234,"mean_force":78.82234,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49806,-0.04339,0.03669]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":331.0,"contact_point_centroid":[0.54287,-0.02056,0.05998],"force_p95":77.92598,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.49413,"mean_force":58.42028,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49818,-0.02034,0.0368]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":77.0,"contact_point_centroid":[0.52512,0.10944,0.04998],"force_p95":25.61274,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.36916,"mean_force":9.55008,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50415,0.1344,0.05559]},{"body_a":"peg","body_b":"channel_base_body","contact_count":732.0,"contact_point_centroid":[0.50632,-0.0192,0.0099],"force_p95":13.50653,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.91934,"mean_force":5.17479,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49888,0.02596,0.0372]},{"body_a":"attachment","body_b":"peg","contact_count":888.0,"contact_point_centroid":[0.50378,0.0156,0.04262],"force_p95":12.78997,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.67879,"mean_force":3.98233,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49875,0.0273,0.03703]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":438.0,"contact_point_centroid":[0.52503,-0.00345,0.0285],"force_p95":2.36588,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.55178,"mean_force":0.52164,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4988,0.02541,0.03711]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49739,0.13784,0.22305]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49938,0.19825,0.29763]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50808,-0.08858,0.00999],"force_p95":0.56009,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56009,"mean_force":0.56009,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49806,-0.04339,0.03669]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50433,-0.05528,0.04534],"force_p95":0.48083,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48083,"mean_force":0.48083,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49806,-0.04339,0.03669]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,-0.07418,0.06],"force_p95":0.20802,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20802,"mean_force":0.20802,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49806,-0.04339,0.03669]}],"total_contact_groups":13},"final_pose_error":0.03681,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50687,-0.07248,0.03621],"final_tcp_position":[0.49806,-0.04339,0.03669],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":172.41615,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.43116,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":634.0,"raw_peak_contact_force":172.41615,"tcp_end":[0.4968,0.08149,0.1563],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12497,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":470.0,"n_steps_budget":870.0,"object_pos_end":[0.50676,0.09791,0.03655],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.17807,"object_to_goal_dist_start":0.18484,"object_z_max":0.03637,"peak_contact_force":72.97175,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2389.0,"raw_peak_contact_force":78.49413,"tcp_end":[0.50441,0.14061,0.04263],"tcp_start":[0.4968,0.08149,0.1563],"tcp_to_object_dist_end":0.0432,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50687,-0.07248,0.03621],"object_pos_start":[0.50676,0.09791,0.03655],"object_to_goal_dist_end":0.01087,"object_to_goal_dist_start":0.17807,"object_z_max":0.0382,"peak_contact_force":78.82234,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4.0,"raw_peak_contact_force":78.82234,"tcp_end":[0.49806,-0.04339,0.03669],"tcp_start":[0.50441,0.14061,0.04263],"tcp_to_object_dist_end":0.03039,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50687,-0.07248,0.03621],"object_pos_start":[0.50687,-0.07248,0.03621],"object_to_goal_dist_end":0.01087,"object_to_goal_dist_start":0.01087,"object_z_max":0.03621,"peak_contact_force":0.54104,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49806,-0.04339,0.03669],"tcp_start":[0.49806,-0.04339,0.03669],"tcp_to_object_dist_end":0.03039,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `b230a5798f38c3fb8968a6bc74f96ee85fe7026f3170cf8216fc868a1c5c570f`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,0.06746,0.04]},{"name":"goal","value":[0.50305,-0.09254,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50305,-0.09254,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88785,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00419,"align_1.lateral_offset_y":-0.00977,"insert_1.insertion_depth":0.08577,"insert_1.insertion_force":10.45092,"push_1.push_distance":0.05635,"push_1.push_speed":0.09388},"optimized_scores":{"best_composite_score":0.47525,"best_fitness_score":0.50192,"best_task_score":0.97085},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":508.0,"contact_point_centroid":[0.54198,-0.02224,0.05999],"force_p95":121.11453,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":143.83862,"mean_force":70.21901,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49721,-0.02215,0.03686]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54334,-0.05499,0.05998],"force_p95":113.61328,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":113.61328,"mean_force":113.61328,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49873,-0.05863,0.03651]},{"body_a":"attachment","body_b":"peg","contact_count":899.0,"contact_point_centroid":[0.50263,-0.01213,0.04339],"force_p95":78.45103,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":100.85851,"mean_force":20.44611,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49668,-0.0008,0.03701]},{"body_a":"peg","body_b":"channel_base_body","contact_count":253.0,"contact_point_centroid":[0.50496,-0.10219,0.05448],"force_p95":79.97157,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.34163,"mean_force":56.61744,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49834,-0.0574,0.03657]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50339,-0.07031,0.04636],"force_p95":59.20345,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.20345,"mean_force":59.20345,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49873,-0.05863,0.03651]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.5035,-0.10299,0.06027],"force_p95":59.20307,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.20307,"mean_force":59.20307,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49873,-0.05863,0.03651]},{"body_a":"peg","body_b":"channel_base_body","contact_count":703.0,"contact_point_centroid":[0.50558,-0.03115,0.00985],"force_p95":15.68603,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.49744,"mean_force":6.05433,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49655,0.01059,0.03722]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":385.0,"contact_point_centroid":[0.52505,-0.00243,0.02182],"force_p95":7.52041,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.54353,"mean_force":2.22756,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49595,0.02361,0.03714]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49737,0.14208,0.21682]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.50306,0.06745,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54665,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49644,0.09569,0.09171]}],"total_contact_groups":10},"final_pose_error":0.02169,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50323,-0.08787,0.03538],"final_tcp_position":[0.49873,-0.05863,0.03651],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":143.83862,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54567,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":333.0,"raw_peak_contact_force":0.55071,"tcp_end":[0.49669,0.08806,0.14209],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11043,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":333.0,"n_steps_budget":720.0,"object_pos_end":[0.50307,0.06743,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":110.57999,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2748.0,"raw_peak_contact_force":143.83862,"tcp_end":[0.49835,0.1043,0.04183],"tcp_start":[0.49669,0.08806,0.14209],"tcp_to_object_dist_end":0.03803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50322,-0.08786,0.03536],"object_pos_start":[0.50307,0.06743,0.0338],"object_to_goal_dist_end":0.00968,"object_to_goal_dist_start":0.14759,"object_z_max":0.03845,"peak_contact_force":113.61328,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3.0,"raw_peak_contact_force":113.61328,"tcp_end":[0.49873,-0.05863,0.03651],"tcp_start":[0.49835,0.1043,0.04183],"tcp_to_object_dist_end":0.02959,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50323,-0.08787,0.03538],"object_pos_start":[0.50322,-0.08786,0.03536],"object_to_goal_dist_end":0.00968,"object_to_goal_dist_start":0.00968,"object_z_max":0.03536,"peak_contact_force":0.54571,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49873,-0.05863,0.03651],"tcp_start":[0.49873,-0.05863,0.03651],"tcp_to_object_dist_end":0.02961,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```