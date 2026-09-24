## Search State

- **Seed**: 4
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4176 | 0.79 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4172 | 0.80 | ✅ accepted |

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

## Current Skill (Q=0.418) — your mutation base

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

- **Composite score**: 0.418
- **task_score** (E): 0.792
- **fitness_score**: 0.444  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| push_1 | 1.00 | 1.00 | 0.1900 |
| align_1 | 1.00 | 1.00 | 0.1750 |
| release_1 | 0.33 | 1.00 | 0.1687 |
| insert_1 | 1.00 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.496, -0.062, 0.122) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 3.667 | 24.996 | 93.798 |
| align_1 | align | 1.00 / step_budget | (0.496, -0.062, 0.122)→(0.527, 0.079, 0.027) | (0.531, 0.007, 0.025)→(0.534, 0.017, 0.028) | 0.161→0.171 | 1.00 / 5.000 | 20.809 | 100.417 |
| release_1 | release | 0.33 / step_budget | (0.527, 0.079, 0.027)→(0.504, -0.087, 0.020) | (0.534, 0.017, 0.028)→(0.522, -0.130, 0.025) | 0.171→0.036 | 1.00 / 5.000 | 39.854 | 39.854 |
| insert_1 | insert | 1.00 / force_exceeded | (0.504, -0.087, 0.020)→(0.504, -0.087, 0.020) | (0.522, -0.130, 0.025)→(0.522, -0.130, 0.025) | 0.036→0.036 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.696
- goal_progress: 0.932
- terminal_score: 0.932
- phase_score: 0.218
- phase_breakdown.push_score: 0.107
- phase_breakdown.approach_score: 0.821
- phase_breakdown.contact_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.504
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.932
- **Median Q (composite search score)**: 0.406
- **K-run variance**: 0.0020
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.68889,"average_solve_count":135.0,"average_success_count":135.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.0003,"align_1.lateral_offset_y":0.00028,"insert_1.insertion_depth":0.07811,"insert_1.insertion_force":7.44283,"push_1.push_distance":0.06921,"push_1.push_speed":0.06495},"optimized_scores":{"best_composite_score":0.4065,"best_fitness_score":0.43316,"best_task_score":0.77159},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":24.0,"contact_point_centroid":[0.5352,0.02708,0.04965],"force_p95":49.94088,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":95.39886,"mean_force":32.24806,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52943,0.03721,0.05175]},{"body_a":"world","body_b":"push_box","contact_count":2234.0,"contact_point_centroid":[0.5555,-0.05668,-0.00016],"force_p95":57.06776,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.99625,"mean_force":20.37407,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52609,-0.01002,0.02113]},{"body_a":"push_box","body_b":"link7","contact_count":1076.0,"contact_point_centroid":[0.56112,-0.04817,0.04973],"force_p95":57.2377,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.25349,"mean_force":35.52721,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52223,-0.02907,0.02135]},{"body_a":"attachment","body_b":"push_box","contact_count":865.0,"contact_point_centroid":[0.52915,-0.05539,0.03783],"force_p95":42.83616,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.23226,"mean_force":14.38442,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51915,-0.04485,0.02167]},{"body_a":"world","body_b":"push_box","contact_count":2897.0,"contact_point_centroid":[0.5533,0.00183,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":50.73081,"mean_force":0.51713,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52027,0.01647,0.06718]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54618,-0.11084,0.04916],"force_p95":45.45606,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.45606,"mean_force":45.45606,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50904,-0.09186,0.02114]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.53216,-0.13286,-0.00014],"force_p95":26.47703,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.60124,"mean_force":13.91437,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50904,-0.09186,0.02114]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53072,-0.10008,0.04951],"force_p95":12.53014,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.53014,"mean_force":12.53014,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50904,-0.09186,0.02114]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49722,-0.022,0.20635]}],"total_contact_groups":9},"final_pose_error":0.05897,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53232,-0.13274,0.02471],"final_tcp_position":[0.50904,-0.09185,0.02113],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":95.39886,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2921.0,"raw_peak_contact_force":95.39886,"tcp_end":[0.49644,-0.04398,0.11629],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11666,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":738.0,"n_steps_budget":1000.0,"object_pos_end":[0.5536,0.00135,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16056,"object_to_goal_dist_start":0.16043,"object_z_max":0.02533,"peak_contact_force":30.94975,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4175.0,"raw_peak_contact_force":82.99625,"tcp_end":[0.54596,0.07472,0.02357],"tcp_start":[0.49644,-0.04398,0.11629],"tcp_to_object_dist_end":0.07378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":6.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53232,-0.13274,0.02471],"object_pos_start":[0.5536,0.00135,0.02499],"object_to_goal_dist_end":0.03664,"object_to_goal_dist_start":0.16056,"object_z_max":0.02885,"peak_contact_force":45.45606,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":6.0,"raw_peak_contact_force":45.45606,"tcp_end":[0.50904,-0.09186,0.02114],"tcp_start":[0.54596,0.07472,0.02357],"tcp_to_object_dist_end":0.04718,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53232,-0.13274,0.02471],"object_pos_start":[0.53232,-0.13274,0.02471],"object_to_goal_dist_end":0.03664,"object_to_goal_dist_start":0.03664,"object_z_max":0.02471,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50904,-0.09185,0.02113],"tcp_start":[0.50904,-0.09186,0.02114],"tcp_to_object_dist_end":0.04719,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90551,"average_solve_count":127.0,"average_success_count":127.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00574,"align_1.lateral_offset_y":0.00917,"insert_1.insertion_depth":0.01926,"insert_1.insertion_force":1.92513,"push_1.push_distance":0.17715,"push_1.push_speed":0.09649},"optimized_scores":{"best_composite_score":0.36936,"best_fitness_score":0.39603,"best_task_score":0.67104},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":239.0,"contact_point_centroid":[0.53614,0.07006,0.04621],"force_p95":153.50951,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":185.74896,"mean_force":102.88111,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52876,0.07729,0.04823]},{"body_a":"attachment","body_b":"push_box","contact_count":910.0,"contact_point_centroid":[0.53382,0.03072,0.03481],"force_p95":155.46962,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":163.56146,"mean_force":116.22318,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52963,0.0409,0.03558]},{"body_a":"world","body_b":"push_box","contact_count":3284.0,"contact_point_centroid":[0.53713,0.04071,-8e-05],"force_p95":62.0048,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":149.04817,"mean_force":8.46027,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.51042,0.00109,0.08441]},{"body_a":"world","body_b":"push_box","contact_count":2426.0,"contact_point_centroid":[0.53848,-0.02296,-0.00042],"force_p95":104.87233,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.61963,"mean_force":59.37181,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52596,0.0238,0.03309]},{"body_a":"push_box","body_b":"link7","contact_count":1047.0,"contact_point_centroid":[0.56189,-0.00031,0.06726],"force_p95":72.97261,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.83841,"mean_force":47.23616,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52817,0.0351,0.03443]},{"body_a":"push_box","body_b":"link7","contact_count":34.0,"contact_point_centroid":[0.56771,0.07374,0.06721],"force_p95":77.76449,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":77.82734,"mean_force":65.70806,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.53411,0.10646,0.03444]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.55327,-0.07282,0.04975],"force_p95":31.85989,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":31.85989,"mean_force":31.85989,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50986,-0.04947,0.02243]},{"body_a":"world","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.5446,-0.09047,-5e-05],"force_p95":20.25132,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.84005,"mean_force":10.99589,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50986,-0.04947,0.02243]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49728,-0.04154,0.21399]}],"total_contact_groups":9},"final_pose_error":0.10105,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53715,-0.09953,0.02493],"final_tcp_position":[0.50985,-0.04947,0.02242],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":185.74896,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":74.4968,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3557.0,"raw_peak_contact_force":185.74896,"tcp_end":[0.49657,-0.08209,0.1335],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16598,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":950.0,"n_steps_budget":1000.0,"object_pos_end":[0.5428,0.06716,0.03284],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.22147,"object_to_goal_dist_start":0.1905,"object_z_max":0.03486,"peak_contact_force":6.22548,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":4383.0,"raw_peak_contact_force":163.56146,"tcp_end":[0.53526,0.1103,0.03213],"tcp_start":[0.49657,-0.08209,0.1335],"tcp_to_object_dist_end":0.0438,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53714,-0.09953,0.02493],"object_pos_start":[0.5428,0.06716,0.03284],"object_to_goal_dist_end":0.06266,"object_to_goal_dist_start":0.22147,"object_z_max":0.03448,"peak_contact_force":31.85989,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":4.0,"raw_peak_contact_force":31.85989,"tcp_end":[0.50986,-0.04947,0.02243],"tcp_start":[0.53526,0.1103,0.03213],"tcp_to_object_dist_end":0.05707,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":660.0,"object_pos_end":[0.53715,-0.09953,0.02493],"object_pos_start":[0.53714,-0.09953,0.02493],"object_to_goal_dist_end":0.06267,"object_to_goal_dist_start":0.06266,"object_z_max":0.02493,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50985,-0.04947,0.02242],"tcp_start":[0.50986,-0.04947,0.02243],"tcp_to_object_dist_end":0.05707,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.90083,"average_solve_count":121.0,"average_success_count":121.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.0015,"align_1.lateral_offset_y":0.00397,"insert_1.insertion_depth":0.0431,"insert_1.insertion_force":9.69997,"push_1.push_distance":0.07599,"push_1.push_speed":0.08241},"optimized_scores":{"best_composite_score":0.47702,"best_fitness_score":0.50369,"best_task_score":0.93224},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2263.0,"contact_point_centroid":[0.50614,-0.09219,-8e-05],"force_p95":36.07903,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":54.69442,"mean_force":10.00632,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49631,-0.04056,0.02108]},{"body_a":"attachment","body_b":"push_box","contact_count":788.0,"contact_point_centroid":[0.51239,-0.06609,0.0473],"force_p95":43.83653,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.85442,"mean_force":17.99694,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49692,-0.05483,0.02165]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52186,-0.14725,0.04935],"force_p95":42.24743,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.24743,"mean_force":42.24743,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49425,-0.12052,0.01762]},{"body_a":"push_box","body_b":"link7","contact_count":711.0,"contact_point_centroid":[0.52372,-0.07898,0.05309],"force_p95":30.80076,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.10122,"mean_force":18.16426,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49673,-0.05728,0.02132]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49752,-0.15865,-0.00012],"force_p95":22.3029,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":23.35406,"mean_force":10.84,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49425,-0.12052,0.01762]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49722,-0.03085,0.20598]},{"body_a":"world","body_b":"push_box","contact_count":2300.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49673,-0.00398,0.06909]}],"total_contact_groups":7},"final_pose_error":0.03093,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49759,-0.15856,0.02475],"final_tcp_position":[0.49425,-0.12052,0.01761],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":54.69442,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2300.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.4964,-0.06135,0.1165],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10125,"terminated_normally":true,"termination_reason":"time_limit"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":575.0,"n_steps_budget":960.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":25.25312,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","raw_contact_event_count":3762.0,"raw_peak_contact_force":54.69442,"tcp_end":[0.49982,0.05264,0.02607],"tcp_start":[0.4964,-0.06135,0.1165],"tcp_to_object_dist_end":0.07162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4976,-0.15856,0.02476],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00889,"object_to_goal_dist_start":0.13127,"object_z_max":0.02918,"peak_contact_force":42.24743,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":5.0,"raw_peak_contact_force":42.24743,"tcp_end":[0.49425,-0.12052,0.01762],"tcp_start":[0.49982,0.05264,0.02607],"tcp_to_object_dist_end":0.03885,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49759,-0.15856,0.02475],"object_pos_start":[0.4976,-0.15856,0.02476],"object_to_goal_dist_end":0.00889,"object_to_goal_dist_start":0.00889,"object_z_max":0.02476,"peak_contact_force":0.24525,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.49425,-0.12052,0.01761],"tcp_start":[0.49425,-0.12052,0.01762],"tcp_to_object_dist_end":0.03885,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```