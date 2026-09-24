## Search State

- **Seed**: 0
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 7 | -0.1885 | 0.08 | ❌ rejected |
| 9 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | 0.1537 | 0.22 | ❌ rejected |
| 8 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2024 | 0.72 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.0855 | 0.00 | ❌ rejected |
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 8 | -0.0781 | 0.01 | ❌ rejected |

**Proposal policy**: task_score is 0.08 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.189) — your mutation base

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

- **Composite score**: -0.189
- **task_score** (E): 0.081
- **fitness_score**: 0.191  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2604 |
| push_1 | 0.33 | 1.00 | 0.0157 |
| retract_1 | 1.00 | 1.00 | 0.2305 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.108, 0.058) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.667 | 196.778 | 199.076 |
| push_1 | push | 0.33 / guard_failure | (0.495, 0.108, 0.058)→(0.493, 0.096, 0.049) | (0.500, 0.080, 0.034)→(0.501, 0.068, 0.034) | 0.161→0.148 | 1.00 / 2.000 | 260.803 | 267.036 |
| retract_1 | retract | 1.00 / step_budget | (0.500, 0.052, 0.032)→(0.505, 0.024, 0.260) | (0.507, 0.023, 0.035)→(0.507, 0.023, 0.034) | 0.103→0.103 | 1.00 / 1.000 | 0.554 | 6.931 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.242
- alignment_error: None
- force_efficiency: 0.556
- terminal_score: 0.242
- phase_score: 0.391
- phase_breakdown.insert_peg_score: 0.270
- phase_breakdown.approach_peg_score: 0.675

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.331
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.242
- **Median Q (composite search score)**: -0.258
- **K-run variance**: 0.0098
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.343


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.15288,"push_1.force_limit":25.84705,"push_1.max_time":3.63077,"push_1.push_distance":0.19993,"push_1.push_speed":0.03589,"retract_1.retract_height":0.14446,"retract_1.retract_speed":0.13525},"optimized_scores":{"best_composite_score":-0.04856,"best_fitness_score":0.33144,"best_task_score":0.2416},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":528.0,"contact_point_centroid":[0.50415,0.05773,0.04606],"force_p95":12.80354,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.20012,"mean_force":4.59094,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50131,0.06956,0.04019]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":379.0,"contact_point_centroid":[0.52518,0.04335,0.03015],"force_p95":14.3494,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.16302,"mean_force":2.7441,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50141,0.07246,0.04163]},{"body_a":"peg","body_b":"channel_base_body","contact_count":568.0,"contact_point_centroid":[0.50687,0.02734,0.0099],"force_p95":6.26668,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.06503,"mean_force":3.72111,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50085,0.07335,0.04069]},{"body_a":"attachment","body_b":"peg","contact_count":30.0,"contact_point_centroid":[0.50292,0.03867,0.05169],"force_p95":6.26798,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.93069,"mean_force":1.48553,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49923,0.05034,0.04516]},{"body_a":"peg","body_b":"channel_base_body","contact_count":409.0,"contact_point_centroid":[0.50358,0.06156,0.00933],"force_p95":0.60058,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.91858,"mean_force":0.59663,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50313,0.14324,0.17233]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50559,0.07929,0.05755],"force_p95":6.75831,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":6.78082,"mean_force":6.55572,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50686,0.0912,0.05747]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":108.0,"contact_point_centroid":[0.52504,0.02211,0.04763],"force_p95":0.5112,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.48944,"mean_force":0.37173,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49985,0.04564,0.08268]},{"body_a":"peg","body_b":"channel_base_body","contact_count":597.0,"contact_point_centroid":[0.50632,0.01998,0.00951],"force_p95":0.64519,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.96885,"mean_force":0.54467,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50159,0.03814,0.14368]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49996,0.19838,0.2968]}],"total_contact_groups":9},"final_pose_error":0.01973,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50695,0.02293,0.03378],"final_tcp_position":[0.50503,0.02386,0.26026],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":22.20012,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":432.0,"n_steps_budget":600.0,"object_pos_end":[0.50362,0.06119,0.03393],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14136,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.02533,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":430.0,"raw_peak_contact_force":6.91858,"subtask_id":"approach_peg","tcp_end":[0.50686,0.09089,0.0568],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03762,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":661.0,"n_steps_budget":840.0,"object_pos_end":[0.50692,0.02291,0.03541],"object_pos_start":[0.50362,0.06119,0.03393],"object_to_goal_dist_end":0.10324,"object_to_goal_dist_start":0.14136,"object_z_max":0.03628,"peak_contact_force":3.50194,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1475.0,"raw_peak_contact_force":22.20012,"subtask_id":"insert_peg","tcp_end":[0.50049,0.05231,0.0316],"tcp_start":[0.50686,0.09089,0.0568],"tcp_to_object_dist_end":0.03034,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":599.0,"n_steps_budget":1000.0,"object_pos_end":[0.50695,0.02293,0.03378],"object_pos_start":[0.50692,0.02291,0.03541],"object_to_goal_dist_end":0.10335,"object_to_goal_dist_start":0.10324,"object_z_max":0.03623,"peak_contact_force":0.55365,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":735.0,"raw_peak_contact_force":6.93069,"tcp_end":[0.50503,0.02386,0.26026],"tcp_start":[0.50049,0.05231,0.0316],"tcp_to_object_dist_end":0.22649,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.03571,"average_solve_count":28.0,"average_success_count":28.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.10627,"push_1.force_limit":30.50106,"push_1.max_time":5.758,"push_1.push_distance":0.14045,"push_1.push_speed":0.0388,"retract_1.retract_height":0.11711,"retract_1.retract_speed":0.07712},"optimized_scores":{"best_composite_score":-0.25837,"best_fitness_score":0.12163,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51828,0.12,0.00935],"force_p95":100.40754,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":100.40754,"mean_force":100.40754,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49792,0.14096,0.05873]},{"body_a":"attachment","body_b":"peg","contact_count":1.0,"contact_point_centroid":[0.50697,0.13322,0.05806],"force_p95":98.87493,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.87493,"mean_force":98.87493,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49792,0.14096,0.05873]},{"body_a":"peg","body_b":"channel_base_body","contact_count":412.0,"contact_point_centroid":[0.50087,0.11602,0.00935],"force_p95":0.6327,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.59599,"mean_force":0.92031,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49847,0.16957,0.17542]},{"body_a":"attachment","body_b":"peg","contact_count":2.0,"contact_point_centroid":[0.50684,0.1332,0.05845],"force_p95":83.18584,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.26286,"mean_force":73.49267,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49792,0.14111,0.05941]}],"total_contact_groups":4},"final_pose_error":0.03701,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50113,0.11631,0.0338],"final_tcp_position":[0.49805,0.14125,0.05826],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":100.40754,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":428.0,"n_steps_budget":810.0,"object_pos_end":[0.50105,0.11612,0.03377],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19623,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":84.59599,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":414.0,"raw_peak_contact_force":84.59599,"subtask_id":"approach_peg","tcp_end":[0.49792,0.14096,0.05873],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.03535,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":630.0,"object_pos_end":[0.50113,0.11631,0.0338],"object_pos_start":[0.50105,0.11612,0.03377],"object_to_goal_dist_end":0.19641,"object_to_goal_dist_start":0.19623,"object_z_max":0.03377,"peak_contact_force":100.40754,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":100.40754,"subtask_id":"insert_peg","tcp_end":[0.49805,0.14125,0.05826],"tcp_start":[0.49792,0.14096,0.05873],"tcp_to_object_dist_end":0.03507,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.03846,"average_solve_count":26.0,"average_success_count":26.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.12328,"push_1.force_limit":21.71878,"push_1.max_time":4.91967,"push_1.push_distance":0.15812,"push_1.push_speed":0.02539,"retract_1.retract_height":0.1268,"retract_1.retract_speed":0.09995},"optimized_scores":{"best_composite_score":-0.25859,"best_fitness_score":0.12141,"best_task_score":0.00076},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":1.0,"contact_point_centroid":[0.47488,0.08239,0.0591],"force_p95":678.49949,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":678.49949,"mean_force":678.49949,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48008,0.09309,0.05757]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":6.0,"contact_point_centroid":[0.47493,0.0826,0.05948],"force_p95":493.24809,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":505.71345,"mean_force":367.42221,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47988,0.09343,0.05836]},{"body_a":"peg","body_b":"channel_base_body","contact_count":426.0,"contact_point_centroid":[0.49542,0.06399,0.00936],"force_p95":0.60216,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56548,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48888,0.14366,0.17116]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49935,0.19762,0.29482]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.48443,0.04938,0.00939],"force_p95":0.54675,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54675,"mean_force":0.54675,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48008,0.09309,0.05757]}],"total_contact_groups":5},"final_pose_error":0.04447,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49503,0.06369,0.03394],"final_tcp_position":[0.48021,0.0931,0.05752],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":678.49949,"phases":[{"contact_detected":true,"contact_event_count":2.0,"n_steps":453.0,"n_steps_budget":750.0,"object_pos_end":[0.49497,0.06372,0.03393],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14393,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":505.71345,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":460.0,"raw_peak_contact_force":505.71345,"subtask_id":"approach_peg","tcp_end":[0.48008,0.09309,0.05757],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.04053,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.49503,0.06369,0.03394],"object_pos_start":[0.49497,0.06372,0.03393],"object_to_goal_dist_end":0.1439,"object_to_goal_dist_start":0.14393,"object_z_max":0.03393,"peak_contact_force":678.49949,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":678.49949,"subtask_id":"insert_peg","tcp_end":[0.48021,0.0931,0.05752],"tcp_start":[0.48008,0.09309,0.05757],"tcp_to_object_dist_end":0.04051,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```