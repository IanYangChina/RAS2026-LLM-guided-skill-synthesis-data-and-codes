## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.1346 | 0.04 | ❌ rejected |
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 8 | 0.1116 | 0.48 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 5 | -0.2476 | 0.00 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | force_exceeded | 4 | 0.1604 | 0.10 | ❌ rejected |
| 1 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2176 | 0.78 | ✅ accepted |

**Proposal policy**: task_score is 0.04 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.135) — your mutation base

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

- **Composite score**: -0.135
- **task_score** (E): 0.037
- **fitness_score**: 0.095  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1817 |
| descend_1 | 1.00 | 0.0775 |
| push_1 | 0.00 | 0.0473 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, 0.200, 0.300)→(0.495, 0.094, 0.154) | (0.498, 0.080, 0.040)→(0.500, 0.081, 0.034) | 0.161→0.161 |
| descend_1 | descend | 1.00 / step_budget | (0.495, 0.094, 0.154)→(0.496, 0.083, 0.078) | (0.500, 0.081, 0.034)→(0.500, 0.081, 0.034) | 0.161→0.161 |
| push_1 | push | 0.00 / step_budget | (0.496, 0.083, 0.078)→(0.517, 0.044, 0.089) | (0.500, 0.081, 0.034)→(0.495, 0.073, 0.035) | 0.161→0.154 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- insertion_depth_ratio: 0.049
- alignment_error: None
- terminal_score: 0.034
- phase_score: 0.146
- phase_breakdown.approach_peg_score: 0.281
- phase_breakdown.push_through_channel_score: 0.089

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.101
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.072
- **Median Q (composite search score)**: -0.134
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.356


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.74419,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0833,"descend_1.descend_speed":0.01684,"push_1.push_distance":0.17172,"push_1.push_speed":0.02339},"optimized_scores":{"best_composite_score":-0.14116,"best_fitness_score":0.08884,"best_task_score":0.00453},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":948.0,"contact_point_centroid":[0.52527,0.08563,0.05988],"force_p95":406.98283,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":645.66005,"mean_force":353.39239,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5195,0.02567,0.09822]},{"body_a":"attachment","body_b":"peg","contact_count":49.0,"contact_point_centroid":[0.50268,0.05193,0.04773],"force_p95":429.95882,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":469.68006,"mean_force":189.76417,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49617,0.04612,0.05166]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.49588,0.05361,0.00939],"force_p95":11.08643,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":468.73619,"mean_force":10.09236,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51854,0.02673,0.09652]},{"body_a":"peg","body_b":"world","contact_count":22.0,"contact_point_centroid":[0.49895,0.05102,-0.00163],"force_p95":101.89556,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":105.21504,"mean_force":15.66054,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49377,0.04723,0.04583]},{"body_a":"peg","body_b":"link7","contact_count":455.0,"contact_point_centroid":[0.50201,0.07855,0.05987],"force_p95":8.82662,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.21426,"mean_force":1.44662,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52314,0.02402,0.10103]},{"body_a":"peg","body_b":"channel_base_body","contact_count":363.0,"contact_point_centroid":[0.50359,0.06163,0.00933],"force_p95":0.60276,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.17216,"mean_force":0.56874,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.503,0.13573,0.22195]},{"body_a":"peg","body_b":"channel_left_wall","contact_count":19.0,"contact_point_centroid":[0.52623,0.06158,0.03217],"force_p95":0.5921,"geom_a":"peg_geom","geom_b":"channel_left_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.62339,"mean_force":0.34148,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49973,0.19834,0.29816]},{"body_a":"peg","body_b":"channel_base_body","contact_count":205.0,"contact_point_centroid":[0.50372,0.06144,0.00938],"force_p95":0.55611,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.5737,"mean_force":0.54664,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.50334,0.07052,0.11703]}],"total_contact_groups":8},"final_pose_error":0.28352,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49679,0.06044,0.03511],"final_tcp_position":[0.52535,0.024,0.10094],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.51096,0.06158,0.04]},"phases":[{"n_steps":386.0,"n_steps_budget":1000.0,"object_pos_end":[0.50376,0.06157,0.03378],"object_pos_start":[0.51096,0.06158,0.04],"object_to_goal_dist_end":0.14176,"object_to_goal_dist_start":0.14201,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.50703,0.07637,0.15259],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.11978,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.50374,0.06158,0.03378],"object_pos_start":[0.50376,0.06157,0.03378],"object_to_goal_dist_end":0.14177,"object_to_goal_dist_start":0.14176,"object_z_max":0.03378,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_peg","tcp_end":[0.50099,0.06429,0.07807],"tcp_start":[0.50703,0.07637,0.15259],"tcp_to_object_dist_end":0.04445,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49679,0.06044,0.03511],"object_pos_start":[0.50374,0.06158,0.03378],"object_to_goal_dist_end":0.14056,"object_to_goal_dist_start":0.14177,"object_z_max":0.03538,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through_channel","tcp_end":[0.52535,0.024,0.10094],"tcp_start":[0.50099,0.06429,0.07807],"tcp_to_object_dist_end":0.08048,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42105,"average_solve_count":133.0,"average_success_count":133.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.09078,"descend_1.descend_speed":0.06727,"push_1.push_distance":0.05136,"push_1.push_speed":0.02819},"optimized_scores":{"best_composite_score":-0.13399,"best_fitness_score":0.09601,"best_task_score":0.0721},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"peg","contact_count":544.0,"contact_point_centroid":[0.50568,0.09611,0.05708],"force_p95":272.86319,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":454.08699,"mean_force":54.05442,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50591,0.08446,0.06685]},{"body_a":"peg","body_b":"channel_base_body","contact_count":998.0,"contact_point_centroid":[0.50298,0.09321,0.00931],"force_p95":218.07666,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":453.66359,"mean_force":32.54223,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50611,0.0829,0.06952]},{"body_a":"channel_right_wall","body_b":"link7","contact_count":828.0,"contact_point_centroid":[0.47497,0.11995,0.05999],"force_p95":268.35334,"geom_a":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":277.83262,"mean_force":256.54727,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50814,0.08093,0.07172]},{"body_a":"channel_left_wall","body_b":"link7","contact_count":89.0,"contact_point_centroid":[0.52705,0.11966,0.05991],"force_p95":222.77408,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":226.00288,"mean_force":171.82935,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49801,0.07942,0.06657]},{"body_a":"peg","body_b":"link7","contact_count":723.0,"contact_point_centroid":[0.4933,0.12093,0.05214],"force_p95":49.46631,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":138.41745,"mean_force":7.33638,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50617,0.08043,0.07141]},{"body_a":"peg","body_b":"world","contact_count":51.0,"contact_point_centroid":[0.49104,0.11198,-0.00202],"force_p95":92.13764,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":126.25109,"mean_force":32.96986,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49336,0.1029,0.04728]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":112.0,"contact_point_centroid":[0.47469,0.11417,0.02759],"force_p95":63.7793,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.70212,"mean_force":27.00727,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4951,0.0861,0.06078]},{"body_a":"peg","body_b":"channel_base_body","contact_count":296.0,"contact_point_centroid":[0.50101,0.11604,0.00933],"force_p95":0.6953,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.92055,"mean_force":0.57215,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49854,0.1625,0.22565]},{"body_a":"peg","body_b":"channel_base_body","contact_count":194.0,"contact_point_centroid":[0.50109,0.11615,0.0094],"force_p95":0.61518,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.64195,"mean_force":0.54434,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49687,0.12197,0.11769]}],"total_contact_groups":9},"final_pose_error":0.21676,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.4951,0.104,0.03508],"final_tcp_position":[0.51192,0.08303,0.06962],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.50095,0.11604,0.04]},"phases":[{"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.50097,0.11613,0.03389],"object_pos_start":[0.50095,0.11604,0.04],"object_to_goal_dist_end":0.19622,"object_to_goal_dist_start":0.19604,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.49823,0.12669,0.15667],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12326,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":194.0,"n_steps_budget":870.0,"object_pos_end":[0.5009,0.11605,0.03381],"object_pos_start":[0.50097,0.11613,0.03389],"object_to_goal_dist_end":0.19615,"object_to_goal_dist_start":0.19622,"object_z_max":0.03393,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_peg","tcp_end":[0.49703,0.11752,0.07808],"tcp_start":[0.49823,0.12669,0.15667],"tcp_to_object_dist_end":0.04446,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4951,0.104,0.03508],"object_pos_start":[0.5009,0.11605,0.03381],"object_to_goal_dist_end":0.18413,"object_to_goal_dist_start":0.19615,"object_z_max":0.03644,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through_channel","tcp_end":[0.51192,0.08303,0.06962],"tcp_start":[0.49703,0.11752,0.07808],"tcp_to_object_dist_end":0.04377,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.54701,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.11681,"descend_1.descend_speed":0.07333,"push_1.push_distance":0.19569,"push_1.push_speed":0.05061},"optimized_scores":{"best_composite_score":-0.12856,"best_fitness_score":0.10144,"best_task_score":0.03389},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"channel_left_wall","body_b":"link7","contact_count":943.0,"contact_point_centroid":[0.52511,0.08416,0.05989],"force_p95":427.72828,"geom_a":"channel_left_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1120.40663,"mean_force":354.21174,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50863,0.02928,0.09333]},{"body_a":"attachment","body_b":"channel_right_wall","contact_count":8.0,"contact_point_centroid":[0.47475,0.05586,0.0502],"force_p95":657.71606,"geom_a":"pusher_tip","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":691.48807,"mean_force":323.93666,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48505,0.0541,0.04477]},{"body_a":"attachment","body_b":"peg","contact_count":51.0,"contact_point_centroid":[0.49525,0.057,0.04827],"force_p95":383.17527,"geom_a":"pusher_tip","geom_b":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":404.27021,"mean_force":184.96988,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48832,0.05142,0.05235]},{"body_a":"peg","body_b":"channel_base_body","contact_count":1000.0,"contact_point_centroid":[0.4931,0.04578,0.00961],"force_p95":10.62788,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":403.89488,"mean_force":10.78562,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50763,0.03047,0.09168]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":183.0,"contact_point_centroid":[0.47496,0.06069,0.04976],"force_p95":24.72004,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.76044,"mean_force":4.18577,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5046,0.03308,0.08669]},{"body_a":"peg","body_b":"world","contact_count":20.0,"contact_point_centroid":[0.4955,0.05221,-0.00101],"force_p95":53.83374,"geom_a":"peg_geom","geom_b":"table","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":57.073,"mean_force":12.90856,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48663,0.0528,0.0461]},{"body_a":"peg","body_b":"link7","contact_count":799.0,"contact_point_centroid":[0.49553,0.07609,0.06064],"force_p95":5.95647,"geom_a":"peg_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.1032,"mean_force":1.34226,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51045,0.02806,0.09565]},{"body_a":"peg","body_b":"channel_base_body","contact_count":344.0,"contact_point_centroid":[0.49566,0.06406,0.00935],"force_p95":0.62772,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.44546,"mean_force":0.57014,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48917,0.13613,0.22136]},{"body_a":"peg","body_b":"channel_right_wall","contact_count":28.0,"contact_point_centroid":[0.47133,0.06388,0.03676],"force_p95":0.92436,"geom_a":"peg_geom","geom_b":"channel_right_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.16907,"mean_force":0.37063,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4991,0.19698,0.29622]},{"body_a":"peg","body_b":"channel_base_body","contact_count":198.0,"contact_point_centroid":[0.49522,0.06382,0.0094],"force_p95":0.54998,"geom_a":"peg_geom","geom_b":"channel_base","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.55112,"mean_force":0.54576,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48361,0.07246,0.11549]}],"total_contact_groups":10},"final_pose_error":0.30763,"key_states":{"actual_goal_position":[0.5,-0.08,0.04],"final_object_position":[0.49332,0.05603,0.03605],"final_tcp_position":[0.51444,0.02645,0.09602],"realised_goal_position":[0.5,-0.08,0.04],"realised_object_initial_position":[0.48093,0.06388,0.04]},"phases":[{"n_steps":371.0,"n_steps_budget":1000.0,"object_pos_end":[0.49491,0.0639,0.03392],"object_pos_start":[0.48093,0.06388,0.04],"object_to_goal_dist_end":0.14412,"object_to_goal_dist_start":0.14514,"object_z_max":0.04,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_peg","tcp_end":[0.48046,0.07864,0.15329],"tcp_start":[0.49981,0.19962,0.30031],"tcp_to_object_dist_end":0.12114,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":198.0,"n_steps_budget":810.0,"object_pos_end":[0.49492,0.06399,0.03394],"object_pos_start":[0.49491,0.0639,0.03392],"object_to_goal_dist_end":0.14421,"object_to_goal_dist_start":0.14412,"object_z_max":0.03394,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_peg","tcp_end":[0.48866,0.06637,0.07713],"tcp_start":[0.48046,0.07864,0.15329],"tcp_to_object_dist_end":0.0437,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49332,0.05603,0.03605],"object_pos_start":[0.49492,0.06399,0.03394],"object_to_goal_dist_end":0.13625,"object_to_goal_dist_start":0.14421,"object_z_max":0.03605,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_through_channel","tcp_end":[0.51444,0.02645,0.09602],"tcp_start":[0.48866,0.06637,0.07713],"tcp_to_object_dist_end":0.07013,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```