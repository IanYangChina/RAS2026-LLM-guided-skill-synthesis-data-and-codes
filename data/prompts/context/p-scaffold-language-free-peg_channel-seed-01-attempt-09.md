## Search State

- **Seed**: 1
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2165 | 0.63 | ❌ rejected |
| 8 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2220 | 0.61 | ❌ rejected |
| 7 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.2954 | 0.00 | ❌ rejected |
| 6 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2156 | 0.60 | ❌ rejected |
| 5 | approach → approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.0486 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.63 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.216) — your mutation base

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

- **Composite score**: 0.216
- **task_score** (E): 0.627
- **fitness_score**: 0.606  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.390

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.2578 |
| approach_1 | 1.00 | 1.00 | 0.0163 |
| contact_1 | 1.00 | 1.00 | 0.0110 |
| push_1 | 0.67 | 1.00 | 0.1542 |
| retract_1 | 0.00 | 1.00 | 0.1659 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.484, 0.125, 0.055) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.667 | 221.293 | 237.641 |
| approach_1 | approach | 1.00 / step_budget | (0.484, 0.125, 0.055)→(0.491, 0.121, 0.041) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.547 | 178.050 |
| contact_1 | contact | 1.00 / step_budget | (0.491, 0.121, 0.041)→(0.494, 0.113, 0.036) | (0.497, 0.080, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 159.950 | 177.915 |
| push_1 | push | 0.67 / step_budget | (0.494, 0.113, 0.036)→(0.499, -0.042, 0.037) | (0.497, 0.079, 0.034)→(0.502, -0.070, 0.036) | 0.160→0.019 | 1.00 / 2.667 | 46.625 | 134.307 |
| retract_1 | retract | 0.00 / step_budget | (0.499, -0.042, 0.037)→(0.497, 0.009, 0.195) | (0.502, -0.070, 0.036)→(0.498, -0.067, 0.034) | 0.019→0.018 | 1.00 / 1.000 | 0.547 | 75.990 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 1.000
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 1.000
- phase_score: 0.499
- phase_breakdown.push_score: 0.266
- phase_breakdown.approach_score: 0.897
- phase_breakdown.contact_score: 0.798

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.699
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.249
- **K-run variance**: 0.0084
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.366


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.19118,"average_solve_count":204.0,"average_success_count":204.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00407,"approach_1.approach_height":0.14356,"approach_1.speed":0.01099,"contact_1.speed":0.01041,"push_1.push_distance":0.19993,"push_1.push_speed":0.09885},"optimized_scores":{"best_composite_score":0.30912,"best_fitness_score":0.69912,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":754.0,"contact_point_centroid":[0.54388,0.06852,0.05998],"force_p95":122.28295,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":136.3626,"mean_force":102.56324,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49825,0.07258,0.0363]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":776.0,"contact_point_centroid":[0.54793,0.12,0.05998],"force_p95":111.15941,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.87421,"mean_force":66.16672,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49567,0.14675,0.03428]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.54356,-0.01916,0.06],"force_p95":69.9733,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.72175,"mean_force":62.44883,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49886,-0.01407,0.03689]},{"body_a":"attachment","body_b":"peg","contact_count":436.0,"contact_point_centroid":[0.50018,0.04701,0.03964],"force_p95":22.64582,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.3261,"mean_force":3.50345,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49839,0.05872,0.03642]},{"body_a":"peg","body_b":"channel_base_body","contact_count":795.0,"contact_point_centroid":[0.4987,0.03433,0.00966],"force_p95":14.94657,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.67302,"mean_force":2.28694,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49824,0.07337,0.03629]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":164.0,"contact_point_centroid":[0.47482,0.06844,0.04143],"force_p95":2.02544,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.18501,"mean_force":0.56173,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49789,0.0992,0.0361]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":107.0,"contact_point_centroid":[0.52515,-0.02143,0.02912],"force_p95":4.89663,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.8649,"mean_force":1.24331,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49894,0.00735,0.03693]},{"body_a":"peg","body_b":"channel_base_body","contact_count":946.0,"contact_point_centroid":[0.50088,0.11441,0.00946],"force_p95":0.68014,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.90301,"mean_force":0.58888,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49542,0.14755,0.03471]},{"body_a":"attachment","body_b":"peg","contact_count":136.0,"contact_point_centroid":[0.50062,0.13362,0.04179],"force_p95":1.99151,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.47951,"mean_force":0.48779,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49706,0.14556,0.03418]},{"body_a":"peg","body_b":"channel_base_body","contact_count":755.0,"contact_point_centroid":[0.50092,0.11599,0.00939],"force_p95":0.61661,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55392,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4977,0.17803,0.1717]},{"body_a":"peg","body_b":"channel_base_body","contact_count":993.0,"contact_point_centroid":[0.50553,-0.04502,0.00942],"force_p95":0.56185,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.38038,"mean_force":0.54848,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49597,0.00976,0.11599]},{"body_a":"peg","body_b":"channel_base_body","contact_count":32.0,"contact_point_centroid":[0.50082,0.11662,0.00945],"force_p95":0.58221,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58736,"mean_force":0.54134,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49623,0.15693,0.04611]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":7.0,"contact_point_centroid":[0.52506,-0.04361,0.03874],"force_p95":0.31419,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.31712,"mean_force":0.15403,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49704,-0.01032,0.04325]}],"total_contact_groups":13},"final_pose_error":0.10274,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50546,-0.04497,0.03386],"final_tcp_position":[0.49681,0.01894,0.19907],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":136.3626,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11605,0.03394],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.54801,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":755.0,"raw_peak_contact_force":1.92055,"tcp_end":[0.49706,0.15726,0.04892],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04401,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":32.0,"n_steps_budget":900.0,"object_pos_end":[0.50097,0.11606,0.03389],"object_pos_start":[0.50095,0.11605,0.03394],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19615,"object_z_max":0.03394,"peak_contact_force":0.55147,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":32.0,"raw_peak_contact_force":0.58736,"tcp_end":[0.49615,0.15682,0.04249],"tcp_start":[0.49706,0.15726,0.04892],"tcp_to_object_dist_end":0.04194,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":946.0,"n_steps_budget":1000.0,"object_pos_end":[0.5009,0.11518,0.03426],"object_pos_start":[0.50097,0.11606,0.03389],"object_to_goal_dist_end":0.19527,"object_to_goal_dist_start":0.19615,"object_z_max":0.03464,"peak_contact_force":111.09416,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1858.0,"raw_peak_contact_force":115.87421,"tcp_end":[0.49763,0.14514,0.03417],"tcp_start":[0.49615,0.15682,0.04249],"tcp_to_object_dist_end":0.03014,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50701,-0.04325,0.03681],"object_pos_start":[0.5009,0.11518,0.03426],"object_to_goal_dist_end":0.03755,"object_to_goal_dist_start":0.19527,"object_z_max":0.03742,"peak_contact_force":0.80569,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2256.0,"raw_peak_contact_force":136.3626,"tcp_end":[0.49887,-0.0139,0.03689],"tcp_start":[0.49763,0.14514,0.03417],"tcp_to_object_dist_end":0.03045,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50546,-0.04497,0.03386],"object_pos_start":[0.50701,-0.04325,0.03681],"object_to_goal_dist_end":0.03598,"object_to_goal_dist_start":0.03755,"object_z_max":0.03681,"peak_contact_force":0.54681,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1003.0,"raw_peak_contact_force":70.72175,"tcp_end":[0.49681,0.01894,0.19907],"tcp_start":[0.49887,-0.0139,0.03689],"tcp_to_object_dist_end":0.17735,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.23881,"average_solve_count":201.0,"average_success_count":201.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00011,"approach_1.approach_height":0.15082,"approach_1.speed":0.01813,"contact_1.speed":0.01297,"push_1.push_distance":0.13081,"push_1.push_speed":0.09352},"optimized_scores":{"best_composite_score":0.2488,"best_fitness_score":0.6388,"best_task_score":0.62892},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":60.0,"contact_point_centroid":[0.4749,0.12,0.0598],"force_p95":341.5277,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.62701,"mean_force":311.80708,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47984,0.111,0.05723]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.47497,0.1178,0.05995],"force_p95":248.92157,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":268.36975,"mean_force":188.09882,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48306,0.11067,0.0559]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":806.0,"contact_point_centroid":[0.53535,0.10338,0.05996],"force_p95":191.49956,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":199.16115,"mean_force":155.94594,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48985,0.10203,0.0379]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":725.0,"contact_point_centroid":[0.54124,0.02801,0.05999],"force_p95":108.98335,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":118.31441,"mean_force":89.86665,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49591,0.02989,0.03782]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54352,-0.04765,0.06],"force_p95":59.15111,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":59.15111,"mean_force":59.15111,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49851,-0.05186,0.03744]},{"body_a":"attachment","body_b":"peg","contact_count":309.0,"contact_point_centroid":[0.49627,0.01355,0.03947],"force_p95":15.40442,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.58694,"mean_force":2.65296,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49609,0.02526,0.03784]},{"body_a":"peg","body_b":"channel_base_body","contact_count":781.0,"contact_point_centroid":[0.4967,-0.01139,0.00961],"force_p95":5.5328,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.05032,"mean_force":1.48005,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49601,0.02716,0.03781]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":357.0,"contact_point_centroid":[0.47482,-0.02052,0.02613],"force_p95":1.50815,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.51043,"mean_force":0.47832,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49669,0.00974,0.03783]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49656,-0.06359,0.03838],"force_p95":9.01296,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.96865,"mean_force":3.4468,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49833,-0.05188,0.03753]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49348,-0.08038,0.00941],"force_p95":0.55694,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.14648,"mean_force":0.56711,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49565,-0.01642,0.11141]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":300.0,"contact_point_centroid":[0.47498,-0.08014,0.05546],"force_p95":0.42609,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.63573,"mean_force":0.17716,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49577,-0.01995,0.10309]},{"body_a":"peg","body_b":"channel_base_body","contact_count":14.0,"contact_point_centroid":[0.4934,-0.10019,0.05908],"force_p95":2.21708,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.91383,"mean_force":0.47419,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49847,-0.05057,0.03745]},{"body_a":"peg","body_b":"channel_base_body","contact_count":12.0,"contact_point_centroid":[0.49248,-0.10008,0.05959],"force_p95":3.75178,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.16584,"mean_force":2.22481,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49793,-0.0516,0.03788]},{"body_a":"peg","body_b":"channel_base_body","contact_count":820.0,"contact_point_centroid":[0.49531,0.0638,0.00938],"force_p95":0.56258,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55591,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48773,0.15105,0.1656]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49933,0.19869,0.29695]},{"body_a":"peg","body_b":"channel_base_body","contact_count":836.0,"contact_point_centroid":[0.49512,0.06385,0.00941],"force_p95":0.55086,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.54513,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48979,0.10211,0.03795]}],"total_contact_groups":17},"final_pose_error":0.1076,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49308,-0.08003,0.03378],"final_tcp_position":[0.49658,0.00504,0.19257],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":355.62701,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":847.0,"n_steps_budget":1000.0,"object_pos_end":[0.49535,0.06392,0.03399],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":334.70153,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":908.0,"raw_peak_contact_force":355.62701,"tcp_end":[0.481,0.11081,0.05671],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05405,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":103.0,"n_steps_budget":960.0,"object_pos_end":[0.49485,0.06399,0.03401],"object_pos_start":[0.49535,0.06392,0.03399],"object_to_goal_dist_end":0.14421,"object_to_goal_dist_start":0.14412,"object_z_max":0.03401,"peak_contact_force":0.54332,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":138.0,"raw_peak_contact_force":268.36975,"tcp_end":[0.48854,0.10587,0.04092],"tcp_start":[0.481,0.11081,0.05671],"tcp_to_object_dist_end":0.04291,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.49488,0.06409,0.03403],"object_pos_start":[0.49485,0.06399,0.03401],"object_to_goal_dist_end":0.1443,"object_to_goal_dist_start":0.14421,"object_z_max":0.03404,"peak_contact_force":189.2422,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1642.0,"raw_peak_contact_force":199.16115,"tcp_end":[0.49338,0.09901,0.03762],"tcp_start":[0.48854,0.10587,0.04092],"tcp_to_object_dist_end":0.03514,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49303,-0.08087,0.03521],"object_pos_start":[0.49488,0.06409,0.03403],"object_to_goal_dist_end":0.00851,"object_to_goal_dist_start":0.1443,"object_z_max":0.0378,"peak_contact_force":1.48582,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2186.0,"raw_peak_contact_force":118.31441,"tcp_end":[0.49852,-0.05174,0.03745],"tcp_start":[0.49338,0.09901,0.03762],"tcp_to_object_dist_end":0.02973,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49308,-0.08003,0.03378],"object_pos_start":[0.49303,-0.08087,0.03521],"object_to_goal_dist_end":0.0093,"object_to_goal_dist_start":0.00851,"object_z_max":0.03548,"peak_contact_force":0.54658,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1321.0,"raw_peak_contact_force":59.15111,"tcp_end":[0.49658,0.00504,0.19257],"tcp_start":[0.49852,-0.05174,0.03745],"tcp_to_object_dist_end":0.18018,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.27317,"average_solve_count":205.0,"average_success_count":205.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00663,"approach_1.approach_height":0.27055,"approach_1.speed":0.01308,"contact_1.speed":0.04563,"push_1.push_distance":0.16218,"push_1.push_speed":0.09977},"optimized_scores":{"best_composite_score":0.09145,"best_fitness_score":0.48145,"best_task_score":0.25161},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":106.0,"contact_point_centroid":[0.47492,0.11854,0.05985],"force_p95":346.92903,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":355.37637,"mean_force":313.68239,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.47019,0.10819,0.06243]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":77.0,"contact_point_centroid":[0.47497,0.11534,0.05995],"force_p95":264.51795,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":265.19176,"mean_force":210.06859,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48012,0.10608,0.05752]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":402.0,"contact_point_centroid":[0.53378,0.09769,0.05996],"force_p95":212.63745,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":218.71081,"mean_force":164.8845,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48847,0.09663,0.0375]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":705.0,"contact_point_centroid":[0.53998,0.01789,0.05999],"force_p95":114.34252,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":148.24427,"mean_force":92.19181,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49492,0.01917,0.0373]},{"body_a":"attachment","body_b":"peg","contact_count":573.0,"contact_point_centroid":[0.50156,-0.01122,0.04415],"force_p95":68.01749,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":112.92068,"mean_force":13.07778,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49563,0.00021,0.03727]},{"body_a":"peg","body_b":"channel_base_body","contact_count":105.0,"contact_point_centroid":[0.50578,-0.10109,0.05606],"force_p95":89.20573,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":112.19355,"mean_force":45.76731,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49765,-0.0551,0.03687]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":2.0,"contact_point_centroid":[0.54313,-0.05519,0.05999],"force_p95":96.8861,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":98.09668,"mean_force":85.99088,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49842,-0.05903,0.03676]},{"body_a":"peg","body_b":"channel_base_body","contact_count":73.0,"contact_point_centroid":[0.50476,-0.10095,0.06062],"force_p95":27.76402,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.58211,"mean_force":12.38574,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49649,-0.05421,0.04029]},{"body_a":"attachment","body_b":"peg","contact_count":88.0,"contact_point_centroid":[0.50051,-0.0643,0.04826],"force_p95":26.6993,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.35592,"mean_force":10.34829,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49621,-0.05284,0.04215]},{"body_a":"peg","body_b":"channel_base_body","contact_count":671.0,"contact_point_centroid":[0.50282,-0.01467,0.00973],"force_p95":23.85768,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.18829,"mean_force":4.55191,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49466,0.02609,0.03734]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":193.0,"contact_point_centroid":[0.52512,-0.02329,0.02135],"force_p95":8.47268,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.89585,"mean_force":1.51715,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49556,0.00295,0.03736]},{"body_a":"peg","body_b":"channel_base_body","contact_count":930.0,"contact_point_centroid":[0.49648,-0.0768,0.00941],"force_p95":0.5838,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.01371,"mean_force":0.5685,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4955,-0.0186,0.116]},{"body_a":"peg","body_b":"channel_base_body","contact_count":854.0,"contact_point_centroid":[0.49433,0.05892,0.00937],"force_p95":0.55492,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56328,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48064,0.14718,0.16216]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49899,0.19829,0.29587]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":37.0,"contact_point_centroid":[0.47481,0.055,0.02588],"force_p95":0.47688,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.44975,"mean_force":0.29621,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49232,0.08504,0.03731]},{"body_a":"peg","body_b":"channel_base_body","contact_count":439.0,"contact_point_centroid":[0.49417,0.05911,0.0094],"force_p95":0.5506,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55347,"mean_force":0.54552,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48837,0.09684,0.03762]}],"total_contact_groups":17},"final_pose_error":0.10805,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49611,-0.07643,0.03378],"final_tcp_position":[0.49651,0.00246,0.19203],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":355.37637,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":883.0,"n_steps_budget":1000.0,"object_pos_end":[0.49422,0.0591,0.03391],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13935,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":328.62809,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":995.0,"raw_peak_contact_force":355.37637,"tcp_end":[0.4745,0.10691,0.06026],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.05804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":154.0,"n_steps_budget":1000.0,"object_pos_end":[0.49423,0.05912,0.03393],"object_pos_start":[0.49422,0.0591,0.03391],"object_to_goal_dist_end":0.13937,"object_to_goal_dist_start":0.13935,"object_z_max":0.03393,"peak_contact_force":0.54612,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":231.0,"raw_peak_contact_force":265.19176,"tcp_end":[0.48767,0.10104,0.041],"tcp_start":[0.4745,0.10691,0.06026],"tcp_to_object_dist_end":0.04302,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":439.0,"n_steps_budget":600.0,"object_pos_end":[0.49397,0.05919,0.03401],"object_pos_start":[0.49423,0.05912,0.03393],"object_to_goal_dist_end":0.13945,"object_to_goal_dist_start":0.13937,"object_z_max":0.03401,"peak_contact_force":179.51217,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":841.0,"raw_peak_contact_force":218.71081,"tcp_end":[0.49207,0.09351,0.03707],"tcp_start":[0.48767,0.10104,0.041],"tcp_to_object_dist_end":0.03451,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5057,-0.08691,0.03511],"object_pos_start":[0.49397,0.05919,0.03401],"object_to_goal_dist_end":0.0102,"object_to_goal_dist_start":0.13945,"object_z_max":0.0382,"peak_contact_force":137.58478,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2284.0,"raw_peak_contact_force":148.24427,"tcp_end":[0.49841,-0.05899,0.03676],"tcp_start":[0.49207,0.09351,0.03707],"tcp_to_object_dist_end":0.0289,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49611,-0.07643,0.03378],"object_pos_start":[0.5057,-0.08691,0.03511],"object_to_goal_dist_end":0.00816,"object_to_goal_dist_start":0.0102,"object_z_max":0.03837,"peak_contact_force":0.54648,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1093.0,"raw_peak_contact_force":98.09668,"tcp_end":[0.49651,0.00246,0.19203],"tcp_start":[0.49841,-0.05899,0.03676],"tcp_to_object_dist_end":0.17683,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```