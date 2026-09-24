## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1624 | 0.63 | ❌ rejected |
| 5 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.0674 | 0.00 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.0947 | 0.00 | ❌ rejected |
| 3 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.2184 | 0.00 | ❌ rejected |
| 2 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.0224 | 0.03 | ❌ rejected |

**Proposal policy**: task_score is 0.63 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.162) — your mutation base

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

- **Composite score**: 0.162
- **task_score** (E): 0.635
- **fitness_score**: 0.522  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2117 |
| descend_1 | 1.00 | 0.67 | 0.0655 |
| push_1 | 1.00 | 1.00 | 0.1360 |
| retract_1 | 0.67 | 1.00 | 0.0995 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.494, 0.115, 0.108) | (0.498, 0.080, 0.040)→(0.500, 0.080, 0.034) | 0.161→0.161 | 1.00 / 1.000 | 0.527 | 2.179 |
| descend_1 | descend | 1.00 / step_budget | (0.494, 0.115, 0.108)→(0.502, 0.097, 0.046) | (0.500, 0.080, 0.034)→(0.503, 0.051, 0.032) | 0.161→0.131 | 0.67 / 1.667 | 189.536 | 258.080 |
| push_1 | push | 1.00 / step_budget | (0.502, 0.097, 0.046)→(0.499, -0.038, 0.041) | (0.503, 0.051, 0.032)→(0.495, -0.046, 0.026) | 0.131→0.042 | 1.00 / 2.333 | 51.157 | 175.237 |
| retract_1 | retract | 0.67 / step_budget | (0.499, -0.038, 0.041)→(0.496, -0.038, 0.140) | (0.495, -0.046, 0.026)→(0.502, -0.036, 0.024) | 0.042→0.050 | 1.00 / 1.000 | 0.632 | 46.865 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.853
- alignment_error: None
- force_efficiency: 0.000
- terminal_score: 0.823
- phase_score: 0.644
- phase_breakdown.reach_pre_contact_score: 0.337
- phase_breakdown.reach_goal_score: 0.776

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.716
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.823
- **Median Q (composite search score)**: 0.106
- **K-run variance**: 0.0197
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.207


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41081,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06112,"descend_1.descend_speed":0.05975,"push_1.push_distance":0.16209,"push_1.push_speed":0.07543,"retract_1.retract_height":0.14292,"retract_1.retract_speed":0.06322},"optimized_scores":{"best_composite_score":0.35558,"best_fitness_score":0.71558,"best_task_score":0.82265},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_left_wall","contact_count":79.0,"contact_point_centroid":[0.52503,0.07826,0.05999],"force_p95":351.42353,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":363.12661,"mean_force":315.32388,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50674,0.07822,0.04825]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":123.0,"contact_point_centroid":[0.52502,-0.04142,0.05999],"force_p95":114.08988,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":191.87225,"mean_force":66.84906,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50369,-0.04122,0.04274]},{"body_a":"peg","body_b":"channel_base_body","contact_count":310.0,"contact_point_centroid":[0.50604,0.05654,0.00865],"force_p95":144.50195,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":163.83068,"mean_force":40.07947,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5045,0.08513,0.06921]},{"body_a":"attachment","body_b":"peg","contact_count":111.0,"contact_point_centroid":[0.51291,0.07326,0.05387],"force_p95":153.43812,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.19509,"mean_force":110.35964,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50489,0.08051,0.05553]},{"body_a":"attachment","body_b":"peg","contact_count":663.0,"contact_point_centroid":[0.50152,-0.02704,0.04327],"force_p95":115.22591,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.64246,"mean_force":37.80721,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50273,-0.01587,0.04264]},{"body_a":"peg","body_b":"channel_base_body","contact_count":320.0,"contact_point_centroid":[0.50605,-0.10145,0.03484],"force_p95":111.42185,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":129.52888,"mean_force":71.17019,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50332,-0.04573,0.04269]},{"body_a":"peg","body_b":"channel_base_body","contact_count":886.0,"contact_point_centroid":[0.4956,-0.04799,0.0095],"force_p95":12.24779,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":32.02388,"mean_force":4.44578,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50285,-0.00296,0.04287]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":305.0,"contact_point_centroid":[0.47491,-0.07836,0.02758],"force_p95":7.89527,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":17.37792,"mean_force":4.48144,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5031,-0.02373,0.04263]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49926,-0.0744,0.00816],"force_p95":0.69709,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.1353,"mean_force":0.61907,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49977,-0.06777,0.0943]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":13.0,"contact_point_centroid":[0.47497,-0.06925,0.02706],"force_p95":2.93966,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.95193,"mean_force":1.81149,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50078,-0.0683,0.04682]},{"body_a":"peg","body_b":"channel_base_body","contact_count":715.0,"contact_point_centroid":[0.50368,0.0616,0.00934],"force_p95":0.64161,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.55784,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50261,0.14736,0.19969]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":7.0,"contact_point_centroid":[0.47486,0.00564,0.04903],"force_p95":1.84642,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.95393,"mean_force":1.11341,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50679,0.07819,0.0483]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":15.0,"contact_point_centroid":[0.52517,0.03377,0.02859],"force_p95":1.15923,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.19811,"mean_force":0.71414,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.5065,0.07817,0.04788]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49967,0.19907,0.29869]},{"body_a":"peg","body_b":"channel_base_body","contact_count":207.0,"contact_point_centroid":[0.49873,-0.10004,0.03674],"force_p95":0.36256,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.44899,"mean_force":0.06053,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50015,-0.06792,0.08448]}],"total_contact_groups":15},"final_pose_error":0.03939,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50523,-0.07494,0.02414],"final_tcp_position":[0.49998,-0.06772,0.14632],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"peak_contact_force":363.12661,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":738.0,"n_steps_budget":1000.0,"object_pos_end":[0.50382,0.06158,0.03376],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"peak_contact_force":0.52214,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":734.0,"raw_peak_contact_force":2.17216,"subtask_id":"reach_pre_contact","tcp_end":[0.50683,0.09738,0.10684],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08143,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":342.0,"n_steps_budget":810.0,"object_pos_end":[0.5006,0.01415,0.02485],"object_pos_start":[0.50382,0.06158,0.03376],"object_to_goal_dist_end":0.09537,"object_to_goal_dist_start":0.14177,"object_z_max":0.0413,"peak_contact_force":341.4163,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":522.0,"raw_peak_contact_force":363.12661,"subtask_id":"reach_pre_contact","tcp_end":[0.50625,0.07815,0.04746],"tcp_start":[0.50683,0.09738,0.10684],"tcp_to_object_dist_end":0.06811,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":943.0,"n_steps_budget":1000.0,"object_pos_end":[0.49353,-0.07573,0.02721],"object_pos_start":[0.5006,0.01415,0.02485],"object_to_goal_dist_end":0.01496,"object_to_goal_dist_start":0.09537,"object_z_max":0.02992,"peak_contact_force":1.9707,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2297.0,"raw_peak_contact_force":191.87225,"subtask_id":"reach_goal","tcp_end":[0.50328,-0.06804,0.04266],"tcp_start":[0.50625,0.07815,0.04746],"tcp_to_object_dist_end":0.01982,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50523,-0.07494,0.02414],"object_pos_start":[0.49353,-0.07573,0.02721],"object_to_goal_dist_end":0.01745,"object_to_goal_dist_start":0.01496,"object_z_max":0.02721,"peak_contact_force":0.61913,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1220.0,"raw_peak_contact_force":3.1353,"tcp_end":[0.49998,-0.06772,0.14632],"tcp_start":[0.50328,-0.06804,0.04266],"tcp_to_object_dist_end":0.12251,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.33498,"average_solve_count":203.0,"average_success_count":203.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07266,"descend_1.descend_speed":0.07534,"push_1.push_distance":0.17672,"push_1.push_speed":0.04487,"retract_1.retract_height":0.16279,"retract_1.retract_speed":0.03734},"optimized_scores":{"best_composite_score":0.02566,"best_fitness_score":0.38566,"best_task_score":0.61168},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":307.0,"contact_point_centroid":[0.50656,0.11772,0.00838],"force_p95":217.61208,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":229.48162,"mean_force":74.30392,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49856,0.13879,0.0692]},{"body_a":"attachment","body_b":"peg","contact_count":157.0,"contact_point_centroid":[0.51095,0.13096,0.05115],"force_p95":223.77798,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":228.66145,"mean_force":145.2644,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50105,0.13538,0.05299]},{"body_a":"peg","body_b":"channel_base_body","contact_count":960.0,"contact_point_centroid":[0.49811,0.06321,0.00876],"force_p95":156.68495,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":177.56253,"mean_force":47.32133,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50589,0.08079,0.04658]},{"body_a":"attachment","body_b":"peg","contact_count":791.0,"contact_point_centroid":[0.50622,0.08725,0.04905],"force_p95":158.55185,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":177.055,"mean_force":63.43655,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50671,0.09683,0.04761]},{"body_a":"attachment","body_b":"channel_left_wall","contact_count":213.0,"contact_point_centroid":[0.52502,0.11085,0.05999],"force_p95":115.79982,"geom_a":"pusher_tip","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":120.72355,"mean_force":68.56535,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50916,0.11379,0.05138]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":540.0,"contact_point_centroid":[0.47422,0.06013,0.0374],"force_p95":50.72974,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.04213,"mean_force":21.17841,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50508,0.08219,0.04534]},{"body_a":"peg","body_b":"world","contact_count":15.0,"contact_point_centroid":[0.50418,0.12738,-7e-05],"force_p95":33.67611,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.68103,"mean_force":12.33691,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50574,0.13596,0.04719]},{"body_a":"peg","body_b":"world","contact_count":4.0,"contact_point_centroid":[0.50421,0.12738,-6e-05],"force_p95":15.75134,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.87096,"mean_force":8.80617,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50629,0.13613,0.04692]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50108,0.01794,0.00806],"force_p95":0.68491,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.87922,"mean_force":0.61468,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49853,0.00259,0.08795]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":4.0,"contact_point_centroid":[0.525,0.01801,0.02418],"force_p95":8.04378,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.39073,"mean_force":2.61726,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49856,0.00262,0.11574]},{"body_a":"peg","body_b":"channel_base_body","contact_count":602.0,"contact_point_centroid":[0.50092,0.11601,0.00938],"force_p95":0.60708,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.55698,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49795,0.17388,0.20214]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":4.0,"contact_point_centroid":[0.47498,0.04301,0.02419],"force_p95":0.41251,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41942,"mean_force":0.35398,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4994,0.00242,0.04607]}],"total_contact_groups":12},"final_pose_error":0.06983,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50583,0.01817,0.02416],"final_tcp_position":[0.4987,0.00263,0.13496],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"peak_contact_force":229.48162,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":618.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11607,0.03384],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19617,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"peak_contact_force":0.51814,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":602.0,"raw_peak_contact_force":1.92055,"subtask_id":"reach_pre_contact","tcp_end":[0.49754,0.14879,0.1087],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08177,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":307.0,"n_steps_budget":660.0,"object_pos_end":[0.50436,0.11659,0.02869],"object_pos_start":[0.50096,0.11607,0.03384],"object_to_goal_dist_end":0.19696,"object_to_goal_dist_start":0.19617,"object_z_max":0.03394,"peak_contact_force":227.19044,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":479.0,"raw_peak_contact_force":229.48162,"subtask_id":"reach_pre_contact","tcp_end":[0.5062,0.13608,0.04688],"tcp_start":[0.49754,0.14879,0.1087],"tcp_to_object_dist_end":0.02673,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49473,0.01805,0.02409],"object_pos_start":[0.50436,0.11659,0.02869],"object_to_goal_dist_end":0.09948,"object_to_goal_dist_start":0.19696,"object_z_max":0.04021,"peak_contact_force":0.72556,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2508.0,"raw_peak_contact_force":177.56253,"subtask_id":"reach_goal","tcp_end":[0.50209,0.00272,0.04191],"tcp_start":[0.5062,0.13608,0.04688],"tcp_to_object_dist_end":0.02463,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50583,0.01817,0.02416],"object_pos_start":[0.49473,0.01805,0.02409],"object_to_goal_dist_end":0.09961,"object_to_goal_dist_start":0.09948,"object_z_max":0.02436,"peak_contact_force":0.57992,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1008.0,"raw_peak_contact_force":9.87922,"tcp_end":[0.4987,0.00263,0.13496],"tcp_start":[0.50209,0.00272,0.04191],"tcp_to_object_dist_end":0.11211,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.2359,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.06005,"descend_1.descend_speed":0.05321,"push_1.push_distance":0.16221,"push_1.push_speed":0.07077,"retract_1.retract_height":0.14987,"retract_1.retract_speed":0.05997},"optimized_scores":{"best_composite_score":0.10609,"best_fitness_score":0.46609,"best_task_score":0.47051},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":307.0,"contact_point_centroid":[0.49862,0.06547,0.00874],"force_p95":165.1084,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":181.63161,"mean_force":45.6989,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48475,0.08824,0.07258]},{"body_a":"attachment","body_b":"peg","contact_count":118.0,"contact_point_centroid":[0.49971,0.07819,0.05375],"force_p95":167.94341,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":181.06528,"mean_force":117.54409,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49016,0.08273,0.05624]},{"body_a":"attachment","body_b":"peg","contact_count":364.0,"contact_point_centroid":[0.4933,-0.05496,0.04422],"force_p95":150.7702,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":156.27676,"mean_force":96.96319,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49004,-0.04471,0.03754]},{"body_a":"peg","body_b":"channel_base_body","contact_count":341.0,"contact_point_centroid":[0.49756,-0.10194,0.04275],"force_p95":150.32443,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":154.46334,"mean_force":102.42959,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4901,-0.04548,0.03752]},{"body_a":"peg","body_b":"channel_base_body","contact_count":345.0,"contact_point_centroid":[0.49215,-0.10099,0.04429],"force_p95":76.44212,"geom_a":"peg_geom","geom_b":"channel_end","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":127.57996,"mean_force":41.52972,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48854,-0.04422,0.05393]},{"body_a":"attachment","body_b":"peg","contact_count":340.0,"contact_point_centroid":[0.49036,-0.05494,0.05318],"force_p95":76.71702,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.37471,"mean_force":41.87685,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48855,-0.04416,0.05367]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":3.0,"contact_point_centroid":[0.53659,-0.0461,0.05999],"force_p95":114.11209,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":115.44974,"mean_force":97.39062,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49161,-0.04995,0.03728]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":204.0,"contact_point_centroid":[0.53538,-0.03247,0.05999],"force_p95":68.43908,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":70.1158,"mean_force":32.57127,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4903,-0.03482,0.03753]},{"body_a":"peg","body_b":"channel_base_body","contact_count":650.0,"contact_point_centroid":[0.49487,-0.05346,0.0082],"force_p95":0.86118,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.16424,"mean_force":0.79643,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48807,-0.04966,0.10481]},{"body_a":"peg","body_b":"channel_base_body","contact_count":866.0,"contact_point_centroid":[0.49954,-0.0731,0.00902],"force_p95":8.61134,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":15.66246,"mean_force":1.72983,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48956,-0.00277,0.03789]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":105.0,"contact_point_centroid":[0.47493,-0.04831,0.03733],"force_p95":6.56716,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.09151,"mean_force":0.90425,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.48835,-0.0441,0.05866]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":31.0,"contact_point_centroid":[0.52523,-0.04884,0.04364],"force_p95":6.53423,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.62113,"mean_force":1.05885,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48952,0.04379,0.03828]},{"body_a":"peg","body_b":"channel_base_body","contact_count":700.0,"contact_point_centroid":[0.49526,0.06389,0.00938],"force_p95":0.56539,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.55771,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48829,0.14836,0.19974]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":2.0,"contact_point_centroid":[0.47499,-0.09003,0.03076],"force_p95":1.33384,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34659,"mean_force":1.21911,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48918,0.03655,0.03789]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49929,0.19859,0.2975]}],"total_contact_groups":15},"final_pose_error":0.04828,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49437,-0.05093,0.02414],"final_tcp_position":[0.48829,-0.04975,0.13898],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"peak_contact_force":181.63161,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":727.0,"n_steps_budget":1000.0,"object_pos_end":[0.49511,0.06363,0.03398],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14384,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"peak_contact_force":0.54155,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":728.0,"raw_peak_contact_force":2.44546,"subtask_id":"reach_pre_contact","tcp_end":[0.47876,0.09978,0.10777],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":321.0,"n_steps_budget":960.0,"object_pos_end":[0.50328,0.02148,0.04283],"object_pos_start":[0.49511,0.06363,0.03398],"object_to_goal_dist_end":0.10158,"object_to_goal_dist_start":0.14384,"object_z_max":0.04301,"peak_contact_force":0.0,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":425.0,"raw_peak_contact_force":181.63161,"subtask_id":"reach_pre_contact","tcp_end":[0.49308,0.07803,0.04249],"tcp_start":[0.47876,0.09978,0.10777],"tcp_to_object_dist_end":0.05746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":958.0,"n_steps_budget":1000.0,"object_pos_end":[0.49692,-0.08103,0.02785],"object_pos_start":[0.50328,0.02148,0.04283],"object_to_goal_dist_end":0.01257,"object_to_goal_dist_start":0.10158,"object_z_max":0.04283,"peak_contact_force":150.77403,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1808.0,"raw_peak_contact_force":156.27676,"subtask_id":"reach_goal","tcp_end":[0.4916,-0.04998,0.03728],"tcp_start":[0.49308,0.07803,0.04249],"tcp_to_object_dist_end":0.03288,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49437,-0.05093,0.02414],"object_pos_start":[0.49692,-0.08103,0.02785],"object_to_goal_dist_end":0.0336,"object_to_goal_dist_start":0.01257,"object_z_max":0.04205,"peak_contact_force":0.69711,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1443.0,"raw_peak_contact_force":127.57996,"tcp_end":[0.48829,-0.04975,0.13898],"tcp_start":[0.4916,-0.04998,0.03728],"tcp_to_object_dist_end":0.11501,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```