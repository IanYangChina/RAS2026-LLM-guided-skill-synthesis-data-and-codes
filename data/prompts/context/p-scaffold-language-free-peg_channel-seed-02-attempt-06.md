## Search State

- **Seed**: 2
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 4 | 0.3477 | 0.21 | ❌ rejected |
| 5 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2835 | 0.23 | ❌ rejected |
| 4 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2845 | 0.23 | ✅ accepted |
| 3 | align → approach → contact → push → retract | linear_cartesian | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | admittance_control | position_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 3 | 0.2728 | 0.20 | ❌ rejected |
| 2 | approach → descend → push → retract | arc_cartesian | linear_cartesian | impedance_motion | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1941 | 0.12 | ❌ rejected |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`
- Frozen object start: [0.48092897073994534, 0.06387929147312987, 0.04]
- Frozen task target: [0.48092897073994534, -0.09612070852687013, 0.04]
- Goal object position: (0.48092897073994534, -0.09612070852687013, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.48092897073994534, 0.06387929147312987, 0.04)
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
  frozen_object_start: [0.4809, 0.0639, 0.04]
  frozen_task_target: [0.4809, -0.0961, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.48092897073994534, 0.06387929147312987, 0.04]}
  frozen_targets: {'channel_exit': [0.48092897073994534, -0.09612070852687013, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: 2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7

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
| `object` | offset from object initial position (0.48092897073994534, 0.06387929147312987, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.48092897073994534, -0.09612070852687013, 0.04) | final destination targets |
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

## Current Skill (Q=0.348) — your mutation base

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
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: force_exceeded
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: pose_tolerance
  parameters:
    push_depth:
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

- **Composite score**: 0.348
- **task_score** (E): 0.211
- **fitness_score**: 0.438  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.290

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| align_1 | 1.00 | 1.00 | 0.1932 |
| approach_1 | 1.00 | 1.00 | 0.0886 |
| contact_1 | 1.00 | 1.00 | 0.0080 |
| push_1 | 1.00 | 1.00 | 0.1447 |
| retract_1 | 1.00 | 1.00 | 0.1013 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| align_1 | align | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.499, 0.078, 0.153) | (0.494, 0.068, 0.040)→(0.498, 0.068, 0.034) | 0.151→0.148 | 1.00 / 1.000 | 0.547 | 3.659 |
| approach_1 | approach | 1.00 / step_budget | (0.499, 0.078, 0.153)→(0.496, 0.090, 0.067) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 1.000 | 0.547 | 0.552 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.090, 0.067)→(0.494, 0.088, 0.060) | (0.498, 0.068, 0.034)→(0.498, 0.068, 0.034) | 0.148→0.148 | 1.00 / 2.000 | 39.331 | 39.331 |
| push_1 | push | 1.00 / step_budget | (0.494, 0.088, 0.060)→(0.492, -0.056, 0.057) | (0.498, 0.068, 0.034)→(0.496, -0.007, 0.027) | 0.148→0.074 | 1.00 / 1.667 | 23.650 | 76.342 |
| retract_1 | retract | 1.00 / step_budget | (0.492, -0.056, 0.057)→(0.491, -0.049, 0.158) | (0.496, -0.007, 0.027)→(0.497, -0.009, 0.024) | 0.074→0.073 | 1.00 / 1.000 | 0.553 | 133.161 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.504
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.349
- phase_score: 0.624
- phase_breakdown.push_to_goal_score: 0.545
- phase_breakdown.reach_above_peg_score: 0.588
- phase_breakdown.reach_behind_peg_score: 0.779

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.514
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.349
- **Median Q (composite search score)**: 0.340
- **K-run variance**: 0.0035
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.256


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `6269840a353345700ffa70ea476a3ad730b138bf2ec3c52304c054f0e194e023`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a2936262b79fcd5a49fda15d77b54223f43c58bfee2e71dc505f8a2f79369706`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.83571,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00474,"align_1.lateral_offset_y":0.00843,"contact_1.contact_force_threshold":33.16876,"push_1.push_depth":0.17308},"optimized_scores":{"best_composite_score":0.42396,"best_fitness_score":0.51396,"best_task_score":0.34944},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":9.0,"contact_point_centroid":[0.47497,-0.07746,0.05861],"force_p95":321.03917,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":321.76633,"mean_force":273.78908,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48679,-0.07744,0.05672]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":194.0,"contact_point_centroid":[0.475,-0.05092,0.05825],"force_p95":53.01994,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":62.51481,"mean_force":39.39023,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48684,-0.05091,0.05635]},{"body_a":"peg","body_b":"channel_base_body","contact_count":883.0,"contact_point_centroid":[0.49637,0.01355,0.00909],"force_p95":58.07764,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":60.08289,"mean_force":29.91977,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48786,0.0029,0.05791]},{"body_a":"attachment","body_b":"peg","contact_count":592.0,"contact_point_centroid":[0.49749,0.03389,0.05808],"force_p95":58.03338,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.57629,"mean_force":43.89489,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48836,0.02999,0.05867]},{"body_a":"peg","body_b":"channel_base_body","contact_count":42.0,"contact_point_centroid":[0.4943,0.06385,0.0094],"force_p95":25.00064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.41965,"mean_force":5.24323,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48908,0.08703,0.06311]},{"body_a":"attachment","body_b":"peg","contact_count":8.0,"contact_point_centroid":[0.4994,0.08093,0.0588],"force_p95":41.74261,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.90533,"mean_force":24.78338,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4887,0.08609,0.06022]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47499,-0.00523,0.05955],"force_p95":5.83849,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.84755,"mean_force":3.63286,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48742,-0.02148,0.05754]},{"body_a":"peg","body_b":"channel_base_body","contact_count":336.0,"contact_point_centroid":[0.49566,0.06374,0.00935],"force_p95":0.62976,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57074,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49155,0.1402,0.22155]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49935,0.19713,0.2962]},{"body_a":"peg","body_b":"channel_base_body","contact_count":122.0,"contact_point_centroid":[0.49351,-0.0172,0.00805],"force_p95":0.68339,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.85994,"mean_force":0.60689,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48602,-0.07005,0.10018]},{"body_a":"peg","body_b":"channel_base_body","contact_count":218.0,"contact_point_centroid":[0.49496,0.06385,0.0094],"force_p95":0.55001,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55112,"mean_force":0.54575,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48672,0.09093,0.1108]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,-0.04164,0.02417],"force_p95":0.36257,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.36257,"mean_force":0.36257,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48617,-0.06761,0.1411]}],"total_contact_groups":12},"final_pose_error":0.04978,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49325,-0.01676,0.02419],"final_tcp_position":[0.4863,-0.06976,0.15697],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":321.76633,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.49526,0.06394,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14415,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54841,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":364.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_above_peg","tcp_end":[0.4849,0.08633,0.15362],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12221,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":218.0,"n_steps_budget":660.0,"object_pos_end":[0.4953,0.06385,0.03394],"object_pos_start":[0.49526,0.06394,0.03392],"object_to_goal_dist_end":0.14405,"object_to_goal_dist_start":0.14415,"object_z_max":0.03395,"peak_contact_force":0.55102,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":218.0,"raw_peak_contact_force":0.55112,"subtask_id":"reach_behind_peg","tcp_end":[0.49019,0.08832,0.06713],"tcp_start":[0.4849,0.08633,0.15362],"tcp_to_object_dist_end":0.04155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":42.0,"n_steps_budget":600.0,"object_pos_end":[0.49506,0.06355,0.03391],"object_pos_start":[0.4953,0.06385,0.03394],"object_to_goal_dist_end":0.14377,"object_to_goal_dist_start":0.14405,"object_z_max":0.03395,"peak_contact_force":50.41965,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":50.0,"raw_peak_contact_force":50.41965,"tcp_end":[0.48874,0.08598,0.05965],"tcp_start":[0.49019,0.08832,0.06713],"tcp_to_object_dist_end":0.03472,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":888.0,"n_steps_budget":1000.0,"object_pos_end":[0.49384,-0.01682,0.02413],"object_pos_start":[0.49506,0.06355,0.03391],"object_to_goal_dist_end":0.06544,"object_to_goal_dist_start":0.14377,"object_z_max":0.04061,"peak_contact_force":0.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1679.0,"raw_peak_contact_force":62.51481,"subtask_id":"push_to_goal","tcp_end":[0.48685,-0.07767,0.05612],"tcp_start":[0.48874,0.08598,0.05965],"tcp_to_object_dist_end":0.0691,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":122.0,"n_steps_budget":930.0,"object_pos_end":[0.49325,-0.01676,0.02419],"object_pos_start":[0.49384,-0.01682,0.02413],"object_to_goal_dist_end":0.06554,"object_to_goal_dist_start":0.06544,"object_z_max":0.02419,"peak_contact_force":0.59477,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":132.0,"raw_peak_contact_force":321.76633,"tcp_end":[0.4863,-0.06976,0.15697],"tcp_start":[0.48685,-0.07767,0.05612],"tcp_to_object_dist_end":0.14314,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `78f29ebb38dd2df9149fb0cd7c7c33d55e802bb94eee599b284bb0b197a04fb7`; realized-scene SHA-256: `990d03f436076caee02f5d9d8b3b9b0b3759564b7644084e4eac46818881d834`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.46685,0.05894,0.04]},{"name":"goal","value":[0.46685,-0.10106,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.46685,0.05894,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.46685,-0.10106,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.84286,"average_solve_count":140.0,"average_success_count":140.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.0058,"align_1.lateral_offset_y":-0.00308,"contact_1.contact_force_threshold":32.1582,"push_1.push_depth":0.16563},"optimized_scores":{"best_composite_score":0.33952,"best_fitness_score":0.42952,"best_task_score":0.16423},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":245.0,"contact_point_centroid":[0.475,-0.05082,0.05999],"force_p95":94.58128,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":109.91213,"mean_force":77.04074,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48562,-0.04556,0.05836]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":3.0,"contact_point_centroid":[0.475,-0.07874,0.05999],"force_p95":72.30385,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":73.34107,"mean_force":63.16111,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4859,-0.0741,0.05832]},{"body_a":"peg","body_b":"channel_base_body","contact_count":855.0,"contact_point_centroid":[0.49481,0.0108,0.00916],"force_p95":56.80686,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.04446,"mean_force":28.35614,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48567,0.00089,0.05879]},{"body_a":"attachment","body_b":"peg","contact_count":534.0,"contact_point_centroid":[0.49536,0.03387,0.05837],"force_p95":56.96811,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.54292,"mean_force":44.61058,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48567,0.03017,0.05905]},{"body_a":"peg","body_b":"channel_base_body","contact_count":38.0,"contact_point_centroid":[0.49611,0.0585,0.00939],"force_p95":25.6088,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.6556,"mean_force":3.83389,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48637,0.0806,0.06321]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.49746,0.07658,0.05876],"force_p95":32.27884,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.19009,"mean_force":25.09412,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.48604,0.07977,0.0604]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47499,0.00067,0.06],"force_p95":11.72503,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":13.01048,"mean_force":8.53507,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4856,-0.01561,0.0588]},{"body_a":"peg","body_b":"channel_base_body","contact_count":359.0,"contact_point_centroid":[0.49457,0.05887,0.00934],"force_p95":0.60751,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.20518,"mean_force":0.58696,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.48538,0.13185,0.22077]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46807,0.05895,0.03796],"force_p95":1.19991,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.42382,"mean_force":0.50385,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49881,0.19587,0.29493]},{"body_a":"peg","body_b":"channel_base_body","contact_count":117.0,"contact_point_centroid":[0.49375,-0.0192,0.00801],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72557,"mean_force":0.60543,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48451,-0.0667,0.10408]},{"body_a":"peg","body_b":"channel_base_body","contact_count":229.0,"contact_point_centroid":[0.49385,0.05901,0.00939],"force_p95":0.55072,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55326,"mean_force":0.54621,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47915,0.07978,0.11065]}],"total_contact_groups":11},"final_pose_error":0.04985,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4937,-0.01939,0.0241],"final_tcp_position":[0.48522,-0.06627,0.15908],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.46685,0.05894,0.04]},"peak_contact_force":109.91213,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":388.0,"n_steps_budget":1000.0,"object_pos_end":[0.4942,0.05903,0.03385],"object_pos_start":[0.46685,0.05894,0.04],"object_to_goal_dist_end":0.13929,"object_to_goal_dist_start":0.14284,"object_z_max":0.04001,"peak_contact_force":0.54657,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":394.0,"raw_peak_contact_force":4.20518,"subtask_id":"reach_above_peg","tcp_end":[0.47322,0.07085,0.15273],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1213,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":229.0,"n_steps_budget":660.0,"object_pos_end":[0.49421,0.05885,0.03388],"object_pos_start":[0.4942,0.05903,0.03385],"object_to_goal_dist_end":0.13911,"object_to_goal_dist_start":0.13929,"object_z_max":0.03388,"peak_contact_force":0.54291,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":229.0,"raw_peak_contact_force":0.55326,"subtask_id":"reach_behind_peg","tcp_end":[0.48728,0.0816,0.06684],"tcp_start":[0.47322,0.07085,0.15273],"tcp_to_object_dist_end":0.04064,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":38.0,"n_steps_budget":600.0,"object_pos_end":[0.4943,0.05893,0.03387],"object_pos_start":[0.49421,0.05885,0.03388],"object_to_goal_dist_end":0.13918,"object_to_goal_dist_start":0.13911,"object_z_max":0.03388,"peak_contact_force":33.6556,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":43.0,"raw_peak_contact_force":33.6556,"tcp_end":[0.48604,0.07967,0.05997],"tcp_start":[0.48728,0.0816,0.06684],"tcp_to_object_dist_end":0.03435,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":864.0,"n_steps_budget":1000.0,"object_pos_end":[0.49376,-0.01947,0.0241],"object_pos_start":[0.4943,0.05893,0.03387],"object_to_goal_dist_end":0.0629,"object_to_goal_dist_start":0.13918,"object_z_max":0.04077,"peak_contact_force":69.5367,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1662.0,"raw_peak_contact_force":109.91213,"subtask_id":"push_to_goal","tcp_end":[0.48591,-0.07403,0.05831],"tcp_start":[0.48604,0.07967,0.05997],"tcp_to_object_dist_end":0.06488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":117.0,"n_steps_budget":930.0,"object_pos_end":[0.4937,-0.01939,0.0241],"object_pos_start":[0.49376,-0.01947,0.0241],"object_to_goal_dist_end":0.06298,"object_to_goal_dist_start":0.0629,"object_z_max":0.0241,"peak_contact_force":0.56201,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":120.0,"raw_peak_contact_force":73.34107,"tcp_end":[0.48522,-0.06627,0.15908],"tcp_start":[0.48591,-0.07403,0.05831],"tcp_to_object_dist_end":0.14314,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `ecba62e37d233197bb248f7fe6e722b45204af5e83240a6f27138a89bcccfe42`; realized-scene SHA-256: `5d75b33f12bcf5a2f8bdcc4693a93f63ce145f4d32d6acfe75032964e261854c`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53544,0.08091,0.04]},{"name":"goal","value":[0.53544,-0.07909,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53544,0.08091,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53544,-0.07909,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.82707,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.01192,"align_1.lateral_offset_y":-0.01648,"contact_1.contact_force_threshold":31.32774,"push_1.push_depth":0.1247},"optimized_scores":{"best_composite_score":0.27963,"best_fitness_score":0.36963,"best_task_score":0.11917},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":589.0,"contact_point_centroid":[0.51099,0.04471,0.00947],"force_p95":55.25363,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.59888,"mean_force":39.37731,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50585,0.04412,0.05874]},{"body_a":"attachment","body_b":"peg","contact_count":531.0,"contact_point_centroid":[0.51409,0.05508,0.05859],"force_p95":54.90039,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.09664,"mean_force":43.17747,"phase_index":3.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50609,0.04974,0.05901]},{"body_a":"peg","body_b":"channel_base_body","contact_count":39.0,"contact_point_centroid":[0.50596,0.08183,0.00938],"force_p95":3.03649,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.91745,"mean_force":2.04002,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50758,0.09997,0.06386]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.51758,0.09468,0.05862],"force_p95":32.99156,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.41639,"mean_force":29.1681,"phase_index":2.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50654,0.09905,0.06023]},{"body_a":"peg","body_b":"channel_base_body","contact_count":118.0,"contact_point_centroid":[0.49871,0.01832,0.00902],"force_p95":1.14439,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.37429,"mean_force":0.6496,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50114,-0.01035,0.10143]},{"body_a":"peg","body_b":"channel_base_body","contact_count":368.0,"contact_point_centroid":[0.50562,0.08091,0.00935],"force_p95":0.56485,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.32595,"mean_force":0.58823,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52024,0.13564,0.22001]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50299,-0.00569,0.05592],"force_p95":3.39068,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.15833,"mean_force":1.30083,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50239,-0.01762,0.05594]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":36.0,"contact_point_centroid":[0.5324,0.0809,0.02649],"force_p95":1.27622,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70803,"mean_force":0.52144,"phase_index":0.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50085,0.19606,0.2948]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47487,-0.0117,0.03571],"force_p95":1.09699,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.12981,"mean_force":0.70366,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50038,-0.01086,0.08147]},{"body_a":"peg","body_b":"channel_base_body","contact_count":212.0,"contact_point_centroid":[0.50591,0.08074,0.00938],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55014,"mean_force":0.54677,"phase_index":1.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52491,0.09234,0.11151]}],"total_contact_groups":10},"final_pose_error":0.04912,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50355,0.00772,0.02401],"final_tcp_position":[0.50203,-0.00998,0.157],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53544,0.08091,0.04]},"peak_contact_force":56.59888,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.08086,0.03378],"object_pos_start":[0.53544,0.08091,0.04],"object_to_goal_dist_end":0.16109,"object_to_goal_dist_start":0.16476,"object_z_max":0.04001,"peak_contact_force":0.54621,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":404.0,"raw_peak_contact_force":4.32595,"subtask_id":"reach_above_peg","tcp_end":[0.53956,0.07829,0.15143],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12238,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":212.0,"n_steps_budget":690.0,"object_pos_end":[0.50596,0.08089,0.03378],"object_pos_start":[0.50598,0.08086,0.03378],"object_to_goal_dist_end":0.16112,"object_to_goal_dist_start":0.16109,"object_z_max":0.03378,"peak_contact_force":0.54639,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":212.0,"raw_peak_contact_force":0.55014,"subtask_id":"reach_behind_peg","tcp_end":[0.50929,0.10076,0.06801],"tcp_start":[0.53956,0.07829,0.15143],"tcp_to_object_dist_end":0.03972,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":39.0,"n_steps_budget":600.0,"object_pos_end":[0.50601,0.0809,0.03378],"object_pos_start":[0.50596,0.08089,0.03378],"object_to_goal_dist_end":0.16113,"object_to_goal_dist_start":0.16112,"object_z_max":0.03378,"peak_contact_force":33.91745,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":41.0,"raw_peak_contact_force":33.91745,"tcp_end":[0.50649,0.09898,0.05998],"tcp_start":[0.50929,0.10076,0.06801],"tcp_to_object_dist_end":0.03184,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":592.0,"n_steps_budget":780.0,"object_pos_end":[0.50091,0.01423,0.03421],"object_pos_start":[0.50601,0.0809,0.03378],"object_to_goal_dist_end":0.09441,"object_to_goal_dist_start":0.16113,"object_z_max":0.04053,"peak_contact_force":1.41452,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1120.0,"raw_peak_contact_force":56.59888,"subtask_id":"push_to_goal","tcp_end":[0.50301,-0.01755,0.05553],"tcp_start":[0.50649,0.09898,0.05998],"tcp_to_object_dist_end":0.03832,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":120.0,"n_steps_budget":930.0,"object_pos_end":[0.50355,0.00772,0.02401],"object_pos_start":[0.50091,0.01423,0.03421],"object_to_goal_dist_end":0.08924,"object_to_goal_dist_start":0.09441,"object_z_max":0.03447,"peak_contact_force":0.5013,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":135.0,"raw_peak_contact_force":4.37429,"tcp_end":[0.50203,-0.00998,0.157],"tcp_start":[0.50301,-0.01755,0.05553],"tcp_to_object_dist_end":0.13418,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```