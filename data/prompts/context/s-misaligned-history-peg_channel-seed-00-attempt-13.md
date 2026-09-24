## Search State

- **Seed**: 0
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → lift → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 9  | -0.2830 | 0.15 | ❌ rejected |
| 12 | approach → contact → push → lift → retract | arc_cartesian | linear_cartesian | impedance_motion | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 8  | -0.2392 | 0.00 | ❌ rejected |
| 11 | approach → contact → push → lift → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 8  | 0.0280 | 0.00 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | force_exceeded | pose_tolerance | 7  | 0.1778 | 0.72 | ❌ rejected |
| 9 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5  | -0.3722 | 0.16 | ❌ rejected |

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

## Current Skill (Q=-0.372) — your mutation base

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

- **Composite score**: -0.372
- **task_score** (E): 0.157
- **fitness_score**: 0.101  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_peg | 1.00 | 1.00 | 0.1738 |
| descend_to_peg | 0.33 | 1.00 | 0.1084 |
| push_through | 0.00 | 1.00 | 0.0022 |
| lift_off | 1.00 | 1.00 | 0.0806 |
| retract_clear | 1.00 | 1.00 | 0.2197 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_peg | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.494, 0.121, 0.151) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.529 | 2.179 |
| descend_to_peg | contact | 0.33 / step_budget | (0.494, 0.121, 0.151)→(0.495, 0.119, 0.044) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.333 | 6.545 | 6.580 |
| push_through | push | 0.00 / guard_failure | (0.509, 0.106, 0.034)→(0.510, 0.105, 0.033) | (0.500, 0.080, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.160 | 1.00 / 2.000 | 435.663 | 533.336 |
| lift_off | lift | 1.00 / step_budget | (0.510, 0.105, 0.033)→(0.507, 0.104, 0.113) | (0.499, 0.078, 0.034)→(0.496, 0.023, 0.031) | 0.159→0.107 | 1.00 / 1.000 | 0.526 | 394.425 |
| retract_clear | retract | 1.00 / step_budget | (0.507, 0.104, 0.113)→(0.503, -0.001, 0.306) | (0.496, 0.023, 0.031)→(0.498, 0.023, 0.031) | 0.107→0.107 | 1.00 / 1.000 | 0.540 | 0.642 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.867
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.335
- phase_score: 0.082
- phase_breakdown.push_channel_score: 0.035
- phase_breakdown.reach_peg_score: 0.193

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.183
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.335
- **Median Q (composite search score)**: -0.468
- **K-run variance**: 0.0233
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.319


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.14035,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.14972,"approach_peg.arc_height":0.17514,"descend_to_peg.contact_force_threshold":23.17768,"lift_off.lift_speed":0.09204,"push_through.force_guard_threshold":24.08074,"push_through.push_distance":0.12738,"push_through.push_speed":0.0517,"retract_clear.retract_arc_height":0.10745,"retract_clear.retract_speed":0.05718},"optimized_scores":{"best_composite_score":-0.46819,"best_fitness_score":0.07181,"best_task_score":0.08603},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":3.0,"contact_point_centroid":[0.52573,0.09164,0.05989],"force_p95":1459.00302,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1476.20889,"mean_force":1300.90437,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51013,0.08988,0.03106]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":11.0,"contact_point_centroid":[0.52664,0.08852,0.05974],"force_p95":174.16529,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":187.18883,"mean_force":55.15012,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.51111,0.08489,0.02871]},{"body_a":"peg","body_b":"channel_base_body","contact_count":233.0,"contact_point_centroid":[0.49494,0.03728,0.00938],"force_p95":1.08587,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.57085,"mean_force":0.63977,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50828,0.08604,0.0725]},{"body_a":"attachment","body_b":"peg","contact_count":9.0,"contact_point_centroid":[0.50815,0.07498,0.03083],"force_p95":4.30058,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.5137,"mean_force":2.30889,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.51182,0.08472,0.02895]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.5081,0.07819,0.03184],"force_p95":3.72909,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.79067,"mean_force":3.17484,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51079,0.08903,0.03068]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.50375,0.05816,0.00938],"force_p95":2.70114,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.26809,"mean_force":0.9385,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50477,0.0957,0.0341]},{"body_a":"peg","body_b":"channel_base_body","contact_count":345.0,"contact_point_centroid":[0.50358,0.06157,0.00932],"force_p95":0.62669,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56997,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.5066,0.12611,0.2425]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":30.0,"contact_point_centroid":[0.47388,0.04462,0.03521],"force_p95":1.13702,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.39487,"mean_force":0.53177,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50519,0.08645,0.03309]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49976,0.19709,0.29926]},{"body_a":"peg","body_b":"channel_base_body","contact_count":298.0,"contact_point_centroid":[0.49457,0.03705,0.00938],"force_p95":0.58077,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58436,"mean_force":0.54666,"phase_index":4.0,"phase_name":"retract_clear","phase_type":"retract","tcp_position_centroid":[0.50861,0.08749,0.22077]},{"body_a":"peg","body_b":"channel_base_body","contact_count":586.0,"contact_point_centroid":[0.50373,0.06162,0.00938],"force_p95":0.55017,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55453,"mean_force":0.54675,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.50346,0.09815,0.09616]}],"total_contact_groups":11},"final_pose_error":0.04974,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49442,0.03707,0.03378],"final_tcp_position":[0.50406,-0.00046,0.30172],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":1476.20889,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":368.0,"n_steps_budget":810.0,"object_pos_end":[0.50375,0.06157,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14175,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.54924,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":364.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_peg","tcp_end":[0.50921,0.0963,0.15901],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13008,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":586.0,"n_steps_budget":810.0,"object_pos_end":[0.50377,0.06157,0.03378],"object_pos_start":[0.50375,0.06157,0.03378],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14175,"object_z_max":0.03378,"peak_contact_force":0.54483,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":586.0,"raw_peak_contact_force":0.55453,"subtask_id":"reach_peg","tcp_end":[0.50017,0.10044,0.03698],"tcp_start":[0.50921,0.0963,0.15901],"tcp_to_object_dist_end":0.03916,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.06159,0.03378],"object_pos_start":[0.50377,0.06157,0.03378],"object_to_goal_dist_end":0.14178,"object_to_goal_dist_start":0.14176,"object_z_max":0.03382,"peak_contact_force":1304.15018,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":16.0,"raw_peak_contact_force":1476.20889,"subtask_id":"push_channel","tcp_end":[0.51221,0.08679,0.03003],"tcp_start":[0.51135,0.08823,0.0304],"tcp_to_object_dist_end":0.02685,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":274.0,"n_steps_budget":690.0,"object_pos_end":[0.49445,0.0371,0.03381],"object_pos_start":[0.50362,0.06126,0.03388],"object_to_goal_dist_end":0.11739,"object_to_goal_dist_start":0.14144,"object_z_max":0.03911,"peak_contact_force":0.54501,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":283.0,"raw_peak_contact_force":187.18883,"tcp_end":[0.50897,0.08612,0.11049],"tcp_start":[0.51221,0.08679,0.03003],"tcp_to_object_dist_end":0.09216,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":298.0,"n_steps_budget":1000.0,"object_pos_end":[0.49442,0.03707,0.03378],"object_pos_start":[0.49445,0.0371,0.03381],"object_to_goal_dist_end":0.11737,"object_to_goal_dist_start":0.11739,"object_z_max":0.03381,"peak_contact_force":0.55516,"phase_name":"retract_clear","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":298.0,"raw_peak_contact_force":0.58436,"tcp_end":[0.50406,-0.00046,0.30172],"tcp_start":[0.50897,0.08612,0.11049],"tcp_to_object_dist_end":0.27073,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02395,"average_solve_count":167.0,"average_success_count":167.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.08527,"approach_peg.arc_height":0.11326,"descend_to_peg.contact_force_threshold":32.10793,"lift_off.lift_speed":0.09707,"push_through.force_guard_threshold":30.38474,"push_through.push_distance":0.14241,"push_through.push_speed":0.08356,"retract_clear.retract_arc_height":0.14753,"retract_clear.retract_speed":0.07797},"optimized_scores":{"best_composite_score":-0.49149,"best_fitness_score":0.04851,"best_task_score":0.05166},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.54215,0.11965,0.05888],"force_p95":756.25713,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":992.38621,"mean_force":213.23041,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.52269,0.13824,0.01585]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50963,0.13135,0.0254],"force_p95":31.0232,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.33961,"mean_force":19.1755,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.51539,0.14154,0.02349]},{"body_a":"peg","body_b":"channel_base_body","contact_count":16.0,"contact_point_centroid":[0.49898,0.11587,0.00941],"force_p95":10.575,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.17894,"mean_force":2.55214,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.50611,0.14897,0.03069]},{"body_a":"peg","body_b":"channel_base_body","contact_count":362.0,"contact_point_centroid":[0.50095,0.116,0.00936],"force_p95":0.62592,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56612,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49857,0.21788,0.21284]},{"body_a":"peg","body_b":"channel_base_body","contact_count":263.0,"contact_point_centroid":[0.49476,0.10613,0.0095],"force_p95":0.81316,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.41631,"mean_force":0.56355,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.51673,0.13826,0.05742]},{"body_a":"peg","body_b":"link7","contact_count":8.0,"contact_point_centroid":[0.50701,0.12447,0.06084],"force_p95":0.75176,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.78858,"mean_force":0.40343,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.52362,0.13741,0.01442]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":102.0,"contact_point_centroid":[0.47483,0.10654,0.0358],"force_p95":0.47348,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.75868,"mean_force":0.22417,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.5181,0.1385,0.0373]},{"body_a":"peg","body_b":"channel_base_body","contact_count":515.0,"contact_point_centroid":[0.50089,0.11602,0.00942],"force_p95":0.60813,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64663,"mean_force":0.54291,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.49634,0.16556,0.08761]},{"body_a":"peg","body_b":"channel_base_body","contact_count":360.0,"contact_point_centroid":[0.49307,0.10658,0.0094],"force_p95":0.57599,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.60933,"mean_force":0.54508,"phase_index":4.0,"phase_name":"retract_clear","phase_type":"retract","tcp_position_centroid":[0.51387,0.12162,0.23371]}],"total_contact_groups":9},"final_pose_error":0.04947,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49312,0.10652,0.03381],"final_tcp_position":[0.50497,-0.00218,0.31163],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":992.38621,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":378.0,"n_steps_budget":1000.0,"object_pos_end":[0.50093,0.1161,0.034],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19619,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.49329,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":362.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_peg","tcp_end":[0.49812,0.17562,0.14146],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":515.0,"n_steps_budget":690.0,"object_pos_end":[0.50096,0.11611,0.03386],"object_pos_start":[0.50093,0.1161,0.034],"object_to_goal_dist_end":0.19621,"object_to_goal_dist_start":0.19619,"object_z_max":0.03402,"peak_contact_force":0.55093,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":515.0,"raw_peak_contact_force":0.64663,"subtask_id":"reach_peg","tcp_end":[0.49685,0.15632,0.03677],"tcp_start":[0.49812,0.17562,0.14146],"tcp_to_object_dist_end":0.04052,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.50021,0.11573,0.0338],"object_pos_start":[0.50096,0.11611,0.03386],"object_to_goal_dist_end":0.19583,"object_to_goal_dist_start":0.19621,"object_z_max":0.03393,"peak_contact_force":1.43934,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":18.0,"raw_peak_contact_force":32.33961,"subtask_id":"push_channel","tcp_end":[0.5188,0.13927,0.01898],"tcp_start":[0.51729,0.14009,0.02084],"tcp_to_object_dist_end":0.03345,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":275.0,"n_steps_budget":660.0,"object_pos_end":[0.49313,0.10658,0.03381],"object_pos_start":[0.49901,0.11457,0.03399],"object_to_goal_dist_end":0.1868,"object_to_goal_dist_start":0.19467,"object_z_max":0.0364,"peak_contact_force":0.53394,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":394.0,"raw_peak_contact_force":992.38621,"tcp_end":[0.51554,0.13822,0.09953],"tcp_start":[0.5188,0.13927,0.01898],"tcp_to_object_dist_end":0.07631,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":360.0,"n_steps_budget":1000.0,"object_pos_end":[0.49312,0.10652,0.03381],"object_pos_start":[0.49313,0.10658,0.03381],"object_to_goal_dist_end":0.18675,"object_to_goal_dist_start":0.1868,"object_z_max":0.03386,"peak_contact_force":0.50331,"phase_name":"retract_clear","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":360.0,"raw_peak_contact_force":0.60933,"tcp_end":[0.50497,-0.00218,0.31163],"tcp_start":[0.51554,0.13822,0.09953],"tcp_to_object_dist_end":0.29856,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.53125,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_peg.approach_speed":0.1115,"approach_peg.arc_height":0.10108,"descend_to_peg.contact_force_threshold":14.68712,"lift_off.lift_speed":0.1301,"push_through.force_guard_threshold":18.59488,"push_through.push_distance":0.1343,"push_through.push_speed":0.04147,"retract_clear.retract_arc_height":0.10309,"retract_clear.retract_speed":0.11401},"optimized_scores":{"best_composite_score":-0.15692,"best_fitness_score":0.18308,"best_task_score":0.33474},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":3.0,"contact_point_centroid":[0.49549,0.08046,0.05341],"force_p95":85.64567,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.45817,"mean_force":44.20487,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49555,0.09194,0.05287]},{"body_a":"peg","body_b":"channel_base_body","contact_count":11.0,"contact_point_centroid":[0.50256,0.05129,0.00933],"force_p95":61.48835,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.27295,"mean_force":12.13425,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.49159,0.09554,0.05505]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47495,0.09976,0.0599],"force_p95":18.53893,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":18.53893,"mean_force":18.53893,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.48677,0.09977,0.05816]},{"body_a":"peg","body_b":"channel_base_body","contact_count":252.0,"contact_point_centroid":[0.50041,-0.05715,0.00886],"force_p95":1.0484,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.70051,"mean_force":0.58019,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.49597,0.08707,0.08552]},{"body_a":"peg","body_b":"channel_base_body","contact_count":100.0,"contact_point_centroid":[0.4953,-0.10013,0.0255],"force_p95":1.27413,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.99584,"mean_force":0.31779,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.49646,0.08723,0.08818]},{"body_a":"peg","body_b":"channel_base_body","contact_count":462.0,"contact_point_centroid":[0.49554,0.064,0.00936],"force_p95":0.59676,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56392,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.48009,0.10643,0.25286]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47491,0.03827,0.06],"force_p95":2.15153,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17231,"mean_force":1.96453,"phase_index":3.0,"phase_name":"lift_off","phase_type":"lift","tcp_position_centroid":[0.50374,0.0861,0.04292]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_peg","phase_type":"approach","tcp_position_centroid":[0.49832,0.19528,0.30067]},{"body_a":"peg","body_b":"channel_base_body","contact_count":263.0,"contact_point_centroid":[0.50355,-0.07501,0.00801],"force_p95":0.72696,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73222,"mean_force":0.60679,"phase_index":4.0,"phase_name":"retract_clear","phase_type":"retract","tcp_position_centroid":[0.49732,0.08371,0.23337]},{"body_a":"peg","body_b":"channel_base_body","contact_count":564.0,"contact_point_centroid":[0.49493,0.06381,0.0094],"force_p95":0.55069,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55289,"mean_force":0.54545,"phase_index":1.0,"phase_name":"descend_to_peg","phase_type":"contact","tcp_position_centroid":[0.48011,0.09457,0.10358]},{"body_a":"peg","body_b":"channel_base_body","contact_count":74.0,"contact_point_centroid":[0.49456,-0.10002,0.03949],"force_p95":0.0307,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.05463,"mean_force":0.00404,"phase_index":4.0,"phase_name":"retract_clear","phase_type":"retract","tcp_position_centroid":[0.49734,0.08337,0.23347]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47497,0.09979,0.05972],"force_p95":0.0,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_through","phase_type":"push","tcp_position_centroid":[0.48681,0.09979,0.05798]}],"total_contact_groups":12},"final_pose_error":0.04915,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50497,-0.07489,0.02409],"final_tcp_position":[0.50011,-0.00096,0.30331],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":91.45817,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.49491,0.06394,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14415,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54539,"phase_name":"approach_peg","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":490.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_peg","tcp_end":[0.47594,0.08968,0.15302],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1233,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":564.0,"n_steps_budget":780.0,"object_pos_end":[0.49504,0.06359,0.03402],"object_pos_start":[0.49491,0.06394,0.03394],"object_to_goal_dist_end":0.1438,"object_to_goal_dist_start":0.14415,"object_z_max":0.03402,"peak_contact_force":18.53893,"phase_name":"descend_to_peg","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":565.0,"raw_peak_contact_force":18.53893,"subtask_id":"reach_peg","tcp_end":[0.48681,0.09979,0.05798],"tcp_start":[0.47594,0.08968,0.15302],"tcp_to_object_dist_end":0.04419,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":11.0,"n_steps_budget":1000.0,"object_pos_end":[0.4948,0.06261,0.03412],"object_pos_start":[0.49504,0.06359,0.03402],"object_to_goal_dist_end":0.14283,"object_to_goal_dist_start":0.1438,"object_z_max":0.03479,"peak_contact_force":1.40019,"phase_name":"push_through","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":91.45817,"subtask_id":"push_channel","tcp_end":[0.5003,0.08805,0.04949],"tcp_start":[0.49876,0.08926,0.05072],"tcp_to_object_dist_end":0.03023,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":314.0,"n_steps_budget":600.0,"object_pos_end":[0.50177,-0.07495,0.02408],"object_pos_start":[0.49454,0.05924,0.03552],"object_to_goal_dist_end":0.0168,"object_to_goal_dist_start":0.13942,"object_z_max":0.04577,"peak_contact_force":0.49926,"phase_name":"lift_off","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":354.0,"raw_peak_contact_force":3.70051,"tcp_end":[0.49733,0.08743,0.12996],"tcp_start":[0.5003,0.08805,0.04949],"tcp_to_object_dist_end":0.1939,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":263.0,"n_steps_budget":1000.0,"object_pos_end":[0.50497,-0.07489,0.02409],"object_pos_start":[0.50177,-0.07495,0.02408],"object_to_goal_dist_end":0.01744,"object_to_goal_dist_start":0.0168,"object_z_max":0.02409,"peak_contact_force":0.56292,"phase_name":"retract_clear","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":337.0,"raw_peak_contact_force":0.73222,"tcp_end":[0.50011,-0.00096,0.30331],"tcp_start":[0.49733,0.08743,0.12996],"tcp_to_object_dist_end":0.28889,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```