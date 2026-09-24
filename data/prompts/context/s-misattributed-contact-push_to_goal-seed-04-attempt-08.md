## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | impedance_control | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 6 | 0.0304 | 0.09 | ❌ rejected |
| 7 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | force_exceeded | 7 | -0.0045 | 0.00 | ❌ rejected |
| 6 | approach → descend → push | linear_cartesian | linear_cartesian | impedance_motion | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | pose_tolerance | 5 | 0.1573 | 0.00 | ❌ rejected |
| 5 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4202 | 0.80 | ❌ rejected |
| 4 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4288 | 0.84 | ✅ accepted |

**Proposal policy**: task_score is 0.09 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.839, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.030) — your mutation base

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

- **Composite score**: 0.030
- **task_score** (E): 0.094
- **fitness_score**: 0.138  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.222
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.330

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_behind | 1.00 | 1.00 | 0.1657 |
| descend_contact | 0.00 | 1.00 | 0.1055 |
| push_to_goal | 0.67 | 1.00 | 0.0390 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_behind | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.545, 0.061, 0.156) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| descend_contact | descend | 0.00 / step_budget | (0.545, 0.061, 0.156)→(0.547, 0.066, 0.051) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 50596.300 | 3.304 |
| push_to_goal | push | 0.67 / force_exceeded | (0.547, 0.066, 0.051)→(0.535, 0.029, 0.046) | (0.531, 0.007, 0.025)→(0.525, -0.007, 0.025) | 0.161→0.146 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.000
- lateral_force_integral: None
- approach_alignment: 0.463
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.104
- phase_breakdown.push_object_to_goal_score: 0.000
- phase_breakdown.approach_object_score: 0.348

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.290
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.283
- **Median Q (composite search score)**: 0.065
- **K-run variance**: 0.0025
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: approach_behind.approach_z_offset
- **Final σ (mean)**: 0.313


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.67089,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.21049,"approach_behind.approach_z_offset":0.08579,"descend_contact.descend_force_threshold":10.75414,"push_to_goal.push_distance":0.12415,"push_to_goal.push_force_threshold":17.76745,"push_to_goal.push_speed":0.04048},"optimized_scores":{"best_composite_score":-0.03966,"best_fitness_score":0.29034,"best_task_score":0.28335},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":631.0,"contact_point_centroid":[0.54943,0.0055,0.04385],"force_p95":7.50053,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":9.42248,"mean_force":3.74707,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55059,0.01738,0.04354]},{"body_a":"world","body_b":"push_box","contact_count":2441.0,"contact_point_centroid":[0.54784,-0.01689,-2e-05],"force_p95":4.20599,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.6938,"mean_force":1.26195,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.55588,0.0333,0.0436]},{"body_a":"world","body_b":"push_box","contact_count":2408.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.53149,0.02825,0.20772]},{"body_a":"world","body_b":"push_box","contact_count":1616.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.56556,0.05885,0.07849]}],"total_contact_groups":4},"final_pose_error":0.05284,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53513,-0.04053,0.02506],"final_tcp_position":[0.54375,-0.00461,0.04392],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":9.42248,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":602.0,"n_steps_budget":660.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1616.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.56524,0.05725,0.11628],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10772,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":404.0,"n_steps_budget":600.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":1.82737,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3072.0,"raw_peak_contact_force":9.42248,"subtask_id":"approach_object","tcp_end":[0.56824,0.06052,0.04859],"tcp_start":[0.56524,0.05725,0.11628],"tcp_to_object_dist_end":0.06545,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53513,-0.04053,0.02506],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.11497,"object_to_goal_dist_start":0.16043,"object_z_max":0.0252,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2408.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_object_to_goal","tcp_end":[0.54375,-0.00461,0.04392],"tcp_start":[0.56824,0.06052,0.04859],"tcp_to_object_dist_end":0.04148,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.01754,"average_solve_count":57.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.20698,"approach_behind.approach_z_offset":0.15,"descend_contact.descend_force_threshold":6.89636,"push_to_goal.push_distance":0.11387,"push_to_goal.push_force_threshold":16.12648,"push_to_goal.push_speed":0.05876},"optimized_scores":{"best_composite_score":0.06489,"best_fitness_score":0.06156,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2116.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.52411,0.0448,0.23748]},{"body_a":"world","body_b":"push_box","contact_count":2456.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.54971,0.0927,0.11186]},{"body_a":"world","body_b":"push_box","contact_count":892.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.54699,0.08467,0.04682]}],"total_contact_groups":3},"final_pose_error":0.08936,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5366,0.03695,0.02499],"final_tcp_position":[0.54452,0.07391,0.04558],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":529.0,"n_steps_budget":600.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2456.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.54985,0.08997,0.17759],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16209,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":614.0,"n_steps_budget":810.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":892.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.55201,0.09577,0.05156],"tcp_start":[0.54985,0.08997,0.17759],"tcp_to_object_dist_end":0.06635,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":223.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2116.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_object_to_goal","tcp_end":[0.54452,0.07391,0.04558],"tcp_start":[0.55201,0.09577,0.05156],"tcp_to_object_dist_end":0.04304,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.77049,"average_solve_count":61.0,"average_success_count":61.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_behind.approach_speed":0.2873,"approach_behind.approach_z_offset":0.14262,"descend_contact.descend_force_threshold":2.76695,"push_to_goal.push_distance":0.23621,"push_to_goal.push_force_threshold":5.82749,"push_to_goal.push_speed":0.02395},"optimized_scores":{"best_composite_score":0.06594,"best_fitness_score":0.06261,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1628.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_behind","phase_type":"approach","tcp_position_centroid":[0.50877,0.01809,0.23747]},{"body_a":"world","body_b":"push_box","contact_count":2464.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_contact","phase_type":"descend","tcp_position_centroid":[0.51861,0.03877,0.11152]},{"body_a":"world","body_b":"push_box","contact_count":1248.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":2.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5166,0.0288,0.04795]}],"total_contact_groups":3},"final_pose_error":0.21303,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50458,-0.01881,0.02499],"final_tcp_position":[0.51583,0.01813,0.04712],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":407.0,"n_steps_budget":600.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_behind","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2464.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.51941,0.03713,0.17486],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16065,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":616.0,"n_steps_budget":810.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"descend_contact","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1248.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_object","tcp_end":[0.52024,0.04057,0.05238],"tcp_start":[0.51941,0.03713,0.17486],"tcp_to_object_dist_end":0.06724,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":312.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1628.0,"raw_peak_contact_force":0.24534,"subtask_id":"push_object_to_goal","tcp_end":[0.51583,0.01813,0.04712],"tcp_start":[0.52024,0.04057,0.05238],"tcp_to_object_dist_end":0.04451,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```