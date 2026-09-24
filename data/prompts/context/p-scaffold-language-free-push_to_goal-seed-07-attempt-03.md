## Search State

- **Seed**: 7
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.0079 | 0.00 | ❌ rejected |
| 2 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | admittance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | -0.2661 | 0.00 | ❌ rejected |
| 1 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | -0.0681 | 0.00 | ❌ rejected |
| 0 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2751 | 0.69 | ✅ accepted |

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
- Frozen realised-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`
- Frozen object start: [0.51501145599256, 0.047665656116349056, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.51501145599256, 0.047665656116349056, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.515, 0.0477, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.51501145599256, 0.047665656116349056, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.015, -0.1977, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752

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
| `object` | offset from object initial position (0.51501145599256, 0.047665656116349056, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

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

## Current Skill (Q=-0.008) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: admittance_control
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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

- **Composite score**: -0.008
- **task_score** (E): 0.004
- **fitness_score**: 0.252  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.510

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1676 |
| contact_1 | 1.00 | 1.00 | 0.0883 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 1.00 | 1.00 | 0.1305 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.034, 0.142) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.509, 0.034, 0.142)→(0.509, 0.027, 0.054) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 50609.507 | 0.245 |
| push_1 | push | 0.00 / guard_failure | (0.508, 0.026, 0.054)→(0.508, 0.026, 0.054) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 51.682 | 62.272 |
| retract_1 | retract | 1.00 / step_budget | (0.508, 0.026, 0.054)→(0.505, 0.026, 0.184) | (0.513, 0.026, 0.025)→(0.512, 0.026, 0.025) | 0.180→0.179 | 1.00 / 4.000 | 0.245 | 39.259 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.007
- lateral_force_integral: None
- approach_alignment: 0.549
- goal_progress: 0.007
- terminal_score: 0.007
- phase_score: 0.435
- phase_breakdown.reach_approach_score: 0.675
- phase_breakdown.reach_goal_score: 0.070
- phase_breakdown.reach_contact_score: 0.883

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.264
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.007
- **Median Q (composite search score)**: -0.013
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.326


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `75e2389a1a667086aa2b9c0de482ff37adf5571150b90a83772692baadf8b52e`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `154c216c563de6b8ee153943e5b668ca6d0c7dfd9253696b060f91a67dca06ec`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.81818,"average_solve_count":110.0,"average_success_count":110.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.14277,"approach_1.speed":0.05461,"contact_1.force_guard_limit":19.62146,"contact_1.force_threshold":4.68449,"contact_1.speed":0.03898,"push_1.push_distance":0.19926,"push_1.push_force_guard_threshold":29.87068,"push_1.push_speed":0.04698,"retract_1.speed":0.0381},"optimized_scores":{"best_composite_score":-0.01289,"best_fitness_score":0.24711,"best_task_score":0.00232},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.52158,0.04774,0.04979],"force_p95":56.06281,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":58.61641,"mean_force":39.65347,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51037,0.04735,0.05385]},{"body_a":"attachment","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.52097,0.04669,0.04961],"force_p95":32.02948,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":37.42906,"mean_force":11.63915,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50976,0.04632,0.05368]},{"body_a":"world","body_b":"push_box","contact_count":24.0,"contact_point_centroid":[0.50655,0.04551,-4e-05],"force_p95":33.08279,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.92454,"mean_force":15.17532,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51036,0.04732,0.05384]},{"body_a":"world","body_b":"push_box","contact_count":1638.0,"contact_point_centroid":[0.51428,0.04718,-2e-05],"force_p95":0.25065,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.80362,"mean_force":0.313,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50712,0.04622,0.1188]},{"body_a":"world","body_b":"push_box","contact_count":1360.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50401,0.03816,0.22787]},{"body_a":"world","body_b":"push_box","contact_count":1872.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50904,0.04971,0.09689]}],"total_contact_groups":6},"final_pose_error":0.01971,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51456,0.04724,0.02499],"final_tcp_position":[0.50726,0.04628,0.18405],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":340.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1360.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_approach","tcp_end":[0.51024,0.05208,0.14343],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":468.0,"n_steps_budget":780.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1872.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.51059,0.04769,0.05418],"tcp_start":[0.51024,0.05208,0.14343],"tcp_to_object_dist_end":0.02952,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":9.0,"n_steps_budget":1000.0,"object_pos_end":[0.51486,0.04742,0.02488],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19798,"object_to_goal_dist_start":0.19823,"object_z_max":0.02505,"peak_contact_force":52.23241,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":33.0,"raw_peak_contact_force":58.61641,"subtask_id":"reach_goal","tcp_end":[0.51011,0.04659,0.05355],"tcp_start":[0.51014,0.04673,0.0536],"tcp_to_object_dist_end":0.02908,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":416.0,"n_steps_budget":1000.0,"object_pos_end":[0.51456,0.04724,0.02499],"object_pos_start":[0.5149,0.04729,0.02482],"object_to_goal_dist_end":0.19777,"object_to_goal_dist_start":0.19785,"object_z_max":0.02508,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1647.0,"raw_peak_contact_force":37.42906,"tcp_end":[0.50726,0.04628,0.18405],"tcp_start":[0.51011,0.04659,0.05355],"tcp_to_object_dist_end":0.15923,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `4d55d9375783bea830660bf0a13dfc76a97a0d4f5645e7ebcc1ef7143776d0b7`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.15385,"average_solve_count":78.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.11595,"approach_1.speed":0.0913,"contact_1.force_guard_limit":22.33914,"contact_1.force_threshold":8.05614,"contact_1.speed":0.03877,"push_1.push_distance":0.1181,"push_1.push_force_guard_threshold":19.6695,"push_1.push_speed":0.06832,"retract_1.speed":0.07181},"optimized_scores":{"best_composite_score":-0.0144,"best_fitness_score":0.2456,"best_task_score":0.00155},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.48621,0.05897,0.04974],"force_p95":51.79706,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.25656,"mean_force":31.30631,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4753,0.0583,0.05447]},{"body_a":"world","body_b":"push_box","contact_count":21.0,"contact_point_centroid":[0.47319,0.05484,-4e-05],"force_p95":23.86498,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.23131,"mean_force":12.24433,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47531,0.05828,0.05447]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.4858,0.0582,0.04959],"force_p95":31.49556,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":34.60828,"mean_force":13.71041,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4749,0.05762,0.05434]},{"body_a":"world","body_b":"push_box","contact_count":1445.0,"contact_point_centroid":[0.47861,0.05816,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.24979,"mean_force":0.31481,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4725,0.05739,0.11929]},{"body_a":"world","body_b":"push_box","contact_count":1316.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49042,0.04736,0.23025]},{"body_a":"world","body_b":"push_box","contact_count":1856.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47609,0.06103,0.09773]}],"total_contact_groups":6},"final_pose_error":0.01983,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47883,0.05811,0.02499],"final_tcp_position":[0.47265,0.05745,0.18452],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":57.25656,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":329.0,"n_steps_budget":660.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1316.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_approach","tcp_end":[0.47938,0.06393,0.14374],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11887,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":464.0,"n_steps_budget":780.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":41.44777,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1856.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.47547,0.05853,0.05478],"tcp_start":[0.47938,0.06393,0.14374],"tcp_to_object_dist_end":0.03003,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.47916,0.0583,0.02491],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20934,"object_to_goal_dist_start":0.2095,"object_z_max":0.02504,"peak_contact_force":31.8706,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":29.0,"raw_peak_contact_force":57.25656,"subtask_id":"reach_goal","tcp_end":[0.47519,0.05779,0.05418],"tcp_start":[0.47521,0.0579,0.05423],"tcp_to_object_dist_end":0.02954,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":366.0,"n_steps_budget":660.0,"object_pos_end":[0.47883,0.05811,0.02499],"object_pos_start":[0.47918,0.05819,0.02484],"object_to_goal_dist_end":0.20918,"object_to_goal_dist_start":0.20923,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1452.0,"raw_peak_contact_force":34.60828,"tcp_end":[0.47265,0.05745,0.18452],"tcp_start":[0.47519,0.05779,0.05418],"tcp_to_object_dist_end":0.15965,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `0a9238470f4497c7aa88b149b7cee960f9853513db10bf496723f5ea1d3a6043`; realized-scene SHA-256: `2cf7387f3e8baf02f18930263090d6f78777bdbc147b7fa30c178332e76b547b`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54443,-0.02558,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.04443,-0.12442,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.54443,-0.02558,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65714,"average_solve_count":105.0,"average_success_count":105.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.arc_height":0.18071,"approach_1.speed":0.09078,"contact_1.force_guard_limit":21.30362,"contact_1.force_threshold":7.89542,"contact_1.speed":0.0173,"push_1.push_distance":0.11553,"push_1.push_force_guard_threshold":29.96011,"push_1.push_speed":0.01247,"retract_1.speed":0.08503},"optimized_scores":{"best_composite_score":0.00368,"best_fitness_score":0.26368,"best_task_score":0.00683},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.55048,-0.02474,0.04974],"force_p95":69.78404,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.94271,"mean_force":47.41593,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53906,-0.02483,0.05315]},{"body_a":"world","body_b":"push_box","contact_count":27.0,"contact_point_centroid":[0.53033,-0.03031,-5e-05],"force_p95":45.39851,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":67.58468,"mean_force":21.37746,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53907,-0.02483,0.05317]},{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.54952,-0.02597,0.04958],"force_p95":41.2249,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.74055,"mean_force":16.57644,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53811,-0.02611,0.05306]},{"body_a":"world","body_b":"push_box","contact_count":1493.0,"contact_point_centroid":[0.54353,-0.02634,-2e-05],"force_p95":0.24739,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.3794,"mean_force":0.33702,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53561,-0.02589,0.11782]},{"body_a":"world","body_b":"push_box","contact_count":1260.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5177,0.00389,0.21961]},{"body_a":"world","body_b":"push_box","contact_count":2108.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5366,-0.01954,0.09362]}],"total_contact_groups":6},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54374,-0.02629,0.02499],"final_tcp_position":[0.53588,-0.02583,0.18332],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":315.0,"n_steps_budget":660.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1260.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_approach","tcp_end":[0.53663,-0.01447,0.13919],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":527.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2108.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_contact","tcp_end":[0.53945,-0.02437,0.05355],"tcp_start":[0.53663,-0.01447,0.13919],"tcp_to_object_dist_end":0.02901,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":12.0,"n_steps_budget":1000.0,"object_pos_end":[0.54401,-0.026,0.02488],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13158,"object_to_goal_dist_start":0.13211,"object_z_max":0.02508,"peak_contact_force":70.94271,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":39.0,"raw_peak_contact_force":70.94271,"subtask_id":"reach_goal","tcp_end":[0.53852,-0.02589,0.05286],"tcp_start":[0.53857,-0.02574,0.05289],"tcp_to_object_dist_end":0.02851,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":378.0,"n_steps_budget":600.0,"object_pos_end":[0.54374,-0.02629,0.02499],"object_pos_start":[0.54407,-0.02617,0.02481],"object_to_goal_dist_end":0.13121,"object_to_goal_dist_start":0.13144,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1501.0,"raw_peak_contact_force":45.74055,"tcp_end":[0.53588,-0.02583,0.18332],"tcp_start":[0.53852,-0.02589,0.05286],"tcp_to_object_dist_end":0.15852,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```