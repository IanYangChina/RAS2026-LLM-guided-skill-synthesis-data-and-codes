## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | force_exceeded | 5  | 0.4264 | 0.83 | ✅ accepted |
| 7 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6  | 0.1356 | 0.17 | ❌ rejected |
| 6 | approach → push | linear_cartesian | linear_cartesian | position_control | admittance_control | pose_tolerance | time_limit | 3  | 0.4202 | 0.80 | ❌ rejected |
| 5 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6  | 0.1104 | 0.00 | ❌ rejected |
| 4 | approach → contact → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | admittance_control | pose_tolerance | force_exceeded | force_exceeded | 6  | -0.1441 | 0.00 | ❌ rejected |

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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.828, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=-0.144) — your mutation base

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

- **Composite score**: -0.144
- **task_score** (E): 0.001
- **fitness_score**: 0.106  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.250

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_phase | 1.00 | 1.00 | 0.2561 |
| push_phase | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_phase | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.531, 0.006, 0.048) | (0.531, 0.007, 0.025)→(0.534, 0.007, 0.024) | 0.161→0.161 | 1.00 / 5.000 | 232.560 | 267.425 |
| push_phase | push | 0.00 / guard_failure | (0.531, 0.006, 0.048)→(0.531, 0.006, 0.048) | (0.534, 0.007, 0.024)→(0.534, 0.007, 0.024) | 0.161→0.161 | 1.00 / 5.000 | 99.587 | 99.587 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.019
- lateral_force_integral: None
- approach_alignment: 0.541
- goal_progress: 0.002
- terminal_score: 0.002
- phase_score: 0.177
- phase_breakdown.approach_sub_score: 0.590
- phase_breakdown.push_sub_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.107
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.002
- **Median Q (composite search score)**: -0.144
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.259


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89474,"average_solve_count":57.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_phase.approach_offset_x":0.00577,"approach_phase.approach_offset_y":-0.00949,"push_phase.push_distance":0.09709,"push_phase.push_force":15.46904,"push_phase.push_speed":0.06982},"optimized_scores":{"best_composite_score":-0.14489,"best_fitness_score":0.10511,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":67.0,"contact_point_centroid":[0.55685,0.00159,0.04773],"force_p95":233.07865,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":266.17284,"mean_force":188.20055,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.54548,0.00165,0.05017]},{"body_a":"world","body_b":"push_box","contact_count":3524.0,"contact_point_centroid":[0.55324,0.00136,-3e-05],"force_p95":21.62033,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":129.59739,"mean_force":3.84172,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.52107,0.00085,0.16716]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.56249,0.00171,0.04656],"force_p95":99.7875,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":99.7875,"mean_force":99.7875,"phase_index":1.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.55105,0.0017,0.04818]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.5553,0.00137,-0.00057],"force_p95":48.22382,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.53123,"mean_force":25.13243,"phase_index":1.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.55105,0.0017,0.04818]}],"total_contact_groups":4},"final_pose_error":0.06747,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55585,0.00138,0.02387],"final_tcp_position":[0.55116,0.0017,0.0482],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":266.17284,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":881.0,"n_steps_budget":1000.0,"object_pos_end":[0.55587,0.00138,0.02385],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16137,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":221.14552,"phase_name":"approach_phase","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3591.0,"raw_peak_contact_force":266.17284,"subtask_id":"approach_sub","tcp_end":[0.55105,0.0017,0.04818],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0248,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":630.0,"object_pos_end":[0.55585,0.00138,0.02387],"object_pos_start":[0.55587,0.00138,0.02385],"object_to_goal_dist_end":0.16136,"object_to_goal_dist_start":0.16137,"object_z_max":0.02385,"peak_contact_force":99.7875,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":99.7875,"subtask_id":"push_sub","tcp_end":[0.55116,0.0017,0.0482],"tcp_start":[0.55105,0.0017,0.04818],"tcp_to_object_dist_end":0.02478,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89474,"average_solve_count":57.0,"average_success_count":57.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_phase.approach_offset_x":0.007,"approach_phase.approach_offset_y":-0.0081,"push_phase.push_distance":0.20292,"push_phase.push_force":17.30231,"push_phase.push_speed":0.02584},"optimized_scores":{"best_composite_score":-0.1444,"best_fitness_score":0.1056,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":67.0,"contact_point_centroid":[0.54249,0.03594,0.04765],"force_p95":237.82036,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":265.34543,"mean_force":191.86168,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.53124,0.036,0.0504]},{"body_a":"world","body_b":"push_box","contact_count":3504.0,"contact_point_centroid":[0.53667,0.03697,-3e-05],"force_p95":19.77676,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":135.00223,"mean_force":3.93375,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.51366,0.01869,0.16722]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.54781,0.03694,0.04641],"force_p95":99.20296,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":99.20296,"mean_force":99.20296,"phase_index":1.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.53649,0.03702,0.04833]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.53854,0.03738,-0.00059],"force_p95":45.87739,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.594,"mean_force":25.04785,"phase_index":1.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.53649,0.03702,0.04833]}],"total_contact_groups":4},"final_pose_error":0.02763,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53915,0.03744,0.02383],"final_tcp_position":[0.53659,0.03704,0.04834],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":265.34543,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":876.0,"n_steps_budget":1000.0,"object_pos_end":[0.53917,0.03744,0.02382],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.19149,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":227.77042,"phase_name":"approach_phase","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3571.0,"raw_peak_contact_force":265.34543,"subtask_id":"approach_sub","tcp_end":[0.53649,0.03702,0.04833],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02466,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":690.0,"object_pos_end":[0.53915,0.03744,0.02383],"object_pos_start":[0.53917,0.03744,0.02382],"object_to_goal_dist_end":0.19149,"object_to_goal_dist_start":0.19149,"object_z_max":0.02382,"peak_contact_force":99.20296,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":99.20296,"subtask_id":"push_sub","tcp_end":[0.53659,0.03704,0.04834],"tcp_start":[0.53649,0.03702,0.04833],"tcp_to_object_dist_end":0.02465,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89286,"average_solve_count":56.0,"average_success_count":56.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_phase.approach_offset_x":0.00576,"approach_phase.approach_offset_y":-0.01272,"push_phase.push_distance":0.19142,"push_phase.push_force":8.89493,"push_phase.push_speed":0.03002},"optimized_scores":{"best_composite_score":-0.14307,"best_fitness_score":0.10693,"best_task_score":0.0017},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":64.0,"contact_point_centroid":[0.51103,-0.02014,0.04747],"force_p95":256.35464,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":270.75532,"mean_force":207.23242,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.50013,-0.02012,0.05093]},{"body_a":"world","body_b":"push_box","contact_count":3344.0,"contact_point_centroid":[0.50464,-0.01882,-4e-05],"force_p95":25.02812,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.49717,"mean_force":4.22769,"phase_index":0.0,"phase_name":"approach_phase","phase_type":"approach","tcp_position_centroid":[0.49756,-0.01042,0.16777]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.51553,-0.02062,0.04613],"force_p95":99.77137,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":99.77137,"mean_force":99.77137,"phase_index":1.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50455,-0.02071,0.04871]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.50613,-0.01903,-0.00062],"force_p95":45.94734,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.28004,"mean_force":25.2583,"phase_index":1.0,"phase_name":"push_phase","phase_type":"push","tcp_position_centroid":[0.50455,-0.02071,0.04871]}],"total_contact_groups":4},"final_pose_error":0.06715,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50674,-0.01913,0.02375],"final_tcp_position":[0.50464,-0.02072,0.04872],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":270.75532,"phases":[{"contact_detected":true,"contact_event_count":5.0,"n_steps":836.0,"n_steps_budget":1000.0,"object_pos_end":[0.50675,-0.01913,0.02374],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13105,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":248.76498,"phase_name":"approach_phase","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3408.0,"raw_peak_contact_force":270.75532,"subtask_id":"approach_sub","tcp_end":[0.50455,-0.02071,0.04871],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02511,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":1000.0,"object_pos_end":[0.50674,-0.01913,0.02375],"object_pos_start":[0.50675,-0.01913,0.02374],"object_to_goal_dist_end":0.13105,"object_to_goal_dist_start":0.13105,"object_z_max":0.02374,"peak_contact_force":99.77137,"phase_name":"push_phase","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":99.77137,"subtask_id":"push_sub","tcp_end":[0.50464,-0.02072,0.04872],"tcp_start":[0.50455,-0.02071,0.04871],"tcp_to_object_dist_end":0.0251,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```