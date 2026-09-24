## Search State

- **Seed**: 7
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 0 | 0.4567 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.30 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.457) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  weight: 0.3
- id: push_to_goal
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
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: reach_object
- id: descend_1
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.005
    orientation:
      mode: keep_current
  subtask_id: reach_object
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  subtask_id: push_to_goal
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.005
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_1** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.1], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **descend_1** (`descend`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.0, 0.0], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none
- **push_1** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings: none
- **retract_1** (`retract`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.0, 0.1], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: 0.457
- **task_score** (E): 0.302
- **fitness_score**: 0.517  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.060

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1805 |
| descend_1 | 1.00 | 1.00 | 0.0842 |
| push_1 | 1.00 | 1.00 | 0.1640 |
| retract_1 | 1.00 | 1.00 | 0.0926 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.026, 0.128) | (0.513, 0.027, 0.025)→(0.513, 0.027, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_1 | descend | 1.00 / step_budget | (0.509, 0.026, 0.128)→(0.525, 0.027, 0.045) | (0.513, 0.027, 0.025)→(0.518, 0.027, 0.024) | 0.180→0.181 | 1.00 / 4.333 | 241.296 | 252.856 |
| push_1 | push | 1.00 / step_budget | (0.525, 0.027, 0.045)→(0.500, -0.131, 0.023) | (0.518, 0.027, 0.024)→(0.507, -0.026, 0.025) | 0.181→0.127 | 1.00 / 4.000 | 0.244 | 167.870 |
| retract_1 | retract | 1.00 / step_budget | (0.500, -0.131, 0.023)→(0.497, -0.148, 0.114) | (0.507, -0.026, 0.025)→(0.507, -0.026, 0.025) | 0.127→0.127 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.277
- lateral_force_integral: None
- approach_alignment: 0.810
- goal_progress: 0.276
- terminal_score: 0.276
- phase_score: 0.661
- phase_breakdown.push_to_goal_score: 0.674
- phase_breakdown.reach_object_score: 0.631

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.517
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.302
- **Median Q (composite search score)**: 0.457
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: no_parameters
- **Mean generations**: 0.0
- **Final σ (mean)**: 0.000


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90323,"average_solve_count":124.0,"average_success_count":124.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":0.44703,"best_fitness_score":0.50703,"best_task_score":0.27629},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":155.0,"contact_point_centroid":[0.52937,0.04734,0.04716],"force_p95":249.28297,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":250.70064,"mean_force":189.53203,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51754,0.04737,0.04776]},{"body_a":"attachment","body_b":"push_box","contact_count":270.0,"contact_point_centroid":[0.5356,0.02388,0.04715],"force_p95":157.78057,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.72275,"mean_force":130.77392,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52747,0.01665,0.04702]},{"body_a":"world","body_b":"push_box","contact_count":1417.0,"contact_point_centroid":[0.51616,0.00588,-0.00035],"force_p95":126.77505,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":137.21191,"mean_force":25.34218,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51476,-0.04214,0.03555]},{"body_a":"world","body_b":"push_box","contact_count":2119.0,"contact_point_centroid":[0.5157,0.04786,-0.00012],"force_p95":111.66105,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":128.41569,"mean_force":14.17893,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.51157,0.04631,0.07691]},{"body_a":"world","body_b":"push_box","contact_count":3692.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50462,0.0229,0.21103]},{"body_a":"world","body_b":"push_box","contact_count":2524.0,"contact_point_centroid":[0.5132,-0.00714,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49587,-0.1384,0.06288]}],"total_contact_groups":6},"final_pose_error":0.01225,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5132,-0.00714,0.02499],"final_tcp_position":[0.49661,-0.14791,0.11341],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":250.70064,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":923.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3692.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.51104,0.04545,0.12699],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1021,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":534.0,"n_steps_budget":660.0,"object_pos_end":[0.51977,0.04812,0.02378],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19911,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":241.89097,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2274.0,"raw_peak_contact_force":250.70064,"subtask_id":"reach_object","tcp_end":[0.52645,0.04829,0.04498],"tcp_start":[0.51104,0.04545,0.12699],"tcp_to_object_dist_end":0.02223,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.5132,-0.00714,0.02499],"object_pos_start":[0.51977,0.04812,0.02378],"object_to_goal_dist_end":0.14346,"object_to_goal_dist_start":0.19911,"object_z_max":0.03539,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1687.0,"raw_peak_contact_force":164.72275,"subtask_id":"push_to_goal","tcp_end":[0.49884,-0.13052,0.02196],"tcp_start":[0.52645,0.04829,0.04498],"tcp_to_object_dist_end":0.12425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":631.0,"n_steps_budget":660.0,"object_pos_end":[0.5132,-0.00714,0.02499],"object_pos_start":[0.5132,-0.00714,0.02499],"object_to_goal_dist_end":0.14346,"object_to_goal_dist_start":0.14346,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2524.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49661,-0.14791,0.11341],"tcp_start":[0.49884,-0.13052,0.02196],"tcp_to_object_dist_end":0.16706,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90625,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":0.43703,"best_fitness_score":0.49703,"best_task_score":0.25607},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":149.0,"contact_point_centroid":[0.49431,0.05808,0.04697],"force_p95":261.064,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":265.49068,"mean_force":200.7915,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.48246,0.05817,0.04745]},{"body_a":"attachment","body_b":"push_box","contact_count":272.0,"contact_point_centroid":[0.50651,0.03404,0.04644],"force_p95":163.96781,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":174.2053,"mean_force":135.88119,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49889,0.02583,0.0461]},{"body_a":"world","body_b":"push_box","contact_count":1258.0,"contact_point_centroid":[0.48567,0.01456,-0.0004],"force_p95":155.29839,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":164.79853,"mean_force":29.90589,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49575,-0.04895,0.03297]},{"body_a":"world","body_b":"push_box","contact_count":2155.0,"contact_point_centroid":[0.48001,0.05861,-0.00012],"force_p95":119.53746,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.63701,"mean_force":14.19053,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.4766,0.05669,0.07844]},{"body_a":"world","body_b":"push_box","contact_count":3496.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48752,0.0277,0.21256]},{"body_a":"world","body_b":"push_box","contact_count":2528.0,"contact_point_centroid":[0.47712,0.00417,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49423,-0.13891,0.065]}],"total_contact_groups":6},"final_pose_error":0.01201,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47712,0.00417,0.02499],"final_tcp_position":[0.49642,-0.14797,0.11371],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":265.49068,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":874.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3496.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47693,0.05555,0.12829],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":548.0,"n_steps_budget":660.0,"object_pos_end":[0.48406,0.05908,0.02401],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20969,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":249.11659,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2304.0,"raw_peak_contact_force":265.49068,"subtask_id":"reach_object","tcp_end":[0.49194,0.05942,0.04454],"tcp_start":[0.47693,0.05555,0.12829],"tcp_to_object_dist_end":0.02199,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":540.0,"n_steps_budget":1000.0,"object_pos_end":[0.47712,0.00417,0.02499],"object_pos_start":[0.48406,0.05908,0.02401],"object_to_goal_dist_end":0.15586,"object_to_goal_dist_start":0.20969,"object_z_max":0.03968,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1530.0,"raw_peak_contact_force":174.2053,"subtask_id":"push_to_goal","tcp_end":[0.49569,-0.13076,0.02186],"tcp_start":[0.49194,0.05942,0.04454],"tcp_to_object_dist_end":0.13623,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":632.0,"n_steps_budget":690.0,"object_pos_end":[0.47712,0.00417,0.02499],"object_pos_start":[0.47712,0.00417,0.02499],"object_to_goal_dist_end":0.15586,"object_to_goal_dist_start":0.15586,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2528.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49642,-0.14797,0.11371],"tcp_start":[0.49569,-0.13076,0.02186],"tcp_to_object_dist_end":0.17717,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89189,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{},"optimized_scores":{"best_composite_score":0.48614,"best_fitness_score":0.54614,"best_task_score":0.3746},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":156.0,"contact_point_centroid":[0.55828,-0.02546,0.04729],"force_p95":240.26953,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":242.37567,"mean_force":181.92809,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54645,-0.02553,0.04797]},{"body_a":"attachment","body_b":"push_box","contact_count":317.0,"contact_point_centroid":[0.55664,-0.04961,0.04718],"force_p95":161.8124,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.68254,"mean_force":136.64043,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54807,-0.05631,0.04709]},{"body_a":"world","body_b":"push_box","contact_count":2106.0,"contact_point_centroid":[0.54514,-0.02569,-0.00012],"force_p95":105.60326,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":123.38399,"mean_force":13.79116,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.54007,-0.02493,0.07681]},{"body_a":"world","body_b":"push_box","contact_count":901.0,"contact_point_centroid":[0.54451,-0.05492,-0.00062],"force_p95":101.86408,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":110.84572,"mean_force":48.6454,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54117,-0.06746,0.04296]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.54443,-0.02558,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51883,-0.01238,0.2106]},{"body_a":"world","body_b":"push_box","contact_count":2524.0,"contact_point_centroid":[0.53172,-0.07371,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24495,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4997,-0.13875,0.06406]}],"total_contact_groups":6},"final_pose_error":0.012,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53172,-0.07371,0.02499],"final_tcp_position":[0.49704,-0.14796,0.11355],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.54443,-0.02558,0.025]},"peak_contact_force":242.37567,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54443,-0.02558,0.02499],"object_pos_start":[0.54443,-0.02558,0.025],"object_to_goal_dist_end":0.13211,"object_to_goal_dist_start":0.13211,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.5389,-0.02432,0.12766],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":530.0,"n_steps_budget":660.0,"object_pos_end":[0.54923,-0.02583,0.0238],"object_pos_start":[0.54443,-0.02558,0.02499],"object_to_goal_dist_end":0.13358,"object_to_goal_dist_start":0.13211,"object_z_max":0.02499,"peak_contact_force":232.87935,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2262.0,"raw_peak_contact_force":242.37567,"subtask_id":"reach_object","tcp_end":[0.55535,-0.02602,0.04534],"tcp_start":[0.5389,-0.02432,0.12766],"tcp_to_object_dist_end":0.02239,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":411.0,"n_steps_budget":870.0,"object_pos_end":[0.53174,-0.07367,0.02454],"object_pos_start":[0.54923,-0.02583,0.0238],"object_to_goal_dist_end":0.08266,"object_to_goal_dist_start":0.13358,"object_z_max":0.03599,"peak_contact_force":0.24044,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1218.0,"raw_peak_contact_force":164.68254,"subtask_id":"push_to_goal","tcp_end":[0.50578,-0.13112,0.02418],"tcp_start":[0.55535,-0.02602,0.04534],"tcp_to_object_dist_end":0.06304,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":631.0,"n_steps_budget":660.0,"object_pos_end":[0.53172,-0.07371,0.02499],"object_pos_start":[0.53174,-0.07367,0.02454],"object_to_goal_dist_end":0.08262,"object_to_goal_dist_start":0.08266,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2524.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49704,-0.14796,0.11355],"tcp_start":[0.50578,-0.13112,0.02418],"tcp_to_object_dist_end":0.12067,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```