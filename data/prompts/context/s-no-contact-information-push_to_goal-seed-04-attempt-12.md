## Search State

- **Seed**: 4
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 14 | -0.2265 | 0.66 | ❌ rejected |
| 11 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 13 | -0.6239 | 0.03 | ❌ rejected |
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5048 | 0.15 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.6273 | 0.07 | ❌ rejected |
| 8 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4172 | 0.79 | ❌ rejected |

**Proposal policy**: task_score is 0.66 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.227) — your mutation base

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

- **Composite score**: -0.227
- **task_score** (E): 0.664
- **fitness_score**: 0.533  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.760

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1969 |
| descend_1 | 1.00 | 0.1090 |
| push_1 | 1.00 | 0.1727 |
| retract_1 | 1.00 | 0.1462 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.521, 0.093, 0.139) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 |
| descend_1 | descend | 1.00 / step_budget | (0.521, 0.093, 0.139)→(0.562, 0.098, 0.056) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 |
| push_1 | push | 1.00 / step_budget | (0.562, 0.098, 0.056)→(0.509, -0.063, 0.050) | (0.531, 0.007, 0.025)→(0.498, -0.088, 0.030) | 0.161→0.062 |
| retract_1 | retract | 1.00 / step_budget | (0.509, -0.063, 0.050)→(0.507, -0.063, 0.196) | (0.498, -0.088, 0.030)→(0.493, -0.100, 0.025) | 0.062→0.052 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.802
- approach_alignment: 0.694
- goal_progress: 0.742
- terminal_score: 0.742
- phase_score: 0.525
- phase_breakdown.push_to_goal_score: 0.709

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.612
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.746
- **Median Q (composite search score)**: -0.174
- **K-run variance**: 0.0086
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Parameters at upper bound**: approach_1.approach_distance
- **Final σ (mean)**: 0.359


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.455,"average_solve_count":200.0,"average_success_count":200.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_distance":0.15,"approach_1.approach_offset_x":-0.03109,"approach_1.approach_offset_y":0.01581,"approach_1.approach_speed":0.0868,"descend_1.descent_distance":0.08813,"descend_1.descent_offset_x":0.03043,"descend_1.descent_offset_y":-0.0266,"descend_1.descent_speed":0.06443,"push_1.push_distance":0.05856,"push_1.push_offset_x":-0.01598,"push_1.push_offset_y":0.0027,"push_1.push_speed":0.05109,"retract_1.retract_speed":0.10971,"retract_1.retract_z":0.12556},"optimized_scores":{"best_composite_score":-0.14845,"best_fitness_score":0.61155,"best_task_score":0.7421},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":157.0,"contact_point_centroid":[0.54209,-0.02794,0.04696],"force_p95":28.80437,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.42248,"mean_force":7.91993,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54443,-0.01638,0.04636]},{"body_a":"world","body_b":"push_box","contact_count":796.0,"contact_point_centroid":[0.54041,-0.02426,-4e-05],"force_p95":13.31808,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.14687,"mean_force":1.96123,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5725,0.02927,0.04814]},{"body_a":"world","body_b":"push_box","contact_count":1238.0,"contact_point_centroid":[0.4891,-0.10991,-4e-05],"force_p95":0.24739,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.79843,"mean_force":0.25903,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50842,-0.07115,0.10014]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.5081,-0.08291,0.04628],"force_p95":0.47273,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.47423,"mean_force":0.31115,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51138,-0.07157,0.04548]},{"body_a":"world","body_b":"push_box","contact_count":1928.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52933,0.06856,0.21738]},{"body_a":"world","body_b":"push_box","contact_count":1264.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.58189,0.11064,0.09321]}],"total_contact_groups":6},"final_pose_error":0.01972,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48904,-0.1101,0.02499],"final_tcp_position":[0.50852,-0.07099,0.15155],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"phases":[{"n_steps":482.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.56107,0.13964,0.13479],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17675,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":316.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_pre_contact","tcp_end":[0.60619,0.08042,0.05431],"tcp_start":[0.56107,0.13964,0.13479],"tcp_to_object_dist_end":0.0996,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":422.0,"n_steps_budget":1000.0,"object_pos_end":[0.4939,-0.10378,0.02605],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.04663,"object_to_goal_dist_start":0.16043,"object_z_max":0.02636,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.51144,-0.07131,0.04549],"tcp_start":[0.60619,0.08042,0.05431],"tcp_to_object_dist_end":0.04171,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":325.0,"n_steps_budget":720.0,"object_pos_end":[0.48904,-0.1101,0.02499],"object_pos_start":[0.4939,-0.10378,0.02605],"object_to_goal_dist_end":0.04137,"object_to_goal_dist_start":0.04663,"object_z_max":0.02624,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.50852,-0.07099,0.15155],"tcp_start":[0.51144,-0.07131,0.04549],"tcp_to_object_dist_end":0.13389,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.56279,"average_solve_count":215.0,"average_success_count":215.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_distance":0.10103,"approach_1.approach_offset_x":-0.04004,"approach_1.approach_offset_y":0.00585,"approach_1.approach_speed":0.06703,"descend_1.descent_distance":0.09821,"descend_1.descent_offset_x":0.03126,"descend_1.descent_offset_y":0.00752,"descend_1.descent_speed":0.04836,"push_1.push_distance":0.06866,"push_1.push_offset_x":-0.00208,"push_1.push_offset_y":0.00591,"push_1.push_speed":0.07521,"retract_1.retract_speed":0.10584,"retract_1.retract_z":0.19857},"optimized_scores":{"best_composite_score":-0.17431,"best_fitness_score":0.58569,"best_task_score":0.7465},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":229.0,"contact_point_centroid":[0.52622,-0.01979,0.0487],"force_p95":90.33079,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":93.43061,"mean_force":37.25139,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52862,-0.00836,0.04797]},{"body_a":"world","body_b":"push_box","contact_count":942.0,"contact_point_centroid":[0.52306,-0.00303,-9e-05],"force_p95":65.71859,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":89.83605,"mean_force":9.49605,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54621,0.05222,0.04956]},{"body_a":"world","body_b":"push_box","contact_count":2012.0,"contact_point_centroid":[0.48224,-0.10456,-7e-05],"force_p95":0.44431,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":85.07469,"mean_force":0.32493,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51305,-0.0627,0.14667]},{"body_a":"attachment","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.51319,-0.07484,0.05186],"force_p95":51.60051,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":83.63949,"mean_force":10.46202,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51544,-0.0634,0.05092]},{"body_a":"world","body_b":"push_box","contact_count":1776.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50516,0.06307,0.21879]},{"body_a":"world","body_b":"push_box","contact_count":1244.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.53961,0.1279,0.09535]}],"total_contact_groups":6},"final_pose_error":0.01978,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48191,-0.10522,0.02499],"final_tcp_position":[0.51358,-0.0627,0.22942],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"phases":[{"n_steps":444.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.51198,0.12898,0.13712],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14714,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":311.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_pre_contact","tcp_end":[0.57049,0.12702,0.05567],"tcp_start":[0.51198,0.12898,0.13712],"tcp_to_object_dist_end":0.101,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":489.0,"n_steps_budget":1000.0,"object_pos_end":[0.49268,-0.08317,0.03457],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.0679,"object_to_goal_dist_start":0.1905,"object_z_max":0.03462,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.51592,-0.06292,0.05049],"tcp_start":[0.57049,0.12702,0.05567],"tcp_to_object_dist_end":0.03469,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":552.0,"n_steps_budget":1000.0,"object_pos_end":[0.48191,-0.10522,0.02499],"object_pos_start":[0.49268,-0.08317,0.03457],"object_to_goal_dist_end":0.04829,"object_to_goal_dist_start":0.0679,"object_z_max":0.03457,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.51358,-0.0627,0.22942],"tcp_start":[0.51592,-0.06292,0.05049],"tcp_to_object_dist_end":0.2112,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.42487,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_distance":0.03043,"approach_1.approach_offset_x":-0.01344,"approach_1.approach_offset_y":0.00158,"approach_1.approach_speed":0.07427,"descend_1.descent_distance":0.11654,"descend_1.descent_offset_x":0.00671,"descend_1.descent_offset_y":0.01619,"descend_1.descent_speed":0.04122,"push_1.push_distance":0.0754,"push_1.push_offset_x":-0.00549,"push_1.push_offset_y":0.01708,"push_1.push_speed":0.05921,"retract_1.retract_speed":0.16375,"retract_1.retract_z":0.17331},"optimized_scores":{"best_composite_score":-0.35677,"best_fitness_score":0.40323,"best_task_score":0.50327},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":215.0,"contact_point_centroid":[0.50239,-0.03032,0.0508],"force_p95":103.17762,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":105.53455,"mean_force":75.65448,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5001,-0.01909,0.05094]},{"body_a":"world","body_b":"push_box","contact_count":1133.0,"contact_point_centroid":[0.5053,-0.03338,-0.00011],"force_p95":53.23713,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":56.57309,"mean_force":14.66844,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50188,0.02567,0.05142]},{"body_a":"world","body_b":"push_box","contact_count":1585.0,"contact_point_centroid":[0.50917,-0.08515,-6e-05],"force_p95":0.29661,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":48.24974,"mean_force":0.37187,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49821,-0.05497,0.13315]},{"body_a":"attachment","body_b":"push_box","contact_count":9.0,"contact_point_centroid":[0.50777,-0.06499,0.05217],"force_p95":46.25477,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.94923,"mean_force":18.17283,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50046,-0.05577,0.05318]},{"body_a":"world","body_b":"push_box","contact_count":1224.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49509,0.00495,0.22407]},{"body_a":"world","body_b":"push_box","contact_count":1396.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49812,0.0473,0.09976]}],"total_contact_groups":6},"final_pose_error":0.01993,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50932,-0.08546,0.02499],"final_tcp_position":[0.49851,-0.05488,0.20619],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":306.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"reach_pre_contact","tcp_end":[0.49065,0.01031,0.14455],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12384,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":349.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"reach_pre_contact","tcp_end":[0.50822,0.08599,0.05681],"tcp_start":[0.49065,0.01031,0.14455],"tcp_to_object_dist_end":0.10959,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":399.0,"n_steps_budget":1000.0,"object_pos_end":[0.50731,-0.07783,0.0308],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.07277,"object_to_goal_dist_start":0.13127,"object_z_max":0.03449,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_to_goal","tcp_end":[0.50085,-0.05509,0.05267],"tcp_start":[0.50822,0.08599,0.05681],"tcp_to_object_dist_end":0.03221,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":422.0,"n_steps_budget":690.0,"object_pos_end":[0.50932,-0.08546,0.02499],"object_pos_start":[0.50731,-0.07783,0.0308],"object_to_goal_dist_end":0.06521,"object_to_goal_dist_start":0.07277,"object_z_max":0.0308,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49851,-0.05488,0.20619],"tcp_start":[0.50085,-0.05509,0.05267],"tcp_to_object_dist_end":0.18408,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```