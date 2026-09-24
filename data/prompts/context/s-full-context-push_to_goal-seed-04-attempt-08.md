## Search State

- **Seed**: 4
- **Iteration**: 9 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 8 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4172 | 0.79 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.1299 | 0.30 | ❌ rejected |
| 6 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4196 | 0.80 | ❌ rejected |
| 5 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4202 | 0.80 | ❌ rejected |
| 4 | approach → descend → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | 4 | 0.3996 | 0.37 | ❌ rejected |

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
- **task_score** (E): 0.792
- **fitness_score**: 0.444  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1894 |
| align_1 | 1.00 | 1.00 | 0.1781 |
| release_1 | 0.33 | 1.00 | 0.1685 |
| insert_1 | 1.00 | 1.00 | 0.0011 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.496, -0.066, 0.124) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| align_1 | align | 1.00 / step_budget | (0.496, -0.066, 0.124)→(0.527, 0.079, 0.027) | (0.531, 0.007, 0.025)→(0.534, 0.016, 0.028) | 0.161→0.171 | 1.00 / 3.667 | 24.196 | 127.773 |
| release_1 | release | 0.33 / step_budget | (0.527, 0.079, 0.027)→(0.505, -0.087, 0.021) | (0.534, 0.016, 0.028)→(0.523, -0.131, 0.025) | 0.171→0.036 | 1.00 / 4.333 | 24.855 | 100.659 |
| insert_1 | insert | 1.00 / force_exceeded | (0.505, -0.087, 0.021)→(0.505, -0.088, 0.021) | (0.523, -0.131, 0.025)→(0.523, -0.131, 0.025) | 0.036→0.036 | 1.00 / 4.667 | 38.466 | 38.466 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.696
- goal_progress: 0.935
- terminal_score: 0.935
- phase_score: 0.219
- phase_breakdown.approach_score: 0.820
- phase_breakdown.push_score: 0.111
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.506
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.935
- **Median Q (composite search score)**: 0.402
- **K-run variance**: 0.0021
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.293


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69343,"average_solve_count":137.0,"average_success_count":137.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00503,"align_1.lateral_offset_y":0.00463,"insert_1.insertion_depth":0.06851,"insert_1.insertion_force":7.70126,"push_1.push_distance":0.10745,"push_1.push_speed":0.06371},"optimized_scores":{"best_composite_score":0.40236,"best_fitness_score":0.42903,"best_task_score":0.76215},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2146.0,"contact_point_centroid":[0.55764,-0.05204,-0.00016],"force_p95":58.16008,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":81.9499,"mean_force":21.14154,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52662,-0.00794,0.0212]},{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.53755,0.0264,0.04992],"force_p95":67.49029,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.17695,"mean_force":38.90795,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53168,0.0366,0.05214]},{"body_a":"push_box","body_b":"link7","contact_count":1071.0,"contact_point_centroid":[0.56218,-0.04779,0.0494],"force_p95":55.20183,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":60.2738,"mean_force":36.16554,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52204,-0.03021,0.02139]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54696,-0.11118,0.04886],"force_p95":52.46471,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.46471,"mean_force":52.46471,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5086,-0.09433,0.02132]},{"body_a":"world","body_b":"push_box","contact_count":3256.0,"contact_point_centroid":[0.55329,0.00145,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.0691,"mean_force":0.34187,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52057,0.00733,0.0741]},{"body_a":"attachment","body_b":"push_box","contact_count":853.0,"contact_point_centroid":[0.5299,-0.05617,0.03874],"force_p95":35.66749,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.52161,"mean_force":12.42243,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51893,-0.04591,0.02167]},{"body_a":"world","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.55049,-0.11732,-0.00031],"force_p95":31.17788,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.23069,"mean_force":30.70262,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5086,-0.09433,0.02132]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53105,-0.10167,0.04939],"force_p95":11.57866,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.57866,"mean_force":11.57866,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.5086,-0.09433,0.02132]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49726,-0.03171,0.2133]}],"total_contact_groups":9},"final_pose_error":0.05645,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53529,-0.13549,0.02562],"final_tcp_position":[0.5086,-0.09433,0.02132],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":81.9499,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4965,-0.06316,0.13085],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13631,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":817.0,"n_steps_budget":1000.0,"object_pos_end":[0.55339,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.1605,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3264.0,"raw_peak_contact_force":75.17695,"tcp_end":[0.54619,0.07436,0.02385],"tcp_start":[0.4965,-0.06316,0.13085],"tcp_to_object_dist_end":0.07336,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53529,-0.13549,0.02562],"object_pos_start":[0.55339,0.00136,0.02499],"object_to_goal_dist_end":0.03816,"object_to_goal_dist_start":0.1605,"object_z_max":0.02977,"peak_contact_force":43.66752,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4070.0,"raw_peak_contact_force":81.9499,"tcp_end":[0.5086,-0.09433,0.02132],"tcp_start":[0.54619,0.07436,0.02385],"tcp_to_object_dist_end":0.04924,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53529,-0.13549,0.02562],"object_pos_start":[0.53529,-0.13549,0.02562],"object_to_goal_dist_end":0.03816,"object_to_goal_dist_start":0.03816,"object_z_max":0.02562,"peak_contact_force":52.46471,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4.0,"raw_peak_contact_force":52.46471,"tcp_end":[0.5086,-0.09433,0.02132],"tcp_start":[0.5086,-0.09433,0.02132],"tcp_to_object_dist_end":0.04925,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90625,"average_solve_count":128.0,"average_success_count":128.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00357,"align_1.lateral_offset_y":-0.00242,"insert_1.insertion_depth":0.09202,"insert_1.insertion_force":13.27654,"push_1.push_distance":0.19052,"push_1.push_speed":0.09986},"optimized_scores":{"best_composite_score":0.37018,"best_fitness_score":0.39685,"best_task_score":0.6787},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":221.0,"contact_point_centroid":[0.53604,0.07098,0.04602],"force_p95":152.78972,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":181.69965,"mean_force":98.59982,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5288,0.07836,0.04803]},{"body_a":"attachment","body_b":"push_box","contact_count":933.0,"contact_point_centroid":[0.5334,0.0284,0.03469],"force_p95":155.59435,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.84029,"mean_force":115.99739,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52927,0.0386,0.03545]},{"body_a":"world","body_b":"push_box","contact_count":3371.0,"contact_point_centroid":[0.53702,0.04029,-7e-05],"force_p95":56.16289,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":147.63191,"mean_force":7.36799,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51043,-0.00123,0.08742]},{"body_a":"world","body_b":"push_box","contact_count":2523.0,"contact_point_centroid":[0.53727,-0.02533,-0.00041],"force_p95":104.36175,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":113.85051,"mean_force":57.97762,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52581,0.0214,0.03314]},{"body_a":"push_box","body_b":"link7","contact_count":973.0,"contact_point_centroid":[0.56194,0.00547,0.06871],"force_p95":72.59053,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":85.41045,"mean_force":51.13756,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52954,0.04177,0.03531]},{"body_a":"push_box","body_b":"link7","contact_count":33.0,"contact_point_centroid":[0.56732,0.07361,0.06702],"force_p95":75.60417,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":75.67147,"mean_force":62.85481,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53387,0.1063,0.0342]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55376,-0.07275,0.04998],"force_p95":18.5644,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":18.5644,"mean_force":18.5644,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51038,-0.04975,0.02279]},{"body_a":"world","body_b":"push_box","contact_count":84.0,"contact_point_centroid":[0.53593,-0.10044,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.39587,"mean_force":0.46431,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.51125,-0.04836,0.02361]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.4973,-0.044,0.21669]}],"total_contact_groups":9},"final_pose_error":0.10068,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53593,-0.10044,0.02499],"final_tcp_position":[0.5103,-0.04988,0.02272],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":181.69965,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49661,-0.08671,0.13928],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17307,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.54237,0.06685,0.03274],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.22109,"object_to_goal_dist_start":0.1905,"object_z_max":0.03489,"peak_contact_force":72.09696,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3625.0,"raw_peak_contact_force":181.69965,"tcp_end":[0.53501,0.1101,0.03195],"tcp_start":[0.49661,-0.08671,0.13928],"tcp_to_object_dist_end":0.04387,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53593,-0.10044,0.02499],"object_pos_start":[0.54237,0.06685,0.03274],"object_to_goal_dist_end":0.06121,"object_to_goal_dist_start":0.22109,"object_z_max":0.03447,"peak_contact_force":0.24525,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4429.0,"raw_peak_contact_force":163.84029,"tcp_end":[0.51197,-0.04737,0.02434],"tcp_start":[0.53501,0.1101,0.03195],"tcp_to_object_dist_end":0.05823,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":21.0,"n_steps_budget":660.0,"object_pos_end":[0.53593,-0.10044,0.02499],"object_pos_start":[0.53593,-0.10044,0.02499],"object_to_goal_dist_end":0.06121,"object_to_goal_dist_start":0.06121,"object_z_max":0.02499,"peak_contact_force":18.5644,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":85.0,"raw_peak_contact_force":18.5644,"tcp_end":[0.5103,-0.04988,0.02272],"tcp_start":[0.51197,-0.04737,0.02434],"tcp_to_object_dist_end":0.05673,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.89189,"average_solve_count":111.0,"average_success_count":111.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00933,"align_1.lateral_offset_y":0.0075,"insert_1.insertion_depth":0.10318,"insert_1.insertion_force":10.68768,"push_1.push_distance":0.04854,"push_1.push_speed":0.09748},"optimized_scores":{"best_composite_score":0.47895,"best_fitness_score":0.50562,"best_task_score":0.93487},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":51.0,"contact_point_centroid":[0.50445,0.00951,0.04895],"force_p95":98.78298,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":126.44322,"mean_force":62.21039,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49832,0.01897,0.05149]},{"body_a":"world","body_b":"push_box","contact_count":1855.0,"contact_point_centroid":[0.50501,-0.01744,-6e-05],"force_p95":12.31056,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":110.47479,"mean_force":1.97987,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49676,0.00134,0.0637]},{"body_a":"world","body_b":"push_box","contact_count":2367.0,"contact_point_centroid":[0.50621,-0.09309,-8e-05],"force_p95":35.26985,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.18715,"mean_force":10.09075,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49644,-0.04224,0.02117]},{"body_a":"attachment","body_b":"push_box","contact_count":741.0,"contact_point_centroid":[0.51161,-0.06279,0.04599],"force_p95":46.01199,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.26929,"mean_force":18.6093,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49705,-0.05153,0.0218]},{"body_a":"push_box","body_b":"link7","contact_count":679.0,"contact_point_centroid":[0.52468,-0.07444,0.05287],"force_p95":34.84256,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.75878,"mean_force":21.16695,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49686,-0.05378,0.02144]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52403,-0.14687,0.04925],"force_p95":44.36745,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.36745,"mean_force":44.36745,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49486,-0.12056,0.01817]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49907,-0.15862,-0.00014],"force_p95":24.98176,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.57468,"mean_force":11.34658,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49486,-0.12056,0.01817]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49718,-0.02361,0.19907]}],"total_contact_groups":8},"final_pose_error":0.03066,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49915,-0.1585,0.02472],"final_tcp_position":[0.49486,-0.12055,0.01816],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":126.44322,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49629,-0.04701,0.10251],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08291,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":499.0,"n_steps_budget":840.0,"object_pos_end":[0.5054,-0.01924,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13087,"object_to_goal_dist_start":0.13127,"object_z_max":0.02752,"peak_contact_force":0.24525,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":1906.0,"raw_peak_contact_force":126.44322,"tcp_end":[0.49983,0.05257,0.02603],"tcp_start":[0.49629,-0.04701,0.10251],"tcp_to_object_dist_end":0.07204,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49916,-0.1585,0.02472],"object_pos_start":[0.5054,-0.01924,0.02499],"object_to_goal_dist_end":0.00855,"object_to_goal_dist_start":0.13087,"object_z_max":0.02901,"peak_contact_force":30.65335,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":3787.0,"raw_peak_contact_force":56.18715,"tcp_end":[0.49486,-0.12056,0.01817],"tcp_start":[0.49983,0.05257,0.02603],"tcp_to_object_dist_end":0.03875,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49915,-0.1585,0.02472],"object_pos_start":[0.49916,-0.1585,0.02472],"object_to_goal_dist_end":0.00855,"object_to_goal_dist_start":0.00855,"object_z_max":0.02472,"peak_contact_force":44.36745,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":5.0,"raw_peak_contact_force":44.36745,"tcp_end":[0.49486,-0.12055,0.01816],"tcp_start":[0.49486,-0.12056,0.01817],"tcp_to_object_dist_end":0.03875,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```