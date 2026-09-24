## Search State

- **Seed**: 3
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | 0.1495 | 0.42 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | 0.0702 | 0.43 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | -0.0416 | 0.21 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | 0.1391 | 0.41 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | 0.3490 | 0.62 | ✅ accepted |

**Proposal policy**: task_score is 0.42 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.150) — your mutation base

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

- **Composite score**: 0.150
- **task_score** (E): 0.424
- **fitness_score**: 0.490  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.2032 |
| descend_to_grasp | 1.00 | 1.00 | 0.0213 |
| grasp | 1.00 | 1.00 | 0.0157 |
| lift | 1.00 | 1.00 | 0.2310 |
| transport_to_goal | 0.33 | 1.00 | 0.0602 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.506, 0.002, 0.102) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / force_exceeded | (0.506, 0.002, 0.102)→(0.521, 0.003, 0.089) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 306.016 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.512, 0.003, 0.059)→(0.506, 0.004, 0.045) | (0.511, 0.002, 0.026)→(0.509, 0.005, 0.024) | 0.246→0.245 | 1.00 / 24.667 | 0.945 | 4.900 |
| lift | lift | 1.00 / step_budget | (0.506, 0.004, 0.045)→(0.503, 0.004, 0.276) | (0.509, 0.005, 0.024)→(0.518, 0.000, 0.087) | 0.245→0.225 | 1.00 / 19.667 | 91001.528 | 1.933 |
| transport_to_goal | approach | 0.33 / guard_failure | (0.503, 0.004, 0.276)→(0.534, 0.055, 0.266) | (0.518, 0.000, 0.087)→(0.544, 0.050, 0.072) | 0.225→0.171 | 1.00 / 19.000 | 94253.114 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 0.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.845
- phase_score: 0.644
- phase_breakdown.reach_object_score: 0.580
- phase_breakdown.reach_goal_score: 0.672
- grasp_place_fitness: 0.883

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.883
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.845
- **Median Q (composite search score)**: 0.017
- **K-run variance**: 0.0799
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Parameters at lower bound**: approach_to_object.approach_height
- **Final σ (mean)**: 0.377


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.78846,"average_solve_count":52.0,"average_success_count":52.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.05,"approach_to_object.approach_speed":0.29134,"descend_to_grasp.descend_depth":0.10423,"descend_to_grasp.descend_force_threshold":7.38926,"descend_to_grasp.descend_speed":0.036,"grasp.grasp_duration":0.97238,"lift.lift_height":0.28252,"lift.lift_speed":0.21868,"transport_to_goal.transport_speed":0.29705},"optimized_scores":{"best_composite_score":-0.11059,"best_fitness_score":0.22941,"best_task_score":0.13208},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1352.0,"contact_point_centroid":[0.45856,-0.02632,-0.0019],"force_p95":0.13562,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12299,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.47976,-0.01131,0.20083]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4528,-0.02253,0.09023]},{"body_a":"world","body_b":"grasp_target","contact_count":2732.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44951,-0.0224,0.22035]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.45058,-0.02246,0.35225]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.45975,-0.02316,0.09943]},{"body_a":"left_finger","body_b":"right_finger","contact_count":748.0,"contact_point_centroid":[0.45231,-0.02251,0.09163],"force_p95":0.01321,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01099,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45198,-0.02251,0.08939]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2868.0,"contact_point_centroid":[0.44981,-0.02241,0.22259],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01287,"mean_force":0.0106,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44951,-0.0224,0.22032]},{"body_a":"left_finger","body_b":"right_finger","contact_count":12.0,"contact_point_centroid":[0.4508,-0.02246,0.35434],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01101,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.45058,-0.02246,0.35225]}],"total_contact_groups":8},"final_pose_error":0.37711,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.45856,-0.02632,0.02602],"final_tcp_position":[0.45058,-0.02246,0.35237],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273010.799,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":339.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1352.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.45975,-0.0232,0.09972],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07377,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":405.43398,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12262,"tcp_end":[0.45985,-0.02291,0.09848],"tcp_start":[0.45975,-0.0232,0.09972],"tcp_to_object_dist_end":0.07255,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2948.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45198,-0.02251,0.08939],"tcp_start":[0.45198,-0.02251,0.08939],"tcp_to_object_dist_end":0.06382,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":683.0,"n_steps_budget":810.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5600.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.45057,-0.02246,0.35214],"tcp_start":[0.45198,-0.02251,0.08939],"tcp_to_object_dist_end":0.32624,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":273010.799,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.45058,-0.02246,0.35237],"tcp_start":[0.45059,-0.02246,0.35234],"tcp_to_object_dist_end":0.32648,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":34.0,"average_failure_rate":0.28333,"average_mean_iterations":60.61667,"average_solve_count":120.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.05619,"approach_to_object.approach_speed":0.13488,"descend_to_grasp.descend_depth":0.09974,"descend_to_grasp.descend_force_threshold":2.20694,"descend_to_grasp.descend_speed":0.04987,"grasp.grasp_duration":0.58117,"lift.lift_height":0.23523,"lift.lift_speed":0.17228,"transport_to_goal.transport_speed":0.18947},"optimized_scores":{"best_composite_score":0.5425,"best_fitness_score":0.8825,"best_task_score":0.84517},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"right_finger","contact_count":7353.0,"contact_point_centroid":[0.53891,0.02995,-0.00361],"force_p95":2.36299,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":13.70596,"mean_force":1.61058,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.5483,-0.00904,0.00019]},{"body_a":"world","body_b":"left_finger","contact_count":5858.0,"contact_point_centroid":[0.5559,-0.04908,-0.00173],"force_p95":1.31163,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":6.54024,"mean_force":0.7881,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54823,-0.00904,0.00011]},{"body_a":"world","body_b":"right_finger","contact_count":360.0,"contact_point_centroid":[0.53854,0.02783,-0.00251],"force_p95":3.25676,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.96412,"mean_force":1.03462,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54736,-0.00896,0.00358]},{"body_a":"world","body_b":"left_finger","contact_count":181.0,"contact_point_centroid":[0.55771,-0.04651,-0.00136],"force_p95":2.50021,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":2.72679,"mean_force":0.86833,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54773,-0.00898,0.00188]},{"body_a":"grasp_target","body_b":"hand","contact_count":515.0,"contact_point_centroid":[0.55538,0.01623,0.04442],"force_p95":0.53754,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.13705,"mean_force":0.50469,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.54856,-0.00902,0.00043]},{"body_a":"world","body_b":"grasp_target","contact_count":267.0,"contact_point_centroid":[0.53707,-0.00146,-0.00271],"force_p95":0.32995,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.99895,"mean_force":0.1866,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54624,-0.00894,0.01009]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":11984.0,"contact_point_centroid":[0.54011,0.00995,0.11557],"force_p95":0.07942,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.67793,"mean_force":0.05177,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54403,-0.00922,0.11493]},{"body_a":"grasp_target","body_b":"hand","contact_count":657.0,"contact_point_centroid":[0.5649,-0.01124,0.14439],"force_p95":0.43482,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.63104,"mean_force":0.12188,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54424,-0.0092,0.10728]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.54154,-0.00107,-0.00365],"force_p95":0.362,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.43187,"mean_force":0.23598,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.55083,-0.00893,0.0036]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":11576.0,"contact_point_centroid":[0.54886,-0.02761,0.12603],"force_p95":0.07739,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.34615,"mean_force":0.04978,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.54401,-0.00923,0.12307]},{"body_a":"world","body_b":"grasp_target","contact_count":1500.0,"contact_point_centroid":[0.54431,0.00113,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12295,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51672,0.00046,0.2028]},{"body_a":"world","body_b":"grasp_target","contact_count":84.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54605,-0.00265,0.095]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8844.0,"contact_point_centroid":[0.59426,0.04825,0.20099],"force_p95":0.0724,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11961,"mean_force":0.04844,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.58947,0.06653,0.19807]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8353.0,"contact_point_centroid":[0.58745,0.08846,0.19815],"force_p95":0.07661,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11944,"mean_force":0.05218,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.59126,0.06953,0.19748]}],"total_contact_groups":14},"final_pose_error":0.01989,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.63718,0.14308,0.17371],"final_tcp_position":[0.63616,0.14332,0.18432],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":431.47224,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":376.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1500.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53564,0.00095,0.10416],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07862,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":21.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":431.47224,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":84.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.56829,-0.00813,0.08092],"tcp_start":[0.53564,0.00095,0.10416],"tcp_to_object_dist_end":0.06062,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":31.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.53918,0.00141,0.02225],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25459,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":2.347,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":15926.0,"raw_peak_contact_force":13.70596,"tcp_end":[0.54817,-0.00903,-4e-05],"tcp_start":[0.54817,-0.00903,-4e-05],"tcp_to_object_dist_end":0.02621,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":659.0,"n_steps_budget":870.0,"object_pos_end":[0.55836,-0.00618,0.21769],"object_pos_start":[0.53881,0.001,0.02232],"object_to_goal_dist_end":0.18884,"object_to_goal_dist_start":0.25495,"object_z_max":0.21745,"peak_contact_force":0.07568,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":25025.0,"raw_peak_contact_force":3.96412,"tcp_end":[0.54501,-0.00919,0.2157],"tcp_start":[0.54817,-0.00903,-4e-05],"tcp_to_object_dist_end":0.01383,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":432.0,"n_steps_budget":1000.0,"object_pos_end":[0.63718,0.14308,0.17371],"object_pos_start":[0.55836,-0.00618,0.21769],"object_to_goal_dist_end":0.02523,"object_to_goal_dist_start":0.18884,"object_z_max":0.21807,"peak_contact_force":0.0758,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":17197.0,"raw_peak_contact_force":0.11961,"subtask_id":"reach_goal","tcp_end":[0.63616,0.14332,0.18432],"tcp_start":[0.54501,-0.00919,0.2157],"tcp_to_object_dist_end":0.01067,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":28.0,"average_failure_rate":0.24561,"average_mean_iterations":52.39474,"average_solve_count":114.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.05279,"approach_to_object.approach_speed":0.17318,"descend_to_grasp.descend_depth":0.0583,"descend_to_grasp.descend_force_threshold":9.20664,"descend_to_grasp.descend_speed":0.06678,"grasp.grasp_duration":0.27382,"lift.lift_height":0.23414,"lift.lift_speed":0.08829,"transport_to_goal.transport_speed":0.26458},"optimized_scores":{"best_composite_score":0.01663,"best_fitness_score":0.35663,"best_task_score":0.2945},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":550.0,"contact_point_centroid":[0.53483,0.03568,-0.00408],"force_p95":0.77794,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.71343,"mean_force":0.19909,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51422,0.04429,0.20315]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5149.0,"contact_point_centroid":[0.51879,0.02364,0.04621],"force_p95":0.10639,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.87019,"mean_force":0.05235,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51718,0.0446,0.04547]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53079,0.03184,-0.00299],"force_p95":0.38337,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.59755,"mean_force":0.19397,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51935,0.045,0.04788]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4865.0,"contact_point_centroid":[0.51625,0.06305,0.10669],"force_p95":0.16038,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.36509,"mean_force":0.10491,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51319,0.0442,0.11006]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":7986.0,"contact_point_centroid":[0.51628,0.02626,0.11583],"force_p95":0.1325,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.33612,"mean_force":0.07102,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51316,0.0442,0.11495]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2647.0,"contact_point_centroid":[0.51865,0.06361,0.04281],"force_p95":0.13027,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16942,"mean_force":0.07471,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51701,0.04459,0.04529]},{"body_a":"world","body_b":"grasp_target","contact_count":1448.0,"contact_point_centroid":[0.5305,0.03079,-0.00191],"force_p95":0.13511,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12296,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51077,0.01323,0.20131]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.53677,0.03371,-0.00193],"force_p95":0.12534,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12534,"mean_force":0.12471,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51423,0.04428,0.25985]},{"body_a":"world","body_b":"grasp_target","contact_count":52.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52711,0.03137,0.09589]},{"body_a":"left_finger","body_b":"right_finger","contact_count":247.0,"contact_point_centroid":[0.51459,0.04432,0.25285],"force_p95":0.01459,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01565,"mean_force":0.0115,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51404,0.04427,0.25072]},{"body_a":"left_finger","body_b":"right_finger","contact_count":14.0,"contact_point_centroid":[0.51466,0.04433,0.26191],"force_p95":0.01094,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01094,"mean_force":0.00998,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51423,0.04428,0.25985]}],"total_contact_groups":11},"final_pose_error":0.22075,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.53675,0.03378,0.01611],"final_tcp_position":[0.51431,0.04429,0.26004],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273009.35881,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":363.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1448.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52345,0.02719,0.10068],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.07508,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":13.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":81.14225,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":52.0,"raw_peak_contact_force":0.12262,"tcp_end":[0.53519,0.04032,0.08842],"tcp_start":[0.52345,0.02719,0.10068],"tcp_to_object_dist_end":0.0633,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53018,0.03992,0.02264],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.17782,"object_to_goal_dist_start":0.18336,"object_z_max":0.02608,"peak_contact_force":0.365,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":9596.0,"raw_peak_contact_force":0.87019,"tcp_end":[0.51698,0.04459,0.04525],"tcp_start":[0.53519,0.04032,0.08842],"tcp_to_object_dist_end":0.0266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":716.0,"n_steps_budget":1000.0,"object_pos_end":[0.53675,0.03379,0.01614],"object_pos_start":[0.53018,0.03992,0.02264],"object_to_goal_dist_end":0.18335,"object_to_goal_dist_start":0.17782,"object_z_max":0.16579,"peak_contact_force":273004.38442,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":13648.0,"raw_peak_contact_force":1.71343,"tcp_end":[0.51418,0.04428,0.2597],"tcp_start":[0.51698,0.04459,0.04525],"tcp_to_object_dist_end":0.24482,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.53675,0.03379,0.01613],"object_pos_start":[0.53675,0.03379,0.01614],"object_to_goal_dist_end":0.18335,"object_to_goal_dist_start":0.18335,"object_z_max":0.01614,"peak_contact_force":9748.46783,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":26.0,"raw_peak_contact_force":0.12534,"subtask_id":"reach_goal","tcp_end":[0.51431,0.04429,0.26004],"tcp_start":[0.51428,0.04429,0.25999],"tcp_to_object_dist_end":0.24517,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```