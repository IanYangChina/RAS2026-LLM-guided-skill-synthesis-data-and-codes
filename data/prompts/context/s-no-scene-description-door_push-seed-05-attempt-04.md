## Search State

- **Seed**: 5
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.6700 | 1.00 | ❌ rejected |
| 3 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | -0.0520 | 0.33 | ❌ rejected |
| 2 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.7311 | 1.00 | ✅ accepted |
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 2 | -0.1000 | 0.00 | ❌ rejected |
| 0 | push → release → pull → release → release → grasp | linear_cartesian | — | arc_cartesian | linear_cartesian | linear_cartesian | — | position_control | position_control | impedance_control | admittance_control | position_control | position_control | time_limit | time_limit | time_limit | pose_tolerance | time_limit | time_limit | 2 | 0.0920 | 0.31 | ✅ accepted |

**Proposal policy**: task_score is near-perfect (1.00). Preserve useful working parts and make only evidence-backed refinements. A HOLD is acceptable if you genuinely cannot find a better structure.

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

## Current Skill (Q=0.670) — your mutation base

```yaml
skill: door_push
dsl_version: 2
subtasks:
- id: tcp_contact
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: hinge_progress
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.1
      - 1.0
      default: 0.5
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: approach_pose_guard
    when: after_phase
    predicate: pose_within_tolerance
    threshold: 0.02
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: tcp_contact
- id: contact_1
  type: descend
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    orientation:
      mode: keep_current
  parameters:
    contact_force_threshold:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 10.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: contact_force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: abort
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: task_goal_direction
      mode: add_to_offset
      sign: positive
    tolerance: 0.05
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_x
      tolerance: 0.1
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_pose_tol:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.02
      - 0.2
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: push_force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: reduce_speed
  subtask_id: hinge_progress

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=approach_pose_guard, when=after_phase, predicate=pose_within_tolerance, on_failure=retry, threshold=0.02
  - retries: max_attempts=1, strategy=reduce_speed
- **contact_1** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0]
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=contact_force_guard, when=during_phase, predicate=force_below, on_failure=abort, threshold=30.0
- **push_1** (`push`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=task_goal_direction, distance=0.2, mode=add_to_offset, sign=positive}, tolerance=0.05
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_x, tolerance=0.1
  - parameter_bindings:
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_pose_tol: status=consumed; consumers=termination.pose_tolerance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=push_force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=30.0
  - retries: max_attempts=2, strategy=reduce_speed

## Design Metrics

- **Composite score**: 0.670
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 0.00 | 0.67 | 0.3089 |
| descend_goal | 0.00 | 0.33 | 0.1732 |
| push_door | 0.00 | 0.67 | 0.0003 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 0.00 / step_budget | (-0.077, 0.273, 0.318)→(0.045, 0.135, 0.297) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 2.667 | 489.534 | 2314.636 |
| descend_goal | descend | 0.00 / step_budget | (0.054, 0.098, 0.286)→(0.139, 0.144, 0.331) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 0.333 | 39.715 | 1310.200 |
| push_door | push | 0.00 / guard_failure | (0.183, 0.141, 0.320)→(0.183, 0.141, 0.320) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 0.667 | 2.342 | 48.425 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.670
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.262


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `e036e59174e9f4dc4d090dc26b64c24f51b2862ad33098baa3e34b1ab5217b2c`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `121441f93055d9c3a0317d86ccf3c4d50a1368e9262fdd196bc29f47a537ab6f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":6.0,"average_failure_rate":0.05714,"average_mean_iterations":18.4,"average_solve_count":105.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15543,"approach_1.approach_speed":0.67346,"descend_goal.descend_speed":0.07344,"push_door.push_distance":0.39336,"push_door.push_pose_tol":0.04789,"push_door.push_speed":0.11521},"optimized_scores":{"best_composite_score":0.67,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link1","body_b":"link5","contact_count":110.0,"contact_point_centroid":[0.07464,0.07992,0.36781],"force_p95":4815.9684,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4904.73656,"mean_force":1837.2194,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.11788,0.27915,0.41493]},{"body_a":"door_panel","body_b":"link5","contact_count":279.0,"contact_point_centroid":[0.11231,0.10977,0.50089],"force_p95":2682.01401,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3343.94926,"mean_force":864.53779,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.03007,0.28559,0.41804]},{"body_a":"door_panel","body_b":"link6","contact_count":281.0,"contact_point_centroid":[0.13047,0.13448,0.42508],"force_p95":1359.48371,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2242.82986,"mean_force":657.43818,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.02997,0.28431,0.42009]},{"body_a":"link1","body_b":"link5","contact_count":1742.0,"contact_point_centroid":[0.10961,-0.00261,0.35299],"force_p95":1251.59436,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1852.05158,"mean_force":405.8957,"phase_index":1.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.23845,0.14051,0.31014]},{"body_a":"door_panel","body_b":"link5","contact_count":515.0,"contact_point_centroid":[0.14093,0.02535,0.43515],"force_p95":600.2116,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":701.99204,"mean_force":441.90242,"phase_index":1.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.16043,0.25718,0.39923]},{"body_a":"door_panel","body_b":"link6","contact_count":938.0,"contact_point_centroid":[0.26128,0.00627,0.34994],"force_p95":413.46078,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":633.9296,"mean_force":157.89122,"phase_index":1.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.2136,0.1809,0.33773]},{"body_a":"door_panel","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.29127,-0.14117,0.27198],"force_p95":41.65631,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.38368,"mean_force":21.83993,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.29148,-0.0148,0.24464]},{"body_a":"link1","body_b":"link5","contact_count":4.0,"contact_point_centroid":[0.10699,-0.06817,0.34133],"force_p95":0.51535,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.6063,"mean_force":0.15157,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.28754,-0.00957,0.24336]},{"body_a":"world","body_b":"door_panel","contact_count":972.0,"contact_point_centroid":[0.30292,0.16606,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.01298,0.28299,0.35794]},{"body_a":"world","body_b":"door_panel","contact_count":1352.0,"contact_point_centroid":[0.36508,0.06133,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.23069,0.15708,0.32084]},{"body_a":"world","body_b":"door_panel","contact_count":4.0,"contact_point_centroid":[0.40437,0.02406,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.29264,-0.01505,0.24496]}],"total_contact_groups":11},"final_pose_error":0.29865,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.29292,-0.01494,0.24507],"hinge_angle":1.02379,"initial_hinge_angle":0.10647,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.10647,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":4904.73656,"phases":[{"contact_detected":true,"contact_event_count":7.0,"n_steps":962.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":1040.72997,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1642.0,"raw_peak_contact_force":4904.73656,"subtask_id":"tcp_contact","tcp_end":[0.1247,0.28044,0.40007],"tcp_start":[-0.10079,0.26514,0.36215],"tcp_to_object_dist_end":0.50423,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1835.0,"n_steps_budget":990.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":119.14587,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":4547.0,"raw_peak_contact_force":1852.05158,"subtask_id":"goal_reach","tcp_end":[0.2877,-0.00862,0.24348],"tcp_start":[0.26087,0.10777,0.27774],"tcp_to_object_dist_end":0.377,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":16.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":13.0,"raw_peak_contact_force":45.38368,"subtask_id":"hinge_progress","tcp_end":[0.29292,-0.01494,0.24507],"tcp_start":[0.29264,-0.01505,0.24496],"tcp_to_object_dist_end":0.38221,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `fbf559b1c4ad02fb5807d56e72eb3a3daf90ab4647e10f958130a5b70ea34720`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":11.0,"average_failure_rate":0.09735,"average_mean_iterations":24.87611,"average_solve_count":113.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13713,"approach_1.approach_speed":0.54098,"descend_goal.descend_speed":0.05772,"push_door.push_distance":0.2769,"push_door.push_pose_tol":0.06095,"push_door.push_speed":0.13659},"optimized_scores":{"best_composite_score":0.67,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link5","contact_count":41.0,"contact_point_centroid":[0.10176,0.16035,0.54479],"force_p95":974.21421,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1022.63265,"mean_force":460.64118,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.04461,0.27257,0.29411]},{"body_a":"door_panel","body_b":"link6","contact_count":137.0,"contact_point_centroid":[0.10766,0.16813,0.36657],"force_p95":549.61795,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":779.84784,"mean_force":388.39969,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.02512,0.26596,0.30245]},{"body_a":"door_panel","body_b":"link6","contact_count":16.0,"contact_point_centroid":[0.23504,0.02695,0.51435],"force_p95":80.93906,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.29965,"mean_force":28.55273,"phase_index":1.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.15891,0.12787,0.38296]},{"body_a":"door_panel","body_b":"link6","contact_count":3.0,"contact_point_centroid":[0.28618,0.06136,0.50921],"force_p95":61.21702,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.73876,"mean_force":33.76245,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.22949,0.19139,0.3953]},{"body_a":"door_panel","body_b":"link7","contact_count":16.0,"contact_point_centroid":[0.11867,0.19309,0.2959],"force_p95":16.83086,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.74328,"mean_force":14.00516,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.056,0.25034,0.27364]},{"body_a":"world","body_b":"door_panel","contact_count":764.0,"contact_point_centroid":[0.30096,0.18263,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.00358,0.27708,0.29799]},{"body_a":"world","body_b":"door_panel","contact_count":972.0,"contact_point_centroid":[0.33971,0.07999,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[0.12124,0.1803,0.41112]},{"body_a":"world","body_b":"door_panel","contact_count":112.0,"contact_point_centroid":[0.33763,0.0828,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.16284,0.19428,0.41509]}],"total_contact_groups":8},"final_pose_error":0.15329,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.23063,0.19146,0.39443],"hinge_angle":0.57557,"initial_hinge_angle":0.01332,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.01332,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1022.63265,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":812.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":958.0,"raw_peak_contact_force":1022.63265,"subtask_id":"tcp_contact","tcp_end":[0.14611,0.15511,0.38398],"tcp_start":[-0.075,0.26135,0.24206],"tcp_to_object_dist_end":0.43915,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1213.0,"n_steps_budget":690.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":988.0,"raw_peak_contact_force":87.29965,"subtask_id":"goal_reach","tcp_end":[0.10494,0.19558,0.43139],"tcp_start":[0.1119,0.19049,0.41175],"tcp_to_object_dist_end":0.48514,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":141.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":7.02721,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":115.0,"raw_peak_contact_force":64.73876,"subtask_id":"hinge_progress","tcp_end":[0.23063,0.19146,0.39443],"tcp_start":[0.23024,0.1914,0.39495],"tcp_to_object_dist_end":0.4954,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `99847c10f6e36b39751f22a6e7e446b09a6cc2d5cdc4857751225dedfedfe952`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":5.0,"average_failure_rate":0.04902,"average_mean_iterations":16.70588,"average_solve_count":102.0,"average_success_count":97.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.10791,"approach_1.approach_speed":0.59252,"descend_goal.descend_speed":0.06151,"push_door.push_distance":0.2191,"push_door.push_pose_tol":0.04018,"push_door.push_speed":0.10409},"optimized_scores":{"best_composite_score":0.67,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link3","contact_count":5.0,"contact_point_centroid":[0.17861,-0.0372,0.55271],"force_p95":1966.02832,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1991.25006,"mean_force":1531.59242,"phase_index":1.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[-0.10581,0.23999,0.20622]},{"body_a":"link2","body_b":"link6","contact_count":1537.0,"contact_point_centroid":[-0.09148,0.03187,0.29949],"force_p95":456.90413,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1433.607,"mean_force":317.44607,"phase_index":1.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[-0.18184,0.01054,0.15886]},{"body_a":"door_panel","body_b":"link4","contact_count":566.0,"contact_point_centroid":[0.14169,0.11317,0.5994],"force_p95":909.88074,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1275.64448,"mean_force":529.83153,"phase_index":1.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[-0.17823,0.11914,0.19926]},{"body_a":"link2","body_b":"link6","contact_count":53.0,"contact_point_centroid":[-0.10714,-0.03478,0.33023],"force_p95":821.71624,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1016.53775,"mean_force":431.63159,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.19805,0.00741,0.18947]},{"body_a":"link0","body_b":"link7","contact_count":59.0,"contact_point_centroid":[-0.0705,0.02031,0.11711],"force_p95":227.16724,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":797.75883,"mean_force":141.41608,"phase_index":1.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[-0.13722,-0.03254,0.10895]},{"body_a":"link0","body_b":"link7","contact_count":4.0,"contact_point_centroid":[-0.07105,0.02093,0.11571],"force_p95":426.61735,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":427.87271,"mean_force":381.86586,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.13852,-0.03074,0.1078]},{"body_a":"door_panel","body_b":"link4","contact_count":2.0,"contact_point_centroid":[0.37162,-0.06658,0.39457],"force_p95":34.48633,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.15201,"mean_force":28.49523,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.02498,0.24571,0.31956]},{"body_a":"world","body_b":"door_panel","contact_count":916.0,"contact_point_centroid":[0.30061,0.18148,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[-0.04619,0.23622,0.31715]},{"body_a":"world","body_b":"door_panel","contact_count":1812.0,"contact_point_centroid":[0.31261,0.16004,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"descend_goal","phase_type":"descend","tcp_position_centroid":[-0.17195,0.02525,0.1691]}],"total_contact_groups":9},"final_pose_error":0.30265,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.02523,0.24567,0.31954],"hinge_angle":1.1232,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":1991.25006,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":992.0,"n_steps_budget":600.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":427.87271,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":973.0,"raw_peak_contact_force":1016.53775,"subtask_id":"tcp_contact","tcp_end":[-0.13638,-0.03146,0.10677],"tcp_start":[-0.05412,0.29277,0.35101],"tcp_to_object_dist_end":0.17603,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1951.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"descend_goal","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3979.0,"raw_peak_contact_force":1991.25006,"subtask_id":"goal_reach","tcp_end":[0.02484,0.24568,0.31956],"tcp_start":[-0.20927,-0.00465,0.1699],"tcp_to_object_dist_end":0.40385,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":5.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2.0,"raw_peak_contact_force":35.15201,"subtask_id":"hinge_progress","tcp_end":[0.02523,0.24567,0.31954],"tcp_start":[0.0252,0.24567,0.31955],"tcp_to_object_dist_end":0.40385,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```