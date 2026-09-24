## Search State

- **Seed**: 6
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | -0.0797 | 0.00 | ❌ rejected |
| 4 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | 0.0445 | 0.00 | ✅ accepted |
| 3 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 6 | -0.1777 | 0.00 | ❌ rejected |
| 2 | contact → push | linear_cartesian | linear_cartesian | force_threshold_switch | impedance_control | force_exceeded | pose_tolerance | 5 | -0.2128 | 0.00 | ❌ rejected |
| 1 | approach → push | linear_cartesian | linear_cartesian | position_control | impedance_control | pose_tolerance | pose_tolerance | 4 | 0.0444 | 0.00 | ✅ accepted |

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

## Current Skill (Q=-0.080) — your mutation base

```yaml
skill: push_to_goal
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: pre_contact
  anchor: object
  offset:
  - 0.0
  - 0.025
  - 0.025
  weight: 0.3
- id: push_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_contact
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: push_box
    offset:
    - 0.0
    - 0.025
    - 0.025
    tolerance: 0.005
    orientation:
      mode: keep_current
  parameters:
    approach_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    approach_tolerance:
      type: scalar
      range:
      - 0.001
      - 0.01
      default: 0.005
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: contact_during_approach
    when: during_phase
    predicate: contact_detected
    threshold: 1.0
    on_failure: continue
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.005
    - 0.0
  subtask_id: pre_contact
- id: push_to_goal
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: goal_marker
    offset:
    - 0.0
    - 0.025
    - 0.025
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    push_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  guards:
  - id: force_guard
    when: during_phase
    predicate: force_below
    threshold: 20.0
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: reduce_speed
  subtask_id: push_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_contact** (`approach`)
  - target: source=yaml, anchor=task_object, entity=push_box, offset=[0.0, 0.025, 0.025], tolerance=0.005
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_speed: status=consumed; consumers=generator.speed (replace)
    - approach_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=contact_during_approach, when=during_phase, predicate=contact_detected, on_failure=continue, threshold=1.0
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.005, 0.0]
- **push_to_goal** (`push`)
  - target: source=yaml, anchor=task_goal, entity=goal_marker, offset=[0.0, 0.025, 0.025], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - push_speed: status=consumed; consumers=generator.speed (replace)
    - push_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
  - guards:
    - id=force_guard, when=during_phase, predicate=force_below, on_failure=retry, threshold=20.0
  - retries: max_attempts=1, strategy=reduce_speed

## Design Metrics

- **Composite score**: -0.080
- **task_score** (E): 0.000
- **fitness_score**: 0.120  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.200

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_contact | 1.00 | 1.00 | 0.2649 |
| push_to_goal | 0.00 | 1.00 | 0.0001 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_contact | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.505, 0.057, 0.044) | (0.500, 0.029, 0.025)→(0.502, 0.031, 0.024) | 0.180→0.182 | 1.00 / 4.000 | 266.555 | 270.058 |
| push_to_goal | push | 0.00 / guard_failure | (0.505, 0.057, 0.044)→(0.505, 0.057, 0.044) | (0.502, 0.031, 0.024)→(0.502, 0.031, 0.024) | 0.182→0.182 | 1.00 / 4.000 | 127.371 | 127.371 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.024
- lateral_force_integral: None
- approach_alignment: 0.476
- goal_progress: 0.000
- terminal_score: 0.000
- phase_score: 0.203
- phase_breakdown.push_goal_score: 0.000
- phase_breakdown.reach_pre_contact_score: 0.677

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.122
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.000
- **Median Q (composite search score)**: -0.080
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.480


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.57143,"average_solve_count":28.0,"average_success_count":28.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.22141,"approach_contact.approach_tolerance":0.00511,"push_to_goal.push_speed":0.13657,"push_to_goal.push_tolerance":0.00589},"optimized_scores":{"best_composite_score":-0.07808,"best_fitness_score":0.12192,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":50.0,"contact_point_centroid":[0.51526,0.0068,0.04681],"force_p95":266.65564,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":267.59966,"mean_force":210.97942,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.50422,0.01094,0.04724]},{"body_a":"world","body_b":"push_box","contact_count":2820.0,"contact_point_centroid":[0.50504,-0.0184,-3e-05],"force_p95":9.0105,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":236.40315,"mean_force":4.0217,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.49962,0.00514,0.16909]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.51938,0.00578,0.04463],"force_p95":114.06992,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":114.73878,"mean_force":108.05014,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5093,0.01212,0.04392]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.51429,-0.01111,-0.00081],"force_p95":81.97667,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.83017,"mean_force":36.31957,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.5093,0.01212,0.04392]}],"total_contact_groups":4},"final_pose_error":0.16352,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50733,-0.01748,0.02438],"final_tcp_position":[0.50948,0.01214,0.04399],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":267.59966,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":717.0,"n_steps_budget":780.0,"object_pos_end":[0.50738,-0.01748,0.02436],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13273,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":265.31837,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2870.0,"raw_peak_contact_force":267.59966,"subtask_id":"reach_pre_contact","tcp_end":[0.50923,0.01211,0.0439],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03551,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":750.0,"object_pos_end":[0.50736,-0.01748,0.02437],"object_pos_start":[0.50738,-0.01748,0.02436],"object_to_goal_dist_end":0.13273,"object_to_goal_dist_start":0.13273,"object_z_max":0.02437,"peak_contact_force":114.73878,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":114.73878,"subtask_id":"push_goal","tcp_end":[0.50948,0.01214,0.04399],"tcp_start":[0.50937,0.01213,0.04393],"tcp_to_object_dist_end":0.03559,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.57143,"average_solve_count":28.0,"average_success_count":28.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.23037,"approach_contact.approach_tolerance":0.00505,"push_to_goal.push_speed":0.03742,"push_to_goal.push_tolerance":0.00926},"optimized_scores":{"best_composite_score":-0.08,"best_fitness_score":0.12,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":51.0,"contact_point_centroid":[0.52513,0.06792,0.04704],"force_p95":266.54932,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":267.65549,"mean_force":212.68903,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.51386,0.07095,0.04752]},{"body_a":"world","body_b":"push_box","contact_count":2867.0,"contact_point_centroid":[0.51548,0.0481,-3e-05],"force_p95":9.25449,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":241.16171,"mean_force":4.06319,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.50438,0.03532,0.1701]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.52959,0.06777,0.04509],"force_p95":156.37145,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":159.0381,"mean_force":132.37167,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51936,0.07388,0.04445]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.52501,0.05652,-0.00084],"force_p95":134.59683,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":149.36252,"mean_force":44.56928,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.51936,0.07388,0.04445]}],"total_contact_groups":4},"final_pose_error":0.22561,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.51808,0.05,0.02429],"final_tcp_position":[0.51941,0.07392,0.04452],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.51501,0.04767,0.025]},"peak_contact_force":267.65549,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":729.0,"n_steps_budget":780.0,"object_pos_end":[0.51811,0.04998,0.02427],"object_pos_start":[0.51501,0.04767,0.025],"object_to_goal_dist_end":0.20079,"object_to_goal_dist_start":0.19823,"object_z_max":0.025,"peak_contact_force":261.54939,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2918.0,"raw_peak_contact_force":267.65549,"subtask_id":"reach_pre_contact","tcp_end":[0.51935,0.07386,0.04444],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.03129,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.51808,0.04999,0.02427],"object_pos_start":[0.51811,0.04998,0.02427],"object_to_goal_dist_end":0.2008,"object_to_goal_dist_start":0.20079,"object_z_max":0.02427,"peak_contact_force":159.0381,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":159.0381,"subtask_id":"push_goal","tcp_end":[0.51941,0.07392,0.04452],"tcp_start":[0.51938,0.0739,0.04447],"tcp_to_object_dist_end":0.03138,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.55556,"average_solve_count":27.0,"average_success_count":27.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_contact.approach_speed":0.25211,"approach_contact.approach_tolerance":0.00619,"push_to_goal.push_speed":0.17001,"push_to_goal.push_tolerance":0.01332},"optimized_scores":{"best_composite_score":-0.08095,"best_fitness_score":0.11905,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":47.0,"contact_point_centroid":[0.49247,0.07778,0.04707],"force_p95":274.19258,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":274.91993,"mean_force":214.33887,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.48117,0.08068,0.04761]},{"body_a":"world","body_b":"push_box","contact_count":2758.0,"contact_point_centroid":[0.47967,0.0589,-3e-05],"force_p95":5.79166,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":227.33678,"mean_force":3.92691,"phase_index":0.0,"phase_name":"approach_contact","phase_type":"approach","tcp_position_centroid":[0.48816,0.04005,0.17095]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49563,0.07757,0.0449],"force_p95":107.8104,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":108.3376,"mean_force":103.06556,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48548,0.08382,0.04417]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.48863,0.0674,-0.00085],"force_p95":73.81769,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":75.72353,"mean_force":34.68407,"phase_index":1.0,"phase_name":"push_to_goal","phase_type":"push","tcp_position_centroid":[0.48548,0.08382,0.04417]}],"total_contact_groups":4},"final_pose_error":0.23513,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.4818,0.06083,0.02428],"final_tcp_position":[0.48567,0.0839,0.04423],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.47924,0.05847,0.025]},"peak_contact_force":274.91993,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":701.0,"n_steps_budget":750.0,"object_pos_end":[0.48185,0.06081,0.02427],"object_pos_start":[0.47924,0.05847,0.025],"object_to_goal_dist_end":0.21159,"object_to_goal_dist_start":0.2095,"object_z_max":0.025,"peak_contact_force":272.79603,"phase_name":"approach_contact","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2805.0,"raw_peak_contact_force":274.91993,"subtask_id":"reach_pre_contact","tcp_end":[0.48542,0.08379,0.04416],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0306,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":870.0,"object_pos_end":[0.48183,0.06083,0.02428],"object_pos_start":[0.48185,0.06081,0.02427],"object_to_goal_dist_end":0.21161,"object_to_goal_dist_start":0.21159,"object_z_max":0.02428,"peak_contact_force":108.3376,"phase_name":"push_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":8.0,"raw_peak_contact_force":108.3376,"subtask_id":"push_goal","tcp_end":[0.48567,0.0839,0.04423],"tcp_start":[0.48555,0.08385,0.04418],"tcp_to_object_dist_end":0.03074,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```