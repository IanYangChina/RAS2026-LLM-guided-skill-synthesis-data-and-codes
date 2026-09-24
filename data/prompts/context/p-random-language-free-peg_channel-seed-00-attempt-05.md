## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 7 | -0.0598 | 0.00 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1293 | 0.00 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | -0.2036 | 0.00 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.5176 | 0.24 | ❌ rejected |
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.1133 | 0.00 | ❌ rejected |

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

## Current Skill (Q=-0.060) — your mutation base

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

- **Composite score**: -0.060
- **task_score** (E): 0.000
- **fitness_score**: 0.098  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1636 |
| descend_1 | 0.33 | 1.00 | 0.0970 |
| push_1 | 0.33 | 1.00 | 0.0024 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.144, 0.148) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.533 | 2.179 |
| descend_1 | descend | 0.33 / step_budget | (0.495, 0.144, 0.148)→(0.496, 0.103, 0.061) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.333 | 4.511 | 4.534 |
| push_1 | push | 0.33 / guard_failure | (0.497, 0.106, 0.060)→(0.497, 0.109, 0.059) | (0.500, 0.080, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 2.000 | 116.487 | 116.487 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.181
- terminal_score: 0.000
- phase_score: 0.167
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_pre_contact_score: 0.557

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.100
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: 0.050
- **K-run variance**: 0.0250
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.248


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.0365,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06559,"descend_1.contact_force_threshold":9.38632,"descend_1.descend_speed":0.02721,"push_1.push_distance":0.13097,"push_1.push_force_threshold":31.86769,"push_1.push_lateral_offset":-0.00262,"push_1.push_speed":0.02629},"optimized_scores":{"best_composite_score":-0.28334,"best_fitness_score":0.09666,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":7.0,"contact_point_centroid":[0.49945,0.06193,0.0093],"force_p95":191.31926,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":192.66351,"mean_force":77.19946,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50107,0.08685,0.05992]},{"body_a":"attachment","body_b":"peg","contact_count":4.0,"contact_point_centroid":[0.50967,0.07974,0.05817],"force_p95":189.71089,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":190.40487,"mean_force":132.85365,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50152,0.08837,0.05934]},{"body_a":"peg","body_b":"channel_base_body","contact_count":537.0,"contact_point_centroid":[0.50366,0.06162,0.00934],"force_p95":0.59385,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56154,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50277,0.16229,0.22015]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49978,0.1991,0.29863]},{"body_a":"peg","body_b":"channel_base_body","contact_count":585.0,"contact_point_centroid":[0.50379,0.06157,0.00938],"force_p95":0.55248,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55826,"mean_force":0.54649,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50241,0.10554,0.10245]}],"total_contact_groups":5},"final_pose_error":0.13951,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50392,0.06372,0.03467],"final_tcp_position":[0.50225,0.09294,0.05824],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":192.66351,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":560.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06154,0.0338],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14172,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.55107,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":556.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_pre_contact","tcp_end":[0.50708,0.12688,0.14732],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13102,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":585.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.06149,0.03384],"object_pos_start":[0.50377,0.06154,0.0338],"object_to_goal_dist_end":0.14168,"object_to_goal_dist_start":0.14172,"object_z_max":0.03384,"peak_contact_force":0.54774,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":585.0,"raw_peak_contact_force":0.55826,"subtask_id":"reach_pre_contact","tcp_end":[0.50031,0.08445,0.06093],"tcp_start":[0.50708,0.12688,0.14732],"tcp_to_object_dist_end":0.03568,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":7.0,"n_steps_budget":1000.0,"object_pos_end":[0.50378,0.0622,0.03394],"object_pos_start":[0.50376,0.06149,0.03384],"object_to_goal_dist_end":0.14238,"object_to_goal_dist_start":0.14168,"object_z_max":0.03424,"peak_contact_force":192.66351,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":192.66351,"subtask_id":"push_to_goal","tcp_end":[0.50225,0.09294,0.05824],"tcp_start":[0.50199,0.09081,0.05865],"tcp_to_object_dist_end":0.03922,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01493,"average_solve_count":134.0,"average_success_count":134.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0511,"descend_1.contact_force_threshold":9.73819,"descend_1.descend_speed":0.03084,"push_1.push_distance":0.13538,"push_1.push_force_threshold":23.41685,"push_1.push_lateral_offset":0.00298,"push_1.push_speed":0.03739},"optimized_scores":{"best_composite_score":0.05365,"best_fitness_score":0.10032,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":4.0,"contact_point_centroid":[0.49244,0.12,0.00939],"force_p95":34.91158,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.97442,"mean_force":10.63966,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49723,0.13903,0.06071]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50707,0.1332,0.05871],"force_p95":39.72576,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":39.72576,"mean_force":39.72576,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49738,0.1401,0.06023]},{"body_a":"peg","body_b":"channel_base_body","contact_count":481.0,"contact_point_centroid":[0.5009,0.11595,0.00939],"force_p95":0.61961,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55882,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49817,0.18811,0.22272]},{"body_a":"peg","body_b":"channel_base_body","contact_count":558.0,"contact_point_centroid":[0.50102,0.11602,0.00942],"force_p95":0.61349,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.65192,"mean_force":0.54322,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49625,0.15753,0.10369]}],"total_contact_groups":4},"final_pose_error":0.13843,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50095,0.11639,0.03381],"final_tcp_position":[0.49728,0.14131,0.05976],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":40.97442,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":497.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11607,0.03397],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19616,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.50283,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":481.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.49798,0.17718,0.14948],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":558.0,"n_steps_budget":1000.0,"object_pos_end":[0.50092,0.11612,0.03382],"object_pos_start":[0.50096,0.11607,0.03397],"object_to_goal_dist_end":0.19622,"object_to_goal_dist_start":0.19616,"object_z_max":0.03398,"peak_contact_force":0.59335,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":558.0,"raw_peak_contact_force":0.65192,"subtask_id":"reach_pre_contact","tcp_end":[0.49706,0.13828,0.06112],"tcp_start":[0.49798,0.17718,0.14948],"tcp_to_object_dist_end":0.03537,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.50095,0.11639,0.03381],"object_pos_start":[0.50092,0.11612,0.03382],"object_to_goal_dist_end":0.19648,"object_to_goal_dist_start":0.19622,"object_z_max":0.03382,"peak_contact_force":40.97442,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":40.97442,"subtask_id":"push_to_goal","tcp_end":[0.49728,0.14131,0.05976],"tcp_start":[0.49706,0.13828,0.06112],"tcp_to_object_dist_end":0.03617,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12319,"average_solve_count":138.0,"average_success_count":138.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07796,"descend_1.contact_force_threshold":3.34185,"descend_1.descend_speed":0.02372,"push_1.push_distance":0.13453,"push_1.push_force_threshold":27.17655,"push_1.push_lateral_offset":0.00453,"push_1.push_speed":0.01622},"optimized_scores":{"best_composite_score":0.0503,"best_fitness_score":0.09697,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50647,0.06674,0.00929],"force_p95":112.33028,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":115.82371,"mean_force":58.63975,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49076,0.08782,0.06014]},{"body_a":"attachment","body_b":"peg","contact_count":5.0,"contact_point_centroid":[0.50093,0.08165,0.05863],"force_p95":110.18809,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":113.76936,"mean_force":57.08925,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49076,0.08782,0.06014]},{"body_a":"peg","body_b":"channel_base_body","contact_count":747.0,"contact_point_centroid":[0.49493,0.06381,0.0094],"force_p95":0.55075,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.39184,"mean_force":0.56121,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48378,0.10717,0.1017]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50044,0.0805,0.05921],"force_p95":11.96123,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.96123,"mean_force":11.96123,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49024,0.08663,0.06073]},{"body_a":"peg","body_b":"channel_base_body","contact_count":500.0,"contact_point_centroid":[0.49555,0.06394,0.00937],"force_p95":0.59534,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56254,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48882,0.16331,0.2202]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49931,0.1986,0.29731]}],"total_contact_groups":6},"final_pose_error":0.13926,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49605,0.06589,0.03469],"final_tcp_position":[0.49179,0.09129,0.05916],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":115.82371,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.49499,0.06404,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14425,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.5438,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":528.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.47969,0.12924,0.14829],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13252,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":747.0,"n_steps_budget":1000.0,"object_pos_end":[0.4952,0.06359,0.03403],"object_pos_start":[0.49499,0.06404,0.03394],"object_to_goal_dist_end":0.14379,"object_to_goal_dist_start":0.14425,"object_z_max":0.03402,"peak_contact_force":12.39184,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":748.0,"raw_peak_contact_force":12.39184,"subtask_id":"reach_pre_contact","tcp_end":[0.49026,0.08658,0.06064],"tcp_start":[0.47969,0.12924,0.14829],"tcp_to_object_dist_end":0.03551,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.4956,0.06445,0.03406],"object_pos_start":[0.4952,0.06359,0.03403],"object_to_goal_dist_end":0.14464,"object_to_goal_dist_start":0.14379,"object_z_max":0.03432,"peak_contact_force":115.82371,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":10.0,"raw_peak_contact_force":115.82371,"subtask_id":"push_to_goal","tcp_end":[0.49179,0.09129,0.05916],"tcp_start":[0.49145,0.08972,0.05954],"tcp_to_object_dist_end":0.03695,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```