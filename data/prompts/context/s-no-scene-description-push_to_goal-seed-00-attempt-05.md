## Search State

- **Seed**: 0
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → push → retract | linear_cartesian | linear_cartesian | arc_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1526 | 0.00 | ❌ rejected |
| 4 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2365 | 0.82 | ❌ rejected |
| 3 | approach → push | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | contact_detected | pose_tolerance | 3 | 0.1715 | 0.00 | ❌ rejected |
| 2 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2392 | 0.81 | ❌ rejected |
| 1 | insert → approach → push → retract → lift → insert | linear_cartesian | linear_cartesian | impedance_motion | arc_cartesian | linear_cartesian | impedance_motion | impedance_control | force_threshold_switch | impedance_control | position_control | position_control | admittance_control | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | force_exceeded | 5 | 0.2365 | 0.82 | ✅ accepted |

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

## Current Skill (Q=-0.153) — your mutation base

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

- **Composite score**: -0.153
- **task_score** (E): 0.000
- **fitness_score**: 0.127  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.280

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1715 |
| push_1 | 0.00 | 1.00 | 0.0016 |
| retract_1 | 0.00 | 1.00 | 0.1037 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.494, 0.001, 0.134) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 0.00 / guard_failure | (0.579, -0.032, 0.001)→(0.579, -0.032, -0.001) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 5.000 | 1654.741 | 1692.261 |
| retract_1 | retract | 0.00 / step_budget | (0.579, -0.032, -0.001)→(0.584, -0.017, 0.101) | (0.496, 0.001, 0.025)→(0.496, 0.001, 0.025) | 0.152→0.152 | 1.00 / 4.000 | 0.245 | 1337.215 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.000
- lateral_force_integral: None
- approach_alignment: 0.638
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.230
- phase_breakdown.push_goal_score: 0.082
- phase_breakdown.pre_contact_score: 0.823

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.138
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.149
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.373


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":1.0,"average_failure_rate":0.01064,"average_mean_iterations":6.20213,"average_solve_count":94.0,"average_success_count":93.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07682,"push_1.push_distance":0.15145,"push_1.push_speed":0.07361,"retract_1.arc_height":0.13992,"retract_1.retract_speed":0.02936},"optimized_scores":{"best_composite_score":-0.16679,"best_fitness_score":0.11321,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":2.0,"contact_point_centroid":[0.61652,-0.01022,-0.00168],"force_p95":1552.04888,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1559.13824,"mean_force":1488.24462,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.60624,-0.01228,0.00248]},{"body_a":"attachment","body_b":"world","contact_count":89.0,"contact_point_centroid":[0.61222,-0.01067,-0.00186],"force_p95":456.28084,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1162.98427,"mean_force":176.11173,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.60243,-0.01264,0.00294]},{"body_a":"world","body_b":"push_box","contact_count":2216.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50505,-0.01244,0.21691]},{"body_a":"world","body_b":"push_box","contact_count":220.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.56924,-0.01377,0.08885]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51644,-0.02763,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.61278,0.00254,0.04057]}],"total_contact_groups":5},"final_pose_error":0.21373,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51644,-0.02763,0.02499],"final_tcp_position":[0.61664,0.0071,0.08902],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51644,-0.02763,0.025]},"peak_contact_force":1559.13824,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":554.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.025],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2216.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.51193,-0.02544,0.13336],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10849,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":1417.35099,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":222.0,"raw_peak_contact_force":1559.13824,"subtask_id":"push_goal","tcp_end":[0.60536,-0.01272,-0.00166],"tcp_start":[0.6059,-0.01244,0.00083],"tcp_to_object_dist_end":0.09402,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51644,-0.02763,0.02499],"object_pos_start":[0.51644,-0.02763,0.02499],"object_to_goal_dist_end":0.12347,"object_to_goal_dist_start":0.12347,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4089.0,"raw_peak_contact_force":1162.98427,"tcp_end":[0.61664,0.0071,0.08902],"tcp_start":[0.60536,-0.01272,-0.00166],"tcp_to_object_dist_end":0.12388,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `88c86884172a74f1f27b08fda534b767baf4d8d60d3fd4d782dec9555f4aae87`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.13158,"average_mean_iterations":29.60526,"average_solve_count":152.0,"average_success_count":132.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04593,"push_1.push_distance":0.05748,"push_1.push_speed":0.04682,"retract_1.arc_height":0.1352,"retract_1.retract_speed":0.06909},"optimized_scores":{"best_composite_score":-0.14176,"best_fitness_score":0.13824,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":1.0,"contact_point_centroid":[0.5872,-0.05281,-0.00095],"force_p95":1910.63435,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1910.63435,"mean_force":1910.63435,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.57665,-0.05302,0.00381]},{"body_a":"attachment","body_b":"world","contact_count":61.0,"contact_point_centroid":[0.58215,-0.05625,-0.00299],"force_p95":981.34562,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1729.97625,"mean_force":304.62466,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.57203,-0.05526,0.00039]},{"body_a":"world","body_b":"push_box","contact_count":2444.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4982,0.02433,0.21669]},{"body_a":"world","body_b":"push_box","contact_count":216.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54908,0.00161,0.09088]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50142,0.05406,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.58262,-0.03996,0.06474]}],"total_contact_groups":5},"final_pose_error":0.12821,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50142,0.05406,0.02499],"final_tcp_position":[0.57351,-0.05207,0.13699],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50142,0.05406,0.025]},"peak_contact_force":1939.86065,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":611.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.025],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2444.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.49816,0.04976,0.13313],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10828,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":54.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":1939.86065,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":217.0,"raw_peak_contact_force":1910.63435,"subtask_id":"push_goal","tcp_end":[0.5757,-0.05386,0.00019],"tcp_start":[0.5757,-0.05386,0.00019],"tcp_to_object_dist_end":0.13334,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50142,0.05406,0.02499],"object_pos_start":[0.50142,0.05406,0.02499],"object_to_goal_dist_end":0.20406,"object_to_goal_dist_start":0.20406,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4061.0,"raw_peak_contact_force":1729.97625,"tcp_end":[0.57351,-0.05207,0.13699],"tcp_start":[0.5757,-0.05386,0.00019],"tcp_to_object_dist_end":0.17031,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3cdbd735282928b0caf1de02aaaeed7f0a3d0a10908989412c558d20f3517fa`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":14.0,"average_failure_rate":0.09722,"average_mean_iterations":23.11806,"average_solve_count":144.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.04412,"push_1.push_distance":0.23035,"push_1.push_speed":0.07754,"retract_1.arc_height":0.14272,"retract_1.retract_speed":0.02686},"optimized_scores":{"best_composite_score":-0.14927,"best_fitness_score":0.13073,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"world","contact_count":2.0,"contact_point_centroid":[0.56598,-0.02722,-0.00197],"force_p95":1602.48493,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1607.01116,"mean_force":1561.74888,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55587,-0.02874,0.00234]},{"body_a":"attachment","body_b":"world","contact_count":79.0,"contact_point_centroid":[0.56156,-0.02797,-0.00195],"force_p95":462.46284,"geom_a":"pusher_tip","geom_b":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1118.68343,"mean_force":179.74049,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.55205,-0.02936,0.00327]},{"body_a":"world","body_b":"push_box","contact_count":2276.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4848,-0.01081,0.21772]},{"body_a":"world","body_b":"push_box","contact_count":220.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52264,-0.02286,0.08829]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47139,-0.02418,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.558,-0.01308,0.03556]}],"total_contact_groups":5},"final_pose_error":0.18388,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47139,-0.02418,0.02499],"final_tcp_position":[0.56079,-0.00745,0.07602],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47139,-0.02418,0.025]},"peak_contact_force":1607.01116,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.025],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2276.0,"raw_peak_contact_force":0.24534,"subtask_id":"pre_contact","tcp_end":[0.47062,-0.02219,0.13453],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10956,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":55.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":1607.01116,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":222.0,"raw_peak_contact_force":1607.01116,"subtask_id":"push_goal","tcp_end":[0.555,-0.02917,-0.00146],"tcp_start":[0.55553,-0.0289,0.00083],"tcp_to_object_dist_end":0.08784,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47139,-0.02418,0.02499],"object_pos_start":[0.47139,-0.02418,0.02499],"object_to_goal_dist_end":0.12903,"object_to_goal_dist_start":0.12903,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":4079.0,"raw_peak_contact_force":1118.68343,"tcp_end":[0.56079,-0.00745,0.07602],"tcp_start":[0.555,-0.02917,-0.00146],"tcp_to_object_dist_end":0.10429,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```