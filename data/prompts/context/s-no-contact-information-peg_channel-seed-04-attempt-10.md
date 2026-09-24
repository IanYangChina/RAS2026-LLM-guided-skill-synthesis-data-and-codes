## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | time_limit | 4 | -0.1107 | 0.00 | ❌ rejected |
| 9 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3033 | 0.61 | ❌ rejected |
| 8 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3046 | 0.61 | ✅ accepted |
| 7 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.3046 | 0.60 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 8 | 0.0566 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.111) — your mutation base

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

- **Composite score**: -0.111
- **task_score** (E): 0.000
- **fitness_score**: 0.119  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_peg | 1.00 | 0.2124 |
| contact_peg | 0.00 | 0.0781 |
| push_through | 1.00 | 0.0655 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.516, 0.140, 0.098) | (0.521, 0.084, 0.040)→(0.505, 0.084, 0.034) | 0.166→0.164 |
| contact_peg | contact | 0.00 / step_budget | (0.516, 0.140, 0.098)→(0.502, 0.069, 0.071) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.164→0.164 |
| push_through | push | 1.00 / time_limit | (0.502, 0.069, 0.071)→(0.499, 0.004, 0.072) | (0.505, 0.084, 0.034)→(0.505, 0.084, 0.034) | 0.164→0.165 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- terminal_score: 0.000
- phase_score: 0.204
- phase_breakdown.behind_peg_score: 0.268
- phase_breakdown.push_to_goal_score: 0.188

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.123
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.112
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.400


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.07229,"average_solve_count":166.0,"average_success_count":166.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.appr_speed":0.0274,"contact_peg.contact_force":8.58651,"push_through.push_dist":0.08003,"push_through.push_speed":0.05381},"optimized_scores":{"best_composite_score":-0.11313,"best_fitness_score":0.11687,"best_task_score":4e-05},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":410.0,"contact_point_centroid":[0.50565,0.08091,0.00935],"force_p95":0.56113,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58398,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.51423,0.16709,0.19322]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50023,0.19832,0.29497]},{"body_a":"peg","body_b":"channel_base_body","contact_count":533.0,"contact_point_centroid":[0.50595,0.08089,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5501,"mean_force":0.54677,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.51482,0.10114,0.08165]},{"body_a":"peg","body_b":"channel_base_body","contact_count":695.0,"contact_point_centroid":[0.50595,0.08086,0.00938],"force_p95":0.55006,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55006,"mean_force":0.54677,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50002,0.03417,0.06925]}],"total_contact_groups":4},"final_pose_error":0.00734,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50598,0.08089,0.03378],"final_tcp_position":[0.49936,0.00385,0.07188],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"phases":[{"n_steps":439.0,"n_steps_budget":1000.0,"object_pos_end":[0.50597,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"behind_peg","tcp_end":[0.52875,0.1372,0.09737],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08796,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":533.0,"n_steps_budget":600.0,"object_pos_end":[0.50599,0.08087,0.03378],"object_pos_start":[0.50597,0.08086,0.03378],"object_to_goal_dist_end":0.1611,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"behind_peg","tcp_end":[0.50389,0.06567,0.0706],"tcp_start":[0.52875,0.1372,0.09737],"tcp_to_object_dist_end":0.03989,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":695.0,"n_steps_budget":780.0,"object_pos_end":[0.50598,0.08089,0.03378],"object_pos_start":[0.50599,0.08087,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.1611,"object_z_max":0.03378,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.49936,0.00385,0.07188],"tcp_start":[0.50389,0.06567,0.0706],"tcp_to_object_dist_end":0.0862,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59596,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.appr_speed":0.09877,"contact_peg.contact_force":2.5127,"push_through.push_dist":0.08001,"push_through.push_speed":0.05892},"optimized_scores":{"best_composite_score":-0.11162,"best_fitness_score":0.11838,"best_task_score":0.00023},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":367.0,"contact_point_centroid":[0.50558,0.10458,0.00936],"force_p95":0.58318,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.57716,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50929,0.17807,0.19336]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50032,0.19869,0.29449]},{"body_a":"peg","body_b":"channel_base_body","contact_count":533.0,"contact_point_centroid":[0.50589,0.10464,0.00939],"force_p95":0.57564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57865,"mean_force":0.54633,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.50951,0.12349,0.08223]},{"body_a":"peg","body_b":"channel_base_body","contact_count":881.0,"contact_point_centroid":[0.50589,0.10469,0.00939],"force_p95":0.57568,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57576,"mean_force":0.54632,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49934,0.0462,0.06944]}],"total_contact_groups":4},"final_pose_error":0.00751,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50594,0.10456,0.03384],"final_tcp_position":[0.49889,0.00423,0.07237],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"phases":[{"n_steps":394.0,"n_steps_budget":1000.0,"object_pos_end":[0.50584,0.10459,0.03383],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"behind_peg","tcp_end":[0.51896,0.15858,0.09842],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08519,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":533.0,"n_steps_budget":600.0,"object_pos_end":[0.50584,0.10459,0.03384],"object_pos_start":[0.50584,0.10459,0.03383],"object_to_goal_dist_end":0.18479,"object_to_goal_dist_start":0.18479,"object_z_max":0.03384,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"behind_peg","tcp_end":[0.50309,0.08909,0.07069],"tcp_start":[0.51896,0.15858,0.09842],"tcp_to_object_dist_end":0.04008,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":881.0,"n_steps_budget":960.0,"object_pos_end":[0.50594,0.10456,0.03384],"object_pos_start":[0.50584,0.10459,0.03384],"object_to_goal_dist_end":0.18476,"object_to_goal_dist_start":0.18479,"object_z_max":0.03384,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.49889,0.00423,0.07237],"tcp_start":[0.50309,0.08909,0.07069],"tcp_to_object_dist_end":0.10771,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65421,"average_solve_count":107.0,"average_success_count":107.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.appr_speed":0.08133,"contact_peg.contact_force":4.51493,"push_through.push_dist":0.08021,"push_through.push_speed":0.03999},"optimized_scores":{"best_composite_score":-0.10736,"best_fitness_score":0.12264,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":400.0,"contact_point_centroid":[0.50311,0.06749,0.00932],"force_p95":0.58632,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.56815,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49944,0.1618,0.19589]},{"body_a":"peg","body_b":"channel_base_body","contact_count":541.0,"contact_point_centroid":[0.50306,0.06742,0.00938],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55115,"mean_force":0.54665,"phase_index":1.0,"phase_name":"contact_peg","phase_type":"contact","tcp_position_centroid":[0.49799,0.08896,0.08228]},{"body_a":"peg","body_b":"channel_base_body","contact_count":734.0,"contact_point_centroid":[0.50299,0.06749,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55074,"mean_force":0.54665,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49694,0.0267,0.06933]}],"total_contact_groups":3},"final_pose_error":0.00688,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50308,0.06748,0.0338],"final_tcp_position":[0.49783,0.00301,0.07168],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"phases":[{"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.50305,0.06742,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"behind_peg","tcp_end":[0.49982,0.12513,0.09766],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08614,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":541.0,"n_steps_budget":600.0,"object_pos_end":[0.50302,0.06743,0.0338],"object_pos_start":[0.50305,0.06742,0.0338],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14758,"object_z_max":0.0338,"phase_name":"contact_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","subtask_id":"behind_peg","tcp_end":[0.49917,0.05244,0.07079],"tcp_start":[0.49982,0.12513,0.09766],"tcp_to_object_dist_end":0.04009,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":734.0,"n_steps_budget":840.0,"object_pos_end":[0.50308,0.06748,0.0338],"object_pos_start":[0.50302,0.06743,0.0338],"object_to_goal_dist_end":0.14765,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.49783,0.00301,0.07168],"tcp_start":[0.49917,0.05244,0.07079],"tcp_to_object_dist_end":0.07497,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```