## Search State

- **Seed**: 1
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → align → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 7  | -0.0465 | 0.16 | ✅ accepted |
| 0 | rotate → align → push → align → lift | impedance_motion | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | impedance_control | position_control | position_control | position_control | position_control | time_limit | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 3  | -0.3662 | 0.14 | ❌ rejected |

**Proposal policy**: task_score is 0.14 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`
- Frozen object start: [0.5011821624700257, 0.045046369632593536, 0.03]
- Frozen task target: [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]
- Goal object position: (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.5644159612719634, 0.2448649447137244, 0.1467747178015728)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.5011821624700257, 0.045046369632593536, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5012, 0.045, 0.03]
  frozen_task_target: [0.5644, 0.2449, 0.1468]
  frozen_object_starts: {'grasp_target': [0.5011821624700257, 0.045046369632593536, 0.03]}
  frozen_targets: {'place_target': [0.5644159612719634, 0.2448649447137244, 0.1467747178015728]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb

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
| `object` | offset from object initial position (0.5011821624700257, 0.045046369632593536, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5644159612719634, 0.2448649447137244, 0.1467747178015728) | final destination targets |
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

## Current Skill (Q=-0.366) — your mutation base

```yaml
skill: grasp_place
phases:
- id: rotate_1
  type: rotate
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: push_1
  type: push
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: align_2
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: lift_1
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: -0.366
- **task_score** (E): 0.137
- **fitness_score**: 0.164  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.530

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 0.00 | 1.00 | 0.1650 |
| align_grasp | 0.00 | 1.00 | 0.0563 |
| grasp | 1.00 | 1.00 | 0.0038 |
| lift | 0.67 | 1.00 | 0.0235 |
| approach_goal | 0.00 | 1.00 | 0.1047 |
| descend_place | 0.00 | 1.00 | 0.0118 |
| release | 1.00 | 1.00 | 0.0281 |
| retract | 1.00 | 1.00 | 0.0861 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 0.00 / step_budget | (0.500, -0.000, 0.301)→(0.407, 0.001, 0.165) | (0.479, -0.000, 0.030)→(0.437, 0.002, 0.016) | 0.276→0.302 | 1.00 / 5.000 | 208.432 | 1402.128 |
| align_grasp | align | 0.00 / step_budget | (0.407, 0.001, 0.165)→(0.453, -0.002, 0.162) | (0.437, 0.002, 0.016)→(0.437, 0.002, 0.016) | 0.302→0.302 | 1.00 / 4.667 | 50609.370 | 737.561 |
| grasp | grasp | 1.00 / step_budget | (0.453, -0.002, 0.162)→(0.452, -0.004, 0.159) | (0.437, 0.002, 0.016)→(0.437, 0.002, 0.016) | 0.302→0.302 | 1.00 / 9.333 | 57.043 | 121.140 |
| lift | lift | 0.67 / step_budget | (0.452, -0.004, 0.159)→(0.441, -0.007, 0.165) | (0.437, 0.002, 0.016)→(0.437, 0.002, 0.016) | 0.302→0.302 | 1.00 / 8.667 | 94254.657 | 199.385 |
| approach_goal | approach | 0.00 / step_budget | (0.441, -0.007, 0.165)→(0.492, 0.022, 0.220) | (0.437, 0.002, 0.016)→(0.437, 0.002, 0.016) | 0.302→0.302 | 1.00 / 8.000 | 0.123 | 136.803 |
| descend_place | descend | 0.00 / step_budget | (0.492, 0.022, 0.220)→(0.499, 0.030, 0.219) | (0.437, 0.002, 0.016)→(0.437, 0.002, 0.016) | 0.302→0.302 | 1.00 / 9.000 | 95.162 | 124.148 |
| release | release | 1.00 / step_budget | (0.499, 0.030, 0.219)→(0.499, 0.032, 0.246) | (0.437, 0.002, 0.016)→(0.437, 0.002, 0.016) | 0.302→0.302 | 1.00 / 4.667 | 84.602 | 84.602 |
| retract | retract | 1.00 / step_budget | (0.499, 0.032, 0.246)→(0.500, 0.035, 0.332) | (0.437, 0.002, 0.016)→(0.437, 0.002, 0.016) | 0.302→0.302 | 1.00 / 4.000 | 0.123 | 85.475 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: 0.000
- terminal_score: 0.179
- phase_score: 0.054
- phase_breakdown.lift_clearance_score: 0.000
- phase_breakdown.grasp_complete_score: 0.000
- phase_breakdown.place_accuracy_score: 0.017
- phase_breakdown.pre_grasp_score: 0.163
- grasp_place_fitness: 0.185

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.185
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.179
- **Median Q (composite search score)**: -0.368
- **K-run variance**: 0.0003
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.536


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8110053be9072e64e15984c6424e4a66fe19af4b6c37a60139a43e94cc34ad53`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `46ef03f7b16015a0d14bf26d80c05d326b92c02b0bf759391930f5ab902d1933`; realized-scene SHA-256: `a2ed2c4162d37489f2d2d0fa0373774d72c951d58f2469e0ba2d602ff46b6cfb`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50118,0.04505,0.03]},{"name":"goal","value":[0.56442,0.24486,0.14677]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.50118,0.04505,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.56442,0.24486,0.14677]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":82.0,"average_failure_rate":0.46067,"average_mean_iterations":95.30899,"average_solve_count":178.0,"average_success_count":96.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":-0.01994,"align_grasp.lateral_offset_y":0.01193,"approach_goal.transport_speed":0.11238,"approach_object.approach_speed":0.09285,"descend_place.placement_offset_z":-0.01868,"lift.lift_height":0.19884,"lift.lift_speed":0.07522},"optimized_scores":{"best_composite_score":-0.34502,"best_fitness_score":0.18498,"best_task_score":0.17893},"replay_outcomes":[{"contacts":{"omitted_contact_groups":4,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":885.0,"contact_point_centroid":[0.63183,0.0117,-0.00047],"force_p95":217.77294,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1446.29097,"mean_force":209.73626,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40095,0.01125,0.13996]},{"body_a":"world","body_b":"link6","contact_count":691.0,"contact_point_centroid":[0.64565,0.03506,-0.00021],"force_p95":446.00535,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":892.60438,"mean_force":325.10564,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.44803,0.03221,0.19405]},{"body_a":"world","body_b":"link6","contact_count":39.0,"contact_point_centroid":[0.70041,0.04716,-8e-05],"force_p95":174.87459,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":276.53143,"mean_force":83.59953,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4666,0.04256,0.15774]},{"body_a":"world","body_b":"link6","contact_count":446.0,"contact_point_centroid":[0.70079,0.04849,-0.00012],"force_p95":70.75528,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":190.82755,"mean_force":66.90244,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46807,0.04148,0.15974]},{"body_a":"grasp_target","body_b":"link7","contact_count":133.0,"contact_point_centroid":[0.4914,0.02712,0.03418],"force_p95":3.34838,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":4.96657,"mean_force":0.72558,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38397,0.00515,0.0884]},{"body_a":"grasp_target","body_b":"hand","contact_count":180.0,"contact_point_centroid":[0.47704,0.02899,0.05325],"force_p95":3.02662,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.93932,"mean_force":0.64227,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38627,0.00535,0.09409]},{"body_a":"world","body_b":"grasp_target","contact_count":3530.0,"contact_point_centroid":[0.46664,0.04905,-0.00244],"force_p95":0.30014,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.37713,"mean_force":0.16394,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.41471,0.01099,0.15194]},{"body_a":"world","body_b":"grasp_target","contact_count":2884.0,"contact_point_centroid":[0.45723,0.04984,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.44873,0.0326,0.19322]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45723,0.04984,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46807,0.04148,0.15974]},{"body_a":"world","body_b":"grasp_target","contact_count":1936.0,"contact_point_centroid":[0.45723,0.04984,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46132,0.04588,0.14968]},{"body_a":"world","body_b":"grasp_target","contact_count":1012.0,"contact_point_centroid":[0.45723,0.04984,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.46469,0.0524,0.15127]},{"body_a":"world","body_b":"grasp_target","contact_count":4.0,"contact_point_centroid":[0.45723,0.04984,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.47029,0.06318,0.15635]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.45723,0.04984,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.46715,0.06259,0.15899]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.45723,0.04984,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.46378,0.0619,0.21564]},{"body_a":"left_finger","body_b":"right_finger","contact_count":339.0,"contact_point_centroid":[0.47007,0.04163,0.15893],"force_p95":0.01362,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01115,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46808,0.04152,0.1597]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2078.0,"contact_point_centroid":[0.46333,0.04595,0.14884],"force_p95":0.01096,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01273,"mean_force":0.01039,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46132,0.04587,0.14969]}],"total_contact_groups":20},"final_pose_error":0.01257,"key_states":{"actual_goal_position":[0.56442,0.24486,0.14677],"final_object_position":[0.45723,0.04984,0.01602],"final_tcp_position":[0.46397,0.06195,0.26092],"realised_goal_position":[0.56442,0.24486,0.14677],"realised_object_initial_position":[0.50118,0.04505,0.03]},"peak_contact_force":151458.80606,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45723,0.04984,0.01602],"object_pos_start":[0.50118,0.04505,0.03],"object_to_goal_dist_end":0.25811,"object_to_goal_dist_start":0.23992,"object_z_max":0.03,"peak_contact_force":228.77287,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4749.0,"raw_peak_contact_force":1446.29097,"subtask_id":"pre_grasp","tcp_end":[0.42139,0.02224,0.1864],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17628,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":721.0,"n_steps_budget":750.0,"object_pos_end":[0.45723,0.04984,0.01602],"object_pos_start":[0.45723,0.04984,0.01602],"object_to_goal_dist_end":0.25811,"object_to_goal_dist_start":0.25811,"object_z_max":0.01602,"peak_contact_force":151458.80606,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3575.0,"raw_peak_contact_force":892.60438,"tcp_end":[0.46805,0.04109,0.16015],"tcp_start":[0.42139,0.02224,0.1864],"tcp_to_object_dist_end":0.1448,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45723,0.04984,0.01602],"object_pos_start":[0.45723,0.04984,0.01602],"object_to_goal_dist_end":0.25811,"object_to_goal_dist_start":0.25811,"object_z_max":0.01602,"peak_contact_force":65.41113,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2585.0,"raw_peak_contact_force":190.82755,"tcp_end":[0.46808,0.04152,0.1597],"tcp_start":[0.46805,0.04109,0.16015],"tcp_to_object_dist_end":0.14433,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":484.0,"n_steps_budget":600.0,"object_pos_end":[0.45723,0.04984,0.01602],"object_pos_start":[0.45723,0.04984,0.01602],"object_to_goal_dist_end":0.25811,"object_to_goal_dist_start":0.25811,"object_z_max":0.01602,"peak_contact_force":9748.96524,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4053.0,"raw_peak_contact_force":276.53143,"subtask_id":"lift_clearance","tcp_end":[0.45838,0.03819,0.14773],"tcp_start":[0.46808,0.04152,0.1597],"tcp_to_object_dist_end":0.13223,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.45723,0.04984,0.01602],"object_pos_start":[0.45723,0.04984,0.01602],"object_to_goal_dist_end":0.25811,"object_to_goal_dist_start":0.25811,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2099.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.47029,0.06318,0.15635],"tcp_start":[0.45838,0.03819,0.14773],"tcp_to_object_dist_end":0.14156,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.45723,0.04984,0.01602],"object_pos_start":[0.45723,0.04984,0.01602],"object_to_goal_dist_end":0.25811,"object_to_goal_dist_start":0.25811,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.47033,0.06321,0.15634],"tcp_start":[0.47029,0.06318,0.15635],"tcp_to_object_dist_end":0.14157,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45723,0.04984,0.01602],"object_pos_start":[0.45723,0.04984,0.01602],"object_to_goal_dist_end":0.25811,"object_to_goal_dist_start":0.25811,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1023.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.46517,0.06218,0.17343],"tcp_start":[0.47033,0.06321,0.15634],"tcp_to_object_dist_end":0.1581,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.45723,0.04984,0.01602],"object_pos_start":[0.45723,0.04984,0.01602],"object_to_goal_dist_end":0.25811,"object_to_goal_dist_start":0.25811,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.46397,0.06195,0.26092],"tcp_start":[0.46517,0.06218,0.17343],"tcp_to_object_dist_end":0.24529,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1efc3ad2e58ea1c47cd56203c4986b53dab7b80d759e458b85d233ccc9cc04bd`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":74.0,"average_failure_rate":0.45679,"average_mean_iterations":94.82716,"average_solve_count":162.0,"average_success_count":88.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":0.00464,"align_grasp.lateral_offset_y":-0.01019,"approach_goal.transport_speed":0.29511,"approach_object.approach_speed":0.18825,"descend_place.placement_offset_z":-0.00691,"lift.lift_height":0.10413,"lift.lift_speed":0.12666},"optimized_scores":{"best_composite_score":-0.36835,"best_fitness_score":0.16165,"best_task_score":0.12083},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":887.0,"contact_point_centroid":[0.63132,-0.00657,-0.00046],"force_p95":208.16764,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1428.84052,"mean_force":204.45012,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39677,-0.00654,0.13355]},{"body_a":"world","body_b":"link6","contact_count":551.0,"contact_point_centroid":[0.6408,-0.01265,-0.00024],"force_p95":479.10776,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":896.52106,"mean_force":310.01709,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.44232,-0.01598,0.19213]},{"body_a":"world","body_b":"link7","contact_count":21.0,"contact_point_centroid":[0.52692,0.00115,-0.00321],"force_p95":0.0,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":467.69695,"mean_force":22.27128,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37289,-0.00264,0.04912]},{"body_a":"world","body_b":"link6","contact_count":18.0,"contact_point_centroid":[0.68904,-0.03586,-8e-05],"force_p95":405.70918,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":410.16268,"mean_force":128.65124,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.44934,-0.034,0.14466]},{"body_a":"link5","body_b":"hand","contact_count":28.0,"contact_point_centroid":[0.53176,0.06666,0.1207],"force_p95":317.71406,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":388.20333,"mean_force":152.05305,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.46497,-0.02495,0.16034]},{"body_a":"link5","body_b":"hand","contact_count":66.0,"contact_point_centroid":[0.52112,0.05539,0.13254],"force_p95":235.46239,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":306.21524,"mean_force":130.34784,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.48346,-0.03589,0.18871]},{"body_a":"world","body_b":"link5","contact_count":47.0,"contact_point_centroid":[0.66206,0.08513,-0.00014],"force_p95":137.96593,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":260.98634,"mean_force":106.78273,"phase_index":4.0,"phase_name":"approach_goal","phase_type":"approach","tcp_position_centroid":[0.47294,-0.02629,0.16763]},{"body_a":"world","body_b":"link6","contact_count":437.0,"contact_point_centroid":[0.69678,-0.04944,-0.00022],"force_p95":208.76814,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":212.24407,"mean_force":173.90342,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45396,-0.03654,0.14259]},{"body_a":"world","body_b":"link5","contact_count":9.0,"contact_point_centroid":[0.65456,0.07061,-4e-05],"force_p95":156.29453,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":165.59735,"mean_force":94.59715,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46375,-0.03875,0.14682]},{"body_a":"world","body_b":"link5","contact_count":367.0,"contact_point_centroid":[0.65466,0.07044,-7e-05],"force_p95":53.79184,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":63.44178,"mean_force":38.42999,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46392,-0.03872,0.14718]},{"body_a":"grasp_target","body_b":"hand","contact_count":40.0,"contact_point_centroid":[0.45666,-0.0128,0.03924],"force_p95":3.61233,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.98226,"mean_force":1.6655,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38324,-0.0026,0.05203]},{"body_a":"world","body_b":"grasp_target","contact_count":3933.0,"contact_point_centroid":[0.44037,-0.01931,-0.00213],"force_p95":0.13741,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.31183,"mean_force":0.138,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.40812,-0.00601,0.14209]},{"body_a":"grasp_target","body_b":"link7","contact_count":27.0,"contact_point_centroid":[0.4817,-0.00492,0.0112],"force_p95":0.64588,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.68904,"mean_force":0.2447,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37321,-0.00265,0.05351]},{"body_a":"world","body_b":"grasp_target","contact_count":2404.0,"contact_point_centroid":[0.43545,-0.01918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.44414,-0.01641,0.19053]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.43545,-0.01918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46421,-0.03881,0.14776]},{"body_a":"world","body_b":"grasp_target","contact_count":1764.0,"contact_point_centroid":[0.43545,-0.01918,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45405,-0.03656,0.14263]}],"total_contact_groups":27},"final_pose_error":0.01284,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.43545,-0.01918,0.01602],"final_tcp_position":[0.51956,-0.05727,0.42458],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":273014.88288,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.43545,-0.01918,0.01602],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.31701,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":201.83717,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4908.0,"raw_peak_contact_force":1428.84052,"subtask_id":"pre_grasp","tcp_end":[0.41553,-0.01276,0.17556],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1609,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":601.0,"n_steps_budget":660.0,"object_pos_end":[0.43545,-0.01918,0.01602],"object_pos_start":[0.43545,-0.01918,0.01602],"object_to_goal_dist_end":0.31701,"object_to_goal_dist_start":0.31701,"object_z_max":0.01602,"peak_contact_force":92.3687,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2983.0,"raw_peak_contact_force":896.52106,"tcp_end":[0.46628,-0.03441,0.15581],"tcp_start":[0.41553,-0.01276,0.17556],"tcp_to_object_dist_end":0.14396,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43545,-0.01918,0.01602],"object_pos_start":[0.43545,-0.01918,0.01602],"object_to_goal_dist_end":0.31701,"object_to_goal_dist_start":0.31701,"object_z_max":0.01602,"peak_contact_force":36.2074,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2520.0,"raw_peak_contact_force":63.44178,"tcp_end":[0.46393,-0.03868,0.14715],"tcp_start":[0.46628,-0.03441,0.15581],"tcp_to_object_dist_end":0.1356,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":441.0,"n_steps_budget":600.0,"object_pos_end":[0.43545,-0.01918,0.01602],"object_pos_start":[0.43545,-0.01918,0.01602],"object_to_goal_dist_end":0.31701,"object_to_goal_dist_start":0.31701,"object_z_max":0.01602,"peak_contact_force":273014.88288,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4093.0,"raw_peak_contact_force":212.24407,"subtask_id":"lift_clearance","tcp_end":[0.44794,-0.03598,0.14325],"tcp_start":[0.46393,-0.03868,0.14715],"tcp_to_object_dist_end":0.12894,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":207.0,"n_steps_budget":1000.0,"object_pos_end":[0.43545,-0.01918,0.01602],"object_pos_start":[0.43545,-0.01918,0.01602],"object_to_goal_dist_end":0.31701,"object_to_goal_dist_start":0.31701,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1860.0,"raw_peak_contact_force":410.16268,"tcp_end":[0.51681,-0.0591,0.29897],"tcp_start":[0.44794,-0.03598,0.14325],"tcp_to_object_dist_end":0.29711,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.43545,-0.01918,0.01602],"object_pos_start":[0.43545,-0.01918,0.01602],"object_to_goal_dist_end":0.31701,"object_to_goal_dist_start":0.31701,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_accuracy","tcp_end":[0.517,-0.05855,0.30082],"tcp_start":[0.51681,-0.0591,0.29897],"tcp_to_object_dist_end":0.29885,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.43545,-0.01918,0.01602],"object_pos_start":[0.43545,-0.01918,0.01602],"object_to_goal_dist_end":0.31701,"object_to_goal_dist_start":0.31701,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1028.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51835,-0.05725,0.33736],"tcp_start":[0.517,-0.05855,0.30082],"tcp_to_object_dist_end":0.33404,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.43545,-0.01918,0.01602],"object_pos_start":[0.43545,-0.01918,0.01602],"object_to_goal_dist_end":0.31701,"object_to_goal_dist_start":0.31701,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51956,-0.05727,0.42458],"tcp_start":[0.51835,-0.05725,0.33736],"tcp_to_object_dist_end":0.41887,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `37495cb43897015e78e007c86af160d11c8460c1ce7249e5c03dce38206c0daf`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":40.0,"average_failure_rate":0.25,"average_mean_iterations":54.33125,"average_solve_count":160.0,"average_success_count":120.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_grasp.lateral_offset_x":-0.01344,"align_grasp.lateral_offset_y":0.00211,"approach_goal.transport_speed":0.07463,"approach_object.approach_speed":0.05375,"descend_place.placement_offset_z":0.00045,"lift.lift_height":0.19861,"lift.lift_speed":0.08922},"optimized_scores":{"best_composite_score":-0.38537,"best_fitness_score":0.14463,"best_task_score":0.10998},"replay_outcomes":[{"contacts":{"omitted_contact_groups":11,"reported_contact_groups":[{"body_a":"world","body_b":"link6","contact_count":886.0,"contact_point_centroid":[0.62811,-0.00429,-0.00047],"force_p95":196.58603,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":1331.25285,"mean_force":202.31099,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.38257,-0.00423,0.11538]},{"body_a":"world","body_b":"link6","contact_count":542.0,"contact_point_centroid":[0.63087,-0.009,-0.0003],"force_p95":329.23821,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":423.55888,"mean_force":284.19245,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.404,-0.01025,0.15087]},{"body_a":"link5","body_b":"hand","contact_count":188.0,"contact_point_centroid":[0.52705,-0.00384,0.16982],"force_p95":343.06016,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":372.1988,"mean_force":294.94104,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.4962,0.07428,0.1953]},{"body_a":"world","body_b":"link6","contact_count":29.0,"contact_point_centroid":[0.65531,0.00373,-0.00041],"force_p95":335.54104,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":336.01064,"mean_force":272.80416,"phase_index":5.0,"phase_name":"descend_place","phase_type":"descend","tcp_position_centroid":[0.50508,0.08838,0.19313]},{"body_a":"link5","body_b":"hand","contact_count":13.0,"contact_point_centroid":[0.52983,0.01806,0.17954],"force_p95":229.05448,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":256.18089,"mean_force":173.74041,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51474,0.09064,0.229]},{"body_a":"link5","body_b":"hand","contact_count":200.0,"contact_point_centroid":[0.52347,0.01338,0.15682],"force_p95":250.34877,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":253.56048,"mean_force":229.23367,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.51208,0.08699,0.20696]},{"body_a":"world","body_b":"link6","contact_count":74.0,"contact_point_centroid":[0.65646,0.00717,-0.00011],"force_p95":73.55156,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":177.85831,"mean_force":53.07206,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.51176,0.08562,0.20045]},{"body_a":"world","body_b":"link6","contact_count":6.0,"contact_point_centroid":[0.63856,-0.01269,-9e-05],"force_p95":108.45483,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":109.37902,"mean_force":91.8014,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.42439,-0.01379,0.16927]},{"body_a":"world","body_b":"link6","contact_count":450.0,"contact_point_centroid":[0.63839,-0.01263,-0.00013],"force_p95":77.32598,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":109.15024,"mean_force":71.46925,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.42435,-0.01374,0.16938]},{"body_a":"left_finger","body_b":"link5","contact_count":163.0,"contact_point_centroid":[0.50028,0.059,0.22635],"force_p95":2.45648,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.86634,"mean_force":1.15689,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.51537,0.0939,0.23804]},{"body_a":"grasp_target","body_b":"hand","contact_count":38.0,"contact_point_centroid":[0.44073,-0.02149,0.0434],"force_p95":3.45739,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":3.71072,"mean_force":1.51343,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.37945,-0.0023,0.05388]},{"body_a":"world","body_b":"grasp_target","contact_count":3919.0,"contact_point_centroid":[0.4222,-0.02557,-0.00212],"force_p95":0.13762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.24634,"mean_force":0.13749,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.39531,-0.00393,0.12578]},{"body_a":"left_finger","body_b":"link5","contact_count":49.0,"contact_point_centroid":[0.50178,0.05195,0.20425],"force_p95":0.50139,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.51087,"mean_force":0.46817,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.51313,0.08913,0.22019]},{"body_a":"grasp_target","body_b":"link7","contact_count":9.0,"contact_point_centroid":[0.47183,-0.00709,0.00788],"force_p95":0.37293,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.37354,"mean_force":0.246,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.3677,-0.00234,0.04982]},{"body_a":"world","body_b":"grasp_target","contact_count":2168.0,"contact_point_centroid":[0.41701,-0.02545,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"align_grasp","phase_type":"align","tcp_position_centroid":[0.404,-0.01025,0.15087]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.41701,-0.02545,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.42435,-0.01374,0.16938]}],"total_contact_groups":27},"final_pose_error":0.02007,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.41701,-0.02545,0.01602],"final_tcp_position":[0.51743,0.10008,0.31077],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1331.25285,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41701,-0.02545,0.01602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":194.68695,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4871.0,"raw_peak_contact_force":1331.25285,"subtask_id":"pre_grasp","tcp_end":[0.38543,-0.00716,0.13339],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.12291,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":542.0,"n_steps_budget":600.0,"object_pos_end":[0.41701,-0.02545,0.01602],"object_pos_start":[0.41701,-0.02545,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":276.93437,"phase_name":"align_grasp","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2710.0,"raw_peak_contact_force":423.55888,"tcp_end":[0.424,-0.01363,0.16992],"tcp_start":[0.38543,-0.00716,0.13339],"tcp_to_object_dist_end":0.15451,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41701,-0.02545,0.01602],"object_pos_start":[0.41701,-0.02545,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":69.51046,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2582.0,"raw_peak_contact_force":109.15024,"tcp_end":[0.42441,-0.01377,0.16924],"tcp_start":[0.424,-0.01363,0.16992],"tcp_to_object_dist_end":0.15384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":358.0,"n_steps_budget":600.0,"object_pos_end":[0.41701,-0.02545,0.01602],"object_pos_start":[0.41701,-0.02545,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":2930.0,"raw_peak_contact_force":109.37902,"subtask_id":"lift_clearance","tcp_end":[0.41566,-0.02427,0.20479],"tcp_start":[0.42441,-0.01377,0.16924],"tcp_to_object_dist_end":0.18878,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.41701,-0.02545,0.01602],"object_pos_start":[0.41701,-0.02545,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"approach_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":8264.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.48972,0.06137,0.20584],"tcp_start":[0.41566,-0.02427,0.20479],"tcp_to_object_dist_end":0.22103,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":10.0,"n_steps":214.0,"n_steps_budget":1000.0,"object_pos_end":[0.41701,-0.02545,0.01602],"object_pos_start":[0.41701,-0.02545,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":285.24156,"phase_name":"descend_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2010.0,"raw_peak_contact_force":372.1988,"subtask_id":"place_accuracy","tcp_end":[0.51033,0.08672,0.19854],"tcp_start":[0.48972,0.06137,0.20584],"tcp_to_object_dist_end":0.23367,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.41701,-0.02545,0.01602],"object_pos_start":[0.41701,-0.02545,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":253.56048,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1350.0,"raw_peak_contact_force":253.56048,"tcp_end":[0.51379,0.09019,0.22785],"tcp_start":[0.51033,0.08672,0.19854],"tcp_to_object_dist_end":0.26002,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.41701,-0.02545,0.01602],"object_pos_start":[0.41701,-0.02545,0.01602],"object_to_goal_dist_end":0.33112,"object_to_goal_dist_start":0.33112,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2348.0,"raw_peak_contact_force":256.18089,"tcp_end":[0.51743,0.10008,0.31077],"tcp_start":[0.51379,0.09019,0.22785],"tcp_to_object_dist_end":0.33573,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```