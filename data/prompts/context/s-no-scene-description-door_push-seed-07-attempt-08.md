## Search State

- **Seed**: 7
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 7 | 0.6200 | 1.00 | ✅ accepted |
| 7 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 6 | -0.1124 | 0.11 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 7 | -0.1690 | 0.10 | ❌ rejected |
| 5 | descend → push | linear_cartesian | linear_cartesian | position_control | impedance_control | contact_detected | pose_tolerance | 4 | 0.3304 | 0.20 | ❌ rejected |
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | -0.1966 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.620) — your mutation base

```yaml
skill: door_push
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_door
  anchor: object
  offset:
  - 0.0
  - -0.2
  - 0.15
  weight: 0.3
- id: push_open
  metric: goal_progress
  weight: 0.7
phases:
- id: approach_door
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: door_panel
    offset:
    - 0.0
    - -0.2
    - 0.15
    tolerance: 0.02
    orientation:
      mode: none
  parameters:
    app_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
    app_y:
      type: scalar
      range:
      - -0.35
      - -0.05
      default: -0.2
      binds_to:
      - path: target.offset.y
        mode: replace
  subtask_id: reach_door
- id: contact_door
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    entity: door_panel
    offset:
    - 0.0
    - -0.08
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    contact_force:
      type: scalar
      range:
      - 5.0
      - 30.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    contact_speed:
      type: scalar
      range:
      - 0.01
      - 0.08
      default: 0.03
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_door
- id: push_door
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: door_panel
    offset:
    - 0.0
    - -0.08
    - 0.1
    offset_along_axis:
      distance: 0.25
      axis: world_x
      mode: add_to_offset
      sign: positive
    tolerance: 0.03
    orientation:
      mode: keep_current
  parameters:
    force_limit:
      type: scalar
      range:
      - 30.0
      - 120.0
      default: 60.0
      binds_to:
      - path: guards.safe_force.threshold
        mode: replace
    push_dist:
      type: scalar
      range:
      - 0.05
      - 0.4
      default: 0.25
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.04
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: safe_force
    when: during_phase
    predicate: force_below
    threshold: 60.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.01
    - 0.0
  subtask_id: push_open

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_door** (`approach`)
  - target: source=yaml, anchor=task_object, entity=door_panel, offset=[0.0, -0.2, 0.15], tolerance=0.02
  - orientation: mode=none
  - parameter_bindings:
    - app_speed: status=consumed; consumers=generator.speed (replace)
    - app_y: status=consumed; consumers=target.offset.y (replace)
- **contact_door** (`contact`)
  - target: source=yaml, anchor=task_object, entity=door_panel, offset=[0.0, -0.08, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - contact_force: status=consumed; consumers=termination.force_threshold (replace)
    - contact_speed: status=consumed; consumers=generator.speed (replace)
- **push_door** (`push`)
  - target: source=yaml, anchor=task_object, entity=door_panel, offset=[0.0, -0.08, 0.1], offset_along_axis={axis=world_x, distance=0.25, mode=add_to_offset, sign=positive}, tolerance=0.03
  - orientation: mode=keep_current
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.safe_force.threshold (replace)
    - push_dist: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=safe_force, when=during_phase, predicate=force_below, on_failure=retry, threshold=60.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.01, 0.0]

## Design Metrics

- **Composite score**: 0.620
- **task_score** (E): 1.000
- **fitness_score**: 1.000  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.380

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_door | 0.00 | 0.33 | 0.3158 |
| contact_door | 0.00 | 0.33 | 0.0345 |
| push_door | 0.33 | 1.00 | 0.2211 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_door | approach | 0.00 / step_budget | (0.100, 0.399, 0.350)→(0.054, 0.102, 0.255) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 26.116 |
| contact_door | contact | 0.00 / step_budget | (0.054, 0.102, 0.255)→(0.048, 0.127, 0.232) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.33 / 1.333 | 0.000 | 0.000 |
| push_door | push | 0.33 / step_budget | (0.091, 0.100, 0.210)→(0.258, -0.022, 0.134) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 2.667 | 9.277 | 62.295 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.620
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.3
- **Final σ (mean)**: 0.387


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `2fa9c04e562df03eff32cc7f63abe386d265bbd85d42dcee2df7f90a42e2de0a`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `fb31b2d7951f101afe3533d0babe40d387e4396f53837e61e543f2cfc46b7e19`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.68056,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.app_speed":0.07367,"approach_door.app_y":-0.24475,"contact_door.contact_force":19.4472,"contact_door.contact_speed":0.02977,"push_door.force_limit":76.52592,"push_door.push_dist":0.18664,"push_door.push_speed":0.08658},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"link2","body_b":"link5","contact_count":10.0,"contact_point_centroid":[0.05089,0.10604,0.33079],"force_p95":80.74458,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":88.07558,"mean_force":31.36594,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.17923,0.04087,0.17513]},{"body_a":"door_panel","body_b":"link7","contact_count":452.0,"contact_point_centroid":[0.21007,0.06143,0.2544],"force_p95":27.9993,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.38451,"mean_force":16.6392,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.1445,0.09231,0.20427]},{"body_a":"door_panel","body_b":"link7","contact_count":461.0,"contact_point_centroid":[0.12225,0.10929,0.32379],"force_p95":18.29031,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.56151,"mean_force":12.34461,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.06046,0.14492,0.27343]},{"body_a":"world","body_b":"door_panel","contact_count":900.0,"contact_point_centroid":[0.30555,0.15778,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.07033,0.20847,0.29181]},{"body_a":"world","body_b":"door_panel","contact_count":1028.0,"contact_point_centroid":[0.31357,0.12691,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.05582,0.11146,0.25204]},{"body_a":"world","body_b":"door_panel","contact_count":812.0,"contact_point_centroid":[0.32106,0.11243,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.12389,0.10279,0.21362]}],"total_contact_groups":6},"final_pose_error":0.14207,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.17929,0.04047,0.17495],"hinge_angle":0.64374,"initial_hinge_angle":0.04367,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04367,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":88.07558,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1361.0,"raw_peak_contact_force":27.56151,"subtask_id":"reach_door","tcp_end":[0.05769,0.09962,0.26098],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.28524,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_door","tcp_end":[0.05272,0.12287,0.24125],"tcp_start":[0.05769,0.09962,0.26098],"tcp_to_object_dist_end":0.27582,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1274.0,"raw_peak_contact_force":88.07558,"subtask_id":"push_open","tcp_end":[0.17929,0.04047,0.17495],"tcp_start":[0.1793,0.04054,0.17495],"tcp_to_object_dist_end":0.25375,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `2fe1c8aab50c64fd16f940100e2036790f2ea8f75271c649e6989441e8f9191e`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.76991,"average_solve_count":226.0,"average_success_count":226.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.app_speed":0.07365,"approach_door.app_y":-0.11707,"contact_door.contact_force":15.57073,"contact_door.contact_speed":0.0288,"push_door.force_limit":61.40166,"push_door.push_dist":0.3446,"push_door.push_speed":0.05506},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":635.0,"contact_point_centroid":[0.23377,0.0451,0.21791],"force_p95":36.9649,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.79329,"mean_force":21.85233,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.15999,0.06815,0.1778]},{"body_a":"door_panel","body_b":"link7","contact_count":413.0,"contact_point_centroid":[0.11845,0.13663,0.30992],"force_p95":20.76969,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.81727,"mean_force":13.51782,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.05481,0.17176,0.26142]},{"body_a":"world","body_b":"door_panel","contact_count":1028.0,"contact_point_centroid":[0.30393,0.16992,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.06348,0.21606,0.27833]},{"body_a":"world","body_b":"door_panel","contact_count":976.0,"contact_point_centroid":[0.31005,0.13661,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.0395,0.12253,0.22786]},{"body_a":"world","body_b":"door_panel","contact_count":884.0,"contact_point_centroid":[0.33164,0.10248,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.13831,0.08422,0.18642]}],"total_contact_groups":5},"final_pose_error":0.06262,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.29565,-0.04492,0.11716],"hinge_angle":1.14464,"initial_hinge_angle":-0.0604,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.0604,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":50.79329,"phases":[{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1441.0,"raw_peak_contact_force":24.81727,"subtask_id":"reach_door","tcp_end":[0.04245,0.11208,0.23579],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.2645,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":976.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_door","tcp_end":[0.03486,0.13314,0.21727],"tcp_start":[0.04245,0.11208,0.23579],"tcp_to_object_dist_end":0.25719,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":27.83191,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1519.0,"raw_peak_contact_force":50.79329,"subtask_id":"push_open","tcp_end":[0.29565,-0.04492,0.11716],"tcp_start":[0.03486,0.13314,0.21727],"tcp_to_object_dist_end":0.32117,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `356d1c9659b48b76a1cff255b134bf18d0729848f67621b991467785bdaaef44`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.73973,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_door.app_speed":0.09015,"approach_door.app_y":-0.29261,"contact_door.contact_force":19.96959,"contact_door.contact_speed":0.05619,"push_door.force_limit":86.6935,"push_door.push_dist":0.32046,"push_door.push_speed":0.05291},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":448.0,"contact_point_centroid":[0.26284,0.01695,0.20764],"force_p95":40.67092,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.01538,"mean_force":26.75352,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.18564,0.04066,0.17857]},{"body_a":"door_panel","body_b":"link7","contact_count":398.0,"contact_point_centroid":[0.12464,0.09592,0.32544],"force_p95":16.80813,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":25.97024,"mean_force":12.41717,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.0619,0.1308,0.2764]},{"body_a":"world","body_b":"door_panel","contact_count":1100.0,"contact_point_centroid":[0.30695,0.14947,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_door","phase_type":"approach","tcp_position_centroid":[0.0728,0.20851,0.29648]},{"body_a":"world","body_b":"door_panel","contact_count":872.0,"contact_point_centroid":[0.31517,0.12295,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"contact_door","phase_type":"contact","tcp_position_centroid":[0.06143,0.10924,0.25676]},{"body_a":"world","body_b":"door_panel","contact_count":620.0,"contact_point_centroid":[0.34117,0.0883,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.15625,0.06576,0.19522]}],"total_contact_groups":5},"final_pose_error":0.02957,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.29905,-0.06211,0.10979],"hinge_angle":1.19041,"initial_hinge_angle":0.12924,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.12924,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":48.01538,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1498.0,"raw_peak_contact_force":25.97024,"subtask_id":"reach_door","tcp_end":[0.06311,0.09438,0.26869],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.2917,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"contact_door","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":872.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_door","tcp_end":[0.05742,0.12539,0.23871],"tcp_start":[0.06311,0.09438,0.26869],"tcp_to_object_dist_end":0.27569,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":772.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1068.0,"raw_peak_contact_force":48.01538,"subtask_id":"push_open","tcp_end":[0.29905,-0.06211,0.10979],"tcp_start":[0.05742,0.12539,0.23871],"tcp_to_object_dist_end":0.32456,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```