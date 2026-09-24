## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 12  | -0.4202 | 0.28 | ❌ rejected |
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 12  | 0.0384 | 0.30 | ❌ rejected |
| 11 | approach → push → retract | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 7  | -0.5148 | 0.00 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 11  | -0.2562 | 0.00 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 10  | -0.3486 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.349) — your mutation base

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

- **Composite score**: -0.349
- **task_score** (E): 0.000
- **fitness_score**: 0.061  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_pre_push | 1.00 | 1.00 | 0.1709 |
| descend_to_peg | 1.00 | 1.00 | 0.1014 |
| push_along_channel | 1.00 | 1.00 | 0.0187 |
| retract_from_channel | 1.00 | 1.00 | 0.1715 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_pre_push | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.524, 0.095, 0.168) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 | 1.00 / 1.000 | 0.547 | 3.242 |
| descend_to_peg | descend | 1.00 / step_budget | (0.524, 0.095, 0.168)→(0.509, 0.086, 0.069) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.556 | 0.560 |
| push_along_channel | push | 1.00 / force_exceeded | (0.509, 0.086, 0.069)→(0.520, 0.074, 0.059) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.165→0.165 | 1.00 / 2.000 | 1002.876 | 1002.876 |
| retract_from_channel | retract | 1.00 / step_budget | (0.520, 0.074, 0.059)→(0.498, -0.070, 0.149) | (0.505, 0.084, 0.034)→(0.503, 0.085, 0.034) | 0.165→0.165 | 1.00 / 1.000 | 0.543 | 487.988 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.000
- phase_score: 0.116
- phase_breakdown.reach_pre_push_score: 0.239
- phase_breakdown.push_to_goal_score: 0.064

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.070
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.350
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.293


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42236,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_push.approach_speed":0.06145,"approach_pre_push.approach_tolerance":0.01198,"approach_pre_push.approach_x_offset":0.00717,"descend_to_peg.descend_speed":0.06351,"descend_to_peg.descend_tolerance":0.00777,"descend_to_peg.descend_x_offset":0.00881,"push_along_channel.push_distance":0.1173,"push_along_channel.push_force_threshold":20.11274,"push_along_channel.push_speed":0.08498,"push_along_channel.push_x_offset":-0.00413,"retract_from_channel.retract_speed":0.06544,"retract_from_channel.retract_tolerance":0.01233},"optimized_scores":{"best_composite_score":-0.34995,"best_fitness_score":0.06005,"best_task_score":8e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53529,0.07575,0.05939],"force_p95":1293.24206,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1293.24206,"mean_force":1293.24206,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.52411,0.07182,0.06068]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.53868,0.07294,0.05885],"force_p95":385.56246,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":585.40163,"mean_force":138.92614,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.52837,0.06717,0.05976]},{"body_a":"peg","body_b":"channel_base_body","contact_count":438.0,"contact_point_centroid":[0.5056,0.0809,0.00935],"force_p95":0.56052,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58161,"phase_index":0.0,"phase_name":"approach_pre_push","phase_type":"approach","tcp_position_centroid":[0.51786,0.14314,0.22914]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_pre_push","phase_type":"approach","tcp_position_centroid":[0.5004,0.19702,0.29599]},{"body_a":"peg","body_b":"channel_base_body","contact_count":665.0,"contact_point_centroid":[0.5058,0.08088,0.00939],"force_p95":0.57772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.46535,"mean_force":0.54908,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51078,-0.00092,0.10286]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.52365,0.07873,0.05862],"force_p95":0.86573,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.97749,"mean_force":0.25096,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.52854,0.06787,0.05855]},{"body_a":"peg","body_b":"channel_base_body","contact_count":239.0,"contact_point_centroid":[0.50598,0.0808,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5501,"mean_force":0.54676,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.52514,0.08675,0.11893]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.50911,0.08097,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54696,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51848,0.07803,0.06517]}],"total_contact_groups":8},"final_pose_error":0.01485,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50594,0.08086,0.03378],"final_tcp_position":[0.49862,-0.07022,0.1489],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":1293.24206,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":467.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.08089,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.55006,"phase_name":"approach_pre_push","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":474.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_pre_push","tcp_end":[0.53581,0.09148,0.16761],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13752,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":239.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.50599,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":0.54526,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":239.0,"raw_peak_contact_force":0.5501,"subtask_id":"reach_pre_push","tcp_end":[0.51503,0.08215,0.06859],"tcp_start":[0.53581,0.09148,0.16761],"tcp_to_object_dist_end":0.036,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":10.0,"n_steps_budget":900.0,"object_pos_end":[0.50596,0.08087,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"peak_contact_force":1293.24206,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":1293.24206,"subtask_id":"push_to_goal","tcp_end":[0.52542,0.07068,0.05979],"tcp_start":[0.51503,0.08215,0.06859],"tcp_to_object_dist_end":0.03404,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":665.0,"n_steps_budget":1000.0,"object_pos_end":[0.50594,0.08086,0.03378],"object_pos_start":[0.50596,0.08087,0.03378],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.1611,"object_z_max":0.0341,"peak_contact_force":0.54818,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":701.0,"raw_peak_contact_force":585.40163,"tcp_end":[0.49862,-0.07022,0.1489],"tcp_start":[0.52542,0.07068,0.05979],"tcp_to_object_dist_end":0.19009,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92632,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_push.approach_speed":0.13,"approach_pre_push.approach_tolerance":0.01681,"approach_pre_push.approach_x_offset":0.00985,"descend_to_peg.descend_speed":0.07996,"descend_to_peg.descend_tolerance":0.01488,"descend_to_peg.descend_x_offset":0.00875,"push_along_channel.push_distance":0.13226,"push_along_channel.push_force_threshold":23.58773,"push_along_channel.push_speed":0.06058,"push_along_channel.push_x_offset":-0.00371,"retract_from_channel.retract_speed":0.129,"retract_from_channel.retract_tolerance":0.01353},"optimized_scores":{"best_composite_score":-0.3555,"best_fitness_score":0.0545,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.53451,0.09978,0.05936],"force_p95":1338.64068,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1338.64068,"mean_force":1338.64068,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.52337,0.09574,0.06057]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":25.0,"contact_point_centroid":[0.53857,0.09733,0.05884],"force_p95":395.73526,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":602.25454,"mean_force":145.433,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.52835,0.09137,0.0597]},{"body_a":"peg","body_b":"channel_base_body","contact_count":355.0,"contact_point_centroid":[0.50552,0.10455,0.00936],"force_p95":0.58813,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57821,"phase_index":0.0,"phase_name":"approach_pre_push","phase_type":"approach","tcp_position_centroid":[0.51389,0.15479,0.22999]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_pre_push","phase_type":"approach","tcp_position_centroid":[0.50041,0.19739,0.29589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":665.0,"contact_point_centroid":[0.50581,0.10472,0.00939],"force_p95":0.58223,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.04684,"mean_force":0.54776,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51056,0.01155,0.10291]},{"body_a":"peg","body_b":"channel_base_body","contact_count":239.0,"contact_point_centroid":[0.5057,0.10484,0.00939],"force_p95":0.57553,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.54636,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5203,0.10976,0.11989]},{"body_a":"peg","body_b":"channel_base_body","contact_count":10.0,"contact_point_centroid":[0.50715,0.10031,0.00939],"force_p95":0.55144,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55174,"mean_force":0.5455,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.51723,0.10162,0.06513]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.52374,0.10314,0.05849],"force_p95":0.33631,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.45102,"mean_force":0.17488,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.52829,0.09215,0.0584]}],"total_contact_groups":8},"final_pose_error":0.01479,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50587,0.10474,0.03386],"final_tcp_position":[0.49851,-0.06972,0.14948],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":1338.64068,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":382.0,"n_steps_budget":840.0,"object_pos_end":[0.50583,0.10463,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18482,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54494,"phase_name":"approach_pre_push","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":387.0,"raw_peak_contact_force":3.33087,"subtask_id":"reach_pre_push","tcp_end":[0.52788,0.11418,0.1696],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13787,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":239.0,"n_steps_budget":930.0,"object_pos_end":[0.50597,0.10471,0.03384],"object_pos_start":[0.50583,0.10463,0.03384],"object_to_goal_dist_end":0.18491,"object_to_goal_dist_start":0.18482,"object_z_max":0.03384,"peak_contact_force":0.57562,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":239.0,"raw_peak_contact_force":0.57865,"subtask_id":"reach_pre_push","tcp_end":[0.51345,0.10554,0.0686],"tcp_start":[0.52788,0.11418,0.1696],"tcp_to_object_dist_end":0.03557,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.50585,0.1047,0.03384],"object_pos_start":[0.50597,0.10471,0.03384],"object_to_goal_dist_end":0.1849,"object_to_goal_dist_start":0.18491,"object_z_max":0.03384,"peak_contact_force":1338.64068,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":1338.64068,"subtask_id":"push_to_goal","tcp_end":[0.52482,0.09468,0.05967],"tcp_start":[0.51345,0.10554,0.0686],"tcp_to_object_dist_end":0.03358,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":665.0,"n_steps_budget":990.0,"object_pos_end":[0.50587,0.10474,0.03386],"object_pos_start":[0.50585,0.1047,0.03384],"object_to_goal_dist_end":0.18494,"object_to_goal_dist_start":0.1849,"object_z_max":0.03396,"peak_contact_force":0.54073,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":700.0,"raw_peak_contact_force":602.25454,"tcp_end":[0.49851,-0.06972,0.14948],"tcp_start":[0.52482,0.09468,0.05967],"tcp_to_object_dist_end":0.20942,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18719,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_pre_push.approach_speed":0.04188,"approach_pre_push.approach_tolerance":0.01409,"approach_pre_push.approach_x_offset":0.00807,"descend_to_peg.descend_speed":0.03494,"descend_to_peg.descend_tolerance":0.01077,"descend_to_peg.descend_x_offset":-0.00178,"push_along_channel.push_distance":0.14067,"push_along_channel.push_force_threshold":30.15403,"push_along_channel.push_speed":0.06822,"push_along_channel.push_x_offset":0.00281,"retract_from_channel.retract_speed":0.09086,"retract_from_channel.retract_tolerance":0.01082},"optimized_scores":{"best_composite_score":-0.34024,"best_fitness_score":0.06976,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.50604,0.06804,0.00938],"force_p95":188.64732,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":376.74436,"mean_force":34.74619,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5031,0.06415,0.06464]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.52014,0.06179,0.05807],"force_p95":376.11824,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":376.11824,"mean_force":376.11824,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50921,0.05725,0.05932]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52559,0.05521,0.05991],"force_p95":208.36104,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":276.30894,"mean_force":87.55994,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51301,0.0544,0.05322]},{"body_a":"peg","body_b":"channel_base_body","contact_count":616.0,"contact_point_centroid":[0.49966,0.0661,0.00945],"force_p95":34.3666,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":231.22923,"mean_force":5.59619,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50296,-0.00684,0.10038]},{"body_a":"attachment","body_b":"peg","contact_count":71.0,"contact_point_centroid":[0.51711,0.0601,0.05692],"force_p95":217.82112,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":230.97547,"mean_force":43.95337,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.51044,0.05043,0.05709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":465.0,"contact_point_centroid":[0.50308,0.06741,0.00933],"force_p95":0.56429,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56515,"phase_index":0.0,"phase_name":"approach_pre_push","phase_type":"approach","tcp_position_centroid":[0.50294,0.13861,0.23134]},{"body_a":"peg","body_b":"channel_base_body","contact_count":256.0,"contact_point_centroid":[0.50293,0.06761,0.00938],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55098,"mean_force":0.54665,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50252,0.07409,0.11925]}],"total_contact_groups":7},"final_pose_error":0.01479,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49817,0.06862,0.03482],"final_tcp_position":[0.49773,-0.07085,0.1486],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":376.74436,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.50301,0.06745,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14761,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54698,"phase_name":"approach_pre_push","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":465.0,"raw_peak_contact_force":2.06903,"subtask_id":"reach_pre_push","tcp_end":[0.50735,0.07921,0.16796],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13475,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":256.0,"n_steps_budget":1000.0,"object_pos_end":[0.50309,0.06748,0.0338],"object_pos_start":[0.50301,0.06745,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14761,"object_z_max":0.0338,"peak_contact_force":0.54738,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":256.0,"raw_peak_contact_force":0.55098,"subtask_id":"reach_pre_push","tcp_end":[0.49897,0.06898,0.06854],"tcp_start":[0.50735,0.07921,0.16796],"tcp_to_object_dist_end":0.03501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.50322,0.06737,0.03381],"object_pos_start":[0.50309,0.06748,0.0338],"object_to_goal_dist_end":0.14753,"object_to_goal_dist_start":0.14764,"object_z_max":0.0338,"peak_contact_force":376.74436,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":12.0,"raw_peak_contact_force":376.74436,"subtask_id":"push_to_goal","tcp_end":[0.51045,0.05606,0.05803],"tcp_start":[0.49897,0.06898,0.06854],"tcp_to_object_dist_end":0.0277,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":616.0,"n_steps_budget":1000.0,"object_pos_end":[0.49817,0.06862,0.03482],"object_pos_start":[0.50322,0.06737,0.03381],"object_to_goal_dist_end":0.14872,"object_to_goal_dist_start":0.14753,"object_z_max":0.03807,"peak_contact_force":0.54063,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":698.0,"raw_peak_contact_force":276.30894,"tcp_end":[0.49773,-0.07085,0.1486],"tcp_start":[0.51045,0.05606,0.05803],"tcp_to_object_dist_end":0.17999,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```