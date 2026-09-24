## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

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

## Current Skill (Q=-0.041) — your mutation base

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

- **Composite score**: -0.041
- **task_score** (E): 0.143
- **fitness_score**: 0.269  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1830 |
| descend_to_peg | 1.00 | 1.00 | 0.1104 |
| lateral_align | 1.00 | 1.00 | 0.0042 |
| push_along_channel | 0.00 | 1.00 | 0.0866 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.482, 0.093, 0.154) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.533 | 2.857 |
| descend_to_peg | descend | 1.00 / step_budget | (0.482, 0.093, 0.154)→(0.504, 0.082, 0.047) | (0.497, 0.080, 0.034)→(0.503, 0.078, 0.025) | 0.160→0.159 | 1.00 / 3.000 | 224.145 | 270.072 |
| lateral_align | align | 1.00 / step_budget | (0.504, 0.082, 0.047)→(0.506, 0.082, 0.050) | (0.503, 0.078, 0.025)→(0.499, 0.075, 0.032) | 0.159→0.155 | 1.00 / 3.667 | 218.125 | 309.262 |
| push_along_channel | push | 0.00 / step_budget | (0.506, 0.082, 0.050)→(0.500, -0.004, 0.042) | (0.499, 0.075, 0.032)→(0.503, 0.040, 0.024) | 0.155→0.121 | 1.00 / 3.000 | 272.444 | 368.962 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.240
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.240
- phase_score: 0.349
- phase_breakdown.push_through_channel_score: 0.194
- phase_breakdown.contact_peg_score: 0.782
- phase_breakdown.approach_peg_score: 0.674

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.305
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.240
- **Median Q (composite search score)**: -0.024
- **K-run variance**: 0.0015
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.331


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43182,"average_solve_count":132.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.18766,"descend_to_peg.descend_speed":0.0415,"lateral_align.lateral_offset_x":0.00335,"push_along_channel.push_distance":0.19884,"push_along_channel.push_speed":0.14445},"optimized_scores":{"best_composite_score":-0.00477,"best_fitness_score":0.30523,"best_task_score":0.23993},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":408.0,"contact_point_centroid":[0.5463,0.03303,0.05993],"force_p95":331.96823,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":339.30388,"mean_force":261.03907,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50008,0.03604,0.03956]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":736.0,"contact_point_centroid":[0.52503,0.05934,0.05998],"force_p95":275.19092,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":331.21593,"mean_force":172.23356,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50328,0.05952,0.04464]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":338.0,"contact_point_centroid":[0.52507,0.11931,0.05997],"force_p95":288.70387,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":320.64835,"mean_force":157.06518,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50747,0.11921,0.04999]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":60.0,"contact_point_centroid":[0.52513,0.11881,0.05995],"force_p95":296.17259,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":299.88063,"mean_force":155.86302,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50795,0.11879,0.04964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":339.0,"contact_point_centroid":[0.51698,0.11934,0.00653],"force_p95":224.12984,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":225.2438,"mean_force":207.20797,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50747,0.11921,0.04999]},{"body_a":"attachment","body_b":"peg","contact_count":339.0,"contact_point_centroid":[0.51841,0.11933,0.04905],"force_p95":223.64876,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":224.69118,"mean_force":206.72786,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50747,0.11921,0.04999]},{"body_a":"peg","body_b":"channel_base_body","contact_count":530.0,"contact_point_centroid":[0.50658,0.117,0.00843],"force_p95":220.0587,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":223.24382,"mean_force":67.94964,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49937,0.12066,0.08682]},{"body_a":"attachment","body_b":"peg","contact_count":214.0,"contact_point_centroid":[0.51494,0.11854,0.05106],"force_p95":220.34641,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":222.78561,"mean_force":166.97226,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.5039,0.11847,0.05284]},{"body_a":"peg","body_b":"channel_base_body","contact_count":781.0,"contact_point_centroid":[0.50705,0.08838,0.00803],"force_p95":179.87003,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":186.47189,"mean_force":69.43932,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5035,0.06128,0.045]},{"body_a":"attachment","body_b":"peg","contact_count":351.0,"contact_point_centroid":[0.51625,0.09636,0.05071],"force_p95":180.80044,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":185.56702,"mean_force":153.83525,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50762,0.09179,0.05163]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":121.0,"contact_point_centroid":[0.47455,0.10612,0.02118],"force_p95":60.54272,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.9213,"mean_force":38.59417,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50583,0.06991,0.04853]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":49.0,"contact_point_centroid":[0.52508,0.07551,0.02497],"force_p95":9.12319,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.75387,"mean_force":4.6855,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50012,0.0359,0.0392]},{"body_a":"peg","body_b":"channel_base_body","contact_count":272.0,"contact_point_centroid":[0.50101,0.11607,0.00932],"force_p95":0.73654,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.57555,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49865,0.16212,0.22491]}],"total_contact_groups":13},"final_pose_error":0.11959,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50549,0.07765,0.02413],"final_tcp_position":[0.49988,0.03633,0.04086],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":339.30388,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":288.0,"n_steps_budget":630.0,"object_pos_end":[0.50093,0.11605,0.03381],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.51509,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":272.0,"raw_peak_contact_force":1.92055,"subtask_id":"approach_peg","tcp_end":[0.4983,0.12657,0.15644],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12311,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":530.0,"n_steps_budget":1000.0,"object_pos_end":[0.50471,0.11618,0.02786],"object_pos_start":[0.50093,0.11605,0.03381],"object_to_goal_dist_end":0.19662,"object_to_goal_dist_start":0.19615,"object_z_max":0.03393,"peak_contact_force":221.21013,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":804.0,"raw_peak_contact_force":299.88063,"subtask_id":"contact_peg","tcp_end":[0.50777,0.11884,0.04971],"tcp_start":[0.4983,0.12657,0.15644],"tcp_to_object_dist_end":0.02223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":339.0,"n_steps_budget":600.0,"object_pos_end":[0.50287,0.11628,0.02827],"object_pos_start":[0.50471,0.11618,0.02786],"object_to_goal_dist_end":0.19665,"object_to_goal_dist_start":0.19662,"object_z_max":0.02834,"peak_contact_force":224.17208,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1016.0,"raw_peak_contact_force":320.64835,"subtask_id":"contact_peg","tcp_end":[0.50714,0.11934,0.05006],"tcp_start":[0.50777,0.11884,0.04971],"tcp_to_object_dist_end":0.02241,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":794.0,"n_steps_budget":900.0,"object_pos_end":[0.50549,0.07765,0.02413],"object_pos_start":[0.50287,0.11628,0.02827],"object_to_goal_dist_end":0.15854,"object_to_goal_dist_start":0.19665,"object_z_max":0.03892,"peak_contact_force":310.3938,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2446.0,"raw_peak_contact_force":339.30388,"subtask_id":"push_through_channel","tcp_end":[0.49988,0.03633,0.04086],"tcp_start":[0.50714,0.11934,0.05006],"tcp_to_object_dist_end":0.04493,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.4939,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.06993,"descend_to_peg.descend_speed":0.06308,"lateral_align.lateral_offset_x":0.01401,"push_along_channel.push_distance":0.17922,"push_along_channel.push_speed":0.07027},"optimized_scores":{"best_composite_score":-0.02386,"best_fitness_score":0.28614,"best_task_score":0.14723},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":902.0,"contact_point_centroid":[0.52503,0.02173,0.05999],"force_p95":261.35222,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":340.90035,"mean_force":188.67951,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50556,0.02183,0.0494]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":346.0,"contact_point_centroid":[0.52509,0.06616,0.05996],"force_p95":207.77229,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":299.84305,"mean_force":184.62021,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50669,0.06608,0.04946]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":265.0,"contact_point_centroid":[0.54594,-0.03523,0.05997],"force_p95":216.32015,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":255.65135,"mean_force":152.93682,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4999,-0.02909,0.03996]},{"body_a":"attachment","body_b":"peg","contact_count":159.0,"contact_point_centroid":[0.50534,0.0668,0.0504],"force_p95":239.35104,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":254.50144,"mean_force":154.59406,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49448,0.06667,0.05296]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.51089,0.06289,0.00682],"force_p95":245.64449,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":254.26691,"mean_force":220.04757,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.5065,0.06606,0.04931]},{"body_a":"peg","body_b":"channel_base_body","contact_count":473.0,"contact_point_centroid":[0.49892,0.06451,0.00841],"force_p95":221.21272,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":253.88289,"mean_force":52.23862,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48656,0.0709,0.08977]},{"body_a":"attachment","body_b":"peg","contact_count":368.0,"contact_point_centroid":[0.51786,0.0641,0.04849],"force_p95":245.23918,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":253.5341,"mean_force":221.87257,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.5065,0.06606,0.04931]},{"body_a":"attachment","body_b":"peg","contact_count":689.0,"contact_point_centroid":[0.51748,0.04601,0.05134],"force_p95":170.43208,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":184.94668,"mean_force":148.84791,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50776,0.04169,0.05308]},{"body_a":"peg","body_b":"channel_base_body","contact_count":988.0,"contact_point_centroid":[0.50269,0.03946,0.00813],"force_p95":156.24894,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.17434,"mean_force":97.45055,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.5054,0.02062,0.04915]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":692.0,"contact_point_centroid":[0.474,0.05019,0.01913],"force_p95":65.74436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.81948,"mean_force":54.35019,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50772,0.04137,0.05302]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":208.0,"contact_point_centroid":[0.47397,0.05762,0.01398],"force_p95":64.03504,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.33808,"mean_force":56.09499,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50648,0.06608,0.04978]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":64.0,"contact_point_centroid":[0.52503,0.0467,0.0525],"force_p95":1.88778,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.07446,"mean_force":1.67278,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50827,0.04251,0.05393]},{"body_a":"peg","body_b":"world","contact_count":33.0,"contact_point_centroid":[0.51149,0.06523,-0.00015],"force_p95":13.36183,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.20656,"mean_force":4.61838,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.50009,0.06592,0.04714]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.49574,0.06388,0.00936],"force_p95":0.62526,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56913,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48916,0.13634,0.2216]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49913,0.19728,0.29658]},{"body_a":"peg","body_b":"world","contact_count":10.0,"contact_point_centroid":[0.51454,0.06504,-0.0002],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50197,0.06577,0.04651]}],"total_contact_groups":16},"final_pose_error":0.09222,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49862,0.01945,0.02412],"final_tcp_position":[0.49982,-0.0302,0.0402],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":340.90035,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.49509,0.06406,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14427,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.5402,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":387.0,"raw_peak_contact_force":2.44546,"subtask_id":"approach_peg","tcp_end":[0.48041,0.07855,0.15318],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12103,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":473.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,0.06183,0.02448],"object_pos_start":[0.49509,0.06406,0.03392],"object_to_goal_dist_end":0.14268,"object_to_goal_dist_start":0.14427,"object_z_max":0.03397,"peak_contact_force":237.55597,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":665.0,"raw_peak_contact_force":254.50144,"subtask_id":"contact_peg","tcp_end":[0.50146,0.06577,0.04629],"tcp_start":[0.48041,0.07855,0.15318],"tcp_to_object_dist_end":0.02217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":368.0,"n_steps_budget":600.0,"object_pos_end":[0.49713,0.05706,0.03394],"object_pos_start":[0.50094,0.06183,0.02448],"object_to_goal_dist_end":0.13722,"object_to_goal_dist_start":0.14268,"object_z_max":0.03393,"peak_contact_force":209.69032,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1300.0,"raw_peak_contact_force":299.84305,"subtask_id":"contact_peg","tcp_end":[0.50634,0.06606,0.05012],"tcp_start":[0.50146,0.06577,0.04629],"tcp_to_object_dist_end":0.02068,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49862,0.01945,0.02412],"object_pos_start":[0.49713,0.05706,0.03394],"object_to_goal_dist_end":0.10072,"object_to_goal_dist_start":0.13722,"object_z_max":0.03871,"peak_contact_force":211.04685,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3600.0,"raw_peak_contact_force":340.90035,"subtask_id":"push_through_channel","tcp_end":[0.49982,-0.0302,0.0402],"tcp_start":[0.50634,0.06606,0.05012],"tcp_to_object_dist_end":0.0522,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.8995,"average_solve_count":199.0,"average_success_count":199.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.19811,"descend_to_peg.descend_speed":0.02075,"lateral_align.lateral_offset_x":0.01994,"push_along_channel.push_distance":0.16728,"push_along_channel.push_speed":0.103},"optimized_scores":{"best_composite_score":-0.09477,"best_fitness_score":0.21523,"best_task_score":0.04174},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":894.0,"contact_point_centroid":[0.52503,0.02293,0.05998],"force_p95":302.49184,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":426.68264,"mean_force":214.12529,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50524,0.02324,0.05045]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":244.0,"contact_point_centroid":[0.54684,-0.02379,0.05991],"force_p95":314.11565,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":342.61175,"mean_force":289.6194,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49965,-0.01763,0.04274]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":383.0,"contact_point_centroid":[0.52508,0.06072,0.05996],"force_p95":199.98271,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":307.29569,"mean_force":149.48441,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50607,0.0606,0.04909]},{"body_a":"peg","body_b":"channel_base_body","contact_count":397.0,"contact_point_centroid":[0.5137,0.05931,0.00631],"force_p95":249.33366,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":264.57675,"mean_force":231.08786,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.506,0.0606,0.04897]},{"body_a":"attachment","body_b":"peg","contact_count":397.0,"contact_point_centroid":[0.51703,0.05983,0.04795],"force_p95":248.9395,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":264.46441,"mean_force":230.92716,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.506,0.0606,0.04897]},{"body_a":"attachment","body_b":"peg","contact_count":283.0,"contact_point_centroid":[0.50575,0.06133,0.04815],"force_p95":242.52635,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":255.83537,"mean_force":165.38173,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.4949,0.06123,0.05036]},{"body_a":"peg","body_b":"channel_base_body","contact_count":648.0,"contact_point_centroid":[0.4998,0.05963,0.0077],"force_p95":224.11996,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":254.56915,"mean_force":71.1598,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.48311,0.06522,0.08299]},{"body_a":"peg","body_b":"channel_base_body","contact_count":915.0,"contact_point_centroid":[0.50527,0.03935,0.00799],"force_p95":169.36896,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":191.88305,"mean_force":113.57251,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50534,0.02416,0.05061]},{"body_a":"attachment","body_b":"peg","contact_count":687.0,"contact_point_centroid":[0.51726,0.04224,0.05108],"force_p95":172.84433,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":191.70386,"mean_force":157.45223,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50723,0.03808,0.0532]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":699.0,"contact_point_centroid":[0.47408,0.04809,0.01754],"force_p95":62.75337,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.80613,"mean_force":49.95444,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50711,0.03717,0.05301]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":104.0,"contact_point_centroid":[0.47423,0.05189,0.0117],"force_p95":52.17294,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.40429,"mean_force":45.12003,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50566,0.06051,0.04984]},{"body_a":"peg","body_b":"world","contact_count":163.0,"contact_point_centroid":[0.51025,0.06069,-0.00056],"force_p95":18.42118,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.48776,"mean_force":7.39971,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"descend","tcp_position_centroid":[0.49941,0.06066,0.04666]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":18.0,"contact_point_centroid":[0.52513,-0.00155,0.02466],"force_p95":10.60352,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.47461,"mean_force":3.26259,"phase_index":3.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4996,-0.01777,0.04272]},{"body_a":"peg","body_b":"channel_base_body","contact_count":320.0,"contact_point_centroid":[0.49466,0.05904,0.00933],"force_p95":0.61319,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.5919,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48251,0.1328,0.22025]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49834,0.19513,0.29398]},{"body_a":"peg","body_b":"world","contact_count":12.0,"contact_point_centroid":[0.51854,0.06081,-0.00048],"force_p95":0.0,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"lateral_align","phase_type":"align","tcp_position_centroid":[0.50368,0.06042,0.0458]}],"total_contact_groups":16},"final_pose_error":0.09773,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50586,0.02238,0.02412],"final_tcp_position":[0.49958,-0.01793,0.04349],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":426.68264,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":349.0,"n_steps_budget":690.0,"object_pos_end":[0.49405,0.05902,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13929,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54431,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":355.0,"raw_peak_contact_force":4.20518,"subtask_id":"approach_peg","tcp_end":[0.46803,0.07396,0.15311],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12298,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":648.0,"n_steps_budget":1000.0,"object_pos_end":[0.50259,0.05633,0.02356],"object_pos_start":[0.49405,0.05902,0.03385],"object_to_goal_dist_end":0.13734,"object_to_goal_dist_start":0.13929,"object_z_max":0.03389,"peak_contact_force":213.67036,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1094.0,"raw_peak_contact_force":255.83537,"subtask_id":"contact_peg","tcp_end":[0.50277,0.06032,0.04537],"tcp_start":[0.46803,0.07396,0.15311],"tcp_to_object_dist_end":0.02217,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":397.0,"n_steps_budget":600.0,"object_pos_end":[0.49625,0.05228,0.03274],"object_pos_start":[0.50259,0.05633,0.02356],"object_to_goal_dist_end":0.13253,"object_to_goal_dist_start":0.13734,"object_z_max":0.03274,"peak_contact_force":220.51329,"phase_name":"lateral_align","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1293.0,"raw_peak_contact_force":307.29569,"subtask_id":"contact_peg","tcp_end":[0.50562,0.06048,0.05009],"tcp_start":[0.50277,0.06032,0.04537],"tcp_to_object_dist_end":0.02135,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":938.0,"n_steps_budget":1000.0,"object_pos_end":[0.50586,0.02238,0.02412],"object_pos_start":[0.49625,0.05228,0.03274],"object_to_goal_dist_end":0.10377,"object_to_goal_dist_start":0.13253,"object_z_max":0.03865,"peak_contact_force":295.89155,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3457.0,"raw_peak_contact_force":426.68264,"subtask_id":"push_through_channel","tcp_end":[0.49958,-0.01793,0.04349],"tcp_start":[0.50562,0.06048,0.05009],"tcp_to_object_dist_end":0.04516,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```