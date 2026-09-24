## Search State

- **Seed**: 0
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1551 | 0.00 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.4551 | 0.69 | ❌ rejected |
| 6 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1593 | 0.72 | ❌ rejected |
| 5 | approach → approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.4015 | 0.36 | ❌ rejected |
| 4 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2691 | 0.74 | ❌ rejected |

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

## Current Skill (Q=0.155) — your mutation base

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

- **Composite score**: 0.155
- **task_score** (E): 0.001
- **fitness_score**: 0.232  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_peg | 1.00 | 1.00 | 0.1820 |
| descend_to_contact | 1.00 | 1.00 | 0.0913 |
| push_along_channel | 0.00 | 1.00 | 0.0009 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.094, 0.154) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 29.439 | 29.439 |
| descend_to_contact | descend | 1.00 / force_exceeded | (0.495, 0.094, 0.154)→(0.495, 0.082, 0.064) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 39.616 | 39.616 |
| push_along_channel | push | 0.00 / guard_failure | (0.495, 0.082, 0.064)→(0.495, 0.081, 0.063) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.537 | 2.179 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.001
- alignment_error: None
- force_efficiency: 0.223
- terminal_score: 0.001
- phase_score: 0.390
- phase_breakdown.reach_approach_score: 0.677
- phase_breakdown.reach_contact_score: 0.621
- phase_breakdown.push_progress_score: 0.002

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.234
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: 0.155
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.394


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39024,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.approach_speed":0.07269,"descend_to_contact.descend_force_threshold":17.74382,"descend_to_contact.descend_speed":0.0334,"push_along_channel.push_distance":0.14876,"push_along_channel.push_speed":0.01018,"retract_from_channel.retract_height":0.17822,"retract_from_channel.retract_speed":0.16245},"optimized_scores":{"best_composite_score":0.153,"best_fitness_score":0.22966,"best_task_score":0.00023},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.49372,0.06153,0.00932],"force_p95":32.54264,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.37933,"mean_force":20.04396,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50022,0.06313,0.06314]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.51115,0.06321,0.05843],"force_p95":31.99523,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.84697,"mean_force":19.60602,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.50022,0.06313,0.06314]},{"body_a":"peg","body_b":"channel_base_body","contact_count":488.0,"contact_point_centroid":[0.50375,0.06155,0.00938],"force_p95":0.55464,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.31941,"mean_force":0.63367,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50242,0.06952,0.10655]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.51127,0.06329,0.0587],"force_p95":26.28217,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.83425,"mean_force":21.3134,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50034,0.06325,0.06357]},{"body_a":"peg","body_b":"channel_base_body","contact_count":367.0,"contact_point_centroid":[0.50353,0.06164,0.00933],"force_p95":0.60131,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56851,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.50299,0.13576,0.22198]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49971,0.19844,0.29829]}],"total_contact_groups":6},"final_pose_error":0.15165,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50354,0.06154,0.0336],"final_tcp_position":[0.50006,0.06301,0.06289],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":33.37933,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":390.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.06157,0.03377],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":27.31941,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":490.0,"raw_peak_contact_force":27.31941,"subtask_id":"reach_approach","tcp_end":[0.50704,0.07619,0.15239],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":488.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.06162,0.03376],"object_pos_start":[0.50378,0.06157,0.03377],"object_to_goal_dist_end":0.1418,"object_to_goal_dist_start":0.14176,"object_z_max":0.03379,"peak_contact_force":33.37933,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10.0,"raw_peak_contact_force":33.37933,"subtask_id":"reach_contact","tcp_end":[0.50036,0.06321,0.06333],"tcp_start":[0.50704,0.07619,0.15239],"tcp_to_object_dist_end":0.02982,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.50354,0.06154,0.0336],"object_pos_start":[0.50378,0.06162,0.03376],"object_to_goal_dist_end":0.14173,"object_to_goal_dist_start":0.1418,"object_z_max":0.03376,"peak_contact_force":0.55664,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":386.0,"raw_peak_contact_force":2.17216,"subtask_id":"push_progress","tcp_end":[0.50006,0.06301,0.06289],"tcp_start":[0.50036,0.06321,0.06333],"tcp_to_object_dist_end":0.02953,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.44828,"average_solve_count":87.0,"average_success_count":87.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.approach_speed":0.17091,"descend_to_contact.descend_force_threshold":15.10001,"descend_to_contact.descend_speed":0.03513,"push_along_channel.push_distance":0.15476,"push_along_channel.push_speed":0.06232,"retract_from_channel.retract_height":0.19452,"retract_from_channel.retract_speed":0.13366},"optimized_scores":{"best_composite_score":0.15782,"best_fitness_score":0.23449,"best_task_score":0.00102},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":523.0,"contact_point_centroid":[0.50103,0.11601,0.00943],"force_p95":0.60279,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.82655,"mean_force":0.61541,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4962,0.12124,0.10811]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50767,0.11664,0.05877],"force_p95":38.31588,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.31588,"mean_force":38.31588,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.49669,0.1167,0.06358]},{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49341,0.11878,0.00934],"force_p95":35.44985,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.0714,"mean_force":24.65372,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49653,0.11649,0.06316]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.50749,0.11655,0.05855],"force_p95":34.95017,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.55592,"mean_force":24.24066,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.49653,0.11649,0.06316]},{"body_a":"peg","body_b":"channel_base_body","contact_count":275.0,"contact_point_centroid":[0.5008,0.11597,0.00934],"force_p95":0.73513,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.57316,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49863,0.16217,0.225]}],"total_contact_groups":5},"final_pose_error":0.1563,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50064,0.11587,0.03372],"final_tcp_position":[0.49637,0.11597,0.06283],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":38.82655,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":291.0,"n_steps_budget":690.0,"object_pos_end":[0.50096,0.11607,0.0339],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19617,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":38.82655,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":524.0,"raw_peak_contact_force":38.82655,"subtask_id":"reach_approach","tcp_end":[0.49829,0.12648,0.15627],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12285,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":523.0,"n_steps_budget":1000.0,"object_pos_end":[0.50105,0.11627,0.03386],"object_pos_start":[0.50096,0.11607,0.0339],"object_to_goal_dist_end":0.19637,"object_to_goal_dist_start":0.19617,"object_z_max":0.03405,"peak_contact_force":38.0714,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14.0,"raw_peak_contact_force":38.0714,"subtask_id":"reach_contact","tcp_end":[0.49671,0.11668,0.06343],"tcp_start":[0.49829,0.12648,0.15627],"tcp_to_object_dist_end":0.02989,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50064,0.11587,0.03372],"object_pos_start":[0.50105,0.11627,0.03386],"object_to_goal_dist_end":0.19598,"object_to_goal_dist_start":0.19637,"object_z_max":0.03386,"peak_contact_force":0.50811,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":275.0,"raw_peak_contact_force":1.92055,"subtask_id":"push_progress","tcp_end":[0.49637,0.11597,0.06283],"tcp_start":[0.49671,0.11668,0.06343],"tcp_to_object_dist_end":0.02942,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.872,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_peg.approach_speed":0.15905,"descend_to_contact.descend_force_threshold":15.69344,"descend_to_contact.descend_speed":0.02067,"push_along_channel.push_distance":0.13456,"push_along_channel.push_speed":0.09657,"retract_from_channel.retract_height":0.06757,"retract_from_channel.retract_speed":0.15076},"optimized_scores":{"best_composite_score":0.15454,"best_fitness_score":0.23121,"best_task_score":0.00107},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49358,0.07233,0.00936],"force_p95":41.45837,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.39769,"mean_force":18.97447,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4887,0.0653,0.0637]},{"body_a":"attachment","body_b":"peg","contact_count":7.0,"contact_point_centroid":[0.49951,0.06539,0.05868],"force_p95":40.75862,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.65242,"mean_force":18.51286,"phase_index":2.0,"phase_name":"push_along_channel","phase_type":"push","tcp_position_centroid":[0.4887,0.0653,0.0637]},{"body_a":"peg","body_b":"channel_base_body","contact_count":662.0,"contact_point_centroid":[0.49513,0.0637,0.0094],"force_p95":0.55058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.17239,"mean_force":0.57821,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48339,0.07162,0.10594]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49965,0.06555,0.05894],"force_p95":21.67463,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.67463,"mean_force":21.67463,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48884,0.06556,0.06413]},{"body_a":"peg","body_b":"channel_base_body","contact_count":325.0,"contact_point_centroid":[0.49568,0.06407,0.00935],"force_p95":0.63319,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57157,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.48918,0.13571,0.22087]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_to_peg","phase_type":"approach","tcp_position_centroid":[0.49907,0.19671,0.2959]}],"total_contact_groups":6},"final_pose_error":0.13741,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49499,0.06361,0.03364],"final_tcp_position":[0.48861,0.06457,0.06327],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":47.39769,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":352.0,"n_steps_budget":840.0,"object_pos_end":[0.49491,0.06389,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.1441,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":22.17239,"phase_name":"approach_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":663.0,"raw_peak_contact_force":22.17239,"subtask_id":"reach_approach","tcp_end":[0.48049,0.07845,0.15306],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":662.0,"n_steps_budget":1000.0,"object_pos_end":[0.49534,0.06404,0.03401],"object_pos_start":[0.49491,0.06389,0.03392],"object_to_goal_dist_end":0.14424,"object_to_goal_dist_start":0.1441,"object_z_max":0.03401,"peak_contact_force":47.39769,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":14.0,"raw_peak_contact_force":47.39769,"subtask_id":"reach_contact","tcp_end":[0.48886,0.06554,0.06402],"tcp_start":[0.48049,0.07845,0.15306],"tcp_to_object_dist_end":0.03073,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":7.0,"n_steps_budget":900.0,"object_pos_end":[0.49499,0.06361,0.03364],"object_pos_start":[0.49534,0.06404,0.03401],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14424,"object_z_max":0.03401,"peak_contact_force":0.54566,"phase_name":"push_along_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":353.0,"raw_peak_contact_force":2.44546,"subtask_id":"push_progress","tcp_end":[0.48861,0.06457,0.06327],"tcp_start":[0.48886,0.06554,0.06402],"tcp_to_object_dist_end":0.03033,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```