## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7  | 0.1778 | 0.72 | ❌ rejected |
| 9 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | 0.2024 | 0.72 | ❌ rejected |
| 8 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | 0.1642 | 0.68 | ❌ rejected |
| 7 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | 0.0255 | 0.20 | ❌ rejected |
| 6 | approach → contact → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7  | 0.0280 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.028) — your mutation base

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

- **Composite score**: 0.028
- **task_score** (E): 0.003
- **fitness_score**: 0.105  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.2341 |
| descend_to_peg | 1.00 | 1.00 | 0.0333 |
| push_through | 0.33 | 1.00 | 0.0002 |
| retract_from_channel | 1.00 | 1.00 | 0.1169 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.494, 0.086, 0.097) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.544 | 2.179 |
| descend_to_peg | contact | 1.00 / force_exceeded | (0.494, 0.086, 0.097)→(0.493, 0.088, 0.064) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 17.003 | 17.003 |
| push_through | push | 0.33 / guard_failure | (0.493, 0.087, 0.064)→(0.493, 0.087, 0.064) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.000 | 18.743 | 52.443 |
| retract_from_channel | retract | 1.00 / step_budget | (0.493, 0.087, 0.064)→(0.490, 0.087, 0.180) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.160→0.160 | 1.00 / 1.000 | 0.546 | 17.244 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.002
- alignment_error: None
- force_efficiency: 0.414
- terminal_score: 0.002
- phase_score: 0.168
- phase_breakdown.push_channel_score: 0.001
- phase_breakdown.reach_peg_score: 0.558

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.106
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.003
- **Median Q (composite search score)**: -0.054
- **K-run variance**: 0.0134
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.234


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81013,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.12463,"descend_to_peg.contact_force_threshold":12.47849,"push_through.push_distance":0.16989,"push_through.push_force_threshold":19.10222,"push_through.push_speed":0.071,"retract_from_channel.retract_height":0.15058,"retract_from_channel.retract_speed":0.13864},"optimized_scores":{"best_composite_score":0.19194,"best_fitness_score":0.10194,"best_task_score":0.00213},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.50964,0.05901,0.00936],"force_p95":27.88913,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.29522,"mean_force":15.23428,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50158,0.0692,0.06341]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.51253,0.06925,0.05863],"force_p95":27.19928,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.53229,"mean_force":15.20215,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50158,0.0692,0.06341]},{"body_a":"peg","body_b":"channel_base_body","contact_count":163.0,"contact_point_centroid":[0.50375,0.06166,0.00938],"force_p95":0.55448,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.51688,"mean_force":0.68754,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.50347,0.06845,0.07942]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.51259,0.06919,0.05875],"force_p95":23.00433,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.00433,"mean_force":23.00433,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.50164,0.0692,0.06362]},{"body_a":"peg","body_b":"channel_base_body","contact_count":384.0,"contact_point_centroid":[0.50302,0.06137,0.0094],"force_p95":0.60579,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.53089,"mean_force":0.66973,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49877,0.06877,0.12747]},{"body_a":"attachment","body_b":"peg","contact_count":10.0,"contact_point_centroid":[0.51179,0.06919,0.0587],"force_p95":20.39129,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":21.85332,"mean_force":4.86495,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.50085,0.06909,0.06345]},{"body_a":"peg","body_b":"channel_base_body","contact_count":742.0,"contact_point_centroid":[0.50363,0.06159,0.00935],"force_p95":0.5828,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55754,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.50264,0.13226,0.19366]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49967,0.19889,0.29858]}],"total_contact_groups":8},"final_pose_error":0.01998,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50359,0.0612,0.03398],"final_tcp_position":[0.499,0.0688,0.19402],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":29.29522,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":765.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06161,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.1418,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.55544,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":761.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_peg","tcp_end":[0.5068,0.0683,0.09594],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06259,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":163.0,"n_steps_budget":600.0,"object_pos_end":[0.50379,0.06162,0.03379],"object_pos_start":[0.50377,0.06161,0.03378],"object_to_goal_dist_end":0.14181,"object_to_goal_dist_start":0.1418,"object_z_max":0.03379,"peak_contact_force":23.51688,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":164.0,"raw_peak_contact_force":23.51688,"subtask_id":"reach_peg","tcp_end":[0.50163,0.06921,0.06347],"tcp_start":[0.5068,0.0683,0.09594],"tcp_to_object_dist_end":0.03071,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.06142,0.03367],"object_pos_start":[0.50379,0.06162,0.03379],"object_to_goal_dist_end":0.14161,"object_to_goal_dist_start":0.14181,"object_z_max":0.03379,"peak_contact_force":29.29522,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":29.29522,"subtask_id":"push_channel","tcp_end":[0.50147,0.06917,0.06326],"tcp_start":[0.50163,0.06921,0.06347],"tcp_to_object_dist_end":0.03067,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":384.0,"n_steps_budget":690.0,"object_pos_end":[0.50359,0.0612,0.03398],"object_pos_start":[0.50373,0.06142,0.03367],"object_to_goal_dist_end":0.14137,"object_to_goal_dist_start":0.14161,"object_z_max":0.03467,"peak_contact_force":0.5391,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":394.0,"raw_peak_contact_force":22.53089,"tcp_end":[0.499,0.0688,0.19402],"tcp_start":[0.50147,0.06917,0.06326],"tcp_to_object_dist_end":0.16029,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.86316,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.10177,"descend_to_peg.contact_force_threshold":11.89326,"push_through.push_distance":0.15149,"push_through.push_force_threshold":18.39036,"push_through.push_speed":0.05303,"retract_from_channel.retract_height":0.16984,"retract_from_channel.retract_speed":0.10675},"optimized_scores":{"best_composite_score":-0.05454,"best_fitness_score":0.10546,"best_task_score":0.00305},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.50401,0.10362,0.00938],"force_p95":68.42842,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.91582,"mean_force":23.7679,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49517,0.12183,0.0635]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50613,0.12221,0.05876],"force_p95":67.88381,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.24097,"mean_force":23.62067,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49517,0.12183,0.0635]},{"body_a":"peg","body_b":"channel_base_body","contact_count":459.0,"contact_point_centroid":[0.49999,0.11526,0.00944],"force_p95":0.63495,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.86821,"mean_force":0.73597,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.49238,0.12104,0.13731]},{"body_a":"attachment","body_b":"peg","contact_count":11.0,"contact_point_centroid":[0.50545,0.12204,0.05888],"force_p95":20.98585,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":23.19255,"mean_force":8.15028,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.4945,0.12166,0.06361]},{"body_a":"peg","body_b":"channel_base_body","contact_count":187.0,"contact_point_centroid":[0.50084,0.11595,0.00945],"force_p95":0.58827,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":14.75851,"mean_force":0.61603,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.49539,0.12087,0.08001]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50618,0.12229,0.05895],"force_p95":14.31597,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.31597,"mean_force":14.31597,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.49522,0.12206,0.06379]},{"body_a":"peg","body_b":"channel_base_body","contact_count":649.0,"contact_point_centroid":[0.50101,0.116,0.00938],"force_p95":0.61021,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55595,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49788,0.15939,0.19606]}],"total_contact_groups":7},"final_pose_error":0.01975,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.5008,0.11555,0.03387],"final_tcp_position":[0.49271,0.12109,0.21352],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":77.91582,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":665.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11603,0.03393],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.5347,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":649.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_peg","tcp_end":[0.49741,0.12039,0.09796],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06428,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":187.0,"n_steps_budget":600.0,"object_pos_end":[0.50096,0.11603,0.03396],"object_pos_start":[0.50096,0.11603,0.03393],"object_to_goal_dist_end":0.19613,"object_to_goal_dist_start":0.19613,"object_z_max":0.03398,"peak_contact_force":14.75851,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":188.0,"raw_peak_contact_force":14.75851,"subtask_id":"reach_peg","tcp_end":[0.49523,0.12207,0.06365],"tcp_start":[0.49741,0.12039,0.09796],"tcp_to_object_dist_end":0.03084,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50089,0.11572,0.03376],"object_pos_start":[0.50096,0.11603,0.03396],"object_to_goal_dist_end":0.19582,"object_to_goal_dist_start":0.19613,"object_z_max":0.03396,"peak_contact_force":1.30578,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":77.91582,"subtask_id":"push_channel","tcp_end":[0.49505,0.12169,0.06329],"tcp_start":[0.49513,0.12162,0.06336],"tcp_to_object_dist_end":0.03068,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":459.0,"n_steps_budget":990.0,"object_pos_end":[0.5008,0.11555,0.03387],"object_pos_start":[0.50086,0.11569,0.03369],"object_to_goal_dist_end":0.19565,"object_to_goal_dist_start":0.1958,"object_z_max":0.03501,"peak_contact_force":0.5555,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":470.0,"raw_peak_contact_force":23.86821,"tcp_end":[0.49271,0.12109,0.21352],"tcp_start":[0.49505,0.12169,0.06329],"tcp_to_object_dist_end":0.17993,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.87097,"average_solve_count":93.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.08561,"descend_to_peg.contact_force_threshold":8.17765,"push_through.push_distance":0.18008,"push_through.push_force_threshold":13.68422,"push_through.push_speed":0.07225,"retract_from_channel.retract_height":0.08922,"retract_from_channel.retract_speed":0.1777},"optimized_scores":{"best_composite_score":-0.05352,"best_fitness_score":0.10648,"best_task_score":0.00233},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":2.0,"contact_point_centroid":[0.49179,0.04616,0.0094],"force_p95":48.89419,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.11866,"mean_force":37.87397,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48204,0.07146,0.06427]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.49275,0.07209,0.05902],"force_p95":48.43452,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.65772,"mean_force":37.4257,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48204,0.07146,0.06427]},{"body_a":"peg","body_b":"channel_base_body","contact_count":231.0,"contact_point_centroid":[0.49506,0.06407,0.0094],"force_p95":0.55064,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.73289,"mean_force":0.59815,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.47929,0.07084,0.0789]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.49275,0.07203,0.05907],"force_p95":12.23191,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.23191,"mean_force":12.23191,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.48204,0.07145,0.06441]},{"body_a":"peg","body_b":"channel_base_body","contact_count":214.0,"contact_point_centroid":[0.4941,0.06317,0.00945],"force_p95":0.67825,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.33358,"mean_force":0.58992,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.47932,0.07108,0.09778]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.49221,0.07189,0.0591],"force_p95":3.50493,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.69535,"mean_force":1.23403,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.4815,0.07144,0.06426]},{"body_a":"peg","body_b":"channel_base_body","contact_count":747.0,"contact_point_centroid":[0.49525,0.06384,0.00938],"force_p95":0.56475,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55692,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48812,0.13318,0.1936]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49928,0.1983,0.29735]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":10.0,"contact_point_centroid":[0.47487,0.06364,0.05911],"force_p95":0.09874,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12717,"mean_force":0.02077,"phase_index":3.0,"phase_name":"retract_from_channel","phase_type":"retract","tcp_position_centroid":[0.48042,0.07129,0.06678]}],"total_contact_groups":9},"final_pose_error":0.01981,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49497,0.06329,0.03408],"final_tcp_position":[0.47906,0.07103,0.13379],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":50.11866,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":774.0,"n_steps_budget":1000.0,"object_pos_end":[0.49524,0.06367,0.03398],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14387,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54197,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":775.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.47851,0.07072,0.09678],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06537,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":231.0,"n_steps_budget":600.0,"object_pos_end":[0.49504,0.06359,0.03401],"object_pos_start":[0.49524,0.06367,0.03398],"object_to_goal_dist_end":0.1438,"object_to_goal_dist_start":0.14387,"object_z_max":0.03401,"peak_contact_force":12.73289,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":232.0,"raw_peak_contact_force":12.73289,"subtask_id":"reach_peg","tcp_end":[0.48206,0.07146,0.06431],"tcp_start":[0.47851,0.07072,0.09678],"tcp_to_object_dist_end":0.03389,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.49503,0.0635,0.03405],"object_pos_start":[0.49504,0.06359,0.03401],"object_to_goal_dist_end":0.14371,"object_to_goal_dist_start":0.1438,"object_z_max":0.03405,"peak_contact_force":25.62929,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4.0,"raw_peak_contact_force":50.11866,"subtask_id":"push_channel","tcp_end":[0.48199,0.07148,0.06417],"tcp_start":[0.48201,0.07147,0.06424],"tcp_to_object_dist_end":0.03378,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":214.0,"n_steps_budget":600.0,"object_pos_end":[0.49497,0.06329,0.03408],"object_pos_start":[0.49502,0.06343,0.03408],"object_to_goal_dist_end":0.1435,"object_to_goal_dist_start":0.14364,"object_z_max":0.0351,"peak_contact_force":0.54369,"phase_name":"retract_from_channel","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":233.0,"raw_peak_contact_force":5.33358,"tcp_end":[0.47906,0.07103,0.13379],"tcp_start":[0.48199,0.07148,0.06417],"tcp_to_object_dist_end":0.10127,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```