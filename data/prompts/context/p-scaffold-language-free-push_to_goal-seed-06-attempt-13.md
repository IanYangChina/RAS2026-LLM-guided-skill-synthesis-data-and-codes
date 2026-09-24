## Search State

- **Seed**: 6
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 8 | -0.3065 | 0.00 | ❌ rejected |
| 12 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | arc_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 9 | -0.1488 | 0.00 | ❌ rejected |
| 11 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4860 | 0.75 | ❌ rejected |
| 10 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4861 | 0.76 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | impedance_motion | impedance_motion | arc_cartesian | force_threshold_switch | force_threshold_switch | impedance_control | position_control | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | 0.4816 | 0.75 | ❌ rejected |

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

## Current Skill (Q=-0.306) — your mutation base

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

- **Composite score**: -0.306
- **task_score** (E): 0.000
- **fitness_score**: 0.042  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
  → CMA-ES cannot optimise this structure (shaped reward also near zero)
- **Termination Fidelity** (C): 0.111
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.460

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.1708 |
| contact_1 | 0.33 | 1.00 | 0.0872 |
| push_1 | 0.00 | 1.00 | 0.0007 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.497, 0.046, 0.140) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 0.33 / step_budget | (0.497, 0.046, 0.140)→(0.496, 0.053, 0.053) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.333 | 13.985 | 0.245 |
| push_1 | push | 0.00 / guard_failure | (0.496, 0.053, 0.053)→(0.495, 0.053, 0.052) | (0.500, 0.029, 0.025)→(0.500, 0.029, 0.025) | 0.180→0.180 | 1.00 / 4.333 | 13.623 | 31.369 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.000
- lateral_force_integral: None
- approach_alignment: 0.361
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.070
- phase_breakdown.push_to_goal_score: 0.000
- phase_breakdown.reach_object_score: 0.234

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.043
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.417
- **K-run variance**: 0.0246
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.313


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.80769,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.0389,"contact_1.contact_force":4.82141,"contact_1.speed":0.02867,"push_1.push_depth":0.13198,"push_1.speed":0.02617,"retract_1.arc_height":0.10808,"retract_1.retract_height":0.1489,"retract_1.speed":0.04557},"optimized_scores":{"best_composite_score":-0.41749,"best_fitness_score":0.04251,"best_task_score":0.00028},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.51183,0.00592,0.04989],"force_p95":25.81104,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.28118,"mean_force":22.56646,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5001,0.00597,0.05231]},{"body_a":"world","body_b":"push_box","contact_count":28.0,"contact_point_centroid":[0.501,-0.01524,-1e-05],"force_p95":13.91092,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":16.92638,"mean_force":5.09047,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.50017,0.00599,0.05241]},{"body_a":"world","body_b":"push_box","contact_count":3768.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.49951,0.00288,0.21287]},{"body_a":"world","body_b":"push_box","contact_count":1896.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.49939,0.00589,0.08931]}],"total_contact_groups":4},"final_pose_error":0.13173,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50451,-0.01884,0.02497],"final_tcp_position":[0.49994,0.0058,0.0521],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":26.28118,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":942.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3768.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.50104,0.00581,0.12846],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.10642,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":474.0,"n_steps_budget":1000.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":1896.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.50038,0.00604,0.05269],"tcp_start":[0.50104,0.00581,0.12846],"tcp_to_object_dist_end":0.03744,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":8.0,"n_steps_budget":1000.0,"object_pos_end":[0.50451,-0.01884,0.02497],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13124,"object_to_goal_dist_start":0.13127,"object_z_max":0.02499,"peak_contact_force":12.55925,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":34.0,"raw_peak_contact_force":26.28118,"subtask_id":"push_to_goal","tcp_end":[0.49994,0.0058,0.0521],"tcp_start":[0.50038,0.00604,0.05269],"tcp_to_object_dist_end":0.03694,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.09402,"average_solve_count":117.0,"average_success_count":117.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06092,"contact_1.contact_force":7.32479,"contact_1.speed":0.03421,"push_1.push_depth":0.06767,"push_1.speed":0.07983,"retract_1.arc_height":0.08961,"retract_1.retract_height":0.13739,"retract_1.speed":0.07206},"optimized_scores":{"best_composite_score":-0.08457,"best_fitness_score":0.0421,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":1.0,"contact_point_centroid":[0.52241,0.07129,0.04999],"force_p95":41.51413,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":41.51413,"mean_force":41.51413,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51068,0.07122,0.0525]},{"body_a":"world","body_b":"push_box","contact_count":4.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":26.0974,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":28.19203,"mean_force":10.60496,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51068,0.07122,0.0525]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.50384,0.03116,0.22019]},{"body_a":"world","body_b":"push_box","contact_count":2316.0,"contact_point_centroid":[0.51501,0.04767,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.50877,0.06622,0.09736]}],"total_contact_groups":4},"final_pose_error":0.06768,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51497,0.04767,0.02501],"final_tcp_position":[0.51063,0.07123,0.05242],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":41.51413,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.50953,0.06159,0.1458],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12174,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":579.0,"n_steps_budget":1000.0,"object_pos_end":[0.51501,0.04767,0.02499],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":41.46376,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2316.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.51068,0.07122,0.0525],"tcp_start":[0.50953,0.06159,0.1458],"tcp_to_object_dist_end":0.03647,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":1.0,"n_steps_budget":600.0,"object_pos_end":[0.51497,0.04767,0.02501],"object_pos_start":[0.51501,0.04767,0.02499],"object_to_goal_dist_end":0.19823,"object_to_goal_dist_start":0.19823,"object_z_max":0.02499,"peak_contact_force":2.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":5.0,"raw_peak_contact_force":41.51413,"subtask_id":"push_to_goal","tcp_end":[0.51063,0.07123,0.05242],"tcp_start":[0.51068,0.07122,0.0525],"tcp_to_object_dist_end":0.0364,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.36967,"average_solve_count":211.0,"average_success_count":211.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.04487,"contact_1.contact_force":7.64845,"contact_1.speed":0.01534,"push_1.push_depth":0.12585,"push_1.speed":0.01594,"retract_1.arc_height":0.12206,"retract_1.retract_height":0.19927,"retract_1.speed":0.01624},"optimized_scores":{"best_composite_score":-0.41731,"best_fitness_score":0.04269,"best_task_score":0.00021},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":5.0,"contact_point_centroid":[0.48672,0.08183,0.04988],"force_p95":25.77746,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":26.31076,"mean_force":20.59853,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47498,0.08171,0.05229]},{"body_a":"world","body_b":"push_box","contact_count":40.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":8.52411,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":9.76186,"mean_force":2.8016,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.47517,0.08181,0.05251]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.48842,0.03591,0.22021]},{"body_a":"world","body_b":"push_box","contact_count":2472.0,"contact_point_centroid":[0.47924,0.05847,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.47593,0.07655,0.09745]}],"total_contact_groups":4},"final_pose_error":0.12549,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.47923,0.05843,0.02497],"final_tcp_position":[0.47485,0.08149,0.05212],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":26.31076,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"subtask_id":"reach_object","tcp_end":[0.47894,0.07168,0.14442],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.12016,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":618.0,"n_steps_budget":1000.0,"object_pos_end":[0.47924,0.05847,0.02499],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.2095,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":2472.0,"raw_peak_contact_force":0.24525,"subtask_id":"reach_object","tcp_end":[0.47553,0.08192,0.05296],"tcp_start":[0.47894,0.07168,0.14442],"tcp_to_object_dist_end":0.03669,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":10.0,"n_steps_budget":1000.0,"object_pos_end":[0.47923,0.05843,0.02497],"object_pos_start":[0.47924,0.05847,0.02499],"object_to_goal_dist_end":0.20946,"object_to_goal_dist_start":0.2095,"object_z_max":0.02499,"peak_contact_force":26.31076,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":45.0,"raw_peak_contact_force":26.31076,"subtask_id":"push_to_goal","tcp_end":[0.47485,0.08149,0.05212],"tcp_start":[0.47553,0.08192,0.05296],"tcp_to_object_dist_end":0.03588,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```