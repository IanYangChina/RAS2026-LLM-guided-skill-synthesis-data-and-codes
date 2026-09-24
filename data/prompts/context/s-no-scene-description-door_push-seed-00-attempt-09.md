## Search State

- **Seed**: 0
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | -0.1713 | 0.21 | ❌ rejected |
| 8 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.2161 | 0.47 | ❌ rejected |
| 7 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 5 | 0.5434 | 0.46 | ❌ rejected |
| 6 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.2532 | 0.50 | ❌ rejected |
| 5 | approach → push | arc_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | pose_tolerance | 7 | -0.0024 | 0.35 | ❌ rejected |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: door_push
- target_hinge_angle: 0.524 rad (task success = realised hinge-angle delta ratio; not TCP proximity)
- Goal tolerance: 0.05 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 30.0 N
- Primary evaluation target: **hinge angle delta ratio (realised hinge motion / target_hinge_angle)**

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
| `object` | offset from object initial position | approach/contact targets near object |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | approach/contact targets near fixture |

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

## Current Skill (Q=-0.171) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: pre_push_position
  offset:
  - 0.03
  - 0.0
  - 0.1
  weight: 0.3
- id: push_complete
  weight: 0.7
phases:
- id: approach_to_door
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.03
    - 0.0
    - 0.1
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.03
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_x_offset:
      type: scalar
      range:
      - -0.02
      - 0.08
      default: 0.03
      binds_to:
      - path: target.offset.x
        mode: replace
    speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.06
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: pre_push_position
- id: push_door_open
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: force_limit
    when: during_phase
    predicate: force_below
    threshold: 28.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: push_complete

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_door** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.03, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_x_offset: status=consumed; consumers=target.offset.x (replace)
    - speed: status=consumed; consumers=generator.speed (replace)
- **push_door_open** (`push`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=force_limit, when=during_phase, predicate=force_below, on_failure=retry, threshold=28.0
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: -0.171
- **task_score** (E): 0.209
- **fitness_score**: 0.209  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_over_handle | 1.00 | 0.67 | 0.2004 |
| descend_to_push | 1.00 | 1.00 | 0.1085 |
| push_door_open | 0.33 | 0.33 | 0.0329 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_over_handle | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.099, 0.237, 0.468) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 10.708 | 55.756 |
| descend_to_push | align | 1.00 / step_budget | (0.099, 0.237, 0.468)→(0.100, 0.230, 0.360) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 3.333 | 0.000 | 13.141 |
| push_door_open | push | 0.33 / guard_failure | (0.100, 0.230, 0.360)→(0.100, 0.262, 0.359) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 21.905 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.344
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.344
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.344
- **Median Q (composite search score)**: -0.199
- **K-run variance**: 0.0102
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.404


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `275c70960dc683bb9d0f514db4e615bd3a6644bf8e38d8dd2bfa731bf179f097`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `35996939e2e1630dea7cedb55906290b2cb0393492844f540c2c9d9496e5416e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42,"average_solve_count":150.0,"average_success_count":150.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_handle.approach_height":0.10085,"approach_over_handle.approach_y_offset":0.0228,"approach_over_handle.arc_height":0.11537,"approach_over_handle.speed":0.11973,"descend_to_push.descend_speed":0.0563,"push_door_open.push_distance":0.10822,"push_door_open.push_speed":0.03243},"optimized_scores":{"best_composite_score":-0.27865,"best_fitness_score":0.10135,"best_task_score":0.10135},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":66.0,"contact_point_centroid":[0.10113,0.17153,0.59334],"force_p95":43.42574,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":55.08604,"mean_force":18.21421,"phase_index":0.0,"phase_name":"approach_over_handle","phase_type":"approach","tcp_position_centroid":[0.09955,0.24146,0.48759]},{"body_a":"world","body_b":"door_panel","contact_count":948.0,"contact_point_centroid":[0.30075,0.18009,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_over_handle","phase_type":"approach","tcp_position_centroid":[0.09981,0.34154,0.46149]},{"body_a":"world","body_b":"door_panel","contact_count":472.0,"contact_point_centroid":[0.30214,0.16912,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"align","tcp_position_centroid":[0.0995,0.22669,0.41738]},{"body_a":"world","body_b":"door_panel","contact_count":556.0,"contact_point_centroid":[0.30207,0.16963,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.09938,0.27875,0.35785]}],"total_contact_groups":4},"final_pose_error":0.0099,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09924,0.32705,0.35749],"hinge_angle":0.10092,"initial_hinge_angle":0.04781,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04781,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":55.08604,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_over_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1014.0,"raw_peak_contact_force":55.08604,"subtask_id":"pre_push","tcp_end":[0.09953,0.2254,0.47632],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.53628,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":465.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":472.0,"raw_peak_contact_force":0.0,"subtask_id":"pre_push","tcp_end":[0.0997,0.22843,0.35986],"tcp_start":[0.09953,0.2254,0.47632],"tcp_to_object_dist_end":0.43775,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":583.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":556.0,"raw_peak_contact_force":0.0,"subtask_id":"push_door","tcp_end":[0.09924,0.32705,0.35749],"tcp_start":[0.0997,0.22843,0.35986],"tcp_to_object_dist_end":0.49458,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7a748efd829eb09daaf6b07ec36a2131763f35cca8c1f058f1a757467a8ce067`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.63542,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_handle.approach_height":0.10495,"approach_over_handle.approach_y_offset":0.04836,"approach_over_handle.arc_height":0.12992,"approach_over_handle.speed":0.11149,"descend_to_push.descend_speed":0.04135,"push_door_open.push_distance":0.27319,"push_door_open.push_speed":0.05755},"optimized_scores":{"best_composite_score":-0.1995,"best_fitness_score":0.1805,"best_task_score":0.1805},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":93.0,"contact_point_centroid":[0.10044,0.18494,0.57828],"force_p95":29.50527,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.95443,"mean_force":17.52973,"phase_index":0.0,"phase_name":"approach_over_handle","phase_type":"approach","tcp_position_centroid":[0.09955,0.25778,0.47156]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10191,0.16101,0.4657],"force_p95":33.63628,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.63628,"mean_force":33.63628,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.09969,0.23001,0.35977]},{"body_a":"door_panel","body_b":"link6","contact_count":48.0,"contact_point_centroid":[0.10153,0.16512,0.513],"force_p95":18.65799,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.56823,"mean_force":15.24725,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"align","tcp_position_centroid":[0.09948,0.23429,0.40705]},{"body_a":"world","body_b":"door_panel","contact_count":1112.0,"contact_point_centroid":[0.30012,0.1882,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_over_handle","phase_type":"approach","tcp_position_centroid":[0.09973,0.3473,0.4393]},{"body_a":"world","body_b":"door_panel","contact_count":424.0,"contact_point_centroid":[0.3016,0.17288,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"align","tcp_position_centroid":[0.09945,0.23498,0.41462]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30194,0.17047,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.09969,0.22994,0.35962]}],"total_contact_groups":6},"final_pose_error":0.27337,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09969,0.22983,0.35942],"hinge_angle":0.09871,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":49.95443,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":16.6261,"phase_name":"approach_over_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1205.0,"raw_peak_contact_force":49.95443,"subtask_id":"pre_push","tcp_end":[0.09951,0.23958,0.46186],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.52973,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":413.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":472.0,"raw_peak_contact_force":19.56823,"subtask_id":"pre_push","tcp_end":[0.09969,0.23001,0.35977],"tcp_start":[0.09951,0.23958,0.46186],"tcp_to_object_dist_end":0.4385,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":33.63628,"subtask_id":"push_door","tcp_end":[0.09969,0.22983,0.35942],"tcp_start":[0.09967,0.22989,0.3595],"tcp_to_object_dist_end":0.43811,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `8f682501979e58f93da2583f25150788eff90e19c055477d4547c33e5c9d7ff1`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.59236,"average_solve_count":157.0,"average_success_count":157.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_over_handle.approach_height":0.10988,"approach_over_handle.approach_y_offset":0.05776,"approach_over_handle.arc_height":0.08189,"approach_over_handle.speed":0.1189,"descend_to_push.descend_speed":0.01849,"push_door_open.push_distance":0.18365,"push_door_open.push_speed":0.0496},"optimized_scores":{"best_composite_score":-0.03579,"best_fitness_score":0.34421,"best_task_score":0.34421},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":191.0,"contact_point_centroid":[0.10048,0.20547,0.58856],"force_p95":26.78213,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.22779,"mean_force":16.62849,"phase_index":0.0,"phase_name":"approach_over_handle","phase_type":"approach","tcp_position_centroid":[0.09943,0.28145,0.48088]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.10185,0.16162,0.46569],"force_p95":32.0783,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.0783,"mean_force":32.0783,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.09964,0.2306,0.35976]},{"body_a":"door_panel","body_b":"link6","contact_count":63.0,"contact_point_centroid":[0.10129,0.1682,0.51564],"force_p95":19.47406,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":19.8553,"mean_force":16.46051,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"align","tcp_position_centroid":[0.09941,0.23785,0.40951]},{"body_a":"world","body_b":"door_panel","contact_count":1020.0,"contact_point_centroid":[0.29991,0.20326,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_over_handle","phase_type":"approach","tcp_position_centroid":[0.09972,0.35816,0.44156]},{"body_a":"world","body_b":"door_panel","contact_count":484.0,"contact_point_centroid":[0.30138,0.17459,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_to_push","phase_type":"align","tcp_position_centroid":[0.09939,0.23898,0.41723]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.30188,0.17086,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.09964,0.2306,0.35976]}],"total_contact_groups":6},"final_pose_error":0.18376,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.09961,0.2305,0.35952],"hinge_angle":0.09715,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":62.22779,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":954.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.49691,"phase_name":"approach_over_handle","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1211.0,"raw_peak_contact_force":62.22779,"subtask_id":"pre_push","tcp_end":[0.09945,0.24618,0.46511],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.53556,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":461.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_to_push","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":547.0,"raw_peak_contact_force":19.8553,"subtask_id":"pre_push","tcp_end":[0.09964,0.2306,0.35976],"tcp_start":[0.09945,0.24618,0.46511],"tcp_to_object_dist_end":0.43879,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":32.0783,"subtask_id":"push_door","tcp_end":[0.09961,0.2305,0.35952],"tcp_start":[0.09962,0.23053,0.35958],"tcp_to_object_dist_end":0.43853,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```