## Search State

- **Seed**: 4
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 12  | 0.0384 | 0.30 | ❌ rejected |
| 11 | approach → push → retract | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7  | -0.5148 | 0.00 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11  | -0.2562 | 0.00 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10  | -0.4386 | 0.49 | ❌ rejected |
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 20  | -0.4202 | 0.28 | ❌ rejected |

**Proposal policy**: task_score is 0.28 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.420) — your mutation base

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

- **Composite score**: -0.420
- **task_score** (E): 0.277
- **fitness_score**: 0.240  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_push | 1.00 | 1.00 | 0.1665 |
| descend_to_peg | 1.00 | 1.00 | 0.0853 |
| push_along_channel | 0.33 | 1.00 | 0.1013 |
| retract_from_channel | 1.00 | 1.00 | 0.0906 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_push | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.517, 0.139, 0.147) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.556 | 3.242 |
| descend_to_peg | descend | 1.00 / step_budget | (0.517, 0.139, 0.147)→(0.507, 0.134, 0.063) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.164 | 1.00 / 1.000 | 0.543 | 0.559 |
| push_along_channel | push | 0.33 / step_budget | (0.507, 0.134, 0.063)→(0.502, 0.036, 0.041) | (0.505, 0.084, 0.034)→(0.503, 0.038, 0.032) | 0.164→0.119 | 1.00 / 1.667 | 30.277 | 14.460 |
| retract_from_channel | retract | 1.00 / step_budget | (0.502, 0.036, 0.041)→(0.499, 0.035, 0.132) | (0.503, 0.038, 0.032)→(0.505, 0.039, 0.031) | 0.119→0.119 | 1.00 / 1.000 | 0.557 | 2.389 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.554
- alignment_error: None
- force_efficiency: 0.519
- terminal_score: 0.554
- phase_score: 0.179
- phase_breakdown.reach_pre_push_score: 0.212
- phase_breakdown.push_to_goal_score: 0.165

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.329
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.554
- **Median Q (composite search score)**: -0.430
- **K-run variance**: 0.0048
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.340


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82946,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_push.approach_speed":0.09506,"approach_pre_push.approach_tolerance":0.01137,"approach_pre_push.approach_x_offset":0.00373,"descend_to_peg.approach_x_offset":0.00966,"descend_to_peg.descend_speed":0.08552,"descend_to_peg.descend_tolerance":0.01356,"push_along_channel.approach_x_offset":-0.00369,"push_along_channel.push_distance":0.1918,"push_along_channel.push_force_threshold":30.97719,"push_along_channel.push_speed":0.09997,"retract_from_channel.retract_speed":0.06968,"retract_from_channel.retract_tolerance":0.01855},"optimized_scores":{"best_composite_score":-0.43041,"best_fitness_score":0.22959,"best_task_score":0.08192},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":997.0,"contact_point_centroid":[0.50034,0.04835,0.00879],"force_p95":9.33265,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.35663,"mean_force":2.25845,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50712,0.04994,0.04906]},{"body_a":"attachment","body_b":"peg","contact_count":239.0,"contact_point_centroid":[0.50742,0.07121,0.05379],"force_p95":10.58712,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.00329,"mean_force":7.07844,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50908,0.08301,0.05324]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47499,0.01095,0.02424],"force_p95":6.42141,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.47986,"mean_force":2.17058,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5048,0.01182,0.0441]},{"body_a":"peg","body_b":"channel_base_body","contact_count":521.0,"contact_point_centroid":[0.50566,0.08086,0.00936],"force_p95":0.55849,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.57605,"phase_index":0.0,"phase_name":"approach_pre_push","phase_type":"approach","tcp_position_centroid":[0.51636,0.16613,0.21869]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_pre_push","phase_type":"approach","tcp_position_centroid":[0.50028,0.19825,0.29597]},{"body_a":"peg","body_b":"channel_base_body","contact_count":791.0,"contact_point_centroid":[0.50142,0.03337,0.00801],"force_p95":0.72554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.81676,"mean_force":0.6058,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49903,-0.03174,0.08376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":250.0,"contact_point_centroid":[0.5061,0.08088,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55007,"mean_force":0.54678,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.52361,0.13278,0.1054]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.525,0.05616,0.02415],"force_p95":0.38863,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38863,"mean_force":0.38863,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49906,-0.0317,0.12745]}],"total_contact_groups":8},"final_pose_error":0.01011,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50455,0.03308,0.02418],"final_tcp_position":[0.49914,-0.0317,0.12917],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":12.35663,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":550.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54526,"phase_name":"approach_pre_push","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":557.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_pre_push","tcp_end":[0.53313,0.13526,0.14645],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12802,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":250.0,"n_steps_budget":720.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50598,0.0809,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":0.54819,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":250.0,"raw_peak_contact_force":0.55007,"subtask_id":"reach_pre_push","tcp_end":[0.51496,0.1307,0.06354],"tcp_start":[0.53313,0.13526,0.14645],"tcp_to_object_dist_end":0.05874,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49808,0.03368,0.0241],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.1148,"object_to_goal_dist_start":0.1611,"object_z_max":0.04043,"peak_contact_force":0.63683,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1240.0,"raw_peak_contact_force":12.35663,"subtask_id":"push_to_goal","tcp_end":[0.50246,-0.03178,0.03872],"tcp_start":[0.51496,0.1307,0.06354],"tcp_to_object_dist_end":0.06722,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":791.0,"n_steps_budget":900.0,"object_pos_end":[0.50455,0.03308,0.02418],"object_pos_start":[0.49808,0.03368,0.0241],"object_to_goal_dist_end":0.11427,"object_to_goal_dist_start":0.1148,"object_z_max":0.02417,"peak_contact_force":0.57317,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":792.0,"raw_peak_contact_force":0.81676,"tcp_end":[0.49914,-0.0317,0.12917],"tcp_start":[0.50246,-0.03178,0.03872],"tcp_to_object_dist_end":0.12349,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.48148,"average_solve_count":108.0,"average_success_count":108.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_push.approach_speed":0.12753,"approach_pre_push.approach_tolerance":0.01497,"approach_pre_push.approach_x_offset":-0.00448,"descend_to_peg.approach_x_offset":0.00035,"descend_to_peg.descend_speed":0.07166,"descend_to_peg.descend_tolerance":0.01431,"push_along_channel.approach_x_offset":-0.00128,"push_along_channel.push_distance":0.15986,"push_along_channel.push_force_threshold":35.77612,"push_along_channel.push_speed":0.07637,"retract_from_channel.retract_speed":0.04833,"retract_from_channel.retract_tolerance":0.01461},"optimized_scores":{"best_composite_score":-0.49949,"best_fitness_score":0.16051,"best_task_score":0.19569},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":199.0,"contact_point_centroid":[0.50628,0.10114,0.00943],"force_p95":0.88674,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.96063,"mean_force":0.73543,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50118,0.14185,0.0577]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50296,0.12096,0.05735],"force_p95":6.52164,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.71168,"mean_force":3.56135,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50051,0.13266,0.05554]},{"body_a":"attachment","body_b":"peg","contact_count":53.0,"contact_point_centroid":[0.50125,0.11706,0.05868],"force_p95":0.50832,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":5.43606,"mean_force":0.37936,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49848,0.12871,0.05905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":946.0,"contact_point_centroid":[0.50571,0.10263,0.00946],"force_p95":0.57953,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.43337,"mean_force":0.5449,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49726,0.12854,0.10012]},{"body_a":"peg","body_b":"channel_base_body","contact_count":451.0,"contact_point_centroid":[0.5055,0.10468,0.00937],"force_p95":0.57903,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57143,"phase_index":0.0,"phase_name":"approach_pre_push","phase_type":"approach","tcp_position_centroid":[0.50716,0.1777,0.21986]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_pre_push","phase_type":"approach","tcp_position_centroid":[0.49992,0.19878,0.29637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":263.0,"contact_point_centroid":[0.50607,0.10472,0.00939],"force_p95":0.57562,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57678,"mean_force":0.5463,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50899,0.15552,0.10592]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52503,0.10173,0.05935],"force_p95":0.42058,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57225,"mean_force":0.108,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49852,0.12883,0.06274]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":6.0,"contact_point_centroid":[0.52505,0.09965,0.06],"force_p95":0.12429,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13111,"mean_force":0.0637,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5005,0.12983,0.05514]}],"total_contact_groups":9},"final_pose_error":0.00998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50586,0.10434,0.0338],"final_tcp_position":[0.49741,0.1286,0.14561],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":89.94655,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":478.0,"n_steps_budget":840.0,"object_pos_end":[0.50597,0.10471,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.57503,"phase_name":"approach_pre_push","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":483.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_pre_push","tcp_end":[0.51526,0.15752,0.14819],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":263.0,"n_steps_budget":840.0,"object_pos_end":[0.50598,0.1046,0.03384],"object_pos_start":[0.50597,0.10471,0.03383],"object_to_goal_dist_end":0.1848,"object_to_goal_dist_start":0.18491,"object_z_max":0.03384,"peak_contact_force":0.5357,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":263.0,"raw_peak_contact_force":0.57678,"subtask_id":"reach_pre_push","tcp_end":[0.50414,0.15406,0.0633],"tcp_start":[0.51526,0.15752,0.14819],"tcp_to_object_dist_end":0.0576,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":199.0,"n_steps_budget":1000.0,"object_pos_end":[0.50656,0.10186,0.03651],"object_pos_start":[0.50598,0.1046,0.03384],"object_to_goal_dist_end":0.18201,"object_to_goal_dist_start":0.1848,"object_z_max":0.03649,"peak_contact_force":89.94655,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":217.0,"raw_peak_contact_force":6.96063,"subtask_id":"push_to_goal","tcp_end":[0.5005,0.12939,0.05507],"tcp_start":[0.50414,0.15406,0.0633],"tcp_to_object_dist_end":0.03375,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":946.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,0.10434,0.0338],"object_pos_start":[0.50656,0.10186,0.03651],"object_to_goal_dist_end":0.18454,"object_to_goal_dist_start":0.18201,"object_z_max":0.03694,"peak_contact_force":0.55009,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1006.0,"raw_peak_contact_force":5.43606,"tcp_end":[0.49741,0.1286,0.14561],"tcp_start":[0.5005,0.12939,0.05507],"tcp_to_object_dist_end":0.11473,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5037,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_push.approach_speed":0.11346,"approach_pre_push.approach_tolerance":0.01554,"approach_pre_push.approach_x_offset":0.00182,"descend_to_peg.approach_x_offset":0.00468,"descend_to_peg.descend_speed":0.05345,"descend_to_peg.descend_tolerance":0.01552,"push_along_channel.approach_x_offset":0.00503,"push_along_channel.push_distance":0.06321,"push_along_channel.push_force_threshold":25.5839,"push_along_channel.push_speed":0.06718,"retract_from_channel.retract_speed":0.07207,"retract_from_channel.retract_tolerance":0.01568},"optimized_scores":{"best_composite_score":-0.33071,"best_fitness_score":0.32929,"best_task_score":0.55434},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":942.0,"contact_point_centroid":[0.50469,0.02907,0.00976],"force_p95":19.92681,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.06227,"mean_force":9.17074,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50218,0.0666,0.0455]},{"body_a":"attachment","body_b":"peg","contact_count":739.0,"contact_point_centroid":[0.50398,0.04408,0.04271],"force_p95":19.93809,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.75296,"mean_force":11.13958,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50258,0.05579,0.04265]},{"body_a":"peg","body_b":"channel_base_body","contact_count":509.0,"contact_point_centroid":[0.5031,0.06744,0.00934],"force_p95":0.55807,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56355,"phase_index":0.0,"phase_name":"approach_pre_push","phase_type":"approach","tcp_position_centroid":[0.49998,0.16083,0.22114]},{"body_a":"peg","body_b":"channel_base_body","contact_count":761.0,"contact_point_centroid":[0.50406,-0.02129,0.0094],"force_p95":0.55942,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.91307,"mean_force":0.54903,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50042,0.00929,0.07565]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52504,-0.01385,0.01239],"force_p95":0.87173,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.88321,"mean_force":0.77446,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50374,0.01503,0.03187]},{"body_a":"peg","body_b":"channel_base_body","contact_count":295.0,"contact_point_centroid":[0.50302,0.06756,0.00938],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55092,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50135,0.12011,0.10506]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50427,-0.00253,0.03064],"force_p95":0.25981,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27349,"mean_force":0.13674,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50386,0.00942,0.03039]}],"total_contact_groups":7},"final_pose_error":0.0101,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50399,-0.02123,0.0338],"final_tcp_position":[0.5005,0.00932,0.12089],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":24.06227,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":525.0,"n_steps_budget":990.0,"object_pos_end":[0.50303,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54808,"phase_name":"approach_pre_push","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":509.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_pre_push","tcp_end":[0.50154,0.12314,0.14752],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12664,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50303,0.06743,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54525,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":295.0,"raw_peak_contact_force":0.55092,"subtask_id":"reach_pre_push","tcp_end":[0.50325,0.11744,0.0625],"tcp_start":[0.50154,0.12314,0.14752],"tcp_to_object_dist_end":0.05766,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50482,-0.02047,0.03542],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.0599,"object_to_goal_dist_start":0.14759,"object_z_max":0.04053,"peak_contact_force":0.24857,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1684.0,"raw_peak_contact_force":24.06227,"subtask_id":"push_to_goal","tcp_end":[0.50388,0.00946,0.03041],"tcp_start":[0.50325,0.11744,0.0625],"tcp_to_object_dist_end":0.03036,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":763.0,"n_steps_budget":870.0,"object_pos_end":[0.50399,-0.02123,0.0338],"object_pos_start":[0.50482,-0.02047,0.03542],"object_to_goal_dist_end":0.05923,"object_to_goal_dist_start":0.0599,"object_z_max":0.03542,"peak_contact_force":0.54685,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":763.0,"raw_peak_contact_force":0.91307,"tcp_end":[0.5005,0.00932,0.12089],"tcp_start":[0.50388,0.00946,0.03041],"tcp_to_object_dist_end":0.09236,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```