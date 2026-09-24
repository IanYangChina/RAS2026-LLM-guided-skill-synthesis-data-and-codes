## Search State

- **Seed**: 6
- **Iteration**: 3 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 2 | approach → contact → push → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | pose_tolerance | 10 | -0.2615 | 0.13 | ❌ rejected |
| 1 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4871 | 0.76 | ✅ accepted |
| 0 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4850 | 0.76 | ✅ accepted |

**Proposal policy**: task_score is 0.13 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.261) — your mutation base

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

- **Composite score**: -0.261
- **task_score** (E): 0.134
- **fitness_score**: 0.262  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.067
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.590

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.0596 |
| contact_1 | 0.33 | 1.00 | 0.1732 |
| push_1 | 1.00 | 1.00 | 0.0703 |
| push_2 | 1.00 | 1.00 | 0.0736 |
| retract_1 | 1.00 | 1.00 | 0.2617 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.498, 0.019, 0.273) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.33 / step_budget | (0.498, 0.019, 0.273)→(0.496, 0.025, 0.100) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.333 | 16.780 | 0.245 |
| push_1 | push | 1.00 / step_budget | (0.496, 0.025, 0.100)→(0.519, -0.000, 0.044) | (0.500, 0.029, 0.025)→(0.505, 0.026, 0.025) | 0.180→0.176 | 1.00 / 3.000 | 220.932 | 236.975 |
| push_2 | push | 1.00 / step_budget | (0.519, -0.000, 0.044)→(0.501, -0.069, 0.024) | (0.505, 0.026, 0.025)→(0.501, -0.011, 0.028) | 0.176→0.140 | 1.00 / 3.333 | 0.324 | 156.302 |
| retract_1 | retract | 1.00 / step_budget | (0.501, -0.069, 0.024)→(0.501, 0.007, 0.274) | (0.501, -0.011, 0.028)→(0.500, 0.037, 0.025) | 0.140→0.188 | 1.00 / 4.000 | 0.245 | 30.773 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.403
- lateral_force_integral: None
- approach_alignment: 0.988
- goal_progress: 0.403
- terminal_score: 0.403
- phase_score: 0.334
- phase_breakdown.push_to_goal_score: 0.377
- phase_breakdown.reach_object_score: 0.233

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.361
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.403
- **Median Q (composite search score)**: -0.355
- **K-run variance**: 0.0275
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.448


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.99371,"average_solve_count":159.0,"average_success_count":159.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.15796,"approach_1.speed":0.08594,"contact_1.contact_force":5.29778,"contact_1.speed":0.07428,"push_1.push_depth1":0.02407,"push_1.speed":0.07398,"push_2.push_depth2":0.11988,"push_2.speed":0.07695,"retract_1.retract_height":0.19634,"retract_1.speed":0.17188},"optimized_scores":{"best_composite_score":-0.02854,"best_fitness_score":0.36146,"best_task_score":0.40286},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":392.0,"contact_point_centroid":[0.52325,-0.02654,0.04665],"force_p95":222.82436,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":232.14112,"mean_force":193.97541,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51277,-0.03004,0.04667]},{"body_a":"world","body_b":"push_box","contact_count":1147.0,"contact_point_centroid":[0.5154,-0.02619,-0.00065],"force_p95":146.48354,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":163.43879,"mean_force":66.73997,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51137,-0.02891,0.04695]},{"body_a":"attachment","body_b":"push_box","contact_count":376.0,"contact_point_centroid":[0.52961,-0.05477,0.04557],"force_p95":141.2692,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":144.36717,"mean_force":112.90442,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.5261,-0.06588,0.0442]},{"body_a":"world","body_b":"push_box","contact_count":1366.0,"contact_point_centroid":[0.50961,-0.05579,-0.00036],"force_p95":125.35305,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":132.42096,"mean_force":31.5721,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.51623,-0.08948,0.03587]},{"body_a":"world","body_b":"push_box","contact_count":784.0,"contact_point_centroid":[0.50458,-0.01881,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50037,-0.00703,0.2529]},{"body_a":"world","body_b":"push_box","contact_count":3104.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49962,-0.01649,0.12485]},{"body_a":"world","body_b":"push_box","contact_count":1432.0,"contact_point_centroid":[0.50298,-0.07167,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49807,-0.14926,0.169]}],"total_contact_groups":7},"final_pose_error":0.0495,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50298,-0.07167,0.02499],"final_tcp_position":[0.50056,-0.04853,0.29027],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":232.14112,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":196.0,"n_steps_budget":870.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":784.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.50154,-0.01492,0.20224],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.17732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":776.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":49.85019,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3104.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.50023,-0.01806,0.05238],"tcp_start":[0.50154,-0.01492,0.20224],"tcp_to_object_dist_end":0.02775,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":392.0,"n_steps_budget":600.0,"object_pos_end":[0.5114,-0.02471,0.0249],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.12581,"object_to_goal_dist_start":0.13127,"object_z_max":0.02531,"peak_contact_force":212.36098,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1539.0,"raw_peak_contact_force":232.14112,"subtask_id":"push_to_goal","tcp_end":[0.52777,-0.04052,0.04422],"tcp_start":[0.50023,-0.01806,0.05238],"tcp_to_object_dist_end":0.02985,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":567.0,"n_steps_budget":900.0,"object_pos_end":[0.50298,-0.07167,0.02499],"object_pos_start":[0.5114,-0.02471,0.0249],"object_to_goal_dist_end":0.07839,"object_to_goal_dist_start":0.12581,"object_z_max":0.0354,"peak_contact_force":0.24525,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1742.0,"raw_peak_contact_force":144.36717,"subtask_id":"push_to_goal","tcp_end":[0.49887,-0.13488,0.02169],"tcp_start":[0.52777,-0.04052,0.04422],"tcp_to_object_dist_end":0.06343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":358.0,"n_steps_budget":1000.0,"object_pos_end":[0.50298,-0.07167,0.02499],"object_pos_start":[0.50298,-0.07167,0.02499],"object_to_goal_dist_end":0.07839,"object_to_goal_dist_start":0.07839,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1432.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.50056,-0.04853,0.29027],"tcp_start":[0.49887,-0.13488,0.02169],"tcp_to_object_dist_end":0.2663,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.3908,"average_solve_count":174.0,"average_success_count":174.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.2853,"approach_1.speed":0.0641,"contact_1.contact_force":9.13034,"contact_1.speed":0.03676,"push_1.push_depth1":0.03781,"push_1.speed":0.09821,"push_2.push_depth2":0.07468,"push_2.speed":0.10368,"retract_1.retract_height":0.14699,"retract_1.speed":0.19382},"optimized_scores":{"best_composite_score":-0.40128,"best_fitness_score":0.18872,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":122.0,"contact_point_centroid":[0.52481,0.02158,0.04634],"force_p95":249.81622,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":250.39696,"mean_force":201.27396,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51489,0.0159,0.04662]},{"body_a":"world","body_b":"push_box","contact_count":1132.0,"contact_point_centroid":[0.51567,0.04269,-0.00019],"force_p95":181.03732,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":221.34953,"mean_force":22.06464,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50905,0.02806,0.07602]},{"body_a":"attachment","body_b":"push_box","contact_count":140.0,"contact_point_centroid":[0.52709,0.00916,0.04319],"force_p95":168.39588,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":174.27449,"mean_force":107.71042,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.52364,-0.00172,0.04257]},{"body_a":"world","body_b":"push_box","contact_count":334.0,"contact_point_centroid":[0.51844,0.02748,-0.00055],"force_p95":129.93977,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":153.92181,"mean_force":45.6869,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.52224,-0.00442,0.04057]},{"body_a":"attachment","body_b":"push_box","contact_count":32.0,"contact_point_centroid":[0.5136,0.00775,0.03098],"force_p95":20.29869,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":48.59552,"mean_force":4.25167,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51224,-0.00388,0.03114]},{"body_a":"world","body_b":"push_box","contact_count":961.0,"contact_point_centroid":[0.52368,0.10036,-0.00019],"force_p95":1.00734,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":30.70976,"mean_force":0.48535,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50599,0.08368,0.16714]},{"body_a":"push_box","body_b":"link7","contact_count":10.0,"contact_point_centroid":[0.5317,0.0098,0.06574],"force_p95":22.65278,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":29.46152,"mean_force":4.40309,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.51276,-0.018,0.02829]},{"body_a":"world","body_b":"push_box","contact_count":376.0,"contact_point_centroid":[0.51501,0.04767,-0.0],"force_p95":0.24534,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50356,0.0143,0.30092]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50789,0.03614,0.2076]}],"total_contact_groups":9},"final_pose_error":0.04977,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52398,0.10164,0.02499],"final_tcp_position":[0.50196,0.04095,0.27177],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":250.39696,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":94.0,"n_steps_budget":600.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":376.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.50831,0.03084,0.30261],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.27821,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.50923,0.04149,0.11683],"tcp_start":[0.50831,0.03084,0.30261],"tcp_to_object_dist_end":0.09223,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":340.0,"n_steps_budget":630.0,"object_pos_end":[0.51968,0.0444,0.02607],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.1954,"object_to_goal_dist_start":0.19823,"object_z_max":0.02605,"peak_contact_force":244.2365,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1254.0,"raw_peak_contact_force":250.39696,"subtask_id":"push_to_goal","tcp_end":[0.52256,0.01139,0.04353],"tcp_start":[0.50923,0.04149,0.11683],"tcp_to_object_dist_end":0.03746,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":2.0,"n_steps":177.0,"n_steps_budget":600.0,"object_pos_end":[0.51653,0.02279,0.03351],"object_pos_start":[0.51968,0.0444,0.02607],"object_to_goal_dist_end":0.17379,"object_to_goal_dist_start":0.1954,"object_z_max":0.03564,"peak_contact_force":0.48234,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":474.0,"raw_peak_contact_force":174.27449,"subtask_id":"push_to_goal","tcp_end":[0.51375,-0.02061,0.02844],"tcp_start":[0.52256,0.01139,0.04353],"tcp_to_object_dist_end":0.04379,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":333.0,"n_steps_budget":900.0,"object_pos_end":[0.52398,0.10164,0.02499],"object_pos_start":[0.51653,0.02279,0.03351],"object_to_goal_dist_end":0.25278,"object_to_goal_dist_start":0.17379,"object_z_max":0.03605,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1003.0,"raw_peak_contact_force":48.59552,"tcp_end":[0.50196,0.04095,0.27177],"tcp_start":[0.51375,-0.02061,0.02844],"tcp_to_object_dist_end":0.25509,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.12992,"average_solve_count":254.0,"average_success_count":254.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.approach_height":0.29899,"approach_1.speed":0.13135,"contact_1.contact_force":2.88703,"contact_1.speed":0.01541,"push_1.push_depth1":0.03101,"push_1.speed":0.02747,"push_2.push_depth2":0.11689,"push_2.speed":0.04857,"retract_1.retract_height":0.20294,"retract_1.speed":0.16372},"optimized_scores":{"best_composite_score":-0.35465,"best_fitness_score":0.23535,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":336.0,"contact_point_centroid":[0.50092,0.03713,0.04549],"force_p95":216.08773,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":228.38767,"mean_force":196.78451,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.49208,0.03061,0.04519]},{"body_a":"world","body_b":"push_box","contact_count":2101.0,"contact_point_centroid":[0.48532,0.05606,-0.00032],"force_p95":187.99483,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":210.72613,"mean_force":31.84175,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.48265,0.03812,0.07169]},{"body_a":"world","body_b":"push_box","contact_count":1001.0,"contact_point_centroid":[0.48575,0.02457,-0.00026],"force_p95":131.09025,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":150.26305,"mean_force":18.85912,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.49756,-0.0195,0.03115]},{"body_a":"attachment","body_b":"push_box","contact_count":200.0,"contact_point_centroid":[0.50714,0.02351,0.04423],"force_p95":146.12964,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":149.28097,"mean_force":92.39573,"phase_index":3.0,"phase_name":"push_2","phase_type":"push","tcp_position_centroid":[0.50622,0.01183,0.04223]},{"body_a":"attachment","body_b":"push_box","contact_count":23.0,"contact_point_centroid":[0.48942,0.00046,0.03893],"force_p95":26.6068,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":43.47802,"mean_force":5.93017,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49027,-0.01049,0.0387]},{"body_a":"world","body_b":"push_box","contact_count":823.0,"contact_point_centroid":[0.47544,0.0643,-0.00016],"force_p95":0.85174,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":20.59195,"mean_force":0.50736,"phase_index":4.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49465,0.03369,0.1449]},{"body_a":"world","body_b":"push_box","contact_count":504.0,"contact_point_centroid":[0.47924,0.05847,-0.0],"force_p95":0.24533,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49153,0.02022,0.30569]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4797,0.04709,0.21993]}],"total_contact_groups":8},"final_pose_error":0.04954,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47255,0.08118,0.02499],"final_tcp_position":[0.49946,0.03008,0.26065],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":228.38767,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":126.0,"n_steps_budget":600.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":504.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.48345,0.0423,0.31318],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.28867,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.47766,0.05199,0.13001],"tcp_start":[0.48345,0.0423,0.31318],"tcp_to_object_dist_end":0.10523,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":636.0,"n_steps_budget":1000.0,"object_pos_end":[0.48522,0.05724,0.02492],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20777,"object_to_goal_dist_start":0.2095,"object_z_max":0.02523,"peak_contact_force":206.19946,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2437.0,"raw_peak_contact_force":228.38767,"subtask_id":"push_to_goal","tcp_end":[0.50543,0.02892,0.04299],"tcp_start":[0.47766,0.05199,0.13001],"tcp_to_object_dist_end":0.0392,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":421.0,"n_steps_budget":1000.0,"object_pos_end":[0.48346,0.01587,0.02499],"object_pos_start":[0.48522,0.05724,0.02492],"object_to_goal_dist_end":0.1667,"object_to_goal_dist_start":0.20777,"object_z_max":0.03541,"peak_contact_force":0.24525,"phase_name":"push_2","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":1201.0,"raw_peak_contact_force":150.26305,"subtask_id":"push_to_goal","tcp_end":[0.49091,-0.05011,0.02232],"tcp_start":[0.50543,0.02892,0.04299],"tcp_to_object_dist_end":0.06646,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":307.0,"n_steps_budget":1000.0,"object_pos_end":[0.47255,0.08118,0.02499],"object_pos_start":[0.48346,0.01587,0.02499],"object_to_goal_dist_end":0.2328,"object_to_goal_dist_start":0.1667,"object_z_max":0.03535,"peak_contact_force":0.24521,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":846.0,"raw_peak_contact_force":43.47802,"tcp_end":[0.49946,0.03008,0.26065],"tcp_start":[0.49091,-0.05011,0.02232],"tcp_to_object_dist_end":0.24263,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```