## Search State

- **Seed**: 4
- **Iteration**: 1 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4172 | 0.80 | ✅ accepted |

**Proposal policy**: task_score is 0.80 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.795, which indicates the subtask decomposition is already effective.
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

## Current Skill (Q=0.417) — your mutation base

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

- **Composite score**: 0.417
- **task_score** (E): 0.795
- **fitness_score**: 0.444  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1865 |
| align_1 | 1.00 | 1.00 | 0.1779 |
| release_1 | 0.33 | 1.00 | 0.1680 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.497, -0.063, 0.126) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 3.667 | 24.762 | 61.137 |
| align_1 | align | 1.00 / step_budget | (0.497, -0.063, 0.126)→(0.527, 0.079, 0.027) | (0.531, 0.007, 0.025)→(0.533, 0.016, 0.028) | 0.161→0.171 | 1.00 / 4.667 | 10.316 | 102.227 |
| release_1 | release | 0.33 / step_budget | (0.527, 0.079, 0.027)→(0.504, -0.087, 0.020) | (0.533, 0.016, 0.028)→(0.522, -0.130, 0.025) | 0.171→0.035 | 1.00 / 4.333 | 1320.924 | 37.768 |
| insert_1 | insert | 1.00 / force_exceeded | (0.504, -0.087, 0.020)→(0.504, -0.087, 0.020) | (0.522, -0.130, 0.025)→(0.522, -0.130, 0.025) | 0.035→0.035 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.694
- goal_progress: 0.939
- terminal_score: 0.939
- phase_score: 0.219
- phase_breakdown.push_score: 0.109
- phase_breakdown.approach_score: 0.821
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.507
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.939
- **Median Q (composite search score)**: 0.402
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.312


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.43056,"average_solve_count":144.0,"average_success_count":144.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00232,"align_1.lateral_offset_y":0.00011,"insert_1.insertion_depth":0.07248,"insert_1.insertion_force":15.44888,"push_1.push_distance":0.06157,"push_1.push_speed":0.0541},"optimized_scores":{"best_composite_score":0.40249,"best_fitness_score":0.42915,"best_task_score":0.77168},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2127.0,"contact_point_centroid":[0.55656,-0.0552,-0.00016],"force_p95":52.07564,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":73.40444,"mean_force":21.09764,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52658,-0.00798,0.02153]},{"body_a":"push_box","body_b":"link7","contact_count":1062.0,"contact_point_centroid":[0.56143,-0.04875,0.05005],"force_p95":58.97387,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.22186,"mean_force":35.19908,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52214,-0.03003,0.02172]},{"body_a":"attachment","body_b":"push_box","contact_count":860.0,"contact_point_centroid":[0.52966,-0.05533,0.03909],"force_p95":45.43974,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.80144,"mean_force":15.57966,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51936,-0.0447,0.02205]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54647,-0.11021,0.04933],"force_p95":41.36458,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.36458,"mean_force":41.36458,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50941,-0.09111,0.0213]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.54993,-0.11534,-0.0002],"force_p95":26.93342,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.07996,"mean_force":25.61461,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50941,-0.09111,0.0213]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53088,-0.09951,0.04978],"force_p95":13.40949,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.40949,"mean_force":13.40949,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50941,-0.09111,0.0213]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49723,-0.0189,0.20926]},{"body_a":"world","body_b":"push_box","contact_count":2860.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52039,0.01985,0.06976]}],"total_contact_groups":8},"final_pose_error":0.05975,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53186,-0.13192,0.02506],"final_tcp_position":[0.50941,-0.09111,0.02128],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":73.40444,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2860.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49648,-0.03785,0.12178],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11882,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":715.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":23.12856,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4049.0,"raw_peak_contact_force":73.40444,"tcp_end":[0.54581,0.0747,0.02408],"tcp_start":[0.49648,-0.03785,0.12178],"tcp_to_object_dist_end":0.07372,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53186,-0.13191,0.02507],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.03663,"object_to_goal_dist_start":0.16043,"object_z_max":0.02881,"peak_contact_force":41.36458,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4.0,"raw_peak_contact_force":41.36458,"tcp_end":[0.50941,-0.09111,0.0213],"tcp_start":[0.54581,0.0747,0.02408],"tcp_to_object_dist_end":0.04672,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53186,-0.13192,0.02506],"object_pos_start":[0.53186,-0.13191,0.02507],"object_to_goal_dist_end":0.03663,"object_to_goal_dist_start":0.03663,"object_z_max":0.02507,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50941,-0.09111,0.02128],"tcp_start":[0.50941,-0.09111,0.0213],"tcp_to_object_dist_end":0.04673,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90551,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00421,"align_1.lateral_offset_y":-0.00079,"insert_1.insertion_depth":0.08694,"insert_1.insertion_force":7.14316,"push_1.push_distance":0.18646,"push_1.push_speed":0.09613},"optimized_scores":{"best_composite_score":0.36891,"best_fitness_score":0.39558,"best_task_score":0.67529},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":223.0,"contact_point_centroid":[0.53597,0.07101,0.04599],"force_p95":152.02411,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":182.91918,"mean_force":98.36843,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52874,0.0784,0.048]},{"body_a":"attachment","body_b":"push_box","contact_count":911.0,"contact_point_centroid":[0.53357,0.03039,0.03473],"force_p95":153.36348,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":161.42266,"mean_force":115.3174,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52946,0.04061,0.03548]},{"body_a":"world","body_b":"push_box","contact_count":3335.0,"contact_point_centroid":[0.53706,0.04036,-7e-05],"force_p95":56.42394,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":148.49623,"mean_force":7.52719,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51042,-0.00032,0.08687]},{"body_a":"world","body_b":"push_box","contact_count":2408.0,"contact_point_centroid":[0.53763,-0.02228,-0.00041],"force_p95":103.19549,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":115.36791,"mean_force":59.26138,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5259,0.02412,0.03306]},{"body_a":"push_box","body_b":"link7","contact_count":1053.0,"contact_point_centroid":[0.56141,-0.00112,0.06713],"force_p95":72.72872,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.82292,"mean_force":46.26028,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52788,0.03441,0.03424]},{"body_a":"push_box","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.56742,0.07327,0.06724],"force_p95":77.05023,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.11771,"mean_force":64.77724,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53392,0.10624,0.03442]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55314,-0.07292,0.04966],"force_p95":33.05903,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.05903,"mean_force":33.05903,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50972,-0.04975,0.02236]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.54346,-0.09068,-6e-05],"force_p95":21.72759,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.45797,"mean_force":11.40639,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50972,-0.04975,0.02236]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49729,-0.04316,0.2161]}],"total_contact_groups":9},"final_pose_error":0.10076,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.536,-0.0997,0.02492],"final_tcp_position":[0.50972,-0.04974,0.02235],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":182.91918,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":73.79692,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3592.0,"raw_peak_contact_force":182.91918,"tcp_end":[0.49661,-0.08501,0.1382],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17114,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":955.0,"n_steps_budget":1000.0,"object_pos_end":[0.54249,0.06686,0.03285],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.22113,"object_to_goal_dist_start":0.1905,"object_z_max":0.03489,"peak_contact_force":7.81875,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4372.0,"raw_peak_contact_force":161.42266,"tcp_end":[0.53511,0.11012,0.03211],"tcp_start":[0.49661,-0.08501,0.1382],"tcp_to_object_dist_end":0.04389,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.536,-0.0997,0.02492],"object_pos_start":[0.54249,0.06686,0.03285],"object_to_goal_dist_end":0.06186,"object_to_goal_dist_start":0.22113,"object_z_max":0.03449,"peak_contact_force":33.05903,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4.0,"raw_peak_contact_force":33.05903,"tcp_end":[0.50972,-0.04975,0.02236],"tcp_start":[0.53511,0.11012,0.03211],"tcp_to_object_dist_end":0.0565,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.536,-0.0997,0.02492],"object_pos_start":[0.536,-0.0997,0.02492],"object_to_goal_dist_end":0.06186,"object_to_goal_dist_start":0.06186,"object_z_max":0.02492,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50972,-0.04974,0.02235],"tcp_start":[0.50972,-0.04975,0.02236],"tcp_to_object_dist_end":0.05651,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89916,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00542,"align_1.lateral_offset_y":-0.0098,"insert_1.insertion_depth":0.12627,"insert_1.insertion_force":2.30754,"push_1.push_distance":0.08545,"push_1.push_speed":0.08753},"optimized_scores":{"best_composite_score":0.48018,"best_fitness_score":0.50685,"best_task_score":0.93925},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2274.0,"contact_point_centroid":[0.50697,-0.09173,-9e-05],"force_p95":45.86466,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":71.8533,"mean_force":11.8171,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49647,-0.03993,0.0212]},{"body_a":"attachment","body_b":"push_box","contact_count":873.0,"contact_point_centroid":[0.5126,-0.06896,0.04691],"force_p95":49.11112,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.16686,"mean_force":19.48409,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49705,-0.05784,0.02167]},{"body_a":"push_box","body_b":"link7","contact_count":748.0,"contact_point_centroid":[0.5238,-0.07181,0.05361],"force_p95":37.84836,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":47.48067,"mean_force":21.65929,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49707,-0.05074,0.02168]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52129,-0.14612,0.04938],"force_p95":38.88047,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.88047,"mean_force":38.88047,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49414,-0.11927,0.01748]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.497,-0.15749,-0.00011],"force_p95":22.58459,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.55827,"mean_force":11.19428,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49414,-0.11927,0.01748]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.51029,-0.13134,0.04965],"force_p95":8.21859,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.21859,"mean_force":8.21859,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49414,-0.11927,0.01748]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49723,-0.03346,0.20719]},{"body_a":"world","body_b":"push_box","contact_count":2392.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49679,-0.00653,0.07035]}],"total_contact_groups":8},"final_pose_error":0.03218,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49707,-0.15741,0.02477],"final_tcp_position":[0.49414,-0.11926,0.01747],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":3888.34821,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2392.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4965,-0.06647,0.11914],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10584,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":598.0,"n_steps_budget":990.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.0,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3895.0,"raw_peak_contact_force":71.8533,"tcp_end":[0.49984,0.0526,0.02603],"tcp_start":[0.4965,-0.06647,0.11914],"tcp_to_object_dist_end":0.07157,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49708,-0.15741,0.02477],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00797,"object_to_goal_dist_start":0.13127,"object_z_max":0.0309,"peak_contact_force":3888.34821,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":6.0,"raw_peak_contact_force":38.88047,"tcp_end":[0.49414,-0.11927,0.01748],"tcp_start":[0.49984,0.0526,0.02603],"tcp_to_object_dist_end":0.03895,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49707,-0.15741,0.02477],"object_pos_start":[0.49708,-0.15741,0.02477],"object_to_goal_dist_end":0.00797,"object_to_goal_dist_start":0.00797,"object_z_max":0.02477,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49414,-0.11926,0.01747],"tcp_start":[0.49414,-0.11927,0.01748],"tcp_to_object_dist_end":0.03895,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```