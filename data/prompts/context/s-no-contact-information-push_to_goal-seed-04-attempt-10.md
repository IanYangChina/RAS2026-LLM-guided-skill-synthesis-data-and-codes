## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 12 | -0.5048 | 0.15 | ❌ rejected |
| 9 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 13 | -0.6273 | 0.07 | ❌ rejected |
| 8 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4172 | 0.79 | ❌ rejected |
| 7 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4264 | 0.83 | ❌ rejected |
| 6 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4196 | 0.80 | ❌ rejected |

**Proposal policy**: task_score is 0.15 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.505) — your mutation base

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

- **Composite score**: -0.505
- **task_score** (E): 0.147
- **fitness_score**: 0.155  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Complexity Penalty**: 0.660

## Per-Phase Performance

| Phase | Normal Term. Rate | Mean Displacement (m) |
| ------- | ------------------- | ------------------------ |
| approach_1 | 1.00 | 0.1192 |
| descend_1 | 1.00 | 0.1481 |
| push_1 | 0.33 | 0.0594 |
| retract_1 | 1.00 | 0.1303 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end |
| --- | --- | --- | --- | --- | --- |
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.524, 0.013, 0.192) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 |
| descend_1 | descend | 1.00 / step_budget | (0.524, 0.013, 0.192)→(0.532, 0.035, 0.057) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 |
| push_1 | push | 0.33 / guard_failure | (0.532, 0.035, 0.057)→(0.521, -0.023, 0.051) | (0.531, 0.007, 0.025)→(0.522, -0.018, 0.026) | 0.161→0.136 |
| retract_1 | retract | 1.00 / step_budget | (0.521, -0.023, 0.051)→(0.519, -0.023, 0.181) | (0.522, -0.018, 0.026)→(0.523, -0.020, 0.025) | 0.136→0.134 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.376
- approach_alignment: 0.485
- goal_progress: 0.354
- terminal_score: 0.354
- phase_score: 0.285
- phase_breakdown.approach_sub_score: 0.132
- phase_breakdown.push_sub_score: 0.350

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.312
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.354
- **Median Q (composite search score)**: -0.570
- **K-run variance**: 0.0125
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 6.0
- **Final σ (mean)**: 0.266


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36471,"average_solve_count":170.0,"average_success_count":170.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08501,"approach_1.approach_x_offset":0.03884,"approach_1.approach_y_offset":0.03899,"descend_1.descent_speed":0.03284,"descend_1.descent_x_offset":-0.00897,"descend_1.descent_y_offset":0.00361,"push_1.guard_force_threshold":10.58682,"push_1.push_distance":0.16152,"push_1.push_speed":0.06388,"push_1.push_x_offset":-0.00921,"push_1.push_y_offset":0.0022,"retract_1.retract_speed":0.11515},"optimized_scores":{"best_composite_score":-0.57028,"best_fitness_score":0.08972,"best_task_score":0.06302},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1533.0,"contact_point_centroid":[0.55941,-0.01198,-4e-05],"force_p95":0.27324,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.7412,"mean_force":0.3034,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52858,-0.02376,0.12043]},{"body_a":"attachment","body_b":"push_box","contact_count":7.0,"contact_point_centroid":[0.54276,-0.02136,0.05052],"force_p95":26.62512,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":28.32286,"mean_force":9.20791,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53134,-0.02394,0.05299]},{"body_a":"world","body_b":"push_box","contact_count":1050.0,"contact_point_centroid":[0.55172,-0.00127,-1e-05],"force_p95":8.35574,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":11.43797,"mean_force":0.88665,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53677,-0.00531,0.0541]},{"body_a":"attachment","body_b":"push_box","contact_count":86.0,"contact_point_centroid":[0.54381,-0.01713,0.05026],"force_p95":9.33843,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":10.42715,"mean_force":7.22088,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53243,-0.01964,0.05275]},{"body_a":"world","body_b":"push_box","contact_count":1216.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53685,0.01674,0.24371]},{"body_a":"world","body_b":"push_box","contact_count":1624.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.55981,0.02178,0.12276]}],"total_contact_groups":6},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55982,-0.0121,0.02499],"final_tcp_position":[0.52886,-0.02373,0.18316],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"phases":[{"n_steps":304.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_sub","tcp_end":[0.57688,0.03454,0.18644],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.16652,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":406.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_sub","tcp_end":[0.5439,0.00809,0.05945],"tcp_start":[0.57688,0.03454,0.18644],"tcp_to_object_dist_end":0.03632,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":320.0,"n_steps_budget":1000.0,"object_pos_end":[0.55644,-0.00677,0.02697],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15396,"object_to_goal_dist_start":0.16043,"object_z_max":0.02698,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_sub","tcp_end":[0.53162,-0.02379,0.05287],"tcp_start":[0.5439,0.00809,0.05945],"tcp_to_object_dist_end":0.0397,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":404.0,"n_steps_budget":840.0,"object_pos_end":[0.55982,-0.0121,0.02499],"object_pos_start":[0.55644,-0.00677,0.02697],"object_to_goal_dist_end":0.15031,"object_to_goal_dist_start":0.15396,"object_z_max":0.02741,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.52886,-0.02373,0.18316],"tcp_start":[0.53162,-0.02379,0.05287],"tcp_to_object_dist_end":0.16159,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.18033,"average_solve_count":183.0,"average_success_count":183.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.05108,"approach_1.approach_x_offset":-0.02749,"approach_1.approach_y_offset":-0.01655,"descend_1.descent_speed":0.05204,"descend_1.descent_x_offset":0.02725,"descend_1.descent_y_offset":0.07388,"push_1.guard_force_threshold":16.80608,"push_1.push_distance":0.23052,"push_1.push_speed":0.06653,"push_1.push_x_offset":0.01052,"push_1.push_y_offset":0.00028,"retract_1.retract_speed":0.12762},"optimized_scores":{"best_composite_score":-0.34757,"best_fitness_score":0.31243,"best_task_score":0.35405},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":527.0,"contact_point_centroid":[0.53964,0.02665,0.04706],"force_p95":10.36816,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":14.42362,"mean_force":4.5845,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54252,0.03807,0.04636]},{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.52969,-0.01303,0.04793],"force_p95":10.20515,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":12.48313,"mean_force":3.09777,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53573,-0.0028,0.04651]},{"body_a":"world","body_b":"push_box","contact_count":2462.0,"contact_point_centroid":[0.52608,0.01365,-3e-05],"force_p95":6.24544,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.13529,"mean_force":1.29662,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54603,0.06004,0.04675]},{"body_a":"world","body_b":"push_box","contact_count":1552.0,"contact_point_centroid":[0.50408,-0.02743,-2e-05],"force_p95":0.2453,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":7.70799,"mean_force":0.26134,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53346,-0.00263,0.1124]},{"body_a":"world","body_b":"push_box","contact_count":896.0,"contact_point_centroid":[0.5366,0.03695,-0.0],"force_p95":0.24532,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50194,0.00774,0.24884]},{"body_a":"world","body_b":"push_box","contact_count":3020.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.52978,0.06086,0.12037]}],"total_contact_groups":6},"final_pose_error":0.01985,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50433,-0.02702,0.02499],"final_tcp_position":[0.53372,-0.00258,0.17651],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"phases":[{"n_steps":224.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_sub","tcp_end":[0.50508,0.01644,0.1938],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17295,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":755.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_sub","tcp_end":[0.55641,0.10462,0.05226],"tcp_start":[0.50508,0.01644,0.1938],"tcp_to_object_dist_end":0.0756,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50502,-0.02631,0.02498],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.12379,"object_to_goal_dist_start":0.1905,"object_z_max":0.02554,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_sub","tcp_end":[0.5365,-0.00253,0.04617],"tcp_start":[0.55641,0.10462,0.05226],"tcp_to_object_dist_end":0.04479,"terminated_normally":true,"termination_reason":"time_limit"},{"n_steps":400.0,"n_steps_budget":750.0,"object_pos_end":[0.50433,-0.02702,0.02499],"object_pos_start":[0.50502,-0.02631,0.02498],"object_to_goal_dist_end":0.12305,"object_to_goal_dist_start":0.12379,"object_z_max":0.02521,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.53372,-0.00258,0.17651],"tcp_start":[0.5365,-0.00253,0.04617],"tcp_to_object_dist_end":0.15627,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12195,"average_solve_count":164.0,"average_success_count":164.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.12315,"approach_1.approach_x_offset":-0.01473,"approach_1.approach_y_offset":0.00531,"descend_1.descent_speed":0.03009,"descend_1.descent_x_offset":-0.0027,"descend_1.descent_y_offset":0.01003,"push_1.guard_force_threshold":13.23709,"push_1.push_distance":0.16088,"push_1.push_speed":0.05517,"push_1.push_x_offset":0.0016,"push_1.push_y_offset":-0.00577,"retract_1.retract_speed":0.11222},"optimized_scores":{"best_composite_score":-0.59667,"best_fitness_score":0.06333,"best_task_score":0.0229},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.50677,-0.03862,0.05054],"force_p95":29.0239,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.99259,"mean_force":11.07453,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49579,-0.04273,0.05287]},{"body_a":"world","body_b":"push_box","contact_count":1477.0,"contact_point_centroid":[0.50537,-0.02199,-4e-05],"force_p95":0.32006,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.85292,"mean_force":0.31823,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49328,-0.04248,0.11995]},{"body_a":"attachment","body_b":"push_box","contact_count":58.0,"contact_point_centroid":[0.50717,-0.03783,0.05013],"force_p95":8.69001,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":13.72866,"mean_force":6.63834,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49574,-0.0401,0.0526]},{"body_a":"world","body_b":"push_box","contact_count":1394.0,"contact_point_centroid":[0.50458,-0.02086,-1e-05],"force_p95":2.76765,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":12.24438,"mean_force":0.54135,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49494,-0.02459,0.05385]},{"body_a":"world","body_b":"push_box","contact_count":812.0,"contact_point_centroid":[0.50458,-0.01881,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49481,-0.00516,0.24894]},{"body_a":"world","body_b":"push_box","contact_count":1980.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"descend_1","phase_type":"descend","tcp_position_centroid":[0.49221,-0.00996,0.12612]}],"total_contact_groups":6},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50572,-0.02186,0.02499],"final_tcp_position":[0.49348,-0.04245,0.1829],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"phases":[{"n_steps":203.0,"n_steps_budget":660.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","subtask_id":"approach_sub","tcp_end":[0.48975,-0.01088,0.19453],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17037,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":495.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"phase_name":"descend_1","phase_peak_obstacle_force":0.0,"phase_type":"descend","subtask_id":"approach_sub","tcp_end":[0.4971,-0.00898,0.05869],"tcp_start":[0.48975,-0.01088,0.19453],"tcp_to_object_dist_end":0.03589,"terminated_normally":true,"termination_reason":"step_budget"},{"n_steps":377.0,"n_steps_budget":1000.0,"object_pos_end":[0.50485,-0.02117,0.02688],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12894,"object_to_goal_dist_start":0.13127,"object_z_max":0.02686,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","subtask_id":"push_sub","tcp_end":[0.49608,-0.04262,0.05263],"tcp_start":[0.4971,-0.00898,0.05869],"tcp_to_object_dist_end":0.03464,"terminated_normally":false,"termination_reason":"guard_failure"},{"n_steps":387.0,"n_steps_budget":840.0,"object_pos_end":[0.50572,-0.02186,0.02499],"object_pos_start":[0.50485,-0.02117,0.02688],"object_to_goal_dist_end":0.12827,"object_to_goal_dist_start":0.12894,"object_z_max":0.02712,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","tcp_end":[0.49348,-0.04245,0.1829],"tcp_start":[0.49608,-0.04262,0.05263],"tcp_to_object_dist_end":0.15971,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```