## Search State

- **Seed**: 3
- **Iteration**: 8 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 5 | 0.2069 | 0.41 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 4 | -0.1333 | 0.00 | ❌ rejected |
| 5 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4639 | 0.71 | ❌ rejected |
| 4 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4751 | 0.73 | ✅ accepted |
| 3 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4582 | 0.64 | ✅ accepted |

**Proposal policy**: task_score is 0.41 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.207) — your mutation base

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

- **Composite score**: 0.207
- **task_score** (E): 0.407
- **fitness_score**: 0.517  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1561 |
| contact_1 | 1.00 | 1.00 | 0.0995 |
| push_1 | 1.00 | 1.00 | 0.1177 |
| retract_1 | 1.00 | 1.00 | 0.0804 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.002, 0.153) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.002, 0.153)→(0.510, 0.002, 0.053) | (0.513, 0.002, 0.025)→(0.514, 0.002, 0.025) | 0.160→0.160 | 1.00 / 5.000 | 79.149 | 79.707 |
| push_1 | push | 1.00 / step_budget | (0.510, 0.002, 0.053)→(0.505, -0.109, 0.046) | (0.514, 0.002, 0.025)→(0.513, -0.059, 0.025) | 0.160→0.097 | 1.00 / 4.000 | 0.273 | 122.431 |
| retract_1 | retract | 1.00 / step_budget | (0.505, -0.109, 0.046)→(0.502, -0.109, 0.126) | (0.513, -0.059, 0.025)→(0.513, -0.059, 0.025) | 0.097→0.097 | 1.00 / 4.000 | 0.245 | 0.266 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.542
- lateral_force_integral: None
- approach_alignment: 0.787
- goal_progress: 0.535
- terminal_score: 0.535
- phase_score: 0.666
- phase_breakdown.reach_object_score: 0.821
- phase_breakdown.push_to_goal_score: 0.535
- phase_breakdown.contact_object_score: 0.906

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.614
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.535
- **Median Q (composite search score)**: 0.191
- **K-run variance**: 0.0054
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.377


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.05479,"average_solve_count":219.0,"average_success_count":219.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05197,"contact_1.speed":0.03134,"push_1.push_distance":0.14139,"push_1.speed":0.06928,"retract_1.speed":0.04964},"optimized_scores":{"best_composite_score":0.3036,"best_fitness_score":0.6136,"best_task_score":0.53475},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":528.0,"contact_point_centroid":[0.46905,-0.07048,-0.00058],"force_p95":135.9374,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":157.07594,"mean_force":41.90238,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47317,-0.08991,0.0507]},{"body_a":"attachment","body_b":"push_box","contact_count":225.0,"contact_point_centroid":[0.47229,-0.05987,0.05023],"force_p95":144.0176,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":155.83772,"mean_force":96.82716,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46472,-0.06568,0.05359]},{"body_a":"attachment","body_b":"push_box","contact_count":22.0,"contact_point_centroid":[0.45724,-0.03149,0.04928],"force_p95":100.80561,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":102.43819,"mean_force":76.87348,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44704,-0.03122,0.05512]},{"body_a":"world","body_b":"push_box","contact_count":2508.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":42.29188,"mean_force":0.92114,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.44781,-0.02994,0.10236]},{"body_a":"world","body_b":"push_box","contact_count":1096.0,"contact_point_centroid":[0.46981,-0.09844,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.26186,"mean_force":0.24501,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49168,-0.14516,0.08437]},{"body_a":"world","body_b":"push_box","contact_count":2068.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24529,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.47566,-0.01394,0.22771]}],"total_contact_groups":6},"final_pose_error":0.01996,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.46981,-0.09844,0.02499],"final_tcp_position":[0.49153,-0.14493,0.12589],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":157.07594,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":517.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2068.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.45163,-0.02874,0.15433],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12938,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":627.0,"n_steps_budget":1000.0,"object_pos_end":[0.45067,-0.03162,0.02452],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12825,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":102.43819,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2530.0,"raw_peak_contact_force":102.43819,"subtask_id":"contact_object","tcp_end":[0.4477,-0.0313,0.0542],"tcp_start":[0.45163,-0.02874,0.15433],"tcp_to_object_dist_end":0.02983,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":343.0,"n_steps_budget":1000.0,"object_pos_end":[0.46976,-0.09853,0.02484],"object_pos_start":[0.45067,-0.03162,0.02452],"object_to_goal_dist_end":0.0597,"object_to_goal_dist_start":0.12825,"object_z_max":0.0427,"peak_contact_force":0.26516,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":753.0,"raw_peak_contact_force":157.07594,"subtask_id":"push_to_goal","tcp_end":[0.49465,-0.14568,0.04559],"tcp_start":[0.4477,-0.0313,0.0542],"tcp_to_object_dist_end":0.05721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":274.0,"n_steps_budget":1000.0,"object_pos_end":[0.46981,-0.09844,0.02499],"object_pos_start":[0.46976,-0.09853,0.02484],"object_to_goal_dist_end":0.05975,"object_to_goal_dist_start":0.0597,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1096.0,"raw_peak_contact_force":0.26186,"tcp_end":[0.49153,-0.14493,0.12589],"tcp_start":[0.49465,-0.14568,0.04559],"tcp_to_object_dist_end":0.1132,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.66548,"average_solve_count":281.0,"average_success_count":281.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06232,"contact_1.speed":0.01855,"push_1.push_distance":0.14896,"push_1.speed":0.0483,"retract_1.speed":0.03891},"optimized_scores":{"best_composite_score":0.1911,"best_fitness_score":0.5011,"best_task_score":0.38637},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":235.0,"contact_point_centroid":[0.54821,-0.02488,0.05165],"force_p95":100.48622,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":101.29113,"mean_force":70.00934,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.54007,-0.03201,0.05357]},{"body_a":"world","body_b":"push_box","contact_count":818.0,"contact_point_centroid":[0.54436,-0.03849,-0.00026],"force_p95":69.6665,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":76.31955,"mean_force":20.55645,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52847,-0.06089,0.05024]},{"body_a":"attachment","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.55985,0.00126,0.04959],"force_p95":65.12832,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":66.21705,"mean_force":48.86773,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54848,0.00123,0.05311]},{"body_a":"world","body_b":"push_box","contact_count":2560.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.13823,"mean_force":0.51476,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54568,0.00117,0.09908]},{"body_a":"world","body_b":"push_box","contact_count":1124.0,"contact_point_centroid":[0.53845,-0.05938,-1e-05],"force_p95":0.24527,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24539,"mean_force":0.24523,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50311,-0.11972,0.0838]},{"body_a":"world","body_b":"push_box","contact_count":2236.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52156,0.00057,0.22575]}],"total_contact_groups":6},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.53845,-0.05938,0.02499],"final_tcp_position":[0.50296,-0.11943,0.12559],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":101.29113,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":559.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2236.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.54583,0.00118,0.15147],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.1267,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":640.0,"n_steps_budget":1000.0,"object_pos_end":[0.55343,0.00136,0.02479],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16051,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":64.54209,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2574.0,"raw_peak_contact_force":66.21705,"subtask_id":"contact_object","tcp_end":[0.5489,0.00123,0.05254],"tcp_start":[0.54583,0.00118,0.15147],"tcp_to_object_dist_end":0.02812,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":359.0,"n_steps_budget":1000.0,"object_pos_end":[0.53844,-0.05939,0.02497],"object_pos_start":[0.55343,0.00136,0.02479],"object_to_goal_dist_end":0.09843,"object_to_goal_dist_start":0.16051,"object_z_max":0.03518,"peak_contact_force":0.2454,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1053.0,"raw_peak_contact_force":101.29113,"subtask_id":"push_to_goal","tcp_end":[0.50615,-0.12003,0.04521],"tcp_start":[0.5489,0.00123,0.05254],"tcp_to_object_dist_end":0.07162,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":281.0,"n_steps_budget":1000.0,"object_pos_end":[0.53845,-0.05938,0.02499],"object_pos_start":[0.53844,-0.05939,0.02497],"object_to_goal_dist_end":0.09844,"object_to_goal_dist_start":0.09843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1124.0,"raw_peak_contact_force":0.24539,"tcp_end":[0.50296,-0.11943,0.12559],"tcp_start":[0.50615,-0.12003,0.04521],"tcp_to_object_dist_end":0.12242,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.7561,"average_solve_count":287.0,"average_success_count":287.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.02635,"contact_1.speed":0.03766,"push_1.push_distance":0.1204,"push_1.speed":0.02983,"retract_1.speed":0.07016},"optimized_scores":{"best_composite_score":0.12593,"best_fitness_score":0.43593,"best_task_score":0.29939},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":226.0,"contact_point_centroid":[0.53693,0.01126,0.05107],"force_p95":107.73417,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.92479,"mean_force":73.39754,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52904,0.00437,0.05337]},{"body_a":"attachment","body_b":"push_box","contact_count":14.0,"contact_point_centroid":[0.54336,0.03636,0.04952],"force_p95":69.60753,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":70.46556,"mean_force":57.21582,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.53213,0.03634,0.05338]},{"body_a":"world","body_b":"push_box","contact_count":606.0,"contact_point_centroid":[0.53373,0.00778,-0.00031],"force_p95":60.54748,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":61.91909,"mean_force":27.81858,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52643,-0.00577,0.05192]},{"body_a":"world","body_b":"push_box","contact_count":2344.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":31.55453,"mean_force":0.5891,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52988,0.03498,0.09974]},{"body_a":"world","body_b":"push_box","contact_count":1056.0,"contact_point_centroid":[0.52994,-0.01993,-2e-05],"force_p95":0.24567,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.29163,"mean_force":0.24484,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51049,-0.06187,0.08471]},{"body_a":"world","body_b":"push_box","contact_count":2348.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24528,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51399,0.01646,0.22614]}],"total_contact_groups":6},"final_pose_error":0.0199,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52994,-0.01993,0.02499],"final_tcp_position":[0.51028,-0.06159,0.12616],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":108.92479,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":587.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2348.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.53051,0.03377,0.15198],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12717,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":586.0,"n_steps_budget":1000.0,"object_pos_end":[0.53691,0.03698,0.02475],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19059,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":70.46556,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2358.0,"raw_peak_contact_force":70.46556,"subtask_id":"contact_object","tcp_end":[0.53259,0.03639,0.05276],"tcp_start":[0.53051,0.03377,0.15198],"tcp_to_object_dist_end":0.02834,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":293.0,"n_steps_budget":1000.0,"object_pos_end":[0.52983,-0.02036,0.02452],"object_pos_start":[0.53691,0.03698,0.02475],"object_to_goal_dist_end":0.13303,"object_to_goal_dist_start":0.19059,"object_z_max":0.03519,"peak_contact_force":0.30986,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":832.0,"raw_peak_contact_force":108.92479,"subtask_id":"push_to_goal","tcp_end":[0.51348,-0.06186,0.0458],"tcp_start":[0.53259,0.03639,0.05276],"tcp_to_object_dist_end":0.04942,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":900.0,"object_pos_end":[0.52994,-0.01993,0.02499],"object_pos_start":[0.52983,-0.02036,0.02452],"object_to_goal_dist_end":0.13347,"object_to_goal_dist_start":0.13303,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.29163,"tcp_end":[0.51028,-0.06159,0.12616],"tcp_start":[0.51348,-0.06186,0.0458],"tcp_to_object_dist_end":0.11117,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```