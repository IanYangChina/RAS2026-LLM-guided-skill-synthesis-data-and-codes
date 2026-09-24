## Search State

- **Seed**: 7
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2736 | 0.69 | ❌ rejected |
| 13 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1459 | 0.00 | ❌ rejected |
| 12 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2628 | 0.66 | ❌ rejected |
| 11 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.2542 | 0.67 | ❌ rejected |
| 10 | approach → contact → push → retract | arc_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 6 | 0.4392 | 0.31 | ❌ rejected |

**Proposal policy**: task_score is 0.69 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.274) — your mutation base

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

- **Composite score**: 0.274
- **task_score** (E): 0.689
- **fitness_score**: 0.634  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2787 |
| contact_1 | 1.00 | 1.00 | 0.0575 |
| push_1 | 1.00 | 1.00 | 0.1261 |
| retract_1 | 0.00 | 1.00 | 0.1354 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.508, 0.104, 0.046) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.508, 0.104, 0.046)→(0.508, 0.054, 0.021) | (0.513, 0.027, 0.025)→(0.515, 0.017, 0.025) | 0.180→0.171 | 1.00 / 3.000 | 0.834 | 11.093 |
| push_1 | push | 1.00 / step_budget | (0.508, 0.054, 0.021)→(0.501, -0.070, 0.024) | (0.515, 0.017, 0.025)→(0.507, -0.104, 0.028) | 0.171→0.059 | 1.00 / 3.333 | 46.242 | 79.004 |
| retract_1 | retract | 0.00 / step_budget | (0.501, -0.070, 0.024)→(0.497, 0.049, 0.088) | (0.507, -0.104, 0.028)→(0.505, -0.100, 0.025) | 0.059→0.058 | 1.00 / 4.000 | 0.245 | 37.443 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.869
- lateral_force_integral: None
- approach_alignment: 0.457
- goal_progress: 0.762
- terminal_score: 0.762
- phase_score: 0.826
- phase_breakdown.approach_score: 0.822
- phase_breakdown.contact_score: 0.860
- phase_breakdown.push_score: 0.808

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.800
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.762
- **Median Q (composite search score)**: 0.203
- **K-run variance**: 0.0140
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.445


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.02165,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05233,"contact_1.speed":0.04018,"push_1.push_depth":0.09516,"push_1.push_distance":0.10568,"push_1.push_speed":0.06007,"retract_1.speed":0.06159},"optimized_scores":{"best_composite_score":0.17763,"best_fitness_score":0.53763,"best_task_score":0.65469},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1733.0,"contact_point_centroid":[0.51982,-0.04644,-0.00014],"force_p95":46.18275,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":58.38869,"mean_force":26.78487,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50375,0.00975,0.02165]},{"body_a":"push_box","body_b":"link7","contact_count":971.0,"contact_point_centroid":[0.52946,-0.00555,0.05441],"force_p95":42.64278,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.07336,"mean_force":34.58081,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50376,0.01125,0.0215]},{"body_a":"attachment","body_b":"push_box","contact_count":980.0,"contact_point_centroid":[0.52238,0.00125,0.05207],"force_p95":39.86154,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.76675,"mean_force":30.50903,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50383,0.01186,0.02151]},{"body_a":"world","body_b":"push_box","contact_count":3880.0,"contact_point_centroid":[0.50231,-0.08212,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.53764,"mean_force":0.27316,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49523,0.00957,0.05388]},{"body_a":"push_box","body_b":"link7","contact_count":11.0,"contact_point_centroid":[0.5251,-0.0729,0.05399],"force_p95":26.95424,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":27.56524,"mean_force":16.83325,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49842,-0.04639,0.02197]},{"body_a":"attachment","body_b":"push_box","contact_count":35.0,"contact_point_centroid":[0.51759,-0.0548,0.05441],"force_p95":19.20769,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":24.13275,"mean_force":4.61558,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49744,-0.04405,0.02238]},{"body_a":"attachment","body_b":"push_box","contact_count":177.0,"contact_point_centroid":[0.51544,0.06814,0.03819],"force_p95":11.25727,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.22897,"mean_force":6.02229,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50988,0.08001,0.02601]},{"body_a":"world","body_b":"push_box","contact_count":3105.0,"contact_point_centroid":[0.51521,0.04601,-1e-05],"force_p95":3.40204,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.61895,"mean_force":0.58987,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50782,0.09789,0.0407]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50294,0.07203,0.19077]}],"total_contact_groups":9},"final_pose_error":0.11153,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50219,-0.08158,0.02499],"final_tcp_position":[0.49569,0.0588,0.08595],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":58.38869,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50877,0.12222,0.06444],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":843.0,"n_steps_budget":990.0,"object_pos_end":[0.5169,0.03822,0.025],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.18897,"object_to_goal_dist_start":0.19823,"object_z_max":0.02506,"peak_contact_force":1.33088,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3282.0,"raw_peak_contact_force":13.22897,"tcp_end":[0.51053,0.07496,0.02194],"tcp_start":[0.50877,0.12222,0.06444],"tcp_to_object_dist_end":0.03742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50329,-0.0846,0.02857],"object_pos_start":[0.5169,0.03822,0.025],"object_to_goal_dist_end":0.06558,"object_to_goal_dist_start":0.18897,"object_z_max":0.02885,"peak_contact_force":33.21311,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3684.0,"raw_peak_contact_force":58.38869,"tcp_end":[0.49877,-0.04637,0.02202],"tcp_start":[0.51053,0.07496,0.02194],"tcp_to_object_dist_end":0.03905,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50219,-0.08158,0.02499],"object_pos_start":[0.50329,-0.0846,0.02857],"object_to_goal_dist_end":0.06845,"object_to_goal_dist_start":0.06558,"object_z_max":0.02857,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3926.0,"raw_peak_contact_force":28.53764,"tcp_end":[0.49569,0.0588,0.08595],"tcp_start":[0.49877,-0.04637,0.02202],"tcp_to_object_dist_end":0.15318,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.13077,"average_solve_count":260.0,"average_success_count":260.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09639,"contact_1.speed":0.03339,"push_1.push_depth":0.09993,"push_1.push_distance":0.17044,"push_1.push_speed":0.01324,"retract_1.speed":0.07105},"optimized_scores":{"best_composite_score":0.20286,"best_fitness_score":0.56286,"best_task_score":0.64971},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1506.0,"contact_point_centroid":[0.48946,-0.03305,-0.0001],"force_p95":45.93046,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":51.05833,"mean_force":11.63861,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48488,0.01391,0.01949]},{"body_a":"attachment","body_b":"push_box","contact_count":901.0,"contact_point_centroid":[0.49206,0.01412,0.03494],"force_p95":32.19202,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":36.32274,"mean_force":12.77916,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48308,0.02547,0.01951]},{"body_a":"push_box","body_b":"link7","contact_count":402.0,"contact_point_centroid":[0.50601,0.03727,0.0512],"force_p95":33.44545,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.29478,"mean_force":24.4875,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47796,0.0603,0.01985]},{"body_a":"attachment","body_b":"push_box","contact_count":193.0,"contact_point_centroid":[0.47945,0.07883,0.03105],"force_p95":8.06846,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.6617,"mean_force":4.30271,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47466,0.09058,0.02291]},{"body_a":"world","body_b":"push_box","contact_count":3207.0,"contact_point_centroid":[0.47949,0.0567,-1e-05],"force_p95":2.62883,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.56417,"mean_force":0.5049,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47356,0.10998,0.02933]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49192,-0.05503,0.02144],"force_p95":1.21507,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.21507,"mean_force":1.21507,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49456,-0.04341,0.02006]},{"body_a":"world","body_b":"push_box","contact_count":3984.0,"contact_point_centroid":[0.48182,-0.07896,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.02842,"mean_force":0.24666,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4924,0.01449,0.0545]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48504,0.08104,0.18041]}],"total_contact_groups":8},"final_pose_error":0.10099,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48183,-0.0789,0.02499],"final_tcp_position":[0.49405,0.06848,0.09068],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":51.05833,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.47586,0.13504,0.04155],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":880.0,"n_steps_budget":1000.0,"object_pos_end":[0.48154,0.04887,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.19972,"object_to_goal_dist_start":0.2095,"object_z_max":0.02507,"peak_contact_force":0.0002,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3400.0,"raw_peak_contact_force":11.6617,"tcp_end":[0.47501,0.08555,0.0213],"tcp_start":[0.47586,0.13504,0.04155],"tcp_to_object_dist_end":0.03744,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48209,-0.07822,0.02502],"object_pos_start":[0.48154,0.04887,0.02499],"object_to_goal_dist_end":0.07398,"object_to_goal_dist_start":0.19972,"object_z_max":0.02882,"peak_contact_force":0.93824,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2809.0,"raw_peak_contact_force":51.05833,"tcp_end":[0.49456,-0.04341,0.02006],"tcp_start":[0.47501,0.08555,0.0213],"tcp_to_object_dist_end":0.03731,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48183,-0.0789,0.02499],"object_pos_start":[0.48209,-0.07822,0.02502],"object_to_goal_dist_end":0.07339,"object_to_goal_dist_start":0.07398,"object_z_max":0.02503,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3985.0,"raw_peak_contact_force":1.21507,"tcp_end":[0.49405,0.06848,0.09068],"tcp_start":[0.49456,-0.04341,0.02006],"tcp_to_object_dist_end":0.16182,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73514,"average_solve_count":185.0,"average_success_count":185.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08401,"contact_1.speed":0.03479,"push_1.push_depth":0.09878,"push_1.push_distance":0.18071,"push_1.push_speed":0.08004,"retract_1.speed":0.07482},"optimized_scores":{"best_composite_score":0.44042,"best_fitness_score":0.80042,"best_task_score":0.76165},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":981.0,"contact_point_centroid":[0.55525,-0.07568,0.05428],"force_p95":109.82968,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":127.56392,"mean_force":76.33676,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52232,-0.0595,0.02343]},{"body_a":"attachment","body_b":"push_box","contact_count":981.0,"contact_point_centroid":[0.54136,-0.06814,0.05342],"force_p95":86.47697,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":92.9818,"mean_force":52.22389,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52233,-0.05948,0.02343]},{"body_a":"world","body_b":"push_box","contact_count":1912.0,"contact_point_centroid":[0.54885,-0.11077,-0.00034],"force_p95":74.14943,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":86.21705,"mean_force":49.70769,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52203,-0.06078,0.02357]},{"body_a":"push_box","body_b":"link7","contact_count":58.0,"contact_point_centroid":[0.54796,-0.12705,0.05654],"force_p95":73.38962,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":82.57569,"mean_force":30.38352,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50724,-0.11495,0.02973]},{"body_a":"world","body_b":"push_box","contact_count":3671.0,"contact_point_centroid":[0.53034,-0.13961,-3e-05],"force_p95":0.25052,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":77.22934,"mean_force":0.55198,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.5021,-0.04205,0.05868]},{"body_a":"attachment","body_b":"push_box","contact_count":69.0,"contact_point_centroid":[0.53134,-0.11776,0.06076],"force_p95":54.08303,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":67.04931,"mean_force":19.86507,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50678,-0.11288,0.03011]},{"body_a":"attachment","body_b":"push_box","contact_count":170.0,"contact_point_centroid":[0.54512,-0.00506,0.03583],"force_p95":6.08058,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.389,"mean_force":2.75325,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53914,0.00684,0.02038]},{"body_a":"world","body_b":"push_box","contact_count":3348.0,"contact_point_centroid":[0.54455,-0.02754,-1e-05],"force_p95":1.45145,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.29023,"mean_force":0.38993,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53671,0.0302,0.0237]},{"body_a":"world","body_b":"push_box","contact_count":3788.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51726,0.04383,0.17043]}],"total_contact_groups":9},"final_pose_error":0.14527,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52968,-0.13949,0.02499],"final_tcp_position":[0.50031,0.01939,0.08642],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":127.56392,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":947.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3788.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5381,0.05607,0.03232],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":934.0,"n_steps_budget":1000.0,"object_pos_end":[0.54644,-0.0346,0.02511],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.12439,"object_to_goal_dist_start":0.13211,"object_z_max":0.02514,"peak_contact_force":1.17218,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3518.0,"raw_peak_contact_force":8.389,"tcp_end":[0.53971,0.00215,0.01979],"tcp_start":[0.5381,0.05607,0.03232],"tcp_to_object_dist_end":0.03774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":991.0,"n_steps_budget":1000.0,"object_pos_end":[0.53606,-0.14772,0.03103],"object_pos_start":[0.54644,-0.0346,0.02511],"object_to_goal_dist_end":0.03663,"object_to_goal_dist_start":0.12439,"object_z_max":0.03109,"peak_contact_force":104.575,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3874.0,"raw_peak_contact_force":127.56392,"tcp_end":[0.50838,-0.1196,0.02879],"tcp_start":[0.53971,0.00215,0.01979],"tcp_to_object_dist_end":0.03952,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52968,-0.13949,0.02499],"object_pos_start":[0.53606,-0.14772,0.03103],"object_to_goal_dist_end":0.03149,"object_to_goal_dist_start":0.03663,"object_z_max":0.03495,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3798.0,"raw_peak_contact_force":82.57569,"tcp_end":[0.50031,0.01939,0.08642],"tcp_start":[0.50838,-0.1196,0.02879],"tcp_to_object_dist_end":0.17285,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```