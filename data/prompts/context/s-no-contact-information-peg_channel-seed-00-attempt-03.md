## Search State

- **Seed**: 0
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | -0.2476 | 0.00 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 4 | 0.1604 | 0.10 | ❌ rejected |
| 1 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2176 | 0.78 | ✅ accepted |
| 0 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.1861 | 0.75 | ✅ accepted |

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

## Current Skill (Q=-0.248) — your mutation base

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

- **Composite score**: -0.248
- **task_score** (E): 0.001
- **fitness_score**: 0.032  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.2148 |
| descend_1 | 1.00 | 0.0989 |
| push_1 | 0.00 | 0.0537 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.047, 0.151) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 |
| descend_1 | descend | 1.00 / step_budget | (0.495, 0.047, 0.151)→(0.496, 0.034, 0.053) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 |
| push_1 | push | 0.00 / step_budget | (0.496, 0.034, 0.053)→(0.494, -0.018, 0.038) | (0.500, 0.081, 0.034)→(0.500, 0.080, 0.034) | 0.161→0.160 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.002
- alignment_error: None
- terminal_score: 0.001
- phase_score: 0.054
- phase_breakdown.approach_peg_score: 0.173
- phase_breakdown.push_through_channel_score: 0.004

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.033
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.248
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.274


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.87143,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05022,"descend_1.descend_speed":0.03354,"push_1.force_threshold":14.62848,"push_1.push_distance":0.1607,"push_1.push_speed":0.02559},"optimized_scores":{"best_composite_score":-0.24819,"best_fitness_score":0.03181,"best_task_score":0.00042},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":469.0,"contact_point_centroid":[0.50361,0.06161,0.00934],"force_p95":0.58924,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56349,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50302,0.11146,0.22076]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50379,0.0616,0.00938],"force_p95":0.56188,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.63077,"mean_force":0.54648,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49807,-0.00841,0.04482]},{"body_a":"peg","body_b":"channel_base_body","contact_count":204.0,"contact_point_centroid":[0.50373,0.06155,0.00938],"force_p95":0.58299,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62868,"mean_force":0.54674,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50376,0.02195,0.10328]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49965,0.19848,0.2987]}],"total_contact_groups":4},"final_pose_error":0.07038,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50376,0.06151,0.03382],"final_tcp_position":[0.49836,-0.02933,0.04105],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"phases":[{"n_steps":492.0,"n_steps_budget":1000.0,"object_pos_end":[0.50377,0.06158,0.03377],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.50725,0.02851,0.14972],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12063,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":204.0,"n_steps_budget":1000.0,"object_pos_end":[0.50373,0.06158,0.03378],"object_pos_start":[0.50377,0.06158,0.03377],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14177,"object_z_max":0.03378,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_peg","tcp_end":[0.50133,0.01496,0.05332],"tcp_start":[0.50725,0.02851,0.14972],"tcp_to_object_dist_end":0.05061,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.06151,0.03382],"object_pos_start":[0.50373,0.06158,0.03378],"object_to_goal_dist_end":0.14169,"object_to_goal_dist_start":0.14177,"object_z_max":0.03383,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through_channel","tcp_end":[0.49836,-0.02933,0.04105],"tcp_start":[0.50133,0.01496,0.05332],"tcp_to_object_dist_end":0.09128,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.96667,"average_solve_count":210.0,"average_success_count":210.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0417,"descend_1.descend_speed":0.03433,"push_1.force_threshold":24.98612,"push_1.push_distance":0.14354,"push_1.push_speed":0.04019},"optimized_scores":{"best_composite_score":-0.24766,"best_fitness_score":0.03234,"best_task_score":0.00065},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"peg","body_b":"channel_base_body","contact_count":381.0,"contact_point_centroid":[0.50094,0.11608,0.00936],"force_p95":0.62919,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.56521,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49846,0.13935,0.22396]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.50088,0.11599,0.00942],"force_p95":0.60746,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.66395,"mean_force":0.5423,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49483,0.03425,0.04206]},{"body_a":"peg","body_b":"channel_base_body","contact_count":211.0,"contact_point_centroid":[0.50106,0.11599,0.00943],"force_p95":0.5917,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62025,"mean_force":0.54201,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49705,0.07455,0.10484]}],"total_contact_groups":3},"final_pose_error":0.02959,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.50096,0.11593,0.03395],"final_tcp_position":[0.49589,0.00167,0.03528],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"phases":[{"n_steps":397.0,"n_steps_budget":1000.0,"object_pos_end":[0.50093,0.11608,0.03393],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19617,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.49825,0.08044,0.15299],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.1243,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":211.0,"n_steps_budget":1000.0,"object_pos_end":[0.50093,0.11608,0.03394],"object_pos_start":[0.50093,0.11608,0.03393],"object_to_goal_dist_end":0.19617,"object_to_goal_dist_start":0.19617,"object_z_max":0.03399,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_peg","tcp_end":[0.49727,0.06852,0.0534],"tcp_start":[0.49825,0.08044,0.15299],"tcp_to_object_dist_end":0.05151,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50096,0.11593,0.03395],"object_pos_start":[0.50093,0.11608,0.03394],"object_to_goal_dist_end":0.19603,"object_to_goal_dist_start":0.19617,"object_z_max":0.03399,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through_channel","tcp_end":[0.49589,0.00167,0.03528],"tcp_start":[0.49727,0.06852,0.0534],"tcp_to_object_dist_end":0.11439,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.85484,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05871,"descend_1.descend_speed":0.0389,"push_1.force_threshold":25.76251,"push_1.push_distance":0.12536,"push_1.push_speed":0.0253},"optimized_scores":{"best_composite_score":-0.24686,"best_fitness_score":0.03314,"best_task_score":0.00123},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"channel_right_wall","contact_count":193.0,"contact_point_centroid":[0.475,0.00849,0.04857],"force_p95":20.02483,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":25.79348,"mean_force":12.3579,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48685,0.00853,0.04673]},{"body_a":"peg","body_b":"channel_base_body","contact_count":454.0,"contact_point_centroid":[0.4955,0.06377,0.00936],"force_p95":0.59684,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.56424,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48899,0.11171,0.22024]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49921,0.19707,0.29713]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49496,0.06387,0.0094],"force_p95":0.55076,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55403,"mean_force":0.5452,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48737,-0.00551,0.04307]},{"body_a":"peg","body_b":"channel_base_body","contact_count":214.0,"contact_point_centroid":[0.49534,0.06422,0.0094],"force_p95":0.55044,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5516,"mean_force":0.54565,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48369,0.02403,0.10284]}],"total_contact_groups":5},"final_pose_error":0.0359,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49506,0.06357,0.03404],"final_tcp_position":[0.48856,-0.02618,0.03786],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":481.0,"n_steps_budget":1000.0,"object_pos_end":[0.49528,0.06393,0.03394],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14414,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.48009,0.0306,0.15016],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12186,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.495,0.06408,0.03397],"object_pos_start":[0.49528,0.06393,0.03394],"object_to_goal_dist_end":0.1443,"object_to_goal_dist_start":0.14414,"object_z_max":0.03397,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_peg","tcp_end":[0.48922,0.0171,0.05271],"tcp_start":[0.48009,0.0306,0.15016],"tcp_to_object_dist_end":0.05092,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49506,0.06357,0.03404],"object_pos_start":[0.495,0.06408,0.03397],"object_to_goal_dist_end":0.14378,"object_to_goal_dist_start":0.1443,"object_z_max":0.03404,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through_channel","tcp_end":[0.48856,-0.02618,0.03786],"tcp_start":[0.48922,0.0171,0.05271],"tcp_to_object_dist_end":0.09006,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```