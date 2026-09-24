## Search State

- **Seed**: 9
- **Iteration**: 7 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 6 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | 0.1636 | 0.36 | ✅ accepted |
| 5 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | impedance_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 6 | -0.1002 | 0.19 | ❌ rejected |
| 4 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | -0.1455 | 0.17 | ❌ rejected |
| 3 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | pose_tolerance | 5 | 0.0380 | 0.20 | ✅ accepted |
| 2 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | — | linear_cartesian | position_control | force_threshold_switch | position_control | position_control | position_control | force_threshold_switch | position_control | position_control | pose_tolerance | force_exceeded | grasp_success | pose_tolerance | pose_tolerance | force_exceeded | pose_tolerance | pose_tolerance | 7 | -0.1077 | 0.17 | ❌ rejected |

**Proposal policy**: task_score is 0.36 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

## Current Skill (Q=0.164) — your mutation base

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
    anchor: task_object
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
      default: 0.2
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.01
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
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
  guards:
  - id: transport_lift_check
    when: before_phase
    predicate: object_lifted
    threshold: 0.1
    on_failure: retry
  retries:
    max_attempts: 2
    strategy: repeat
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
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.01], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - descend_speed: status=consumed; consumers=generator.speed (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
- **lift** (`lift`)
  - target: source=yaml, anchor=task_object, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=grasp_lift_check, when=before_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=2, strategy=repeat
- **transport** (`approach`)
  - target: source=yaml, anchor=task_goal, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=transport_lift_check, when=before_phase, predicate=object_lifted, on_failure=retry, threshold=0.1
  - retries: max_attempts=2, strategy=repeat
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

- **Composite score**: 0.164
- **task_score** (E): 0.360
- **fitness_score**: 0.644  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.480

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_object | 1.00 | 1.00 | 0.1097 |
| descend_to_grasp | 1.00 | 1.00 | 0.1424 |
| grasp | 1.00 | 1.00 | 0.0130 |
| lift | 1.00 | 1.00 | 0.0946 |
| transport | 1.00 | 0.67 | 0.2649 |
| descend_to_place | 1.00 | 1.00 | 0.1009 |
| release | 1.00 | 1.00 | 0.0195 |
| retract | 1.00 | 1.00 | 0.0849 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.510, -0.014, 0.197) | (0.515, -0.017, 0.030)→(0.515, -0.017, 0.026) | 0.268→0.270 | 1.00 / 4.000 | 0.123 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.510, -0.014, 0.197)→(0.510, -0.016, 0.055) | (0.515, -0.017, 0.026)→(0.515, -0.017, 0.026) | 0.270→0.270 | 1.00 / 4.000 | 0.123 | 0.123 |
| grasp | grasp | 1.00 / step_budget | (0.510, -0.016, 0.055)→(0.502, -0.016, 0.045) | (0.515, -0.017, 0.026)→(0.515, -0.016, 0.026) | 0.270→0.270 | 1.00 / 42.333 | 0.139 | 0.184 |
| lift | lift | 1.00 / step_budget | (0.502, -0.016, 0.045)→(0.509, -0.016, 0.139) | (0.515, -0.016, 0.026)→(0.513, -0.016, 0.113) | 0.270→0.237 | 1.00 / 35.333 | 0.094 | 0.396 |
| transport | approach | 1.00 / step_budget | (0.509, -0.016, 0.139)→(0.609, 0.166, 0.297) | (0.513, -0.016, 0.113)→(0.611, 0.147, 0.168) | 0.237→0.115 | 0.67 / 7.667 | 0.085 | 0.720 |
| descend_to_place | descend | 1.00 / step_budget | (0.609, 0.166, 0.297)→(0.613, 0.177, 0.197) | (0.611, 0.147, 0.168)→(0.614, 0.150, 0.048) | 0.115→0.127 | 1.00 / 7.333 | 91009.245 | 0.950 |
| release | release | 1.00 / step_budget | (0.613, 0.177, 0.197)→(0.607, 0.175, 0.216) | (0.614, 0.150, 0.048)→(0.616, 0.148, 0.016) | 0.127→0.158 | 1.00 / 4.000 | 0.123 | 0.542 |
| retract | retract | 1.00 / step_budget | (0.607, 0.175, 0.216)→(0.605, 0.175, 0.301) | (0.616, 0.148, 0.016)→(0.616, 0.148, 0.016) | 0.158→0.158 | 1.00 / 4.000 | 0.123 | 0.123 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.000
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 0.492
- phase_score: 0.492
- phase_breakdown.lift_object_score: 0.451
- phase_breakdown.reach_object_score: 0.224
- phase_breakdown.place_object_score: 0.556
- grasp_place_fitness: 0.709

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.709
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.492
- **Median Q (composite search score)**: 0.142
- **K-run variance**: 0.0022
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 8.0
- **Final σ (mean)**: 0.270


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
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.76518,"average_solve_count":247.0,"average_success_count":247.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.08422,"descend_to_grasp.descend_speed":0.07936,"descend_to_place.descend_speed":0.07855,"lift.lift_height":0.13998,"lift.lift_speed":0.05974,"transport.speed":0.07579},"optimized_scores":{"best_composite_score":0.11913,"best_fitness_score":0.59913,"best_task_score":0.27057},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":307.0,"contact_point_centroid":[0.62838,0.18846,-0.00682],"force_p95":1.36622,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":2.43469,"mean_force":0.32794,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6035,0.21356,0.25615]},{"body_a":"world","body_b":"grasp_target","contact_count":216.0,"contact_point_centroid":[0.53393,-0.02019,-0.00118],"force_p95":0.23211,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41828,"mean_force":0.06724,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52098,-0.02043,0.04588]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18888.0,"contact_point_centroid":[0.52581,-0.03962,0.09372],"force_p95":0.07746,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26894,"mean_force":0.05359,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52451,-0.02049,0.0918]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19688.0,"contact_point_centroid":[0.5253,-0.00141,0.09226],"force_p95":0.07482,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26649,"mean_force":0.05173,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52435,-0.02049,0.09051]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12866.0,"contact_point_centroid":[0.56195,0.09596,0.21886],"force_p95":0.1301,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.23367,"mean_force":0.07387,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55917,0.07709,0.21975]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":15176.0,"contact_point_centroid":[0.56265,0.06111,0.22126],"force_p95":0.10861,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.21796,"mean_force":0.0627,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.56002,0.07968,0.22197]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.53705,-0.02123,-0.00208],"force_p95":0.14341,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.19351,"mean_force":0.12869,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52372,-0.02048,0.04555]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.62826,0.18908,-0.00192],"force_p95":0.13502,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13849,"mean_force":0.12277,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60177,0.2181,0.23361]},{"body_a":"world","body_b":"grasp_target","contact_count":864.0,"contact_point_centroid":[0.53702,-0.02132,-0.00185],"force_p95":0.13725,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12319,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51253,-0.00821,0.24952]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5066.0,"contact_point_centroid":[0.52318,-0.00128,0.04728],"force_p95":0.06681,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.12681,"mean_force":0.04278,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52254,-0.02046,0.04418]},{"body_a":"world","body_b":"grasp_target","contact_count":1076.0,"contact_point_centroid":[0.53702,-0.02132,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.52809,-0.01887,0.12606]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.62826,0.18907,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59871,0.21665,0.29309]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4929.0,"contact_point_centroid":[0.52353,-0.03974,0.04597],"force_p95":0.07074,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07313,"mean_force":0.04498,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52254,-0.02046,0.04419]},{"body_a":"left_finger","body_b":"right_finger","contact_count":245.0,"contact_point_centroid":[0.60442,0.21503,0.25299],"force_p95":0.01417,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01509,"mean_force":0.01143,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60396,0.21501,0.25069]},{"body_a":"left_finger","body_b":"right_finger","contact_count":224.0,"contact_point_centroid":[0.60422,0.21908,0.2321],"force_p95":0.01091,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01267,"mean_force":0.00996,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60369,0.21906,0.22983]}],"total_contact_groups":15},"final_pose_error":0.01545,"key_states":{"actual_goal_position":[0.61031,0.22775,0.20741],"final_object_position":[0.62826,0.18907,0.01602],"final_tcp_position":[0.59911,0.21674,0.33773],"realised_goal_position":[0.61031,0.22775,0.20741],"realised_object_initial_position":[0.53702,-0.02132,0.03]},"peak_contact_force":273010.10134,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":217.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.03],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31446,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":864.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.52705,-0.01723,0.19665],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17097,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":269.0,"n_steps_budget":1000.0,"object_pos_end":[0.53702,-0.02132,0.02602],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31672,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1076.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53128,-0.0206,0.05471],"tcp_start":[0.52705,-0.01723,0.19665],"tcp_to_object_dist_end":0.02926,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":45.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.53696,-0.02073,0.02571],"object_pos_start":[0.53702,-0.02132,0.02602],"object_to_goal_dist_end":0.31645,"object_to_goal_dist_start":0.31672,"object_z_max":0.02602,"peak_contact_force":0.14053,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":11795.0,"raw_peak_contact_force":0.19351,"tcp_end":[0.52251,-0.02046,0.04415],"tcp_start":[0.53128,-0.0206,0.05471],"tcp_to_object_dist_end":0.02343,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5358,-0.02071,0.11489],"object_pos_start":[0.53696,-0.02073,0.02571],"object_to_goal_dist_end":0.27541,"object_to_goal_dist_start":0.31645,"object_z_max":0.11478,"peak_contact_force":0.07795,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38792.0,"raw_peak_contact_force":0.41828,"subtask_id":"lift_object","tcp_end":[0.53053,-0.0206,0.14081],"tcp_start":[0.52251,-0.02046,0.04415],"tcp_to_object_dist_end":0.02645,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":false,"contact_event_count":0.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61381,0.18997,0.26595],"object_pos_start":[0.5358,-0.02071,0.11489],"object_to_goal_dist_end":0.06976,"object_to_goal_dist_start":0.27541,"object_z_max":0.28254,"peak_contact_force":0.0,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":28042.0,"raw_peak_contact_force":0.23367,"tcp_end":[0.59892,0.19746,0.32315],"tcp_start":[0.53053,-0.0206,0.14081],"tcp_to_object_dist_end":0.05958,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":9.0,"n_steps":165.0,"n_steps_budget":1000.0,"object_pos_end":[0.62839,0.18975,0.01739],"object_pos_start":[0.61381,0.18997,0.26595],"object_to_goal_dist_end":0.19463,"object_to_goal_dist_start":0.06976,"object_z_max":0.26595,"peak_contact_force":273010.10134,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":552.0,"raw_peak_contact_force":2.43469,"subtask_id":"place_object","tcp_end":[0.60536,0.21935,0.23474],"tcp_start":[0.59892,0.19746,0.32315],"tcp_to_object_dist_end":0.22056,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.62826,0.18906,0.01602],"object_pos_start":[0.62839,0.18975,0.01739],"object_to_goal_dist_end":0.19609,"object_to_goal_dist_start":0.19463,"object_z_max":0.01739,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1024.0,"raw_peak_contact_force":0.13849,"tcp_end":[0.60066,0.21755,0.25308],"tcp_start":[0.60536,0.21935,0.23474],"tcp_to_object_dist_end":0.24035,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.62826,0.18907,0.01602],"object_pos_start":[0.62826,0.18906,0.01602],"object_to_goal_dist_end":0.19609,"object_to_goal_dist_start":0.19609,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.59911,0.21674,0.33773],"tcp_start":[0.60066,0.21755,0.25308],"tcp_to_object_dist_end":0.32421,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `1e57d18e69439f9d4839513252d085a45363faa5c1c2b52093c9c8149b88bb68`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.7277,"average_solve_count":213.0,"average_success_count":213.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.07842,"descend_to_grasp.descend_speed":0.07813,"descend_to_place.descend_speed":0.08124,"lift.lift_height":0.14703,"lift.lift_speed":0.05864,"transport.speed":0.13409},"optimized_scores":{"best_composite_score":0.14231,"best_fitness_score":0.62231,"best_task_score":0.31675},"replay_outcomes":[{"contacts":{"omitted_contact_groups":1,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1368.0,"contact_point_centroid":[0.61177,0.10662,-0.00281],"force_p95":0.39834,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.72307,"mean_force":0.16125,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.60942,0.12142,0.2766]},{"body_a":"world","body_b":"grasp_target","contact_count":239.0,"contact_point_centroid":[0.5422,-0.02756,-0.00121],"force_p95":0.21762,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.41058,"mean_force":0.0713,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52907,-0.02796,0.04548]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18765.0,"contact_point_centroid":[0.53337,-0.00885,0.09062],"force_p95":0.08119,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27924,"mean_force":0.05422,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53217,-0.02797,0.08874]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":19523.0,"contact_point_centroid":[0.53362,-0.04704,0.09105],"force_p95":0.07561,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.27416,"mean_force":0.05215,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.53222,-0.02797,0.08912]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5528.0,"contact_point_centroid":[0.56203,0.03637,0.17578],"force_p95":0.1178,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.25948,"mean_force":0.07707,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55726,0.01761,0.17601]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5872.0,"contact_point_centroid":[0.5607,-0.00301,0.17406],"force_p95":0.12118,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24356,"mean_force":0.07266,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.55632,0.01565,0.17417]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54564,-0.02908,-0.00211],"force_p95":0.15264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.21223,"mean_force":0.13089,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53197,-0.02806,0.04515]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4229.0,"contact_point_centroid":[0.53182,-0.00881,0.04652],"force_p95":0.07853,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14432,"mean_force":0.05035,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53077,-0.02802,0.04374]},{"body_a":"world","body_b":"grasp_target","contact_count":920.0,"contact_point_centroid":[0.5456,-0.02923,-0.00186],"force_p95":0.13709,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12316,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.51596,-0.01142,0.24868]},{"body_a":"world","body_b":"grasp_target","contact_count":1064.0,"contact_point_centroid":[0.5456,-0.02923,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53595,-0.02603,0.12544]},{"body_a":"world","body_b":"grasp_target","contact_count":724.0,"contact_point_centroid":[0.61182,0.10657,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62763,0.15878,0.26004]},{"body_a":"world","body_b":"grasp_target","contact_count":800.0,"contact_point_centroid":[0.61182,0.10657,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62469,0.16086,0.20437]},{"body_a":"world","body_b":"grasp_target","contact_count":2292.0,"contact_point_centroid":[0.61182,0.10657,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.62093,0.15964,0.26372]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4966.0,"contact_point_centroid":[0.53185,-0.04717,0.04551],"force_p95":0.07222,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.07428,"mean_force":0.04457,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53077,-0.02802,0.04374]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1246.0,"contact_point_centroid":[0.61225,0.12621,0.28356],"force_p95":0.01236,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01737,"mean_force":0.01069,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.61188,0.12621,0.28129]},{"body_a":"left_finger","body_b":"right_finger","contact_count":218.0,"contact_point_centroid":[0.62716,0.16162,0.20269],"force_p95":0.01099,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.011,"mean_force":0.01017,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.62699,0.16161,0.20067]}],"total_contact_groups":17},"final_pose_error":0.01534,"key_states":{"actual_goal_position":[0.63284,0.16493,0.17692],"final_object_position":[0.61182,0.10657,0.01602],"final_tcp_position":[0.62131,0.1597,0.30858],"realised_goal_position":[0.63284,0.16493,0.17692],"realised_object_initial_position":[0.5456,-0.02923,0.03]},"peak_contact_force":1.72307,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":231.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.03],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.25864,"object_z_max":0.03,"peak_contact_force":0.12262,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":920.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.53446,-0.02391,0.19531],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.16974,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":266.0,"n_steps_budget":1000.0,"object_pos_end":[0.5456,-0.02923,0.02602],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26092,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1064.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.53962,-0.02826,0.0546],"tcp_start":[0.53446,-0.02391,0.19531],"tcp_to_object_dist_end":0.02921,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54555,-0.02824,0.02562],"object_pos_start":[0.5456,-0.02923,0.02602],"object_to_goal_dist_end":0.26044,"object_to_goal_dist_start":0.26092,"object_z_max":0.02602,"peak_contact_force":0.14786,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10995.0,"raw_peak_contact_force":0.21223,"tcp_end":[0.53074,-0.02802,0.0437],"tcp_start":[0.53962,-0.02826,0.0546],"tcp_to_object_dist_end":0.02337,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":35.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.54347,-0.02814,0.11099],"object_pos_start":[0.54555,-0.02824,0.02562],"object_to_goal_dist_end":0.22273,"object_to_goal_dist_start":0.26044,"object_z_max":0.11088,"peak_contact_force":0.09189,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":38527.0,"raw_peak_contact_force":0.41058,"subtask_id":"lift_object","tcp_end":[0.53788,-0.02805,0.13677],"tcp_start":[0.53074,-0.02802,0.0437],"tcp_to_object_dist_end":0.02638,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":882.0,"n_steps_budget":1000.0,"object_pos_end":[0.61182,0.10657,0.01602],"object_pos_start":[0.54347,-0.02814,0.11099],"object_to_goal_dist_end":0.17244,"object_to_goal_dist_start":0.22273,"object_z_max":0.19374,"peak_contact_force":0.12263,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14014.0,"raw_peak_contact_force":1.72307,"tcp_end":[0.62701,0.15587,0.31013],"tcp_start":[0.53788,-0.02805,0.13677],"tcp_to_object_dist_end":0.29861,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":181.0,"n_steps_budget":1000.0,"object_pos_end":[0.61182,0.10657,0.01602],"object_pos_start":[0.61182,0.10657,0.01602],"object_to_goal_dist_end":0.17244,"object_to_goal_dist_start":0.17244,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1513.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.62887,0.16205,0.20575],"tcp_start":[0.62701,0.15587,0.31013],"tcp_to_object_dist_end":0.19841,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.61182,0.10657,0.01602],"object_pos_start":[0.61182,0.10657,0.01602],"object_to_goal_dist_end":0.17244,"object_to_goal_dist_start":0.17244,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":1018.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62334,0.16041,0.22377],"tcp_start":[0.62887,0.16205,0.20575],"tcp_to_object_dist_end":0.21492,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":573.0,"n_steps_budget":660.0,"object_pos_end":[0.61182,0.10657,0.01602],"object_pos_start":[0.61182,0.10657,0.01602],"object_to_goal_dist_end":0.17244,"object_to_goal_dist_start":0.17244,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2292.0,"raw_peak_contact_force":0.12263,"tcp_end":[0.62131,0.1597,0.30858],"tcp_start":[0.62334,0.16041,0.22377],"tcp_to_object_dist_end":0.2975,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `5836f8a66456087ed82e2e1accc6472c2a7681a19bf8e3d54637158aadaafc47`.


Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.51681,"average_solve_count":238.0,"average_success_count":238.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_object.speed":0.12708,"descend_to_grasp.descend_speed":0.0855,"descend_to_place.descend_speed":0.14843,"lift.lift_height":0.1326,"lift.lift_speed":0.03558,"transport.speed":0.0672},"optimized_scores":{"best_composite_score":0.22931,"best_fitness_score":0.70931,"best_task_score":0.49233},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":600.0,"contact_point_centroid":[0.60802,0.14906,-0.00329],"force_p95":0.70196,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.36373,"mean_force":0.18943,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.59865,0.14852,0.15172]},{"body_a":"world","body_b":"grasp_target","contact_count":169.0,"contact_point_centroid":[0.4592,-0.00042,-0.00117],"force_p95":0.30433,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.3604,"mean_force":0.07281,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.4509,-0.00021,0.04881]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":1355.0,"contact_point_centroid":[0.60326,0.12895,0.20367],"force_p95":0.20253,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.29368,"mean_force":0.12806,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60155,0.14699,0.20797]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":1709.0,"contact_point_centroid":[0.6045,0.16461,0.19676],"force_p95":0.16112,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.26349,"mean_force":0.09708,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.60191,0.14735,0.20133]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":16620.0,"contact_point_centroid":[0.4521,-0.01945,0.09414],"force_p95":0.08995,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2603,"mean_force":0.06081,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45301,-0.00029,0.0934]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":20382.0,"contact_point_centroid":[0.45303,0.0186,0.09583],"force_p95":0.07247,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24863,"mean_force":0.04928,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.45316,-0.00029,0.09493]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9546.0,"contact_point_centroid":[0.51962,0.04695,0.19026],"force_p95":0.12472,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.20264,"mean_force":0.08014,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52083,0.06574,0.19202]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":12047.0,"contact_point_centroid":[0.5205,0.08443,0.19082],"force_p95":0.11877,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19885,"mean_force":0.06491,"phase_index":4.0,"phase_name":"transport","phase_type":"approach","tcp_position_centroid":[0.52097,0.06589,0.19213]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":10.0,"contact_point_centroid":[0.60606,0.1636,0.14377],"force_p95":0.1529,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.16748,"mean_force":0.08791,"phase_index":6.0,"phase_name":"release","phase_type":"release","tcp_position_centroid":[0.60451,0.15012,0.15043]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.46285,-0.00014,-0.00202],"force_p95":0.12935,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.14767,"mean_force":0.12452,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45319,-0.00018,0.04838]},{"body_a":"world","body_b":"grasp_target","contact_count":768.0,"contact_point_centroid":[0.46286,-7e-05,-0.00183],"force_p95":0.13759,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12326,"phase_index":0.0,"phase_name":"approach_object","phase_type":"approach","tcp_position_centroid":[0.48433,-4e-05,0.25125]},{"body_a":"world","body_b":"grasp_target","contact_count":2172.0,"contact_point_centroid":[0.6085,0.14809,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12291,"mean_force":0.12262,"phase_index":7.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.59483,0.14744,0.21065]},{"body_a":"world","body_b":"grasp_target","contact_count":1120.0,"contact_point_centroid":[0.46286,-7e-05,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12262,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46323,-9e-05,0.12792]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4129.0,"contact_point_centroid":[0.45145,-0.0194,0.04891],"force_p95":0.07593,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09827,"mean_force":0.05182,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45214,-0.00019,0.04736]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4864.0,"contact_point_centroid":[0.45227,0.01887,0.04866],"force_p95":0.06782,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08802,"mean_force":0.04462,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.45214,-0.00019,0.04736]}],"total_contact_groups":15},"final_pose_error":0.01508,"key_states":{"actual_goal_position":[0.61015,0.15287,0.12219],"final_object_position":[0.6085,0.14809,0.01602],"final_tcp_position":[0.59507,0.14746,0.25532],"realised_goal_position":[0.61015,0.15287,0.12219],"realised_object_initial_position":[0.46286,-7e-05,0.03]},"peak_contact_force":17.51178,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":193.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.03],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.23148,"object_z_max":0.03,"peak_contact_force":0.12263,"phase_name":"approach_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":768.0,"raw_peak_contact_force":0.13845,"tcp_end":[0.46785,-7e-05,0.1993],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.17335,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":280.0,"n_steps_budget":1000.0,"object_pos_end":[0.46286,-7e-05,0.02602],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.2331,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12262,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1120.0,"raw_peak_contact_force":0.12263,"subtask_id":"reach_object","tcp_end":[0.45999,-0.00011,0.05533],"tcp_start":[0.46785,-7e-05,0.1993],"tcp_to_object_dist_end":0.02945,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.46277,-0.00033,0.02591],"object_pos_start":[0.46286,-7e-05,0.02602],"object_to_goal_dist_end":0.23337,"object_to_goal_dist_start":0.2331,"object_z_max":0.02602,"peak_contact_force":0.12879,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.14767,"tcp_end":[0.45212,-0.00019,0.04733],"tcp_start":[0.45999,-0.00011,0.05533],"tcp_to_object_dist_end":0.02393,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":33.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.4601,0.00021,0.11256],"object_pos_start":[0.46277,-0.00033,0.02591],"object_to_goal_dist_end":0.21427,"object_to_goal_dist_start":0.23337,"object_z_max":0.11249,"peak_contact_force":0.11295,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37171.0,"raw_peak_contact_force":0.3604,"subtask_id":"lift_object","tcp_end":[0.45763,-0.00034,0.14059],"tcp_start":[0.45212,-0.00019,0.04733],"tcp_to_object_dist_end":0.02814,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":15.0,"n_steps":812.0,"n_steps_budget":1000.0,"object_pos_end":[0.60615,0.14503,0.22326],"object_pos_start":[0.4601,0.00021,0.11256],"object_to_goal_dist_end":0.10145,"object_to_goal_dist_start":0.21427,"object_z_max":0.22315,"peak_contact_force":0.13305,"phase_name":"transport","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":21593.0,"raw_peak_contact_force":0.20264,"tcp_end":[0.5998,0.1445,0.25751],"tcp_start":[0.45763,-0.00034,0.14059],"tcp_to_object_dist_end":0.03484,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":184.0,"n_steps_budget":1000.0,"object_pos_end":[0.60272,0.15322,0.10949],"object_pos_start":[0.60615,0.14503,0.22326],"object_to_goal_dist_end":0.01471,"object_to_goal_dist_start":0.10145,"object_z_max":0.22328,"peak_contact_force":17.51178,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3064.0,"raw_peak_contact_force":0.29368,"subtask_id":"place_object","tcp_end":[0.60461,0.15012,0.15085],"tcp_start":[0.5998,0.1445,0.25751],"tcp_to_object_dist_end":0.04151,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.6085,0.14809,0.01601],"object_pos_start":[0.60272,0.15322,0.10949],"object_to_goal_dist_end":0.1063,"object_to_goal_dist_start":0.01471,"object_z_max":0.10949,"peak_contact_force":0.12293,"phase_name":"release","phase_peak_obstacle_force":0.0,"phase_type":"release","raw_contact_event_count":610.0,"raw_peak_contact_force":1.36373,"tcp_end":[0.59789,0.1483,0.17011],"tcp_start":[0.60461,0.15012,0.15085],"tcp_to_object_dist_end":0.15447,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":543.0,"n_steps_budget":630.0,"object_pos_end":[0.6085,0.14809,0.01602],"object_pos_start":[0.6085,0.14809,0.01601],"object_to_goal_dist_end":0.10629,"object_to_goal_dist_start":0.1063,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":2172.0,"raw_peak_contact_force":0.12291,"tcp_end":[0.59507,0.14746,0.25532],"tcp_start":[0.59789,0.1483,0.17011],"tcp_to_object_dist_end":0.23967,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```