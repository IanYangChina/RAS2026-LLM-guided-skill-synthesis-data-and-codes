## Search State

- **Seed**: 4
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3039 | 0.61 | ✅ accepted |
| 12 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.0093 | 0.08 | ❌ rejected |
| 11 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3041 | 0.61 | ❌ rejected |
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 4 | -0.1107 | 0.00 | ❌ rejected |
| 9 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3033 | 0.61 | ❌ rejected |

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
- **task_score** (E): 0.606
- **fitness_score**: 0.331  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| push_1 | 1.00 | 0.1889 |
| align_1 | 1.00 | 0.1053 |
| release_1 | 1.00 | 0.1730 |
| insert_1 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| push_1 | push | 1.00 / time_limit | (0.500, 0.200, 0.300)→(0.497, 0.096, 0.143) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.165 |
| align_1 | align | 1.00 / step_budget | (0.497, 0.096, 0.143)→(0.501, 0.121, 0.042) | (0.505, 0.084, 0.034)→(0.505, 0.082, 0.035) | 0.165→0.162 |
| release_1 | release | 1.00 / step_budget | (0.501, 0.121, 0.042)→(0.498, -0.052, 0.037) | (0.505, 0.082, 0.035)→(0.506, -0.081, 0.036) | 0.162→0.010 |
| insert_1 | insert | 1.00 / force_exceeded | (0.498, -0.052, 0.037)→(0.498, -0.052, 0.037) | (0.506, -0.081, 0.036)→(0.506, -0.081, 0.036) | 0.010→0.010 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.971
- alignment_error: None
- terminal_score: 0.971
- phase_score: 0.189
- phase_breakdown.push_score: 0.019
- phase_breakdown.approach_score: 0.888

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.502
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.971
- **Median Q (composite search score)**: 0.275
- **K-run variance**: 0.0167
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.261


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41045,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00268,"align_1.lateral_offset_y":0.00378,"insert_1.insertion_depth":0.06404,"insert_1.insertion_force":10.61831,"push_1.push_distance":0.06347,"push_1.push_speed":0.04383},"optimized_scores":{"best_composite_score":0.16215,"best_fitness_score":0.18882,"best_task_score":0.30969},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":470.0,"contact_point_centroid":[0.54244,-0.01577,0.05999],"force_p95":82.3492,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":94.49543,"mean_force":58.98412,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49768,-0.01554,0.03684]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5428,-0.05007,0.05998],"force_p95":84.89008,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":84.89008,"mean_force":84.89008,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49816,-0.05402,0.03662]},{"body_a":"attachment","body_b":"peg","contact_count":870.0,"contact_point_centroid":[0.5038,-0.00369,0.04504],"force_p95":26.83555,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.03815,"mean_force":9.01406,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49756,0.00788,0.03692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":187.0,"contact_point_centroid":[0.50694,-0.10059,0.05727],"force_p95":32.39244,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.71921,"mean_force":24.2256,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49803,-0.0538,0.03664]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50716,-0.06568,0.05584],"force_p95":24.13293,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.13293,"mean_force":24.13293,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49816,-0.05402,0.03662]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50698,-0.10062,0.0602],"force_p95":24.01879,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.01879,"mean_force":24.01879,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49816,-0.05402,0.03662]},{"body_a":"peg","body_b":"channel_base_body","contact_count":588.0,"contact_point_centroid":[0.50631,-0.01629,0.00983],"force_p95":15.47275,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.38848,"mean_force":5.84959,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49759,0.0271,0.0372]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":423.0,"contact_point_centroid":[0.52506,-0.01272,0.02392],"force_p95":5.28006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.54344,"mean_force":1.34221,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49749,0.0146,0.03695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":971.0,"contact_point_centroid":[0.50581,0.08087,0.00937],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.56248,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4974,0.14873,0.22358]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49933,0.19849,0.29756]},{"body_a":"peg","body_b":"channel_base_body","contact_count":377.0,"contact_point_centroid":[0.50602,0.08085,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49781,0.10941,0.09876]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,-0.08321,0.01023],"force_p95":0.06058,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.06058,"mean_force":0.06058,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49816,-0.05402,0.03662]}],"total_contact_groups":12},"final_pose_error":0.02627,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.507,-0.08322,0.03521],"final_tcp_position":[0.49816,-0.05402,0.03662],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.0809,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49679,0.10179,0.15643],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12476,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":377.0,"n_steps_budget":780.0,"object_pos_end":[0.50595,0.08088,0.03378],"object_pos_start":[0.50597,0.0809,0.03378],"object_to_goal_dist_end":0.16111,"object_to_goal_dist_start":0.16113,"object_z_max":0.03378,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.50108,0.11798,0.04174],"tcp_start":[0.49679,0.10179,0.15643],"tcp_to_object_dist_end":0.03825,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.507,-0.08322,0.03521],"object_pos_start":[0.50595,0.08088,0.03378],"object_to_goal_dist_end":0.00907,"object_to_goal_dist_start":0.16111,"object_z_max":0.038,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.49816,-0.05402,0.03662],"tcp_start":[0.50108,0.11798,0.04174],"tcp_to_object_dist_end":0.03054,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.507,-0.08322,0.03521],"object_pos_start":[0.507,-0.08322,0.03521],"object_to_goal_dist_end":0.00907,"object_to_goal_dist_start":0.00907,"object_z_max":0.03521,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.49816,-0.05402,0.03662],"tcp_start":[0.49816,-0.05402,0.03662],"tcp_to_object_dist_end":0.03055,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.88991,"average_solve_count":109.0,"average_success_count":109.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00549,"align_1.lateral_offset_y":0.00462,"insert_1.insertion_depth":0.12585,"insert_1.insertion_force":2.52127,"push_1.push_distance":0.06621,"push_1.push_speed":0.09586},"optimized_scores":{"best_composite_score":0.27467,"best_fitness_score":0.30134,"best_task_score":0.53825},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":88.0,"contact_point_centroid":[0.51125,0.12647,0.05536],"force_p95":145.30293,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":174.45007,"mean_force":101.42448,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50266,0.13259,0.05705]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.50706,0.10736,0.00918],"force_p95":142.29694,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":162.01788,"mean_force":25.00686,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4987,0.11734,0.08253]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":333.0,"contact_point_centroid":[0.54281,-0.01946,0.05998],"force_p95":78.31873,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":79.78498,"mean_force":58.38043,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.4981,-0.0193,0.03682]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54264,-0.03845,0.05998],"force_p95":78.73911,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":78.73911,"mean_force":78.73911,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49801,-0.04301,0.03671]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":86.0,"contact_point_centroid":[0.52513,0.1079,0.04529],"force_p95":23.61117,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.76913,"mean_force":8.45523,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50388,0.13533,0.05398]},{"body_a":"peg","body_b":"channel_base_body","contact_count":741.0,"contact_point_centroid":[0.50592,-0.01935,0.00991],"force_p95":13.73966,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.0248,"mean_force":5.1474,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49872,0.02545,0.03721]},{"body_a":"attachment","body_b":"peg","contact_count":899.0,"contact_point_centroid":[0.50353,0.01531,0.042],"force_p95":13.37562,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.72612,"mean_force":3.98108,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49857,0.02696,0.03704]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":526.0,"contact_point_centroid":[0.52505,-0.00202,0.02513],"force_p95":3.14598,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.2354,"mean_force":0.72017,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49864,0.02624,0.03709]},{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49731,0.14538,0.20887]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4994,0.19851,0.2975]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50356,-0.05475,0.04231],"force_p95":0.56128,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.56128,"mean_force":0.56128,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49801,-0.04301,0.03671]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50701,-0.08738,0.00999],"force_p95":0.54108,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54108,"mean_force":0.54108,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49801,-0.04301,0.03671]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":1.0,"contact_point_centroid":[0.52501,-0.07185,0.03582],"force_p95":0.39506,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.39506,"mean_force":0.39506,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49801,-0.04301,0.03671]}],"total_contact_groups":13},"final_pose_error":0.03719,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50701,-0.07193,0.03663],"final_tcp_position":[0.49801,-0.04301,0.03671],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49658,0.09533,0.12795],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.09504,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":363.0,"n_steps_budget":690.0,"object_pos_end":[0.50732,0.09807,0.03634],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.17826,"object_to_goal_dist_start":0.18484,"object_z_max":0.0362,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.50405,0.14039,0.04263],"tcp_start":[0.49658,0.09533,0.12795],"tcp_to_object_dist_end":0.04291,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,-0.07193,0.03663],"object_pos_start":[0.50732,0.09807,0.03634],"object_to_goal_dist_end":0.01121,"object_to_goal_dist_start":0.17826,"object_z_max":0.03754,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.49801,-0.04301,0.03671],"tcp_start":[0.50405,0.14039,0.04263],"tcp_to_object_dist_end":0.03029,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50701,-0.07193,0.03663],"object_pos_start":[0.50701,-0.07193,0.03663],"object_to_goal_dist_end":0.01121,"object_to_goal_dist_start":0.01121,"object_z_max":0.03663,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.49801,-0.04301,0.03671],"tcp_start":[0.49801,-0.04301,0.03671],"tcp_to_object_dist_end":0.03029,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89091,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00029,"align_1.lateral_offset_y":0.00195,"insert_1.insertion_depth":0.08462,"insert_1.insertion_force":17.29692,"push_1.push_distance":0.05676,"push_1.push_speed":0.08512},"optimized_scores":{"best_composite_score":0.47493,"best_fitness_score":0.50159,"best_task_score":0.97079},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":498.0,"contact_point_centroid":[0.54207,-0.0252,0.05999],"force_p95":120.39636,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":134.12214,"mean_force":70.22036,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49731,-0.02525,0.03685]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54355,-0.05519,0.05998],"force_p95":116.67328,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":116.67328,"mean_force":116.67328,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49895,-0.05882,0.03649]},{"body_a":"attachment","body_b":"peg","contact_count":863.0,"contact_point_centroid":[0.50294,-0.01517,0.04439],"force_p95":80.56889,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.80986,"mean_force":21.81089,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49672,-0.00381,0.037]},{"body_a":"peg","body_b":"channel_base_body","contact_count":259.0,"contact_point_centroid":[0.50564,-0.10225,0.05465],"force_p95":83.29234,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.33144,"mean_force":59.75433,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49848,-0.05767,0.03657]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50421,-0.07045,0.0474],"force_p95":65.61818,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.61818,"mean_force":65.61818,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49895,-0.05882,0.03649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.50426,-0.10306,0.05986],"force_p95":65.22956,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":65.22956,"mean_force":65.22956,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49895,-0.05882,0.03649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":665.0,"contact_point_centroid":[0.50535,-0.03247,0.00984],"force_p95":15.06178,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.11107,"mean_force":5.23456,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49656,0.00958,0.03726]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":397.0,"contact_point_centroid":[0.52509,-0.00829,0.02708],"force_p95":5.97504,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.66369,"mean_force":1.76126,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49599,0.01847,0.03715]},{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49738,0.1429,0.21812]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.49928,-0.10488,0.00993],"force_p95":0.60809,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60809,"mean_force":0.60809,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49895,-0.05882,0.03649]},{"body_a":"peg","body_b":"channel_base_body","contact_count":337.0,"contact_point_centroid":[0.503,0.06731,0.00938],"force_p95":0.55057,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54665,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49643,0.09644,0.09311]}],"total_contact_groups":11},"final_pose_error":0.0215,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50433,-0.08786,0.03501],"final_tcp_position":[0.49895,-0.05881,0.03649],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49668,0.08939,0.14427],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11282,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":337.0,"n_steps_budget":720.0,"object_pos_end":[0.50301,0.06748,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14764,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.49836,0.10446,0.04209],"tcp_start":[0.49668,0.08939,0.14427],"tcp_to_object_dist_end":0.03818,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50434,-0.08788,0.03503],"object_pos_start":[0.50301,0.06748,0.0338],"object_to_goal_dist_end":0.01028,"object_to_goal_dist_start":0.14764,"object_z_max":0.03825,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.49895,-0.05882,0.03649],"tcp_start":[0.49836,0.10446,0.04209],"tcp_to_object_dist_end":0.0296,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50433,-0.08786,0.03501],"object_pos_start":[0.50434,-0.08788,0.03503],"object_to_goal_dist_end":0.01027,"object_to_goal_dist_start":0.01028,"object_z_max":0.03503,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.49895,-0.05881,0.03649],"tcp_start":[0.49895,-0.05882,0.03649],"tcp_to_object_dist_end":0.02958,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```