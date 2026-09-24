## Search State

- **Seed**: 4
- **Iteration**: 5 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 4 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4288 | 0.84 | ✅ accepted |
| 3 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4198 | 0.80 | ✅ accepted |
| 2 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | -0.0519 | 0.00 | ❌ rejected |
| 1 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | pose_tolerance | 3 | 0.0297 | 0.07 | ❌ rejected |
| 0 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4172 | 0.80 | ✅ accepted |

**Proposal policy**: task_score is 0.84 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.429) — your mutation base

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

- **Composite score**: 0.429
- **task_score** (E): 0.839
- **fitness_score**: 0.456  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.333
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.360

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| push_1 | 1.00 | 0.1878 |
| align_1 | 1.00 | 0.1491 |
| release_1 | 0.33 | 0.1771 |
| insert_1 | 1.00 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| push_1 | push | 1.00 / time_limit | (0.500, -0.000, 0.301)→(0.496, -0.032, 0.118) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 |
| align_1 | align | 1.00 / step_budget | (0.496, -0.032, 0.118)→(0.525, 0.079, 0.025) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 |
| release_1 | release | 0.33 / step_budget | (0.525, 0.079, 0.025)→(0.502, -0.096, 0.019) | (0.531, 0.007, 0.025)→(0.512, -0.135, 0.025) | 0.161→0.027 |
| insert_1 | insert | 1.00 / force_exceeded | (0.502, -0.096, 0.019)→(0.502, -0.096, 0.019) | (0.512, -0.135, 0.025)→(0.512, -0.135, 0.025) | 0.027→0.027 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- approach_alignment: 0.695
- goal_progress: 0.933
- terminal_score: 0.933
- phase_score: 0.207
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.086

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.497
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.933
- **Median Q (composite search score)**: 0.410
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.340


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75194,"average_solve_count":129.0,"average_success_count":129.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00223,"align_1.lateral_offset_y":-0.00792,"insert_1.insertion_depth":0.09393,"insert_1.insertion_force":4.46376,"push_1.push_distance":0.04509,"push_1.push_speed":0.07014},"optimized_scores":{"best_composite_score":0.40595,"best_fitness_score":0.43262,"best_task_score":0.77463},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":2244.0,"contact_point_centroid":[0.55523,-0.05621,-0.00016],"force_p95":56.33718,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":82.79522,"mean_force":20.33558,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52613,-0.0091,0.02105]},{"body_a":"push_box","body_b":"link7","contact_count":1076.0,"contact_point_centroid":[0.56067,-0.04833,0.04977],"force_p95":57.20205,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":62.99219,"mean_force":35.7756,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.52215,-0.0289,0.0213]},{"body_a":"attachment","body_b":"push_box","contact_count":869.0,"contact_point_centroid":[0.52887,-0.05519,0.03763],"force_p95":42.93288,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.60389,"mean_force":14.21871,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51911,-0.04459,0.02163]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.54595,-0.111,0.04917],"force_p95":45.01502,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.01502,"mean_force":45.01502,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50899,-0.09171,0.02107]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.53156,-0.13277,-0.00014],"force_p95":26.22491,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.32776,"mean_force":13.81831,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50899,-0.09171,0.02107]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.53175,0.02637,0.04998],"force_p95":15.85593,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":15.86063,"mean_force":15.6315,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52659,0.037,0.052]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.53056,-0.10005,0.04953],"force_p95":12.6215,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.6215,"mean_force":12.6215,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50899,-0.09171,0.02107]},{"body_a":"world","body_b":"push_box","contact_count":2723.0,"contact_point_centroid":[0.55315,0.00141,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.90647,"mean_force":0.26306,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.52035,0.02406,0.062]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49719,-0.01492,0.20178]}],"total_contact_groups":9},"final_pose_error":0.05912,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53172,-0.13266,0.02472],"final_tcp_position":[0.50899,-0.0917,0.02106],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49638,-0.02987,0.10684],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1044,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":682.0,"n_steps_budget":930.0,"object_pos_end":[0.55318,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.54574,0.07497,0.02343],"tcp_start":[0.49638,-0.02987,0.10684],"tcp_to_object_dist_end":0.074,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53172,-0.13265,0.02472],"object_pos_start":[0.55318,0.00136,0.02499],"object_to_goal_dist_end":0.03616,"object_to_goal_dist_start":0.16043,"object_z_max":0.0287,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.50899,-0.09171,0.02107],"tcp_start":[0.54574,0.07497,0.02343],"tcp_to_object_dist_end":0.04697,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.53172,-0.13266,0.02472],"object_pos_start":[0.53172,-0.13265,0.02472],"object_to_goal_dist_end":0.03616,"object_to_goal_dist_start":0.03616,"object_z_max":0.02472,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.50899,-0.0917,0.02106],"tcp_start":[0.50899,-0.09171,0.02107],"tcp_to_object_dist_end":0.04698,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.39873,"average_solve_count":158.0,"average_success_count":158.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":-0.00336,"align_1.lateral_offset_y":0.00192,"insert_1.insertion_depth":0.11894,"insert_1.insertion_force":9.26499,"push_1.push_distance":0.03863,"push_1.push_speed":0.04542},"optimized_scores":{"best_composite_score":0.40974,"best_fitness_score":0.43641,"best_task_score":0.80958},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.53176,-0.10201,0.04927],"force_p95":44.33687,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":44.33687,"mean_force":44.33687,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50313,-0.07616,0.01778]},{"body_a":"push_box","body_b":"link7","contact_count":660.0,"contact_point_centroid":[0.5484,-0.01099,0.04968],"force_p95":31.90055,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":35.35495,"mean_force":17.79479,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51474,0.01052,0.0199]},{"body_a":"world","body_b":"push_box","contact_count":2386.0,"contact_point_centroid":[0.52444,-0.03946,-9e-05],"force_p95":20.26869,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.96499,"mean_force":6.55136,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51417,0.00608,0.01985]},{"body_a":"attachment","body_b":"push_box","contact_count":658.0,"contact_point_centroid":[0.51595,-0.02247,0.02987],"force_p95":18.08786,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.59061,"mean_force":5.18507,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.51227,-0.01063,0.02006]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.50776,-0.11469,-0.00014],"force_p95":24.38773,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.77964,"mean_force":11.34761,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.50313,-0.07616,0.01778]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49721,-0.00059,0.20571]},{"body_a":"world","body_b":"push_box","contact_count":2640.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.5122,0.05537,0.06634]}],"total_contact_groups":7},"final_pose_error":0.07426,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50784,-0.11458,0.02473],"final_tcp_position":[0.50313,-0.07616,0.01777],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.4964,-0.00117,0.11424],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10505,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":660.0,"n_steps_budget":960.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.53001,0.10958,0.02429],"tcp_start":[0.4964,-0.00117,0.11424],"tcp_to_object_dist_end":0.07293,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50784,-0.11458,0.02473],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.03628,"object_to_goal_dist_start":0.1905,"object_z_max":0.02766,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.50313,-0.07616,0.01778],"tcp_start":[0.53001,0.10958,0.02429],"tcp_to_object_dist_end":0.03933,"terminated_normally":false,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.50784,-0.11458,0.02473],"object_pos_start":[0.50784,-0.11458,0.02473],"object_to_goal_dist_end":0.03627,"object_to_goal_dist_start":0.03628,"object_z_max":0.02473,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.50313,-0.07616,0.01777],"tcp_start":[0.50313,-0.07616,0.01778],"tcp_to_object_dist_end":0.03933,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.69466,"average_solve_count":131.0,"average_success_count":131.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"align_1.lateral_offset_x":0.00128,"align_1.lateral_offset_y":0.0007,"insert_1.insertion_depth":0.05629,"insert_1.insertion_force":10.26258,"push_1.push_distance":0.09133,"push_1.push_speed":0.06651},"optimized_scores":{"best_composite_score":0.47082,"best_fitness_score":0.49748,"best_task_score":0.93305},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":885.0,"contact_point_centroid":[0.51222,-0.06998,0.0467],"force_p95":42.42675,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":54.41245,"mean_force":17.25846,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49679,-0.05882,0.02174]},{"body_a":"world","body_b":"push_box","contact_count":2310.0,"contact_point_centroid":[0.50622,-0.09137,-7e-05],"force_p95":33.62489,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":46.89336,"mean_force":10.04478,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49634,-0.03917,0.02151]},{"body_a":"push_box","body_b":"link7","contact_count":747.0,"contact_point_centroid":[0.52322,-0.07659,0.05377],"force_p95":32.13999,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.64773,"mean_force":17.47358,"phase_index":2.0,"phase_name":"release_1","phase_type":"release","tcp_position_centroid":[0.49681,-0.0559,0.02172]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52095,-0.14661,0.0494],"force_p95":40.94442,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":40.94442,"mean_force":40.94442,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49394,-0.11973,0.01743]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.49694,-0.15834,-0.00011],"force_p95":21.11299,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":22.01321,"mean_force":10.51891,"phase_index":3.0,"phase_name":"insert_1","phase_type":"insert","tcp_position_centroid":[0.49394,-0.11973,0.01743]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49727,-0.03269,0.21388]},{"body_a":"world","body_b":"push_box","contact_count":2432.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"align_1","phase_type":"align","tcp_position_centroid":[0.49687,-0.00595,0.07734]}],"total_contact_groups":7},"final_pose_error":0.03179,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49701,-0.15826,0.02478],"final_tcp_position":[0.49394,-0.11973,0.01742],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","tcp_end":[0.49656,-0.06509,0.13207],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11693,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":608.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"phase_name":"align_1","phase_peak_obstacle_force":0.0,"phase_type":"align","tcp_end":[0.49987,0.05271,0.02683],"tcp_start":[0.49656,-0.06509,0.13207],"tcp_to_object_dist_end":0.0717,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49701,-0.15826,0.02478],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00879,"object_to_goal_dist_start":0.13127,"object_z_max":0.02897,"phase_name":"release_1","phase_peak_obstacle_force":0.0,"phase_type":"release","tcp_end":[0.49394,-0.11973,0.01743],"tcp_start":[0.49987,0.05271,0.02683],"tcp_to_object_dist_end":0.03935,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.49701,-0.15826,0.02478],"object_pos_start":[0.49701,-0.15826,0.02478],"object_to_goal_dist_end":0.00879,"object_to_goal_dist_start":0.00879,"object_z_max":0.02478,"phase_name":"insert_1","phase_peak_obstacle_force":0.0,"phase_type":"insert","tcp_end":[0.49394,-0.11973,0.01742],"tcp_start":[0.49394,-0.11973,0.01743],"tcp_to_object_dist_end":0.03935,"terminated_normally":true,"termination_reason":"force_exceeded"}],"success":true}]}
```