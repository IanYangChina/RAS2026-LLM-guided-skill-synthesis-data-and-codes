## Search State

- **Seed**: 1
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1858 | 0.16 | ❌ rejected |
| 2 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.1872 | 0.00 | ❌ rejected |
| 1 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2338 | 0.64 | ✅ accepted |
| 0 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | admittance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2185 | 0.60 | ✅ accepted |

**Proposal policy**: task_score is 0.16 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.186) — your mutation base

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

- **Composite score**: -0.186
- **task_score** (E): 0.162
- **fitness_score**: 0.154  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1730 |
| approach_1 | 1.00 | 1.00 | 0.0686 |
| contact_1 | 1.00 | 1.00 | 0.0213 |
| push_1 | 0.00 | 1.00 | 0.0173 |
| retract_1 | 1.00 | 1.00 | 0.1196 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.483, 0.101, 0.162) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 1.000 | 0.543 | 2.857 |
| approach_1 | approach | 1.00 / step_budget | (0.483, 0.101, 0.162)→(0.493, 0.098, 0.096) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.537 | 0.588 |
| contact_1 | contact | 1.00 / force_exceeded | (0.493, 0.098, 0.096)→(0.492, 0.096, 0.075) | (0.497, 0.080, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 25.296 | 25.296 |
| push_1 | push | 0.00 / guard_failure | (0.492, 0.096, 0.075)→(0.491, 0.079, 0.073) | (0.497, 0.079, 0.034)→(0.497, 0.061, 0.037) | 0.160→0.141 | 1.00 / 2.000 | 41.334 | 64.317 |
| retract_1 | retract | 1.00 / step_budget | (0.491, 0.079, 0.073)→(0.488, 0.086, 0.193) | (0.497, 0.061, 0.037)→(0.495, 0.054, 0.031) | 0.141→0.134 | 1.00 / 1.000 | 0.577 | 62.714 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.483
- alignment_error: None
- force_efficiency: 0.559
- terminal_score: 0.483
- phase_score: 0.251
- phase_breakdown.pre_insertion_score: 0.199
- phase_breakdown.push_complete_score: 0.273

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.344
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.483
- **Median Q (composite search score)**: -0.272
- **K-run variance**: 0.0180
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.308


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.03093,"average_solve_count":194.0,"average_success_count":194.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00224,"align_1.lateral_offset_y":0.00746,"approach_1.approach_height":0.03452,"approach_1.speed":0.02876,"contact_1.force_threshold":4.39038,"contact_1.speed":0.02212,"push_1.push_distance":0.16625,"push_1.push_speed":0.01253,"retract_1.speed":0.08078},"optimized_scores":{"best_composite_score":0.00355,"best_fitness_score":0.34355,"best_task_score":0.48302},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":988.0,"contact_point_centroid":[0.4983,0.10556,0.04374],"force_p95":6.45156,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.05595,"mean_force":3.87213,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49394,0.10552,0.05486]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49996,0.08045,0.00994],"force_p95":6.76109,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.00359,"mean_force":4.22079,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49397,0.10586,0.05491]},{"body_a":"peg","body_b":"channel_base_body","contact_count":72.0,"contact_point_centroid":[0.50156,0.11297,0.00943],"force_p95":1.50725,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.49865,"mean_force":0.8467,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49712,0.13491,0.06561]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50083,0.13385,0.0494],"force_p95":9.29906,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.20455,"mean_force":4.71303,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49688,0.13402,0.0607]},{"body_a":"peg","body_b":"channel_base_body","contact_count":993.0,"contact_point_centroid":[0.4977,0.04084,0.0082],"force_p95":0.74222,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.75248,"mean_force":0.67961,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49138,0.09197,0.11964]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.49784,0.08236,0.0438],"force_p95":6.74235,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.25897,"mean_force":1.60948,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49375,0.0823,0.05497]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":17.0,"contact_point_centroid":[0.52514,0.06162,0.02444],"force_p95":7.63204,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.78557,"mean_force":1.99744,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49103,0.08812,0.07118]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":16.0,"contact_point_centroid":[0.47499,0.01777,0.02642],"force_p95":7.17431,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.27947,"mean_force":3.05797,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49131,0.09352,0.10979]},{"body_a":"peg","body_b":"channel_base_body","contact_count":655.0,"contact_point_centroid":[0.5009,0.11604,0.0094],"force_p95":0.61533,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.5545,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49645,0.17761,0.22465]},{"body_a":"peg","body_b":"channel_base_body","contact_count":505.0,"contact_point_centroid":[0.50087,0.11595,0.00942],"force_p95":0.61028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65769,"mean_force":0.54266,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49843,0.1455,0.11761]}],"total_contact_groups":10},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4965,0.03875,0.0241],"final_tcp_position":[0.49173,0.08655,0.18573],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":22.05595,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":671.0,"n_steps_budget":960.0,"object_pos_end":[0.50097,0.11615,0.03396],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19625,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.5457,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":655.0,"raw_peak_contact_force":1.92055,"subtask_id":"pre_insertion","tcp_end":[0.50072,0.14565,0.16375],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1331,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":505.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11605,0.03388],"object_pos_start":[0.50097,0.11615,0.03396],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19625,"object_z_max":0.03401,"peak_contact_force":0.51676,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":505.0,"raw_peak_contact_force":0.65769,"subtask_id":"pre_insertion","tcp_end":[0.49792,0.1363,0.07164],"tcp_start":[0.50072,0.14565,0.16375],"tcp_to_object_dist_end":0.04296,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":72.0,"n_steps_budget":600.0,"object_pos_end":[0.50091,0.11575,0.03419],"object_pos_start":[0.50095,0.11605,0.03388],"object_to_goal_dist_end":0.19584,"object_to_goal_dist_start":0.19615,"object_z_max":0.03415,"peak_contact_force":10.49865,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":77.0,"raw_peak_contact_force":10.49865,"subtask_id":"pre_insertion","tcp_end":[0.49692,0.13382,0.05937],"tcp_start":[0.49792,0.1363,0.07164],"tcp_to_object_dist_end":0.03125,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50205,0.06242,0.04042],"object_pos_start":[0.50091,0.11575,0.03419],"object_to_goal_dist_end":0.14244,"object_to_goal_dist_start":0.19584,"object_z_max":0.04063,"peak_contact_force":5.9133,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1988.0,"raw_peak_contact_force":22.05595,"subtask_id":"push_complete","tcp_end":[0.49388,0.0824,0.05493],"tcp_start":[0.49692,0.13382,0.05937],"tcp_to_object_dist_end":0.026,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4965,0.03875,0.0241],"object_pos_start":[0.50205,0.06242,0.04042],"object_to_goal_dist_end":0.11986,"object_to_goal_dist_start":0.14244,"object_z_max":0.04042,"peak_contact_force":0.63684,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1033.0,"raw_peak_contact_force":9.75248,"tcp_end":[0.49173,0.08655,0.18573],"tcp_start":[0.49388,0.0824,0.05493],"tcp_to_object_dist_end":0.16862,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46617,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00593,"align_1.lateral_offset_y":-0.00122,"approach_1.approach_height":0.06851,"approach_1.speed":0.07434,"contact_1.force_threshold":8.19883,"contact_1.speed":0.02695,"push_1.push_distance":0.06271,"push_1.push_speed":0.02515,"retract_1.speed":0.07225},"optimized_scores":{"best_composite_score":-0.28863,"best_fitness_score":0.05137,"best_task_score":0.00148},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.475,0.11986,0.04304],"force_p95":100.64004,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":105.87429,"mean_force":62.12711,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48929,0.07982,0.06957]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.475,0.11988,0.0433],"force_p95":43.7405,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":44.2263,"mean_force":36.33305,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4895,0.07988,0.06974]},{"body_a":"peg","body_b":"channel_base_body","contact_count":18.0,"contact_point_centroid":[0.49701,0.04649,0.00947],"force_p95":25.32489,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.27643,"mean_force":7.96415,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48983,0.08046,0.07022]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.49337,0.08085,0.05919],"force_p95":25.49376,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.87994,"mean_force":16.9085,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4901,0.08086,0.0706]},{"body_a":"peg","body_b":"channel_base_body","contact_count":204.0,"contact_point_centroid":[0.49481,0.06346,0.00941],"force_p95":0.5507,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.35159,"mean_force":0.6226,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48993,0.08167,0.08769]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49114,0.0808,0.05918],"force_p95":15.92295,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.92295,"mean_force":15.92295,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49028,0.08094,0.07108]},{"body_a":"peg","body_b":"channel_base_body","contact_count":884.0,"contact_point_centroid":[0.49522,0.06388,0.00938],"force_p95":0.55928,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55514,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48979,0.14797,0.22532]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5043,0.21552,0.29323]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49524,0.06317,0.00942],"force_p95":0.55328,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.07857,"mean_force":0.5434,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48699,0.08973,0.12898]},{"body_a":"peg","body_b":"channel_base_body","contact_count":332.0,"contact_point_centroid":[0.49526,0.06408,0.0094],"force_p95":0.55107,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55315,"mean_force":0.54523,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4872,0.0875,0.13312]}],"total_contact_groups":10},"final_pose_error":0.02944,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49482,0.06351,0.03403],"final_tcp_position":[0.48731,0.08669,0.19106],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":105.87429,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":911.0,"n_steps_budget":1000.0,"object_pos_end":[0.49514,0.06361,0.034],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14382,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54129,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":912.0,"raw_peak_contact_force":2.44546,"subtask_id":"pre_insertion","tcp_end":[0.4852,0.08696,0.16193],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13042,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":332.0,"n_steps_budget":600.0,"object_pos_end":[0.49482,0.06379,0.03402],"object_pos_start":[0.49514,0.06361,0.034],"object_to_goal_dist_end":0.14401,"object_to_goal_dist_start":0.14382,"object_z_max":0.03402,"peak_contact_force":0.54863,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":332.0,"raw_peak_contact_force":0.55315,"subtask_id":"pre_insertion","tcp_end":[0.49114,0.08314,0.10507],"tcp_start":[0.4852,0.08696,0.16193],"tcp_to_object_dist_end":0.07373,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.49518,0.06357,0.03403],"object_pos_start":[0.49482,0.06379,0.03402],"object_to_goal_dist_end":0.14378,"object_to_goal_dist_start":0.14401,"object_z_max":0.03403,"peak_contact_force":16.35159,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":205.0,"raw_peak_contact_force":16.35159,"subtask_id":"pre_insertion","tcp_end":[0.49029,0.08094,0.07093],"tcp_start":[0.49114,0.08314,0.10507],"tcp_to_object_dist_end":0.04107,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.49583,0.06154,0.03541],"object_pos_start":[0.49518,0.06357,0.03403],"object_to_goal_dist_end":0.14168,"object_to_goal_dist_start":0.14378,"object_z_max":0.03552,"peak_contact_force":44.2263,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":31.0,"raw_peak_contact_force":44.2263,"subtask_id":"push_complete","tcp_end":[0.4894,0.07972,0.06958],"tcp_start":[0.48942,0.07973,0.06966],"tcp_to_object_dist_end":0.03924,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49482,0.06351,0.03403],"object_pos_start":[0.49594,0.06137,0.03562],"object_to_goal_dist_end":0.14373,"object_to_goal_dist_start":0.1415,"object_z_max":0.0361,"peak_contact_force":0.54466,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1007.0,"raw_peak_contact_force":105.87429,"tcp_end":[0.48731,0.08669,0.19106],"tcp_start":[0.4894,0.07972,0.06958],"tcp_to_object_dist_end":0.1589,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.29921,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00251,"align_1.lateral_offset_y":-0.01347,"approach_1.approach_height":0.07701,"approach_1.speed":0.06828,"contact_1.force_threshold":8.49983,"contact_1.speed":0.02683,"push_1.push_distance":0.11816,"push_1.push_speed":0.04316,"retract_1.speed":0.05225},"optimized_scores":{"best_composite_score":-0.27237,"best_fitness_score":0.06763,"best_task_score":0.00034},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47499,0.11995,0.05997],"force_p95":121.7039,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":126.66921,"mean_force":92.51598,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48842,0.07471,0.09576]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.47499,0.11997,0.05998],"force_p95":70.7918,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":72.51538,"mean_force":59.28262,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48848,0.0748,0.09567]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.47499,0.11998,0.05999],"force_p95":49.03657,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":49.03657,"mean_force":49.03657,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48838,0.07467,0.09597]},{"body_a":"peg","body_b":"channel_base_body","contact_count":968.0,"contact_point_centroid":[0.4943,0.05891,0.00937],"force_p95":0.55424,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.56123,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.4796,0.13921,0.22541]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50287,0.22102,0.28805]},{"body_a":"peg","body_b":"channel_base_body","contact_count":98.0,"contact_point_centroid":[0.49381,0.05908,0.0094],"force_p95":0.55231,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55392,"mean_force":0.54518,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48883,0.0749,0.10437]},{"body_a":"peg","body_b":"channel_base_body","contact_count":481.0,"contact_point_centroid":[0.49413,0.05916,0.0094],"force_p95":0.55059,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55347,"mean_force":0.54554,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47788,0.07273,0.13828]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49414,0.05896,0.00941],"force_p95":0.55051,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55316,"mean_force":0.54507,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48619,0.08503,0.14726]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.47737,0.05355,0.0094],"force_p95":0.54928,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54937,"mean_force":0.54753,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48842,0.07471,0.09576]}],"total_contact_groups":9},"final_pose_error":0.04555,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49387,0.05878,0.03404],"final_tcp_position":[0.48644,0.08537,0.20143],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":126.66921,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":997.0,"n_steps_budget":1000.0,"object_pos_end":[0.49426,0.05909,0.03393],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13935,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.5431,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1003.0,"raw_peak_contact_force":4.20518,"subtask_id":"pre_insertion","tcp_end":[0.46364,0.07001,0.16171],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13185,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":481.0,"n_steps_budget":600.0,"object_pos_end":[0.49388,0.05908,0.03401],"object_pos_start":[0.49426,0.05909,0.03393],"object_to_goal_dist_end":0.13935,"object_to_goal_dist_start":0.13935,"object_z_max":0.03401,"peak_contact_force":0.54446,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":481.0,"raw_peak_contact_force":0.55347,"subtask_id":"pre_insertion","tcp_end":[0.48996,0.07546,0.11274],"tcp_start":[0.46364,0.07001,0.16171],"tcp_to_object_dist_end":0.08052,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":98.0,"n_steps_budget":1000.0,"object_pos_end":[0.49384,0.05895,0.03402],"object_pos_start":[0.49388,0.05908,0.03401],"object_to_goal_dist_end":0.13921,"object_to_goal_dist_start":0.13935,"object_z_max":0.03402,"peak_contact_force":49.03657,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":99.0,"raw_peak_contact_force":49.03657,"subtask_id":"pre_insertion","tcp_end":[0.48839,0.07469,0.09581],"tcp_start":[0.48996,0.07546,0.11274],"tcp_to_object_dist_end":0.06401,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49385,0.05887,0.03402],"object_pos_start":[0.49384,0.05895,0.03402],"object_to_goal_dist_end":0.13914,"object_to_goal_dist_start":0.13921,"object_z_max":0.03402,"peak_contact_force":73.86256,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":6.0,"raw_peak_contact_force":126.66921,"subtask_id":"push_complete","tcp_end":[0.48847,0.07477,0.09568],"tcp_start":[0.48845,0.07474,0.09571],"tcp_to_object_dist_end":0.06391,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49387,0.05878,0.03404],"object_pos_start":[0.49393,0.05875,0.03402],"object_to_goal_dist_end":0.13905,"object_to_goal_dist_start":0.13901,"object_z_max":0.03404,"peak_contact_force":0.549,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1003.0,"raw_peak_contact_force":72.51538,"tcp_end":[0.48644,0.08537,0.20143],"tcp_start":[0.48847,0.07477,0.09568],"tcp_to_object_dist_end":0.16965,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```