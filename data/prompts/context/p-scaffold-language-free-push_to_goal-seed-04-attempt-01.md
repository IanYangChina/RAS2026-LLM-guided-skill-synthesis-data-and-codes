## Search State

- **Seed**: 4
- **Iteration**: 2 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0692 | 0.02 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3434 | 0.75 | ✅ accepted |

**Proposal policy**: task_score is 0.02 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.069) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: impedance_control
  termination: contact_detected
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: -0.069
- **task_score** (E): 0.025
- **fitness_score**: 0.091  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1475 |
| contact_1 | 1.00 | 1.00 | 0.1050 |
| push_1 | 0.00 | 1.00 | 0.0001 |
| retract_1 | 0.00 | 1.00 | 0.2585 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.523, 0.005, 0.157) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.523, 0.005, 0.157)→(0.525, 0.006, 0.052) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 5.000 | 25330.009 | 0.245 |
| push_1 | push | 0.00 / guard_failure | (0.525, 0.006, 0.052)→(0.525, 0.006, 0.052) | (0.531, 0.007, 0.025)→(0.531, 0.006, 0.025) | 0.161→0.161 | 1.00 / 3.000 | 18.864 | 42.416 |
| retract_1 | retract | 0.00 / step_budget | (0.525, 0.006, 0.052)→(0.268, 0.003, 0.074) | (0.531, 0.006, 0.025)→(0.494, 0.006, 0.025) | 0.161→0.157 | 1.00 / 4.000 | 0.245 | 73.124 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.338
- lateral_force_integral: None
- approach_alignment: 0.613
- goal_progress: 0.057
- terminal_score: 0.057
- phase_score: 0.132
- phase_breakdown.push_goal_score: 0.041
- phase_breakdown.approach_target_score: 0.346

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.102
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.057
- **Median Q (composite search score)**: -0.069
- **K-run variance**: 0.0001
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.350


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.83588,"average_solve_count":262.0,"average_success_count":262.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11762,"approach_1.speed":0.07498,"contact_1.contact_force_threshold":14.13718,"contact_1.speed":0.0203,"push_1.push_distance":0.09759,"push_1.push_speed":0.0688,"retract_1.speed":0.05601},"optimized_scores":{"best_composite_score":-0.05796,"best_fitness_score":0.10204,"best_task_score":0.0566},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":222.0,"contact_point_centroid":[0.53564,0.00109,0.05215],"force_p95":58.91747,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":78.36578,"mean_force":46.69841,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.52401,0.00107,0.05423]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.55749,0.0012,0.04995],"force_p95":43.66109,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":46.19486,"mean_force":28.83942,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54576,0.00118,0.05241]},{"body_a":"world","body_b":"push_box","contact_count":3258.0,"contact_point_centroid":[0.50404,0.00133,-8e-05],"force_p95":27.91121,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.18947,"mean_force":3.48188,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.40149,0.00082,0.06218]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.54066,0.00136,-1e-05],"force_p95":24.07168,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.4,"mean_force":11.10033,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54577,0.00118,0.05244]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51914,0.00051,0.23107]},{"body_a":"world","body_b":"push_box","contact_count":2968.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54116,0.00107,0.10805]}],"total_contact_groups":6},"final_pose_error":0.28714,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49894,0.00134,0.02499],"final_tcp_position":[0.28588,0.00059,0.07312],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":78.36578,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_target","tcp_end":[0.53914,0.00102,0.16932],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.14501,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":742.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":47.01859,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2968.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_target","tcp_end":[0.5458,0.00118,0.05251],"tcp_start":[0.53914,0.00102,0.16932],"tcp_to_object_dist_end":0.02849,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.55312,0.00136,0.02502],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16041,"object_to_goal_dist_start":0.16043,"object_z_max":0.02504,"peak_contact_force":20.85715,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":46.19486,"subtask_id":"push_goal","tcp_end":[0.54567,0.00117,0.05223],"tcp_start":[0.54571,0.00117,0.05231],"tcp_to_object_dist_end":0.02821,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49894,0.00134,0.02499],"object_pos_start":[0.55302,0.00135,0.02506],"object_to_goal_dist_end":0.15134,"object_to_goal_dist_start":0.16037,"object_z_max":0.03535,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3480.0,"raw_peak_contact_force":78.36578,"tcp_end":[0.28588,0.00059,0.07312],"tcp_start":[0.54567,0.00117,0.05223],"tcp_to_object_dist_end":0.21842,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.80669,"average_solve_count":269.0,"average_success_count":269.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11246,"approach_1.speed":0.05484,"contact_1.contact_force_threshold":6.60184,"contact_1.speed":0.07737,"push_1.push_distance":0.06284,"push_1.push_speed":0.05619,"retract_1.speed":0.06278},"optimized_scores":{"best_composite_score":-0.08103,"best_fitness_score":0.07897,"best_task_score":0.01758},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":229.0,"contact_point_centroid":[0.51949,0.03386,0.05217],"force_p95":57.4132,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":74.22647,"mean_force":45.28553,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50784,0.03383,0.05427]},{"body_a":"world","body_b":"push_box","contact_count":3153.0,"contact_point_centroid":[0.48803,0.03626,-8e-05],"force_p95":28.84227,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":45.05968,"mean_force":3.59924,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.3853,0.02558,0.06282]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.54203,0.03526,0.04994],"force_p95":40.13348,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":42.51544,"mean_force":25.69448,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5303,0.03515,0.05238]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.52409,0.03695,-1e-05],"force_p95":22.73431,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.29438,"mean_force":9.9149,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53031,0.03515,0.05241]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5131,0.01576,0.2257]},{"body_a":"world","body_b":"push_box","contact_count":2656.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52769,0.03301,0.10273]}],"total_contact_groups":6},"final_pose_error":0.27399,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48185,0.03627,0.02499],"final_tcp_position":[0.27213,0.01809,0.07377],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_target","tcp_end":[0.52776,0.03106,0.15719],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.13263,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":664.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2656.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_target","tcp_end":[0.53035,0.03515,0.05248],"tcp_start":[0.52776,0.03106,0.15719],"tcp_to_object_dist_end":0.02825,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53656,0.03695,0.02501],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19049,"object_to_goal_dist_start":0.1905,"object_z_max":0.02503,"peak_contact_force":18.69588,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":42.51544,"subtask_id":"push_goal","tcp_end":[0.5302,0.03515,0.0522],"tcp_start":[0.53025,0.03515,0.05228],"tcp_to_object_dist_end":0.02798,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.48185,0.03627,0.02499],"object_pos_start":[0.53647,0.03694,0.02505],"object_to_goal_dist_end":0.18715,"object_to_goal_dist_start":0.19046,"object_z_max":0.03534,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3382.0,"raw_peak_contact_force":74.22647,"tcp_end":[0.27213,0.01809,0.07377],"tcp_start":[0.5302,0.03515,0.0522],"tcp_to_object_dist_end":0.21608,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.69611,"average_solve_count":283.0,"average_success_count":283.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11745,"approach_1.speed":0.0865,"contact_1.contact_force_threshold":7.10021,"contact_1.speed":0.05813,"push_1.push_distance":0.08699,"push_1.push_speed":0.05385,"retract_1.speed":0.06236},"optimized_scores":{"best_composite_score":-0.06867,"best_fitness_score":0.09133,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":236.0,"contact_point_centroid":[0.48874,-0.01782,0.05235],"force_p95":55.84745,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.78083,"mean_force":44.03074,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.47709,-0.01781,0.05445]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.51148,-0.01853,0.04995],"force_p95":36.38881,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":38.53877,"mean_force":23.72132,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49974,-0.01849,0.05239]},{"body_a":"world","body_b":"push_box","contact_count":3132.0,"contact_point_centroid":[0.49451,-0.01823,-8e-05],"force_p95":26.24747,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":33.88779,"mean_force":3.62888,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.35675,-0.01329,0.06379]},{"body_a":"world","body_b":"push_box","contact_count":8.0,"contact_point_centroid":[0.49207,-0.01881,-1e-05],"force_p95":19.90015,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.48733,"mean_force":9.17593,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49976,-0.01849,0.05241]},{"body_a":"world","body_b":"push_box","contact_count":3576.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49956,-0.00883,0.22168]},{"body_a":"world","body_b":"push_box","contact_count":2392.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49912,-0.01812,0.09775]}],"total_contact_groups":6},"final_pose_error":0.24688,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50063,-0.01815,0.02499],"final_tcp_position":[0.24545,-0.00915,0.07508],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":66.78083,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":894.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3576.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_target","tcp_end":[0.50113,-0.01779,0.14577],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12084,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":598.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":49.47047,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2392.0,"raw_peak_contact_force":0.24525,"subtask_id":"approach_target","tcp_end":[0.49979,-0.01849,0.05249],"tcp_start":[0.50113,-0.01779,0.14577],"tcp_to_object_dist_end":0.02792,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.50453,-0.01881,0.02502],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02504,"peak_contact_force":17.03921,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":11.0,"raw_peak_contact_force":38.53877,"subtask_id":"push_goal","tcp_end":[0.49963,-0.01849,0.0522],"tcp_start":[0.49969,-0.01849,0.05229],"tcp_to_object_dist_end":0.02763,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50063,-0.01815,0.02499],"object_pos_start":[0.50444,-0.01881,0.02506],"object_to_goal_dist_end":0.13185,"object_to_goal_dist_start":0.13126,"object_z_max":0.03528,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3368.0,"raw_peak_contact_force":66.78083,"tcp_end":[0.24545,-0.00915,0.07508],"tcp_start":[0.49963,-0.01849,0.0522],"tcp_to_object_dist_end":0.26021,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```