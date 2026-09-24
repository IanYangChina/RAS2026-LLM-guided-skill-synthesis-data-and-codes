## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.0781 | 0.01 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.0325 | 0.01 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.2743 | 0.00 | ❌ rejected |
| 3 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1533 | 0.67 | ❌ rejected |
| 2 | approach → align → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.1320 | 0.13 | ❌ rejected |

**Proposal policy**: task_score is 0.01 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5109569349857164, -0.09841706289889038, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5109569349857164, -0.09841706289889038, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5109569349857164, 0.061582937101109625, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5109569349857164, 0.061582937101109625, 0.04]
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
  frozen_object_starts: {'peg': [0.5109569349857164, -0.09841706289889038, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
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
| `object` | offset from object initial position (0.5109569349857164, -0.09841706289889038, 0.04) | approach/contact targets near object start |
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

## Current Skill (Q=-0.078) — your mutation base

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

- **Composite score**: -0.078
- **task_score** (E): 0.011
- **fitness_score**: 0.132  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1446 |
| descend | 1.00 | 1.00 | 0.1413 |
| push | 0.00 | 1.00 | 0.0001 |
| retract | 1.00 | 1.00 | 0.2426 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.496, 0.097, 0.201) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.540 | 2.179 |
| descend | descend | 1.00 / force_exceeded | (0.496, 0.097, 0.201)→(0.496, 0.081, 0.061) | (0.500, 0.080, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 17.794 | 17.794 |
| push | push | 0.00 / guard_failure | (0.495, 0.077, 0.059)→(0.495, 0.076, 0.059) | (0.500, 0.081, 0.034)→(0.499, 0.078, 0.034) | 0.161→0.158 | 1.00 / 2.000 | 46.999 | 46.999 |
| retract | retract | 1.00 / step_budget | (0.495, 0.076, 0.059)→(0.498, 0.021, 0.295) | (0.499, 0.078, 0.034)→(0.499, 0.078, 0.034) | 0.158→0.159 | 1.00 / 1.000 | 0.553 | 46.105 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.019
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.013
- phase_score: 0.218
- phase_breakdown.push_channel_score: 0.024
- phase_breakdown.reach_above_score: 0.672

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.136
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.014
- **Median Q (composite search score)**: -0.078
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.293


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
{"anchors":[{"name":"object","value":[0.51096,-0.09842,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,0.06158,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51096,-0.09842,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.55333,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.09411,"descend.descend_force_threshold":7.28844,"descend.descend_speed":0.05997,"push.duration_max_time":4.69204,"push.push_distance":0.0836,"push.push_speed":0.04766,"retract.retract_arc_height":0.14876,"retract.retract_speed":0.09163},"optimized_scores":{"best_composite_score":-0.08213,"best_fitness_score":0.12787,"best_task_score":0.00608},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":38.0,"contact_point_centroid":[0.50448,0.0481,0.00942],"force_p95":39.56554,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.1039,"mean_force":33.76666,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49987,0.06115,0.05964]},{"body_a":"attachment","body_b":"peg","contact_count":38.0,"contact_point_centroid":[0.51173,0.06097,0.0584],"force_p95":39.09781,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.61743,"mean_force":33.30345,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49987,0.06115,0.05964]},{"body_a":"peg","body_b":"channel_base_body","contact_count":903.0,"contact_point_centroid":[0.50265,0.06173,0.00943],"force_p95":0.91639,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":43.93261,"mean_force":1.12802,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49747,0.09982,0.18282]},{"body_a":"attachment","body_b":"peg","contact_count":44.0,"contact_point_centroid":[0.50859,0.05973,0.06085],"force_p95":24.55289,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.51485,"mean_force":12.05939,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49884,0.06549,0.06193]},{"body_a":"peg","body_b":"channel_base_body","contact_count":751.0,"contact_point_centroid":[0.50381,0.06157,0.00938],"force_p95":0.59861,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.51806,"mean_force":0.5704,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50258,0.07033,0.12786]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51222,0.06201,0.05878],"force_p95":18.00196,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.00196,"mean_force":18.00196,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50036,0.06245,0.06053]},{"body_a":"peg","body_b":"channel_base_body","contact_count":301.0,"contact_point_centroid":[0.50345,0.06161,0.00932],"force_p95":0.65113,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.57314,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50312,0.13634,0.24542]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49977,0.19803,0.29839]}],"total_contact_groups":8},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50282,0.06044,0.03382],"final_tcp_position":[0.49837,0.01869,0.29335],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":49.1039,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":324.0,"n_steps_budget":1000.0,"object_pos_end":[0.5038,0.06157,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.60144,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":320.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_above","tcp_end":[0.5072,0.07862,0.19887],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16602,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":751.0,"n_steps_budget":1000.0,"object_pos_end":[0.50375,0.06154,0.03379],"object_pos_start":[0.5038,0.06157,0.03376],"object_to_goal_dist_end":0.14173,"object_to_goal_dist_start":0.14176,"object_z_max":0.03382,"peak_contact_force":18.51806,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":752.0,"raw_peak_contact_force":18.51806,"tcp_end":[0.50036,0.06243,0.06038],"tcp_start":[0.5072,0.07862,0.19887],"tcp_to_object_dist_end":0.02682,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":38.0,"n_steps_budget":1000.0,"object_pos_end":[0.50321,0.0603,0.03388],"object_pos_start":[0.50375,0.06154,0.03379],"object_to_goal_dist_end":0.14047,"object_to_goal_dist_start":0.14173,"object_z_max":0.03401,"peak_contact_force":49.1039,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":76.0,"raw_peak_contact_force":49.1039,"subtask_id":"push_channel","tcp_end":[0.49962,0.05973,0.05926],"tcp_start":[0.49962,0.05979,0.05927],"tcp_to_object_dist_end":0.02564,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.50282,0.06044,0.03382],"object_pos_start":[0.50322,0.06025,0.03387],"object_to_goal_dist_end":0.14061,"object_to_goal_dist_start":0.14042,"object_z_max":0.03844,"peak_contact_force":0.54744,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":947.0,"raw_peak_contact_force":43.93261,"tcp_end":[0.49837,0.01869,0.29335],"tcp_start":[0.49962,0.05973,0.05926],"tcp_to_object_dist_end":0.26291,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `f24211f27d4adabdef509c8ed61621317fdbcaa86fc9ac888f85a717335bb714`; realized-scene SHA-256: `9fd07833843a6ee28e14c5e2ce05f86547005983f45e63c41c77b8dac2024c0a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50095,-0.04396,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,0.11604,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50095,-0.04396,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56522,"average_solve_count":184.0,"average_success_count":184.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.10631,"descend.descend_force_threshold":10.50989,"descend.descend_speed":0.04879,"push.duration_max_time":5.59629,"push.push_distance":0.13367,"push.push_speed":0.04461,"retract.retract_arc_height":0.11286,"retract.retract_speed":0.06042},"optimized_scores":{"best_composite_score":-0.07832,"best_fitness_score":0.13168,"best_task_score":0.01391},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.4998,0.11422,0.00942],"force_p95":0.62948,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.78541,"mean_force":0.70395,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49607,0.132,0.19355]},{"body_a":"attachment","body_b":"peg","contact_count":23.0,"contact_point_centroid":[0.50718,0.1114,0.05896],"force_p95":32.85449,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.39929,"mean_force":7.06028,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49569,0.1137,0.06018]},{"body_a":"peg","body_b":"channel_base_body","contact_count":57.0,"contact_point_centroid":[0.50327,0.10093,0.00947],"force_p95":39.77913,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":41.49523,"mean_force":35.1504,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49653,0.11421,0.0596]},{"body_a":"attachment","body_b":"peg","contact_count":57.0,"contact_point_centroid":[0.50839,0.11425,0.05844],"force_p95":39.31891,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.01394,"mean_force":34.68449,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.49653,0.11421,0.0596]},{"body_a":"peg","body_b":"channel_base_body","contact_count":793.0,"contact_point_centroid":[0.50095,0.11604,0.00941],"force_p95":0.61063,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":18.88015,"mean_force":0.56645,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49674,0.12265,0.1301]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50901,0.11603,0.05896],"force_p95":18.40883,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.40883,"mean_force":18.40883,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.49714,0.11628,0.06068]},{"body_a":"peg","body_b":"channel_base_body","contact_count":217.0,"contact_point_centroid":[0.50075,0.11589,0.00932],"force_p95":0.84214,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.58098,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49889,0.16363,0.24907]}],"total_contact_groups":7},"final_pose_error":0.02677,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50017,0.11381,0.03381],"final_tcp_position":[0.49847,0.02668,0.29833],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":47.78541,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":233.0,"n_steps_budget":840.0,"object_pos_end":[0.50097,0.11606,0.03386],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19616,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.47373,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":217.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_above","tcp_end":[0.49871,0.12971,0.20377],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.17048,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":793.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.116,0.03398],"object_pos_start":[0.50097,0.11606,0.03386],"object_to_goal_dist_end":0.1961,"object_to_goal_dist_start":0.19616,"object_z_max":0.034,"peak_contact_force":18.88015,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":794.0,"raw_peak_contact_force":18.88015,"tcp_end":[0.49715,0.11627,0.06051],"tcp_start":[0.49871,0.12971,0.20377],"tcp_to_object_dist_end":0.0268,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":57.0,"n_steps_budget":1000.0,"object_pos_end":[0.50029,0.11398,0.03391],"object_pos_start":[0.50095,0.116,0.03398],"object_to_goal_dist_end":0.19407,"object_to_goal_dist_start":0.1961,"object_z_max":0.03412,"peak_contact_force":41.49523,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":114.0,"raw_peak_contact_force":41.49523,"subtask_id":"push_channel","tcp_end":[0.49627,0.11208,0.05923],"tcp_start":[0.49627,0.11212,0.05924],"tcp_to_object_dist_end":0.0257,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50017,0.11381,0.03381],"object_pos_start":[0.5003,0.11395,0.0339],"object_to_goal_dist_end":0.19391,"object_to_goal_dist_start":0.19405,"object_z_max":0.03491,"peak_contact_force":0.56333,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1023.0,"raw_peak_contact_force":47.78541,"tcp_end":[0.49847,0.02668,0.29833],"tcp_start":[0.49627,0.11208,0.05923],"tcp_to_object_dist_end":0.27851,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `d098a7862ff18c9bbe982af3446a89a0fa6bcfa8790d7d955f65b2375d67a881`; realized-scene SHA-256: `2a92d231da5879af7af8916eb4c7dff00148227e84220c4d9643d9841dc77ee7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.48093,-0.09612,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,0.06388,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.48093,-0.09612,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.60234,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.07159,"descend.descend_force_threshold":12.28779,"descend.descend_speed":0.04685,"push.duration_max_time":4.61285,"push.push_distance":0.07612,"push.push_speed":0.04738,"retract.retract_arc_height":0.16036,"retract.retract_speed":0.10391},"optimized_scores":{"best_composite_score":-0.074,"best_fitness_score":0.136,"best_task_score":0.01258},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":90.0,"contact_point_centroid":[0.49675,0.04803,0.00948],"force_p95":39.77678,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.39866,"mean_force":35.68276,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48979,0.06115,0.05963]},{"body_a":"attachment","body_b":"peg","contact_count":90.0,"contact_point_centroid":[0.50165,0.0612,0.05849],"force_p95":39.30425,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.91209,"mean_force":35.21605,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.48979,0.06115,0.05963]},{"body_a":"peg","body_b":"channel_base_body","contact_count":851.0,"contact_point_centroid":[0.49369,0.06201,0.00943],"force_p95":0.81012,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.59609,"mean_force":1.01941,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.49275,0.09364,0.18182]},{"body_a":"attachment","body_b":"peg","contact_count":40.0,"contact_point_centroid":[0.49889,0.05726,0.06082],"force_p95":21.64823,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.1952,"mean_force":10.19655,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48883,0.06257,0.06189]},{"body_a":"peg","body_b":"channel_base_body","contact_count":871.0,"contact_point_centroid":[0.4952,0.06394,0.0094],"force_p95":0.55061,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.98262,"mean_force":0.56319,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.48464,0.07262,0.12788]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50223,0.06357,0.05906],"force_p95":15.49977,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.49977,"mean_force":15.49977,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.4904,0.06459,0.06079]},{"body_a":"peg","body_b":"channel_base_body","contact_count":293.0,"contact_point_centroid":[0.49552,0.06387,0.00935],"force_p95":0.65171,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.5744,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.48949,0.13699,0.24529]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.49906,0.19675,0.29698]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47498,0.0601,0.05883],"force_p95":0.06152,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.06456,"mean_force":0.03703,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.48811,0.0974,0.09062]}],"total_contact_groups":9},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49378,0.0609,0.03384],"final_tcp_position":[0.49822,0.01795,0.29195],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":50.39866,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.49515,0.06371,0.03391],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14392,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54524,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":321.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_above","tcp_end":[0.48121,0.08121,0.19976],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.16735,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":871.0,"n_steps_budget":1000.0,"object_pos_end":[0.49488,0.06405,0.03401],"object_pos_start":[0.49515,0.06371,0.03391],"object_to_goal_dist_end":0.14426,"object_to_goal_dist_start":0.14392,"object_z_max":0.03402,"peak_contact_force":15.98262,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":872.0,"raw_peak_contact_force":15.98262,"tcp_end":[0.49043,0.06457,0.06065],"tcp_start":[0.48121,0.08121,0.19976],"tcp_to_object_dist_end":0.02701,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":90.0,"n_steps_budget":1000.0,"object_pos_end":[0.49403,0.06055,0.03389],"object_pos_start":[0.49488,0.06405,0.03401],"object_to_goal_dist_end":0.14081,"object_to_goal_dist_start":0.14426,"object_z_max":0.03426,"peak_contact_force":50.39866,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":180.0,"raw_peak_contact_force":50.39866,"subtask_id":"push_channel","tcp_end":[0.48951,0.05768,0.05922],"tcp_start":[0.48951,0.05774,0.05923],"tcp_to_object_dist_end":0.02589,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":852.0,"n_steps_budget":1000.0,"object_pos_end":[0.49378,0.0609,0.03384],"object_pos_start":[0.49404,0.06052,0.03389],"object_to_goal_dist_end":0.14117,"object_to_goal_dist_start":0.14078,"object_z_max":0.03813,"peak_contact_force":0.54764,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":895.0,"raw_peak_contact_force":46.59609,"tcp_end":[0.49822,0.01795,0.29195],"tcp_start":[0.48951,0.05768,0.05922],"tcp_to_object_dist_end":0.2617,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```