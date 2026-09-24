## Search State

- **Seed**: 1
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | align → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | 0.3426 | 0.36 | ❌ rejected |
| 1 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1706 | 0.42 | ✅ accepted |
| 0 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1472 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5009457299760205, -0.04396290429392519, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5009457299760205, -0.04396290429392519, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5009457299760205, 0.11603709570607482, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5009457299760205, 0.11603709570607482, 0.04]
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
  frozen_object_starts: {'peg': [0.5009457299760205, -0.04396290429392519, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
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
| `object` | offset from object initial position (0.5009457299760205, -0.04396290429392519, 0.04) | approach/contact targets near object start |
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

## Current Skill (Q=0.343) — your mutation base

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

- **Composite score**: 0.343
- **task_score** (E): 0.364
- **fitness_score**: 0.543  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_behind | 1.00 | 1.00 | 0.2620 |
| push_channel | 1.00 | 1.00 | 0.1685 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_behind | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.101, 0.061) | (0.483, 0.080, 0.040)→(0.497, 0.079, 0.035) | 0.161→0.159 | 1.00 / 2.000 | 198.592 | 208.888 |
| push_channel | push | 1.00 / step_budget | (0.481, 0.101, 0.061)→(0.500, -0.065, 0.038) | (0.497, 0.079, 0.035)→(0.497, -0.005, 0.035) | 0.159→0.076 | 1.00 / 3.333 | 281.876 | 321.238 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.730
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.730
- phase_score: 0.762
- phase_breakdown.alignment_score: 0.728
- phase_breakdown.push_completion_score: 0.777

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.749
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.730
- **Median Q (composite search score)**: 0.302
- **K-run variance**: 0.0240
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.321


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
{"anchors":[{"name":"object","value":[0.50095,-0.04396,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,-0.04396,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.26744,"average_solve_count":172.0,"average_success_count":172.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.offset_y":0.02952,"align_behind.offset_z":0.01131,"push_channel.push_distance":0.17628,"push_channel.push_speed":0.02846},"optimized_scores":{"best_composite_score":0.54935,"best_fitness_score":0.74935,"best_task_score":0.73001},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":179.0,"contact_point_centroid":[0.52505,-0.03145,0.05998],"force_p95":235.40573,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":274.10884,"mean_force":172.00445,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50071,-0.0314,0.03653]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":186.0,"contact_point_centroid":[0.54513,-0.03738,0.05995],"force_p95":215.15145,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":229.18502,"mean_force":177.23231,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.5007,-0.03131,0.03653]},{"body_a":"peg","body_b":"channel_base_body","contact_count":680.0,"contact_point_centroid":[0.49991,0.03933,0.00939],"force_p95":76.7389,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":80.42024,"mean_force":32.29801,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49866,0.03503,0.04429]},{"body_a":"attachment","body_b":"peg","contact_count":434.0,"contact_point_centroid":[0.50387,0.04815,0.04399],"force_p95":77.631,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.87149,"mean_force":51.45826,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49843,0.04591,0.04564]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":69.0,"contact_point_centroid":[0.52507,0.07476,0.05581],"force_p95":24.42429,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.5299,"mean_force":19.70171,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49505,0.11221,0.05245]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47499,0.03924,0.04985],"force_p95":22.43414,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.70425,"mean_force":16.72974,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50192,-0.01637,0.03963]},{"body_a":"peg","body_b":"channel_base_body","contact_count":727.0,"contact_point_centroid":[0.50089,0.11601,0.00939],"force_p95":0.61944,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55436,"phase_index":0.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.49775,0.17315,0.17738]}],"total_contact_groups":7},"final_pose_error":0.02858,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49646,-0.00076,0.03937],"final_tcp_position":[0.50065,-0.03181,0.03663],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":274.10884,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":743.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11601,0.03387],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19611,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.55731,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":727.0,"raw_peak_contact_force":1.92055,"subtask_id":"alignment","tcp_end":[0.49714,0.14757,0.06027],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04131,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":684.0,"n_steps_budget":1000.0,"object_pos_end":[0.49646,-0.00076,0.03937],"object_pos_start":[0.50096,0.11601,0.03387],"object_to_goal_dist_end":0.07932,"object_to_goal_dist_start":0.19611,"object_z_max":0.04078,"peak_contact_force":203.18947,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1576.0,"raw_peak_contact_force":274.10884,"subtask_id":"push_completion","tcp_end":[0.50065,-0.03181,0.03663],"tcp_start":[0.49714,0.14757,0.06027],"tcp_to_object_dist_end":0.03145,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `8416ac3bebb4dbec2abbf751596843a33db171fd8d70765023f3b940d846bd0c`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,-0.09612,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.09612,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33766,"average_solve_count":154.0,"average_success_count":154.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.offset_y":0.0147,"align_behind.offset_z":0.00578,"push_channel.push_distance":0.1603,"push_channel.push_speed":0.03945},"optimized_scores":{"best_composite_score":0.3024,"best_fitness_score":0.5024,"best_task_score":0.25542},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":31.0,"contact_point_centroid":[0.47487,0.09631,0.05975],"force_p95":325.77114,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":327.7701,"mean_force":302.35074,"phase_index":0.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.47923,0.08542,0.05739]},{"body_a":"channel_base_body","body_b":"link7","contact_count":177.0,"contact_point_centroid":[0.54022,-0.10001,0.06496],"force_p95":257.33651,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":258.81667,"mean_force":209.31308,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49737,-0.07243,0.03807]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":64.0,"contact_point_centroid":[0.53486,-0.05034,0.05998],"force_p95":171.86379,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":182.16212,"mean_force":124.43596,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48962,-0.05219,0.03792]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":225.0,"contact_point_centroid":[0.47499,0.05883,0.05851],"force_p95":137.49158,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":141.82256,"mean_force":107.77205,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48425,0.05471,0.05375]},{"body_a":"attachment","body_b":"peg","contact_count":438.0,"contact_point_centroid":[0.49482,0.01481,0.04361],"force_p95":94.9987,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":103.81016,"mean_force":47.40968,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48579,0.01651,0.04778]},{"body_a":"peg","body_b":"channel_base_body","contact_count":701.0,"contact_point_centroid":[0.5048,0.00549,0.00961],"force_p95":77.24447,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.56319,"mean_force":20.60052,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48879,-0.00265,0.04593]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":621.0,"contact_point_centroid":[0.52525,-0.00574,0.03503],"force_p95":55.96613,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.91009,"mean_force":17.98456,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48974,-0.01583,0.04417]},{"body_a":"peg","body_b":"channel_base_body","contact_count":833.0,"contact_point_centroid":[0.49574,0.06311,0.00938],"force_p95":0.77468,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.59674,"mean_force":0.88811,"phase_index":0.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.48779,0.13907,0.16971]},{"body_a":"attachment","body_b":"peg","contact_count":29.0,"contact_point_centroid":[0.48803,0.07596,0.06134],"force_p95":34.78568,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.47503,"mean_force":9.68828,"phase_index":0.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.47919,0.08585,0.05825]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":234.0,"contact_point_centroid":[0.47495,-0.00655,0.05318],"force_p95":4.11299,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.647,"mean_force":1.03928,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49617,-0.06971,0.03799]},{"body_a":"peg","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.51034,-0.00932,0.0729],"force_p95":0.99808,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.29497,"mean_force":0.29556,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48633,-0.04016,0.03836]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.49931,0.19848,0.29704]}],"total_contact_groups":12},"final_pose_error":0.02229,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5,-0.01873,0.04024],"final_tcp_position":[0.49991,-0.07724,0.03841],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":327.7701,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":860.0,"n_steps_budget":1000.0,"object_pos_end":[0.49656,0.06113,0.03621],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14122,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":303.23776,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":921.0,"raw_peak_contact_force":327.7701,"subtask_id":"alignment","tcp_end":[0.48001,0.0851,0.05746],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03606,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":761.0,"n_steps_budget":1000.0,"object_pos_end":[0.5,-0.01873,0.04024],"object_pos_start":[0.49656,0.06113,0.03621],"object_to_goal_dist_end":0.06127,"object_to_goal_dist_start":0.14122,"object_z_max":0.04287,"peak_contact_force":222.53754,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2469.0,"raw_peak_contact_force":258.81667,"subtask_id":"push_completion","tcp_end":[0.49991,-0.07724,0.03841],"tcp_start":[0.48001,0.0851,0.05746],"tcp_to_object_dist_end":0.05854,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0188121de1b8142d5ff7a7406b62c43adf6da5520b986a997e46ef53b7d11bf9`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,-0.10106,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,-0.10106,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29213,"average_solve_count":178.0,"average_success_count":178.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_behind.offset_y":0.00509,"align_behind.offset_z":0.01622,"push_channel.push_distance":0.1767,"push_channel.push_speed":0.02325},"optimized_scores":{"best_composite_score":0.17607,"best_fitness_score":0.37607,"best_task_score":0.10736},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_base_body","body_b":"link7","contact_count":469.0,"contact_point_centroid":[0.53774,-0.10001,0.06493],"force_p95":402.37101,"geom_a":"channel_end","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":430.7871,"mean_force":304.22022,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.4947,-0.08026,0.0392]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":21.0,"contact_point_centroid":[0.47486,0.07618,0.05973],"force_p95":296.91447,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":296.97376,"mean_force":248.3404,"phase_index":0.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.46565,0.07035,0.06456]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":288.0,"contact_point_centroid":[0.47499,-0.00029,0.05684],"force_p95":183.43851,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":196.535,"mean_force":113.40262,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48112,-0.00135,0.05377]},{"body_a":"peg","body_b":"channel_base_body","contact_count":989.0,"contact_point_centroid":[0.4985,0.01452,0.00856],"force_p95":114.44792,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.4329,"mean_force":21.90751,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48695,-0.03696,0.04696]},{"body_a":"attachment","body_b":"peg","contact_count":315.0,"contact_point_centroid":[0.48539,0.02955,0.05544],"force_p95":123.92057,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.94566,"mean_force":66.97246,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.47673,0.02502,0.0589]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":70.0,"contact_point_centroid":[0.52508,0.03735,0.02427],"force_p95":17.59325,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":19.73844,"mean_force":5.8432,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48415,-0.01012,0.05399]},{"body_a":"peg","body_b":"channel_base_body","contact_count":829.0,"contact_point_centroid":[0.49423,0.05895,0.00937],"force_p95":0.55595,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56381,"phase_index":0.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.48082,0.13174,0.17465]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"align_behind","phase_type":"align","tcp_position_centroid":[0.49897,0.19788,0.29608]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.475,-0.01957,0.02423],"force_p95":0.40485,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.40731,"mean_force":0.3827,"phase_index":1.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.49798,-0.08457,0.03959]}],"total_contact_groups":9},"final_pose_error":0.03373,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49485,0.0047,0.02416],"final_tcp_position":[0.49881,-0.08499,0.03969],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":430.7871,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":858.0,"n_steps_budget":1000.0,"object_pos_end":[0.49418,0.0588,0.03391],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13906,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":291.98125,"phase_name":"align_behind","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":885.0,"raw_peak_contact_force":296.97376,"subtask_id":"alignment","tcp_end":[0.46668,0.06978,0.06448],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04256,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49485,0.0047,0.02416],"object_pos_start":[0.49418,0.0588,0.03391],"object_to_goal_dist_end":0.08632,"object_to_goal_dist_start":0.13906,"object_z_max":0.04016,"peak_contact_force":419.90159,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2133.0,"raw_peak_contact_force":430.7871,"subtask_id":"push_completion","tcp_end":[0.49881,-0.08499,0.03969],"tcp_start":[0.46668,0.06978,0.06448],"tcp_to_object_dist_end":0.09111,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```