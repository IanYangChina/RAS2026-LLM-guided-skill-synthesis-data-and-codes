## Search State

- **Seed**: 4
- **Iteration**: 5 / 15

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

## Current Skill (Q=0.305) — your mutation base

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

- **Composite score**: 0.305
- **task_score** (E): 0.606
- **fitness_score**: 0.331  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1915 |
| align_1 | 1.00 | 1.00 | 0.1087 |
| release_1 | 1.00 | 1.00 | 0.1727 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.089, 0.144) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.544 | 3.242 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.089, 0.144)→(0.501, 0.121, 0.042) | (0.505, 0.084, 0.034)→(0.505, 0.082, 0.034) | 0.165→0.162 | 1.00 / 1.000 | 0.549 | 63.405 |
| release_1 | release | 1.00 / step_budget | (0.501, 0.121, 0.042)→(0.498, -0.052, 0.037) | (0.505, 0.082, 0.034)→(0.506, -0.081, 0.036) | 0.162→0.009 | 1.00 / 3.333 | 84.723 | 99.328 |
| insert_1 | insert | 1.00 / force_exceeded | (0.498, -0.052, 0.037)→(0.498, -0.052, 0.037) | (0.506, -0.081, 0.036)→(0.506, -0.081, 0.036) | 0.009→0.009 | 1.00 / 3.333 | 91.265 | 91.265 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.970
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.970
- phase_score: 0.188
- phase_breakdown.push_score: 0.017
- phase_breakdown.contact_score: 0.000
- phase_breakdown.approach_score: 0.890

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.501
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.970
- **Median Q (composite search score)**: 0.276
- **K-run variance**: 0.0165
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.280


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88889,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00057,"align_1.lateral_offset_y":0.00544,"insert_1.insertion_depth":0.11857,"insert_1.insertion_force":6.03691,"push_1.push_distance":0.07844,"push_1.push_speed":0.09113},"optimized_scores":{"best_composite_score":0.16399,"best_fitness_score":0.19066,"best_task_score":0.30969},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":539.0,"contact_point_centroid":[0.54254,-0.00309,0.05999],"force_p95":79.40392,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":87.03426,"mean_force":58.24486,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49776,-0.00244,0.03683]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54263,-0.04873,0.05998],"force_p95":80.13864,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":80.13864,"mean_force":80.13864,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49799,-0.05276,0.03664]},{"body_a":"attachment","body_b":"peg","contact_count":874.0,"contact_point_centroid":[0.50377,0.00082,0.04455],"force_p95":15.89835,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.69009,"mean_force":5.85892,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49775,0.01246,0.03688]},{"body_a":"peg","body_b":"channel_base_body","contact_count":164.0,"contact_point_centroid":[0.50688,-0.10026,0.05958],"force_p95":17.20317,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.44811,"mean_force":8.67752,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49791,-0.05266,0.03664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":633.0,"contact_point_centroid":[0.50607,-0.01607,0.00986],"force_p95":16.16567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.378,"mean_force":6.28659,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49782,0.02773,0.03704]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":362.0,"contact_point_centroid":[0.52506,-0.01107,0.02731],"force_p95":4.00407,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.02707,"mean_force":0.88252,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49773,0.01661,0.03684]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50705,-0.06467,0.05592],"force_p95":6.34634,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.34634,"mean_force":6.34634,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49799,-0.05276,0.03664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50688,-0.10024,0.0608],"force_p95":6.23964,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.23964,"mean_force":6.23964,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49799,-0.05276,0.03664]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50581,0.08087,0.00937],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56248,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49736,0.14064,0.21832]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49933,0.1982,0.29727]},{"body_a":"peg","body_b":"channel_base_body","contact_count":369.0,"contact_point_centroid":[0.50606,0.08092,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49773,0.10084,0.09335]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52506,-0.08241,0.01091],"force_p95":0.04455,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.04455,"mean_force":0.04455,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49799,-0.05276,0.03664]}],"total_contact_groups":12},"final_pose_error":0.02752,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.507,-0.08244,0.03582],"final_tcp_position":[0.49799,-0.05276,0.03664],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":87.03426,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54527,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1007.0,"raw_peak_contact_force":4.32595,"tcp_end":[0.49671,0.08658,0.14683],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11358,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":369.0,"n_steps_budget":750.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54612,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":369.0,"raw_peak_contact_force":0.55006,"tcp_end":[0.50103,0.11631,0.0409],"tcp_start":[0.49671,0.08658,0.14683],"tcp_to_object_dist_end":0.0365,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,-0.08244,0.03582],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.00851,"object_to_goal_dist_start":0.16109,"object_z_max":0.03748,"peak_contact_force":73.44514,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2572.0,"raw_peak_contact_force":87.03426,"tcp_end":[0.49799,-0.05276,0.03664],"tcp_start":[0.50103,0.11631,0.0409],"tcp_to_object_dist_end":0.03102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.507,-0.08244,0.03582],"object_pos_start":[0.507,-0.08244,0.03582],"object_to_goal_dist_end":0.00851,"object_to_goal_dist_start":0.00851,"object_z_max":0.03582,"peak_contact_force":80.13864,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":80.13864,"tcp_end":[0.49799,-0.05276,0.03664],"tcp_start":[0.49799,-0.05276,0.03664],"tcp_to_object_dist_end":0.03103,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88785,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00747,"align_1.lateral_offset_y":0.00439,"insert_1.insertion_depth":0.04925,"insert_1.insertion_force":10.31675,"push_1.push_distance":0.07271,"push_1.push_speed":0.09991},"optimized_scores":{"best_composite_score":0.27581,"best_fitness_score":0.30248,"best_task_score":0.53716},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":99.0,"contact_point_centroid":[0.512,0.1273,0.05487],"force_p95":158.56178,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.11533,"mean_force":109.95542,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50315,0.13301,0.05656]},{"body_a":"peg","body_b":"channel_base_body","contact_count":379.0,"contact_point_centroid":[0.50749,0.10826,0.00916],"force_p95":145.47989,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":179.00622,"mean_force":29.16612,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49887,0.11633,0.0832]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54271,-0.03986,0.05998],"force_p95":78.89064,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.89064,"mean_force":78.89064,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49809,-0.04434,0.03669]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":306.0,"contact_point_centroid":[0.54284,-0.02531,0.05998],"force_p95":76.53467,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.91028,"mean_force":58.51959,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49816,-0.02543,0.0368]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":99.0,"contact_point_centroid":[0.52519,0.10944,0.0457],"force_p95":28.99885,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.74467,"mean_force":11.18582,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50424,0.13551,0.054]},{"body_a":"peg","body_b":"channel_base_body","contact_count":730.0,"contact_point_centroid":[0.50597,-0.01897,0.00991],"force_p95":12.76022,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.23096,"mean_force":4.83643,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49901,0.02614,0.03733]},{"body_a":"attachment","body_b":"peg","contact_count":886.0,"contact_point_centroid":[0.50381,0.01522,0.04249],"force_p95":12.77286,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.091,"mean_force":3.76877,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49883,0.02692,0.03713]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":433.0,"contact_point_centroid":[0.52505,0.01803,0.02157],"force_p95":3.93854,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.94123,"mean_force":1.05439,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49916,0.04641,0.03734]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49731,0.14394,0.20997]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4994,0.19845,0.29747]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50706,-0.08947,0.00999],"force_p95":0.6263,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6263,"mean_force":0.6263,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49809,-0.04434,0.03669]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50431,-0.05621,0.04508],"force_p95":0.30037,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.30037,"mean_force":0.30037,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49809,-0.04434,0.03669]}],"total_contact_groups":12},"final_pose_error":0.03586,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50697,-0.0734,0.03626],"final_tcp_position":[0.49809,-0.04434,0.03669],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":189.11533,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54104,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"tcp_end":[0.49658,0.0926,0.13018],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09755,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":379.0,"n_steps_budget":690.0,"object_pos_end":[0.5064,0.09837,0.03574],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.17853,"object_to_goal_dist_start":0.18484,"object_z_max":0.03553,"peak_contact_force":0.55109,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":577.0,"raw_peak_contact_force":189.11533,"tcp_end":[0.50483,0.1413,0.04308],"tcp_start":[0.49658,0.0926,0.13018],"tcp_to_object_dist_end":0.04359,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50697,-0.0734,0.03626],"object_pos_start":[0.5064,0.09837,0.03574],"object_to_goal_dist_end":0.01031,"object_to_goal_dist_start":0.17853,"object_z_max":0.03863,"peak_contact_force":72.31088,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2355.0,"raw_peak_contact_force":76.91028,"tcp_end":[0.49809,-0.04434,0.03669],"tcp_start":[0.50483,0.1413,0.04308],"tcp_to_object_dist_end":0.03038,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50697,-0.0734,0.03626],"object_pos_start":[0.50697,-0.0734,0.03626],"object_to_goal_dist_end":0.01031,"object_to_goal_dist_start":0.01031,"object_z_max":0.03626,"peak_contact_force":78.89064,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":78.89064,"tcp_end":[0.49809,-0.04434,0.03669],"tcp_start":[0.49809,-0.04434,0.03669],"tcp_to_object_dist_end":0.03039,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88696,"average_solve_count":115.0,"average_success_count":115.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00338,"align_1.lateral_offset_y":-0.00393,"insert_1.insertion_depth":0.07862,"insert_1.insertion_force":7.36007,"push_1.push_distance":0.07759,"push_1.push_speed":0.07606},"optimized_scores":{"best_composite_score":0.47429,"best_fitness_score":0.50096,"best_task_score":0.97002},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":506.0,"contact_point_centroid":[0.54208,-0.02409,0.05999],"force_p95":114.13766,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.03989,"mean_force":68.65703,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49732,-0.02405,0.03686]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54349,-0.05492,0.05998],"force_p95":114.7662,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":114.7662,"mean_force":114.7662,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49889,-0.05856,0.03649]},{"body_a":"attachment","body_b":"peg","contact_count":881.0,"contact_point_centroid":[0.50291,-0.01317,0.04437],"force_p95":73.95954,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.67804,"mean_force":20.45817,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49674,-0.00177,0.037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":254.0,"contact_point_centroid":[0.50504,-0.10224,0.05511],"force_p95":76.36409,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":95.92107,"mean_force":55.38669,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49844,-0.05735,0.03658]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50352,-0.07022,0.04612],"force_p95":60.07184,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.07184,"mean_force":60.07184,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49889,-0.05856,0.03649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50374,-0.10295,0.06029],"force_p95":60.05737,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.05737,"mean_force":60.05737,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49889,-0.05856,0.03649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":607.0,"contact_point_centroid":[0.50648,-0.02224,0.00981],"force_p95":17.06916,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.51127,"mean_force":6.73199,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49634,0.01953,0.03732]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":393.0,"contact_point_centroid":[0.52507,-0.00284,0.02232],"force_p95":7.26189,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.79501,"mean_force":2.07229,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49601,0.02335,0.03715]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49742,0.14162,0.22418]},{"body_a":"peg","body_b":"channel_base_body","contact_count":375.0,"contact_point_centroid":[0.50295,0.06739,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54665,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49653,0.0953,0.09891]}],"total_contact_groups":10},"final_pose_error":0.02175,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50344,-0.08774,0.03544],"final_tcp_position":[0.49889,-0.05856,0.03649],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":134.03989,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"tcp_end":[0.49677,0.08708,0.15637],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1243,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":375.0,"n_steps_budget":780.0,"object_pos_end":[0.50306,0.0675,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14766,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.5505,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":375.0,"raw_peak_contact_force":0.55071,"tcp_end":[0.49844,0.10446,0.04189],"tcp_start":[0.49677,0.08708,0.15637],"tcp_to_object_dist_end":0.03811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50343,-0.08772,0.03542],"object_pos_start":[0.50306,0.0675,0.0338],"object_to_goal_dist_end":0.00961,"object_to_goal_dist_start":0.14766,"object_z_max":0.03818,"peak_contact_force":108.41258,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":2641.0,"raw_peak_contact_force":134.03989,"tcp_end":[0.49889,-0.05856,0.03649],"tcp_start":[0.49844,0.10446,0.04189],"tcp_to_object_dist_end":0.02953,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50344,-0.08774,0.03544],"object_pos_start":[0.50343,-0.08772,0.03542],"object_to_goal_dist_end":0.00962,"object_to_goal_dist_start":0.00961,"object_z_max":0.03542,"peak_contact_force":114.7662,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":114.7662,"tcp_end":[0.49889,-0.05856,0.03649],"tcp_start":[0.49889,-0.05856,0.03649],"tcp_to_object_dist_end":0.02955,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```