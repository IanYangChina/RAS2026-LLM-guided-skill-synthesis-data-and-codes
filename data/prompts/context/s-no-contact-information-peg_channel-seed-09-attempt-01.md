## Search State

- **Seed**: 9
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → descend → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | time_limit | 9 | -0.4463 | 0.00 | ❌ rejected |
| 0 | rotate → pull → push → descend → descend → grasp | arc_cartesian | arc_cartesian | impedance_motion | linear_cartesian | linear_cartesian | — | impedance_control | impedance_control | position_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | contact_detected | grasp_success | 5 | -0.2578 | 0.06 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`
- Frozen object start: [0.5296199363176067, 0.06294537672700443, 0.04]
- Frozen task target: [0.5296199363176067, -0.09705462327299558, 0.04]
- Goal object position: (0.5296199363176067, -0.09705462327299558, 0.04)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5296199363176067, 0.06294537672700443, 0.04)
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
  frozen_object_start: [0.5296, 0.0629, 0.04]
  frozen_task_target: [0.5296, -0.0971, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5296199363176067, 0.06294537672700443, 0.04]}
  frozen_targets: {'channel_exit': [0.5296199363176067, -0.09705462327299558, 0.04]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9

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
| `object` | offset from object initial position (0.5296199363176067, 0.06294537672700443, 0.04) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5296199363176067, -0.09705462327299558, 0.04) | final destination targets |
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

## Current Skill (Q=-0.446) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: rotate_1
  type: rotate
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
- id: pull_1
  type: pull
  generator: arc_cartesian
  control: impedance_control
  termination: time_limit
  parameters:
    pull_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
- id: push_1
  type: push
  generator: impedance_motion
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
- id: descend_2
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: contact_detected
- id: grasp_1
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  parameters:
    grip_force:
      type: scalar
      range:
      - 5.0
      - 30.0

```

## Design Metrics

- **Composite score**: -0.446
- **task_score** (E): 0.000
- **fitness_score**: 0.034  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_above | 1.00 | 0.1883 |
| descend_to_contact | 1.00 | 0.0942 |
| push_channel | 0.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_above | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.510, 0.097, 0.147) | (0.512, 0.067, 0.040)→(0.502, 0.067, 0.034) | 0.150→0.147 |
| descend_to_contact | descend | 1.00 / step_budget | (0.510, 0.097, 0.147)→(0.499, 0.124, 0.059) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 |
| push_channel | push | 0.00 / guard_failure | (0.499, 0.124, 0.059)→(0.499, 0.124, 0.059) | (0.502, 0.067, 0.034)→(0.502, 0.067, 0.034) | 0.147→0.147 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- terminal_score: 0.000
- phase_score: 0.059
- phase_breakdown.approach_peg_score: 0.197
- phase_breakdown.insertion_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.035
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.447
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.318


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `bf8103833c1e96f48e87b3ce39b3b3bf17e268470bd7b5c037546fb78b5150b8`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `98954a34ee744fa939070f7dadee8a411de43cdcfeddcf3b4bfc5c3a4c536020`; realized-scene SHA-256: `a0d7ea14565b0a67e86de15fa43f3773b761884db645527685cd53e0fd95aeb9`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.52962,0.06295,0.04]},{"name":"goal","value":[0.52962,-0.09705,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.52962,0.06295,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.52962,-0.09705,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.45263,"average_solve_count":95.0,"average_success_count":95.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_behind":0.03183,"approach_above.approach_height":0.11512,"approach_above.approach_speed":0.17899,"approach_above.arc_height":0.08771,"descend_to_contact.descend_speed":0.03895,"push_channel.push_distance":0.20202,"push_channel.push_duration":5.81224,"push_channel.push_force_limit":28.71483,"push_channel.push_speed":0.06322},"optimized_scores":{"best_composite_score":-0.4466,"best_fitness_score":0.0334,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":299.0,"contact_point_centroid":[0.50909,0.17618,-8e-05],"force_p95":187.66715,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":220.48839,"mean_force":161.76109,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50619,0.11676,0.05689]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.50942,0.17608,-6e-05],"force_p95":71.17661,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":71.17661,"mean_force":71.17661,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50496,0.11919,0.05939]},{"body_a":"peg","body_b":"channel_base_body","contact_count":603.0,"contact_point_centroid":[0.50577,0.06293,0.00936],"force_p95":0.56285,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.88411,"mean_force":0.569,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.5209,0.1101,0.25268]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":34.0,"contact_point_centroid":[0.53102,0.06295,0.03156],"force_p95":1.1362,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.98455,"mean_force":0.48262,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50292,0.21963,0.28911]},{"body_a":"peg","body_b":"channel_base_body","contact_count":932.0,"contact_point_centroid":[0.50596,0.06304,0.00938],"force_p95":0.55234,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55532,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51411,0.10426,0.09061]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.52214,0.0709,0.00939],"force_p95":0.54251,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54251,"mean_force":0.54251,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50496,0.11919,0.05939]}],"total_contact_groups":6},"final_pose_error":0.202,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50605,0.06298,0.03383],"final_tcp_position":[0.50498,0.1192,0.05937],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.52962,0.06295,0.04]},"phases":[{"n_steps":631.0,"n_steps_budget":660.0,"object_pos_end":[0.50593,0.063,0.03381],"object_pos_start":[0.52962,0.06295,0.04],"object_to_goal_dist_end":0.14325,"object_to_goal_dist_start":0.14598,"object_z_max":0.04001,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.53015,0.08413,0.16275],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.13289,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":932.0,"n_steps_budget":1000.0,"object_pos_end":[0.50605,0.06301,0.03383],"object_pos_start":[0.50593,0.063,0.03381],"object_to_goal_dist_end":0.14328,"object_to_goal_dist_start":0.14325,"object_z_max":0.03382,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_peg","tcp_end":[0.50496,0.11919,0.05939],"tcp_start":[0.53015,0.08413,0.16275],"tcp_to_object_dist_end":0.06172,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50605,0.06298,0.03383],"object_pos_start":[0.50605,0.06301,0.03383],"object_to_goal_dist_end":0.14324,"object_to_goal_dist_start":0.14328,"object_z_max":0.03383,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"insertion","tcp_end":[0.50498,0.1192,0.05937],"tcp_start":[0.50496,0.11919,0.05939],"tcp_to_object_dist_end":0.06177,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `cae0d95026bac46aa2e5d95cffd531753a79751757c4f25fa56c1ec6e19c2175`; realized-scene SHA-256: `11c1f773d01ee1d435c5ecc0d1531095d6f84a2c0ab26c3ff2560d4c62fcd41a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.53648,0.05661,0.04]},{"name":"goal","value":[0.53648,-0.10339,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.53648,0.05661,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.53648,-0.10339,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56122,"average_solve_count":98.0,"average_success_count":98.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_behind":0.03082,"approach_above.approach_height":0.08656,"approach_above.approach_speed":0.15906,"approach_above.arc_height":0.02644,"descend_to_contact.descend_speed":0.03217,"push_channel.push_distance":0.20816,"push_channel.push_duration":5.40302,"push_channel.push_force_limit":27.78722,"push_channel.push_speed":0.05957},"optimized_scores":{"best_composite_score":-0.44789,"best_fitness_score":0.03211,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link7","contact_count":339.0,"contact_point_centroid":[0.51137,0.17059,-8e-05],"force_p95":189.86246,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":213.99954,"mean_force":163.39081,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.50813,0.1111,0.0568]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.51165,0.17047,-6e-05],"force_p95":76.11952,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":76.11952,"mean_force":76.11952,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50692,0.1132,0.05901]},{"body_a":"peg","body_b":"channel_base_body","contact_count":602.0,"contact_point_centroid":[0.50586,0.05661,0.00935],"force_p95":0.60128,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":4.44541,"mean_force":0.57296,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.5153,0.13772,0.21827]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":37.0,"contact_point_centroid":[0.53251,0.05661,0.02607],"force_p95":1.30561,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.83578,"mean_force":0.52649,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50235,0.2214,0.28602]},{"body_a":"peg","body_b":"channel_base_body","contact_count":799.0,"contact_point_centroid":[0.50612,0.05662,0.00938],"force_p95":0.55201,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.56072,"mean_force":0.54651,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.51533,0.10332,0.07818]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1.0,"contact_point_centroid":[0.51188,0.0736,0.00939],"force_p95":0.54744,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54744,"mean_force":0.54744,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.50692,0.1132,0.05901]}],"total_contact_groups":6},"final_pose_error":0.20815,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50619,0.05667,0.03384],"final_tcp_position":[0.50693,0.11322,0.059],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.53648,0.05661,0.04]},"phases":[{"n_steps":631.0,"n_steps_budget":840.0,"object_pos_end":[0.50614,0.05665,0.03378],"object_pos_start":[0.53648,0.05661,0.04],"object_to_goal_dist_end":0.13693,"object_to_goal_dist_start":0.1414,"object_z_max":0.04001,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.53313,0.0888,0.13581],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11032,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":799.0,"n_steps_budget":1000.0,"object_pos_end":[0.50615,0.05669,0.03384],"object_pos_start":[0.50614,0.05665,0.03378],"object_to_goal_dist_end":0.13697,"object_to_goal_dist_start":0.13693,"object_z_max":0.03384,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_peg","tcp_end":[0.50692,0.1132,0.05901],"tcp_start":[0.53313,0.0888,0.13581],"tcp_to_object_dist_end":0.06187,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50619,0.05667,0.03384],"object_pos_start":[0.50615,0.05669,0.03384],"object_to_goal_dist_end":0.13695,"object_to_goal_dist_start":0.13697,"object_z_max":0.03384,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"insertion","tcp_end":[0.50693,0.11322,0.059],"tcp_start":[0.50692,0.1132,0.05901],"tcp_to_object_dist_end":0.06189,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `fd7ada9a67242f1adcdb6e23860d1223cdc8a17daf859e94e1687ff0564d9575`; realized-scene SHA-256: `8df62a5afc1e0110114ab6e06b493b5783d0c746729f7f7f1f2cb046babeda91`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47029,0.07994,0.04]},{"name":"goal","value":[0.47029,-0.08006,0.04]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.54,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.47029,0.07994,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.47029,-0.08006,0.04]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.38983,"average_solve_count":59.0,"average_success_count":59.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above.approach_behind":0.04466,"approach_above.approach_height":0.09452,"approach_above.approach_speed":0.14373,"approach_above.arc_height":0.05135,"descend_to_contact.descend_speed":0.08248,"push_channel.push_distance":0.2008,"push_channel.push_duration":5.66147,"push_channel.push_force_limit":22.8181,"push_channel.push_speed":0.06373},"optimized_scores":{"best_composite_score":-0.44456,"best_fitness_score":0.03544,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":24.0,"contact_point_centroid":[0.49681,0.32564,-0.00022],"force_p95":498.28348,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":510.87247,"mean_force":358.62423,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.4834,0.13884,0.05984]},{"body_a":"world","body_b":"link7","contact_count":156.0,"contact_point_centroid":[0.48613,0.19525,-8e-05],"force_p95":266.42895,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":333.10297,"mean_force":183.6407,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.48374,0.13607,0.05714]},{"body_a":"world","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.48783,0.19608,-0.0],"force_p95":40.71713,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":40.71713,"mean_force":40.71713,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48426,0.13946,0.05983]},{"body_a":"peg","body_b":"channel_base_body","contact_count":600.0,"contact_point_centroid":[0.49404,0.07994,0.00937],"force_p95":0.58707,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.77147,"mean_force":0.56779,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.4692,0.13887,0.22369]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":35.0,"contact_point_centroid":[0.46907,0.07994,0.03235],"force_p95":1.18295,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95027,"mean_force":0.45938,"phase_index":0.0,"phase_name":"approach_above","phase_type":"approach","tcp_position_centroid":[0.50086,0.21963,0.28687]},{"body_a":"peg","body_b":"channel_base_body","contact_count":775.0,"contact_point_centroid":[0.4938,0.07994,0.00937],"force_p95":0.6194,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64007,"mean_force":0.54657,"phase_index":1.0,"phase_name":"descend_to_contact","phase_type":"descend","tcp_position_centroid":[0.47637,0.12766,0.08734]},{"body_a":"peg","body_b":"channel_base_body","contact_count":5.0,"contact_point_centroid":[0.50443,0.08325,0.00936],"force_p95":0.624,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63275,"mean_force":0.55539,"phase_index":2.0,"phase_name":"push_channel","phase_type":"push","tcp_position_centroid":[0.48424,0.1394,0.05988]}],"total_contact_groups":7},"final_pose_error":0.20064,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49386,0.07998,0.03378],"final_tcp_position":[0.48426,0.1395,0.0598],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.47029,0.07994,0.04]},"phases":[{"n_steps":628.0,"n_steps_budget":810.0,"object_pos_end":[0.49383,0.07995,0.03376],"object_pos_start":[0.47029,0.07994,0.04],"object_to_goal_dist_end":0.16019,"object_to_goal_dist_start":0.16268,"object_z_max":0.04001,"phase_name":"approach_above","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.46629,0.11869,0.14132],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11759,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":775.0,"n_steps_budget":870.0,"object_pos_end":[0.49381,0.07994,0.03378],"object_pos_start":[0.49383,0.07995,0.03376],"object_to_goal_dist_end":0.16018,"object_to_goal_dist_start":0.16019,"object_z_max":0.03379,"phase_name":"descend_to_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_peg","tcp_end":[0.48415,0.13934,0.05994],"tcp_start":[0.46629,0.11869,0.14132],"tcp_to_object_dist_end":0.06562,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.49386,0.07998,0.03378],"object_pos_start":[0.49381,0.07994,0.03378],"object_to_goal_dist_end":0.16022,"object_to_goal_dist_start":0.16018,"object_z_max":0.03378,"phase_name":"push_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"insertion","tcp_end":[0.48426,0.1395,0.0598],"tcp_start":[0.48415,0.13934,0.05994],"tcp_to_object_dist_end":0.06566,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```