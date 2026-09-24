## Search State

- **Seed**: 1
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1584 | 0.11 | ❌ rejected |
| 11 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2199 | 0.63 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 5 | 0.1478 | 0.01 | ❌ rejected |
| 9 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2165 | 0.63 | ❌ rejected |
| 8 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2220 | 0.61 | ❌ rejected |

**Proposal policy**: task_score is 0.11 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.158) — your mutation base

```yaml
skill: peg_channel
phases:
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
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: impedance_motion
  control: admittance_control
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
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
- id: retract_1
  type: retract
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: -0.158
- **task_score** (E): 0.107
- **fitness_score**: 0.148  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.440

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1931 |
| approach_1 | 1.00 | 1.00 | 0.0644 |
| contact_1 | 0.67 | 1.00 | 0.1107 |
| push_1 | 0.00 | 1.00 | 0.0671 |
| retract_1 | 1.00 | 1.00 | 0.1658 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.483, 0.087, 0.146) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.540 | 2.857 |
| approach_1 | approach | 1.00 / step_budget | (0.483, 0.087, 0.146)→(0.493, 0.099, 0.206) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.553 | 0.588 |
| contact_1 | contact | 0.67 / force_exceeded | (0.493, 0.099, 0.206)→(0.493, 0.083, 0.096) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.667 | 34.713 | 34.754 |
| push_1 | push | 0.00 / step_budget | (0.493, 0.083, 0.096)→(0.505, 0.017, 0.087) | (0.497, 0.080, 0.034)→(0.499, 0.042, 0.036) | 0.160→0.122 | 1.00 / 3.333 | 141.134 | 342.291 |
| retract_1 | retract | 1.00 / step_budget | (0.505, 0.017, 0.087)→(0.503, 0.027, 0.253) | (0.499, 0.042, 0.036)→(0.498, 0.045, 0.034) | 0.122→0.125 | 1.00 / 1.000 | 0.549 | 146.285 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.244
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.140
- phase_score: 0.208
- phase_breakdown.reach_goal_score: 0.009
- phase_breakdown.reach_pre_contact_score: 0.674

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.181
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.140
- **Median Q (composite search score)**: -0.093
- **K-run variance**: 0.0138
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.306


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13043,"average_solve_count":253.0,"average_success_count":253.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00393,"approach_1.approach_height":0.19153,"approach_1.speed":0.04918,"contact_1.force_threshold":5.01592,"contact_1.speed":0.02217,"push_1.push_distance":0.10227,"push_1.push_speed":0.091},"optimized_scores":{"best_composite_score":-0.32367,"best_fitness_score":0.11633,"best_task_score":0.09207},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":388.0,"contact_point_centroid":[0.47086,0.11989,0.05969],"force_p95":209.00927,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":239.1873,"mean_force":184.41241,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49993,0.08083,0.07197]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.47147,0.11992,0.05999],"force_p95":92.10097,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":92.2025,"mean_force":57.57199,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50286,0.08245,0.07151]},{"body_a":"peg","body_b":"channel_base_body","contact_count":527.0,"contact_point_centroid":[0.50094,0.10324,0.00946],"force_p95":6.51174,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.57642,"mean_force":1.22328,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49905,0.08564,0.07251]},{"body_a":"attachment","body_b":"peg","contact_count":31.0,"contact_point_centroid":[0.49642,0.12088,0.06029],"force_p95":11.88555,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.19279,"mean_force":6.11242,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49649,0.0814,0.07238]},{"body_a":"peg","body_b":"link7","contact_count":57.0,"contact_point_centroid":[0.50022,0.12479,0.04434],"force_p95":12.89643,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.82698,"mean_force":3.4288,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49645,0.08461,0.07255]},{"body_a":"peg","body_b":"channel_base_body","contact_count":520.0,"contact_point_centroid":[0.50093,0.11599,0.00937],"force_p95":0.61847,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55973,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50001,0.16011,0.221]},{"body_a":"peg","body_b":"channel_base_body","contact_count":767.0,"contact_point_centroid":[0.50092,0.11599,0.00942],"force_p95":0.60583,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65555,"mean_force":0.54289,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49752,0.13294,0.16786]},{"body_a":"peg","body_b":"channel_base_body","contact_count":788.0,"contact_point_centroid":[0.50095,0.116,0.00943],"force_p95":0.604,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65179,"mean_force":0.54176,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49778,0.12568,0.14628]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50043,0.10134,0.00939],"force_p95":0.55151,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55541,"mean_force":0.5465,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50083,0.09632,0.15145]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.52503,0.11995,0.05998],"force_p95":0.0,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49668,0.0791,0.07231]}],"total_contact_groups":10},"final_pose_error":0.03897,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50035,0.10131,0.03382],"final_tcp_position":[0.50119,0.09298,0.23402],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":239.1873,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":536.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11604,0.03381],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19614,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.52712,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":520.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.50157,0.12178,0.14742],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11376,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":767.0,"n_steps_budget":1000.0,"object_pos_end":[0.5009,0.11605,0.03381],"object_pos_start":[0.50096,0.11604,0.03381],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19614,"object_z_max":0.03396,"peak_contact_force":0.56158,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":767.0,"raw_peak_contact_force":0.65555,"subtask_id":"reach_pre_contact","tcp_end":[0.49916,0.136,0.21554],"tcp_start":[0.50157,0.12178,0.14742],"tcp_to_object_dist_end":0.18283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":788.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.116,0.03389],"object_pos_start":[0.5009,0.11605,0.03381],"object_to_goal_dist_end":0.1961,"object_to_goal_dist_start":0.19615,"object_z_max":0.03413,"peak_contact_force":0.52859,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":788.0,"raw_peak_contact_force":0.65179,"subtask_id":"reach_pre_contact","tcp_end":[0.49799,0.1157,0.07776],"tcp_start":[0.49916,0.136,0.21554],"tcp_to_object_dist_end":0.04397,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":542.0,"n_steps_budget":720.0,"object_pos_end":[0.50036,0.10134,0.0338],"object_pos_start":[0.50096,0.116,0.03389],"object_to_goal_dist_end":0.18145,"object_to_goal_dist_start":0.1961,"object_z_max":0.03532,"peak_contact_force":209.00519,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1017.0,"raw_peak_contact_force":239.1873,"subtask_id":"reach_goal","tcp_end":[0.50291,0.08244,0.07149],"tcp_start":[0.49799,0.1157,0.07776],"tcp_to_object_dist_end":0.04224,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50035,0.10131,0.03382],"object_pos_start":[0.50036,0.10134,0.0338],"object_to_goal_dist_end":0.18141,"object_to_goal_dist_start":0.18145,"object_z_max":0.03383,"peak_contact_force":0.54562,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1004.0,"raw_peak_contact_force":92.2025,"subtask_id":"reach_goal","tcp_end":[0.50119,0.09298,0.23402],"tcp_start":[0.50291,0.08244,0.07149],"tcp_to_object_dist_end":0.20037,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60748,"average_solve_count":214.0,"average_success_count":214.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00153,"approach_1.approach_height":0.21945,"approach_1.speed":0.06615,"contact_1.force_threshold":3.74514,"contact_1.speed":0.04914,"push_1.push_distance":0.19891,"push_1.push_speed":0.09008},"optimized_scores":{"best_composite_score":-0.05896,"best_fitness_score":0.18104,"best_task_score":0.14023},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":432.0,"contact_point_centroid":[0.52505,0.04797,0.05992],"force_p95":386.17859,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":426.08285,"mean_force":285.81242,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50528,-0.00614,0.09522]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":929.0,"contact_point_centroid":[0.47498,0.09424,0.05998],"force_p95":253.71231,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":367.76453,"mean_force":178.04199,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50099,0.01713,0.09762]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.47499,0.08066,0.05999],"force_p95":134.80129,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.70827,"mean_force":117.63851,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50912,-0.00668,0.09535]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.52506,0.04902,0.05991],"force_p95":90.15405,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.35061,"mean_force":34.42778,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5091,-0.00669,0.09547]},{"body_a":"peg","body_b":"link7","contact_count":694.0,"contact_point_centroid":[0.49687,0.04585,0.06332],"force_p95":63.7061,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.10114,"mean_force":11.09369,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5031,0.00213,0.09612]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49846,0.0302,0.00972],"force_p95":24.28905,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.00839,"mean_force":8.15241,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50087,0.01779,0.09769]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47499,0.11999,0.05999],"force_p95":55.98013,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":55.98013,"mean_force":55.98013,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49177,0.06679,0.10394]},{"body_a":"peg","body_b":"channel_base_body","contact_count":627.0,"contact_point_centroid":[0.49543,0.06397,0.00937],"force_p95":0.56806,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55912,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48775,0.13361,0.21839]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49927,0.19795,0.2974]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.4969,0.02462,0.00943],"force_p95":0.56255,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.02301,"mean_force":0.54502,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50724,0.00758,0.17772]},{"body_a":"peg","body_b":"channel_base_body","contact_count":862.0,"contact_point_centroid":[0.49502,0.06388,0.0094],"force_p95":0.55075,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54525,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48103,0.08522,0.18335]},{"body_a":"peg","body_b":"channel_base_body","contact_count":795.0,"contact_point_centroid":[0.4952,0.06384,0.00941],"force_p95":0.55078,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55347,"mean_force":0.54506,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49134,0.07565,0.17359]},{"body_a":"peg","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.49719,0.0416,0.06098],"force_p95":0.5147,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.53005,"mean_force":0.19995,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50837,-0.00537,0.09838]}],"total_contact_groups":13},"final_pose_error":0.03456,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49698,0.02489,0.03379],"final_tcp_position":[0.50759,0.00323,0.26225],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":426.08285,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":654.0,"n_steps_budget":1000.0,"object_pos_end":[0.49489,0.06397,0.03396],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14418,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54541,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":655.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.47781,0.07194,0.14563],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11325,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":862.0,"n_steps_budget":1000.0,"object_pos_end":[0.49483,0.06372,0.03403],"object_pos_start":[0.49489,0.06397,0.03396],"object_to_goal_dist_end":0.14394,"object_to_goal_dist_start":0.14418,"object_z_max":0.03403,"peak_contact_force":0.55076,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":862.0,"raw_peak_contact_force":0.55403,"subtask_id":"reach_pre_contact","tcp_end":[0.49235,0.08473,0.2438],"tcp_start":[0.47781,0.07194,0.14563],"tcp_to_object_dist_end":0.21083,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":795.0,"n_steps_budget":1000.0,"object_pos_end":[0.49489,0.06408,0.03403],"object_pos_start":[0.49483,0.06372,0.03403],"object_to_goal_dist_end":0.1443,"object_to_goal_dist_start":0.14394,"object_z_max":0.03404,"peak_contact_force":55.98013,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":796.0,"raw_peak_contact_force":55.98013,"subtask_id":"reach_pre_contact","tcp_end":[0.49178,0.06678,0.10378],"tcp_start":[0.49235,0.08473,0.2438],"tcp_to_object_dist_end":0.06987,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49799,0.02085,0.03746],"object_pos_start":[0.49489,0.06408,0.03403],"object_to_goal_dist_end":0.1009,"object_to_goal_dist_start":0.1443,"object_z_max":0.03757,"peak_contact_force":0.16685,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3055.0,"raw_peak_contact_force":426.08285,"subtask_id":"reach_goal","tcp_end":[0.50913,-0.00667,0.09533],"tcp_start":[0.49178,0.06678,0.10378],"tcp_to_object_dist_end":0.06504,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49698,0.02489,0.03379],"object_pos_start":[0.49799,0.02085,0.03746],"object_to_goal_dist_end":0.10512,"object_to_goal_dist_start":0.1009,"object_z_max":0.03746,"peak_contact_force":0.54587,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1015.0,"raw_peak_contact_force":136.70827,"subtask_id":"reach_goal","tcp_end":[0.50759,0.00323,0.26225],"tcp_start":[0.50913,-0.00667,0.09533],"tcp_to_object_dist_end":0.22973,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15271,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00316,"approach_1.approach_height":0.12989,"approach_1.speed":0.08576,"contact_1.force_threshold":8.1163,"contact_1.speed":0.01771,"push_1.push_distance":0.19905,"push_1.push_speed":0.06804},"optimized_scores":{"best_composite_score":-0.09267,"best_fitness_score":0.14733,"best_task_score":0.09019},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":928.0,"contact_point_centroid":[0.47498,0.09568,0.05998],"force_p95":228.32419,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":361.60343,"mean_force":168.47951,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49633,0.02265,0.10089]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":75.0,"contact_point_centroid":[0.52502,0.029,0.05997],"force_p95":259.92403,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":324.33089,"mean_force":203.38816,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50227,-0.02364,0.09517]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47498,0.05995,0.05998],"force_p95":203.36528,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":209.94282,"mean_force":136.27714,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50265,-0.024,0.09511]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.52502,0.02892,0.05997],"force_p95":146.07228,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":154.29426,"mean_force":75.45622,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50265,-0.024,0.09511]},{"body_a":"peg","body_b":"link7","contact_count":562.0,"contact_point_centroid":[0.49594,0.04503,0.06176],"force_p95":62.9996,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.78591,"mean_force":15.61645,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49939,-0.00146,0.09807]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49676,0.03348,0.00961],"force_p95":19.86709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.59805,"mean_force":9.25126,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49638,0.02245,0.10087]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.475,0.12,0.06],"force_p95":47.6294,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":47.6294,"mean_force":47.6294,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48851,0.06537,0.10742]},{"body_a":"peg","body_b":"channel_base_body","contact_count":640.0,"contact_point_centroid":[0.49432,0.05889,0.00936],"force_p95":0.56138,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56906,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48317,0.13092,0.21809]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49894,0.19731,0.29651]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49709,0.00778,0.00941],"force_p95":0.56712,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.17885,"mean_force":0.5457,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50074,-0.00971,0.17744]},{"body_a":"peg","body_b":"channel_base_body","contact_count":347.0,"contact_point_centroid":[0.49423,0.05894,0.00939],"force_p95":0.55003,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54596,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.46939,0.07423,0.13376]},{"body_a":"peg","body_b":"channel_base_body","contact_count":334.0,"contact_point_centroid":[0.49396,0.05893,0.0094],"force_p95":0.55041,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55169,"mean_force":0.54559,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48696,0.07045,0.13246]},{"body_a":"peg","body_b":"link7","contact_count":6.0,"contact_point_centroid":[0.49732,0.02144,0.06273],"force_p95":0.40369,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47253,"mean_force":0.18533,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50228,-0.02329,0.09674]}],"total_contact_groups":13},"final_pose_error":0.03462,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49706,0.00806,0.03378],"final_tcp_position":[0.50111,-0.01408,0.26194],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":361.60343,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":669.0,"n_steps_budget":1000.0,"object_pos_end":[0.49426,0.05894,0.03388],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13919,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54863,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":675.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_pre_contact","tcp_end":[0.469,0.06714,0.14555],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11478,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":347.0,"n_steps_budget":600.0,"object_pos_end":[0.49428,0.05907,0.03393],"object_pos_start":[0.49426,0.05894,0.03388],"object_to_goal_dist_end":0.13932,"object_to_goal_dist_start":0.13919,"object_z_max":0.03393,"peak_contact_force":0.54628,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":347.0,"raw_peak_contact_force":0.55382,"subtask_id":"reach_pre_contact","tcp_end":[0.48708,0.07568,0.15777],"tcp_start":[0.469,0.06714,0.14555],"tcp_to_object_dist_end":0.12516,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":334.0,"n_steps_budget":1000.0,"object_pos_end":[0.49436,0.05888,0.03398],"object_pos_start":[0.49428,0.05907,0.03393],"object_to_goal_dist_end":0.13912,"object_to_goal_dist_start":0.13932,"object_z_max":0.03398,"peak_contact_force":47.6294,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":335.0,"raw_peak_contact_force":47.6294,"subtask_id":"reach_pre_contact","tcp_end":[0.48853,0.06535,0.10729],"tcp_start":[0.48708,0.07568,0.15777],"tcp_to_object_dist_end":0.07382,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49781,0.00409,0.03731],"object_pos_start":[0.49436,0.05888,0.03398],"object_to_goal_dist_end":0.08417,"object_to_goal_dist_start":0.13912,"object_z_max":0.03731,"peak_contact_force":214.23031,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2565.0,"raw_peak_contact_force":361.60343,"subtask_id":"reach_goal","tcp_end":[0.50266,-0.02398,0.09507],"tcp_start":[0.48853,0.06535,0.10729],"tcp_to_object_dist_end":0.06441,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49706,0.00806,0.03378],"object_pos_start":[0.49781,0.00409,0.03731],"object_to_goal_dist_end":0.08833,"object_to_goal_dist_start":0.08417,"object_z_max":0.03733,"peak_contact_force":0.55647,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1012.0,"raw_peak_contact_force":209.94282,"subtask_id":"reach_goal","tcp_end":[0.50111,-0.01408,0.26194],"tcp_start":[0.50266,-0.02398,0.09507],"tcp_to_object_dist_end":0.22926,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```