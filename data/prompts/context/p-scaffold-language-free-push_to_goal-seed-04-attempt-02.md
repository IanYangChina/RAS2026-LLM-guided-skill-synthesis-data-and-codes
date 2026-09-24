## Search State

- **Seed**: 4
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | pose_tolerance | pose_tolerance | pose_tolerance | 9 | 0.0329 | 0.50 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0692 | 0.02 | ❌ rejected |
| 0 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | 0.3434 | 0.75 | ✅ accepted |

**Proposal policy**: task_score is 0.50 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.033) — your mutation base

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

- **Composite score**: 0.033
- **task_score** (E): 0.502
- **fitness_score**: 0.513  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2603 |
| push_1 | 1.00 | 1.00 | 0.1961 |
| retract_1 | 1.00 | 1.00 | 0.0991 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.555, 0.068, 0.057) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 4.000 | 0.245 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.555, 0.068, 0.057)→(0.505, -0.121, 0.047) | (0.531, 0.007, 0.025)→(0.508, -0.071, 0.025) | 0.161→0.081 | 1.00 / 3.333 | 0.880 | 118.624 |
| retract_1 | retract | 1.00 / step_budget | (0.505, -0.121, 0.047)→(0.503, -0.121, 0.146) | (0.508, -0.071, 0.025)→(0.507, -0.071, 0.025) | 0.081→0.081 | 1.00 / 4.000 | 0.245 | 4.198 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.606
- lateral_force_integral: None
- approach_alignment: 0.870
- goal_progress: 0.598
- terminal_score: 0.598
- phase_score: 0.605
- phase_breakdown.push_goal_score: 0.593
- phase_breakdown.approach_target_score: 0.634

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.602
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.598
- **Median Q (composite search score)**: 0.015
- **K-run variance**: 0.0045
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.80311,"average_solve_count":193.0,"average_success_count":193.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07358,"approach_1.approach_tolerance":0.01029,"approach_1.approach_x_offset":0.03631,"approach_1.approach_y_offset":0.06211,"push_1.push_speed":0.07275,"push_1.push_tolerance":0.02841,"retract_1.retract_height":0.17304,"retract_1.retract_speed":0.06599,"retract_1.retract_tolerance":0.01318},"optimized_scores":{"best_composite_score":0.12219,"best_fitness_score":0.60219,"best_task_score":0.59769},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":316.0,"contact_point_centroid":[0.55575,-0.0307,0.05059],"force_p95":121.63817,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.15494,"mean_force":81.98935,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54622,-0.03146,0.05329]},{"body_a":"world","body_b":"push_box","contact_count":911.0,"contact_point_centroid":[0.54127,-0.03283,-0.00026],"force_p95":107.83105,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":117.02244,"mean_force":28.88638,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.55207,-0.01445,0.05276]},{"body_a":"attachment","body_b":"push_box","contact_count":20.0,"contact_point_centroid":[0.51339,-0.11391,0.05025],"force_p95":9.67834,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":11.6136,"mean_force":2.09907,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50728,-0.12456,0.04892]},{"body_a":"world","body_b":"push_box","contact_count":3804.0,"contact_point_centroid":[0.51141,-0.08626,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":10.93613,"mean_force":0.25547,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50543,-0.12295,0.12807]},{"body_a":"world","body_b":"push_box","contact_count":3720.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.53957,0.02992,0.17633]}],"total_contact_groups":5},"final_pose_error":0.01305,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51136,-0.08647,0.02499],"final_tcp_position":[0.50601,-0.12293,0.20794],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":124.15494,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":930.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3720.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_target","tcp_end":[0.58123,0.0601,0.055],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07169,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":401.0,"n_steps_budget":1000.0,"object_pos_end":[0.51327,-0.08604,0.02586],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.06533,"object_to_goal_dist_start":0.16043,"object_z_max":0.0349,"peak_contact_force":1.57031,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1227.0,"raw_peak_contact_force":124.15494,"subtask_id":"push_goal","tcp_end":[0.50866,-0.12348,0.04766],"tcp_start":[0.58123,0.0601,0.055],"tcp_to_object_dist_end":0.04357,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":964.0,"n_steps_budget":1000.0,"object_pos_end":[0.51136,-0.08647,0.02499],"object_pos_start":[0.51327,-0.08604,0.02586],"object_to_goal_dist_end":0.06454,"object_to_goal_dist_start":0.06533,"object_z_max":0.02586,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3824.0,"raw_peak_contact_force":11.6136,"tcp_end":[0.50601,-0.12293,0.20794],"tcp_start":[0.50866,-0.12348,0.04766],"tcp_to_object_dist_end":0.18663,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.11952,"average_solve_count":251.0,"average_success_count":251.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.07712,"approach_1.approach_tolerance":0.01102,"approach_1.approach_x_offset":0.02058,"approach_1.approach_y_offset":0.05834,"push_1.push_speed":0.05699,"push_1.push_tolerance":0.03648,"retract_1.retract_height":0.12514,"retract_1.retract_speed":0.02835,"retract_1.retract_tolerance":0.03053},"optimized_scores":{"best_composite_score":-0.03849,"best_fitness_score":0.44151,"best_task_score":0.41828},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":199.0,"contact_point_centroid":[0.54464,0.01486,0.05177],"force_p95":134.84027,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":137.28385,"mean_force":88.7589,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53509,0.01205,0.05491]},{"body_a":"world","body_b":"push_box","contact_count":776.0,"contact_point_centroid":[0.52972,-0.00441,-0.00033],"force_p95":96.79521,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":103.52611,"mean_force":23.15851,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.53157,0.00086,0.05313]},{"body_a":"world","body_b":"push_box","contact_count":3440.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5241,0.04461,0.17751]},{"body_a":"world","body_b":"push_box","contact_count":820.0,"contact_point_centroid":[0.52283,-0.04156,-2e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.2444,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50243,-0.11461,0.0897]}],"total_contact_groups":4},"final_pose_error":0.03029,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52283,-0.04156,0.02499],"final_tcp_position":[0.50251,-0.114,0.14146],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":137.28385,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":860.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3440.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_target","tcp_end":[0.55033,0.08988,0.05659],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.06315,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":326.0,"n_steps_budget":1000.0,"object_pos_end":[0.52286,-0.04146,0.02456],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.11093,"object_to_goal_dist_start":0.1905,"object_z_max":0.03498,"peak_contact_force":0.24433,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":975.0,"raw_peak_contact_force":137.28385,"subtask_id":"push_goal","tcp_end":[0.50512,-0.11446,0.04649],"tcp_start":[0.55033,0.08988,0.05659],"tcp_to_object_dist_end":0.07826,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":205.0,"n_steps_budget":1000.0,"object_pos_end":[0.52283,-0.04156,0.02499],"object_pos_start":[0.52286,-0.04146,0.02456],"object_to_goal_dist_end":0.11082,"object_to_goal_dist_start":0.11093,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":820.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50251,-0.114,0.14146],"tcp_start":[0.50512,-0.11446,0.04649],"tcp_to_object_dist_end":0.13866,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.16514,"average_solve_count":218.0,"average_success_count":218.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_speed":0.0118,"approach_1.approach_tolerance":0.01126,"approach_1.approach_x_offset":0.03597,"approach_1.approach_y_offset":0.07564,"push_1.push_speed":0.06316,"push_1.push_tolerance":0.02573,"retract_1.retract_height":0.09171,"retract_1.retract_speed":0.06298,"retract_1.retract_tolerance":0.04989},"optimized_scores":{"best_composite_score":0.01494,"best_fitness_score":0.49494,"best_task_score":0.49015},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":179.0,"contact_point_centroid":[0.51885,-0.0419,0.05149],"force_p95":91.27942,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":94.43463,"mean_force":54.68668,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51612,-0.05207,0.05218]},{"body_a":"world","body_b":"push_box","contact_count":972.0,"contact_point_centroid":[0.49827,-0.03596,-0.00014],"force_p95":67.24417,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":78.70338,"mean_force":10.43984,"phase_index":1.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52043,-0.01954,0.05257]},{"body_a":"world","body_b":"push_box","contact_count":223.0,"contact_point_centroid":[0.48674,-0.08545,-0.00024],"force_p95":0.51731,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.73507,"mean_force":0.27309,"phase_index":2.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49965,-0.12533,0.06397]},{"body_a":"world","body_b":"push_box","contact_count":3284.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51604,0.02625,0.17916]}],"total_contact_groups":4},"final_pose_error":0.04989,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.48826,-0.08411,0.02495],"final_tcp_position":[0.49975,-0.12489,0.08887],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":94.43463,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":821.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3284.0,"raw_peak_contact_force":0.24534,"subtask_id":"approach_target","tcp_end":[0.53432,0.05319,0.0586],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.08485,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":365.0,"n_steps_budget":1000.0,"object_pos_end":[0.48808,-0.08513,0.0237],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.06597,"object_to_goal_dist_start":0.13127,"object_z_max":0.03555,"peak_contact_force":0.82678,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1151.0,"raw_peak_contact_force":94.43463,"subtask_id":"push_goal","tcp_end":[0.50185,-0.12476,0.047],"tcp_start":[0.53432,0.05319,0.0586],"tcp_to_object_dist_end":0.04799,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":59.0,"n_steps_budget":930.0,"object_pos_end":[0.48826,-0.08411,0.02495],"object_pos_start":[0.48808,-0.08513,0.0237],"object_to_goal_dist_end":0.06693,"object_to_goal_dist_start":0.06597,"object_z_max":0.02495,"peak_contact_force":0.24566,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":223.0,"raw_peak_contact_force":0.73507,"tcp_end":[0.49975,-0.12489,0.08887],"tcp_start":[0.50185,-0.12476,0.047],"tcp_to_object_dist_end":0.07668,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```