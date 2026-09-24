## Search State

- **Seed**: 1
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 4 | 0.3286 | 0.00 | ❌ rejected |
| 5 | approach → align → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1682 | 0.00 | ❌ rejected |
| 4 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1680 | 0.40 | ✅ accepted |
| 3 | rotate → align → push → align | impedance_motion | linear_cartesian | impedance_motion | linear_cartesian | impedance_control | position_control | impedance_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | 3 | 0.1494 | 0.30 | ✅ accepted |
| 2 | approach → descend → push → push | linear_cartesian | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | force_threshold_switch | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | time_limit | 6 | -0.3041 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.329) — your mutation base

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

- **Composite score**: 0.329
- **task_score** (E): 0.000
- **fitness_score**: 0.225  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above | 1.00 | 1.00 | 0.1772 |
| descend_to_push | 1.00 | 1.00 | 0.0888 |
| push_along_channel | 0.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.481, 0.115, 0.147) | (0.483, 0.080, 0.040)→(0.497, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.000 | 55.443 | 55.443 |
| descend_to_push | descend | 1.00 / force_exceeded | (0.481, 0.115, 0.147)→(0.489, 0.110, 0.059) | (0.497, 0.080, 0.034)→(0.497, 0.080, 0.034) | 0.160→0.160 | 1.00 / 2.000 | 55.654 | 95.427 |
| push_along_channel | push | 0.00 / guard_failure | (0.489, 0.110, 0.059)→(0.489, 0.110, 0.059) | (0.497, 0.080, 0.034)→(0.497, 0.079, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.538 | 2.857 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.002
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.001
- phase_score: 0.397
- phase_breakdown.reach_above_peg_score: 0.821
- phase_breakdown.reach_push_start_score: 0.725
- phase_breakdown.push_through_channel_score: 0.030

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.239
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: 0.340
- **K-run variance**: 0.0003
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86538,"average_solve_count":52.0,"average_success_count":52.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.12567,"descend_to_push.contact_force":12.95362,"push_along_channel.push_distance":0.1464,"push_along_channel.push_speed":0.03056},"optimized_scores":{"best_composite_score":0.34007,"best_fitness_score":0.23674,"best_task_score":0.00014},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.49849,0.207,-0.00019],"force_p95":91.82839,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":95.78042,"mean_force":67.79957,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49734,0.14498,0.05395]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.4985,0.207,-6e-05],"force_p95":64.45639,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":64.45639,"mean_force":64.45639,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.49734,0.14498,0.0542]},{"body_a":"peg","body_b":"channel_base_body","contact_count":457.0,"contact_point_centroid":[0.50084,0.11603,0.00938],"force_p95":0.61627,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.5606,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49829,0.17427,0.22182]},{"body_a":"peg","body_b":"channel_base_body","contact_count":477.0,"contact_point_centroid":[0.50096,0.11588,0.00946],"force_p95":0.60701,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64886,"mean_force":0.53964,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.49453,0.14876,0.08953]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.50689,0.11771,0.00937],"force_p95":0.6083,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.6191,"mean_force":0.5388,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49734,0.14498,0.05395]}],"total_contact_groups":5},"final_pose_error":0.14641,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50089,0.11601,0.03376],"final_tcp_position":[0.49733,0.14499,0.05386],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":95.78042,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":473.0,"n_steps_budget":840.0,"object_pos_end":[0.50093,0.11602,0.03383],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":64.45639,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":478.0,"raw_peak_contact_force":64.45639,"subtask_id":"reach_above_peg","tcp_end":[0.49802,0.14971,0.14856],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":477.0,"n_steps_budget":720.0,"object_pos_end":[0.50099,0.11602,0.03376],"object_pos_start":[0.50093,0.11602,0.03383],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19612,"object_z_max":0.03416,"peak_contact_force":51.35816,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6.0,"raw_peak_contact_force":95.78042,"subtask_id":"reach_push_start","tcp_end":[0.49735,0.14498,0.05402],"tcp_start":[0.49802,0.14971,0.14856],"tcp_to_object_dist_end":0.03553,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11602,0.03376],"object_pos_start":[0.50099,0.11602,0.03376],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19612,"object_z_max":0.03376,"peak_contact_force":0.5189,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":457.0,"raw_peak_contact_force":1.92055,"subtask_id":"push_through_channel","tcp_end":[0.49733,0.14499,0.05386],"tcp_start":[0.49733,0.14498,0.05389],"tcp_to_object_dist_end":0.03544,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.8871,"average_solve_count":62.0,"average_success_count":62.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.1048,"descend_to_push.contact_force":18.51023,"push_along_channel.push_distance":0.14643,"push_along_channel.push_speed":0.06508},"optimized_scores":{"best_composite_score":0.34198,"best_fitness_score":0.23865,"best_task_score":0.00112},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.48824,0.15582,-0.00014],"force_p95":86.22491,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":89.73791,"mean_force":64.78604,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48867,0.09376,0.05401]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.48821,0.15583,-2e-05],"force_p95":67.168,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":67.168,"mean_force":67.168,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.48864,0.09377,0.05424]},{"body_a":"peg","body_b":"channel_base_body","contact_count":546.0,"contact_point_centroid":[0.49537,0.06399,0.00937],"force_p95":0.58292,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56114,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48861,0.14855,0.21917]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49926,0.19819,0.29723]},{"body_a":"peg","body_b":"channel_base_body","contact_count":525.0,"contact_point_centroid":[0.49509,0.06389,0.0094],"force_p95":0.55082,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54537,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.47923,0.09918,0.08903]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.48252,0.05154,0.0094],"force_p95":0.547,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54728,"mean_force":0.54494,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48867,0.09376,0.05401]}],"total_contact_groups":6},"final_pose_error":0.14641,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49502,0.0636,0.03402],"final_tcp_position":[0.48868,0.09374,0.05393],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":89.73791,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.49492,0.06375,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14397,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":67.168,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":526.0,"raw_peak_contact_force":67.168,"subtask_id":"reach_above_peg","tcp_end":[0.47941,0.1008,0.14686],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11984,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":525.0,"n_steps_budget":720.0,"object_pos_end":[0.49485,0.06373,0.03402],"object_pos_start":[0.49492,0.06375,0.03394],"object_to_goal_dist_end":0.14395,"object_to_goal_dist_start":0.14397,"object_z_max":0.03402,"peak_contact_force":50.01227,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6.0,"raw_peak_contact_force":89.73791,"subtask_id":"reach_push_start","tcp_end":[0.48867,0.09376,0.05407],"tcp_start":[0.47941,0.1008,0.14686],"tcp_to_object_dist_end":0.03664,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49489,0.06367,0.03402],"object_pos_start":[0.49485,0.06373,0.03402],"object_to_goal_dist_end":0.14389,"object_to_goal_dist_start":0.14395,"object_z_max":0.03402,"peak_contact_force":0.55002,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":574.0,"raw_peak_contact_force":2.44546,"subtask_id":"push_through_channel","tcp_end":[0.48868,0.09374,0.05393],"tcp_start":[0.48868,0.09375,0.05396],"tcp_to_object_dist_end":0.03659,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.12,"average_solve_count":50.0,"average_success_count":50.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_speed":0.14519,"descend_to_push.contact_force":17.14018,"push_along_channel.push_distance":0.1647,"push_along_channel.push_speed":0.06656},"optimized_scores":{"best_composite_score":0.30367,"best_fitness_score":0.20034,"best_task_score":0.00019},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.47494,0.12,0.05991],"force_p95":97.84339,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":100.76199,"mean_force":79.30935,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48146,0.09007,0.07004]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47497,0.12,0.05996],"force_p95":34.70332,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":34.70332,"mean_force":34.70332,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.48139,0.09009,0.07021]},{"body_a":"peg","body_b":"channel_base_body","contact_count":528.0,"contact_point_centroid":[0.49445,0.05891,0.00935],"force_p95":0.56947,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.57392,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.48186,0.14582,0.2187]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.49885,0.19755,0.29619]},{"body_a":"peg","body_b":"channel_base_body","contact_count":472.0,"contact_point_centroid":[0.49393,0.05903,0.00939],"force_p95":0.55016,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55382,"mean_force":0.54599,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"descend","tcp_position_centroid":[0.46842,0.09592,0.09494]},{"body_a":"peg","body_b":"channel_base_body","contact_count":3.0,"contact_point_centroid":[0.49935,0.04227,0.0094],"force_p95":0.54595,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54653,"mean_force":0.54212,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.48146,0.09007,0.07004]}],"total_contact_groups":6},"final_pose_error":0.16465,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49428,0.05885,0.03393],"final_tcp_position":[0.48153,0.09003,0.06999],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":100.76199,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":557.0,"n_steps_budget":870.0,"object_pos_end":[0.49419,0.05907,0.03387],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13933,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":34.70332,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":473.0,"raw_peak_contact_force":34.70332,"subtask_id":"reach_above_peg","tcp_end":[0.46636,0.09599,0.14672],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":472.0,"n_steps_budget":750.0,"object_pos_end":[0.49412,0.05877,0.03393],"object_pos_start":[0.49419,0.05907,0.03387],"object_to_goal_dist_end":0.13902,"object_to_goal_dist_start":0.13933,"object_z_max":0.03393,"peak_contact_force":65.59007,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":6.0,"raw_peak_contact_force":100.76199,"subtask_id":"reach_push_start","tcp_end":[0.48143,0.09008,0.07008],"tcp_start":[0.46636,0.09599,0.14672],"tcp_to_object_dist_end":0.04949,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.49418,0.05878,0.03393],"object_pos_start":[0.49412,0.05877,0.03393],"object_to_goal_dist_end":0.13903,"object_to_goal_dist_start":0.13902,"object_z_max":0.03393,"peak_contact_force":0.54445,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":563.0,"raw_peak_contact_force":4.20518,"subtask_id":"push_through_channel","tcp_end":[0.48153,0.09003,0.06999],"tcp_start":[0.4815,0.09005,0.07001],"tcp_to_object_dist_end":0.04937,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```