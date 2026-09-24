## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4250 | 0.81 | ✅ accepted |
| 1 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4176 | 0.79 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4172 | 0.80 | ✅ accepted |

**Proposal policy**: task_score is 0.81 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.425) — your mutation base

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

- **Composite score**: 0.425
- **task_score** (E): 0.810
- **fitness_score**: 0.452  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1929 |
| align_1 | 1.00 | 1.00 | 0.1708 |
| release_1 | 0.33 | 1.00 | 0.1680 |
| insert_1 | 1.00 | 1.00 | 0.0013 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.496, -0.060, 0.119) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 3.333 | 54.965 | 147.469 |
| align_1 | align | 1.00 / step_budget | (0.496, -0.060, 0.119)→(0.529, 0.080, 0.029) | (0.531, 0.007, 0.025)→(0.535, 0.025, 0.030) | 0.161→0.180 | 1.00 / 4.333 | 18.911 | 111.302 |
| release_1 | release | 0.33 / step_budget | (0.529, 0.080, 0.029)→(0.505, -0.086, 0.021) | (0.535, 0.025, 0.030)→(0.521, -0.131, 0.026) | 0.180→0.033 | 1.00 / 4.667 | 34.422 | 34.422 |
| insert_1 | insert | 1.00 / force_exceeded | (0.505, -0.086, 0.021)→(0.504, -0.087, 0.021) | (0.521, -0.131, 0.026)→(0.521, -0.131, 0.026) | 0.033→0.033 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.692
- goal_progress: 0.954
- terminal_score: 0.954
- phase_score: 0.223
- phase_breakdown.push_score: 0.117
- phase_breakdown.approach_score: 0.822
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.516
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.954
- **Median Q (composite search score)**: 0.415
- **K-run variance**: 0.0024
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.342


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.79231,"average_solve_count":130.0,"average_success_count":130.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00114,"align_1.lateral_offset_y":-0.00859,"insert_1.insertion_depth":0.0827,"insert_1.insertion_force":12.43528,"push_1.push_distance":0.04746,"push_1.push_speed":0.07018},"optimized_scores":{"best_composite_score":0.41528,"best_fitness_score":0.44194,"best_task_score":0.79661},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":34.0,"contact_point_centroid":[0.53363,0.02777,0.04941],"force_p95":75.37328,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":122.88632,"mean_force":43.56139,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52752,0.03758,0.05159]},{"body_a":"world","body_b":"push_box","contact_count":2151.0,"contact_point_centroid":[0.55567,-0.05406,-0.00015],"force_p95":52.94968,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":79.97358,"mean_force":20.07101,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52629,-0.00785,0.02091]},{"body_a":"world","body_b":"push_box","contact_count":2654.0,"contact_point_centroid":[0.55347,0.00211,-3e-05],"force_p95":0.25955,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":69.67204,"mean_force":0.81128,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52008,0.02256,0.06257]},{"body_a":"push_box","body_b":"link7","contact_count":1080.0,"contact_point_centroid":[0.56048,-0.04907,0.04959],"force_p95":51.97966,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.94373,"mean_force":34.27369,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52195,-0.02922,0.0211]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.5454,-0.1124,0.04864],"force_p95":45.61872,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.61872,"mean_force":45.61872,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50827,-0.09334,0.02062]},{"body_a":"attachment","body_b":"push_box","contact_count":868.0,"contact_point_centroid":[0.52721,-0.05617,0.03583],"force_p95":32.83799,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.44994,"mean_force":11.48722,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51879,-0.04534,0.02141]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.54524,-0.12162,-0.00027],"force_p95":28.35804,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.45924,"mean_force":27.44716,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50827,-0.09334,0.02062]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.5299,-0.1019,0.04954],"force_p95":11.31936,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.31936,"mean_force":11.31936,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50827,-0.09334,0.02062]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49719,-0.01576,0.20157]}],"total_contact_groups":9},"final_pose_error":0.05743,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52953,-0.13634,0.02749],"final_tcp_position":[0.50828,-0.09334,0.02062],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":122.88632,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2688.0,"raw_peak_contact_force":122.88632,"tcp_end":[0.49637,-0.0315,0.10675],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10483,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":684.0,"n_steps_budget":960.0,"object_pos_end":[0.55401,0.00129,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16064,"object_to_goal_dist_start":0.16043,"object_z_max":0.02562,"peak_contact_force":34.75301,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4099.0,"raw_peak_contact_force":79.97358,"tcp_end":[0.54574,0.0749,0.02342],"tcp_start":[0.49637,-0.0315,0.10675],"tcp_to_object_dist_end":0.07409,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52952,-0.13634,0.02749],"object_pos_start":[0.55401,0.00129,0.02499],"object_to_goal_dist_end":0.03263,"object_to_goal_dist_start":0.16064,"object_z_max":0.02908,"peak_contact_force":45.61872,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4.0,"raw_peak_contact_force":45.61872,"tcp_end":[0.50827,-0.09334,0.02062],"tcp_start":[0.54574,0.0749,0.02342],"tcp_to_object_dist_end":0.04845,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.52953,-0.13634,0.02749],"object_pos_start":[0.52952,-0.13634,0.02749],"object_to_goal_dist_end":0.03263,"object_to_goal_dist_start":0.03263,"object_z_max":0.02749,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50828,-0.09334,0.02062],"tcp_start":[0.50827,-0.09334,0.02062],"tcp_to_object_dist_end":0.04846,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90698,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00707,"align_1.lateral_offset_y":-0.00199,"insert_1.insertion_depth":0.04537,"insert_1.insertion_force":2.60248,"push_1.push_distance":0.18723,"push_1.push_speed":0.09748},"optimized_scores":{"best_composite_score":0.37079,"best_fitness_score":0.39746,"best_task_score":0.67918},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":223.0,"contact_point_centroid":[0.53604,0.07082,0.04606],"force_p95":153.4347,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":181.88722,"mean_force":99.36298,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52878,0.07819,0.04807]},{"body_a":"attachment","body_b":"push_box","contact_count":935.0,"contact_point_centroid":[0.53341,0.02827,0.0347],"force_p95":155.80926,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":164.07126,"mean_force":116.07703,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52927,0.03847,0.03545]},{"body_a":"world","body_b":"push_box","contact_count":3351.0,"contact_point_centroid":[0.53703,0.04034,-7e-05],"force_p95":56.5442,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.69668,"mean_force":7.52135,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51042,-0.00064,0.08684]},{"body_a":"world","body_b":"push_box","contact_count":2489.0,"contact_point_centroid":[0.53736,-0.02458,-0.00043],"force_p95":104.76129,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":114.94864,"mean_force":58.93571,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52605,0.02244,0.03329]},{"body_a":"push_box","body_b":"link7","contact_count":974.0,"contact_point_centroid":[0.56197,0.00546,0.06871],"force_p95":72.60484,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.58128,"mean_force":51.23067,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52954,0.04172,0.03532]},{"body_a":"push_box","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.56733,0.07369,0.06701],"force_p95":75.66443,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.72935,"mean_force":62.9438,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53389,0.10633,0.0342]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55375,-0.07289,0.04998],"force_p95":17.46689,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":17.46689,"mean_force":17.46689,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51037,-0.04987,0.02278]},{"body_a":"world","body_b":"push_box","contact_count":96.0,"contact_point_centroid":[0.53593,-0.10055,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.96546,"mean_force":0.42543,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51136,-0.04828,0.0237]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49729,-0.04337,0.21611]}],"total_contact_groups":9},"final_pose_error":0.10056,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53592,-0.10056,0.02499],"final_tcp_position":[0.5103,-0.04999,0.02271],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":181.88722,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":72.14804,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3607.0,"raw_peak_contact_force":181.88722,"tcp_end":[0.49662,-0.08549,0.13811],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17143,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":960.0,"n_steps_budget":1000.0,"object_pos_end":[0.54238,0.06691,0.03274],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.22114,"object_to_goal_dist_start":0.1905,"object_z_max":0.03488,"peak_contact_force":0.24527,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4398.0,"raw_peak_contact_force":164.07126,"tcp_end":[0.53503,0.11012,0.03195],"tcp_start":[0.49662,-0.08549,0.13811],"tcp_to_object_dist_end":0.04384,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53592,-0.10055,0.02499],"object_pos_start":[0.54238,0.06691,0.03274],"object_to_goal_dist_end":0.06112,"object_to_goal_dist_start":0.22114,"object_z_max":0.03447,"peak_contact_force":17.46689,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":97.0,"raw_peak_contact_force":17.46689,"tcp_end":[0.51221,-0.04707,0.02455],"tcp_start":[0.53503,0.11012,0.03195],"tcp_to_object_dist_end":0.0585,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":24.0,"n_steps_budget":660.0,"object_pos_end":[0.53592,-0.10056,0.02499],"object_pos_start":[0.53592,-0.10055,0.02499],"object_to_goal_dist_end":0.06112,"object_to_goal_dist_start":0.06112,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.5103,-0.04999,0.02271],"tcp_start":[0.51221,-0.04707,0.02455],"tcp_to_object_dist_end":0.05673,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89474,"average_solve_count":114.0,"average_success_count":114.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00039,"align_1.lateral_offset_y":0.00614,"insert_1.insertion_depth":0.04592,"insert_1.insertion_force":12.83332,"push_1.push_distance":0.0769,"push_1.push_speed":0.09826},"optimized_scores":{"best_composite_score":0.48892,"best_fitness_score":0.51558,"best_task_score":0.95437},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":147.0,"contact_point_centroid":[0.50795,0.02116,0.04412],"force_p95":113.97709,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.63425,"mean_force":71.52371,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50108,0.02988,0.04672]},{"body_a":"world","body_b":"push_box","contact_count":1837.0,"contact_point_centroid":[0.50486,-0.01463,-7e-05],"force_p95":58.1872,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":120.38762,"mean_force":7.58807,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49675,-0.01475,0.0749]},{"body_a":"push_box","body_b":"link7","contact_count":36.0,"contact_point_centroid":[0.53235,0.00846,0.06851],"force_p95":94.7193,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.53488,"mean_force":79.90274,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.50336,0.05048,0.03385]},{"body_a":"attachment","body_b":"push_box","contact_count":779.0,"contact_point_centroid":[0.50319,-0.04084,0.02851],"force_p95":84.50983,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":89.86046,"mean_force":40.08825,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.5018,-0.02933,0.02734]},{"body_a":"push_box","body_b":"link7","contact_count":562.0,"contact_point_centroid":[0.52756,-0.04887,0.06494],"force_p95":71.99508,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.51125,"mean_force":31.27808,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50332,-0.00822,0.02897]},{"body_a":"world","body_b":"push_box","contact_count":2613.0,"contact_point_centroid":[0.49967,-0.09159,-0.00018],"force_p95":59.55019,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":68.09814,"mean_force":17.49078,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.50004,-0.04721,0.02523]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52335,-0.14384,0.0494],"force_p95":40.18001,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.18001,"mean_force":40.18001,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49466,-0.11739,0.01822]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49836,-0.15587,-0.00011],"force_p95":22.0289,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.40151,"mean_force":10.29879,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49466,-0.11739,0.01822]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49721,-0.03189,0.20383]}],"total_contact_groups":9},"final_pose_error":0.03374,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49842,-0.15578,0.02478],"final_tcp_position":[0.49466,-0.11739,0.01821],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":137.63425,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":92.50282,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2020.0,"raw_peak_contact_force":137.63425,"tcp_end":[0.49646,-0.06331,0.11252],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09853,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":549.0,"n_steps_budget":960.0,"object_pos_end":[0.50735,0.00635,0.03377],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.15677,"object_to_goal_dist_start":0.13127,"object_z_max":0.03541,"peak_contact_force":21.73412,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3954.0,"raw_peak_contact_force":89.86046,"tcp_end":[0.50474,0.05429,0.03196],"tcp_start":[0.49646,-0.06331,0.11252],"tcp_to_object_dist_end":0.04804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49843,-0.15577,0.02479],"object_pos_start":[0.50735,0.00635,0.03377],"object_to_goal_dist_end":0.00599,"object_to_goal_dist_start":0.15677,"object_z_max":0.03481,"peak_contact_force":40.18001,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":5.0,"raw_peak_contact_force":40.18001,"tcp_end":[0.49466,-0.11739,0.01822],"tcp_start":[0.50474,0.05429,0.03196],"tcp_to_object_dist_end":0.03913,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49842,-0.15578,0.02478],"object_pos_start":[0.49843,-0.15577,0.02479],"object_to_goal_dist_end":0.00599,"object_to_goal_dist_start":0.00599,"object_z_max":0.02479,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49466,-0.11739,0.01821],"tcp_start":[0.49466,-0.11739,0.01822],"tcp_to_object_dist_end":0.03913,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```