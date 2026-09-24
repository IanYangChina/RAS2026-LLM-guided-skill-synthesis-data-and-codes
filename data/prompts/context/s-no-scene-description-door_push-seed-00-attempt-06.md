## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.2532 | 0.50 | ❌ rejected |
| 5 | approach → push | arc_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | pose_tolerance | 7 | -0.0024 | 0.35 | ❌ rejected |
| 4 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.2537 | 0.50 | ✅ accepted |
| 3 | approach → push | arc_cartesian | linear_cartesian | impedance_control | impedance_control | force_exceeded | pose_tolerance | 7 | 0.0750 | 0.09 | ❌ rejected |
| 2 | approach → push | arc_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 5 | 0.2503 | 0.50 | ✅ accepted |

**Proposal policy**: task_score is 0.50 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.253) — your mutation base

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

- **Composite score**: 0.253
- **task_score** (E): 0.503
- **fitness_score**: 0.503  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_door | 1.00 | 1.00 | 0.2312 |
| push_door_open | 0.67 | 0.00 | 0.0913 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_door | approach | 1.00 / step_budget | (0.100, 0.399, 0.350)→(0.175, 0.189, 0.408) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 1.00 / 1.000 | 11.101 | 48.936 |
| push_door_open | push | 0.67 / step_budget | (0.175, 0.189, 0.408)→(0.198, 0.230, 0.486) | (0.000, 0.000, 0.000)→(0.000, 0.000, 0.000) | 0.406→0.406 | 0.00 / 0.000 | 0.000 | 6.058 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- hinge_angle_ratio: 0.642
- arc_quality: 1.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.642
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.642
- **Median Q (composite search score)**: 0.219
- **K-run variance**: 0.0105
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.456


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":64.0,"average_success_count":64.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_door.approach_height":0.03739,"approach_to_door.approach_x_offset":0.07994,"approach_to_door.speed":0.13211,"push_door_open.push_distance":0.07108,"push_door_open.push_speed":0.05542},"optimized_scores":{"best_composite_score":0.14872,"best_fitness_score":0.39872,"best_task_score":0.39872},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":46.0,"contact_point_centroid":[0.2393,0.13719,0.41262],"force_p95":23.478,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.53124,"mean_force":19.3806,"phase_index":0.0,"phase_name":"approach_to_door","phase_type":"approach","tcp_position_centroid":[0.17395,0.19449,0.38886]},{"body_a":"door_panel","body_b":"link6","contact_count":268.0,"contact_point_centroid":[0.11943,0.15215,0.51969],"force_p95":20.28087,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.08176,"mean_force":11.92199,"phase_index":0.0,"phase_name":"approach_to_door","phase_type":"approach","tcp_position_centroid":[0.15851,0.23654,0.39248]},{"body_a":"world","body_b":"door_panel","contact_count":888.0,"contact_point_centroid":[0.30181,0.1737,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_door","phase_type":"approach","tcp_position_centroid":[0.13776,0.29356,0.38249]},{"body_a":"door_panel","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.24134,0.13164,0.41166],"force_p95":0.0,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.17597,0.18902,0.3879]},{"body_a":"world","body_b":"door_panel","contact_count":436.0,"contact_point_centroid":[0.30924,0.13909,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.18358,0.20296,0.41438]}],"total_contact_groups":5},"final_pose_error":0.00994,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.19107,0.21654,0.44039],"hinge_angle":0.25674,"initial_hinge_angle":0.04781,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.04781,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":48.53124,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":17.65337,"phase_name":"approach_to_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1202.0,"raw_peak_contact_force":48.53124,"subtask_id":"pre_push_position","tcp_end":[0.17597,0.18902,0.3879],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.46601,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":401.0,"n_steps_budget":810.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":437.0,"raw_peak_contact_force":0.0,"subtask_id":"push_complete","tcp_end":[0.19107,0.21654,0.44039],"tcp_start":[0.17597,0.18902,0.3879],"tcp_to_object_dist_end":0.52663,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `7a748efd829eb09daaf6b07ec36a2131763f35cca8c1f058f1a757467a8ce067`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.92222,"average_solve_count":90.0,"average_success_count":90.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_door.approach_height":0.07813,"approach_to_door.approach_x_offset":0.07998,"approach_to_door.speed":0.14907,"push_door_open.push_distance":0.38615,"push_door_open.push_speed":0.0505},"optimized_scores":{"best_composite_score":0.2188,"best_fitness_score":0.4688,"best_task_score":0.4688},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":49.0,"contact_point_centroid":[0.23925,0.13731,0.44996],"force_p95":24.32902,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.39908,"mean_force":18.94623,"phase_index":0.0,"phase_name":"approach_to_door","phase_type":"approach","tcp_position_centroid":[0.17391,0.19466,0.42624]},{"body_a":"door_panel","body_b":"link6","contact_count":337.0,"contact_point_centroid":[0.11553,0.1603,0.54898],"force_p95":16.70508,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.64981,"mean_force":12.01989,"phase_index":0.0,"phase_name":"approach_to_door","phase_type":"approach","tcp_position_centroid":[0.15531,0.24565,0.42115]},{"body_a":"door_panel","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.24135,0.13135,0.44989],"force_p95":14.01554,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.43339,"mean_force":5.35362,"phase_index":1.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.17601,0.18871,0.4262]},{"body_a":"world","body_b":"door_panel","contact_count":960.0,"contact_point_centroid":[0.30131,0.17997,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_door","phase_type":"approach","tcp_position_centroid":[0.13349,0.30553,0.39781]},{"body_a":"world","body_b":"door_panel","contact_count":884.0,"contact_point_centroid":[0.30904,0.13972,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.19614,0.22534,0.49569]}],"total_contact_groups":5},"final_pose_error":0.22158,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.21695,0.26275,0.56741],"hinge_angle":0.24978,"initial_hinge_angle":0.00413,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":0.00413,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":49.39908,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":972.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":15.64969,"phase_name":"approach_to_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1346.0,"raw_peak_contact_force":49.39908,"subtask_id":"pre_push_position","tcp_end":[0.17599,0.18878,0.42621],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.49827,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":888.0,"raw_peak_contact_force":15.43339,"subtask_id":"push_complete","tcp_end":[0.21695,0.26275,0.56741],"tcp_start":[0.17599,0.18878,0.42621],"tcp_to_object_dist_end":0.66186,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `8f682501979e58f93da2583f25150788eff90e19c055477d4547c33e5c9d7ff1`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.64189,"average_solve_count":148.0,"average_success_count":148.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_door.approach_height":0.06094,"approach_to_door.approach_x_offset":0.07667,"approach_to_door.speed":0.14906,"push_door_open.push_distance":0.05814,"push_door_open.push_speed":0.01037},"optimized_scores":{"best_composite_score":0.392,"best_fitness_score":0.642,"best_task_score":0.642},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"door_panel","body_b":"link7","contact_count":44.0,"contact_point_centroid":[0.23621,0.13724,0.43413],"force_p95":23.37339,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.87907,"mean_force":18.37009,"phase_index":0.0,"phase_name":"approach_to_door","phase_type":"approach","tcp_position_centroid":[0.17092,0.19454,0.41038]},{"body_a":"door_panel","body_b":"link6","contact_count":456.0,"contact_point_centroid":[0.11021,0.17557,0.53322],"force_p95":17.64378,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.93585,"mean_force":11.8169,"phase_index":0.0,"phase_name":"approach_to_door","phase_type":"approach","tcp_position_centroid":[0.14692,0.26287,0.40509]},{"body_a":"door_panel","body_b":"link7","contact_count":7.0,"contact_point_centroid":[0.23815,0.13151,0.43373],"force_p95":2.1631,"geom_a":"door_panel_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":2.74037,"mean_force":0.50807,"phase_index":1.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.17286,0.18888,0.40998]},{"body_a":"world","body_b":"door_panel","contact_count":984.0,"contact_point_centroid":[0.30092,0.19067,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":0.0,"phase_name":"approach_to_door","phase_type":"approach","tcp_position_centroid":[0.13152,0.30702,0.39035]},{"body_a":"world","body_b":"door_panel","contact_count":316.0,"contact_point_centroid":[0.30902,0.13978,0.0],"force_p95":0.0,"geom_a":"table","geom_b":"door_panel_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.0,"mean_force":0.0,"phase_index":1.0,"phase_name":"push_door_open","phase_type":"push","tcp_position_centroid":[0.17796,0.19839,0.42766]}],"total_contact_groups":5},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.1,0.18,0.35],"final_tcp_position":[0.18479,0.2108,0.45136],"hinge_angle":0.2532,"initial_hinge_angle":-0.08321,"realised_door_panel_position":[0.5,0.2,0.0],"realised_goal_position":[0.1,0.18,0.35],"realised_initial_hinge_angle":-0.08321,"realised_object_initial_position":[0.0,0.0,0.0]},"peak_contact_force":48.87907,"phases":[{"contact_detected":true,"contact_event_count":1.0,"n_steps":930.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"approach_to_door","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1484.0,"raw_peak_contact_force":48.87907,"subtask_id":"pre_push_position","tcp_end":[0.17285,0.189,0.41007],"tcp_start":[0.10002,0.39926,0.35004],"tcp_to_object_dist_end":0.48348,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":354.0,"n_steps_budget":1000.0,"object_pos_end":[0.0,0.0,0.0],"object_pos_start":[0.0,0.0,0.0],"object_to_goal_dist_end":0.40608,"object_to_goal_dist_start":0.40608,"object_z_max":0.0,"peak_contact_force":0.0,"phase_name":"push_door_open","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":323.0,"raw_peak_contact_force":2.74037,"subtask_id":"push_complete","tcp_end":[0.18479,0.2108,0.45136],"tcp_start":[0.17285,0.189,0.41007],"tcp_to_object_dist_end":0.53133,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```