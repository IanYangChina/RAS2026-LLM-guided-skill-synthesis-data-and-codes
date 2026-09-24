## Search State

- **Seed**: 9
- **Iteration**: 6 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1002 | 0.19 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1455 | 0.17 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0380 | 0.20 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1077 | 0.17 | ❌ rejected |
| 1 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | impedance_control | position_control | position_control | position_control | impedance_control | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 5 | -0.0077 | 0.17 | ✅ accepted |

**Proposal policy**: task_score is 0.19 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=-0.100) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
skill_type: arm_gripper
subtasks:
- id: reach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.1
  weight: 0.1
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.3
- id: place_object
  target_entity: object
  weight: 0.6
phases:
- id: approach_object
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    offset:
    - 0.0
    - 0.0
    - 0.02
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: reach_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
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
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
  guards:
  - id: grasp_lift_check
    when: before_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
  subtask_id: lift_object
- id: transport
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
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.2
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    offset:
    - 0.0
    - 0.0
    - 0.01
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    descend_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: place_object
- id: release
  type: release
  control: position_control
  termination: pose_tolerance
  end_effector_action: open
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
- id: retract
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.1
    orientation:
      mode: keep_current

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_object** (`approach`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.02], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
  - guards:
    - id=grasp_lift_check, when=before_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **release** (`release`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **retract** (`retract`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.1]
  - orientation: mode=keep_current
  - parameter_bindings: none

## Design Metrics

- **Composite score**: -0.100
- **task_score** (E): 0.190
- **fitness_score**: 0.380  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1098 |
| descend_to_grasp | 1.00 | 1.00 | 0.1322 |
| grasp | 1.00 | 1.00 | 0.0129 |
| lift | 0.67 | 1.00 | 0.0824 |
| transport | 0.00 | 1.00 | 0.0937 |
| descend_to_place | 1.00 | 1.00 | 0.0907 |
| release | 1.00 | 1.00 | 0.0191 |
| retract | 1.00 | 1.00 | 0.0847 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.197) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.197)→(0.510, -0.016, 0.065) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.016, 0.065)→(0.502, -0.016, 0.055) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 26.333 | 0.141 | 0.181 |
| lift | lift | 0.67 / step_budget | (0.502, -0.016, 0.055)→(0.498, -0.016, 0.138) | (0.515, -0.017, 0.026)→(0.498, 0.001, 0.053) | 0.270→0.254 | 1.00 / 11.667 | 0.119 | 0.483 |
| transport | approach | 0.00 / guard_failure | (0.498, -0.016, 0.138)→(0.524, 0.055, 0.193) | (0.498, 0.001, 0.053)→(0.509, 0.025, 0.019) | 0.254→0.250 | 1.00 / 8.000 | 0.123 | 0.527 |
| descend_to_place | descend | 1.00 / step_budget | (0.596, 0.192, 0.320)→(0.605, 0.218, 0.234) | (0.560, 0.053, 0.016)→(0.560, 0.053, 0.016) | 0.264→0.264 | 1.00 / 8.000 | 0.123 | 0.123 |
| release | release | 1.00 / step_budget | (0.605, 0.218, 0.234)→(0.600, 0.216, 0.252) | (0.560, 0.053, 0.016)→(0.560, 0.053, 0.016) | 0.264→0.264 | 1.00 / 4.000 | 0.123 | 0.123 |
| retract | retract | 1.00 / step_budget | (0.600, 0.216, 0.252)→(0.598, 0.216, 0.337) | (0.560, 0.053, 0.016)→(0.560, 0.053, 0.016) | 0.264→0.264 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.172
- phase_score: 0.520
- phase_breakdown.lift_object_score: 0.520
- phase_breakdown.reach_object_score: 0.269
- phase_breakdown.place_object_score: 0.563
- grasp_place_fitness: 0.538

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.538
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.216
- **Median Q (composite search score)**: -0.172
- **K-run variance**: 0.0126
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.399


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `425c48e82220fc6e1b680086671cf7dd2586733ee271dec2149f96a25d69d0c6`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `58e88c03db0a62276863b22a53636bc89fead3e4bc7f4d35fd72d2282ace32bf`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.24188,"average_solve_count":277.0,"average_success_count":277.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.14613,"descend_to_grasp.descend_speed":0.03614,"descend_to_place.place_descend_speed":0.11989,"lift.lift_height":0.11145,"lift.lift_speed":0.10138,"transport.transport_speed":0.04224},"optimized_scores":{"best_composite_score":0.05814,"best_fitness_score":0.53814,"best_task_score":0.17182},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2699.0,"contact_point_centroid":[0.5599,0.05267,-0.00236],"force_p95":0.12815,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.58035,"mean_force":0.14046,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56936,0.12323,0.26437]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5935.0,"contact_point_centroid":[0.52203,-0.00201,0.09588],"force_p95":0.13307,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2912,"mean_force":0.09738,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51853,-0.02032,0.09941]},{"body_a":"world","body_b":"grasp_target","contact_count":150.0,"contact_point_centroid":[0.53407,-0.02001,-0.0012],"force_p95":0.23397,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.28346,"mean_force":0.0583,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52101,-0.02038,0.05583]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6080.0,"contact_point_centroid":[0.52194,-0.03862,0.09663],"force_p95":0.13375,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27546,"mean_force":0.0955,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.51855,-0.02032,0.10027]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1932.0,"contact_point_centroid":[0.53129,0.02414,0.16497],"force_p95":0.14574,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21554,"mean_force":0.1091,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52561,0.00588,0.16992]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02125,-0.00207],"force_p95":0.14405,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.18761,"mean_force":0.12783,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52382,-0.02044,0.05556]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2207.0,"contact_point_centroid":[0.53114,-0.01146,0.16578],"force_p95":0.12314,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16643,"mean_force":0.0949,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52585,0.00657,0.17046]},{"body_a":"world","body_b":"grasp_target","contact_count":832.0,"contact_point_centroid":[0.53702,-0.02132,-0.00184],"force_p95":0.13728,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12321,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51264,-0.00824,0.24934]},{"body_a":"world","body_b":"grasp_target","contact_count":1056.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52807,-0.01882,0.13186]},{"body_a":"world","body_b":"grasp_target","contact_count":648.0,"contact_point_centroid":[0.55993,0.05274,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59975,0.2042,0.27866]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.55993,0.05274,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60106,0.21693,0.23283]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.55993,0.05274,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59799,0.21548,0.29235]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2664.0,"contact_point_centroid":[0.52368,-0.00166,0.05126],"force_p95":0.09832,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1066,"mean_force":0.07622,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52265,-0.02041,0.05419]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2969.0,"contact_point_centroid":[0.52333,-0.03911,0.05109],"force_p95":0.09357,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09364,"mean_force":0.0697,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52265,-0.02041,0.05419]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2654.0,"contact_point_centroid":[0.57192,0.12903,0.27132],"force_p95":0.01104,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01622,"mean_force":0.01052,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.57157,0.12903,0.26909]},{"body_a":"left_finger","body_b":"right_finger","contact_count":689.0,"contact_point_centroid":[0.60013,0.20416,0.28096],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01102,"mean_force":0.01047,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.59974,0.20415,0.27885]}],"total_contact_groups":17},"final_pose_error":0.01542,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.55993,0.05274,0.01602],"final_tcp_position":[0.59839,0.21556,0.337],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":1.58035,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":209.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":832.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52715,-0.0172,0.19689],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17121,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":264.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1056.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53123,-0.02055,0.06469],"tcp_start":[0.52715,-0.0172,0.19689],"tcp_to_object_dist_end":0.03911,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53697,-0.0207,0.02576],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.3164,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14164,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7433.0,"raw_peak_contact_force":0.18761,"tcp_end":[0.52262,-0.02041,0.05415],"tcp_start":[0.53123,-0.02055,0.06469],"tcp_to_object_dist_end":0.03181,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":19.0,"n_steps":608.0,"n_steps_budget":690.0,"object_pos_end":[0.52472,-0.02037,0.11633],"object_pos_start":[0.53697,-0.0207,0.02576],"object_to_goal_dist_end":0.27783,"object_to_goal_dist_start":0.3164,"object_z_max":0.11621,"peak_contact_force":0.11324,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":12165.0,"raw_peak_contact_force":0.2912,"subtask_id":"lift_object","tcp_end":[0.51866,-0.02032,0.15291],"tcp_start":[0.52262,-0.02041,0.05415],"tcp_to_object_dist_end":0.03708,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55993,0.05274,0.01602],"object_pos_start":[0.52472,-0.02037,0.11633],"object_to_goal_dist_end":0.2642,"object_to_goal_dist_start":0.27783,"object_z_max":0.15107,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":9492.0,"raw_peak_contact_force":1.58035,"tcp_end":[0.59571,0.19211,0.32032],"tcp_start":[0.51866,-0.02032,0.15291],"tcp_to_object_dist_end":0.33661,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":162.0,"n_steps_budget":1000.0,"object_pos_end":[0.55993,0.05274,0.01602],"object_pos_start":[0.55993,0.05274,0.01602],"object_to_goal_dist_end":0.2642,"object_to_goal_dist_start":0.2642,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1337.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.60469,0.21814,0.23392],"tcp_start":[0.59571,0.19211,0.32032],"tcp_to_object_dist_end":0.27721,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.55993,0.05274,0.01602],"object_pos_start":[0.55993,0.05274,0.01602],"object_to_goal_dist_end":0.2642,"object_to_goal_dist_start":0.2642,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1025.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59995,0.21638,0.25231],"tcp_start":[0.60469,0.21814,0.23392],"tcp_to_object_dist_end":0.29019,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.55993,0.05274,0.01602],"object_pos_start":[0.55993,0.05274,0.01602],"object_to_goal_dist_end":0.2642,"object_to_goal_dist_start":0.2642,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59839,0.21556,0.337],"tcp_start":[0.59995,0.21638,0.25231],"tcp_to_object_dist_end":0.36196,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":2.44298,"average_solve_count":228.0,"average_success_count":228.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.02235,"descend_to_grasp.descend_speed":0.06853,"descend_to_place.place_descend_speed":0.04841,"lift.lift_height":0.11042,"lift.lift_speed":0.01026,"transport.transport_speed":0.08957},"optimized_scores":{"best_composite_score":-0.18709,"best_fitness_score":0.29291,"best_task_score":0.18248},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":2017.0,"contact_point_centroid":[0.5218,-0.00608,-0.00223],"force_p95":0.2998,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.58372,"mean_force":0.14272,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52655,-0.02781,0.08523]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4796.0,"contact_point_centroid":[0.52803,-0.00925,0.06077],"force_p95":0.15546,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.39754,"mean_force":0.09661,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52652,-0.02782,0.06454]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54565,-0.02915,-0.0021],"force_p95":0.15303,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.20561,"mean_force":0.13071,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53202,-0.02799,0.05556]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5672.0,"contact_point_centroid":[0.52729,-0.04566,0.06183],"force_p95":0.11923,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.18411,"mean_force":0.07907,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52648,-0.02781,0.06539]},{"body_a":"world","body_b":"grasp_target","contact_count":1008.0,"contact_point_centroid":[0.5456,-0.02923,-0.00187],"force_p95":0.13691,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12311,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51534,-0.01113,0.24981]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2622.0,"contact_point_centroid":[0.53223,-0.00928,0.05117],"force_p95":0.1193,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.126,"mean_force":0.08334,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53084,-0.02796,0.05414]},{"body_a":"world","body_b":"grasp_target","contact_count":1004.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53595,-0.026,0.13077]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2992.0,"contact_point_centroid":[0.53164,-0.04651,0.05104],"force_p95":0.09467,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09675,"mean_force":0.06852,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53085,-0.02796,0.05415]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1617.0,"contact_point_centroid":[0.52658,-0.02781,0.09532],"force_p95":0.01163,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01645,"mean_force":0.0106,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52623,-0.0278,0.09295]}],"total_contact_groups":9},"final_pose_error":0.06253,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.51706,0.00426,0.01602],"final_tcp_position":[0.52631,-0.0278,0.10216],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":0.58372,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":253.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":1008.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53442,-0.02392,0.19527],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.1697,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":251.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1004.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53955,-0.02819,0.06504],"tcp_start":[0.53442,-0.02392,0.19527],"tcp_to_object_dist_end":0.0395,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":27.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54579,-0.02829,0.02558],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26041,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.15032,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":7414.0,"raw_peak_contact_force":0.20561,"tcp_end":[0.53081,-0.02795,0.05411],"tcp_start":[0.53955,-0.02819,0.06504],"tcp_to_object_dist_end":0.03222,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.51706,0.00426,0.01602],"object_pos_start":[0.54579,-0.02829,0.02558],"object_to_goal_dist_end":0.25516,"object_to_goal_dist_start":0.26041,"object_z_max":0.04033,"peak_contact_force":0.12262,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":14102.0,"raw_peak_contact_force":0.58372,"subtask_id":"lift_object","tcp_end":[0.52631,-0.0278,0.10216],"tcp_start":[0.53081,-0.02795,0.05411],"tcp_to_object_dist_end":0.09238,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.51706,0.00426,0.01602],"object_pos_start":[0.51706,0.00426,0.01602],"object_to_goal_dist_end":0.25516,"object_to_goal_dist_start":0.25516,"peak_contact_force":0.12262,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.52631,-0.0278,0.10216],"tcp_start":[0.52631,-0.0278,0.10216],"tcp_to_object_dist_end":0.09238,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.14103,"average_solve_count":156.0,"average_success_count":156.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.08826,"descend_to_grasp.descend_speed":0.05577,"descend_to_place.place_descend_speed":0.04615,"lift.lift_height":0.14901,"lift.lift_speed":0.03219,"transport.transport_speed":0.14827},"optimized_scores":{"best_composite_score":-0.17155,"best_fitness_score":0.30845,"best_task_score":0.21609},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":3229.0,"contact_point_centroid":[0.45119,0.01596,-0.00207],"force_p95":0.22306,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57541,"mean_force":0.12945,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44853,-0.00021,0.11601]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2237.0,"contact_point_centroid":[0.44893,0.01797,0.06212],"force_p95":0.11316,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29261,"mean_force":0.07837,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4492,-0.00021,0.06611]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1691.0,"contact_point_centroid":[0.4481,-0.0189,0.06211],"force_p95":0.14986,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26059,"mean_force":0.10066,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44927,-0.00021,0.06559]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46286,-0.00018,-0.00202],"force_p95":0.13112,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14837,"mean_force":0.12454,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4534,-0.00017,0.05845]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.46286,-7e-05,-0.00184],"force_p95":0.1373,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12324,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48431,-4e-05,0.25111]},{"body_a":"world","body_b":"grasp_target","contact_count":1088.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46314,-9e-05,0.133]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":2193.0,"contact_point_centroid":[0.45043,-0.01896,0.05438],"force_p95":0.11407,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.1149,"mean_force":0.0903,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45236,-0.00018,0.05743]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":2928.0,"contact_point_centroid":[0.45196,0.01823,0.05352],"force_p95":0.09135,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09201,"mean_force":0.06947,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45236,-0.00018,0.05743]},{"body_a":"left_finger","body_b":"right_finger","contact_count":2835.0,"contact_point_centroid":[0.44867,-0.00021,0.12549],"force_p95":0.01119,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01653,"mean_force":0.01077,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44843,-0.00021,0.12333]}],"total_contact_groups":9},"final_pose_error":0.04908,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.45089,0.01796,0.02602],"final_tcp_position":[0.44863,-0.0002,0.15747],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":0.57541,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":201.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":800.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46782,-7e-05,0.19896],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17301,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":272.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1088.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.46005,-0.0001,0.06537],"tcp_start":[0.46782,-7e-05,0.19896],"tcp_to_object_dist_end":0.03945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":25.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00055,0.02592],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23351,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.13023,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":6921.0,"raw_peak_contact_force":0.14837,"tcp_end":[0.45233,-0.00018,0.0574],"tcp_start":[0.46005,-0.0001,0.06537],"tcp_to_object_dist_end":0.03317,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45089,0.01796,0.02602],"object_pos_start":[0.46277,-0.00055,0.02592],"object_to_goal_dist_end":0.22981,"object_to_goal_dist_start":0.23351,"object_z_max":0.04001,"peak_contact_force":0.12263,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":9992.0,"raw_peak_contact_force":0.57541,"subtask_id":"lift_object","tcp_end":[0.44863,-0.0002,0.15747],"tcp_start":[0.45233,-0.00018,0.0574],"tcp_to_object_dist_end":0.13272,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":0.0,"n_steps_budget":0.0,"object_pos_end":[0.45089,0.01796,0.02602],"object_pos_start":[0.45089,0.01796,0.02602],"object_to_goal_dist_end":0.22981,"object_to_goal_dist_start":0.22981,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":0.0,"raw_peak_contact_force":0.0,"tcp_end":[0.44863,-0.0002,0.15747],"tcp_start":[0.44863,-0.0002,0.15747],"tcp_to_object_dist_end":0.13272,"terminated_normally":false,"termination_reason":"guard_failure"}],"success":true}]}
```