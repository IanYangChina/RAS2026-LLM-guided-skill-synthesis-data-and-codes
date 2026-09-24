## Search State

- **Seed**: 3
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 4 | -0.1333 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4639 | 0.71 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.73 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4582 | 0.64 | ✅ accepted |
| 2 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.0256 | 0.00 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

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
| `object` | offset from object initial position (0.45027790005723495, -0.03158273920846803, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=-0.133) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
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
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
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
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: -0.133
- **task_score** (E): 0.000
- **fitness_score**: 0.127  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.260

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1648 |
| contact_1 | 1.00 | 1.00 | 0.0898 |
| push_1 | 0.00 | 1.00 | 0.0000 |
| retract_1 | 1.00 | 1.00 | 0.0505 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.002, 0.143) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.002, 0.143)→(0.510, 0.002, 0.053) | (0.513, 0.002, 0.025)→(0.514, 0.002, 0.025) | 0.160→0.160 | 1.00 / 5.000 | 80.718 | 83.782 |
| push_1 | push | 0.00 / guard_failure | (0.510, 0.002, 0.053)→(0.510, 0.002, 0.053) | (0.514, 0.002, 0.025)→(0.514, 0.002, 0.025) | 0.160→0.160 | 1.00 / 5.000 | 52.827 | 63.459 |
| retract_1 | retract | 1.00 / step_budget | (0.510, 0.002, 0.053)→(0.508, 0.002, 0.104) | (0.514, 0.002, 0.025)→(0.514, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.248 | 55.793 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.002
- lateral_force_integral: None
- approach_alignment: 0.459
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.212
- phase_breakdown.reach_object_score: 0.677
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.contact_object_score: 0.574

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.127
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.133
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.328


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.10256,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07446,"contact_1.speed":0.02372,"push_1.push_distance":0.02298,"push_1.speed":0.06298},"optimized_scores":{"best_composite_score":-0.13412,"best_fitness_score":0.12588,"best_task_score":0.00053},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":22.0,"contact_point_centroid":[0.45747,-0.03129,0.04931],"force_p95":96.921,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":98.47464,"mean_force":73.92131,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44726,-0.03106,0.05516]},{"body_a":"attachment","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.45752,-0.03136,0.04942],"force_p95":50.68214,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.28309,"mean_force":14.44418,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.44733,-0.03115,0.0551]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.45809,-0.03135,0.0487],"force_p95":61.47486,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":61.52887,"mean_force":59.72152,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44787,-0.03115,0.05424]},{"body_a":"world","body_b":"push_box","contact_count":2276.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":40.05016,"mean_force":0.96143,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44911,-0.02921,0.09694]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.45042,-0.03162,-0.00023],"force_p95":28.50941,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":29.87591,"mean_force":15.14467,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44787,-0.03115,0.05424]},{"body_a":"world","body_b":"push_box","contact_count":198.0,"contact_point_centroid":[0.44394,-0.0316,-0.00019],"force_p95":5.59488,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":21.51685,"mean_force":1.18699,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.44612,-0.03112,0.07818]},{"body_a":"world","body_b":"push_box","contact_count":1284.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47732,-0.01318,0.22337]}],"total_contact_groups":7},"final_pose_error":0.04977,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.45044,-0.03159,0.02479],"final_tcp_position":[0.44639,-0.03114,0.10445],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":98.47464,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":321.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1284.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.45414,-0.02738,0.14367],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11882,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":569.0,"n_steps_budget":1000.0,"object_pos_end":[0.45065,-0.03163,0.02453],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12824,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":98.47464,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2298.0,"raw_peak_contact_force":98.47464,"subtask_id":"contact_object","tcp_end":[0.44786,-0.03115,0.05426],"tcp_start":[0.45414,-0.02738,0.14367],"tcp_to_object_dist_end":0.02987,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.45063,-0.03163,0.02453],"object_pos_start":[0.45065,-0.03163,0.02453],"object_to_goal_dist_end":0.12826,"object_to_goal_dist_start":0.12824,"object_z_max":0.02453,"peak_contact_force":61.52887,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":61.52887,"subtask_id":"push_to_goal","tcp_end":[0.44787,-0.03116,0.0542],"tcp_start":[0.44787,-0.03116,0.05421],"tcp_to_object_dist_end":0.0298,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":62.0,"n_steps_budget":630.0,"object_pos_end":[0.45044,-0.03159,0.02479],"object_pos_start":[0.45058,-0.03163,0.02453],"object_to_goal_dist_end":0.12836,"object_to_goal_dist_start":0.12827,"object_z_max":0.02597,"peak_contact_force":0.2469,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":210.0,"raw_peak_contact_force":64.28309,"tcp_end":[0.44639,-0.03114,0.10445],"tcp_start":[0.44787,-0.03116,0.0542],"tcp_to_object_dist_end":0.07976,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.47154,"average_solve_count":123.0,"average_success_count":123.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.07223,"contact_1.speed":0.04032,"push_1.push_distance":0.05881,"push_1.speed":0.04917},"optimized_scores":{"best_composite_score":-0.13284,"best_fitness_score":0.12716,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":16.0,"contact_point_centroid":[0.55965,0.00126,0.04952],"force_p95":70.21252,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":73.36397,"mean_force":54.14815,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54828,0.00122,0.05299]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.56025,0.00128,0.04912],"force_p95":63.24238,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":64.92125,"mean_force":52.73317,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54887,0.00123,0.05235]},{"body_a":"attachment","body_b":"push_box","contact_count":13.0,"contact_point_centroid":[0.55971,0.00124,0.04993],"force_p95":49.03157,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":51.05741,"mean_force":15.68283,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54834,0.0012,0.05329]},{"body_a":"world","body_b":"push_box","contact_count":2220.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.44405,"mean_force":0.63822,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54447,0.00114,0.09345]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.55333,0.00136,-0.00013],"force_p95":32.54653,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":34.4813,"mean_force":13.45721,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54887,0.00123,0.05235]},{"body_a":"world","body_b":"push_box","contact_count":190.0,"contact_point_centroid":[0.5444,0.00133,-0.00017],"force_p95":8.96842,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":25.47329,"mean_force":1.41651,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.54699,0.00114,0.07673]},{"body_a":"world","body_b":"push_box","contact_count":1340.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52047,0.00054,0.22254]}],"total_contact_groups":7},"final_pose_error":0.04959,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55337,0.00132,0.02468],"final_tcp_position":[0.54697,0.00112,0.10275],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":73.36397,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":335.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1340.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.54356,0.00111,0.14201],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":555.0,"n_steps_budget":1000.0,"object_pos_end":[0.55355,0.00136,0.02475],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16055,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":69.16204,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2236.0,"raw_peak_contact_force":73.36397,"subtask_id":"contact_object","tcp_end":[0.54884,0.00123,0.05238],"tcp_start":[0.54356,0.00111,0.14201],"tcp_to_object_dist_end":0.02803,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.55352,0.00136,0.02475],"object_pos_start":[0.55355,0.00136,0.02475],"object_to_goal_dist_end":0.16054,"object_to_goal_dist_start":0.16055,"object_z_max":0.02475,"peak_contact_force":48.13258,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":64.92125,"subtask_id":"push_to_goal","tcp_end":[0.5489,0.00122,0.05231],"tcp_start":[0.54889,0.00123,0.05233],"tcp_to_object_dist_end":0.02795,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":65.0,"n_steps_budget":630.0,"object_pos_end":[0.55337,0.00132,0.02468],"object_pos_start":[0.55346,0.00135,0.02474],"object_to_goal_dist_end":0.16045,"object_to_goal_dist_start":0.16052,"object_z_max":0.0268,"peak_contact_force":0.24842,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":203.0,"raw_peak_contact_force":51.05741,"tcp_end":[0.54697,0.00112,0.10275],"tcp_start":[0.5489,0.00122,0.05231],"tcp_to_object_dist_end":0.07833,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.81657,"average_solve_count":169.0,"average_success_count":169.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05626,"contact_1.speed":0.0243,"push_1.push_distance":0.07983,"push_1.speed":0.05971},"optimized_scores":{"best_composite_score":-0.13304,"best_fitness_score":0.12696,"best_task_score":0.00021},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":17.0,"contact_point_centroid":[0.54323,0.03616,0.0495],"force_p95":75.68954,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":79.50704,"mean_force":56.98376,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.532,0.03615,0.05336]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.54384,0.03623,0.04906],"force_p95":62.41573,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":63.92645,"mean_force":52.70645,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5326,0.03623,0.05268]},{"body_a":"attachment","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.54338,0.03622,0.04974],"force_p95":48.98923,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":52.03784,"mean_force":16.57629,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53215,0.03619,0.05346]},{"body_a":"world","body_b":"push_box","contact_count":2312.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":38.56782,"mean_force":0.66763,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.529,0.03403,0.09432]},{"body_a":"world","body_b":"push_box","contact_count":12.0,"contact_point_centroid":[0.53676,0.03698,-0.00015],"force_p95":31.76436,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":36.85122,"mean_force":13.45333,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5326,0.03623,0.05268]},{"body_a":"world","body_b":"push_box","contact_count":190.0,"contact_point_centroid":[0.52837,0.03664,-0.00018],"force_p95":10.03503,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":27.79726,"mean_force":1.38989,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.53076,0.03603,0.07722]},{"body_a":"world","body_b":"push_box","contact_count":1376.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.5134,0.01538,0.22277]}],"total_contact_groups":7},"final_pose_error":0.04919,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53679,0.03687,0.02469],"final_tcp_position":[0.53079,0.03601,0.10348],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":79.50704,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":344.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.52906,0.03197,0.14233],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.11769,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":578.0,"n_steps_budget":1000.0,"object_pos_end":[0.53699,0.03699,0.02471],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19061,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":74.51615,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2329.0,"raw_peak_contact_force":79.50704,"subtask_id":"contact_object","tcp_end":[0.53258,0.03622,0.05271],"tcp_start":[0.52906,0.03197,0.14233],"tcp_to_object_dist_end":0.02836,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53696,0.03699,0.02471],"object_pos_start":[0.53699,0.03699,0.02471],"object_to_goal_dist_end":0.19061,"object_to_goal_dist_start":0.19061,"object_z_max":0.02471,"peak_contact_force":48.81921,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":15.0,"raw_peak_contact_force":63.92645,"subtask_id":"push_to_goal","tcp_end":[0.53263,0.03623,0.05264],"tcp_start":[0.53262,0.03623,0.05266],"tcp_to_object_dist_end":0.02827,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":65.0,"n_steps_budget":630.0,"object_pos_end":[0.53679,0.03687,0.02469],"object_pos_start":[0.53691,0.03698,0.0247],"object_to_goal_dist_end":0.19046,"object_to_goal_dist_start":0.19059,"object_z_max":0.02668,"peak_contact_force":0.24853,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":202.0,"raw_peak_contact_force":52.03784,"tcp_end":[0.53079,0.03601,0.10348],"tcp_start":[0.53263,0.03623,0.05264],"tcp_to_object_dist_end":0.07902,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```