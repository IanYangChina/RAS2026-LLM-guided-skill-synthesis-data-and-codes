## Search State

- **Seed**: 3
- **Iteration**: 12 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 11 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | -0.0416 | 0.21 | ❌ rejected |
| 10 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | 0.1391 | 0.41 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | 9 | 0.3490 | 0.62 | ✅ accepted |
| 8 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.0852 | 0.25 | ❌ rejected |
| 7 | approach → descend → grasp → lift → approach → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | position_control | position_control | pose_tolerance | force_exceeded | time_limit | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 11 | -0.1283 | 0.30 | ✅ accepted |

**Proposal policy**: task_score is 0.21 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.042) — your mutation base

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

- **Composite score**: -0.042
- **task_score** (E): 0.209
- **fitness_score**: 0.298  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.200
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.540

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_to_object | 1.00 | 1.00 | 0.1845 |
| descend_to_grasp | 1.00 | 1.00 | 0.0278 |
| grasp | 1.00 | 1.00 | 0.0281 |
| lift | 1.00 | 0.67 | 0.2395 |
| transport_to_goal | 0.00 | 0.67 | 0.0000 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_to_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.507, 0.002, 0.120) | (0.511, 0.002, 0.030)→(0.511, 0.002, 0.026) | 0.244→0.246 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / force_exceeded | (0.507, 0.002, 0.120)→(0.526, 0.002, 0.101) | (0.511, 0.002, 0.026)→(0.511, 0.002, 0.026) | 0.246→0.246 | 1.00 / 4.000 | 280.213 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.514, 0.005, 0.065)→(0.505, 0.003, 0.038) | (0.511, 0.002, 0.026)→(0.510, -0.001, 0.025) | 0.246→0.249 | 1.00 / 27.000 | 91002.175 | 4.058 |
| lift | lift | 1.00 / step_budget | (0.505, 0.003, 0.038)→(0.503, 0.003, 0.278) | (0.510, -0.001, 0.025)→(0.497, 0.006, 0.042) | 0.248→0.243 | 0.67 / 5.333 | 0.082 | 1.529 |
| transport_to_goal | approach | 0.00 / guard_failure | (0.503, 0.003, 0.278)→(0.503, 0.003, 0.278) | (0.497, 0.006, 0.042)→(0.497, 0.005, 0.040) | 0.243→0.244 | 0.67 / 6.000 | 182006.597 | 0.082 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 0.000
- transport_retention: None
- terminal_score: 0.214
- phase_score: 0.243
- phase_breakdown.reach_object_score: 0.772
- phase_breakdown.reach_goal_score: 0.015
- grasp_place_fitness: 0.332

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.332
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.295
- **Median Q (composite search score)**: -0.035
- **K-run variance**: 0.0009
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.397


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0814,"average_solve_count":86.0,"average_success_count":86.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.07186,"approach_to_object.approach_speed":0.12197,"descend_to_grasp.descend_contact_offset":-0.00133,"descend_to_grasp.descend_force_threshold":10.03156,"descend_to_grasp.descend_speed":0.05548,"grasp.grasp_duration":0.85321,"lift.lift_height":0.2835,"lift.lift_speed":0.1372,"transport_to_goal.transport_speed":0.29506},"optimized_scores":{"best_composite_score":-0.08186,"best_fitness_score":0.25814,"best_task_score":0.11863},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"left_finger","contact_count":5978.0,"contact_point_centroid":[0.47224,-0.04848,-0.002],"force_p95":1.51882,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11.59876,"mean_force":0.87725,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46974,-0.00725,0.00214]},{"body_a":"world","body_b":"right_finger","contact_count":5326.0,"contact_point_centroid":[0.46347,0.03368,-0.00201],"force_p95":1.44211,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":11.28893,"mean_force":0.87825,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46972,-0.00725,0.00214]},{"body_a":"world","body_b":"left_finger","contact_count":182.0,"contact_point_centroid":[0.4751,-0.04609,-0.00157],"force_p95":3.15241,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.5698,"mean_force":1.13564,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46941,-0.00728,0.00442]},{"body_a":"world","body_b":"right_finger","contact_count":160.0,"contact_point_centroid":[0.46654,0.03192,-0.00157],"force_p95":2.96487,"geom_a":"table","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":3.23783,"mean_force":1.00262,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46943,-0.00728,0.00431]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1753.0,"contact_point_centroid":[0.47472,-0.04496,0.00568],"force_p95":0.04427,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.11681,"mean_force":0.02551,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46988,-0.00724,0.00222]},{"body_a":"world","body_b":"grasp_target","contact_count":2660.0,"contact_point_centroid":[0.40739,0.00213,-0.00215],"force_p95":0.33628,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.01564,"mean_force":0.1439,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46659,-0.0073,0.15142]},{"body_a":"grasp_target","body_b":"hand","contact_count":504.0,"contact_point_centroid":[0.47098,-0.00624,0.04696],"force_p95":0.20681,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.97733,"mean_force":0.09547,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4698,-0.00725,0.00219]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":159.0,"contact_point_centroid":[0.45535,0.01237,0.02719],"force_p95":0.36885,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.97635,"mean_force":0.27407,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46645,-0.00731,0.02886]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.45705,-0.02595,-0.00225],"force_p95":0.23675,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72015,"mean_force":0.14375,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.47301,-0.00739,0.00619]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":915.0,"contact_point_centroid":[0.4701,-0.03454,0.01675],"force_p95":0.24246,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.40118,"mean_force":0.09087,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46744,-0.00731,0.01951]},{"body_a":"grasp_target","body_b":"hand","contact_count":11.0,"contact_point_centroid":[0.46986,-0.00475,0.0477],"force_p95":0.25776,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26059,"mean_force":0.18706,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46974,-0.00726,0.00297]},{"body_a":"world","body_b":"grasp_target","contact_count":944.0,"contact_point_centroid":[0.45856,-0.02632,-0.00186],"force_p95":0.13706,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12314,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.48218,-0.01042,0.21753]},{"body_a":"world","body_b":"grasp_target","contact_count":100.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47296,-0.0181,0.11666]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.40442,0.00406,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46757,-0.00731,0.26604]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2296.0,"contact_point_centroid":[0.46743,-0.00722,0.17872],"force_p95":0.01122,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01045,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46659,-0.0073,0.17685]},{"body_a":"left_finger","body_b":"right_finger","contact_count":12.0,"contact_point_centroid":[0.46839,-0.00723,0.26797],"force_p95":0.01079,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01079,"mean_force":0.01076,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.46757,-0.00731,0.26604]}],"total_contact_groups":16},"final_pose_error":0.3098,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.40442,0.00406,0.01602],"final_tcp_position":[0.46768,-0.00731,0.26622],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":273009.99123,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":237.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":944.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.46336,-0.02169,0.13069],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.10488,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":25.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":426.67973,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":100.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.49645,-0.01463,0.09595],"tcp_start":[0.46336,-0.02169,0.13069],"tcp_to_object_dist_end":0.08038,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":32.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.45408,-0.02629,0.02596],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30619,"object_to_goal_dist_start":0.30365,"object_z_max":0.02603,"peak_contact_force":1.46412,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":15761.0,"raw_peak_contact_force":11.59876,"tcp_end":[0.47001,-0.00723,0.00223],"tcp_start":[0.47,-0.00723,0.00222],"tcp_to_object_dist_end":0.03435,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":784.0,"n_steps_budget":1000.0,"object_pos_end":[0.40442,0.00406,0.01602],"object_pos_start":[0.45392,-0.0259,0.02603],"object_to_goal_dist_end":0.31976,"object_to_goal_dist_start":0.30597,"object_z_max":0.03707,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":6383.0,"raw_peak_contact_force":3.5698,"tcp_end":[0.46751,-0.00731,0.26589],"tcp_start":[0.47001,-0.00723,0.00223],"tcp_to_object_dist_end":0.25796,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.40442,0.00406,0.01602],"object_pos_start":[0.40442,0.00406,0.01602],"object_to_goal_dist_end":0.31976,"object_to_goal_dist_start":0.31976,"object_z_max":0.01602,"peak_contact_force":273009.99123,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.46768,-0.00731,0.26622],"tcp_start":[0.46766,-0.00731,0.26616],"tcp_to_object_dist_end":0.25832,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `aa6ec658384c70fac6b4eb656cc8c53536c3d5c760368ab2b384dccf294e2c48`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":37.0,"average_failure_rate":0.32174,"average_mean_iterations":67.5913,"average_solve_count":115.0,"average_success_count":78.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.06397,"approach_to_object.approach_speed":0.15846,"descend_to_grasp.descend_contact_offset":-0.03405,"descend_to_grasp.descend_force_threshold":12.70011,"descend_to_grasp.descend_speed":0.05829,"grasp.grasp_duration":0.40489,"lift.lift_height":0.22612,"lift.lift_speed":0.10363,"transport_to_goal.transport_speed":0.1392},"optimized_scores":{"best_composite_score":-0.00789,"best_fitness_score":0.33211,"best_task_score":0.21386},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":106.0,"contact_point_centroid":[0.54462,-0.00886,-0.00198],"force_p95":0.70288,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.89446,"mean_force":0.15803,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53006,-0.00968,0.02258]},{"body_a":"grasp_target","body_b":"hand","contact_count":99.0,"contact_point_centroid":[0.54989,0.01098,0.06744],"force_p95":0.1969,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.48154,"mean_force":0.07586,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.5285,-0.0097,0.03332]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54529,-0.00159,-0.00273],"force_p95":0.34334,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.45158,"mean_force":0.19907,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53522,-0.00975,0.02484]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6476.0,"contact_point_centroid":[0.52993,0.00971,0.10265],"force_p95":0.1424,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.42899,"mean_force":0.09669,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52771,-0.00972,0.10218]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":8641.0,"contact_point_centroid":[0.53458,-0.02729,0.10227],"force_p95":0.12636,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32684,"mean_force":0.07733,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52775,-0.00972,0.10126]},{"body_a":"grasp_target","body_b":"hand","contact_count":372.0,"contact_point_centroid":[0.55244,0.01421,0.05475],"force_p95":0.28099,"geom_a":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32173,"mean_force":0.10968,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53188,-0.00958,0.02041]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":3905.0,"contact_point_centroid":[0.53551,-0.02776,0.02305],"force_p95":0.09169,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2158,"mean_force":0.04645,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53173,-0.00961,0.02017]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4334.0,"contact_point_centroid":[0.53118,0.0124,0.02174],"force_p95":0.13186,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16516,"mean_force":0.07458,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53176,-0.0096,0.02022]},{"body_a":"world","body_b":"grasp_target","contact_count":972.0,"contact_point_centroid":[0.54431,0.00113,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12313,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51639,0.00044,0.21262]},{"body_a":"world","body_b":"grasp_target","contact_count":72.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.54203,-0.00065,0.11295]}],"total_contact_groups":10},"final_pose_error":0.20864,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.55545,-0.01861,0.07357],"final_tcp_position":[0.52884,-0.00967,0.22688],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":331.10329,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":244.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":972.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.53427,0.0009,0.12189],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.09639,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":18.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":331.10329,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":72.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.55838,-0.00501,0.10005],"tcp_start":[0.53427,0.0009,0.12189],"tcp_to_object_dist_end":0.07561,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":40.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54683,-0.00736,0.02371],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25603,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.24379,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10411.0,"raw_peak_contact_force":0.45158,"tcp_end":[0.53173,-0.00964,0.02016],"tcp_start":[0.55838,-0.00501,0.10005],"tcp_to_object_dist_end":0.01569,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":689.0,"n_steps_budget":1000.0,"object_pos_end":[0.55517,-0.01815,0.08506],"object_pos_start":[0.54683,-0.00736,0.02371],"object_to_goal_dist_end":0.2255,"object_to_goal_dist_start":0.25603,"object_z_max":0.18592,"peak_contact_force":0.0,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":15322.0,"raw_peak_contact_force":0.89446,"tcp_end":[0.52862,-0.00973,0.2266],"tcp_start":[0.53173,-0.00964,0.02016],"tcp_to_object_dist_end":0.14425,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":4.0,"n_steps_budget":1000.0,"object_pos_end":[0.55531,-0.01838,0.07939],"object_pos_start":[0.55517,-0.01815,0.08506],"object_to_goal_dist_end":0.22834,"object_to_goal_dist_start":0.2255,"object_z_max":0.08506,"peak_contact_force":0.0,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"subtask_id":"reach_goal","tcp_end":[0.52884,-0.00967,0.22688],"tcp_start":[0.52883,-0.00968,0.22689],"tcp_to_object_dist_end":0.15009,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e1209649252ffcf03853fe0727696e22a1eda11729c6c1ae21659980557d7e98`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":85.0,"average_failure_rate":0.62963,"average_mean_iterations":127.72593,"average_solve_count":135.0,"average_success_count":50.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_to_object.approach_height":0.05003,"approach_to_object.approach_speed":0.26165,"descend_to_grasp.descend_contact_offset":-0.0226,"descend_to_grasp.descend_force_threshold":8.36835,"descend_to_grasp.descend_speed":0.02043,"grasp.grasp_duration":0.81829,"lift.lift_height":0.26829,"lift.lift_speed":0.22047,"transport_to_goal.transport_speed":0.27906},"optimized_scores":{"best_composite_score":-0.03507,"best_fitness_score":0.30493,"best_task_score":0.29452},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":996.0,"contact_point_centroid":[0.5305,0.03079,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12312,"phase_index":0.0,"phase_name":"approach_to_object","phase_type":"approach","tcp_position_centroid":[0.51086,0.01247,0.20582]},{"body_a":"world","body_b":"grasp_target","contact_count":2200.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51484,0.02663,0.09408]},{"body_a":"world","body_b":"grasp_target","contact_count":2752.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51119,0.02638,0.21669]},{"body_a":"world","body_b":"grasp_target","contact_count":12.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51239,0.02644,0.34162]},{"body_a":"world","body_b":"grasp_target","contact_count":8.0,"contact_point_centroid":[0.5305,0.03079,-0.00199],"force_p95":0.12262,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12262,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52293,0.02597,0.10778]},{"body_a":"left_finger","body_b":"right_finger","contact_count":761.0,"contact_point_centroid":[0.51424,0.02657,0.09538],"force_p95":0.01282,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01566,"mean_force":0.01083,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.51394,0.02657,0.09302]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2938.0,"contact_point_centroid":[0.51138,0.02638,0.21894],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01277,"mean_force":0.01044,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51119,0.02638,0.2166]},{"body_a":"left_finger","body_b":"right_finger","contact_count":12.0,"contact_point_centroid":[0.51264,0.02644,0.34371],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01101,"phase_index":4.0,"phase_name":"transport_to_goal","phase_type":"approach","tcp_position_centroid":[0.51239,0.02644,0.34162]}],"total_contact_groups":8},"final_pose_error":0.29275,"key_states":{"actual_goal_position":[0.60153,0.17858,0.10809],"final_object_position":[0.5305,0.03079,0.02602],"final_tcp_position":[0.51249,0.02645,0.34182],"realised_goal_position":[0.60153,0.17858,0.10809],"realised_object_initial_position":[0.5305,0.03079,0.03]},"peak_contact_force":273009.79904,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":250.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.03],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18162,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_to_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":996.0,"raw_peak_contact_force":0.13845,"subtask_id":"reach_object","tcp_end":[0.52285,0.02579,0.10817],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.08266,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":2.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":82.85697,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":8.0,"raw_peak_contact_force":0.12262,"tcp_end":[0.52327,0.02678,0.10656],"tcp_start":[0.52285,0.02579,0.10817],"tcp_to_object_dist_end":0.08096,"terminated_normally":true,"termination_reason":"force_exceeded"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":150.0,"n_steps_budget":50.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":273004.81854,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":2961.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51394,0.02657,0.09302],"tcp_start":[0.51394,0.02657,0.09302],"tcp_to_object_dist_end":0.06914,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":688.0,"n_steps_budget":780.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":5690.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.51234,0.02644,0.34146],"tcp_start":[0.51394,0.02657,0.09302],"tcp_to_object_dist_end":0.316,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.5305,0.03079,0.02602],"object_pos_start":[0.5305,0.03079,0.02602],"object_to_goal_dist_end":0.18336,"object_to_goal_dist_start":0.18336,"object_z_max":0.02602,"peak_contact_force":273009.79904,"phase_name":"transport_to_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":24.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_goal","tcp_end":[0.51249,0.02645,0.34182],"tcp_start":[0.51247,0.02645,0.34176],"tcp_to_object_dist_end":0.31634,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":false}]}
```