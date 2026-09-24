## Search State

- **Seed**: 4
- **Iteration**: 4 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3415 | 0.74 | ❌ rejected |
| 2 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0329 | 0.50 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0692 | 0.02 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3434 | 0.75 | ✅ accepted |

**Proposal policy**: task_score is 0.74 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.746, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.342) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
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
  control: impedance_control
  termination: contact_detected
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
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

- **Composite score**: 0.342
- **task_score** (E): 0.744
- **fitness_score**: 0.702  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2798 |
| contact_1 | 1.00 | 1.00 | 0.0481 |
| push_1 | 1.00 | 1.00 | 0.1273 |
| retract_1 | 0.00 | 1.00 | 0.1400 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.525, 0.081, 0.035) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.525, 0.081, 0.035)→(0.527, 0.036, 0.021) | (0.531, 0.007, 0.025)→(0.533, -0.001, 0.025) | 0.161→0.154 | 1.00 / 3.667 | 5.517 | 14.308 |
| push_1 | push | 1.00 / step_budget | (0.527, 0.036, 0.021)→(0.504, -0.089, 0.026) | (0.533, -0.001, 0.025)→(0.524, -0.119, 0.029) | 0.154→0.043 | 1.00 / 3.000 | 79.311 | 110.050 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.089, 0.026)→(0.498, 0.037, 0.088) | (0.524, -0.119, 0.029)→(0.520, -0.113, 0.025) | 0.043→0.045 | 1.00 / 4.000 | 0.245 | 62.038 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.500
- goal_progress: 0.970
- terminal_score: 0.970
- phase_score: 0.839
- phase_breakdown.push_score: 0.833
- phase_breakdown.approach_score: 0.821
- phase_breakdown.contact_score: 0.860

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.891
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.970
- **Median Q (composite search score)**: 0.276
- **K-run variance**: 0.0186
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.402


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11864,"average_solve_count":236.0,"average_success_count":236.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0391,"contact_1.contact_force":19.38249,"push_1.push_depth":0.1,"push_1.push_distance":0.06896,"push_1.push_speed":0.07868,"retract_1.speed":0.02298},"optimized_scores":{"best_composite_score":0.2758,"best_fitness_score":0.6358,"best_task_score":0.63308},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":984.0,"contact_point_centroid":[0.56227,-0.04693,0.05422],"force_p95":122.31382,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":135.54875,"mean_force":80.24893,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52649,-0.03239,0.02444]},{"body_a":"world","body_b":"push_box","contact_count":1941.0,"contact_point_centroid":[0.557,-0.07966,-0.00038],"force_p95":83.95732,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":96.14914,"mean_force":51.45018,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52636,-0.03297,0.02453]},{"body_a":"world","body_b":"push_box","contact_count":3602.0,"contact_point_centroid":[0.53634,-0.10323,-3e-05],"force_p95":0.47628,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":84.00721,"mean_force":0.6614,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50307,-0.0248,0.05814]},{"body_a":"attachment","body_b":"push_box","contact_count":986.0,"contact_point_centroid":[0.54639,-0.04052,0.05545],"force_p95":78.29417,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.9336,"mean_force":50.22427,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52656,-0.03222,0.02444]},{"body_a":"push_box","body_b":"link7","contact_count":63.0,"contact_point_centroid":[0.55067,-0.09471,0.05702],"force_p95":70.92386,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.33896,"mean_force":29.86049,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50846,-0.087,0.03102]},{"body_a":"attachment","body_b":"push_box","contact_count":84.0,"contact_point_centroid":[0.53286,-0.08844,0.06174],"force_p95":44.42529,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.86098,"mean_force":15.23358,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50776,-0.08421,0.03162]},{"body_a":"attachment","body_b":"push_box","contact_count":93.0,"contact_point_centroid":[0.5536,0.02269,0.04038],"force_p95":12.47403,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":16.78547,"mean_force":5.30849,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54728,0.03461,0.02225]},{"body_a":"world","body_b":"push_box","contact_count":1885.0,"contact_point_centroid":[0.55331,-4e-05,-1e-05],"force_p95":2.58968,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":8.17879,"mean_force":0.51241,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54425,0.05345,0.02941]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52126,0.03684,0.16994]}],"total_contact_groups":9},"final_pose_error":0.14104,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53563,-0.10315,0.02499],"final_tcp_position":[0.50115,0.02571,0.08334],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":135.54875,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54466,0.07412,0.04176],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07515,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":520.0,"n_steps_budget":600.0,"object_pos_end":[0.55562,-0.00664,0.02487],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15377,"object_to_goal_dist_start":0.16043,"object_z_max":0.02511,"peak_contact_force":0.6027,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1978.0,"raw_peak_contact_force":16.78547,"tcp_end":[0.54808,0.03036,0.02074],"tcp_start":[0.54466,0.07412,0.04176],"tcp_to_object_dist_end":0.03799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54194,-0.11523,0.03116],"object_pos_start":[0.55562,-0.00664,0.02487],"object_to_goal_dist_end":0.05482,"object_to_goal_dist_start":0.15377,"object_z_max":0.03116,"peak_contact_force":123.94185,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3911.0,"raw_peak_contact_force":135.54875,"tcp_end":[0.50963,-0.09143,0.02992],"tcp_start":[0.54808,0.03036,0.02074],"tcp_to_object_dist_end":0.04015,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53563,-0.10315,0.02499],"object_pos_start":[0.54194,-0.11523,0.03116],"object_to_goal_dist_end":0.05886,"object_to_goal_dist_start":0.05482,"object_z_max":0.03444,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3749.0,"raw_peak_contact_force":84.00721,"tcp_end":[0.50115,0.02571,0.08334],"tcp_start":[0.50963,-0.09143,0.02992],"tcp_to_object_dist_end":0.1456,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80864,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08958,"contact_1.contact_force":11.97722,"push_1.push_depth":0.09989,"push_1.push_distance":0.06397,"push_1.push_speed":0.08193,"retract_1.speed":0.09673},"optimized_scores":{"best_composite_score":0.21744,"best_fitness_score":0.57744,"best_task_score":0.62772},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":949.0,"contact_point_centroid":[0.54826,-0.01322,0.05463],"force_p95":107.20134,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":120.45383,"mean_force":70.4441,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51729,0.00324,0.02333]},{"body_a":"attachment","body_b":"push_box","contact_count":954.0,"contact_point_centroid":[0.53669,-0.00554,0.0534],"force_p95":92.20992,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":99.13193,"mean_force":51.64678,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51737,0.00358,0.02331]},{"body_a":"world","body_b":"push_box","contact_count":3693.0,"contact_point_centroid":[0.52481,-0.08353,-3e-05],"force_p95":0.25651,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":88.28411,"mean_force":0.48093,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50034,0.02071,0.06902]},{"body_a":"push_box","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.54659,-0.06563,0.05572],"force_p95":81.82573,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":86.84714,"mean_force":38.78136,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50564,-0.05285,0.02958]},{"body_a":"world","body_b":"push_box","contact_count":1820.0,"contact_point_centroid":[0.54251,-0.04897,-0.00032],"force_p95":69.83459,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.05388,"mean_force":47.70897,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51705,0.00155,0.02355]},{"body_a":"attachment","body_b":"push_box","contact_count":61.0,"contact_point_centroid":[0.52863,-0.05696,0.0603],"force_p95":63.41488,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":80.34062,"mean_force":23.34767,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50503,-0.05037,0.03031]},{"body_a":"attachment","body_b":"push_box","contact_count":96.0,"contact_point_centroid":[0.53656,0.05805,0.03451],"force_p95":9.26061,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.44931,"mean_force":3.74119,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5312,0.06997,0.02061]},{"body_a":"world","body_b":"push_box","contact_count":1881.0,"contact_point_centroid":[0.53672,0.03533,-1e-05],"force_p95":1.89581,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.76628,"mean_force":0.44004,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52924,0.08978,0.02366]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51447,0.05539,0.16429]}],"total_contact_groups":9},"final_pose_error":0.07888,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52423,-0.08335,0.02499],"final_tcp_position":[0.49854,0.0842,0.10653],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":120.45383,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53083,0.111,0.03141],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07455,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":523.0,"n_steps_budget":600.0,"object_pos_end":[0.53864,0.0289,0.02496],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18302,"object_to_goal_dist_start":0.1905,"object_z_max":0.02507,"peak_contact_force":7.21143,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1977.0,"raw_peak_contact_force":11.44931,"tcp_end":[0.53176,0.06569,0.0201],"tcp_start":[0.53083,0.111,0.03141],"tcp_to_object_dist_end":0.03774,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":959.0,"n_steps_budget":1000.0,"object_pos_end":[0.53017,-0.08728,0.03106],"object_pos_start":[0.53864,0.0289,0.02496],"object_to_goal_dist_end":0.06986,"object_to_goal_dist_start":0.18302,"object_z_max":0.03107,"peak_contact_force":113.84086,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3723.0,"raw_peak_contact_force":120.45383,"tcp_end":[0.50658,-0.05617,0.02838],"tcp_start":[0.53176,0.06569,0.0201],"tcp_to_object_dist_end":0.03913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52423,-0.08335,0.02499],"object_pos_start":[0.53017,-0.08728,0.03106],"object_to_goal_dist_end":0.07092,"object_to_goal_dist_start":0.06986,"object_z_max":0.03376,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3799.0,"raw_peak_contact_force":88.28411,"tcp_end":[0.49854,0.0842,0.10653],"tcp_start":[0.50658,-0.05617,0.02838],"tcp_to_object_dist_end":0.1881,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.5,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.08651,"contact_1.contact_force":7.65774,"push_1.push_depth":0.09994,"push_1.push_distance":0.1184,"push_1.push_speed":0.09473,"retract_1.speed":0.03736},"optimized_scores":{"best_composite_score":0.5313,"best_fitness_score":0.8913,"best_task_score":0.9702},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1125.0,"contact_point_centroid":[0.50941,-0.10759,-0.00014],"force_p95":59.71687,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.14593,"mean_force":23.52921,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49818,-0.05219,0.02015]},{"body_a":"attachment","body_b":"push_box","contact_count":753.0,"contact_point_centroid":[0.51262,-0.06168,0.04493],"force_p95":51.28523,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.86007,"mean_force":23.91091,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49817,-0.05046,0.02011]},{"body_a":"push_box","body_b":"link7","contact_count":531.0,"contact_point_centroid":[0.52502,-0.05353,0.05282],"force_p95":47.56756,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.44324,"mean_force":31.03321,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49898,-0.03167,0.02036]},{"body_a":"attachment","body_b":"push_box","contact_count":86.0,"contact_point_centroid":[0.50596,0.00258,0.0342],"force_p95":11.86059,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.68914,"mean_force":4.37363,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49964,0.01443,0.02145]},{"body_a":"push_box","body_b":"link7","contact_count":46.0,"contact_point_centroid":[0.52434,-0.13841,0.05034],"force_p95":9.1558,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.8235,"mean_force":4.88188,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49379,-0.11291,0.02021]},{"body_a":"world","body_b":"push_box","contact_count":3845.0,"contact_point_centroid":[0.50081,-0.1533,-2e-05],"force_p95":0.25119,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.1057,"mean_force":0.31411,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49293,-0.05486,0.04593]},{"body_a":"world","body_b":"push_box","contact_count":1928.0,"contact_point_centroid":[0.5048,-0.01993,-1e-05],"force_p95":1.76854,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.22164,"mean_force":0.44361,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49821,0.03556,0.02523]},{"body_a":"attachment","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.51006,-0.13067,0.05011],"force_p95":1.03385,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.0646,"mean_force":0.48222,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49582,-0.11879,0.01978]},{"body_a":"world","body_b":"push_box","contact_count":3544.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49924,0.02861,0.1662]}],"total_contact_groups":9},"final_pose_error":0.16865,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50097,-0.15379,0.02499],"final_tcp_position":[0.49385,0.00026,0.07266],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":74.14593,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":886.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3544.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.05778,0.03322],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":525.0,"n_steps_budget":600.0,"object_pos_end":[0.50608,-0.02619,0.02491],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12396,"object_to_goal_dist_start":0.13127,"object_z_max":0.02513,"peak_contact_force":8.73553,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2014.0,"raw_peak_contact_force":14.68914,"tcp_end":[0.50003,0.01052,0.02085],"tcp_start":[0.50029,0.05778,0.03322],"tcp_to_object_dist_end":0.03742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":798.0,"n_steps_budget":900.0,"object_pos_end":[0.49957,-0.1555,0.02514],"object_pos_start":[0.50608,-0.02619,0.02491],"object_to_goal_dist_end":0.00552,"object_to_goal_dist_start":0.12396,"object_z_max":0.02839,"peak_contact_force":0.15008,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2409.0,"raw_peak_contact_force":74.14593,"tcp_end":[0.49588,-0.11869,0.01983],"tcp_start":[0.50003,0.01052,0.02085],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50097,-0.15379,0.02499],"object_pos_start":[0.49957,-0.1555,0.02514],"object_to_goal_dist_end":0.00391,"object_to_goal_dist_start":0.00552,"object_z_max":0.0274,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3895.0,"raw_peak_contact_force":13.8235,"tcp_end":[0.49385,0.00026,0.07266],"tcp_start":[0.49588,-0.11869,0.01983],"tcp_to_object_dist_end":0.16141,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```