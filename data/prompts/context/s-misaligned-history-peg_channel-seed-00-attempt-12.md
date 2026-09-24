## Search State

- **Seed**: 0
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → contact → push → lift → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 8  | -0.2392 | 0.00 | ❌ rejected |
| 11 | approach → contact → push → lift → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.0280 | 0.00 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7  | 0.1778 | 0.72 | ❌ rejected |
| 9 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | 0.2024 | 0.72 | ❌ rejected |
| 8 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | -0.2830 | 0.15 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.283) — your mutation base

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

- **Composite score**: -0.283
- **task_score** (E): 0.154
- **fitness_score**: 0.207  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.490

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1712 |
| descend_to_peg | 0.00 | 1.00 | 0.0815 |
| push_through | 0.67 | 1.00 | 0.1114 |
| lift_off | 1.00 | 1.00 | 0.0804 |
| retract_clear | 1.00 | 1.00 | 0.0917 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.119, 0.154) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.573 | 2.179 |
| descend_to_peg | contact | 0.00 / step_budget | (0.495, 0.119, 0.154)→(0.496, 0.101, 0.076) | (0.500, 0.080, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.540 | 0.590 |
| push_through | push | 0.67 / step_budget | (0.495, 0.086, 0.070)→(0.496, -0.022, 0.042) | (0.500, 0.081, 0.034)→(0.499, 0.051, 0.028) | 0.161→0.132 | 1.00 / 1.333 | 10.756 | 31.767 |
| lift_off | lift | 1.00 / step_budget | (0.496, -0.022, 0.042)→(0.493, -0.022, 0.123) | (0.499, 0.051, 0.028)→(0.499, 0.052, 0.028) | 0.132→0.133 | 1.00 / 1.000 | 0.621 | 17.630 |
| retract_clear | retract | 1.00 / step_budget | (0.493, -0.022, 0.123)→(0.498, -0.050, 0.205) | (0.499, 0.052, 0.028)→(0.499, 0.051, 0.028) | 0.133→0.132 | 1.00 / 1.000 | 0.546 | 0.651 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.272
- alignment_error: None
- force_efficiency: 0.422
- terminal_score: 0.272
- phase_score: 0.275
- phase_breakdown.push_channel_score: 0.218
- phase_breakdown.reach_peg_score: 0.406

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.274
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.272
- **Median Q (composite search score)**: -0.223
- **K-run variance**: 0.0081
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.239


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.71186,"average_solve_count":177.0,"average_success_count":177.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.07532,"approach_peg.arc_height":0.14025,"descend_to_peg.contact_force_threshold":10.95141,"lift_off.lift_speed":0.07773,"push_through.push_distance":0.13074,"push_through.push_speed":0.033,"retract_clear.retract_arc_height":0.14527,"retract_clear.retract_speed":0.09667},"optimized_scores":{"best_composite_score":-0.40992,"best_fitness_score":0.08008,"best_task_score":0.00549},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":245.0,"contact_point_centroid":[0.50249,0.06121,0.0095],"force_p95":0.63241,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.35919,"mean_force":0.80612,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.49615,0.03367,0.09842]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50781,0.04045,0.05859],"force_p95":32.40952,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.125,"mean_force":6.09387,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.4982,0.03347,0.05974]},{"body_a":"attachment","body_b":"peg","contact_count":12.0,"contact_point_centroid":[0.50846,0.04283,0.05856],"force_p95":36.03982,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.86171,"mean_force":27.53497,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.4985,0.03635,0.0599]},{"body_a":"peg","body_b":"channel_base_body","contact_count":131.0,"contact_point_centroid":[0.50398,0.06009,0.00938],"force_p95":26.94919,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":37.73423,"mean_force":3.06974,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49839,0.06041,0.06713]},{"body_a":"peg","body_b":"channel_base_body","contact_count":411.0,"contact_point_centroid":[0.50361,0.06155,0.00933],"force_p95":0.60738,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56623,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50723,0.11939,0.24736]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49967,0.1975,0.29972]},{"body_a":"peg","body_b":"channel_base_body","contact_count":372.0,"contact_point_centroid":[0.50377,0.06167,0.00938],"force_p95":0.55564,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5594,"mean_force":0.54659,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.50409,0.08702,0.11661]},{"body_a":"peg","body_b":"channel_base_body","contact_count":124.0,"contact_point_centroid":[0.50594,0.06208,0.00948],"force_p95":0.54273,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54431,"mean_force":0.53945,"phase_index":4.0,"phase_name":"retract_clear","phase_type":"retract","tcp_position_centroid":[0.4962,0.01014,0.1841]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.52505,0.06255,0.05892],"force_p95":0.18168,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19052,"mean_force":0.11074,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.49648,0.03357,0.07435]}],"total_contact_groups":9},"final_pose_error":0.04984,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50389,0.06061,0.03475],"final_tcp_position":[0.49859,-0.03331,0.22261],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":42.35919,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":434.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.06157,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54871,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":430.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_peg","tcp_end":[0.50958,0.09197,0.15746],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12749,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":372.0,"n_steps_budget":600.0,"object_pos_end":[0.50376,0.06155,0.03379],"object_pos_start":[0.50373,0.06157,0.03378],"object_to_goal_dist_end":0.14174,"object_to_goal_dist_start":0.14176,"object_z_max":0.03379,"peak_contact_force":0.54364,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":372.0,"raw_peak_contact_force":0.5594,"subtask_id":"reach_peg","tcp_end":[0.50076,0.08206,0.07766],"tcp_start":[0.50958,0.09197,0.15746],"tcp_to_object_dist_end":0.04852,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":131.0,"n_steps_budget":1000.0,"object_pos_end":[0.50393,0.06021,0.03483],"object_pos_start":[0.50376,0.06155,0.03379],"object_to_goal_dist_end":0.14036,"object_to_goal_dist_start":0.14174,"object_z_max":0.03493,"peak_contact_force":31.10319,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":143.0,"raw_peak_contact_force":37.86171,"subtask_id":"push_channel","tcp_end":[0.49867,0.034,0.05942],"tcp_start":[0.49868,0.03423,0.05948],"tcp_to_object_dist_end":0.03632,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":245.0,"n_steps_budget":810.0,"object_pos_end":[0.50365,0.06289,0.03477],"object_pos_start":[0.5039,0.06001,0.035],"object_to_goal_dist_end":0.14303,"object_to_goal_dist_start":0.14016,"object_z_max":0.03558,"peak_contact_force":0.53674,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":260.0,"raw_peak_contact_force":42.35919,"tcp_end":[0.49586,0.03375,0.13962],"tcp_start":[0.49867,0.034,0.05942],"tcp_to_object_dist_end":0.1091,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":124.0,"n_steps_budget":990.0,"object_pos_end":[0.50389,0.06061,0.03475],"object_pos_start":[0.50365,0.06289,0.03477],"object_to_goal_dist_end":0.14076,"object_to_goal_dist_start":0.14303,"object_z_max":0.03477,"peak_contact_force":0.53805,"phase_name":"retract_clear","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":124.0,"raw_peak_contact_force":0.54431,"tcp_end":[0.49859,-0.03331,0.22261],"tcp_start":[0.49586,0.03375,0.13962],"tcp_to_object_dist_end":0.2101,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.46639,"average_solve_count":238.0,"average_success_count":238.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.08833,"approach_peg.arc_height":0.18476,"descend_to_peg.contact_force_threshold":20.51269,"lift_off.lift_speed":0.10093,"push_through.push_distance":0.1611,"push_through.push_speed":0.03244,"retract_clear.retract_arc_height":0.18162,"retract_clear.retract_speed":0.07132},"optimized_scores":{"best_composite_score":-0.21626,"best_fitness_score":0.27374,"best_task_score":0.27224},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":407.0,"contact_point_centroid":[0.5006,0.09521,0.00908],"force_p95":22.51315,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.89683,"mean_force":2.77389,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49575,0.05838,0.05329]},{"body_a":"attachment","body_b":"peg","contact_count":61.0,"contact_point_centroid":[0.50139,0.08829,0.05749],"force_p95":27.89061,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.42184,"mean_force":14.74309,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49565,0.07806,0.05808]},{"body_a":"peg","body_b":"channel_base_body","contact_count":301.0,"contact_point_centroid":[0.50103,0.11601,0.00933],"force_p95":0.68297,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.57253,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49867,0.20385,0.21856]},{"body_a":"peg","body_b":"channel_base_body","contact_count":238.0,"contact_point_centroid":[0.49901,0.0723,0.00801],"force_p95":0.72552,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72575,"mean_force":0.60587,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.49455,-0.02555,0.0729]},{"body_a":"peg","body_b":"channel_base_body","contact_count":107.0,"contact_point_centroid":[0.49831,0.07322,0.00801],"force_p95":0.72551,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72551,"mean_force":0.60468,"phase_index":4.0,"phase_name":"retract_clear","phase_type":"retract","tcp_position_centroid":[0.4957,-0.03145,0.1546]},{"body_a":"peg","body_b":"channel_base_body","contact_count":408.0,"contact_point_centroid":[0.50094,0.11597,0.00943],"force_p95":0.60259,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65712,"mean_force":0.5419,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.49649,0.15548,0.11097]}],"total_contact_groups":6},"final_pose_error":0.04927,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4981,0.07248,0.02409],"final_tcp_position":[0.49838,-0.0507,0.20042],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":28.89683,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.50088,0.11612,0.0338],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19622,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.62173,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":301.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_peg","tcp_end":[0.49818,0.17304,0.14933],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":408.0,"n_steps_budget":600.0,"object_pos_end":[0.50096,0.11608,0.03389],"object_pos_start":[0.50088,0.11612,0.0338],"object_to_goal_dist_end":0.19617,"object_to_goal_dist_start":0.19622,"object_z_max":0.03403,"peak_contact_force":0.52738,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":408.0,"raw_peak_contact_force":0.65712,"subtask_id":"reach_peg","tcp_end":[0.49703,0.13852,0.07579],"tcp_start":[0.49818,0.17304,0.14933],"tcp_to_object_dist_end":0.0477,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":418.0,"n_steps_budget":1000.0,"object_pos_end":[0.49953,0.07252,0.0241],"object_pos_start":[0.50096,0.11608,0.03389],"object_to_goal_dist_end":0.15335,"object_to_goal_dist_start":0.19617,"object_z_max":0.04077,"peak_contact_force":0.56223,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":468.0,"raw_peak_contact_force":28.89683,"subtask_id":"push_channel","tcp_end":[0.49718,-0.02548,0.03389],"tcp_start":[0.49703,0.13852,0.07579],"tcp_to_object_dist_end":0.09851,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":238.0,"n_steps_budget":630.0,"object_pos_end":[0.49851,0.07257,0.02409],"object_pos_start":[0.49953,0.07252,0.0241],"object_to_goal_dist_end":0.15341,"object_to_goal_dist_start":0.15335,"object_z_max":0.0241,"peak_contact_force":0.72551,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":238.0,"raw_peak_contact_force":0.72575,"tcp_end":[0.49438,-0.02535,0.11422],"tcp_start":[0.49718,-0.02548,0.03389],"tcp_to_object_dist_end":0.13315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":107.0,"n_steps_budget":1000.0,"object_pos_end":[0.4981,0.07248,0.02409],"object_pos_start":[0.49851,0.07257,0.02409],"object_to_goal_dist_end":0.15332,"object_to_goal_dist_start":0.15341,"object_z_max":0.0241,"peak_contact_force":0.49887,"phase_name":"retract_clear","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":107.0,"raw_peak_contact_force":0.72551,"tcp_end":[0.49838,-0.0507,0.20042],"tcp_start":[0.49438,-0.02535,0.11422],"tcp_to_object_dist_end":0.21509,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55708,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.11975,"approach_peg.arc_height":0.12396,"descend_to_peg.contact_force_threshold":9.94515,"lift_off.lift_speed":0.10107,"push_through.push_distance":0.15873,"push_through.push_speed":0.02379,"retract_clear.retract_arc_height":0.16956,"retract_clear.retract_speed":0.10891},"optimized_scores":{"best_composite_score":-0.22289,"best_fitness_score":0.26711,"best_task_score":0.185},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":406.0,"contact_point_centroid":[0.49516,0.04255,0.00904],"force_p95":23.99572,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.54305,"mean_force":2.99249,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48944,0.00601,0.0531]},{"body_a":"attachment","body_b":"peg","contact_count":67.0,"contact_point_centroid":[0.49515,0.03649,0.05753],"force_p95":27.41617,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.05316,"mean_force":14.71354,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48907,0.02666,0.05817]},{"body_a":"peg","body_b":"channel_base_body","contact_count":239.0,"contact_point_centroid":[0.49321,0.02029,0.00823],"force_p95":8.55987,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.8043,"mean_force":1.29735,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.48879,-0.07532,0.07296]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":40.0,"contact_point_centroid":[0.47498,0.0122,0.02476],"force_p95":8.97313,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.35032,"mean_force":4.47263,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.48865,-0.07528,0.06234]},{"body_a":"peg","body_b":"channel_base_body","contact_count":405.0,"contact_point_centroid":[0.49548,0.06402,0.00936],"force_p95":0.60822,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.5665,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48176,0.1149,0.24787]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49832,0.19515,0.29991]},{"body_a":"peg","body_b":"channel_base_body","contact_count":93.0,"contact_point_centroid":[0.49388,0.01938,0.00804],"force_p95":0.6834,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.68378,"mean_force":0.60587,"phase_index":4.0,"phase_name":"retract_clear","phase_type":"retract","tcp_position_centroid":[0.49109,-0.06688,0.14908]},{"body_a":"peg","body_b":"channel_base_body","contact_count":509.0,"contact_point_centroid":[0.49516,0.06363,0.0094],"force_p95":0.55034,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55239,"mean_force":0.54551,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.48224,0.08816,0.11318]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.475,-0.00432,0.02415],"force_p95":0.38462,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.38462,"mean_force":0.38462,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49125,-0.06836,0.03556]}],"total_contact_groups":9},"final_pose_error":0.04987,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49397,0.01963,0.02413],"final_tcp_position":[0.49559,-0.06734,0.19197],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":28.54305,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":432.0,"n_steps_budget":990.0,"object_pos_end":[0.49493,0.06377,0.03393],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14398,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.5483,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":433.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.47667,0.09294,0.15587],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":509.0,"n_steps_budget":600.0,"object_pos_end":[0.49535,0.06395,0.034],"object_pos_start":[0.49493,0.06377,0.03393],"object_to_goal_dist_end":0.14415,"object_to_goal_dist_start":0.14398,"object_z_max":0.034,"peak_contact_force":0.54921,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":509.0,"raw_peak_contact_force":0.55239,"subtask_id":"reach_peg","tcp_end":[0.49004,0.0838,0.07513],"tcp_start":[0.47667,0.09294,0.15587],"tcp_to_object_dist_end":0.04597,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.49319,0.02061,0.0242],"object_pos_start":[0.49535,0.06395,0.034],"object_to_goal_dist_end":0.10207,"object_to_goal_dist_start":0.14415,"object_z_max":0.04081,"peak_contact_force":0.6012,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":474.0,"raw_peak_contact_force":28.54305,"subtask_id":"push_channel","tcp_end":[0.49145,-0.07552,0.03387],"tcp_start":[0.49004,0.0838,0.07513],"tcp_to_object_dist_end":0.09663,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":239.0,"n_steps_budget":630.0,"object_pos_end":[0.49365,0.01966,0.02413],"object_pos_start":[0.49319,0.02061,0.0242],"object_to_goal_dist_end":0.10112,"object_to_goal_dist_start":0.10207,"object_z_max":0.02553,"peak_contact_force":0.60188,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":279.0,"raw_peak_contact_force":9.8043,"tcp_end":[0.48862,-0.0751,0.11432],"tcp_start":[0.49145,-0.07552,0.03387],"tcp_to_object_dist_end":0.13092,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":93.0,"n_steps_budget":750.0,"object_pos_end":[0.49397,0.01963,0.02413],"object_pos_start":[0.49365,0.01966,0.02413],"object_to_goal_dist_end":0.10106,"object_to_goal_dist_start":0.10112,"object_z_max":0.02413,"peak_contact_force":0.60162,"phase_name":"retract_clear","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":93.0,"raw_peak_contact_force":0.68378,"tcp_end":[0.49559,-0.06734,0.19197],"tcp_start":[0.48862,-0.0751,0.11432],"tcp_to_object_dist_end":0.18904,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```