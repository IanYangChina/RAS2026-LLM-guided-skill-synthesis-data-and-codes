## Search State

- **Seed**: 6
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4817 | 0.75 | ❌ rejected |
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.3065 | 0.00 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1488 | 0.00 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4860 | 0.75 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4861 | 0.76 | ❌ rejected |

**Proposal policy**: task_score is 0.75 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`
- Frozen object start: [0.5045797221766332, -0.01880749562239939, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5045797221766332, -0.01880749562239939, 0.025)
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
  frozen_object_start: [0.5046, -0.0188, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5045797221766332, -0.01880749562239939, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0046, -0.1312, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.757, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.5045797221766332, -0.01880749562239939, 0.025) | approach/contact targets near object start |
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

## Current Skill (Q=0.482) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: force_threshold_switch
  termination: pose_tolerance
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.3
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: impedance_motion
  control: force_threshold_switch
  termination: force_exceeded
  parameters:
    contact_force:
      type: scalar
      range:
      - 1.0
      - 20.0
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: impedance_motion
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
  generator: arc_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    retract_height:
      type: scalar
      range:
      - 0.05
      - 0.2
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1

```

## Design Metrics

- **Composite score**: 0.482
- **task_score** (E): 0.749
- **fitness_score**: 0.642  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.250
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.410

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2884 |
| contact_1 | 1.00 | 1.00 | 0.0386 |
| push_1 | 1.00 | 1.00 | 0.1289 |
| retract_1 | 0.00 | 1.00 | 0.1240 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, 0.103, 0.033) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / force_exceeded | (0.496, 0.103, 0.033)→(0.494, 0.066, 0.022) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 5.000 | 25308.191 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.494, 0.066, 0.022)→(0.496, -0.062, 0.020) | (0.500, 0.029, 0.025)→(0.498, -0.099, 0.026) | 0.180→0.051 | 1.00 / 2.000 | 1.223 | 66.879 |
| retract_1 | retract | 0.00 / step_budget | (0.496, -0.062, 0.020)→(0.494, 0.031, 0.102) | (0.498, -0.099, 0.026)→(0.497, -0.099, 0.025) | 0.051→0.051 | 1.00 / 4.000 | 0.245 | 1.948 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.990
- lateral_force_integral: None
- approach_alignment: 0.546
- goal_progress: 0.988
- terminal_score: 0.988
- phase_score: 0.762
- phase_breakdown.approach_score: 0.821
- phase_breakdown.push_score: 0.738
- phase_breakdown.contact_score: 0.764

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.852
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.988
- **Median Q (composite search score)**: 0.390
- **K-run variance**: 0.0223
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.443


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `acf3715aaa310bcc73047d49f01e71bc863ef036ae437b7dc851a0f6d3fe40ae`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `ec1d0331416d42e6883eeb3b72499fac99c0735b785eb70ece69dc94e8044fc3`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.01299,"average_solve_count":231.0,"average_success_count":231.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.11373,"approach_1.speed":0.03072,"contact_1.contact_force":10.81232,"contact_1.speed":0.02584,"push_1.push_depth":0.1,"retract_1.retract_height":0.18082,"retract_1.speed":0.05279},"optimized_scores":{"best_composite_score":0.69249,"best_fitness_score":0.85249,"best_task_score":0.98761},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1051.0,"contact_point_centroid":[0.50919,-0.09789,-0.00013],"force_p95":62.20517,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":74.81936,"mean_force":20.91873,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49728,-0.04496,0.02039]},{"body_a":"attachment","body_b":"push_box","contact_count":721.0,"contact_point_centroid":[0.5112,-0.05708,0.0445],"force_p95":51.17493,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":59.67323,"mean_force":21.59465,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49727,-0.04579,0.02038]},{"body_a":"push_box","body_b":"link7","contact_count":466.0,"contact_point_centroid":[0.52452,-0.04708,0.05282],"force_p95":44.56822,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":53.19778,"mean_force":27.02324,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49789,-0.02557,0.0207]},{"body_a":"world","body_b":"push_box","contact_count":3986.0,"contact_point_centroid":[0.501,-0.14876,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.29941,"mean_force":0.24692,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49276,-0.06652,0.05664]},{"body_a":"push_box","body_b":"link7","contact_count":1.0,"contact_point_centroid":[0.52598,-0.13657,0.0498],"force_p95":1.77083,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.77083,"mean_force":1.77083,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49496,-0.11095,0.01997]},{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.49601,-0.12329,0.01986],"force_p95":0.36987,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36987,"mean_force":0.36987,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49585,-0.1113,0.01992]},{"body_a":"world","body_b":"push_box","contact_count":3812.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4992,0.02866,0.16595]},{"body_a":"world","body_b":"push_box","contact_count":3516.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49792,0.0367,0.0252]}],"total_contact_groups":8},"final_pose_error":0.17901,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50094,-0.14867,0.02499],"final_tcp_position":[0.49362,-0.01923,0.09201],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":75893.53664,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":953.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3812.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.50029,0.05779,0.03318],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07715,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":879.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":75893.53664,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3516.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.49922,0.01817,0.02199],"tcp_start":[0.50029,0.05779,0.03318],"tcp_to_object_dist_end":0.03748,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":774.0,"n_steps_budget":870.0,"object_pos_end":[0.50115,-0.14825,0.02495],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.00209,"object_to_goal_dist_start":0.13127,"object_z_max":0.02864,"peak_contact_force":1.59554,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2238.0,"raw_peak_contact_force":74.81936,"tcp_end":[0.49585,-0.1113,0.01992],"tcp_start":[0.49922,0.01817,0.02199],"tcp_to_object_dist_end":0.03767,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.50094,-0.14867,0.02499],"object_pos_start":[0.50115,-0.14825,0.02495],"object_to_goal_dist_end":0.00163,"object_to_goal_dist_start":0.00209,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3988.0,"raw_peak_contact_force":2.29941,"tcp_end":[0.49362,-0.01923,0.09201],"tcp_start":[0.49585,-0.1113,0.01992],"tcp_to_object_dist_end":0.14595,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `589e611c6c27578474525e3fd29be4fb5907d8bbd5d1ca44922bfd811e342c78`; realized-scene SHA-256: `c8d09cd43835becf8e5eb4413394fad8627e4bf404e9e7726e9f380b60e09752`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.51501,0.04767,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.01501,-0.19767,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.51501,0.04767,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.41935,"average_solve_count":186.0,"average_success_count":186.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.06246,"approach_1.speed":0.08442,"contact_1.contact_force":10.22723,"contact_1.speed":0.02776,"push_1.push_depth":0.0995,"retract_1.retract_height":0.12632,"retract_1.speed":0.0452},"optimized_scores":{"best_composite_score":0.39002,"best_fitness_score":0.55002,"best_task_score":0.64887},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1067.0,"contact_point_centroid":[0.51969,-0.03335,-0.00013],"force_p95":55.54809,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":70.1045,"mean_force":27.31408,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50316,0.02198,0.02122]},{"body_a":"attachment","body_b":"push_box","contact_count":736.0,"contact_point_centroid":[0.51932,0.01108,0.04773],"force_p95":51.81994,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":57.8742,"mean_force":26.72035,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50302,0.02175,0.0211]},{"body_a":"push_box","body_b":"link7","contact_count":674.0,"contact_point_centroid":[0.52968,0.00453,0.05365],"force_p95":47.06691,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":56.40735,"mean_force":28.47194,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50329,0.0247,0.02112]},{"body_a":"world","body_b":"push_box","contact_count":3922.0,"contact_point_centroid":[0.49791,-0.08079,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.20557,"mean_force":0.24979,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49356,-0.00587,0.05962]},{"body_a":"push_box","body_b":"link7","contact_count":4.0,"contact_point_centroid":[0.5224,-0.06968,0.0527],"force_p95":1.57686,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.59635,"mean_force":1.29971,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49669,-0.04377,0.02035]},{"body_a":"attachment","body_b":"push_box","contact_count":22.0,"contact_point_centroid":[0.51359,-0.05417,0.05208],"force_p95":1.05278,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.24585,"mean_force":0.57052,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49557,-0.04264,0.02109]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50417,0.06014,0.16516]},{"body_a":"world","body_b":"push_box","contact_count":2960.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50802,0.10124,0.0251]}],"total_contact_groups":8},"final_pose_error":0.12796,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49784,-0.08043,0.02499],"final_tcp_position":[0.49439,0.0343,0.09563],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":70.1045,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.51025,0.1205,0.03322],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07346,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":740.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":18.34957,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2960.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50939,0.08466,0.02196],"tcp_start":[0.51025,0.1205,0.03322],"tcp_to_object_dist_end":0.03754,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":760.0,"n_steps_budget":870.0,"object_pos_end":[0.49934,-0.08106,0.02707],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.06898,"object_to_goal_dist_start":0.19823,"object_z_max":0.02883,"peak_contact_force":1.66457,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2477.0,"raw_peak_contact_force":70.1045,"tcp_end":[0.49675,-0.04364,0.02039],"tcp_start":[0.50939,0.08466,0.02196],"tcp_to_object_dist_end":0.03809,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49784,-0.08043,0.02499],"object_pos_start":[0.49934,-0.08106,0.02707],"object_to_goal_dist_end":0.06961,"object_to_goal_dist_start":0.06898,"object_z_max":0.0271,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3948.0,"raw_peak_contact_force":2.20557,"tcp_end":[0.49439,0.0343,0.09563],"tcp_start":[0.49675,-0.04364,0.02039],"tcp_to_object_dist_end":0.13478,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `f2c9c63f0d9eca1b3ff8bf951759f6a3adee73f9f65e1cd3613c5e9d1203ebcc`; realized-scene SHA-256: `f3b8ea82cefd9504be10e2d47c49094a836a703404c06bdee3b01a27a59bf7be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47924,0.05847,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.02076,-0.20847,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.47924,0.05847,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.65497,"average_solve_count":171.0,"average_success_count":171.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.13586,"approach_1.speed":0.08688,"contact_1.contact_force":9.89049,"contact_1.speed":0.02502,"push_1.push_depth":0.09649,"retract_1.retract_height":0.11423,"retract_1.speed":0.08758},"optimized_scores":{"best_composite_score":0.36263,"best_fitness_score":0.52263,"best_task_score":0.61136},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"push_box","contact_count":1141.0,"contact_point_centroid":[0.4931,-0.02048,-0.00014],"force_p95":44.63053,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":55.71433,"mean_force":12.16834,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48486,0.02455,0.0203]},{"body_a":"attachment","body_b":"push_box","contact_count":662.0,"contact_point_centroid":[0.49351,0.0245,0.03734],"force_p95":38.3987,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":45.55201,"mean_force":15.79021,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48304,0.03575,0.02044]},{"body_a":"push_box","body_b":"link7","contact_count":307.0,"contact_point_centroid":[0.50712,0.04011,0.0518],"force_p95":28.96884,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":33.36144,"mean_force":18.76778,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47867,0.06248,0.02076]},{"body_a":"world","body_b":"push_box","contact_count":3983.0,"contact_point_centroid":[0.49154,-0.06901,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.34006,"mean_force":0.2467,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49255,0.02006,0.07283]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.49382,-0.04304,0.02066],"force_p95":1.338,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.3389,"mean_force":0.94198,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49464,-0.03118,0.02017]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48725,0.06524,0.1654]},{"body_a":"world","body_b":"push_box","contact_count":3116.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4736,0.11132,0.02595]}],"total_contact_groups":7},"final_pose_error":0.07889,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49151,-0.06902,0.02499],"final_tcp_position":[0.49446,0.07808,0.11806],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":55.71433,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.4764,0.13065,0.03387],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07277,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":779.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":12.68558,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3116.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.47429,0.09545,0.02274],"tcp_start":[0.4764,0.13065,0.03387],"tcp_to_object_dist_end":0.03737,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":1.0,"n_steps":760.0,"n_steps_budget":870.0,"object_pos_end":[0.49234,-0.06776,0.02514],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.08259,"object_to_goal_dist_start":0.2095,"object_z_max":0.03169,"peak_contact_force":0.40972,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2110.0,"raw_peak_contact_force":55.71433,"tcp_end":[0.49467,-0.0311,0.02019],"tcp_start":[0.47429,0.09545,0.02274],"tcp_to_object_dist_end":0.03707,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49151,-0.06902,0.02499],"object_pos_start":[0.49234,-0.06776,0.02514],"object_to_goal_dist_end":0.08142,"object_to_goal_dist_start":0.08259,"object_z_max":0.02514,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3986.0,"raw_peak_contact_force":1.34006,"tcp_end":[0.49446,0.07808,0.11806],"tcp_start":[0.49467,-0.0311,0.02019],"tcp_to_object_dist_end":0.1741,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```