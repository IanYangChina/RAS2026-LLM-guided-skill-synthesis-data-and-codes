## Search State

- **Seed**: 4
- **Iteration**: 10 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 9 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4173 | 0.79 | ❌ rejected |
| 8 | approach → push → retract | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 8 | -0.3030 | 0.00 | ❌ rejected |
| 7 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4264 | 0.83 | ✅ accepted |
| 6 | approach → push → retract | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | time_limit | pose_tolerance | 2 | 0.4256 | 0.59 | ❌ rejected |
| 5 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4202 | 0.80 | ❌ rejected |

**Proposal policy**: task_score is 0.79 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen object start: [0.5, -0.15, 0.025]
- Frozen task target: [0.5, 0.0, 0.3]
- Goal object position: (0.5, 0.0, 0.3)
- Object initial pose: (0.5, -0.15, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5531667326686841, 0.0013593063377233885, 0.025)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5531667326686841, 0.0013593063377233885, 0.025]
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
  frozen_task_target: [0.5, 0.0, 0.3]
  frozen_object_starts: {'push_box': [0.5, -0.15, 0.025]}
  frozen_targets: {'task_goal': [0.5, 0.0, 0.3]}
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
| `object` | offset from object initial position (0.5, -0.15, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, 0.0, 0.3) | final destination targets |
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
- **task_score** (E): 0.794
- **fitness_score**: 0.444  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1871 |
| align_1 | 1.00 | 1.00 | 0.1834 |
| release_1 | 0.33 | 1.00 | 0.1694 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.497, -0.069, 0.128) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_1 | align | 1.00 / step_budget | (0.497, -0.069, 0.128)→(0.527, 0.079, 0.027) | (0.531, 0.007, 0.025)→(0.534, 0.016, 0.028) | 0.161→0.171 | 1.00 / 3.667 | 24.728 | 91.001 |
| release_1 | release | 0.33 / step_budget | (0.527, 0.079, 0.027)→(0.504, -0.088, 0.021) | (0.534, 0.016, 0.028)→(0.523, -0.131, 0.025) | 0.171→0.036 | 1.00 / 4.333 | 27.303 | 101.535 |
| insert_1 | insert | 1.00 / force_exceeded | (0.504, -0.088, 0.021)→(0.504, -0.088, 0.021) | (0.523, -0.131, 0.025)→(0.523, -0.131, 0.025) | 0.036→0.036 | 1.00 / 4.333 | 43.092 | 43.092 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.697
- goal_progress: 0.935
- terminal_score: 0.935
- phase_score: 0.216
- phase_breakdown.contact_score: 0.000
- phase_breakdown.push_score: 0.104
- phase_breakdown.approach_score: 0.821

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.503
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.935
- **Median Q (composite search score)**: 0.407
- **K-run variance**: 0.0020
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.357


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
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.55317,0.00136,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68382,"average_solve_count":136.0,"average_success_count":136.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00089,"align_1.lateral_offset_y":-0.00032,"insert_1.insertion_depth":0.10181,"insert_1.insertion_force":14.36497,"push_1.push_distance":0.07288,"push_1.push_speed":0.0638},"optimized_scores":{"best_composite_score":0.40663,"best_fitness_score":0.4333,"best_task_score":0.7719},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":25.0,"contact_point_centroid":[0.53548,0.02711,0.04966],"force_p95":47.56339,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":90.34354,"mean_force":31.68097,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52979,0.03728,0.05174]},{"body_a":"world","body_b":"push_box","contact_count":2168.0,"contact_point_centroid":[0.55703,-0.05193,-0.00016],"force_p95":58.24196,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.83816,"mean_force":20.96946,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52663,-0.00715,0.02109]},{"body_a":"push_box","body_b":"link7","contact_count":1075.0,"contact_point_centroid":[0.56166,-0.04777,0.04949],"force_p95":55.37261,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.28164,"mean_force":36.04088,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5221,-0.02942,0.02131]},{"body_a":"world","body_b":"push_box","contact_count":2918.0,"contact_point_centroid":[0.55331,0.00185,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":53.88245,"mean_force":0.52174,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52029,0.01546,0.06795]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54657,-0.11106,0.04882],"force_p95":49.84777,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":49.84777,"mean_force":49.84777,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5086,-0.09351,0.02113]},{"body_a":"attachment","body_b":"push_box","contact_count":870.0,"contact_point_centroid":[0.52914,-0.05543,0.03775],"force_p95":36.76751,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.26024,"mean_force":12.54611,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51904,-0.04497,0.02161]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.54883,-0.11845,-0.0003],"force_p95":30.1099,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.17843,"mean_force":29.49312,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5086,-0.09351,0.02113]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53081,-0.10123,0.04945],"force_p95":11.61445,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.61445,"mean_force":11.61445,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5086,-0.09351,0.02113]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49722,-0.023,0.20709]}],"total_contact_groups":9},"final_pose_error":0.05727,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53356,-0.13549,0.02637],"final_tcp_position":[0.5086,-0.09351,0.02112],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":90.34354,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49646,-0.04597,0.1178],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11862,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":744.0,"n_steps_budget":1000.0,"object_pos_end":[0.55362,0.00135,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16057,"object_to_goal_dist_start":0.16043,"object_z_max":0.02528,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2943.0,"raw_peak_contact_force":90.34354,"tcp_end":[0.54597,0.07464,0.02363],"tcp_start":[0.49646,-0.04597,0.1178],"tcp_to_object_dist_end":0.0737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53356,-0.13548,0.02637],"object_pos_start":[0.55362,0.00135,0.02499],"object_to_goal_dist_end":0.03659,"object_to_goal_dist_start":0.16057,"object_z_max":0.02971,"peak_contact_force":39.80319,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4113.0,"raw_peak_contact_force":83.83816,"tcp_end":[0.5086,-0.09351,0.02113],"tcp_start":[0.54597,0.07464,0.02363],"tcp_to_object_dist_end":0.04911,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53356,-0.13549,0.02637],"object_pos_start":[0.53356,-0.13548,0.02637],"object_to_goal_dist_end":0.03659,"object_to_goal_dist_start":0.03659,"object_z_max":0.02637,"peak_contact_force":49.84777,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":49.84777,"tcp_end":[0.5086,-0.09351,0.02112],"tcp_start":[0.5086,-0.09351,0.02113],"tcp_to_object_dist_end":0.04912,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.5366,0.03695,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90698,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00083,"align_1.lateral_offset_y":0.00923,"insert_1.insertion_depth":0.08497,"insert_1.insertion_force":13.74071,"push_1.push_distance":0.18095,"push_1.push_speed":0.08935},"optimized_scores":{"best_composite_score":0.36854,"best_fitness_score":0.39521,"best_task_score":0.67381},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":222.0,"contact_point_centroid":[0.53586,0.07107,0.04597],"force_p95":153.1335,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":182.41475,"mean_force":98.39269,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52864,0.07847,0.04797]},{"body_a":"attachment","body_b":"push_box","contact_count":911.0,"contact_point_centroid":[0.53355,0.03026,0.03474],"force_p95":153.49699,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":161.55746,"mean_force":115.5016,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52943,0.04048,0.03549]},{"body_a":"world","body_b":"push_box","contact_count":3293.0,"contact_point_centroid":[0.53706,0.04038,-7e-05],"force_p95":56.68416,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.75234,"mean_force":7.5943,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51035,0.00088,0.08625]},{"body_a":"world","body_b":"push_box","contact_count":2427.0,"contact_point_centroid":[0.53801,-0.02278,-0.00041],"force_p95":103.28826,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":115.77434,"mean_force":58.84881,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52576,0.02353,0.03298]},{"body_a":"push_box","body_b":"link7","contact_count":1055.0,"contact_point_centroid":[0.56138,-0.00117,0.06708],"force_p95":72.73187,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.94702,"mean_force":46.14886,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52782,0.03426,0.03421]},{"body_a":"push_box","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.56743,0.07327,0.06723],"force_p95":76.92156,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.99809,"mean_force":65.02945,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53388,0.10624,0.03442]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55313,-0.07261,0.04962],"force_p95":33.92034,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.92034,"mean_force":33.92034,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5097,-0.04984,0.02237]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.54355,-0.09042,-7e-05],"force_p95":22.51973,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":24.33156,"mean_force":11.6956,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5097,-0.04984,0.02237]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49729,-0.0418,0.21566]}],"total_contact_groups":9},"final_pose_error":0.10067,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53613,-0.09944,0.02492],"final_tcp_position":[0.5097,-0.04984,0.02235],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":182.41475,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49656,-0.08255,0.1369],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16854,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":944.0,"n_steps_budget":1000.0,"object_pos_end":[0.54249,0.06686,0.03285],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.22112,"object_to_goal_dist_start":0.1905,"object_z_max":0.03489,"peak_contact_force":73.69271,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3549.0,"raw_peak_contact_force":182.41475,"tcp_end":[0.53508,0.11013,0.0321],"tcp_start":[0.49656,-0.08255,0.1369],"tcp_to_object_dist_end":0.04391,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53613,-0.09945,0.02492],"object_pos_start":[0.54249,0.06686,0.03285],"object_to_goal_dist_end":0.06214,"object_to_goal_dist_start":0.22112,"object_z_max":0.03449,"peak_contact_force":8.72322,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4393.0,"raw_peak_contact_force":161.55746,"tcp_end":[0.5097,-0.04984,0.02237],"tcp_start":[0.53508,0.11013,0.0321],"tcp_to_object_dist_end":0.05627,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.53613,-0.09944,0.02492],"object_pos_start":[0.53613,-0.09945,0.02492],"object_to_goal_dist_end":0.06214,"object_to_goal_dist_start":0.06214,"object_z_max":0.02492,"peak_contact_force":33.92034,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":33.92034,"tcp_end":[0.5097,-0.04984,0.02235],"tcp_start":[0.5097,-0.04984,0.02237],"tcp_to_object_dist_end":0.05627,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5,-0.15,0.025]},{"name":"goal","value":[0.50458,-0.01881,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89655,"average_solve_count":116.0,"average_success_count":116.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.0088,"align_1.lateral_offset_y":0.00295,"insert_1.insertion_depth":0.044,"insert_1.insertion_force":4.30433,"push_1.push_distance":0.11207,"push_1.push_speed":0.09875},"optimized_scores":{"best_composite_score":0.47683,"best_fitness_score":0.5035,"best_task_score":0.93485},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2305.0,"contact_point_centroid":[0.50526,-0.09407,-8e-05],"force_p95":35.09893,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.20926,"mean_force":8.78934,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49633,-0.04386,0.02106]},{"body_a":"attachment","body_b":"push_box","contact_count":766.0,"contact_point_centroid":[0.50981,-0.06417,0.04371],"force_p95":39.82983,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":50.89342,"mean_force":14.44827,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49667,-0.05274,0.02147]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52491,-0.14711,0.04922],"force_p95":45.50823,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.50823,"mean_force":45.50823,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49512,-0.12094,0.0184]},{"body_a":"push_box","body_b":"link7","contact_count":583.0,"contact_point_centroid":[0.52487,-0.06941,0.05254],"force_p95":35.75555,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.35959,"mean_force":20.46153,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49667,-0.0479,0.02133]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.50002,-0.15866,-0.00015],"force_p95":25.69081,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.28919,"mean_force":11.63183,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49512,-0.12094,0.0184]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49726,-0.03997,0.21147]},{"body_a":"world","body_b":"push_box","contact_count":2616.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49682,-0.01261,0.07494]}],"total_contact_groups":7},"final_pose_error":0.0302,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50011,-0.15855,0.0247],"final_tcp_position":[0.49512,-0.12094,0.01839],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":59.20926,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49647,-0.07897,0.12856],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12005,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":654.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2616.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49989,0.05257,0.02606],"tcp_start":[0.49647,-0.07897,0.12856],"tcp_to_object_dist_end":0.07154,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50011,-0.15855,0.0247],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00855,"object_to_goal_dist_start":0.13127,"object_z_max":0.0292,"peak_contact_force":33.38374,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3654.0,"raw_peak_contact_force":59.20926,"tcp_end":[0.49512,-0.12094,0.0184],"tcp_start":[0.49989,0.05257,0.02606],"tcp_to_object_dist_end":0.03846,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50011,-0.15855,0.0247],"object_pos_start":[0.50011,-0.15855,0.0247],"object_to_goal_dist_end":0.00855,"object_to_goal_dist_start":0.00855,"object_z_max":0.0247,"peak_contact_force":45.50823,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":45.50823,"tcp_end":[0.49512,-0.12094,0.01839],"tcp_start":[0.49512,-0.12094,0.0184],"tcp_to_object_dist_end":0.03846,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```