## Search State

- **Seed**: 4
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.2139 | 0.36 | ❌ rejected |
| 9 | approach → push | linear_cartesian | impedance_motion | position_control | impedance_control | pose_tolerance | time_limit | 4 | 0.2069 | 0.00 | ❌ rejected |
| 8 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4172 | 0.79 | ❌ rejected |
| 7 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 8 | -0.1299 | 0.30 | ❌ rejected |
| 6 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4196 | 0.80 | ❌ rejected |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.214) — your mutation base

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

- **Composite score**: 0.214
- **task_score** (E): 0.359
- **fitness_score**: 0.414  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2605 |
| push_1 | 1.00 | 1.00 | 0.1846 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.545, 0.006, 0.046) | (0.531, 0.007, 0.025)→(0.536, 0.007, 0.026) | 0.161→0.162 | 1.00 / 3.000 | 224.899 | 261.263 |
| push_1 | push | 1.00 / time_limit | (0.545, 0.006, 0.046)→(0.495, -0.170, 0.029) | (0.536, 0.007, 0.026)→(0.536, -0.052, 0.025) | 0.162→0.105 | 1.00 / 4.000 | 0.245 | 136.205 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.586
- lateral_force_integral: None
- approach_alignment: 0.797
- goal_progress: 0.459
- terminal_score: 0.459
- phase_score: 0.518
- phase_breakdown.push_to_goal_score: 0.459
- phase_breakdown.approach_object_score: 0.656

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.494
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.459
- **Median Q (composite search score)**: 0.198
- **K-run variance**: 0.0036
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.652


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.62121,"average_solve_count":66.0,"average_success_count":66.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.18909,"approach_1.approach_tolerance":0.03875,"push_1.push_distance":0.20592,"push_1.push_speed":0.14911},"optimized_scores":{"best_composite_score":0.19797,"best_fitness_score":0.39797,"best_task_score":0.33802},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":30.0,"contact_point_centroid":[0.5687,0.00119,0.04745],"force_p95":264.77216,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":264.98763,"mean_force":246.29666,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.55683,0.00112,0.04798]},{"body_a":"attachment","body_b":"push_box","contact_count":358.0,"contact_point_centroid":[0.56126,-0.02358,0.04796],"force_p95":130.58398,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":134.6329,"mean_force":96.99413,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55326,-0.0303,0.04802]},{"body_a":"world","body_b":"push_box","contact_count":1906.0,"contact_point_centroid":[0.55395,0.00136,-3e-05],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":133.54552,"mean_force":4.129,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52617,0.00056,0.17295]},{"body_a":"world","body_b":"push_box","contact_count":3159.0,"contact_point_centroid":[0.54604,-0.04425,-0.00013],"force_p95":71.74993,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.72921,"mean_force":11.31416,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51228,-0.11998,0.03575]}],"total_contact_groups":4},"final_pose_error":0.13277,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54226,-0.05257,0.02499],"final_tcp_position":[0.47202,-0.21768,0.0276],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":264.98763,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":491.0,"n_steps_budget":930.0,"object_pos_end":[0.55699,0.00136,0.0248],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16173,"object_to_goal_dist_start":0.16043,"object_z_max":0.02512,"peak_contact_force":249.41511,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1936.0,"raw_peak_contact_force":264.98763,"subtask_id":"approach_object","tcp_end":[0.56193,0.00114,0.04584],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54226,-0.05257,0.02499],"object_pos_start":[0.55699,0.00136,0.0248],"object_to_goal_dist_end":0.1062,"object_to_goal_dist_start":0.16173,"object_z_max":0.03537,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3517.0,"raw_peak_contact_force":134.6329,"subtask_id":"push_to_goal","tcp_end":[0.47202,-0.21768,0.0276],"tcp_start":[0.56193,0.00114,0.04584],"tcp_to_object_dist_end":0.17945,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93162,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07153,"approach_1.approach_tolerance":0.02488,"push_1.push_distance":0.24917,"push_1.push_speed":0.06371},"optimized_scores":{"best_composite_score":0.14943,"best_fitness_score":0.34943,"best_task_score":0.28014},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":48.0,"contact_point_centroid":[0.5558,0.03365,0.04714],"force_p95":258.8801,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":259.80807,"mean_force":222.14176,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.54387,0.03335,0.0476]},{"body_a":"world","body_b":"push_box","contact_count":2130.0,"contact_point_centroid":[0.5376,0.03697,-4e-05],"force_p95":4.00319,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":134.64775,"mean_force":5.26606,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51902,0.01667,0.17085]},{"body_a":"attachment","body_b":"push_box","contact_count":611.0,"contact_point_centroid":[0.55322,0.00707,0.04657],"force_p95":111.58583,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":131.34971,"mean_force":84.10353,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5455,-0.00067,0.04662]},{"body_a":"world","body_b":"push_box","contact_count":2555.0,"contact_point_centroid":[0.5363,0.00043,-0.00023],"force_p95":91.80298,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":99.62969,"mean_force":20.5161,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53355,-0.03469,0.04079]}],"total_contact_groups":4},"final_pose_error":0.31432,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52887,-0.01594,0.02499],"final_tcp_position":[0.51709,-0.08727,0.03416],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":259.80807,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":553.0,"n_steps_budget":1000.0,"object_pos_end":[0.54207,0.03746,0.02634],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.19213,"object_to_goal_dist_start":0.1905,"object_z_max":0.02623,"peak_contact_force":217.15339,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2178.0,"raw_peak_contact_force":259.80807,"subtask_id":"approach_object","tcp_end":[0.55148,0.03431,0.04575],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0218,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52887,-0.01594,0.02499],"object_pos_start":[0.54207,0.03746,0.02634],"object_to_goal_dist_end":0.13713,"object_to_goal_dist_start":0.19213,"object_z_max":0.03544,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3166.0,"raw_peak_contact_force":131.34971,"subtask_id":"push_to_goal","tcp_end":[0.51709,-0.08727,0.03416],"tcp_start":[0.55148,0.03431,0.04575],"tcp_to_object_dist_end":0.07287,"terminated_normally":true,"termination_reason":"time_limit"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.93939,"average_solve_count":99.0,"average_success_count":99.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.08842,"approach_1.approach_tolerance":0.02366,"push_1.push_distance":0.13242,"push_1.push_speed":0.11997},"optimized_scores":{"best_composite_score":0.29443,"best_fitness_score":0.49443,"best_task_score":0.45893},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":39.0,"contact_point_centroid":[0.52594,-0.01715,0.047],"force_p95":258.74588,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":258.99451,"mean_force":225.48746,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51402,-0.01709,0.04737]},{"body_a":"attachment","body_b":"push_box","contact_count":429.0,"contact_point_centroid":[0.52901,-0.04143,0.04647],"force_p95":136.99243,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.63142,"mean_force":109.77235,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52137,-0.0498,0.04647]},{"body_a":"world","body_b":"push_box","contact_count":2174.0,"contact_point_centroid":[0.53331,-0.06961,-0.00027],"force_p95":128.65883,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":140.86934,"mean_force":22.17228,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50647,-0.12822,0.03364]},{"body_a":"world","body_b":"push_box","contact_count":2040.0,"contact_point_centroid":[0.50533,-0.01881,-3e-05],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.64168,"mean_force":4.56871,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50451,-0.00853,0.17119]},{"body_a":"push_box","body_b":"link7","contact_count":62.0,"contact_point_centroid":[0.53213,-0.07739,0.07995],"force_p95":1.72591,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.85681,"mean_force":0.51799,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50541,-0.11819,0.03225]}],"total_contact_groups":5},"final_pose_error":0.07801,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53626,-0.08892,0.02499],"final_tcp_position":[0.49533,-0.20421,0.0245],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":258.99451,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":525.0,"n_steps_budget":1000.0,"object_pos_end":[0.50933,-0.01907,0.02637],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02622,"peak_contact_force":208.12987,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2079.0,"raw_peak_contact_force":258.99451,"subtask_id":"approach_object","tcp_end":[0.52055,-0.01753,0.04516],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.02195,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53626,-0.08892,0.02499],"object_pos_start":[0.50933,-0.01907,0.02637],"object_to_goal_dist_end":0.07103,"object_to_goal_dist_start":0.13127,"object_z_max":0.04327,"peak_contact_force":0.24525,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2665.0,"raw_peak_contact_force":142.63142,"subtask_id":"push_to_goal","tcp_end":[0.49533,-0.20421,0.0245],"tcp_start":[0.52055,-0.01753,0.04516],"tcp_to_object_dist_end":0.12234,"terminated_normally":true,"termination_reason":"time_limit"}],"success":true}]}
```