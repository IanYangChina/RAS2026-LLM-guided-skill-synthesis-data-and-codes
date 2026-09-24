## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7  | -0.0814 | 0.02 | ❌ rejected |
| 5 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 5  | 0.2691 | 0.74 | ❌ rejected |
| 4 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | -0.1276 | 0.00 | ❌ rejected |
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 5  | 0.1045 | 0.24 | ❌ rejected |
| 2 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 5  | 0.0255 | 0.20 | ❌ rejected |

**Proposal policy**: task_score is 0.20 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`
- Frozen object start: [0.5109569349857164, 0.061582937101109625, 0.04]
- Frozen task target: [0.5109569349857164, -0.09841706289889038, 0.04]
- Goal object position: (0.5109569349857164, -0.09841706289889038, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, 0.061582937101109625, 0.04)
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
  frozen_object_start: [0.511, 0.0616, 0.04]
  frozen_task_target: [0.511, -0.0984, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5109569349857164, 0.061582937101109625, 0.04]}
  frozen_targets: {'channel_exit': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454

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
| `object` | offset from object initial position (0.5109569349857164, 0.061582937101109625, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5109569349857164, -0.09841706289889038, 0.04) | final destination targets |
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

## Current Skill (Q=0.025) — your mutation base

```yaml
skill: peg_channel
phases:
- id: insert_1
  type: insert
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
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
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: insert_2
  type: insert
  generator: impedance_motion
  control: admittance_control
  termination: force_exceeded

```

## Design Metrics

- **Composite score**: 0.025
- **task_score** (E): 0.197
- **fitness_score**: 0.405  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1565 |
| descend_to_peg | 0.00 | 1.00 | 0.0728 |
| push_through_channel | 0.00 | 1.00 | 0.1890 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.227, 0.148) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.540 | 2.179 |
| descend_to_peg | contact | 0.00 / step_budget | (0.495, 0.227, 0.148)→(0.496, 0.229, 0.076) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.540 | 0.582 |
| push_through_channel | push | 0.00 / guard_failure | (0.496, 0.229, 0.076)→(0.495, 0.042, 0.046) | (0.500, 0.080, 0.034)→(0.502, 0.043, 0.030) | 0.161→0.123 | 1.00 / 2.333 | 26.762 | 36.803 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.281
- alignment_error: None
- force_efficiency: 0.234
- terminal_score: 0.164
- phase_score: 0.670
- phase_breakdown.push_to_goal_score: 0.812
- phase_breakdown.reach_pre_push_score: 0.337

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.467
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.291
- **Median Q (composite search score)**: 0.084
- **K-run variance**: 0.0072
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.276


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `d6915c31707ac435a9367b840736087e39a7a48adfeb36a4f94b6b3ae57cce94`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `19172182883d287409b73cab43749e937e65f1ca1d4501d52b4a913a881aad36`; realized-scene SHA-256: `cd60c08f71f9d10bc11dd62c79067fee574cade1f8d1192fc945700528a8d454`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51096,0.06158,0.04]},{"name":"goal","value":[0.51096,-0.09842,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.51096,-0.09842,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.32143,"average_solve_count":112.0,"average_success_count":112.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.speed":0.1356,"descend_to_peg.descend_speed":0.0908,"descend_to_peg.force_threshold":6.8985,"push_through_channel.force_limit_threshold":29.3083,"push_through_channel.pose_tolerance":0.02013,"push_through_channel.push_distance":0.15124,"push_through_channel.push_speed":0.03085},"optimized_scores":{"best_composite_score":-0.09458,"best_fitness_score":0.28542,"best_task_score":0.13631},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50197,0.06461,0.05404],"force_p95":29.16908,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.34317,"mean_force":16.06154,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49862,0.07595,0.05308]},{"body_a":"peg","body_b":"channel_base_body","contact_count":352.0,"contact_point_centroid":[0.50399,0.05848,0.00946],"force_p95":0.55007,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.35419,"mean_force":0.9978,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49841,0.13859,0.06257]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52501,0.0241,0.05808],"force_p95":16.74866,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.96549,"mean_force":15.04957,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49873,0.06566,0.05162]},{"body_a":"peg","body_b":"channel_base_body","contact_count":429.0,"contact_point_centroid":[0.50353,0.06158,0.00933],"force_p95":0.58918,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.5654,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50296,0.20431,0.22092]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49988,0.19972,0.29836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":333.0,"contact_point_centroid":[0.50386,0.06163,0.00938],"force_p95":0.5507,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55481,"mean_force":0.54675,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.50289,0.20915,0.11222]}],"total_contact_groups":6},"final_pose_error":0.15516,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50558,0.03936,0.04035],"final_tcp_position":[0.49876,0.06439,0.05148],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":32.34317,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":452.0,"n_steps_budget":750.0,"object_pos_end":[0.50376,0.0616,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14179,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.53826,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":448.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_pre_push","tcp_end":[0.50715,0.20934,0.14889],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":333.0,"n_steps_budget":600.0,"object_pos_end":[0.50376,0.06156,0.03378],"object_pos_start":[0.50376,0.0616,0.03378],"object_to_goal_dist_end":0.14175,"object_to_goal_dist_start":0.14179,"object_z_max":0.03378,"peak_contact_force":0.54561,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":333.0,"raw_peak_contact_force":0.55481,"subtask_id":"reach_pre_push","tcp_end":[0.50061,0.20988,0.0771],"tcp_start":[0.50715,0.20934,0.14889],"tcp_to_object_dist_end":0.15455,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":355.0,"n_steps_budget":1000.0,"object_pos_end":[0.50558,0.03936,0.04035],"object_pos_start":[0.50376,0.06156,0.03378],"object_to_goal_dist_end":0.11949,"object_to_goal_dist_start":0.14175,"object_z_max":0.0408,"peak_contact_force":2.22042,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":367.0,"raw_peak_contact_force":32.34317,"subtask_id":"push_to_goal","tcp_end":[0.49876,0.06439,0.05148],"tcp_start":[0.50061,0.20988,0.0771],"tcp_to_object_dist_end":0.02823,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,0.11604,0.04]},{"name":"goal","value":[0.50095,-0.04396,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.50095,-0.04396,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.28378,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.speed":0.09625,"descend_to_peg.descend_speed":0.06864,"descend_to_peg.force_threshold":4.12341,"push_through_channel.force_limit_threshold":38.94185,"push_through_channel.pose_tolerance":0.03558,"push_through_channel.push_distance":0.19001,"push_through_channel.push_speed":0.0065},"optimized_scores":{"best_composite_score":0.08351,"best_fitness_score":0.46351,"best_task_score":0.29128},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":542.0,"contact_point_centroid":[0.50202,0.10032,0.00923],"force_p95":27.45529,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":39.77301,"mean_force":4.25153,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49553,0.15132,0.05766]},{"body_a":"attachment","body_b":"peg","contact_count":105.0,"contact_point_centroid":[0.5012,0.09776,0.05196],"force_p95":30.78676,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.16426,"mean_force":19.13927,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49617,0.10724,0.05245]},{"body_a":"peg","body_b":"channel_base_body","contact_count":519.0,"contact_point_centroid":[0.50093,0.11605,0.00939],"force_p95":0.61766,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55817,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49829,0.22949,0.22066]},{"body_a":"peg","body_b":"channel_base_body","contact_count":371.0,"contact_point_centroid":[0.50093,0.11586,0.00944],"force_p95":0.60056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64032,"mean_force":0.54066,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.4965,0.26094,0.10982]}],"total_contact_groups":4},"final_pose_error":0.11349,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50423,0.06943,0.0262],"final_tcp_position":[0.49651,0.03899,0.04366],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":39.77301,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":535.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11612,0.03384],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19621,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.53178,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":519.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_push","tcp_end":[0.49803,0.25944,0.14666],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.18242,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":371.0,"n_steps_budget":690.0,"object_pos_end":[0.50091,0.11602,0.03382],"object_pos_start":[0.50096,0.11612,0.03384],"object_to_goal_dist_end":0.19612,"object_to_goal_dist_start":0.19621,"object_z_max":0.03404,"peak_contact_force":0.53052,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":371.0,"raw_peak_contact_force":0.64032,"subtask_id":"reach_pre_push","tcp_end":[0.49718,0.26359,0.07593],"tcp_start":[0.49803,0.25944,0.14666],"tcp_to_object_dist_end":0.15351,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":544.0,"n_steps_budget":1000.0,"object_pos_end":[0.50423,0.06943,0.0262],"object_pos_start":[0.50091,0.11602,0.03382],"object_to_goal_dist_end":0.15013,"object_to_goal_dist_start":0.19612,"object_z_max":0.04022,"peak_contact_force":39.77301,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":647.0,"raw_peak_contact_force":39.77301,"subtask_id":"push_to_goal","tcp_end":[0.49651,0.03899,0.04366],"tcp_start":[0.49718,0.26359,0.07593],"tcp_to_object_dist_end":0.03593,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,0.06388,0.04]},{"name":"goal","value":[0.48093,-0.09612,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.48093,-0.09612,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.30496,"average_solve_count":141.0,"average_success_count":141.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.speed":0.11539,"descend_to_peg.descend_speed":0.0762,"descend_to_peg.force_threshold":7.02557,"push_through_channel.force_limit_threshold":26.06636,"push_through_channel.pose_tolerance":0.03236,"push_through_channel.push_distance":0.13661,"push_through_channel.push_speed":0.03145},"optimized_scores":{"best_composite_score":0.08748,"best_fitness_score":0.46748,"best_task_score":0.16403},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":459.0,"contact_point_centroid":[0.49642,0.05406,0.00937],"force_p95":18.28472,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.29292,"mean_force":2.49491,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.489,0.11823,0.0571]},{"body_a":"attachment","body_b":"peg","contact_count":64.0,"contact_point_centroid":[0.49724,0.04768,0.04788],"force_p95":20.62547,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.0968,"mean_force":13.87776,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49,0.05677,0.04835]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47489,0.04062,0.02419],"force_p95":6.24938,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.46218,"mean_force":2.34288,"phase_index":2.0,"phase_name":"push_through_channel","phase_type":"push","tcp_position_centroid":[0.49039,0.02404,0.04357]},{"body_a":"peg","body_b":"channel_base_body","contact_count":425.0,"contact_point_centroid":[0.49546,0.06402,0.00936],"force_p95":0.60251,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56552,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48899,0.20541,0.22055]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49933,0.19975,0.29692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":461.0,"contact_point_centroid":[0.49502,0.06367,0.0094],"force_p95":0.55032,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.5455,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.48403,0.21131,0.10947]}],"total_contact_groups":6},"final_pose_error":0.09578,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49666,0.01899,0.02428],"final_tcp_position":[0.49041,0.02226,0.0433],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":38.29292,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":452.0,"n_steps_budget":900.0,"object_pos_end":[0.49493,0.06376,0.03393],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14398,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.55076,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":453.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_push","tcp_end":[0.47991,0.21141,0.14934],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.188,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":461.0,"n_steps_budget":660.0,"object_pos_end":[0.49527,0.06367,0.034],"object_pos_start":[0.49493,0.06376,0.03393],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.14398,"object_z_max":0.034,"peak_contact_force":0.54437,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":461.0,"raw_peak_contact_force":0.5516,"subtask_id":"reach_pre_push","tcp_end":[0.49026,0.2121,0.07447],"tcp_start":[0.47991,0.21141,0.14934],"tcp_to_object_dist_end":0.15393,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.49666,0.01899,0.02428],"object_pos_start":[0.49527,0.06367,0.034],"object_to_goal_dist_end":0.10028,"object_to_goal_dist_start":0.14387,"object_z_max":0.0408,"peak_contact_force":38.29292,"phase_name":"push_through_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":531.0,"raw_peak_contact_force":38.29292,"subtask_id":"push_to_goal","tcp_end":[0.49041,0.02226,0.0433],"tcp_start":[0.49026,0.2121,0.07447],"tcp_to_object_dist_end":0.02029,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```