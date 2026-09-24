## Search State

- **Seed**: 0
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | arc_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 4 | -0.1559 | 0.13 | ❌ rejected |
| 5 | approach → push → retract | linear_cartesian | linear_cartesian | arc_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1526 | 0.00 | ❌ rejected |
| 4 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2365 | 0.82 | ❌ rejected |
| 3 | approach → push | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | contact_detected | pose_tolerance | 3 | 0.1715 | 0.00 | ❌ rejected |
| 2 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2392 | 0.81 | ❌ rejected |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: push_to_goal
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Primary evaluation target: **object displacement ratio toward goal_object_position**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=-0.156) — your mutation base

```yaml
skill: push_to_goal
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

- **Composite score**: -0.156
- **task_score** (E): 0.132
- **fitness_score**: 0.074  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.230

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_push_start | 0.00 | 1.00 | 0.1226 |
| push_to_goal | 0.00 | 1.00 | 0.0536 |
| retract_up | 1.00 | 1.00 | 0.0519 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_push_start | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.460, 0.025, 0.192) | (0.496, 0.001, 0.025)→(0.468, -0.007, 0.025) | 0.152→0.147 | 1.00 / 4.667 | 623.406 | 775.347 |
| push_to_goal | push | 0.00 / step_budget | (0.460, 0.025, 0.192)→(0.479, -0.023, 0.183) | (0.468, -0.007, 0.025)→(0.463, -0.011, 0.025) | 0.147→0.145 | 1.00 / 4.667 | 271.693 | 692.974 |
| retract_up | retract | 1.00 / step_budget | (0.479, -0.023, 0.183)→(0.468, -0.013, 0.230) | (0.463, -0.011, 0.025)→(0.463, -0.011, 0.025) | 0.145→0.145 | 1.00 / 4.000 | 0.245 | 321.713 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.496
- lateral_force_integral: None
- approach_alignment: 0.906
- goal_progress: 0.384
- terminal_score: 0.384
- phase_score: 0.018
- phase_breakdown.push_goal_score: 0.000
- phase_breakdown.pre_contact_score: 0.060

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.164
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.384
- **Median Q (composite search score)**: -0.193
- **K-run variance**: 0.0041
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.346


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `1efc9b29f7d131941a1bd842274a029ca5b2a2ff6a8656033ab118e32e2fae7d`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `6150c547b3cd2920ed4582689733d59ef61d18dc295ccd2a0d2317d1cf4e7764`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":5.27329,"average_solve_count":161.0,"average_success_count":161.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_push_start.approach_speed":0.05109,"push_to_goal.push_speed":0.07742,"retract_up.retract_height":0.14218,"retract_up.retract_speed":0.02165},"optimized_scores":{"best_composite_score":-0.06577,"best_fitness_score":0.16423,"best_task_score":0.38354},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":922.0,"contact_point_centroid":[0.55857,-0.03696,-0.00011],"force_p95":685.42947,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":866.28862,"mean_force":465.76316,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45714,-0.02708,0.19352]},{"body_a":"world","body_b":"link6","contact_count":720.0,"contact_point_centroid":[0.53945,0.00591,-3e-05],"force_p95":741.78014,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":744.35311,"mean_force":627.64804,"phase_index":0.0,"phase_name":"approach_to_push_start","phase_type":"approach","tcp_position_centroid":[0.44623,0.00322,0.19939]},{"body_a":"world","body_b":"link6","contact_count":5.0,"contact_point_centroid":[0.61105,-0.09326,-0.00014],"force_p95":456.8211,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":487.94546,"mean_force":251.96687,"phase_index":2.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48387,-0.0799,0.17586]},{"body_a":"push_box","body_b":"link6","contact_count":33.0,"contact_point_centroid":[0.52512,-0.00491,0.04757],"force_p95":364.56229,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":388.23633,"mean_force":113.50481,"phase_index":0.0,"phase_name":"approach_to_push_start","phase_type":"approach","tcp_position_centroid":[0.41651,0.00157,0.13589]},{"body_a":"world","body_b":"push_box","contact_count":3549.0,"contact_point_centroid":[0.48472,-0.06987,-5e-05],"force_p95":0.47565,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":242.89204,"mean_force":1.33614,"phase_index":0.0,"phase_name":"approach_to_push_start","phase_type":"approach","tcp_position_centroid":[0.4528,0.00282,0.19831]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.4797,-0.07664,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.45771,-0.02785,0.19324]},{"body_a":"world","body_b":"push_box","contact_count":1268.0,"contact_point_centroid":[0.4797,-0.07664,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.48023,-0.0723,0.21275]}],"total_contact_groups":7},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4797,-0.07664,0.02499],"final_tcp_position":[0.4775,-0.07368,0.24755],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":866.28862,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4797,-0.07664,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.07612,"object_to_goal_dist_start":0.12347,"object_z_max":0.03489,"peak_contact_force":744.35311,"phase_name":"approach_to_push_start","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4302.0,"raw_peak_contact_force":744.35311,"subtask_id":"pre_contact","tcp_end":[0.45413,0.00437,0.19691],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.19177,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4797,-0.07664,0.02499],"object_pos_start":[0.4797,-0.07664,0.02499],"object_to_goal_dist_end":0.07612,"object_to_goal_dist_start":0.07612,"object_z_max":0.02499,"peak_contact_force":434.15508,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4922.0,"raw_peak_contact_force":866.28862,"subtask_id":"push_goal","tcp_end":[0.48392,-0.07966,0.17576],"tcp_start":[0.45413,0.00437,0.19691],"tcp_to_object_dist_end":0.15086,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":317.0,"n_steps_budget":1000.0,"object_pos_end":[0.4797,-0.07664,0.02499],"object_pos_start":[0.4797,-0.07664,0.02499],"object_to_goal_dist_end":0.07612,"object_to_goal_dist_start":0.07612,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1273.0,"raw_peak_contact_force":487.94546,"tcp_end":[0.4775,-0.07368,0.24755],"tcp_start":[0.48392,-0.07966,0.17576],"tcp_to_object_dist_end":0.22259,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":7.11111,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_push_start.approach_speed":0.09988,"push_to_goal.push_speed":0.02536,"retract_up.retract_height":0.14757,"retract_up.retract_speed":0.08576},"optimized_scores":{"best_composite_score":-0.20868,"best_fitness_score":0.02132,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":785.0,"contact_point_centroid":[0.56047,0.02611,-0.00012],"force_p95":708.92503,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":866.31202,"mean_force":465.76229,"phase_index":0.0,"phase_name":"approach_to_push_start","phase_type":"approach","tcp_position_centroid":[0.45648,0.03156,0.19106]},{"body_a":"world","body_b":"link6","contact_count":967.0,"contact_point_centroid":[0.57928,0.04415,-9e-05],"force_p95":415.86857,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":468.33817,"mean_force":318.77609,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46842,0.06347,0.18613]},{"body_a":"push_box","body_b":"link6","contact_count":19.0,"contact_point_centroid":[0.52312,0.035,0.04836],"force_p95":323.40009,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":345.1966,"mean_force":180.30286,"phase_index":0.0,"phase_name":"approach_to_push_start","phase_type":"approach","tcp_position_centroid":[0.41551,0.0074,0.12201]},{"body_a":"world","body_b":"link6","contact_count":4.0,"contact_point_centroid":[0.59589,0.01071,-7e-05],"force_p95":248.79394,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":268.17317,"mean_force":161.85626,"phase_index":2.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.4842,0.06241,0.18353]},{"body_a":"world","body_b":"push_box","contact_count":3867.0,"contact_point_centroid":[0.47049,0.07565,-2e-05],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":183.17932,"mean_force":1.14357,"phase_index":0.0,"phase_name":"approach_to_push_start","phase_type":"approach","tcp_position_centroid":[0.46196,0.0283,0.19068]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.46576,0.07896,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.46845,0.06348,0.18604]},{"body_a":"world","body_b":"push_box","contact_count":1076.0,"contact_point_centroid":[0.46576,0.07896,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.47439,0.07675,0.2177]}],"total_contact_groups":7},"final_pose_error":0.01988,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46576,0.07896,0.02499],"final_tcp_position":[0.46624,0.08178,0.25289],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":866.31202,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46576,0.07896,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.2315,"object_to_goal_dist_start":0.20406,"object_z_max":0.02596,"peak_contact_force":425.32687,"phase_name":"approach_to_push_start","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4671.0,"raw_peak_contact_force":866.31202,"subtask_id":"pre_contact","tcp_end":[0.48232,0.06652,0.17921],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.15561,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46576,0.07896,0.02499],"object_pos_start":[0.46576,0.07896,0.02499],"object_to_goal_dist_end":0.2315,"object_to_goal_dist_start":0.2315,"object_z_max":0.02499,"peak_contact_force":380.67966,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4967.0,"raw_peak_contact_force":468.33817,"subtask_id":"push_goal","tcp_end":[0.48413,0.06241,0.18348],"tcp_start":[0.48232,0.06652,0.17921],"tcp_to_object_dist_end":0.16041,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":269.0,"n_steps_budget":690.0,"object_pos_end":[0.46576,0.07896,0.02499],"object_pos_start":[0.46576,0.07896,0.02499],"object_to_goal_dist_end":0.2315,"object_to_goal_dist_start":0.2315,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1080.0,"raw_peak_contact_force":268.17317,"tcp_end":[0.46624,0.08178,0.25289],"tcp_start":[0.48413,0.06241,0.18348],"tcp_to_object_dist_end":0.22792,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":6.71875,"average_solve_count":96.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_push_start.approach_speed":0.05277,"push_to_goal.push_speed":0.0624,"retract_up.retract_height":0.06686,"retract_up.retract_speed":0.06139},"optimized_scores":{"best_composite_score":-0.19318,"best_fitness_score":0.03682,"best_task_score":0.01354},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":949.0,"contact_point_centroid":[0.53729,-0.02626,-0.00011],"force_p95":703.71063,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":744.29411,"mean_force":485.15308,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.44447,-0.01875,0.1995]},{"body_a":"world","body_b":"link6","contact_count":695.0,"contact_point_centroid":[0.52846,0.01487,-5e-05],"force_p95":673.42239,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":715.37663,"mean_force":506.82585,"phase_index":0.0,"phase_name":"approach_to_push_start","phase_type":"approach","tcp_position_centroid":[0.43739,0.00389,0.20243]},{"body_a":"push_box","body_b":"link6","contact_count":738.0,"contact_point_centroid":[0.46755,-0.00072,0.06067],"force_p95":22.99591,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":280.2869,"mean_force":5.50356,"phase_index":0.0,"phase_name":"approach_to_push_start","phase_type":"approach","tcp_position_centroid":[0.43516,0.00362,0.19948]},{"body_a":"world","body_b":"link6","contact_count":11.0,"contact_point_centroid":[0.57458,-0.05772,-3e-05],"force_p95":175.68592,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":209.02042,"mean_force":101.37074,"phase_index":2.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.46612,-0.04975,0.1885]},{"body_a":"world","body_b":"push_box","contact_count":2216.0,"contact_point_centroid":[0.44417,-0.02682,-2e-05],"force_p95":8.65385,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":207.75201,"mean_force":2.22221,"phase_index":0.0,"phase_name":"approach_to_push_start","phase_type":"approach","tcp_position_centroid":[0.44847,0.00294,0.19844]},{"body_a":"push_box","body_b":"link6","contact_count":66.0,"contact_point_centroid":[0.47264,-0.01067,0.05009],"force_p95":58.06426,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":148.7405,"mean_force":10.14514,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.43472,0.00094,0.20267]},{"body_a":"world","body_b":"push_box","contact_count":3804.0,"contact_point_centroid":[0.44472,-0.03525,-2e-05],"force_p95":0.25483,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":125.13699,"mean_force":0.42976,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.44518,-0.0199,0.19927]},{"body_a":"push_box","body_b":"link7","contact_count":5.0,"contact_point_centroid":[0.48753,-7e-05,0.04978],"force_p95":46.61313,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.73718,"mean_force":15.57082,"phase_index":0.0,"phase_name":"approach_to_push_start","phase_type":"approach","tcp_position_centroid":[0.41077,0.00112,0.12044]},{"body_a":"world","body_b":"push_box","contact_count":128.0,"contact_point_centroid":[0.44471,-0.03535,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract_up","phase_type":"retract","tcp_position_centroid":[0.46568,-0.04954,0.1886]}],"total_contact_groups":9},"final_pose_error":0.01974,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.44471,-0.03535,0.02499],"final_tcp_position":[0.46074,-0.04644,0.1887],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":744.29411,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45998,-0.02294,0.0257],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.13322,"object_to_goal_dist_start":0.12903,"object_z_max":0.0341,"peak_contact_force":700.53759,"phase_name":"approach_to_push_start","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3654.0,"raw_peak_contact_force":715.37663,"subtask_id":"pre_contact","tcp_end":[0.44273,0.00511,0.20105],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17841,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.44471,-0.03535,0.02499],"object_pos_start":[0.45998,-0.02294,0.0257],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.13322,"object_z_max":0.0257,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4819.0,"raw_peak_contact_force":744.29411,"subtask_id":"push_goal","tcp_end":[0.46867,-0.05086,0.1885],"tcp_start":[0.44273,0.00511,0.20105],"tcp_to_object_dist_end":0.16598,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":32.0,"n_steps_budget":600.0,"object_pos_end":[0.44471,-0.03535,0.02499],"object_pos_start":[0.44471,-0.03535,0.02499],"object_to_goal_dist_end":0.12728,"object_to_goal_dist_start":0.12728,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_up","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":139.0,"raw_peak_contact_force":209.02042,"tcp_end":[0.46074,-0.04644,0.1887],"tcp_start":[0.46867,-0.05086,0.1885],"tcp_to_object_dist_end":0.16486,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```