## Search State

- **Seed**: 5
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 2 | 0.1402 | 0.00 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp → retract | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | impedance_control | admittance_control | position_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | pose_tolerance | 3 | -0.2993 | 0.00 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`
- Frozen object start: [0.5244002338996304, -0.05536473682108051, 0.04]
- Frozen task target: [0.5, 0.2, 0.3]
- Goal object position: (0.5, 0.2, 0.3)
- Task success criterion: peg must traverse the channel (0.16 m long) along axis (0.0, -1.0, 0.0); score = axial progress × lateral alignment — NOT a fixed TCP endpoint
- Object initial pose: (0.5244002338996304, -0.05536473682108051, 0.04)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.5
- Force limit: 40.0 N
- Peg body: `peg`
- Channel axis: `(0.0, -1.0, 0.0)` — use `impedance_control` to absorb lateral wall forces
- Robot initial TCP position: (0.5244002338996304, 0.1046352631789195, 0.04)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **insertion depth × lateral alignment (axial progress penalised by wall deviation)**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5244002338996304, 0.1046352631789195, 0.04]
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
  frozen_object_start: [0.5244, 0.1046, 0.04]
  frozen_task_target: [0.5244, -0.0554, 0.04]
  frozen_fixture_position: [0.54, 0, 0.035]
  frozen_object_starts: {'peg': [0.5244002338996304, -0.05536473682108051, 0.04]}
  frozen_targets: {'channel_exit': [0.5, 0.2, 0.3]}
  frozen_fixtures: {'channel_left_wall': [0.54, 0.0, 0.035], 'channel_right_wall': [0.46, 0.0, 0.035]}
  channel_axis: [0, -1, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 40
  channel_length_m: 0.16
  force_scale_n: 5
  realized_scene_sha256: ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e

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
| `object` | offset from object initial position (0.5244002338996304, -0.05536473682108051, 0.04) | approach/contact targets near object start |
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

## Current Skill (Q=0.140) — your mutation base

```yaml
skill: peg_channel
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: release_1
  type: release
  control: position_control
  termination: time_limit
  end_effector_action: open
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
- id: release_2
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: release_3
  type: release
  generator: linear_cartesian
  control: position_control
  termination: time_limit
  end_effector_action: open
- id: grasp_1
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.140
- **task_score** (E): 0.000
- **fitness_score**: 0.240  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.100

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 0.67 | 1.00 | 0.2123 |
| push_into_channel | 1.00 | 1.00 | 0.1603 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 0.67 / step_budget | (0.500, 0.200, 0.300)→(0.507, 0.130, 0.100) | (0.512, 0.095, 0.040)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.555 | 2.488 |
| push_into_channel | push | 1.00 / time_limit | (0.507, 0.130, 0.100)→(0.501, -0.020, 0.047) | (0.504, 0.095, 0.034)→(0.504, 0.095, 0.034) | 0.175→0.175 | 1.00 / 1.000 | 0.549 | 0.587 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.000
- alignment_error: None
- force_efficiency: 0.959
- terminal_score: 0.000
- phase_score: 0.476
- phase_breakdown.push_peg_score: 0.460
- phase_breakdown.approach_peg_score: 0.514

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.286
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: 0.135
- **K-run variance**: 0.0013
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 11.0
- **Parameters at upper bound**: push_into_channel.push_depth
- **Final σ (mean)**: 0.397


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `9b36d26f861d7a613dfb3d8c86d70470e42095a430c2befa4bd6e530468a8a7e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.04,0.04]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `2af86d8f59685db6584febc0596b9044223ae39cea3120c112c665a54a1c4732`; realized-scene SHA-256: `ca4f9624fc0e37438ffe7fd92236fc537e25f346e4aaef8c3b399c2f4b45089e`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5244,-0.05536,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,0.10464,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.5244,-0.05536,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02532,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push_into_channel.push_depth":0.18364,"push_into_channel.speed":0.09984},"optimized_scores":{"best_composite_score":0.13505,"best_fitness_score":0.23505,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":973.0,"contact_point_centroid":[0.50574,0.10468,0.00938],"force_p95":0.57571,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":3.33087,"mean_force":0.55797,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50738,0.16757,0.19505]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":32.0,"contact_point_centroid":[0.52975,0.10463,0.03425],"force_p95":1.06006,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.32726,"mean_force":0.42874,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49963,0.19894,0.29728]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50587,0.10463,0.00939],"force_p95":0.57567,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57575,"mean_force":0.54634,"phase_index":1.0,"phase_name":"push_into_channel","phase_type":"push","tcp_position_centroid":[0.50868,0.06566,0.07159]}],"total_contact_groups":3},"final_pose_error":0.04844,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50598,0.10467,0.03384],"final_tcp_position":[0.50448,-0.01191,0.04508],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.5244,0.10464,0.04]},"peak_contact_force":3.33087,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50599,0.10464,0.03384],"object_pos_start":[0.5244,0.10464,0.04],"object_to_goal_dist_end":0.18484,"object_to_goal_dist_start":0.18624,"object_z_max":0.04,"peak_contact_force":0.54104,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1005.0,"raw_peak_contact_force":3.33087,"subtask_id":"approach_peg","tcp_end":[0.51605,0.13824,0.10113],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.07589,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50598,0.10467,0.03384],"object_pos_start":[0.50599,0.10464,0.03384],"object_to_goal_dist_end":0.18487,"object_to_goal_dist_start":0.18484,"object_z_max":0.03384,"peak_contact_force":0.54955,"phase_name":"push_into_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.57575,"subtask_id":"push_peg","tcp_end":[0.50448,-0.01191,0.04508],"tcp_start":[0.51605,0.13824,0.10113],"tcp_to_object_dist_end":0.11712,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `314cefd2153cfe84bc0d0d2dfbeb7f4daf8feaf5f2c7ce7d396802b52a157f39`; realized-scene SHA-256: `07dc0764c781629358e2f97446117d9c410d14c078397be91277b4276116a1de`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50305,-0.09254,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,0.06746,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.50305,-0.09254,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.025,"average_solve_count":80.0,"average_success_count":80.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push_into_channel.push_depth":0.18733,"push_into_channel.speed":0.09981},"optimized_scores":{"best_composite_score":0.09963,"best_fitness_score":0.19963,"best_task_score":0.00026},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":984.0,"contact_point_centroid":[0.50307,0.06748,0.00936],"force_p95":0.55225,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06903,"mean_force":0.55539,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.49849,0.15445,0.20016]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50307,0.06744,0.00938],"force_p95":0.55056,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55071,"mean_force":0.54665,"phase_index":1.0,"phase_name":"push_into_channel","phase_type":"push","tcp_position_centroid":[0.4967,0.03919,0.07829]}],"total_contact_groups":2},"final_pose_error":0.06392,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50304,0.06742,0.0338],"final_tcp_position":[0.498,-0.03845,0.05064],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50305,0.06746,0.04]},"peak_contact_force":2.06903,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50308,0.06743,0.0338],"object_pos_start":[0.50305,0.06746,0.04],"object_to_goal_dist_end":0.14759,"object_to_goal_dist_start":0.14749,"object_z_max":0.04,"peak_contact_force":0.54571,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":984.0,"raw_peak_contact_force":2.06903,"subtask_id":"approach_peg","tcp_end":[0.49885,0.11169,0.10847],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.08691,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50304,0.06742,0.0338],"object_pos_start":[0.50308,0.06743,0.0338],"object_to_goal_dist_end":0.14758,"object_to_goal_dist_start":0.14759,"object_z_max":0.0338,"peak_contact_force":0.54781,"phase_name":"push_into_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.55071,"subtask_id":"push_peg","tcp_end":[0.498,-0.03845,0.05064],"tcp_start":[0.49885,0.11169,0.10847],"tcp_to_object_dist_end":0.10732,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `7acce370299b32aeef0e4239da3e97eae076cb9602edead185a6cf774ee0bc4e`; realized-scene SHA-256: `d0d8b50673ee8d816e4de306a6620129fbd254b61025859fc8d57d0983f18415`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51001,-0.04822,0.04]},{"name":"goal","value":[0.54,0.0,0.035]}],"axes":[{"name":"channel_axis","value":[0.0,-1.0,0.0]}],"fixture_states":[],"fixtures":[{"name":"channel_left_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.46,0.0,0.035]},{"name":"channel_right_wall","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,0.11178,0.04]}],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":40.0},{"name":"channel_length_m","value":0.16},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"peg","orientation":[1.0,0.0,0.0,0.0],"position":[0.51001,-0.04822,0.04]}],"obstacles":[],"targets":[{"name":"channel_exit","position":[0.54,0.0,0.035]}],"task_name":"peg_channel"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.02469,"average_solve_count":81.0,"average_success_count":81.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"push_into_channel.push_depth":0.2,"push_into_channel.speed":0.09987},"optimized_scores":{"best_composite_score":0.18578,"best_fitness_score":0.28578,"best_task_score":0.00038},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":978.0,"contact_point_centroid":[0.50364,0.11168,0.00938],"force_p95":0.61242,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.06328,"mean_force":0.55232,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50156,0.16933,0.19094]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50365,0.1117,0.0094],"force_p95":0.5953,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63543,"mean_force":0.54482,"phase_index":1.0,"phase_name":"push_into_channel","phase_type":"push","tcp_position_centroid":[0.50071,0.06762,0.06658]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":16.0,"contact_point_centroid":[0.52601,0.11178,0.02875],"force_p95":0.50724,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.54079,"mean_force":0.34334,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.4997,0.1994,0.29905]}],"total_contact_groups":3},"final_pose_error":0.05841,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50376,0.11171,0.0338],"final_tcp_position":[0.50011,-0.01099,0.04486],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51001,0.11178,0.04]},"peak_contact_force":2.06328,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50371,0.11177,0.03383],"object_pos_start":[0.51001,0.11178,0.04],"object_to_goal_dist_end":0.1919,"object_to_goal_dist_start":0.19204,"object_z_max":0.04,"peak_contact_force":0.57716,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":994.0,"raw_peak_contact_force":2.06328,"subtask_id":"approach_peg","tcp_end":[0.50477,0.14117,0.09152],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.06476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.11171,0.0338],"object_pos_start":[0.50371,0.11177,0.03383],"object_to_goal_dist_end":0.19185,"object_to_goal_dist_start":0.1919,"object_z_max":0.03394,"peak_contact_force":0.54922,"phase_name":"push_into_channel","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1000.0,"raw_peak_contact_force":0.63543,"subtask_id":"push_peg","tcp_end":[0.50011,-0.01099,0.04486],"tcp_start":[0.50477,0.14117,0.09152],"tcp_to_object_dist_end":0.12325,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```