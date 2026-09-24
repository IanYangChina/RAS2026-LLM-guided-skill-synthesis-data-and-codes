## Search State

- **Seed**: 1
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.2016 | 0.27 | ❌ rejected |
| 12 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1527 | 0.31 | ❌ rejected |
| 11 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.2183 | 0.00 | ❌ rejected |
| 10 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 5 | -0.1004 | 0.00 | ❌ rejected |
| 9 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1157 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.27 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.202) — your mutation base

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

- **Composite score**: 0.202
- **task_score** (E): 0.275
- **fitness_score**: 0.402  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2648 |
| push_1 | 1.00 | 1.00 | 0.1279 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.483, 0.099, 0.057) | (0.483, 0.080, 0.040)→(0.498, 0.079, 0.032) | 0.161→0.159 | 1.00 / 1.333 | 0.883 | 99.940 |
| push_1 | push | 1.00 / time_limit | (0.483, 0.099, 0.057)→(0.482, -0.029, 0.059) | (0.498, 0.079, 0.032)→(0.499, 0.013, 0.029) | 0.159→0.094 | 1.00 / 2.333 | 184.006 | 224.809 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.465
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.465
- phase_score: 0.482
- phase_breakdown.pre_push_score: 0.736
- phase_breakdown.push_task_score: 0.373

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.475
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.465
- **Median Q (composite search score)**: 0.243
- **K-run variance**: 0.0068
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.367


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.42188,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.16805,"approach_1.lateral_offset_x":-0.00993,"push_1.push_distance":0.14411,"push_1.push_lateral_x":-0.00122},"optimized_scores":{"best_composite_score":0.27518,"best_fitness_score":0.47518,"best_task_score":0.46494},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":961.0,"contact_point_centroid":[0.50101,0.11626,0.00929],"force_p95":85.41296,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":190.4327,"mean_force":8.23891,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49303,0.16376,0.17118]},{"body_a":"attachment","body_b":"peg","contact_count":73.0,"contact_point_centroid":[0.50072,0.13079,0.05381],"force_p95":150.45111,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":189.8872,"mean_force":101.20472,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49,0.13255,0.05721]},{"body_a":"peg","body_b":"channel_base_body","contact_count":838.0,"contact_point_centroid":[0.50234,0.07626,0.00809],"force_p95":119.47404,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":141.28943,"mean_force":67.59991,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49125,0.06578,0.05558]},{"body_a":"attachment","body_b":"peg","contact_count":654.0,"contact_point_centroid":[0.50244,0.08342,0.05309],"force_p95":120.52844,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":140.59764,"mean_force":85.96143,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49273,0.08106,0.05596]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":20.0,"contact_point_centroid":[0.475,0.00799,0.05964],"force_p95":38.2345,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.56898,"mean_force":21.51083,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48569,0.00801,0.05419]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47496,0.03759,0.05014],"force_p95":0.80709,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.82841,"mean_force":0.63912,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48663,0.02393,0.05382]}],"total_contact_groups":6},"final_pose_error":0.00908,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50285,0.04165,0.02414],"final_tcp_position":[0.48526,-0.00515,0.05488],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":190.4327,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":977.0,"n_steps_budget":1000.0,"object_pos_end":[0.50293,0.11541,0.02817],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19579,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.66594,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1516.0,"raw_peak_contact_force":141.28943,"subtask_id":"pre_push","tcp_end":[0.49227,0.13202,0.05116],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0303,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":842.0,"n_steps_budget":900.0,"object_pos_end":[0.50285,0.04165,0.02414],"object_pos_start":[0.50293,0.11541,0.02817],"object_to_goal_dist_end":0.12271,"object_to_goal_dist_start":0.19579,"object_z_max":0.04039,"peak_contact_force":146.9182,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1034.0,"raw_peak_contact_force":190.4327,"subtask_id":"push_task","tcp_end":[0.48526,-0.00515,0.05488],"tcp_start":[0.49227,0.13202,0.05116],"tcp_to_object_dist_end":0.05869,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.44444,"average_solve_count":63.0,"average_success_count":63.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1643,"approach_1.lateral_offset_x":0.00266,"push_1.push_distance":0.13045,"push_1.push_lateral_x":0.0029},"optimized_scores":{"best_composite_score":0.2429,"best_fitness_score":0.4429,"best_task_score":0.27847},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.49532,0.06391,0.00938],"force_p95":0.56573,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.55747,"mean_force":1.38254,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48973,0.14184,0.17735]},{"body_a":"attachment","body_b":"peg","contact_count":14.0,"contact_point_centroid":[0.49135,0.08111,0.05809],"force_p95":71.69866,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.13108,"mean_force":57.72735,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48173,0.08627,0.06221]},{"body_a":"peg","body_b":"channel_base_body","contact_count":780.0,"contact_point_centroid":[0.49574,0.02038,0.00915],"force_p95":56.04526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.61001,"mean_force":39.60081,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48379,0.026,0.06201]},{"body_a":"attachment","body_b":"peg","contact_count":697.0,"contact_point_centroid":[0.4937,0.03416,0.05775],"force_p95":56.39167,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.23224,"mean_force":43.78532,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48369,0.03283,0.06198]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49937,0.19883,0.29784]}],"total_contact_groups":5},"final_pose_error":0.00911,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49652,-0.01179,0.03794],"final_tcp_position":[0.48471,-0.03809,0.06226],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":77.55747,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4956,0.06337,0.03318],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.1436,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":1.41483,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1477.0,"raw_peak_contact_force":62.61001,"subtask_id":"pre_push","tcp_end":[0.48192,0.08563,0.06092],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.0381,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":782.0,"n_steps_budget":840.0,"object_pos_end":[0.49652,-0.01179,0.03794],"object_pos_start":[0.4956,0.06337,0.03318],"object_to_goal_dist_end":0.06832,"object_to_goal_dist_start":0.1436,"object_z_max":0.04074,"peak_contact_force":77.55747,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1015.0,"raw_peak_contact_force":77.55747,"subtask_id":"push_task","tcp_end":[0.48471,-0.03809,0.06226],"tcp_start":[0.48192,0.08563,0.06092],"tcp_to_object_dist_end":0.03772,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.42373,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.19096,"approach_1.lateral_offset_x":0.00226,"push_1.push_distance":0.1295,"push_1.push_lateral_x":0.00186},"optimized_scores":{"best_composite_score":0.08685,"best_fitness_score":0.28685,"best_task_score":0.0802},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":57.0,"contact_point_centroid":[0.47493,0.09141,0.05987],"force_p95":361.92465,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":406.43685,"mean_force":316.88049,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47136,0.08041,0.06183]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":332.0,"contact_point_centroid":[0.47499,0.05286,0.05999],"force_p95":79.05536,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.92073,"mean_force":56.92602,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47586,0.04404,0.05963]},{"body_a":"attachment","body_b":"peg","contact_count":21.0,"contact_point_centroid":[0.48272,0.07113,0.05918],"force_p95":79.61674,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.51155,"mean_force":20.58803,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47391,0.07907,0.06057]},{"body_a":"peg","body_b":"channel_base_body","contact_count":893.0,"contact_point_centroid":[0.4946,0.05871,0.00937],"force_p95":0.58579,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":92.4271,"mean_force":1.04334,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4826,0.13625,0.17091]},{"body_a":"peg","body_b":"channel_base_body","contact_count":740.0,"contact_point_centroid":[0.50107,0.02451,0.00906],"force_p95":5.03574,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.41787,"mean_force":1.43385,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47607,0.02031,0.0596]},{"body_a":"attachment","body_b":"peg","contact_count":159.0,"contact_point_centroid":[0.48849,0.05343,0.06367],"force_p95":17.97634,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.24612,"mean_force":4.6681,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47572,0.06015,0.05974]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":40.0,"contact_point_centroid":[0.52501,0.02375,0.05719],"force_p95":8.6635,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.67161,"mean_force":3.267,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47601,0.03535,0.05954]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47494,0.03022,0.02395],"force_p95":5.46216,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.85837,"mean_force":1.38276,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47612,0.00815,0.0594]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49911,0.19843,0.29689]}],"total_contact_groups":9},"final_pose_error":0.00933,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49874,0.00972,0.02415],"final_tcp_position":[0.47703,-0.04387,0.06006],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":406.43685,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":922.0,"n_steps_budget":960.0,"object_pos_end":[0.4954,0.05756,0.03452],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13775,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.56829,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1281.0,"raw_peak_contact_force":95.92073,"subtask_id":"pre_push","tcp_end":[0.47503,0.07865,0.05974],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":752.0,"n_steps_budget":810.0,"object_pos_end":[0.49874,0.00972,0.02415],"object_pos_start":[0.4954,0.05756,0.03452],"object_to_goal_dist_end":0.09111,"object_to_goal_dist_start":0.13775,"object_z_max":0.04081,"peak_contact_force":327.54305,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1006.0,"raw_peak_contact_force":406.43685,"subtask_id":"push_task","tcp_end":[0.47703,-0.04387,0.06006],"tcp_start":[0.47503,0.07865,0.05974],"tcp_to_object_dist_end":0.06806,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```