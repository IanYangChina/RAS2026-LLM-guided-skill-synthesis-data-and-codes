## Search State

- **Seed**: 4
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4202 | 0.80 | ❌ rejected |
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | -0.0657 | 0.00 | ❌ rejected |
| 3 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4198 | 0.80 | ❌ rejected |
| 2 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4250 | 0.81 | ✅ accepted |
| 1 | approach → push | linear_cartesian | linear_cartesian | force_threshold_switch | position_control | force_exceeded | time_limit | 4 | -0.1772 | 0.00 | ❌ rejected |

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

## Current Skill (Q=0.420) — your mutation base

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

- **Composite score**: 0.420
- **task_score** (E): 0.801
- **fitness_score**: 0.447  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1891 |
| align_1 | 1.00 | 1.00 | 0.1766 |
| release_1 | 0.33 | 1.00 | 0.1681 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.497, -0.063, 0.124) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_1 | align | 1.00 / step_budget | (0.497, -0.063, 0.124)→(0.527, 0.079, 0.027) | (0.531, 0.007, 0.025)→(0.533, 0.016, 0.028) | 0.161→0.171 | 1.00 / 3.667 | 24.651 | 60.497 |
| release_1 | release | 0.33 / step_budget | (0.527, 0.079, 0.027)→(0.505, -0.087, 0.021) | (0.533, 0.016, 0.028)→(0.521, -0.130, 0.026) | 0.171→0.035 | 1.00 / 4.000 | 24.195 | 101.519 |
| insert_1 | insert | 1.00 / force_exceeded | (0.505, -0.087, 0.021)→(0.505, -0.087, 0.021) | (0.521, -0.130, 0.026)→(0.521, -0.130, 0.026) | 0.035→0.035 | 1.00 / 4.000 | 41.160 | 41.160 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.696
- goal_progress: 0.938
- terminal_score: 0.938
- phase_score: 0.219
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.109
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.506
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.938
- **Median Q (composite search score)**: 0.411
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.358


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68148,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00062,"align_1.lateral_offset_y":-0.00228,"insert_1.insertion_depth":0.03071,"insert_1.insertion_force":14.07133,"push_1.push_distance":0.06304,"push_1.push_speed":0.06421},"optimized_scores":{"best_composite_score":0.41137,"best_fitness_score":0.43804,"best_task_score":0.78583},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2184.0,"contact_point_centroid":[0.55283,-0.05772,-0.00017],"force_p95":58.74266,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.03046,"mean_force":22.04728,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52656,-0.00925,0.02148]},{"body_a":"push_box","body_b":"link7","contact_count":1072.0,"contact_point_centroid":[0.55959,-0.04981,0.05082],"force_p95":66.62818,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":81.84992,"mean_force":37.15405,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52253,-0.02973,0.02177]},{"body_a":"attachment","body_b":"push_box","contact_count":869.0,"contact_point_centroid":[0.52902,-0.0557,0.03881],"force_p95":51.29931,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":65.24181,"mean_force":19.01741,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51973,-0.04481,0.0222]},{"body_a":"world","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.56152,-0.13403,-0.00039],"force_p95":47.89242,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":47.89242,"mean_force":47.89242,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51074,-0.09072,0.02255]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54641,-0.11214,0.05138],"force_p95":46.03255,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.03255,"mean_force":46.03255,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51074,-0.09072,0.02255]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53231,-0.09965,0.0535],"force_p95":22.20782,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":22.20782,"mean_force":22.20782,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51074,-0.09072,0.02255]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49721,-0.02016,0.20564]},{"body_a":"world","body_b":"push_box","contact_count":2904.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52043,0.0188,0.06593]}],"total_contact_groups":8},"final_pose_error":0.0603,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52852,-0.13096,0.02706],"final_tcp_position":[0.51072,-0.09071,0.02252],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":87.03046,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49644,-0.04035,0.11469],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11403,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":726.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2904.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.54586,0.07468,0.02364],"tcp_start":[0.49644,-0.04035,0.11469],"tcp_to_object_dist_end":0.0737,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52853,-0.13095,0.02709],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.03437,"object_to_goal_dist_start":0.16043,"object_z_max":0.02953,"peak_contact_force":36.86285,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4125.0,"raw_peak_contact_force":87.03046,"tcp_end":[0.51074,-0.09072,0.02255],"tcp_start":[0.54586,0.07468,0.02364],"tcp_to_object_dist_end":0.04423,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.52852,-0.13096,0.02706],"object_pos_start":[0.52853,-0.13095,0.02709],"object_to_goal_dist_end":0.03436,"object_to_goal_dist_start":0.03437,"object_z_max":0.02709,"peak_contact_force":47.89242,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":3.0,"raw_peak_contact_force":47.89242,"tcp_end":[0.51072,-0.09071,0.02252],"tcp_start":[0.51074,-0.09072,0.02255],"tcp_to_object_dist_end":0.04425,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90476,"average_solve_count":126.0,"average_success_count":126.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00386,"align_1.lateral_offset_y":-0.00863,"insert_1.insertion_depth":0.11383,"insert_1.insertion_force":14.27149,"push_1.push_distance":0.19361,"push_1.push_speed":0.0993},"optimized_scores":{"best_composite_score":0.36967,"best_fitness_score":0.39634,"best_task_score":0.67899},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":218.0,"contact_point_centroid":[0.53601,0.07126,0.04595],"force_p95":150.44622,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":180.9998,"mean_force":97.33474,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52881,0.07867,0.04795]},{"body_a":"attachment","body_b":"push_box","contact_count":916.0,"contact_point_centroid":[0.53349,0.02982,0.0347],"force_p95":153.34592,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":162.19512,"mean_force":115.28598,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5294,0.04005,0.03544]},{"body_a":"world","body_b":"push_box","contact_count":3387.0,"contact_point_centroid":[0.53704,0.04023,-6e-05],"force_p95":55.18552,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.25599,"mean_force":7.20439,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51049,-0.00157,0.08807]},{"body_a":"world","body_b":"push_box","contact_count":2432.0,"contact_point_centroid":[0.53758,-0.02322,-0.00041],"force_p95":102.73677,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.03311,"mean_force":58.67342,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52577,0.02342,0.03296]},{"body_a":"push_box","body_b":"link7","contact_count":1048.0,"contact_point_centroid":[0.56131,-0.00076,0.06725],"force_p95":72.71759,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.93223,"mean_force":46.01973,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52799,0.03489,0.03428]},{"body_a":"push_box","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.56735,0.07321,0.06721],"force_p95":76.73473,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.80859,"mean_force":64.91611,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53391,0.10624,0.03436]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5532,-0.07311,0.04974],"force_p95":31.43304,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.43304,"mean_force":31.43304,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50979,-0.04962,0.02241]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.54283,-0.09107,-5e-05],"force_p95":20.70554,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.34148,"mean_force":10.86492,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50979,-0.04962,0.02241]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4973,-0.04453,0.21731]}],"total_contact_groups":9},"final_pose_error":0.10089,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53547,-0.10019,0.02494],"final_tcp_position":[0.50978,-0.04961,0.0224],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":180.9998,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49667,-0.08768,0.14065],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17466,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":966.0,"n_steps_budget":1000.0,"object_pos_end":[0.5424,0.0668,0.03285],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.22104,"object_to_goal_dist_start":0.1905,"object_z_max":0.0349,"peak_contact_force":73.4634,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3639.0,"raw_peak_contact_force":180.9998,"tcp_end":[0.5351,0.11012,0.03206],"tcp_start":[0.49667,-0.08768,0.14065],"tcp_to_object_dist_end":0.04394,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53547,-0.10019,0.02494],"object_pos_start":[0.5424,0.0668,0.03285],"object_to_goal_dist_end":0.06115,"object_to_goal_dist_start":0.22104,"object_z_max":0.03449,"peak_contact_force":5.84315,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4396.0,"raw_peak_contact_force":162.19512,"tcp_end":[0.50979,-0.04962,0.02241],"tcp_start":[0.5351,0.11012,0.03206],"tcp_to_object_dist_end":0.05677,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.53547,-0.10019,0.02494],"object_pos_start":[0.53547,-0.10019,0.02494],"object_to_goal_dist_end":0.06115,"object_to_goal_dist_start":0.06115,"object_z_max":0.02494,"peak_contact_force":31.43304,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":31.43304,"tcp_end":[0.50978,-0.04961,0.0224],"tcp_start":[0.50979,-0.04962,0.02241],"tcp_to_object_dist_end":0.05678,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89916,"average_solve_count":119.0,"average_success_count":119.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00105,"align_1.lateral_offset_y":0.00258,"insert_1.insertion_depth":0.08722,"insert_1.insertion_force":13.50172,"push_1.push_distance":0.07739,"push_1.push_speed":0.08579},"optimized_scores":{"best_composite_score":0.47959,"best_fitness_score":0.50626,"best_task_score":0.93766},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2379.0,"contact_point_centroid":[0.50586,-0.09355,-8e-05],"force_p95":32.86643,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.33177,"mean_force":9.62036,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49641,-0.04242,0.02115]},{"body_a":"attachment","body_b":"push_box","contact_count":763.0,"contact_point_centroid":[0.51135,-0.06224,0.04533],"force_p95":42.81255,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.24219,"mean_force":17.74545,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49698,-0.05099,0.02174]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52381,-0.14663,0.04927],"force_p95":44.15361,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.15361,"mean_force":44.15361,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49482,-0.12027,0.01812]},{"body_a":"push_box","body_b":"link7","contact_count":681.0,"contact_point_centroid":[0.5242,-0.07018,0.05309],"force_p95":32.09147,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.62877,"mean_force":19.94316,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49684,-0.04877,0.02147]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49912,-0.15825,-0.00014],"force_p95":24.39986,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.80791,"mean_force":11.30169,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49482,-0.12027,0.01812]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49722,-0.03131,0.20596]},{"body_a":"world","body_b":"push_box","contact_count":2316.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49675,-0.00449,0.069]}],"total_contact_groups":7},"final_pose_error":0.03096,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4992,-0.15814,0.02473],"final_tcp_position":[0.49482,-0.12027,0.01811],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":55.33177,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49644,-0.06231,0.11633],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1015,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":579.0,"n_steps_budget":960.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":2316.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49982,0.05261,0.02604],"tcp_start":[0.49644,-0.06231,0.11633],"tcp_to_object_dist_end":0.07158,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4992,-0.15814,0.02473],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00818,"object_to_goal_dist_start":0.13127,"object_z_max":0.02902,"peak_contact_force":29.87751,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3823.0,"raw_peak_contact_force":55.33177,"tcp_end":[0.49482,-0.12027,0.01812],"tcp_start":[0.49982,0.05261,0.02604],"tcp_to_object_dist_end":0.03869,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.4992,-0.15814,0.02473],"object_pos_start":[0.4992,-0.15814,0.02473],"object_to_goal_dist_end":0.00818,"object_to_goal_dist_start":0.00818,"object_z_max":0.02473,"peak_contact_force":44.15361,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":44.15361,"tcp_end":[0.49482,-0.12027,0.01811],"tcp_start":[0.49482,-0.12027,0.01812],"tcp_to_object_dist_end":0.03869,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```