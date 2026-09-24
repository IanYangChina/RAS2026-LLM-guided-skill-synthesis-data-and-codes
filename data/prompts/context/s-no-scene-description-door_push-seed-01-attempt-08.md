## Search State

- **Seed**: 1
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.6200 | 1.00 | ❌ rejected |
| 7 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.4322 | 0.81 | ❌ rejected |
| 6 | approach → align → push | arc_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | impedance_control | pose_tolerance | pose_tolerance | pose_tolerance | 7 | 0.6200 | 1.00 | ✅ accepted |
| 5 | rotate → align → push | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | position_control | time_limit | pose_tolerance | time_limit | 3 | 0.3605 | 0.54 | ❌ rejected |
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | force_exceeded | 4 | 0.4281 | 0.29 | ❌ rejected |

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
subtasks:
- id: reach_door
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: open_door
  target_entity: hinge
  metric: hinge_angle
  weight: 0.7
phases:
- id: approach
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_door
- id: align_contact
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
      default: 0.0
      binds_to:
      - path: target.offset.x
        mode: add
  subtask_id: reach_door
- id: push_door
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.3
      axis: world_y
      mode: add_to_offset
      sign: negative
    tolerance: 0.05
    orientation:
      mode: none
  parameters:
    force_limit:
      type: scalar
      range:
      - 10.0
      - 50.0
      default: 30.0
      binds_to:
      - path: guards.force_guard.threshold
        mode: replace
    hinge_threshold:
      type: scalar
      range:
      - 0.1
      - 0.524
      default: 0.524
      binds_to:
      - path: guards.push_guard.threshold
        mode: replace
    push_distance:
      type: scalar
      range:
      - 0.1
      - 0.5
      default: 0.3
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 30.0
    on_failure: continue
  - id: push_guard
    when: during_phase
    predicate: hinge_delta_reached
    threshold: 0.524
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - -0.02
    - 0.0
  subtask_id: open_door

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.1], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **align_contact** (`align`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lateral_offset_x: status=consumed; consumers=target.offset.x (add)
- **push_door** (`push`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_y, distance=0.3, mode=add_to_offset, sign=negative}, tolerance=0.05
  - orientation: mode=none
  - parameter_bindings:
    - force_limit: status=consumed; consumers=guards.force_guard.threshold (replace)
    - hinge_threshold: status=consumed; consumers=guards.push_guard.threshold (replace)
    - push_distance: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=continue, threshold=30.0
    - id=push_guard, when=during_phase, predicate=hinge_delta_reached, on_failure=retry, threshold=0.524
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, -0.02, 0.0]

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
| approach | 1.00 | 1.00 | 0.2214 |
| align_contact | 1.00 | 0.67 | 0.0892 |
| push_door | 0.00 | 1.00 | 0.1955 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.100, 0.200, 0.446) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 8.946 | 56.050 |
| align_contact | align | 1.00 / step_budget | (0.100, 0.200, 0.446)→(0.104, 0.181, 0.360) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.67 / 1.667 | 4.943 | 27.728 |
| push_door | push | 0.00 / guard_failure | (0.104, 0.181, 0.360)→(0.110, -0.014, 0.359) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 51.632 | 51.632 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 1.000
- arc_quality: 0.667

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 1.000
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.620
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.420


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `083132501f1ba139cf05fa7994a1ee954b157d46058e9396ba8b78c93b367725`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"hinge_delta_deg":10.0,"object_xy_delta":[0.0,0.0]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `a0caaf91521131af8da2ca1e0ce4fb631dc10b8d496fc3757eb1acd97f543da3`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.38235,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.lateral_offset_x":0.00553,"approach.approach_speed":0.18503,"push_door.force_limit":40.09645,"push_door.hinge_threshold":0.15868,"push_door.push_distance":0.24339,"push_door.push_speed":0.04502,"push_door.push_tolerance":0.05802},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":162.0,"contact_point_centroid":[0.10118,0.17355,0.54386],"force_p95":21.44961,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.38458,"mean_force":15.0583,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09975,0.2447,0.43754]},{"body_a":"door_panel","body_b":"link7","contact_count":101.0,"contact_point_centroid":[0.16643,0.05492,0.38915],"force_p95":37.74202,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.4466,"mean_force":31.28779,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10699,0.1169,0.36052]},{"body_a":"door_panel","body_b":"link7","contact_count":73.0,"contact_point_centroid":[0.1651,0.14476,0.46976],"force_p95":20.77645,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.49242,"mean_force":14.7829,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.0998,0.20213,0.44594]},{"body_a":"door_panel","body_b":"link7","contact_count":58.0,"contact_point_centroid":[0.16756,0.12789,0.42529],"force_p95":20.22926,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.96529,"mean_force":15.79757,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.10223,0.18527,0.40135]},{"body_a":"world","body_b":"door_panel","contact_count":860.0,"contact_point_centroid":[0.30072,0.18328,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09984,0.30376,0.40892]},{"body_a":"world","body_b":"door_panel","contact_count":304.0,"contact_point_centroid":[0.30657,0.14822,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.10189,0.18599,0.40744]},{"body_a":"world","body_b":"door_panel","contact_count":164.0,"contact_point_centroid":[0.32255,0.11003,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10722,0.11111,0.36058]}],"total_contact_groups":7},"final_pose_error":0.10213,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10973,0.03774,0.3604],"hinge_angle":0.59731,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":44.38458,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":782.0,"n_steps_budget":840.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.29933,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1095.0,"raw_peak_contact_force":44.38458,"subtask_id":"reach_door","tcp_end":[0.09987,0.19084,0.44726],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49642,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":327.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":362.0,"raw_peak_contact_force":22.96529,"subtask_id":"reach_door","tcp_end":[0.10462,0.18045,0.35983],"tcp_start":[0.09987,0.19084,0.44726],"tcp_to_object_dist_end":0.41591,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":160.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":40.4466,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":265.0,"raw_peak_contact_force":40.4466,"subtask_id":"open_door","tcp_end":[0.10973,0.03774,0.3604],"tcp_start":[0.10462,0.18045,0.35983],"tcp_to_object_dist_end":0.37862,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `5bc49f053da41ee2995fb91d1adc375d35d8209a2f6f497df40da3fd7dd59d69`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.35152,"average_solve_count":165.0,"average_success_count":165.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.lateral_offset_x":0.0005,"approach.approach_speed":0.19906,"push_door.force_limit":41.70178,"push_door.hinge_threshold":0.25877,"push_door.push_distance":0.27055,"push_door.push_speed":0.02856,"push_door.push_tolerance":0.08551},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":238.0,"contact_point_centroid":[0.10094,0.18865,0.5385],"force_p95":27.92215,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.14922,"mean_force":17.68932,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.0997,0.26255,0.43129]},{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.24308,-0.01154,0.43794],"force_p95":50.67354,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.67354,"mean_force":50.67354,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10902,-0.0367,0.35721]},{"body_a":"door_panel","body_b":"link7","contact_count":126.0,"contact_point_centroid":[0.1658,0.04025,0.38666],"force_p95":37.72921,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.87545,"mean_force":30.37929,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10456,0.10105,0.36091]},{"body_a":"door_panel","body_b":"link7","contact_count":66.0,"contact_point_centroid":[0.16513,0.14568,0.46975],"force_p95":26.00852,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.47854,"mean_force":14.74546,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09987,0.203,0.44587]},{"body_a":"door_panel","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.16526,0.12868,0.42772],"force_p95":17.78513,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.94807,"mean_force":14.96955,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09995,0.18606,0.40374]},{"body_a":"world","body_b":"door_panel","contact_count":792.0,"contact_point_centroid":[0.30055,0.19366,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09983,0.30501,0.40844]},{"body_a":"world","body_b":"door_panel","contact_count":300.0,"contact_point_centroid":[0.30649,0.14851,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09995,0.18605,0.4036]},{"body_a":"world","body_b":"door_panel","contact_count":200.0,"contact_point_centroid":[0.32761,0.10287,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10504,0.08923,0.36071]}],"total_contact_groups":8},"final_pose_error":0.0541,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.10899,-0.03767,0.35709],"hinge_angle":0.68941,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":81.14922,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":722.0,"n_steps_budget":780.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":13.53814,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1096.0,"raw_peak_contact_force":81.14922,"subtask_id":"reach_door","tcp_end":[0.09993,0.19175,0.44722],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49675,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":327.0,"n_steps_budget":630.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":363.0,"raw_peak_contact_force":22.94807,"subtask_id":"reach_door","tcp_end":[0.10021,0.18056,0.35983],"tcp_start":[0.09993,0.19175,0.44722],"tcp_to_object_dist_end":0.41487,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":50.67354,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":327.0,"raw_peak_contact_force":50.67354,"subtask_id":"open_door","tcp_end":[0.10899,-0.03767,0.35709],"tcp_start":[0.10021,0.18056,0.35983],"tcp_to_object_dist_end":0.37525,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `36664242b94803fac749fdbd125449f5f6a464dcd4b70b6714af07046570273f`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.1547,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_contact.lateral_offset_x":0.0077,"approach.approach_speed":0.06806,"push_door.force_limit":44.09806,"push_door.hinge_threshold":0.10004,"push_door.push_distance":0.2922,"push_door.push_speed":0.05911,"push_door.push_tolerance":0.02777},"optimized_scores":{"best_composite_score":0.62,"best_fitness_score":1.0,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link6","contact_count":1.0,"contact_point_centroid":[0.24184,-0.01761,0.44467],"force_p95":63.77492,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.77492,"mean_force":63.77492,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11087,-0.04067,0.35865]},{"body_a":"door_panel","body_b":"link7","contact_count":126.0,"contact_point_centroid":[0.17009,0.03848,0.38754],"force_p95":40.60266,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.84015,"mean_force":31.36694,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.10932,0.09982,0.36162]},{"body_a":"door_panel","body_b":"link6","contact_count":375.0,"contact_point_centroid":[0.1009,0.1938,0.53655],"force_p95":25.56467,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.61694,"mean_force":16.5748,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09952,0.26862,0.42908]},{"body_a":"door_panel","body_b":"link6","contact_count":12.0,"contact_point_centroid":[0.10326,0.14915,0.54359],"force_p95":29.35026,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.27203,"mean_force":16.85561,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.09996,0.21505,0.43902]},{"body_a":"door_panel","body_b":"link7","contact_count":118.0,"contact_point_centroid":[0.16862,0.14101,0.42077],"force_p95":24.17717,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.23852,"mean_force":16.9465,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.10332,0.19839,0.39675]},{"body_a":"world","body_b":"door_panel","contact_count":984.0,"contact_point_centroid":[0.30028,0.19793,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.09959,0.31129,0.40662]},{"body_a":"world","body_b":"door_panel","contact_count":340.0,"contact_point_centroid":[0.30454,0.15688,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"align_contact","phase_type":"align","tcp_position_centroid":[0.10269,0.2015,0.40462]},{"body_a":"world","body_b":"door_panel","contact_count":240.0,"contact_point_centroid":[0.33315,0.09354,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":2.0,"phase_name":"push_door","phase_type":"push","tcp_position_centroid":[0.11007,0.0675,0.36162]}],"total_contact_groups":8},"final_pose_error":0.07185,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.11083,-0.04169,0.35853],"hinge_angle":0.70037,"initial_hinge_angle":-0.14464,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.14464,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":63.77492,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1359.0,"raw_peak_contact_force":42.61694,"subtask_id":"reach_door","tcp_end":[0.09968,0.21694,0.44381],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.50395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":344.0,"n_steps_budget":660.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":14.83035,"phase_name":"align_contact","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":470.0,"raw_peak_contact_force":37.27203,"subtask_id":"reach_door","tcp_end":[0.10653,0.18342,0.35911],"tcp_start":[0.09968,0.21694,0.44381],"tcp_to_object_dist_end":0.41707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":240.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":63.77492,"phase_name":"push_door","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":367.0,"raw_peak_contact_force":63.77492,"subtask_id":"open_door","tcp_end":[0.11083,-0.04169,0.35853],"tcp_start":[0.10653,0.18342,0.35911],"tcp_to_object_dist_end":0.37758,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```