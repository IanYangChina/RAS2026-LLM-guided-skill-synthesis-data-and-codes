## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.1931 | 0.38 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.3961 | 0.36 | ❌ rejected |
| 8 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.1413 | 0.37 | ❌ rejected |
| 7 | approach → push → retract | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 4 | -0.0682 | 0.00 | ❌ rejected |
| 6 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | admittance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 4 | 0.1801 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.38 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`
- Frozen object start: [0.5531667326686841, 0.0013593063377233885, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5531667326686841, 0.0013593063377233885, 0.025)
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
  frozen_object_start: [0.5532, 0.0014, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5531667326686841, 0.0013593063377233885, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0532, -0.1514, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.810, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

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
| `object` | offset from object initial position (0.5531667326686841, 0.0013593063377233885, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.193) — your mutation base

```yaml
skill: push_to_goal
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
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
- id: align_1
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
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: 0.193
- **task_score** (E): 0.381
- **fitness_score**: 0.436  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.167
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1426 |
| contact_1 | 0.67 | 1.00 | 0.1103 |
| push_1 | 0.67 | 1.00 | 0.1702 |
| retract_1 | 1.00 | 1.00 | 0.1303 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.524, 0.006, 0.163) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.67 / force_exceeded | (0.524, 0.006, 0.163)→(0.527, 0.006, 0.053) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.667 | 50595.773 | 0.245 |
| push_1 | push | 0.67 / step_budget | (0.527, 0.006, 0.053)→(0.494, -0.159, 0.046) | (0.531, 0.007, 0.025)→(0.523, -0.053, 0.025) | 0.161→0.101 | 1.00 / 4.000 | 0.245 | 72.982 |
| retract_1 | retract | 1.00 / step_budget | (0.494, -0.159, 0.046)→(0.491, -0.159, 0.176) | (0.523, -0.053, 0.025)→(0.523, -0.053, 0.025) | 0.101→0.101 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.403
- lateral_force_integral: None
- approach_alignment: 0.876
- goal_progress: 0.401
- terminal_score: 0.401
- phase_score: 0.489
- phase_breakdown.push_to_goal_score: 0.632
- phase_breakdown.reach_pre_contact_score: 0.157

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.454
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.431
- **Median Q (composite search score)**: 0.265
- **K-run variance**: 0.0150
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.381


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8d5a7e825d9524a0954b44a69bda19e1d764760f64bb1262d03aec3c389fadbb`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c4094dd933e0897d422d7ea261a82b80810f7dec183b19c1da5b940157e7d0c4`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39227,"average_solve_count":181.0,"average_success_count":181.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.29826,"contact_1.contact_force_threshold":4.7653,"contact_1.descent_speed":0.06831,"push_1.push_distance":0.05398,"push_1.push_speed":0.0243,"push_1.push_tolerance":0.01489,"retract_1.retract_speed":0.11609},"optimized_scores":{"best_composite_score":0.29384,"best_fitness_score":0.45384,"best_task_score":0.40076},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":487.0,"contact_point_centroid":[0.54507,-0.02581,0.0506],"force_p95":67.73023,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":68.21237,"mean_force":48.06552,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53701,-0.03323,0.05168]},{"body_a":"world","body_b":"push_box","contact_count":2731.0,"contact_point_centroid":[0.54123,-0.04867,-0.00011],"force_p95":46.20571,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.92365,"mean_force":8.92219,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51566,-0.09012,0.0479]},{"body_a":"world","body_b":"push_box","contact_count":1084.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5205,0.00054,0.23211]},{"body_a":"world","body_b":"push_box","contact_count":2424.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54434,0.00114,0.10413]},{"body_a":"world","body_b":"push_box","contact_count":1576.0,"contact_point_centroid":[0.53728,-0.06139,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.4895,-0.15626,0.10965]}],"total_contact_groups":5},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53728,-0.06139,0.02499],"final_tcp_position":[0.48968,-0.15621,0.17576],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":271.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1084.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.54309,0.0011,0.16193],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":606.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2424.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.54829,0.00123,0.05247],"tcp_start":[0.54309,0.0011,0.16193],"tcp_to_object_dist_end":0.02791,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53728,-0.06139,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.09613,"object_to_goal_dist_start":0.16043,"object_z_max":0.03531,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3218.0,"raw_peak_contact_force":68.21237,"subtask_id":"push_to_goal","tcp_end":[0.49231,-0.15695,0.04549],"tcp_start":[0.54829,0.00123,0.05247],"tcp_to_object_dist_end":0.10759,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":394.0,"n_steps_budget":810.0,"object_pos_end":[0.53728,-0.06139,0.02499],"object_pos_start":[0.53728,-0.06139,0.02499],"object_to_goal_dist_end":0.09613,"object_to_goal_dist_start":0.09613,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1576.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.48968,-0.15621,0.17576],"tcp_start":[0.49231,-0.15695,0.04549],"tcp_to_object_dist_end":0.18436,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0,"average_solve_count":125.0,"average_success_count":125.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1448,"contact_1.contact_force_threshold":5.62705,"contact_1.descent_speed":0.0674,"push_1.push_distance":0.12188,"push_1.push_speed":0.08921,"push_1.push_tolerance":0.01825,"retract_1.retract_speed":0.22193},"optimized_scores":{"best_composite_score":0.26493,"best_fitness_score":0.42493,"best_task_score":0.31143},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":394.0,"contact_point_centroid":[0.53318,0.00973,0.0508],"force_p95":73.87485,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.93416,"mean_force":49.07856,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52586,0.00173,0.05184]},{"body_a":"world","body_b":"push_box","contact_count":2980.0,"contact_point_centroid":[0.52957,-0.01245,-9e-05],"force_p95":38.15932,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.87379,"mean_force":6.8052,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50948,-0.07217,0.04786]},{"body_a":"world","body_b":"push_box","contact_count":1108.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51357,0.01516,0.23227]},{"body_a":"world","body_b":"push_box","contact_count":2428.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52909,0.03377,0.10474]},{"body_a":"world","body_b":"push_box","contact_count":1460.0,"contact_point_centroid":[0.52785,-0.02182,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49171,-0.1485,0.10993]}],"total_contact_groups":5},"final_pose_error":0.01999,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52785,-0.02182,0.02499],"final_tcp_position":[0.49194,-0.14844,0.17612],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":277.0,"n_steps_budget":720.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1108.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.52884,0.03142,0.16221],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13755,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":607.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2428.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.53203,0.03623,0.05246],"tcp_start":[0.52884,0.03142,0.16221],"tcp_to_object_dist_end":0.02786,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52785,-0.02182,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.13117,"object_to_goal_dist_start":0.1905,"object_z_max":0.0353,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3374.0,"raw_peak_contact_force":74.93416,"subtask_id":"push_to_goal","tcp_end":[0.49441,-0.1491,0.04594],"tcp_start":[0.53203,0.03623,0.05246],"tcp_to_object_dist_end":0.13326,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":365.0,"n_steps_budget":600.0,"object_pos_end":[0.52785,-0.02182,0.02499],"object_pos_start":[0.52785,-0.02182,0.02499],"object_to_goal_dist_end":0.13117,"object_to_goal_dist_start":0.13117,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1460.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49194,-0.14844,0.17612],"tcp_start":[0.49441,-0.1491,0.04594],"tcp_to_object_dist_end":0.20041,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.34737,"average_solve_count":190.0,"average_success_count":190.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.1721,"contact_1.contact_force_threshold":9.49089,"contact_1.descent_speed":0.05496,"push_1.push_distance":0.05013,"push_1.push_speed":0.01034,"push_1.push_tolerance":0.0318,"retract_1.retract_speed":0.20749},"optimized_scores":{"best_composite_score":0.02055,"best_fitness_score":0.43055,"best_task_score":0.43135},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":449.0,"contact_point_centroid":[0.50738,-0.04652,0.05029],"force_p95":74.74029,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.79907,"mean_force":49.75729,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49993,-0.05412,0.05138]},{"body_a":"world","body_b":"push_box","contact_count":2830.0,"contact_point_centroid":[0.50335,-0.06435,-0.0001],"force_p95":45.39656,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":49.3842,"mean_force":8.21881,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49676,-0.10948,0.04781]},{"body_a":"world","body_b":"push_box","contact_count":996.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50037,-0.00761,0.23363]},{"body_a":"world","body_b":"push_box","contact_count":2568.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49969,-0.01721,0.10636]},{"body_a":"world","body_b":"push_box","contact_count":1476.0,"contact_point_centroid":[0.50247,-0.07539,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49201,-0.171,0.10946]}],"total_contact_groups":5},"final_pose_error":0.01976,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50247,-0.07539,0.02499],"final_tcp_position":[0.49224,-0.17097,0.17569],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":75.79907,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":249.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":996.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_pre_contact","tcp_end":[0.50152,-0.01587,0.16417],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13925,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":642.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2568.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_pre_contact","tcp_end":[0.50049,-0.01857,0.05281],"tcp_start":[0.50152,-0.01587,0.16417],"tcp_to_object_dist_end":0.02812,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50247,-0.07539,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.07465,"object_to_goal_dist_start":0.13127,"object_z_max":0.03532,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3279.0,"raw_peak_contact_force":75.79907,"subtask_id":"push_to_goal","tcp_end":[0.49471,-0.17175,0.04528],"tcp_start":[0.50049,-0.01857,0.05281],"tcp_to_object_dist_end":0.09877,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":369.0,"n_steps_budget":600.0,"object_pos_end":[0.50247,-0.07539,0.02499],"object_pos_start":[0.50247,-0.07539,0.02499],"object_to_goal_dist_end":0.07465,"object_to_goal_dist_start":0.07465,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1476.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49224,-0.17097,0.17569],"tcp_start":[0.49471,-0.17175,0.04528],"tcp_to_object_dist_end":0.17875,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```