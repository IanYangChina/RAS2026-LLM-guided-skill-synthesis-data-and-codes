## Search State

- **Seed**: 1
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0494 | 0.19 | ❌ rejected |
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1472 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`
- Frozen object start: [0.5009457299760205, 0.11603709570607482, 0.04]
- Frozen task target: [0.5009457299760205, -0.04396290429392519, 0.04]
- Goal object position: (0.5009457299760205, -0.04396290429392519, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, 0.11603709570607482, 0.04)
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
  frozen_object_start: [0.5009, 0.116, 0.04]
  frozen_task_target: [0.5009, -0.044, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5009457299760205, 0.11603709570607482, 0.04]}
  frozen_targets: {'channel_exit': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a

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
| `object` | offset from object initial position (0.5009457299760205, 0.11603709570607482, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5009457299760205, -0.04396290429392519, 0.04) | final destination targets |
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

## Current Skill (Q=-0.049) — your mutation base

```yaml
skill: peg_channel
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
- id: align_2
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

```

## Design Metrics

- **Composite score**: -0.049
- **task_score** (E): 0.190
- **fitness_score**: 0.261  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_to_peg | 1.00 | 0.1889 |
| descend_to_contact | 1.00 | 0.0976 |
| push_through_channel | 0.00 | 0.0011 |
| retract_upward | 1.00 | 0.0883 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_to_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.106, 0.139) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 |
| descend_to_contact | descend | 1.00 / step_budget | (0.481, 0.106, 0.139)→(0.499, 0.103, 0.044) | (0.497, 0.080, 0.034)→(0.500, 0.056, 0.037) | 0.160→0.136 |
| push_through_channel | push | 0.00 / guard_failure | (0.506, 0.091, 0.035)→(0.507, 0.091, 0.035) | (0.500, 0.056, 0.037)→(0.500, 0.048, 0.035) | 0.136→0.128 |
| retract_upward | retract | 1.00 / step_budget | (0.507, 0.091, 0.035)→(0.503, 0.090, 0.123) | (0.500, 0.046, 0.034)→(0.499, 0.033, 0.024) | 0.126→0.115 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.300
- alignment_error: None
- terminal_score: 0.300
- phase_score: 0.301
- phase_breakdown.reach_goal_score: 0.045

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.301
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.300
- **Median Q (composite search score)**: -0.053
- **K-run variance**: 0.0010
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.270


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a904e23429ae963dd2788b3e8d0575d9ce341e1daddfe013fbb1224c3e0c850e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6bee39a4c127c6d39ee1365e3969a50bb09484f7e2580b1a3dc4d8c4ae20213b`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.06742,"average_solve_count":89.0,"average_success_count":89.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.approach_height":0.09087,"descend_to_contact.contact_offset_x":0.00986,"push_through_channel.force_guard_threshold":20.06045,"push_through_channel.lateral_retry_offset":0.00916,"push_through_channel.push_distance":0.08333},"optimized_scores":{"best_composite_score":-0.00943,"best_fitness_score":0.30057,"best_task_score":0.3003},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52506,0.11964,0.03722],"force_p95":634.02577,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":639.48537,"mean_force":539.51314,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.52281,0.13106,0.03615]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":24.0,"contact_point_centroid":[0.55465,0.11969,0.05886],"force_p95":315.37201,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":374.45673,"mean_force":102.55046,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.51881,0.13927,0.02578]},{"body_a":"peg","body_b":"channel_base_body","contact_count":364.0,"contact_point_centroid":[0.50529,0.11715,0.0091],"force_p95":169.57187,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":178.84103,"mean_force":40.59434,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50236,0.13869,0.08573]},{"body_a":"attachment","body_b":"peg","contact_count":117.0,"contact_point_centroid":[0.51546,0.13162,0.05332],"force_p95":175.64262,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":177.87853,"mean_force":124.69972,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50888,0.13994,0.05387]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.525,0.11995,0.05501],"force_p95":48.06008,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.42716,"mean_force":31.55803,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.51998,0.13098,0.05039]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50878,0.13218,0.04794],"force_p95":3.17085,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.17619,"mean_force":3.12288,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51367,0.14255,0.04606]},{"body_a":"peg","body_b":"channel_base_body","contact_count":558.0,"contact_point_centroid":[0.50398,0.0696,0.00814],"force_p95":0.72064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.07877,"mean_force":0.60435,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.52007,0.1309,0.0746]},{"body_a":"peg","body_b":"channel_base_body","contact_count":13.0,"contact_point_centroid":[0.49461,0.10288,0.00785],"force_p95":2.29755,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.29826,"mean_force":1.24229,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.51829,0.13679,0.04154]},{"body_a":"peg","body_b":"channel_base_body","contact_count":508.0,"contact_point_centroid":[0.50102,0.11602,0.00937],"force_p95":0.62377,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.5599,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49808,0.16955,0.21727]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52501,0.04418,0.02417],"force_p95":0.40998,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41259,"mean_force":0.3865,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.51945,0.13101,0.05218]}],"total_contact_groups":10},"final_pose_error":0.01273,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50474,0.06799,0.02414],"final_tcp_position":[0.52068,0.12967,0.1215],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"phases":[{"n_steps":524.0,"n_steps_budget":1000.0,"object_pos_end":[0.50097,0.11598,0.03387],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19608,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.49777,0.14028,0.13932],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.10826,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":364.0,"n_steps_budget":690.0,"object_pos_end":[0.50122,0.11447,0.03179],"object_pos_start":[0.50097,0.11598,0.03387],"object_to_goal_dist_end":0.19464,"object_to_goal_dist_start":0.19608,"object_z_max":0.034,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.51359,0.14273,0.04627],"tcp_start":[0.49777,0.14028,0.13932],"tcp_to_object_dist_end":0.03408,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":13.0,"n_steps_budget":600.0,"object_pos_end":[0.50135,0.10586,0.03358],"object_pos_start":[0.50122,0.11447,0.03179],"object_to_goal_dist_end":0.18598,"object_to_goal_dist_start":0.19464,"object_z_max":0.03401,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.52407,0.13059,0.03374],"tcp_start":[0.52343,0.13064,0.03488],"tcp_to_object_dist_end":0.03358,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":572.0,"n_steps_budget":630.0,"object_pos_end":[0.50474,0.06799,0.02414],"object_pos_start":[0.50144,0.10463,0.03445],"object_to_goal_dist_end":0.14891,"object_to_goal_dist_start":0.18472,"object_z_max":0.04024,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.52068,0.12967,0.1215],"tcp_start":[0.52407,0.13059,0.03374],"tcp_to_object_dist_end":0.11635,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.98958,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.approach_height":0.09471,"descend_to_contact.contact_offset_x":-0.00178,"push_through_channel.force_guard_threshold":32.0851,"push_through_channel.lateral_retry_offset":-0.00301,"push_through_channel.push_distance":0.04385},"optimized_scores":{"best_composite_score":-0.05292,"best_fitness_score":0.25708,"best_task_score":0.19039},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54045,0.07737,0.05945],"force_p95":1078.12559,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1098.28992,"mean_force":961.11707,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49512,0.07559,0.03656]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":18.0,"contact_point_centroid":[0.53953,0.08518,0.05915],"force_p95":251.70053,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":323.71971,"mean_force":97.66893,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49589,0.07232,0.03662]},{"body_a":"peg","body_b":"channel_base_body","contact_count":340.0,"contact_point_centroid":[0.49648,0.06403,0.00922],"force_p95":124.33739,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":174.56442,"mean_force":18.77775,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48294,0.08769,0.09102]},{"body_a":"attachment","body_b":"peg","contact_count":59.0,"contact_point_centroid":[0.49718,0.0807,0.05595],"force_p95":149.27641,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":174.04059,"mean_force":105.24484,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48804,0.08605,0.05858]},{"body_a":"peg","body_b":"channel_base_body","contact_count":539.0,"contact_point_centroid":[0.49712,0.01684,0.00792],"force_p95":0.81723,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.41328,"mean_force":0.62994,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49247,0.073,0.07951]},{"body_a":"peg","body_b":"channel_base_body","contact_count":583.0,"contact_point_centroid":[0.49549,0.06394,0.00937],"force_p95":0.57832,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56014,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.48843,0.1435,0.21618]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49921,0.19811,0.29724]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49855,0.04498,0.00996],"force_p95":0.57272,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60162,"mean_force":0.36546,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49409,0.07814,0.03841]}],"total_contact_groups":8},"final_pose_error":0.01203,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49438,0.01739,0.02399],"final_tcp_position":[0.49243,0.07316,0.12405],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":610.0,"n_steps_budget":1000.0,"object_pos_end":[0.49495,0.06404,0.03395],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14425,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.47912,0.09107,0.14116],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11169,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":348.0,"n_steps_budget":690.0,"object_pos_end":[0.49906,0.03393,0.03893],"object_pos_start":[0.49495,0.06404,0.03395],"object_to_goal_dist_end":0.11394,"object_to_goal_dist_start":0.14425,"object_z_max":0.04042,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.48994,0.08511,0.04316],"tcp_start":[0.47912,0.09107,0.14116],"tcp_to_object_dist_end":0.05215,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.49927,0.02676,0.03483],"object_pos_start":[0.49906,0.03393,0.03893],"object_to_goal_dist_end":0.10689,"object_to_goal_dist_start":0.11394,"object_z_max":0.03893,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.49574,0.07374,0.0356],"tcp_start":[0.49548,0.0746,0.03592],"tcp_to_object_dist_end":0.04712,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":546.0,"n_steps_budget":630.0,"object_pos_end":[0.49438,0.01739,0.02399],"object_pos_start":[0.49932,0.02509,0.03374],"object_to_goal_dist_end":0.09886,"object_to_goal_dist_start":0.10528,"object_z_max":0.03374,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49243,0.07316,0.12405],"tcp_start":[0.49574,0.07374,0.0356],"tcp_to_object_dist_end":0.11457,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.05208,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.approach_height":0.09098,"descend_to_contact.contact_offset_x":0.00558,"push_through_channel.force_guard_threshold":29.91006,"push_through_channel.lateral_retry_offset":-0.01048,"push_through_channel.push_distance":0.07056},"optimized_scores":{"best_composite_score":-0.08582,"best_fitness_score":0.22418,"best_task_score":0.07823},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54516,0.07172,0.05939],"force_p95":1578.92096,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1617.63811,"mean_force":1244.95275,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50008,0.07026,0.03593]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":2.0,"contact_point_centroid":[0.52515,0.07181,0.05993],"force_p95":1496.70644,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1529.90397,"mean_force":1197.92869,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.50027,0.06971,0.03557]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":17.0,"contact_point_centroid":[0.54378,0.0802,0.05908],"force_p95":292.28997,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":334.13486,"mean_force":174.52098,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.5004,0.06702,0.03604]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52548,0.07023,0.05976],"force_p95":223.16433,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.47685,"mean_force":107.81277,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.50068,0.06694,0.03538]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.49652,0.06027,0.0092],"force_p95":136.74584,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":180.03803,"mean_force":23.08179,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47834,0.08276,0.08927]},{"body_a":"attachment","body_b":"peg","contact_count":75.0,"contact_point_centroid":[0.49911,0.07543,0.05554],"force_p95":151.89528,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":179.37022,"mean_force":109.20443,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4903,0.08111,0.05796]},{"body_a":"peg","body_b":"channel_base_body","contact_count":601.0,"contact_point_centroid":[0.4943,0.05902,0.00936],"force_p95":0.56367,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57055,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.48162,0.14092,0.21418]},{"body_a":"peg","body_b":"channel_base_body","contact_count":540.0,"contact_point_centroid":[0.49841,0.01087,0.00823],"force_p95":0.78378,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.7296,"mean_force":0.61991,"phase_index":3.0,"phase_name":"retract_upward","phase_type":"retract","tcp_position_centroid":[0.49735,0.06766,0.07866]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.4988,0.19755,0.29628]}],"total_contact_groups":9},"final_pose_error":0.0121,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49713,0.01465,0.02409],"final_tcp_position":[0.49733,0.06777,0.12337],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"phases":[{"n_steps":630.0,"n_steps_budget":1000.0,"object_pos_end":[0.49404,0.05885,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13911,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.46593,0.08622,0.13752],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11082,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":380.0,"n_steps_budget":690.0,"object_pos_end":[0.49896,0.01981,0.04017],"object_pos_start":[0.49404,0.05885,0.03388],"object_to_goal_dist_end":0.09982,"object_to_goal_dist_start":0.13911,"object_z_max":0.04201,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","tcp_end":[0.49497,0.08012,0.0424],"tcp_start":[0.46593,0.08622,0.13752],"tcp_to_object_dist_end":0.06049,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":11.0,"n_steps_budget":600.0,"object_pos_end":[0.49931,0.01048,0.03516],"object_pos_start":[0.49896,0.01981,0.04017],"object_to_goal_dist_end":0.09062,"object_to_goal_dist_start":0.09982,"object_z_max":0.04017,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"reach_goal","tcp_end":[0.50067,0.06832,0.03498],"tcp_start":[0.50042,0.06922,0.0353],"tcp_to_object_dist_end":0.05785,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":545.0,"n_steps_budget":630.0,"object_pos_end":[0.49713,0.01465,0.02409],"object_pos_start":[0.49939,0.00841,0.03362],"object_to_goal_dist_end":0.09602,"object_to_goal_dist_start":0.08864,"object_z_max":0.03847,"phase_name":"retract_upward","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49733,0.06777,0.12337],"tcp_start":[0.50067,0.06832,0.03498],"tcp_to_object_dist_end":0.11259,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```