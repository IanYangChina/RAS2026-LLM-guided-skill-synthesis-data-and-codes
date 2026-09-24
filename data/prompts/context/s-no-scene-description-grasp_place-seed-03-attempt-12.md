## Search State

- **Seed**: 3
- **Iteration**: 13 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 12 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | 0.0702 | 0.43 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | -0.0416 | 0.21 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | 0.1391 | 0.41 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | 0.3490 | 0.62 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0852 | 0.25 | ❌ rejected |

**Proposal policy**: task_score is 0.43 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

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
| `object` | offset from object initial position | approach/contact targets near object start |
| `goal` | offset from task goal position | final destination targets |
| `fixture` | offset from fixture pose | targets near fixture |

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

## Current Skill (Q=0.070) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.3
- id: reach_goal
  target_entity: object
  weight: 0.7
phases:
- id: approach_to_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.1
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.05
      - 0.2
      default: 0.1
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: impedance_control
  termination: force_exceeded
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.2
      axis: world_z
      mode: add_to_offset
      sign: negative
    orientation:
      mode: align_axis
      axis:
      - 0.0
      - 0.0
      - 1.0
      align_with: world_z
      tolerance: 0.05
  parameters:
    descend_depth:
      type: scalar
      range:
      - 0.1
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    descend_force_threshold:
      type: scalar
      range:
      - 5.0
      - 20.0
      default: 15.0
      binds_to:
      - path: termination.force_threshold
        mode: replace
    descend_speed:
      type: scalar
      range:
      - 0.02
      - 0.08
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
- id: grasp
  type: grasp
  control: position_control
  termination: time_limit
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  parameters:
    grasp_duration:
      type: scalar
      range:
      - 0.2
      - 1.0
      default: 0.5
      binds_to:
      - path: duration.max_time
        mode: replace
  guards:
  - id: check_grasp
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.2
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.15
      - 0.3
      default: 0.2
      binds_to:
      - path: target.offset.z
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.05
      - 0.25
      default: 0.1
      binds_to:
      - path: generator.speed
        mode: replace
- id: transport_to_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    transport_speed:
      type: scalar
      range:
      - 0.1
      - 0.4
      default: 0.2
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: check_object_held
    when: during_phase
    predicate: object_lifted
    threshold: 0.05
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.05
  subtask_id: reach_goal

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_to_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.1], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.2, mode=add_to_offset, sign=negative}
  - orientation: mode=align_axis, axis=[0.0, 0.0, 1.0], align_with=world_z, tolerance=0.05
  - parameter_bindings:
    - descend_depth: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - descend_force_threshold: status=consumed; consumers=termination.force_threshold (replace)
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings:
    - grasp_duration: status=consumed; consumers=duration.max_time (replace)
  - guards:
    - id=check_grasp, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=repeat
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.2], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset.z (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
- **transport_to_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.0], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - transport_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=check_object_held, when=during_phase, predicate=object_lifted, on_failure=retry, threshold=0.05
  - retries: max_attempts=2, strategy=offset_target, offset=[0.0, 0.0, 0.05]

## Design Metrics

- **Composite score**: 0.070
- **task_score** (E): 0.425
- **fitness_score**: 0.477  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.133
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.2018 |
| descend_to_grasp | 0.67 | 1.00 | 0.0140 |
| grasp | 1.00 | 1.00 | 0.0000 |
| lift | 1.00 | 1.00 | 0.2282 |
| transport_to_goal | 1.00 | 1.00 | 0.2530 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.103) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 0.67 / force_exceeded | (0.506, 0.002, 0.103)→(0.517, -0.002, 0.095) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 278.165 | 0.082 |
| grasp | grasp | 1.00 / step_budget | (0.504, -0.002, 0.061)→(0.504, -0.002, 0.061) | (0.511, 0.002, 0.026)→(0.510, 0.002, 0.025) | 0.246→0.247 | 1.00 / 12.333 | 0.540 | 3.370 |
| lift | lift | 1.00 / step_budget | (0.504, -0.002, 0.061)→(0.502, -0.002, 0.289) | (0.510, 0.002, 0.025)→(0.516, -0.000, 0.109) | 0.247→0.230 | 1.00 / 17.333 | 0.116 | 1.521 |
| transport_to_goal | approach | 1.00 / step_budget | (0.502, -0.002, 0.289)→(0.614, 0.167, 0.141) | (0.516, -0.000, 0.109)→(0.543, 0.049, 0.075) | 0.230→0.171 | 1.00 / 19.000 | 182011.498 | 0.147 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.848
- phase_score: 0.669
- phase_breakdown.reach_object_score: 0.663
- phase_breakdown.reach_goal_score: 0.672
- grasp_place_fitness: 0.890

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.890
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.848
- **Median Q (composite search score)**: -0.111
- **K-run variance**: 0.1176
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.393


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `a4a71a7b2980790489e8194d1356bdee33fb951291c2e0792659ad3d3b3dc711`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `8a78b0f0015ebaf8c4b14c8fbc8142d9b66e4b4efca10f362859101c0ae207df`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.54902,"average_solve_count":102.0,"average_success_count":102.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.05001,"approach_to_object.approach_speed":0.29271,"descend_to_grasp.descend_force_threshold":15.22337,"descend_to_grasp.descend_speed":0.07342,"descend_to_grasp.descend_z_offset":-0.01854,"grasp.grasp_duration":0.70035,"lift.lift_height":0.25576,"lift.lift_speed":0.12069,"transport_to_goal.transport_speed":0.20816},"optimized_scores":{"best_composite_score":-0.11061,"best_fitness_score":0.22939,"best_task_score":0.13208},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1352.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.13562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.47976,-0.01131,0.20084]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4528,-0.02253,0.09024]},{"body_a":"world","body_b":"grasp_target","contact_count":2800.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44923,-0.02239,0.2071]},{"body_a":"world","body_b":"grasp_target","contact_count":2788.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.53258,0.0856,0.22034]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45975,-0.02316,0.09944]},{"body_a":"left_finger","body_b":"right_finger","contact_count":750.0,"contact_point_centroid":[0.45217,-0.02251,0.09163],"force_p95":0.01316,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01097,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45198,-0.02251,0.0894]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2933.0,"contact_point_centroid":[0.44948,-0.0224,0.21002],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01297,"mean_force":0.01062,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44923,-0.02239,0.20772]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2957.0,"contact_point_centroid":[0.53251,0.08524,0.22291],"force_p95":0.011,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01281,"mean_force":0.0105,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.5323,0.08524,0.22068]}],"total_contact_groups":8},"final_pose_error":0.01968,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45856,-0.02632,0.02602],"final_tcp_position":[0.6167,0.19429,0.11774],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273016.61103,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1352.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45975,-0.0232,0.09973],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07378,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":405.43194,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12262,"tcp_end":[0.45985,-0.02291,0.09849],"tcp_start":[0.45975,-0.0232,0.09973],"tcp_to_object_dist_end":0.07256,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2950.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45198,-0.02251,0.0894],"tcp_start":[0.45198,-0.02251,0.0894],"tcp_to_object_dist_end":0.06383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":700.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5733.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45002,-0.02243,0.32548],"tcp_start":[0.45198,-0.02251,0.0894],"tcp_to_object_dist_end":0.29961,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":697.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":273016.61103,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":5745.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.6167,0.19429,0.11774],"tcp_start":[0.45002,-0.02243,0.32548],"tcp_to_object_dist_end":0.28651,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":80.0,"average_failure_rate":0.46512,"average_mean_iterations":95.82558,"average_solve_count":172.0,"average_success_count":92.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.06385,"approach_to_object.approach_speed":0.18358,"descend_to_grasp.descend_force_threshold":5.20036,"descend_to_grasp.descend_speed":0.02285,"descend_to_grasp.descend_z_offset":-0.01921,"grasp.grasp_duration":0.76133,"lift.lift_height":0.29041,"lift.lift_speed":0.13046,"transport_to_goal.transport_speed":0.24359},"optimized_scores":{"best_composite_score":0.55028,"best_fitness_score":0.89028,"best_task_score":0.8485},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":5943.0,"contact_point_centroid":[0.5342,0.02843,-0.00187],"force_p95":1.39522,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":9.86331,"mean_force":0.83864,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54518,-0.00981,0.00488]},{"body_a":"world","body_b":"right_finger","contact_count":190.0,"contact_point_centroid":[0.53696,0.02634,-0.00142],"force_p95":3.86919,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":4.31641,"mean_force":1.51425,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54444,-0.00959,0.00655]},{"body_a":"world","body_b":"left_finger","contact_count":38.0,"contact_point_centroid":[0.55947,-0.04519,-0.00059],"force_p95":3.42193,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.49438,"mean_force":2.08888,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54486,-0.00961,0.00519]},{"body_a":"grasp_target","body_b":"hand","contact_count":510.0,"contact_point_centroid":[0.55751,0.01836,0.0458],"force_p95":0.45889,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.95181,"mean_force":0.42148,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54541,-0.0098,0.00511]},{"body_a":"world","body_b":"grasp_target","contact_count":221.0,"contact_point_centroid":[0.53889,-0.00098,-0.0025],"force_p95":0.37194,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.94008,"mean_force":0.19658,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54322,-0.00957,0.01219]},{"body_a":"grasp_target","body_b":"hand","contact_count":533.0,"contact_point_centroid":[0.56447,-0.00158,0.12045],"force_p95":0.51096,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.67464,"mean_force":0.13926,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54106,-0.0098,0.08566]},{"body_a":"world","body_b":"left_finger","contact_count":1951.0,"contact_point_centroid":[0.5604,-0.04812,-0.00067],"force_p95":0.45532,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.4749,"mean_force":0.39202,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54515,-0.0098,0.00484]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.54194,-0.00078,-0.00336],"force_p95":0.31772,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.4122,"mean_force":0.21575,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54804,-0.00972,0.00868]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":17374.0,"contact_point_centroid":[0.53746,0.00922,0.14687],"force_p95":0.08279,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40371,"mean_force":0.05167,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54132,-0.00981,0.14629]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15231.0,"contact_point_centroid":[0.54625,-0.02821,0.15059],"force_p95":0.08136,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25237,"mean_force":0.05441,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54126,-0.00982,0.14737]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":7554.0,"contact_point_centroid":[0.58883,0.08926,0.22836],"force_p95":0.10246,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19676,"mean_force":0.05831,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59125,0.07053,0.22821]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6173.0,"contact_point_centroid":[0.5981,0.05286,0.23036],"force_p95":0.10886,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18798,"mean_force":0.06972,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59127,0.07057,0.22816]},{"body_a":"world","body_b":"grasp_target","contact_count":1376.0,"contact_point_centroid":[0.54431,0.00113,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12298,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51672,0.00046,0.20647]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54589,-0.00296,0.10242]}],"total_contact_groups":14},"final_pose_error":0.01991,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63886,0.14274,0.17392],"final_tcp_position":[0.6355,0.14238,0.18944],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":428.94144,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":345.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1376.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53555,0.00094,0.11139],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08582,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":428.94144,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":84.0,"raw_peak_contact_force":0.12262,"tcp_end":[0.56799,-0.00915,0.0888],"tcp_start":[0.53555,0.00094,0.11139],"tcp_to_object_dist_end":0.06788,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":21.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.5405,0.00174,0.0229],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.2534,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":1.37544,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10604.0,"raw_peak_contact_force":9.86331,"tcp_end":[0.54512,-0.00963,0.00475],"tcp_start":[0.54512,-0.00963,0.00476],"tcp_to_object_dist_end":0.02191,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":36.0,"n_steps":890.0,"n_steps_budget":1000.0,"object_pos_end":[0.5596,-0.00591,0.27426],"object_pos_start":[0.54023,0.00142,0.02295],"object_to_goal_dist_end":0.20385,"object_to_goal_dist_start":0.25367,"object_z_max":0.27403,"peak_contact_force":0.10405,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":33587.0,"raw_peak_contact_force":4.31641,"tcp_end":[0.54265,-0.00975,0.2754],"tcp_start":[0.54512,-0.00963,0.00475],"tcp_to_object_dist_end":0.01742,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":39.0,"n_steps":411.0,"n_steps_budget":1000.0,"object_pos_end":[0.63886,0.14274,0.17392],"object_pos_start":[0.5596,-0.00591,0.27426],"object_to_goal_dist_end":0.02464,"object_to_goal_dist_start":0.20385,"object_z_max":0.2745,"peak_contact_force":0.08539,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":13727.0,"raw_peak_contact_force":0.19676,"subtask_id":"reach_goal","tcp_end":[0.6355,0.14238,0.18944],"tcp_start":[0.54265,-0.00975,0.2754],"tcp_to_object_dist_end":0.01588,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":20.0,"average_failure_rate":0.19802,"average_mean_iterations":43.14851,"average_solve_count":101.0,"average_success_count":81.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.05002,"approach_to_object.approach_speed":0.22088,"descend_to_grasp.descend_force_threshold":17.42164,"descend_to_grasp.descend_speed":0.06457,"descend_to_grasp.descend_z_offset":0.01864,"grasp.grasp_duration":0.61398,"lift.lift_height":0.19762,"lift.lift_speed":0.11621,"transport_to_goal.transport_speed":0.21765},"optimized_scores":{"best_composite_score":-0.22905,"best_fitness_score":0.31095,"best_task_score":0.29452},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1420.0,"contact_point_centroid":[0.5305,0.03079,-0.0019],"force_p95":0.1356,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12297,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51083,0.01329,0.1996]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51634,0.02689,0.08873]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51219,0.02662,0.17569]},{"body_a":"world","body_b":"grasp_target","contact_count":1704.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55021,0.09418,0.18931]},{"body_a":"left_finger","body_b":"right_finger","contact_count":758.0,"contact_point_centroid":[0.51548,0.02684,0.08973],"force_p95":0.0132,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01087,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51543,0.02683,0.0876]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2441.0,"contact_point_centroid":[0.51246,0.02663,0.17854],"force_p95":0.01101,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.0128,"mean_force":0.01046,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5122,0.02663,0.17622]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1801.0,"contact_point_centroid":[0.55069,0.09424,0.19145],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01266,"mean_force":0.01054,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.55025,0.09423,0.18925]}],"total_contact_groups":7},"final_pose_error":0.01992,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5305,0.03079,0.02602],"final_tcp_position":[0.59008,0.16383,0.11504],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273017.79731,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":356.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1420.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52343,0.02722,0.0979],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07232,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":0.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.52343,0.02722,0.0979],"tcp_start":[0.52343,0.02722,0.0979],"tcp_to_object_dist_end":0.07232,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2958.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51543,0.02683,0.0876],"tcp_start":[0.51543,0.02683,0.0876],"tcp_to_object_dist_end":0.06352,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":573.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":4733.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51277,0.02666,0.26552],"tcp_start":[0.51543,0.02683,0.0876],"tcp_to_object_dist_end":0.2402,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":426.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":273017.79731,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3505.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.59008,0.16383,0.11504],"tcp_start":[0.51277,0.02666,0.26552],"tcp_to_object_dist_end":0.1708,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```